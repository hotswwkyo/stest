#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author: 思文伟
@Date: 2021/09/16
'''
import copy
import json
from .utils import strclass
from .test_wrapper import Test
from .abstract_testcase import AbstractTestCase
from .attrs_manager import AttributeManager
from .attrs_marker import ConstAttributeMarker


class TestCaseWrapper(AttributeManager):

    SUCCESS = ConstAttributeMarker(0, "通过", alias="通过")
    FAILURE = ConstAttributeMarker(1, "失败", alias="失败")
    ERROR = ConstAttributeMarker(2, "异常", alias="异常")
    BLOCKED = ConstAttributeMarker(3, "阻塞", alias="阻塞")
    SKIPED = ConstAttributeMarker(4, "跳过", alias="skiped")
    XFAILURE = ConstAttributeMarker(5, "预期失败", alias="预期失败")
    XSUCCESS = ConstAttributeMarker(6, "预期失败却成功", alias="unexpected successes")

    def __init__(self, test, id, result_code, message=""):

        self.test = test
        self.id = id
        self.set_result(result_code, message)
        self.is_abstract_testcase = isinstance(self.test, AbstractTestCase)
        # self.is_abstract_testcase = hasattr(self.test, "collect_testcases")

    @property
    def name(self):

        return self.description or self.method_name

    @property
    def method_name(self):

        if self.is_abstract_testcase:
            name = self.test.real_test_method_name
        else:
            name = self.test.id()
        return name

    @property
    def number(self):
        return self.id

    @property
    def testpoint(self):
        if self.is_abstract_testcase:
            return self.test.strclass()
        else:
            try:
                classname = strclass(self.test.__class__)
            except Exception:
                classname = self.test.id()
            return classname

    @property
    def result_name(self):

        markers = self.__class__.const_attrs.values()
        for marker in markers:
            code = marker.value
            if self.__result_code == code:
                return marker.expend_kwargs["alias"]

    @property
    def result_code(self):
        return self.__result_code

    @classmethod
    def result_codes(cls):
        markers = cls.const_attrs.values()
        codes = [marker.value for marker in markers]
        return codes

    @property
    def description(self):

        return self.test.shortDescription() or ''

    @property
    def output_message(self):

        return ''

    @property
    def error_message(self):

        return self.message

    @property
    def testdatas(self):
        args_mapinfo = {}
        kwargs_mapinfo = {}
        if self.is_abstract_testcase:
            spec = getattr(self.test.test_method_obj, Test.ORIGINAL_TEST_METHOD_ARGSPEC)
            runtimedatas = self.test.get_testcase_runtime_datas()
            args = runtimedatas['args']
            kwargs = runtimedatas['kwargs']
            for index, arg_value in enumerate(args):
                try:
                    arg_name = spec.args[index]
                except IndexError:
                    arg_name = ''  # 代表传入了多余的参数
                if arg_value == self.test:
                    continue
                else:
                    args_mapinfo[index] = (arg_name, arg_value)

            kwargs_mapinfo = copy.deepcopy(kwargs)

        return (args_mapinfo, kwargs_mapinfo)

    def __to_str(self, value):

        try:
            fstr = json.dumps(value, ensure_ascii=False, indent=4)
        except Exception:
            fstr = str(value)
        return fstr

    @property
    def printable_testdatas(self):

        args_mapinfo, kwargs_mapinfo = self.testdatas
        printable_args = {}
        printable_kwargs = {}
        for k, v in args_mapinfo.items():
            arg_name, arg_value = v
            printable_args[k] = (arg_name, self.__to_str(arg_value))
        for k, v in kwargs_mapinfo.items():
            printable_kwargs[k] = self.__to_str(v)
        return (printable_args, printable_kwargs)

    def set_result(self, result_code, message=""):

        if result_code not in self.result_codes():
            raise ValueError('The value range of result code is: {}'.format(' | '.join(self.result_codes())))
        self.__result_code = result_code
        self.message = message


class TestResultFormatter(object):
    def __init__(self, test_result):

        self.__test_result = test_result

    @property
    def result(self):
        return self.__test_result

    def _get_belong_project(self):

        return ""

    def to_py_json(self):

        testpoints = []
        for pointname, group_testcases in self._group_by_belong_testpoint():
            results = []
            for tc in group_testcases:
                result = dict(
                    result=dict(code=tc.result_code, name=tc.result_name),
                    id=tc.id,
                    name=tc.name,
                    method_name=tc.method_name,
                    testdatas=tc.printable_testdatas,
                    number=tc.number,
                    description=tc.description,
                    output_message=tc.output_message,
                    error_message=tc.error_message,
                )
                results.append(result)
            testpoint = dict(name=pointname,
                             count=len(group_testcases),
                             pass_count=self.counts(group_testcases, TestCaseWrapper.SUCCESS),
                             fail_count=self.counts(group_testcases, TestCaseWrapper.FAILURE),
                             error_count=self.counts(group_testcases, TestCaseWrapper.ERROR),
                             block_count=self.counts(group_testcases, TestCaseWrapper.BLOCKED),
                             skip_count=self.counts(group_testcases, TestCaseWrapper.SKIPED),
                             xfail_count=self.counts(group_testcases, TestCaseWrapper.XFAILURE),
                             xpass_count=self.counts(group_testcases, TestCaseWrapper.XSUCCESS),
                             testcases=results)
            testpoints.append(testpoint)
        root = dict(project=self._get_belong_project(), testpoints=testpoints)
        return root

    def to_json_string(self):

        return json.dumps(self.to_py_json(), ensure_ascii=False)

    @property
    def testcases(self):

        testcaselist = []
        id = 1
        for test, message in self.result.errors:
            testcaselist.append(TestCaseWrapper(test, id, TestCaseWrapper.ERROR, message=message))
            id = id + 1
        for test, message in self.result.skipped:
            testcaselist.append(TestCaseWrapper(test, id, TestCaseWrapper.SKIPED, message=message))
            id = id + 1

        for test, message in self.result.failures:
            testcaselist.append(TestCaseWrapper(test, id, TestCaseWrapper.FAILURE, message=message))
            id = id + 1

        for test in self.result.successes:
            testcaselist.append(TestCaseWrapper(test, id, TestCaseWrapper.SUCCESS))
            id = id + 1

        for test, message in self.result.expectedFailures:
            testcaselist.append(TestCaseWrapper(test, id, TestCaseWrapper.XFAILURE, message=message))
            id = id + 1

        for test, message in self.result.unexpectedSuccesses:
            testcaselist.append(TestCaseWrapper(test, id, TestCaseWrapper.XSUCCESS))
            id = id + 1
        return testcaselist

    def _get_testpoints(self):

        testpoints = []
        for testcase in self.testcases:
            testpoint = testcase.testpoint
            if testpoint not in testpoints:
                testpoints.append(testpoint)
        return testpoints

    def _group_by_belong_testpoint(self):

        groups = []
        for testpoint in self._get_testpoints():
            group_testcases = []
            for test in self.testcases:
                if testpoint == test.testpoint:
                    group_testcases.append(test)
            groups.append((testpoint, group_testcases))
        return groups

    @classmethod
    def counts(cls, testcases, result_code):

        return len([tc for tc in testcases if tc.result_code == result_code])
