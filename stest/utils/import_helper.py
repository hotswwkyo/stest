# -*- coding:utf-8 -*-
"""
导入助手
"""

__version__ = "1.0"
__author__ = "si wen wei"

import os
from ..pylibs import python_imp as imp
import inspect


class ImportHelper(object):
    """动态导入"""
    def __init__(self):

        self.dot = "."

    def is_package(self, dirpath):

        ispkg = False
        if not os.path.isdir(dirpath):
            return ispkg

        filenames = os.listdir(dirpath)
        for fn in filenames:
            subname = inspect.getmodulename(fn)
            if subname == "__init__":
                ispkg = True
                break
        return ispkg

    def __load_package(self, dirpath):
        """
        分析包路径，依次导入路径中的包. eg: F:\\zone\\seven\\finders seven是顶层包 finders是子包
        那么将会导入这两个包, 导入后 可以通过sys.modules["seven"] sys.modules["finders"]取得包模块对象

        @param dirpath 包路径
        """

        packages = []
        while True:
            if dirpath.endswith(os.sep):
                dirpath = dirpath.rstrip(os.sep)

            if not self.is_package(dirpath):
                break

            dirname = os.path.basename(dirpath)
            dirpath = os.path.dirname(dirpath)

            if dirname:
                file_object, file_path, describer = imp.find_module(dirname, [dirpath])
                try:
                    package = imp.load_module(dirname, file_object, file_path, describer)
                    packages.append(package)
                finally:
                    if file_object:
                        file_object.close()
            else:
                break
        packages.reverse()
        return packages

    def __load_parent_module(self, modules):
        """
        handle hierarchical module names (names containing dots).
        In order to find P.M, that is, submodule M of package P,
        use find_module() and load_module() to find and load package P,
        and then use find_module() with the path argument set to P.__path__.
        When P itself has a dotted name, apply this recipe recursively. eg: seven.finders.JSONFinder

        @param modules 包类型模块对象
        """

        names = []
        for module in modules:
            names.append(module.__name__)
        parent_module_name = self.dot.join(names)
        if parent_module_name:
            the_last_module = modules[-1]
            the_last_module_name = the_last_module.__name__
            the_last_module_dir = os.path.dirname(the_last_module.__path__[-1])

            file_object, file_path, describer = imp.find_module(the_last_module_name, [the_last_module_dir])
            try:
                module = imp.load_module(parent_module_name, file_object, file_path, describer)
                modules.append(module)
            finally:
                if file_object:
                    file_object.close()
        return parent_module_name

    def load_modules(self, dirpath):
        """
        动态导入目录下的所有py文件模块(__init__.py除外)

        @param dirpath 模块所在的目录路径
        """

        if not os.path.isdir(dirpath):
            raise EnvironmentError('%s is not a directory' % dirpath)

        parent_module_name = self.__load_parent_module(self.__load_package(dirpath))
        names = os.listdir(dirpath)
        modules = []

        for name in names:
            if os.path.isfile(os.path.join(dirpath, name)):
                if name.endswith('.py') and name != '__init__.py':

                    module_name = name[:-3]
                    file_object, file_path, describer = imp.find_module(module_name, [dirpath])
                    try:
                        if parent_module_name:
                            hierarchical_module_name = self.dot.join([parent_module_name, module_name])
                        else:
                            hierarchical_module_name = module_name

                        module = imp.load_module(hierarchical_module_name, file_object, file_path, describer)
                        modules.append(module)
                    finally:
                        if file_object:
                            file_object.close()
        return modules

    def load_module(self, module_file_path):
        """
        动态导入目录下的所有py文件模块(__init__.py除外)

        @param dirpath 模块所在的目录路径
        """

        if not os.path.isfile(module_file_path):
            raise EnvironmentError('%s is not a file' % module_file_path)

        dirpath = os.path.dirname(module_file_path)
        parent_module_name = self.__load_parent_module(self.__load_package(dirpath))
        name = os.path.basename(module_file_path)
        module = None

        if os.path.isfile(os.path.join(dirpath, name)):
            if name.endswith('.py') and name != '__init__.py':

                module_name = name[:-3]
                file_object, file_path, describer = imp.find_module(module_name, [dirpath])
                try:
                    if parent_module_name:
                        hierarchical_module_name = self.dot.join([parent_module_name, module_name])
                    else:
                        hierarchical_module_name = module_name

                    module = imp.load_module(hierarchical_module_name, file_object, file_path, describer)
                finally:
                    if file_object:
                        file_object.close()
        return module
