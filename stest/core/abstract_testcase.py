#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author: 思文伟
@Date: 2021/03/30 11:21:57
'''
import os
import sys
import time
import inspect
import unittest
from ..conf import settings
from ..conf import SettingsFileFinder
from ..conf import image_show
from ..utils.sutils import strclass
from .test_wrapper import Test


class AbstractTestCase(unittest.TestCase):
    """为测试类添加自动收集和自行测试用例的方法"""

    def __init__(self, methodName='runTest', serial_number=1):
        super(AbstractTestCase, self).__init__(methodName)
        self._serial_number = serial_number
        self.__testcase_runtime_datas = dict(args=[], kwargs={})

    @classmethod
    def sleep(cls, seconds):

        time.sleep(seconds)
        return cls

    def strclass(self):
        return strclass(self.__class__)

    @property
    def serial_number(self):
        return self._serial_number

    @property
    def test_method_obj(self):
        return getattr(self, self._testMethodName)

    @property
    def real_test_method_name(self):
        return self._testMethodName

    @property
    def test_method_settings(self):

        return Test.get_test_marker(self.test_method_obj)

    @property
    def _test_method_name(self):

        return "{}_{}".format(self._testMethodName, self._serial_number)

    def set_testcase_runtime_datas(self, args=[], kwargs={}):

        self.__testcase_runtime_datas["args"] = args
        self.__testcase_runtime_datas["kwargs"] = kwargs

    def get_testcase_runtime_datas(self):
        return self.__testcase_runtime_datas

    def shortDescription(self):

        name = Test.get_test_marker(self.test_method_obj, key=Test.NAME, default_value=None)
        doc = self.test_method_obj.__doc__
        first_line = doc.strip().split("\n")[0].strip() if doc else None
        return name or first_line

    def id(self):
        return "{}.{}".format(strclass(self.__class__), self._test_method_name)

    def __eq__(self, other):
        if type(self) is not type(other):
            return NotImplemented

        return self._test_method_name == other._test_method_name

    def __hash__(self):
        return hash((type(self), self._test_method_name))

    def __str__(self):
        return "%s (%s)" % (self._test_method_name, strclass(self.__class__))

    def __repr__(self):
        return "<%s testMethod=%s>" % \
               (strclass(self.__class__), self._test_method_name)

    def run(self, result=None):

        if result is not None:
            dm = getattr(result, 'depend_manager', None)
            # 如果有设置依赖管理器，则运行依赖管理器
            if dm is not None:

                addFailure = getattr(result, 'mark_test_failure', None)

                # 检查是否有无法解析的依赖
                missing = dm.get_missing(self)
                miss_msg = '{} depends on {}, which was not found'.format(
                    self.id(), ", ".join(missing))
                if missing:
                    try:
                        raise self.failureException(miss_msg)
                    except self.failureException:
                        exc_info = sys.exc_info()
                        if addFailure:
                            addFailure(self, exc_info)
                    return result

                # 检查是否存在循环依赖
                clinks = dm.get_cyclic_links(self)
                printables = []
                for clink in clinks:
                    printable = '------>'.join(clink)
                    printables.append(printable)
                if clinks:
                    try:
                        raise self.failureException(
                            '{} circular dependency: {}'.format(self.id(), ", ".join(printables)))
                    except self.failureException:
                        exc_info = sys.exc_info()
                        if addFailure:
                            addFailure(self, exc_info)
                    return result

                # alway_run 为True，则不管该用例所依赖的其他用例是否成功都会执行该用例
                alway_run = self.test_method_settings.get(Test.ALWAY_RUN, False)
                if alway_run:
                    return super().run(result=result)

                # 检查用例所依赖的其他测试用例是否测试通过，如果不通过则不执行该用例并标记结果为失败
                tresult, msglist = dm.dependent_test_is_pass(self)
                if not tresult:
                    try:
                        raise self.failureException(
                            '{} depends on: {}'.format(self.id(), '\n'.join(msglist)))
                    except self.failureException:
                        exc_info = sys.exc_info()
                        if addFailure:
                            addFailure(self, exc_info)
                    return result
        return super().run(result=result)

    def show2html(self, *, base64data="", filepath="", name="", **other_info):
        """显示截图到html测试报告中

        Parameters
        ----------
        base64data : base64编码的截图文件数据，如果同时提供filepath，则有限使用filepath，忽略该参数
        filepath : 截图文件完整路径
        name : 在html报告中显示的名称
        other_info : 其它信息
        """
        return image_show.show2html(self, base64data=base64data, filepath=filepath, name=name, other_info=other_info)

    @classmethod
    def collect_testcases(cls, args_namespace=None, print_tips=False):
        # 1. 性能优化：使用 inspect.isroutine 替代多次逻辑或判断
        members = [
            obj_val for obj_val in cls.__dict__.values()
            if inspect.isroutine(obj_val)
        ]

        # 2. 可读性优化：使用有意义的变量名，合并过滤与排序逻辑
        enabled_test_funcs = [
            func for func in members
            if Test.get_test_marker(func, key=Test.ENABLED, default_value=False)
        ]
        enabled_test_funcs.sort(
            key=lambda func: Test.get_test_marker(func, key=Test.PRIORITY, default_value=1)
        )

        # 3. 性能优化：使用集合进行交集判断，替代低效的双重循环
        groups = getattr(args_namespace, 'groups', None)
        if groups and isinstance(groups, (list, tuple, set)):
            target_groups = set(groups)
            enabled_test_funcs = [
                func for func in enabled_test_funcs
                if target_groups.intersection(
                    Test.get_test_marker(func, key=Test.GROUPS, default_value=[])
                )
            ]

        settings_file = getattr(args_namespace, 'settings_file', None)
        testcases = []

        for test_func in enabled_test_funcs:
            # 4. 逻辑/性能优化：将配置文件加载逻辑移出循环，避免重复加载和冗余判断
            if not settings.is_loaded:
                finder = SettingsFileFinder()
                start_path = filepath = None

                if settings_file:
                    # 5. 安全与可读性优化：使用 os.path 抽象方法替代 os.path.exists，合并重复的异常抛出
                    if os.path.isfile(settings_file):
                        start_path = os.path.dirname(settings_file)
                        filepath = settings_file
                    elif os.path.isdir(settings_file):
                        start_path = settings_file
                        filepath = finder.find_settings_file_from_start_dir(settings_file)
                    else:
                        raise FileNotFoundError(
                            f"No such file or directory: '{settings_file}'"
                        )
                else:
                    start_path, filepath = finder.find_settings_file_by_testcase_class(cls)

                if filepath:
                    settings.load_configure_from_file(filepath)
                    tips = f'加载的配置文件是：{filepath}'
                else:
                    tips = f'在该目录（{start_path}）及其子孙目录中没有找到配置文件: {finder.settings_file_name}'

                if print_tips:
                    print(tips)

            # 6. 逻辑优化：提取数据集获取逻辑，简化条件判断
            test_func.collect_test_datasets(cls, test_func)
            datasets = test_func.test_settings.get(Test.TEST_DATASETS, [])

            if datasets:
                # 7. 性能优化：使用列表推导式替代循环中的 append
                testcases.extend(
                    cls(test_func.__name__, i + 1) for i in range(len(datasets))
                )
            else:
                testcases.append(cls(test_func.__name__))

        return testcases

    @classmethod
    def build_self_suite(cls, args_namespace=None, print_tips=False):

        suite = unittest.TestSuite()
        suite.addTests(cls.collect_testcases(args_namespace, print_tips))
        return suite

    @classmethod
    def run_test(cls, **kwargs):

        from stest.main import main
        task = main(**kwargs)
        return task.result
