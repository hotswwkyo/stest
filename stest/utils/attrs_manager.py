#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Author: 思文伟
@Date: 2021/04/22 18:06:23
'''

from ..core.errors import ConstAttributeException
from .attrs_marker import Var


class AttributeMetaclass(type):

    _CLASS_ATTRIBUTES = "_CLASS_ATTRIBUTES"  # 禁止修改的类属性和类实例属性名

    def __new__(cls, name, bases, attrs):

        attributes = dict()

        for base in bases:
            if hasattr(base, cls._CLASS_ATTRIBUTES):
                attributes.update(base._CLASS_ATTRIBUTES)

        for attribute, value in attrs.items():
            if isinstance(value, Var):
                attributes[attribute] = value

        for attribute in attributes.keys():
            if attribute in attrs.keys():
                # attrs.pop(attribute)
                attrs[attribute] = attributes[attribute].value
        attrs[cls._CLASS_ATTRIBUTES] = attributes

        return type.__new__(cls, name, bases, attrs)

    def __init__(cls, name, bases, attrs):

        return type.__init__(cls, name, bases, attrs)

    def __setattr__(cls, name, value):

        if name in cls.const_attrs.keys():
            raise ConstAttributeException("Unable to modify constant attribute(%s)" % name)
        type.__setattr__(cls, name, value)

    @property
    def const_attrs(cls):
        """禁止修改的属性"""

        attrs = {}
        for attr, marker in cls._CLASS_ATTRIBUTES.items():

            if marker.final:
                attrs[attr] = marker
        return attrs

    def get_attribute_marker(cls, attribute_name):

        if attribute_name in cls.const_attrs.keys():
            return cls.const_attrs[attribute_name]
        else:
            raise ConstAttributeException("'%s' class has no attribute '%s'" %
                                          (cls.__name__, attribute_name))


class AttributeManager(object, metaclass=AttributeMetaclass):
    def __setattr__(self, name, value):

        if name in self.__class__.const_attrs.keys():
            raise ConstAttributeException("Unable to modify constant attribute(%s)" % name)
        object.__setattr__(self, name, value)

    def get_attr_marker(self, attribute_name):

        return self.__class__.get_attribute_marker(attribute_name)


def unique(enumeration):
    """
    Class decorator for enumerations ensuring unique member values.
    """

    cadict = enumeration.const_attrs
    vk = {}
    for name, maker in cadict.items():
        if maker.value not in vk:
            vk[maker.value] = [name]
        else:
            vk[maker.value].append(name)
    dk = {}
    for k, v in vk.items():
        if len(v) > 1:
            dk[k] = v
    if dk:
        sames = []
        for k, v in dk.items():
            for o in v:
                sames.append('{}={}'.format(o, k))
        alias_details = ' '.join(sames)
        raise ValueError('duplicate values found in %s: %s' %
                         (enumeration, alias_details))
    return enumeration
