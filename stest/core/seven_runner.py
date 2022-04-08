#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author: 思文伟
@Date: 2021/09/17
'''
from unittest.suite import TestSuite
from unittest.runner import TextTestRunner
from ..const import Const
from .depends import DependsManager
from .seven_result import SevenTestResult


class SevenTestRunner(TextTestRunner):

    resultclass = SevenTestResult

    def __init__(self, stream=None, descriptions=True, verbosity=1, failfast=False, buffer=False, resultclass=None, warnings=None, *, tb_locals=False, depend_manager=None):
        super().__init__(stream=stream, descriptions=descriptions, verbosity=verbosity, failfast=failfast, buffer=buffer, resultclass=resultclass, warnings=warnings, tb_locals=tb_locals)
        self.depend_manager = DependsManager() if depend_manager is None else depend_manager

    def _makeResult(self):
        results = super()._makeResult()
        self.depend_manager.results = results
        results.depend_manager = self.depend_manager
        return results

    def run(self, test):
        def _issuite(tc):
            "A crude way to tell apart testcases and suites with duck-typing"
            try:
                iter(tc)
            except TypeError:
                return False
            return True

        def all_in_one(tc):

            alltests = []
            if _issuite(tc):
                for one in tc:
                    if not _issuite(one):
                        alltests.append(one)
                    else:
                        alltests.extend(all_in_one(one))
            else:
                alltests.append(tc)
            return alltests

        def set_exec_number_to_testcase(testcases):

            for i, t in enumerate(testcases):
                setattr(t, Const.STEST_TESTCASE_EXEC_NUMBER, i + 1)

        testlist = all_in_one(test)
        self.depend_manager.tests = testlist
        suite = self.depend_manager.sorted_tests(suiteclass=TestSuite)
        set_exec_number_to_testcase(suite)
        return super().run(suite)
