# -*- coding: utf-8 -*-
'''
Created on 2019年12月5日

@author: siwenwei
'''

import os
import sys
import copy

from .html import elements
from .widgets import tables

if getattr(sys, 'frozen', False):
    # BASE_DIR = os.path.dirname(os.path.abspath(sys.executable))
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class HtmlReportTemplate(object):

    CSS_AND_JS_DIR = "resources"
    CSS_FILE_NAME = "style.css"
    JS_FILE_NAME = "main.js"
    JQUERY_FILE_NAME = "jquery-1.11.0.min.js"

    def __init__(self, testpoints, settings=None, title="", task_number="", start_time="", finish_time="", executor="", project_name="", task_description=""):

        self.html = elements.HTML()
        self.title = title
        self.summary_table = tables.SummaryTable(
            title, task_number, start_time, finish_time, executor, project_name, task_description, self.pie_chart_info(testpoints))
        self.report_table = tables.ReportTable(settings=settings)
        self.testpoints = testpoints
        self.layer = elements.Div().add_css_class("layer")
        self.html.body.append_child(self.layer)

    def pie_chart_info(self, testpoints):

        points = copy.deepcopy(testpoints)
        fail_count = 0
        block_count = 0
        error_count = 0
        pass_count = 0
        skip_count = 0
        xfail_count = 0
        xpass_count = 0
        for p in points:
            fail_count = fail_count + p["fail_count"]
            block_count = block_count + p["block_count"]
            error_count = error_count + p["error_count"]
            pass_count = pass_count + p["pass_count"]
            skip_count = skip_count + p["skip_count"]
            xfail_count = xfail_count + p["xfail_count"]
            xpass_count = xpass_count + p["xpass_count"]
        return (pass_count, fail_count, block_count, error_count, skip_count, xfail_count, xpass_count)

    def _write_metas(self):

        m1 = elements.Meta().set_attr("name", "description").set_attr("content", "auto test html report")
        m2 = elements.Meta().set_attr("name", "author").set_attr("content", "siwenwei")
        m3 = elements.Meta().set_attr("http-equiv", "Content-Type").set_attr("content", "text/html; charset=utf-8")

        self.html.head.append_child(m1).append_child(m2).append_child(m3)

    def _write_inline_style(self):

        style = elements.Style().set_attr("type", "text/css").set_attr("media", "screen")
        with open(os.path.join(BASE_DIR, self.CSS_AND_JS_DIR, self.CSS_FILE_NAME), "r", encoding="utf-8") as f:
            style.text = """\n%s\n""" % f.read()
        self.html.head.append_child(style)

    def _write_jquery_script(self):

        script = elements.Script().set_attr("type", "text/javascript").set_attr("language", "javascript")
        with open(os.path.join(BASE_DIR, self.CSS_AND_JS_DIR, self.JQUERY_FILE_NAME), "r", encoding="utf-8") as f:
            script.text = """<!-- \n%s\n -->""" % f.read()
        self.html.head.append_child(script)

    def _write_inline_script(self):

        script = elements.Script().set_attr("type", "text/javascript").set_attr("language", "javascript")
        with open(os.path.join(BASE_DIR, self.CSS_AND_JS_DIR, self.JS_FILE_NAME), "r", encoding="utf-8") as f:
            script.text = """<!-- \n%s\n -->""" % f.read()
        self.html.head.append_child(script)

    def set_report_title(self):

        self.html.head.title.text = self.title

    def _fill_summary_table(self):

        self.layer.append_child(self.summary_table)

    def _fill_report_table(self):

        testpoints = []
        for testpoint in self.testpoints:
            testpoints.append(testpoint)
        self.report_table.set_testpoints(*tuple(testpoints))
        self.layer.append_child(self.report_table)

    def to_html(self):

        self._write_metas()
        self.set_report_title()
        self._write_inline_style()
        self._write_jquery_script()
        self._write_inline_script()
        self._fill_summary_table()
        self._fill_report_table()
        return self.html.to_html()

    def save_as_file(self, full_file_path):

        with open(full_file_path, "w", encoding="utf-8") as f:
            f.write(self.to_html())
