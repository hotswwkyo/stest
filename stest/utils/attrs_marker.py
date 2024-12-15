#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author: 思文伟
@Date: 2021/04/22 18:05:27
'''


class Var(object):
    def __init__(self, value, final=False, description="", *expend_args, **expend_kwargs):

        self.value = value
        self.final = final
        self.description = description
        self.expend_args = expend_args
        self.expend_kwargs = expend_kwargs

    def __str__(self):

        return "{value} ------> {description}".format(value=self.value, description=self.description)


class Const(Var):
    def __init__(self, value, description="", *expend_args, **expend_kwargs):

        Var.__init__(self, value, True, description, *expend_args, **expend_kwargs)
