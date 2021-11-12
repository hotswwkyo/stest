#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author: 思文伟
@Date: 2021/09/17
'''
import os
import sys
import datetime
import unittest
from unittest.signals import installHandler
from .seven_runner import SevenTestRunner
from .seven_loader import SevenTestLoader
from .report_builder import ReportBuilder


class SevenTestProgram(unittest.TestProgram):
    def __init__(self,
                 module='__main__',
                 defaultTest=None,
                 argv=None,
                 testRunner=SevenTestRunner,
                 testLoader=SevenTestLoader(),
                 exit=True,
                 verbosity=1,
                 failfast=None,
                 catchbreak=None,
                 buffer=None,
                 warnings=None,
                 *,
                 tb_locals=False):

        super().__init__(module=module,
                         defaultTest=defaultTest,
                         argv=argv,
                         testRunner=testRunner,
                         testLoader=testLoader,
                         exit=exit,
                         verbosity=verbosity,
                         failfast=failfast,
                         catchbreak=catchbreak,
                         buffer=buffer,
                         warnings=warnings,
                         tb_locals=tb_locals)

    def _initArgParsers(self):

        super()._initArgParsers()
        self._main_parser.add_argument('-html', '--html-report', dest='html', help="html report file full path")
        self._main_parser.add_argument('-title', '--report-title', dest='title', default="", help="html report title")
        self._main_parser.add_argument('-project', '--project-name', dest='project', default="", help="test project name")
        self._main_parser.add_argument('-task', '--task-number', dest='task', help="test task number")
        self._main_parser.add_argument('-tester', '--tester-name', dest='tester', help="tester name")
        self._main_parser.add_argument('-taskinfo', '--task-info', dest='task_description', default="", help="task description")
        self._main_parser.add_argument('-junit_xml', '--jenkins_junit_xml', dest='jenkins_junit_xml', help="xml report full path,junit xml format report that jenkins supports")

        self._discovery_parser.add_argument('-html', '--html-report', dest='html', help="html report file full path")
        self._discovery_parser.add_argument('-title', '--report-title', dest='title', default="", help="html report title")
        self._discovery_parser.add_argument('-project', '--project-name', dest='project', default="", help="test project name")
        self._discovery_parser.add_argument('-task', '--task-number', dest='task', help="test task number")
        self._discovery_parser.add_argument('-tester', '--tester-name', dest='tester', help="tester name")
        self._discovery_parser.add_argument('-taskinfo', '--task-info', dest='task_description', default="", help="task description")
        self._discovery_parser.add_argument('-junit_xml', '--jenkins_junit_xml', dest='jenkins_junit_xml', help="xml report full path,junit xml format report that jenkins supports")

    def __build_html_report(self, result, start_time, finish_time):

        fname = self.html
        ext = '.html'
        notice = False
        if not fname:
            if self.module is None:
                # warning_message = '没有传入报告文件名，不会生成测试报告文件'
                # print(warning_message)
                return None
            else:
                filepath = os.path.abspath(self.module.__file__)
                fname = os.path.splitext(filepath)[0] + ext
                notice = True
        title_key = 'title'
        title = self.title
        summary_info = {}
        if not title:
            pathname, extname = os.path.splitext(fname)
            summary_info[title_key] = os.path.basename(pathname)
        summary_info['start_time'] = start_time.strftime("%Y-%m-%d %H:%M:%S")
        summary_info['finish_time'] = finish_time.strftime("%Y-%m-%d %H:%M:%S")
        summary_info['task_description'] = self.task_description
        summary_info['executor'] = self.tester if self.tester else ''
        summary_info['task_number'] = self.task if self.task else start_time.strftime("%Y%m%d%H%M%S%f")
        ReportBuilder(result).build_html_report(fname, **summary_info)
        if notice:
            print('html report file: {}'.format(fname))
        return fname

    def __build_jenkins_junit_xml_report(self, result, start_time, finish_time, disable_if_no_file_name=False):

        fname = self.jenkins_junit_xml
        ext = '.xml'
        notice = False
        if not fname:
            if self.module is None:
                # warning_message = '没有传入报告文件名，不会生成测试报告文件'
                # print(warning_message)
                return None
            else:
                if disable_if_no_file_name:
                    return None
                filepath = os.path.abspath(self.module.__file__)
                fname = os.path.splitext(filepath)[0] + ext
                notice = True
        title_key = 'title'
        title = self.title
        summary_info = {}
        if not title:
            pathname, extname = os.path.splitext(fname)
            summary_info[title_key] = os.path.basename(pathname)
        summary_info['start_time'] = start_time.strftime("%Y-%m-%d %H:%M:%S")
        summary_info['finish_time'] = finish_time.strftime("%Y-%m-%d %H:%M:%S")
        summary_info['task_description'] = self.task_description
        summary_info['executor'] = self.tester if self.tester else ''
        summary_info['task_number'] = self.task if self.task else start_time.strftime("%Y%m%d%H%M%S%f")
        ReportBuilder(result).build_jenkins_junit_xml_report(fname, **summary_info)
        if notice:
            print('jenkins junit xml report file: {}'.format(fname))
        return fname

    def runTests(self):
        if self.catchbreak:
            installHandler()
        if self.testRunner is None:
            self.testRunner = SevenTestRunner
        if isinstance(self.testRunner, type):
            try:
                try:
                    testRunner = self.testRunner(verbosity=self.verbosity, failfast=self.failfast, buffer=self.buffer, warnings=self.warnings, tb_locals=self.tb_locals)
                except TypeError:
                    # didn't accept the tb_locals argument
                    testRunner = self.testRunner(verbosity=self.verbosity, failfast=self.failfast, buffer=self.buffer, warnings=self.warnings)
            except TypeError:
                # didn't accept the verbosity, buffer or failfast arguments
                testRunner = self.testRunner()
        else:
            # it is assumed to be a TestRunner instance
            testRunner = self.testRunner
        start_time = datetime.datetime.now()
        self.result = testRunner.run(self.test)
        finish_time = datetime.datetime.now()
        self.__build_html_report(self.result, start_time, finish_time)
        self.__build_jenkins_junit_xml_report(self.result, start_time, finish_time)
        if self.exit:
            sys.exit(not self.result.wasSuccessful())


main = SevenTestProgram
