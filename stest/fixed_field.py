#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author: 思文伟
@Date: 2021/11/15 13:53:35
'''

from .utils.attrs_manager import AttributeManager
from .utils.attrs_marker import Const


class FixedField(AttributeManager):

    STEST_TESTCASE_START_TIME = Const(
        'start_time_of_stest_execution_testcase', 'testcase 实例中记录用例开始执行时间(datetime.datetime.now())的属性名')

    STEST_START_PERF_COUNTER = Const(
        'stest_start_perf_counter', 'testcase 实例中记录用例开始执行时间的一个性能计时(time.perf_counter())的属性名')

    STEST_FINISH_PERF_COUNTER = Const(
        'stest_finish_perf_counter', 'testcase 实例中记录用例执行完成时的一个性能计时(time.perf_counter())的属性名')

    STEST_TESTCASE_EXEC_NUMBER = Const(
        'stest_testcase_exec_number', 'testcase 实例中记录用例执行顺序编号的属性名')
