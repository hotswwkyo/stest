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
 * 内置参数化数据存取方案(使用excel（xlsx或xls格式）存取和管理维护参数化测试数据，简洁直观，易于修改维护)
 * 支持生成更加简洁美观且可作为独立文件发送的HTML测试报告
 * 支持生成jenkins junit xml 格式测试报告，用于jenkins集成
 * 支持自动查找并载入项目下的settings.py配置文件
 * 支持灵活控制测试失败自动截图并附加到测试报告中
 * 支持page object模式，内置一套易于维护的解决方案
 * 驱动管理器（DRIVER_MANAGER）更加便捷的管理打开的驱动会话
 * 对selenium、appium、minium（微信小程序自动化测试库）以及WinAppDriver（微软官方提供的一款用于做Window桌面应用程序的界面（UI）自动化测试工具）做了底层集成支持


Simple usage:

    import os

    from stest import settings
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
        # 则会检测settings.SEVEN_DATA_PROVIDER_DATA_FILE_DIR 是否设置
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

__all__ = ['Test', 'AbstractTestCase', 'AbsractDataProvider', 'main', 'settings']

from .main import main
from .conf import settings
from .core.test_wrapper import Test
from .core.abstract_testcase import AbstractTestCase
from .core.abstract_data_provider import AbsractDataProvider
