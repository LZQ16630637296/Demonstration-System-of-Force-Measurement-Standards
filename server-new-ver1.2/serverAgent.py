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
from infoCollector import get_device_utilization, get_software_environment, get_full_storage_info, \
    get_net_full_info,get_system_memory_info, get_cpu_info, get_all_gpu_info, get_device_ip,\
get_device_latitude_longitude

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
        if topic == 'mqtt/system/Attribute':
            uri=str(get_device_ip())
            msg = self.clientID + ':' + uri + ':' + self.clientID +':'+ str(self.res.Node.unit_prize)+':'+str(self.res.Node.priority)
            return msg
        if not self.real_res:
            if topic == 'NEW':
                pass
        else:
            if topic == 'mqtt/system/Computing_Power_Configuration/Computing_Units_Set/Processor/CPU_Specifications':
                cpus=get_cpu_info()
                msg=''
                for i in range(len(cpus)):
                    cpu=cpus[i]
                    if(i>=1):
                        msg+=';'
                    str1=self.clientID+'_CPU_'+str(i)
                    # str2=cpu['加速指令能力']
                    str2=str(self.res.Node.getCPU_Specifications('Accelerated_Instruction'))
                    str3=str(cpu['内核基频'])
                    str4=str(cpu['内核数'])
                    str5 = str(cpu['架构'])
                    str6 = str(cpu['一级缓存'])
                    str7 = str(cpu['二级缓存'])
                    str8 = str(cpu['三级缓存'])
                    # str9 = cpu['总线']
                    # str6 = str(int(round(self.res.Node.getCPU_Specifications('L1_Cache'), 2)))
                    # str7 = str(int(round(self.res.Node.getCPU_Specifications('L2_Cache'), 2)))
                    # str8 = str(int(round(self.res.Node.getCPU_Specifications('L3_Cache'), 2)))
                    str9 = str(round(self.res.Node.getCPU_Specifications('Bus'), 2))
                    str10 = str(cpu['线程数'])
                    # str11 = cpu['速度集合/速度/每秒运算次数']
                    # str12 = cpu['速度集合/速度/操作数类型']
                    # str13 = cpu['速度集合/速度/位数']
                    str11 = str(self.res.Node.getSpeed_Attributes('FLOPS'))
                    str12 = str(self.res.Node.getSpeed_Attributes('Operand_Types'))
                    str13 = str(self.res.Node.getSpeed_Attributes('number_digit'))
                    msg += self.clientID + ':' + str1 + ':' + str2 + ':' + str3 + ':' + str4 + ':' + str5 + ':' + str6 + ':' + str7 + ':' + str8 + ':' + str9 + ':' + str10 + ':' + str11 + ':' + str12 + ':' + str13
                return msg
            elif topic == 'mqtt/system/Computing_Power_Configuration/Computing_Units_Set/Processor/GPU_Specifications':
                gpus=get_all_gpu_info()
                if(len(gpus)>=1):
                    msg=''
                    for i in range(len(gpus)):
                        if(i>=1):
                            msg+=';'
                        gpu=gpus[i]
                        str1 = self.clientID+'_GPU_'+str(i)
                        str2=  str(gpu['显存大小'])
                        # str3 = str(gpu['显存带宽'])
                        # str4 = str(gpu['时钟频率'])
                        # str5 = str(gpu['流处理器数量'])
                        str3 = str(int(round(self.res.Node.getGPU_Specifications('Graphics_Memory_Bandwidth'), 2)))
                        str4 = str(round(self.res.Node.getGPU_Specifications('clock_frequency'), 2))
                        # str6 = str(gpu['型号'])
                        # str9 = str(gpu['接口名称'])
                        # str10 = str(gpu['接口版本号'])
                        # str11 = str(gpu['速度'])
                        # str12 = str(gpu['位数'])
                        # str13 = str(gpu['操作数'])
                        str5 = str(self.res.Node.getGPU_Specifications('Supported_Interface_Name'))
                        str6 = str(self.res.Node.getGPU_Specifications('Supported_Interface_Version'))
                        str7 = str(round(self.res.Node.getGPU_Specifications('Number_of_Stream_Processors'), 2))
                        str8 = str(self.res.Node.getSpeed_Attributes('FLOPS'))
                        str9 = str(self.res.Node.getSpeed_Attributes('Operand_Types'))
                        str10 = str(self.res.Node.getSpeed_Attributes('number_digit'))
                        msg += self.clientID + ':' + str1 + ':' + str2 + ':' + str3 + ':' + str4 + ':' + str5+':'+str6+':'+ str7+ ':' + str8+':'+str9+':'+ str10
                    return msg
            elif topic == 'mqtt/system/Computing_Power_Configuration/Computing_Units_Set/Processor/FPGA_Specifications':
                fpgas =[]#get_all_fpga_info()
                if(len(fpgas)>=1):
                    msg=''
                    for i in range(len(fpgas)+1):#暂时无FPGA，虚构一个替代
                        if(i>=1):
                            msg+=';'
                        #fpga=fpgas[i]
                        str1 = self.clientID + '_FPGA_' + str(i)
                        # str2 = str(fpga['M20K存储器容量'])
                        # str3 = str(fpga['精度可调DSP模块'])
                        # str4 = str(fpga['逻辑单元LE'])
                        # str5 = str(fpga['ALM'])
                        str2 = str(self.res.Node.getFPGA_Specifications('M20K'))
                        str3 = str(self.res.Node.getFPGA_Specifications('DSP'))
                        str4 = str(self.res.Node.getFPGA_Specifications('LE'))
                        str5 = str(self.res.Node.getFPGA_Specifications('ALM'))
                        # 处理器速度集合
                        str6 = str(self.res.Node.getSpeed_Attributes('FLOPS'))
                        str7 = str(self.res.Node.getSpeed_Attributes('Operand_Types'))
                        str8 = str(self.res.Node.getSpeed_Attributes('number_digit'))
                        msg+=self.clientID + ':' + str1 + ':' + str2+ ':' + str3+ ':' + str4+ ':' + str5 + ':' + str6+ ':' + str7+ ':' + str8
                    return msg
            elif topic =='mqtt/system/Computing_Power_Configuration/Computing_Units_Set/Memory/Specifications':
                mem_info=get_system_memory_info()
                str1 = self.clientID + '_memory_' + (self.res.Node.getMemory_Attributes('ID'))
                # str2 = mem_info['纠错方式']
                str2 = str(self.res.Node.getMemory_Attributes('Correction'))
                str3 = str(mem_info['总容量'])
                # str4 = mem_info['内存带宽']
                # str5 = mem_info['延迟']
                # str6 = mem_info['类型']
                # str7 = mem_info['通道数']
                str4 = str(round(self.res.Node.getMemory_Specifications('内存带宽'),2))
                str5 = str(round(self.res.Node.getMemory_Specifications('延迟'),2))
                str6 = str(self.res.Node.getMemory_Specifications('类型'))
                str7 = str(self.res.Node.getMemory_Specifications('通道数'))
                msg = self.clientID + ':' + str1 + ':' + str2 + ':' + str3 + ':' + str4 + ':' + str5 + ':' + str6 + ':' + str7
                return msg
            elif topic == 'mqtt/system/Computing_Power_Configuration/Communicate_Units_Set/Communicate_Unit/Specifications': ###获取的很慢
                units=get_net_full_info()
                msg=''
                for unit in units:
                    if(units.index(unit)>=1):
                        msg+=';'
                    str1=self.clientID+'_'+str(unit['ID'])
                    str2 = str(unit['带宽上行'])
                    str3 = str(unit['带宽下行'])
                    str4 = str(unit['时延'])
                    str5 = str(unit['FIB转发速率'])
                    # str6 = str(unit['IPSec速率'])
                    # str7 = str(unit['虚拟网络带宽'])
                    # str8 = str(unit['防火墙损耗'])
                    str9 = str(unit['支持的网络协议'])
                    # str10 = str(unit['DPDK-L3转发速率'])
                    # str11 = str(unit['可靠性'])
                    #str5 = str(round(self.res.Node.getCommunicate_Specifications('FIB转发速率'), 2))
                    str6 = str(round(self.res.Node.getCommunicate_Specifications('IPSec速率'), 2))
                    str7 = str(round(self.res.Node.getCommunicate_Specifications('虚拟网络带宽'), 2))
                    str8 = str(round(self.res.Node.getCommunicate_Specifications('防火墙损耗'), 2))
                    #str9 = str(self.res.Node.getCommunicate_Specifications('支持的网络协议'))
                    str10 = str(self.res.Node.getCommunicate_Specifications('DPDK-L3转发速率'))
                    str11 = str(self.res.Node.getCommunicate_Specifications('可靠性'))
                    msg += self.clientID + ':' + str1 + ':' + str2 + ':' + str3 + ':' + str4 + ':' + str5 + ':' + str6 + ':' + str7 + ':' + str8 + ':' + str9 + ':' + str10 + ':' + str11
                return msg
            elif topic == 'mqtt/system/Computing_Power_Configuration/Storage_Units_Set/Storage_Unit/Specifications':
                storage_units=get_full_storage_info()
                msg=''
                for i in range(len(storage_units)):
                    storage_unit=storage_units[i]
                    if(i>=1):
                        msg+=';'
                    str1 = self.clientID+'_'+str(storage_unit['ID'])
                    str2 = str(storage_unit['容量'])
                    #str3 = str(storage_unit['存储带宽'])
                    str3 = str(round(self.res.Node.getStorage_Specifications('存储带宽'), 2))
                    str4 = str(storage_unit['IOPS'])
                    #str5 = str(storage_unit['备份数量'])
                    #str6 = str(storage_unit['可靠性'])
                    #str7 = str(storage_unit['存储架构'])
                    #str8 = str(storage_unit['RAID级别'])
                    #str9 = str(storage_unit['冗余方式'])
                    str5 = str(round(self.res.Node.getStorage_Specifications('备份数量'), 2))
                    str6 = str(round(self.res.Node.getStorage_Specifications('可靠性'), 2))
                    str7 = str(self.res.Node.getStorage_Specifications('存储架构'))
                    str8 = str(self.res.Node.getStorage_Specifications('RAID级别'))
                    str9 = str(self.res.Node.getStorage_Specifications('冗余方式'))
                    msg +=  self.clientID + ':' + str1 + ':' + str2 + ':' + str3 + ':' + str4 + ':' + str5+ ':' + str6 + ':' + str7 + ':' + str8 + ':' + str9
                return msg
            elif topic == 'mqtt/system/Computing_Power_Configuration/Software_env':
                str1 = str(get_software_environment())
                msg = self.clientID + ':' + str1
                return msg
            elif topic == 'mqtt/system/Terminal_Device_or_not':
                str1 = str(self.res.Node.getTerminal_Attributes('type'))
                if str1 == '1':
                    str2 = str(self.res.Node.getTerminal_Attributes('类型'))
                    str3 = str(self.res.Node.getTerminal_Attributes('续航时长'))
                    msg = self.clientID + ':' + str1 + ':' + str2 + ':' + str3
                    return msg
                else:
                    str2 = str(round(self.res.Node.getTerminal_Attributes('能效'),2))
                    coordinates = get_device_latitude_longitude()
                    (lat_degrees, lat_minutes, lat_seconds), (lon_degrees, lon_minutes, lon_seconds) = coordinates
                    str3 = str(lon_degrees)
                    str4 = str(lon_minutes)
                    str5 = str(lon_seconds)
                    str6 = str(lat_degrees)
                    str7 = str(lat_minutes)
                    str8 = str(lat_seconds)
                    msg = self.clientID + ':' + str1 + ':' + str2 + ':' + str3 + ':' + str4 + ':' + str5 + ':' + str6 + ':' + str7 + ':' + str8
                    return msg
            elif topic == 'mqtt/system/Usage':
                utiliz=get_device_utilization()
                str1 = str(utiliz['处理器占用率'])
                str2 = str(utiliz['内存占用率'])
                #str3 = str(utiliz['内存带宽占用率'])
                str3=str(fabs(round(self.res.Node.config.getUsage('MemBandUsage'), 2)))
                str4 = str(utiliz['网络带宽占用率']['上行'])
                str5 = str(utiliz['网络带宽占用率']['下行'])
                #str6 = str(utiliz['IOPS占用率'])
                str6=str6 = str(fabs(round(self.res.Node.config.getUsage('IOPSUsage'), 2)))
                str7 = str(utiliz['存储空间占用率'])
                msg = self.clientID + ':' + str1 + ':' + str2 + ':' + str3 + ':' + str4 + ':' + str5 + ':' + str6 + ':' + str7
                return msg



            elif topic == 'NEW':
                pass
            elif topic == 'mqtt/system/Computing_Power_Configuration/Computing_Power':
                str1=str(random.randint(80,100))
                msg=self.clientID+':'+str1
                return msg


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



