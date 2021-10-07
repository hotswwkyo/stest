#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author: 思文伟
@Date: 2021/04/22 18:12:55
'''


class UnittestHelperError(Exception):
    pass


class AttributeMarkerException(UnittestHelperError):
    pass


class ConstAttributeException(UnittestHelperError):
    pass
