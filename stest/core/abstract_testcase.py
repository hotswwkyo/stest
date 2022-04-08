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
        name = Test.get_test_marker(self.test_method_obj, key=Test.DESCRIPTION, default_value=None)
        return name or None

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

                addFailure = getattr(result, 'addFailure', None)

                # 检查是否有无法解析的依赖
                missing = dm.get_missing(self)
                miss_msg = '{} depends on {}, which was not found'.format(self.id(), ", ".join(missing))
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
                        raise self.failureException('{} circular dependency: {}'.format(self.id(), ", ".join(printables)))
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
                        raise self.failureException('{} depends on: {}'.format(self.id(), '\n'.join(msglist)))
                    except self.failureException:
                        exc_info = sys.exc_info()
                        if addFailure:
                            addFailure(self, exc_info)
                    return result
        return super().run(result=result)

    @classmethod
    def collect_testcases(cls, settings_file=None, print_tips=False):

        members = [obj_val for obj_key, obj_val in cls.__dict__.items() if inspect.ismethod(obj_val) or inspect.isfunction(obj_val)]
        test_func_list = [member for member in members if Test.func_has_test_marker(member)]
        run_test_func_list = [tf for tf in test_func_list if Test.get_test_marker(tf, key=Test.ENABLED, default_value=False)]
        run_test_func_list.sort(key=lambda tf: Test.get_test_marker(tf, key=Test.PRIORITY, default_value=1))
        testcases = []
        for test_func in run_test_func_list:

            if not settings.is_loaded:
                finder = SettingsFileFinder()
                start_path = filepath = None
                if settings_file:
                    if os.path.exists(settings_file):
                        if os.path.isfile(settings_file):
                            start_path = os.path.dirname(settings_file)
                            filepath = settings_file
                        elif os.path.isdir(settings_file):
                            start_path = settings_file
                            filepath = finder.find_settings_file_from_start_dir(settings_file)
                        else:
                            raise FileNotFoundError("No such file or directory: '{}'".format(settings_file))
                    else:
                        raise FileNotFoundError("No such file or directory: '{}'".format(settings_file))
                else:  # 未指定配置文件查找目录或者配置文件路径，则使用自动查找
                    start_path, filepath = finder.find_settings_file_by_testcase_class(cls)

                if filepath:
                    settings.load_configure_from_file(filepath)
                    tips = '加载的配置文件是：{}'.format(filepath)
                else:
                    tips = '在该目录（{}）及其子孙目录中没有找到配置文件'.format(start_path)
                if print_tips:
                    print(tips)
            test_func.collect_test_datasets(cls, test_func)
            datasets = test_func.test_settings[Test.TEST_DATASETS]
            if (len(datasets) > 0):
                for i, v in enumerate(datasets):
                    testcases.append(cls(test_func.__name__, (i + 1)))
            else:
                testcases.append(cls(test_func.__name__))
        return testcases

    @classmethod
    def build_self_suite(cls):

        suite = unittest.TestSuite()
        suite.addTests(cls.collect_testcases())
        return suite

    @classmethod
    def run_test(cls, **kwargs):

        from stest.main import main
        task = main(**kwargs)
        return task.result
