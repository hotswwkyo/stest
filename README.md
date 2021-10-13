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
    # GLOBAL_CONFIG.seven_data_provider_data_file_dir = r'E:\sw'


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
            则会检测GLOBAL_CONFIG.seven_data_provider_data_file_dir 是否设置
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

## Test参数说明

| 参数 | 类型 | 描述 |
| ---- | ---- | ---- |
| author | 字符串 | 用例编写者 |
| editors | 列表 | 修改者列表 |
| dname | 字符串或列表 | 用于给用例起一个用于设置依赖的名称 |
| depends | 列表 | 用于设置用例依赖，是一个用例依赖列表 |
| groups | 列表 | 方法所属的组的列表|
| enabled | 布尔值 | 是否启用执行该测试方法 |
| priority | 整数 | 测试方法的执行优先级，数值越小执行越靠前 |
| alway_run | 布尔值 | 如果设置为True，不管依赖它所依赖的其他用例结果如何都始终运行，为False时，则它所依赖的其他用例不成功，就不会执行，默认值为False |
| description | 字符串 | 测试用例名称 |
| data_provider | object | 测试方法的参数化数据提供者，默认值是None，AbsractDataProvider的子类或者一个可调用的对象，返回数据集列表（当测试方法只有一个参数化时，应返回一维列表，多个参数化时返回二维列表） |
| data_provider_args | 元祖 | 数据提供者变长位置参数(args) |
| data_provider_kwargs | 字典 | 数据提供者变长关键字参数(kwargs) |
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
        通过测试方法装饰器Test参数data_provider_kwargs传入data_file_dir_path，如果没有传入，则会去检查全局配置unittest_seven_helper.GLOBAL_CONFIG.seven_data_provider_data_file_dir是否设置，设置了则取该值作为参数化测试数据文件的查找目录，否则以被装饰的测试方法所在的模块目录作为查找目录
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
            则会检测GLOBAL_CONFIG.seven_data_provider_data_file_dir 是否设置
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
    from stest.attrs_marker import AttributeMarker
    from stest.abstract_data_provider import AbsractDataProvider
    from stest.excel_file_reader import TestCaseExcelFileReader as ExcelReader


    class SevenDataProvider(AbsractDataProvider):

        FILE_EXT = AttributeMarker(".xlsx", True, "数据文件拓展名")
        BLOCK_FLAG = AttributeMarker("用例名称", True, "用例分隔标记")
        DEFAULT_SHEET_INDEX = AttributeMarker(0, True, "默认从索引为0的工作表读取数据")

        # get_datasets方法变长字典参数kwargs接收的参数的键名
        PARAM_DATA_FILE_NAME = AttributeMarker("data_file_name", True, "数据文件名称参数")
        PARAM_DATA_FILE_DIR_PATH = AttributeMarker("data_file_dir_path", True, "数据文件所在目录路径参数")
        PARAM_SHEET_NAME_OR_INDEX = AttributeMarker("sheet_name_or_index", True, "数据文件中数据所在的工作表索引(从0开始)或名称参数")
        KWARGS_NAMES = AttributeMarker((PARAM_DATA_FILE_NAME, PARAM_DATA_FILE_DIR_PATH, PARAM_SHEET_NAME_OR_INDEX), True, "接收的参数名")

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
