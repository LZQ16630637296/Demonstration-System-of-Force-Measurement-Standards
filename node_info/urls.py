#!/usr/bin/python3
#-*- coding:utf-8 -*-
############################
# File Name: urls.py
# Author: taowang
# mail: wangtao573@bistu.edu.cn or 907993189@qq.com
# Create Time: 2023/5/16 21:12:04
############################

from django.urls import path, include
from node_info.views import NodeList, NodeCreate, SysStatus, NodeDetail, SysStatusFile, SysStatusFile1, ServerStart, \
    ServerStop, ServerDelete, TaskStatusFile, TaskStatusFile1, ResBaseFile, ResBaseFile1, TaskStart, TaskStop, Echart, \
    TaskStatusPos, ResultFile, ResultFile1

app_name = 'node_info'

urlpatterns = [
    path('', NodeList.as_view(), name='node_list'),
    path('<int:pk>/', NodeDetail.as_view(), name='node_detail'),
    path('create/', NodeCreate.as_view(), name='node_create'),
    path('sys/', SysStatus, name='sys_status'),
    path('sysFile/', SysStatusFile, name='sys_status_file'),
    path('sysFile1/', SysStatusFile1, name='sys_status_file1'),
    path('taskFile/', TaskStatusFile, name='task_status_file'),
    path('taskFile1/', TaskStatusFile1, name='task_status_file1'),
    path('resFile/', ResBaseFile, name='res_base_file'),
    path('resFile1/', ResBaseFile1, name='res_base_file1'),
    path('resultFile/', ResultFile, name='result_file'),
    path('resultFile1/', ResultFile1, name='result_file1'),
    path('start/', ServerStart, name='server_start'),
    path('stop/', ServerStop, name='server_stop'),
    path('delete/', ServerDelete, name='server_delete'),
    path('taskStart/', TaskStart, name='task_start'),
    path('taskStop/', TaskStop, name='task_stop'),
    path('echart/', Echart, name='echart'),
    path('taskFilePos/', TaskStatusPos, name='task_status_pos'),

]
