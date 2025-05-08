#!/usr/bin/python3
# -*- coding:utf-8 -*-
############################
# File Name: taskModule.py
# Author: 
# mail: 
# Create Time: 2023/5/4 15:46:11
############################
import string
import datetime
import numpy as np

""" TODO + 
TaskType - 类型
         - 能生成实例
         - 需要更多参数 如 ID、模型参数、 算力req、存储req、网络、req....
Task - 类型的实例
     - 有具体的任务参数值 如 存储Req = 100MB
     - 包括 virtual 需求的值 以及 标准中需要的值 
TaskManager - 类型与实例的管理 
"""


class TaskManager():
    def __init__(
            self,
    ):
        self.taskType = []
        self.taskType.append(
            TaskType(
                operandReq=[[10, 10, 10, 10, 0, 10, 0, 10, 10, 0, 10, 0]],
                data=[15],
                algorithm='图像分类',
                computePower=10.0,
                memReq=4.5,
                cacheReq=1.3,
                diskReq=6.7,
                networkProtocol=['TCP/IP', 'Bluetooth'],
                minIORate=10.0,
                maxIORate=20.0,
                delay=1.0,
                minRespTime=10.0,
                maxRespTime=20.0,
                aveRespTime=15.0,
                energy=10.0,
                stability='good',
                security='good',
            )
        )
        self.taskType.append(
            TaskType(
                operandReq=[[10, 10, 0, 10, 0, 10, 0, 10, 10, 0, 10, 0]],
                data=[10],
                algorithm='实例分割',
                computePower=20.0,
                memReq=5.3,
                cacheReq=3.1,
                diskReq=0.0,
                networkProtocol=['TCP/IP', 'Modbus'],
                minIORate=6.0,
                maxIORate=18.0,
                delay=2.0,
                minRespTime=12.0,
                maxRespTime=22.0,
                aveRespTime=17.0,
                energy=20.0,
                stability='good',
                security='bad',
            )
        )
        self.taskType.append(
            TaskType(
                operandReq=[[10, 0, 10, 10, 0, 0, 0, 10, 10, 0, 10, 0]],
                data=[30],
                algorithm='语音识别',
                computePower=30.0,
                memReq=4.0,
                cacheReq=0.0,
                diskReq=10.0,
                networkProtocol=['TCP/IP', 'Bluetooth'],
                minIORate=5.0,
                maxIORate=18.0,
                delay=5.0,
                minRespTime=6.0,
                maxRespTime=10.0,
                aveRespTime=8.0,
                energy=14.0,
                stability='good',
                security='bad',
            )
        )
        self.taskType.append(
            TaskType(
                operandReq=[[0, 10, 10, 10, 0, 10, 0, 10, 10, 0, 10, 0]],
                data=[25],
                algorithm='强化学习',
                computePower=5.0,
                memReq=5.0,
                cacheReq=0.0,
                diskReq=8.0,
                networkProtocol=['TCP/IP', 'Bluetooth', 'Modbus'],
                minIORate=10.0,
                maxIORate=20.0,
                delay=3.0,
                minRespTime=11.0,
                maxRespTime=23.0,
                aveRespTime=17.0,
                energy=15.0,
                stability='great',
                security='good',
            )
        )
        self.subtasks = []
        self.task = None
        self.taskid = tid_maker()
        self.task_type_list = [[0, 1, 3], [2, 0, 3], [1, 2], [2, 3], [0, 1], [0], [2], [3]]
        pass

    def generate(
            self,
            task_type: int = 0
    ):
        self.subtasks = []
        task_types = self.task_type_list[task_type]
        for subtask_type in task_types:
            self.taskid = tid_maker()
            tmp = self.taskType[subtask_type].generate(self.taskid)
            self.subtasks.append(tmp)
        # self.task = tmp

    def getTaskID(
            self,
    ):
        return self.task.getTaskID()

    def getOperandReq(
            self,
    ):
        return self.task.getOperandReq()

    def getData(
            self,
    ):
        return self.task.getData()

    def getAlgorithm(
            self,
    ):
        return self.task.getAlgorithm()

    def getComputePower(
            self,
    ):
        return self.task.getComputePower()

    def getMemReq(
            self,
    ):
        return self.task.getMemReq()

    def getCacheReq(
            self,
    ):
        return self.task.getCacheReq()

    def getDiskReq(
            self,
    ):
        return self.task.getDiskReq()

    def getNetworkProtocol(
            self,
    ):
        return self.task.getNetworkProtocol()

    def getIORate(
            self,
    ):
        min, max = self.task.getIORate()
        return min, max

    def getDelay(
            self,
    ):
        return self.task.getDelay()

    def getRespTime(
            self,
    ):
        min, max, ave = self.task.getRespTime()
        return min, max, ave

    def getEnergy(
            self,
    ):
        return self.task.getEnergy()

    def getStability(
            self,
    ):
        return self.task.getStability()

    def getSecurity(
            self,
    ):
        return self.task.getSecurity()


"""TODO+ Task operation
MORE TASK INFO ___  IN STANDARD FILE 
"""


class Task():
    def __init__(
            self,
            # taskID: int,  # 任务id
            # operandReq: list,  # 操作数需求
            # data: float,  # 数据要求
            # algorithm: string,  # 算法
            # computePower: float,  # 算力值
            # storageType: list,  # 存储类型
            # memReq: float,  # 内存字节数
            # cacheReq: float,  # 缓存字节数
            # diskReq: float,  # 外存字节数
            # networkProtocol: list,  # 支持的网络协议
            # minIORate: int,  # 最小吞吐率
            # maxIORate: int,  # 最大吞吐率
            # delay: float,  # 延迟
            # minRespTime: float,  # 最小响应时间
            # maxRespTime: float,  # 最大响应时间
            # aveRespTime: float,  # 平均响应时间
            # energy: float,  # 能耗
            # stability: string,  # 稳定性
            # security: string,  # 安全性

            taskID: int,  # 任务id
            operandReq: list = [],  # 操作数需求
            data: list = [],  # 数据要求
            algorithm: string = '',  # 算法
            computePower: float = 0.0,  # 算力值
            # storageType: list=[],  # 存储类型
            memReq: float = 0.0,  # 内存字节数
            cacheReq: float = 0.0,  # 缓存字节数
            diskReq: float = 0.0,  # 外存字节数
            networkProtocol: list = [],  # 支持的网络协议
            minIORate: float = 0.0,  # 最小吞吐率
            maxIORate: float = 0.0,  # 最大吞吐率
            delay: float = 0.0,  # 延迟
            minRespTime: float = 0.0,  # 最小响应时间
            maxRespTime: float = 0.0,  # 最大响应时间
            aveRespTime: float = 0.0,  # 平均响应时间
            energy: float = 0.0,  # 能耗
            stability: string = '',  # 稳定性
            security: string = '',  # 安全性
    ):
        self.taskID = taskID
        self.operandReq = operandReq
        self.data = data
        self.algorithm = algorithm
        self.computePower = computePower
        # self.storageType = storageType
        self.memReq = memReq
        self.cacheReq = cacheReq
        self.diskReq = diskReq
        self.networkProtocol = networkProtocol
        self.minIORate = minIORate
        self.maxIORate = maxIORate
        self.delay = delay
        self.minRespTime = minRespTime
        self.maxRespTime = maxRespTime
        self.aveRespTime = aveRespTime
        self.energy = energy
        self.stability = stability
        self.security = security
        pass

    def getTaskID(
            self,
    ):
        return self.taskID

    def getOperandReq(
            self,
    ):
        return self.operandReq

    def getData(
            self,
    ):
        return self.data

    def getAlgorithm(
            self,
    ):
        return self.algorithm

    def getComputePower(
            self,
    ):
        return self.computePower

    def getMemReq(
            self,
    ):
        return self.memReq

    def getCacheReq(
            self,
    ):
        return self.cacheReq

    def getDiskReq(
            self,
    ):
        return self.diskReq

    def getNetworkProtocol(
            self,
    ):
        return self.networkProtocol

    def getIORate(
            self,
    ):
        return self.minIORate, self.maxIORate

    def getDelay(
            self,
    ):
        return self.delay

    def getRespTime(
            self,
    ):
        return self.minRespTime, self.maxRespTime, self.aveRespTime

    def getEnergy(
            self,
    ):
        return self.energy

    def getStability(
            self,
    ):
        return self.stability

    def getSecurity(
            self,
    ):
        return self.security


# taskID=taskid,
# operandReq
# data
# algorithm
# computePower
# storageType
# memReq
# cacheReq
# diskReq
# networkProtocol
# minIORate
# maxIORate
# delay
# minRespTime
# maxRespTime
# aveRespTime
# energy
# stability
# security
class TaskType():
    def __init__(
            self,
            operandReq: list,
            data: list,
            algorithm: string,
            computePower: float,
            # storageType: list,
            memReq: float,
            cacheReq: float,
            diskReq: float,
            networkProtocol: list,
            minIORate: float,
            maxIORate: float,
            delay: float,
            minRespTime: float,
            maxRespTime: float,
            aveRespTime: float,
            energy: float,
            stability: string,
            security: string,

    ):
        self.operandReq = operandReq
        self.data = data
        self.algorithm = algorithm
        self.computePower = computePower
        # self.storageType = storageType
        self.memReq = memReq
        self.cacheReq = cacheReq
        self.diskReq = diskReq
        self.networkProtocol = networkProtocol
        self.minIORate = minIORate
        self.maxIORate = maxIORate
        self.delay = delay
        self.minRespTime = minRespTime
        self.maxRespTime = maxRespTime
        self.aveRespTime = aveRespTime
        self.energy = energy
        self.stability = stability
        self.security = security

    def generate(
            self,
            taskid
    ):
        """TODO- Genrate policy : """
        operandReq = self.operandReq
        data = self.data
        algorithm = self.algorithm
        computePower = np.random.normal(self.computePower) if self.computePower > 0 else 0
        # storageType = self.storageType
        memReq = np.abs(np.random.normal(self.memReq)) if self.memReq > 0 else 0
        cacheReq = np.abs(np.random.normal(self.cacheReq)) if self.cacheReq > 0 else 0
        diskReq = np.abs(np.random.normal(self.diskReq)) if self.diskReq > 0 else 0
        networkProtocol = self.networkProtocol
        minIORate = np.abs(np.random.normal(self.minIORate)) if self.minIORate > 0 else 0
        maxIORate = np.abs(np.random.normal(self.maxIORate)) if self.maxIORate > 0 else 0
        delay = np.abs(np.random.normal(self.delay)) if self.delay > 0 else 0
        minRespTime = np.abs(np.random.normal(self.minRespTime)) if self.minRespTime > 0 else 0
        maxRespTime = np.abs(np.random.normal(self.maxRespTime)) if self.maxRespTime > 0 else 0
        aveRespTime = np.abs(np.random.normal(self.aveRespTime)) if self.aveRespTime > 0 else 0
        energy = np.abs(np.random.normal(self.energy)) if self.energy > 0 else 0
        stability = self.stability
        security = self.security
        return Task(
            taskID=taskid,
            operandReq=operandReq,
            data=data,
            algorithm=algorithm,
            computePower=computePower,
            # storageType=storageType,
            memReq=memReq,
            cacheReq=cacheReq,
            diskReq=diskReq,
            networkProtocol=networkProtocol,
            minIORate=minIORate,
            maxIORate=maxIORate,
            delay=delay,
            minRespTime=minRespTime,
            maxRespTime=maxRespTime,
            aveRespTime=aveRespTime,
            energy=energy,
            stability=stability,
            security=security
        )

def tid_maker():
    return '{0:%d%H%M%S%f}'.format(datetime.datetime.now())