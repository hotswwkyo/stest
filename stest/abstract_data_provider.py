#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author: 思文伟
'''

from .attrs_manager import AttributeManager


class AbsractDataProvider(AttributeManager):
    def __init__(self):
        super(AbsractDataProvider, self).__init__()

    def get_testdatas(self, test_class_name, test_method_name, *args, **kwargs):
        """当测试方法只有一个参数化时，应返回一维列表，多个参数化时返回二维列表"""

        raise NotImplementedError
