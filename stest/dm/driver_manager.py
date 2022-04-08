#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author: 思文伟
@Date: 2022/03/18 13:51:38
'''

from ..utils import sutils
from ..utils import attrs_marker
from ..utils import attrs_manager
from .driver_cache import DriverCache
from ..pylibs.lazy_libs import LazyLibs
from .wechat_minium_proxy import WechatMiniumProxy


class DriverManager(attrs_manager.AttributeManager):

    CHROME = attrs_marker.ConstAttributeMarker("chrome", "谷歌浏览器")
    FIREFOX = attrs_marker.ConstAttributeMarker("firefox", "火狐浏览器")
    EDGE = attrs_marker.ConstAttributeMarker("edge", "Edge浏览器")
    IE = attrs_marker.ConstAttributeMarker("ie", "IE浏览器")
    OPERA = attrs_marker.ConstAttributeMarker("opera", "欧朋（Opera）浏览器")
    SAFARI = attrs_marker.ConstAttributeMarker("safari", "Safari浏览器")
    BLACKBERRY = attrs_marker.ConstAttributeMarker("blackberry", "黑莓")
    PHANTOMJS = attrs_marker.ConstAttributeMarker("phantomjs", "PhantomJS 是一个无界面的webkit内核浏览器")
    ANDROID = attrs_marker.ConstAttributeMarker("android", "安卓")
    WEBKITGTK = attrs_marker.ConstAttributeMarker("webkitgtk", "WebKitGTK")
    SELENIUM_WEBDRIVER_REMOTE = attrs_marker.ConstAttributeMarker("selenium.webdriver.Remote", "调用selenium.webdriver.Remote的名称")
    APPIUM_WEBDRIVER_REMOTE = attrs_marker.ConstAttributeMarker("appium", "调用appium.webdriver.Remote的名称")
    WINDOW_APP = attrs_marker.ConstAttributeMarker("winapp", "window操作系统应用")
    WINDOW_DESKTOP = attrs_marker.ConstAttributeMarker("windesktop", "window操作系统桌面")
    DESKTOP_ALIAS = attrs_marker.AttributeMarker("WindowDesktop", True, "创建的window桌面会话默认别名")
    WECHAT_ALIAS = attrs_marker.AttributeMarker("wechat", True, "微信小程序minium会话默认别名")

    def __init__(self, script_timeout=5.0, implicit_wait_timeout=0.0):
        """

        Args:
            script_timeout: Set the amount of time(seconds) that the script should wait before throwing an error.
            implicit_wait_timeout: Sets a sticky timeout to implicitly wait for an element to be found, or a command to complete.This method only needs to be called one time per session
        @see selenium.webdriver.remote.webdriver.set_script_timeout
        @see selenium.webdriver.remote.webdriver.implicitly_wait
        """

        self.script_timeout = script_timeout
        self.implicit_wait_timeout = implicit_wait_timeout
        self._driver_cache = DriverCache()

    @property
    def index(self):
        """返回当前驱动实例索引"""
        return self._driver_cache.current_index

    @property
    def driver(self):
        """返回当前驱动实例"""

        return self._driver_cache.current_driver

    def open_url(self, url):
        """Loads a web page in the current browser session."""

        return self.driver.get(url)

    def register_driver(self, driver, alias=None, quit_method=None):

        return self._driver_cache.register_driver(driver, alias, quit_method)

    def switch_driver(self, index_or_alias):

        return self._driver_cache.switch_driver(index_or_alias)

    def close_driver(self):
        """关闭当前驱动"""

        return self._driver_cache.close_driver()

    def close_all_drivers(self):

        return self._driver_cache.close_all_drivers()

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

        index = self._driver_cache.get_index(alias)
        if index:
            self.switch_driver(alias)
            return index
        driver = LazyLibs.Appium().webdriver.Remote(*appdriver_args, **appdriver_kwargs)
        # print('Opened application with session id %s' % driver.session_id)
        try:
            driver.set_script_timeout(self.script_timeout if script_timeout is None else script_timeout)
        except LazyLibs.Selenium().exceptions.WebDriverException:
            pass
        driver.implicitly_wait(self.implicit_wait_timeout if implicit_wait_timeout is None else implicit_wait_timeout)
        return self.register_driver(driver, alias, quit_method)

    open_app = create_appdriver

    create_win_app_driver = create_appdriver

    def create_webdriver(self, browser=None, alias=None, quit_method=None, script_timeout=None, implicit_wait_timeout=None, *webdriver_args, **webdriver_kwargs):
        """如果在缓存中已存在该别名的驱动实例，则不会创建，而只会把当前驱动实例指向该别名驱动实例，返回该别名驱动实例的索引号

        Args:
            browser: 根据传入的名称调用对应的浏览器驱动
            alias: 缓存中存放驱动实例的别名
            quit_method: appium.webdirver的退出方法名称，不传则默认为quit
            script_timeout: 用于execute_async_script()执行的异步js超时时间
            implicit_wait_timeout: 智能等待超时时间
            webdriver_args:位置参数，没有则不需要传,具体根据browser值确定，如browser为chrome，则为webdirver.Chrome的参数
            webdriver_kwargs: 关键字参数,具体根据browser值确定，如browser为chrome，则为webdirver.Chrome的参数
        See:
            selenium.webdriver.Remote webdirver.Chrome
        """

        wd = LazyLibs.Selenium().webdriver
        index = self._driver_cache.get_index(alias)
        if index:
            self.switch_driver(alias)
            return index
        clazz = self.__class__
        if browser is None:
            browser = clazz.SELENIUM_WEBDRIVER_REMOTE

        classmaps = {
            clazz.CHROME: wd.Chrome,
            clazz.FIREFOX: wd.Firefox,
            clazz.EDGE: wd.Edge,
            clazz.IE: wd.Ie,
            clazz.OPERA: wd.Opera,
            clazz.SAFARI: wd.Safari,
            clazz.BLACKBERRY: wd.BlackBerry,
            clazz.PHANTOMJS: wd.PhantomJS,
            clazz.ANDROID: wd.Android,
            clazz.WEBKITGTK: wd.WebKitGTK,
            clazz.SELENIUM_WEBDRIVER_REMOTE: wd.Remote
        }
        classmaps = {k.lower(): v for k, v in classmaps.items()}
        driverclass = classmaps.get(browser, None)
        if driverclass is None:
            raise ValueError('{} is not a supported browser.'.format(browser))
        driver = driverclass(*webdriver_args, **webdriver_kwargs)
        driver.set_script_timeout(self.script_timeout if script_timeout is None else script_timeout)
        driver.implicitly_wait(self.implicit_wait_timeout if implicit_wait_timeout is None else implicit_wait_timeout)
        return self.register_driver(driver, alias, quit_method)

    def open_browser(self, name, url=None, alias=None, *args, **kwargs):

        webdriver_args = args
        quit_method = kwargs.pop("quit_method", None)
        script_timeout = kwargs.pop("script_timeout", None)
        implicit_wait_timeout = kwargs.pop("implicit_wait_timeout", None)
        webdriver_kwargs = kwargs
        if sutils.is_string(name):
            index = self.create_webdriver(name, alias, quit_method, script_timeout, implicit_wait_timeout, *webdriver_args, **webdriver_kwargs)
            if url is not None:
                self.open_url(url)
            return index
        else:
            raise ValueError('name must be string, please check.')

    def chrome(self, url=None, alias=None, *args, **kwargs):

        k = 'options'
        if k not in kwargs.keys():
            options = LazyLibs.Selenium().webdriver.ChromeOptions()
            options.add_argument('--disable-logging')
            kwargs[k] = options

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
            desktop_capabilities = dict({"app": "Root", "platformName": "Windows", "deviceName": "Windows", "alias": alias, "newCommandTimeout": 3600, "forceMjsonwp": True})
            self.create_win_app_driver(alias=alias, command_executor=remote_url, desired_capabilities=desktop_capabilities)
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
        web_driver_names = [clazz.CHROME, clazz.FIREFOX, clazz.EDGE, clazz.IE, clazz.OPERA, clazz.SAFARI, clazz.BLACKBERRY, clazz.PHANTOMJS, clazz.ANDROID, clazz.WEBKITGTK, clazz.SELENIUM_WEBDRIVER_REMOTE]
        app_driver_names = [clazz.APPIUM_WEBDRIVER_REMOTE]
        win_app_driver_names = [clazz.WINDOW_APP]
        win_desktop_driver_names = [clazz.WINDOW_DESKTOP]

        if driver_name in web_driver_names:
            self.open_browser(driver_name, alias=alias, *driver_args, **driver_kwargs)
        elif driver_name in app_driver_names:
            self.create_appdriver(alias, *driver_args, **driver_kwargs)
        elif driver_name in win_app_driver_names:
            remote_url = driver_kwargs.pop("remote_url", driver_kwargs.get("command_executor", None))
            self.open_window_app(remote_url, alias, *driver_args, **driver_kwargs)
        elif driver_name in win_desktop_driver_names:
            remote_url = driver_kwargs.pop("remote_url", driver_kwargs.get("command_executor", None))
            self.open_desktop_session(driver_kwargs.get(remote_url, None), alias)
        else:
            values = []
            values.extend(web_driver_names)
            values.extend(app_driver_names)
            values.extend(win_app_driver_names)
            values.extend(win_desktop_driver_names)
            raise ValueError('{} is a invalid name,vaild value range is: {}'.format(driver_name, values))

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


DRIVER_MANAGER = DriverManager()
