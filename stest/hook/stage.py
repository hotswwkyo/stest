#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from stest.utils.attrs_marker import Const
from stest.utils.attrs_manager import unique
from stest.utils.attrs_manager import AttributeManager


@unique
class RunStage(AttributeManager):
    """运行阶段标记 - 值应是唯一的"""

    startTestRun = Const(1, description="Called once before any tests are executed.")

    startTest = Const(
        2, description="Called when the given test is about to be run.", restore_stdout=True)

    stopTest = Const(3, description="Called when the given test has been run.",
                     restore_stdout=True)

    stopTestRun = Const(4, description="Called once after all tests are executed.")

    addSuccess = Const(5, description="Called when a test has completed successfully")

    addError = Const(
        6, description="Called when an error has occurred. 'err' is a tuple of values as returned by sys.exc_info().")

    addFailure = Const(
        7, description="Called when an error has occurred. 'err' is a tuple of values as returned by sys.exc_info().")

    addSkip = Const(8, description="Called when a test is skipped.")

    addExpectedFailure = Const(9, description="Called when an expected failure/error occurred.")

    addUnexpectedSuccess = Const(
        10, description="Called when a test was expected to fail, but succeed.")

    @classmethod
    def newstage(cls, field, value, mark="", throw_exception=True):

        fields = cls._CLASS_ATTRIBUTES
        if field not in fields and value not in [m.value for m in fields.values()]:
            setattr(cls, field, value)
            cls._CLASS_ATTRIBUTES[field] = Const(value, description=mark)
            return True
        else:
            exists = ", ".join(["{}={}".format(k, v.value) for k, v in fields.items()])
            err_msg = "attribute: {} or value: {} is same as exists ones in {}: {}".format(
                field, value, cls, exists)

            if throw_exception:
                raise ValueError(err_msg)
            else:
                return False
