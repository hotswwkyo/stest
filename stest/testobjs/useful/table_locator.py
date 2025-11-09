#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import re
import json
import typing
from typing import List
from typing import Union
from playwright.sync_api import Page
from playwright.sync_api import Locator
from stest.testobjs.abstract_playwright_page import AbstractPlaywrightPage


class Cell(object):

    SETABLE_PROPERTYS: typing.Final = (
        "title", "cxpath", "value", "position", "settings", "element_tag")

    def __init__(self, position, *, cxpath=None, title=None, value=None, element_tag="td", settings: dict = None):
        """

        Parameters
        ----------
        position : 单元格位置索引，从1开始
        cxpath : 单元格中内容元素xpath，相对于单元格元素（一般为th或td）
        title : 单元格标题
        value : 单元格内容
        element_tag : 单元格元素标签（一般为th或td）
        settings: dict 其它配置信息
        """

        self.title = title
        self.value = value
        self.position = position
        self.cxpath = cxpath
        self.element_tag = element_tag
        self.xpath_func = None
        self.settings: dict = {}
        if settings is not None:
            self.settings.update(settings)

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
            xpath = AbstractPlaywrightPage.join_xpaths(xpath, self.cxpath)
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

    def set_by_dict(self, **options):

        for k, v in options.items():
            if k in self.SETABLE_PROPERTYS:
                self.__setattr__(k, v)


class Table(object):
    """通用定位表格"""

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

    def __init__(self, parent: Union[Page, Locator, AbstractPlaywrightPage], *titles):
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
        self.__parent = parent
        self.__head_columns = self.__build_head_columns(*titles)
        self.__body_columns = self.__build_body_columns(*titles)
        self.row_element_name = self.ROW_ELEMENT_NAME
        self.head_element_name = self.HEAD_ELEMENT_NAME
        self.body_element_name = self.BODY_ELEMENT_NAME
        self.__default_head_xpath = self.DEFAULT_HEAD_XPATH
        self.__default_body_xpath = self.DEFAULT_BODY_XPATH
        self.__non_data_columns: typing.List[Cell] = []

    join_xpaths = AbstractPlaywrightPage.join_xpaths

    @property
    def parent(self):

        return self.__parent.pwpage if isinstance(self.__parent, AbstractPlaywrightPage) else self.__parent

    @parent.setter
    def parent(self, value: Union[Page, Locator, AbstractPlaywrightPage]):
        self.__parent = value

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
        same_indexs = set()
        if self.__all_subelement_is_datatype(str, titles):
            for i, title in enumerate(titles):
                nt.append(Cell(i + 1, title=title, cxpath=cxpath,
                          value=value, element_tag=element_tag))
        elif self.__all_subelement_is_datatype(dict, titles):
            for title in titles:
                ei = title[self.INDEX_KEY]
                et = title[self.TITLE_KEY]
                if ei in same_indexs:
                    raise ValueError('has same index: {}'.format(ei))
                else:
                    same_indexs.add(ei)
                cxpath = title.get(self.XPATH_KEY, cxpath)
                value = title.get(self.VALUE_KEY, value)
                nt.append(Cell(ei, title=et, cxpath=cxpath,
                          value=value, element_tag=element_tag))
        elif self.__all_subelement_is_datatype((tuple, list), titles):
            for title in titles:
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
                nt.append(Cell(title[0], title=title[1], cxpath=cxpath,
                          value=value, element_tag=element_tag))
        else:
            raise ValueError(
                "invalid titles, titles  parameter can only be list or tuple, and it's subelement can only be one of a string, dictionary, list, or tuple. {}".format(titles))
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
        """表头单元格"""
        return self.__head_columns

    @property
    def body_columns(self):
        """正文单元格"""
        return self.__body_columns

    @property
    def default_head_xpath(self):
        return self.__default_head_xpath

    @default_head_xpath.setter
    def default_head_xpath(self, xpath):
        """表格头部xpath，一般定位到table的thead元素"""
        self.__default_head_xpath = xpath

    @property
    def default_body_xpath(self):
        return self.__default_body_xpath

    @default_body_xpath.setter
    def default_body_xpath(self, xpath):
        """相对于default_head_xpath的body元素xpath，一般定位到table的tbody元素"""
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
        """设置表头表格单元格xpath

        Parameters
        ----------
        cxpath : 单元格中内容元素相对xpath，相对于单元格元素(td或th)
        titles : 单元格标题
        """

        for col in self.head_columns:
            if col.title in titles:
                col.cxpath = cxpath
        return self

    def add_exclude_titles(self, *titles):
        """标记非数据列，返回单元格数据时，排除标记的这些列单元格，如： 操作列 都是些按钮
        这时返回一行的各单元格数据时，就不用返回该列"""

        for title in titles:
            for cell in self.body_columns:
                if title == cell.title:
                    self.__non_data_columns.append(cell)
        return self

    def mark_non_data_columns_by_position(self, *poslist):

        for pos in poslist:
            for cell in self.body_columns:
                if pos == cell.position:
                    self.__non_data_columns.append(cell)
        return self

    def get_columns_by_title(self, title, body=True) -> typing.List[Cell]:
        """获取给定列标题的所有列

        Parameters
        ----------
        title: str
            列标题
        body: bool
            控制获取表头列，还是正文列，True-正文列 False-表头列, 默认值是True，即正文列
        """

        r_columns = []
        if body:
            columns = self.body_columns
        else:
            columns = self.head_columns

        for cell in columns:
            if cell.title == title:
                r_columns.append(cell)
        return r_columns

    def get_column_by_title(self, title, body=True):
        """通过列标题获取表格列，如果有相同标题的多列，则只返回第一个，建议使用`Table.get_column_by_index`来精确获取

        Parameters
        ----------
        title: str
            列标题
        body: bool
            控制获取表头列，还是正文列，True-正文列 False-表头列, 默认值是True，即正文列
        """

        if body:
            columns = self.body_columns
        else:
            columns = self.head_columns
        column = None
        for cell in columns:
            if cell.title == title:
                column = cell
                break
        if column is None:
            raise ValueError("The columns does not exist, column title : {}".format(title))
        return column

    def get_columns_by_index(self, index, body=True) -> typing.List[Cell]:
        """获取给定索引的所有列

        Parameters
        ----------
        index: int
            索引，从1开始
        body: bool
            控制获取表头列，还是正文列，True-正文列 False-表头列, 默认值是True，即正文列
        """

        r_columns = []
        if body:
            columns = self.body_columns
        else:
            columns = self.head_columns

        for cell in columns:
            if cell.position == index:
                r_columns.append(cell)
        return r_columns

    def get_column_by_index(self, index, body=True):
        """通过列索引获取表格列

        Parameters
        ----------
        index: int
            列索引，从1开始
        body: bool
            控制获取表头列，还是正文列，True-正文列 False-表头列, 默认值是True，即正文列
        """

        columns = self.get_columns_by_index(index, body)
        count = len(columns)
        if count < 1:
            raise ValueError("The columns does not exist, column index : {}".format(index))
        elif count == 1:
            return columns[0]
        else:
            raise ValueError("has duplicate column index, column index : {}".format(index))

    def get_duplicate_position_columns(self, which_part: typing.Literal["head", "body", "both"] = "both"):
        """获取table中body olumns和head columns各自存在相同position的列

        Parameters
        ----------
        which_part: str
            控制检查哪里有重复索引列
            - head 表头
            - body 正文
            - both 表头 和 正文

        Returns
        -------
        包含重复position信息的字典，{'head': [重复的head_cell列表], 'body': [重复的body_cell列表]}
        """

        def find_same_position_cells(columns):
            same = []
            group = {}
            for cell in columns:
                if cell.position in group:
                    group[cell.position].append(cell)
                else:
                    group[cell.position] = [cell]
            for position, cells in group.items():
                if len(cells) > 1:
                    same.extend(cells)
            return same

        result = {
            'head': [],
            'body': []
        }
        if which_part == "head":
            hc = find_same_position_cells(self.head_columns)
            result["head"].extend(hc)
        elif which_part == "body":
            bc = find_same_position_cells(self.body_columns)
            result["body"].extend(bc)
        elif which_part == "both":
            hc = find_same_position_cells(self.head_columns)
            bc = find_same_position_cells(self.body_columns)
            result["head"].extend(hc)
            result["body"].extend(bc)
        else:
            raise ValueError(
                "invalid value of which_part parameter, it can only be head, body or both.")
        return result

    def has_duplicate_position_columns(self, which_part: typing.Literal["head", "body", "both"] = "both"):
        """判断table中body_columns和head_columns各自内部是否存在相同position的cell，如果任一内部存在重复position返回True，否则返回False

        Parameters
        ----------
        which_part: str
            控制检查哪里有重复索引列
            - head 表头
            - body 正文
            - both 表头 和 正文

        Returns
        -------
        bool
        """
        def has_same_position(columns: typing.List[Cell]):
            positions = set()
            for cell in columns:
                if cell.position in positions:
                    return True
                positions.add(cell.position)
            return False

        if which_part == "head":
            return has_same_position(self.head_columns)
        elif which_part == "body":
            return has_same_position(self.body_columns)

        elif which_part == "both":
            return has_same_position(self.head_columns) or has_same_position(self.body_columns)
        else:
            raise ValueError(
                "invalid value of which_part parameter, it can only be head, body or both.")

    @property
    def head_xpath(self):
        """表头xpath"""
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

    def head_cell(self, title, index: typing.Optional[int] = None):
        """返回匹配的表头单元格

        Parameters
        ----------
        title: str
            单元格内容
        index: typing.Optional[int]
            单元格在行中的索引位置，从1开始
        """

        parts = []
        for column in self.__head_columns:
            if index is None:
                if column.title == title:
                    cellxpath = column.xpath
                    parts.append(cellxpath)
            else:
                if column.title == title and column.position == index:
                    cellxpath = column.xpath
                    parts.append(cellxpath)
        r = '/{}/'.format(self.row_element_name)
        if parts:
            if len(parts) > 2:
                p2 = r.join(parts)
            else:
                p2 = self.join_xpaths(r, parts[0])
            xpath = self.join_xpaths(self.head_xpath, p2)
        else:
            raise ValueError("未设置该标题：{}".format(title))
        return self.parent.locator(xpath)

    @property
    def body_xpath(self):
        xpath = self.join_xpaths(self.head_xpath, self.default_body_xpath)
        return xpath

    def row_xpath(self, cells: dict, **return_settings):
        """根据给定的行信息字段，生成行或者单元格xpath

        Parameters
        ----------
        cells: dict
            行信息字典, 如：{"专资编码":"80002048","营业状态":"开业"}，如果是空字典则返回匹配表格所有行的xpath
        return_settings:
            控制返回的xpath，变长参数，参数说明如下
            - `el_type`  元素类型，row 或者cell， row即行元素（tr）， cell即单元格元素（td或者th下的元素）, 默认返回cell的xpath
            - `title`  要返回的单元格的标题，el_type为cell时有效，不传则默认返回第一个单元格的xpath

        **Useage**

        Consider the following table:

        | 专资编码 |  影城名称  | 营业状态 |
        |:----:|:----|:-----|
        | 80002048 | 影院名称-80002048 | 开业 |
        | 80002105 | 影院名称-80002105 | 停业 |
        | 80002212 | 影院名称-80002212 | 开业 |


        ```python
        row_xpath({"专资编码":"80002048","营业状态":"开业"}, el_type="row")
        ### match -> | 80002048 | 影院名称-80002048 | 开业 |
        ```
        """

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
        """返回列表匹配的所有行，有相同标题的列时，建议用`row2(cells: dict, **return_settings)`方法

        Parameters
        ----------
        row : 行信息字典, 如：{"专资编码":"80002048","营业状态":"开业"}，如果是空字典则返回表格所有行
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

    def row_xpath2(self, cells: dict, **return_settings):
        """根据给定的行信息字段，生成行或者单元格xpath，当有相同标题的列时，该方法能准确生成，

        Parameters
        ----------
        cells: dict
            行信息字典，键为单元格所在列的索引, 如：{1:"80002048",2:"开业"}，索引从1开始，如果是空字典则返回匹配表格所有行的xpath
        return_settings:
            控制返回的xpath，变长参数，参数说明如下
            - `el_type`  元素类型，row 或者cell， row即行元素（tr）， cell即单元格元素（td或者th下的元素）, 默认返回cell的xpath
            - `index`  要返回的单元格的标题，el_type为cell时有效，不传则默认返回第一个单元格的xpath

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
        ```python
        row_xpath({1:"80002048",2:"开业"}, el_type="row")
        ### match -> | 80002048 | 影院名称-80002048 | 开业 |
        ```
        """

        p1 = "./{}".format(self.row_element_name)
        if not cells:
            return self.join_xpaths(self.body_xpath, p1)
        columns: List[Cell] = []
        for t, v in cells.items():
            for col in self.__body_columns:
                if col.position == t:
                    col.value = v
                    columns.append(col)
                    break
        columns.sort(key=lambda one: one.position)
        others = []
        for cell in columns:
            others.append(cell.xpath)
        p2 = '/ancestor::{}/'.format(self.row_element_name).join(others)
        el_type = return_settings.get("el_type", "cell")
        pos = columns[0].position if columns else self.body_columns[0].position
        column_index = return_settings.get("index", pos)
        if el_type == "cell":
            cell_xpath = ""
            for c in self.__body_columns:
                if c.position == column_index:
                    cell_xpath = c.xpath
                    break
            p3 = self.join_xpaths('ancestor::{}'.format(self.row_element_name), cell_xpath)
        else:
            p3 = 'ancestor::{}'.format(self.row_element_name)
        xpath = self.join_xpaths(p1, p2)
        if not xpath.endswith(p3):
            xpath = self.join_xpaths(xpath, p3)
        return self.join_xpaths(self.body_xpath, xpath)

    def row2(self, cells: dict, **return_settings):
        """返回列表匹配的所有行，该方法通过单元格所在列索引（从1开始）来传单元格内容

        Parameters
        ----------
        row : 行信息字典，键为单元格所在列的索引, 如：{1:"80002048",2:"开业"}，索引从1开始，如果是空字典则返回表格所有行
        return_settings : 控制返回的元素设置，变长参数，参数说明如下
            - `el_type`  元素类型，row 或者cell， row即行元素（tr）， cell即单元格元素（td或者th下的元素）, 默认返回cell
            - `index`  要返回的单元格的标题，el_type为cell时有效，不传则默认返回第一个单元格

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
        row({1:"80002048",2:"开业"}) -> | 80002048 | 影院名称-80002048 | 开业 |
        """

        selector = self.row_xpath2(cells, **return_settings)
        return self.parent.locator(selector)

    def cells(self, row: Locator, return_locator=False, title_as_key=True) -> typing.Dict[str, typing.Union[str, Locator]]:
        """返回一行的各单元格数据，非数据列不会返回

        Parameters
        ----------

        return_locator: bool
            控制返回元素locator还是返回元素内容
        """
        js_code = '(element)=> element.tagName;'
        tag_name = row.evaluate(js_code)
        return_cells = {}
        columns: typing.List[Cell] = []
        ndc_poslist = [ndc_cell.position for ndc_cell in self.__non_data_columns]
        for c in self.body_columns:
            if c.position not in ndc_poslist:
                columns.append(c)
        if isinstance(tag_name, str) and tag_name.lower() == "tr".lower():
            for cell in columns:
                xpath = self.join_xpaths("./", cell.xpath, prefix=self.XPATH_PREFIX)
                el_cell = row.locator(xpath)
                if title_as_key:
                    ckey = cell.title
                else:
                    ckey = cell.position
                return_cells[ckey] = el_cell if return_locator else el_cell.text_content()
        else:
            for cell in columns:
                el_cell = self.sibling_cell(row, cell.position, by="position")
                if title_as_key:
                    ckey = cell.title
                else:
                    ckey = cell.position
                return_cells[ckey] = el_cell if return_locator else el_cell.text_content()
        return return_cells

    def cell(self, row: Locator, title_or_position, by: typing.Literal["title", "position"] = "title"):

        # titles = [o.title for o in self.body_columns]
        js_code = '(element)=> element.tagName;'
        tag_name = row.evaluate(js_code)
        rc = None
        for c in self.body_columns:
            if by == "title":
                cv = c.title
            else:
                cv = c.position
            if cv == title_or_position:
                rc = c
        if rc is None:
            if by == "title":
                dtype = "列标题"
            else:
                dtype = "列号（从1开始）"
            celllist = [{"列号": cell.position, "列标题": cell.title}for cell in self.body_columns]
            raise ValueError("表格未设置该列->{}：{}，已设置的如下：{}".format(dtype,
                             title_or_position, json.dumps(celllist, ensure_ascii=False)))
        if isinstance(tag_name, str) and tag_name.lower() == "tr".lower():
            xpath = self.join_xpaths("./", rc.xpath, prefix=self.XPATH_PREFIX)
            el_cell = row.locator(xpath)
            return el_cell
        else:
            el_cell = self.sibling_cell(row, rc.title)
            return el_cell

    def sibling_cell(self, cell: Locator, condition, by: typing.Literal["title", "position"] = "title"):

        for col in self.body_columns:
            if by == "title":
                cv = col.title
            else:
                cv = col.position
            if cv == condition:
                cxpath = col.xpath
                break
        r = './ancestor::{}'.format(self.row_element_name)
        xpath = self.join_xpaths(r, cxpath, prefix=self.XPATH_PREFIX)
        return cell.locator(xpath)
