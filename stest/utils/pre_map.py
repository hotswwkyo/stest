#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import inspect
import importlib


class Premap(object):

    def __init__(self):
        # {name:item} item = Item(name, module, obj)
        self.__maps = {}

    @property
    def maps(self):
        return self.__maps

    @property
    def names(self):

        return list(self.__maps.keys())

    def exists(self, name):
        """判断映射是否已经存在"""

        return name in self.__maps

    def add(self, name, module, obj, *, convert=False, final_value=False):
        """添加映射

        Parameters
        ----------
        name : str
            映射名
        module : str | ModuleType
            可导入驱动的模块对象或者 可导入路径字符串
        obj : Any
            指明要映射的对象，可以是模块中的对象或对象在模块中的名称
        convert : bool
            映射已经存在是否覆盖，True -> 覆盖  False -> 不覆盖 , 默认为False
        final_value : `bool`
            标记`obj`是否是最终值，是则获取的时候直接返回，否则使用自动判断。默认为`False` -> `使用自动判断规则`：
            如果`obj`是字符串，且模块中有该名为`obj`的值的属性名，则意味着要从模块中获取该属性，
            否则则认为预映射的值已经是最终值，不需要再次从模块中去获取，直接返回即可

        Usage
        -----
        ```py
        Premap().add(\"chrome\", \"selenium.webdriver\", \"Chrome\")

        from selenium.webdriver import Chrome
        Premap().add(\"chrome\", \"selenium.webdriver\", Chrome)

        from selenium import webdriver
        Premap().add(\"chrome\", webdriver, webdriver.Chrome)

        Premap().add(\"chrome\", webdriver, \"Chrome\")
        ```
        """

        if convert:
            self.__maps[name] = self.Item(name, module, obj, final_value)
        else:
            if not self.exists(name):
                self.__maps[name] = self.Item(name, module, obj, final_value)
        return self

    def get(self, name, *args, **kwargs):
        k = "default"
        if k in kwargs:
            item = self.__maps.get(name, kwargs[k])
        else:
            if len(args) > 0:
                item = self.__maps.get(name, args[0])
            else:
                item = self.__maps.get(name)
        return item

    def remove(self, name):

        self.__maps.pop(name, None)
        return self

    class Item(object):

        def __init__(self, name, module, obj, final_value=False):

            self.name = name
            self.module = module
            self.obj = obj
            self.final_value = final_value

        @property
        def module(self):
            return self.__module

        @module.setter
        def module(self, v):
            if isinstance(v, str) or inspect.ismodule(v):
                self.__module = v
            else:
                raise TypeError('值类型应该是字符串或者模块对象')

        @property
        def obj(self):
            return self.__obj

        @obj.setter
        def obj(self, v):
            self.__obj = v

        def get_object_from_module(self):
            """获取最终值

            属性`final_value`标记`self.obj`是否是最终值，是则获取的时候直接返回，否则使用自动判断规则。final_value 默认为False -> 使用自动判断规则：
                - 如果 `self.obj` 是字符串，且模块中有该名为`self.obj`的值的属性名，则意味着要从模块中获取该属性，
                否则则认为预映射的值已经是最终值，不需要再次从模块中去获取，直接返回即可

            """
            if self.final_value:
                o = self.obj
            else:
                if isinstance(self.obj, str):
                    if isinstance(self.module, str):
                        m = importlib.import_module(self.module)
                    elif inspect.ismodule(self.module):
                        m = self.module
                    else:
                        raise TypeError('module的值类型需要是字符串或者模块对象')
                    if self.obj in dir(m):
                        o = getattr(m, self.obj)
                else:
                    o = self.obj
            return o

        get_final_object = get_object_from_module
