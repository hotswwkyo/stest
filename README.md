# stest
 基于unittest开发的测试框架，更友好、更灵活的编写、管理与运行测试，生成更加美观的独立单文件HTML报告。内置参数化测试数据存取方案，省去设计的烦恼，节省更多的时间，从而更快的投入到编写用例阶段。
 * 现已支持的功能
    >* 支持命名测试方法且不与方法的doc string（文档字符串）冲突
    >* 支持设置测试方法编写人，修改人，最后修改人以及最后一次修改时间等额外记录信息
    >* 支持设置测试方法的执行顺序
    >* 支持参数化功能
    >* 支持数据驱动测试
    >* 支持设置用例依赖
    >* 内置参数化数据存取方案(使用excel（xlsx或xls格式）存取和管理维护参数化测试数据，简洁直观，易于修改维护)
    >* 支持生成更加简洁美观且可作为独立文件发送的HTML测试报告
    >* 支持生成jenkins junit xml 格式测试报告，用于jenkins集成
    >* 支持自动查找并载入项目下的settings.py配置文件
    >* 支持灵活控制测试失败自动截图并附加到测试报告中
    >* 支持page object模式，内置一套易于维护的解决方案
    >* 驱动管理器（DRIVER_MANAGER）更加便捷的管理打开的驱动会话
    >* 提供selenium、appium、playwright、minium（微信小程序自动化测试库）以及WinAppDriver（微软官方提供的一款用于做Window桌面应用程序的界面（UI）自动化测试工具）的page object的实现方案
    >    ![](https://github.com/hotswwkyo/stest/blob/main/img/htmlreport.png)


## 安装

pip方式安装
> pip install stest

源码方式安装(注意以管理员方式执行)
> python setup.py install

## 执行测试
命令行执行
> python -m stest -v -html D:\temp\tms_apitest.html calculation_test.py

查看命令行参数
> python -m stest -h

代码中调stest.main()执行

```python
#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import stest
from stest import AbstractTestCase
from stest import Test as testcase


def get_testdatas(test_class_name, test_method_name, *args, **kwargs):

    return [[1,2,3], [3,4,7]]


class Demo1Test(AbstractTestCase):

    @testcase(priority=1, enabled=True, data_provider=get_testdatas, author='思文伟', description='两数加法测试01')
    def integer_addition_02(self, number_1, number_2, expected):

        result = number_1 + number_2
        self.assertEqual(result, expected)
if __name__ == '__main__':
    # Demo1Test.run_test()
    stest.main()
```

## 快速开始

1. 导入抽象测试类（AbstractTestCase）和测试方法装饰器（Test）
2. 编写继承自AbstractTestCase的测试子类，子类提供以下实用方法
    - collect_testcases()
        > 获取类下所有使用Test装饰的enable为True，并根据priority排序后的测试用例对象列表
    - build_self_suite()
        > 构建该类测试用例构成的测试套件
    - run_test()
        > 执行该类所有使用Test装饰的enable为True，并根据priority排序后的测试用例
3. 使用Test标记测试方法。
4. 直接调用测试类的run_test()执行测试
* 简单示例
    ```python
    #!/usr/bin/env python
    # -*- encoding: utf-8 -*-

    from stest import AbstractTestCase
    from stest import Test as testcase


    def get_testdatas(test_class_name, test_method_name, *args, **kwargs):

        return [[1,2,3], [3,4,7]]


    class Demo1Test(AbstractTestCase):

        @testcase(priority=1, enabled=True, data_provider=get_testdatas, author='思文伟', description='两数加法测试01')
        def integer_addition_02(self, number_1, number_2, expected):

            result = number_1 + number_2
            self.assertEqual(result, expected)
    if __name__ == '__main__':
        Demo1Test.run_test()
    ```

* 综合示例（来自源码包下的samples/calculation_test.py）

    ```python
    #!/usr/bin/env python
    # -*- encoding: utf-8 -*-
    '''
    @Author: 思文伟
    @Date: 2021/03/30 15:49:32
    '''
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
        """数学运算测试"""
        @classmethod
        def setUpClass(cls):
            pass

        def setUp(self):
            pass

        @testcase(priority=1, enabled=True, data_provider=DataProvider01().get_testdatas, author='思文伟', description='整数加法测试01')
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

        @testcase(priority=4, enabled=True, author='思文伟', data_provider_kwargs={'data_file_dir_path':TEST_DATA_FILE_DIRPATH}, description='整数减法测试02')
        def integer_subtraction_02(self, testdata):
            """使用内置的数据提供者 - 传入测试数据文件所在的目录路径"""

            number_1 = testdata.get("减数1")
            number_2 = testdata.get("减数2")
            expected = testdata.get("预期")

            result = int(number_1) - int(number_2)
            self.assertEqual(result, int(expected))

        @testcase(priority=5, enabled=True, author='思文伟', description='整数减法测试03')
        def integer_subtraction_03(self,testdata):
            """使用内置的数据提供者 - 不传入测试数据文件所在的目录路径,
            则会检测settings.SEVEN_DATA_PROVIDER_DATA_FILE_DIR 是否设置
            ，没有设置则会使用该方法所属的测试类所在的模块目录路径作为测试数据文件的查找目录
            """

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

    ```

## settings.py配置文件
可以通过命令行参数-sfile指定配置文件路径或者指定查找配置文件的开始目录路径，如果未指定，则框架会自动递归遍历项目目录（根据用例所在目录往外推，第一个非python包的目录即被认定为项目目录）及其子孙目录，查找settings.py配置文件，找到则会在收集用例测试数据之前自动导入该文件。可通过from stest import settings 导入配置对象，然后通过settings对象访问配置文件中的配置字段（字段必须是大写的,如：settings.SCREENSHOT）
* 框架使用的配置
    | 字段 | 描述 |
    | :---- | :---- |
    | SCREENSHOT | 控制测试失败后是否自动截图 |
    | ATTACH_SCREENSHOT_TO_REPORT | 控制截图后是否附加到测试报告中，如果附加到报告中，则截图转base64数据附加到报告中 |
    | SCREENSHOT_SAVE_DIR | 以后将用到的字段，截图存放目录 |
    | SEVEN_DATA_PROVIDER_DATA_FILE_DIR | 内置参数化数据提供者(SevenDataProvider)读取的测试数据文件所在的目录路径，不设置则自动获取测试用例所在模块的目录路径作为测试数据文件所在的目录路径，内置参数化数据提供者会从该目录路径查找用例测试数据文件 |
    | TEST_REPORT_DIR | 测试报告存放目录，优先级低于从命令行参数传入的。命令行没有传入以及配置文件没有设置，则获取模块所在的目录作为存放目录，如果测试模块也没有传入，则不生成测试报告 |
    | TEST_REPORT_NAME | 测试报告名称，优先级低于从命令行参数传入的。命令行没有传入以及配置文件没有设置，则获取模块名称作为报告名，如果连测试模块也没有给，则获取命令行设置的测试任务名作为报告名称，任务名也未设置则用测试开始时间作为报告名称 |
    | EXECUTOR | 任务执行人，命令行没有传入则取该设置 |
    | PROJECT_NAME | 项目名称，命令行没有传入则取该设置 |
    | DESCRIPTION | 描述，命令行没有传入则取该设置 |
    | DRIVER_MANAGER | 驱动管理器，框架自动赋值，勿修改 |

* stestdemo
    >    ![](https://github.com/hotswwkyo/stest/blob/main/img/project_dirs.png)

## Test参数说明

| 参数 | 类型 | 描述 |
| :---- | :---- | :---- |
| name | 字符串 | 测试用例名称 |
| author | 字符串 | 用例编写者 |
| editors | 列表 | 修改者列表 |
| dname | 字符串或列表 | 用于给用例起一个用于设置依赖的名称 |
| depends | 列表 | 用于设置用例依赖，是一个用例依赖列表 |
| groups | 列表 | 方法所属的组的列表|
| enabled | 布尔值 | 是否启用执行该测试方法 |
| priority | 整数 | 测试方法的执行优先级，数值越小执行越靠前 |
| alway_run | 布尔值 | 如果设置为True，不管依赖它所依赖的其他用例结果如何都始终运行，为False时，则它所依赖的其他用例不成功，就不会执行，默认值为False |
| description | 字符串 | 弃用，原用于设置测试用例名称 |
| data_provider | object | 测试方法的参数化数据提供者，默认值是None，AbsractDataProvider的子类或者一个可调用的对象，返回数据集列表（当测试方法只有一个参数化时，应返回一维列表，多个参数化时返回二维列表） |
| data_provider_args | 元祖 | 数据提供者变长位置参数(args) |
| data_provider_kwargs | 字典 | 数据提供者变长关键字参数(kwargs) |
| screenshot | 布尔值 | 控制该用例测试失败是否截图，该设置优先级大于配置文件中的截图设置 |
| attach_screenshot_to_report | 布尔值 | 控制该用例是否附加测试失败的截图到测试报告中，优先级大于配置文件中的截图设置 |
| last_modifyied_by | 字符串 | 最后修改者 |
| last_modified_time | 字符串 | 最后一次修改的时间 |
| enable_default_data_provider | 布尔值 | 是否使用内置数据提供者(SevenDataProvider)，默认值是True，未设置data_provider，且该值为True 才会使用内置数据提供者(SevenDataProvider) |

## 用例依赖设置
用例依赖于其它用例成功后执行，如用例所依赖的用例不成功或没有执行，则该用例会被设置为失败。在实际当中，有时会需要用到两个或多个测试用例依赖运行，比如这一种场景：添加和删除设备，如果只有一台设备，那么添加和删除这两个用例就会共用测试数据，就会产生依赖（即：删除设备用例依赖于添加设备用例成功后执行）

* dname和depends参数使用示例

    ```python
    #!/usr/bin/env python
    # -*- encoding: utf-8 -*-
    '''
    @Author: 思文伟
    @Date: 2021/09/29
    '''

    import stest
    from stest import AbstractTestCase
    from stest import Test as testcase


    class DependTest(AbstractTestCase):
        """依赖设置测试"""
        @classmethod
        def setUpClass(cls):
            pass

        def setUp(self):
            pass

        @testcase(priority=1, enabled=True, author='思文伟', description='dtest1', depends=['vnctest.py'])
        def dtest1(self):
            """ 用例依赖于vnctest.py模块中的所有用例 """

            pass

        @testcase(priority=2, enabled=True, author='思文伟', description='dtest2', depends=['vnctest.py.LoginTest'])
        def dtest2(self):
            """ 用例依赖于vnctest.py模块中LoginTest类的所有用例 """

            pass

        @testcase(priority=2, enabled=True, author='思文伟', description='dtest3', depends=['vnctest.py.LoginTest.login'])
        def dtest3(self):
            """ 用例依赖于vnctest.py模块中LoginTest类的login用例 """
            pass

        @testcase(priority=2, enabled=True, author='思文伟', description='dtest4', dname='four')
        def dtest4(self):
            """ 命名用例为 four """
            pass

        @testcase(priority=2, enabled=True, author='思文伟', description='dtest5', depends=['dtest6'])
        def dtest5(self):
            """ 用例依赖于当前类的dtest6用例 """
            pass

        @testcase(priority=2, enabled=True, author='思文伟', description='dtest6', depends=['four'])
        def dtest6(self):
            """ 用例依赖于当前类的命名为four的dtest4用例 """
            pass

        def tearDown(self):
            pass

        @classmethod
        def tearDownClass(cls):
            pass


    if __name__ == '__main__':
        stest.main()

    ```

## 参数化数据提供者(data provider)

 测试方法装饰器Test会调用数据提供者(data provider), 传测试类名称和测试方法名称给data provider的前两个固定位置参数, data_provider_args参数传给data provider的变长位置参数，data_provider_kwargs参数传给data provider的变长关键字参数

### 内置参数化数据提供者 - SevenDataProvider

实现了参数化测试数据存取方案，使用excel（xlsx或xls格式）存取和管理维护参数化测试数据，简洁直观，易于修改维护。数据在文件中以用例数据块的方式存储。

* 数据块定义：
    >- 所有行中的第一列是标记列，第一行第一列是数据块开始标记
    >- 第一行: 用例名称信息(标记列的下一列是用例方法名称列，之后是用例名称列)
    >- 第二行: 用例数据标题
    >- 第三行 开始 每一行都是一组完整的测试数据直至遇见空行或者下一个数据块

    >![](https://github.com/hotswwkyo/stest/blob/main/img/testcase_data_excel_file.png)

* kwargs变长关键字参数接收参数:
    >- data_file_name - 数据文件名称
    >- data_file_dir_path - 数据文件所在目录路径
    >- sheet_name_or_index - 数据文件中数据所在的工作表索引(从0开始)或名称

* 返回值
    测试数据行信息字典构成的一维列表, 如：
    > [{"减数1": "36", "减数2": "10", "预期": "26"}, {"减数1": "57", "减数2": "30", "预期": "27"}]
    >![](https://github.com/hotswwkyo/stest/blob/main/img/testcase_data_excel_file.png)

* 使用
    框架是默认启用内置的数据提供者（SevenDataProvider）所以不需要做任何设置，返回值是测试数据行信息字典构成的一维列表，所以测试方法统一接收一个参数化参数
    - 启用条件
        >- 测试方法装饰器Test参数enable_default_data_provider 为True，默认值是True
        >- 测试方法装饰器Test参数data_provider 为None（即未设置数据提供者），默认值是True为None

    - 数据文件存放目录
        stest.settings.SEVEN_DATA_PROVIDER_DATA_FILE_DIR 是否设置，设置了则取该值作为参数化测试数据文件的查找目录，否则以被装饰的测试方法所在的模块目录作为查找目录
        > data_provider_kwargs={'data_file_dir_path':'E:\\mytestdatas'}

    - 数据文件名
        通过测试方法装饰器Test参数data_provider_kwargs传入data_file_name，如果没有传入，则取测试方法所属的测试类名作为测试数据文件名称
        > data_provider_kwargs={'data_file_name':'mytest'}

* 示例
```python
class CalculationTest(AbstractTestCase):
        @classmethod
        def setUpClass(cls):
            pass

        def setUp(self):
            pass

        @testcase(priority=4, enabled=True, author='思文伟', data_provider_kwargs={'data_file_dir_path':'E:\\alltest'}, description='整数减法测试02')
        def integer_subtraction_02(self, testdata):
            """使用内置的数据提供者 - 传入测试数据文件所在的目录路径"""

            number_1 = testdata.get("减数1")
            number_2 = testdata.get("减数2")
            expected = testdata.get("预期")

            result = int(number_1) - int(number_2)
            self.assertEqual(result, int(expected))

        @testcase(priority=5, enabled=True, author='思文伟', description='整数减法测试03')
        def integer_subtraction_03(self,testdata):
            """使用内置的数据提供者 - 不传入测试数据文件所在的目录路径,
            则会检测settings.SEVEN_DATA_PROVIDER_DATA_FILE_DIR 是否设置
            ，没有设置则会使用该方法所属的测试类所在的模块目录路径作为测试数据文件的查找目录
            """

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
```


### 自定义参数化数据提供者

自定义参数化数据提供者，可以是AbsractDataProvider的子类或者一个可调用的对象，返回数据集列表（当测试方法只有一个参数化时，应返回一维列表，多个参数化时返回二维列表），必须接收两个固定位置参数，变长位置参数(args)和变长关键字参数(kwargs)，固定位置参数，第一个是测试类名，第二个是测试方法名。

* 返回值
    > 返回测试方法的参数化测试数据列表
    >- 测试方法只有一个参数化时, 返回一维列表 如: demotest(self, testdata), data provider 返回 [{'name':'zhansan', 'age':17}, {'name':'xiaoming', 'age':18}]，方法demotest会执行两次，第一次参数testdata是：{'name':'zhansan', 'age':17}，
    第二次则是：{'name':'xiaoming', 'age':18}
    >- 测试方法有多个参数化时，返回二维列表 如: demotest(self, name, age), data provider 返回 [['zhansan', 17], ['xiaoming', 18]], 方法demotest会执行两次，第一次参数name和age的值分别是：'zhansan', 18，
    第二次则是：'xiaoming', 18

* 实现方式
    >- 继承AbsractDataProvider，实现get_testdatas(self, test_class_name, test_method_name, *args, **kwargs)方法
    >- 其他类型的类似接收以下参数的可调用对象 ------> get_testdatas(test_class_name, test_method_name, *args, **kwargs)

* 使用
    > 通过测试方法装饰器Test参数data_provider来设置为自己的数据提供者（data provider）, 参数data_provider_args和data_provider_kwargs分别用来传给数据提供者（data provider）对应的变长位置参数(args)和变长关键字参数(kwargs)

* 示例
    > 继承自AbsractDataProvider的数据提供者示例(来自内置数据提供者 - SevenDataProvider)
    ```python
    #!/usr/bin/env python
    # -*- encoding: utf-8 -*-
    '''
    @Author: 思文伟
    '''

    import os
    from stest import utils
    from stest.attrs_marker import Var
    from stest.abstract_data_provider import AbsractDataProvider
    from stest.excel_file_reader import TestCaseExcelFileReader as ExcelReader


    class SevenDataProvider(AbsractDataProvider):

        FILE_EXT = Var(".xlsx", True, "数据文件拓展名")
        BLOCK_FLAG = Var("用例名称", True, "用例分隔标记")
        DEFAULT_SHEET_INDEX = Var(0, True, "默认从索引为0的工作表读取数据")

        # get_datasets方法变长字典参数kwargs接收的参数的键名
        PARAM_DATA_FILE_NAME = Var("data_file_name", True, "数据文件名称参数")
        PARAM_DATA_FILE_DIR_PATH = Var("data_file_dir_path", True, "数据文件所在目录路径参数")
        PARAM_SHEET_NAME_OR_INDEX = Var("sheet_name_or_index", True, "数据文件中数据所在的工作表索引(从0开始)或名称参数")
        KWARGS_NAMES = Var((PARAM_DATA_FILE_NAME, PARAM_DATA_FILE_DIR_PATH, PARAM_SHEET_NAME_OR_INDEX), True, "接收的参数名")

        def _get_data_file_name(self, kwargs, default_value=None):

            param = self.PARAM_DATA_FILE_NAME
            filename = kwargs.get(param, default_value)
            if utils.is_blank_space(filename):
                raise ValueError("数据文件名必须是字符串类型且不能为空")
            return filename

        def _get_data_file_dir_paht(self, kwargs):

            param = self.PARAM_DATA_FILE_DIR_PATH
            if param not in kwargs.keys():
                raise AttributeError("没有传入数据文件目录")
            dirpath = kwargs[param]
            if utils.is_blank_space(dirpath):
                raise ValueError("数据文件目录必须是字符串类型且不能为空")
            return dirpath

        def _get_sheet_name_or_index(self, kwargs):
            return kwargs.get(self.PARAM_SHEET_NAME_OR_INDEX, self.DEFAULT_SHEET_INDEX)

        def _build_file_full_path(self, data_file_dir_path, data_file_name):
            """构建完整的excel数据文件路径

            Args:
                data_file_dir_path: 文件目录
                data_file_name: 文件名称
            """

            name = data_file_name
            ext = self.FILE_EXT
            if utils.is_blank_space(data_file_dir_path):
                raise ValueError("传入的数据文件目录路径不能为空：{}".format(data_file_dir_path))
            dir_path = data_file_dir_path
            if name and not utils.is_blank_space(name):
                full_name = name if name.endswith(ext) else name + ext
            else:
                raise ValueError("无效数据文件名称：{}".format(name))
            return os.path.join(dir_path, full_name)

        def get_testdatas(self, test_class_name, test_method_name, *args, **kwargs):
            """根据文件名从指定的excel文件(xlsx文件格式)读取出数据, 返回一维列表，每个元素是excel表中一行测试数据信息字典.
            eg: [{"减数1": "36", "减数2": "10", "预期": "26"}, {"减数1": "57", "减数2": "30", "预期": "27"}]

            Args:
                kwargs:
                    file_name 数据文件名, 不提供则测试类名称作为文件名
                    file_dir_path 数据文件所在目录路径
                    sheet_index_or_name Excel工作表索引(从0开始)或名称,不提供则默认取索引0的工作表
            """

            datasets = []

            filename = self._get_data_file_name(kwargs, test_class_name)
            dirpath = self._get_data_file_dir_paht(kwargs)
            full_file_path = self._build_file_full_path(dirpath, filename)

            reader = ExcelReader(full_file_path, testcase_block_separators=self.BLOCK_FLAG, sheet_index_or_name=self._get_sheet_name_or_index(kwargs))
            datas_blocks = reader.load_testcase_data()
            for block in datas_blocks:
                if block.name == test_method_name:
                    for row in block.datas:
                        line = {}
                        for cell in row:
                            for title, value in cell.items():
                                if title in line.keys():
                                    continue
                                else:
                                    line[title] = value
                        datasets.append(line)
                    break
            return datasets


    class CalculationTest(AbstractTestCase):
        @classmethod
        def setUpClass(cls):
            pass

        def setUp(self):
            pass

        @testcase(priority=1, enabled=True, data_provider=SevenDataProvider, data_provider_kwargs={'data_file_dir_path':'E:\\mytestdatas'}, author='思文伟', description='整数加法测试01')
        def integer_addition_01(self, testdata):
            """自定义数据提供者 - 测试方法一个参数化示例"""

            number_1 = testdata.get("加数1")
            number_2 = testdata.get("加数2")
            expected = testdata.get("预期")

            result = number_1 + number_2
            self.assertEqual(result, expected)

        def tearDown(self):
            pass

        @classmethod
        def tearDownClass(cls):
            pass

    if __name__ == '__main__':
        CalculationTest.run_test()

    ```

    > 非AbsractDataProvider子类数据提供者示例
    ```python
    #!/usr/bin/env python
    # -*- encoding: utf-8 -*-
    '''
    @Author: 思文伟
    '''

    from stest import AbstractTestCase
    from stest import Test as testcase


    class Demo1DataProvider(object):

        def get_testdatas(self, test_class_name, test_method_name, *args, **kwargs):

            return [[1,2,3],[3,4,7]]


    class Demo1Test(AbstractTestCase):

        @testcase(priority=1, enabled=True, data_provider=Demo1DataProvider().get_testdatas, author='思文伟', description='两数加法测试01')
        def integer_addition_02(self, number_1, number_2, expected):

            result = number_1 + number_2
            self.assertEqual(result, expected)

    if __name__ == '__main__':

        Demo1Test.run_test()
    ```

    > 函数数据提供者示例
    ```python
    #!/usr/bin/env python
    # -*- encoding: utf-8 -*-
    '''
    @Author: 思文伟
    '''

    from stest import AbstractTestCase
    from stest import Test as testcase


    def get_testdatas(test_class_name, test_method_name, *args, **kwargs):

        return [[1,2,3], [3,4,7]]


    class Demo1Test(AbstractTestCase):

        @testcase(priority=1, enabled=True, data_provider=get_testdatas, author='思文伟', description='两数加法测试01')
        def integer_addition_02(self, number_1, number_2, expected):

            result = number_1 + number_2
            self.assertEqual(result, expected)

    if __name__ == '__main__':

        Demo1Test.run_test()
    ```

## 钩子(hook)

>* 通过wrapper 定义钩子
>* 钩子函数需要能接收它所挂载到的宿主函数的所有参数，此外还需要接收一个额外参数作为第一个位置参数，这个额外参数为全局变量settings。
>* 通过runstage参数指定钩子的运行阶段，框架会根据运行阶段标志执行钩子
>* 框架内置运行阶段标志见 RunStage类，对应于SevenTestResult的同名方法。编写这些运行阶段的钩子函数时，除了第一个参数为全局变量settings外，其它参数与SevenTestResult的同名方法参数一一对应

#### 示例
    ```python
    #!/usr/bin/env python
    # -*- encoding: utf-8 -*-

    import stest
    from stest import hook
    from stest import AbstractTestCase
    from stest import Test as testcase
    from playwright.sync_api import sync_playwright


    @hook.wrapper(hook.RunStage.startTestRun)
    def startTestRun(conf:stest.settings, result:stest.core.seven_result.SevenTestResult):
        """Called once before any tests are executed."""
        conf.playwright = sync_playwright().start()

    @hook.wrapper(hook.RunStage.stopTestRun)
    def stopTestRun(conf:stest.settings, result:stest.core.seven_result.SevenTestResult):
        """Called once after all tests are executed."""
        playwright = getattr(conf, 'playwright', None)
        if playwright is not None:
            playwright.stop()
    ```


## Page object 实现方案

*  web页面、app页面和window应用程序页面封装（selenium appium WinAppDriver）
    > 封装的页面类应继承自抽象页面类AbstractPage。页面需要有两个内部类Elements（元素类）和Actions（动作类）,分别继承自抽象也的AbstractPage.Elements（元素类）和AbstractPage.Actions（动作类），分别用于封装页面的元素和页面动作。实例化页面的时候会自动实例化Elements（元素类）和Actions（动作类），分别赋给页面实例属性elements和actions。页面类属性DRIVER_MANAGER指向驱动管理器，WIN_APP_DRIVER_HELPER指向启动和关闭WinAppDriver.exe助手。
* 微信小程序页面封装（minium）
    > 封装的页面类应继承自抽象页面类AbstractMiniumPage。页面需要有两个内部类Elements（元素类）和Actions（动作类）,分别继承自抽象也的AbstractMiniumPage.Elements（元素类）和AbstractMiniumPage.Actions（动作类），分别用于封装页面的元素和页面动作。实例化页面的时候会自动实例化Elements（元素类）和Actions（动作类），分别赋给页面实例属性elements和actions。页面类属性WECHAT_MANAGER指向驱动管理器
* web页面封装（playwright 自动化测试工具）
    > 封装的页面类应继承自抽象页面类AbstractPlaywrightPage。页面需要有两个内部类Elements（元素类）和Actions（动作类）,分别继承自抽象也的AbstractPlaywrightPage.Elements（元素类）和AbstractPlaywrightPage.Actions（动作类），分别用于封装页面的元素和页面动作。实例化页面的时候会自动实例化Elements（元素类）和Actions（动作类），分别赋给页面实例属性elements和actions。页面类属性DRIVER_MANAGER指向驱动管理器。

### Web页面示例
```python
#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author: 思文伟
'''

from stest.testobjs.abstract_page import AbstractPage


class LoginPage(AbstractPage):
    """登录页面"""
    def init(self):
        """其实不需要这个，页面会自省的去自动创建元素和动作，这样做只是为了开发工具可以使用.引出相关的元素和动作方法"""
        cls = self.__class__
        self.elements = cls.Elements(self)
        self.actions = cls.Actions(self)

    class Elements(AbstractPage.Elements):
        @property
        def username(self):

            name = "用户名"
            xpath = '//div[@id="app"]//div[@class="loginBox"]//form//label[normalize-space()="{}"]/following-sibling::div//input'.format(name)
            return self.page.find_element_by_xpath(xpath)

        @property
        def password(self):

            name = "密码"
            xpath = '//div[@id="app"]//div[@class="loginBox"]//form//label[normalize-space()="{}"]/following-sibling::div//input'.format(name)
            return self.page.find_element_by_xpath(xpath)

        @property
        def login(self):

            name = "登录"
            xpath = '//div[@id="app"]//div[@class="loginBox"]//form//button//span[normalize-space()="{}"]'.format(name)
            return self.page.find_element_by_xpath(xpath)

    class Actions(AbstractPage.Actions):
        def username(self, name):

            self.page.elements.username.clear()
            self.page.elements.username.send_keys(name)
            return self

        def password(self, pwd):

            self.page.elements.password.clear()
            self.page.elements.password.send_keys(pwd)
            return self

        def login(self):

            self.page.elements.login.click()
            return self

```
```python
#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author: 思文伟
'''

import stest
from stest import settings
from stest import AbstractTestCase
from stest import Test as testcase

# 驱动管理器
from stest.dm import DRIVER_MANAGER

from ..pages.web.login_page import LoginPage


class WebLoginPageTest(AbstractTestCase):
    """ 登录页面测试 """
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    @testcase(priority=1, enabled=True, screenshot=True, author='思文伟', description='用正确账号密码登录测试')
    def login_with_right_user_and_password(self, testdata):

        user = testdata.get("用户名")
        pwd = testdata.get("用户密码")
        url = settings.URLS.get('登录页面url')
        LoginPage().chrome(url, executable_path=settings.CHROME_DRIVER_PATH).maximize_window().actions.username(user).sleep(2).password(pwd).login().sleep(7)

    def tearDown(self):
        pass

    @classmethod
    def tearDownClass(cls):

        DRIVER_MANAGER.close_all_drivers()


if __name__ == '__main__':
    # WebLoginPageTest.run_test()
    stest.main()

```
### APP页面示例
```python
#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author: 思文伟
'''

from stest.testobjs.abstract_page import AbstractPage


class LoginPage(AbstractPage):
    """ APP登录页面 """
    class Elements(AbstractPage.Elements):
        @property
        def continue_btn(self):
            """授权页->继续按钮"""

            xpath = 'UiSelector().resourceId("com.android.permissioncontroller:id/continue_button")'
            return self.page.find_element_by_android_uiautomator(xpath)

        @property
        def confirm_btn(self):
            """更新提示->确定按钮"""

            xpath = 'UiSelector().resourceId("android:id/button1")'
            return self.page.find_element_by_android_uiautomator(xpath)

        @property
        def username(self):
            """用户名输入框"""

            xpath = 'UiSelector().resourceId("userName")'
            return self.page.find_element_by_android_uiautomator(xpath)

        @property
        def password(self):
            """密码输入框"""

            xpath = 'UiSelector().resourceId("password")'
            return self.page.find_element_by_android_uiautomator(xpath)

        @property
        def login(self):
            """登录按钮"""

            xpath = 'UiSelector().resourceId("submit")'
            return self.page.find_element_by_android_uiautomator(xpath)

        @property
        def reminder(self):
            """下次提醒"""

            xpath = 'UiSelector().resourceId("android:id/button1")'
            return self.page.find_element_by_android_uiautomator(xpath)

    class Actions(AbstractPage.Actions):
        def click_continue_btn(self):
            self.page.elements.continue_btn.click()
            return self

        def click_confirm_btn(self):
            self.page.elements.confirm_btn.click()
            return self

        def username(self, name):
            """输入用户名"""

            self.page.elements.username.clear()
            self.page.elements.username.send_keys(name)
            return self

        def password(self, pwd):
            """输入密码"""

            self.page.elements.password.clear()
            self.page.elements.password.send_keys(pwd)
            return self

        def login(self):
            """点击登录按钮"""

            self.page.elements.login.click()
            return self

        def reminder(self):
            """下次提醒"""

            self.page.elements.reminder.click()
            return self

```
```python
#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author: 思文伟
'''

import stest
from stest import AbstractTestCase
from stest import Test as testcase
from stest.dm import DRIVER_MANAGER

from ..pages.app.login_page import LoginPage
from ..pages.app.home_page import HomePage
from ..pages.app.main_page import SettlementMainPage


class AppLoginPageTest(AbstractTestCase):
    """APP登录页面测试"""
    @classmethod
    def setUpClass(cls):

        cls.desired_caps = {
            'platformName': 'Android',  # 平台名称
            'platformVersion': '10.0',  # 系统版本号
            'deviceName': 'P10 Plus',  # 设备名称。如果是真机，在'设置->关于手机->设备名称'里查看
            'appPackage': 'com.ddnapalon.calculator.gp',  # apk的包名
            'appActivity': 'com.ddnapalon.calculator.gp.ScienceFragment',  # activity 名称
            # 'automationName': "uiautomator2"
        }
        cls.desired_caps["appPackage"] = "com.zgdygf.zygfpfapp"
        cls.desired_caps["appActivity"] = "io.dcloud.PandoraEntry"
        cls.server_url = "http://127.0.0.1:4723/wd/hub"
        # adb shell am start -W -n com.zgdygf.zygfpfapp/io.dcloud.PandoraEntry

    def setUp(self):
        pass

    @testcase(priority=1, enabled=True, screenshot=True, author='思文伟', description='成功登录测试')
    def test_successfully_login(self, testdata):

        name = testdata.get("用户名")
        pwd = testdata.get("密码")

        page = LoginPage()
        page.open_app(self.server_url, desired_capabilities=self.desired_caps, implicit_wait_timeout=10)
        page.actions.click_continue_btn().sleep(2).click_confirm_btn().sleep(2).username(name).password(pwd).login().sleep(2).reminder().sleep(21)
        # HomePage().elements.settlement_tab
        HomePage().actions.sleep(2).click_settlement_tab()
        sp = SettlementMainPage()
        sp.actions.sleep(7).swipe_to_select_year("2019年").sleep(7).input_film_name("单行道").click_search().sleep(3)
        page.hide_keyboard()
        sp.actions.click_film_item("单行道")

    def tearDown(self):
        pass

    @classmethod
    def tearDownClass(cls):

        DRIVER_MANAGER.close_all_drivers()


if __name__ == "__main__":
    # AppLoginPageTest.run_test()
    stest.main()

```
### 微信小程序页面示例
```python
# -*- coding:utf-8 -*-

from stest.testobjs.abstract_minium_page import AbstractMiniumPage


class ADBasketPage(AbstractMiniumPage):
    """ 广告篮页面 """
    class Elements(AbstractMiniumPage.Elements):
        @property
        def do_ad_btn(self):
            """去投放广告"""

            selector = '#cart'
            inner_text = '去投放广告'
            return self.page.get_element(selector).get_element('view').get_element('view').get_element('button', inner_text=inner_text)

        @property
        def tabbar(self):
            """首页下方tab工具栏"""

            selector = '.mp-tabbar'
            return self.page.get_element(selector)

        @property
        def home_tab(self):
            """首页 标签"""

            selector = '.weui-tabbar__label'
            inner_text = "首页"
            return self.tabbar.get_element(selector, inner_text=inner_text)

        @property
        def ad_tab(self):
            """广告篮 标签"""

            selector = '.weui-tabbar__label'
            inner_text = "广告篮"
            return self.tabbar.get_element(selector, inner_text=inner_text)

        @property
        def order_tab(self):
            """订单 标签"""

            selector = '.weui-tabbar__label'
            inner_text = "订单"
            return self.tabbar.get_element(selector, inner_text=inner_text)

        @property
        def my_tab(self):
            """我的 标签"""

            selector = '.weui-tabbar__label'
            inner_text = "我的"
            return self.tabbar.get_element(selector, inner_text=inner_text)

        @property
        def _ad_cart(self):
            """广告购物车"""

            s = 'view>cart#cart'
            el_cart = self.page.get_element(s)
            el_cart.click()
            self.page.sleep(1)
            return el_cart

        def cinema_checkbox(self, cinema):
            """影院复选框

            Args:
                cinema: 影院
            """

            s1 = 'view.container.car>view.cinema-list>view.backgroud-float>view.flex-row>view.cinema-title'
            # 影院名
            s2 = 'text'
            # 复选框
            s8 = 'view>image.cart-icon'
            el_cts = self._ad_cart.get_elements(s1)
            el_cb = None
            for el_ct in el_cts:
                el_cinema = el_ct.get_element(s2)
                if el_cinema and el_cinema.inner_text == cinema:
                    el_cb = el_ct.get_element(s8)
                    if el_cb:
                        break
            return el_cb

        @property
        def all_schedules(self):
            """所有影院排期, 未调试，误用

            Args:
                cinema: 影院
            """

            s1 = 'view.container.car>view.cinema-list>view.backgroud-float'
            # 影院名
            s2 = 'view.flex-row>view.cinema-title>text.cinema-Name'
            # 放映日期
            s3 = 'view.cart--cinema-time'
            # 排期列表
            s4 = 'view.cart--cart-goods'
            # 影片名称
            s5 = 'view.cart-img>view.cart-message>view.name>text.filmName'
            # 放映时间
            s6 = 'view.cart-img>view.cart-message>view.common-flex>text.playTime'
            # 影厅
            s7 = 'view.cart-img>view.cart-message>view.common-flex>text.filmType'

            el_cinemaboxs = self._ad_cart.get_elements(s1)
            schedules = {}
            # {
            # 'el_cinema': {
            # 'el_showdate': [
            # (el_film, el_showtime, el_hall),...
            # ]
            # }
            # }
            for el_cinemabox in el_cinemaboxs:
                el_cinema = el_cinemabox.get_element(s2)
                if el_cinema:
                    cinema_schedules = {}  # 影院排期
                    el_cart_boxes = el_cinemabox.get_elements('view>view.cart--cart-box')
                    for el_cart_box in el_cart_boxes:
                        el_showdate = el_cinemabox.get_element(s3)
                        if not el_showdate:
                            continue
                        el_cart_goods = el_cart_box.get_element(s4)
                        one_day_schedules = []
                        for el_cart_good in el_cart_goods:
                            el_film = el_cart_good.get_element(s5)
                            el_showtime = el_cart_good.get_element(s6)
                            el_hall = el_cart_good.get_element(s7)
                            if el_film and el_showtime and el_hall:
                                one_day_schedules.append((el_film, el_showtime, el_hall))
                        cinema_schedules[el_showdate] = one_day_schedules
                    schedules[el_cinema] = cinema_schedules
            return schedules

        def schedule_checkbox(self, cinema, film, hall, showdate, showtime):
            """排期复选框

            Args:
                film: 影片
                cinema: 影院
                hall: 影厅
                showdate: 放映日期
                showtime: 放映时间
            """

            s1 = 'view.container.car>view.cinema-list>view.backgroud-float'
            # 影院名
            s2 = 'view.flex-row>view.cinema-title>text'
            # 放映日期
            s3 = 'view>view.cart--cart-box>view.cart--cinema-time'
            # 排期列表
            s4 = 'view>view.cart--cart-box>view.cart--cart-goods'
            # 影片名称
            s5 = 'view.cart-img>view.cart-message>view.name>text'
            # 放映时间
            s6 = 'view.cart-img>view.cart-message>view.common-flex>text'
            # 影厅
            s7 = 'view.cart-img>view.cart-message>view.common-flex>text'
            # 复选框
            s8 = 'view>image'
            el_cinemaboxs = self._ad_cart.get_elements(s1)
            el_cb = None
            for el_cinemabox in el_cinemaboxs:
                el_cinema = el_cinemabox.get_element(s2, inner_text=cinema)
                if el_cinema:
                    el_showdate = el_cinemabox.get_element(s3, inner_text=showdate)
                    if el_cinema and el_showdate:
                        el_goods = el_cinemabox.get_elements(s4)
                        for el_good in el_goods:

                            el_film = el_good.get_element(s5, inner_text=film)
                            el_showtime = el_good.get_element(s6, inner_text=showtime)
                            el_halls = el_good.get_elements(s7)
                            el_rhall = None
                            for el_hall in el_halls:
                                if el_hall.inner_text.strip().startswith(hall):
                                    el_rhall = el_hall
                                    break

                            if el_film and el_showtime and el_rhall:
                                el_cb = el_good.get_element(s8)
                                if el_cb:
                                    break
                if el_cb:
                    break
            return el_cb

        @property
        def select_all_btn(self):
            """全选按钮"""

            inner_text = '全选'
            s = 'view.container.car>view.cart-bottom>view.car-pay>view.cart-bottom-select>text'
            return self._ad_cart.get_element(s, inner_text=inner_text)

        @property
        def org_price(self):
            """原价结算金额"""

            inner_text = '原价结算'
            s1 = 'view.container.car>view.cart-bottom>view.car-pay>view.cart-bottom-pay>view.cart-btn'
            s2 = 'view'

            el_p_btn = None
            el_btns = self._ad_cart.get_elements(s1)
            for el_btn in el_btns:
                el_yj = el_btn.get_element(s2, inner_text=inner_text)
                if el_yj:
                    el_views = el_btn.get_elements(s2)
                    el_p_btn = el_views[0]
            return el_p_btn

        @property
        def org_price_btn(self):
            """原价结算按钮"""

            inner_text = '原价结算'
            s = 'view.container.car>view.cart-bottom>view.car-pay>view.cart-bottom-pay>view.cart-btn>view'
            return self._ad_cart.get_element(s, inner_text=inner_text)

        @property
        def pt_price(self):
            """拼团结算金额"""

            inner_text = '拼团结算'
            s1 = 'view.container.car>view.cart-bottom>view.car-pay>view.cart-bottom-pay>view.cart-btn'
            s2 = 'view'

            el_p_btn = None
            el_btns = self._ad_cart.get_elements(s1)
            for el_btn in el_btns:
                el_yj = el_btn.get_element(s2, inner_text=inner_text)
                if el_yj:
                    el_views = el_btn.get_elements(s2)
                    el_p_btn = el_views[0]
            return el_p_btn

        @property
        def pt_price_btn(self):
            """拼团结算按钮"""

            inner_text = '拼团结算'
            s = 'view.container.car>view.cart-bottom>view.car-pay>view.cart-bottom-pay>view.cart-btn>view'
            return self._ad_cart.get_element(s, inner_text=inner_text)

    class Actions(AbstractMiniumPage.Actions):
        def click_do_ad_btn(self):
            """点击去投放广告按钮"""

            self.page.elements.do_ad_btn.click()
            return self

        def click_tabbar(self):
            """点击下方标签工具栏"""

            self.page.elements.tabbar.click()
            return self

        def click_home_tab(self):
            """点击下方首页标签"""

            self.page.elements.home_tab.click()
            return self

        def click_ad_tab(self):
            """点击下方广告篮标签"""

            self.page.elements.ad_tab.click()
            return self

        def click_order_tab(self):
            """点击下方订单标签"""

            self.page.elements.order_tab.click()
            return self

        def click_my_tab(self):
            """点击下方我的标签"""

            self.page.elements.my_tab.click()
            return self

        def click_cinema_checkbox(self, cinema):
            """点击 影院复选框"""

            self.page.elements.cinema_checkbox(cinema).click()
            return self

        def click_schedule_checkbox(self, cinema, film, hall, showdate, showtime):
            """点击 排期复选框"""

            self.page.elements.schedule_checkbox(cinema, film, hall, showdate, showtime).click()
            return self

        def select_all(self):
            """点击全选按钮"""

            self.page.elements.select_all_btn.click()
            return self

        def org_price_equals(self, price, prefix='￥'):
            """检查原价结算金额是否正确"""

            ptext = self.page.elements.org_price.inner_text
            a_price = ptext.strip().lstrip(prefix)
            if a_price != price:
                self.page.fail('原价结算金额实际({})显示与预期({})不等'.format(a_price, price))
            return self

        def click_org_price(self):
            """点击原价结算按钮"""

            self.page.elements.org_price_btn.click()
            return self

        def pt_price_equals(self, price, prefix='￥'):
            """检查拼团结算金额是否正确"""

            ptext = self.page.elements.pt_price.inner_text
            a_price = ptext.strip().lstrip(prefix)
            if a_price != price:
                self.page.fail('拼团结算金额实际({})显示与预期({})不等'.format(a_price, price))
            return self

        def click_pt_price(self):
            """点击拼团结算按钮"""

            self.page.elements.pt_price_btn.click()
            return self

```
```python
#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author: 思文伟
'''

import datetime

import stest
from stest import AbstractTestCase
from stest import Test as testcase
from stest.dm import DRIVER_MANAGER

from ..pages.wechat_mini.ad_basket_page import ADBasketPage
from ..pages.wechat_mini.index_page import IndexPage
from ..pages.wechat_mini.my_adlist_page import MyAdListPage
from ..pages.wechat_mini.cinema_list_page import CinemaListPage
from ..pages.wechat_mini.cinema_detail_page import CinemaDetailPage


class WechatMiniPageTest(AbstractTestCase):
    """微信小程序页面示例"""
    @classmethod
    def setUpClass(cls):

        cls.minium_config = {
            "platform": "ide",
            "debug_mode": "info",
            "close_ide": False,
            "no_assert_capture": False,
            "auto_relaunch": False,
            "device_desire": {},
            "report_usage": True,
            "remote_connect_timeout": 180,
            "use_push": True
        }

    def setUp(self):
        pass

    @testcase(priority=1, enabled=True, author='思文伟', description='广告投放界面->广告视频显示的正确性 - 影院列表>加入广告栏')
    def test_add_ad_to_ad_basket_in_cinemalist(self, testdata):

        ad_name = testdata.get('广告名')
        cinema = testdata.get('影院名称')
        film = testdata.get('影片名称')
        hall = testdata.get('影厅名称')
        showdate = testdata.get('放映日期')
        showtime = testdata.get('放映时间')
        showdate_fmt = testdata.get('放映日期格式', '%Y-%m-%d')

        month_day = datetime.datetime.strptime(showdate, showdate_fmt).strftime('%m-%d')
        ipage = IndexPage('/pages/index/index', minium_config=self.minium_config)
        ipage.actions.click_tabbar().sleep(1).click_home_tab().sleep(1)
        ipage.actions.click_cinema_ad_btn()

        clpage = CinemaListPage()
        clpage.actions.sleep(1).is_page_self('/pages/cinema/cinema')
        clpage.actions.upload_ad().sleep(2)

        p = MyAdListPage()
        p.actions.is_page_self().click_ad_checkbox(ad_name).sleep(1).to_launch().sleep(2)
        clpage.actions.click_cinema_item(cinema).sleep(1)

        cdp = CinemaDetailPage()
        cdp.actions.click_film(film).select_day(month_day).sleep(1).click_schedule(film, hall, showtime).sleep(1).confirm().sleep(2)
        clpage.actions.join_to_ad_basket().sleep(1).shopping_basket().sleep(1)

        bp = ADBasketPage()
        bp.actions.click_schedule_checkbox(cinema, film, hall, showdate, showtime)

    def tearDown(self):
        pass

    @classmethod
    def tearDownClass(cls):

        DRIVER_MANAGER.close_all_drivers()


if __name__ == "__main__":
    # WechatMiniPageTest.run_test()
    stest.main()

```
### window应用程序页面示例
```python
#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author: 思文伟
'''

from stest.testobjs.abstract_page import AbstractPage


class VNCViewerPage(AbstractPage):
    """VNCViewer页面"""
    def init(self):
        """其实不需要这个，页面会自省的去自动创建元素和动作，这样做只是为了开发工具可以使用.引出相关的元素和动作方法"""
        cls = self.__class__
        self.elements = cls.Elements(self)
        self.actions = cls.Actions(self)

    class Elements(AbstractPage.Elements):
        @property
        def server_ip(self):
            """ip地址输入框"""

            return self.page.find_element_by_accessibility_id('1001')

        @property
        def ok(self):
            """ok按钮"""

            return self.page.find_element_by_name("OK")

        @property
        def pwd(self):
            """密码输入框"""

            locator = "./*"
            childrens = self.page.find_elements_by_xpath(locator)  # 获取当前窗口下的所有子元素
            element = None
            for c in childrens:
                # print("c.get_attribute("IsEnabled")=", c.get_attribute("IsEnabled"))
                if c.get_attribute("IsEnabled") == "true":  # 通过界面我们知道 只有输入密码框是可编辑的，所以使用该条件来判断是否密码输入框元素
                    element = c
                    break
            if element is None:
                message = "{} with locator '{}' not found.".format("xpath", locator)
                self.page.raise_no_such_element_exc(message)
            return element

    class Actions(AbstractPage.Actions):
        def server_ip(self, ip):
            """输入ip"""

            element = self.page.elements.server_ip
            element.clear()
            element.send_keys(ip)
            return self

        def ok(self):
            """点击ok按钮"""

            self.page.elements.ok.click()
            return self

        def pwd(self, password):

            element = self.page.elements.pwd
            element.clear()
            element.send_keys(password)
            return self

```
```python
#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author: 思文伟
'''

import stest
# from stest import settings
from stest import AbstractTestCase
from stest import Test as testcase
from stest.dm import DRIVER_MANAGER
from stest.dm import WIN_APP_DRIVER_HELPER

from ..pages.winapp.vncviewer_page import VNCViewerPage


class VNCViewerPageTest(AbstractTestCase):
    """ 使用WinAppDriver.exe测试Window应用程序VNCViewer示例 """
    @classmethod
    def setUpClass(cls):

        WIN_APP_DRIVER_HELPER.startup_winappdriver(r"E:\Program Files (x86)\Windows Application Driver\WinAppDriver.exe")

    def setUp(self):
        pass

    @testcase(priority=1, enabled=True, screenshot=True, author='思文伟', description='用正确账号密码登录测试')
    def connect_remote_pc_desktop(self, testdata):

        ip = testdata.get("远程桌面登录账户")
        pwd = testdata.get("远程桌面登录密码")
        vnc_title = "VNC Viewer : Authentication [No Encryption]"
        desired_capabilities = {}
        desired_capabilities["app"] = r"C:\Users\siwenwei\Desktop\vnc-4_1_2-x86_win32_viewer.exe"  # vnc viewer 的执行路径
        server_url = "http://127.0.0.1:4723"
        page = VNCViewerPage()
        page.open_window_app(server_url, desired_capabilities)

        page.actions.sleep(5).server_ip(ip).sleep(1).ok()
        # 上面点击ok后，到下一个界面显示出来需要时间，所以这里设置延时等待
        page.switch_window_by_title(vnc_title, timeout=20).actions.pwd(pwd).sleep(2).ok()

    def tearDown(self):
        pass

    @classmethod
    def tearDownClass(cls):

        DRIVER_MANAGER.close_all_drivers()
        WIN_APP_DRIVER_HELPER.shutdown_winappdriver()


if __name__ == '__main__':
    # VNCViewerPageTest.run_test()
    stest.main()

```
### playwrigh自动化测试工具 - Web页面示例
```python
#!/usr/bin/env python
# -*- encoding: utf-8 -*-


from stest.testobjs.abstract_playwright_page import AbstractPlaywrightPage


class LoginPage(AbstractPlaywrightPage):

    # 因是利用反射自动构建的实例对象，ide无法通过点(dot)带出实例下的属性以及方法，
    # 通过self.elements = typing.cast(LoginPage.Elements, self.elements)这个方式就可以解决该问题
    def _build_elements(self):
        rv = super()._build_elements()
        self.elements = typing.cast(LoginPage.Elements, self.elements)
        return rv

    # 因是利用反射自动构建的实例对象，ide无法通过点(dot)带出实例下的属性以及方法，
    # 通过self.actions = typing.cast(LoginPage.Actions, self.actions)这个方式就可以解决该问题
    def _build_actions(self):
        rv = super()._build_actions()
        self.actions = typing.cast(LoginPage.Actions, self.actions)
        return rv

    class Elements(AbstractPlaywrightPage.Elements):

        def __init__(self, page):
            super().__init__(page)
            self.page = typing.cast(LoginPage, self.page)

        @property
        def login_link(self):
            """登录弹窗按钮"""

            selector = '//*[@id="bid"]//div[contains(@class,"user_icon")]/a'
            return self.page.get_by_xpath(selector)

        @property
        def login_title(self):

            return self.page.get_by_text("账号登录", exact=True)

        @property
        def username(self):

            self.page.get_by_text("手机号/邮箱").click()
            self.sleep(1)
            return self.page.get_by_id("Id")

        @property
        def password(self):

            self.page.get_by_xpath('//*[@id="showpsd"]').click()
            self.sleep(1)
            return self.page.get_by_id("passwordFU")

        @property
        def login(self):
            """登录按钮"""

            return self.page.pwpage.get_by_role("link", name="登 录")

    class Actions(AbstractPlaywrightPage.Actions):

        # 因是利用反射自动构建的实例对象，ide无法通过点(dot)带出实例下的属性以及方法，
        # 通过这个方式就可以解决该问题：self.page = typing.cast(LoginPage, self.page)
        def __init__(self, page):
            super().__init__(page)
            self.page = typing.cast(LoginPage, self.page)

        def login(self, name, pwd):
            """登录

            Args
            -------
            name : 手机号/邮箱
            pwd : 密码
            """

            self.page.elements.login_link.click()
            self.sleep(1)
            self.page.elements.login_title.click()
            self.sleep(1)
            self.page.elements.username.fill(name)
            self.page.elements.password.fill(pwd)
            self.page.elements.login.click()
            return self

```
```python
#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import stest
from ..pages.login_page import LoginPage


class LoginTest(stest.AbstractTestCase):

    @classmethod
    def setUpClass(cls):

        pass

    def setUp(self):

        pass

    @stest.Test(enabled=True, name="用正确账号密码登录测试", screenshot=True, groups=["all", "cctv"])
    def login_with_right_user_and_password(self):

        LoginPage().chrome().open_url("https://tv.cctv.com/").actions.login("test@qq.com", '123456')

    def tearDown(self):

        pass

    @classmethod
    def tearDownClass(cls):

        pass

    @classmethod
    def tearDownClass(cls):

        pass


if __name__ == '__main__':
    LoginTest.run_test()

```
