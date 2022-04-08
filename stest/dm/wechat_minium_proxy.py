#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author: 思文伟
@Date: 2022/04/06
'''

import os
import base64
import warnings
import datetime
import tempfile

from ..pylibs.lazy_libs import LazyLibs


class WechatMiniumProxy(object):

    DEVICE_INFO = {}
    DEFAULT_MINI_CONFIG = {
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

    def __init__(self):

        self.mini = None
        self.native = None
        self.log_message_list = []

    def init_minium(self, mini_config_dict_or_file_path=None):

        self.set_config(mini_config_dict_or_file_path)
        if not self.testconfig.report_usage:
            LazyLibs.Wechat().minium.wechatdriver.minium_log.existFlag = 1
        self.set_minium()
        self.set_native()

    def set_config(self, mini_config_dict_or_file_path=None):

        if mini_config_dict_or_file_path is None:
            self.mini_config = self.DEFAULT_MINI_CONFIG
        elif isinstance(mini_config_dict_or_file_path, dict):
            self.mini_config = LazyLibs.Wechat().miniconfig.MiniConfig(mini_config_dict_or_file_path)
        elif isinstance(mini_config_dict_or_file_path, str):
            self.mini_config = LazyLibs.Wechat().miniconfig.MiniConfig.from_file(mini_config_dict_or_file_path)
        else:
            raise ValueError("mini_config_dict_or_file_path's value must be str or dictionary")
        self.testconfig = LazyLibs.Wechat().miniconfig.MiniConfig(self.mini_config)

    def release_minium(self):

        if not self.testconfig.close_ide and self.mini:
            self.mini.shutdown()
        if self.testconfig.platform != 'ide' and not self.testconfig.close_ide:
            self.native.stop_wechat() if self.native else print("Native module has not start, there is no need to stop WeChat")
        if self.native:
            self.native.release()
        self.mini = None
        self.native = None

    @property
    def page(self):

        return self.mini.app.get_current_page()

    def get_screenshot_as_file(self, filename):
        """
        :Args:
         - filename: The full path you wish to save your screenshot to. This
           should end with a `.png` extension.
        """
        if not filename.lower().endswith('.png'):
            warnings.warn("name used for saved screenshot does not match file " "type. It should end with a `.png` extension", UserWarning)

        return self.native.screen_shot(filename)

    def get_screenshot_as_base64(self):

        filename = tempfile.mktemp(suffix=".png")
        self.get_screenshot_as_file(filename)
        raw_data = b""
        if os.path.exists(filename):
            with open(filename, "rb") as f:
                raw_data = f.read()
            os.unlink(filename)
        else:
            FileNotFoundError("No such file: {}".format(filename))
        return base64.b64encode(raw_data).decode()

    def set_minium(self):

        if self.mini is None:
            self.mini = LazyLibs.Wechat().minium.Minium(project_path=self.testconfig.project_path, test_port=self.testconfig.test_port, dev_tool_path=self.testconfig.dev_tool_path)
            if self.testconfig.enable_app_log:

                def mini_log_added(message):
                    dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    message["dt"] = dt
                    self.log_message_list.append(message)

                self.mini.connection.register("App.logAdded", mini_log_added)
                self.mini.app.enable_log()
        return self.mini

    def set_native(self):

        if self.native is None:
            self.native = LazyLibs.Wechat().minium.native.get_native_driver(self.testconfig.platform, self.testconfig.device_desire)
            if self.testconfig.platform != "ide" and not self.testconfig.close_ide:
                self.set_minium()
                self.native.start_wechat()
                path = self.mini.enable_remote_debug(use_push=self.testconfig.use_push, connect_timeout=self.testconfig.remote_connect_timeout)
                if not self.testconfig.use_push:
                    self.native.connect_weapp(path)
                    self.mini.connection.wait_for(method="App.initialized")
