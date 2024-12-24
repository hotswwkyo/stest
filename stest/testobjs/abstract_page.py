#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author: 思文伟
@Date: 2022/03/22 17:23:26
'''

import time
import base64
import inspect
import subprocess

from ..utils import sutils
from ..utils import attrs_manager
from ..utils import attrs_marker
from ..core.errors import WindowNotFound
from ..dm import DRIVER_MANAGER
from ..dm import WIN_APP_DRIVER_HELPER
from ..pylibs.lazy_libs import LazyLibs
from ..utils.screenshot_capturer import ScreenshotCapturer


class AbstractPage(attrs_manager.AttributeManager):
    """ 抽象页 """

    DRIVER_MANAGER = attrs_marker.Const(DRIVER_MANAGER, "Driver管理器")
    WIN_APP_DRIVER_HELPER = attrs_marker.Const(WIN_APP_DRIVER_HELPER, "启动和关闭WinAppDriver.exe助手")

    def __init__(self, driver=None, alias=None, timeout=0.0, *args, **kwargs):
        """一般不建议创建页面的时候直接创建驱动实例，建议页面实例化后再调用页面提供的相关驱动实例化方法更好

        Args:
            driver: 驱动实例或者驱动名称
            alias: 在缓存中驱动实例的别名，可通过该别名来切换驱动实例，如果在缓存中已存在则直接切换到该实例
            timeout: 查找元素的默认超时时间
            args: 见DriverManager.create_driver
            kwargs: 见DriverManager.create_driver
        """

        self._dm = self.__class__.DRIVER_MANAGER
        self._dm.script_timeout = kwargs.pop("script_timeout", 5.0)
        self._dm.implicit_wait_timeout = kwargs.pop("implicit_wait_timeout", 0.0)

        if isinstance(driver, str):
            self.create_driver(driver, alias, *args, **kwargs)
        elif driver:
            self._dm.register_driver(driver, alias)

        self.timeout = timeout
        self._build_elements()
        self._build_actions()
        self.init()

    def init(self):

        pass

    def _build_elements(self):

        self.elements = self.__class__.Elements(self)

    def _build_actions(self):

        self.actions = self.__class__.Actions(self)

    @property
    def browser(self):

        return self.driver

    @property
    def driver(self):

        return self._dm.driver

    @property
    def window_app(self):

        return self._dm.driver

    @property
    def action_chains(self):
        """动作链对象"""

        return LazyLibs.Selenium().ActionChains(self.driver)

    @property
    def driver_manager(self):
        """Driver管理器"""

        return self._dm

    @property
    def index(self):
        """driver索引"""

        return self._dm.index

    @classmethod
    def startup_winappdriver(cls, executable_path, output_stream=None, auto_close_output_stream=False):
        """启动WinAppDriver.exe

        Args:
            executable_path: WinAppDriver.exe程序完整路径
            output_stream: 输出流
            auto_close_output_stream: 是否自动关闭output_stream
        """

        return cls.WIN_APP_DRIVER_HELPER.startup_winappdriver(executable_path, output_stream, auto_close_output_stream)

    @classmethod
    def shutdown_winappdriver(cls):
        """关闭WinAppDriver.exe"""

        return cls.WIN_APP_DRIVER_HELPER.shutdown_winappdriver()

    def open_url(self, url):

        self.driver_manager.open_url(url)
        return self

    def open_app(self, remote_url='http://127.0.0.1:4444/wd/hub', alias=None, **kwargs):

        kwargs['implicit_wait_timeout'] = kwargs.get('implicit_wait_timeout', 7.0)
        kwargs['command_executor'] = remote_url
        self._dm.open_app(alias=alias, **kwargs)
        return self

    def open_window_app(self, remote_url="http://127.0.0.1:4723", desired_capabilities={}, alias=None, window_name=None, splash_delay=0, exact_match=True, desktop_alias=None):
        """ 创建 Windows 应用程序驱动程序会话

        Args:
            remote_url: WinAppDriver or Appium server url
            desired_capabilities:用于创建 Windows 应用程序驱动程序会话的功能
                app Application identifier or executable full path Microsoft.MicrosoftEdge_8wekyb3d8bbwe!MicrosoftEdge

                appArguments Application launch arguments https://github.com/Microsoft/WinAppDriver

                appTopLevelWindow Existing application top level window to attach to 0xB822E2

                appWorkingDir 应用程序工作目录 (仅限经典应用程序) C:\\Temp

                platformName Target platform name Windows

                platformVersion Target platform version 1.0

            alias: 为创建的应用会话设置别名
            window_name: 要附加的窗口名称，通常在启动屏幕之后
            exact_match: 如果窗口名称不需要完全匹配，则设置为False
            desktop_alias: 为创建的桌面会话设置别名，将默认为“WindowDesktop”
        """

        if window_name:
            subprocess.Popen(desired_capabilities['app'])
            if splash_delay > 0:
                # print('Waiting %s seconds for splash screen' % splash_delay)
                self.sleep(splash_delay)
            return self.switch_window_app_by_name(remote_url, alias=alias, window_name=window_name, exact_match=exact_match, desktop_alias=desktop_alias, **desired_capabilities)
        self.driver_manager.open_desktop_session(remote_url, desktop_alias)
        self.driver_manager.open_window_app(
            remote_url, alias=alias, desired_capabilities=desired_capabilities)
        return self

    def switch_window_app_by_window_element(self, remote_url, window_element, alias=None, **kwargs):

        desired_caps = kwargs
        window_name = window_element.get_attribute("Name")
        if not window_name:
            msg = 'Error connecting webdriver to window "' + window_name + '". \n'
        else:
            msg = 'Error connecting webdriver to window(which window element tag name is:{}). \n'.format(
                window_element.tag_name)
        window = hex(int(window_element.get_attribute("NativeWindowHandle")))
        if "app" in desired_caps:
            del desired_caps["app"]
        if "platformName" not in desired_caps:
            desired_caps["platformName"] = "Windows"
        if "forceMjsonwp" not in desired_caps:
            desired_caps["forceMjsonwp"] = True
        desired_caps["appTopLevelWindow"] = window
        try:
            self.driver_manager.open_window_app(
                remote_url, alias=alias, desired_capabilities=desired_caps)
        except Exception as e:
            raise WindowNotFound(msg + str(e))
        return self

    def switch_window_app_by_name(self, remote_url, window_name, alias=None, timeout=5, exact_match=True, desktop_alias=None, **kwargs):

        desired_caps = kwargs
        self.driver_manager.open_desktop_session(remote_url, desktop_alias)
        window_xpath = '//Window[contains(@Name, "' + window_name + '")]'
        window_locator = window_name
        try:
            if exact_match:
                window = self.find_element_by_name(window_locator)
            else:
                window = self.find_element_by_xpath(window_xpath)
            window = hex(int(window.get_attribute("NativeWindowHandle")))
        except Exception:
            try:
                if exact_match:
                    window = self.find_element_by_name(window_locator, timeout=timeout)
                else:
                    window = self.find_element_by_xpath(window_xpath, timeout=timeout)
                window = hex(int(window.get_attribute("NativeWindowHandle")))
            except Exception as e:
                msg = 'Error finding window "{}" in the desktop session. Is it a top level window handle? \n {}'
                raise LazyLibs.Selenium().exceptions.NoSuchWindowException(msg.format(window_name, str(e)))
        if "app" in desired_caps:
            del desired_caps["app"]
        if "platformName" not in desired_caps:
            desired_caps["platformName"] = "Windows"
        if "forceMjsonwp" not in desired_caps:
            desired_caps["forceMjsonwp"] = True
        desired_caps["appTopLevelWindow"] = window
        # global application
        try:
            # print('Connecting to window_name "%s".' % window_name)
            self.driver_manager.open_window_app(
                remote_url, alias=alias, desired_capabilities=desired_caps)
        except Exception as e:
            msg = 'Error connecting webdriver to window "{}" .\n {}'
            raise WindowNotFound(msg.format(window_name, str(e)))
        return self

    def create_driver(self, driver_name, alias=None, *driver_args, **driver_kwargs):

        return self._dm.create_driver(driver_name, alias=alias, *driver_args, **driver_kwargs)

    def close_driver(self):
        self._dm.close_driver()
        return self

    def close_all_drivers(self):
        self._dm.close_all_drivers()
        return self

    def open_browser(self, browser_name, url=None, alias=None, *args, **kwargs):

        self._dm.open_browser(browser_name, url, alias, *args, **kwargs)
        return self

    def ie(self, url=None, alias=None, *args, **kwargs):

        self.driver_manager.ie(url=url, alias=alias, *args, **kwargs)
        return self

    def chrome(self, url=None, alias=None, *args, **kwargs):
        """Creates a new instance of the chrome driver.

        Starts the service and then creates new instance of chrome driver.

        Parameters
        ----------
        kwargs : refer to the `selenium.webdriver.Chome`
        """
        # args = ()
        self.driver_manager.chrome(url=url, alias=alias, *args, **kwargs)
        return self

    def firefox(self, url=None, alias=None, *args, **kwargs):

        self.driver_manager.firefox(url=url, alias=alias, *args, **kwargs)
        return self

    def switch_driver(self, index_or_alias):
        self._dm.switch_driver(index_or_alias)
        return self

    switch_browser = switch_driver
    switch_window_app = switch_driver

    @staticmethod
    def is_web_element(obj):

        return isinstance(obj, LazyLibs.Selenium().WebElement)

    def _validate_timeout(self, timeout):

        return isinstance(timeout, (int, float))

    def maximize_window(self):

        self.driver.maximize_window()
        return self

    def minimize_window(self):

        self.driver.minimize_window()
        return self

    def find_element_by_id(self, element_id, timeout=None, parent=None):
        """Finds an element by id.

        @param element_id - The id of the element to be found.

        @return WebElement - the element if it was found

        @raise NoSuchElementException - if the element wasn't found

        @usage  element = driver.find_element_by_id('foo')
        """

        return self.find_element(by=LazyLibs.Selenium().By.ID, locator=element_id, timeout=timeout, parent=parent)

    def find_elements_by_id(self, element_id, timeout=None, parent=None):
        """
        Finds multiple elements by id.

        @param element_id - The id of the elements to be found.

        @return list of WebElement - a list with elements if any was found.  An empty list if not

        @usage  elements = driver.find_elements_by_id('foo')
        """

        return self.find_elements(by=LazyLibs.Selenium().By.ID, locator=element_id, timeout=timeout, parent=parent)

    def find_element_by_xpath(self, xpath, timeout=None, parent=None):
        """
        Finds an element by xpath.

        @param xpath - The xpath locator of the element to find.

        @return WebElement - the element if it was found

        @raise NoSuchElementException - if the element wasn't found

        @usage  element = driver.find_element_by_xpath('//div/td[1]')
        """

        return self.find_element(by=LazyLibs.Selenium().By.XPATH, locator=xpath, timeout=timeout, parent=parent)

    def find_elements_by_xpath(self, xpath, timeout=None, parent=None):
        """
        Finds multiple elements by xpath.

        @param xpath - The xpath locator of the elements to be found.

        @return list of WebElement - a list with elements if any was found.  An empty list if not

        @usage  elements = driver.find_elements_by_xpath("//div[contains(@class, 'foo')]")
        """

        return self.find_elements(by=LazyLibs.Selenium().By.XPATH, locator=xpath, timeout=timeout, parent=parent)

    def find_element_by_link_text(self, link_text, timeout=None, parent=None):
        """
        Finds an element by link text.

        @param link_text: The text of the element to be found.

        @return WebElement - the element if it was found

        @raise NoSuchElementException - if the element wasn't found

        @usage  element = driver.find_element_by_link_text('Sign In')
        """

        return self.find_element(by=LazyLibs.Selenium().By.LINK_TEXT, locator=link_text, timeout=timeout, parent=parent)

    def find_elements_by_link_text(self, link_text, timeout=None, parent=None):
        """
        Finds elements by link text.

        @param link_text: The text of the elements to be found.

        @return list of webelement - a list with elements if any was found.  an empty list if not

        @usage  elements = driver.find_elements_by_link_text('Sign In')
        """

        return self.find_elements(by=LazyLibs.Selenium().By.LINK_TEXT, locator=link_text, timeout=timeout, parent=parent)

    def find_element_by_partial_link_text(self, link_text, timeout=None, parent=None):
        """
        Finds an element by a partial match of its link text.

        @param link_text The text of the element to partially match on.

        @return WebElement - the element if it was found

        @raise NoSuchElementException - if the element wasn't found

        @usage element = driver.find_element_by_partial_link_text('Sign')
        """

        return self.find_element(by=LazyLibs.Selenium().By.PARTIAL_LINK_TEXT, locator=link_text, timeout=timeout, parent=parent)

    def find_elements_by_partial_link_text(self, link_text, timeout=None, parent=None):
        """
        Finds elements by a partial match of their link text.

        @param link_text: The text of the element to partial match on.

        @return list of webelement - a list with elements if any was found.  an empty list if not

        @usage:
            elements = driver.find_elements_by_partial_link_text('Sign')
        """

        return self.find_elements(by=LazyLibs.Selenium().By.PARTIAL_LINK_TEXT, locator=link_text, timeout=timeout, parent=parent)

    def find_element_by_name(self, name, timeout=None, parent=None):
        """
        Finds an element by name.

        @param name: The name of the element to find.

        @return WebElement - the element if it was found

        @raise NoSuchElementException - if the element wasn't found

        @usage
            element = driver.find_element_by_name('foo')
        """

        return self.find_element(by=LazyLibs.Selenium().By.NAME, locator=name, timeout=timeout, parent=parent)

    def find_elements_by_name(self, name, timeout=None, parent=None):
        """
        Finds elements by name.

        @param name: The name of the elements to find.

        @return list of webelement - a list with elements if any was found.  an empty list if not

        @usage:
            elements = driver.find_elements_by_name('foo')
        """

        return self.find_elements(by=LazyLibs.Selenium().By.NAME, locator=name, timeout=timeout, parent=parent)

    def find_element_by_tag_name(self, name, timeout=None, parent=None):
        """
        Finds an element by tag name.

        @param name - name of html tag (eg: h1, a, span)

        @return WebElement - the element if it was found

        @raise NoSuchElementException - if the element wasn't found

        @usage
            element = driver.find_element_by_tag_name('h1')
        """

        return self.find_element(by=LazyLibs.Selenium().By.TAG_NAME, locator=name, timeout=timeout, parent=parent)

    def find_elements_by_tag_name(self, name, timeout=None, parent=None):
        """
        Finds elements by tag name.

        @param name - name of html tag (eg: h1, a, span)

        @return list of WebElement - a list with elements if any was found.  An empty list if not

        @usage
            elements = driver.find_elements_by_tag_name('h1')
        """

        return self.find_elements(by=LazyLibs.Selenium().By.TAG_NAME, locator=name, timeout=timeout, parent=parent)

    def find_element_by_class_name(self, name, timeout=None, parent=None):
        """
        Finds an element by class name.

        @param name The class name of the element to find.

        @return WebElement - the element if it was found

        @raise NoSuchElementException - if the element wasn't found

        @usage:
            element = driver.find_element_by_class_name('foo')
        """

        return self.find_element(by=LazyLibs.Selenium().By.CLASS_NAME, locator=name, timeout=timeout, parent=parent)

    def find_elements_by_class_name(self, name, timeout=None, parent=None):
        """
        Finds elements by class name.

        @param name The class name of the elements to find.

        @return list of WebElement - a list with elements if any was found.  An empty list if not

        @usage
            elements = driver.find_elements_by_class_name('foo')
        """

        return self.find_elements(by=LazyLibs.Selenium().By.CLASS_NAME, locator=name, timeout=timeout, parent=parent)

    def find_element_by_css_selector(self, css_selector, timeout=None, parent=None):
        """
        Finds an element by css selector.

        @param css_selector - CSS selector string, ex: 'a.nav#home'

        @return WebElement - the element if it was found

        @raise NoSuchElementException - if the element wasn't found

        @usage
            element = driver.find_element_by_css_selector('#foo')
        """

        return self.find_element(by=LazyLibs.Selenium().By.CSS_SELECTOR, locator=css_selector, timeout=timeout, parent=parent)

    def find_elements_by_css_selector(self, css_selector, timeout=None, parent=None):
        """
        Finds elements by css selector.

        @param css_selector - CSS selector string, ex: 'a.nav#home'

        @return list of WebElement - a list with elements if any was found.  An empty list if not

        @usage
            elements = driver.find_elements_by_css_selector('.foo')
        """

        return self.find_elements(by=LazyLibs.Selenium().By.CSS_SELECTOR, locator=css_selector, timeout=timeout, parent=parent)

    def find_element(self, by="id", locator=None, timeout=None, parent=None):
        """查找匹配的元素

        Args:
            - by       - 查找方式
            - locator  - 元素定位器
            - timeout  - 查找元素超时时间
            - parent   - 父元素,提供则从父元素下查找

        Raises:
            - NoSuchElementException - if the element wasn't found
            - TimeoutException - if the element wasn't found when time out

        Returns:
            - WebElement - the element if it was found
        """

        if not (timeout and self._validate_timeout(timeout)):
            timeout = self.timeout

        if parent and self.is_web_element(parent):
            driver = parent.parent
        else:
            driver = self.browser

        # 如果设置的超时时间无效或者超时时间小于0，则不会执行超时
        if not (self._validate_timeout(timeout) and timeout > 0):
            return driver.find_element(by, locator)
        message = "{} with locator '{}' not found".format(by, locator)
        try:
            element = LazyLibs.Selenium().WebDriverWait(driver, timeout).until(lambda x: x.find_element(by, locator))
        except LazyLibs.Selenium().exceptions.TimeoutException as exc:
            message = message + "in {timeout}".format(timeout=timeout)
            screen = getattr(exc, 'screen', None)
            stacktrace = getattr(exc, 'stacktrace', None)
            raise LazyLibs.Selenium().exceptions.TimeoutException(message, screen, stacktrace)
        except LazyLibs.Selenium().exceptions.NoSuchWindowException as e:
            message = message + "," + e.msg
            screen = getattr(e, 'screen', None)
            stacktrace = getattr(e, 'stacktrace', None)
            raise LazyLibs.Selenium().exceptions.NoSuchWindowException(message, screen, stacktrace)
        except Exception as e:
            raise e
        else:
            return element

    def find_elements(self, by="id", locator=None, timeout=None, parent=None):
        """查找所有匹配的元素

        Args:
            - by - 查找方式
            - locator - 元素定位器
            - timeout - 查找元素超时时间
            - parent - 父元素,提供则从父元素下查找

        Returns:
            - list of WebElement - a list with elements if any was found. An empty list if not
        """

        if not (timeout and self._validate_timeout(timeout)):
            timeout = self.timeout

        if parent and self.is_web_element(parent):
            driver = parent.parent
        else:
            driver = self.browser
        # 如果设置的超时时间无效或者超时时间小于0，则不会执行超时
        if not (self._validate_timeout(timeout) and timeout > 0):
            return driver.find_elements(by, locator)
        message = "{} with locator '{}' not found.".format(by, locator)
        try:
            elements = LazyLibs.Selenium().WebDriverWait(
                driver, timeout).until(lambda x: x.find_elements(by, locator))
        except LazyLibs.Selenium().exceptions.TimeoutException as t:
            message = message + "in {timeout}".format(timeout=timeout)
            screen = getattr(t, 'screen', None)
            stacktrace = getattr(t, 'stacktrace', None)
            # raise TimeoutException(message, screen, stacktrace)
            # print(message)
            return []
        except LazyLibs.Selenium().exceptions.NoSuchWindowException as e:
            message = message + "," + e.message
            screen = getattr(e, 'screen', None)
            stacktrace = getattr(e, 'stacktrace', None)
            raise LazyLibs.Selenium().exceptions.NoSuchWindowException(message, screen, stacktrace)
        except Exception as e:
            raise e
        else:
            return elements

    def find_element_by_ios_uiautomation(self, uia_string, timeout=None):
        """Finds an element by uiautomation in iOS.

        Args:
            uia_string (str): The element name in the iOS UIAutomation library

        Usage:
            driver.find_element_by_ios_uiautomation('.elements()[1].cells()[2]')

        Returns:
            `appium.webdriver.webelement.WebElement`

        :rtype: `MobileWebElement`
        """
        return self.find_element(by=LazyLibs.Appium().MobileBy.IOS_UIAUTOMATION, locator=uia_string, timeout=timeout, parent=None)

    def find_elements_by_ios_uiautomation(self, uia_string, timeout=None):
        """Finds elements by uiautomation in iOS.

        Args:
            uia_string: The element name in the iOS UIAutomation library

        Usage:
            driver.find_elements_by_ios_uiautomation('.elements()[1].cells()[2]')

        Returns:
            :obj:`list` of :obj:`appium.webdriver.webelement.WebElement`

        :rtype: list of `MobileWebElement`
        """
        return self.find_elements(by=LazyLibs.Appium().MobileBy.IOS_UIAUTOMATION, locator=uia_string, timeout=timeout, parent=None)

    def find_element_by_ios_predicate(self, predicate_string, timeout=None):
        """Find an element by ios predicate string.

        Args:
            predicate_string (str): The predicate string

        Usage:
            driver.find_element_by_ios_predicate('label == "myLabel"')

        Returns:
            `appium.webdriver.webelement.WebElement`

        :rtype: `MobileWebElement`
        """
        return self.find_element(by=LazyLibs.Appium().MobileBy.IOS_PREDICATE, locator=predicate_string, timeout=timeout, parent=None)

    def find_elements_by_ios_predicate(self, predicate_string, timeout=None):
        """Finds elements by ios predicate string.

        Args:
            predicate_string (str): The predicate string

        Usage:
            driver.find_elements_by_ios_predicate('label == "myLabel"')

        Returns:
            :obj:`list` of :obj:`appium.webdriver.webelement.WebElement`

        :rtype: list of `MobileWebElement`
        """
        return self.find_elements(by=LazyLibs.Appium().MobileBy.IOS_PREDICATE, locator=predicate_string, timeout=timeout, parent=None)

    def find_element_by_ios_class_chain(self, class_chain_string, timeout=None):
        """Find an element by ios class chain string.

        Args:
            class_chain_string (str): The class chain string

        Usage:
            driver.find_element_by_ios_class_chain('XCUIElementTypeWindow/XCUIElementTypeButton[3]')

        Returns:
            `appium.webdriver.webelement.WebElement`

        :rtype: `MobileWebElement`
        """
        return self.find_element(by=LazyLibs.Appium().MobileBy.IOS_CLASS_CHAIN, locator=class_chain_string, timeout=timeout, parent=None)

    def find_elements_by_ios_class_chain(self, class_chain_string, timeout=None):
        """Finds elements by ios class chain string.

        Args:
            class_chain_string (str): The class chain string

        Usage:
            driver.find_elements_by_ios_class_chain('XCUIElementTypeWindow[2]/XCUIElementTypeAny[-2]')

        Returns:
            :obj:`list` of :obj:`appium.webdriver.webelement.WebElement`

        :rtype: list of `MobileWebElement`
        """
        return self.find_elements(by=LazyLibs.Appium().MobileBy.IOS_CLASS_CHAIN, locator=class_chain_string, timeout=timeout, parent=None)

    def find_element_by_android_uiautomator(self, uia_string, timeout=None):

        return self.find_element(by=LazyLibs.Appium().MobileBy.ANDROID_UIAUTOMATOR, locator=uia_string, timeout=timeout, parent=None)

    def find_elements_by_android_uiautomator(self, uia_string, timeout=None):

        return self.find_elements(by=LazyLibs.Appium().MobileBy.ANDROID_UIAUTOMATOR, locator=uia_string, timeout=timeout, parent=None)

    def find_element_by_android_viewtag(self, tag, timeout=None):
        """Finds element by [View#tags](https://developer.android.com/reference/android/view/View#tags) in Android.

        It works with [Espresso Driver](https://github.com/appium/appium-espresso-driver).

        Args:
            tag (str): The tag name of the view to look for

        Usage:
            driver.find_element_by_android_viewtag('a tag name')

        Returns:
            `appium.webdriver.webelement.WebElement`

        :rtype: `MobileWebElement`
        """
        return self.find_element(by=LazyLibs.Appium().MobileBy.ANDROID_VIEWTAG, locator=tag, timeout=timeout, parent=None)

    def find_elements_by_android_viewtag(self, tag, timeout=None):
        """Finds element by [View#tags](https://developer.android.com/reference/android/view/View#tags) in Android.

        It works with [Espresso Driver](https://github.com/appium/appium-espresso-driver).

        Args:
            tag (str): The tag name of the view to look for

        Usage:
            driver.find_elements_by_android_viewtag('a tag name')

        Returns:
            :obj:`list` of :obj:`appium.webdriver.webelement.WebElement`

        :rtype: list of `MobileWebElement`
        """
        return self.find_elements(by=LazyLibs.Appium().MobileBy.ANDROID_VIEWTAG, locator=tag, timeout=timeout, parent=None)

    def find_element_by_image(self, img_path, timeout=None):
        """Finds a portion of a screenshot by an image.

        Uses driver.find_image_occurrence under the hood.

        Args:
            img_path (str): a string corresponding to the path of a image

        Returns:
            `appium.webdriver.webelement.WebElement`

        :rtype: `MobileWebElement`
        """
        with open(img_path, 'rb') as i_file:
            b64_data = base64.b64encode(i_file.read()).decode('UTF-8')

        return self.find_element(by=LazyLibs.Appium().MobileBy.IMAGE, locator=b64_data, timeout=timeout, parent=None)

    def find_elements_by_image(self, img_path, timeout=None):
        """Finds a portion of a screenshot by an image.

        Uses driver.find_image_occurrence under the hood. Note that this will
        only ever return at most one element

        Args:
            img_path (str): a string corresponding to the path of a image

        Return:
            :obj:`list` of :obj:`appium.webdriver.webelement.WebElement`

        :rtype: list of `MobileWebElement`
        """
        with open(img_path, 'rb') as i_file:
            b64_data = base64.b64encode(i_file.read()).decode('UTF-8')

        return self.find_elements(by=LazyLibs.Appium().MobileBy.IMAGE, locator=b64_data, timeout=timeout, parent=None)

    def find_element_by_accessibility_id(self, accessibility_id, timeout=None):
        """Finds an element by accessibility id.

        Args:
            accessibility_id (str): A string corresponding to a recursive element search using the
                Id/Name that the native Accessibility options utilize

        Usage:
            driver.find_element_by_accessibility_id()

        Returns:
            `appium.webdriver.webelement.WebElement`

        :rtype: `MobileWebElement`
        """
        return self.find_element(by=LazyLibs.Appium().MobileBy.ACCESSIBILITY_ID, locator=accessibility_id, timeout=timeout, parent=None)

    def find_elements_by_accessibility_id(self, accessibility_id, timeout=None):
        """Finds elements by accessibility id.

        Args:
            accessibility_id (str): a string corresponding to a recursive element search using the
                Id/Name that the native Accessibility options utilize

        Usage:
            driver.find_elements_by_accessibility_id()

        Returns:
            :obj:`list` of :obj:`appium.webdriver.webelement.WebElement`

        :rtype: list of `MobileWebElement`
        """
        return self.find_elements(by=LazyLibs.Appium().MobileBy.ACCESSIBILITY_ID, locator=accessibility_id, timeout=timeout, parent=None)

    def find_element_by_custom(self, selector, timeout=None):
        """Finds an element in conjunction with a custom element finding plugin

        Args:
            selector (str): a string of the form "module:selector", where "module" is
                the shortcut name given in the customFindModules capability, and
                "selector" is the string that will be passed to the custom element
                finding plugin itself

        Usage:
            driver.find_element_by_custom("foo:bar")

        Returns:
            `appium.webdriver.webelement.WebElement`

        :rtype: `MobileWebElement`
        """
        return self.find_element(by=LazyLibs.Appium().MobileBy.CUSTOM, locator=selector, timeout=timeout, parent=None)

    def find_elements_by_custom(self, selector, timeout=None):
        """Finds elements in conjunction with a custom element finding plugin

        Args:
            selector: a string of the form "module:selector", where "module" is
                the shortcut name given in the customFindModules capability, and
                "selector" is the string that will be passed to the custom element
                finding plugin itself

        Usage:
            driver.find_elements_by_custom("foo:bar")

        Returns:
            :obj:`list` of :obj:`appium.webdriver.webelement.WebElement`

        :rtype: list of `MobileWebElement`
        """
        return self.find_elements(by=LazyLibs.Appium().MobileBy.CUSTOM, locator=selector, timeout=timeout, parent=None)

    def sleep(self, seconds):
        """seconds the length of time to sleep in seconds"""
        time.sleep(seconds)
        return self

    def wait_until_contains(self, text, timeout=None):
        """等待文本出现在当前页面"""

        locator = "//*contains(., %s)" % sutils.escape_xpath_value(text)
        try:
            self.find_element_by_xpath(locator, timeout=timeout)
        except Exception:
            message = "Text '%s' did not appear in %s." % (text, timeout)
            raise LazyLibs.Selenium().exceptions.TimeoutException(message)

    @classmethod
    def wait_until(cls, callable_method, message="", timeout=None, poll_frequency=0.2, ignored_exceptions=None):

        if timeout is None:
            timeout = 0.0
        exceptions = [LazyLibs.Selenium().exceptions.NoSuchElementException]
        if ignored_exceptions is not None:
            try:
                exceptions.extend(iter(ignored_exceptions))
            except TypeError:
                exceptions.append(ignored_exceptions)
        _ignored_exceptions = tuple(exceptions)
        end_time = time.time() + timeout
        not_found = None
        while True:
            try:
                if callable_method():
                    return
            except _ignored_exceptions as err:
                not_found = str(err)
            else:
                not_found = None
            if time.time() > end_time:
                break
            time.sleep(poll_frequency)
        raise LazyLibs.Selenium().exceptions.TimeoutException(not_found or message)

    def execute_script(self, script, *args):

        return self.driver.execute_script(script, *args)

    def click_element_by_javascript(self, web_element):

        script = "arguments[0].click();"
        return self.execute_script(script, web_element)

    def scroll_to(self, xpos, ypos):
        """scroll to any position of an opened window of browser"""

        js_code = "window.scrollTo(%s, %s);" % (xpos, ypos)
        self.execute_script(js_code)

    def scroll_into_view(self, web_element):

        js_code = 'arguments[0].scrollIntoView();'
        self.execute_script(js_code, web_element)

    def scroll_to_bottom(self):

        bottom = self.execute_script("return document.body.scrollHeight;")
        self.scroll_to(0, bottom)

    def scroll_to_top(self):

        self.scroll_to(0, 0)

    def drag_and_drop(self, source, target):

        self.action_chains.drag_and_drop(source, target).perform()

    def screenshot(self, file_name):
        """截图并保存

        Args:
            file_name: 保存截图文件的完整路径名
        Usage:
            page.screenshot("E:\\SevenPytest\\screenshots\\debug.png")
        """
        return ScreenshotCapturer.screenshot(file_name, self.driver)

    @property
    def session_id(self):
        """Returns the currently active browser session id"""

        return self.driver.session_id

    @property
    def page_source(self):
        """Returns the entire HTML source of the current page or frame."""

        return self.driver.page_source

    @property
    def title(self):
        """Returns the title of the current page."""

        return self.driver.title

    @property
    def active_element(self):
        """Returns the element with focus, or BODY if nothing has focus.

        @see selenium.webdriver.remote.switch_to.SwitchTo.active_element
        @usage element = page.active_element
        """
        return self.driver.switch_to.active_element

    @property
    def alert(self):
        """Switches focus to an alert on the page.

        @see selenium.webdriver.remote.switch_to.SwitchTo.alert
        @usage alert = page.alert
        """
        return self.driver.switch_to.alert

    def select_frame(self, reference):
        """切换frame

        @param reference frame id name index 或 webelement 对象
        @see selenium.webdriver.remote.switch_to.SwitchTo.frame()
        @usage page.select_frame()
        """
        self.driver.switch_to.frame(reference)

    def default_frame(self):
        """ Switch focus to the default frame.

        @see selenium.webdriver.remote.switch_to.SwitchTo.default_content()
        @usage page.default_frame()
        """
        self.driver.switch_to.default_content()
        return self

    def parent_frame(self):
        """嵌套frame时，可以从子frame切回父frame

        @see selenium.webdriver.remote.switch_to.SwitchTo.parent_frame()
        @usage page.parent_frame()
        """

        self.driver.switch_to.parent_frame()

    @property
    def current_window_handle(self):

        return self.driver.current_window_handle

    @property
    def window_handles(self):

        return self.driver.window_handles

    def switch_window(self, window_name_or_handle):
        """切换浏览器窗口

        @param window_name_or_handle 窗口句柄或窗口名
        """
        self.driver.switch_to.window(window_name_or_handle)

    def switch_current_window(self):
        """切换到当前浏览器"""

        self.switch_window(self.current_window_handle)
        return self

    @property
    def window_infos_maps(self):
        """所有窗口信息

        @return 返回列表 [{"handle":window handle, "name": window name, "title": window title, "url": window url}, ...]
        """
        infos_maps = []
        try:
            source_handle = self.current_window_handle
        except LazyLibs.Selenium().exceptions.NoSuchWindowException:
            source_handle = None
        try:
            for handle in self.window_handles:
                self.driver.switch_to.window(handle)
                infos_maps.append(self._get_window_infos_map(handle))
        finally:
            if source_handle:
                self.driver.switch_to.window(source_handle)
        return infos_maps

    def _get_window_infos_map(self, handle):

        title = self.driver.title
        try:
            name = self.execute_script("return window.name;")
        except Exception:
            name = title
        try:
            current_url = self.driver.current_url
        except Exception:
            current_url = None

        infos = {"handle": handle, "name": name, "title": title, "url": current_url}
        return infos

    def switch_window_by_title(self, title, matcher=None, timeout=None):
        """根据标题切换窗口

        Args:
            title: 窗口标题
            matcher: 匹配函数，接收两个参数，遍历传入每一个窗口的标题给第一个参数，要打开的窗口标题传给第二个参数，匹配返回True否则返回False
            timeout: 超时时间
        """
        def _switch_window_by_title():
            be_found = False
            for win_handle in self.window_handles:
                self.switch_window(win_handle)
                info = self._get_window_infos_map(win_handle)
                if inspect.isfunction(matcher):
                    if matcher(info["title"], title):
                        be_found = True
                        break
                else:
                    if info["title"] == title:
                        be_found = True
                        break
            return be_found

        message = "No window matching title(%s)" % title
        self.wait_until(_switch_window_by_title, message=message, timeout=timeout)
        return self

    def switch_window_by_url(self, url, matcher=None, timeout=None):
        """根据url切换窗口

        @see select_window_by_url(self, url, matcher=None)
        """
        def _switch_window_by_url():
            be_found = False
            for win_handle in self.window_handles:
                self.switch_window(win_handle)
                info = self._get_window_infos_map(win_handle)
                if inspect.isfunction(matcher):
                    if matcher(info["url"], url):
                        be_found = True
                        break
                else:
                    if info["url"] == url:
                        be_found = True
                        break
            return be_found

        message = "No window matching url(%s)" % url
        self.wait_until(_switch_window_by_url, message=message, timeout=timeout)
        return self

    def set_window_size(self, width, height, window_handle='current'):
        """Sets current windows size to given ``width`` and ``height``

        @see WebDriver.set_window_size(self, width, height, windowHandle='current')
        """

        self.driver.set_window_size(width, height, window_handle)
        return self

    def get_window_size(self, window_handle='current'):
        """Gets the width and height of the current window.

        @see WebDriver.get_window_size(self, windowHandle='current')
        """
        return self.driver.get_window_size(window_handle)

    def set_window_position(self, x, y, window_handle='current'):

        self.driver.set_window_position(self, x, y, window_handle)
        return self

    def get_window_position(self, window_handle='current'):

        return self.driver.get_window_position(window_handle)

    def refresh(self):
        """刷新当前页面"""

        self.browser.refresh()
        return self

    def hide_keyboard(self, key_name=None, key=None, strategy=None):
        self.driver.hide_keyboard(key_name=key_name, key=key, strategy=strategy)
        return self

    def keyevent(self, keycode, metastate=None):
        """Sends a keycode to the android device.

        @see appium.webdriver.exceptions.keyboard.Keyboard.keyevent
        """
        self.driver.keyevent(keycode, metastate=metastate)
        return self

    def press_keycode(self, keycode, metastate=None, flags=None):
        """Sends a keycode to the device.

        Android only. Possible keycodes can be found in http://developer.android.com/reference/android/view/KeyEvent.html
        @see appium.webdriver.exceptions.keyboard.Keyboard.press_keycode
        """
        self.driver.press_keycode(keycode, metastate=metastate, flags=flags)
        return self

    def create_select_element_wrapper(self, select_element):
        """创建操作html select 元素的包装器

        Args:
            select_element: select标签元素

        Returns: 返回 Select 实例
            提供以下属性：
                options 返回select元素的所有选项
                all_selected_options 返回所有被选中的选项
                first_selected_option 第一个选中项

            提供以下方法：
                select_by_value(value) 通过选项中的value属性值选中选项
                select_by_index(index)
                select_by_visible_text(text) 通过选项中的文本选中选项 - <option>text</option>

                deselect_all()
                deselect_by_value(value)
                deselect_by_index(index)
                deselect_by_visible_text(text)

        See: selenium.webdriver.support.ui.Select
        """

        return LazyLibs.Selenium().Select(select_element)

    def close_current_window(self):
        """ Closes the current window.

        @see selenium.webdriver.remote.webdriver.close()
        """
        self.driver.close()

    def is_element_enabled(self, element):
        """判断元素是否可用"""

        return (element.is_enabled() and element.get_attribute("readonly") is None)

    def get_value(self, element):

        return element.get_attribute("value")

    @classmethod
    def raise_no_such_element_exc(cls, message):

        raise LazyLibs.Selenium().exceptions.NoSuchElementException(message)

    @classmethod
    def join_xpaths(cls, *xpaths):
        def join_two_xpath(x1, x2):
            """拼接xpath"""

            slash = '/'
            if x2.strip() == "":
                return x1
            if x1.endswith(slash) and x2.startswith(slash):
                return x1 + x2[1:]
            elif not x1.endswith(slash) and x2.startswith(slash):
                return x1 + x2
            elif x1.endswith(slash) and not x2.startswith(slash):
                return x1 + x2
            else:
                return x1 + slash + x2

        first = xpaths[0]
        others = xpaths[1:]
        full_xpath = first
        for one in others:
            full_xpath = join_two_xpath(full_xpath, one)
        return full_xpath

    class Elements(object):
        def __init__(self, page):

            self.page = page

        def sleep(self, seconds):
            """延时"""

            self.page.sleep(seconds)
            return self

    class Actions(object):
        def __init__(self, page):

            self.page = page

        def sleep(self, seconds):
            """延时"""

            self.page.sleep(seconds)
            return self

        def turn_to_page(self, page_number):
            """翻页， 由具体页面实现"""

            raise NotImplementedError
