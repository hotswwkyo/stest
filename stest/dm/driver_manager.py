#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author: 思文伟
@Date: 2022/03/18 13:51:38
'''
# import warnings
import inspect
import importlib
from ..utils import sutils
from ..conf import settings
from ..utils.attrs_marker import Const
from ..utils import attrs_manager
from .driver_cache import DriverCache
from ..pylibs.lazy_libs import LazyLibs
from .wechat_minium_proxy import WechatMiniumProxy


class DriverMap(object):

    def __init__(self):
        # {name:item} item = Item(name, module, driver)
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

    def add(self, name, module, driver, convert=False):
        """添加驱动映射

        Parameters
        ----------
        name: 映射名
        module: 可导入驱动的模块对象或者 可导入路径字符串
        driver: 驱动类对象或者类名
        convert: 映射已经存在是否覆盖，True -> 覆盖  False -> 不覆盖 , 默认为False
        """

        if convert:
            self.__maps[name] = self.Item(name, module, driver)
        else:
            if not self.exists(name):
                self.__maps[name] = self.Item(name, module, driver)
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

        def __init__(self, name, module, driver):

            self.name = name
            self.module = module
            self.driver = driver

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
        def driver(self):
            return self.__driver

        @driver.setter
        def driver(self, v):
            if isinstance(v, str) or callable(v):
                self.__driver = v
            else:
                raise TypeError("值类型应该是字符串或者驱动类")

        def get_driver_class(self):
            """获取驱动类"""

            if callable(self.driver):
                clazz = self.driver
            elif isinstance(self.driver, str):
                if inspect.ismodule(self.module):
                    clazz = getattr(self.module, self.driver)
                elif isinstance(self.module, str):
                    m = importlib.import_module(self.module)
                    clazz = getattr(m, self.driver)
            return clazz


class DriverManager(attrs_manager.AttributeManager):

    CHROME = Const("chrome", "谷歌浏览器")
    FIREFOX = Const("firefox", "火狐浏览器")
    EDGE = Const("edge", "Edge浏览器")
    IE = Const("ie", "IE浏览器")
    SAFARI = Const("safari", "Safari浏览器")
    SELENIUM_WEBDRIVER_REMOTE = Const("selenium.webdriver.Remote", "调用selenium.webdriver.Remote的名称")
    APPIUM_WEBDRIVER_REMOTE = Const("appium.webdriver.Remote", "调用appium.webdriver.Remote的名称")
    WINDOW_APP = Const("winapp", "window操作系统应用")
    WINDOW_DESKTOP = Const("windesktop", "window操作系统桌面")
    DESKTOP_ALIAS = Const("WindowDesktop", "创建的window桌面会话默认别名")
    WECHAT_ALIAS = Const("wechat", "微信小程序minium会话默认别名")
    KEY_IN_SETTINGS = Const("DRIVER_MANAGER", "驱动管理器(即DriverManager实例)在全局配置(settings)中的键名")

    SELENIUM_WEBDRIVER_MAP = DriverMap()
    SELENIUM_WEBDRIVER_MAP.add(IE.value, 'selenium.webdriver', 'Ie')
    SELENIUM_WEBDRIVER_MAP.add(EDGE.value, 'selenium.webdriver', 'Edge')
    SELENIUM_WEBDRIVER_MAP.add(CHROME.value, 'selenium.webdriver', 'Chrome')
    SELENIUM_WEBDRIVER_MAP.add(FIREFOX.value, 'selenium.webdriver', 'Firefox')
    SELENIUM_WEBDRIVER_MAP.add(SAFARI.value, 'selenium.webdriver', 'Safari')
    SELENIUM_WEBDRIVER_MAP.add(SELENIUM_WEBDRIVER_REMOTE.value, 'selenium.webdriver', 'Remote')

    APPIUM_WEBDRIVER_MAP = DriverMap()
    APPIUM_WEBDRIVER_MAP.add(APPIUM_WEBDRIVER_REMOTE.value, 'appium.webdriver', 'Remote')

    def __init__(self, script_timeout=5.0, implicit_wait_timeout=0.0):
        """驱动管理器

        Parameters
        ----------
        script_timeout: Set the amount of time(seconds) that the script should wait before throwing an error. refer to the `selenium.webdriver.remote.webdriver.set_script_timeout`
        implicit_wait_timeout: Sets a sticky timeout to implicitly wait for an element to be found, or a command to complete.This method only needs to be called one time per session, refer to the `selenium.webdriver.remote.webdriver.implicitly_wait`
        """

        self.script_timeout = script_timeout
        self.implicit_wait_timeout = implicit_wait_timeout
        self.__save_to_global_settings()
        self.__cache = DriverCache()

    def __save_to_global_settings(self):

        dm = getattr(settings, self.KEY_IN_SETTINGS, None)
        if not isinstance(dm, DriverManager):
            setattr(settings, self.KEY_IN_SETTINGS, self)

    @property
    def cache(self):
        return self.__cache

    @property
    def index(self):
        """返回当前驱动实例索引"""
        return self.__cache.current_index

    @property
    def driver(self):
        """返回当前驱动实例"""

        return self.__cache.current_driver

    def open_url(self, url):
        """Loads a web page in the current browser session."""

        return self.driver.get(url)

    def register_driver(self, driver, alias=None, quit_method=None):

        return self.__cache.register_driver(driver, alias, quit_method)

    def switch_driver(self, index_or_alias):

        return self.__cache.switch_driver(index_or_alias)

    def close_driver(self):
        """关闭当前驱动"""

        return self.__cache.close_driver()

    def close_all_drivers(self):

        return self.__cache.close_all_drivers()

    def set_script_timeout(self, time_to_wait):
        return self.driver.set_script_timeout(time_to_wait)

    def implicitly_wait(self, time_to_wait):
        return self.driver.implicitly_wait(time_to_wait)

    def create_appdriver(self, alias=None, quit_method=None, script_timeout=None, implicit_wait_timeout=None, *appdriver_args, **appdriver_kwargs):
        """

        Args:
            alias: 缓存中存放驱动实例的别名
            quit_method: appium.webdirver的退出方法名称，不传则默认为quit
            script_timeout: 用于execute_async_script()执行的异步js超时时间
            implicit_wait_timeout: 智能等待超时时间
            appdriver_args: appium.webdirver的位置参数，没有则不需要传
            appdriver_kwargs: appium.webdirver的关键字参数
        See:
            appium.webdriver
        """

        index = self.__cache.get_index(alias)
        if index:
            self.switch_driver(alias)
            return index
        driver = LazyLibs.Appium().webdriver.Remote(*appdriver_args, **appdriver_kwargs)
        # print('Opened application with session id %s' % driver.session_id)
        try:
            driver.set_script_timeout(
                self.script_timeout if script_timeout is None else script_timeout)
        except LazyLibs.Selenium().exceptions.WebDriverException:
            pass
        driver.implicitly_wait(
            self.implicit_wait_timeout if implicit_wait_timeout is None else implicit_wait_timeout)
        return self.register_driver(driver, alias, quit_method)

    open_app = create_appdriver

    create_win_app_driver = create_appdriver

    @classmethod
    def add_selenium_webdriver(cls, name, module, webdriver, convert=False):
        """添加selenium 测试驱动映射，供后面的创建驱动方法使用（set browser name map driver class of selenium support browser. it will be use in create browser driver of selenium test lib.）

        Parameters
        ----------
        name: 映射名
        module: 可导入selenium webdriver 的模块对象或者 可导入路径字符串
        webdriver: selenium webdriver类对象或者类名
        convert: 映射已经存在是否覆盖，True -> 覆盖  False -> 不覆盖 , 默认为False

        Usage
        ------
        ```py
        DriverManager.add_selenium_webdriver(\"chrome\",\"selenium.webdriver\", \"Chrome\")
        DRIVER_MANAGER.open_browser(\"chrome\")
        ```

        """
        cls.SELENIUM_WEBDRIVER_MAP.add(name, module, webdriver, convert=convert)

    def remove_selenium_webdriver(cls, name):

        cls.SELENIUM_WEBDRIVER_MAP.remove(name)

    def create_webdriver(self, browser=None, alias=None, quit_method=None, script_timeout=None, implicit_wait_timeout=None, *webdriver_args, **webdriver_kwargs):
        """如果在缓存中已存在该别名的驱动实例，则不会创建，而只会把当前驱动实例指向该别名驱动实例，返回该别名驱动实例的索引号

        Parameters
        ----------
        browser: 根据传入的映射名称调用对应的浏览器驱动
        alias: 缓存中存放驱动实例的别名
        quit_method: 退出驱动的方法名称，不传则默认为quit
        script_timeout: 用于execute_async_script()执行的异步js超时时间
        implicit_wait_timeout: 智能等待超时时间
        webdriver_args:位置参数，没有则不需要传,具体根据browser值确定，如browser为chrome，则为`selenium.webdirver.Chrome`的参数
        webdriver_kwargs: 关键字参数,具体根据browser值确定，如browser为chrome，则为`selenium.webdirver.Chrome`的参数

        Refer
        -----
            - `selenium.webdriver.Ie`
            - `selenium.webdriver.Edge`
            - `selenium.webdriver.Chrome`
            - `selenium.webdriver.Firefox`
            - `selenium.webdriver.Safari`
            - `selenium.webdriver.Remote`
        """

        index = self.__cache.get_index(alias)
        if index:
            self.switch_driver(alias)
            return index
        clazz = self.__class__
        if browser is None:
            browser = clazz.SELENIUM_WEBDRIVER_REMOTE
        classmap: DriverMap.Item = self.SELENIUM_WEBDRIVER_MAP.get(browser, default=None)
        if classmap is None:
            raise ValueError(
                '未找到映射名为{} 的驱动映射，请先用add_selenium_webdriver方法添加selenium驱动映射'.format(browser))
        driverclass = classmap.get_driver_class()
        driver = driverclass(*webdriver_args, **webdriver_kwargs)
        driver.set_script_timeout(self.script_timeout if script_timeout is None else script_timeout)
        driver.implicitly_wait(
            self.implicit_wait_timeout if implicit_wait_timeout is None else implicit_wait_timeout)
        return self.register_driver(driver, alias, quit_method)

    def open_browser(self, name, url=None, alias=None, *args, **kwargs):

        webdriver_args = args
        quit_method = kwargs.pop("quit_method", None)
        script_timeout = kwargs.pop("script_timeout", None)
        implicit_wait_timeout = kwargs.pop("implicit_wait_timeout", None)
        webdriver_kwargs = kwargs
        if sutils.is_string(name):
            index = self.create_webdriver(
                name, alias, quit_method, script_timeout, implicit_wait_timeout, *webdriver_args, **webdriver_kwargs)
            if url is not None:
                self.open_url(url)
            return index
        else:
            raise ValueError('name must be string, please check.')

    def chrome(self, url=None, alias=None, *args, **kwargs):

        return self.open_browser(self.CHROME, url=url, alias=alias, *args, **kwargs)

    def firefox(self, url=None, alias=None, *args, **kwargs):

        return self.open_browser(self.FIREFOX, url=url, alias=alias, *args, **kwargs)

    def ie(self, url=None, alias=None, *args, **kwargs):

        return self.open_browser(self.IE, url=url, alias=alias, *args, **kwargs)

    def edge(self, url=None, alias=None, *args, **kwargs):

        return self.open_browser(self.EDGE, url=url, alias=alias, *args, **kwargs)

    def open_desktop_session(self, remote_url, alias=None):
        """开启window桌面会话"""

        alias = alias if alias else self.DESKTOP_ALIAS
        try:
            self.switch_driver(alias)
        except RuntimeError:
            desktop_capabilities = dict({"app": "Root", "platformName": "Windows", "deviceName": "Windows",
                                        "alias": alias, "newCommandTimeout": 3600, "forceMjsonwp": True})
            self.create_win_app_driver(alias=alias, command_executor=remote_url,
                                       desired_capabilities=desktop_capabilities)
        return self.index

    def open_window_app(self, remote_url, alias=None, *args, **kwargs):
        """"""

        desired_capabilities = kwargs.get("desired_capabilities", {})
        if "platformName" not in desired_capabilities:
            desired_capabilities["platformName"] = "Windows"
        if "forceMjsonwp" not in desired_capabilities:
            desired_capabilities["forceMjsonwp"] = True
        kwargs["command_executor"] = remote_url
        kwargs["desired_capabilities"] = desired_capabilities
        return self.create_win_app_driver(alias=alias, *args, **kwargs)

    def create_driver(self, driver_name, alias=None, *driver_args, **driver_kwargs):

        clazz = self.__class__
        web_driver_names = clazz.SELENIUM_WEBDRIVER_MAP.names
        app_driver_names = clazz.APPIUM_WEBDRIVER_MAP.names
        win_app_driver_names = [clazz.WINDOW_APP]
        win_desktop_driver_names = [clazz.WINDOW_DESKTOP]

        if driver_name in web_driver_names:
            self.open_browser(driver_name, alias=alias, *driver_args, **driver_kwargs)
        elif driver_name in app_driver_names:
            self.create_appdriver(alias, *driver_args, **driver_kwargs)
        elif driver_name in win_app_driver_names:
            remote_url = driver_kwargs.pop(
                "remote_url", driver_kwargs.get("command_executor", None))
            self.open_window_app(remote_url, alias, *driver_args, **driver_kwargs)
        elif driver_name in win_desktop_driver_names:
            remote_url = driver_kwargs.pop(
                "remote_url", driver_kwargs.get("command_executor", None))
            self.open_desktop_session(driver_kwargs.get(remote_url, None), alias)
        else:
            values = []
            values.extend(web_driver_names)
            values.extend(app_driver_names)
            values.extend(win_app_driver_names)
            values.extend(win_desktop_driver_names)
            raise ValueError(
                '{} is a invalid name,vaild value range is: {}'.format(driver_name, values))

    def open_wechat_minium(self, minium_config=None):

        try:
            mini_proxy = self.switch_driver(self.WECHAT_ALIAS)
        except RuntimeError:
            mini_proxy = WechatMiniumProxy()
            mini_proxy.init_minium(minium_config)
            self.register_driver(mini_proxy, self.WECHAT_ALIAS, "release_minium")
        return mini_proxy

    def switch_to_wechat_minium(self):
        return self.switch_driver(self.WECHAT_ALIAS)

    def create_playwright_driver(self, browser_type="chromium", alias=None, *, playwright=None, browser_launch_args={}, browser_context_args={}):
        """创建playwright驱动

        Args
        -------
        browser_type : str  default value is `chromium`
            chromium | firefox | webkit
        alias : 缓存中存放驱动实例的别名
        playwright : playwright实例，默认为None，框架自动创建
        browser_launch_args : dict
            key value pairs same as Parameters of `BrowserType.launch`
        browser_context_args : dict
            key value pairs same as Parameters of `Browser.new_context`

        """

        from .playwright_driver import PlaywrightDriver
        quit_method = "quit"
        index = self.cache.get_index(alias)
        if index:
            self.switch_driver(alias)
            return index
        driver = PlaywrightDriver(playwright)
        driver.open_browser(browser_type=browser_type, browser_launch_args=browser_launch_args,
                            browser_context_args=browser_context_args)
        return self.register_driver(driver, alias, quit_method)


DRIVER_MANAGER = DriverManager()
