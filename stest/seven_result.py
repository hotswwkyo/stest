#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author: 思文伟
@Date: 2021/09/15
'''
import time
from unittest.runner import TextTestResult

from .const import Const


class SevenTestResult(TextTestResult):
    def __init__(self, stream, descriptions, verbosity, depend_manager=None):
        super().__init__(stream, descriptions, verbosity)
        self.successes = []
        self.depend_manager = depend_manager

    def startTest(self, test):

        stime = time.perf_counter()
        setattr(test, Const.STEST_START_TIME, stime)
        return super().startTest(test)

    def stopTest(self, test):

        rv = super().stopTest(test)
        ftime = time.perf_counter()
        setattr(test, Const.STEST_FINISH_TIME, ftime)
        return rv

    def addSuccess(self, test):

        return_value = super().addSuccess(test)
        self.successes.append(test)
        return return_value

    def getDescription(self, test):

        short_desc = test.shortDescription()
        if self.descriptions and short_desc:
            return '\n'.join((str(test), short_desc))
        else:
            return str(test)
