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

# xml_path = "C:\KubeEdge\js-client"
xml_path = r"node_info/templates/node_info"
lomsg = {}
lomsg1 = {}
lomsg2 = {}
lomsg3 = {}
resmsg = {}
"""TODO+ 依据标准增加更多内容"""
topics = [

    'mqtt/system/Attribute',

    'mqtt/system/Computing_Power_Configuration/Computing_Units_Set/Processor/CPU_Specifications',
    'mqtt/system/Computing_Power_Configuration/Computing_Units_Set/Processor/GPU_Specifications',
    'mqtt/system/Computing_Power_Configuration/Computing_Units_Set/Processor/FPGA_Specifications',
    'mqtt/system/Computing_Power_Configuration/Computing_Units_Set/Processor/TPU_Specifications',
    'mqtt/system/Computing_Power_Configuration/Computing_Units_Set/Processor/Frequency_Set/Frequency',

    'mqtt/system/Computing_Power_Configuration/Computing_Units_Set/Processor/Speed_Set/Speed_Attributes',

    'mqtt/system/Computing_Power_Configuration/Computing_Units_Set/Memory/Specifications',


    'mqtt/system/Computing_Power_Configuration/Communicate_Units_Set/Communicate_Unit/Specifications',

    'mqtt/system/Computing_Power_Configuration/Storage_Units_Set/Storage_Unit/Specifications',

    'mqtt/system/Computing_Power_Configuration/Computing_Power',

    'mqtt/system/Terminal_Device_or_not',
    # 资源占用新加
    'mqtt/system/Usage',
    'mqtt/system/Computing_Power_Configuration/Software_env',

]

# 启动节点相关操作
server_topics = [
    'mqtt/server/start',
    'mqtt/server/stop',
    'mqtt/server/delete',
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

#修改字典，使其符合标准格式
def node_nested_dict(data):
    if isinstance(data, dict):
        new_dict = {}
        for key, value in data.items():
            # 递归处理值，如果值是字典的话
            processed_value = process_nested_dict(value)
            if '节点' in key:
                new_key = '节点'
                if new_key in new_dict:
                    if isinstance(new_dict[new_key], list):
                        new_dict[new_key].append(processed_value)
                    else:
                        new_dict[new_key] = [new_dict[new_key], processed_value]
                else:
                    new_dict[new_key] = processed_value
            else:
                new_dict[key] = processed_value
        return new_dict
    return data
def process_nested_dict(data):
    data=node_nested_dict(data)
    if isinstance(data, dict):
        new_dict = {}
        for key, value in data.items():
            # 递归处理值，如果值是字典的话
            processed_value = process_nested_dict(value)
            if '处理器' in key and key !='处理器占用率' and key !='流处理器数量':
                new_key = '处理器'
                if new_key in new_dict:
                    if isinstance(new_dict[new_key], list):
                        new_dict[new_key].append(processed_value)
                    else:
                        new_dict[new_key] = [new_dict[new_key], processed_value]
                else:
                    new_dict[new_key] = processed_value
            else:
                new_dict[key] = processed_value
        return new_dict
    return data

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
            server_topics: list = [
                'mqtt/server/start',
            ],
            task_ctl: list = [
                'mqtt/task/class'
            ],
    ) -> object:
        self.client = None
        self.topics = topics
        self.server_topics = server_topics
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
                print("Failed to connect, return code ", rc)

        # 连接mqtt代理服务器，并获取连接引用
        self.client = mqtt_client.Client(self.clientID)
        self.client.on_connect = on_connect
        self.client.connect(self.broker, self.port, self.keepalive)

    def disconnect_mqtt(self):
        '''关闭mqtt连接'''
        self.client.disconnect()
        print("Disconnected from MQTT")

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
                    # if tmpmsg[i] != '0':
                    #     lomsg1[task_str][tmpmsg[0]]['构成']['模型']['操作数'][operands[i - 2]] = tmpmsg[i]
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
                if tmpmsg[2]:
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
                if tmpmsg[2]:
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
                if tmpmsg[2]:
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
                if task_str + tmpmsg[0] in lomsg2['offloadingRes']:
                    del lomsg2['offloadingRes'][task_str + tmpmsg[0]]
                task_types = ['云端任务', '边缘端任务', '终端任务']
                for task_type in task_types:
                    if task_type in lomsg3:
                        if '分配' + tmpmsg[1] in lomsg3[task_type]:
                            del lomsg3[task_type]['分配' + tmpmsg[1]]

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
                if '分配' + subtask_id not in lomsg3[task_type]:
                    lomsg3[task_type]['分配' + subtask_id] = {}
                if '任务ID' not in lomsg3[task_type]['分配' + subtask_id]:
                    lomsg3[task_type]['分配' + subtask_id]['任务ID'] = {}
                if '节点ID' not in lomsg3[task_type]['分配' + subtask_id]:
                    lomsg3[task_type]['分配' + subtask_id]['节点ID'] = {}
                lomsg3[task_type]['分配' + subtask_id]['任务ID'] = subtask_id
                lomsg3[task_type]['分配' + subtask_id]['节点ID'] = device_id
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
            # print(lomsg1)
            json_to_xml(json.dumps(lomsg1), xml_path, 'task')
            json_to_xml(json.dumps(lomsg2), xml_path, 'task_off_res')
            json_to_xml(json.dumps(lomsg3), xml_path, 'task_off_res1')

            '''订阅消息回调函数'''

            if topic == 'mqtt/system/Attribute':
                tmpmsg = msg.payload.decode().split(':')
                node_name = '节点' + tmpmsg[0]
                node_dict={}
                if node_name not in lomsg:
                    lomsg[node_name] = {}
                if '@URL' not in lomsg[node_name]:
                    lomsg[node_name]['@URI'] = {}
                if '@ID' not in lomsg[node_name]:
                    lomsg[node_name]['@ID'] = {}
                if '@单价' not in lomsg[node_name]:
                    lomsg[node_name]['@单价'] = {}
                if '@优先级' not in lomsg[node_name]:
                    lomsg[node_name]['@优先级'] = {}
                lomsg[node_name]['@URI'] = tmpmsg[1]
                lomsg[node_name]['@ID'] = tmpmsg[2]
                lomsg[node_name]['@单价'] = tmpmsg[3]
                lomsg[node_name]['@优先级'] = tmpmsg[4]
                # processor
            elif topic == 'mqtt/system/System_Computing_power':
                tmpmsg = msg.payload.decode().split(':')
                if tmpmsg[0] not in lomsg:
                    lomsg[tmpmsg[0]] = {}
                if '节点' not in lomsg[tmpmsg[0]]:
                    lomsg[tmpmsg[0]]['节点'] = {}
                if '系统算力值' not in lomsg[tmpmsg[0]]['节点']:
                    lomsg[tmpmsg[0]]['节点']['系统算力值'] = tmpmsg[1]

            elif topic == 'mqtt/system/Computing_Power_Configuration/Computing_Units_Set/Processor/CPU_Specifications':
                tmpmsg = msg.payload.decode().split(';')
                for cpu in tmpmsg:
                    cpu=cpu.split(':')
                    node_name = '节点' + cpu[0]
                    processor_name = '处理器' + cpu[1]
                    if node_name not in lomsg:
                        lomsg[node_name] = {}
                    if '算力配置' not in lomsg[node_name]:
                        lomsg[node_name]['算力配置'] = {}
                    if '计算单元集合' not in lomsg[node_name]['算力配置']:
                        lomsg[node_name]['算力配置']['计算单元集合'] = {}
                    if processor_name not in lomsg[node_name]['算力配置']['计算单元集合']:
                        lomsg[node_name]['算力配置']['计算单元集合'][processor_name] = {}

                    if '类型' not in lomsg[node_name]['算力配置']['计算单元集合'][processor_name]:
                        lomsg[node_name]['算力配置']['计算单元集合'][processor_name]['类型'] = {}
                    if 'CPU' not in lomsg[node_name]['算力配置']['计算单元集合'][processor_name]['类型']:
                        lomsg[node_name]['算力配置']['计算单元集合'][processor_name]['类型']['CPU'] = {}
                    lomsg[node_name]['算力配置']['计算单元集合'][processor_name]['类型']['CPU']['加速指令能力'] = []
                    lomsg[node_name]['算力配置']['计算单元集合'][processor_name]['@ID'] = cpu[1]
                    acce_capabilitys = cpu[2].split(',')
                    for acce_capability in acce_capabilitys:
                        lomsg[node_name]['算力配置']['计算单元集合'][processor_name]['类型']['CPU']['加速指令能力'].append(acce_capability)
                    lomsg[node_name]['算力配置']['计算单元集合'][processor_name]['类型']['CPU']['内核基频'] = cpu[3]
                    lomsg[node_name]['算力配置']['计算单元集合'][processor_name]['类型']['CPU']['内核数'] = cpu[4]
                    lomsg[node_name]['算力配置']['计算单元集合'][processor_name]['类型']['CPU']['架构'] = cpu[5]
                    lomsg[node_name]['算力配置']['计算单元集合'][processor_name]['类型']['CPU']['一级缓存'] = cpu[6]
                    lomsg[node_name]['算力配置']['计算单元集合'][processor_name]['类型']['CPU']['二级缓存'] = cpu[7]
                    lomsg[node_name]['算力配置']['计算单元集合'][processor_name]['类型']['CPU']['三级缓存'] = cpu[8]
                    lomsg[node_name]['算力配置']['计算单元集合'][processor_name]['类型']['CPU']['总线'] = cpu[9]
                    lomsg[node_name]['算力配置']['计算单元集合'][processor_name]['类型']['CPU']['线程数'] = cpu[10]
                    if '速度集合' not in lomsg[node_name]['算力配置']['计算单元集合'][processor_name]:
                        lomsg[node_name]['算力配置']['计算单元集合'][processor_name]['速度集合'] = {}
                    if '速度' not in lomsg[node_name]['算力配置']['计算单元集合'][processor_name]['速度集合']:
                        lomsg[node_name]['算力配置']['计算单元集合'][processor_name]['速度集合']['速度'] = []
                    flops,opertypes,digits = cpu[11].split(','),cpu[12].split(','),cpu[13].split(',')
                    for flop,opertype,digit in zip(flops,opertypes,digits):
                        if {'@每秒运算次数': flop, '@操作数类型': opertype, '@位数': digit} not in lomsg[node_name]['算力配置']['计算单元集合'][processor_name]['速度集合']['速度']:
                            lomsg[node_name]['算力配置']['计算单元集合'][processor_name]['速度集合']['速度'].append({'@每秒运算次数':flop,'@操作数类型':opertype,'@位数':digit})

            elif topic == 'mqtt/system/Computing_Power_Configuration/Computing_Units_Set/Processor/GPU_Specifications':
                if(msg.payload.decode()!=''):
                    tmpmsg = msg.payload.decode().split(';')
                    for gpu in tmpmsg:
                        gpu=gpu.split(':')
                        node_name = '节点' + gpu[0]
                        processor_name = '处理器' + gpu[1]
                        if node_name not in lomsg:
                            lomsg[node_name] = {}
                        if '算力配置' not in lomsg[node_name]:
                            lomsg[node_name]['算力配置'] = {}
                        if '计算单元集合' not in lomsg[node_name]['算力配置']:
                            lomsg[node_name]['算力配置']['计算单元集合'] = {}
                        if processor_name not in lomsg[node_name]['算力配置']['计算单元集合']:
                            lomsg[node_name]['算力配置']['计算单元集合'][processor_name] = {}

                        if '类型' not in lomsg[node_name]['算力配置']['计算单元集合'][processor_name]:
                            lomsg[node_name]['算力配置']['计算单元集合'][processor_name]['类型'] = {}
                        if 'GPU' not in lomsg[node_name]['算力配置']['计算单元集合'][processor_name]['类型']:
                            lomsg[node_name]['算力配置']['计算单元集合'][processor_name]['类型']['GPU'] = {}

                        lomsg[node_name]['算力配置']['计算单元集合'][processor_name]['@ID'] = gpu[1]
                        lomsg[node_name]['算力配置']['计算单元集合'][processor_name]['类型']['GPU']['显存大小'] = gpu[2]
                        lomsg[node_name]['算力配置']['计算单元集合'][processor_name]['类型']['GPU']['显存带宽'] = gpu[3]
                        lomsg[node_name]['算力配置']['计算单元集合'][processor_name]['类型']['GPU']['时钟频率'] = gpu[4]

                        if '支持的接口集合' not in lomsg[node_name]['算力配置']['计算单元集合'][processor_name]['类型']['GPU']:
                            lomsg[node_name]['算力配置']['计算单元集合'][processor_name]['类型']['GPU']['支持的接口集合'] = {}
                        if '接口' not in lomsg[node_name]['算力配置']['计算单元集合'][processor_name]['类型']['GPU']['支持的接口集合']:
                            lomsg[node_name]['算力配置']['计算单元集合'][processor_name]['类型']['GPU']['支持的接口集合']['接口'] = []
                        names,versions = gpu[5].split(','),gpu[6].split(',')
                        for name,version in zip(names,versions):
                            if {'@名称': name, '@版本号': version} not in lomsg[node_name]['算力配置']['计算单元集合'][processor_name]['类型']['GPU']['支持的接口集合']['接口']:
                                lomsg[node_name]['算力配置']['计算单元集合'][processor_name]['类型']['GPU']['支持的接口集合']['接口'].append({'@名称': name, '@版本号': version})

                        lomsg[node_name]['算力配置']['计算单元集合'][processor_name]['类型']['GPU']['流处理器数量'] = gpu[7]
                        if '速度集合' not in lomsg[node_name]['算力配置']['计算单元集合'][processor_name]:
                            lomsg[node_name]['算力配置']['计算单元集合'][processor_name]['速度集合'] = {}
                        if '速度' not in lomsg[node_name]['算力配置']['计算单元集合'][processor_name]['速度集合']:
                            lomsg[node_name]['算力配置']['计算单元集合'][processor_name]['速度集合']['速度'] = []
                        flops,opertypes,digits = gpu[8].split(','),gpu[9].split(','),gpu[10].split(',')
                        for flop,opertype,digit in zip(flops,opertypes,digits):
                            if {'@每秒运算次数': flop, '@操作数类型': opertype, '@位数': digit} not in lomsg[node_name]['算力配置']['计算单元集合'][processor_name]['速度集合']['速度']:
                                lomsg[node_name]['算力配置']['计算单元集合'][processor_name]['速度集合']['速度'].append({'@每秒运算次数':flop,'@操作数类型':opertype,'@位数':digit})

            elif topic == 'mqtt/system/Computing_Power_Configuration/Computing_Units_Set/Processor/FPGA_Specifications':
                if (msg.payload.decode() != ''):
                    tmpmsg = msg.payload.decode().split(';')
                    for fpga in tmpmsg:
                        fpga = fpga.split(':')
                        node_name = '节点' + fpga[0]
                        processor_name = '处理器' + fpga[1]
                        if node_name not in lomsg:
                            lomsg[node_name] = {}
                        if '算力配置' not in lomsg[node_name]:
                            lomsg[node_name]['算力配置'] = {}
                        if '计算单元集合' not in lomsg[node_name]['算力配置']:
                            lomsg[node_name]['算力配置']['计算单元集合'] = {}
                        if processor_name not in lomsg[node_name]['算力配置']['计算单元集合']:
                            lomsg[node_name]['算力配置']['计算单元集合'][processor_name] = {}

                        if '类型' not in lomsg[node_name]['算力配置']['计算单元集合'][processor_name]:
                            lomsg[node_name]['算力配置']['计算单元集合'][processor_name]['类型'] = {}
                        if 'FPGA' not in lomsg[node_name]['算力配置']['计算单元集合'][processor_name]['类型']:
                            lomsg[node_name]['算力配置']['计算单元集合'][processor_name]['类型']['FPGA'] = {}
                        lomsg[node_name]['算力配置']['计算单元集合'][processor_name]['@ID'] = fpga[1]
                        lomsg[node_name]['算力配置']['计算单元集合'][processor_name]['类型']['FPGA']['M20K存储器容量'] = fpga[2]
                        lomsg[node_name]['算力配置']['计算单元集合'][processor_name]['类型']['FPGA']['精度可调DSP模块'] = fpga[3]
                        lomsg[node_name]['算力配置']['计算单元集合'][processor_name]['类型']['FPGA']['逻辑单元LE'] = fpga[4]
                        lomsg[node_name]['算力配置']['计算单元集合'][processor_name]['类型']['FPGA']['ALM'] = fpga[5]

                        if '速度集合' not in lomsg[node_name]['算力配置']['计算单元集合'][processor_name]:
                            lomsg[node_name]['算力配置']['计算单元集合'][processor_name]['速度集合'] = {}
                        if '速度' not in lomsg[node_name]['算力配置']['计算单元集合'][processor_name]['速度集合']:
                            lomsg[node_name]['算力配置']['计算单元集合'][processor_name]['速度集合']['速度'] = []
                        flops, opertypes, digits = fpga[6].split(','), fpga[7].split(','), fpga[8].split(',')
                        for flop, opertype, digit in zip(flops, opertypes, digits):
                            if {'@每秒运算次数': flop, '@操作数类型': opertype, '@位数': digit} not in lomsg[node_name]['算力配置']['计算单元集合'][processor_name]['速度集合']['速度']:
                                lomsg[node_name]['算力配置']['计算单元集合'][processor_name]['速度集合']['速度'].append({'@每秒运算次数': flop, '@操作数类型': opertype, '@位数': digit})

            elif topic == 'mqtt/system/Computing_Power_Configuration/Computing_Units_Set/Memory/Specifications':
                tmpmsg = msg.payload.decode().split(':')
                node_name = '节点' + tmpmsg[0]
                if node_name not in lomsg:
                    lomsg[node_name] = {}
                if '算力配置' not in lomsg[node_name]:
                    lomsg[node_name]['算力配置'] = {}
                if '计算单元集合' not in lomsg[node_name]['算力配置']:
                    lomsg[node_name]['算力配置']['计算单元集合'] = {}
                if '内存' not in lomsg[node_name]['算力配置']['计算单元集合']:
                    lomsg[node_name]['算力配置']['计算单元集合']['内存'] = {}
                lomsg[node_name]['算力配置']['计算单元集合']['内存']['@ID'] = tmpmsg[1]
                lomsg[node_name]['算力配置']['计算单元集合']['内存']['@纠错方式'] = tmpmsg[2]
                lomsg[node_name]['算力配置']['计算单元集合']['内存']['容量'] = tmpmsg[3]
                lomsg[node_name]['算力配置']['计算单元集合']['内存']['内存带宽'] = tmpmsg[4]
                lomsg[node_name]['算力配置']['计算单元集合']['内存']['延迟'] = tmpmsg[5]
                lomsg[node_name]['算力配置']['计算单元集合']['内存']['类型'] = tmpmsg[6]
                lomsg[node_name]['算力配置']['计算单元集合']['内存']['通道数'] = tmpmsg[7]
            elif topic == 'mqtt/system/Computing_Power_Configuration/Communicate_Units_Set/Communicate_Unit/Specifications':
                tmpmsg = msg.payload.decode().split(';')
                for unit in tmpmsg:
                    unit = unit.split(':')
                    node_name = '节点' + unit[0]
                    if node_name not in lomsg:
                        lomsg[node_name] = {}
                    if '算力配置' not in lomsg[node_name]:
                        lomsg[node_name]['算力配置'] = {}
                    if '通信单元集合' not in lomsg[node_name]['算力配置']:
                        lomsg[node_name]['算力配置']['通信单元集合'] = {}
                    if '通信单元' not in lomsg[node_name]['算力配置']['通信单元集合']:
                        lomsg[node_name]['算力配置']['通信单元集合']['通信单元'] = []
                    com_unit = {}
                    if '网络带宽' not in com_unit:
                        com_unit['网络带宽'] = {}
                    com_unit['@ID'] = unit[1]
                    com_unit['网络带宽']['上行'] = unit[2]
                    com_unit['网络带宽']['下行'] = unit[3]
                    com_unit['时延'] = unit[4]
                    com_unit['FIB转发速率'] = unit[5]
                    com_unit['IPSec速率'] = unit[6]
                    com_unit['虚拟网络带宽'] = unit[7]
                    com_unit['防火墙损耗'] = unit[8]
                    com_unit['支持的网络协议']=[]
                    for protocal in unit[9].split(','):
                        com_unit['支持的网络协议'].append(protocal)
                    com_unit['DPDK-L3转发速率'] = unit[10]
                    com_unit['可靠性'] = unit[11]
                    is_exist = 0
                    for exist_unit in lomsg[node_name]['算力配置']['通信单元集合']['通信单元']:
                        if (exist_unit['@ID'] == com_unit['@ID']):
                            is_exist = 1
                            exist_unit.update(com_unit)
                            break
                    if (is_exist == 0):
                        lomsg[node_name]['算力配置']['通信单元集合']['通信单元'].append(com_unit)
            elif topic == 'mqtt/system/Computing_Power_Configuration/Storage_Units_Set/Storage_Unit/Specifications':
                tmpmsg = msg.payload.decode().split(';')
                for unit in tmpmsg:
                    unit=unit.split(':')
                    node_name = '节点' + unit[0]
                    if node_name not in lomsg:
                        lomsg[node_name] = {}
                    if '算力配置' not in lomsg[node_name]:
                        lomsg[node_name]['算力配置'] = {}
                    if '存储单元集合' not in lomsg[node_name]['算力配置']:
                        lomsg[node_name]['算力配置']['存储单元集合'] = {}
                    if '存储单元' not in lomsg[node_name]['算力配置']['存储单元集合']:
                        lomsg[node_name]['算力配置']['存储单元集合']['存储单元'] = []
                    store_unit={}
                    store_unit['@ID'] = unit[1]
                    store_unit['容量'] = unit[2]
                    store_unit['存储带宽'] = unit[3]
                    store_unit['IOPS'] = unit[4]
                    store_unit['备份数量'] = unit[5]
                    store_unit['可靠性'] = unit[6]
                    store_unit['存储架构'] = unit[7]
                    store_unit['RAID级别'] = unit[8]
                    store_unit['冗余方式'] = unit[9]
                    is_exist=0
                    for exist_unit in lomsg[node_name]['算力配置']['存储单元集合']['存储单元']:
                        if(exist_unit['@ID']==store_unit['@ID']):
                            #ID相同，用store_unit更新字典中的exist_unit
                            exist_unit.update(store_unit)
                            is_exist=1
                            break
                    #ID不同则加入
                    if(is_exist==0):
                        lomsg[node_name]['算力配置']['存储单元集合']['存储单元'].append(store_unit)
            elif topic == 'mqtt/system/Computing_Power_Configuration/Computing_Power':
                tmpmsg = msg.payload.decode().split(':')
                node_name = '节点' + tmpmsg[0]
                if node_name not in lomsg:
                    lomsg[node_name] = {}
                if '算力配置' not in lomsg[node_name]:
                    lomsg[node_name]['算力配置'] = {}
                lomsg[node_name]['算力配置']['算力值'] = tmpmsg[1]
            elif topic == 'mqtt/system/Computing_Power_Configuration/Software_env':
                tmpmsg = msg.payload.decode().split(':')
                node_name = '节点' + tmpmsg[0]
                if node_name not in lomsg:
                    lomsg[node_name] = {}
                if '算力配置' not in lomsg[node_name]:
                    lomsg[node_name]['算力配置'] = {}
                lomsg[node_name]['算力配置']['软件环境'] = tmpmsg[1]
            elif topic == 'mqtt/system/Terminal_Device_or_not':
                tmpmsg = msg.payload.decode().split(':')
                node_name = '节点' + tmpmsg[0]
                if node_name not in lomsg:
                    lomsg[node_name] = {}
                if tmpmsg[1] == '1' and '非终端设备' not in lomsg[node_name]:
                    if '终端设备' not in lomsg[node_name]:
                        lomsg[node_name]['终端设备'] = {}
                    lomsg[node_name]['终端设备']['类型'] = tmpmsg[2]
                    lomsg[node_name]['终端设备']['续航时长'] = tmpmsg[3]
                elif tmpmsg[1] == '0' and '终端设备' not in lomsg[node_name]:
                    if '非终端设备' not in lomsg[node_name]:
                        lomsg[node_name]['非终端设备'] = {}
                    lomsg[node_name]['非终端设备']['能效'] = tmpmsg[2]
                    if '位置' not in lomsg[node_name]['非终端设备']:
                        lomsg[node_name]['非终端设备']['位置'] = {}
                    if '经度' not in lomsg[node_name]['非终端设备']['位置']:
                        lomsg[node_name]['非终端设备']['位置']['经度'] = {}
                    if '纬度' not in lomsg[node_name]['非终端设备']['位置']:
                        lomsg[node_name]['非终端设备']['位置']['纬度'] = {}
                    lomsg[node_name]['非终端设备']['位置']['经度']['@度'] = tmpmsg[3]
                    lomsg[node_name]['非终端设备']['位置']['经度']['@分'] = tmpmsg[4]
                    lomsg[node_name]['非终端设备']['位置']['经度']['@秒'] = tmpmsg[5]
                    lomsg[node_name]['非终端设备']['位置']['纬度']['@度'] = tmpmsg[6]
                    lomsg[node_name]['非终端设备']['位置']['纬度']['@分'] = tmpmsg[7]
                    lomsg[node_name]['非终端设备']['位置']['纬度']['@秒'] = tmpmsg[8]
            elif topic == 'mqtt/system/Usage':
                tmpmsg = msg.payload.decode().split(':')
                node_name = '节点' + tmpmsg[0]
                if node_name not in lomsg:
                    lomsg[node_name] = {}
                if '资源占用' not in lomsg[node_name]:
                    lomsg[node_name]['资源占用'] = {}
                if '处理器占用率' not in lomsg[node_name]['资源占用']:
                    lomsg[node_name]['资源占用']['处理器占用率'] = {}
                if '内存占用率' not in lomsg[node_name]['资源占用']:
                    lomsg[node_name]['资源占用']['内存占用率'] = {}
                if '内存带宽占用率' not in lomsg[node_name]['资源占用']:
                    lomsg[node_name]['资源占用']['内存带宽占用率'] = {}
                if '网络带宽占用率' not in lomsg[node_name]['资源占用']:
                    lomsg[node_name]['资源占用']['网络带宽占用率'] = {}
                    if '网络上行带宽占用率' not in lomsg[node_name]['资源占用']['网络带宽占用率']:
                        lomsg[node_name]['资源占用']['网络带宽占用率']['上行'] = {}
                    if '网络下行带宽占用率' not in lomsg[node_name]['资源占用']['网络带宽占用率']:
                        lomsg[node_name]['资源占用']['网络带宽占用率']['下行'] = {}
                if 'IOPS占用率' not in lomsg[node_name]['资源占用']:
                    lomsg[node_name]['资源占用']['IOPS占用率'] = {}
                if '存储空间占用率' not in lomsg[node_name]['资源占用']:
                    lomsg[node_name]['资源占用']['存储空间占用率'] = {}
                lomsg[node_name]['资源占用']['处理器占用率'] = tmpmsg[1]
                lomsg[node_name]['资源占用']['内存占用率'] = tmpmsg[2]
                lomsg[node_name]['资源占用']['内存带宽占用率'] = tmpmsg[3]
                lomsg[node_name]['资源占用']['网络带宽占用率']['上行'] = tmpmsg[4]
                lomsg[node_name]['资源占用']['网络带宽占用率']['下行'] = tmpmsg[5]
                lomsg[node_name]['资源占用']['IOPS占用率'] = tmpmsg[6]
                lomsg[node_name]['资源占用']['存储空间占用率'] = tmpmsg[7]















            elif topic == 'NEW':
                pass
            # print("原始system_dict:", lomsg)
            json_to_xml(json.dumps(process_nested_dict(lomsg)), xml_path, 'system')

            # dict_to_xml(lomsg, xml_path, 'system')
            # dict_to_xml(json.dumps(lomsg), xml_path, 'system')
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

            # 处理器
            elif topic == 'mqtt/system/CPUPercent':
                tmpmsg = msg.payload.decode().split(':')
                if '节点' not in resmsg[tmpmsg[0]]:
                    resmsg[tmpmsg[0]]['节点'] = {}
                if '容器' not in resmsg[tmpmsg[0]]['节点']:
                    resmsg[tmpmsg[0]]['节点']['容器'] = {}
                # if tmpmsg[1] != '0':
                if '处理器1' not in resmsg[tmpmsg[0]]['节点']['容器']:
                    resmsg[tmpmsg[0]]['节点']['容器']['处理器1'] = {}
                resmsg[tmpmsg[0]]['节点']['容器']['处理器1']['类型'] = 'CPU'
                resmsg[tmpmsg[0]]['节点']['容器']['处理器1']['利用率'] = tmpmsg[1]

            elif topic == 'mqtt/system/GPUPercent':
                tmpmsg = msg.payload.decode().split(':')
                if '节点' not in resmsg[tmpmsg[0]]:
                    resmsg[tmpmsg[0]]['节点'] = {}
                if '容器' not in resmsg[tmpmsg[0]]['节点']:
                    resmsg[tmpmsg[0]]['节点']['容器'] = {}
                # if tmpmsg[1] != '0':
                if '处理器2' not in resmsg[tmpmsg[0]]['节点']['容器']:
                    resmsg[tmpmsg[0]]['节点']['容器']['处理器2'] = {}
                resmsg[tmpmsg[0]]['节点']['容器']['处理器2']['类型'] = 'GPU'
                resmsg[tmpmsg[0]]['节点']['容器']['处理器2']['利用率'] = tmpmsg[1]

            elif topic == 'mqtt/system/TPUPercent':
                tmpmsg = msg.payload.decode().split(':')
                if '节点' not in resmsg[tmpmsg[0]]:
                    resmsg[tmpmsg[0]]['节点'] = {}
                if '容器' not in resmsg[tmpmsg[0]]['节点']:
                    resmsg[tmpmsg[0]]['节点']['容器'] = {}
                # if tmpmsg[1] != '0':
                if '处理器3' not in resmsg[tmpmsg[0]]['节点']['容器']:
                    resmsg[tmpmsg[0]]['节点']['容器']['处理器3'] = {}
                resmsg[tmpmsg[0]]['节点']['容器']['处理器3']['类型'] = 'TPU'
                resmsg[tmpmsg[0]]['节点']['容器']['处理器3']['利用率'] = tmpmsg[1]
                # 算力
            elif topic == 'mqtt/system/ComputerPower_M':
                tmpmsg = msg.payload.decode().split(':')
                # print(tmpmsg)
                if tmpmsg[0] not in resmsg:
                    resmsg[tmpmsg[0]] = {}
                if '节点' not in resmsg[tmpmsg[0]]:
                    resmsg[tmpmsg[0]]['节点'] = {}
                if '算力' not in resmsg[tmpmsg[0]]['节点']:
                    resmsg[tmpmsg[0]]['节点']['算力'] = {}
                if '图像分类' not in resmsg[tmpmsg[0]]['节点']['算力']:
                    resmsg[tmpmsg[0]]['节点']['算力']['图像分类'] = {}
                if '实例分割' not in resmsg[tmpmsg[0]]['节点']['算力']:
                    resmsg[tmpmsg[0]]['节点']['算力']['实例分割'] = {}
                if '医疗图像分割' not in resmsg[tmpmsg[0]]['节点']['算力']:
                    resmsg[tmpmsg[0]]['节点']['算力']['医疗图像分割'] = {}
                if '目标检测' not in resmsg[tmpmsg[0]]['节点']['算力']:
                    resmsg[tmpmsg[0]]['节点']['算力']['目标检测'] = {}
                if '自然语言处理' not in resmsg[tmpmsg[0]]['节点']['算力']:
                    resmsg[tmpmsg[0]]['节点']['算力']['自然语言处理'] = {}
                if '语音识别' not in resmsg[tmpmsg[0]]['节点']['算力']:
                    resmsg[tmpmsg[0]]['节点']['算力']['语音识别'] = {}
                if '智能推荐' not in resmsg[tmpmsg[0]]['节点']['算力']:
                    resmsg[tmpmsg[0]]['节点']['算力']['智能推荐'] = {}
                if '强化学习' not in resmsg[tmpmsg[0]]['节点']['算力']:
                    resmsg[tmpmsg[0]]['节点']['算力']['强化学习'] = {}
                resmsg[tmpmsg[0]]['节点']['算力']['图像分类']['总算力'] = tmpmsg[1]
                resmsg[tmpmsg[0]]['节点']['算力']['实例分割']['总算力'] = tmpmsg[2]
                resmsg[tmpmsg[0]]['节点']['算力']['医疗图像分割']['总算力'] = tmpmsg[3]
                resmsg[tmpmsg[0]]['节点']['算力']['目标检测']['总算力'] = tmpmsg[4]
                resmsg[tmpmsg[0]]['节点']['算力']['自然语言处理']['总算力'] = tmpmsg[5]
                resmsg[tmpmsg[0]]['节点']['算力']['语音识别']['总算力'] = tmpmsg[6]
                resmsg[tmpmsg[0]]['节点']['算力']['智能推荐']['总算力'] = tmpmsg[7]
                resmsg[tmpmsg[0]]['节点']['算力']['强化学习']['总算力'] = tmpmsg[8]

            elif topic == 'mqtt/system/ComputerPower_A':
                tmpmsg = msg.payload.decode().split(':')
                # print(tmpmsg)
                if tmpmsg[0] not in resmsg:
                    resmsg[tmpmsg[0]] = {}
                if '节点' not in resmsg[tmpmsg[0]]:
                    resmsg[tmpmsg[0]]['节点'] = {}
                if '算力' not in resmsg[tmpmsg[0]]['节点']:
                    resmsg[tmpmsg[0]]['节点']['算力'] = {}
                if '图像分类' not in resmsg[tmpmsg[0]]['节点']['算力']:
                    resmsg[tmpmsg[0]]['节点']['算力']['图像分类'] = {}
                if '实例分割' not in resmsg[tmpmsg[0]]['节点']['算力']:
                    resmsg[tmpmsg[0]]['节点']['算力']['实例分割'] = {}
                if '医疗图像分割' not in resmsg[tmpmsg[0]]['节点']['算力']:
                    resmsg[tmpmsg[0]]['节点']['算力']['医疗图像分割'] = {}
                if '目标检测' not in resmsg[tmpmsg[0]]['节点']['算力']:
                    resmsg[tmpmsg[0]]['节点']['算力']['目标检测'] = {}
                if '自然语言处理' not in resmsg[tmpmsg[0]]['节点']['算力']:
                    resmsg[tmpmsg[0]]['节点']['算力']['自然语言处理'] = {}
                if '语音识别' not in resmsg[tmpmsg[0]]['节点']['算力']:
                    resmsg[tmpmsg[0]]['节点']['算力']['语音识别'] = {}
                if '智能推荐' not in resmsg[tmpmsg[0]]['节点']['算力']:
                    resmsg[tmpmsg[0]]['节点']['算力']['智能推荐'] = {}
                if '强化学习' not in resmsg[tmpmsg[0]]['节点']['算力']:
                    resmsg[tmpmsg[0]]['节点']['算力']['强化学习'] = {}
                resmsg[tmpmsg[0]]['节点']['算力']['图像分类']['已分配'] = tmpmsg[1]
                resmsg[tmpmsg[0]]['节点']['算力']['实例分割']['已分配'] = tmpmsg[2]
                resmsg[tmpmsg[0]]['节点']['算力']['医疗图像分割']['已分配'] = tmpmsg[3]
                resmsg[tmpmsg[0]]['节点']['算力']['目标检测']['已分配'] = tmpmsg[4]
                resmsg[tmpmsg[0]]['节点']['算力']['自然语言处理']['已分配'] = tmpmsg[5]
                resmsg[tmpmsg[0]]['节点']['算力']['语音识别']['已分配'] = tmpmsg[6]
                resmsg[tmpmsg[0]]['节点']['算力']['智能推荐']['已分配'] = tmpmsg[7]
                resmsg[tmpmsg[0]]['节点']['算力']['强化学习']['已分配'] = tmpmsg[8]
            elif topic == 'mqtt/system/Storage_M':
                tmpmsg = msg.payload.decode().split(':')
                # print(tmpmsg)
                # if tmpmsg[0] not in resmsg:
                #     resmsg[tmpmsg[0]] = {}
                if '节点' not in resmsg[tmpmsg[0]]:
                    resmsg[tmpmsg[0]]['节点'] = {}
                if '容器' not in resmsg[tmpmsg[0]]['节点']:
                    resmsg[tmpmsg[0]]['节点']['容器'] = {}
                if '存储1' not in resmsg[tmpmsg[0]]['节点']:
                    resmsg[tmpmsg[0]]['节点']['容器']['存储1'] = {}
                if '存储2' not in resmsg[tmpmsg[0]]['节点']:
                    resmsg[tmpmsg[0]]['节点']['容器']['存储2'] = {}
                if '存储3' not in resmsg[tmpmsg[0]]['节点']:
                    resmsg[tmpmsg[0]]['节点']['容器']['存储3'] = {}
                resmsg[tmpmsg[0]]['节点']['容器']['存储1']['类型'] = '内存'
                resmsg[tmpmsg[0]]['节点']['容器']['存储2']['类型'] = '外存'
                resmsg[tmpmsg[0]]['节点']['容器']['存储3']['类型'] = '缓存'
                resmsg[tmpmsg[0]]['节点']['容器']['存储1']['总空间'] = tmpmsg[1]
                resmsg[tmpmsg[0]]['节点']['容器']['存储2']['总空间'] = tmpmsg[2]
                resmsg[tmpmsg[0]]['节点']['容器']['存储3']['总空间'] = tmpmsg[3]

            elif topic == 'mqtt/system/Storage_A':
                tmpmsg = msg.payload.decode().split(':')
                resmsg[tmpmsg[0]]['节点']['容器']['存储1']['类型'] = '内存'
                resmsg[tmpmsg[0]]['节点']['容器']['存储2']['类型'] = '外存'
                resmsg[tmpmsg[0]]['节点']['容器']['存储3']['类型'] = '缓存'
                resmsg[tmpmsg[0]]['节点']['容器']['存储1']['已分配'] = tmpmsg[1]
                resmsg[tmpmsg[0]]['节点']['容器']['存储2']['已分配'] = tmpmsg[2]
                resmsg[tmpmsg[0]]['节点']['容器']['存储3']['已分配'] = tmpmsg[3]
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
            # dict_to_xml(resmsg, xml_path, 'res')
            # print('tmpmsg',tmpmsg)

        # 订阅指定消息主题
        for topic in self.topics:
            self.client.subscribe(topic)
            print(topic, '-------------------------------')
        # TODO 输出看看这儿的topic的内容，能不能直接用
        for topic in self.server_topics:
            self.client.subscribe(topic)
            print(topic, '+++')
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
            xml_str = xmltodict.unparse({'算力资源': {**json_dic, '@ID': 'system1'}}, encoding='utf-8')
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
            xml_str = xmltodict.unparse({'算力资源': {**json_dic, '@ID': 'system1'}}, encoding='utf-8')
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
    # print("load_dict:", load_dict)
    json_result = jsonToXml(load_dict, type)
    # print("json_result:", json_result)
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
        # print(dom.toprettyxml())
        f.write(dom.toprettyxml())
        f.close()
        # 测试输出用
        # print("system_dict:", json_str)
        # with open(os.path.join(xml_path, "system_info.json"), 'w', encoding="UTF-8") as f:
        #     json.dump(json_str, f)

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


def dictToXml(root, xml_path, type):
    xml_string = ET.tostring(root, encoding='utf8', method='xml', xml_declaration=False)  # 将XML文档对象转换为字符串
    if type == "task":
        path_to_xml = os.path.join(xml_path, "task_info_.xml")
    elif type == "system":
        path_to_xml = os.path.join(xml_path, "system_info_.xml")
    elif type == "res":
        path_to_xml = os.path.join(xml_path, "res_info.xml")
    elif type == "task_off_res":
        path_to_xml = os.path.join(xml_path, "task_off_res.xml")
    elif type == "task_off_res1":
        path_to_xml = os.path.join(xml_path, "task_off_res1.xml")
    f = open(path_to_xml, 'w', encoding="UTF-8")  # 覆盖
    f.write(xml_string.decode('utf8'))
    f.close()
    tree = ET.parse(path_to_xml)  # 解析xml文件
    root = tree.getroot()  # 得到根元素，Element类
    pretty_xml(root, '\t', '\n')  # 执行美化方法
    tree.write(path_to_xml, encoding='utf8', method='xml', xml_declaration=True)


def dict_to_xml(json_str, xml_path, type):
    if not os.path.exists(xml_path):
        os.makedirs(xml_path)
    # dict = json.loads(json_str)
    dict = json_str
    # print("load_dict:", dict)
    if type == 'task':
        # 创建xml的根元素：任务信息
        print('任务信息:', dict)
        root = ET.Element("任务信息")
        """TODO 根据xsd文件格式将字典的内容转换为xml"""
        for task in dict.values():
            # print('task:',task)
            # 创建任务信息的子元素：任务
            task_element = ET.SubElement(root, "任务")
            for sub_task in task.values():
                # print('subtask:',sub_task)
                # 创建任务的子元素：子任务
                sub_task_element = ET.SubElement(task_element, "子任务")
                sub_task_element.set("ID", sub_task['ID'])  # 为元素子任务设置属性
                # TODO: TypeError: string indices must be integers
                # 创建子任务的子元素：构成，资源需求
                constitute_element = ET.SubElement(sub_task_element, "构成")
                require_element = ET.SubElement(sub_task_element, "资源需求")
                model_element = ET.SubElement(constitute_element, "模型")
                ops_element = ET.SubElement(model_element, "操作数")
                data_element = ET.SubElement(model_element, "数据要求")
                if '操作数' in sub_task['构成']['模型']:
                    ops = sub_task['构成']['模型']['操作数']
                    # print('ops:',ops)
                    for i in range(0, len(ops)):
                        if ops[operands[i]] != '0':
                            op_element = ET.SubElement(ops_element,
                                                       operands[i])  # 创建具体的操作数元素并赋值:<Convolution>10</Convolution>
                            op_element.text = ops[operands[i]]
                if '数据要求' in sub_task['构成']['模型']:
                    data = sub_task['构成']['模型']['数据要求']
                    data_element.text = data  # 为数据要求元素赋值
                # 按上面的方法将整个xml重新构建

                # 资源需求
                '''
                        <xs:element name="算力" type="算力Type"/>
						<xs:element name="存储" type="存储Type"/>
						<xs:element name="网络" type="网络Type"/>
						<xs:element name="性能要求" type="性能Type"/>
                '''

                '''
                弃用ver
                # 资源需求的子元素：算力
                computingpowercp_element = ET.SubElement(require_element, "算力")
                # 创建算力的子元素以及赋值
                for key, value in sub_task['资源需求']['算力'].items():
                    ET.SubElement(computingpowercp_element, "算法").text = key
                    for _, subvalue in value.items():
                        ET.SubElement(computingpowercp_element, "值").text = subvalue

                # 资源需求的子元素：存储
                storage_element = ET.SubElement(require_element, "存储")
                # 创建存储的子元素以及赋值
                for key, value in sub_task['资源需求']['存储'].items():
                    ET.SubElement(storage_element, "类型").text = key
                    for _, subvalue in value.items():
                        ET.SubElement(storage_element, "字节数").text = subvalue
                '''
                # 创建资源需求的子元素：算力、存储、网络、性能要求
                if '资源需求' in sub_task:
                    request = sub_task['资源需求']
                    for key, value in request.items():
                        if "算力" in key:
                            res_element = ET.SubElement(require_element, "算力")
                        elif "存储" in key:
                            res_element = ET.SubElement(require_element, "存储")
                        elif "网络" in key:
                            res_element = ET.SubElement(require_element, "网络")
                        elif "性能要求" in key:
                            res_element = ET.SubElement(require_element, "性能要求")
                        # type_element = ET.SubElement(res_element, "类型")

                        # 创建算力、存储、网络、性能要求的子元素以及赋值
                        if "算力" in key:
                            type_element = ET.SubElement(res_element, "算法")
                            flops_element = ET.SubElement(res_element, "值")
                            if "算法" in value:
                                type_element.text = value['算法']
                            if "值" in value:
                                flops_element.text = value['值']
                        elif "存储" in key:
                            for i in range(1, 4):
                                type_element = ET.SubElement(res_element, "类型")
                                size_element = ET.SubElement(res_element, "字节数")
                                if f'类型{i}' in value:
                                    type_element.text = value[f'类型{i}']
                                    size_element.text = value[f'字节数{i}']
                                    # print('类型:',value[f'类型{i}'])

                            # type_element = ET.SubElement(res_element, "类型")
                            # size_element = ET.SubElement(res_element, "字节数")
                            # if "类型" in value:
                            #     type_element.text = value['类型']
                            #     print('类型：',value['类型'])
                            # if "字节数" in value:
                            #     size_element.text = value['字节数']
                            # TODO 生成逻辑不一致
                        elif "网络" in key:
                            protocol = ET.SubElement(res_element, "支持的网络协议")
                            throughput = ET.SubElement(res_element, "最小最大吞吐率")
                            upload = ET.SubElement(throughput, "上行")
                            download = ET.SubElement(throughput, "下行")
                            latency = ET.SubElement(res_element, "最小最大延迟")

                            if '最小最大吞吐率' in value:
                                # print('吞吐：',value['最小最大吞吐率'])
                                upload.text = value['最小最大吞吐率']['上行']
                                download.text = value['最小最大吞吐率']['下行']
                            if '支持的网络协议' in value:
                                # print('xieyi:',value['支持的网络协议'])
                                for proto in value['支持的网络协议'].values():
                                    protocol_element = ET.SubElement(protocol, "网络协议")
                                    protocol_element.text = proto
                            if '延迟' in value:
                                # print('延迟:',value['延迟'])
                                latency.text = value['延迟']
                        elif "性能要求" in key:
                            # 响应时间
                            time_element = ET.SubElement(res_element, "响应时间")
                            time1 = ET.SubElement(time_element, "最大")
                            time2 = ET.SubElement(time_element, "最小")
                            time3 = ET.SubElement(time_element, "平均")
                            if '响应时间' in value:
                                time1.text = value['响应时间']['最大']
                                time2.text = value['响应时间']['最小']
                                time3.text = value['响应时间']['平均']

                            energy_element = ET.SubElement(res_element, "能耗")
                            stable_element = ET.SubElement(res_element, "稳定性")
                            safe_element = ET.SubElement(res_element, "安全性")
                            if '能耗' in value:
                                energy_element.text = value['能耗']
                                # 稳定性，安全性暂无


    elif type == 'system':
        root = ET.Element("系统信息")
        # print('系统信息:',dict)
        """TODO 根据xsd文件格式将字典的内容转换为xml"""
        for sys_id, system in dict.items():
            # print('system:',system)
            # 创建系统信息的子元素：云端/边缘端/终端
            # if 'cloud' in system['节点']['ID']:
            if 'cloud' in sys_id:
                ec_element = ET.SubElement(root, "云端")
            else:
                ec_element = ET.SubElement(root, "边缘端")
            # 创建云边端算力资源的子元素：节点
            node_element = ET.SubElement(ec_element, "节点")
            # 节点属性添加
            node_element.set('URL', system['节点']['URL'])
            node_element.set('ID', system['节点']['ID'])
            node_element.set('优先级', system['节点']['优先级'])
            node_element.remove()
            # 创建节点的子元素：pod
            pod_element = ET.SubElement(node_element, "Pod")
            # 创建pod的子元素：容器
            container_element = ET.SubElement(pod_element, "容器")
            print('节点:', system['节点'])
            if '容器' in system['节点']:
                container = system['节点']['容器']
                # 创建容器的子元素：处理器、存储、网络
                for key, value in container.items():
                    if "处理器" in key:
                        res_element = ET.SubElement(container_element, "处理器")
                    elif "存储" in key:
                        res_element = ET.SubElement(container_element, "存储")
                    elif "网络" in key:
                        res_element = ET.SubElement(container_element, "网络")
                    # type_element = ET.SubElement(res_element, "类型")

                    # 创建处理器、存储、网络的子元素以及赋值
                    if "处理器" in key:
                        type_element = ET.SubElement(res_element, "类型")
                        flops_element = ET.SubElement(res_element, "FLOPS")
                        type_element.text = value['类型']
                        flops_element.text = value['FLOPS']
                    elif "存储" in key:
                        type_element = ET.SubElement(res_element, "类型")
                        size_element = ET.SubElement(res_element, "字节数")
                        type_element.text = value['类型']
                        size_element.text = value['字节数']
                    elif "网络" in key:
                        protocol = ET.SubElement(res_element, "支持的网络协议")
                        throughput = ET.SubElement(res_element, "最小最大吞吐率")
                        upload = ET.SubElement(throughput, "上行")
                        download = ET.SubElement(throughput, "下行")
                        latency = ET.SubElement(res_element, "最小最大延迟")
                        if '上行' in value['最小最大吞吐率']:
                            upload.text = value['最小最大吞吐率']['上行']
                        if '下行' in value['最小最大吞吐率']:
                            download.text = value['最小最大吞吐率']['下行']
                        if '支持的网络协议' in value:
                            protocol.text = value['支持的网络协议']
                        if '最小最大延迟' in value:
                            latency.text = value['最小最大延迟']

                '''
                和pod同级
                <算力>
				<安全性>			    
                '''
            # 创建节点的子元素：算力
            computingpowercp_element = ET.SubElement(node_element, "算力")
            # 创建算力的子元素以及赋值
            if '算力' in system['节点']:
                computingpower = system['节点']['算力']
                for key, value in computingpower.items():
                    # cp_element = ET.SubElement(computingpowercp_element, key)
                    ET.SubElement(computingpowercp_element, "算法").text = key
                    for subkey, subvalue in value.items():
                        # subtask = ET.SubElement(cp_element, subkey)
                        # subtask.text = subvalue
                        ET.SubElement(computingpowercp_element, "值").text = subvalue

            # 创建节点的子元素：安全性
            safe_element = ET.SubElement(node_element, "安全性")
            safe_element.text = "正常"


    elif type == 'res':
        root = ET.Element("资源基础利用")
        """TODO 根据xsd文件格式将字典的内容转换为xml"""


    elif type == 'task_off_res':
        # 没必要改，演示用的位置信息，在标准里没有体现
        root = ET.Element("任务位置")
        """TODO 根据xsd文件格式将字典的内容转换为xml"""


    elif type == 'task_off_res1':
        root = ET.Element("资源调度结果")
        """TODO 根据xsd文件格式将字典的内容转换为xml"""

    # print(ET.tostring(root, encoding='utf8', method='xml', xml_declaration=False))
    dictToXml(root, xml_path, type)


def pretty_xml(element, indent, newline, level=0):  # elemnt为传进来的Elment类，参数indent用于缩进，newline用于换行
    if element:  # 判断element是否有子元素
        if (element.text is None) or element.text.isspace():  # 如果element的text没有内容
            element.text = newline + indent * (level + 1)
        else:
            element.text = newline + indent * (level + 1) + element.text.strip() + newline + indent * (level + 1)
            # else:  # 此处两行如果把注释去掉，Element的text也会另起一行
            # element.text = newline + indent * (level + 1) + element.text.strip() + newline + indent * level
    temp = list(element)  # 将element转成list
    for subelement in temp:
        if temp.index(subelement) < (len(temp) - 1):  # 如果不是list的最后一个元素，说明下一个行是同级别元素的起始，缩进应一致
            subelement.tail = newline + indent * (level + 1)
        else:  # 如果是list的最后一个元素， 说明下一行是母元素的结束，缩进应该少一个
            subelement.tail = newline + indent * level
        pretty_xml(subelement, indent, newline, level=level + 1)  # 对子元素进行递归操作


if __name__ == '__main__':
    server = ServerAgent(
        keepalive=keepalive,
        broker=brokerIP,
        port=port,
        clientID=clientID,
        topics=topics,
    )

    server.run()
