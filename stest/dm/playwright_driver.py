#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import copy
import base64
from typing import Optional
from typing import List
from stest import settings
from stest.core.errors import NoOpendPageError
from stest.core.errors import NoOpendContextError
from stest.core.errors import NoOpendBrowserError


from playwright.sync_api import Page
from playwright.sync_api import Browser
from playwright.sync_api import Playwright
from playwright.sync_api import BrowserType
from playwright.sync_api import BrowserContext
from playwright.sync_api import sync_playwright


class SupportBrowserType(object):
    WEBKIT = "webkit"
    FIREFOX = "firefox"
    CHROMIUM = "chromium"


class PlaywrightDriver(object):

    PLAYWRIGHT = "playwright"
    AUTO_STOP_PLAYWRIGHT = "AUTO_STOP_PLAYWRIGHT_AFTER_ALL_TESTS_ARE_EXECUTED"
    already_set_auto_stop_playwright = False

    def __init__(self, playwright: Optional[Playwright] = None):

        if not isinstance(playwright, Playwright):
            pw = getattr(settings, self.PLAYWRIGHT, None)
            if not pw:
                self.playwright = sync_playwright().start()
                setattr(settings, self.PLAYWRIGHT, self.playwright)
            else:
                self.playwright = pw
        else:
            self.playwright = playwright
            settings.playwright = playwright

        if not self.already_set_auto_stop_playwright:
            setattr(settings, self.AUTO_STOP_PLAYWRIGHT, True)
            self.already_set_auto_stop_playwright = True

        self.browser_launch_args = dict(args=['--start-maximized'], headless=False)
        self.browser_context_args = dict(no_viewport=True)

        self.__page: Optional[Page] = None
        self.__context: Optional[BrowserContext] = None
        self.__browser: Optional[Browser] = None
        self.__browsers: List[Browser] = []

        self.warning_if_error_when_close = True

    @property
    def browsers(self):

        return self.__browsers

    @property
    def browser(self):
        """current browser"""

        if self.__browser is None:
            raise NoOpendBrowserError("No any opened browser")

        return self.__browser

    @browser.setter
    def browser(self, v: Browser):

        if v != self.__browser:
            self.__browser = v
        if v is not None and v not in self.__browsers:
            self.__browsers.append(v)

    @property
    def context(self):
        """current browser context"""

        if self.__context is None:
            raise NoOpendContextError("No any opened context of browser")
        return self.__context

    @context.setter
    def context(self, v: BrowserContext):

        if self.__context != v:
            self.__context = v
        if self.__context is not None:
            self.browser = self.__context.browser

    @property
    def page(self):
        """current page"""

        if self.__page is None:
            raise NoOpendPageError("No any opened page")
        return self.__page

    @page.setter
    def page(self, v: Page):

        if self.__page != v:
            self.__page = v
        if self.__page is not None:
            self.context = self.__page.context

    def has_opened_page(self):
        return self.__page is not None

    def has_opened_context(self):
        return self.__context is not None

    def has_opened_browser(self):

        return self.__browser is not None and self.__browser.is_connected()

    def set_browser_launch_args(self, headless=False, channel=None, slow_mo=0, **kwargs):
        """set default browser launch args

        Args
        ------
        headless : Union[bool, None]
            Whether to run browser in headless mode. More details for
            [Chromium](https://developers.google.com/web/updates/2017/04/headless-chrome) and
            [Firefox](https://developer.mozilla.org/en-US/docs/Mozilla/Firefox/Headless_mode). Defaults to `true` unless the
            `devtools` option is `true`.
        channel : Union[str, None]
            Browser distribution channel.  Supported values are "chrome", "chrome-beta", "chrome-dev", "chrome-canary",
            "msedge", "msedge-beta", "msedge-dev", "msedge-canary". Read more about using
            [Google Chrome and Microsoft Edge](../browsers.md#google-chrome--microsoft-edge).
        slow_mo : Union[float, None]
            Slows down Playwright operations by the specified amount of milliseconds. Useful so that you can see what is going on.
        kwargs : dict
            see more about `BrowserType.launch`
        """

        self.browser_launch_args.update(dict(headless=headless, channel=channel, slow_mo=slow_mo))
        self.browser_launch_args.update(kwargs)
        return self

    def set_browser_context_args(self, device=None, **kwargs):
        """set default browser context args

        Args
        -------
        device : str
            see more about `Playwright.devices`
        kwargs : dict
            same as Parameters of `Browser.new_context`
        """

        self.browser_context_args.update(kwargs)
        if device:
            self.browser_context_args.update(self.playwright.devices[device])
        return self

    def clear_browser_launch_args(self, **keys):

        if keys:
            for key in keys:
                self.browser_launch_args.pop(key, None)
        else:
            self.browser_launch_args.clear()
        return self

    def clear_browser_context_args(self, **keys):

        if keys:
            for key in keys:
                self.browser_context_args.pop(key, None)
        else:
            self.browser_context_args.clear()
        return self

    def __get_browser_type(self, type_name=SupportBrowserType.CHROMIUM) -> BrowserType:

        return getattr(self.playwright, type_name)

    def launch_browser(self, browser_type="chromium", browser_launch_args={}):
        """only open browser, itself context and page is not opened"""

        final_browser_kwargs = copy.deepcopy(self.browser_launch_args)
        final_browser_kwargs.update(browser_launch_args)
        self.browser = self.__get_browser_type(
            type_name=browser_type).launch(**final_browser_kwargs)
        return self

    def open_context(self, **browser_context_args):

        final_context_kwargs = copy.deepcopy(self.browser_context_args)
        final_context_kwargs.update(browser_context_args)
        self.context = self.browser.new_context(**final_context_kwargs)
        return self

    def open_page(self, **browser_context_args):
        """打开新页面，browser_context_args传参，则会创建新的上下文，并在此打开新页面

        browser_context_args: 浏览器上下文参数
        """

        if browser_context_args or not self.has_opened_context():
            self.open_context(**browser_context_args)
        self.page = self.context.new_page()
        return self

    def open_browser(self, browser_type="chromium", browser_launch_args={}, browser_context_args={}):
        """ open a new browser，then open its new context and new page. default open chromium browser.

        Args
        -------
        browser_type : str  default value is `chromium`
            chromium | firefox | webkit
        browser_launch_args : dict
            key value pairs same as Parameters of `BrowserType.launch`
        browser_context_args : dict
            key value pairs same as Parameters of `Browser.new_context`
        """

        if not self.has_opened_browser():
            self.launch_browser(browser_type=browser_type, browser_launch_args=browser_launch_args)
            self.open_page(**browser_context_args)
        return self

    def chromium(self, browser_launch_args={}, browser_context_args={}):

        self.open_browser(SupportBrowserType.CHROMIUM, browser_launch_args, browser_context_args)
        return self

    def chrome(self, browser_launch_args={}, browser_context_args={}):

        browser_launch_args["channel"] = "chrome"
        self.open_browser(SupportBrowserType.CHROMIUM, browser_launch_args, browser_context_args)
        return self

    def firfox(self, browser_launch_args={}, browser_context_args={}):

        self.open_browser(SupportBrowserType.FIREFOX, browser_launch_args, browser_context_args)
        return self

    def msedge(self, browser_launch_args={}, browser_context_args={}):

        browser_launch_args["channel"] = "msedge"
        self.open_browser(SupportBrowserType.CHROMIUM, browser_launch_args, browser_context_args)
        return self

    def webkit(self, browser_launch_args={}, browser_context_args={}):

        self.open_browser(SupportBrowserType.WEBKIT, browser_launch_args, browser_context_args)
        return self

    safari = webkit

    def get(self, url, **kwargs):

        if not self.has_opened_page():
            self.open_page()
        return self.page.goto(url, **kwargs)

    def get_pages_by_title(self, title):

        all_pages = []
        for c in self.browser.contexts:
            all_pages.extend(c.pages)

        pages = [page for page in all_pages if page.title == title]
        return pages

    def switch_page_by_title(self, title, index=0):

        pages = self.get_pages_by_title(title)
        page = pages[index]
        if page != self.page:
            self.page = page
            self.context = self.page.context
            self.page.bring_to_front()
        return self

    def sreenshot(self, **kwargs):
        """Page.screenshot

        Returns the buffer with the captured screenshot.

        Parameters
        ----------
        timeout : Union[float, None]
            Maximum time in milliseconds. Defaults to `30000` (30 seconds). Pass `0` to disable timeout. The default value can
            be changed by using the `browser_context.set_default_timeout()` or `page.set_default_timeout()` methods.
        type : Union["jpeg", "png", None]
            Specify screenshot type, defaults to `png`.
        path : Union[pathlib.Path, str, None]
            The file path to save the image to. The screenshot type will be inferred from file extension. If `path` is a
            relative path, then it is resolved relative to the current working directory. If no path is provided, the image
            won't be saved to the disk.
        quality : Union[int, None]
            The quality of the image, between 0-100. Not applicable to `png` images.
        omit_background : Union[bool, None]
            Hides default white background and allows capturing screenshots with transparency. Not applicable to `jpeg` images.
            Defaults to `false`.
        full_page : Union[bool, None]
            When true, takes a screenshot of the full scrollable page, instead of the currently visible viewport. Defaults to
            `false`.
        clip : Union[{x: float, y: float, width: float, height: float}, None]
            An object which specifies clipping of the resulting image.
        animations : Union["allow", "disabled", None]
            When set to `"disabled"`, stops CSS animations, CSS transitions and Web Animations. Animations get different
            treatment depending on their duration:
            - finite animations are fast-forwarded to completion, so they'll fire `transitionend` event.
            - infinite animations are canceled to initial state, and then played over after the screenshot.

            Defaults to `"allow"` that leaves animations untouched.
        caret : Union["hide", "initial", None]
            When set to `"hide"`, screenshot will hide text caret. When set to `"initial"`, text caret behavior will not be
            changed.  Defaults to `"hide"`.
        scale : Union["css", "device", None]
            When set to `"css"`, screenshot will have a single pixel per each css pixel on the page. For high-dpi devices, this
            will keep screenshots small. Using `"device"` option will produce a single pixel per each device pixel, so
            screenshots of high-dpi devices will be twice as large or even larger.

            Defaults to `"device"`.
        mask : Union[List[Locator], None]
            Specify locators that should be masked when the screenshot is taken. Masked elements will be overlaid with a pink
            box `#FF00FF` (customized by `maskColor`) that completely covers its bounding box.
        mask_color : Union[str, None]
            Specify the color of the overlay box for masked elements, in
            [CSS color format](https://developer.mozilla.org/en-US/docs/Web/CSS/color_value). Default color is pink `#FF00FF`.

        Returns
        -------
        bytes
        """
        return self.page.screenshot(**kwargs)

    def get_screenshot_as_base64(self):

        raw_data = self.sreenshot()
        return base64.b64encode(raw_data).decode()

    def get_screenshot_as_file(self, filepath):

        success = True
        try:
            self.sreenshot(path=filepath)
        except Exception:
            success = False
        return success

    def close_browser(self, browser: Optional[Browser] = None, reverse=False):

        to_be_close = []
        if browser is None:
            to_be_close = self.browsers
        else:
            if reverse:
                for one in self.browsers:
                    if one != browser:
                        to_be_close.append(one)
            else:
                to_be_close.append(browser)
        for one in to_be_close:
            if one in self.browsers:
                self.browsers.remove(one)
            one.close()

    def close(self):

        self.__close(self.page)
        self.page = None

    def quit(self):

        self.close_browser()
        self.page = None
        self.context = None
        self.browser = None