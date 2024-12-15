#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from stest.utils.attrs_marker import Const
from stest.utils.attrs_manager import unique
from stest.utils.attrs_manager import AttributeManager


@unique
class RunPolicy(AttributeManager):
    """运行策略标记"""

    BEFORE = Const(1, description="run before host func")

    AFTER = Const(2, description="run after host func")
