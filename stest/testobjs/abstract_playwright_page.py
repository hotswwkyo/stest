#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import time
import typing
from stest import hook
from ..utils import attrs_manager
from ..utils import attrs_marker
from ..dm import DRIVER_MANAGER
from ..dm.driver_manager import DriverManager
from ..dm.playwright_driver import PlaywrightDriver
from ..dm.playwright_driver import SupportBrowserType
from ..dm.playwright_driver import Playwright
from playwright.sync_api import Locator

PageClass = typing.TypeVar("PageClass", bound="AbstractPlaywrightPage")


@hook.wrapper(hook.RunStage.stopTestRun, priority=70, runpolicy=hook.RunPolicy.AFTER)
def stopTestRun(gsettings, result):
    auto_stop_playwright = getattr(gsettings, PlaywrightDriver.AUTO_STOP_PLAYWRIGHT, False)
    if auto_stop_playwright:
        pw = getattr(gsettings, PlaywrightDriver.PLAYWRIGHT, None)
        if isinstance(pw, Playwright):
            pw.stop()
            setattr(gsettings, PlaywrightDriver.PLAYWRIGHT, None)


# rootpage = typing.TypeVar("rootpage", bound="AbstractPlaywrightPage")
# root_element = typing.TypeVar("root_element", bound="AbstractPlaywrightPage.Elements")
# root_action = typing.TypeVar("root_action", bound="AbstractPlaywrightPage.Actions")


class AbstractPlaywrightPage(attrs_manager.AttributeManager):
    """ 抽象页 """

    DRIVER_MANAGER: DriverManager = attrs_marker.Const(DRIVER_MANAGER, "Driver管理器")

    def __init__(self, driver_or_browser_type=None, alias=None, *, browser_launch_args={}, browser_context_args={}):
        """一般不建议创建页面的时候直接创建驱动实例，建议页面实例化后再调用页面提供的相关驱动实例化方法更好

        Args
        -------
        driver_or_browser_type : instance of PlaywrightDriver or browser type  default value is `None`
            support browser type is chromium | firefox | webkit
        alias : 缓存中存放驱动实例的别名
        browser_launch_args : key value pairs same as Parameters of `BrowserType.launch`
        browser_context_args : key value pairs same as Parameters of `Browser.new_context`
        """

        self.__dm = self.__class__.DRIVER_MANAGER
        if isinstance(driver_or_browser_type, str):
            self.__create_driver(browser_type=driver_or_browser_type, alias=alias,
                                 browser_launch_args=browser_launch_args, browser_context_args=browser_context_args)
        elif driver_or_browser_type:
            self.__dm.register_driver(driver_or_browser_type, alias)

        self._build_elements()
        self._build_actions()
        self.init()

    def init(self):

        pass

    def _build_elements(self):

        self.elements = self.Elements(self)

    def _build_actions(self):

        self.actions = self.Actions(self)

    @property
    def driver_manager(self):
        return self.__dm

    @property
    def driver(self) -> PlaywrightDriver:

        return self.driver_manager.driver

    @property
    def index(self):
        """driver索引"""

        return self.driver_manager.index

    @property
    def pwpage(self):
        """current playwright page instance"""

        return self.driver.page

    def open_url(self, url):

        self.driver_manager.open_url(url)
        return self

    def goto(self, url: str,
             *,
             timeout: typing.Optional[float] = None,
             wait_until: typing.Optional[typing.Literal["commit",
                                                        "domcontentloaded", "load", "networkidle"]] = None,
             referer: typing.Optional[str] = None,):

        return self.pwpage.goto(url, timeout=timeout, wait_until=wait_until, referer=referer)

    def __create_driver(self, browser_type=SupportBrowserType.CHROMIUM, alias=None, *, browser_launch_args={}, browser_context_args={}):
        """创建playwright驱动

        Args
        -------
        browser_type : str  default value is `chromium`
            chromium | firefox | webkit
        alias : 缓存中存放驱动实例的别名
        browser_launch_args : dict
            key value pairs same as Parameters of `BrowserType.launch`
        browser_context_args : dict
            key value pairs same as Parameters of `Browser.new_context`
        """

        return self.driver_manager.create_playwright_driver(browser_type=browser_type, alias=alias, browser_launch_args=browser_launch_args, browser_context_args=browser_context_args)

    open_browser = __create_driver

    def chromium(self, alias=None, browser_launch_args={}, browser_context_args={}):

        self.open_browser(browser_type=SupportBrowserType.CHROMIUM, alias=alias,
                          browser_launch_args=browser_launch_args, browser_context_args=browser_context_args)
        return self

    def chrome(self, alias=None, browser_launch_args={}, browser_context_args={}):

        browser_launch_args["channel"] = "chrome"
        self.open_browser(browser_type=SupportBrowserType.CHROMIUM, alias=alias,
                          browser_launch_args=browser_launch_args, browser_context_args=browser_context_args)
        return self

    def firfox(self, alias=None, browser_launch_args={}, browser_context_args={}):

        self.open_browser(browser_type=SupportBrowserType.FIREFOX, alias=alias,
                          browser_launch_args=browser_launch_args, browser_context_args=browser_context_args)
        return self

    def msedge(self, alias=None, browser_launch_args={}, browser_context_args={}):

        browser_launch_args["channel"] = "msedge"
        self.open_browser(browser_type=SupportBrowserType.CHROMIUM, alias=alias,
                          browser_launch_args=browser_launch_args, browser_context_args=browser_context_args)
        return self

    def webkit(self, alias=None, browser_launch_args={}, browser_context_args={}):

        self.open_browser(browser_type=SupportBrowserType.WEBKIT, alias=alias,
                          browser_launch_args=browser_launch_args, browser_context_args=browser_context_args)
        return self

    safari = webkit

    def close_driver(self):
        self.driver_manager.close_driver()
        return self

    def close_all_drivers(self):
        self.driver_manager.close_all_drivers()
        return self

    def sleep(self, seconds):
        """seconds the length of time to sleep in seconds"""
        time.sleep(seconds)
        return self

    def execute_script(self, script, *args):

        return self.driver.page.evaluate(script, args)

    def scroll_to(self, xpos, ypos):
        """scroll to any position of an opened window of browser"""

        js_code = "([xpos,ypos]) => window.scrollTo(xpos, ypos);"
        self.execute_script(js_code, xpos, ypos)
        return self

    def scroll_into_view(self, element: Locator):

        js_code = '(element)=> element.scrollIntoView();'
        element.evaluate(js_code)
        return self

    def scroll_to_bottom(self):

        bottom = self.execute_script("()=> document.body.scrollHeight;")
        self.scroll_to(0, bottom)
        return self

    def scroll_to_top(self):

        self.scroll_to(0, 0)
        return self

    def screenshot(self, timeout=None, type=None, path=None, quality=None, omit_background=None,
                   full_page=None, clip=None, animations=None, caret=None, scale=None, mask=None, mask_color=None, style=None):
        """call Page.screenshot

        Usage:
            page.screenshot(path="E:\\SevenPytest\\screenshots\\debug.png")
        """
        return self.pwpage.screenshot(timeout=timeout, type=type, path=path, quality=quality, omit_background=omit_background, full_page=full_page, clip=clip, animations=animations, caret=caret,
                                      scale=scale, mask=mask, mask_color=mask_color, style=style)

    @property
    def title(self):
        """Returns the title of the current page."""

        return self.driver.page.title()

    def frame(self, name=None, *, url=None):
        """Page.frame

        Returns frame matching the specified criteria. Either `name` or `url` must be specified.

        **Usage**

        ```py
        frame = page.frame(url=r\".*domain.*\")
        ```

        Parameters
        ----------
        name : Union[str, None]
            Frame name specified in the `iframe`'s `name` attribute. Optional.
        url : Union[Callable[[str], bool], Pattern[str], str, None]
            A glob pattern, regex pattern or predicate receiving frame's `url` as a [URL] object. Optional.

        Returns
        -------
        Union[Frame, None]
        """
        return self.driver.page.frame()

    @property
    def main_frame(self):
        """Page.main_frame

        The page's main frame. Page is guaranteed to have a main frame which persists during navigations.

        Returns
        """

        self.driver.page.main_frame

    @property
    def frames(self):
        """Page.frames

        An array of all frames attached to the page.

        Returns
        -------
        List[Frame]
        """

        return self.driver.page.frames

    def set_viewport_size(self, viewport_size):
        """Page.set_viewport_size

        In the case of multiple pages in a single browser, each page can have its own viewport size. However,
        `browser.new_context()` allows to set viewport size (and more) for all pages in the context at once.

        `page.set_viewport_size()` will resize the page. A lot of websites don't expect phones to change size, so you
        should set the viewport size before navigating to the page. `page.set_viewport_size()` will also reset
        `screen` size, use `browser.new_context()` with `screen` and `viewport` parameters if you need better
        control of these properties.

        **Usage**

        ```py
        page = browser.new_page()
        page.set_viewport_size({\"width\": 640, \"height\": 480})
        page.goto(\"https://example.com\")
        ```

        Parameters
        ----------
        viewport_size : {width: int, height: int}
        """

        self.driver.page.set_viewport_size(viewport_size)
        return self

    def viewport_size(self):
        """Page.viewport_size

        Returns
        -------
        Union[{width: int, height: int}, None]
        """
        return self.driver.page.viewport_size

    def refresh(self):
        """刷新当前页面"""

        return self.driver.page.reload()

    def new_page(self, **browser_context_args):
        """Creates a new page in a new browser context if provide browser_context_args, otherwise creates a new page in current browser context.
        then set it as the current page and Brings it to front (activates tab).

        parameter browser_context_args same as `Browser.new_context`

        Parameters
        ----------
        viewport : Union[{width: int, height: int}, None]
            Sets a consistent viewport for each page. Defaults to an 1280x720 viewport. `no_viewport` disables the fixed
            viewport. Learn more about [viewport emulation](../emulation.md#viewport).
        screen : Union[{width: int, height: int}, None]
            Emulates consistent window screen size available inside web page via `window.screen`. Is only used when the
            `viewport` is set.
        no_viewport : Union[bool, None]
            Does not enforce fixed viewport, allows resizing window in the headed mode.
        ignore_https_errors : Union[bool, None]
            Whether to ignore HTTPS errors when sending network requests. Defaults to `false`.
        java_script_enabled : Union[bool, None]
            Whether or not to enable JavaScript in the context. Defaults to `true`. Learn more about
            [disabling JavaScript](../emulation.md#javascript-enabled).
        bypass_csp : Union[bool, None]
            Toggles bypassing page's Content-Security-Policy. Defaults to `false`.
        user_agent : Union[str, None]
            Specific user agent to use in this context.
        locale : Union[str, None]
            Specify user locale, for example `en-GB`, `de-DE`, etc. Locale will affect `navigator.language` value,
            `Accept-Language` request header value as well as number and date formatting rules. Defaults to the system default
            locale. Learn more about emulation in our [emulation guide](../emulation.md#locale--timezone).
        timezone_id : Union[str, None]
            Changes the timezone of the context. See
            [ICU's metaZones.txt](https://cs.chromium.org/chromium/src/third_party/icu/source/data/misc/metaZones.txt?rcl=faee8bc70570192d82d2978a71e2a615788597d1)
            for a list of supported timezone IDs. Defaults to the system timezone.
        geolocation : Union[{latitude: float, longitude: float, accuracy: Union[float, None]}, None]
        permissions : Union[Sequence[str], None]
            A list of permissions to grant to all pages in this context. See `browser_context.grant_permissions()` for
            more details. Defaults to none.
        extra_http_headers : Union[Dict[str, str], None]
            An object containing additional HTTP headers to be sent with every request. Defaults to none.
        offline : Union[bool, None]
            Whether to emulate network being offline. Defaults to `false`. Learn more about
            [network emulation](../emulation.md#offline).
        http_credentials : Union[{username: str, password: str, origin: Union[str, None], send: Union["always", "unauthorized", None]}, None]
            Credentials for [HTTP authentication](https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication). If no
            origin is specified, the username and password are sent to any servers upon unauthorized responses.
        device_scale_factor : Union[float, None]
            Specify device scale factor (can be thought of as dpr). Defaults to `1`. Learn more about
            [emulating devices with device scale factor](../emulation.md#devices).
        is_mobile : Union[bool, None]
            Whether the `meta viewport` tag is taken into account and touch events are enabled. isMobile is a part of device,
            so you don't actually need to set it manually. Defaults to `false` and is not supported in Firefox. Learn more
            about [mobile emulation](../emulation.md#ismobile).
        has_touch : Union[bool, None]
            Specifies if viewport supports touch events. Defaults to false. Learn more about
            [mobile emulation](../emulation.md#devices).
        color_scheme : Union["dark", "light", "no-preference", "null", None]
            Emulates [prefers-colors-scheme](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-color-scheme)
            media feature, supported values are `'light'` and `'dark'`. See `page.emulate_media()` for more details.
            Passing `'null'` resets emulation to system defaults. Defaults to `'light'`.
        reduced_motion : Union["no-preference", "null", "reduce", None]
            Emulates `'prefers-reduced-motion'` media feature, supported values are `'reduce'`, `'no-preference'`. See
            `page.emulate_media()` for more details. Passing `'null'` resets emulation to system defaults. Defaults to
            `'no-preference'`.
        forced_colors : Union["active", "none", "null", None]
            Emulates `'forced-colors'` media feature, supported values are `'active'`, `'none'`. See
            `page.emulate_media()` for more details. Passing `'null'` resets emulation to system defaults. Defaults to
            `'none'`.
        accept_downloads : Union[bool, None]
            Whether to automatically download all the attachments. Defaults to `true` where all the downloads are accepted.
        proxy : Union[{server: str, bypass: Union[str, None], username: Union[str, None], password: Union[str, None]}, None]
            Network proxy settings to use with this context. Defaults to none.
        record_har_path : Union[pathlib.Path, str, None]
            Enables [HAR](http://www.softwareishard.com/blog/har-12-spec) recording for all pages into the specified HAR file
            on the filesystem. If not specified, the HAR is not recorded. Make sure to call `browser_context.close()`
            for the HAR to be saved.
        record_har_omit_content : Union[bool, None]
            Optional setting to control whether to omit request content from the HAR. Defaults to `false`.
        record_video_dir : Union[pathlib.Path, str, None]
            Enables video recording for all pages into the specified directory. If not specified videos are not recorded. Make
            sure to call `browser_context.close()` for videos to be saved.
        record_video_size : Union[{width: int, height: int}, None]
            Dimensions of the recorded videos. If not specified the size will be equal to `viewport` scaled down to fit into
            800x800. If `viewport` is not configured explicitly the video size defaults to 800x450. Actual picture of each page
            will be scaled down if necessary to fit the specified size.
        storage_state : Union[pathlib.Path, str, {cookies: Sequence[{name: str, value: str, domain: str, path: str, expires: float, httpOnly: bool, secure: bool, sameSite: Union["Lax", "None", "Strict"]}], origins: Sequence[{origin: str, localStorage: Sequence[{name: str, value: str}]}]}, None]
            Learn more about [storage state and auth](../auth.md).

            Populates context with given storage state. This option can be used to initialize context with logged-in
            information obtained via `browser_context.storage_state()`.
        base_url : Union[str, None]
            When using `page.goto()`, `page.route()`, `page.wait_for_url()`,
            `page.expect_request()`, or `page.expect_response()` it takes the base URL in consideration by
            using the [`URL()`](https://developer.mozilla.org/en-US/docs/Web/API/URL/URL) constructor for building the
            corresponding URL. Unset by default. Examples:
            - baseURL: `http://localhost:3000` and navigating to `/bar.html` results in `http://localhost:3000/bar.html`
            - baseURL: `http://localhost:3000/foo/` and navigating to `./bar.html` results in
              `http://localhost:3000/foo/bar.html`
            - baseURL: `http://localhost:3000/foo` (without trailing slash) and navigating to `./bar.html` results in
              `http://localhost:3000/bar.html`
        strict_selectors : Union[bool, None]
            If set to true, enables strict selectors mode for this context. In the strict selectors mode all operations on
            selectors that imply single target DOM element will throw when more than one element matches the selector. This
            option does not affect any Locator APIs (Locators are always strict). Defaults to `false`. See `Locator` to learn
            more about the strict mode.
        service_workers : Union["allow", "block", None]
            Whether to allow sites to register Service workers. Defaults to `'allow'`.
            - `'allow'`: [Service Workers](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API) can be
              registered.
            - `'block'`: Playwright will block all registration of Service Workers.
        record_har_url_filter : Union[Pattern[str], str, None]
        record_har_mode : Union["full", "minimal", None]
            When set to `minimal`, only record information necessary for routing from HAR. This omits sizes, timing, page,
            cookies, security and other types of HAR information that are not used when replaying from HAR. Defaults to `full`.
        record_har_content : Union["attach", "embed", "omit", None]
            Optional setting to control resource content management. If `omit` is specified, content is not persisted. If
            `attach` is specified, resources are persisted as separate files and all of these files are archived along with the
            HAR file. Defaults to `embed`, which stores content inline the HAR file as per HAR specification.
        client_certificates : Union[Sequence[{origin: str, certPath: Union[pathlib.Path, str, None], cert: Union[bytes, None], keyPath: Union[pathlib.Path, str, None], key: Union[bytes, None], pfxPath: Union[pathlib.Path, str, None], pfx: Union[bytes, None], passphrase: Union[str, None]}], None]
            TLS Client Authentication allows the server to request a client certificate and verify it.

            **Details**

            An array of client certificates to be used. Each certificate object must have either both `certPath` and `keyPath`,
            a single `pfxPath`, or their corresponding direct value equivalents (`cert` and `key`, or `pfx`). Optionally,
            `passphrase` property should be provided if the certificate is encrypted. The `origin` property should be provided
            with an exact match to the request origin that the certificate is valid for.

            **NOTE** When using WebKit on macOS, accessing `localhost` will not pick up client certificates. You can make it
            work by replacing `localhost` with `local.playwright`.


        Returns
        -------
        instance of subclass of AbstractPlaywrightPage
        """

        self.driver.open_page(**browser_context_args)
        self.driver.page.bring_to_front()
        return self

    def content(self):
        """Page.content

        Gets the full HTML contents of the current page, including the doctype.

        Returns
        -------
        str
        """

        return self.driver.page.content()

    def locator(self, selector, *, has_text=None, has_not_text=None, has=None, has_not=None):
        """Page.locator

        The method returns an element locator that can be used to perform actions on this page / frame. Locator is resolved
        to the element immediately before performing an action, so a series of actions on the same locator can in fact be
        performed on different DOM elements. That would happen if the DOM structure between those actions has changed.

        [Learn more about locators](https://playwright.dev/python/docs/locators).

        Parameters
        ----------
        selector : str
            A selector to use when resolving DOM element.
        has_text : Union[Pattern[str], str, None]
            Matches elements containing specified text somewhere inside, possibly in a child or a descendant element. When
            passed a [string], matching is case-insensitive and searches for a substring. For example, `"Playwright"` matches
            `<article><div>Playwright</div></article>`.
        has_not_text : Union[Pattern[str], str, None]
            Matches elements that do not contain specified text somewhere inside, possibly in a child or a descendant element.
            When passed a [string], matching is case-insensitive and searches for a substring.
        has : Union[Locator, None]
            Narrows down the results of the method to those which contain elements matching this relative locator. For example,
            `article` that has `text=Playwright` matches `<article><div>Playwright</div></article>`.

            Inner locator **must be relative** to the outer locator and is queried starting with the outer locator match, not
            the document root. For example, you can find `content` that has `div` in
            `<article><content><div>Playwright</div></content></article>`. However, looking for `content` that has `article
            div` will fail, because the inner locator must be relative and should not use any elements outside the `content`.

            Note that outer and inner locators must belong to the same frame. Inner locator must not contain `FrameLocator`s.
        has_not : Union[Locator, None]
            Matches elements that do not contain an element that matches an inner locator. Inner locator is queried against the
            outer one. For example, `article` that does not have `div` matches `<article><span>Playwright</span></article>`.

            Note that outer and inner locators must belong to the same frame. Inner locator must not contain `FrameLocator`s.

        Returns
        -------
        Locator
        """

        return self.driver.page.locator(selector, has_text=has_text, has_not_text=has_not_text, has=has, has_not=has_not)

    def get_by_xpath(self, selector: str):

        return self.locator(self.join_xpaths(selector, prefix="xpath="))

    def get_by_id(self, value: str):
        """
        **Usage**

        Consider the following DOM structure:

        ```html
        <div><span class=\"input_box\"><input type=\"password\" id=\"passwordFU\" autocomplete=\"off\" maxlength=\"16\"></span></div>
        <div>Hello</div>
        ```

        You can locate by the id value:

        ```py
        # Matches <input>
        page.get_by_id(\"passwordFU\")
        ```
        """

        selector = '//*[@id="{}"]'.format(value)
        return self.get_by_xpath(selector)

    def get_by_text(self, text: typing.Union[str, typing.Pattern[str]], *, exact: typing.Optional[bool] = None):
        """call  Page.get_by_text
        """

        return self.pwpage.get_by_text(text, exact=exact)

    def get_by_alt_text(self, text: typing.Union[str, typing.Pattern[str]], *, exact: typing.Optional[bool] = None):
        """call Page.get_by_alt_text"""

        return self.pwpage.get_by_alt_text(text, exact=exact)

    def frame_locator(self, selector: str):
        """call Page.frame_locator"""

        return self.pwpage.frame_locator(selector)

    def get_by_title(self, text: typing.Union[str, typing.Pattern[str]], *, exact: typing.Optional[bool] = None):
        """call Page.get_by_title"""

        return self.pwpage.get_by_title(text, exact=exact)

    def get_attribute(self, selector: str, name: str, *, strict: typing.Optional[bool] = None, timeout: typing.Optional[float] = None):
        """call Page.get_attribute"""

        return self.pwpage.get_attribute(selector, name, strict=strict, timeout=timeout)

    def get_by_placeholder(self, text: typing.Union[str, typing.Pattern[str]], *, exact: typing.Optional[bool] = None):
        """call Page.get_by_placeholder"""

        return self.pwpage.get_by_placeholder(text, exact=exact)

    @classmethod
    def join_xpaths(cls, *xpaths, prefix=""):
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
        return prefix + full_xpath

    class Elements(object):
        def __init__(self, page):
            self.page = typing.cast(PageClass, page)

        def sleep(self, seconds):
            """延时"""

            self.page.sleep(seconds)
            return self

    class Actions(object):
        def __init__(self, page):

            self.page = typing.cast(PageClass, page)

        def sleep(self, seconds):
            """延时"""

            self.page.sleep(seconds)
            return self

        def turn_to_page(self, page_number):
            """翻页， 由具体页面实现"""

            raise NotImplementedError
