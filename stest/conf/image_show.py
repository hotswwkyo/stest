#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author: 思文伟
@Date: 2025/06/3028 15:18:00
'''
from . import settings


def show2html(master, *, base64data="", filepath="", name="", **other_info):
    """显示截图到html测试报告中

    Parameters
    ----------
    master : 截图所的对象，主要是用来指示截图显示在html测试报告中的哪个区域，目前只有测试用例对象(`AbstractTestCase`)才会生效
    base64data : base64编码的截图文件数据，如果同时提供filepath，则有限使用filepath，忽略该参数
    filepath : 截图文件完整路径
    name : 在html报告中显示的名称
    other_info : 其它信息
    """

    if base64data and filepath:
        base64data = ""
    elif base64data == "" and filepath == "":
        return False
    user_screenshots = getattr(settings, "USER_SCREENSHOTS", {})
    screenshots = user_screenshots.get(master, [])
    screenshots.append(
        dict(base64data=base64data, filepath=filepath, name=name, other_info=other_info))
    user_screenshots[master] = screenshots
    settings.USER_SCREENSHOTS = user_screenshots
    return True
