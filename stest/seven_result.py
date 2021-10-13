#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author: 思文伟
@Date: 2021/09/15
'''
from unittest.runner import TextTestResult


class SevenTestResult(TextTestResult):
    def __init__(self, stream, descriptions, verbosity, depend_manager=None):
        super().__init__(stream, descriptions, verbosity)
        self.successes = []
        self.depend_manager = depend_manager

    def startTest(self, test):

        return super().startTest(test)

    def stopTest(self, test):
        return super().stopTest(test)

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
