# -*- coding: utf-8 -*-
'''
Created on 2019年12月5日

@author: siwenwei
'''

from ..html import elements
from .piechart import PieChart


class SummaryTable(elements.Table):

    FIXED_WIDTH = "fixed-width"
    DEFAULT_CSS_CLASSES = ["seven-table", "summary"]
    PIE_CHART_FAIL_LABEL = "失败"
    PIE_CHART_FAIL_COLOR = "red"
    PIE_CHART_FAIL_CSS_CLASSES = {"pie_chart_css_class": "fail", "legend_css_class": "fail-legend", "legend_text_css_class": "fail-legend-text"}
    PIE_CHART_BLOCK_LABEL = "阻塞"
    PIE_CHART_BLOCK_COLOR = "sandybrown"
    PIE_CHART_BLOCK_CSS_CLASSES = {"pie_chart_css_class": "block", "legend_css_class": "block-legend", "legend_text_css_class": "block-legend-text"}

    PIE_CHART_ERROR_LABEL = "异常"
    PIE_CHART_ERROR_COLOR = "blueviolet"
    PIE_CHART_ERROR_CSS_CLASSES = {"pie_chart_css_class": "error", "legend_css_class": "error-legend", "legend_text_css_class": "error-legend-text"}

    PIE_CHART_SUCCESS_LABEL = "通过"
    PIE_CHART_SUCCESS_COLOR = "green"
    PIE_CHART_SUCCESS_CSS_CLASSES = {"pie_chart_css_class": "success", "legend_css_class": "success-legend", "legend_text_css_class": "success-legend-text"}

    PIE_CHART_SKIP_LABEL = "skip"
    PIE_CHART_SKIP_COLOR = "#c0c0c0"
    PIE_CHART_SKIP_CSS_CLASSES = {"pie_chart_css_class": "skip", "legend_css_class": "skip-legend", "legend_text_css_class": "skip-legend-text"}

    PIE_CHART_XFAIL_LABEL = "预期失败"
    PIE_CHART_XFAIL_COLOR = "#9acd32"
    PIE_CHART_XFAIL_CSS_CLASSES = {"pie_chart_css_class": "xfail", "legend_css_class": "xfail-legend", "legend_text_css_class": "xfail-legend-text"}

    PIE_CHART_XPASS_LABEL = "unexpected passes"
    PIE_CHART_XPASS_COLOR = "#a52a2a"
    PIE_CHART_XPASS_CSS_CLASSES = {"pie_chart_css_class": "xpass", "legend_css_class": "xpass-legend", "legend_text_css_class": "xpass-legend-text"}

    SVG_BOX_CSS_CLASSES = ["svg-box"]

    def __init__(self, title="", task_number="", start_time="", finish_time="", executor="", project_name="", task_description="", pie_chart_info=()):
        super().__init__()
        self.add_css_class(*self.DEFAULT_CSS_CLASSES)
        self.append_child(elements.Thead(), elements.Tbody())
        self.title = title
        self.task_number = task_number
        self.start_time = start_time
        self.finish_time = finish_time
        self.executor = executor
        self.project_name = project_name
        self.task_description = task_description
        self.pie_chart_info = pie_chart_info

    def _build_header(self):
        row = elements.TR()
        colspan = 3 if self.pie_chart_info else 2
        task_title_cell = elements.TD(self.title).add_css_class(self.FIXED_WIDTH).set_attr("colspan", colspan)
        row.append_child(task_title_cell)
        self.thead.append_child(row)

    def _build_body(self):
        self._set_task_number(self.task_number)
        self._set_project_name(self.project_name)
        self._set_executor(self.executor)
        self._set_start_time(self.start_time)
        self._set_finish_time(self.finish_time)
        self._set_task_description(self.task_description)

    def _set_task_number(self, task_number):

        title = "测试任务"
        row, title_col, value_col = self._build_row(title, task_number)
        if self.pie_chart_info and max(self.pie_chart_info) > 0:
            width = 500
            height = 260
            cx = 100
            cy = 100
            r = 100
            pass_count, fail_count, block_count, error_count, skip_count, xfail_count, xpass_count = self.pie_chart_info
            parts = [
                PieChart.build_part(pass_count, self.PIE_CHART_SUCCESS_LABEL, self.PIE_CHART_SUCCESS_COLOR, **self.PIE_CHART_SUCCESS_CSS_CLASSES),
                PieChart.build_part(fail_count, self.PIE_CHART_FAIL_LABEL, self.PIE_CHART_FAIL_COLOR, **self.PIE_CHART_FAIL_CSS_CLASSES),
                PieChart.build_part(block_count, self.PIE_CHART_BLOCK_LABEL, self.PIE_CHART_BLOCK_COLOR, **self.PIE_CHART_BLOCK_CSS_CLASSES),
                PieChart.build_part(error_count, self.PIE_CHART_ERROR_LABEL, self.PIE_CHART_ERROR_COLOR, **self.PIE_CHART_ERROR_CSS_CLASSES),
                PieChart.build_part(skip_count, self.PIE_CHART_SKIP_LABEL, self.PIE_CHART_SKIP_COLOR, **self.PIE_CHART_SKIP_CSS_CLASSES),
                PieChart.build_part(xfail_count, self.PIE_CHART_XFAIL_LABEL, self.PIE_CHART_XFAIL_COLOR, **self.PIE_CHART_XFAIL_CSS_CLASSES),
                PieChart.build_part(xpass_count, self.PIE_CHART_XPASS_LABEL, self.PIE_CHART_XPASS_COLOR, **self.PIE_CHART_XPASS_CSS_CLASSES),
            ]
            pie = PieChart(parts, width, height, cx, cy, r)
            pie_chart_column = elements.TD().set_attr("rowspan", 6)
            pie_chart_column.add_css_class(*self.SVG_BOX_CSS_CLASSES)
            pie_chart_column.append_child(pie)
            row.append_child(pie_chart_column)

        self.tbody.append_child(row)

    def _build_row(self, title, value):
        row = elements.TR()
        task_title_cell = elements.TD(title).add_css_class(self.FIXED_WIDTH)
        task_value_cell = elements.TD(value)
        row.append_child(task_title_cell)
        row.append_child(task_value_cell)
        return (row, task_title_cell, task_value_cell)

    def _set_task_description(self, task_description):

        title = "描述"
        row, title_col, value_col = self._build_row(title, task_description)
        self.tbody.append_child(row)

    def _set_project_name(self, project_name):

        title = "项目名称"
        row, title_col, value_col = self._build_row(title, project_name)
        self.tbody.append_child(row)

    def _set_executor(self, executor):

        title = "任务执行人"
        row, title_col, value_col = self._build_row(title, executor)
        self.tbody.append_child(row)

    def _set_start_time(self, start_time):

        title = "开始时间"
        row, title_col, value_col = self._build_row(title, start_time)
        self.tbody.append_child(row)

    def _set_finish_time(self, finish_time):

        title = "完成时间"
        row, title_col, value_col = self._build_row(title, finish_time)
        self.tbody.append_child(row)


class ReportTable(elements.Table):

    DEFAULT_CSS_CLASSES = ["seven-table", "details"]
    FIXED_HEADER_TITLES = ["测试点 / 测试用例", "总计", "通过", "失败", "阻塞", "异常", "skip", "预期失败", "unexpected passes"]
    TESTPOINT_ID_PREFIX = "testpoint_"
    TESTCASE_ID_PREFIX = "testcase_"
    ID_SEP = "."
    TESTPOINT_ROW_CSS_CLASS = "testpoint"
    TESTPOINT_NAME_CSS_CLASS = "testpoint-name"
    TESTPOINT_COUNT_CSS_CLASS = "testpoint-count"
    TESTPOINT_PASS_CSS_CLASS = "testpoint-pass"
    TESTPOINT_FAIL_CSS_CLASS = "testpoint-fail"
    TESTPOINT_BLOCK_CSS_CLASS = "testpoint-block"
    TESTPOINT_ERROR_CSS_CLASS = "testpoint-error"

    TESTPOINT_SKIP_CSS_CLASS = "testpoint-skip"
    TESTPOINT_XFAIL_CSS_CLASS = "testpoint-xfail"
    TESTPOINT_XPASS_CSS_CLASS = "testpoint-xpass"

    TESTCASE_ROW_CSS_CLASS = ["testcase", "testcase-show"]
    TESTCASE_NAME_COL_CSS_CLASS = "testcase-name"
    TESTCASE_RESULT_COL_CSS_CLASS = "testcase-result"
    TESTSTEPS_ZONE_ROW_ID = "teststeps"
    TESTSTEPS_ZONE_ROW_CSS_CLASS = "teststeps"
    TESTSTEP_ID_PREFIX = "teststep_"
    TESTSTEP_TABLE_CONTAINER_CSS_CLASS = "seven-table-container"

    SCREENSHOT_OF_TEST_FAILURE = "screenshot-of-test-failure"
    TESTCASE_SHOW_INFO_LAYER = 'testcase-show-info-layer'

    def __init__(self, testpoints=[]):
        super().__init__()
        self._header_titles = []
        self._testpoints = testpoints
        self._header_titles.extend(self.FIXED_HEADER_TITLES)
        self.append_child(elements.Thead(), elements.Tbody())
        self.add_css_class(*self.DEFAULT_CSS_CLASSES)

    def set_testpoints(self, *testpoints):

        self._testpoints = testpoints

    @property
    def header_titles(self):
        return self._header_titles

    def add_header_titles(self, title, index=None):

        if isinstance(index, int) and index >= 0:
            self._header_titles.insert(index, title)
        else:
            self._header_titles.append(title)
        return self

    def _build_header(self):

        tr = elements.TR()
        for col_title in self.header_titles:
            cell = elements.TH(col_title)
            tr.append_child(cell)
        self.thead.append_child(tr)
        return self

    def __build_params_area(self, arguments_dict, label="", param_type="args"):
        """构建参数显示区域

        Args:
            - arguments_dict: 参数字典
            - param_type: 参数类型 args - 位置参数      kwargs - 关键字参数
            - label: 区域标签名
        """

        el_fs, el_item, el_title, el_content = self.__build_fieldset()
        el_title_name = elements.Span(label)
        el_title.append_child(el_title_name)
        if param_type == "args":
            el_title_name.add_css_class("seven-testcase-args")
        elif param_type == "kwargs":
            el_title_name.add_css_class("seven-testcase-kwargs")
        else:
            # 无效类型则什么都不做，也不抛异常
            return

        for k, v in arguments_dict.items():
            fs = elements.Fieldset(k)
            styles = ["border-top-style: solid; border-top-width: 1px; border-left: none; border-right: none; border-bottom: none;"]
            styles.append("border-color: #e6e6e6;")
            styles.append("margin-left: 7px;")
            styles.append("margin-right: 7px;")
            fs.set_attr("style", "".join(styles))
            fs.append_child(elements.Pre(v).set_attr("style", "padding-left: 21px; padding-right: 21px;"))
            el_content.append_child(fs)
        return el_fs

    def __build_extra_info_area(self, extra_info, label=""):

        namemaps = {
            "author": "编写者",
            "editors": "修改者",
            "last_modifyied_by": "最后修改者",
            "last_modified_time": "最近修改时间",
        }

        el_fs, el_item, el_title, el_content = self.__build_fieldset()
        el_title_name = elements.Span(label)
        el_title.append_child(el_title_name)
        el_item.add_css_class("seven-fieldset-item-hidden")
        el_title_name.add_css_class("seven-testcase-extra-info")

        for k, v in extra_info.items():
            if not v:
                continue
            v = ",".join(v) if isinstance(v, (list, tuple)) else v
            el_dl, el_dt, el_dd = self.__build_seven_dl(namemaps.get(k, k), elements.Pre(v))

            el_content.append_child(el_dl)
        return el_fs

    def __build_fieldset(self):

        el_fs = elements.Div()
        el_item = elements.Div()
        el_title = elements.Div()
        el_content = elements.Div()

        el_fs.append_child(el_item)
        el_item.append_child(el_title)
        el_item.append_child(el_content)

        el_fs.add_css_class("seven-fieldset")
        el_item.add_css_class("seven-fieldset-item")
        el_title.add_css_class("seven-fieldset-title")
        el_content.add_css_class("seven-fieldset-content")

        return (el_fs, el_item, el_title, el_content)

    def __build_seven_dl(self, dt_val, dd_val, is_block=True):

        el_dl = elements.DL()
        el_dt = elements.DT()
        el_dd = elements.DD()

        el_dl.append_child(el_dt).append_child(el_dd)

        el_dl.add_css_class("seven-dl")
        el_dt.add_css_class("seven-dt")
        el_dd.add_css_class("seven-dd")

        if is_block:
            el_dl.add_css_class("seven-block")

        if isinstance(dt_val, elements.HtmlElement):
            el_dt.append_child(dt_val)
        else:
            el_dt.text = dt_val

        if isinstance(dd_val, elements.HtmlElement):
            el_dd.append_child(dd_val)
        else:
            el_dd.text = dd_val

        return (el_dl, el_dt, el_dd)

    def __build_screenshot_area(self, screenshot_info, label="截图"):

        el_fs, el_item, el_title, el_content = self.__build_fieldset()
        el_title_name = elements.Span(label)

        el_title.append_child(el_title_name)
        el_item.add_css_class("seven-fieldset-item-hidden")
        el_title_name.add_css_class("seven-testcase-screenshots")

        screenshot = screenshot_info.get('screenshot', False)
        attach_screenshot_to_report = screenshot_info.get('attach_screenshot_to_report', False)
        if screenshot and attach_screenshot_to_report:
            if screenshot_info.get("result", False):
                src = "data:image/png;base64,{}".format(screenshot_info.get("base64data", ""))
                showview = elements.Img().set_attr("onclick", 'show_image_on_new_window(this)').set_attr("src", src)
            else:
                showview = elements.Pre(screenshot_info.get("message", ""))
            showview.add_css_class(self.SCREENSHOT_OF_TEST_FAILURE)
            el_content.append_child(showview)
        return el_fs

    def __build_message_area(self, message_list, label="控制台信息"):

        el_fs, el_item, el_title, el_content = self.__build_fieldset()
        el_title_name = elements.Span(label)

        el_title.append_child(el_title_name)
        el_title_name.add_css_class("seven-testcase-traceback")

        outputmsg = '\n'.join(message_list) if message_list else ''
        el_content.append_child(elements.Pre(outputmsg))
        return el_fs

    def _build_console_row(self, testcase_html_id, teststep_zone_html_id, testcase):
        """构建输出控制台区域行"""

        message = [testcase["output_message"], testcase["error_message"]]
        testdatas = testcase['testdatas']
        screenshot_info = testcase["screenshot_info"]
        attach_screenshot_to_report = screenshot_info.get('attach_screenshot_to_report', False)
        args, kwargs = testdatas
        nargs = {}
        for k, v in args.items():
            name = " - ".join([str(k), v[0]])
            nargs[name] = v[1]

        row = elements.TR().set_attr("id", teststep_zone_html_id).add_css_class(self.TESTSTEPS_ZONE_ROW_CSS_CLASS)
        colspan = len(self.header_titles)
        cell = elements.TD().set_attr("colspan", colspan).add_css_class(self.TESTSTEP_TABLE_CONTAINER_CSS_CLASS)
        show_div = elements.Div()
        show_div.add_css_class(self.TESTCASE_SHOW_INFO_LAYER)
        if nargs:
            show_div.append_child(self.__build_params_area(nargs, label="位置参数", param_type="args"))
        if kwargs:
            show_div.append_child(self.__build_params_area(kwargs, label="关键字参数", param_type="kwargs"))
        if message[0] or message[1]:
            show_div.append_child(self.__build_message_area(message))
        show_div.append_child(self.__build_extra_info_area(testcase["extra_info"], label="基本信息"))
        if attach_screenshot_to_report:
            show_div.append_child(self.__build_screenshot_area(screenshot_info, label="截图"))
        cell.append_child(show_div)
        row.append_child(cell)
        return row

    def _build_testcases_rows(self, teststep_html_id, testcases):

        rows = []
        for index, tc in enumerate(testcases):

            tc_html_id = "%(tp_id)s%(sep)s%(prefix)s%(sn)s" % dict(tp_id=teststep_html_id, sep=self.ID_SEP, prefix=self.TESTCASE_ID_PREFIX, sn=(index + 1))
            teststep_zone_html_id = "%(tc_id)s%(sep)s%(sn)s" % dict(tc_id=tc_html_id, sep=self.ID_SEP, sn=self.TESTSTEPS_ZONE_ROW_ID)
            row = elements.TR().set_attr("id", tc_html_id).add_css_class(*self.TESTCASE_ROW_CSS_CLASS)
            row.set_attr("onclick", "toggleTestStepsRow('%s')" % teststep_zone_html_id)
            preceding_siblings = []
            name_cell = elements.TD(tc["name"])
            name_cell.add_css_class(self.TESTCASE_NAME_COL_CSS_CLASS)
            name_cell.set_attr("title", tc["method_name"])
            preceding_siblings.append(name_cell)
            row.append_child(*preceding_siblings)

            result_cell = elements.TD(tc["result"]["name"])
            result_cell.add_css_class(self.TESTCASE_RESULT_COL_CSS_CLASS, tc["result"]["css_class"])
            # result_cell.set_attr("style", "cursor: pointer;")
            duration = tc["duration"]
            timecell = elements.TD('{}秒'.format(duration) if duration else '')
            preceding_siblings.append(timecell)
            result_cell.set_attr("colspan", len(self.header_titles) - len(preceding_siblings))
            row.append_child(result_cell)
            row.append_child(timecell)
            row.after(self._build_console_row(tc_html_id, teststep_zone_html_id, tc))
            rows.append(row)
        return rows

    def build_testpoints_rows(self):

        rows = []
        for index, tp in enumerate(self._testpoints):
            tp_html_id = "%(prefix)s%(sn)s" % dict(prefix=self.TESTPOINT_ID_PREFIX, sn=(index + 1))
            row = elements.TR().set_attr("id", tp_html_id).add_css_class(self.TESTPOINT_ROW_CSS_CLASS)
            row.set_attr("onclick", "toggleTestCaseOfTestPoint('%s','%s','%s',%s)" % (tp_html_id, self.TESTCASE_ID_PREFIX, self.ID_SEP, len(tp["testcases"])))
            point_name = tp["name"]
            short_name = point_name.split(".")[-1]
            name_cell = elements.TD(short_name).add_css_class(self.TESTPOINT_NAME_CSS_CLASS)
            name_cell.set_attr("title", point_name)
            row.append_child(name_cell)
            row.append_child(elements.TD(tp["count"]).add_css_class(self.TESTPOINT_COUNT_CSS_CLASS))
            row.append_child(elements.TD(tp["pass_count"]).add_css_class(self.TESTPOINT_PASS_CSS_CLASS))
            row.append_child(elements.TD(tp["fail_count"]).add_css_class(self.TESTPOINT_FAIL_CSS_CLASS))
            row.append_child(elements.TD(tp["block_count"]).add_css_class(self.TESTPOINT_BLOCK_CSS_CLASS))
            row.append_child(elements.TD(tp["error_count"]).add_css_class(self.TESTPOINT_ERROR_CSS_CLASS))
            row.append_child(elements.TD(tp["skip_count"]).add_css_class(self.TESTPOINT_SKIP_CSS_CLASS))
            row.append_child(elements.TD(tp["xfail_count"]).add_css_class(self.TESTPOINT_XFAIL_CSS_CLASS))
            row.append_child(elements.TD(tp["xpass_count"]).add_css_class(self.TESTPOINT_XPASS_CSS_CLASS))
            row.after(*tuple(self._build_testcases_rows(tp_html_id, tp["testcases"])))
            rows.append(row)
        return rows

    def _build_body(self):
        self.tbody.append_child(*self.build_testpoints_rows())
