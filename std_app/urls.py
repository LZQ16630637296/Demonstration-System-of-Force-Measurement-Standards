#!/usr/bin/python3
#-*- coding:utf-8 -*-
############################
# File Name: urls.py
# Author: taowang
# mail: wangtao573@bistu.edu.cn or 907993189@qq.com
# Create Time: 2023/5/16 19:23:49
############################
#from icecream import install
#install()
#import time
#def timestamp():
#    return '%s |> ' % time.strftime('%Y-%m-%d %T')
#ic.configureOutput(prefix=timestamp)
#
from django.urls import path

#from std_app.views import test_index
from std_app.views import TestIndex

app_name = 'std_app'
urlpatterns = [
    #path('<int:num>', test_index, name='index')
    path('<int:num>', TestIndex.as_view(), name='index')
]
