#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author: 思文伟
'''


class GlobalConfig(object):
    def __init__(self):

        self.__settings = {}

    @property
    def seven_data_provider_data_file_dir(self):

        return self.get('seven_data_provider_data_file_dir', None)

    @seven_data_provider_data_file_dir.setter
    def seven_data_provider_data_file_dir(self, dirpath):

        self.set('seven_data_provider_data_file_dir', dirpath)
        return self

    def set(self, key, val):

        self.__settings[key] = val

    def get(self, key, default_value=None):

        return self.__settings.get(key, default_value)

    def __contains__(self, key):

        return key in self.__settings


GLOBAL_CONFIG = GlobalConfig()
