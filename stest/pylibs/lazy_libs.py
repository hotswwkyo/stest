#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author: 思文伟
@Date: 2022/03/23
'''


class LazyLibs(object):
    class Appium(object):
        @property
        def MobileBy(self):
            from appium.webdriver.common.mobileby import MobileBy
            return MobileBy

        @property
        def webdriver(self):
            from appium import webdriver
            return webdriver

    class Selenium(object):
        @property
        def exceptions(cls):
            from selenium.common import exceptions
            return exceptions

        @property
        def ActionChains(self):
            from selenium.webdriver import ActionChains
            return ActionChains

        @property
        def Keys(self):
            from selenium.webdriver.common.keys import Keys
            return Keys

        @property
        def By(self):
            from selenium.webdriver.common.by import By
            return By

        @property
        def WebDriverWait(self):
            from selenium.webdriver.support.wait import WebDriverWait
            return WebDriverWait

        @property
        def webdriver(self):
            from selenium import webdriver
            return webdriver

        @property
        def WebElement(self):
            from selenium.webdriver.remote.webelement import WebElement
            return WebElement

    class Wechat(object):
        @property
        def minium(self):
            import minium
            return minium

        @property
        def miniconfig(self):
            from minium.framework import miniconfig
            return miniconfig