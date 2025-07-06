# -*- coding:utf-8 -*-
import time
import autoit
from . import sutils

INTDEFAULT = -2147483647


def win_active(title, **kwargs):
    """
    call autoit.win_activate
    判断窗口是否激活
    timeout 单位为秒.
    :return PID:窗口存在; 0:窗口不存在.
    """
    return autoit.win_active(title, **kwargs)


def win_activate(title, **kwargs):
    """
    call autoit.win_activate
    激活指定的窗口(设置焦点到该窗口,使其成为活动窗口).
    timeout 单位为秒.
    :return PID:窗口存在; 0:窗口不存在.
    """
    return autoit.win_activate(title, **kwargs)


def win_exists(title, **kwargs):
    """
    call autoit.win_exists
    检查指定的窗口是否存在.
    :return 1:窗口存在; 0:窗口不存在.
    """

    return autoit.win_exists(title, **kwargs)


def win_wait(title, timeout=0, **kwargs):
    """
    call autoit.win_wait
    暂停脚本的执行直至指定窗口存在(出现)为止.
    timeout 单位为秒.
    :return PID:成功, 0:失败(超时).
    """
    if not isinstance(timeout, int):
        try:
            timeout = int(timeout)
        except Exception:
            timeout = 0

    return autoit.win_wait(title, timeout=timeout, **kwargs)


def win_wait_active(title, timeout=0, **kwargs):
    """
    call autoit.win_wait_active
    暂停脚本的执行直至指定窗口被激活(成为活动状态)为止.
    timeout 单位为秒.
    :return PID:成功, 0:失败(超时)
    """
    if not isinstance(timeout, int):
        try:
            timeout = int(timeout)
        except Exception:
            timeout = 0

    return autoit.win_wait_active(title, timeout=timeout, **kwargs)


def control_set_text(title, control, control_text, **kwargs):
    """
    call autoit.control_set_text
    """
    return autoit.control_set_text(title, control, control_text, **kwargs)


def control_click(title, control, **kwargs):
    """
    call autoit.control_click
    """
    return autoit.control_click(title, control, **kwargs)


def win_wait_close(title, timeout, **kwargs):
    """
    call autoit.control_set_text
    暂停脚本的执行直至所指定窗口不再存在为止
    timeout 单位为秒.
    :return 1:成功, 0:失败(超时).
    """
    if not isinstance(timeout, int):
        try:
            timeout = int(timeout)
        except Exception:
            timeout = 0
    return autoit.win_wait_close(title, timeout=timeout, **kwargs)


def win_close(title, **kwargs):
    """
    call autoit.win_close
    关闭指定窗口.
    :return 1:成功; 0:窗口不存在.
    """
    return autoit.win_close(title, **kwargs)


def win_close_all(title, limit_loop_time=0, **kwargs):
    """
    关闭所有匹配的指定窗口.
    limit_loop_time 限制循环的次数(0 表示无限制)
    :return [ close result, ...] close result(1:成功; 0:窗口不存在.)
    """
    wins = []

    if isinstance(limit_loop_time, (int, float)):
        limit_loop_time = int(limit_loop_time)
    elif isinstance(limit_loop_time, str) and sutils.is_number(limit_loop_time):
        try:
            limit_loop_time = int(limit_loop_time)
        except ValueError:
            limit_loop_time = int(float(limit_loop_time))
    else:
        limit_loop_time = 0

    current_time = 0
    key = "text"
    while True:
        current_time = current_time + 1
        if key in kwargs.keys():
            text = kwargs[key]
        else:
            text = ""
        if autoit.win_exists(title, text=text):
            result = autoit.win_close(title, **kwargs)
            wins.append(result)
        else:
            break

        if limit_loop_time != 0 and current_time > limit_loop_time:
            break

    return wins


def win_kill(title, **kwargs):
    """
    call autoit.win_kill
    强行关闭指定窗口
    :return 1:无论成功失败.
    """
    return autoit.win_kill(title, **kwargs)


def mouse_move(x, y, speed=-1):

    return autoit.mouse_move(x, y, speed=speed)


def mouse_click(x=INTDEFAULT, y=INTDEFAULT, button="left", clicks=1, speed=-1):

    return autoit.mouse_click(button=button, x=x, y=y, clicks=clicks, speed=speed)


def input_upload_file_path(filepath):
    """输入 上传文件路径"""

    win_title = '打开'
    exist = win_wait(win_title)
    if exist:
        win_activate(win_title)
        control_set_text(win_title, 'Edit1', filepath)
        time.sleep(1)
        control_click(win_title, "Button1", text='打开(&O)')
    else:
        pass
