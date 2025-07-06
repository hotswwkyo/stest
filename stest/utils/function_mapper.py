#!/usr/bin/env python
# -*- encoding: utf-8 -*-


class FunctionMapper(object):

    def __init__(self):

        self.__obj_maps = {}
        self.__presettings = {}
        self.__default_settings = {}

    @property
    def maps(self):

        return self.__obj_maps

    @property
    def presettings(self):

        return self.__presettings

    def preset(self, settings: dict, names=None):

        if names is None:
            self.__default_settings.update(settings)
        else:
            for name in names:
                nm = self.presettings.get(name, {})
                nm.update(settings)
                self.presettings[name] = nm
        return self

    def update(self, settings: dict, *names):

        if names:
            for name in names:
                func, es = self.maps.get(name, {})
                es.update(settings)
                self.maps[name] = (func, es)
        return self

    def update_all(self, settings: dict):

        for n, v in self.maps.items():
            v[1].update(settings)
        return self

    def mapping(self, name="", *, enable_preset=True, **settings):
        """通过名称映射函数或方法的装饰器

        Parameters
        ----------
        name: str
            映射名
        enable_preset: bool
            是否使用预设的配置
        settings: dict
            配置

        """

        def wrapper(func):
            nonlocal name
            if not name:
                doc = func.__doc__
                if doc and isinstance(doc, str):
                    name = doc.split('\n')[0]
            if not name:
                raise ValueError('请设置映射名称(Please set the mapping name)')
            if name not in self.maps:
                final_settings = {}
                if enable_preset:
                    final_settings.update(self.__default_settings)
                    final_settings.update(self.presettings.get(name, {}))
                final_settings.update(settings)
                self.maps[name] = (func, final_settings)
            else:
                raise ValueError('name:{} is exists, please rename'.format(name))
            return func
        return wrapper

    def get_settings(self, name, setting_key, default=None):

        settings: dict = self.maps.get(name)[1]
        return settings.get(setting_key, default)

    def execute(self, name, *, args=(), kwargs={}, instance=None, callback=None, callback_args=None, callback_kwargs=None):
        """调用映射的函数或方法

        Parameters
        ----------
        name: str
            映射名
        instance: object
            方法所在类的实例化对象, 如果在args参数指定了方法所在类的实例化对象，则该参数应传None，如果传值，args参数就不应该再传实例化对象，只传除该对象以外的其它位置参数即可，如：
            ```python
            mapper = FunctionMapper()

            class OrderListPage(MenuPage):
                class Elements(MenuPage.Elements):
                @mapper.mapping('退报名')
                def cancel_registration(self, row):
                    btn_name = "退报名"
                    return self.__table_action_column_button(row, btn_name)

                class Actions(MenuPage.Actions):
                    def set_cinema_info(self, row, info):
                        mapper.execute('退报名',instance=self.page.element, args=(row,))
                        mapper.execute('退报名',args=(self.page.element, row))
                        # >>> self.page.element.cancel_registration(row)
                        ...
            ```

        args: tuple
            函数或方法的位置参数
        kwargs: dict
            函数或方法的关键字参数
        callback: callable
            回调函数, callback(name, return_value, settings, callback_args, callback_kwargs), 接受参数说明如下：
                - name 映射名
                - return_value 映射函数或方法的返回值
                - settings 映射函数或方法的配置
                - callback_args 回调函数的位置参数
                - callback_kwargs 回调函数的关键字参数
        callback_args: tuple
            回调函数的位置参数
        callback_kwargs: dict
            回调函数的关键字参数

        Retuns
        ------
        如果未提供回调函数，则返回映射函数或方法的返回值，否则返回回调函数的返回值
        """

        method, settings = self.maps[name]
        if isinstance(method, property):
            final_method = method.fget
        else:
            final_method = method
        return_value = final_method(instance, *args, **kwargs)
        if callable(callback):
            return callback(name, return_value, settings, callback_args, callback_kwargs)
        else:
            return return_value
