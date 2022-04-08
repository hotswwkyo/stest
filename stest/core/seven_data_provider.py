#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author: 思文伟
'''

import os
from ..utils import sutils
from ..utils.attrs_marker import AttributeMarker
from .abstract_data_provider import AbsractDataProvider
from ..utils.excel_file_reader import TestCaseExcelFileReader as ExcelReader


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
        if sutils.is_blank_space(filename):
            raise ValueError("数据文件名必须是字符串类型且不能为空")
        return filename

    def _get_data_file_dir_path(self, kwargs):

        param = self.PARAM_DATA_FILE_DIR_PATH
        if param not in kwargs.keys():
            raise AttributeError("没有传入数据文件目录")
        dirpath = kwargs[param]
        if sutils.is_blank_space(dirpath):
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
        if sutils.is_blank_space(data_file_dir_path):
            raise ValueError("传入的数据文件目录路径不能为空：{}".format(data_file_dir_path))
        dir_path = data_file_dir_path
        if name and not sutils.is_blank_space(name):
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
        dirpath = self._get_data_file_dir_path(kwargs)
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
