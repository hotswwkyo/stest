#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author: 思文伟
@Date: 2021/09/23
'''
import inspect
import collections
from ..utils.attrs_manager import AttributeManager
from ..utils.attrs_marker import Const


class TestCaseWrapper(AttributeManager):

    SEP = Const(".", "id分隔符")
    SN = Const("serial_number", "AbstractTestCase的子类会有个用例序列号属性serial_number，用来实现参数化的")
    SN_PREFIX = Const("_", "serial_number分隔符")
    PY = Const(".py", "Python 模块文件拓展名")
    SETTINGS_KEY = Const("test_method_settings", "测试方法存储设置项的属性名")
    DEPENDS_KEY = Const("depends", "测试方法设置项中设置依赖的键名")
    DNAME_KEY = Const("dname", "测试方法设置命名用于依赖的键名")

    def __init__(self, testcase):

        self._testcase = testcase
        self._testsettings = getattr(self._testcase, self.SETTINGS_KEY, {})
        self._serial_number = getattr(self._testcase, self.SN, None)
        self._init()
        self._parse()

    def _init(self):

        self._new_id = None

        self._module = None
        self._module_file = None
        self._module_real_name = None

        self._module_scope = None
        self._class_scope = None
        self._module_file_name = None

    @property
    def testcase(self):

        return self._testcase

    def id(self):
        """测试用例原id"""

        return self.testcase.id()

    @property
    def serial_number(self):

        return self._serial_number

    @property
    def settings(self):

        return self._testsettings

    @property
    def dnames(self):
        """用来设置依赖的命名"""

        name = self._testsettings.get(self.DNAME_KEY, '')
        if name and isinstance(name, str):
            return [name]
        return name

    @property
    def depends(self):

        return self.settings.get(self.DEPENDS_KEY, [])

    @property
    def module_scope(self):
        """生成的新的测试用例id中模块部分完整域名 test_module.py"""

        return self._module_scope

    @property
    def class_scope(self):
        """生成的新的测试用例id中类部分的完整域名:  test_module.py.TestClass"""

        return self._class_scope

    @property
    def new_id(self):
        """将测试用例原始ID转换为具有模块扩展名的新ID（convert test case original ID  to new ID with module extend name）,如果是用例是AbstractTestCase子类的实例，还会移除id末尾序列号

        原来的ID大体由3部分构成: 模块名.类.测试方法名，新的为 模块文件名.类.测试方法名

        test_module.TestClass.test --> test_module.py.TestClass.test
        """

        return self._new_id

    @property
    def module_real_name(self):
        """测试用例所在的模块名称（不含文件拓展名）"""

        return self._module_real_name

    @property
    def module_file_name(self):
        """测试用例所在的模块文件名，如果找不到模块的实际名称则返回测试用例id中模块名部分,
        id中的模块名部分是调用类的__module__来获取的，则有可能为__main__
        """

        return self._module_file_name

    def _parse(self):

        self._module = inspect.getmodule(self.testcase)
        self._module_file = inspect.getabsfile(self._module)
        self._module_real_name = inspect.getmodulename(self._module_file)

        parts = self.id().split(self.SEP)
        if len(parts) < 3:
            raise ValueError('Invalid Test Case ID: {}'.format(self.id()))
        original_module = parts[0]
        original_clazz = self.SEP.join(parts[1:-1])
        original_testname = parts[-1]

        module_name = self._module_real_name if self._module_real_name else original_module
        self._module_file_name = module_name + self.PY

        self._module_scope = self._module_file_name
        self._class_scope = self.SEP.join([self._module_file_name, original_clazz])
        self._new_id = self.SEP.join([self._module_file_name, original_clazz, original_testname])

        # 如果是用例是AbstractTestCase子类的实例，则移除序列号
        if self.serial_number is not None:
            self._new_id = self._new_id.rsplit(self.SN_PREFIX, 1)[0]

    @classmethod
    def get_absolute_testcase_id(cls, testcase_id, scope):
        """
        Transform a possibly relative test case id to an absolute one using the scope in which it is used.

        >>> scope = 'test_module.py.TestClass.test'
        >>> get_absolute_nodeid('test2', scope)
        'test_module.py.TestClass.test2'
        >>> get_absolute_nodeid('TestClass2.test2', scope)
        'test_module.py.TestClass2.test2'
        >>> get_absolute_nodeid('test_module2.py.TestClass2.test2', scope)
        'test_module2.py.TestClass2.test2'
        """

        tid = testcase_id
        parts = tid.split(cls.SEP)
        id_len = len(parts)
        # Completely relative (test_name), so add the full current scope
        if id_len == 1:
            base_tid = scope.rsplit(cls.SEP, 1)[0]
            tid = cls.SEP.join([base_tid, tid])
        # Contains some scope already (TestClass::test_name), so only add the current file scope
        elif id_len == 2 and '{}{}'.format(cls.SEP, parts[-1]) != cls.PY:
            base_tid = cls.SEP.join(scope.split(cls.SEP)[0:2])
            tid = cls.SEP.join([base_tid, tid])
        return tid

    def get_names(self):
        """
        Get all names for a test.

        This will use the following methods to determine the name of the test:
            - If given, the custom name(s) passed to the keyword argument name on test case settings
            - The full id of the test case
            - All 'scope' parts of the test case id. For example, for a test test_file.py.TestClass.test, this would be
            test_file.py and test_file.py.TestClass
        """

        names = set()

        # test case id
        names.add(self.new_id)

        # 用例所属的域名
        scopes = [self.module_scope, self.class_scope]
        for scope in scopes:
            names.add(scope)

        # Custom name
        for name in self.dnames:
            names.add(name)

        return names


class TestResultFinder(AttributeManager):

    UNRUN_CODE = Const(0, "未运行", alias="未运行")
    PASS_CODE = Const(1, "通过", alias="通过")
    FAIL_CODE = Const(2, "失败", alias="失败")
    ERROR_CODE = Const(3, "异常", alias="异常")

    @classmethod
    def find_test_result(cls, test, results):

        # find pass test case
        for ptest in results.successes:
            if test.id() == ptest.id():
                return (cls.PASS_CODE, cls.get_result_name(cls.PASS_CODE), '')
        for ptest, message in results.expectedFailures:
            if test.id() == ptest.id():
                return (cls.PASS_CODE, cls.get_result_name(cls.PASS_CODE), message)

        # find fail test case
        for ftest, message in results.failures:
            if test.id() == ftest.id():
                return (cls.FAIL_CODE, cls.get_result_name(cls.FAIL_CODE), message)
        for ftest in results.unexpectedSuccesses:
            if test.id() == ftest.id():
                return (cls.FAIL_CODE, cls.get_result_name(cls.FAIL_CODE), '')

        for etest, message in results.errors:
            if test.id() == etest.id():
                return (cls.ERROR_CODE, cls.get_result_name(cls.ERROR_CODE), message)
        return (cls.UNRUN_CODE, cls.get_result_name(cls.UNRUN_CODE), '')

    @classmethod
    def is_pass(cls, result_code):

        return result_code == cls.PASS_CODE

    @classmethod
    def get_result_name(cls, result_code):

        markers = cls.const_attrs.values()
        for marker in markers:
            code = marker.value
            if result_code == code:
                return marker.expend_kwargs["alias"]

    @classmethod
    def result_codes(cls):
        markers = cls.const_attrs.values()
        codes = [marker.value for marker in markers]
        return codes

    @classmethod
    def is_test_pass(cls, test, results):

        cval, cname, m = cls.find_test_result(test, results)
        return cls.PASS_CODE == cval


class TestDepends(object):
    """ Information about the resolved dependencies of a single test """

    def __init__(self, testcase_wrapper, manager):

        self.testid = testcase_wrapper.id()
        self.depends = set()
        self.unresolved = set()

        for depend in testcase_wrapper.depends:
            if depend not in manager.name_to_testids:
                absolute_depend = testcase_wrapper.get_absolute_testcase_id(
                    depend, testcase_wrapper.new_id)
                if absolute_depend in manager.name_to_testids:
                    depend = absolute_depend

            if depend in manager.name_to_testids:
                for testid in manager.name_to_testids[depend]:
                    self.depends.add(testid)
            else:
                self.unresolved.add(depend)


class DependsManager(object):
    def __init__(self):

        self._tests = None
        self._results = None
        self._name_to_testids = None
        self._testid_to_test = None
        self._weights = {}
        self._links = {}
        self._cyclic_links = {}

    @property
    def tests(self):

        if self._tests is None:
            raise AttributeError('The tests attribute has not been set yet')
        return self._tests

    @tests.setter
    def tests(self, testcases):

        if self._tests is not None:
            raise AttributeError('The tests attribute has already been set')
        self._tests = testcases

        self._depends = {}
        self._testid_to_test = {}
        self._name_to_testids = collections.defaultdict(list)

        tc_wrappers = [TestCaseWrapper(tc) for tc in testcases]

        for tc in tc_wrappers:
            self._testid_to_test[tc.id()] = tc.testcase
            for name in tc.get_names():
                self._name_to_testids[name].append(tc.id())

        # Don't allow using unknown keys on the name_to_testids mapping
        self._name_to_testids.default_factory = None

        for tc in tc_wrappers:
            self._depends[tc.id()] = TestDepends(tc, self)

        for tc in tc_wrappers:
            weight, links, cyclic_links = self.calc_weight_and_link(tc.id())
            self._weights[tc.id()] = weight
            self._links[tc.id()] = links
            self._cyclic_links[tc.id()] = cyclic_links

    def calc_weight_and_link(self, testcase_id):
        """ 计算用例的依赖权重和他所依赖的用例（包括直接和间接依赖），同时检查是否存在循环依赖

        Args:
            testcase_id: 测试用例id

        Returns: 返回3个元素的元祖，第一个是权重，第二个是所依赖的用例id列表，第三个是循环依赖的用例id列表

        Useage:
            t1 -> t2 -> t3    t1 -> t2 ->t4 ->t5

            self.calc_weight_and_link(t1.id)

            >>> (4, [[t2.id, t3.id],[t2.id, t4.id, t5.id]], [])

            t1 -> t2 -> t3    t1 -> t2 ->t4 ->t1

            self.calc_weight_and_link(t1.id)

            >>> (4, [[t2.id, t3.id],[t2.id, t4.id]], [[t1.id, t2.id, t4.id, t1.id]])
        """

        count = 0
        cyclic_links = []

        def _calc_weight_and_link(testid, link_recorder=[]):

            weight = 0
            links = []
            nonlocal count
            nonlocal cyclic_links
            depends_info = self.depends.get(testid, None)
            count = count + 1
            link_recorder.append(testid)

            if depends_info is not None:
                know_depends = depends_info.depends
                unknow_depends = depends_info.unresolved
                kcounts = len(know_depends)
                ucounts = len(unknow_depends)
                weight = weight + kcounts + ucounts
                if kcounts > 0:
                    for test_id in know_depends:
                        if test_id in link_recorder:  # 说明当前依赖关系链路已造成循环依赖
                            cyclic_link = [c for c in link_recorder]
                            cyclic_link.append(test_id)
                            cyclic_links.append(cyclic_link)
                            link_recorder.pop()  # 依赖链路死循环，获取父级链路，以便记录其他兄弟节点的链路

                            # continue # 原码 为了获取所有的循环链，但多参数化传入多条数据进行数据驱动测试，设置循环依赖会导致代码死循环，无法获取循环链 2021-09-29 注释 by 思文伟
                            break  # 由continue 改为break  2021-09-29 注释 by 思文伟

                        sub_weight, sub_links = _calc_weight_and_link(test_id, link_recorder)
                        weight = weight + sub_weight
                        link = []
                        if sub_links:
                            for slink in sub_links:
                                onelink = [test_id]
                                onelink.extend(slink)
                                link.append(onelink)
                        else:
                            link.append([test_id])

                            # 依赖链路已经结束，获取父级链路，以便记录其他兄弟节点的链路
                            if link_recorder[-1] == test_id:
                                link_recorder.pop()
                        if link:
                            links.extend(link)
            return (weight, links)

        r = _calc_weight_and_link(testcase_id)
        return (r[0], r[1], cyclic_links)

    @property
    def name_to_testids(self):
        """ A mapping from names to matching test case id(s). """
        assert self.tests is not None
        return self._name_to_testids

    @property
    def testid_to_test(self):
        """ A mapping from node ids to test cases. """

        assert self.tests is not None
        return self._testid_to_test

    def sorted_tests(self, suiteclass=None):
        """ Get a sorted list of tests where all tests are sorted after their dependencies. """

        ztests = [test for test in self.tests if self.weights[test.id()] == 0]
        dtests = [test for test in self.tests if self.weights[test.id()] > 0]
        dtests.sort(key=lambda test: self.weights[test.id()])

        tests = []
        tests.extend(ztests)
        tests.extend(dtests)
        if suiteclass is not None:
            tests = suiteclass(tests)
        return tests

    @property
    def results(self):

        if self._results is None:
            raise AttributeError('The results attribute has not been set yet')
        return self._results

    @results.setter
    def results(self, value):

        self._results = value

    def get_depend_tests(self, test):
        """ 获取测试用例所依赖的其它用例"""

        dtests = []
        test_depend = self.depends[test.id()]
        for dtestid in test_depend.depends:
            dtests.append(self.testid_to_test[dtestid])
        return dtests

    def dependent_test_is_pass(self, test, results=None):
        """ 检查测试用例所依赖的其他测试用例是否测试通过，只要有一个不通过则返回False，否则为True，同时返回失败的详情信息列表"""

        is_pass = True
        sep = '------->'
        fail_details = []
        results = results or self.results
        finder = TestResultFinder()
        for dtest in self.get_depend_tests(test):
            codevalue, codename, message = finder.find_test_result(dtest, results)
            if not finder.is_pass(codevalue):
                is_pass = False
                msg = '{} {} {}({})'.format(dtest.id(), sep, codename, codevalue)
                fail_details.append(msg)
        return (is_pass, fail_details)

    def is_test_pass(self, test, results=None):
        """ 检查 测试用例所依赖的其它测试用例是否通过"""

        results = results or self.results
        finder = TestResultFinder()
        return finder.is_test_pass(test, results)

    @property
    def weights(self):
        """ the weight of  the tests"""

        assert self.tests is not None
        return self._weights

    @property
    def links(self):
        """ the depend chains of the tests"""

        assert self.tests is not None
        return self._links

    @property
    def depends(self):
        """ The dependencies of the tests. """

        assert self.tests is not None
        return self._depends

    def get_missing(self, test):

        return self.depends[test.id()].unresolved

    @property
    def cyclic_links(self):

        assert self.tests is not None
        return self._cyclic_links

    def get_cyclic_links(self, test):

        return self.cyclic_links[test.id()]
