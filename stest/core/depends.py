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
        for ptest, message in results.successes:
            if test.id() == ptest.id():
                return (cls.PASS_CODE, cls.get_result_name(cls.PASS_CODE), message)
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

    def __init__(self, testcase_wrapper: TestCaseWrapper, manager):

        self.testid = testcase_wrapper.id()
        self.newid = testcase_wrapper.new_id
        self.depends = set()
        self.unresolved = set()
        self.depends_without_serial_number = set()
        for depend in testcase_wrapper.depends:
            if depend not in manager.name_to_testids:
                absolute_depend = testcase_wrapper.get_absolute_testcase_id(
                    depend, testcase_wrapper.new_id)
                if absolute_depend in manager.name_to_testids:
                    depend = absolute_depend

            if depend in manager.name_to_testids:
                for testid in manager.name_to_testids[depend]:
                    self.depends.add(testid)
                    self.depends_without_serial_number.add(
                        manager.testid_to_test_wrapper[testid].new_id)
            else:
                self.unresolved.add(depend)


class DependsManager(object):
    def __init__(self):

        self._tests = None
        self._results = None
        self._name_to_testids = None
        self._testid_to_test = None
        self._testid_to_test_wrapper = None
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
        self._newid_to_test_depends = {}
        self._testid_to_test = {}
        self._testid_to_test_wrapper = {}
        self._name_to_testids = collections.defaultdict(list)
        tc_wrappers = [TestCaseWrapper(tc) for tc in testcases]
        for tc in tc_wrappers:
            self._testid_to_test[tc.id()] = tc.testcase
            self._testid_to_test_wrapper[tc.id()] = tc
            for name in tc.get_names():
                self._name_to_testids[name].append(tc.id())

        # Don't allow using unknown keys on the name_to_testids mapping
        self._name_to_testids.default_factory = None

        for tc in tc_wrappers:
            td = TestDepends(tc, self)
            self._depends[tc.id()] = td
            if tc.new_id in self._newid_to_test_depends:
                self._newid_to_test_depends[tc.new_id].add(td)
            else:
                tdset = set()
                tdset.add(td)
                self._newid_to_test_depends[tc.new_id] = tdset

        for tc in tc_wrappers:
            weight, links, cyclic_links, cycle_chain_list = self.calc_weight_and_link_perf(tc.id())
            self._weights[tc.id()] = weight
            self._links[tc.id()] = links
            self._cyclic_links[tc.id()] = cycle_chain_list

    def calc_weight_and_link(self, testcase_id):
        """
        计算用例的依赖权重、完整依赖链和循环依赖链。

        Parameters
        ----------
            testcase_id : 用例对象id。

        Returns
        -------
            - weight (int) : 主用例的权重（直接和间接依赖的用例总数，去重）。
            - all_chains (list of list) : 所有完整依赖链的列表，每条链是从主用例到叶子节点的节点序列。
            - cycle_chains (list of list) : 所有循环依赖链的列表，每条循环链表示检测到的循环路径。
            - cycle_chain_list (list of list) : 所有循环依赖链的列表，每条循环链表示从主用例开始到出现循环依赖结束的链路。

        Usage
        -----
            ```python
            def demo4():
                \"""示例3：多依赖与循环

                a->
                |->b->d->a
                |->c->e->f->g->e
                \"""
                # 构造用例
                a = TestCase('A')
                b = TestCase('B')
                c = TestCase('C')
                d = TestCase('D')
                e = TestCase('E')
                f = TestCase('F')
                g = TestCase('G')
                a.depends = {b, c}
                b.depends = {d}
                c.depends = {e}
                d.depends = {a}
                e.depends = {f}
                f.depends = {g}
                g.depends = {e}

                # 计算依赖
                weight, all_chains, cycle_chains,cycle_chain_list = calc_weight_and_link(a)
                print("权重:", weight)
                print("完整依赖链:", all_chains)
                for cycle_chain in cycle_chains:
                    print("循环依赖链:", "->".join([one.name for one in cycle_chain]))

                for cycle_chain in cycle_chain_list:
                    print("从主用例开始到出现循环依赖的链路:", "->".join([one.name for one in cycle_chain]))
            demo4()
            >>> 权重: 6
            >>> 完整依赖链: []
            >>> 循环依赖链: A->B->D->A
            >>> 循环依赖链: E->F->G->E
            >>> 从主用例开始到出现循环依赖的链路: A->B->D->A
            >>> 从主用例开始到出现循环依赖的链路: A->C->E->F->G->E
            ```
        """
        count = 0
        dependency_nodes = set()  # 存储所有依赖节点（直接和间接，去重）
        all_chains = []			 # 存储完整依赖链（非循环路径）
        cycle_chains = []		 # 存储循环依赖链 （只存储循环部分）
        seen_cycle_sets = set()	 # 用于去重循环链的集合（存储节点集合的冻结集）
        cycle_chain_list = []    # 存储从主用例开始到出现循环依赖结束的链路
        main_case: TestDepends = self.depends.get(testcase_id, None)

        def dfs(node, path):
            """深度优先搜索遍历依赖图，记录路径并检测循环。"""
            nonlocal count
            count += len(node.unresolved)
            # 遍历当前节点的所有依赖
            for newid in node.depends_without_serial_number:
                dep_set = self.newid_to_test_depends.get(newid, set())
                dep = list(dep_set)[0]
                if dep.newid in path:
                    # 发现循环：当前依赖已在路径中出现
                    idx = path.index(dep.newid)
                    cycle_chain_list.append(path + [dep.newid])
                    cycle_chain = path[idx:] + [dep.newid]  # 构建循环链：从首次出现位置到当前节点，再加当前依赖
                    cycle_set = frozenset(cycle_chain)  # 使用节点集合标识循环
                    if cycle_set not in seen_cycle_sets:
                        seen_cycle_sets.add(cycle_set)
                        cycle_chains.append(cycle_chain)
                    continue  # 跳过循环依赖，避免无限递归

                # 非循环依赖：将依赖节点加入集合，继续递归
                dependency_nodes.add(dep.newid)
                new_path = path + [dep.newid]	 # 扩展路径
                ntc = self.newid_to_test_depends.get(dep.newid, set())
                if ntc:
                    dfs(list(ntc)[0], new_path)		 # 递归处理依赖

            # 当前节点无依赖时，记录完整依赖链（叶子节点）
            if not node.depends:
                all_chains.append(path)
        if main_case is not None:
            count += len(main_case.unresolved)
            # 从主用例开始处理
            start_path = [main_case.newid]
            if not main_case.depends_without_serial_number:
                # 主用例无依赖：自身即为完整链
                all_chains.append(start_path)
            else:
                for newid in main_case.depends_without_serial_number:
                    if newid in start_path:
                        # 主用例直接依赖自身（循环）
                        idx = start_path.index(newid)
                        cycle_chain_list.append(start_path + [newid])
                        cycle_chain = start_path[idx:] + [newid]
                        cycle_set = frozenset(cycle_chain)
                        if cycle_set not in seen_cycle_sets:
                            seen_cycle_sets.add(cycle_set)
                            cycle_chains.append(cycle_chain)
                        continue

                    # 处理非循环依赖
                    dependency_nodes.add(newid)
                    new_path = start_path + [newid]
                    tc = self.newid_to_test_depends.get(newid, set())
                    if tc:
                        dfs(list(tc)[0], new_path)

        weight = len(dependency_nodes)  # 权重为依赖节点总数（去重）
        return weight, all_chains, cycle_chains, cycle_chain_list

    def calc_weight_and_link_perf(self, testcase_id):
        """
        高性能版本：计算用例的依赖权重、完整依赖链和循环依赖链

        优化点：
        1. 使用迭代DFS替代递归DFS，避免栈溢出
        2. 使用路径集合快速检测循环依赖 (O(1)查找)
        3. 节点状态跟踪避免重复计算
        4. 环检测使用节点集合去重

        Parameters
        ----------
            testcase_id : 用例对象id。

        Returns
        -------
        - weight (int) : 主用例的权重（直接和间接依赖的用例总数，去重）。
        - all_chains (list of list) : 截止到发行循环链时当前所获取到的完整依赖链的列表，每条链是从主用例到叶子节点的节点序列。
        - cycle_chains (list of list) : 截止到发行循环链时当前所获取到的循环依赖链的列表，每条循环链表示检测到的循环路径。
        - cycle_chain_list (list of list) : 截止到发行循环链时当前所获取到的循环依赖链的列表，每条循环链表示从主用例开始到出现循环依赖结束的链路。

        Usage
        -----
            ```python
            def demo4():
                \"""示例3：多依赖与循环

                a->
                |->b->d->a
                |->c->e->f->g->e
                \"""
                # 构造用例
                a = TestCase('A')
                b = TestCase('B')
                c = TestCase('C')
                d = TestCase('D')
                e = TestCase('E')
                f = TestCase('F')
                g = TestCase('G')
                a.depends = {b, c}
                b.depends = {d}
                c.depends = {e}
                d.depends = {a}
                e.depends = {f}
                f.depends = {g}
                g.depends = {e}

                # 计算依赖
                weight, all_chains, cycle_chains,cycle_chain_list = calc_weight_and_link(a)
                print("权重:", weight)
                print("完整依赖链:", all_chains)
                for cycle_chain in cycle_chains:
                    print("循环依赖链:", "->".join([one.name for one in cycle_chain]))

                for cycle_chain in cycle_chain_list:
                    print("从主用例开始到出现循环依赖的链路:", "->".join([one.name for one in cycle_chain]))
            demo4()
            >>> 权重: 6
            >>> 完整依赖链: []
            >>> 循环依赖链: A->B->D->A
            >>> 循环依赖链: E->F->G->E
            >>> 从主用例开始到出现循环依赖的链路: A->B->D->A
            >>> 从主用例开始到出现循环依赖的链路: A->C->E->F->G->E
            ```
        """
        # 初始化数据结构
        visited_global = set()       # 全局访问节点（用于权重计算）
        all_chains = []             # 完整依赖链
        cycle_chains = []           # 循环依赖链
        seen_cycles = set()         # 环标识集合（用于去重）
        stack = []                  # DFS栈: (当前节点, 路径列表, 路径集合)
        cycle_chain_list = []    # 存储从主用例开始到出现循环依赖结束的链路
        # 主用例对象，每个用例对象应具有属性'depends'，该属性是一个集合，包含其直接依赖的用例用例id。
        main_case: TestDepends = self.depends.get(testcase_id, None)
        # 主用例特殊处理
        if not main_case.depends_without_serial_number:
            # 无依赖：自身即为完整链
            all_chains.append([main_case.newid])
            return 0, all_chains, cycle_chains, cycle_chain_list

        # 初始化栈：主用例的直接依赖
        for newid in main_case.depends_without_serial_number:
            dep_set: set = self.newid_to_test_depends.get(newid, set())
            dep: TestDepends = list(dep_set)[0]
            # 处理自循环 (主用例依赖自身)
            if dep.newid is main_case.newid:
                cycle = (main_case.newid,)
                if cycle not in seen_cycles:
                    seen_cycles.add(cycle)
                    cycle_chains.append([main_case.newid, main_case.newid])
                    cycle_chain_list.append([main_case.newid, main_case.newid])
                continue

            # 初始化路径
            path = [main_case.newid, dep.newid]
            path_set = {main_case.newid, dep.newid}

            # 添加到全局节点
            if dep.newid not in visited_global:
                visited_global.add(dep.newid)

            # 入栈处理
            stack.append((dep.newid, path, path_set))

        # 迭代DFS处理
        while stack:
            current_id, path, path_set = stack.pop()
            current_set: set = self.newid_to_test_depends.get(current_id, set())
            current: TestDepends = list(current_set)[0]
            has_dependencies = False

            # 处理当前节点的依赖
            for dep_id in current.depends_without_serial_number:
                dep_set: set = self.newid_to_test_depends.get(dep_id, set())
                dep: TestDepends = list(dep_set)[0]
                # 检测循环依赖
                if dep.newid in path_set:
                    # 获取环路径 (从首次出现位置开始)
                    idx = path.index(dep.newid)
                    cycle_path = tuple(path[idx:])  # 使用元组作为环标识
                    cycle_chain_list.append(path + [dep.newid])
                    # 环去重处理
                    if cycle_path not in seen_cycles:
                        seen_cycles.add(cycle_path)
                        # 构建完整环链 (首尾闭合)
                        cycle_chain = path[idx:] + [dep.newid]
                        cycle_chains.append(cycle_chain)
                    continue

                # 标记有依赖关系
                has_dependencies = True

                # 更新全局节点
                if dep.newid not in visited_global:
                    visited_global.add(dep.newid)

                # 创建新路径
                new_path = path + [dep.newid]
                new_path_set = path_set | {dep.newid}  # 创建新集合避免修改原集合

                # 压栈继续处理
                stack.append((dep.newid, new_path, new_path_set))

            # 记录完整依赖链 (叶子节点)
            if not has_dependencies:
                all_chains.append(path)

        # 计算权重 (全局节点数)
        weight = len(visited_global)
        return weight, all_chains, cycle_chains, cycle_chain_list

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

    @property
    def testid_to_test_wrapper(self):
        assert self.tests is not None
        return self._testid_to_test_wrapper

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

    @property
    def newid_to_test_depends(self):

        assert self.tests is not None
        return self._newid_to_test_depends

    def get_missing(self, test):

        return self.depends[test.id()].unresolved

    @property
    def cyclic_links(self):

        assert self.tests is not None
        return self._cyclic_links

    def get_cyclic_links(self, test):

        return self.cyclic_links[test.id()]
