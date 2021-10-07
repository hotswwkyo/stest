#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
基于unittest开发的测试框架，更友好、更灵活的编写、管理与运行测试，生成更加美观的独立单文件HTML报告。内置参数化测试数据存取方案，省去设计的烦恼，节省更多的时间，从而更快的投入到编写用例阶段

 * 使用装饰器Test来标记测试方法更加灵活
 * 支持命名测试方法且不与方法的doc string（文档字符串）冲突
 * 支持设置测试方法编写人，修改人，最后修改人以及最后一次修改时间等额外记录信息
 * 支持设置测试方法的执行顺序
 * 支持参数化功能
 * 支持数据驱动测试
 * 支持设置用例依赖
 * 内置参数化数据存取方案
 * 更加美观的HTML报告


Simple usage:

    import os

    from stest import GLOBAL_CONFIG
    from stest import AbstractTestCase
    from stest import Test as testcase


    class DataProvider01(object):
        def get_testdatas(self, testclass, testmethod, *args, **kwargs):

            datas = [
                {'加数1':1,'加数2':2,'预期':3},
                {'加数1':4,'加数2':5,'预期':9}
            ]
            return datas

    class DataProvider02(object):
        def get_testdatas(self, testclass, testmethod, *args, **kwargs):

            datas = [
                [{'加数1':7}, {'加数2':5}, {'预期':12}],
                [{'加数1':10}, {'加数2':5}, {'预期':15}]
            ]
            return datas

    TEST_DATA_FILE_DIRPATH = os.path.dirname(os.path.abspath(__file__))

    # 全局配置 配置默认内置参数数据提供者 测试数据文件所在的目录路径
    # GLOBAL_CONFIG.seven_data_provider_data_file_dir = 'E:\\sw'


    class CalculationTest(AbstractTestCase):

        @classmethod
        def setUpClass(cls):
            pass

        def setUp(self):
            pass

        # 自定义数据提供者 - 测试方法一个参数化示例
        @testcase(priority=1, enabled=True, data_provider=DataProvider01().get_testdatas, author='思文伟', description='整数加法测试01')
        def integer_addition_01(self, testdata):

            number_1 = testdata.get("加数1")
            number_2 = testdata.get("加数2")
            expected = testdata.get("预期")
            result = number_1 + number_2
            self.assertEqual(result, expected)

        # 自定义数据提供者 - 测试方法多个参数化示例
        @testcase(priority=2, enabled=True, data_provider=DataProvider02().get_testdatas, author='思文伟', description='整数加法测试02')
        def integer_addition_02(self, testdata_01, testdata_02, testdata_03):

            number_1 = testdata_01.get("加数1")
            number_2 = testdata_02.get("加数2")
            expected = testdata_03.get("预期")

            result = number_1 + number_2
            self.assertEqual(result, expected)

        # 不参数化示例
        @testcase(priority=3, enabled=True, author='思文伟', description='整数减法测试01')
        def integer_subtraction_01(self):

            number_1 = 21
            number_2 = 10
            result = number_1 - number_2
            expected = 11
            self.assertEqual(result, expected)

        # 使用内置的数据提供者 - 传入测试数据文件所在的目录路径
        @testcase(priority=4, enabled=True, author='思文伟', data_provider_kwargs={'data_file_dir_path':TEST_DATA_FILE_DIRPATH}, description='整数减法测试02')
        def integer_subtraction_02(self, testdata):

            number_1 = testdata.get("减数1")
            number_2 = testdata.get("减数2")
            expected = testdata.get("预期")

            result = int(number_1) - int(number_2)
            self.assertEqual(result, int(expected))

        # 使用内置的数据提供者 - 不传入测试数据文件所在的目录路径,
        # 则会检测GLOBAL_CONFIG.seven_data_provider_data_file_dir 是否设置
        # 没有设置则会使用该方法所属的测试类所在的模块目录路径作为测试数据文件的查找目录
        @testcase(priority=5, enabled=True, author='思文伟', description='整数减法测试03')
        def integer_subtraction_03(self,testdata):

            number_1 = testdata.get("减数1")
            number_2 = testdata.get("减数2")
            expected = testdata.get("预期")

            result = int(number_1) - int(number_2)
            self.assertEqual(result, int(expected))

        def tearDown(self):
            pass

        @classmethod
        def tearDownClass(cls):
            pass

    if __name__ == '__main__':
        CalculationTest.run_test()

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

__all__ = ['Test', 'GLOBAL_CONFIG', 'AbstractTestCase', 'AbsractDataProvider', 'main']

from .main import main
from .test_wrapper import Test
from .global_config import GLOBAL_CONFIG
from .abstract_testcase import AbstractTestCase
from .abstract_data_provider import AbsractDataProvider
