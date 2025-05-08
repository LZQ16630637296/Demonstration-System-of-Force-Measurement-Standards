#!/usr/bin/python3
#-*- coding:utf-8 -*-
############################
# File Name: templatetags\mytags.py
# Author: taowang
# mail: wangtao573@bistu.edu.cn or 907993189@qq.com
# Create Time: 2023/5/17 21:09:53
############################

from django import template

from functools import reduce

register = template.Library()

@register.filter(is_safe=False)
def add_filter(value, rounded=2):
    assert isinstance(value, list)
    return round(sum(value),rounded)

@register.simple_tag
def add_tag(*args, **kwargs):
    args = args[0]
    result = reduce(lambda x,y: x+y, args)
    rounded = kwargs.get('rounded')
    rounded = rounded or 2
    result = round(result, rounded)
    return result

@register.filter
def label_class(value, cls):
    return value.label_tag(attrs={'class':cls})