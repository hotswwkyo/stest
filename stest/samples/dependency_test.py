#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author: 思文伟
@Date: 2021/09/29
'''
import os
import stest
# from stest import GLOBAL_CONFIG
from stest import AbstractTestCase
from stest import Test as testcase


class DataProvider01(object):
    def get_testdatas(self, testclass, testmethod, *args, **kwargs):

        datas = [{'加数1': 1, '加数2': 2, '预期': 3}, {'加数1': 4, '加数2': 5, '预期': 9}]
        return datas


class DataProvider02(object):
    def get_testdatas(self, testclass, testmethod, *args, **kwargs):

        datas = [[{'加数1': 7}, {'加数2': 5}, {'预期': 12}]]
        return datas


TEST_DATA_FILE_DIRPATH = os.path.dirname(os.path.abspath(__file__))

# 全局配置 配置默认内置参数数据提供者 测试数据文件所在的目录路径
# GLOBAL_CONFIG.seven_data_provider_data_file_dir = r'E:\sw'


class DependTest(AbstractTestCase):
    """依赖设置测试"""
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    @testcase(priority=1, enabled=True, author='思文伟', description='sqq', depends=['oss'])
    def sqq(self):

        number_1 = 21
        number_2 = 10
        result = number_1 - number_2
        expected = 11
        self.assertEqual(result, expected)

    @testcase(priority=2, enabled=True, author='思文伟', description='oss', depends=['sqq'])
    def oss(self):

        number_1 = 21
        number_2 = 10
        result = number_1 - number_2
        expected = 11
        self.assertEqual(result, expected)

    @testcase(priority=3, enabled=True, data_provider=DataProvider01().get_testdatas, author='思文伟', description='t', depends=['sqq'])
    def t(self, testdata):

        number_1 = testdata.get("加数1")
        number_2 = testdata.get("加数2")
        expected = testdata.get("预期")

        result = number_1 + number_2
        self.assertEqual(result, expected)

    @testcase(priority=4, enabled=True, data_provider=DataProvider02().get_testdatas, author='思文伟', description='one', depends=['two'])
    def one(self, testdata_01, testdata_02, testdata_03):

        number_1 = testdata_01.get("加数1")
        number_2 = testdata_02.get("加数2")
        expected = testdata_03.get("预期")

        result = number_1 + number_2
        self.assertEqual(result, expected)

    @testcase(priority=5, enabled=True, data_provider=DataProvider02().get_testdatas, author='思文伟', description='two', depends=['t3'])
    def two(self, testdata_01, testdata_02, testdata_03):

        number_1 = testdata_01.get("加数1")
        number_2 = testdata_02.get("加数2")
        expected = testdata_03.get("预期")

        result = number_1 + number_2
        self.assertEqual(result, expected)

    @testcase(priority=6, enabled=True, data_provider=DataProvider02().get_testdatas, author='思文伟', description='three', dname="t3")
    def three(self, testdata_01, testdata_02, testdata_03):

        number_1 = testdata_01.get("加数1")
        number_2 = testdata_02.get("加数2")
        expected = testdata_03.get("预期")

        result = number_1 + number_2
        self.assertEqual(result, expected)

    def tearDown(self):
        pass

    @classmethod
    def tearDownClass(cls):
        pass


if __name__ == '__main__':
    stest.main()
