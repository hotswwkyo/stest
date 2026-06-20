#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import re
import json
import copy
import typing
import warnings
from typing import List
from typing import Union
from typing import Dict
from typing import Optional
from collections import defaultdict
from playwright.sync_api import Page
from playwright.sync_api import Locator
from stest.testobjs.abstract_playwright_page import AbstractPlaywrightPage


class CellSelector(object):
    """表格单元格定位信息。

    用于描述如何定位表格中的某个单元格（th 或 td）及其内部内容元素。
    """

    def __init__(self, position=None, cxpath=None, title=None, value=None, tagname="td", settings: dict = None):
        """

        Parameters
        ----------
        position : int, optional
            单元格位置索引，从1开始。
        cxpath : str, optional
            单元格中内容元素的相对xpath，相对于单元格元素（一般为th或td）。
            为None时，内容元素即为单元格元素本身。
        title : str, optional
            单元格标题。
        value : str, optional
            单元格内容。
        tagname : str, default="td"
            单元格元素标签（一般为th或td）。
        settings : dict, optional
            其它配置信息。
        """

        self.title = title
        self.value = value
        self.cxpath = cxpath
        self.tagname = tagname
        self.position = position
        self.__xpath_builder = None
        self.__xpath_builder_args = None
        self.__xpath_builder_kwargs = None
        self.settings: dict = {} if settings is None else settings

    def __add_condition(self, xpath, condition, logical_symbol="and"):
        predicates = r'(\[((?:[^"\'[\]]|\'(?:[^\']|\'\')*\'|"(?:[^"]|"")*")*?)\])$'
        regex = predicates
        m = re.compile(regex)
        r = m.search(xpath)
        if r:
            suffix = r.group(0)
            if suffix.rstrip():
                p = xpath[:len(xpath) - len(suffix)]
                creg = r'normalize-space\(\)=".+"'
                m1 = re.compile(creg)
                r1 = m1.search(suffix)
                if r1:
                    ns = m1.sub(condition, suffix)
                    p = "{}{}".format(p, ns)
                else:
                    lb = "]"
                    rb = "["
                    ls = " {} ".format(logical_symbol)
                    suffix = suffix[len(rb):len(suffix) - len(lb)]
                    if suffix.rstrip():
                        p = "{}{}{}{}{}{}".format(p, rb, suffix, ls, condition, lb)
                    else:
                        p = "{}{}{}{}{}".format(p, rb, suffix, condition, lb)
            else:
                p = "{}[{}]".format(xpath, condition)
        else:
            p = "{}[{}]".format(xpath, condition)
        return p

    def __build_xpath(self) -> typing.AnyStr:
        """生成相对于行元素(一般为tr)的单元格xpath。

        当 cell.value 为 None 时，value 不参与生成 xpath。

        示例生成的xpath格式：`td/div[normalize-space()="死侍5"]`
        """

        if self.position is None:
            xpath = '{}'.format(self.tagname)
        else:
            xpath = '{}[{}]'.format(self.tagname, self.position)
        if self.cxpath:
            xpath = AbstractPlaywrightPage.join_xpaths(xpath, self.cxpath)
        if self.value is not None:
            xpath = self.__add_condition(xpath, 'normalize-space()="{}"'.format(self.value))
        return xpath

    @property
    def xpath_builder(self) -> typing.Callable[[typing.Self, typing.Tuple, typing.Dict], typing.AnyStr]:
        """单元格xpath生成器。

        接收三个参数：
        1. 单元格对象（Cell实例）
        2. 位置参数（元组类型）
        3. 关键字参数（字典类型）

        Returns
        -------
        相对于行元素(一般为tr)的单元格xpath。
        """
        return self.__xpath_builder

    @xpath_builder.setter
    def xpath_builder(self, v: typing.Callable[[typing.Self, typing.Tuple, typing.Dict], typing.AnyStr]):
        self.__xpath_builder = v

    @property
    def xpath_builder_args(self):
        """单元格xpath生成器的位置参数（元组类型）。"""
        return self.__xpath_builder_args if self.xpath_builder_args is not None else ()

    @xpath_builder_args.setter
    def xpath_builder_args(self, v):
        if isinstance(v, tuple):
            self.__xpath_builder_args = v
        elif isinstance(v, list):
            self.__xpath_builder_args = tuple(v)
        else:
            raise TypeError(f"无效参数类型，仅接受元组和列表类型的参数：{type(v)}")

    @property
    def xpath_builder_kwargs(self):
        """单元格xpath生成器的关键字参数（字典类型）。"""
        return self.__xpath_builder_kwargs if self.__xpath_builder_kwargs is not None else {}

    @xpath_builder_kwargs.setter
    def xpath_builder_kwargs(self, v):
        if isinstance(v, dict):
            self.__xpath_builder_kwargs = v
        else:
            raise TypeError(f"无效参数类型，仅接受字典类型的参数：{type(v)}")

    def set_xpath_builder(self, func, args, kwargs):
        """设置单元格xpath生成器及其参数。

        Parameters
        ----------
        func : callable
            单元格xpath生成器。接收三个参数：
            - 单元格对象（Cell实例）
            - 位置参数（元组类型）
            - 关键字参数（字典类型）
            返回相对于行元素(一般为tr)的单元格xpath。
        args : tuple
            单元格xpath生成器的位置参数（元组类型）。
        kwargs : dict
            单元格xpath生成器的关键字参数（字典类型）。
        """
        self.xpath_builder = func
        self.xpath_builder_args = args
        self.xpath_builder_kwargs = kwargs
        return self

    @property
    def xpath(self):
        """单元格xpath，相对于行元素(一般为tr)。

        若设置了xpath_builder，则使用生成器生成；否则使用默认的__build_xpath方法。
        """
        if callable(self.xpath_builder):
            return self.xpath_builder(self, self.xpath_builder_args, self.xpath_builder_kwargs)
        else:
            return self.__build_xpath()


class Table(object):
    """基于 Playwright 的表格通用定位器。

    本类采用“由列定表”的设计理念：您只需提供关心的列标题或列索引，Table 即可自动生成
    复杂的 XPath，在页面中精准定位到包含这些列的目标表格，并提供对行、单元格的快速查找
    与数据提取能力。

    **核心能力**

    1. **结构化定位**：支持按列标题、列索引或混合字典配置表格结构，自动生成高精度 XPath。
    2. **智能检测与修复**：支持自动检测实际 DOM 表头，并提供显式的 ``sync_from_dom`` 方法，
       根据检测结果同步或重建内部列配置，应对动态渲染表格的列顺序变更。
    3. **多级表头支持**：自动解析 ``colspan``/``rowspan``，将多行表头合并为扁平化的列标题。
    4. **便捷数据提取**：提供 ``row()``、``cells()``、``cell()`` 等链式 API，支持按内容
       筛选行、排除非数据列（如操作列），快速获取结构化字典数据。

    **Usage**

    以 Element UI 的典型表格 DOM 结构为例：

    ```html
    <div class="el-table__fixed-right">
        <div class="el-table__fixed-header-wrapper">
            <table cellspacing="0" cellpadding="0" border="0" class="el-table__header">
                <thead>
                    <tr>
                        <th><div class="cell">序号</div></th>
                        <th><div class="cell">专资编码</div></th>
                        <th><div class="cell">影城名称</div></th>
                        <th><div class="cell">院线</div></th>
                        <th><div class="cell">影投</div></th>
                        <th><div class="cell">营业状态</div></th>
                        <th><div class="cell">终端绑定状态</div></th>
                        <th><div class="cell">终端安装状态</div></th>
                        <th><div class="cell">操作</div></th>
                    </tr>
                </thead>
            </table>
        </div>
        <div class="el-table__fixed-body-wrapper">
            <table cellspacing="0" cellpadding="0" border="0" class="el-table__body">
                <tbody>
                    <tr class="el-table__row">
                        <td><div class="cell">1</div></td>
                        <td><div class="cell">10001001</div></td>
                        <td><div class="cell">影院名称-10001001</div></td>
                        <td><div class="cell">长城沃美</div></td>
                        <td><div class="cell">BHG华联</div></td>
                        <td><div class="cell">未确认</div></td>
                        <td><div class="cell">已绑定</div></td>
                        <td><div class="cell">已安装</div></td>
                        <td>
                            <div class="cell">
                                <button type="button" class="el-button el-button--text">更新</button>
                                <button type="button" class="el-button el-button--text">编辑</button>
                            </div>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
    ```

    **定位方式说明**

    1. **表头标题定位（位置无关）**：只需提供表头标题，不要求顺序，只要表格包含这些标题列即可定位。
       适用于列顺序可能变化，但标题固定的场景。

       ```python
       Table(page, '专资编码', '院线', '营业状态', auto_set_position=False)
       ```

    2. **按位置顺序传入**：标题列表需与表格实际列顺序完全一致。
       适用于需要精确按索引定位单元格的场景。

       ```python
       Table(page, '序号', '专资编码', '影城名称', '院线', '影投', auto_set_position=True)
       ```

    3. **表头索引定位（从1开始）**：仅通过列索引定位表格，不依赖标题文本。
       适用于表头动态生成或无明确标题的表格。

       ```python
       Table(page, 2, 5, auto_set_position=False)
       Table(page, *list(range(1, 6)), auto_set_position=False)
       ```

    **固定列表示例**

    在 Element UI 等前端框架中，固定列会将表格拆分为多个独立的 `<table>` DOM 节点。
    此时需要修改默认的 XPath 指向，并利用 ``cxpaths_for_rebuild`` 保留内部元素定位路径：

    ```python
    titles = ['序号', '专资编码', '影城名称', '院线', '影投', '营业状态',
              '终端绑定状态', '终端安装状态','操作']
    right_table = Table(page, *titles)
    # 1. 覆盖默认的表头和主体 XPath，指向固定列所在的 DOM 节点
    right_table.default_head_xpath = '//div[@class="el-table__fixed-right"]/div[contains(@class,"el-table__fixed-header-wrapper")]/table/thead'
    right_table.default_body_xpath = './ancestor::table/parent::div/following-sibling::div[contains(@class,"el-table__fixed-body-wrapper")]/table/tbody'
    # 2. 标记非数据列，提取数据时自动忽略
    right_table.mark_non_data_columns_by_titles('操作')
    ```
    """

    INDEX_KEY = "index"
    TITLE_KEY = "title"
    VALUE_KEY = "value"
    XPATH_KEY = "xpath"
    XPATH_PREFIX = "xpath="
    TAGNAME_KEY = "tagname"

    # 行元素名
    ROW_ELEMENT_NAME = "tr"

    HEAD_ELEMENT_NAME = 'thead'
    BODY_ELEMENT_NAME = 'tbody'

    # 表头标题头默认xpath
    DEFAULT_HEAD_XPATH = '//div[@id="app"]//div[contains(@class,"el-table__header-wrapper")]/table/thead'

    # 相对于DEFAULT_HEAD_XPATH的xpath
    DEFAULT_BODY_XPATH = './ancestor::table/parent::div/following-sibling::div[contains(@class,"el-table__body-wrapper")]/table/tbody'

    def __init__(self, parent: Union[Page, Locator, AbstractPlaywrightPage], *config, auto_set_position=True, header_cell_tagname="th", body_cell_tagname="td", header_cell_xpath=None, body_cell_xpath=None):
        """初始化表格定位器。

        根据提供的列配置信息构建表头和主体的列定位模型，用于后续的行列快速查找与定位。

        Parameters
        ----------
        parent : Page | Locator | AbstractPlaywrightPage
            页面对象或父级定位器。若传入 ``AbstractPlaywrightPage`` 包装对象，
            内部会自动提取其原始 ``Page`` 实例。
        config : Union[str, int, dict, list, tuple]
            表头单元格配置信息，用于定义表格的列结构。
            **注意：所有元素必须为同一类型，不能混合使用。** 支持以下类型：

            - **str**：列标题。配合 ``auto_set_position`` 决定是否自动分配列索引。
            - **int**：列索引（从1开始）。仅指定位置，不指定标题。
            - **dict**：包含列详细信息的字典。支持的键：

                > - ``index`` (必填)：列索引，从1开始。
                > - ``title`` (必填)：列标题。
                > - ``value`` (可选)：单元格内容，用于生成 XPath 筛选条件。
                > - ``xpath`` (可选)：单元格内内容元素的相对 XPath。
                > - ``tagname`` (可选)：单元格元素标签名。

            - **list | tuple**：按位置传参的序列，支持 2 到 5 个元素：

                > - 2个元素：``(索引, 标题)``
                > - 3个元素：``(索引, 标题, 相对xpath)``
                > - 4个元素：``(索引, 标题, 相对xpath, 单元格内容)``
                > - 5个元素：``(索引, 标题, 相对xpath, 单元格内容, 元素标签)``

        auto_set_position : bool, default=True
            是否根据标题在 ``config`` 中的传入顺序自动设置列索引（``position = 传入索引 + 1``）。
            **仅当 ``config`` 传入字符串列表时有效**。

            - 为 ``True`` 时：传入的标题列表必须与表格实际列顺序完全一致。
            - 为 ``False`` 时：列索引（``position``）将保持为 ``None``，适用于仅按标题匹配而不关心列位置的场景。
              （注意：后续若需精确生成单元格 XPath，需配合 ``allow_missing_position=True`` 使用，否则会抛出异常）。

        header_cell_tagname : str, default="th"
            表头单元格的默认 HTML 标签名，用于生成表头列的 XPath。
        body_cell_tagname : str, default="td"
            表格主体单元格的默认 HTML 标签名，用于生成主体列的 XPath。
        header_cell_xpath : str, optional
            表头单元格内内容元素的统一相对 XPath（如 ``div[@class="cell"]``）。
            若提供，将应用于所有未单独指定 ``xpath`` 的表头列。为 None 时，内容元素即为 ``<th>`` 本身。
        body_cell_xpath : str, optional
            主体单元格内内容元素的统一相对 XPath（如 ``div[@class="cell"]``）。
            若提供，将应用于所有未单独指定 ``xpath`` 的主体列。为 None 时，内容元素即为 ``<td>`` 本身。

        Notes
        -----
        - 初始化时，``config`` 会被同时用于构建 ``head_columns``（表头列）和 ``body_columns``（主体列）。
          表头列的 ``value`` 会被自动设置为其 ``title``。
        - 初始化后，可通过修改 ``default_head_xpath`` 和 ``default_body_xpath`` 属性来调整整体定位路径，
          或通过 ``set_body_cell_xpath`` 等方法微调特定列的定位。
        """
        self.__parent = parent
        self.multi_level_sep = '-'  # 多级表头合并时的分隔符，默认'-'
        self.default_tagname_of_header_cell = header_cell_tagname
        self.default_tagname_of_body_cell = body_cell_tagname

        self._auto_set_position = auto_set_position
        self.row_element_name = self.ROW_ELEMENT_NAME
        self.head_element_name = self.HEAD_ELEMENT_NAME
        self.body_element_name = self.BODY_ELEMENT_NAME
        self.__default_head_xpath = self.DEFAULT_HEAD_XPATH
        self.__default_body_xpath = self.DEFAULT_BODY_XPATH

        self.__position_of_non_data_columns = []
        self.__title_of_non_data_columns = []

        self.raise_warning = False  # 是否抛出告警

        self.__allow_missing_position: bool = False
        self.__cxpaths_for_rebuild = {}
        self.__build_header_cell_selectors(*config, cxpath=header_cell_xpath, tagname=header_cell_tagname,
                                           auto_set_position=auto_set_position)
        self.__build_body_cell_selectors(*config, cxpath=body_cell_xpath, tagname=body_cell_tagname,
                                         auto_set_position=auto_set_position)

    join_xpaths = AbstractPlaywrightPage.join_xpaths

    @property
    def parent(self):
        """获取底层页面或定位器对象。

        若传入的是 AbstractPlaywrightPage 包装对象，则返回其原始 Page 实例。
        """
        return self.__parent.pwpage if isinstance(self.__parent, AbstractPlaywrightPage) else self.__parent

    @parent.setter
    def parent(self, value: Union[Page, Locator, AbstractPlaywrightPage]):
        self.__parent = value

    @property
    def cxpaths_for_rebuild(self):
        """列索引到单元格内容元素相对 XPath 的映射字典。

        主要用于在显式调用 ``sync_from_dom`` 重建主体列（``body_columns``）时，
        保留或预设各列的 ``cxpath`` 配置。

        **为什么需要此属性？**
        当触发表头自动检测并重建列信息时，由于 DOM 中的表头单元格本身不包含 ``cxpath`` 信息，
        直接重建会导致原有的 ``cxpath`` 丢失（即定位退化为整个 ``<td>``，而非内部的 ``<div>`` 等元素）。
        此属性充当“记忆层”或“预设层”，确保重建后的列仍能精确定位到单元格内部元素。

        **使用场景：**
        - **自动保留**：在重建触发前，将现有 ``body_columns`` 的 ``cxpath`` 提取到此字典中，
        重建时这些值会被自动注入到对应索引的新列中。
        - **手动预设**：在初始化 ``Table`` 后，预先设置某些列索引的 ``cxpath``，
        当后续触发重建时，这些自定义路径将生效。

        Notes
        -----
        - **键**：列索引（从 1 开始的 int）。
        - **值**：相对 XPath 字符串（相对于 ``<td>`` 或 ``<th>`` 元素），如 ``"div/span"``。
        - 修改此映射**不会**立即同步到现有的 ``body_columns``，仅在下次调用
        ``sync_from_dom`` 或 ``rebuild_body_columns`` 时生效。
        - 若不需要保留或预设 ``cxpath``，可将其设置为空字典。
        """
        return self.__cxpaths_for_rebuild

    @property
    def allow_missing_position(self) -> bool:
        """是否允许列索引缺失。

        当列的 ``position`` 属性为 ``None`` 时，无法生成精确的单元格定位 XPath
        （例如 ``td`` 会由明确的``td[1]``退化为 ``td``，可能导致匹配到多个元素）。

        - 若为 ``False``（默认）：遇到未设置列索引的情况将抛出 ``ValueError`` 异常，确保定位的精确性。
        - 若为 ``True``：允许在未设置列索引的情况下继续执行，不抛出异常（但可能导致定位模糊）。
        """
        return self.__allow_missing_position

    @allow_missing_position.setter
    def allow_missing_position(self, v: bool):
        self.__allow_missing_position = v

    def sync_from_dom(self, mode: typing.Literal["sync", "rebuild"] = "rebuild",
                      by: typing.Literal["title", "position"] = "title",
                      sep: str = "-",
                      clear_non_data_column_marks: bool = False):
        """根据当前 DOM 表头状态，显式同步或重建内部列配置。

        此方法替代了旧版的隐式自动检测机制，将控制权交还给开发者。
        当表格列顺序可能发生变化，或初始化时未提供完整列信息时，可显式调用此方法。

        Parameters
        ----------
        mode : {'sync', 'rebuild'}, default='rebuild'
            同步模式。
            - ``'sync'``: 在现有 ``body_columns`` 基础上更新属性（如修正 position 或 cxpath）。
            - ``'rebuild'``: 完全根据 DOM 检测结果清空并重建 ``body_columns``。
        by : {'title', 'position'}, default='title'
            仅当 ``mode='sync'`` 时有效，指定按标题还是按索引匹配现有列。
        sep : str, default="-"
            多级表头合并时的分隔符。``titles`` 列表中的元素将以此分隔符拼接为最终的列标题。
        clear_non_data_column_marks : bool, default=False
            仅当 ``mode='rebuild'`` 时有效。是否在重建时清除之前标记的非数据列信息
            （通过 `mark_non_data_columns_*` 方法设置的标记）。
            为 True 时，重建后所有列都将被视为数据列，直到重新标记。

        Returns
        -------
        None

        Examples
        --------
        >>> table = Table(page, '专资编码', '院线', auto_set_position=False)
        >>> # 明确知道页面列顺序可能变化，手动触发同步
        >>> table.sync_from_dom(mode="rebuild")
        >>> row_el = table.row({"专资编码": "80002048"})
        """
        detection_result = self.detect_header_titles()
        print(detection_result)
        headers = detection_result.get("headers")
        if not headers:
            return

        format_headers = {
            i: {"titles": v, "cxpath": self.cxpaths_for_rebuild.get(i)}
            for i, v in enumerate(headers, start=1)
        }

        if mode == "sync":
            self.sync_body_columns(format_headers, by=by, sep=sep)
        elif mode == "rebuild":
            self.rebuild_body_columns(
                format_headers, sep=sep,
                clear_non_data_column_marks=clear_non_data_column_marks
            )

    def rebuild_body_columns(self, headers: typing.Dict[int, typing.Dict[str, typing.Any]], sep: str = "-", clear_non_data_column_marks: bool = False):
        """根据检测到的表头信息，完全重新生成表格主体列的定位信息。

        此方法会**清空并覆盖**现有的 `body_columns`，根据传入的 `headers` 重新构建所有主体列。
        通常由 ``sync_from_dom`` 调用，或在表格列信息需要彻底重置的场景下直接调用。

        Parameters
        ----------
        headers : typing.Dict[int, typing.Dict[str, typing.Any]]
            检测到的表头信息字典。键为列索引（从1开始），值为包含列详细信息的字典。
            值字典必须包含 ``titles`` 键（多级标题列表），可选包含 ``cxpath`` 键。
            示例：
            ```python
            {
                1: {"titles": ['影院信息', '编码'], "cxpath": 'div[@class="cell"]'},
                2: {"titles": ['影院信息', '名称'], "cxpath": 'div[@class="cell"]'}
            }
            ```
        sep : str, default="-"
            多级表头合并时的分隔符。``titles`` 列表中的元素将以此分隔符拼接为最终的列标题。
        clear_non_data_column_marks : bool, default=False
            是否在重建时清除之前标记的非数据列信息（通过 `mark_non_data_columns_*` 方法设置的标记）。
            为 True 时，重建后所有列都将被视为数据列，直到重新标记。

        Returns
        -------
        None
        """
        config = []
        for position, item in headers.items():
            title = sep.join(item["titles"])
            cxpath = item.get("cxpath")
            config.append({
                "title": title,
                "index": position,
                "cxpath": cxpath,
                "value": None
            })
        self.__build_body_cell_selectors(
            *config,
            tagname=self.default_tagname_of_body_cell
        )

        if clear_non_data_column_marks:
            self.position_of_non_data_columns.clear()
            self.title_of_non_data_columns.clear()

    def sync_body_columns(self, headers: typing.Dict[int, typing.Dict[str, typing.Any]], by: typing.Literal["title", "position"] = "position", sep="-"):
        """根据检测到的表头信息，同步（更新）现有表格主体列的定位信息。

        与 `rebuild_body_columns` 不同，此方法**不会**销毁并重建列，而是在现有 `body_columns` 的基础上，
        根据匹配条件原地更新列的 ``position``、``title`` 或 ``cxpath``。适用于仅需微调列属性的场景。

        Parameters
        ----------
        headers : typing.Dict[int, typing.Dict[str, typing.Any]]
            检测到的表头信息字典。键为列索引（从1开始），值为包含列详细信息的字典。
            值字典必须包含 ``titles`` 键（多级标题列表），可选包含 ``cxpath`` 键。
            示例：
            ```python
            {
                1: {"titles": ['影院信息', '编码'], "cxpath": 'div[@class="cell"]'},
                2: {"titles": ['影院信息', '名称'], "cxpath": 'div[@class="cell"]'}
            }
            ```
        by : {'position', 'title'}, default="position"
            指定以何种方式匹配现有列并进行同步更新：

            - ``'title'``：按列标题匹配。将现有列的标题与 ``headers`` 中的合并标题比对，
              匹配成功则更新该列的 ``position`` 和 ``cxpath``。
            - ``'position'``：按列索引匹配。将现有列的索引与 ``headers`` 的键比对，
              匹配成功则更新该列的 ``title`` 和 ``cxpath``。
        sep : str, default="-"
            多级表头合并时的分隔符。``titles`` 列表中的元素将以此分隔符拼接为最终的列标题。

        Returns
        -------
        None

        Raises
        ------
        ValueError
            当 ``by`` 参数不是 ``'title'`` 或 ``'position'`` 时抛出。
        """
        if by == "title":
            for position, item in headers.items():
                titles = item.get("titles")
                if not titles:
                    continue
                clean_title = sep.join(str(t).strip() for t in titles if t is not None)
                for column in self.body_columns:
                    if column.title == clean_title:
                        column.position = position
                        if "cxpath" in item:
                            column.cxpath = item["cxpath"]

        elif by == "position":
            for position, item in headers.items():
                titles = item.get("titles")
                if titles:
                    clean_title = sep.join(str(t).strip() for t in titles if t is not None)
                else:
                    clean_title = None
                for column in self.body_columns:
                    if column.position == position:
                        if clean_title is not None:
                            column.title = clean_title
                        if "cxpath" in item:
                            column.cxpath = item["cxpath"]
        else:
            raise ValueError(f"invalid by value: {by}, only 'title' or 'position' is allowed.")

    def __build_header_cell_selectors(self, *config, cxpath=None, tagname="th", auto_set_position=True):
        """构建表头列单元格选择器。

        将 config 配置转换为 CellSelector 列表，并设置单元格值为标题。
        """
        cells = self.__create_cell_selector(
            *config, cxpath=cxpath, tagname=tagname, auto_set_position=auto_set_position)
        for cell in cells:
            if cell.value is None:
                cell.value = cell.title
        self.__head_columns = cells

    def __build_body_cell_selectors(self, *config, cxpath=None, tagname="td", auto_set_position=True):
        """构建表格主体列单元格选择器。

        将 config 配置转换为 CellSelector 列表。
        """
        self.__body_columns = self.__create_cell_selector(
            *config, cxpath=cxpath, tagname=tagname, auto_set_position=auto_set_position)

    def __create_cell_selector(self, *config: Union[str, int, dict, list, tuple], cxpath=None, value=None, tagname="td", auto_set_position=True) -> List[CellSelector]:
        """创建单元格选择器列表。

        Parameters
        ----------
        config : Union[str, int, dict, list, tuple]
            单元格选择器配置信息。所有元素必须为同一类型，支持以下类型：

            - **str**：表头标题。
            - **int**：索引位置，从1开始。
            - **dict**：键名说明：

                > - ``title`` — 标题
                > - ``index`` — 索引位置
                > - ``cxpath`` — 内容元素相对xpath（可选，为None时不参与生成xpath）
                > - ``value`` — 单元格内容（可选，为None时不参与生成xpath）
                > - ``tagname`` — 单元格元素标签（可选）

            - **tuple | list**：子元素说明：

                > - 第1个元素 — 索引位置（必传）
                > - 第2个元素 — 标题（必传）
                > - 第3个元素 — 内容元素相对xpath（可选，为None时不参与生成xpath）
                > - 第4个元素 — 单元格内容（可选，为None时不参与生成xpath）
                > - 第5个元素 — 单元格元素标签（可选）

        cxpath : str, optional
            统一设置所有单元格的cxpath，优先级低于config中各单元格单独设置的cxpath。
            为None时不参与生成xpath。
        value : str, optional
            统一设置所有单元格的值，优先级低于config中各单元格单独设置的value。
            为None时不参与生成xpath。
        tagname : str, default="td"
            统一设置所有单元格的元素标签，优先级低于config中各单元格单独设置的tagname。
        auto_set_position : bool, default=True
            是否自动设置索引位置（仅config传入字符串时有效）。

        Returns
        -------
        List[CellSelector]
            列单元格定位信息列表。
        """

        nt = []
        same_indexs = set()
        if self.__all_is(config, str):
            for i, title in enumerate(config):
                if auto_set_position:
                    position = i + 1
                else:
                    position = None
                nt.append(CellSelector(position, title=title, cxpath=cxpath,
                          value=value, tagname=tagname))
        elif self.__all_is(config, int):
            for position in config:
                nt.append(CellSelector(position, cxpath=cxpath,
                          value=value, tagname=tagname))
        elif self.__all_is(config, dict):
            for title in config:
                ei = title[self.INDEX_KEY]
                et = title[self.TITLE_KEY]
                if ei in same_indexs:
                    raise ValueError('has same index: {}'.format(ei))
                else:
                    same_indexs.add(ei)
                cxpath = title.get(self.XPATH_KEY, cxpath)
                value = title.get(self.VALUE_KEY, value)
                tagname = title.get(self.TAGNAME_KEY, tagname)
                nt.append(CellSelector(ei, title=et, cxpath=cxpath,
                          value=value, tagname=tagname))
        elif self.__all_is(config, (tuple, list)):
            for title in config:
                ei = title[0]
                et = title = title[1]
                if ei in same_indexs:
                    raise ValueError('has same index: {}'.format(ei))
                else:
                    same_indexs.add(ei)
                if len(title) >= 3:
                    cxpath = title[2]
                if len(title) >= 4:
                    value = title[3]
                if len(title) >= 5:
                    tagname = title[4]
                nt.append(CellSelector(title[0], title=title[1], cxpath=cxpath,
                          value=value, tagname=tagname))
        else:
            raise ValueError(
                "invalid config, config  parameter can only be list or tuple, and it's subelement can only be one of a integer, string, dictionary, list, or tuple. {}".format(config))
        return nt

    def __all_is(self, datas, datatype):
        if not datas:
            return False
        r = True
        for d in datas:
            if not isinstance(d, datatype):
                r = False
                break
        return r

    @property
    def head_columns(self) -> typing.List[CellSelector]:
        """表头每列单元格的定位信息列表。

        包含一组 ``CellSelector`` 对象，描述了如何定位表格表头（``<thead>``）中的各个列。
        此列表在初始化时由 ``config`` 参数构建，主要用于生成 ``head_xpath``（实现“由列定表”的
        核心定位逻辑）以及 ``header_cells()`` 方法的精确查找。

        **注意：**
        与 ``body_columns`` 不同，若初始化时未显式指定表头列的 ``value``，
        内部会自动将其 ``value`` 设置为 ``title``。这确保了生成的表头 XPath 包含
        文本匹配条件（如 ``th/div[normalize-space()="列标题"]``），从而能在页面中
        精准定位到包含指定标题的表头单元格及所在的表格。
        """
        return self.__head_columns

    @property
    def body_columns(self) -> typing.List[CellSelector]:
        """表格主体每列单元格的定位信息列表。

        包含一组 ``CellSelector`` 对象，描述了如何定位表格主体（``<tbody>``）中的各个列。
        此列表是 ``row()``、``cells()``、``cell()`` 等数据提取与行定位方法的核心依据。

        **与 ``head_columns`` 的关键差异：**
        - **值处理**：主体列的 ``value`` 默认为 ``None``（除非初始化时显式指定），
          不会像表头列那样自动填充为 ``title``。因为主体单元格的值是动态数据，
          通常在运行时通过 ``row()`` 方法的 ``cells`` 参数动态注入，而非写死在配置中。
        - **动态更新**：可通过显式调用 ``sync_from_dom`` 方法，根据实际 DOM 中的表头结构
          重建（``rebuild_body_columns``）或同步（``sync_body_columns``）此列表。
        """
        return self.__body_columns

    @property
    def default_head_xpath(self) -> str:
        """表头基准 XPath，通常指向页面的 ``<thead>`` 元素。

        此路径是“由列定表”机制的起点。它将与 ``head_columns`` 中的列条件拼接，
        生成最终的 ``head_xpath``，从而在页面中唯一定位到包含指定列的目标表格。

        **默认值与覆盖：**
        默认配置为 Element UI 标准表格的路径
        （``//div[@id="app"]//div[contains(@class,"el-table__header-wrapper")]/table/thead``）。
        若页面存在多个表格、表格不在 ``#app`` 下，或使用了固定列（将表头拆分到独立的
        ``<table>`` 节点），则需在初始化后修改此属性，以指向正确的表头 DOM 节点。
        """
        return self.__default_head_xpath

    @default_head_xpath.setter
    def default_head_xpath(self, xpath):
        self.__default_head_xpath = xpath

    @property
    def default_body_xpath(self) -> str:
        """相对于 ``head_xpath`` 的表格主体 XPath，通常指向 ``<tbody>`` 元素。

        此路径用于从已定位的表头节点导航至对应的表格主体。最终会与 ``head_xpath``
        拼接生成 ``body_xpath``。

        **为什么使用相对路径？**
        在 Element UI 等前端框架中，表头（``<thead>``）和主体（``<tbody>``）往往被
        拆分到两个独立的 ``<table>`` DOM 节点下。使用相对路径（如基于 ``ancestor`` 和
        ``following-sibling`` 轴的导航），可以确保即使 DOM 结构分离，也能从表头
        无误地跨越到对应的数据主体区域。

        **默认值与覆盖：**
        默认配置适用于 Element UI 标准表格的兄弟节点跳转逻辑。若表格的 thead 与 tbody
        在同一个 ``<table>`` 内（标准 HTML 结构），可将其简化为 ``./tbody``。
        """
        return self.__default_body_xpath

    @default_body_xpath.setter
    def default_body_xpath(self, xpath):
        self.__default_body_xpath = xpath

    def set_body_cell_xpath(self, cxpath, *titles):
        """批量设置指定主体列的单元格内容元素相对 XPath。

        初始化时可通过 ``body_cell_xpath`` 参数统一设置所有主体列的 ``cxpath``，
        但当表格中某些特殊列（如包含超链接、图标或特殊嵌套结构的列）与默认结构不一致时，
        可使用此方法按列标题进行个性化覆盖。

        Parameters
        ----------
        cxpath : str
            单元格中内容元素的相对 XPath，相对于单元格元素（通常为 ``<td>``）。
            例如：``div[@class="special-cell"]//span``。
        titles : str
            要设置的列标题（可变参数，可传多个）。
            仅修改 ``body_columns`` 中标题匹配的列的 ``cxpath``。

        Returns
        -------
        self
            返回 Table 实例本身，支持链式调用。

        Examples
        --------
        >>> table = Table(page, '姓名', '年龄', '操作')
        >>> # 假设"操作"列的按钮被嵌套在特殊的 div 中
        >>> table.set_body_cell_xpath('div[@class="action-btns"]', '操作')
        """
        for col in self.body_columns:
            if col.title in titles:
                col.cxpath = cxpath
        return self

    def set_head_cell_xpath(self, cxpath, *titles):
        """批量设置指定表头列的单元格内容元素相对 XPath。

        功能与 ``set_body_cell_xpath`` 类似，但作用于表头列（``head_columns``）。
        修改表头列的 ``cxpath`` 会直接影响 ``head_xpath`` 的生成（即“由列定表”的定位逻辑），
        确保能精准匹配到包含特定内部结构的表头单元格。

        Parameters
        ----------
        cxpath : str
            单元格中内容元素的相对 XPath，相对于单元格元素（通常为 ``<th>``）。
        titles : str
            要设置的列标题（可变参数，可传多个）。

        Returns
        -------
        self
            返回 Table 实例本身，支持链式调用。
        """
        for col in self.head_columns:
            if col.title in titles:
                col.cxpath = cxpath
        return self

    def mark_non_data_columns_by_titles(self, *titles):
        """通过列标题将指定列标记为“非数据列”。

        在提取行数据（如调用 ``cells()`` 方法）时，某些列（如“操作”列，包含编辑/删除按钮；
        或“序号”列）不属于业务数据，将其标记后可自动排除，避免干扰数据字典的纯净性。

        Parameters
        ----------
        titles : str
            要标记为非数据列的列标题（可变参数，可传多个）。

        Returns
        -------
        self
            返回 Table 实例本身，支持链式调用。

        See Also
        --------
        mark_non_data_columns_by_position : 通过列索引标记非数据列。
        cells : 提取行数据时会自动跳过非数据列。
        """
        for title in titles:
            if title not in self.__title_of_non_data_columns:
                self.__title_of_non_data_columns.extend(titles)
        return self

    def mark_non_data_columns_by_position(self, *positions):
        """通过列索引将指定列标记为“非数据列”。

        功能与 ``mark_non_data_columns_by_titles`` 相同，但通过列的绝对位置（索引）进行标记。
        适用于表头标题动态变化、存在重复标题，或无明确标题的场景。

        Parameters
        ----------
        positions : int
            要标记为非数据列的列索引（可变参数，可传多个），从 1 开始。

        Returns
        -------
        self
            返回 Table 实例本身，支持链式调用。

        See Also
        --------
        mark_non_data_columns_by_titles : 通过列标题标记非数据列。
        cells : 提取行数据时会自动跳过非数据列。
        """
        for position in positions:
            if position not in self.__position_of_non_data_columns:
                self.__position_of_non_data_columns.append(position)
        return self

    @property
    def title_of_non_data_columns(self) -> typing.List[str]:
        """已标记为非数据列的标题列表。

        存储通过 ``mark_non_data_columns_by_titles`` 方法设置的列标题。
        在调用 ``cells()`` 等数据提取方法时，``body_columns`` 中标题匹配此列表的列将被排除。

        Notes
        -----
        - 此列表仅记录原始的标题标记，不包含按索引标记的列。
        - 若需获取所有非数据列的完整 ``CellSelector`` 对象，请使用 ``non_data_columns`` 属性。

        See Also
        --------
        mark_non_data_columns_by_titles : 添加标题标记的方法。
        non_data_columns : 解析后的完整非数据列对象列表。
        """
        return self.__title_of_non_data_columns

    @property
    def position_of_non_data_columns(self) -> typing.List[int]:
        """已标记为非数据列的索引列表（从 1 开始）。

        存储通过 ``mark_non_data_columns_by_position`` 方法设置的列索引。
        在调用 ``cells()`` 等数据提取方法时，``body_columns`` 中索引匹配此列表的列将被排除。
        适用于表头动态变化、存在重复标题或无明确标题的场景。

        Notes
        -----
        - 此列表仅记录原始的索引标记，不包含按标题标记的列。
        - 若需获取所有非数据列的完整 ``CellSelector`` 对象，请使用 ``non_data_columns`` 属性。

        See Also
        --------
        mark_non_data_columns_by_position : 添加索引标记的方法。
        non_data_columns : 解析后的完整非数据列对象列表。
        """
        return self.__position_of_non_data_columns

    @property
    def non_data_columns(self) -> typing.List[CellSelector]:
        """获取所有被标记为非数据列的单元格定位信息（解析后的最终结果）。

        此属性将 ``title_of_non_data_columns`` 和 ``position_of_non_data_columns`` 中的
        原始标记，映射回 ``body_columns`` 中对应的 ``CellSelector`` 对象。
        ``cells()`` 方法内部即使用此属性来过滤不需要返回的列（如操作列、序号列等）。

        Notes
        -----
        - **去重机制**：如果同一列同时通过标题和索引被标记，此属性只会返回一个对应的
          ``CellSelector`` 对象，不会重复。
        - **仅限主体列**：非数据列的查找范围仅限于 ``body_columns``，不涉及 ``head_columns``。

        See Also
        --------
        cells : 提取行数据时，会自动排除此属性包含的列。
        mark_non_data_columns_by_titles : 按标题标记非数据列。
        mark_non_data_columns_by_position : 按索引标记非数据列。
        """
        columns: typing.List[CellSelector] = []
        for position in self.__position_of_non_data_columns:
            for column in self.body_columns:
                if position == column.position:
                    if column not in columns:
                        columns.append(column)
        for title in self.__title_of_non_data_columns:
            for column in self.body_columns:
                if title == column.title:
                    if column not in columns:
                        columns.append(column)
        return columns

    def get_columns_by_title(self, title: str, body: bool = True) -> list[CellSelector]:
        """通过列标题获取所有匹配的列。

        Parameters
        ----------
        title : str
            列标题。
        body : bool, default=True
            若为True，从主体列（body_columns）中查找；
            若为False，从表头列（head_columns）中查找。

        Returns
        -------
        list[CellSelector]
            匹配的列列表（可能有多列标题相同）。

        Raises
        ------
        ValueError
            如果 title 为空，或指定的列集合未初始化。
        """
        source_columns = self.body_columns if body else self.head_columns
        if source_columns is None:
            raise ValueError(f"{'主体列 (body_columns)' if body else '表头列 (head_columns)'} 未初始化")
        matched_columns = [cell for cell in source_columns if cell.title == title]
        return matched_columns

    def get_columns_by_index(self, index: int, body: bool = True) -> List[CellSelector]:
        """通过列索引获取所有匹配的列。

        Parameters
        ----------
        index : int
            列索引，从1开始。
        body : bool, default=True
            若为True，从主体列中查找；若为False，从表头列中查找。

        Returns
        -------
        List[CellSelector]
            匹配的列列表。
        """
        columns = self.body_columns if body else self.head_columns
        return [cell for cell in columns if cell.position == index]

    def find_unset_position_column(self, body=True) -> typing.List[CellSelector]:
        columns = self.body_columns if body else self.head_columns
        return [column for column in columns if column.position is None]

    def get_duplicate_title_columns(self, body: bool = True) -> typing.Dict[str, List[CellSelector]]:
        """获取所有标题重复的列，按标题分组。

        遍历指定列集合（主体列或表头列），找出标题相同的列，
        并按标题分组返回。仅返回出现次数大于 1 的标题及其对应列。

        Parameters
        ----------
        body : bool, default=True
            若为 True，从主体列（body_columns）中查找；
            若为 False，从表头列（head_columns）中查找。

        Returns
        -------
        Dict[str, List[CellSelector]]
            标题到列列表的映射字典，仅包含重复标题的列。
            键为重复的标题文本，值为该标题对应的所有 CellSelector 对象列表。

        Examples
        --------
        >>> dup = table.get_duplicate_title_columns()
        >>> for title, cells in dup.items():
        ...     print(f\"重复标题 '{title}' 出现在列索引: {[c.position for c in cells]}\")
        """
        columns = self.body_columns if body else self.head_columns
        group = defaultdict(list)
        for cell in columns:
            group[cell.title].append(cell)
        return {title: cells for title, cells in group.items() if len(cells) > 1}

    def get_duplicate_position_columns(self, body: bool = True) -> typing.List[CellSelector]:
        """获取所有索引重复的列，按出现顺序扁平返回。

        遍历指定列集合（主体列或表头列），找出列索引（position）相同的列，
        将重复出现的列按原顺序拼成列表返回。仅返回出现次数大于 1 的索引对应的列。

        Parameters
        ----------
        body : bool, default=True
            若为 True，从主体列（body_columns）中查找；
            若为 False，从表头列（head_columns）中查找。

        Returns
        -------
        List[CellSelector]
            所有具有重复索引的 CellSelector 对象列表，按原列顺序排列。
            若无重复索引，返回空列表。

        Examples
        --------
        >>> dup = table.get_duplicate_position_columns()
        >>> for cell in dup:
        ...     print(f"重复索引 {cell.position}: {cell.title}")
        """
        columns = self.body_columns if body else self.head_columns
        group = defaultdict(list)
        for cell in columns:
            group[cell.position].append(cell)
        return [cell for cells in group.values() if len(cells) > 1 for cell in cells]

    @property
    def head_xpath(self) -> str:
        """最终生成的表头定位 XPath，是实现“由列定表”机制的核心。

        此 XPath 并非简单地指向页面上的 ``<thead>`` 元素，而是结合了 ``head_columns`` 中
        配置的列条件，生成一个**高精度**的定位表达式，确保只匹配包含指定列的目标表格。

        **生成逻辑：**
        1. 以 ``default_head_xpath`` 为起点，进入行元素（``<tr>``）。
        2. 依次拼接 ``head_columns`` 中各列的 XPath 条件（如 ``th/div[normalize-space()="列标题"]``）。
        3. 各列条件之间通过 ``/ancestor::tr/`` 连接，确保这些列条件**必须在同一行中同时满足**。
        4. 最后通过 ``/ancestor::thead`` 回溯到表头节点，作为最终的定位锚点。

        **示例生成的 XPath 结构：**
        ``xpath=//div[...]/thead/tr/th[1]/div[normalize-space()="姓名"]/ancestor::tr/th[2]/div[normalize-space()="年龄"]/ancestor::thead``

        Notes
        -----
        - 此属性为只读，动态根据 ``default_head_xpath`` 和 ``head_columns`` 生成。
          修改表头定位应修改 ``default_head_xpath`` 或通过初始化参数调整列配置。
        - 若 ``head_columns`` 为空，则退化为仅匹配 ``<thead>`` 元素。
        """
        p1 = self.join_xpaths(self.default_head_xpath, self.row_element_name)
        parts = []
        for column in self.__head_columns:
            cellxpath = column.xpath
            parts.append(cellxpath)
        r = '/ancestor::{}/'.format(self.row_element_name)

        rp = "/ancestor::{}".format(self.head_element_name)
        if parts:
            p2 = r.join(parts)
            xpath = self.join_xpaths(p1, p2, rp, prefix=self.XPATH_PREFIX)
        else:
            xpath = self.join_xpaths(p1, rp, prefix=self.XPATH_PREFIX)
        return xpath

    def header_rows(self, xpath_predicates=None) -> Locator:
        """获取匹配条件的表头行元素（``<tr>``）。

        在 ``head_xpath`` 定位到的表头范围内，查找符合条件的行元素。

        Parameters
        ----------
        xpath_predicates : str, optional
            附加在行元素上的 XPath 谓词条件。
            例如传入 ``2`` 可匹配第 2 行（生成 ``tr[2]``），
            传入 ``contains(@class, 'special')`` 可匹配特定类名的行。
            若为 None，则匹配表头下的所有行。

        Returns
        -------
        Locator
            匹配的表头行元素定位器。可能匹配到多个元素，可使用 ``.first`` 或 ``.nth()`` 筛选。
        """
        if xpath_predicates is None:
            hr_xpath = f'/{self.row_element_name}'
        else:
            hr_xpath = f'/{self.row_element_name}[{xpath_predicates}]'
        return self.parent.locator(self.join_xpaths(self.head_xpath, hr_xpath))

    def _match_header_column(self, title: Optional[str], position: Optional[int]) -> CellSelector:
        """
        从 head_columns 中匹配唯一的列。

        若同时提供 title 和 position，则必须同时满足。
        若只提供其一，则按该条件匹配。
        处理重复标题/索引的情况，并抛出明确的异常或警告。

        Returns:
            CellSelector: 匹配到的列对象。

        Raises:
            ValueError: 无匹配、或多个匹配且无法消除歧义时。
        """
        matched = [
            col for col in self.head_columns
            if (title is None or col.title == title) and (position is None or col.position == position)
        ]

        if not matched:
            available = [f"标题='{col.title}' (索引={col.position})" for col in self.head_columns]
            hint = []
            if title is not None:
                hint.append(f"标题 '{title}'")
            if position is not None:
                hint.append(f"索引 {position}")
            raise ValueError(
                f"未找到匹配的列：{' 且 '.join(hint)}。"
                f"当前表头配置的列有：{', '.join(available) if available else '（无配置）'}"
            )

        if len(matched) > 1:
            if position is None:
                # 标题重复且未指定 position -> 歧义
                positions = [col.position for col in matched]
                raise ValueError(
                    f"标题 '{title}' 存在多个匹配列（索引: {positions}），"
                    f"请同时指定 position 参数以消除歧义"
                )
            else:
                # 指定 position 仍有多个匹配（罕见），取第一个并警告
                warnings.warn(
                    f"列索引 {position} 对应多个列，将使用第一个匹配的列",
                    UserWarning
                )
                return matched[0]

        return matched[0]

    def header_cells(self, title: Optional[str] = None, position: Optional[int] = None,
                     tagname: str = "th", row: Optional[Union[int, Locator]] = None) -> Locator:
        """
        获取表头行中匹配指定条件的单元格元素。

        该方法基于初始化时配置的 `head_columns` 信息（标题/索引），在表头范围内精确定位单元格。
        它并不是盲目搜索 DOM，而是将配置条件转换为高效的 XPath 表达式。

        Parameters
        ----------
        title : str, optional
            列标题，对应 `head_columns` 中某个列的 `title` 属性。
            若未提供，则忽略标题匹配。
        position : int, optional
            列索引（从 1 开始），对应 `head_columns` 中某个列的 `position` 属性。
            若未提供，则忽略索引匹配。
            当存在重复标题时，可结合 `position` 精确定位到特定列。
        tagname : str, default="th"
            单元格的 HTML 标签名（如 `"th"` 或 `"td"`）。仅当未指定 `title` 或 `position`，
            且 `row` 为 `int` 时生效（即返回整行所有指定标签的单元格）。否则，该参数会被忽略，
            因为列配置中已定义了各列的 `tagname`。
        row : int or Locator, optional
            表头行的定位方式：
            - 若为 `int`（从 1 开始），表示第几行，将在由 `head_xpath` 定位的表头范围内查找该行。
            - 若为 `Locator`，则直接在该定位器范围内查找单元格（通常用于已定位到的行元素）。
            - 若为 `None`（默认），则匹配所有表头行中的单元格（即不限定行）。

        Returns
        -------
        Locator
            匹配到的单元格元素的 Playwright Locator 对象。
            可能匹配到多个元素，可通过 `.first`、`.nth()` 或 `.all()` 进一步筛选。

        Raises
        ------
        ValueError
            - 当同时提供了 `title` 和 `position`，但找不到同时满足两者的列时。
            - 当只提供 `title` 或 `position`，但在 `head_columns` 中找不到对应列时。
            - 当 `title` 在 `head_columns` 中存在重复，且未同时提供 `position` 来消除歧义时。
            - 当 `tagname` 不合法（非有效的 HTML 标签名）时。

        Warnings
        --------
        UserWarning
            当 `position` 对应多个列（罕见情况）时，会发出警告并选取第一个匹配的列。

        Notes
        -----
        - 若未提供 `title` 和 `position`，则返回指定行（或所有行）中所有标签为 `tagname` 的单元格。
        - 若 `row` 为 `Locator`，则直接在该定位器下查找，`head_xpath` 不会被使用。
        - 列配置中的 `cxpath`（单元格内容相对路径）会影响最终生成的 XPath，确保定位到内部元素。

        Examples
        --------
        假设表头配置为 `head_columns = [CellSelector(title='姓名', position=1),
                                    CellSelector(title='年龄', position=2)]`：

        >>> # 获取第 1 行中标题为 '姓名' 的单元格
        >>> cell = table.header_cells(title='姓名', row=1)
        >>> # 获取第 2 行中 position=2 的单元格
        >>> cell = table.header_cells(position=2, row=2)
        >>> # 获取所有行中标题为 '年龄' 的单元格（可能多个）
        >>> cells = table.header_cells(title='年龄')
        >>> # 获取已定位的行元素中的第 3 个 td 标签单元格（不限定标题/索引）
        >>> row_el = page.locator('//thead/tr[1]')
        >>> cell = table.header_cells(row=row_el, tagname='td')
        """
        # 校验 tagname（仅当未指定标题/索引时使用）
        if title is None and position is None:
            if not tagname or not re.match(r'^[a-zA-Z][a-zA-Z0-9]*$', tagname):
                raise ValueError(f"非法的标签名: {tagname}，标签名必须为合法的 HTML 标签格式")

        # ---- 1. 匹配列（如果提供了 title 或 position） ----
        target_col = None
        if title is not None or position is not None:
            target_col = self._match_header_column(title, position)

        # ---- 2. 根据 row 类型构建 XPath ----
        if isinstance(row, Locator):
            # 直接在行定位器下查找
            if target_col is not None:
                xpath = target_col.xpath
            else:
                # 未指定列条件，返回该行所有指定标签的单元格
                xpath = tagname
            return row.locator(self.join_xpaths(xpath, prefix=self.XPATH_PREFIX))

        else:
            # row 为 int 或 None -> 构造从 head_xpath 到行的路径
            if row is None:
                row_xpath = self.row_element_name
            else:
                row_xpath = f'{self.row_element_name}[{row}]'

            if target_col is not None:
                # 指定了列条件，定位到具体单元格
                cell_xpath = target_col.xpath
                full_xpath = self.join_xpaths(self.head_xpath, row_xpath, cell_xpath)
            else:
                # 未指定列条件，返回该行所有指定标签的单元格
                full_xpath = self.join_xpaths(self.head_xpath, row_xpath, tagname)

            return self.parent.locator(full_xpath)

    @property
    def body_xpath(self) -> str:
        """最终生成的表格主体定位 XPath，通常指向 ``<tbody>`` 元素。

        基于 ``head_xpath`` 和 ``default_body_xpath`` 拼接生成。

        **设计原理：**
        由于 ``head_xpath`` 已经通过列条件在页面中唯一定位到了目标表格的表头，
        ``body_xpath`` 只需从该表头节点出发，按照 ``default_body_xpath`` 配置的
        相对路径（如跨越兄弟节点）导航至对应的 ``<tbody>`` 即可，无需再次进行复杂的条件匹配。

        Notes
        -----
        - 此属性为只读，依赖于 ``head_xpath`` 的计算结果。
        - 若主体定位失败，通常是因为 ``default_body_xpath`` 的相对导航路径
          与实际 DOM 结构不匹配（如 thead 与 tbody 的层级关系发生变化）。
        """
        xpath = self.join_xpaths(self.head_xpath, self.default_body_xpath)
        return xpath

    def _warning_if_has_duplicate_titles(self):
        duplicate_title_columns = self.get_duplicate_title_columns(True)
        if duplicate_title_columns:
            warnings.warn(
                f"表格存在重复标题列: {duplicate_title_columns.keys()}",
                UserWarning,
                stacklevel=2
            )

    def _build_body_row_xpath(
        self,
        cells: dict,
        by: typing.Literal["title", "position"],
        el_type: str = "cell",
        target: Optional[Union[str, int]] = None
    ) -> str:
        """根据列标题或列索引构建表格主体行的 XPath 表达式。

        该方法支持按列标题或列位置定位行中的单元格，并通过拼接各单元格的 XPath 条件，
        实现对特定行的精确筛选。同时，可选择返回整行元素或行内特定单元格的 XPath。

        Parameters
        ----------
        cells : dict
            行筛选条件字典。
            - 当 ``by='title'`` 时，键为列标题字符串，值为期望的单元格文本内容。
            - 当 ``by='position'`` 时，键为列索引（从 1 开始），值为期望的单元格文本内容。
            - 若为空字典，表示不设置筛选条件，匹配所有行。
        by : {'title', 'position'}
            指定 ``cells`` 字典键的匹配方式：
            - ``'title'``：按列标题匹配。若存在重复标题，仅匹配第一个出现的列。
            - ``'position'``：按列索引匹配（推荐，可避免重复标题歧义）。
        el_type : {'cell', 'row'}, default='cell'
            返回的 XPath 指向的元素类型：
            - ``'cell'``：返回特定单元格的 XPath（由 ``target`` 指定）。
            - ``'row'``：返回整行（tr）的 XPath。
        target : str or int, optional
            当 ``el_type='cell'`` 时有效，指定要返回的单元格：
            - 若 ``by='title'``，``target`` 应为列标题字符串。
            - 若 ``by='position'``，``target`` 应为列索引（从 1 开始）。
            - 若为 ``None``，则默认返回表格的**第一个主体列**（``body_columns[0]``）的单元格。

        Returns
        -------
        str
            完整的 XPath 表达式（已包含 ``self.body_xpath`` 前缀），可直接用于 ``parent.locator()``。

        Raises
        ------
        ValueError
            - 当 ``cells`` 中存在不存在的列标题或列索引时抛出。
            - 当 ``el_type='cell'`` 且指定的 ``target`` 列不存在时抛出。
            - 当 ``el_type='cell'`` 且目标列未设置索引（position 为 None）时抛出。因为缺少索引将无法确定该列的具体位置，导致生成的 XPath 无法精确定位到特定单元格。

        Warnings
        --------
        - **安全性**：``cells`` 中的值会被直接嵌入 XPath 字符串的 ``normalize-space()`` 条件中。
          若值来源于不可信输入，请确保调用前对特殊字符（如引号）进行转义，防止 XPath 注入攻击。
        - **重复标题**：当 ``by='title'`` 且表头存在重复标题时，仅匹配第一个出现的列，
          可能导致非预期的定位结果。推荐在存在重复标题时使用 ``by='position'``。
        """
        row_xpath = f"./{self.row_element_name}"

        # 无筛选条件，返回所有行
        if not cells:
            return self.join_xpaths(self.body_xpath, row_xpath)

        if self.raise_warning and by == "title":
            self._warning_if_has_duplicate_titles()

        body_columns_copy: List[CellSelector] = [copy.copy(col) for col in self.__body_columns]
        # ── 1. 构建列查找映射（O(1) 查找，替代内层循环遍历） ──
        if by == "title":
            # 重复标题仅取第一个匹配列
            lookup: Dict[Union[str, int], CellSelector] = {}
            for col in body_columns_copy:
                lookup.setdefault(col.title, col)
        else:
            lookup = {col.position: col for col in body_columns_copy}

        # ── 2. 匹配 cells 中的列 ──
        matched_columns: List[CellSelector] = []
        not_found_keys: List[str] = []
        for key, value in cells.items():
            col = lookup.get(key)
            if col is not None:
                col.value = value
                matched_columns.append(col)
            else:
                not_found_keys.append(str(key))
        if not_found_keys:
            key_desc = "title" if by == "title" else "index"
            raise ValueError(
                f"The column {key_desc}(s) does not exist in body columns: "
                f"{', '.join(not_found_keys)}"
            )

        # ── 3. 按列索引排序（若所有列都有索引） ──
        could_sort = True
        for mcol in matched_columns:
            if not isinstance(mcol.position, int):
                could_sort = False
                break
        if could_sort:
            matched_columns.sort(key=lambda c: c.position)

        mp1 = []
        mp2 = []
        for mcol in matched_columns:
            target_key = mcol.title if by == "title" else mcol.position
            if target == target_key:
                mp2.append(mcol)
            else:
                mp1.append(mcol)
        matched_columns = mp1 + mp2
        # ── 4. 构建筛选条件 XPath：用 ancestor::tr 连接各单元格条件 ──
        row_axis = f"ancestor::{self.row_element_name}"
        filter_xpath = f"/{row_axis}/".join(col.xpath for col in matched_columns)

        # ── 5. 构建目标后缀 XPath ──
        if el_type == "cell":
            # target 为None时，则返回self.body_columns的第一个
            if target is not None:
                target_col = lookup.get(target)
            else:
                target_col = body_columns_copy[0]

            if target_col is None:
                key_desc = "title" if by == "title" else "index"
                raise ValueError(
                    f"The target column {key_desc} does not exist in body columns: {target}"
                )
            if not self.allow_missing_position and target_col.position is None:
                raise ValueError(
                    f"目标列 '{target_col.title}' 未设置列索引(position)，"
                    "无法生成精确的单元格定位 XPath"
                )
            if not row_axis.endswith(target_col.xpath):
                suffix = self.join_xpaths(row_axis, target_col.xpath)
        else:
            suffix = row_axis

        # ── 6. 拼接完整 XPath ──
        full_xpath = self.join_xpaths(row_xpath, filter_xpath)
        if not full_xpath.endswith(suffix):
            full_xpath = self.join_xpaths(full_xpath, suffix)
        return self.join_xpaths(self.body_xpath, full_xpath)

    def row(self, cells: dict, by: typing.Literal["title", "position"] = "title", **return_settings):
        """根据单元格内容条件定位表格主体中的行或单元格。

        通过指定列的期望文本内容构建 XPath 筛选条件，精确定位到满足所有条件的行，
        并可选择返回整行元素（``<tr>``）或行内某个特定单元格元素。

        Parameters
        ----------
        cells : dict
            行筛选条件字典，键值对表示「哪一列」应匹配「什么内容」。

            - 当 ``by='title'`` 时，**键**为列标题，**值**为期望的单元格文本内容。
            - 当 ``by='position'`` 时，**键**为列索引（int，从 1 开始），**值**为期望的单元格文本内容。
            - 多个键值对之间为 **AND** 关系，即所有条件必须同时满足。
            - 若传入空字典 ``{}``，则不设置任何筛选条件，匹配表格主体中的**所有行**。

            .. warning::
                ``cells`` 中的值会被直接嵌入 XPath 的 ``normalize-space()="..."`` 条件中。
                若值来源于不可信输入，请确保对引号等特殊字符进行转义，以防止 XPath 注入风险。

        by : typing.Literal["title", "position"], default='title'
            指定 ``cells`` 字典中键的匹配方式：

            - ``'title'``：按列标题匹配。当表头存在重复标题时，**仅匹配第一个出现的列**，
            可能导致非预期的定位结果。建议在存在重复标题时改用 ``'position'``。
            - ``'position'``：按列索引匹配（推荐），可避免重复标题歧义。

        **return_settings : dict
            控制返回元素类型和目标的关键字参数，支持以下选项：

            - **el_type** : ``typing.Literal["cell", "row"]``，默认 ``'cell'``
                指定返回的元素类型：

                - ``'row'``：返回匹配的整行元素（``<tr>``）。
                - ``'cell'``：返回行内某个特定单元格元素，具体由 ``title`` 或 ``index`` 参数决定。

            - **title** : str, optional
                仅当 ``by='title'`` 且 ``el_type='cell'`` 时有效。
                指定要返回的单元格所属列的标题。若未指定，则默认返回**第一个主体列**的单元格。

            - **index** : int, optional
                仅当 ``by='position'`` 且 ``el_type='cell'`` 时有效。
                指定要返回的单元格所属列的索引（从 1 开始）。若未指定，则默认返回**第一个主体列**的单元格。

        Returns
        -------
        Locator
            匹配的行或单元格的 Playwright Locator 对象。
            可能匹配到多个元素，可链式调用 ``.first``、``.nth()``、``.all()`` 等方法进一步筛选。

        Raises
        ------
        ValueError
            - 当 ``by`` 不是 ``'title'`` 或 ``'position'`` 时。
            - 当 ``cells`` 中存在不存在的列标题或列索引时。
            - 当 ``el_type='cell'`` 且指定的目标列（通过 ``title`` 或 ``index``）不存在时。
            - 当 ``el_type='cell'`` 且目标列未设置列索引（``position`` 为 ``None``）时，
            因为缺少索引将无法生成精确的单元格定位 XPath。

        Warnings
        --------
        - 当 ``by='title'`` 且表头存在重复标题时，仅匹配第一个出现的列，
        可能产生非预期的定位结果，建议改用 ``by='position'``。
        - ``cells`` 中的值会直接嵌入 XPath 字符串，请注意特殊字符转义以防止注入攻击。

        See Also
        --------
        all_rows : 获取表格所有行元素的快捷属性（等价于 ``row({})``）。
        cells : 获取一行中所有数据列的文本内容或 Locator。
        cell : 获取指定行中某个单元格的 Locator。

        Examples
        --------
        假设表格结构如下：

        | 序号 | 专资编码   | 影城名称         | 营业状态 |
        |------|-----------|-----------------|---------|
        | 1    | 80002048  | 影院名称-80002048 | 开业    |
        | 2    | 80002105  | 影院名称-80002105 | 停业    |

        >>> table = Table(page, '序号', '专资编码', '影城名称', '营业状态')

        **1. 按列标题筛选，返回整行元素**

        >>> row_el = table.row({"专资编码": "80002048", "营业状态": "开业"}, el_type="row")

        **2. 按列标题筛选，返回指定列的单元格**

        >>> # 返回"营业状态"列的单元格
        >>> cell_el = table.row({"专资编码": "80002048"}, title="营业状态")
        >>> # 未指定 title 时，默认返回第一个主体列（"序号"）的单元格
        >>> first_cell = table.row({"专资编码": "80002048"})

        **3. 按列索引筛选，返回指定列的单元格**

        >>> # 返回第 4 列（营业状态）的单元格
        >>> cell_el = table.row({2: "80002048"}, by="position", index=4)

        **4. 无筛选条件，获取所有行**

        >>> all_rows = table.row({})

        **5. 多条件组合筛选**

        >>> # 同时匹配"专资编码"和"营业状态"两个列的值
        >>> row_el = table.row({"专资编码": "80002048", "营业状态": "开业"}, el_type="row")
        """
        if by not in ("title", "position"):
            raise ValueError("by 参数必须是 'title' 或 'position'")

        el_type = return_settings.get("el_type", "cell")

        if by == "title":
            target = return_settings.get("title")  # 列标题
            selector = self._build_body_row_xpath(cells, by="title", el_type=el_type, target=target)
        else:  # by == "position"
            target = return_settings.get("index")  # 列索引
            selector = self._build_body_row_xpath(
                cells, by="position", el_type=el_type, target=target)

        return self.parent.locator(selector)

    @property
    def all_rows(self):
        """当前页面表格的所有行元素(tr)。"""
        return self.row({})

    def cells(self, row: Locator, return_locator: bool = False, title_as_key: bool = True) -> typing.Dict[str, typing.Union[str, Locator]]:
        """返回一行中各单元格的数据（仅返回初始化时定义的列）。

        被标记为非数据列（通过 `mark_non_data_columns_*` 方法）的单元格不会返回。

        **Usage**

        |序号|专资编码|影城名称|院线|影投| 营业状态|终端安装状态|安装登记状态|操作|
        |:----:|:----|:----|:----|:----|:----|:----|:----|:----|
        |1| 80002048 | 影院名称-80002048 |中影院线|无|未确认|已安装|未登记|删除|
        |2| 80002105 | 影院名称-80002105 |中影院线|无|未确认|已安装|未登记|删除|

        **按列标题定位并获取指定列**

        ```python
        table = Table(page, '专资编码', '影城名称', '院线', '影投', auto_set_position=False)
        for row in table.all_rows.all():
            # 返回: {'专资编码': '80002048', '影城名称': '影院名称-80002105', '院线': '中影院线', '影投': '无'}
            table.cells(row)
        ```

        **按列号定位并获取所有列**

        ```python
        table = Table(page, *range(1, 10))  # 定位到有9列的表格
        for row in table.all_rows.all():
            # 返回: {1: '1', 2: '80002105', 3: '影院名称-80002105', ...}
            table.cells(row, title_as_key=False)
        ```

        Parameters
        ----------
        row : Locator
            行元素。
        return_locator : bool, default=False
            若为True，返回元素Locator；若为False，返回元素文本内容。
        title_as_key : bool, default=True
            若为True，以列标题作为字典键；若为False，以列号（从1开始）作为字典键。
        """
        # 优化1：使用列表推导式过滤非数据列，提升可读性与性能
        columns = [c for c in self.body_columns if c not in self.non_data_columns]

        # 优化2：移除不必要的JS执行，直接使用Playwright原生API判断标签名，提升性能与安全性
        is_row_element = row.evaluate("el => el.tagName === 'TR'")

        return_cells = {}
        for cell in columns:
            # 优化3：提取公共逻辑，消除冗余代码（DRY原则）
            ckey = cell.title if title_as_key else cell.position

            if not self.allow_missing_position and cell.position is None:
                raise ValueError(f"列 '{cell.title}' 未设置列索引，无法生成精确的单元格定位 XPath")
            if is_row_element:
                # 优化4：简化XPath拼接逻辑，避免潜在的字符串拼接错误
                xpath = self.join_xpaths("./", cell.xpath, prefix=self.XPATH_PREFIX)
                el_cell = row.locator(xpath)
            else:
                el_cell = self.sibling_cell(row, cell.position, by="position")

            return_cells[ckey] = el_cell if return_locator else el_cell.text_content()

        return return_cells

    def cell(self, row: Locator, title_or_position: typing.Union[str, int], by: typing.Literal["title", "position"] = "title") -> Locator:
        """获取指定行中的某个单元格。

        Parameters
        ----------
        row : Locator
            行元素。
        title_or_position : str | int
            列标题或列索引（从1开始）。
        by : Literal["title", "position"], default="title"
            指定按列标题还是列索引查找。

        Returns
        -------
        Locator
            匹配的单元格元素。

        Raises
        ------
        ValueError
            当指定的列不存在时抛出。
        TypeError
            当 by="position" 但传入的不是整数时抛出。
        """
        # 优化1: 使用 Playwright 原生方法获取 tagName，避免自定义 JS 字符串及跨进程开销
        # 注意：如果 row 不存在或定位不到，此处会抛出异常，符合快速失败原则
        tag_name = row.evaluate("el => el.tagName")

        # 优化2: 类型校验，防止 str/int 隐式转换导致的匹配失败
        if by == "position" and not isinstance(title_or_position, int):
            raise TypeError(f"按列索引查找时，title_or_position 必须为 int 类型，当前传入: {type(title_or_position)}")

        # 优化3: 使用生成器表达式查找，找到即停止，提升性能与可读性
        target_column = next(
            (c for c in self.body_columns if getattr(c, by) == title_or_position),
            None
        )

        if target_column is None:
            dtype = "列标题" if by == "title" else "列号（从1开始）"
            cell_list = [{"列号": cell.position, "列标题": cell.title} for cell in self.body_columns]
            # 优化4: 使用 f-string 替代 format，提升可读性
            raise ValueError(
                f"表格未设置该列-> {dtype}：{title_or_position}，已设置的如下："
                f"{json.dumps(cell_list, ensure_ascii=False)}"
            )

        # 优化5: 移除冗余的 .lower() 比较，简化分支返回逻辑
        if isinstance(tag_name, str) and tag_name.lower() == "tr":
            if not self.allow_missing_position and target_column.position is None:
                raise ValueError(f"列'{target_column.title}'未设置position属性，无法生成精确的单元格定位 XPath")

            xpath = self.join_xpaths("./", target_column.xpath, prefix=self.XPATH_PREFIX)
            return row.locator(xpath)
        else:
            return self.sibling_cell(row, target_column.title)

    def sibling_cell(
        self,
        cell: Locator,
        target: typing.Union[str, int],
        by: typing.Literal["title", "position"] = "title"
    ) -> Locator:
        """获取当前单元格所在行中的兄弟单元格。

        Parameters
        ----------
        cell : Locator
            当前单元格元素。
        target : str | int
            目标单元格的列标题或列索引。
        by : Literal["title", "position"], default="title"
            指定按列标题还是列索引查找。

        Returns
        -------
        Locator
            同行中的兄弟单元格元素。

        Raises
        ------
        ValueError
            如果指定的 target 在 body_columns 中未找到。
        """
        # 优化1：使用 next() 和生成器表达式替代 for 循环，找到即停止，提升性能
        # 优化2：增加异常处理，防止未找到匹配项时 cxpath 未定义导致 UnboundLocalError 或逻辑错误
        target_col = next((col for col in self.body_columns if getattr(col, by) == target), None)
        if target_col is None:
            raise ValueError(f"未找到匹配的列：by='{by}', target='{target}'")

        # 优化3：使用 f-string 替代 format，提升可读性
        r = f'./ancestor::{self.row_element_name}'

        # 优化4：提前校验 cxpath，防止拼接出无效或恶意的 XPath
        if not target_col.xpath:
            raise ValueError("目标列的 xpath 属性为空，无法定位兄弟单元格")

        if not self.allow_missing_position and target_col.position is None:
            raise ValueError(f"列'{target_col.title}'未设置position属性，无法生成精确的单元格定位 XPath")
        xpath = self.join_xpaths(r, target_col.xpath, prefix=self.XPATH_PREFIX)

        return cell.locator(xpath)

    def _merge_header_rows(self, matrix: List[List[str]], sep: typing.Optional[str] = None) -> List[str]:
        """将多行表头合并为单行表头。

        Parameters
        ----------
        matrix : List[List[str]]
            表头矩阵，每行表头为一个字符串列表。
        sep : str, optional
            多级表头合并时的分隔符。若不指定，则返回每列的多级表头列表。

        Returns
        -------
        List[str]
            合并后的单行表头列表。
        """
        if not matrix:
            return []

        result = []
        for col in range(len(matrix[0])):
            column_header = []
            for row in range(len(matrix)):
                cell = matrix[row][col]
                # if cell and not cell.endswith('_merged'):
                #     column_header.append(cell)

                if isinstance(cell, str) and not cell.endswith('_merged'):
                    column_header.append(cell)

            if isinstance(sep, str):
                if column_header:
                    # 合并多级表头
                    merged_header = sep.join(column_header)
                    result.append(merged_header)
                else:
                    result.append(f'Column_{col + 1}')
            else:
                result.append(column_header)
        return result

    def detect_header_titles(self) -> Dict[typing.Literal['headers', 'merged_cells', 'header_matrix'], list]:
        """自动检测并提取表格的表头信息，支持多行表头及合并单元格。

        该方法通过 Playwright 定位表头行和单元格，构建一个二维矩阵来映射表头结构，
        并自动处理跨行跨列的合并单元格，最终提取出层级化的列标题信息。

        Returns
        -------
        Dict[Literal['headers', 'merged_cells', 'header_matrix'], list]
            包含表头详细信息的字典，结构如下：

            - **headers** : List[List[str]]
                合并后的列标题层级列表。每个元素是一个列表，包含该列从上到下的多级标题文本。
                （例如：`[['影院信息', '编码'], ['影院信息', '名称']]`）。
                *注意：此结果由内部 `_merge_header_rows` 生成，未使用分隔符拼接。*
            - **merged_cells** : List[Dict[str, any]]
                合并单元格的元信息列表。仅记录 colspan 或 rowspan 大于 1 的单元格，
                每个字典包含以下键：
                - ``text`` (str): 单元格文本内容。
                - ``row`` (int): 单元格起始行索引（从0开始）。
                - ``col`` (int): 单元格起始列索引（从0开始）。
                - ``colspan`` (int): 跨列数。
                - ``rowspan`` (int): 跨行数。
            - **header_matrix** : List[List[str]]
                原始表头矩阵（二维列表）。反映表头在 DOM 中的实际占位情况。
                被合并单元格覆盖的次要位置会填充为 `"{原文本}_merged"`，
                未被任何单元格占用的位置为空字符串 `""`。

        Notes
        -----
        - 该方法依赖 `header_rows` 和 `header_cells` 方法获取 DOM 元素。
        - `merged_cells` 中的 `row` 和 `col` 索引是基于生成的矩阵（从0开始），
          而非 Playwright 定位器通常使用的从1开始的索引。
        """
        merged_cells = []
        rows_locator = self.header_rows()
        hrows = rows_locator.count()
        if hrows == 0:
            return {'headers': [], 'merged_cells': [], 'header_matrix': []}

        # ── 优化1：利用 header_cells 接收 row Locator 的特性，按行批量提取数据 ──
        header_data = []
        for i in range(hrows):
            row_locator = rows_locator.nth(i)
            # 传入 row_locator，直接在该行下查找所有 th 单元格，XPath 更短，效率更高
            cells_locator = self.header_cells(row=row_locator)

            # 使用 evaluate_all 一次性提取该行所有单元格的 text, colspan, rowspan
            # 将原实现每行 3*M 次 IPC 降为每行 1 次
            row_data = cells_locator.evaluate_all("""(cells) => {
                const result = [];
                for (const cell of cells) {
                    result.push({
                        text: cell.textContent || '',
                        colspan: parseInt(cell.getAttribute('colspan') || '1', 10),
                        rowspan: parseInt(cell.getAttribute('rowspan') || '1', 10)
                    });
                }
                return result;
            }""")
            header_data.append(row_data)

        # ── 优化2：移除冗余的 _get_max_columns 嵌套函数，直接在内存数据中计算 ──
        max_cols = max(
            sum(cell['colspan'] for cell in row_data)
            for row_data in header_data
        )

        header_matrix = [[''] * max_cols for _ in range(hrows)]

        # ── 优化3：简化矩阵填充逻辑，移除冗余的恒真判断 ──
        for row_idx, row_data in enumerate(header_data):
            col_idx = 0
            for cell_info in row_data:
                cell_text = cell_info['text']
                colspan = cell_info['colspan']
                rowspan = cell_info['rowspan']

                # 跳过已被合并单元格占用的列
                while col_idx < max_cols and header_matrix[row_idx][col_idx] != '':
                    col_idx += 1

                if col_idx < max_cols:
                    # 预计算边界，简化内层循环判断
                    row_end = min(row_idx + rowspan, hrows)
                    col_end = min(col_idx + colspan, max_cols)

                    for r in range(row_idx, row_end):
                        for c in range(col_idx, col_end):
                            if r == row_idx:
                                header_matrix[r][c] = cell_text
                            else:
                                header_matrix[r][c] = f"{cell_text}_merged"

                    # 记录合并单元格元信息
                    if colspan > 1 or rowspan > 1:
                        merged_cells.append({
                            'text': cell_text,
                            'row': row_idx,
                            'col': col_idx,
                            'colspan': colspan,
                            'rowspan': rowspan
                        })

                col_idx += colspan

        # 合并多行表头
        headers = self._merge_header_rows(header_matrix)
        return {
            'headers': headers,
            'merged_cells': merged_cells,
            'header_matrix': header_matrix
        }
