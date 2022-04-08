#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author: 思文伟
@Date: 2021/09/17
'''

from unittest.loader import TestLoader
from .abstract_testcase import AbstractTestCase


class SevenTestLoader(TestLoader):

    # 参数命名空间
    args_namespace = None

    def loadTestsFromTestCase(self, testCaseClass):
        if issubclass(testCaseClass, AbstractTestCase):
            loaded_suite = self.suiteClass(testCaseClass.collect_testcases(getattr(self.args_namespace, "settings_file", None)))
        else:
            loaded_suite = super().loadTestsFromTestCase(testCaseClass)
        return loaded_suite
