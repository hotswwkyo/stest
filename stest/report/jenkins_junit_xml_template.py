#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author: 思文伟
@Date: 2021/11/12 10:25:11
'''
from xml.etree import ElementTree as ET
from xml.sax import saxutils

from ..core.result_formatter import TestCaseWrapper


class JenkinsXMLElementTags(object):

    testsuites = 'testsuites'
    testsuite = 'testsuite'
    testcase = 'testcase'
    skipped = 'skipped'
    error = 'error'
    failure = 'failure'
    system_out = 'system-out'


class JenkinsJunitXMLReportTemplate(object):
    TAGS = JenkinsXMLElementTags

    def __init__(self, testpoints, test_suite_name='stest'):

        self.testpoints = testpoints
        self.test_suite_name = test_suite_name

        self.el_testsuites = ET.Element(self.TAGS.testsuites)

    def __build_testsuite_element(self, name, tests, errors, failures, skipped, **others):
        """

        Args:
            - tests: The total number of tests in the suite, required.

            - disabled: the total number of disabled tests in the suite. optional. not supported by maven surefire.

            - errors: The total number of tests in the suite that errored. An errored test is one that had an unanticipated problem,
                    for example an unchecked throwable; or a problem with the implementation of the test. optional

            - failures: The total number of tests in the suite that failed. A failure is a test which the code has explicitly failed
                    by using the mechanisms for that purpose. e.g., via an assertEquals. optional

            - hostname: Host on which the tests were executed. 'localhost' should be used if the hostname cannot be determined. optional.
                        not supported by maven surefire.

            - id: Starts at 0 for the first testsuite and is incremented by 1 for each following testsuite. optional. not supported by maven surefire.

            - package: Derived from testsuite/@name in the non-aggregated documents. optional. not supported by maven surefire.

            - skipped: The total number of skipped tests. optional

            - time: Time taken (in seconds) to execute the tests in the suite. optional

            - timestamp: when the test was executed in ISO 8601 format (2014-01-21T16:17:18). Timezone may not be specified. optional.
                        not supported by maven surefire.
        """

        tests = str(tests)
        errors = str(errors)
        failures = str(failures)
        skipped = str(skipped)
        el_testsuite = ET.Element(self.TAGS.testsuite, name=saxutils.quoteattr(name), tests=tests, errors=errors, failures=failures, skipped=skipped, **others)
        return el_testsuite

    def __build_testcase_element(self, name, classname, time, **result):

        tc = ET.Element(self.TAGS.testcase, name=saxutils.quoteattr(name), classname=saxutils.quoteattr(classname), time=time)

        tagname = None
        if self.TAGS.skipped in result:
            tagname = self.TAGS.skipped
            summary, details = result[self.TAGS.skipped]
        elif self.TAGS.failure in result:
            tagname = self.TAGS.failure
            summary, details = result[self.TAGS.failure]
        elif self.TAGS.error in result:
            tagname = self.TAGS.error
            summary, details = result[self.TAGS.error]
        else:
            summary = ''
            details = ''
        if tagname:
            child = ET.Element(tagname, message=saxutils.quoteattr(summary))
            child.text = saxutils.escape(details)
            tc.append(child)

        # <system-out>STDOUT text</system-out>
        if self.TAGS.system_out in result:
            el_sysout = ET.Element(self.TAGS.system_out)
            el_sysout.text = saxutils.escape(result.get(self.TAGS.system_out, ""))
        return tc

    def to_xml(self):

        tests = 0
        error_count = 0
        skip_count = 0
        fail_count = 0

        el_testcases = []
        for testpoint in self.testpoints:
            tests = tests + testpoint['count']
            error_count = error_count + testpoint['error_count']
            skip_count = skip_count + testpoint['skip_count'] + testpoint['block_count']
            fail_count = fail_count + testpoint['fail_count'] + testpoint['xpass_count']
            classname = testpoint['name'][0]
            testcases = testpoint['testcases']

            for testcase in testcases:
                name = testcase['name']
                method = testcase['method_name']
                duration = testcase['duration']
                output_message = testcase['output_message']
                error_message = testcase['error_message']
                summary_and_details = [error_message, error_message]

                rinfo = testcase['result']
                rcode = rinfo['code']
                case_result = {}
                if output_message:
                    case_result[self.TAGS.system_out] = output_message
                if rcode in [TestCaseWrapper.FAILURE, TestCaseWrapper.XSUCCESS]:
                    case_result[self.TAGS.failure] = summary_and_details
                elif rcode in [TestCaseWrapper.SKIPED, TestCaseWrapper.BLOCKED]:
                    case_result[self.TAGS.skipped] = summary_and_details
                elif rcode in [TestCaseWrapper.ERROR]:
                    case_result[self.TAGS.error] = summary_and_details
                el_tc = self.__build_testcase_element('{} - {}'.format(method, name), classname, duration, **case_result)
                el_testcases.append(el_tc)

        suite = self.__build_testsuite_element(self.test_suite_name, tests, error_count, fail_count, skip_count)
        for one in el_testcases:
            suite.append(one)
        self.el_testsuites.append(suite)
        return ET.tostring(self.el_testsuites, encoding="utf-8", xml_declaration=True)

    def save_as_file(self, full_file_path):

        with open(full_file_path, "w", encoding="utf-8") as f:
            f.write(self.to_xml().decode("utf-8"))
