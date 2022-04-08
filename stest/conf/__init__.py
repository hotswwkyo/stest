#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author: 思文伟
@Date: 2022/03/30 17:50:18
'''
import os
import inspect
from ..utils.import_helper import ImportHelper
from ..core.errors import ImproperlyConfigured
from . import global_settings
from ..utils.lazy_obj import empty, LazyObject

__all__ = ['settings', 'SettingsFileFinder']


class SettingsFileFinder(object):
    def __init__(self, settings_file_name='settings.py'):

        self.__settings_file_name = settings_file_name

    def is_py_package(self, dirpath):

        return os.path.isdir(dirpath) and os.path.isfile(os.path.join(dirpath, '__init__.py'))

    @property
    def settings_file_name(self):
        return self.__settings_file_name

    def __issuite(self, tc):
        "A crude way to tell apart testcases and suites with duck-typing"
        try:
            iter(tc)
        except TypeError:
            return False
        return True

    def __all_in_one(self, tc):

        alltests = []
        if self.__issuite(tc):
            for one in tc:
                if not self.__issuite(one):
                    alltests.append(one)
                else:
                    alltests.extend(self.__all_in_one(one))
        else:
            alltests.append(tc)
        return alltests

    def __is_exists_file(self, path):

        return os.path.exists(path) and os.path.isfile(path)

    def find_settings_file_from_start_dir(self, dirpath):
        """ 从给定的目录开始查找配置文件，如果在该目录能找到配置文件，则不会遍历其子目录，否则会一直遍历。
        遍历完其下所有子孙目录后，仍找不到则返回None，找到则返回完整配置文件路径

        Args:
            dirpath: 开始查找的目录
        """
        if not os.path.isdir(dirpath):
            return None
        filepath = os.path.join(dirpath, self.settings_file_name)
        if not self.__is_exists_file(filepath):
            filepath = self.__find_settings_file_from_subdir(dirpath)
        return filepath

    def __find_settings_file_from_subdir(self, dirpath):

        names = os.listdir(dirpath)
        settings_file_path = None

        for name in names:
            dpath = os.path.join(dirpath, name)
            if os.path.isdir(dpath):
                filepath = os.path.join(dpath, self.settings_file_name)
                if self.__is_exists_file(filepath):
                    settings_file_path = filepath
                    break
                else:
                    result = self.__find_settings_file_from_subdir(dpath)
                    if result:
                        settings_file_path = result
                        break
        return settings_file_path

    def set_non_py_package_dir_as_start_dir(self, abspath):
        """ 设置开始查找配置文件的目录为第一个非python包的目录，
        如果给定的路径中的目录没有非python包目录，则设置当前目录为开始查找配置文件的目录

        Args:
            abspath: 绝对路径
        """

        if not os.path.exists(abspath):
            return (None, None)

        if os.path.isfile(abspath):
            dirpath = os.path.dirname(abspath)
        else:
            dirpath = abspath
        current_dirpath = dirpath
        paths = []
        start_dirpath = os.path.dirname(current_dirpath)  # 从哪个路径开始查找配置文件 sconfig.py
        while True:
            if not self.is_py_package(dirpath):
                start_dirpath = dirpath
                break
            if os.path.basename(dirpath):
                paths.append(dirpath)
                dirpath = os.path.dirname(dirpath)
            else:
                break

        return start_dirpath

    def find_settings_file_by_test(self, test):
        used = set()
        start_path = None
        config_path = None
        for t in self.__all_in_one(test):
            mod = inspect.getmodule(t)
            if mod in used:
                continue
            else:
                used.add(mod)
                file_path = os.path.abspath(mod.__file__)
                start_path = self.set_non_py_package_dir_as_start_dir(file_path)
                config_path = self.find_settings_file_from_start_dir(start_path)
                if config_path:
                    break
        return (start_path, config_path)

    def find_settings_file_by_testcase_class(self, testclass):

        start_path = None
        config_path = None
        mod = inspect.getmodule(testclass)
        file_path = os.path.abspath(mod.__file__)
        start_path = self.set_non_py_package_dir_as_start_dir(file_path)
        config_path = self.find_settings_file_from_start_dir(start_path)
        return (start_path, config_path)


class LazySettings(LazyObject):
    """
    框架会在运行测试时去查找项目配置文件，并调用load_configure_from_file()方法载入配置文件中的配置
    """
    def _setup(self):

        self._wrapped = Settings()

    def __repr__(self):
        # Hardcode the class name as otherwise it yields 'Settings'.
        if self._wrapped is empty:
            return '<LazySettings [Unevaluated]>'
        return '<LazySettings "%(settings_module_file_path)s">' % {
            'settings_module_file_path': self._wrapped.SETTINGS_MODULE_FILE_PATH,
        }

    def __getattr__(self, name):

        if self._wrapped is empty:
            self._setup()
        val = getattr(self._wrapped, name)
        self.__dict__[name] = val
        return val

    def __setattr__(self, name, value):
        if name == '_wrapped':
            self.__dict__.clear()
        else:
            self.__dict__.pop(name, None)
        super().__setattr__(name, value)

    def __delattr__(self, name):

        super().__delattr__(name)
        self.__dict__.pop(name, None)

    def load_configure_from_file(self, settings_module_filepath):

        if self._wrapped is empty:
            self._wrapped = Settings()
        self._wrapped.load(settings_module_filepath)

    @property
    def configured(self):
        return self._wrapped is not empty

    @property
    def is_loaded(self):
        return self.configured and self._wrapped.is_loaded


class Settings(object):
    def __init__(self):

        for setting in dir(global_settings):
            if setting.isupper():
                setattr(self, setting, getattr(global_settings, setting))

        self._explicit_settings = set()
        self._is_loaded = False
        self.SETTINGS_MODULE_FILE_PATH = None

    def load(self, settings_module_filepath):

        self.SETTINGS_MODULE_FILE_PATH = settings_module_filepath
        mod = ImportHelper().load_module(self.SETTINGS_MODULE_FILE_PATH)
        tuple_settings = ()
        for setting in dir(mod):
            if setting.isupper():
                setting_value = getattr(mod, setting)

                if (setting in tuple_settings and not isinstance(setting_value, (list, tuple))):
                    raise ImproperlyConfigured("The %s setting must be a list or a tuple. " % setting)
                setattr(self, setting, setting_value)
                self._explicit_settings.add(setting)
        self._is_loaded = True

    def is_overridden(self, setting):
        return setting in self._explicit_settings

    @property
    def is_loaded(self):
        return self._is_loaded

    def __repr__(self):
        return '<%(cls)s "%(settings_module_file_path)s">' % {
            'cls': self.__class__.__name__,
            'settings_module_file_path': self.SETTINGS_MODULE_FILE_PATH,
        }


settings = LazySettings()
