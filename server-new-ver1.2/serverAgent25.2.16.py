#!/usr/bin/python3
#-*- coding:utf-8 -*-
############################
# File Name: serverAgent.py
# Author: 
# mail: 
# Create Time: 2023/5/4 11:10:40
############################
#from icecream import install
#install()
#import time
#def timestamp():
#    return '%s |> ' % time.strftime('%Y-%m-%d %T')
#ic.configureOutput(prefix=timestamp)
import random
from copy import deepcopy
from enum import Enum
import time
from math import fabs
from paho.mqtt import client as mqtt_client
import argparse
from virtualRes import VirtualRes, Node, ResourceConfig, ComputerPower
from infoCollector import getCPUInfo, getCPUFLOPS, getCPUPercent, getGPUInfo, \
    getNetInfo, getMEMInfo, getDiskInfo, getIOPS, getCacheInfo, getCPUPercent, getGPUPercent

parser = argparse.ArgumentParser(description='')
parser.add_argument('--broker', type=str, default='127.0.0.1')
parser.add_argument('--port', type=int, default=1883)
parser.add_argument('--keepalive', type=int, default=60)
parser.add_argument('--timeslot', type=int, default=4)
parser.add_argument('--clientID', type=str, default='cloud')
parser.add_argument('--GPU', type=bool)
args = parser.parse_known_args()[0]
brokerIP = args.broker
port = args.port
keepalive = args.keepalive
clientID = args.clientID
timeslot = args.timeslot
print(args)

"""TODO+ 依据标准增加更多内容"""
# 标准要的
topics = [
    'mqtt/system/Attribute',
    #
    # 'mqtt/system/CPUFLOPS',
    # 'mqtt/system/GPUFLOPS',
    # 'mqtt/system/TPUFLOPS',
    #
    # 'mqtt/system/Storage_M',
    # 'mqtt/system/Storage_A',
    # 'mqtt/system/Internal_storage',
    # 'mqtt/system/External_storage',
    # 'mqtt/system/Cache',
    #
    # 'mqtt/system/Throughput_up',
    # 'mqtt/system/Throughput_down',
    # 'mqtt/system/Latency',
    #
    # 'mqtt/system/ComputerPower_M',
    # 'mqtt/system/ComputerPower_A',
    # 'mqtt/system/ComputerPower',
    #
    # 'mqtt/system/CPUPercent',
    # 'mqtt/system/GPUPercent',
    # 'mqtt/system/TPUPercent',
    #
    # 'mqtt/system/System_Computing_power',

    'mqtt/system/Computing_Power_Configuration/Computing_Units_Set/Processor/CPU_Specifications',
    'mqtt/system/Computing_Power_Configuration/Computing_Units_Set/Processor/GPU_Specifications',
    'mqtt/system/Computing_Power_Configuration/Computing_Units_Set/Processor/FPGA_Specifications',
    'mqtt/system/Computing_Power_Configuration/Computing_Units_Set/Processor/TPU_Specifications',
    'mqtt/system/Computing_Power_Configuration/Computing_Units_Set/Processor/Frequency_Set/Frequency',

    'mqtt/system/Computing_Power_Configuration/Computing_Units_Set/Processor/Speed_Set/Speed_Attributes',

    'mqtt/system/Computing_Power_Configuration/Computing_Units_Set/Memory/Attributes',
    'mqtt/system/Computing_Power_Configuration/Computing_Units_Set/Memory/Specifications',


    'mqtt/system/Computing_Power_Configuration/Communicate_Units_Set/Communicate_Unit/Attributes',
    'mqtt/system/Computing_Power_Configuration/Communicate_Units_Set/Communicate_Unit/Specifications',

    'mqtt/system/Computing_Power_Configuration/Storage_Units_Set/Storage_Unit/Attributes',
    'mqtt/system/Computing_Power_Configuration/Storage_Units_Set/Storage_Unit/Specifications',

    'mqtt/system/Computing_Power_Configuration/Computing_Power',

    'mqtt/system/Terminal_Device_or_not',
    # 'mqtt/system/Image_classification',
    # 'mqtt/system/Instance_segmentation',
    # 'mqtt/system/Image_segmentation',
    # 'mqtt/system/NLP',
    # 'mqtt/system/SR',
    # 'mqtt/system/Recommendation',
    # 'mqtt/system/RL',
    # 资源占用新加的
    'mqtt/system/Usage',
    'mqtt/system/Computing_Power_Configuration/Software_env',
]

"""TODO+ 依据virtual resource """
# 虚拟调度用的
virtual_topics = [
    'mqtt/virtual/updateProcessor', 
    'mqtt/virtual/updateStorage', 

    'mqtt/virtual/releaseProcessor', 
    'mqtt/virtual/releaseStorage', 
]

# 启动节点相关操作
server_topics = [
    'mqtt/server/start',
    'mqtt/server/stop',
    'mqtt/server/delete',
]

class AlgorithmType(Enum):
    图像分类 = 0
    实例分割 = 1
    医疗图像分割 = 2
    目标检测 = 3
    自然语言处理 = 4
    语音识别 = 5
    智能推荐 = 6
    强化学习 = 7

class MemoryType(Enum):
    内存 = 0
    外存 = 1
    缓存 = 2

class ServerAgent():
    def __init__(
        self,
        keepalive: int,
        broker: str,
        clientID: str,
        port : int,
        topics: list = topics,
        virtual_topics: list = virtual_topics,
        server_topics: list = server_topics,
        virtual_res: bool = True,
        real_res: bool = True,
        publish_model: bool = False,
    ) -> object:
        self.client = None
        self.topics = topics
        self.virtual_topics = virtual_topics
        self.server_topics = server_topics
        self.keepalive = keepalive
        self.broker = broker
        self.port = port
        self.clientID = clientID
        self.msg = {}
        self.virtual_res = virtual_res
        self.real_res = real_res
        self.publish_model = publish_model
        self.compurtpower_M = None
        if virtual_res:
            """ TODO+ 增加更多 虚拟资源 以及 模拟逻辑"""
            self.res = VirtualRes()
            self.compurtpower_M = deepcopy(self.res.Node.computerpower)

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
        while self.infoChange():
            '''每隔 timeslot 秒发布一次服务器信息'''
            time.sleep(timeslot)
            for topic in self.topics:
                if not self.infoChange(topic):
                    continue
                """ TODO+ getInfo """
                self.msg = self.getInfo(topic)
                #print(self.msg)
                result = self.client.publish(topic, self.msg)
                status = result[0]
                if status == 1:
                #     print(f"Send `{self.msg}` to topic `{topic}`")
                # else:
                    print(f"Failed to send message to topic {topic}")


    def subscribe(
        self,
    ):
        '''订阅主题并接收消息'''
        def on_message(client, userdata, msg):
            print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
            topic = msg.topic
            #""" TODO  REALITY CALLBACK 
            #elif topic == 'NEW':
            #    具体处理逻辑
            #    pass
            #....
            if topic == 'mqtt/server/start':
                # 启动节点，开启mqtt的发送模式，开始发送设备的信息
                tmpmsg = msg.payload.decode().split(':')
                if tmpmsg[0] == self.clientID:
                    self.publish_model = True
            elif topic == 'mqtt/server/stop':
                # 停止节点，停止发送设备的信息，只接受信息
                tmpmsg = msg.payload.decode().split(':')
                if tmpmsg[0] == self.clientID:
                    self.publish_model = False
            elif topic == 'mqtt/server/delete':
                # 删除节点
                pass

            """ TODO+  VIRTUAL CALLBACK 更新虚拟资源
            elif topic == 'NEW':
                具体处理逻辑
                pass
            ....
            """
            if topic == 'mqtt/virtual/updateProcessor':
                tmpmsg = msg.payload.decode().split(':')
                # print(tmpmsg[1])
                # print(type(tmpmsg[1]))
                # print(AlgorithmType.tmpmsg[1].value)
                if tmpmsg[0] == self.clientID:
                    idx = AlgorithmType[tmpmsg[1]].value
                    self.res.Node.computerpower[idx].value -= float(tmpmsg[2])
                    self.res.Node.computerpower[idx].value_A += float(tmpmsg[2])
                    # for i in range(len(AlgorithmType)):
                    #     update = float(tmpmsg[2])
                    #     update = float(tmpmsg[2]) / self.compurtpower_M[idx].value * self.compurtpower_M[i].value
                    #     self.res.Node.computerpower[i].value -= update
                    
            # if topic == 'mqtt/virtual/updateStorage':
            #     tmpmsg = msg.payload.decode().split(':')
            #     if tmpmsg[0] == self.clientID:
            #         # idx = MemoryType[tmpmsg[1]].value
            #         # update = float(tmpmsg[2])
            #         # self.res.Node.config.memory[idx].byte -= update
            #         self.res.Node.config.memory[0].byte -= float(tmpmsg[1])
            #         self.res.Node.config.memory[2].byte -= float(tmpmsg[2])
            #         self.res.Node.config.memory[1].byte -= float(tmpmsg[3])
            #         self.res.Node.config.memory[0].byte_A += float(tmpmsg[1])
            #         self.res.Node.config.memory[2].byte_A += float(tmpmsg[2])
            #         self.res.Node.config.memory[1].byte_A += float(tmpmsg[3])

            if topic == 'mqtt/virtual/releaseProcessor':
                tmpmsg = msg.payload.decode().split(':')
                if tmpmsg[0] == self.clientID:
                    idx = AlgorithmType[tmpmsg[1]].value
                    # for i in range(len(AlgorithmType)):
                    #     update = float(tmpmsg[2])
                    #     print(update)
                    #     print(update / self.compurtpower_M[idx].value)
                    #     print(update / self.compurtpower_M[idx].value * self.compurtpower_M[i].value)
                    #     print( 1 + update / self.compurtpower_M[idx].value)
                    #     self.res.Node.computerpower[i].value *= 1 + update / self.compurtpower_M[idx].value
                    self.res.Node.computerpower[idx].value += float(tmpmsg[2])
                    self.res.Node.computerpower[idx].value_A -= float(tmpmsg[2])

            # if topic == 'mqtt/virtual/releaseStorage':
            #     tmpmsg = msg.payload.decode().split(':')
            #     if tmpmsg[0] == self.clientID:
            #         # idx = MemoryType[tmpmsg[1]].value
            #         # update = float(tmpmsg[2])
            #         # self.res.Node.config.memory[idx].byte += update
                    
            #         self.res.Node.config.memory[0].byte += float(tmpmsg[1])
            #         self.res.Node.config.memory[2].byte += float(tmpmsg[2])
            #         self.res.Node.config.memory[1].byte += float(tmpmsg[3])
            #         self.res.Node.config.memory[0].byte_A -= float(tmpmsg[1])
            #         self.res.Node.config.memory[2].byte_A -= float(tmpmsg[2])
            #         self.res.Node.config.memory[1].byte_A -= float(tmpmsg[3])
            elif topic == 'NEW':
                pass

            '''订阅消息回调函数'''
        # 订阅指定消息主题
        for topic in self.virtual_topics:
            self.client.subscribe(topic)
            # print(topic)
        for topic in self.server_topics:
            self.client.subscribe(topic)
        self.client.on_message = on_message


    def getInfo(
        self,
        topic : str
    ) -> str:
        """ 先只考虑虚拟情况 """
        if topic == 'mqtt/system/Attribute':
            msg = self.clientID + ':' + self.broker + ':' + self.clientID +':'+ str(self.res.Node.unit_prize)+':'+str(self.res.Node.priority)
            return msg
        if not self.real_res:
            """TODO+ 添加更多获取资源方式"""
            if topic == 'mqtt/system/CPUFLOPS':
                msg = self.clientID + ':' + str(round(self.res.Node.config.getProcessorFLOPS('CPU'), 2)) + 'GFLOPS'
                return msg
            elif topic == 'mqtt/system/GPUFLOPS':
                msg = self.clientID + ':' + str(round(self.res.Node.config.getProcessorFLOPS('GPU'), 2)) + 'TFLOPS'
                return msg
            elif topic == 'mqtt/system/TPUFLOPS':
                msg = self.clientID + ':' + str(round(self.res.Node.config.getProcessorFLOPS('TPU'), 2)) + 'TFLOPS'
                return msg
            elif topic == 'mqtt/system/Internal_storage':
                msg = self.clientID + ':' + str(round(self.res.Node.config.getMemoryByte('Internal_storage'), 2)) + 'GB'
                return msg
            elif topic == 'mqtt/system/External_storage':
                msg = self.clientID + ':' + str(round(self.res.Node.config.getMemoryByte('External_storage'), 2)) + 'GB'
                return msg
            elif topic == 'mqtt/system/Cache':
                msg = self.clientID + ':' + str(round(self.res.Node.config.getMemoryByte('Cache'), 2)) + 'GB'
                return msg
            # TODO:消息处理（多类
            elif topic == 'mqtt/system/Throughput_up':
                str1 = str(round(self.res.Node.config.getThroughput_up('Bluetooth'), 2))
                str2 = str(round(self.res.Node.config.getThroughput_up('TCP/IP'), 2))
                str3 = str(round(self.res.Node.config.getThroughput_up('Modbus'), 2))
                msg = self.clientID + ':' + str1 + 'kbps' + ':' + str2 + 'Mbps' + ':' + str3 + 'kbps' 
                return msg
            elif topic == 'mqtt/system/Throughput_down':
                str1 = str(round(self.res.Node.config.getThroughput_down('Bluetooth'), 2))
                str2 = str(round(self.res.Node.config.getThroughput_down('TCP/IP'), 2))
                str3 = str(round(self.res.Node.config.getThroughput_down('Modbus'), 2))
                msg = self.clientID + ':' + str1 + 'kbps' + ':' + str2 + 'Mbps' + ':' + str3 + 'kbps'
                return msg
            elif topic == 'mqtt/system/Latency':
                str1 = str(round(self.res.Node.config.getLatency('Bluetooth'), 2))
                str2 = str(round(self.res.Node.config.getLatency('TCP/IP'), 2))
                str3 = str(round(self.res.Node.config.getLatency('Modbus'), 2))
                msg = self.clientID + ':' + str1 + 'ms' + ':' + str2 + 'ms' + ':' + str3 + 'ms'
                return msg
            elif topic == 'mqtt/system/ComputerPower':
                str1 = str(round(self.res.Node.getComputerPower('Image_classification'), 2))
                str2 = str(round(self.res.Node.getComputerPower('Instance_segmentation'), 2))
                str3 = str(round(self.res.Node.getComputerPower('Image_segmentation'), 2))
                str4 = str(round(self.res.Node.getComputerPower('Object_detection'), 2))
                str5 = str(round(self.res.Node.getComputerPower('Natural_language_processing'), 2))
                str6 = str(round(self.res.Node.getComputerPower('Speech_recognition'), 2))
                str7 = str(round(self.res.Node.getComputerPower('Intelligent_recommendation'), 2))
                str8 = str(round(self.res.Node.getComputerPower('Reinforcement_learning'), 2))
                msg = self.clientID + ':' + str1 + ':' + str2 + ':' + str3 + ':' + str4 + ':' + str5+ ':' + str6+ ':' + str7 + ':' + str8
                return msg
            # elif topic == 'mqtt/system/Image_classification':
            #     msg = self.clientID + ':' + str(self.res.Node.getComputerPower('Image_classification'))
            #     return msg
            # elif topic == 'mqtt/system/Instance_segmentation':
            #     msg = self.clientID + ':' + str(self.res.Node.getComputerPower('Instance_segmentation'))
            #     return msg
            # elif topic == 'mqtt/system/Image_segmentation':
            #     msg = self.clientID + ':' + str(self.res.Node.getComputerPower('Image_segmentation'))
            #     return msg
            # elif topic == 'mqtt/system/NLP':
            #     msg = self.clientID + ':' + str(self.res.Node.getComputerPower('Natural_language_processing'))
            #     return msg
            # elif topic == 'mqtt/system/SR':
            #     msg = self.clientID + ':' + str(self.res.Node.getComputerPower('Speech_recognition'))
            #     return msg
            # elif topic == 'mqtt/system/Recommendation':
            #     msg = self.clientID + ':' + str(self.res.Node.getComputerPower('Intelligent_recommendation'))
            #     return msg
            # elif topic == 'mqtt/system/RL':
            #     msg = self.clientID + ':' + str(self.res.Node.getComputerPower('Reinforcement_learning'))
            #     return msg
            
            elif topic == 'mqtt/system/ComputerPower_M':
                str1 = str(round(self.res.Node.getComputerPower_M('Image_classification'), 2))
                str2 = str(round(self.res.Node.getComputerPower_M('Instance_segmentation'), 2))
                str3 = str(round(self.res.Node.getComputerPower_M('Image_segmentation'), 2))
                str4 = str(round(self.res.Node.getComputerPower_M('Object_detection'), 2))
                str5 = str(round(self.res.Node.getComputerPower_M('Natural_language_processing'), 2))
                str6 = str(round(self.res.Node.getComputerPower_M('Speech_recognition'), 2))
                str7 = str(round(self.res.Node.getComputerPower_M('Intelligent_recommendation'), 2))
                str8 = str(round(self.res.Node.getComputerPower_M('Reinforcement_learning'), 2))
                msg = self.clientID + ':' + str1 + ':' + str2 + ':' + str3 + ':' + str4 + ':' + str5+ ':' + str6+ ':' + str7 + ':' + str8
                return msg
            
            elif topic == 'mqtt/system/ComputerPower_A':
                str1 = str(fabs(round(self.res.Node.getComputerPower_A('Image_classification'), 2)))
                str2 = str(fabs(round((self.res.Node.getComputerPower_A('Instance_segmentation')), 2)))
                str3 = str(fabs(round(self.res.Node.getComputerPower_A('Image_segmentation'), 2)))
                str4 = str(fabs(round(self.res.Node.getComputerPower_A('Object_detection'), 2)))
                str5 = str(fabs(round(self.res.Node.getComputerPower_A('Natural_language_processing'), 2)))
                str6 = str(fabs(round(self.res.Node.getComputerPower_A('Speech_recognition'), 2)))
                str7 = str(fabs(round(self.res.Node.getComputerPower_A('Intelligent_recommendation'), 2)))
                str8 = str(fabs(round(self.res.Node.getComputerPower_A('Reinforcement_learning'), 2)))
                msg = self.clientID + ':' + str1 + ':' + str2 + ':' + str3 + ':' + str4 + ':' + str5+ ':' + str6+ ':' + str7 + ':' + str8
                return msg
                
            elif topic == 'mqtt/system/Storage_M':
                str1=str(round(self.res.Node.config.getMemoryByte_M('Internal_storage'), 2)) + 'GB'
                str2=str(round(self.res.Node.config.getMemoryByte_M('External_storage'), 2)) + 'GB'
                str3=str(round(self.res.Node.config.getMemoryByte_M('Cache'), 2)) + 'GB'
                msg = self.clientID + ':' + str1 + ':' + str2 + ':' + str3
                return msg
                
            elif topic == 'mqtt/system/Storage_A':
                str1=str(fabs(round(self.res.Node.config.getMemoryByte_A('Internal_storage'), 2))) + 'GB'
                str2=str(fabs(round(self.res.Node.config.getMemoryByte_A('External_storage'), 2))) + 'GB'
                str3=str(fabs(round(self.res.Node.config.getMemoryByte_A('Cache'), 2))) + 'GB'
                msg = self.clientID + ':' + str1 + ':' + str2 + ':' + str3
                return msg
            elif topic == 'NEW':
                pass
        else:
            # TODO: 真实设备数据，目前能获取到的，不能获取的接着使用虚拟数据
            if topic == 'mqtt/system/CPUFLOPS':
                # msg = self.clientID + ':' + str(round(getCPUFLOPS())) + 'GFLOPS'
                # msg = self.clientID + ':' + str(round(self.res.Node.config.getProcessorFLOPS('CPU'))) 
                msg = self.clientID + ':' + str(round(self.res.Node.config.getProcessorFLOPS('CPU'), 2)) + 'GFLOPS'
                return msg
            elif topic == 'mqtt/system/GPUFLOPS':
                # msg = self.clientID + ':' + str(getGPUInfo()) + 'TFLOPS'
                msg = self.clientID + ':' + str(round(self.res.Node.config.getProcessorFLOPS('GPU'), 2)) + 'TFLOPS'
                return msg
            elif topic == 'mqtt/system/TPUFLOPS':
                msg = self.clientID + ':' + str(0) + 'TFLOPS'
                return msg
            elif topic == 'mqtt/system/Internal_storage':
                msg = self.clientID + ':' + str(round(getMEMInfo()[1], 2)) + 'GB'
                return msg
            elif topic == 'mqtt/system/External_storage':
                msg = self.clientID + ':' + str(round(getDiskInfo()[1], 2)) + 'GB'
                return msg
            elif topic == 'mqtt/system/Cache':
                # if platform.system().lower() == 'linux':
                #     msg = self.clientID + ':' + str(round(getCacheInfo(), 2)) + 'GB'
                # else:
                msg = self.clientID + ':' + str(round(getCacheInfo(), 2)) + 'GB'
                return msg
            
            #  处理器利用率（标准没有
            elif topic == 'mqtt/system/CPUPercent':
                msg = self.clientID + ':' + str(round(getCPUPercent()[0], 2)) + '%'
                return msg
            elif topic == 'mqtt/system/GPUPercent':
                msg = self.clientID + ':' + str(round(getGPUPercent()[0], 2)) + '%'
                return msg
            elif topic == 'mqtt/system/TPUPercent':
                msg = self.clientID + ':' + str(0) + '%'
                return msg
            
            # TODO:消息处理（多类
            elif topic == 'mqtt/system/Throughput_up':
                str1 = str(round(self.res.Node.config.getThroughput_up('Bluetooth'), 2))
                str2 = str(round(getNetInfo()[0], 2))
                str3 = str(round(self.res.Node.config.getThroughput_up('Modbus'), 2))
                msg = self.clientID + ':' + str1 + 'kbps' + ':' + str2 + 'Mbps' + ':' + str3 + 'kbps'
                return msg
            elif topic == 'mqtt/system/Throughput_down':
                str1 = str(round(self.res.Node.config.getThroughput_down('Bluetooth'), 2))
                str2 = str(round(getNetInfo()[1], 2))
                str3 = str(round(self.res.Node.config.getThroughput_down('Modbus'), 2))
                msg = self.clientID + ':' + str1 + 'kbps' + ':' + str2 + 'Mbps' + ':' + str3 + 'kbps'
                return msg
            elif topic == 'mqtt/system/Latency':
                str1 = str(round(self.res.Node.config.getLatency('Bluetooth'), 2))
                str2 = str(round(self.res.Node.config.getLatency('TCP/IP'), 2))
                str3 = str(round(self.res.Node.config.getLatency('Modbus'), 2))
                msg = self.clientID + ':' + str1 + 'ms' + ':' + str2 + 'ms' + ':' + str3 + 'ms'
                return msg
            elif topic == 'mqtt/system/ComputerPower':
                str1 = str(round(self.res.Node.getComputerPower('Image_classification'), 2))
                str2 = str(round(self.res.Node.getComputerPower('Instance_segmentation'), 2))
                str3 = str(round(self.res.Node.getComputerPower('Image_segmentation'), 2))
                str4 = str(round(self.res.Node.getComputerPower('Object_detection'), 2))
                str5 = str(round(self.res.Node.getComputerPower('Natural_language_processing'), 2))
                str6 = str(round(self.res.Node.getComputerPower('Speech_recognition'), 2))
                str7 = str(round(self.res.Node.getComputerPower('Intelligent_recommendation'), 2))
                str8 = str(round(self.res.Node.getComputerPower('Reinforcement_learning'), 2))
                msg = self.clientID + ':' + str1 + ':' + str2 + ':' + str3 + ':' + str4 + ':' + str5 + ':' + str6 + ':' + str7 + ':' + str8
                return msg
            elif topic == 'mqtt/system/ComputerPower_M':
                str1 = str(round(self.res.Node.getComputerPower_M('Image_classification'), 2))
                str2 = str(round(self.res.Node.getComputerPower_M('Instance_segmentation'), 2))
                str3 = str(round(self.res.Node.getComputerPower_M('Image_segmentation'), 2))
                str4 = str(round(self.res.Node.getComputerPower_M('Object_detection'), 2))
                str5 = str(round(self.res.Node.getComputerPower_M('Natural_language_processing'), 2))
                str6 = str(round(self.res.Node.getComputerPower_M('Speech_recognition'), 2))
                str7 = str(round(self.res.Node.getComputerPower_M('Intelligent_recommendation'), 2))
                str8 = str(round(self.res.Node.getComputerPower_M('Reinforcement_learning'), 2))
                msg = self.clientID + ':' + str1 + ':' + str2 + ':' + str3 + ':' + str4 + ':' + str5 + ':' + str6 + ':' + str7 + ':' + str8
                return msg

            elif topic == 'mqtt/system/ComputerPower_A':
                str1 = str(fabs(round(self.res.Node.getComputerPower_A('Image_classification'), 2)))
                str2 = str(fabs(round((self.res.Node.getComputerPower_A('Instance_segmentation')), 2)))
                str3 = str(fabs(round(self.res.Node.getComputerPower_A('Image_segmentation'), 2)))
                str4 = str(fabs(round(self.res.Node.getComputerPower_A('Object_detection'), 2)))
                str5 = str(fabs(round(self.res.Node.getComputerPower_A('Natural_language_processing'), 2)))
                str6 = str(fabs(round(self.res.Node.getComputerPower_A('Speech_recognition'), 2)))
                str7 = str(fabs(round(self.res.Node.getComputerPower_A('Intelligent_recommendation'), 2)))
                str8 = str(fabs(round(self.res.Node.getComputerPower_A('Reinforcement_learning'), 2)))
                msg = self.clientID + ':' + str1 + ':' + str2 + ':' + str3 + ':' + str4 + ':' + str5 + ':' + str6 + ':' + str7 + ':' + str8
                return msg

            elif topic == 'mqtt/system/Storage_M':
                str1 = str(round(getMEMInfo()[1], 2)) + 'GB'
                str2 = str(round(getDiskInfo()[1], 2)) + 'GB'
                str3 = str(round(getCacheInfo(), 2)) + 'GB'  # cache 没有总大小（？，它是根据负载动态变化的
                msg = self.clientID + ':' + str1 + ':' + str2 + ':' + str3
                return msg

            elif topic == 'mqtt/system/Storage_A':
                str1 = str(fabs(round(getMEMInfo()[2], 2))) + 'GB'
                str2 = str(fabs(round(getDiskInfo()[2], 2))) + 'GB'
                str3 = str(fabs(round(getCacheInfo(), 2))) + 'GB'
                msg = self.clientID + ':' + str1 + ':' + str2 + ':' + str3
                return msg

            elif topic == 'mqtt/system/Computing_Power_Configuration/Computing_Units_Set/Processor/CPU_Specifications':
                str1 = str(self.res.Node.getCPU_Specifications('Accelerated_Instruction'))
                str2 = str(round(self.res.Node.getCPU_Specifications('Base_Frequency_Of_Core'), 2))+'GHz'
                str3 = str(round(self.res.Node.getCPU_Specifications('Number_Of_Cores'), 2))
                str4 = str(self.res.Node.getCPU_Specifications('Architecture'))
                str5 = str(round(self.res.Node.getCPU_Specifications('L1_Cache'), 2))+'GB'
                str6 = str(round(self.res.Node.getCPU_Specifications('L2_Cache'), 2))+'GB'
                str7 = str(round(self.res.Node.getCPU_Specifications('L3_Cache'), 2)) + 'GB'
                str8 = str(round(self.res.Node.getCPU_Specifications('Bus'), 2)) +'GHz'
                str9 = str(round(self.res.Node.getCPU_Specifications('Number_Of_Threads'), 2))
                str10 = 'CPU'+str(round(self.res.Node.getCPU_Specifications('ID')))
                #处理器速度集合
                str11 = str(round(self.res.Node.getSpeed_Attributes('FLOPS'), 2))+'GFlops'
                str12 = str(self.res.Node.getSpeed_Attributes('Operand_Types'))
                str13 = str(round(self.res.Node.getSpeed_Attributes('number_digit')))
                msg= self.clientID+':'+str1+':'+str2+':'+str3+':'+str4+':'+str5+':'+str6+':'+str7+':'+str8+':'+str9+':'+str10+':'+str11+':'+str12+':'+str13
                return msg

            elif topic == 'mqtt/system/Computing_Power_Configuration/Computing_Units_Set/Processor/GPU_Specifications':
                str1 = str(round(self.res.Node.getGPU_Specifications('Graphics_Memory_size'),2))+'GB'
                str2 = str(round(self.res.Node.getGPU_Specifications('Graphics_Memory_Bandwidth'),2))+'MBps'
                str3 = str(round(self.res.Node.getGPU_Specifications('clock_frequency'), 2))+'GHz'
                str4 = str(self.res.Node.getGPU_Specifications('Supported_Interface_Name'))
                str5 = str(self.res.Node.getGPU_Specifications('Supported_Interface_Version'))
                str6 = str(round(self.res.Node.getGPU_Specifications('Number_of_Stream_Processors'), 2))
                str7 = 'GPU'+str(round(self.res.Node.getGPU_Specifications('ID')))
                #处理器速度集合
                str8 = str(round(self.res.Node.getSpeed_Attributes('FLOPS'), 2)) + 'GFlops'
                str9 = str(self.res.Node.getSpeed_Attributes('Operand_Types'))
                str10 = str(round(self.res.Node.getSpeed_Attributes('number_digit')))
                msg = self.clientID + ':' + str1 + ':' + str2 + ':' + str3 + ':' + str4 + ':' + str5+':'+str6+':'+ str7+ ':' + str8+':'+str9+':'+ str10
                return msg
            elif topic == 'mqtt/system/Computing_Power_Configuration/Computing_Units_Set/Memory/Attributes':
                str1 = str(self.res.Node.getMemory_Attributes('ID'))
                str2 = str(self.res.Node.getMemory_Attributes('Correction'))
                msg = self.clientID + ':' + str1 + ':' + str2
                return msg

            elif topic =='mqtt/system/Computing_Power_Configuration/Computing_Units_Set/Memory/Specifications':
                str1 = str(round(self.res.Node.getMemory_Specifications('容量'),2))+'GB'
                str2 = str(round(self.res.Node.getMemory_Specifications('内存带宽'),2))+'MHZ'
                str3 = str(round(self.res.Node.getMemory_Specifications('延迟'),2))+'ms'
                str4 = str(self.res.Node.getMemory_Specifications('类型'))
                str5 = str(self.res.Node.getMemory_Specifications('通道数'))
                msg = self.clientID + ':' + str1 + ':' + str2 + ':' + str3 + ':' + str4 + ':' + str5
                return msg

            elif topic =='mqtt/system/Computing_Power_Configuration/Communicate_Units_Set/Communicate_Unit/Attributes':
                str1 = str(self.res.Node.getCommunicate_Attributes('ID'))
                msg = self.clientID + ':' + str1
                return msg

            elif topic == 'mqtt/system/Computing_Power_Configuration/Communicate_Units_Set/Communicate_Unit/Specifications':
                str1 = str(round(self.res.Node.getCommunicate_Specifications('带宽上行'),2))+'Mbps'
                str2 = str(round(self.res.Node.getCommunicate_Specifications('带宽下行'),2))+'Mbps'
                str3 = str(round(self.res.Node.getCommunicate_Specifications('时延'),2))+'s'
                str4 = str(round(self.res.Node.getCommunicate_Specifications('FIB转发速率'),2))+'MBps'
                str5 = str(round(self.res.Node.getCommunicate_Specifications('IPSec速率'),2))+'MBps'
                str6 = str(round(self.res.Node.getCommunicate_Specifications('虚拟网络带宽'),2))+'MBps'
                str7 = str(round(self.res.Node.getCommunicate_Specifications('防火墙损耗'),2))+'MBps'
                str8 = str(self.res.Node.getCommunicate_Specifications('支持的网络协议'))
                msg = self.clientID + ':' + str1 + ':' + str2 + ':' + str3 + ':' + str4 + ':' + str5 + ':' + str6 + ':' + str7+':'+str8
                return msg

            elif topic == 'mqtt/system/Computing_Power_Configuration/Storage_Units_Set/Storage_Unit/Attributes':
                str1 = str(self.res.Node.getStorage_Attributes('ID'))
                msg=self.clientID + ':' + str1
                return msg

            elif topic == 'mqtt/system/Computing_Power_Configuration/Storage_Units_Set/Storage_Unit/Specifications':
                str1 = str(round(self.res.Node.getStorage_Specifications('容量'),2))+'GB'
                str2 = str(round(self.res.Node.getStorage_Specifications('存储带宽'), 2))+'GB'
                str3 = str(round(self.res.Node.getStorage_Specifications('IOPS'), 2))+'MHz'
                str4 = str(round(self.res.Node.getStorage_Specifications('备份数量'), 2))
                str5 = str(round(self.res.Node.getStorage_Specifications('可靠性'), 2))+'%'
                msg = self.clientID + ':' + str1 + ':' + str2 + ':' + str3 + ':' + str4 + ':' + str5
                return msg
            elif topic == 'mqtt/system/Computing_Power_Configuration/Software_env':
                str1 = str(self.res.Node.config.getSoftwareenv())
                msg = self.clientID + ':' + str1
                return msg
            elif topic == 'mqtt/system/Terminal_Device_or_not':
                str1 = str(self.res.Node.getTerminal_Attributes('type'))
                if str1 == '1':
                    str2 = str(self.res.Node.getTerminal_Attributes('类型'))
                    str3 = str(round(self.res.Node.getTerminal_Attributes('续航时长'),2))
                    msg = self.clientID + ':' + str1 + ':' + str2 + ':' + str3
                    return msg
                else:
                    str2 = str(round(self.res.Node.getTerminal_Attributes('能效'),2))
                    str3 = str(round(self.res.Node.getTerminal_Attributes('经度-度'),2))
                    str4 = str(round(self.res.Node.getTerminal_Attributes('经度-分'),2))
                    str5 = str(round(self.res.Node.getTerminal_Attributes('经度-秒'),2))
                    str6 = str(round(self.res.Node.getTerminal_Attributes('纬度-度'),2))
                    str7 = str(round(self.res.Node.getTerminal_Attributes('纬度-分'),2))
                    str8 = str(round(self.res.Node.getTerminal_Attributes('纬度-秒'),2))
                    msg = self.clientID + ':' + str1 + ':' + str2 + ':' + str3 + ':' + str4 + ':' + str5 + ':' + str6 + ':' + str7 + ':' + str8
                    return msg
            elif topic == 'mqtt/system/Usage':
                str1 = str(fabs(round(self.res.Node.config.getUsage('ProcessorUsage'), 2))) + '%'
                str2 = str(fabs(round(self.res.Node.config.getUsage('MemoryUsage'), 2))) + '%'
                str3 = str(fabs(round(self.res.Node.config.getUsage('MemBandUsage'), 2))) + '%'
                str4 = str(fabs(round(self.res.Node.config.getUsage('NetBandUpUsage'), 2))) + '%'
                str5 = str(fabs(round(self.res.Node.config.getUsage('NetBandDownUsage'), 2))) + '%'
                str6 = str(fabs(round(self.res.Node.config.getUsage('IOPSUsage'), 2))) + '%'
                str7 = str(fabs(round(self.res.Node.config.getUsage('StorageUsage'), 2))) + '%'
                msg = self.clientID + ':' + str1 + ':' + str2 + ':' + str3 + ':' + str4 + ':' + str5 + ':' + str6 + ':' + str7
                return msg



            elif topic == 'NEW':
                pass
            elif topic == 'mqtt/system/Computing_Power_Configuration/Computing_Power':
                str1=str(random.randint(80,100))
                msg=self.clientID+':'+str1
                return msg

    # def run(
    #     self,
    # ):
    #     '''运行发布者'''
    #     self.connect_mqtt()
    #     """对于 server agent  sub只用于维护虚拟资源"""
    #     self.subscribe()
    #     # 运行一个线程来自动调用loop()处理网络事件, 非阻塞
    #     self.client.loop_start()
    #     self.publish()

    def run(
        self,
    ):
        '''运行发布者'''
        self.connect_mqtt()
        """对于 server agent  sub只用于维护虚拟资源"""
        self.subscribe()
        # 运行一个线程来自动调用loop()处理网络事件, 非阻塞
        self.client.loop_start()

        '''发布消息'''
        while self.infoChange():
            '''每隔 timeslot 秒发布一次服务器信息'''
            time.sleep(timeslot)
            if self.publish_model:
                for topic in self.topics:
                    if not self.infoChange(topic):
                        continue
                    """ TODO+ getInfo """
                    self.msg = self.getInfo(topic)
                    # print(self.msg)
                    result = self.client.publish(topic, self.msg)
                    status = result[0]
                    if status == 0:
                        print(f"Send `{self.msg}` to topic `{topic}`")
                        pass
                    else:
                        print(f"Failed to send message to topic {topic}")
            else:
                # TODO 定时向服务器发送该节点是谁
                pass

    def infoChange(
        self,
        topic:str = 'all'
    ) -> bool:
        """TODO- check data change state"""
        if topic == 'all':
            """ CHECK ALL DATA"""
            pass
        elif topic == 'mqtt/system/CPU_PERCENT':
            """ CHECK CPU_PERCENT"""
            pass

        return True


if __name__ == '__main__':
    server = ServerAgent(
        keepalive = keepalive,
        broker = brokerIP,
        port = port,
        clientID = clientID,
        topics = topics,
        virtual_topics = virtual_topics,
        virtual_res = True,
    )
    server.res.Node = Node('/8080', 'c1', 1,200, ResourceConfig(), )
    # server.res.Node = Node('1@node', 'c1', 1, ResourceConfig(), )
    server.res.Node.safety = 'GOOD' 
    # str1 = server.res.Node.getComputerPower('Image_classification')
    # print(str1)
    server.run()



