#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author: 思文伟
@Date: 2021/09/18
'''
from .result_formatter import TestResultFormatter
from .report.htmltemplate import HtmlReportTemplate


class ReportBuilder(object):
    def __init__(self, result):

        self.result = result

    def build_html_report(self, filename, **summary_info):
        """

        Args:
            filename: 报告文件名（完整文件路径名） eg: E:\\TEST\\autotest.html

            summary_info:
                title: 报告标题
                task_number: 测试任务编号
                start_time: 测试开始时间
                finish_time: 测试完成时间
                executor: 测试任务执行者
                project_name: 项目名称
                task_description: 测试任务描述信息
        """

        json_result = TestResultFormatter(self.result).to_py_json()
        testpoints = json_result.get("testpoints")
        template = HtmlReportTemplate(testpoints, **summary_info)
        template.save_as_file(filename)
