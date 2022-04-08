#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author: 思文伟
@Date: 2021/09/15
'''
import time
import datetime
import traceback
from unittest.runner import TextTestResult

from ..const import Const
from ..conf import settings
from .test_wrapper import Test
from ..dm import DRIVER_MANAGER
from ..utils.screenshot_capturer import ScreenshotCapturer


class SevenTestResult(TextTestResult):
    def __init__(self, stream, descriptions, verbosity, depend_manager=None):
        super().__init__(stream, descriptions, verbosity)
        self.successes = []
        self.screenshots = {}  # 存放测试失败截图的base64数据
        self.depend_manager = depend_manager

    def _screenshot(self, test):

        try:
            driver = DRIVER_MANAGER.driver
        except Exception:
            driver = None

        test_method_settings = getattr(test, 'test_method_settings', {})
        screenshot = test_method_settings.get(Test.SCREENSHOT, getattr(settings, Test.SCREENSHOT.upper(), False))
        attach = test_method_settings.get(Test.ATTACH_SCREENSHOT_TO_REPORT, getattr(settings, Test.ATTACH_SCREENSHOT_TO_REPORT.upper(), False))
        capturerclass = ScreenshotCapturer
        if screenshot:
            message = ''
            try:
                data = capturerclass().screenshot_as_base64(driver)
            except Exception:
                success = False
                message = traceback.format_exc()
                data = ''
            else:
                success = True
            self.screenshots[test] = {Test.SCREENSHOT: screenshot, Test.ATTACH_SCREENSHOT_TO_REPORT: attach, 'result': success, 'base64data': data, 'message': message}

    def startTest(self, test):

        starttime = datetime.datetime.now()
        scounter = time.perf_counter()
        setattr(test, Const.STEST_START_PERF_COUNTER, scounter)
        setattr(test, Const.STEST_TESTCASE_START_TIME, starttime)
        return super().startTest(test)

    def stopTest(self, test):

        rv = super().stopTest(test)
        fcounter = time.perf_counter()
        setattr(test, Const.STEST_FINISH_PERF_COUNTER, fcounter)
        return rv

    def addSuccess(self, test):

        return_value = super().addSuccess(test)
        self.successes.append(test)
        return return_value

    def addError(self, test, err):
        rv = super().addError(test, err)
        self._screenshot(test)
        return rv

    def addFailure(self, test, err):
        rv = super().addFailure(test, err)
        self._screenshot(test)
        return rv

    def addUnexpectedSuccess(self, test):
        rv = super().addUnexpectedSuccess(test)
        self._screenshot(test)
        return rv

    def getDescription(self, test):

        short_desc = test.shortDescription()
        if self.descriptions and short_desc:
            return '\n'.join((str(test), short_desc))
        else:
            return str(test)
