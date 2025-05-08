#!/usr/bin/python3
# -*- coding:utf-8 -*-
############################
# File Name: taskAgent.py
# Author: 
# mail: 
# Create Time: 2023/5/4 11:48:46
############################
# from icecream import install
# install()
# import time
# def timestamp():
#    return '%s |> ' % time.strftime('%Y-%m-%d %T')
# ic.configureOutput(prefix=timestamp)

import time
import threading

import numpy as np
from paho.mqtt import client as mqtt_client

import argparse
from taskModule import TaskManager
from taskModule import tid_maker

parser = argparse.ArgumentParser(description='')
parser.add_argument('--broker', type=str, default='127.0.0.1')
parser.add_argument('--port', type=int, default=1883)
parser.add_argument('--keepalive', type=int, default=60)
parser.add_argument('--timeslot', type=int, default=5)
parser.add_argument('--clientID', type=str, default='task-manager')
args = parser.parse_known_args()[0]
brokerIP = args.broker
port = args.port
keepalive = args.keepalive
clientID = args.clientID
timeslot = args.timeslot
print(args)

"""TODO+ 依据standard 添加 """
topics = [
    # 'mqtt/task/generate',
    # 'mqtt/subtask/generate',
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
]
"""TODO+ 依据virtual resource """
virtual_topics = [
    'mqtt/virtual/deploy',
    'mqtt/virtual/updateProcessor',  # 格式：   节点 : 算法 : 算力值
    'mqtt/virtual/updateStorage',  # 格式：   节点 : 内存字节数 : 缓存字节数 : 外存字节数
    'mqtt/virtual/performance/response_time',
    'mqtt/virtual/performance/energy',
    'mqtt/virtual/performance/stability',
    'mqtt/virtual/performance/security',
]
virtual_release_topics = [
    'mqtt/virtual/release',
    'mqtt/virtual/releaseProcessor',  # 格式：   节点 : 算法 : 算力值
    'mqtt/virtual/releaseStorage',  # 格式：   节点 : 内存字节数 : 缓存字节数 : 外存字节数
]

node_list = [
    'cloud',
    'Raspberry1',
    'Jetson1'
]

class TaskAgent():
    def __init__(
            self,
            keepalive: int,
            broker: str,
            clientID: str,
            port: int,
            topics: list = [
                # 'mqtt/task/generate',
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
                'mqtt/subtask/require/security'
            ],
            virtual_topics: list = [
                'mqtt/virtual/deploy',
                'mqtt/virtual/updateProcessor',
                'mqtt/virtual/updateStorage',
                'mqtt/virtual/performance/response_time',
                'mqtt/virtual/performance/energy',
                'mqtt/virtual/performance/stability',
                'mqtt/virtual/performance/security',
            ],
            virtual_release_topics: list = [
                'mqtt/virtual/release',
                'mqtt/virtual/releaseProcessor',
                'mqtt/virtual/releaseStorage',
            ],
            instr_topics: list = [
                'mqtt/task/class',
            ],
    ) -> object:
        self.client = None
        """ task info """
        self.topics = topics
        """ res update info """
        self.virtual_topics = virtual_topics
        self.virtual_release_topics = virtual_release_topics
        """ task generate ctl """
        self.instr_topics = instr_topics
        self.keepalive = keepalive
        self.broker = broker
        self.port = port
        self.clientID = clientID
        self.msg = {}
        self.msg_list = {}
        self.taskM = None
        self.tasks = TaskManager()
        self.taskID = tid_maker()
        self.subtaskID = ''

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

    """ pub 可以最后修改 ，输入... 后pub的逻辑"""
    """TODO 2024-1-22 增加真实任务和子任务的发布逻辑"""
    def publish(
            self,
    ):
        '''发布任务 以及 任务导致的虚拟资源更新消息 '''
        while True:

            """ TODO+ getTask"""
            msg = []
            msg.append(self.getTask(np.random.randint(0, 7)))
            """ 发布产生任务的信息 """
            topic = 'mqtt/task/generate'
            result = self.client.publish(topic, msg[0][topic])
            status = result[0]
            if status == 1:
            #     print(f"Send `{msg[0][topic]}` to topic `{topic}`")
            # else:
                print(f"Failed to send message to topic {topic}, {result}")

            """ 发布子任务的信息 """
            for subtask in self.tasks.subtasks:
                self.taskM = subtask
                msg.append(self.getSubTask())

            for i in range(1, len(self.tasks.subtasks) + 1):
                # self.subtask_publish(msg[i])
                thread_lock = threading.Lock()
                tmpThread = threading.Thread(target=self.subtask_publish, args=(msg[i],))
                tmpThread.start()

            '''每隔 timeslot 秒发布任务'''
            time.sleep(timeslot)

    def multi_thread_publish(
            self,
            lock,
            taskClass: int = 0,
    ):
        msg = []
        msg.append(self.getTask(taskClass))
        """ 发布产生任务的信息 """
        topic = 'mqtt/task/generate'
        result = self.client.publish(topic, msg[0][topic])
        status = result[0]
        if status == 1:
        #     print(f"Send `{msg[0][topic]}` to topic `{topic}`")
        # else:
            print(f"Failed to send message to topic {topic}")

        """ 发布子任务的信息 """
        for subtask in self.tasks.subtasks:
            self.taskM = subtask
            msg.append(self.getSubTask())

        for i in range(1, len(self.tasks.subtasks) + 1):
            # self.subtask_publish(msg[i])
            thread_lock = threading.Lock()
            tmpThread = threading.Thread(target=self.subtask_publish, args=(msg[i],))
            tmpThread.start()

    def subtask_publish(
            self,
            msg,
    ):
        # lock.acquire()
        '''发布任务 以及 任务导致的虚拟资源更新消息 '''
        """ TODO+ getTask"""
        # msg = self.getSubTask()
        """ 对检测者pub信息 """
        for topic in self.topics:
            result = self.client.publish(topic, msg[topic])
            status = result[0]
            if status == 1:
            #     print(f"Send `{msg[topic]}` to topic `{topic}`")
            # else:
                print(f"Failed to send message to topic {topic}")
        """ 对 virtual res update 信息 """
        for topic in self.virtual_topics:
            # print(self.msg)
            result = self.client.publish(topic, msg[topic])
            status = result[0]
            if status == 1:
            #     print(f"Send `{msg[topic]}` to topic `{topic}`")
            # else:
                print(f"Failed to send message to topic {topic}")
        """ TODO finish task pub the END SIGNAL """
        time.sleep(msg['duration'])
        """ 释放的虚拟资源 信息pub """
        for topic in self.virtual_release_topics:
            # print(self.msg)
            result = self.client.publish(topic, msg[topic])
            status = result[0]
            if status == 1:
            #     print(f"Send `{msg[topic]}` to topic `{topic}`")
            # else:
                print(f"Failed to send message to topic {topic}")
        # lock.release()



    def subscribe(
            self,
    ):
        '''订阅主题并接收消息'''

        def on_message(client, userdata, msg):
            # print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
            topic = msg.topic
            """ REMOTE """
            if topic == 'mqtt/task/class':
                # print('recieve task')
                """ 收到遥控就开个task 线程 """
                self.publish_REMOTE(int(msg.payload.decode()))
            elif topic == 'NEW':
                pass

        # 订阅指定消息主题
        for topic in self.instr_topics:
            self.client.subscribe(topic)
            # print(topic)
        self.client.on_message = on_message

    """ CORE FUNCTION """
    """TODO 2024-1-22 增加获取真实任务信息的逻辑，获取不到的接着用虚拟信息"""
    def getTask(
            self,
            taskClass: int = 0,
    ):
        msg = {}
        self.tasks.generate(taskClass)
        self.taskID = tid_maker()
        # msg['taskid'] = self.taskM.getTaskID()
        topic = 'mqtt/task/generate'
        msg[topic] = self.clientID + '产生任务:' + str(self.taskID) + ':该任务包含子任务数量:' + str(len(self.tasks.subtasks)) + ':'
        return msg

    def getSubTask(
            self,
    ) -> str:
        """TODO+ 添加更多获取资源方式"""
        """
        return 
        [
        topic1 : msg1,
        topic2 : msg2,
        ... ... ... ...
        topicn : msgn,
        ]
        """
        msg = {}
        """ TODO+ 按标准内容写 任务信息"""
        # new task
        # self.tasks.generate(taskClass)
        msg['taskid'] = self.taskM.getTaskID()
        # topic = 'mqtt/task/generate'
        # msg[topic] = self.clientID + '产生任务:' + str(self.taskID) + ':该任务包含:' + str(len(self.tasks.subtasks)) + ':个子任务'
        # for self.taskM in self.tasks.subtasks:
        for topic in self.topics:
            # if topic == 'mqtt/subtask/generate':  # 任务产生的客户端 + ':' + 任务id
            self.subtaskID = '任务~' + str(self.taskID) + '~子任务:' + str(self.taskM.getTaskID())
                # msg[topic] = self.clientID + '产生' + self.subtaskID
            if topic == 'mqtt/subtask/model/operand':
                msg[topic] = self.subtaskID
                operands = self.taskM.getOperandReq()
                for operand in operands:
                    for i in range(len(operand)):
                        msg[topic] = msg[topic] + ':' + str(operand[i])
            elif topic == 'mqtt/subtask/model/data':
                msg[topic] = self.subtaskID
                datas = self.taskM.getData()
                for data in datas:
                    msg[topic] = msg[topic] + ':' + str(round(data, 2)) + 'GB'
                # msg[topic] = self.subtaskID + ':' + str(round(self.taskM.getData(), 2)) + 'GB'
            elif topic == 'mqtt/subtask/require/algorithm':
                msg[topic] = self.subtaskID + ':' + self.taskM.getAlgorithm()
            elif topic == 'mqtt/subtask/require/compute_power':
                msg[topic] = self.subtaskID + ':' + str(round(self.taskM.getComputePower(), 2))
            elif topic == 'mqtt/subtask/require/mem':
                msg[topic] = self.subtaskID + ':' + str(round(self.taskM.getMemReq(), 2)) + 'GB'
            elif topic == 'mqtt/subtask/require/cache':
                msg[topic] = self.subtaskID + ':' + str(round(self.taskM.getCacheReq(), 2)) + 'GB'
            elif topic == 'mqtt/subtask/require/disk':
                msg[topic] = self.subtaskID + ':' + str(round(self.taskM.getDiskReq(), 2)) + 'GB'
            elif topic == 'mqtt/subtask/require/network':
                msg[topic] = self.subtaskID
                protocols = self.taskM.getNetworkProtocol()
                for protocol in protocols:
                    msg[topic] = msg[topic] + ':' + protocol
            elif topic == 'mqtt/subtask/require/io_rate':
                min_, max_ = self.taskM.getIORate()
                msg[topic] = self.subtaskID + ':' + str(round(min_, 2)) + ':' + str(round(max_, 2))
            elif topic == 'mqtt/subtask/require/delay':
                msg[topic] = self.subtaskID + ':' + str(round(self.taskM.getDelay(), 2)) + 's'
            elif topic == 'mqtt/subtask/require/response_time':
                min_, max_, ave_ = self.taskM.getRespTime()
                msg[topic] = self.subtaskID + ':' + str(round(min_, 2)) + 's' + ':' + str(round(max_, 2)) + 's' + ':' + str(
                        round(ave_, 2)) + 's'
            elif topic == 'mqtt/subtask/require/energy':
                msg[topic] = self.subtaskID + ':' + str(round(self.taskM.getEnergy(), 2)) + 'J'
            elif topic == 'mqtt/subtask/require/stability':
                # msg[topic] = self.subtaskID + ':' + self.taskM.getStability()
                msg[topic] = self.subtaskID + ':' + ' '
            elif topic == 'mqtt/subtask/require/security':
                # msg[topic] = self.subtaskID + ':' + self.taskM.getSecurity()
                msg[topic] = self.subtaskID + ':' + ' '
        """ TODO+ 按你自己认为的逻辑 写当前任务导致的CPU增量delta"""

        node = node_list[np.random.randint(0, 3)]  # 将任务调度到node节点上
        for topic in self.virtual_topics:
            if topic == 'mqtt/virtual/deploy':
                msg[topic] = self.subtaskID + '调度到节点' + node
            elif topic == 'mqtt/virtual/updateProcessor':
                msg[topic] = node + ':' + self.taskM.getAlgorithm() + ':' + str(round(self.taskM.getComputePower(), 2))
            elif topic == 'mqtt/virtual/updateStorage':
                msg[topic] = node + ':' + str(round(self.taskM.getMemReq(), 2)) + ':' + str(
                    round(self.taskM.getCacheReq(), 2)) + ':' + str(
                    round(self.taskM.getDiskReq(), 2))

            #  TODO 2023-10-29 任务调度到设备后可达性能 如何设计:
            # 子任务ID:节点ID:响应时间
            # 子任务ID:节点ID:能量
            # 子任务ID:节点ID:稳定性（暂时设为空）
            # 子任务ID:节点ID:安全性（暂时设为空）
            elif topic == 'mqtt/virtual/performance/response_time':
                min_, max_, ave_ = self.taskM.getRespTime()
                msg[topic] = str(self.taskM.getTaskID()) + ':' + node + ':' + str(
                    max(round(min_ - 1, 2), 0.1)) + 's' + ':' + str(
                    max(round(max_ - 1, 2), 0.1)) + 's' + ':' + str(
                    max(round(ave_ - 1, 2), 0.1)) + 's'  # 响应时间： max(任务需要的响应时间 - 1, 0.1)
            elif topic == 'mqtt/virtual/performance/energy':
                msg[topic] = str(self.taskM.getTaskID()) + ':' + node + ':' + str(
                    max(round(self.taskM.getEnergy() - 1, 2), 0.1)) + 'J'  # 响应时间： max(任务需要的能量 - 1, 0.1)
            elif topic == 'mqtt/virtual/performance/stability':
                # msg[topic] = str(self.taskM.getTaskID()) + ':' + node + ':' + self.taskM.getStability()  # 暂时不显示
                msg[topic] = str(self.taskM.getTaskID()) + ':' + node + ':' + ' '
            elif topic == 'mqtt/virtual/performance/security':
                # msg[topic] = str(self.taskM.getTaskID()) + ':' + node + ':' + self.taskM.getSecurity()  # 暂时不显示
                msg[topic] = str(self.taskM.getTaskID()) + ':' + node + ':' + ' '



        """ TODO 持续时间 和 模拟参数间关系 如何设计"""
        msg.setdefault('duration', np.random.randint(20, 50))

        for topic in self.virtual_release_topics:
            if topic == 'mqtt/virtual/release':
                msg[topic] = self.subtaskID  # self.subtaskID + ':运行结束，释放资源'
            elif topic == 'mqtt/virtual/releaseProcessor':
                msg[topic] = node + ':' + self.taskM.getAlgorithm() + ':' + str(round(self.taskM.getComputePower(), 2))
            elif topic == 'mqtt/virtual/releaseStorage':
                msg[topic] = node + ':' + str(round(self.taskM.getMemReq(), 2)) + ':' + str(
                    round(self.taskM.getCacheReq(), 2)) + ':' + str(
                    round(self.taskM.getDiskReq(), 2))
        return msg



    def run(
            self,
    ):
        '''运行发布者'''
        self.connect_mqtt()
        """对于 server agent  sub只用于维护虚拟资源"""
        # self.subscribe()
        # # 运行一个线程来自动调用loop()处理网络事件, 非阻塞
        # self.client.loop_start()
        # self.publish_HUMAN_IN_LOOP()
        self.publish()

    def publish_HUMAN_IN_LOOP(
            self,
    ):
        while True:
            tc = input('请输入发布的任务类型：')
            while tc == '' or tc < '0' or tc > '7':
                tc = input('任务类型错误，请重新输入：')
            thread_lock = threading.Lock()
            tmpThread = threading.Thread(target=self.multi_thread_publish, args=(thread_lock, int(tc),))
            tmpThread.start()
        # tmpThread.join()
        # self.test()

    def publish_REMOTE(
            self,
            tc: int = 0,
    ):
        thread_lock = threading.Lock()
        tmpThread = threading.Thread(target=self.multi_thread_publish, args=(thread_lock, tc,))
        tmpThread.start()
        tmpThread.join()
        # self.test()

    def test(self, ):
        time.sleep(3)
        print('multi-thread-test')


if __name__ == '__main__':
    task = TaskAgent(
        keepalive=keepalive,
        broker=brokerIP,
        port=port,
        clientID=clientID,
        topics=topics,
        virtual_topics=virtual_topics,
        # MODE = 'single',
        virtual_release_topics=virtual_release_topics,
    )
    # MODE = 'SINGLE_AUTO', 'MANAML', 'REMOTE'

    task.run()
    #the function must be defined.
    # what should
