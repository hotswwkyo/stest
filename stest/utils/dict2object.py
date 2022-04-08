#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author: 思文伟
@Date: 2022/03/23 16:09:22
'''


class DictToObject(object):
    def __init__(self, py_dict):
        """

        """
        if not isinstance(py_dict, dict):
            raise ValueError("Data Type Must Be dict")
        for field in py_dict:
            value = py_dict[field]
            if not isinstance(value, (dict, list, tuple)):
                setattr(self, "%s" % field, value)
            else:
                if isinstance(value, dict):
                    setattr(self, "%s" % field, self.__class__(value))
                elif isinstance(value, tuple):
                    setattr(self, "%s" % field, self.analyze_tuple(value))
                else:
                    setattr(self, "%s" % field, self.analyze_list(value))

    def analyze_list(self, array):
        for index, value in enumerate(array):
            if isinstance(value, list):
                self.analyze_list(value)
            elif isinstance(value, tuple):
                self.analyze_tuple(value)
            elif isinstance(value, dict):  # if element of list is dict,converts the value of the element in the list into the object
                array[index] = self.__class__(value)
            else:
                pass
        return array

    def analyze_tuple(self, array):
        tuple_to_list = list(array)
        for index, value in enumerate(tuple_to_list):
            if isinstance(value, tuple):
                self.analyze_tuple(value)
            elif isinstance(value, tuple):
                self.analyze_tuple(value)
            elif isinstance(value, dict):  # if element of list is dict,converts the value of the element in the list into the object
                tuple_to_list[index] = self.__class__(value)
            else:
                pass
        return tuple(tuple_to_list)
