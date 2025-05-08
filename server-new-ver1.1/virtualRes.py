#!/usr/bin/python3
#-*- coding:utf-8 -*-
############################
# File Name: virtualRes.py
# Author: 
# mail: 
# Create Time: 2023/5/4 11:43:40
############################

"""TODO 
VirtualRes - 1. 更多资源
           - 2. update逻辑 随着任务的发布与结束， 资源的更新逻辑
           - 3. getInfo获取 提供给外部检测程序的get方法
"""

from enum import Enum
import random

rand = round(random.uniform(0, 1), 2) + 1

class ProcessorType(Enum):
    CPU = 0
    GPU = 1
    TPU = 2
    NPU = 3
    FPGA = 4
    ASIC = 5
    # CPU = "CPU"
    # GPU = "GPU"
    # TPU = "TPU"
    # NPU = "NPU"
    # FPGA = "FPGA"
    # ASIC = "ASIC"
class MemoryType(Enum):
    INTERNAL = 0
    EXTERNAL = 1
    CACHE = 2
    # INTERNAL = "Internal_storage"
    # EXTERNAL = "External_storage"
    # CACHE = "Cache"
class NetProtocolType(Enum):
    BLUETOOTH = 0
    TCP_IP = 1
    MODBUS = 2
    # BLUETOOTH = 'Bluetooth'
    # TCP_IP = 'TCP_IP'
    # MODBUS = 'Modbus'
class AlgorithmType(Enum):
    IMAGE_C = 0
    INSTANCE = 1
    IMAGE_S = 2
    OD = 3
    NLP = 4
    SR = 5
    RECOMMEND = 6
    RL = 7
    # IMAGE_C = 'Image_classification'
    # INSTANCE = 'Instance_segmentation'
    # IMAGE_S = 'Image_segmentation'
    # OD = 'Object_detection'
    # NLP = 'Natural_language_processing'
    # SR = 'Speech_recognition'
    # RECOMMEND = 'Intelligent_recommendation'
    # RL = 'Reinforcement_learning'
class DeviceType(Enum):
    MOBIL = 'Mobil'
    PAD = 'Pad'
    RSU = 'RSU'
    SENSOR = 'Sensor'
    CAMERA = 'Camera'
    VOBC = 'VOBC'
    # MOBIL = 'Mobil'
    # PAD = 'Pad'
    # RSU = 'RSU'
    # SENSOR = 'Sensor'
    # CAMERA = 'Camera'
    # VOBC = 'VOBC'

class Processor:
    def __init__(self, type: ProcessorType, flops: float):
        self.type = type
        self.flops = flops

class Memory:
    def __init__(self, type: MemoryType, byte: int):
        self.type = type
        self.byte = byte
        self.byte_M = byte
        self.byte_A = 0

class Network:
    def __init__(self, type: NetProtocolType, throughput_up: int, 
                 throughput_down: int, latency: float):
        self.type = type
        self.throughput_up = throughput_up
        self.throughput_down = throughput_down
        self.latency = latency

class ComputerPower:
    def __init__(self, type: AlgorithmType, value: float):
        self.type = type
        self.value = value
        self.value_M = value
        self.value_A = 0

class ResourceConfig:
    def __init__(
        self, 
        processor = [
            Processor('CPU', 12.0 * rand),
            Processor('GPU', 30.0 * rand),
            Processor('TPU', 60.0 * rand),
        ],

        memory = [
            Memory('internal_storage', 512 * rand),
            Memory('external_storage', 500 * rand),
            Memory('cache', 64 * rand),
        ],
        network = [
            Network('Bluetooth', 1 * rand, 3 * rand, 150 * rand),
            Network('TCP_IP', 50 * rand, 500 * rand, 15 * rand),
            Network('Modbus', 25 * rand, 150 * rand, 10 * rand),
        ],
        ):
        self.processor = processor
        self.memory = memory
        self.network = network

    def getProcessorFLOPS(
        self, type
    )->str:
        idx = -1
        if type == 'CPU':
            idx = ProcessorType.CPU.value
        elif type == 'GPU':
            idx = ProcessorType.GPU.value
        elif type == 'TPU':
            idx = ProcessorType.TPU.value
        elif type == 'NPU':
            idx = ProcessorType.NPU.value
        elif type == 'FPGA':
            idx = ProcessorType.FPGA.value
        elif type == 'ASIC':
            idx = ProcessorType.ASIC.value
        return self.processor[idx].flops
    
    def getMemoryByte(
        self, type
    )->str:
        idx = -1
        if type == 'Internal_storage':
            idx = MemoryType.INTERNAL.value
        elif type == 'External_storage':
            idx = MemoryType.EXTERNAL.value
        elif type == 'Cache':
            idx = MemoryType.CACHE.value
        return self.memory[idx].byte  
      
    def getMemoryByte_M(
        self, type
    )->str:
        idx = -1
        if type == 'Internal_storage':
            idx = MemoryType.INTERNAL.value
        elif type == 'External_storage':
            idx = MemoryType.EXTERNAL.value
        elif type == 'Cache':
            idx = MemoryType.CACHE.value
        return self.memory[idx].byte_M   
     
    def getMemoryByte_A(
        self, type
    )->str:
        idx = -1
        if type == 'Internal_storage':
            idx = MemoryType.INTERNAL.value
        elif type == 'External_storage':
            idx = MemoryType.EXTERNAL.value
        elif type == 'Cache':
            idx = MemoryType.CACHE.value
        return self.memory[idx].byte_A    
    
    def getThroughput_up(
        self, type
    )->str:
        idx = -1
        if type =='Bluetooth':
            idx = NetProtocolType.BLUETOOTH.value
        elif type =='TCP_IP':
            idx = NetProtocolType.TCP_IP.value
        elif type =='Modbus':
            idx = NetProtocolType.MODBUS.value
        return self.network[idx].throughput_up   
    
    def getThroughput_down(
        self, type
    )->str:
        idx = -1
        if type =='Bluetooth':
            idx = NetProtocolType.BLUETOOTH.value
        elif type =='TCP_IP':
            idx = NetProtocolType.TCP_IP.value
        elif type =='Modbus':
            idx = NetProtocolType.MODBUS.value
        return self.network[idx].throughput_down   
    
    def getLatency(
        self, type
    )->str:
        idx = -1
        if type =='Bluetooth':
            idx = NetProtocolType.BLUETOOTH.value
        elif type =='TCP_IP':
            idx = NetProtocolType.TCP_IP.value
        elif type =='Modbus':
            idx = NetProtocolType.MODBUS.value
        return self.network[idx].latency  

class Node:
    def __init__(self, url ,id, priority:int, 
                 config: ResourceConfig, 
                 computerpower = [
                    ComputerPower('Image_classification', 1000 * rand),
                    ComputerPower('Instance_segmentation', 1000 * rand),
                    ComputerPower('Image_segmentation', 1000 * rand),
                    ComputerPower('Object_detection', 1000 * rand),
                    ComputerPower('Natural_language_processing', 1000 * rand),
                    ComputerPower('Speech_recognition', 1000 * rand),
                    ComputerPower('Intelligent_recommendation', 1000 * rand),
                    ComputerPower('Reinforcement_learning', 1000 * rand),
                ], 
                safety = 'soso'):
        self.url = url
        self.id = id
        self.priority = priority
        self.config = config
        self.computerpower = computerpower
        self.safety = safety
   
    def getComputerPower(
        self, type
    )->str:
        idx = -1
        if type =='Image_classification':
            idx = AlgorithmType.IMAGE_C.value
        elif type =='Instance_segmentation':
            idx = AlgorithmType.INSTANCE.value
        elif type =='Image_segmentation':
            idx = AlgorithmType.IMAGE_S.value
        elif type =='Object_detection':
            idx = AlgorithmType.OD.value
        elif type =='Natural_language_processing':
            idx = AlgorithmType.NLP.value
        elif type =='Speech_recognition':
            idx = AlgorithmType.SR.value
        elif type =='Intelligent_recommendation':
            idx = AlgorithmType.RECOMMEND.value
        elif type =='Reinforcement_learning':
            idx = AlgorithmType.RL.value
        return self.computerpower[idx].value   

    def getComputerPower_M(
        self, type
    )->str:
        idx = -1
        if type =='Image_classification':
            idx = AlgorithmType.IMAGE_C.value
        elif type =='Instance_segmentation':
            idx = AlgorithmType.INSTANCE.value
        elif type =='Image_segmentation':
            idx = AlgorithmType.IMAGE_S.value
        elif type =='Object_detection':
            idx = AlgorithmType.OD.value
        elif type =='Natural_language_processing':
            idx = AlgorithmType.NLP.value
        elif type =='Speech_recognition':
            idx = AlgorithmType.SR.value
        elif type =='Intelligent_recommendation':
            idx = AlgorithmType.RECOMMEND.value
        elif type =='Reinforcement_learning':
            idx = AlgorithmType.RL.value
        return self.computerpower[idx].value_M   
    
    def getComputerPower_A(
        self, type
    )->str:
        idx = -1
        if type =='Image_classification':
            idx = AlgorithmType.IMAGE_C.value
        elif type =='Instance_segmentation':
            idx = AlgorithmType.INSTANCE.value
        elif type =='Image_segmentation':
            idx = AlgorithmType.IMAGE_S.value
        elif type =='Object_detection':
            idx = AlgorithmType.OD.value
        elif type =='Natural_language_processing':
            idx = AlgorithmType.NLP.value
        elif type =='Speech_recognition':
            idx = AlgorithmType.SR.value
        elif type =='Intelligent_recommendation':
            idx = AlgorithmType.RECOMMEND.value
        elif type =='Reinforcement_learning':
            idx = AlgorithmType.RL.value
        return self.computerpower[idx].value_A   
    
class TerminalDevice:
    def __init__(self, url ,id, priority:int, 
                 type:DeviceType, config: ResourceConfig, 
                 computerpower = [
                    ComputerPower('Image_classification', 1000 * rand),
                    ComputerPower('Instance_segmentation', 1000 * rand),
                    ComputerPower('Image_segmentation', 1000 * rand),
                    ComputerPower('Object_detection', 1000 * rand),
                    ComputerPower('Natural_language_processing', 1000 * rand),
                    ComputerPower('Speech_recognition', 1000 * rand),
                    ComputerPower('Intelligent_recommendation', 1000 * rand),
                    ComputerPower('Reinforcement_learning', 1000 * rand),
                ], 
                stability = 'soso', energy= '', safety= 'soso'):
        self.url = url
        self.id = id
        self.priority = priority
        self.type = type
        self.config = config
        self.computerpower = computerpower
        self.stability = stability
        self.energy = energy
        self.safety = safety
    
    def getComputerPower(
        self, type
    )->str:
        if type =='Image_classification':
            idx = AlgorithmType.IMAGE_C.value
        elif type =='Instance_segmentation':
            idx = AlgorithmType.INSTANCE.value
        elif type =='Image_segmentation':
            idx = AlgorithmType.IMAGE_S.value
        elif type =='Object_detection':
            idx = AlgorithmType.OD.value
        elif type =='Natural_language_processing':
            idx = AlgorithmType.NLP.value
        elif type =='Speech_recognition':
            idx = AlgorithmType.SR.value
        elif type =='Intelligent_recommendation':
            idx = AlgorithmType.RECOMMEND.value
        elif type =='Reinforcement_learning':
            idx = AlgorithmType.RL.value
        return self.computerpower[idx].value

class VirtualRes():
    def __init__(
        self,
        Node = Node('1@node', 'c1', 1, ResourceConfig(), ), 
        # Device = TerminalDevice('1@device', 'd1', 2, 'Mobil', ResourceConfig(), ComputerPower(), 'soso', 'energy', 'bad'), 
    ):
        self.Node = Node
        # self.Device = Device
        pass

    def update(
        self,
    ):
        pass


if __name__=='__main__':
    """TEST VirtualRes"""
    tmpr = VirtualRes()
