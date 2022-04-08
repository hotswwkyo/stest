#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author: 思文伟
@Date: 2022/03/30 17:51:16
'''

# 内置参数化数据提供者(SevenDataProvider)读取的测试数据文件所在的目录路径，
# 不设置则自动获取测试用例所在模块的目录路径作为测试数据文件所在的目录路径，
# 内置参数化数据提供者会从该目录路径查找用例测试数据文件。
SEVEN_DATA_PROVIDER_DATA_FILE_DIR = None

# 控制测试失败是否自动截图
SCREENSHOT = False

# 截图文件存放目录，保存为文件时才会用到
# SCREENSHOT_SAVE_DIR = None

# 控制截图后是否附加到测试报告中，如果附加到报告中，则截图转base64数据附加到报告中，否则保存为文件
ATTACH_SCREENSHOT_TO_REPORT = True
