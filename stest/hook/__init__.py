#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
wrapper 定义钩子，钩子规范如下：
    1. 钩子函数需要能接收它所挂载到的宿主函数的所有参数，此外还需要接收一个额外参数作为第一个位置参数，这个额外参数为全局变量settings。
    2. runstage参数指定钩子的运行阶段，内置钩子运行阶段见 RunStage类，对应于SevenTestResult的同名方法。
    编写这些运行阶段的钩子函数时，除了第一个参数为全局变量settings外，其它参数与SevenTestResult的同名方法参数一一对应

Simple usage:

    import stest
    from stest import hook
    from stest import AbstractTestCase
    from stest import Test as testcase
    from playwright.sync_api import sync_playwright


    @hook.wrapper(hook.RunStage.startTestRun)
    def startTestRun(conf:stest.settings, result:stest.core.seven_result.SevenTestResult):
        conf.playwright = sync_playwright().start()

    @hook.wrapper(hook.RunStage.stopTestRun)
    def stopTestRun(conf:stest.settings, result:stest.core.seven_result.SevenTestResult):
        playwright = getattr(conf, 'playwright', None)
        if playwright is not None:
            playwright.stop()
"""
from .impl import host
from .impl import wrapper
from .impl import HOOK_MANAGER
from .stage import RunStage
from .policy import RunPolicy


__all__ = ["RunStage", "RunPolicy", "HOOK_MANAGER", "wrapper", "host"]
