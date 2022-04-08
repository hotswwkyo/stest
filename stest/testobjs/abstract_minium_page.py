#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author: 思文伟
@Date: 2022/04/06
'''
import time
from ..utils import attrs_manager
from ..utils import attrs_marker
from ..dm import DRIVER_MANAGER


class AbstractMiniumPage(attrs_manager.AttributeManager):
    """微信小程序抽象根页面"""

    WECHAT_MANAGER = attrs_marker.AttributeMarker(DRIVER_MANAGER, True, "微信小程序测试库minium管理器")

    def __init__(self, url=None, minium_config=None):
        """

        Args:
            url: 微信小程序页面url
            minium_config: 初始化配置，只初始化一次，如果在其它页面已经初始化过，则不会再次初始化。
            取值为字典、配置文件路径、None，如果为None则使用默认配置WechatMiniumProxy.DEFAULT_MINI_CONFIG
                值：
                    {
                        "platform": "ide",
                        "debug_mode": "info",
                        "close_ide": False,
                        "no_assert_capture": False,
                        "auto_relaunch": False,
                        "device_desire": {},
                        "report_usage": True,
                        "remote_connect_timeout": 180,
                        "use_push": True
                    }
        """

        self.__mini_proxy = self.WECHAT_MANAGER.open_wechat_minium(minium_config)
        self.mini = self.__mini_proxy.mini
        self.native = self.__mini_proxy.native
        self.app = self.mini.app
        self.url = url

        if self.url and isinstance(self.url, str) and self.url.strip() != "":
            self.app.redirect_to(self.url)
        self._build_elements()
        self._build_actions()
        self.init()

    @property
    def current_page(self):

        return self.app.get_current_page()

    @property
    def wechat_manager(self):
        return self.__class__.WECHAT_MANAGER

    def get_element(self, selector, inner_text=None, text_contains=None, value=None, max_timeout=20):

        return self.app.get_current_page().get_element(selector, inner_text=inner_text, text_contains=text_contains, value=value, max_timeout=max_timeout)

    def get_elements(self, selector, max_timeout=20):

        return self.app.get_current_page().get_elements(selector, max_timeout=max_timeout)

    def init(self):

        pass

    def _build_elements(self):

        self.elements = self.__class__.Elements(self)

    def _build_actions(self):

        self.actions = self.__class__.Actions(self)

    def screenshot(self, filename):

        self.self.__mini_proxy.get_screenshot_as_file(filename)
        return self

    def sleep(self, seconds):
        """seconds the length of time to sleep in seconds"""
        time.sleep(seconds)
        return self

    def raise_error(self, message=''):

        raise AssertionError(message)

    class Elements(object):
        def __init__(self, page):

            self.page = page

        def sleep(self, seconds):

            self.page.sleep(seconds)
            return self

    class Actions(object):
        def __init__(self, page):

            self.page = page

        def sleep(self, seconds):

            self.page.sleep(seconds)
            return self

        def turn_to_page(self, page_number):
            """翻页， 由具体页面实现"""

            raise NotImplementedError

        def screenshot(self, filename):

            self.page.screenshot(filename)
            return self
