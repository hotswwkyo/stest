#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author: 思文伟
@Date: 2021/11/15 13:53:35
'''

from .attrs_manager import AttributeManager
from .attrs_marker import ConstAttributeMarker


class Const(AttributeManager):

    STEST_START_TIME = ConstAttributeMarker('stest_start_time', 'testcase 实例中记录用例开始执行是的一个时间点(time.perf_counter())的属性名')

    STEST_FINISH_TIME = ConstAttributeMarker('stest_finish_time', 'testcase 实例中记录用例执行完成时的一个时间点(time.perf_counter())的属性名')
