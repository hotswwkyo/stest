#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author: 思文伟
@Date: 2021/03/30 15:49:32
'''
import os
import stest
# from stest import settings
from stest import AbstractTestCase
from stest import Test as testcase


class DataProvider01(object):
    def get_testdatas(self, testclass, testmethod, *args, **kwargs):

        datas = [{'加数1': 1, '加数2': 2, '预期': 5}, {'加数1': 4, '加数2': 5, '预期': 9}]
        return datas


class DataProvider02(object):
    def get_testdatas(self, testclass, testmethod, *args, **kwargs):

        datas = [[{'加数1': 7}, {'加数2': 5}, {'预期': 12}], [{'加数1': 10}, {'加数2': 5}, {'预期': 15}]]
        return datas


TEST_DATA_FILE_DIRPATH = os.path.dirname(os.path.abspath(__file__))


class CalculationTest(AbstractTestCase):
    """数学运算测试"""
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    @testcase(priority=1, enabled=True, screenshot=True, attach_screenshot_to_report=True, data_provider=DataProvider01().get_testdatas, author='思文伟', description='整数加法测试01')
    def integer_addition_01(self, testdata):
        """自定义数据提供者 - 测试方法一个参数化示例"""

        number_1 = testdata.get("加数1")
        number_2 = testdata.get("加数2")
        expected = testdata.get("预期")

        result = number_1 + number_2
        self.assertEqual(result, expected)

    @testcase(priority=2, enabled=True, data_provider=DataProvider02().get_testdatas, author='思文伟', description='整数加法测试02')
    def integer_addition_02(self, testdata_01, testdata_02, testdata_03):
        """自定义数据提供者 - 测试方法多个参数化示例"""

        number_1 = testdata_01.get("加数1")
        number_2 = testdata_02.get("加数2")
        expected = testdata_03.get("预期")

        result = number_1 + number_2
        self.assertEqual(result, expected)

    @testcase(priority=3, enabled=True, author='思文伟', description='整数减法测试01')
    def integer_subtraction_01(self):
        """不参数化示例"""

        number_1 = 21
        number_2 = 10
        result = number_1 - number_2
        expected = 11
        self.assertEqual(result, expected)

    @testcase(priority=4, enabled=True, author='思文伟', data_provider_kwargs={'data_file_dir_path': TEST_DATA_FILE_DIRPATH}, description='整数减法测试02')
    def integer_subtraction_02(self, testdata):
        """使用内置的数据提供者 - 传入测试数据文件所在的目录路径"""

        number_1 = testdata.get("减数1")
        number_2 = testdata.get("减数2")
        expected = testdata.get("预期")

        result = int(number_1) - int(number_2)
        self.assertEqual(result, int(expected))

    @testcase(priority=5, enabled=True, author='思文伟', description='整数减法测试03')
    def integer_subtraction_03(self, testdata):
        """使用内置的数据提供者 - 不传入测试数据文件所在的目录路径,
        则会检测settings.SEVEN_DATA_PROVIDER_DATA_FILE_DIR 是否设置
        ，没有设置则会使用该方法所属的测试类所在的模块目录路径作为测试数据文件的查找目录
        """

        number_1 = testdata.get("减数1")
        number_2 = testdata.get("减数2")
        expected = testdata.get("预期")

        result = int(number_1) - int(number_2)
        self.assertEqual(result, int(expected))

    def test_login_baidu(self):

        print("yes")

    def tearDown(self):
        pass

    @classmethod
    def tearDownClass(cls):
        pass


if __name__ == '__main__':
    # CalculationTest.run_test()
    stest.main()
