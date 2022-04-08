#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author: 思文伟
@Date: 2022/03/23 16:23:54
'''

import io
import os
import base64
from .attrs_manager import AttributeManager


class ScreenshotCapturer(AttributeManager):
    """优先使用浏览器截图，如果浏览器截图失败则执行整个屏幕截图"""
    @classmethod
    def screenshot_with_pil(cls, filename=None, region=None):
        """
        截屏返回PIL.Image对象

        Args:
         - filename: 保存截图文件的完整路径名，省略则不保存
         - region: 4整型数据构成的元祖 第1、2为起点坐标，第3、4位长宽，省略则截全屏

        Usage:
            ScreenshotCapturer.screenshot_with_pil('/screenshots/st.png')
        """
        from PIL import ImageGrab

        im = ImageGrab.grab()
        if region is not None:
            assert len(region) == 4, 'region argument must be a tuple of four ints'
            region = [int(x) for x in region]
            im = im.crop((region[0], region[1], region[2] + region[0], region[3] + region[1]))
        if filename is not None:
            im.save(filename)
        return im

    @classmethod
    def full_screenshot_with_pil(cls, file_full_path):

        img = cls.screenshot_with_pil()
        try:
            img.save(file_full_path, "png")
        except ValueError:
            return False
        except IOError:
            return False
        finally:
            del img
        return True

    @classmethod
    def screenshot_with_driver(cls, driver, file_full_path):

        try:
            return driver.get_screenshot_as_file(file_full_path)
        except Exception:
            return False

    @classmethod
    def screenshot(cls, filename, driver=None):
        """浏览器截图失败则启用屏幕截图，返回结果和截图文件路径

        Args:
         - filename: 保存截图文件的完整路径名
         - driver: 驱动实例，省略则使用PIL截图
        """

        result = False
        cls.create_dir(filename)
        if driver:
            result = cls.screenshot_with_driver(driver, filename)
        if not result:
            result = cls.full_screenshot_with_pil(filename)
        return (result, filename)

    @classmethod
    def screenshot_as_base64(cls, driver=None):

        try:
            if driver:
                return driver.get_screenshot_as_base64()
        except Exception:
            pass
        img = cls.screenshot_with_pil()
        temp = io.BytesIO()
        try:
            img.save(temp, "png")
        except ValueError:
            pass
        except IOError:
            pass
        finally:
            del img
        img_datas = temp.getvalue()
        del temp
        return base64.b64encode(img_datas).decode()

    @classmethod
    def screenshot_file_to_base64(cls, file_full_path):
        """转为base64 编码数据

        @filename 完整文件路径
        """
        raw_data = ""
        try:
            with open(file_full_path, "rb") as f:
                raw_data = f.read()
        except IOError as err:
            print(err)
        return base64.b64encode(raw_data).decode()

    @classmethod
    def create_dir(cls, path):

        target_dir = os.path.dirname(path)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
