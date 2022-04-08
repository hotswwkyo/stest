#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author: 思文伟
'''

import os
import inspect
import functools
import collections.abc as collections

from ..conf import settings as SETTINGS
from .abstract_data_provider import AbsractDataProvider
from .seven_data_provider import SevenDataProvider


class Test(object):
    """将方法标记为测试方法

    Args:
        settings: 设置项, 键定义如下
            author: 用例编写者
            editors: 修改者列表
            dname: 用于给用例起一个用于设置依赖的名称
            depends: 用于设置用例依赖，是一个用例依赖列表
            groups: 方法所属的组的列表
            enabled: 是否启用执行该测试方法
            priority: 测试方法的执行优先级，数值越小执行越靠前
            alway_run: 如果设置为True，不管依赖它所依赖的其他用例结果如何都始终运行，为False时，则它所依赖的其他用例不成功，就不会执行，默认值为False
            description: 测试用例名称
            data_provider: 测试方法的参数化数据提供者，AbsractDataProvider的子类或者一个可调用的对象，返回数据集列表
            测试方法只有一个参数化时，data_provider 返回值是 一维列表，如:
                def ia_data_provider(testclass, testmethod, *args, **kwargs):
                    return [1,2,3,4,5]
                @testcase(priority=1, enabled=True, data_provider=ia_data_provider, author='思文伟', description='整数加法测试01')
                def integer_addition_01(self, testdata):
                    print(testdata)

            测试方法有多个参数化时，data_provider 返回值是 二维列表，如:
                def ia_data_provider(testclass, testmethod, *args, **kwargs):
                    return [[1,2],[3,4],[5,6]]
                @testcase(priority=1, enabled=True, data_provider=ia_data_provider, author='思文伟', description='整数加法测试01')
                def integer_addition_01(self, testdata01, testdata_02):
                    print(testdata01)
                    print(testdata_02)

            data_provider_args: 数据提供者变长位置参数(args)
            data_provider_kwargs: 数据提供者变长关键字参数(kwargs)
            screenshot: 测试失败是否截图，如果不传该参数，则取全局配置的设置
            attach_screenshot_to_report: 是否附加测试失败的截图到测试报告中，如果不传该参数，则取全局配置的设置
            last_modifyied_by: 最后修改者
            last_modified_time: 最后一次修改的时间
            enable_default_data_provider: 是否使用内置数据提供者(SevenDataProvider)，未设置data_provider，且该值为True 才会使用内置数据提供者(SevenDataProvider)
    """

    # 添加到测试方法的属性名
    TEST_MARKER = 'test_settings'  # 属性值是一个字典
    COLLECT_TEST_DATASETS = 'collect_test_datasets'  # 一个函数，搜集该方法的参数化测试数据
    ORIGINAL_TEST_METHOD_ARGSPEC = 'original_test_method_argspec'  # inspect.getfullargspec(original_test_method)

    # TEST_MARKER键名
    AUTHOR = 'author'
    DNAME = 'dname'  # 该键名用于给用例起一个用于设置依赖的名称
    DEPENDS = 'depends'  # 该键名用于设置用例依赖，是一个用例依赖列表
    EDITORS = 'editors'
    GROUPS = 'groups'
    ENABLED = 'enabled'
    PRIORITY = 'priority'
    ALWAY_RUN = 'alway_run'
    TEST_CLASS = 'test_class'
    TEST_METHOD = 'test_method'
    TEST_DATASETS = 'test_datasets'
    DESCRIPTION = 'description'
    DATA_PROVIDER = 'data_provider'
    DATA_PROVIDER_ARGS = 'data_provider_args'
    DATA_PROVIDER_KWARGS = 'data_provider_kwargs'
    LAST_MODIFYIED_BY = 'last_modifyied_by'
    LAST_MODIFYIED_TIME = 'last_modified_time'
    SCREENSHOT = "screenshot"
    ATTACH_SCREENSHOT_TO_REPORT = "attach_screenshot_to_report"
    ENABLE_DEFAULT_DATA_PROVIDER = 'enable_default_data_provider'

    _FINAL_ENABLE_DEFAULT_DATA_PROVIDER = '_final_enable_default_data_provider'

    DEFAULT_DATA_PROVIDER = SevenDataProvider
    DEFAULT_DATA_PROVIDER_INIT_KWARGS = {
        SevenDataProvider.PARAM_DATA_FILE_NAME: None,
        SevenDataProvider.PARAM_DATA_FILE_DIR_PATH: None,
        SevenDataProvider.PARAM_SHEET_NAME_OR_INDEX: 0,
    }

    # 默认配置
    DEFAULT_SETTTINGS = {
        GROUPS: [],
        DNAME: "",
        DEPENDS: [],
        ENABLED: True,
        PRIORITY: 1,
        ALWAY_RUN: False,
        TEST_CLASS: None,  # 该值由该类自动设置，不需要用户设置(The value are automatically seted by this class, and do not need to seted by user)
        TEST_METHOD: None,  # 该值由该类自动设置，不需要用户设置(The value are automatically seted by this class, and do not need to seted by user)
        DESCRIPTION: '',
        TEST_DATASETS: [],  # 该值由该类自动设置，不需要用户设置(The value are automatically seted by this class, and do not need to seted by user)
        DATA_PROVIDER: None,
        DATA_PROVIDER_ARGS: (),
        DATA_PROVIDER_KWARGS: {},
        AUTHOR: '',
        EDITORS: [],
        LAST_MODIFYIED_BY: '',
        LAST_MODIFYIED_TIME: '',
        ENABLE_DEFAULT_DATA_PROVIDER: True,
        _FINAL_ENABLE_DEFAULT_DATA_PROVIDER: False,  # 内置标志位，用于判断最终使用的是默认的data provider 还是调用者提供的，该值由该类自动设置，不需要用户设置
    }

    def __init__(self, **settings):
        self.settings = {k: v for k, v in self.DEFAULT_SETTTINGS.items()}
        settings.pop(self.TEST_CLASS, None)
        settings.pop(self.TEST_METHOD, None)
        settings.pop(self.TEST_DATASETS, None)
        settings.pop(self._FINAL_ENABLE_DEFAULT_DATA_PROVIDER, None)
        self.settings.update(settings)

        self.enable_parametrize = False

        # 未设置data_provider同时设置enable_default_data_provider = True,才会启用默认的数据提供者
        if self.settings.get(self.ENABLE_DEFAULT_DATA_PROVIDER) and (not self.settings.get(self.DATA_PROVIDER, None)):
            self.settings[self.DATA_PROVIDER] = self.DEFAULT_DATA_PROVIDER
            self.settings[self._FINAL_ENABLE_DEFAULT_DATA_PROVIDER] = True

    def get_testclass_file_dirpath(self, testclass):

        module = inspect.getmodule(testclass)
        filepath = os.path.abspath(module.__file__)
        dirpath = os.path.dirname(filepath)
        return dirpath

    def get_testmethod_file_dirpath(self, testmethod):
        """获取测试方法所在模块的目录路径

        Args:
            testmethod: 测试方法对象
        """

        module = inspect.getmodule(testmethod)
        filepath = os.path.abspath(module.__file__)
        dirpath = os.path.dirname(filepath)
        return dirpath

    def collect_test_datasets(self, testclass, testmethod):
        """调用参数化数据提供者，获取测试方法的参数化测试数据集

        Args:
            testclass: 被装饰的测试方法所在的测试类
            testmethod: 被装饰的测试方法
        Returns: 返回测试数据集，一个列表，每一个元素是该测试方法每次运行的测试数据
        """

        self.settings[self.TEST_CLASS] = testclass
        self.settings[self.TEST_METHOD] = testmethod
        data_provider = self.settings[self.DATA_PROVIDER]

        if not self.enable_parametrize:
            return
        if data_provider is None:
            return self.settings[self.TEST_DATASETS]

        if inspect.isclass(data_provider) and issubclass(data_provider, AbsractDataProvider):
            if issubclass(data_provider, SevenDataProvider) or data_provider == SevenDataProvider:
                kwargs = {k: v for k, v in self.DEFAULT_DATA_PROVIDER_INIT_KWARGS.items()}
                dp_kwargs = self.settings[self.DATA_PROVIDER_KWARGS]
                for k in kwargs.keys():
                    if k in dp_kwargs:
                        kwargs[k] = dp_kwargs[k]
                dp_kwargs.update(kwargs)

                # 如果没有设置测试数据文件所在的目录路径，则到全局配置去找
                # 全局配置里，也没有设置，则自动获取测试方法所在的模块的目录作为测试数据文件的查找目录
                if not dp_kwargs.get(SevenDataProvider.PARAM_DATA_FILE_DIR_PATH, None):
                    if SETTINGS.SEVEN_DATA_PROVIDER_DATA_FILE_DIR:
                        dp_kwargs[SevenDataProvider.PARAM_DATA_FILE_DIR_PATH] = SETTINGS.SEVEN_DATA_PROVIDER_DATA_FILE_DIR
                    else:
                        dp_kwargs[SevenDataProvider.PARAM_DATA_FILE_DIR_PATH] = self.get_testmethod_file_dirpath(testmethod)

                # 未提供测试数据文件名称则以测试方法所属的类的类名作为测试数据文件名称
                if not dp_kwargs.get(SevenDataProvider.PARAM_DATA_FILE_NAME, None):
                    dp_kwargs[SevenDataProvider.PARAM_DATA_FILE_NAME] = testclass.__name__

                self.settings[self.DATA_PROVIDER_KWARGS] = dp_kwargs
                datasets = data_provider().get_testdatas(testclass.__name__, testmethod.__name__, *self.settings[self.DATA_PROVIDER_ARGS], **self.settings[self.DATA_PROVIDER_KWARGS])
            else:
                datasets = data_provider().get_testdatas(testclass.__name__, testmethod.__name__, *self.settings[self.DATA_PROVIDER_ARGS], **self.settings[self.DATA_PROVIDER_KWARGS])

        elif self._validate_data_provider(data_provider):
            datasets = data_provider(testclass.__name__, testmethod.__name__, *self.settings[self.DATA_PROVIDER_ARGS], **self.settings[self.DATA_PROVIDER_KWARGS])
        else:
            raise TypeError('无效data_provider: {}'.format(data_provider))

        if not self._validate_datesets(datasets):
            # 返回的数据集必须是列表或者元祖类型, 实际返回的类型是
            raise TypeError('{}The returned data set must be a list or tuple type. The actual returned type is: {}'.format(data_provider, type(datasets)))

        self.settings[self.TEST_DATASETS] = datasets
        return datasets

    def _validate_data_provider(self, data_provider):

        return inspect.ismethod(data_provider) or inspect.isfunction(data_provider) or isinstance(data_provider, collections.Callable)

    def _validate_datesets(self, datasets):

        return isinstance(datasets, (list, tuple))

    # def test_datasets_filedir_path(self, module='__main__'):

    # if isinstance(module, str):
    # self.module = __import__(module)
    # for part in module.split('.')[1:]:
    # self.module = getattr(self.module, part)
    # else:
    # self.module = module
    # file_dir_path = os.path.dirname(os.path.abspath(self.module.__file__))

    def __call__(self, func):

        func_name = func.__name__
        argspec = inspect.getfullargspec(func)
        setattr(func, self.TEST_MARKER, self.settings)
        setattr(func, self.COLLECT_TEST_DATASETS, self.collect_test_datasets)
        setattr(func, self.ORIGINAL_TEST_METHOD_ARGSPEC, argspec)

        # 测试方法只有一个位置参数self,则不会执行参数化
        if len(argspec.args) <= 1:
            self.enable_parametrize = False
        else:
            self.enable_parametrize = True

        @functools.wraps(func)
        def _call(*args, **kwargs):

            instance = args[0] if len(args) > 0 else None
            method_instance = instance if instance and self.is_method_instance(instance, func_name) else None
            new_args = list(args)

            # argspec.args 位置参数
            pos_args_len = len(argspec.args)

            # argspec.varargs 变长位置参数,定义有则返回定义的名称否则None
            # 如 def connet(ip, *other) --> 返回other
            pos_varargs_len = 1 if argspec.varargs else 0

            insert_data = False
            insert_pos_index = 0

            if pos_varargs_len <= 0:
                if pos_args_len <= 0:
                    insert_data = False
                elif pos_args_len < 2:
                    if method_instance:
                        insert_data = False
                    else:
                        insert_data = True
                        insert_pos_index = 0
                else:
                    insert_data = True
                    if method_instance:
                        insert_pos_index = 1
                    else:
                        insert_pos_index = 0
            else:
                insert_data = True
                if method_instance:
                    insert_pos_index = 1
                else:
                    insert_pos_index = 0

            if insert_data:
                test_datasets = self.settings[self.TEST_DATASETS]
                runtime_testdatas, found, msg = self._get_runtime_testdatas(test_datasets, method_instance, func_name)

                if self.settings[self.DATA_PROVIDER]:
                    if found:
                        # 计算测试方法需要传入的参数个数
                        need_params_total = pos_args_len
                        # 如果是方法实例, 参数总数-1 如 def test_plus(self, testdata) --> 需要传入的参数是 testdata  就是1个
                        if method_instance:
                            need_params_total = need_params_total - 1

                        if need_params_total == 1:
                            new_args.insert(insert_pos_index, runtime_testdatas)
                        elif need_params_total > 1:
                            if isinstance(runtime_testdatas, (list, tuple)):
                                actual_params_total = len(runtime_testdatas)
                            else:
                                actual_params_total = 1

                            # 实际等到的参数个数大于等于需要的参数个数,
                            # 则传入需要位置索引一样的参数值, 多余的丢弃
                            # 实际等到的参数个数小于需要的参数个数，则报错
                            if actual_params_total >= need_params_total:
                                for i in range(need_params_total):
                                    new_args.insert(insert_pos_index + i, runtime_testdatas[i])
                            else:
                                raise TypeError('{}() need {} positional argument, but only {} were given'.format(func_name, need_params_total, actual_params_total))
                        else:
                            pass
                    else:
                        raise ValueError(msg)
            if method_instance:
                method_instance.set_testcase_runtime_datas(new_args, kwargs)
            return func(*tuple(new_args), **kwargs)

        return _call

    def _get_runtime_testdatas(self, test_datasets, test_method_instance, test_method_name):
        """从方法的测试数据集中获取本次测试方法运行时的测试数据

        Args:
            test_datasets: 测试方法的测试数据集，一个列表，每一个元素是该测试方法每次运行的测试数据
            test_method_instance: 测试方法所属的测试用例对象（即方法所在的测试类的实例化）
            test_method_name: 测试方法名称

        Returns: 返回一个3个元素的元祖，第一个是本次测试方法运行时的测试数据，第二个是查找测试数据的结果(False - 未找到, True - 找到)，第三是相关信息
        """

        runtime_datas = None
        found = False
        msg = ""
        if test_method_instance:
            sn = test_method_instance._serial_number
            for i, v in enumerate(test_datasets):
                if (i + 1) == sn:
                    runtime_datas = v
                    found = True
                    break
            if not found:
                msg = 'The parameterized test data for this method({}) was not found'.format(test_method_instance.id())
        else:
            pass
        return (runtime_datas, found, msg)

    def is_method_instance(self, instance, method_name):
        return inspect.ismethod(getattr(instance, method_name))

    @classmethod
    def func_has_test_marker(cls, obj):
        """判断对象是否有测试标志"""

        if inspect.ismethod(obj) or inspect.isfunction(obj):
            has_marker = getattr(obj, cls.TEST_MARKER, None)
            if has_marker:
                return True
            closure = getattr(obj, '__closure__', None)
            c_func = None
            if closure:
                for c in closure:
                    contents = c.cell_contents
                    if inspect.ismethod(contents) or inspect.isfunction(contents):
                        c_func = contents
                        break
            if c_func and getattr(c_func, cls.TEST_MARKER, None):
                return True
        else:
            return False

    @classmethod
    def get_test_marker(cls, test_func_obj, key=None, default_value=None):
        """返回测试标记配置或者配置中的某个键值

        Args:
            test_func_obj: 测试方法对象
            key: 要获取测试标记配置项的键名，如果不设置则返回整个测试标记配置
            default_value: 键值项不存在时的默认返回值
        Returns: 返回整个测试标记配置 或配置中指定项的值
        """

        test_marker = getattr(test_func_obj, cls.TEST_MARKER, {})
        if key and isinstance(key, str):
            return test_marker.get(key, default_value)
        else:
            return test_marker
