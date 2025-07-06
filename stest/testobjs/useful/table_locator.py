#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import re
from typing import List
from typing import Union
from playwright.sync_api import Locator
from stest.testobjs.abstract_playwright_page import AbstractPlaywrightPage as Page


class Cell(object):

    def __init__(self, position, *, cxpath=None, title=None, value=None, element_tag="td"):
        """

        Parameters
        ----------
        position : 单元格位置索引，从1开始
        cxpath : 单元格中内容元素xpath，相对于单元格元素（一般为th或td）
        title : 单元格标题
        value : 单元格内容
        element_tag : 单元格元素标签（一般为th或td）
        """

        self.title = title
        self.value = value
        self.position = position
        self.cxpath = cxpath
        self.element_tag = element_tag
        self.xpath_func = None

    def _add_condition(self, xpath, condition, logical_symbol="and"):
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

    def build_xpath(self):
        """生成单元格xpath，相对于行元素(一般为tr), cell.value为None时，value不参与生成xpath"""

        xpath = '{}[{}]'.format(self.element_tag, self.position)
        if self.cxpath:
            xpath = Page.join_xpaths(xpath, self.cxpath)
        if self.value is not None:
            xpath = self._add_condition(xpath, 'normalize-space()="{}"'.format(self.value))
        return xpath

    def set_xpath_func(self, xpath_func):
        """设置生成单元格xpath的函数

        Parameters
        ----------
        xpath_func : 生成单元格xpath的函数，接收一个参数，即单元格对象
        """

        self.xpath_func = xpath_func
        return self

    @property
    def xpath(self):
        """单元格xpath，相对于行元素(一般为tr)"""

        if callable(self.xpath_func):
            return self.xpath_func(self)
        else:
            return self.build_xpath()


class Table(object):
    """表格"""

    INDEX_KEY = "index"
    TITLE_KEY = "title"
    VALUE_KEY = "value"
    XPATH_KEY = "xpath"
    XPATH_PREFIX = "xpath="

    # 行元素名
    ROW_ELEMENT_NAME = "tr"

    HEAD_ELEMENT_NAME = 'thead'
    BODY_ELEMENT_NAME = 'tbody'

    # 表头标题头默认xpath
    DEFAULT_HEAD_XPATH = '//div[@id="app"]//div[contains(@class,"el-table__header-wrapper")]/table/thead'

    # 相对于DEFAULT_HEAD_XPATH的xpath
    DEFAULT_BODY_XPATH = './ancestor::table/parent::div/following-sibling::div[contains(@class,"el-table__body-wrapper")]/table/tbody'

    def __init__(self, parent: Union[Page, Locator], *titles):
        """

        Parameters
        ----------
        parent : 页面或父元素
        titles : 列表
            表格头部标题，列表的子元素只能是字符串、字典、列表和元祖中的一种
            - 字符串 则根据它所在列表的位置，确定标题列的索引
            - 字典 则键名如下：
                >- index 标题索引，xpath从1开始
                >- title 标题
                >- value 单元格值
                >- xpath 单元格中内容元素的相对xpath，相对于单元格元素（一般为th或td）
            - 列表或元祖 可以是两个或者四个元素的元祖或列表，两个元素则为 标题索引和标题；4个元素则为 标题索引、标题、单元格值、相对xpath

        Usage
        -----
        ```python
        #!/usr/bin/env python
        # -*- encoding: utf-8 -*-
        import json
        import typing
        from cfd_autotest.utils import helper
        from cfd_autotest.pages.menu_page import MenuPage
        from cfd_autotest.pages.pop_confirm_page import PopConfirmPage
        from cfd_autotest.pages.el_cascader import EL_CascaderPage
        from cfd_autotest.pages.el_select import EL_SelectPage
        from cfd_autotest.pages.calendar_page import CalendarPage
        from .edit_page import CinemaInfoEditPage
        from stest.testobjs.useful.table_locator import Table
        from stest.utils.function_mapper import FunctionMapper


        mapper = FunctionMapper()
        mapper.preset(dict(as_input=True))


        class OrderListPage(MenuPage):
            \"""网络安装工单管理列表页\"""

            def init(self):
                self.elements = typing.cast(OrderListPage.Elements, self.elements)
                self.actions = typing.cast(OrderListPage.Actions, self.actions)

            class Elements(MenuPage.Elements):

                def init(self):

                    self.page = typing.cast(OrderListPage, self.page)

                    self.titles = ['', '序号', '专资编码', '影城名称', '院线', '影投', '营业状态',
                                '终端绑定状态', '终端安装状态', '退报名状态', '专网签约状态', '推送联通日期', '宽带编码', '安装登记状态', '安装登记时间', '报备宽带编码', '安装审核状态', '联通安装日期', 'IPV6首次通信日期', '对账起始日期', '撤网日期', '操作']

                    # 可滚动的表格
                    self.middle_table = Table(self.page.pwpage, *self.titles)

                    # 右边固定列表
                    self.right_table = Table(self.page.pwpage, *self.titles)
                    self.right_table.default_head_xpath = '//div[@id="app"]//div[@class="el-table__fixed-right"]/div[contains(@class,"el-table__fixed-header-wrapper")]/table/thead'
                    self.right_table.default_body_xpath = './ancestor::table/parent::div/following-sibling::div[contains(@class,"el-table__fixed-body-wrapper")]/table/tbody'

                def __el_form_input(self, label):

                    xpath = '//div[contains(@class,"el-form-item")]/label[contains(@class,"el-form-item__label") and normalize-space()="{}"]/following-sibling::div[contains(@class,"el-form-item__content")]//input'.format(label)
                    return self.page.get_by_xpath(xpath)

                def __el_form_button(self, name):

                    xpath = '//form//button/span[normalize-space()="{}"]'.format(name)
                    return self.page.get_by_xpath(xpath)

                @property
                @mapper.mapping()
                def cinema_name(self):
                    \"""影城名称\"""

                    label = "影城名称"
                    return self.__el_form_input(label)

                @property
                @mapper.mapping()
                def cinema_code(self):
                    \"""专资编码\"""

                    label = "专资编码"
                    return self.__el_form_input(label)

                @property
                @mapper.mapping()
                def chain_name(self):
                    \"""院线名称\"""

                    label = "院线名称"
                    return self.__el_form_input(label)

                @property
                @mapper.mapping()
                def invest_name(self):
                    \"""影投名称\"""

                    label = "影投名称"
                    return self.__el_form_input(label)

                @property
                @mapper.mapping(etype='select')
                def open_status(self):
                    \"""营业状态\"""

                    label = "营业状态"
                    return self.__el_form_input(label)

                @property
                @mapper.mapping(etype='cascader')
                def city(self):
                    \"""省市\"""

                    label = "省市"
                    return self.__el_form_input(label)

                @property
                @mapper.mapping(etype='select')
                def is_upload_business_license(self):
                    \"""营业执照上传状态\"""

                    label = "营业执照上传状态"
                    return self.__el_form_input(label)

                @property
                @mapper.mapping(etype='select')
                def is_bing_ts(self):
                    \"""终端绑定状态\"""

                    label = "终端绑定状态"
                    return self.__el_form_input(label)

                @property
                @mapper.mapping(etype='select')
                def is_install_ts(self):
                    \"""终端安装状态\"""

                    label = "终端安装状态"
                    return self.__el_form_input(label)

                @property
                @mapper.mapping(etype='select')
                def zy_network_sign_status(self):
                    \"""专网签约状态\"""

                    label = "专网签约状态"
                    return self.__el_form_input(label)

                @property
                @mapper.mapping(etype='select')
                def is_push2china_unicom(self):
                    \"""推送联通状态\"""

                    label = "推送联通状态"
                    return self.__el_form_input(label)

                @property
                @mapper.mapping(etype='select')
                def is_have_network_order(self):
                    \"""是否回传宽带编码\"""

                    label = "是否回传宽带编码"
                    return self.__el_form_input(label)

                @property
                @mapper.mapping(etype='select')
                def back2cinema(self):
                    \"""退报名状态\"""

                    label = "退报名状态"
                    return self.__el_form_input(label)

                @property
                @mapper.mapping()
                def network_order(self):
                    \"""宽带编码\"""

                    label = "宽带编码"
                    return self.__el_form_input(label)

                @property
                @mapper.mapping(etype='select')
                def install_status(self):
                    \"""安装登记状态\"""

                    label = "安装登记状态"
                    return self.__el_form_input(label)

                @property
                @mapper.mapping(etype='select')
                def compare_network_order(self):
                    \"""宽带编码比对状态\"""

                    label = "宽带编码比对状态"
                    return self.__el_form_input(label)

                @property
                @mapper.mapping(etype='select')
                def duizhang_date_status(self):
                    \"""对账日期状态\"""

                    label = "对账日期状态"
                    return self.__el_form_input(label)

                @property
                @mapper.mapping(etype='select')
                def cancel_network_service(self):
                    \"""撤网状态\"""

                    label = "撤网状态"
                    return self.__el_form_input(label)

                @property
                @mapper.mapping()
                def beizhu(self):
                    \"""备注\"""

                    label = "备注"
                    return self.__el_form_input(label)

                @property
                def search(self):
                    \"""查询按钮\"""

                    return self.page.pwpage.get_by_role("button", name="查询")

                def find_row(self, row, **return_settings):
                    \"""返回列表匹配的首行

                    Args:
                        row: 行信息字典, {"专资编码":"61033701","影城名称":"中影北方国际影城（奥体店）"}
                        return_settings: 控制返回的元素设置，变长参数，参数说明如下
                            el_type: 元素类型，row 或者cell， row即行元素（tr）， cell即单元格元素（td或者th下的元素）, 默认返回cell
                            title: 要返回的单元格的标题，el_type为cell时有效，不传则默认返回第一个单元格
                    \"""
                    return self.middle_table.row(row, **return_settings)

                def find_rows(self, row, **return_settings):
                    \"""返回列表匹配的所有行

                    Args:
                        row: 行信息字典, {"专资编码":"61033701","影城名称":"中影北方国际影城（奥体店）"}
                        return_settings: 控制返回的元素设置，变长参数，参数说明如下
                            el_type: 元素类型，row 或者cell， row即行元素（tr）， cell即单元格元素（td或者th下的元素）, 默认返回cell
                            title: 要返回的单元格的标题，el_type为cell时有效，不传则默认返回第一个单元格
                    \"""

                    return self.middle_table.row(row, **return_settings)

                @property
                def all_rows(self):
                    \"""返回列表所有行\"""

                    return self.middle_table.row({})

                def __table_column_button(self, row, column_title, button_name):
                    \"""返回表格中匹配行的指定列的按钮

                    Args:
                        row: 行信息字典, {"专资编码":"61033701","影城名称":"中影北方国际影城（奥体店）"}
                        column_title: 列标题
                        button_name: 按钮名
                    \"""

                    xpath = 'div//button/span[normalize-space()="{}"]'.format(button_name)
                    self.right_table.set_body_cell_xpath(xpath, column_title)
                    return self.right_table.row(row, title=column_title)

                def __table_action_column_button(self, row, button_name):
                    \"""返回表格中匹配行的操作列的按钮

                    Args:
                        row: 行信息字典, {"专资编码":"61033701","影城名称":"中影北方国际影城（奥体店）"}
                        button_name: 按钮名
                    \"""

                    column_title = "操作"
                    return self.__table_column_button(row, column_title, button_name)

                def update(self, row):
                    \"""返回表格中匹配行的更新按钮

                    Args:
                        row: 行信息字典, {"专资编码":"61033701","影城名称":"中影北方国际影城（奥体店）"}
                    \"""

                    btn_name = "更新"
                    return self.__table_action_column_button(row, btn_name)

                def edit(self, row):
                    \"""返回表格中匹配行的编辑按钮

                    Args:
                        row: 行信息字典, {"专资编码":"61033701","影城名称":"中影北方国际影城（奥体店）"}
                    \"""

                    btn_name = "编辑"
                    return self.__table_action_column_button(row, btn_name)

                def review(self, row):
                    \"""返回表格中匹配行的安装审核按钮

                    Args:
                        row: 行信息字典, {"专资编码":"61033701","影城名称":"中影北方国际影城（奥体店）"}
                    \"""

                    btn_name = "安装审核"
                    return self.__table_action_column_button(row, btn_name)

                def cancel_review(self, row):
                    \"""返回表格中匹配行的撤销审核按钮

                    Args:
                        row: 行信息字典, {"专资编码":"61033701","影城名称":"中影北方国际影城（奥体店）"}
                    \"""

                    btn_name = "撤销审核"
                    return self.__table_action_column_button(row, btn_name)

                def cancel_registration(self, row):
                    \"""返回表格中匹配行的退报名按钮

                    Args:
                        row: 行信息字典, {"专资编码":"61033701","影城名称":"中影北方国际影城（奥体店）"}
                    \"""

                    btn_name = "退报名"
                    return self.__table_action_column_button(row, btn_name)

                def del_btn(self, row):
                    \"""返回表格中匹配行的删除按钮

                    Args:
                        row: 行信息字典, {"专资编码":"61033701","影城名称":"中影北方国际影城（奥体店）"}
                    \"""

                    btn_name = "删除"
                    return self.__table_action_column_button(row, btn_name)

                def page_number(self, number=None):
                    \"""获取分页页码元素

                    Parameters
                    ----------
                    number : 页码，默认为None，返回所有页码元素
                    \"""
                    if number is None:
                        predicates = ""
                    else:
                        predicates = 'normalize-space()="{}"'.format(number)
                    xpath = '//span[@class="el-pagination__sizes"]/following-sibling::ul[@class="el-pager"]/li[contains(@class,"number"){}]'.format(
                        predicates)
                    return self.page.get_by_xpath(xpath)

                @property
                def import_df(self):

                    return self.__el_form_button("导入")

            class Actions(MenuPage.Actions):

                def init(self):
                    self.page = typing.cast(OrderListPage, self.page)
                    self.edit_page = CinemaInfoEditPage()

                def enter(self):
                    \"""进入 网络安装工单管理列表页\"""

                    self.click_network_install_order_manage().sleep(1)
                    return self

                def select_city(self, province, city):
                    \"""选择省市\"""

                    self.page.elements.city.click()
                    self.sleep(1)
                    EL_CascaderPage().actions.select(province, city)
                    return self

                def pop_win(self):
                    helper.prompt()
                    return self

                def search(self, items: dict):
                    \"""设置查询条件，点击查询按钮进行查询\"""

                    def element_set(name, element, settings, args, kwargs):

                        etype = settings.get('etype', 'input')

                        if etype == 'input':
                            element.fill(args[0])
                        else:
                            element.click()
                            self.sleep(1)
                            if etype == 'upload':
                                from stest.utils import autoit_helper
                                autoit_helper.input_upload_file_path(args[0])
                            elif etype == 'date':
                                CalendarPage().actions.select_date(args[0])
                            elif etype == 'select':
                                EL_SelectPage().actions.select(args[0])
                            elif etype == 'cascader':
                                EL_CascaderPage().actions.select(*args[0])

                    for k in items:
                        mapper.execute(k, instance=self.page.elements, callback=element_set,
                                    callback_args=(items[k],))
                    self.page.elements.search.click()
                    return self

                def click_edit_btn(self, row: dict):
                    \"""点击编辑按钮

                    Parameters
                    ----------
                    row: 行信息字典, {"专资编码":"61033701","影城名称":"中影北方国际影城（奥体店）"}
                    \"""

                    self.page.elements.edit(row).click()
                    return self

                def cancel_review(self, qinfo):
                    \"""撤销审核\"""

                    self.page.elements.cancel_review(qinfo).click()

                def delete_cinema(self, row):
                    \"""删除影城

                    Parameters
                    ----------
                    row: 行信息字典, {"专资编码":"61033701","影城名称":"中影北方国际影城（奥体店）"}
                    \"""

                    self.page.elements.del_btn(row).click()
                    self.sleep(1)
                    PopConfirmPage().actions.confirm()
                    self.sleep(1)

                    return self

                def row_equals(self, row1: dict, row2: dict):

                    if not row1:
                        raise ValueError("行数据不能为空")
                    is_equal = True
                    for k, v in row1.items():
                        if row2[k] != v:
                            is_equal = False
                            break
                    return is_equal

                def check_table(self, *rows, **csettings):

                    ymlist = self.page.elements.page_number()
                    pagerows = []
                    match_rows = {}
                    rnumber = 0

                    el_yms = ymlist.all()
                    loop = el_yms if el_yms else [None]
                    for ym in loop:
                        if ym is not None:
                            css = ym.get_attribute("class").split()
                            if 'active' not in css:
                                ym.click()
                                self.sleep(1)

                        rowlist = self.page.elements.all_rows.all()
                        arows = []
                        for one in rowlist:
                            rnumber = rnumber + 1
                            # print("第{}行".format(rnumber))
                            pagerow = self.page.elements.middle_table.cells(one)
                            arows.append(pagerow)
                            pagerows.append(pagerow)
                            # print(json.dumps(pagerow, ensure_ascii=False))

                        for pos, erow in enumerate(rows):
                            for arow in arows:
                                if self.row_equals(erow, arow):
                                    mrows = match_rows.get(pos, [])
                                    mrows.append(pos)
                                    match_rows[pos] = mrows
                    not_found_rows = []
                    for rindex, erow in enumerate(rows):
                        if not match_rows.get(rindex, []):
                            not_found_rows.append(erow)
                    if not_found_rows:
                        raise AssertionError("在表格中未找到以下行：\n{}".format(
                            json.dumps(not_found_rows, ensure_ascii=False)))
                    return self

                def import_file(self, filepath):
                    \"""导入联通宽带编码

                    Parameters
                    ----------
                    filepath : 数据文件路径
                    \"""

                    from stest.utils import autoit_helper
                    self.page.elements.import_df.click()
                    self.sleep(1)
                    autoit_helper.input_upload_file_path(filepath)
                    return self

        ```
        """
        self.parent = parent
        self.__head_columns = self.__build_head_columns(*titles)
        self.__body_columns = self.__build_body_columns(*titles)
        self.row_element_name = self.ROW_ELEMENT_NAME
        self.head_element_name = self.HEAD_ELEMENT_NAME
        self.body_element_name = self.BODY_ELEMENT_NAME
        self.__default_head_xpath = self.DEFAULT_HEAD_XPATH
        self.__default_body_xpath = self.DEFAULT_BODY_XPATH
        self.__exclude_titles = []

    join_xpaths = Page.join_xpaths

    def __build_head_columns(self, *titles, element_tag="th"):

        columns = self.__format_titles(*titles, cxpath='div', element_tag=element_tag)
        for column in columns:
            if column.value is None:
                column.value = column.title
        return columns

    def __build_body_columns(self, *titles, element_tag="td"):

        columns = self.__format_titles(*titles, cxpath='div', element_tag=element_tag)
        return columns

    def __format_titles(self, *titles, cxpath=None, value=None, element_tag="td") -> List[Cell]:

        nt = []
        if self.__all_subelement_is_datatype(str, titles):
            for i, title in enumerate(titles):
                nt.append(Cell(i + 1, title=title, cxpath=cxpath,
                          value=value, element_tag=element_tag))
        elif self.__all_subelement_is_datatype(dict, titles):
            for title in titles:
                ei = title[self.INDEX_KEY]
                et = title[self.TITLE_KEY]
                cxpath = title.get(self.XPATH_KEY, cxpath)
                value = title.get(self.VALUE_KEY, value)
                nt.append(Cell(ei, title=et, cxpath=cxpath,
                          value=value, element_tag=element_tag))
        elif self.__all_subelement_is_datatype((tuple, list), titles):
            for title in titles:
                ei = title[0]
                et = title = title[1]
                if len(title) >= 3:
                    cxpath = title[2]
                if len(title) >= 4:
                    value = title[3]
                nt.append(Cell(title[0], title=title[1], cxpath=cxpath,
                          value=value, element_tag=element_tag))
        else:
            raise ValueError()
        return nt

    def __all_subelement_is_datatype(self, datatype, datas):

        if not datas:
            return False
        r = True
        for d in datas:
            if not isinstance(d, datatype):
                r = False
                break
        return r

    @property
    def head_columns(self):
        return self.__head_columns

    @property
    def body_columns(self):
        return self.__body_columns

    @property
    def default_head_xpath(self):
        return self.__default_head_xpath

    @default_head_xpath.setter
    def default_head_xpath(self, xpath):
        self.__default_head_xpath = xpath

    @property
    def default_body_xpath(self):
        return self.__default_body_xpath

    @default_body_xpath.setter
    def default_body_xpath(self, xpath):
        """相对于default_head_xpath的body元素xpath"""
        self.__default_body_xpath = xpath

    def set_body_cell_xpath(self, cxpath, *titles):
        """设置body单元格xpath

        Parameters
        ----------
        cxpath : 单元格中内容元素相对xpath，相对于单元格元素(td或th)
        titles : 单元格标题
        """

        for col in self.body_columns:
            if col.title in titles:
                col.cxpath = cxpath
        return self

    def set_head_cell_xpath(self, cxpath, *titles):

        for col in self.body_columns:
            if col.title in titles:
                col.cxpath = cxpath
        return self

    def add_exclude_titles(self, *titles):
        """标记非数据列，返回单元格数据时，排除标记的这些列单元格，如： 操作列 都是些按钮
        这时返回一行的各单元格数据时，就不用返回该列"""

        self.__exclude_titles.extend(titles)
        return self

    @property
    def head_xpath(self):

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

    @property
    def body_xpath(self):
        xpath = self.join_xpaths(self.head_xpath, self.default_body_xpath)
        return xpath

    def row_xpath(self, cells: dict, **return_settings):

        p1 = "./{}".format(self.row_element_name)
        if not cells:
            return self.join_xpaths(self.body_xpath, p1)
        columns: List[Cell] = []
        for t, v in cells.items():
            for col in self.__body_columns:
                if col.title == t:
                    col.value = v
                    columns.append(col)
                    break
        columns.sort(key=lambda one: one.position)
        others = []
        for cell in columns:
            others.append(cell.xpath)
        p2 = '/ancestor::{}/'.format(self.row_element_name).join(others)
        el_type = return_settings.get("el_type", "cell")
        t1 = columns[0].title if columns else self.body_columns[0].title
        title = return_settings.get("title", t1)
        if el_type == "cell":
            cell_xpath = ""
            for c in self.__body_columns:
                if c.title == title:
                    cell_xpath = c.xpath
                    break
            p3 = self.join_xpaths('ancestor::{}'.format(self.row_element_name), cell_xpath)
        else:
            p3 = 'ancestor::{}'.format(self.row_element_name)
        xpath = self.join_xpaths(p1, p2)
        if not xpath.endswith(p3):
            xpath = self.join_xpaths(xpath, p3)
        return self.join_xpaths(self.body_xpath, xpath)

    def row(self, cells: dict, **return_settings):
        """返回列表匹配的所有行

        Parameters
        ----------
        row : 行信息字典, 如：{"专资编码":"80002048","营业状态":"开业"}
        return_settings : 控制返回的元素设置，变长参数，参数说明如下
            - `el_type`  元素类型，row 或者cell， row即行元素（tr）， cell即单元格元素（td或者th下的元素）, 默认返回cell
            - `title`  要返回的单元格的标题，el_type为cell时有效，不传则默认返回第一个单元格

        Useage
        ------
        table as follow:

            --------------------------------------
            | 专资编码  |   影城名称    | 营业状态 |
            --------------------------------------
            | 80002048 | 影院名称-80002048 | 开业 |
            --------------------------------------
            | 80002105 | 影院名称-80002105 | 停业 |
            --------------------------------------
            | 80002212 | 影院名称-80002212 | 开业 |
            --------------------------------------
        row({"专资编码":"80002048","营业状态":"开业"}) -> | 80002048 | 影院名称-80002048 | 开业 |
        """

        selector = self.row_xpath(cells, **return_settings)
        return self.parent.locator(selector)

    def cells(self, row: Locator):
        """返回一行的各单元格数据，非数据列不会返回"""

        js_code = '(element)=> element.tagName;'
        tag_name = row.evaluate(js_code)
        return_cells = {}
        columns = []
        for c in self.body_columns:
            if c.title not in self.__exclude_titles:
                columns.append(c)
        if isinstance(tag_name, str) and tag_name.lower() == "tr".lower():
            for cell in columns:
                xpath = self.join_xpaths("./", cell.xpath, prefix=self.XPATH_PREFIX)
                el_cell = row.locator(xpath)
                return_cells[cell.title] = el_cell.text_content()
        else:
            for cell in columns:
                el_cell = self.sibling_cell(row, cell.title)
                return_cells[cell.title] = el_cell.text_content()
        return return_cells

    def cell(self, row: Locator, title):

        titles = [o.title for o in self.body_columns]
        js_code = '(element)=> element.tagName;'
        tag_name = row.evaluate(js_code)
        rc = None
        for c in self.body_columns:
            if c.title == title:
                rc = c
        if rc is None:
            raise ValueError("表格未设置该标题列：{}，已设置的表格标题列如下：{}".format(title, " ".join(titles)))
        if isinstance(tag_name, str) and tag_name.lower() == "tr".lower():
            xpath = self.join_xpaths("./", rc.xpath, prefix=self.XPATH_PREFIX)
            el_cell = row.locator(xpath)
            return el_cell
        else:
            el_cell = self.sibling_cell(row, rc.title)
            return el_cell

    def sibling_cell(self, cell: Locator, title):

        for col in self.body_columns:
            if col.title == title:
                cxpath = col.xpath
                break
        r = './ancestor::{}'.format(self.row_element_name)
        xpath = self.join_xpaths(r, cxpath, prefix=self.XPATH_PREFIX)
        return cell.locator(xpath)
