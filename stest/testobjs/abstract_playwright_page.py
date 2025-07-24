#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import time
import typing
import base64
from stest import hook
from ..conf import image_show
from ..utils import attrs_manager
from ..utils import attrs_marker
from ..dm import DRIVER_MANAGER
from ..dm.driver_manager import DriverManager
from ..dm.playwright_driver import PlaywrightDriver
from ..dm.playwright_driver import SupportBrowserType

from playwright.sync_api import Playwright
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
        browser_launch_args : refer to the `BrowserType.launch`
        browser_context_args : refer to the `BrowserType.new_context`
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

    def close(self, **kwargs):
        """refer to the `Page.close`"""

        self.pwpage.close(**kwargs)

    def goto(self, url: str, **kwargs):
        """refer to the `Page.goto`"""

        return self.pwpage.goto(url, **kwargs)

    def __create_driver(self, browser_type=SupportBrowserType.CHROMIUM, alias=None, *, browser_launch_args={}, browser_context_args={}):
        """创建playwright驱动

        Args
        -------
        browser_type : str  default value is `chromium`
            chromium | firefox | webkit
        alias : 缓存中存放驱动实例的别名
        browser_launch_args : dict
            refer to the `BrowserType.launch`
        browser_context_args : dict
            refer to the `Browser.new_context`
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

    def execute_script(self, script: str, args: typing.Optional[typing.Any] = None):
        """refer to the `Page.evaluate`"""

        return self.driver.page.evaluate(script, args)

    def scroll_to(self, x: int, y: int, element: Locator = None):
        """scroll to any position of an opened window of browser or scrollable element 滚动到指定坐标位置

        Parameters
        ----------
            x : int - 水平滚动位置
            y : int - 垂直滚动位置
            element : Locator - 目标元素定位器(None表示滚动浏览器窗口)
        """
        if element is None:
            # 浏览器窗口滚动
            self.execute_script("""([x, y]) => {{
                window.scrollTo({{
                    left: x,
                    top: y,
                    behavior: 'smooth'
                }});
            }}""", [x, y])
        else:
            # 元素内部滚动
            element.evaluate("""(el, [x, y]) => {{
                el.scrollTo({{
                    left: x,
                    top: y,
                    behavior: 'smooth'
                }});
            }}""", [x, y])
        return self

    def scroll_into_view(self, element: Locator):

        js_code = '(element)=> element.scrollIntoView();'
        element.evaluate(js_code)
        return self

    def scroll_to_center(self, vertical=True, horizontal=False, element: Locator = None):
        """将浏览器窗口或元素滚动条居中

        Parameters
        ----------
            vertical : bool - 是否垂直居中 (默认True)
            horizontal : bool - 是否水平居中 (默认False)
            element : Locator - 目标元素定位器 (None表示滚动浏览器窗口)
        """
        if element is None:
            # 浏览器窗口滚动
            self.execute_script("""([vertical, horizontal]) => {
                if (vertical) {
                    const centerY = document.body.scrollHeight/2 - window.innerHeight/2;
                    window.scrollTo({top: centerY, behavior: 'smooth'});
                }
                if (horizontal) {
                    const centerX = document.body.scrollWidth/2 - window.innerWidth/2;
                    window.scrollTo({left: centerX, behavior: 'smooth'});
                }
            }""", [vertical, horizontal])
        else:
            # 元素内部滚动
            if vertical:
                element.evaluate("""
                    el => {
                        const centerY = (el.scrollHeight - el.clientHeight) / 2;
                        el.scrollTo({top: centerY, behavior: 'smooth'});
                    }
                """)

            if horizontal:
                element.evaluate("""
                    el => {
                        const centerX = (el.scrollWidth - el.clientWidth) / 2;
                        el.scrollTo({left: centerX, behavior: 'smooth'});
                    }
                """)
        return self

    def scroll_to_bottom(self, element: Locator = None):
        """滚动到浏览器窗口或元素底部

        Parameters
        ----------
            element : Locator - 目标元素定位器(None表示滚动浏览器窗口)
        """
        if element is None:
            # 浏览器窗口滚动到底部
            self.execute_script("""() => {
                window.scrollTo({
                    top: document.body.scrollHeight,
                    behavior: 'smooth'
                });
            }""")
        else:
            # 元素内部滚动到底部
            element.evaluate("""el => {
                el.scrollTo({
                    top: el.scrollHeight,
                    behavior: 'smooth'
                });
            }""")
        return self

    def scroll_to_top(self, element: Locator = None):
        """
        滚动到浏览器窗口或元素顶部

        Args:
            element (Locator, optional): 目标元素定位器.
                None表示浏览器窗口. Defaults to None.

        Example:
            >>> page.scroll_to_top()  # 浏览器窗口滚动到顶部
            >>> page.scroll_to_top(element)  # 元素滚动到顶部
        """
        if element is None:
            # 浏览器窗口滚动到顶部
            self.execute_script("""() => {
                window.scrollTo({
                    top: 0,
                    behavior: 'smooth'
                });
            }""")
        else:
            # 元素内部滚动到顶部
            element.evaluate("""el => {
                el.scrollTo({
                    top: 0,
                    behavior: 'smooth'
                });
            }""")
        return self

    def scroll_to_left(self, element: Locator = None):
        """
        滚动到浏览器窗口或元素最左侧

        Args:
            element (Locator, optional): 目标元素定位器.
                None表示浏览器窗口. Defaults to None.

        Example:
            >>> page.scroll_to_left()  # 浏览器窗口滚动到最左
            >>> page.scroll_to_left(element)  # 元素滚动到最左
        """
        if element is None:
            # 浏览器窗口滚动到最左侧
            self.execute_script("""() => {
                window.scrollTo({
                    left: 0,
                    behavior: 'smooth'
                });
            }""")
        else:
            # 元素内部滚动到最左侧
            element.evaluate("""el => {
                el.scrollTo({
                    left: 0,
                    behavior: 'smooth'
                });
            }""")
        return self

    def scroll_to_right(self, element: Locator = None):
        """
        滚动到浏览器窗口或元素最右侧

        Args:
            element (Locator, optional): 目标元素定位器.
                None表示浏览器窗口. Defaults to None.

        Example:
            >>> page.scroll_to_right()  # 浏览器窗口滚动到最右
            >>> page.scroll_to_right(element)  # 元素滚动到最右
        """
        if element is None:
            # 浏览器窗口滚动到最右侧
            self.execute_script("""() => {
                window.scrollTo({
                    left: document.body.scrollWidth,
                    behavior: 'smooth'
                });
            }""")
        else:
            # 元素内部滚动到最右侧
            element.evaluate("""el => {
                el.scrollTo({
                    left: el.scrollWidth,
                    behavior: 'smooth'
                });
            }""")
        return self

    def screenshot(self, path=None, full_page=None, clip=None, **others):
        """refer to the `Page.screenshot`

        Returns the buffer with the captured screenshot.

        Parameters
        ----------
        path :  Union[pathlib.Path, str, None]
            The file path to save the image to. The screenshot type will be inferred from file extension. If `path` is a
            relative path, then it is resolved relative to the current working directory. If no path is provided, the image
            won't be saved to the disk.
        full_page : Union[bool, None]
            When true, takes a screenshot of the full scrollable page, instead of the currently visible viewport. Defaults to `false`.
        clip : Union[{x: float, y: float, width: float, height: float}, None]
            An object which specifies clipping of the resulting image.
        others : refer to the `Page.screenshot`

        Usage
        -----
            page.screenshot(path="E:\\SevenPytest\\screenshots\\debug.png")
        """
        return self.pwpage.screenshot(path=path, full_page=full_page, clip=clip, **others)

    def show2html(self, testcase, *, name="", path=None, **screenshot_kwargs):
        """截图并显示到html测试报告中

        Parameters
        ----------
        testcase : 测试用例实例，显示在html测试报告中的哪个测试用例下
        name : 在html报告中显示的名称
        path : 截图保存路径
        screenshot_kwargs : 其它信息

        Usage
        -----
        ```
        import stest
        from erp_autotest.pages.login import LoginPage

        class LoginTest(stest.AbstractTestCase):
            @classmethod
            def setUpClass(cls):

                cls.url = "https://tv.cctv.com/live/cctv13"
                cls.username = "zhangsan"
                cls.password = "123456"

            def setUp(self):
                pass

            @stest.Test(name="demo1", groups=["ss"])
            def demo1(self):

                page = LoginPage()
                page.chrome().open_url(cls.url).actions.login(cls.username, cls.password).sleep(2)
                page.show2html(self)
                page.show2html(self, path="E:\\erp_autotest\\screenshots\\debug.png")

            def tearDown(self):
                pass

            @classmethod
            def tearDownClass(cls):
                LoginPage.DRIVER_MANAGER.close_all_drivers()

        if __name__ == "__main__":
            LoginTest.run_test(buffer=True, argv=["python -m stest", "-g", "ss"])
        ```
        """
        raw_data = self.pwpage.screenshot(path=path, **screenshot_kwargs)
        if path:
            base64data = ""
        else:
            base64data = base64.b64encode(raw_data).decode()
        image_show.show2html(testcase, base64data=base64data, filepath=path,
                             name=name)
        return self

    @property
    def title(self):
        """Returns the title of the current page."""

        return self.driver.page.title()

    def frame(self, name=None, *, url=None):
        """refer to the `Page.frame`

        Returns frame matching the specified criteria. Either `name` or `url` must be specified.

        **Usage**

        ```
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
        return self.driver.page.frame(name=name, url=url)

    @property
    def main_frame(self):
        """refer to the `Page.main_frame`

        The page's main frame. Page is guaranteed to have a main frame which persists during navigations.

        Returns
        """

        self.driver.page.main_frame

    @property
    def frames(self):
        """refer to the `Page.frames`

        An array of all frames attached to the page.

        Returns
        -------
        List[Frame]
        """

        return self.driver.page.frames

    def set_viewport_size(self, viewport_size):
        """refer to the `Page.set_viewport_size`

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
        """refer to the `Page.viewport_size`

        Returns
        -------
        Union[{width: int, height: int}, None]
        """
        return self.driver.page.viewport_size

    def reload(self, **kwargs):
        """refer to the `Page.reload`"""

        return self.driver.page.reload(**kwargs)

    def new_page(self, **browser_context_args):
        """Creates a new page in a new browser context if provide browser_context_args, otherwise creates a new page in current browser context.
        then set it as the current page and Brings it to front (activates tab).

        parameter browser_context_args same as `Browser.new_context`

        Parameters
        ----------
        refer to the `Browser.new_context`

        Returns
        -------
        instance of subclass of AbstractPlaywrightPage
        """

        self.driver.open_page(**browser_context_args)
        self.driver.page.bring_to_front()
        return self

    def content(self):
        """refer to the `Page.content`

        Gets the full HTML contents of the current page, including the doctype.

        Returns
        -------
        str
        """

        return self.driver.page.content()

    def locator(self, selector, **kwargs):
        """refer to the `Page.locator`

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

        return self.driver.page.locator(selector, **kwargs)

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
        """refer to the `Page.get_by_text`
        """

        return self.pwpage.get_by_text(text, exact=exact)

    def get_by_alt_text(self, text: typing.Union[str, typing.Pattern[str]], *, exact: typing.Optional[bool] = None):
        """refer to the `Page.get_by_alt_text`"""

        return self.pwpage.get_by_alt_text(text, exact=exact)

    def frame_locator(self, selector: str):
        """refer to the `Page.frame_locator`"""

        return self.pwpage.frame_locator(selector)

    def get_by_title(self, text: typing.Union[str, typing.Pattern[str]], *, exact: typing.Optional[bool] = None):
        """refer to the `Page.get_by_title`"""

        return self.pwpage.get_by_title(text, exact=exact)

    def get_by_placeholder(self, text: typing.Union[str, typing.Pattern[str]], *, exact: typing.Optional[bool] = None):
        """refer to the `Page.get_by_placeholder`"""

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
            self.init()

        def init(self):
            pass

        def sleep(self, seconds):
            """延时"""

            self.page.sleep(seconds)
            return self

    class Actions(object):
        def __init__(self, page):

            self.page = typing.cast(PageClass, page)
            self.init()

        def init(self):
            pass

        def sleep(self, seconds):
            """延时"""

            self.page.sleep(seconds)
            return self

        def turn_to_page(self, page_number):
            """翻页， 由具体页面实现"""

            raise NotImplementedError
