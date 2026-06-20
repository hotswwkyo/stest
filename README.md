# stest

更友好、更灵活的编写、管理与运行测试，生成更加美观的独立单文件 HTML 报告。内置参数化测试数据存取方案，省去设计的烦恼，节省更多的时间，从而更快的投入到编写用例阶段。

![](https://github.com/hotswwkyo/stest/blob/main/img/htmlreport.png)

### 功能特性

| 类别 | 特性 |
| :---- | :---- |
| **用例管理** | 命名测试方法（与 docstring 不冲突）、设置执行顺序、用例依赖 |
| **参数化** | 参数化测试、数据驱动测试、内置 Excel 数据存取方案（SevenDataProvider） |
| **测试报告** | 简洁美观的独立单文件 HTML 报告、Jenkins JUnit XML 格式报告 |
| **截图** | 测试失败自动截图、截图附加到报告、快速添加截图到报告 |
| **配置** | 自动查找并载入项目 `settings.py` 配置文件、灵活控制截图与报告行为 |
| **Page Object** | 内置 Selenium/Appium/Playwright/Minium/WinAppDriver 的 Page Object 实现方案 |
| **驱动管理** | DRIVER_MANAGER 统一管理驱动会话，支持多实例切换 |


## 安装

```bash
# pip 方式安装
pip install stest

# 源码方式安装（需以管理员方式执行）
python setup.py install
```

## 执行测试

```bash
# 执行指定测试文件，生成 HTML 报告
python -m stest -v -html D:\temp\tms_apitest.html calculation_test.py

# 发现并执行指定目录下的测试
python -m stest discover -s erp_autotest\testcases -p *.py

# 查看命令行帮助
python -m stest -h
```

代码中调用 `stest.main()` 执行：

```python
#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import stest
from stest import AbstractTestCase
from stest import Test as testcase


def get_testdatas(test_class_name, test_method_name, *args, **kwargs):
    return [[1, 2, 3], [3, 4, 7]]


class Demo1Test(AbstractTestCase):

    @testcase(priority=1, enabled=True, data_provider=get_testdatas, author='思文伟', name='两数加法测试01')
    def integer_addition_02(self, number_1, number_2, expected):
        result = number_1 + number_2
        self.assertEqual(result, expected)


if __name__ == '__main__':
    stest.main()
```

## 快速开始

1. 导入 `AbstractTestCase` 和 `Test` 装饰器
2. 编写继承自 `AbstractTestCase` 的测试类，使用 `@Test` 装饰器标记测试方法
3. 调用 `stest.main()` 或 `TestClassName.run_test()` 执行测试

`AbstractTestCase` 提供以下实用方法：

| 方法 | 说明 |
| :---- | :---- |
| `collect_testcases()` | 获取类下所有 `@Test` 装饰且 `enabled=True`，按 `priority` 排序后的用例列表 |
| `build_self_suite()` | 构建该类测试用例构成的测试套件 |
| `run_test()` | 执行该类所有 `@Test` 装饰且 `enabled=True`，按 `priority` 排序后的用例 |

### 简单示例

```python
#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from stest import AbstractTestCase
from stest import Test as testcase


def get_testdatas(test_class_name, test_method_name, *args, **kwargs):
    return [[1, 2, 3], [3, 4, 7]]


class Demo1Test(AbstractTestCase):

    @testcase(priority=1, enabled=True, data_provider=get_testdatas, author='思文伟', name='两数加法测试01')
    def integer_addition_02(self, number_1, number_2, expected):
        result = number_1 + number_2
        self.assertEqual(result, expected)


if __name__ == '__main__':
    Demo1Test.run_test()
```

### 综合示例

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
        return [
            {'加数1': 1, '加数2': 2, '预期': 3},
            {'加数1': 4, '加数2': 5, '预期': 9}
        ]


class DataProvider02(object):
    def get_testdatas(self, testclass, testmethod, *args, **kwargs):
        return [
            [{'加数1': 7}, {'加数2': 5}, {'预期': 12}],
            [{'加数1': 10}, {'加数2': 5}, {'预期': 15}]
        ]


TEST_DATA_FILE_DIRPATH = os.path.dirname(os.path.abspath(__file__))


class CalculationTest(AbstractTestCase):
    """数学运算测试"""

    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    @testcase(priority=1, enabled=True, data_provider=DataProvider01().get_testdatas, author='思文伟', name='整数加法测试01')
    def integer_addition_01(self, testdata):
        """自定义数据提供者 - 单参数化"""
        number_1 = testdata.get("加数1")
        number_2 = testdata.get("加数2")
        expected = testdata.get("预期")
        result = number_1 + number_2
        self.assertEqual(result, expected)

    @testcase(priority=2, enabled=True, data_provider=DataProvider02().get_testdatas, author='思文伟', name='整数加法测试02')
    def integer_addition_02(self, testdata_01, testdata_02, testdata_03):
        """自定义数据提供者 - 多参数化"""
        number_1 = testdata_01.get("加数1")
        number_2 = testdata_02.get("加数2")
        expected = testdata_03.get("预期")
        result = number_1 + number_2
        self.assertEqual(result, expected)

    @testcase(priority=3, enabled=True, author='思文伟', name='整数减法测试01')
    def integer_subtraction_01(self):
        """不参数化"""
        self.assertEqual(21 - 10, 11)

    @testcase(priority=4, enabled=True, author='思文伟', data_provider_kwargs={'data_file_dir_path': TEST_DATA_FILE_DIRPATH}, name='整数减法测试02')
    def integer_subtraction_02(self, testdata):
        """内置数据提供者 - 指定数据文件目录"""
        result = int(testdata.get("减数1")) - int(testdata.get("减数2"))
        self.assertEqual(result, int(testdata.get("预期")))

    @testcase(priority=5, enabled=True, author='思文伟', name='整数减法测试03')
    def integer_subtraction_03(self, testdata):
        """内置数据提供者 - 自动查找数据文件目录"""
        result = int(testdata.get("减数1")) - int(testdata.get("减数2"))
        self.assertEqual(result, int(testdata.get("预期")))

    def tearDown(self):
        pass

    @classmethod
    def tearDownClass(cls):
        pass


if __name__ == '__main__':
    CalculationTest.run_test()
```

## settings.py 配置文件

框架会自动查找并载入项目下的 `settings.py` 配置文件，通过 `from stest import settings` 导入配置对象，访问配置字段（字段必须大写，如 `settings.SCREENSHOT`）。

**查找规则：**

1. 通过命令行参数 `-sfile` 指定配置文件路径或查找起始目录
2. 若未指定，框架自动递归遍历项目目录（从用例所在目录往外推，第一个非 Python 包的目录即被认定为项目目录）及其子孙目录，查找 `settings.py`

### 框架配置字段

| 字段 | 描述 |
| :---- | :---- |
| `SCREENSHOT` | 控制测试失败后是否自动截图 |
| `ATTACH_SCREENSHOT_TO_REPORT` | 控制截图后是否附加到测试报告中（附加则转为 base64 嵌入报告） |
| `SCREENSHOT_SAVE_DIR` | 截图存放目录（预留字段） |
| `SEVEN_DATA_PROVIDER_DATA_FILE_DIR` | 内置数据提供者（SevenDataProvider）读取的测试数据文件目录。未设置则自动取测试用例所在模块目录 |
| `TEST_REPORT_DIR` | 测试报告存放目录。优先级：命令行参数 > 配置文件 > 模块目录 |
| `TEST_REPORT_NAME` | 测试报告名称。优先级：命令行参数 > 配置文件 > 模块名 > 任务名 > 测试开始时间 |
| `EXECUTOR` | 任务执行人，命令行未传入则取该设置 |
| `PROJECT_NAME` | 项目名称，命令行未传入则取该设置 |
| `DESCRIPTION` | 测试报告概要描述，命令行未传入则取该设置 |
| `DRIVER_MANAGER` | 驱动管理器，框架自动赋值，勿修改 |
| `TEST_PARAM_ALIAS` | `@Test` 参数别名字典，用于测试报告中参数显示名称映射 |
| `TEST_PARAM_NAME_FORMAT_STRING` | `@Test` 参数格式化字符串或函数。字符串可用变量：`{param}`（参数字段）、`{alias}`（参数别名）；函数接收字段名和别名两个参数，返回字符串 |
| `TEST_PARAM_VALUE_FORMATTER` | `@Test` 参数值格式化。字典（键为参数名，值为格式化函数）或统一格式化函数，函数接收参数名和参数值两个参数 |

### 配置文件示例

```python
# settings.py
import os
import html
from stest.report.html import elements

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

# 测试用例数据目录
SEVEN_DATA_PROVIDER_DATA_FILE_DIR = os.path.join(PROJECT_DIR, "testdata")

# 测试报告存放目录
TEST_REPORT_DIR = os.path.join(PROJECT_DIR, "report")

# 截图存放目录
SCREENSHOT_SAVE_DIR = os.path.join(PROJECT_DIR, "screenshot")

# 测试环境地址
WEB_URL = "https://tv.cctv.com/live/cctv13"

# 账号&密码
USER_NAME = "siwenwei"
USER_PWD = "123456"

# 参数名称格式化
TEST_PARAM_NAME_FORMAT_STRING = "{param} - {alias}"

# 参数别名映射
TEST_PARAM_ALIAS = {
    "priority": "优先级",
    "author": "编写者",
    "editors": "修改者",
    "last_modifyied_by": "最后修改者",
    "last_modified_time": "最近修改时间",
    "groups": "所属组",
    "related_testcases": "相关用例",
}


# 参数值格式化函数
def test_param_value_formatter(param, value):
    if isinstance(value, (list, tuple)):
        html_texts = []
        for one in value:
            text = one if isinstance(one, str) else str(one)
            html_texts.append(elements.P(html.escape(text, False)).to_html())
        return "".join(html_texts)
    else:
        return None


TEST_PARAM_VALUE_FORMATTER = dict(related_testcases=test_param_value_formatter)
```

![](https://github.com/hotswwkyo/stest/blob/main/img/test_param_format_01.png)

![](https://github.com/hotswwkyo/stest/blob/main/img/test_param_format_02.png)

### 项目目录结构示例

![](https://github.com/hotswwkyo/stest/blob/main/img/project_dirs.png)

## Test 装饰器参数说明

| 参数 | 类型 | 描述 |
| :---- | :---- | :---- |
| `name` | str | 测试用例名称。未传或为空则取方法 docstring 首行 |
| `dname` | str 或 list | 用于给用例起一个依赖名称，配合 `depends` 使用 |
| `depends` | list | 用例依赖列表。被依赖的用例不成功则当前用例不执行（除非 `alway_run=True`） |
| `groups` | list | 方法所属的组列表 |
| `enabled` | bool | 是否启用执行该测试方法 |
| `priority` | int | 执行优先级，数值越小越先执行 |
| `alway_run` | bool | 为 `True` 时无论依赖用例结果如何都始终运行，默认 `False` |
| `description` | str | 已弃用，原用于设置测试用例名称 |
| `data_provider` | object | 参数化数据提供者。`AbsractDataProvider` 子类或可调用对象，返回数据集列表（单参数化返回一维列表，多参数化返回二维列表） |
| `data_provider_args` | tuple | 数据提供者的变长位置参数 |
| `data_provider_kwargs` | dict | 数据提供者的变长关键字参数 |
| `screenshot` | bool | 控制该用例测试失败是否截图，优先级高于配置文件 |
| `attach_screenshot_to_report` | bool | 控制该用例失败截图是否附加到报告，优先级高于配置文件 |
| `enable_default_data_provider` | bool | 是否使用内置数据提供者（SevenDataProvider），默认 `True`。仅当 `data_provider=None` 且此值为 `True` 时生效 |

## 用例依赖设置

用例可依赖于其它用例成功后执行。若被依赖的用例不成功或未执行，则该用例会被标记为失败（除非设置了 `alway_run=True`）。

典型场景：添加和删除设备共用测试数据，删除用例依赖于添加用例成功后执行。

### 依赖引用格式

| 格式 | 说明 | 示例 |
| :---- | :---- | :---- |
| `模块名.py` | 依赖于指定模块中的所有用例 | `depends=['vnctest.py']` |
| `模块名.py.类名` | 依赖于指定模块中某个类的所有用例 | `depends=['vnctest.py.LoginTest']` |
| `模块名.py.类名.方法名` | 依赖于指定模块中某个类的某个用例 | `depends=['vnctest.py.LoginTest.login']` |
| `方法名` | 依赖于当前类的指定用例 | `depends=['dtest6']` |
| `dname值` | 依赖于当前类中通过 `dname` 命名的用例 | `depends=['four']` |

### 示例

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

    @testcase(priority=1, enabled=True, author='思文伟', name='dtest1', depends=['vnctest.py'])
    def dtest1(self):
        """依赖于 vnctest.py 模块中的所有用例"""
        pass

    @testcase(priority=2, enabled=True, author='思文伟', name='dtest2', depends=['vnctest.py.LoginTest'])
    def dtest2(self):
        """依赖于 vnctest.py 模块中 LoginTest 类的所有用例"""
        pass

    @testcase(priority=2, enabled=True, author='思文伟', name='dtest3', depends=['vnctest.py.LoginTest.login'])
    def dtest3(self):
        """依赖于 vnctest.py 模块中 LoginTest 类的 login 用例"""
        pass

    @testcase(priority=2, enabled=True, author='思文伟', name='dtest4', dname='four')
    def dtest4(self):
        """命名用例为 four，供其他用例通过 dname 引用"""
        pass

    @testcase(priority=2, enabled=True, author='思文伟', name='dtest5', depends=['dtest6'])
    def dtest5(self):
        """依赖于当前类的 dtest6 用例"""
        pass

    @testcase(priority=2, enabled=True, author='思文伟', name='dtest6', depends=['four'])
    def dtest6(self):
        """依赖于当前类中 dname='four' 的 dtest4 用例"""
        pass

    def tearDown(self):
        pass

    @classmethod
    def tearDownClass(cls):
        pass


if __name__ == '__main__':
    stest.main()
```

## 参数化数据提供者（Data Provider）

`@Test` 装饰器会调用数据提供者，传入测试类名称和方法名称作为前两个固定参数，`data_provider_args` 和 `data_provider_kwargs` 分别传给数据提供者的变长位置参数和关键字参数。

### 返回值规则

| 测试方法参数个数 | 数据提供者返回值 | 示例 |
| :---- | :---- | :---- |
| 单参数（如 `def test(self, testdata)`） | 一维字典列表 | `[{'name':'zhangsan','age':17}, {'name':'xiaoming','age':18}]` |
| 多参数（如 `def test(self, name, age)`） | 二维列表 | `[['zhangsan', 17], ['xiaoming', 18]]` |

### 内置数据提供者 - SevenDataProvider

使用 Excel（xlsx 或 xls 格式）存取和管理参数化测试数据，简洁直观，易于修改维护。

**启用条件：** `data_provider=None`（默认）且 `enable_default_data_provider=True`（默认）

#### 数据块格式

Excel 文件中以"数据块"方式存储测试数据：

- 所有行的**第一列**为标记列，第一行第一列为数据块开始标记（默认为"用例名称"）
- 第一行：用例名称信息（标记列的下一列为方法名称列，之后为用例名称列）
- 第二行：用例数据标题
- 第三行起：每一行为一组完整测试数据，直至空行或下一个数据块

![](https://github.com/hotswwkyo/stest/blob/main/img/testcase_data_excel_file.png)

#### 数据文件查找规则

| 配置方式 | 说明 |
| :---- | :---- |
| `data_provider_kwargs={'data_file_dir_path':'路径'}` | 通过 `@Test` 装饰器指定数据文件目录 |
| `settings.SEVEN_DATA_PROVIDER_DATA_FILE_DIR` | 在 `settings.py` 中配置全局数据文件目录 |
| 自动查找 | 以上均未设置，则取测试方法所在模块的目录 |

#### 数据文件名规则

| 配置方式 | 说明 |
| :---- | :---- |
| `data_provider_kwargs={'data_file_name':'mytest'}` | 通过 `@Test` 装饰器指定数据文件名 |
| 自动取类名 | 以上未设置，则取测试类名作为数据文件名 |

#### 其他参数

| 参数 | 说明 |
| :---- | :---- |
| `data_provider_kwargs={'sheet_name_or_index': 0}` | 指定 Excel 工作表索引（从 0 开始）或名称，默认取索引 0 |

#### 示例

```python
#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from stest import AbstractTestCase
from stest import Test as testcase


class CalculationTest(AbstractTestCase):

    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    @testcase(priority=4, enabled=True, author='思文伟',
              data_provider_kwargs={'data_file_dir_path': 'E:\\alltest'},
              name='整数减法测试02')
    def integer_subtraction_02(self, testdata):
        """内置数据提供者 - 指定数据文件目录"""
        number_1 = testdata.get("减数1")
        number_2 = testdata.get("减数2")
        expected = testdata.get("预期")
        result = int(number_1) - int(number_2)
        self.assertEqual(result, int(expected))

    @testcase(priority=5, enabled=True, author='思文伟', name='整数减法测试03')
    def integer_subtraction_03(self, testdata):
        """内置数据提供者 - 自动查找数据文件目录"""
        number_1 = testdata.get("减数1")
        number_2 = testdata.get("减数2")
        expected = testdata.get("预期")
        result = int(number_1) - int(number_2)
        self.assertEqual(result, int(expected))
```

### 自定义数据提供者

自定义数据提供者可以是 `AbsractDataProvider` 的子类或任何可调用对象，必须接收以下参数：

```
get_testdatas(test_class_name, test_method_name, *args, **kwargs)
```

#### 实现方式

1. **继承 `AbsractDataProvider`**：实现 `get_testdatas(self, test_class_name, test_method_name, *args, **kwargs)` 方法
2. **可调用对象**：任何接收上述参数签名的函数或方法

#### 示例

**继承 `AbsractDataProvider` 的数据提供者：**

```python
#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author: 思文伟
'''
from stest import AbstractTestCase
from stest import Test as testcase
from stest.abstract_data_provider import AbsractDataProvider


class SevenDataProvider(AbsractDataProvider):
    """示例：内置 SevenDataProvider 的简化版"""

    def get_testdatas(self, test_class_name, test_method_name, *args, **kwargs):
        # 从 Excel 文件读取数据的逻辑
        return [{"减数1": "36", "减数2": "10", "预期": "26"}]


class CalculationTest(AbstractTestCase):

    @testcase(priority=1, enabled=True,
              data_provider=SevenDataProvider,
              data_provider_kwargs={'data_file_dir_path': 'E:\\mytestdatas'},
              author='思文伟', name='整数加法测试01')
    def integer_addition_01(self, testdata):
        number_1 = testdata.get("加数1")
        number_2 = testdata.get("加数2")
        expected = testdata.get("预期")
        result = number_1 + number_2
        self.assertEqual(result, expected)
```

**普通类的数据提供者：**

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
        return [[1, 2, 3], [3, 4, 7]]


class Demo1Test(AbstractTestCase):

    @testcase(priority=1, enabled=True,
              data_provider=Demo1DataProvider().get_testdatas,
              author='思文伟', name='两数加法测试01')
    def integer_addition_02(self, number_1, number_2, expected):
        result = number_1 + number_2
        self.assertEqual(result, expected)
```

**函数数据提供者：**

```python
#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author: 思文伟
'''
from stest import AbstractTestCase
from stest import Test as testcase


def get_testdatas(test_class_name, test_method_name, *args, **kwargs):
    return [[1, 2, 3], [3, 4, 7]]


class Demo1Test(AbstractTestCase):

    @testcase(priority=1, enabled=True,
              data_provider=get_testdatas,
              author='思文伟', name='两数加法测试01')
    def integer_addition_02(self, number_1, number_2, expected):
        result = number_1 + number_2
        self.assertEqual(result, expected)
```

## 钩子(hook)

钩子机制允许在测试执行的关键节点（运行阶段）插入自定义逻辑，实现测试生命周期的扩展。

### 核心概念

- **钩子（Hook）**：通过 `hook.wrapper` 装饰器定义的函数，在指定运行阶段自动执行
- **宿主函数（Host Function）**：被钩子挂载的函数，通过 `hook.host` 装饰器标记。宿主函数执行时，框架会根据运行策略自动触发挂载的钩子
- **运行阶段（RunStage）**：钩子触发的时机，对应 `SevenTestResult` 的各个生命周期方法
- **运行策略（RunPolicy）**：钩子相对于宿主函数的执行时机

### 运行策略

| 策略 | 值 | 说明 |
| :---- | :---- | :---- |
| `RunPolicy.BEFORE` | 1 | 在宿主函数执行**之前**运行钩子 |
| `RunPolicy.AFTER` | 2 | 在宿主函数执行**之后**运行钩子 |

### 内置运行阶段

框架内置以下运行阶段，对应 `SevenTestResult` 的同名方法：

| 运行阶段 | 说明 | 钩子函数参数（第一个参数始终为 `settings`） |
| :---- | :---- | :---- |
| `RunStage.startTestRun` | 所有测试开始执行前 | `(settings, result)` |
| `RunStage.startTest` | 单个测试开始执行前 | `(settings, test)` |
| `RunStage.stopTest` | 单个测试执行完成后 | `(settings, test)` |
| `RunStage.stopTestRun` | 所有测试执行完成后 | `(settings, result)` |
| `RunStage.addSuccess` | 测试成功时 | `(settings, test)` |
| `RunStage.addError` | 测试发生错误时 | `(settings, test, err)` |
| `RunStage.addFailure` | 测试断言失败时 | `(settings, test, err)` |
| `RunStage.addSkip` | 测试被跳过时 | `(settings, test, reason)` |
| `RunStage.addExpectedFailure` | 预期失败发生时 | `(settings, test, err)` |
| `RunStage.addUnexpectedSuccess` | 预期失败但意外成功时 | `(settings, test)` |

### 定义钩子

使用 `hook.wrapper` 装饰器定义钩子：

```python
hook.wrapper(runstage, *, runpolicy=RunPolicy.BEFORE, priority=49, name=None, options={})
```

| 参数 | 说明 |
| :---- | :---- |
| `runstage` | 钩子运行阶段，指定钩子在哪个生命周期节点触发 |
| `runpolicy` | 运行策略，`RunPolicy.BEFORE`（宿主函数之前）或 `RunPolicy.AFTER`（宿主函数之后），默认 `BEFORE` |
| `priority` | 运行优先级，数值越小越先执行，默认 49 |
| `name` | 钩子名称，默认取函数名 |
| `options` | 钩子额外属性字典 |

**钩子函数签名规则：**

1. 第一个参数必须为全局配置对象 `settings`
2. 其余参数与对应运行阶段的宿主函数参数一一对应（见上方参数表）
3. 框架会在注册时自动校验参数签名是否匹配，不匹配会抛出 `TypeError`

### 标记宿主函数

使用 `hook.host` 装饰器标记宿主函数，框架会在宿主函数执行前后自动触发对应阶段的钩子：

```python
hook.host(runstage, **options)
```

`options` 支持以下参数，用于控制钩子的排序和过滤：

| 键 | 作用范围 | 说明 |
| :---- | :---- | :---- |
| `before` | `RunPolicy.BEFORE` 的钩子 | 字典，支持 `sort_key`、`sort_reverse`、`filter_func` |
| `after` | `RunPolicy.AFTER` 的钩子 | 字典，支持 `sort_key`、`sort_reverse`、`filter_func` |

> **注意**：框架内置的 `SevenTestResult` 方法已通过 `@host` 装饰器标记，无需手动标记。用户只需通过 `@hook.wrapper` 定义钩子即可。

### 自定义运行阶段

可通过 `RunStage.newstage()` 扩展自定义运行阶段：

```python
from stest import hook

hook.RunStage.newstage("myCustomStage", 100, mark="自定义阶段描述")
```

### 示例

**在测试运行前后启动和停止 Playwright：**

```python
import stest
from stest import hook
from playwright.sync_api import sync_playwright

@hook.wrapper(hook.RunStage.startTestRun)
def startTestRun(conf: stest.settings, result):
    """所有测试开始前，启动 Playwright"""
    conf.playwright = sync_playwright().start()

@hook.wrapper(hook.RunStage.stopTestRun, runpolicy=hook.RunPolicy.AFTER)
def stopTestRun(conf: stest.settings, result):
    """所有测试结束后，停止 Playwright"""
    playwright = getattr(conf, 'playwright', None)
    if playwright is not None:
        playwright.stop()
```

**在单个测试开始前打印日志：**

```python
@hook.wrapper(hook.RunStage.startTest, priority=10)
def before_each_test(conf: stest.settings, test):
    """每个测试开始前打印用例名称"""
    print(f"开始执行: {test}")
```

**在测试失败时记录额外信息：**

```python
@hook.wrapper(hook.RunStage.addFailure)
def on_failure(conf: stest.settings, test, err):
    """测试断言失败时记录错误信息"""
    print(f"测试失败: {test}, 错误: {err}")
```


## 表格定位器(Table Locator)

基于 Playwright 的表格通用定位器，采用**"由列定表"**的设计理念：只需提供关心的列标题或列索引，即可自动生成高精度 XPath，精准定位目标表格，并提供行查找与数据提取能力。

### 核心能力

- **结构化定位**：按列标题、列索引或混合字典配置表格结构，自动生成高精度 XPath
- **智能检测与修复**：通过 `sync_from_dom` 方法根据 DOM 检测结果同步或重建内部列配置
- **多级表头支持**：自动解析 `colspan`/`rowspan`，将多行表头合并为扁平化的列标题
- **便捷数据提取**：提供 `row()`、`cells()`、`cell()` 等链式 API

### 快速使用

```python
from stest.testobjs.useful.table_locator import Table

# 1. 创建 Table 实例 —— 传入列标题
table = Table(page, '序号', '专资编码', '影城名称', '营业状态', '操作')

# 2. 标记非数据列（提取数据时自动忽略）
table.mark_non_data_columns_by_titles('操作', '序号')

# 3. 按内容查找行
row_el = table.row({"专资编码": "80002048"}, el_type="row")

# 4. 提取行数据
data = table.cells(row_el)
# => {'专资编码': '80002048', '影城名称': '影院名称-80002048', '营业状态': '开业'}

# 5. 遍历所有行
for row in table.all_rows.all():
    row_data = table.cells(row)
    print(row_data)
```

### 初始化配置

`Table` 的 `config` 参数支持多种类型（同一批次不可混用）：

| 配置类型 | 示例 | 说明 |
| :---- | :---- | :---- |
| 字符串（列标题） | `Table(page, '姓名', '年龄')` | 最常用，`auto_set_position=True` 时标题顺序须与 DOM 一致 |
| 整数（列索引） | `Table(page, 2, 5, auto_set_position=False)` | 适用于无标题或动态标题的表格 |
| 字典 | `Table(page, {"index":1,"title":"姓名"}, {"index":2,"title":"年龄"})` | 精细控制，支持 `xpath`/`value`/`tagname` |
| 列表/元组 | `Table(page, (1,'姓名'), (2,'年龄','div[@class="cell"]'))` | 按位置传参，2~5个元素 |

**`auto_set_position` 参数说明：**

| 值 | 适用场景 |
| :---- | :---- |
| `True`（默认） | 列顺序固定且已知，传入标题顺序须与 DOM 一致 |
| `False` | 只关心列是否存在，不关心顺序；后续需配合 `sync_from_dom` 或 `allow_missing_position=True` |

### 关键方法

| 方法 | 说明 | 示例 |
| :---- | :---- | :---- |
| `row(cells, by, **settings)` | 按内容查找行或单元格 | `table.row({"专资编码": "80002048"}, el_type="row")` |
| `cells(row, return_locator, title_as_key)` | 提取行数据（自动排除非数据列） | `table.cells(row_el)` |
| `cell(row, title_or_position, by)` | 获取单个单元格 | `table.cell(row_el, "营业状态")` |
| `sibling_cell(cell, target, by)` | 获取同行兄弟单元格 | `table.sibling_cell(code_cell, "营业状态")` |
| `header_cells(title, position, row)` | 获取表头单元格 | `table.header_cells(title='姓名', row=1)` |
| `mark_non_data_columns_by_titles(*titles)` | 按标题标记非数据列 | `table.mark_non_data_columns_by_titles('操作')` |
| `mark_non_data_columns_by_position(*positions)` | 按索引标记非数据列 | `table.mark_non_data_columns_by_position(1, 5)` |
| `set_body_cell_xpath(cxpath, *titles)` | 设置指定主体列的内部元素路径 | `table.set_body_cell_xpath('div[@class="action-btns"]', '操作')` |
| `detect_header_titles()` | 自动检测表头信息（含多级表头） | `table.detect_header_titles()` |
| `sync_from_dom(mode, by, sep)` | 从 DOM 同步/重建列配置 | `table.sync_from_dom(mode="rebuild")` |

### 固定列表格示例（Element UI）

Element UI 固定列会将表格拆分为多个独立的 `<table>` DOM 节点，需修改默认 XPath：

```python
from stest.testobjs.useful.table_locator import Table

titles = ['序号', '专资编码', '影城名称', '院线', '影投', '营业状态',
          '终端绑定状态', '终端安装状态', '操作']

right_table = Table(page, *titles)

# 覆盖默认 XPath，指向固定列所在的 DOM 节点
right_table.default_head_xpath = (
    '//div[@class="el-table__fixed-right"]'
    '/div[contains(@class,"el-table__fixed-header-wrapper")]'
    '/table/thead'
)
right_table.default_body_xpath = (
    './ancestor::table/parent::div'
    '/following-sibling::div[contains(@class,"el-table__fixed-body-wrapper")]'
    '/table/tbody'
)

right_table.mark_non_data_columns_by_titles('操作')

# 正常使用
row_el = right_table.row({"专资编码": "80002048"}, el_type="row")
data = right_table.cells(row_el)
```

### 关键点

- **`default_head_xpath` 与 `default_body_xpath`**：默认针对 Element UI 标准表格设计。固定列场景必须修改；标准 HTML 表格（thead 与 tbody 在同一 `<table>` 内）可将 `default_body_xpath` 简化为 `./tbody`
- **`allow_missing_position`**：当 `auto_set_position=False` 时列索引为 `None`，生成的 XPath 可能模糊。建议调用 `sync_from_dom()` 自动填充索引，而非设置 `allow_missing_position = True`
- **`cxpaths_for_rebuild`**：`sync_from_dom` 重建时会丢失 `cxpath`，此属性充当"记忆层"确保重建后路径不丢失
- **重复标题**：`by="title"` 仅匹配第一个出现的列，建议改用 `by="position"`
- **XPath 注入**：`row()` 的 `cells` 参数值会直接嵌入 XPath，注意特殊字符转义

> 详细教程请参考源码包下的 `stest/testobjs/useful/table_locator_tutorial.md`

## Page object 实现方案

框架内置三种抽象页面基类，分别对应不同的自动化测试工具，均遵循**"元素与动作分离"**的设计模式：

| 抽象基类 | 适用场景 | 驱动技术 | 类属性 |
| :---- | :---- | :---- | :---- |
| `AbstractPage` | Web页面、APP页面、Windows桌面应用 | Selenium / Appium / WinAppDriver | `DRIVER_MANAGER`、`WIN_APP_DRIVER_HELPER` |
| `AbstractPlaywrightPage` | Web页面 | Playwright | `DRIVER_MANAGER` |
| `AbstractMiniumPage` | 微信小程序 | minium | `WECHAT_MANAGER` |

### 设计模式

所有抽象基类遵循统一的页面封装规范：

1. **页面类**继承对应的抽象基类，可覆写 `init()` 方法执行自定义初始化逻辑
2. **内部类 `Elements`**（继承基类的 `Elements`）：封装页面元素定位，通过 `@property` 暴露元素访问接口
3. **内部类 `Actions`**（继承基类的 `Actions`）：封装页面操作动作，通过 `self.page.elements` 访问元素，所有动作方法返回 `self` 以支持链式调用
4. 页面实例化时自动构建 `Elements` 和 `Actions` 实例，分别赋给 `self.elements` 和 `self.actions`

### AbstractPage（Selenium / Appium / WinAppDriver）

**核心能力：**

- **多驱动支持**：通过 `DRIVER_MANAGER` 统一管理 Selenium、Appium、WinAppDriver 驱动会话，支持多驱动实例切换
- **丰富的元素查找**：提供 `find_element_by_id`、`find_element_by_xpath`、`find_element_by_android_uiautomator`、`find_element_by_accessibility_id` 等 20+ 种定位方法，支持超时等待
- **浏览器管理**：`chrome()`、`firefox()`、`ie()` 快捷打开浏览器；`maximize_window()`、`set_window_size()` 管理窗口
- **APP 会话**：`open_app()` 创建 Appium 会话；`hide_keyboard()`、`keyevent()` 处理移动端特有操作
- **Windows 应用**：`open_window_app()` 创建 WinAppDriver 会话；`switch_window_app_by_name()` 切换应用窗口；`WIN_APP_DRIVER_HELPER` 管理驱动启停
- **窗口与 Frame**：`switch_window_by_title()`、`switch_window_by_url()` 切换窗口；`select_frame()`、`default_frame()`、`parent_frame()` 切换 Frame
- **滚动操作**：`scroll_to()`、`scroll_to_top()`、`scroll_to_bottom()`、`scroll_to_center()`、`scroll_into_view()`
- **截图与报告**：`screenshot()` 保存截图；`show2html()` 截图并附加到 HTML 测试报告
- **XPath 拼接**：`join_xpaths()` 静态方法，便捷拼接多段 XPath

**驱动创建方式：**

```python
# 方式1：实例化后调用浏览器方法（推荐）
page = LoginPage().chrome(url="https://example.com")

# 方式2：实例化时传入驱动名称
page = LoginPage("chrome", url="https://example.com")

# 方式3：APP 会话
page = LoginPage().open_app(remote_url, desired_capabilities=caps)

# 方式4：Windows 应用
page = LoginPage().open_window_app(remote_url, desired_capabilities=caps)
```

### AbstractPlaywrightPage（Playwright）

**核心能力：**

- **多浏览器支持**：`chrome()`、`chromium()`、`firfox()`、`msedge()`、`webkit()`（别名 `safari()`）快捷打开浏览器，支持 `browser_launch_args` 和 `browser_context_args` 自定义启动参数
- **Playwright 原生 Page 访问**：`pwpage` 属性直接获取底层 Playwright `Page` 实例，可调用 Playwright 原生 API（如 `pwpage.get_by_role()`、`pwpage.wait_for_selector()` 等），适用于框架未封装的 Playwright 能力
- **Playwright 原生定位**：`get_by_xpath()`、`get_by_id()`、`get_by_text()`、`get_by_alt_text()`、`get_by_title()`、`get_by_placeholder()`、`locator()`、`frame_locator()` 等，完整封装 Playwright 的定位能力
- **页面导航**：`open_url()`、`goto()`、`reload()`、`content()`、`new_page()`
- **多页面管理**：`switch2page()` 切换到指定 Page；`switch_to_default_page()` 回到默认页面；`get_playwright_pages_by_title()`、`get_playwright_pages_by_url()` 按标题/URL 查找页面
- **Frame 操作**：`frame()`、`main_frame`、`frames`
- **滚动操作**：`scroll_to()`、`scroll_to_top()`、`scroll_to_bottom()`、`scroll_to_center()`、`scroll_into_view()`
- **视口管理**：`set_viewport_size()`、`viewport_size()`
- **截图与报告**：`screenshot()` 保存截图；`show2html()` 截图并附加到 HTML 测试报告
- **XPath 拼接**：`join_xpaths()` 类方法，便捷拼接多段 XPath
- **自动清理**：支持配置 `PlaywrightDriver.AUTO_STOP_PLAYWRIGHT`，测试运行结束后自动停止 Playwright 进程

**驱动创建方式：**

```python
# 方式1：实例化后调用浏览器方法（推荐）
page = LoginPage().chrome()

# 方式2：实例化时传入浏览器类型
page = LoginPage("chromium", browser_launch_args=dict(channel="chrome"))

# 方式3：指定启动参数
page = LoginPage().chrome(browser_launch_args=dict(channel="chrome"))
```

**IDE 类型提示：**

由于 `Elements` 和 `Actions` 通过反射自动构建，IDE 无法自动推断类型。可通过覆写 `_build_elements()` 和 `_build_actions()` 方法，使用 `typing.cast()` 解决：

```python
import typing

class LoginPage(AbstractPlaywrightPage):

    def _build_elements(self):
        rv = super()._build_elements()
        self.elements = typing.cast(LoginPage.Elements, self.elements)
        return rv

    def _build_actions(self):
        rv = super()._build_actions()
        self.actions = typing.cast(LoginPage.Actions, self.actions)
        return rv
```

### AbstractMiniumPage（微信小程序）

**核心能力：**

- **minium 集成**：自动初始化 minium 实例，通过 `self.mini`、`self.native`、`self.app` 访问 minium 原生能力
- **页面导航**：实例化时传入 `url` 参数自动跳转到指定小程序页面
- **元素查找**：`get_element()`、`get_elements()` 封装 minium 的元素查找，支持 `inner_text`、`text_contains`、`value` 等筛选条件
- **当前页面**：`current_page` 属性获取当前小程序页面实例

**初始化方式：**

```python
# 传入小程序页面路径和 minium 配置
page = IndexPage('/pages/index/index', minium_config={
    "platform": "ide",
    "debug_mode": "info",
    "close_ide": False,
    ...
})
```

### 公共约定

- **链式调用**：`Actions` 中的方法返回 `self`，支持链式操作：`page.actions.username(name).password(pwd).login()`
- **延时等待**：页面和 Elements/Actions 均提供 `sleep(seconds)` 方法
- **翻页接口**：`Actions.turn_to_page(page_number)` 由具体页面实现
- **驱动管理**：所有页面通过 `DRIVER_MANAGER`（或 `WECHAT_MANAGER`）统一管理驱动生命周期，支持多实例、别名切换

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

    @testcase(priority=1, enabled=True, screenshot=True, author='思文伟', name='用正确账号密码登录测试')
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

    @testcase(priority=1, enabled=True, screenshot=True, author='思文伟', name='成功登录测试')
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

    @testcase(priority=1, enabled=True, author='思文伟', name='广告投放界面->广告视频显示的正确性 - 影院列表>加入广告栏')
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
| name | version |
| :---- | :---- |
| selenium | 3.141.0 |
| Appium-Python-Client | 0.48 |
| WinAppDriver | 1.2.200902003-release |
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

    @testcase(priority=1, enabled=True, screenshot=True, author='思文伟', name='用正确账号密码登录测试')
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
import typing
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
