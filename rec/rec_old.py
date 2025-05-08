#!/usr/bin/python3
# -*- coding:utf-8 -*-
############################
# File Name: rec.py
# Author: 
# mail: 
# Create Time: 2023/5/4 19:28:24
############################
import re
import os
import time
import random
import xml.dom.minidom

import xmltodict
import json
from paho.mqtt import client as mqtt_client
from xml.dom.minidom import parseString
import argparse
import xml.etree.ElementTree as ET

def strToNum(str):
    res = re.sub(r'[a-zA-Z]+', '', str)
    return float(res)

parser = argparse.ArgumentParser(description='')
parser.add_argument('--broker', type=str, default='127.0.0.1')
parser.add_argument('--port', type=int, default=1883)
parser.add_argument('--keepalive', type=int, default=60)
parser.add_argument('--timeslot', type=int, default=4)
parser.add_argument('--clientID', type=str, default='rec')
args = parser.parse_known_args()[0]
brokerIP = args.broker
port = args.port
keepalive = args.keepalive
clientID = args.clientID
timeslot = args.timeslot
print(args)

xml_path = "C:\KubeEdge\js-client"
xml_path = r"node_info/templates/node_info"
lomsg = {}
lomsg1 = {}
lomsg2 = {}
lomsg3 = {}
resmsg = {}
"""TODO+ 依据标准增加更多内容"""
topics = [
    'mqtt/task/generate',
    'mqtt/subtask/model/operand',
    'mqtt/subtask/model/data',
    'mqtt/subtask/require/algorithm',
    'mqtt/subtask/require/compute_power',
    'mqtt/subtask/require/mem',
    'mqtt/subtask/require/cache',
    'mqtt/subtask/require/disk',
    'mqtt/subtask/require/network',
    'mqtt/subtask/require/io_rate',
    'mqtt/subtask/require/delay',
    'mqtt/subtask/require/response_time',
    'mqtt/subtask/require/energy',
    'mqtt/subtask/require/stability',
    'mqtt/subtask/require/security',


    'mqtt/virtual/release',
    'mqtt/virtual/deploy',
    'mqtt/virtual/performance/response_time',
    'mqtt/virtual/performance/energy',
    'mqtt/virtual/performance/stability',
    'mqtt/virtual/performance/security',

    'mqtt/system/Attribute',
    'mqtt/system/CPUFLOPS',
    'mqtt/system/GPUFLOPS',
    'mqtt/system/TPUFLOPS',

    'mqtt/system/Storage_M',
    'mqtt/system/Internal_storage',
    'mqtt/system/External_storage',
    'mqtt/system/Cache',

    'mqtt/system/Throughput_up',
    'mqtt/system/Throughput_down',
    'mqtt/system/Latency',

    'mqtt/system/ComputerPower_M',
    'mqtt/system/ComputerPower',

]
operands = ['Convolution',
            'Dense',
            'BatchNormalization',
            'ReLU',
            'Add',
            'MaxPooling',
            'GlobalPooling',
            'SoftMax',
            'ForwardPropagation',
            'BackwardDense',
            'BackwardPropagation',
            'Verify']


class ServerAgent():
    def __init__(
            self,
            keepalive: int,
            broker: str,
            clientID: str,
            port: int,
            topics: list = [
                'mqtt/system/FLOPS',
            ],
            task_ctl: list = [
                'mqtt/task/class'
            ],
    ) -> object:
        self.client = None
        self.topics = topics
        self.ctl = task_ctl
        self.keepalive = keepalive
        self.broker = broker
        self.port = port
        self.clientID = clientID
        self.msg = {}
        self.task_list = []

    def connect_mqtt(
            self,
    ):
        '''连接mqtt代理服务器'''

        def on_connect(client, userdata, flags, rc):
            '''连接回调函数'''
            # 响应状态码为0表示连接成功
            if rc == 0:
                print("Connected to MQTT OK!")
            else:
                print("Failed to connect, return code %d\n", rc)

        # 连接mqtt代理服务器，并获取连接引用
        self.client = mqtt_client.Client(self.clientID)
        self.client.on_connect = on_connect
        self.client.connect(self.broker, self.port, self.keepalive)

    def publish(
            self,
    ):
        '''发布消息'''
        time.sleep(timeslot)
        while True:
            tc = input('输入任务类型 : ')
            """ TODO- 发一个任务 """
            self.msg = tc
            # print(type(self.msg))
            topic = self.ctl[0]
            result = self.client.publish(topic, self.msg)
            status = result[0]
            if status == 0:
                print(f"Send `{self.msg}` to topic `{topic}`")
            else:
                print(f"Failed to send message to topic {topic}")

    def subscribe(
            self,
    ):
        '''订阅主题并接收消息'''

        def on_message(client, userdata, msg):
            # print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
            topic = msg.topic
            """ TODO  REALITY  INFO  CALLBACK 
            elif topic == 'NEW':
                具体处理逻辑
                pass
            ....
            """

            if topic == 'mqtt/subtask/model/operand':
                tmpmsg = msg.payload.decode().split(':')
                task_str = '任务' + tmpmsg[0].split('~')[1]
                tmpmsg[0] = '子任务' + tmpmsg[1]
                if task_str not in lomsg1:
                    lomsg1[task_str] = {}
                if tmpmsg[0] not in lomsg1[task_str]:
                    lomsg1[task_str][tmpmsg[0]] = {}
                lomsg1[task_str][tmpmsg[0]]['ID'] = tmpmsg[1]
                if '构成' not in lomsg1[task_str][tmpmsg[0]]:
                    lomsg1[task_str][tmpmsg[0]]['构成'] = {}
                if '模型' not in lomsg1[task_str][tmpmsg[0]]['构成']:
                    lomsg1[task_str][tmpmsg[0]]['构成']['模型'] = {}
                if '操作数' not in lomsg1[task_str][tmpmsg[0]]['构成']['模型']:
                    lomsg1[task_str][tmpmsg[0]]['构成']['模型']['操作数'] = {}
                for i in range(2, len(tmpmsg)):
                    if tmpmsg[i] != '0':
                        lomsg1[task_str][tmpmsg[0]]['构成']['模型']['操作数'][operands[i - 2]] = tmpmsg[i]
            elif topic == 'mqtt/subtask/model/data':
                tmpmsg = msg.payload.decode().split(':')
                task_str = '任务' + tmpmsg[0].split('~')[1]
                tmpmsg[0] = '子任务' + tmpmsg[1]
                if task_str not in lomsg1:
                    lomsg1[task_str] = {}
                if tmpmsg[0] not in lomsg1[task_str]:
                    lomsg1[task_str][tmpmsg[0]] = {}
                if '构成' not in lomsg1[task_str][tmpmsg[0]]:
                    lomsg1[task_str][tmpmsg[0]]['构成'] = {}
                if '模型' not in lomsg1[task_str][tmpmsg[0]]['构成']:
                    lomsg1[task_str][tmpmsg[0]]['构成']['模型'] = {}
                lomsg1[task_str][tmpmsg[0]]['构成']['模型']['数据要求'] = tmpmsg[2]
            elif topic == 'mqtt/subtask/require/algorithm':
                tmpmsg = msg.payload.decode().split(':')
                task_str = '任务' + tmpmsg[0].split('~')[1]
                tmpmsg[0] = '子任务' + tmpmsg[1]
                if task_str not in lomsg1:
                    lomsg1[task_str] = {}
                if tmpmsg[0] not in lomsg1[task_str]:
                    lomsg1[task_str][tmpmsg[0]] = {}
                if '资源需求' not in lomsg1[task_str][tmpmsg[0]]:
                    lomsg1[task_str][tmpmsg[0]]['资源需求'] = {}
                if '算力' not in lomsg1[task_str][tmpmsg[0]]['资源需求']:
                    lomsg1[task_str][tmpmsg[0]]['资源需求']['算力'] = {}
                lomsg1[task_str][tmpmsg[0]]['资源需求']['算力']['算法'] = tmpmsg[2]
            elif topic == 'mqtt/subtask/require/compute_power':
                tmpmsg = msg.payload.decode().split(':')
                task_str = '任务' + tmpmsg[0].split('~')[1]
                tmpmsg[0] = '子任务' + tmpmsg[1]
                if task_str not in lomsg1:
                    lomsg1[task_str] = {}
                if tmpmsg[0] not in lomsg1[task_str]:
                    lomsg1[task_str][tmpmsg[0]] = {}
                if '资源需求' not in lomsg1[task_str][tmpmsg[0]]:
                    lomsg1[task_str][tmpmsg[0]]['资源需求'] = {}
                if '算力' not in lomsg1[task_str][tmpmsg[0]]['资源需求']:
                    lomsg1[task_str][tmpmsg[0]]['资源需求']['算力'] = {}
                lomsg1[task_str][tmpmsg[0]]['资源需求']['算力']['值'] = tmpmsg[2]
            elif topic == 'mqtt/subtask/require/mem':
                tmpmsg = msg.payload.decode().split(':')
                task_str = '任务' + tmpmsg[0].split('~')[1]
                tmpmsg[0] = '子任务' + tmpmsg[1]
                if task_str not in lomsg1:
                    lomsg1[task_str] = {}
                if tmpmsg[0] not in lomsg1[task_str]:
                    lomsg1[task_str][tmpmsg[0]] = {}
                if '资源需求' not in lomsg1[task_str][tmpmsg[0]]:
                    lomsg1[task_str][tmpmsg[0]]['资源需求'] = {}
                if '存储' not in lomsg1[task_str][tmpmsg[0]]['资源需求']:
                    lomsg1[task_str][tmpmsg[0]]['资源需求']['存储'] = {}
                if tmpmsg[2] != '0GB':
                    if '类型1' not in lomsg1[task_str][tmpmsg[0]]['资源需求']['存储']:
                        lomsg1[task_str][tmpmsg[0]]['资源需求']['存储']['类型1'] = {}
                    lomsg1[task_str][tmpmsg[0]]['资源需求']['存储']['类型1'] = '内存'
                    lomsg1[task_str][tmpmsg[0]]['资源需求']['存储']['字节数1'] = tmpmsg[2]
            elif topic == 'mqtt/subtask/require/cache':
                tmpmsg = msg.payload.decode().split(':')
                task_str = '任务' + tmpmsg[0].split('~')[1]
                tmpmsg[0] = '子任务' + tmpmsg[1]
                if task_str not in lomsg1:
                    lomsg1[task_str] = {}
                if tmpmsg[0] not in lomsg1[task_str]:
                    lomsg1[task_str][tmpmsg[0]] = {}
                if '资源需求' not in lomsg1[task_str][tmpmsg[0]]:
                    lomsg1[task_str][tmpmsg[0]]['资源需求'] = {}
                if '存储' not in lomsg1[task_str][tmpmsg[0]]['资源需求']:
                    lomsg1[task_str][tmpmsg[0]]['资源需求']['存储'] = {}
                if tmpmsg[2] != '0GB':
                    if '类型2' not in lomsg1[task_str][tmpmsg[0]]['资源需求']['存储']:
                        lomsg1[task_str][tmpmsg[0]]['资源需求']['存储']['类型2'] = {}
                    lomsg1[task_str][tmpmsg[0]]['资源需求']['存储']['类型2'] = '缓存'
                    lomsg1[task_str][tmpmsg[0]]['资源需求']['存储']['字节数2'] = tmpmsg[2]
            elif topic == 'mqtt/subtask/require/disk':
                tmpmsg = msg.payload.decode().split(':')
                task_str = '任务' + tmpmsg[0].split('~')[1]
                tmpmsg[0] = '子任务' + tmpmsg[1]
                if task_str not in lomsg1:
                    lomsg1[task_str] = {}
                if tmpmsg[0] not in lomsg1[task_str]:
                    lomsg1[task_str][tmpmsg[0]] = {}
                if '资源需求' not in lomsg1[task_str][tmpmsg[0]]:
                    lomsg1[task_str][tmpmsg[0]]['资源需求'] = {}
                if '存储' not in lomsg1[task_str][tmpmsg[0]]['资源需求']:
                    lomsg1[task_str][tmpmsg[0]]['资源需求']['存储'] = {}
                if tmpmsg[2] != '0GB':
                    if '类型3' not in lomsg1[task_str][tmpmsg[0]]['资源需求']['存储']:
                        lomsg1[task_str][tmpmsg[0]]['资源需求']['存储']['类型3'] = {}
                    lomsg1[task_str][tmpmsg[0]]['资源需求']['存储']['类型3'] = '外存'
                    lomsg1[task_str][tmpmsg[0]]['资源需求']['存储']['字节数3'] = tmpmsg[2]
            elif topic == 'mqtt/subtask/require/network':
                tmpmsg = msg.payload.decode().split(':')
                task_str = '任务' + tmpmsg[0].split('~')[1]
                tmpmsg[0] = '子任务' + tmpmsg[1]
                if task_str not in lomsg1:
                    lomsg1[task_str] = {}
                if tmpmsg[0] not in lomsg1[task_str]:
                    lomsg1[task_str][tmpmsg[0]] = {}
                if '资源需求' not in lomsg1[task_str][tmpmsg[0]]:
                    lomsg1[task_str][tmpmsg[0]]['资源需求'] = {}
                if '网络' not in lomsg1[task_str][tmpmsg[0]]['资源需求']:
                    lomsg1[task_str][tmpmsg[0]]['资源需求']['网络'] = {}
                if '支持的网络协议' not in lomsg1[task_str][tmpmsg[0]]['资源需求']['网络']:
                    lomsg1[task_str][tmpmsg[0]]['资源需求']['网络']['支持的网络协议'] = {}
                for i in range(2, len(tmpmsg)):
                    lomsg1[task_str][tmpmsg[0]]['资源需求']['网络']['支持的网络协议']['网络协议' + str(i - 2)] = tmpmsg[
                        i]
            elif topic == 'mqtt/subtask/require/io_rate':
                tmpmsg = msg.payload.decode().split(':')
                task_str = '任务' + tmpmsg[0].split('~')[1]
                tmpmsg[0] = '子任务' + tmpmsg[1]
                if task_str not in lomsg1:
                    lomsg1[task_str] = {}
                if tmpmsg[0] not in lomsg1[task_str]:
                    lomsg1[task_str][tmpmsg[0]] = {}
                if '资源需求' not in lomsg1[task_str][tmpmsg[0]]:
                    lomsg1[task_str][tmpmsg[0]]['资源需求'] = {}
                if '网络' not in lomsg1[task_str][tmpmsg[0]]['资源需求']:
                    lomsg1[task_str][tmpmsg[0]]['资源需求']['网络'] = {}
                if tmpmsg[2] != '0' or tmpmsg[3] != '0':
                    if '最小最大吞吐率' not in lomsg1[task_str][tmpmsg[0]]['资源需求']['网络']:
                        lomsg1[task_str][tmpmsg[0]]['资源需求']['网络']['最小最大吞吐率'] = {}
                    if tmpmsg[2] != '0':
                        lomsg1[task_str][tmpmsg[0]]['资源需求']['网络']['最小最大吞吐率']['下行'] = tmpmsg[2]
                    if tmpmsg[3] != '0':
                        lomsg1[task_str][tmpmsg[0]]['资源需求']['网络']['最小最大吞吐率']['上行'] = tmpmsg[3]
            elif topic == 'mqtt/subtask/require/delay':
                tmpmsg = msg.payload.decode().split(':')
                task_str = '任务' + tmpmsg[0].split('~')[1]
                tmpmsg[0] = '子任务' + tmpmsg[1]
                if task_str not in lomsg1:
                    lomsg1[task_str] = {}
                if tmpmsg[0] not in lomsg1[task_str]:
                    lomsg1[task_str][tmpmsg[0]] = {}
                if '资源需求' not in lomsg1[task_str][tmpmsg[0]]:
                    lomsg1[task_str][tmpmsg[0]]['资源需求'] = {}
                if '网络' not in lomsg1[task_str][tmpmsg[0]]['资源需求']:
                    lomsg1[task_str][tmpmsg[0]]['资源需求']['网络'] = {}
                if '延迟' not in lomsg1[task_str][tmpmsg[0]]['资源需求']['网络']:
                    lomsg1[task_str][tmpmsg[0]]['资源需求']['网络']['延迟'] = {}
                lomsg1[task_str][tmpmsg[0]]['资源需求']['网络']['延迟'] = tmpmsg[2]
            elif topic == 'mqtt/subtask/require/response_time':
                tmpmsg = msg.payload.decode().split(':')
                task_str = '任务' + tmpmsg[0].split('~')[1]
                tmpmsg[0] = '子任务' + tmpmsg[1]
                if task_str not in lomsg1:
                    lomsg1[task_str] = {}
                if tmpmsg[0] not in lomsg1[task_str]:
                    lomsg1[task_str][tmpmsg[0]] = {}
                if '资源需求' not in lomsg1[task_str][tmpmsg[0]]:
                    lomsg1[task_str][tmpmsg[0]]['资源需求'] = {}
                if '性能要求' not in lomsg1[task_str][tmpmsg[0]]['资源需求']:
                    lomsg1[task_str][tmpmsg[0]]['资源需求']['性能要求'] = {}
                if '响应时间' not in lomsg1[task_str][tmpmsg[0]]['资源需求']['性能要求']:
                    lomsg1[task_str][tmpmsg[0]]['资源需求']['性能要求']['响应时间'] = {}
                lomsg1[task_str][tmpmsg[0]]['资源需求']['性能要求']['响应时间']['最小'] = tmpmsg[2]
                lomsg1[task_str][tmpmsg[0]]['资源需求']['性能要求']['响应时间']['最大'] = tmpmsg[3]
                lomsg1[task_str][tmpmsg[0]]['资源需求']['性能要求']['响应时间']['平均'] = tmpmsg[4]
            elif topic == 'mqtt/subtask/require/energy':
                tmpmsg = msg.payload.decode().split(':')
                task_str = '任务' + tmpmsg[0].split('~')[1]
                tmpmsg[0] = '子任务' + tmpmsg[1]
                if task_str not in lomsg1:
                    lomsg1[task_str] = {}
                if tmpmsg[0] not in lomsg1[task_str]:
                    lomsg1[task_str][tmpmsg[0]] = {}
                if '资源需求' not in lomsg1[task_str][tmpmsg[0]]:
                    lomsg1[task_str][tmpmsg[0]]['资源需求'] = {}
                if '性能要求' not in lomsg1[task_str][tmpmsg[0]]['资源需求']:
                    lomsg1[task_str][tmpmsg[0]]['资源需求']['性能要求'] = {}
                lomsg1[task_str][tmpmsg[0]]['资源需求']['性能要求']['能耗'] = tmpmsg[2]
            elif topic == 'mqtt/subtask/require/stability':
                tmpmsg = msg.payload.decode().split(':')
                task_str = '任务' + tmpmsg[0].split('~')[1]
                tmpmsg[0] = '子任务' + tmpmsg[1]
                if task_str not in lomsg1:
                    lomsg1[task_str] = {}
                if tmpmsg[0] not in lomsg1[task_str]:
                    lomsg1[task_str][tmpmsg[0]] = {}
                if '资源需求' not in lomsg1[task_str][tmpmsg[0]]:
                    lomsg1[task_str][tmpmsg[0]]['资源需求'] = {}
                if '性能要求' not in lomsg1[task_str][tmpmsg[0]]['资源需求']:
                    lomsg1[task_str][tmpmsg[0]]['资源需求']['性能要求'] = {}
                lomsg1[task_str][tmpmsg[0]]['资源需求']['性能要求']['稳定性'] = tmpmsg[2]
            elif topic == 'mqtt/subtask/require/security':
                tmpmsg = msg.payload.decode().split(':')
                task_str = '任务' + tmpmsg[0].split('~')[1]
                tmpmsg[0] = '子任务' + tmpmsg[1]
                if task_str not in lomsg1:
                    lomsg1[task_str] = {}
                if tmpmsg[0] not in lomsg1[task_str]:
                    lomsg1[task_str][tmpmsg[0]] = {}
                if '资源需求' not in lomsg1[task_str][tmpmsg[0]]:
                    lomsg1[task_str][tmpmsg[0]]['资源需求'] = {}
                if '性能要求' not in lomsg1[task_str][tmpmsg[0]]['资源需求']:
                    lomsg1[task_str][tmpmsg[0]]['资源需求']['性能要求'] = {}
                lomsg1[task_str][tmpmsg[0]]['资源需求']['性能要求']['安全性'] = tmpmsg[2]
            elif topic == 'mqtt/virtual/release':
                tmpmsg = msg.payload.decode().split(':')
                task_str = '任务' + tmpmsg[0].split('~')[1]
                tmpmsg[0] = '子任务' + tmpmsg[1]
                if task_str in lomsg1:
                    if tmpmsg[0] in lomsg1[task_str]:
                        del lomsg1[task_str][tmpmsg[0]]
                    if lomsg1[task_str] == {}:
                        del lomsg1[task_str]
                if 'offloadingRes' not in lomsg2:
                    lomsg2['offloadingRes'] = {}
                if task_str+tmpmsg[0] in lomsg2['offloadingRes']:
                    del lomsg2['offloadingRes'][task_str+tmpmsg[0]]

            if topic == 'mqtt/virtual/deploy':
                tmpmsg = msg.payload.decode().split('调度到节点')
                if 'offloadingRes' not in lomsg2:
                    lomsg2['offloadingRes'] = {}
                ## subtask : server
                tmpmsg[0] = tmpmsg[0].replace('~', '')
                tmpmsg[0] = tmpmsg[0].replace(':', '')
                lomsg2['offloadingRes'][tmpmsg[0]] = tmpmsg[1]
                # print("****DDDDDDDD******", lomsg2)


            # TODO 2023-10-29 算力资源调度结果xml
            task_type = ''
            if topic == 'mqtt/virtual/deploy':
                tmpmsg = msg.payload.decode().split('调度到节点')
                task_id = tmpmsg[0].split('~')[1]
                subtask_id = tmpmsg[0].split(':')[1]
                device_id = tmpmsg[1]
                if 'cloud' in device_id:
                    task_type = "云端任务"
                elif 'edge' in device_id:
                    task_type = "边缘端任务"
                else:
                    task_type = "终端任务"
                if task_type not in lomsg3:
                    lomsg3[task_type] = {}
                if '分配'+subtask_id not in lomsg3[task_type]:
                    lomsg3[task_type]['分配'+subtask_id] = {}
                if '任务ID' not in lomsg3[task_type]['分配'+subtask_id]:
                    lomsg3[task_type]['分配'+subtask_id]['任务ID'] = {}
                if '节点ID' not in lomsg3[task_type]['分配'+subtask_id]:
                    lomsg3[task_type]['分配'+subtask_id]['节点ID'] = {}
                lomsg3[task_type]['分配'+subtask_id]['任务ID'] = subtask_id
                lomsg3[task_type]['分配'+subtask_id]['节点ID'] = device_id
            elif topic == 'mqtt/virtual/performance/response_time':
                tmpmsg = msg.payload.decode().split(':')
                subtask_id = tmpmsg[0]
                device_id = tmpmsg[1]
                if 'cloud' in device_id:
                    task_type = "云端任务"
                elif 'edge' in device_id:
                    task_type = "边缘端任务"
                else:
                    task_type = "终端任务"
                if task_type not in lomsg3:
                    lomsg3[task_type] = {}
                if '分配' + subtask_id not in lomsg3[task_type]:
                    lomsg3[task_type]['分配' + subtask_id] = {}
                if '可达性能' not in lomsg3[task_type]['分配' + subtask_id]:
                    lomsg3[task_type]['分配' + subtask_id]['可达性能'] = {}
                if '响应时间' not in lomsg3[task_type]['分配' + subtask_id]['可达性能']:
                    lomsg3[task_type]['分配' + subtask_id]['可达性能']['响应时间'] = {}
                lomsg3[task_type]['分配' + subtask_id]['可达性能']['响应时间']['最小'] = tmpmsg[2]
                lomsg3[task_type]['分配' + subtask_id]['可达性能']['响应时间']['最大'] = tmpmsg[3]
                lomsg3[task_type]['分配' + subtask_id]['可达性能']['响应时间']['平均'] = tmpmsg[4]
            elif topic == 'mqtt/virtual/performance/energy' or topic == 'mqtt/virtual/performance/stability' or topic == 'mqtt/virtual/performance/security':
                performance_type = ''
                if topic == 'mqtt/virtual/performance/energy':
                    performance_type = '能耗'
                elif topic == 'mqtt/virtual/performance/stability':
                    performance_type = '稳定性'
                elif topic == 'mqtt/virtual/performance/security':
                    performance_type = '安全性'
                tmpmsg = msg.payload.decode().split(':')
                subtask_id = tmpmsg[0]
                device_id = tmpmsg[1]
                if 'cloud' in device_id:
                    task_type = "云端任务"
                elif 'edge' in device_id:
                    task_type = "边缘端任务"
                else:
                    task_type = "终端任务"
                if task_type not in lomsg3:
                    lomsg3[task_type] = {}
                if '分配' + subtask_id not in lomsg3[task_type]:
                    lomsg3[task_type]['分配' + subtask_id] = {}
                if '可达性能' not in lomsg3[task_type]['分配' + subtask_id]:
                    lomsg3[task_type]['分配' + subtask_id]['可达性能'] = {}
                if performance_type not in lomsg3[task_type]['分配' + subtask_id]['可达性能']:
                    lomsg3[task_type]['分配' + subtask_id]['可达性能'][performance_type] = {}
                lomsg3[task_type]['分配' + subtask_id]['可达性能'][performance_type] = tmpmsg[2]

            json_to_xml(json.dumps(lomsg1), xml_path, 'task')
            json_to_xml(json.dumps(lomsg2), xml_path, 'task_off_res')
            json_to_xml(json.dumps(lomsg3), xml_path, 'task_off_res1')
            '''订阅消息回调函数'''

            if topic == 'mqtt/system/Attribute':
                tmpmsg = msg.payload.decode().split(':')
                if tmpmsg[0] not in lomsg:
                    lomsg[tmpmsg[0]] = {}
                if '节点' not in lomsg[tmpmsg[0]]:
                    lomsg[tmpmsg[0]]['节点'] = {}
                if 'URL' not in lomsg[tmpmsg[0]]['节点']:
                    lomsg[tmpmsg[0]]['节点']['URL'] = {}
                if 'ID' not in lomsg[tmpmsg[0]]['节点']:
                    lomsg[tmpmsg[0]]['节点']['ID'] = {}
                if '优先级' not in lomsg[tmpmsg[0]]['节点']:
                    lomsg[tmpmsg[0]]['节点']['优先级'] = {}
                lomsg[tmpmsg[0]]['节点']['URL'] = tmpmsg[1]
                lomsg[tmpmsg[0]]['节点']['ID'] = tmpmsg[2]
                lomsg[tmpmsg[0]]['节点']['优先级'] = tmpmsg[3]

                # processor
            if topic == 'mqtt/system/CPUFLOPS':
                tmpmsg = msg.payload.decode().split(':')
                # if tmpmsg[0] not in lomsg:
                #     lomsg[tmpmsg[0]] = { }
                # if '节点' not in lomsg[tmpmsg[0]]:
                #     lomsg[tmpmsg[0]]['节点'] = { }
                if '容器' not in lomsg[tmpmsg[0]]['节点']:
                    lomsg[tmpmsg[0]]['节点']['容器'] = {}
                # if 'FLOPS' not in lomsg[tmpmsg[0]]['节点'] ['容器']:
                #     lomsg[tmpmsg[0]]['节点'] ['容器'] ['处理器']= { }
                # if tmpmsg[1] != '0.0TFLOPS':
                if '处理器1' not in lomsg[tmpmsg[0]]['节点']['容器']:
                    lomsg[tmpmsg[0]]['节点']['容器']['处理器1'] = {}
                lomsg[tmpmsg[0]]['节点']['容器']['处理器1']['类型'] = 'CPU'
                lomsg[tmpmsg[0]]['节点']['容器']['处理器1']['FLOPS'] = tmpmsg[1]
            elif topic == 'mqtt/system/GPUFLOPS':
                tmpmsg = msg.payload.decode().split(':')
                if '容器' not in lomsg[tmpmsg[0]]['节点']:
                    lomsg[tmpmsg[0]]['节点']['容器'] = {}
                # if tmpmsg[1] != '0.0TFLOPS':
                if '处理器2' not in lomsg[tmpmsg[0]]['节点']['容器']:
                    lomsg[tmpmsg[0]]['节点']['容器']['处理器2'] = {}
                lomsg[tmpmsg[0]]['节点']['容器']['处理器2']['类型'] = 'GPU'
                lomsg[tmpmsg[0]]['节点']['容器']['处理器2']['FLOPS'] = tmpmsg[1]
            elif topic == 'mqtt/system/TPUFLOPS':
                tmpmsg = msg.payload.decode().split(':')
                if '容器' not in lomsg[tmpmsg[0]]['节点']:
                    lomsg[tmpmsg[0]]['节点']['容器'] = {}
                # if tmpmsg[1] != '0.0TFLOPS':
                if '处理器3' not in lomsg[tmpmsg[0]]['节点']['容器']:
                    lomsg[tmpmsg[0]]['节点']['容器']['处理器3'] = {}
                lomsg[tmpmsg[0]]['节点']['容器']['处理器3']['类型'] = 'TPU'
                lomsg[tmpmsg[0]]['节点']['容器']['处理器3']['FLOPS'] = tmpmsg[1]

                # memory
            elif topic == 'mqtt/system/Internal_storage':
                tmpmsg = msg.payload.decode().split(':')
                if '容器' not in lomsg[tmpmsg[0]]['节点']:
                    lomsg[tmpmsg[0]]['节点']['容器'] = {}
                if '存储1' not in lomsg[tmpmsg[0]]['节点']['容器']:
                    lomsg[tmpmsg[0]]['节点']['容器']['存储1'] = {}
                lomsg[tmpmsg[0]]['节点']['容器']['存储1']['类型'] = '内存'
                lomsg[tmpmsg[0]]['节点']['容器']['存储1']['字节数'] = tmpmsg[1]
            elif topic == 'mqtt/system/External_storage':
                tmpmsg = msg.payload.decode().split(':')
                if '容器' not in lomsg[tmpmsg[0]]['节点']:
                    lomsg[tmpmsg[0]]['节点']['容器'] = {}
                if '存储2' not in lomsg[tmpmsg[0]]['节点']['容器']:
                    lomsg[tmpmsg[0]]['节点']['容器']['存储2'] = {}
                lomsg[tmpmsg[0]]['节点']['容器']['存储2']['类型'] = '外存'
                lomsg[tmpmsg[0]]['节点']['容器']['存储2']['字节数'] = tmpmsg[1]
            elif topic == 'mqtt/system/Cache':
                tmpmsg = msg.payload.decode().split(':')
                if '容器' not in lomsg[tmpmsg[0]]['节点']:
                    lomsg[tmpmsg[0]]['节点']['容器'] = {}
                if '存储3' not in lomsg[tmpmsg[0]]['节点']['容器']:
                    lomsg[tmpmsg[0]]['节点']['容器']['存储3'] = {}
                lomsg[tmpmsg[0]]['节点']['容器']['存储3']['类型'] = '缓存'
                lomsg[tmpmsg[0]]['节点']['容器']['存储3']['字节数'] = tmpmsg[1]

                # network
            elif topic == 'mqtt/system/Throughput_up':
                tmpmsg = msg.payload.decode().split(':')
                # print(tmpmsg)
                if '容器' not in lomsg[tmpmsg[0]]['节点']:
                    lomsg[tmpmsg[0]]['节点']['容器'] = {}
                if '网络1' not in lomsg[tmpmsg[0]]['节点']['容器']:
                    lomsg[tmpmsg[0]]['节点']['容器']['网络1'] = {}
                if '最小最大吞吐率' not in lomsg[tmpmsg[0]]['节点']['容器']['网络1']:
                    lomsg[tmpmsg[0]]['节点']['容器']['网络1']['最小最大吞吐率'] = {}
                if '网络2' not in lomsg[tmpmsg[0]]['节点']['容器']:
                    lomsg[tmpmsg[0]]['节点']['容器']['网络2'] = {}
                if '最小最大吞吐率' not in lomsg[tmpmsg[0]]['节点']['容器']['网络2']:
                    lomsg[tmpmsg[0]]['节点']['容器']['网络2']['最小最大吞吐率'] = {}
                if '网络3' not in lomsg[tmpmsg[0]]['节点']['容器']:
                    lomsg[tmpmsg[0]]['节点']['容器']['网络3'] = {}
                if '最小最大吞吐率' not in lomsg[tmpmsg[0]]['节点']['容器']['网络3']:
                    lomsg[tmpmsg[0]]['节点']['容器']['网络3']['最小最大吞吐率'] = {}
                lomsg[tmpmsg[0]]['节点']['容器']['网络1']['支持的网络协议'] = 'Bluetooth'
                lomsg[tmpmsg[0]]['节点']['容器']['网络1']['最小最大吞吐率']['上行'] = tmpmsg[1]
                lomsg[tmpmsg[0]]['节点']['容器']['网络2']['支持的网络协议'] = 'TCP/IP'
                lomsg[tmpmsg[0]]['节点']['容器']['网络2']['最小最大吞吐率']['上行'] = tmpmsg[2]
                lomsg[tmpmsg[0]]['节点']['容器']['网络3']['支持的网络协议'] = 'Modbus'
                lomsg[tmpmsg[0]]['节点']['容器']['网络3']['最小最大吞吐率']['上行'] = tmpmsg[3]
            elif topic == 'mqtt/system/Throughput_down':
                tmpmsg = msg.payload.decode().split(':')
                if '容器' not in lomsg[tmpmsg[0]]['节点']:
                    lomsg[tmpmsg[0]]['节点']['容器'] = {}
                if '网络1' not in lomsg[tmpmsg[0]]['节点']['容器']:
                    lomsg[tmpmsg[0]]['节点']['容器']['网络1'] = {}
                if '最小最大吞吐率' not in lomsg[tmpmsg[0]]['节点']['容器']['网络1']:
                    lomsg[tmpmsg[0]]['节点']['容器']['网络1']['最小最大吞吐率'] = {}
                if '网络2' not in lomsg[tmpmsg[0]]['节点']['容器']:
                    lomsg[tmpmsg[0]]['节点']['容器']['网络2'] = {}
                if '最小最大吞吐率' not in lomsg[tmpmsg[0]]['节点']['容器']['网络2']:
                    lomsg[tmpmsg[0]]['节点']['容器']['网络2']['最小最大吞吐率'] = {}
                if '网络3' not in lomsg[tmpmsg[0]]['节点']['容器']:
                    lomsg[tmpmsg[0]]['节点']['容器']['网络3'] = {}
                if '最小最大吞吐率' not in lomsg[tmpmsg[0]]['节点']['容器']['网络3']:
                    lomsg[tmpmsg[0]]['节点']['容器']['网络3']['最小最大吞吐率'] = {}
                lomsg[tmpmsg[0]]['节点']['容器']['网络1']['支持的网络协议'] = 'Bluetooth'
                lomsg[tmpmsg[0]]['节点']['容器']['网络1']['最小最大吞吐率']['下行'] = tmpmsg[1]
                lomsg[tmpmsg[0]]['节点']['容器']['网络2']['支持的网络协议'] = 'TCP/IP'
                lomsg[tmpmsg[0]]['节点']['容器']['网络2']['最小最大吞吐率']['下行'] = tmpmsg[2]
                lomsg[tmpmsg[0]]['节点']['容器']['网络3']['支持的网络协议'] = 'Modbus'
                lomsg[tmpmsg[0]]['节点']['容器']['网络3']['最小最大吞吐率']['下行'] = tmpmsg[3]
            elif topic == 'mqtt/system/Latency':
                tmpmsg = msg.payload.decode().split(':')
                if '容器' not in lomsg[tmpmsg[0]]['节点']:
                    lomsg[tmpmsg[0]]['节点']['容器'] = {}
                if '网络1' not in lomsg[tmpmsg[0]]['节点']['容器']:
                    lomsg[tmpmsg[0]]['节点']['容器']['网络1'] = {}
                if '网络2' not in lomsg[tmpmsg[0]]['节点']['容器']:
                    lomsg[tmpmsg[0]]['节点']['容器']['网络2'] = {}
                if '网络3' not in lomsg[tmpmsg[0]]['节点']['容器']:
                    lomsg[tmpmsg[0]]['节点']['容器']['网络3'] = {}
                lomsg[tmpmsg[0]]['节点']['容器']['网络1']['支持的网络协议'] = 'Bluetooth'
                lomsg[tmpmsg[0]]['节点']['容器']['网络1']['最小最大延迟'] = tmpmsg[1]
                lomsg[tmpmsg[0]]['节点']['容器']['网络2']['支持的网络协议'] = 'TCP/IP'
                lomsg[tmpmsg[0]]['节点']['容器']['网络2']['最小最大延迟'] = tmpmsg[2]
                lomsg[tmpmsg[0]]['节点']['容器']['网络3']['支持的网络协议'] = 'Modbus'
                lomsg[tmpmsg[0]]['节点']['容器']['网络3']['最小最大延迟'] = tmpmsg[3]
                # # computerpower
            elif topic == 'mqtt/system/ComputerPower':
                tmpmsg = msg.payload.decode().split(':')
                if tmpmsg[0] not in lomsg:
                    lomsg[tmpmsg[0]] = {}
                if '节点' not in lomsg[tmpmsg[0]]:
                    lomsg[tmpmsg[0]]['节点'] = {}
                if '算力' not in lomsg[tmpmsg[0]]['节点']:
                    lomsg[tmpmsg[0]]['节点']['算力'] = {}
                if '图像分类' not in lomsg[tmpmsg[0]]['节点']['算力']:
                    lomsg[tmpmsg[0]]['节点']['算力']['图像分类'] = {}
                if '实例分割' not in lomsg[tmpmsg[0]]['节点']['算力']:
                    lomsg[tmpmsg[0]]['节点']['算力']['实例分割'] = {}
                if '医疗图像分割' not in lomsg[tmpmsg[0]]['节点']['算力']:
                    lomsg[tmpmsg[0]]['节点']['算力']['医疗图像分割'] = {}
                if '目标检测' not in lomsg[tmpmsg[0]]['节点']['算力']:
                    lomsg[tmpmsg[0]]['节点']['算力']['目标检测'] = {}
                if '自然语言处理' not in lomsg[tmpmsg[0]]['节点']['算力']:
                    lomsg[tmpmsg[0]]['节点']['算力']['自然语言处理'] = {}
                if '语音识别' not in lomsg[tmpmsg[0]]['节点']['算力']:
                    lomsg[tmpmsg[0]]['节点']['算力']['语音识别'] = {}
                if '智能推荐' not in lomsg[tmpmsg[0]]['节点']['算力']:
                    lomsg[tmpmsg[0]]['节点']['算力']['智能推荐'] = {}
                if '强化学习' not in lomsg[tmpmsg[0]]['节点']['算力']:
                    lomsg[tmpmsg[0]]['节点']['算力']['强化学习'] = {}
                lomsg[tmpmsg[0]]['节点']['算力']['图像分类']['算力值'] = tmpmsg[1]
                lomsg[tmpmsg[0]]['节点']['算力']['实例分割']['算力值'] = tmpmsg[2]
                lomsg[tmpmsg[0]]['节点']['算力']['医疗图像分割']['算力值'] = tmpmsg[3]
                lomsg[tmpmsg[0]]['节点']['算力']['目标检测']['算力值'] = tmpmsg[4]
                lomsg[tmpmsg[0]]['节点']['算力']['自然语言处理']['算力值'] = tmpmsg[5]
                lomsg[tmpmsg[0]]['节点']['算力']['语音识别']['算力值'] = tmpmsg[6]
                lomsg[tmpmsg[0]]['节点']['算力']['智能推荐']['算力值'] = tmpmsg[7]
                lomsg[tmpmsg[0]]['节点']['算力']['强化学习']['算力值'] = tmpmsg[8]
            elif topic == 'NEW':
                pass
            json_to_xml(json.dumps(lomsg), xml_path, 'system')
            '''订阅消息回调函数'''

            '''TODO 新内容 资源基础利用'''
            if topic == 'mqtt/system/Attribute':
                tmpmsg = msg.payload.decode().split(':')
                if tmpmsg[0] not in resmsg:
                    resmsg[tmpmsg[0]] = {}
                if '节点' not in resmsg[tmpmsg[0]]:
                    resmsg[tmpmsg[0]]['节点'] = {} 
                    resmsg[tmpmsg[0]]['节点']['ID'] = {}                               
                resmsg[tmpmsg[0]]['节点']['ID'] = tmpmsg[1]
                
            # 算力
            elif topic == 'mqtt/system/ComputerPower':
                tmpmsg = msg.payload.decode().split(':')
                if tmpmsg[0] not in resmsg:
                    resmsg[tmpmsg[0]] = {}
                if '节点' not in resmsg[tmpmsg[0]]:
                    resmsg[tmpmsg[0]]['节点'] = {}
                if '算力' not in resmsg[tmpmsg[0]]['节点']:
                    resmsg[tmpmsg[0]]['节点']['算力'] = {}
                if '图像分类' not in resmsg[tmpmsg[0]]['节点']['算力']:
                    resmsg[tmpmsg[0]]['节点']['算力']['图像分类'] = {}
                    resmsg[tmpmsg[0]]['节点']['算力']['图像分类']['总算力'] = tmpmsg[1]
                if '实例分割' not in resmsg[tmpmsg[0]]['节点']['算力']:
                    resmsg[tmpmsg[0]]['节点']['算力']['实例分割'] = {}
                    resmsg[tmpmsg[0]]['节点']['算力']['实例分割']['总算力'] = tmpmsg[2]
                if '医疗图像分割' not in resmsg[tmpmsg[0]]['节点']['算力']:
                    resmsg[tmpmsg[0]]['节点']['算力']['医疗图像分割'] = {}
                    resmsg[tmpmsg[0]]['节点']['算力']['医疗图像分割']['总算力'] = tmpmsg[3]
                if '目标检测' not in resmsg[tmpmsg[0]]['节点']['算力']:
                    resmsg[tmpmsg[0]]['节点']['算力']['目标检测'] = {}
                    resmsg[tmpmsg[0]]['节点']['算力']['目标检测']['总算力'] = tmpmsg[4]
                if '自然语言处理' not in resmsg[tmpmsg[0]]['节点']['算力']:
                    resmsg[tmpmsg[0]]['节点']['算力']['自然语言处理'] = {}
                    resmsg[tmpmsg[0]]['节点']['算力']['自然语言处理']['总算力'] = tmpmsg[5]
                if '语音识别' not in resmsg[tmpmsg[0]]['节点']['算力']:
                    resmsg[tmpmsg[0]]['节点']['算力']['语音识别'] = {}
                    resmsg[tmpmsg[0]]['节点']['算力']['语音识别']['总算力'] = tmpmsg[6]
                if '智能推荐' not in resmsg[tmpmsg[0]]['节点']['算力']:
                    resmsg[tmpmsg[0]]['节点']['算力']['智能推荐'] = {}
                    resmsg[tmpmsg[0]]['节点']['算力']['智能推荐']['总算力'] = tmpmsg[7]
                if '强化学习' not in resmsg[tmpmsg[0]]['节点']['算力']:
                    resmsg[tmpmsg[0]]['节点']['算力']['强化学习'] = {}
                    resmsg[tmpmsg[0]]['节点']['算力']['强化学习']['总算力'] = tmpmsg[8]
                # print(tmpmsg[1])
                # print(type(tmpmsg[1]))
                # print(float(tmpmsg[1]))
                resmsg[tmpmsg[0]]['节点']['算力']['图像分类']['已分配'] = float(resmsg[tmpmsg[0]]['节点']['算力']['图像分类']['总算力']) - float(tmpmsg[1])
                resmsg[tmpmsg[0]]['节点']['算力']['实例分割']['已分配'] = float(resmsg[tmpmsg[0]]['节点']['算力']['图像分类']['总算力']) - float(tmpmsg[2])
                resmsg[tmpmsg[0]]['节点']['算力']['医疗图像分割']['已分配'] = float(resmsg[tmpmsg[0]]['节点']['算力']['图像分类']['总算力']) - float(tmpmsg[3])
                resmsg[tmpmsg[0]]['节点']['算力']['目标检测']['已分配'] = float(resmsg[tmpmsg[0]]['节点']['算力']['图像分类']['总算力']) - float(tmpmsg[4])
                resmsg[tmpmsg[0]]['节点']['算力']['自然语言处理']['已分配'] = float(resmsg[tmpmsg[0]]['节点']['算力']['图像分类']['总算力']) - float(tmpmsg[5])
                resmsg[tmpmsg[0]]['节点']['算力']['语音识别']['已分配'] = float(resmsg[tmpmsg[0]]['节点']['算力']['图像分类']['总算力']) - float(tmpmsg[6])
                resmsg[tmpmsg[0]]['节点']['算力']['智能推荐']['已分配'] = float(resmsg[tmpmsg[0]]['节点']['算力']['图像分类']['总算力']) - float(tmpmsg[7])
                resmsg[tmpmsg[0]]['节点']['算力']['强化学习']['已分配'] = float(resmsg[tmpmsg[0]]['节点']['算力']['图像分类']['总算力']) - float(tmpmsg[8])

            #存储
            elif topic == 'mqtt/system/Internal_storage':
                tmpmsg = msg.payload.decode().split(':')               
                # if tmpmsg[0] not in resmsg:
                #     resmsg[tmpmsg[0]] = {}             
                if '节点' not in resmsg[tmpmsg[0]]:
                    resmsg[tmpmsg[0]]['节点'] = {}
                if '容器' not in resmsg[tmpmsg[0]]['节点']:
                    resmsg[tmpmsg[0]]['节点']['容器'] = {}
                if '存储1' not in resmsg[tmpmsg[0]]['节点']:
                    resmsg[tmpmsg[0]]['节点']['容器']['存储1'] = {}
                if '内存' not in resmsg[tmpmsg[0]]['节点']['容器']['存储1']:
                    resmsg[tmpmsg[0]]['节点']['容器']['存储1'] = {}
                    resmsg[tmpmsg[0]]['节点']['容器']['存储1']['类型'] = '内存'
                    resmsg[tmpmsg[0]]['节点']['容器']['存储1']['总空间'] = tmpmsg[1]
                tmpstr = strToNum(resmsg[tmpmsg[0]]['节点']['容器']['存储1']['总空间'])- strToNum(tmpmsg[1])
                tmpstr = str(tmpstr) + 'GB'
                resmsg[tmpmsg[0]]['节点']['容器']['存储1']['已分配'] = tmpstr
                # print(resmsg[tmpmsg[0]]['节点']['容器']['存储1']['总空间'])    
                # print(tmpmsg[1])

            elif topic == 'mqtt/system/External_storage':
                tmpmsg = msg.payload.decode().split(':')
                if '容器' not in resmsg[tmpmsg[0]]['节点']:
                    resmsg[tmpmsg[0]]['节点']['容器'] = {}
                if '存储2' not in resmsg[tmpmsg[0]]['节点']:
                    resmsg[tmpmsg[0]]['节点']['容器']['存储2'] = {}
                if '内存' not in resmsg[tmpmsg[0]]['节点']['容器']['存储2']:
                    resmsg[tmpmsg[0]]['节点']['容器']['存储2'] = {}
                    resmsg[tmpmsg[0]]['节点']['容器']['存储2']['类型'] = '外存'
                    resmsg[tmpmsg[0]]['节点']['容器']['存储2']['总空间'] = tmpmsg[1]
                tmpstr = strToNum(resmsg[tmpmsg[0]]['节点']['容器']['存储2']['总空间'])- strToNum(tmpmsg[1])
                tmpstr = str(tmpstr) + 'GB'
                resmsg[tmpmsg[0]]['节点']['容器']['存储2']['已分配'] = tmpstr

            elif topic == 'mqtt/system/Cache':
                tmpmsg = msg.payload.decode().split(':')
                if '容器' not in resmsg[tmpmsg[0]]['节点']:
                    resmsg[tmpmsg[0]]['节点']['容器'] = {}
                if '存储3' not in resmsg[tmpmsg[0]]['节点']:
                    resmsg[tmpmsg[0]]['节点']['容器']['存储3'] = {}
                if '内存' not in resmsg[tmpmsg[0]]['节点']['容器']['存储3']:
                    resmsg[tmpmsg[0]]['节点']['容器']['存储3'] = {}
                    resmsg[tmpmsg[0]]['节点']['容器']['存储3']['类型'] = '缓存'
                    resmsg[tmpmsg[0]]['节点']['容器']['存储3']['总空间'] = tmpmsg[1]
                tmpstr = strToNum(resmsg[tmpmsg[0]]['节点']['容器']['存储3']['总空间'])- strToNum(tmpmsg[1])
                tmpstr = str(tmpstr) + 'GB'
                resmsg[tmpmsg[0]]['节点']['容器']['存储3']['已分配'] = tmpstr   
            
            # 网络
            elif topic == 'mqtt/system/Throughput_up':
                tmpmsg = msg.payload.decode().split(':')
                # print(tmpmsg)
                if '容器' not in resmsg[tmpmsg[0]]['节点']:
                    resmsg[tmpmsg[0]]['节点']['容器'] = {}
                if '网络1' not in resmsg[tmpmsg[0]]['节点']['容器']:
                    resmsg[tmpmsg[0]]['节点']['容器']['网络1'] = {}
                if '带宽' not in resmsg[tmpmsg[0]]['节点']['容器']['网络1']:
                    resmsg[tmpmsg[0]]['节点']['容器']['网络1']['带宽'] = {}
                if '网络2' not in resmsg[tmpmsg[0]]['节点']['容器']:
                    resmsg[tmpmsg[0]]['节点']['容器']['网络2'] = {}
                if '带宽' not in resmsg[tmpmsg[0]]['节点']['容器']['网络2']:
                    resmsg[tmpmsg[0]]['节点']['容器']['网络2']['带宽'] = {}
                if '网络3' not in resmsg[tmpmsg[0]]['节点']['容器']:
                    resmsg[tmpmsg[0]]['节点']['容器']['网络3'] = {}
                if '带宽' not in resmsg[tmpmsg[0]]['节点']['容器']['网络3']:
                    resmsg[tmpmsg[0]]['节点']['容器']['网络3']['带宽'] = {}
                resmsg[tmpmsg[0]]['节点']['容器']['网络1']['支持的网络协议'] = 'Bluetooth'
                resmsg[tmpmsg[0]]['节点']['容器']['网络1']['带宽']['上行'] = tmpmsg[1]
                resmsg[tmpmsg[0]]['节点']['容器']['网络2']['支持的网络协议'] = 'TCP/IP'
                resmsg[tmpmsg[0]]['节点']['容器']['网络2']['带宽']['上行'] = tmpmsg[2]
                resmsg[tmpmsg[0]]['节点']['容器']['网络3']['支持的网络协议'] = 'Modbus'
                resmsg[tmpmsg[0]]['节点']['容器']['网络3']['带宽']['上行'] = tmpmsg[3]

            elif topic == 'mqtt/system/Throughput_down':
                tmpmsg = msg.payload.decode().split(':')
                if '容器' not in resmsg[tmpmsg[0]]['节点']:
                    resmsg[tmpmsg[0]]['节点']['容器'] = {}
                if '网络1' not in resmsg[tmpmsg[0]]['节点']['容器']:
                    resmsg[tmpmsg[0]]['节点']['容器']['网络1'] = {}
                if '带宽' not in resmsg[tmpmsg[0]]['节点']['容器']['网络1']:
                    resmsg[tmpmsg[0]]['节点']['容器']['网络1']['带宽'] = {}
                if '网络2' not in resmsg[tmpmsg[0]]['节点']['容器']:
                    resmsg[tmpmsg[0]]['节点']['容器']['网络2'] = {}
                if '带宽' not in resmsg[tmpmsg[0]]['节点']['容器']['网络2']:
                    resmsg[tmpmsg[0]]['节点']['容器']['网络2']['带宽'] = {}
                if '网络3' not in resmsg[tmpmsg[0]]['节点']['容器']:
                    resmsg[tmpmsg[0]]['节点']['容器']['网络3'] = {}
                if '带宽' not in resmsg[tmpmsg[0]]['节点']['容器']['网络3']:
                    resmsg[tmpmsg[0]]['节点']['容器']['网络3']['带宽'] = {}
                resmsg[tmpmsg[0]]['节点']['容器']['网络1']['支持的网络协议'] = 'Bluetooth'
                resmsg[tmpmsg[0]]['节点']['容器']['网络1']['带宽']['下行'] = tmpmsg[1]
                resmsg[tmpmsg[0]]['节点']['容器']['网络2']['支持的网络协议'] = 'TCP/IP'
                resmsg[tmpmsg[0]]['节点']['容器']['网络2']['带宽']['下行'] = tmpmsg[2]
                resmsg[tmpmsg[0]]['节点']['容器']['网络3']['支持的网络协议'] = 'Modbus'
                resmsg[tmpmsg[0]]['节点']['容器']['网络3']['带宽']['下行'] = tmpmsg[3]    
            elif topic == 'NEW':
                pass
            json_to_xml(json.dumps(resmsg), xml_path, 'res')   
            # print('tmpmsg',tmpmsg)

        # 订阅指定消息主题
        for topic in self.topics:
            self.client.subscribe(topic)
            # print(topic)
        self.client.on_message = on_message

    def run(
            self,
    ):
        '''运行'''
        self.connect_mqtt()
        """ 接受各种检测信息 """
        self.subscribe()
        # 运行一个线程来自动调用loop()处理网络事件, 非阻塞
        # self.client.loop_start()
        self.client.loop_forever()
        # self.publish()


def jsonToXml(json_dic, type):
    xml_str = ""
    try:
        if type == 'task':
            # if json_dic == {}
            xml_str = xmltodict.unparse({'任务信息': json_dic}, encoding='utf-8', pretty=True)
        elif type == 'system':
            xml_str = xmltodict.unparse({'系统信息': json_dic}, encoding='utf-8')
        elif type == 'res':
            xml_str = xmltodict.unparse({'资源基础利用': json_dic}, encoding='utf-8')
        elif type == 'task_off_res':
            xml_str = xmltodict.unparse({'任务位置': json_dic}, encoding='utf-8')
        elif type == 'task_off_res1':
            xml_str = xmltodict.unparse({'资源调度结果': json_dic}, encoding='utf-8')
    except:
        if type == 'task':
            # if json_dic == {}
            xml_str = xmltodict.unparse({'任务信息': json_dic}, encoding='utf-8', pretty=True)
        elif type == 'system':
            xml_str = xmltodict.unparse({'系统信息': json_dic}, encoding='utf-8')
        elif type == 'res':
            xml_str = xmltodict.unparse({'资源基础利用': json_dic}, encoding='utf-8')
        elif type == 'task_off_res':
            xml_str = xmltodict.unparse({'任务位置': json_dic}, encoding='utf-8')
        elif type == 'task_off_res1':
            xml_str = xmltodict.unparse({'资源调度结果': json_dic}, encoding='utf-8')
    finally:
        return xml_str


def json_to_xml(json_str, xml_path, type):
    if not os.path.exists(xml_path):
        os.makedirs(xml_path)
    load_dict = json.loads(json_str)
    # print(load_dict)
    json_result = jsonToXml(load_dict, type)
    try:
        dom = parseString(json_result)
    except:
        if type == 'task':
            dom = parseString(xmltodict.unparse({'任务信息': ''}, encoding='utf-8', pretty=True))
        elif type == 'system':
            dom = parseString(xmltodict.unparse({'系统': ''}, encoding='utf-8'))
        elif type == 'res':
            dom = parseString(xmltodict.unparse({'资源基础利用': ''}, encoding='utf-8'))
        elif type == 'task_off_res':
            dom = parseString(xmltodict.unparse({'任务位置': ''}, encoding='utf-8'))
        elif type == 'task_off_res1':
            dom = parseString(xmltodict.unparse({'资源调度结果': ''}, encoding='utf-8'))
    if type == 'task':
        # f = open(os.path.join(xml_path, str(pre) + ".xml"), 'w', encoding="UTF-8") # 冗余生成
        f = open(os.path.join(xml_path, "task_info.xml"), 'w', encoding="UTF-8")  # 覆盖
        f.write(dom.toprettyxml())
        f.close()
    elif type == 'system':
        f = open(os.path.join(xml_path, "system_info.xml"), 'w', encoding="UTF-8")  # 覆盖
        f.write(dom.toprettyxml())
        f.close()
    elif type == 'res':
        f = open(os.path.join(xml_path, "res_info.xml"), 'w', encoding="UTF-8")  # 覆盖
        f.write(dom.toprettyxml())
        f.close()
    elif type == 'task_off_res':
        f = open(os.path.join(xml_path, "task_off_res.xml"), 'w', encoding="UTF-8")  # 覆盖
        f.write(dom.toprettyxml())
        f.close()
    elif type == 'task_off_res1':
        f = open(os.path.join(xml_path, "task_off_res1.xml"), 'w', encoding="UTF-8")  # 覆盖
        f.write(dom.toprettyxml())
        f.close()

if __name__ == '__main__':
    server = ServerAgent(
        keepalive=keepalive,
        broker=brokerIP,
        port=port,
        clientID=clientID,
        topics=topics,
    )

    server.run()
