#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author: 思文伟
@Date: 2021/09/15
'''
import sys
import time
import datetime
import traceback
from unittest.runner import TextTestResult

from ..fixed_field import FixedField
from ..conf import settings
from .test_wrapper import Test
from ..utils.screenshot_capturer import ScreenshotCapturer
from ..hook import host
from ..hook import RunStage


class SevenTestResult(TextTestResult):
    def __init__(self, stream, descriptions, verbosity, depend_manager=None):
        super().__init__(stream, descriptions, verbosity)
        self.successes = []
        self.screenshots = {}  # 存放测试失败截图的base64数据
        self.depend_manager = depend_manager

    def _screenshot(self, test):

        try:
            DRIVER_MANAGER = getattr(settings, "DRIVER_MANAGER", None)
            driver = DRIVER_MANAGER.driver
        except Exception:
            driver = None

        test_method_settings = getattr(test, 'test_method_settings', {})
        screenshot = test_method_settings.get(
            Test.SCREENSHOT, getattr(settings, Test.SCREENSHOT.upper(), False))
        attach = test_method_settings.get(Test.ATTACH_SCREENSHOT_TO_REPORT, getattr(
            settings, Test.ATTACH_SCREENSHOT_TO_REPORT.upper(), False))
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
            self.screenshots[test] = {Test.SCREENSHOT: screenshot, Test.ATTACH_SCREENSHOT_TO_REPORT: attach,
                                      'result': success, 'base64data': data, 'message': message}

    @host(RunStage.startTestRun)
    def startTestRun(self) -> None:
        return super().startTestRun()

    @host(RunStage.startTest)
    def startTest(self, test):
        starttime = datetime.datetime.now()
        scounter = time.perf_counter()
        setattr(test, FixedField.STEST_START_PERF_COUNTER, scounter)
        setattr(test, FixedField.STEST_TESTCASE_START_TIME, starttime)
        return super().startTest(test)

    @host(RunStage.stopTest)
    def stopTest(self, test):
        rv = super().stopTest(test)
        fcounter = time.perf_counter()
        setattr(test, FixedField.STEST_FINISH_PERF_COUNTER, fcounter)
        return rv

    @host(RunStage.stopTestRun)
    def stopTestRun(self) -> None:
        return super().stopTestRun()

    @host(RunStage.addSuccess)
    def addSuccess(self, test):
        return_value = super().addSuccess(test)
        self.successes.append((test, self._get_output_message()))
        self._mirrorOutput = True
        return return_value

    @host(RunStage.addError)
    def addError(self, test, err):
        rv = super().addError(test, err)
        self._screenshot(test)
        return rv

    @host(RunStage.addFailure)
    def addFailure(self, test, err):
        rv = super().addFailure(test, err)
        self._screenshot(test)
        return rv

    @host(RunStage.addSkip)
    def addSkip(self, test, reason):
        return super().addSkip(test, reason)

    @host(RunStage.addExpectedFailure)
    def addExpectedFailure(self, test, err):
        return super().addExpectedFailure(test, err)

    @host(RunStage.addUnexpectedSuccess)
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

    def _get_output_message(self):

        msgLines = []
        STDOUT_LINE = '\nStdout:\n%s'
        STDERR_LINE = '\nStderr:\n%s'
        if self.buffer:
            output = sys.stdout.getvalue()
            error = sys.stderr.getvalue()
            if output:
                if not output.endswith('\n'):
                    output += '\n'
                msgLines.append(STDOUT_LINE % output)
            if error:
                if not error.endswith('\n'):
                    error += '\n'
                msgLines.append(STDERR_LINE % error)
        return ''.join(msgLines)

    def restore_stdout(self):
        if self.buffer:
            if self._mirrorOutput:
                if self._stdout_buffer is not None:
                    output = self._stdout_buffer.getvalue()
                    if output:
                        if not output.endswith('\n'):
                            output += '\n'
                        self._original_stdout.write(output)
                    if self._original_stdout is not None:
                        sys.stdout = self._original_stdout
                    self._stdout_buffer.seek(0)
                    self._stdout_buffer.truncate()
                if self._stderr_buffer is not None:
                    error = self._stderr_buffer.getvalue()
                    if error:
                        if not error.endswith('\n'):
                            error += '\n'
                        self._original_stderr.write(error)
                    if self._original_stderr is not None:
                        sys.stderr = self._original_stderr
                    self._stderr_buffer.seek(0)
                    self._stderr_buffer.truncate()
                self._mirrorOutput = False

    def enable_mirror_output(self):
        if self.buffer:
            self._mirrorOutput = True
