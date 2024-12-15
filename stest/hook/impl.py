#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import inspect
import functools
from warnings import warn
from stest.conf import settings
from .stage import RunStage
from .policy import RunPolicy


class Hook(object):

    def __init__(self, func, runstage, *, runpolicy=RunPolicy.AFTER, priority=49, name=None, options={}):
        self.__func = func
        self.runstage = runstage
        self.runpolicy = runpolicy
        self.name = func.__name__ if name is None else name
        self.options = options
        self.runtime_number = None
        self.priority = priority
        self.__host_func_list = []

    @property
    def func(self):
        return self.__func

    @property
    def func_file(self):

        return inspect.getfile(self.func)

    @property
    def is_mounted(self):

        return len(self.__host_func_list) > 0

    @property
    def host_func_list(self):
        """copy"""

        copy_host_func_list = []
        for one in self.__host_func_list:
            item = {}
            for k in one.keys():
                item[k] = one[k]
        return copy_host_func_list

    def printable(self):

        text = "{} priority = {}"
        return text.format(self.func.__qualname__, self.priority)

    def host(self, func, *args, **kwargs):

        if func not in [one["func"] for one in self.__host_func_list]:
            self.__host_func_list.append(dict(func=func, args=args, kwargs=kwargs))
        else:
            self.__update_host_func(func, *args, **kwargs)
        return self

    def get_host_index(self, func):

        index = -1
        for i, hf in enumerate(self.__host_func_list):
            if hf["func"] == func:
                index = i
                break
        return index

    def remove_host_func(self, func):

        index = self.get_host_index(func)
        return self.__host_func_list.pop(index)

    def clear_host(self):

        self.__host_func_list.clear()
        return self

    def __update_host_func(self, func, *args, **kwargs):

        for hf in self.__host_func_list:
            if hf["func"] == func:
                hf["args"] = args
                hf["kwargs"] = kwargs
        return self

    def check(self, host_func):
        """检查钩子函数是否能完全接收宿主函数的参数，同时还需额外接受一个settings参数，作为第一个位置参数

        Args:
            host_func - 宿主函数
        """

        hook = self
        host_spec = inspect.getfullargspec(host_func)
        hook_spec = inspect.getfullargspec(hook.func)

        # 宿主函数定义的位置参数个数
        host_count = len(host_spec.args)

        # 钩子函数定义的位置参数个数
        hook_count = len(hook_spec.args)

        # 钩子函数应接受的位置参数个数 = 宿主函数位置参数个数 + 1，即比钩子的宿主函数多接受一个settings参数，并作为第一个位置参数
        accept_args_count = host_count + 1

        hookname = hook.func.__qualname__
        # hostname = host_func.__qualname__

        # 钩子函数定义的位置参数个数 小于 钩子函数应接受的位置参数个数，
        # 则判断钩子函数是否有定义可变位置参数（如*args），有则说明可以完全接收，没有则报错
        if hook_count < accept_args_count:
            if hook_spec.varargs is None:
                raise TypeError("hook({}()) need to receive {} positional parameters. but it define {} positional parameters".format(
                    hookname, accept_args_count, hook_count))
        elif hook_count > accept_args_count:
            raise TypeError("hook({}()) need to receive {} positional parameters. but it define {} positional parameters".format(
                hookname, accept_args_count, hook_count))

        # 钩子函数({}())除多接收一个settings位置参数作为第一个位置参数外，其它位置参数需要与宿主函数一样
        miss_kwargs = []
        for kwarg in host_spec.kwonlyargs:
            if kwarg not in hook_spec.kwonlyargs:
                miss_kwargs.append(kwarg)
        if miss_kwargs:
            if hook_spec.varkw is None:
                # 钩子函数需要完全接收宿主函数的的关键字参数, 当前钩子函数无法接收以下关键字参数
                en = "The hook function ->{} needs to fully accept the keyword parameters of the host function, Currently, it cannot accept the following keyword parameters, please check: {}"
                raise TypeError(en.format(hook.func.__qualname__, ' '.join(miss_kwargs)))

        # 钩子函数需要完全接收宿主函数的可变位置参数
        if host_spec.varargs is not None and hook_spec.varargs is None:
            raise TypeError("钩子函数需要完全接收宿主函数的可变位置参数: {}".format(host_spec.varargs))

        # 钩子函数需要完全接收宿主函数的可变关键字参数
        if host_spec.varkw is not None and hook_spec.varkw is None:
            raise TypeError("钩子函数需要完全接收宿主函数的可变位置参数: {}".format(host_spec.varkw))

    def __call__(self, *args, **kwargs):

        return self.func(*args, **kwargs)


class HookManager(object):

    def __init__(self):

        self.__hooks = []

    @property
    def hooks(self):

        return self.__hooks

    def add_hook(self, hook: Hook):

        if hook not in self.__hooks:
            self.__hooks.append(hook)
        return self.__hooks.index(hook)

    def record_host_func(self, host_func, runstage, *host_args, **host_kwargs):

        for hook in self.__hooks:
            if hook.runstage == runstage:
                hook.host(host_func, *host_args, **host_kwargs)
        return self

    def __default_sort_func(self, hook):
        """默认排序函数 - 根据钩子的priority属性进行排序"""

        return hook.priority

    def is_need_to_restore_stdout(self, hook):

        for field, marker in RunStage.const_attrs.items():
            if hook.runstage == marker.value:
                return marker.expend_kwargs.get("restore_stdout", False)
        return False

    def warn_if_same_priority(self, hooks):

        groups = {}
        for hook in hooks:
            group = groups.get(hook.priority, [])
            if hook not in group:
                group.append(hook)
                groups[hook.priority] = group
        same = []
        for item in groups.items():
            if len(item[1]) >= 2:
                for h in item:
                    same.append(h.printable())
        if same:
            message = "these hooks has same priority: {}"
            message.format(" ".join(same))
            warn(message)

    def run(self, host_func, args, kwargs, runstage, runpolicy=RunPolicy.BEFORE, sort_key=None, sort_reverse=False, filter_func=None):
        """

        Args:
            host_func: 宿主函数
            args: 钩子函数位置实参构成的元祖
            kwargs: 钩子函数关键字实参构成的字典
            runstage: 运行阶段，指明运行哪个阶段的钩子函数，see :py:class:`RunStage`
            runpolicy: 运行策略，指明运行哪个策略的钩子函数，see :py:class:`RunPolicy`
            sort_key: 排序函数，同内置方法sorted 的key参数
            sort_reverse: 同内置方法sorted 的reverse参数，True -> 降序，False -> 升序
            filter_func: 过滤函数，同内置方法filter的function参数
        Returns:
            返回运行的钩子函数结果构成的字典，键是钩子函数，值是钩子函数运行返回值
        """

        reslist = {}
        hooklist = []
        if isinstance(args, list):
            args = tuple(args)
        for hook in self.hooks:
            if hook.runstage == runstage and hook.runpolicy == runpolicy:
                hooklist.append(hook)
        hooklist = list(filter(filter_func, hooklist))
        if sort_key is None:
            sort_key = self.__default_sort_func
        hooklist.sort(key=sort_key, reverse=sort_reverse)
        if getattr(settings, "WARN_IF_SAME_PRIORITY_OF_HOOK", False):
            self.warn_if_same_priority(hooklist)
        for hook in hooklist:
            throw_exception = False
            try:
                hook.check(host_func)
                reslist[hook] = hook(*args, *kwargs)
            except Exception as e:
                throw_exception = True
                raise e
            finally:
                if throw_exception:
                    result = args[1]
                    self.__call_enable_mirror_output(result)
                    if self.is_need_to_restore_stdout(hook):
                        self.__call_restore_stdout(result)
        return reslist

    def __call_enable_mirror_output(self, result):
        """ self._mirrorOutput 正在某些方法才设置为True，启动输入到标准输入，为False时，不会输出到标准输出"""

        enable_mirror_output = getattr(result, "enable_mirror_output", None)
        if enable_mirror_output and callable(enable_mirror_output):
            enable_mirror_output()

    def __call_restore_stdout(self, result):

        restore_stdout = getattr(result, "restore_stdout", None)
        if restore_stdout and callable(restore_stdout):
            restore_stdout()


hook_manager = HOOK_MANAGER = HookManager()


def wrapper(runstage, *, runpolicy=RunPolicy.BEFORE, priority=49, name=None, options={}):
    """钩子装饰器，包装函数为钩子

    Args:
        runstage: 钩子运行阶段，see :py:class:`RunStage`
        runpolicy: 钩子运行策略，see :py:class:`RunPolicy`
        priority: 钩子运行优先级
        name: 钩子名称
        options: 钩子额外属性

    """
    def decorator(func):
        hook = Hook(func, runstage, runpolicy=runpolicy,
                    priority=priority, name=name, options=options)
        functools.wraps(func)(hook)
        hook_manager.add_hook(hook)
        return hook
    return decorator


def host(runstage, **options):
    """指定宿主函数，并挂载符合条件的钩子，宿主函数运行时，就会根据相应的策略运行挂载的钩子函数（Specify the host function and mount hooks that meet the criteria. When the host function runs, the mounted hook function will be executed according to the corresponding strategy）

    Args:
        runstage: 运行阶段，指明挂载哪个运行阶段的钩子到宿主函数运行
        options: 额外参数，支持以下参数：
            - before: 字典，作用于runpolicy=RunPolicy.BEFORE的所有钩子，键值如下：<br>
                `sort_key` - 排序函数，同内置方法sorted 的key参数 <br>
                `sort_reverse` - 同内置方法sorted 的reverse参数，True -> 降序，False -> 升序 <br>
                `filter_func` - 过滤函数，同内置方法filter的function参数 <br>
            - after: 字典，作用于runpolicy=RunPolicy.AFTER的所有钩子，键值如下：<br>
                `sort_key` - 排序函数，同内置方法sorted 的key参数 <br>
                `sort_reverse` - 同内置方法sorted 的reverse参数，True -> 降序，False -> 升序 <br>
                `filter_func` - 过滤函数，同内置方法filter的function参数 <br>
    """
    def decorator(host_func):
        @functools.wraps(host_func)
        def inner(*args, **kwargs):
            hook_args = [settings]
            hook_args.extend([o for o in args])
            hook_kwargs = kwargs
            hm = HOOK_MANAGER
            before_opts = {k: v for k, v in options.get("before", {}).items() if k != "runpolicy"}
            after_opts = {k: v for k, v in options.get("after", {}).items() if k != "runpolicy"}
            hm.run(host_func, hook_args, hook_kwargs,
                   runstage, runpolicy=RunPolicy.BEFORE, **before_opts)
            res = host_func(*args, **kwargs)
            hm.run(host_func, hook_args, hook_kwargs,
                   runstage, runpolicy=RunPolicy.AFTER, **after_opts)
            return res
        return inner
    return decorator
