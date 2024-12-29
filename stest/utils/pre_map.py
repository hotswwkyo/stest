#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import inspect
import importlib


class Premap(object):

    def __init__(self):
        # {name:item} item = Item(name, obj, module=module, is_final=is_final)
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

    def add(self, name, obj, *, module=None, is_final=False, convert=False):
        """添加映射

        Parameters
        ----------
        name : str
            映射名
        obj : Any
            映射的对象，如果值类型是字符串，且is_final=False，从指定的模块中获取名为obj值的属性
        module : str | ModuleType | None
            可导入驱动的模块对象或者 可导入路径字符串，默认值为None，当obj为字符串，且is_final=False时，
            值必须是模块的绝对导入路径字符串或者模块对象本身。
        is_final : `bool`
            标记`obj`是否是最终值，当is_final=False，obj是字符串类型时，从指定的模块中获取名为obj值的属性
        convert : bool
            映射已经存在是否覆盖，True -> 覆盖  False -> 不覆盖 , 默认为False

        Usage
        -----
        ```py
        Premap().add(\"chrome\", \"Chrome\", module=\"selenium.webdriver\")

        from selenium import webdriver
        Premap().add(\"chrome\", webdriver.Chrome)

        Premap().add(\"chrome\", \"Chrome\", module=webdriver)
        ```
        """

        if convert:
            self.__maps[name] = self.Item(name, obj, module=module, is_final=is_final)
        else:
            if not self.exists(name):
                self.__maps[name] = self.Item(name, obj, module=module, is_final=is_final)
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

        def __init__(self, name, obj, module=None, is_final=False):

            self.obj = obj
            self.name = name
            self.is_final = is_final
            self.module = module

        @property
        def module(self):
            return self.__module

        @module.setter
        def module(self, v):

            if isinstance(self.obj, str) and not self.is_final:
                if isinstance(v, str) or inspect.ismodule(v):
                    self.__module = v
                else:
                    raise TypeError('值类型需要是模块的绝对导入路径字符串或者模块对象本身')
            else:
                self.__module = v

        @property
        def obj(self):
            return self.__obj

        @obj.setter
        def obj(self, v):
            self.__obj = v

        def get_object_from_module(self):
            """获取最终值

            当is_final=False，obj是字符串类型时，从指定的模块中获取名为obj值的属性，否则直接返回

            """
            if self.is_final:
                o = self.obj
            else:
                if isinstance(self.obj, str):
                    if isinstance(self.module, str):
                        m = importlib.import_module(self.module)
                    elif inspect.ismodule(self.module):
                        m = self.module
                    else:
                        raise TypeError('有效类型为模块的绝对导入路径字符串或者模块对象本身，module类型无效：{}'.format(
                            type(self.module)))
                    o = getattr(m, self.obj)
                else:
                    o = self.obj
            return o

        get_final_object = get_object_from_module
