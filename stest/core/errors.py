#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author: 思文伟
@Date: 2021/04/22 18:12:55
'''


class StestException(Exception):
    pass


class ImproperlyConfigured(StestException):
    """stest is somehow improperly configured"""
    pass


class NoOpenDriver(StestException):
    pass


class AttributeMarkerException(StestException):
    pass


class ConstAttributeException(StestException):
    pass


class WindowNotFound(StestException):
    pass


class StestWarning(UserWarning):
    pass


class StestDeprecationWarning(StestWarning, DeprecationWarning):
    pass


class PlaywrightDriverError(StestException):
    pass


class NoOpendPageError(PlaywrightDriverError):
    pass


class NoOpendContextError(PlaywrightDriverError):
    pass


class NoOpendBrowserError(PlaywrightDriverError):
    pass
