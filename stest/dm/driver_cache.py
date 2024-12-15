#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author: 思文伟
@Date: 2022/03/18
'''

from ..utils import sutils
from ..core.errors import NoOpenDriver


class DriverCache(object):
    def __init__(self, error_msg="No current driver"):

        self._error_msg = error_msg
        self._init_items()

    def _init_items(self):

        self._all_drivers = []
        self._current_driver = None
        self._closed_drivers = set()
        self._alias_index_maps = sutils.StringKeyDict()
        self._default_quit_method = 'quit'
        self._quit_methods = sutils.StringKeyDict()

    @property
    def default_quit_method(self):

        return self._default_quit_method

    @default_quit_method.setter
    def default_quit_method(self, value):

        if isinstance(value, str):
            self._default_quit_method = value
        else:
            raise TypeError('pass quit method name of driver must be string')

    @property
    def error_msg(self):

        return self._error_msg

    @error_msg.setter
    def error_msg(self, value):

        if isinstance(value, str):
            self._error_msg = value
        else:
            raise TypeError('value must be string')

    def had_opened_driver(self):
        return self._current_driver is not None

    @property
    def current_driver(self):

        if not self:
            raise NoOpenDriver(self.error_msg)
        return self._current_driver

    @property
    def current_index(self):

        if not self:
            return None
        for index, driver in enumerate(self._all_drivers):
            if driver is self._current_driver:
                return index + 1

    def register_driver(self, driver, alias=None, quit_method=None):
        """注册driver，并返回注册成功后，它在缓存中的位置索引(索引号从1开始)

        Args:
            driver: 驱动对象

            alias: 驱动别名，忽略大小写和空格

            quit_method: 退出驱动的方法名，调用关闭方法时将调用驱动实例的该方法退出，忽略则调用默认退出方法，如果驱动实例没有该方法则抛异常
        """
        if driver is None:
            raise ValueError('invalid driver: {}'.format(driver))
        self._current_driver = driver
        self._all_drivers.append(driver)
        index = len(self._all_drivers)
        if sutils.is_string(alias):
            self._alias_index_maps[alias] = index
        if sutils.is_string(quit_method):
            self._quit_methods[str(index)] = quit_method
        return index

    def switch_driver(self, alias_or_index):
        """通过别名或索引切换到对应的driver"""
        self._current_driver = self._get_driver(alias_or_index)
        return self._current_driver

    def _get_driver(self, alias_or_index=None):
        """通过别名或索引获取缓存中驱动对象

        Args:
            alias_or_index: 如果传入None则返回当前激活的驱动对象，否则根据指定的别名或索引查找并返回
        """
        if alias_or_index is None:
            if not self:
                raise RuntimeError(self.error_msg)
            return self._current_driver
        try:
            index = self._resolve_alias_or_index(alias_or_index)
        except ValueError:
            raise RuntimeError("Non-existing index or alias '%s'." % alias_or_index)
        return self._all_drivers[index - 1]

    @property
    def drivers(self):

        return self._all_drivers

    @property
    def active_drivers(self):

        open_drivers = []
        for driver in self._all_drivers:
            if driver not in self._closed_drivers:
                open_drivers.append(driver)
        return open_drivers

    def _call_method(self, driver, method_name):

        return getattr(driver, method_name)()

    def close_driver(self):

        if self._current_driver:
            driver = self._current_driver
            method = self._quit_methods.get(str(self.current_index), self.default_quit_method)
            self._call_method(self._current_driver, method)
            self._current_driver = None
            if driver not in self._closed_drivers:
                self._closed_drivers.add(driver)

    def close_all_drivers(self):

        for index, driver in enumerate(self._all_drivers):
            if driver not in self._closed_drivers:
                self._call_method(driver, self._quit_methods.get(
                    str(index + 1), self.default_quit_method))
        self.clear_empty_cache()
        return self._current_driver

    def clear_empty_cache(self):

        self._init_items()

    def get_index(self, alias_or_index):

        try:
            index = self._resolve_alias_or_index(alias_or_index)
        except ValueError:
            return None
        try:
            driver = self._get_driver(alias_or_index)
        except RuntimeError:
            return None
        return None if driver in self._closed_drivers else index

    def _resolve_alias_or_index(self, alias_or_index):
        try:
            return self._resolve_alias(alias_or_index)
        except ValueError:
            return self._resolve_index(alias_or_index)

    def _resolve_alias(self, alias):
        if sutils.is_string(alias):
            try:
                return self._alias_index_maps[alias]
            except KeyError:
                pass
        raise ValueError

    def _resolve_index(self, index):
        try:
            index = int(index)
        except TypeError:
            raise ValueError
        if not 0 < index <= len(self._all_drivers):
            raise ValueError
        return index

    def __nonzero__(self):

        return self._current_driver is not None
