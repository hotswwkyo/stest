#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author: 思文伟
'''

import os
import re
import json
import inspect
import tkinter
import smtplib
import functools
import tkinter.simpledialog
import collections.abc as collections
from collections.abc import MutableMapping
from functools import cmp_to_key
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def strclass(cls):

    module = inspect.getmodule(cls)
    mfile = inspect.getabsfile(module)
    name = inspect.getmodulename(mfile)
    return "%s.%s" % (name, cls.__qualname__)


def ignore_unused(*objs):
    return objs


def is_number(self, text):

    number = re.compile(r'^[+]?[0-9]+\.[0-9]+$')
    result = number.match(text)
    if result:
        is_number = True
    else:
        is_number = False

    return is_number


def is_string(value):

    return isinstance(value, (str))


def is_positive_integer(value):

    return isinstance(value, int) and value >= 0


def is_empty_string(value):

    return is_string(value) and value == ""


def is_blank_space(value):

    return is_string(value) and value.strip() == ""


def group_by_suffix_regex(string_key_dict, suffix_regex, is_remove_suffix=True, cmp=None):
    """根据键名正则表达式对字典进行分组和排序

    Args:
        string_key_dict 键名是字符串的字典
        suffix_regex 键名正则表达式
        is_remove_suffix 是否移除匹配的后缀
        cmp 如果是函数，会往cmp传入匹配的后缀，函数要求同sorted方法的cmp参数说明，如果是为True则按照匹配的后缀排序，False则不排序
    Returns: 返回分组后组构成的列表，每个组是一个字典 [group, group, ...]
    """

    regex = "(.)*" + "(" + suffix_regex + ")"
    pattern = re.compile(regex)

    unique_suffixes = []
    suffix_key_val_maps = []
    for k, v in string_key_dict.items():
        matcher = pattern.search(k)
        if matcher:
            full_key_name = matcher.group(0)
            key_name_suffix = matcher.group(2)
            suffix_key_val_maps.append((key_name_suffix, full_key_name, v))
            if key_name_suffix not in unique_suffixes:
                unique_suffixes.append(key_name_suffix)

    # sorted
    if inspect.isfunction(cmp):
        unique_suffixes = sorted(unique_suffixes, key=cmp_to_key(cmp))
    elif cmp:
        unique_suffixes = sorted(unique_suffixes)

    # group
    groups = []
    for us in unique_suffixes:
        group = {}
        for suffix, key, val in suffix_key_val_maps:
            if us == suffix:
                if is_remove_suffix:
                    k = key[:len(key) - len(suffix)]
                else:
                    k = key
                group[k] = val
        if group:
            groups.append(group)
    return groups


def digital_extractor(extractor=None):
    """数字提取函数装饰器,把被装饰的函数变成符合sorted要求的cmp函数

    Args:
        extractor 数字提取函数 需要接受一个字符串参数，从中提取数字并返回
    """
    def wapper(func):
        @functools.wraps(func)
        def recv_args(suffix1, suffix2):
            return func(suffix1, suffix2, extractor)

        return recv_args

    return wapper


@digital_extractor()
def digital_suffix_cmp(suffix1, suffix2, digital_extractor=None):
    """数字后缀比较器

    Args:
        suffix1 以数字结尾的字符串1
        suffix2 以数字结尾的字符串2
        digital_extractor 数字提取函数 需要接受一个字符串参数，从中提取数字并返回
    """
    def _digital_extractor(suffix):
        regex = "(\\d+)$"
        pattern = re.compile(regex)
        matcher = pattern.search(suffix)
        if not matcher:
            message = "所给的后缀" + "(" + suffix + ")" + "没有以数字结尾"
            raise ValueError(message)
        return matcher.group(1)

    if digital_extractor and inspect.isfunction(digital_extractor):
        extractor = digital_extractor
    else:
        extractor = _digital_extractor

    n1 = int(extractor(suffix1))
    n2 = int(extractor(suffix2))

    if n1 > n2:
        return 1
    elif n1 == n2:
        return 0
    else:
        return -1


def digital_suffix_cmp_wrapper(digital_extractor=None):
    """ 数字后缀比较器包装器

    Args:
        digital_extractor 数字提取函数 需要接受一个字符串参数，从中提取数字并返回
    """

    if digital_extractor and inspect.isfunction(digital_extractor):

        extractor = digital_extractor

        def new_digital_suffix_cmp(suffix1, suffix2):

            n1 = int(extractor(suffix1))
            n2 = int(extractor(suffix2))

            if n1 > n2:
                return 1
            elif n1 == n2:
                return 0
            else:
                return -1

        return new_digital_suffix_cmp
    else:
        return digital_suffix_cmp


def prompt(title="", tips="", encoding="utf-8"):
    """用于显示可提示用户进行输入的对话框

    Args:
        title 对话框标题
        tips 要在对话框中显示的文本
    """

    root = tkinter.Tk()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight() - 100  # under windows, taskbar may lie under the screen
    root.resizable(False, False)
    root.withdraw()
    # 移到屏幕外，避免闪烁
    root.geometry('+%d+%d' % (screen_width + 100, screen_height + 100))
    root.update_idletasks()
    # root.deiconify()    #now window size was calculated
    # root.withdraw()     #hide window again
    root.geometry('%sx%s+%s+%s' % (root.winfo_width() + 10, root.winfo_height() + 10, (screen_width -
                  root.winfo_width()) / 2, (screen_height - root.winfo_height()) / 2))  # center window on desktop
    root.update()
    root.withdraw()

    # root.deiconify()
    # add some widgets to the root window
    if not isinstance(title, bytes):
        title = title.decode(encoding)
    if not isinstance(tips, bytes):
        tips = tips.decode(encoding)
    value = tkinter.simpledialog.askstring(title, tips)
    if value is None:
        value = ""
    return value


def escape_xpath_value(value):
    if '"' in value and '\'' in value:
        parts_wo_apos = value.split('\'')
        return "concat('%s')" % "', \"'\", '".join(parts_wo_apos)
    if '\'' in value:
        return "\"%s\"" % value
    return "'%s'" % value


def get_the_number_of_pages(total_data, limit_size):
    """根据数据总数和每页显示数据数计算分页数

    Args:
        total_data 数据总数
        limit_size 每页显示数据条数
    """
    quotient, remainder = divmod(total_data, limit_size)
    if remainder > 0:
        quotient = quotient + 1
    return quotient


def cutout_prefix_digital(string):

    regex = "^(\\d+)\\.*"
    pattern = re.compile(regex)
    matcher = pattern.search(string)
    if matcher:
        return matcher.group(1)
    else:
        return None


def find_same_and_diff_fields(fields_1, fields_2, distinct=True):
    """找出fields_1和fields_2中都存在的字段；fields_1中有，但fields_2中没有的字段；
    fields_2中有，但fields_1中没有的字段

    Args:
        fields_1: 字段列表1
        fields_1: 字段列表2
        distinct: 是否去除返回的3个列表中重复的字段, True则去重

    Returns:
        same: list 都存在的相同字段
        redundant: list fields_1中有，但fields_2中没有的字段
        missing: fields_2中有，但fields_1中没有的字段
    """

    same = []
    redundant = []
    missing = []
    for field in fields_1:
        if field in fields_2:
            if distinct:
                if field not in same:
                    same.append(field)
            else:
                same.append(field)
        else:
            if distinct:
                if field not in redundant:
                    redundant.append(field)
            else:
                redundant.append(field)

    for field in fields_2:
        if field not in fields_1:
            if distinct:
                if field not in missing:
                    missing.append(field)
            else:
                missing.append(field)

    return same, redundant, missing


def isfilelike(f):
    """
    Check if object 'f' is readable file-like
    that it has callable attributes 'read' , 'write' and 'close'
    """
    try:
        if isinstance(getattr(f, "read"), collections.Callable) and isinstance(getattr(f, "write"), collections.Callable) and isinstance(getattr(f, "close"), collections.Callable):
            return True
    except AttributeError:
        pass
    return False


def send_email(sender, password, subject="自动化测试报告", message="", mail_to=[], mail_cc=[], mail_bcc=[], attachment=None, smtpserver="smtp.qiye.163.com", port=0, debug=False):
    """

    Args:
        sender:发件人邮箱地址
        password:密码
        mail_to:主送人邮箱列表
        mail_cc:抄送人邮箱列表
        mail_bcc:密送人邮箱列表
        message:邮件正文
        attachment: 附件完整路径字符串或一个以二进制模式打开的文件对象
    """
    resend_time = 1
    msg = MIMEMultipart("mixed")
    altmsg = MIMEMultipart("alternative")
    message = '<pre style="font-weight: 500;font-size: 16px;color: darkcyan;">%s</pre>' % message
    body = MIMEText(message, _subtype='html', _charset='utf8')
    altmsg.attach(body)
    if attachment:
        if isinstance(attachment, str):
            f = open(attachment, 'rb')
            file_name = os.path.split(attachment)[-1]
        elif isfilelike(attachment):
            f = attachment
            file_name = os.path.split(f.name)[-1]
        else:
            raise TypeError("attachment must be file object or string (full path of file)")
        f_content = f.read()
        f.close()

        if file_name.endswith(".html"):
            html = MIMEText(f_content, _subtype='html', _charset='utf-8')
            altmsg.attach(html)
        att = MIMEText(f_content, "base64", _charset='utf8')
        att["Content-Type"] = 'application/octet-stream;charset=utf-8'
        att.add_header("Content-Disposition", "attachment",
                       filename=Header(file_name, 'utf-8').encode())
        # att["Content-Disposition"]  = 'attachment;filename="%s"' % file_name
        # att = MIMEBase('application', 'octet-stream')
        # att.set_payload(f_content)
        # att.add_header('Content-Disposition', 'attachment', filename=('gbk', '', file_name) )
        # encoders.encode_base64(att)
        msg.attach(att)
    msg.attach(altmsg)
    if mail_to:
        msg["To"] = ",".join(mail_to)
    if mail_cc:
        msg["Cc"] = ",".join(mail_cc)
    if mail_bcc:
        msg["Bcc"] = ",".join(mail_bcc)
    receiver = mail_to + mail_cc + mail_bcc
    msg["from"] = sender
    msg["Subject"] = Header(subject, "utf8")
    msg["Accept-Language"] = "zh-CN"
    msg["Accept-Charset"] = "ISO-8859-1,utf-8"

    smtp_sender = smtplib.SMTP(host=smtpserver, port=port)
    # smtp_sender.connect(smtpserver)
    smtp_sender.ehlo()
    smtp_sender.starttls()
    is_success = True
    while True:
        try:
            smtp_sender.login(sender, password)
            smtp_sender.sendmail(sender, receiver, msg.as_string())
            is_success = True
            break
        except smtplib.SMTPException as e:
            resend_time = resend_time + 1
            is_success = False
            if resend_time == 3:
                if debug:
                    print("send email %s times failed" % resend_time)
                    print(e)
                break

    smtp_sender.quit()
    return is_success


def to_json_obj(json_str):

    return json.loads(json_str)


def to_json_str(json_obj):

    return json.dumps(json_obj, ensure_ascii=False)


def get_caller_name():
    """获取直接调用该函数的函数或方法名"""

    return inspect.stack()[1][3]


class StringKeyDict(MutableMapping):
    def __init__(self, initial=None, remove_chars=(), to_lower_case=True, remove_all_whitespace=True):

        self._data = {}
        self._keys = {}
        self.remove_chars = remove_chars
        self.to_lower_case = to_lower_case
        self.remove_all_whitespace = remove_all_whitespace
        if initial:
            self._add_initial(initial)

    def _normalize_string(self, string):

        empty = ""
        if self.remove_all_whitespace:
            string = empty.join(string.split())
        if self.to_lower_case:
            string = string.lower()
            self.remove_chars = [c.lower() for c in self.remove_chars]
        if self.remove_chars:
            for remove_char in self.remove_chars:
                if remove_char in string:
                    string = string.replace(remove_char, empty)
        return string

    def _add_initial(self, initial):

        items = initial.items() if hasattr(initial, 'items') else initial
        for key, value in items:
            self[key] = value

    def __getitem__(self, key):

        return self._data[self._normalize_string(key)]

    def __setitem__(self, key, value):

        lower_key = self._normalize_string(key)
        self._data[lower_key] = value
        self._keys.setdefault(lower_key, key)

    def __delitem__(self, key):

        lower_key = self._normalize_string(key)
        del self._data[lower_key]
        del self._keys[lower_key]

    def __iter__(self):

        return (self._keys[lower_key] for lower_key in sorted(self._keys))

    def __len__(self):

        return len(self._data)

    def __str__(self):

        return '{%s}' % ', '.join('%r: %r' % (key, self[key]) for key in self)

    def __eq__(self, other):

        if isinstance(other, StringKeyDict):
            return self._data == other._data
        else:
            return False

    def __ne__(self, other):

        return not self == other

    def __contains__(self, key):

        return self._normalize_string(key) in self._data

    def clear(self):

        self._data.clear()
        self._keys.clear()


def mkdirs(dirpath, **kwargs):
    """

    See: os.makedirs
    """

    if not os.path.exists(dirpath):
        os.makedirs(dirpath, **kwargs)
