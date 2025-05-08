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
class CPU_Accelerated_Instruction(Enum):
    type1='MMX'
    type2='SSE'
    type3='AVX'
    type4='NEOM'
    type5='VMX'
    type6='AltiVec'

class CPU_Architecture(Enum):
    type1='X86'
    type2='ARM'
    type3='PowerPC'




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

class GPU_Supported_Interface_Names_Version:
    def __init__(self,name:str,version:str):
        self.name=name
        self.version=version

    OPenCL = '2.0'

class CPU_Specifications:
    def __init__(self,Accelerated_Instruction:str,Base_Frequency_Of_Core:float,
                 Number_Of_Cores:int,Architecture:str,
                 L1_Cache:int,L2_Cache:int,L3_Cache:int,
                 Bus:float,Number_Of_Threads:int):
        self.Accelerated_Instruction=Accelerated_Instruction
        self.Base_Frequency_Of_Core=Base_Frequency_Of_Core
        self.Number_Of_Cores=Number_Of_Cores
        self.Architecture=Architecture
        self.L1_Cache=L1_Cache
        self.L2_Cache=L2_Cache
        self.L3_Cache=L3_Cache
        self.Bus=Bus
        self.Number_Of_Threads=Number_Of_Threads

class Memory_Attributes:
    def __init__(self,ID:str,Correction:str):
        self.ID=ID
        self.Correction=Correction
class Memory_Specifications:
    def __init__(self,size:str,memory_bandwidth:str,latency:float,type:str,channel_number):
        self.size=size
        self.memory_bandwidth=memory_bandwidth
        self.latency=latency
        self.type=type
        self.channel_number=channel_number

class Communicate_Specifications:
    def __init__(self,up_bandwidth:str,down_bandwidth:str,latency:float,FIB_speed:str,IPsec_speed,Virtual_bandwidth:str,Firewall_Loss,network_protocol):
        self.up_bandwidth=up_bandwidth
        self.down_bandwidth=down_bandwidth
        self.latency=latency
        self.FIB_speed=FIB_speed
        self.IPsec_speed=IPsec_speed
        self.Virtual_bandwidth=Virtual_bandwidth
        self.Firewall_Loss=Firewall_Loss
        self.network_protocol=network_protocol

class Storage_Specifications:
    def __init__(self,size:str,storage_bandwidth:str,IOPS:float,Backup_num:str,reliability):
        self.size=size
        self.storage_bandwidth=storage_bandwidth
        self.IOPS=IOPS
        self.Backup_num=Backup_num
        self.reliability=reliability

class Terminal:
    def __init__(self,type,duration):
        self.type=type
        self.duration=duration

class No_Terminal:
    def __init__(self,energy_efficiency,x1,x2,x3,y1,y2,y3):
        self.energy_efficiency=energy_efficiency
        self.x1=x1
        self.x2=x2
        self.x3=x3
        self.y1=y1
        self.y2=y2
        self.y3=y3

class UsageType(Enum):
    ProcessorUsage = 'ProcessorUsage'
    MemoryUsage = 'MemoryUsage'
    ExMemBandUsage = 'MemBandUsage'
    NetBandUpUsage = 'NetBandUpUsage'
    NetBandDownUsage = 'NetBandDownUsage'
    IOPSUsage='IOPSUsage'
    StorageUsage='StorageUsage'
class Usage:
    def __init__(self, type: UsageType, usage: float):
        self.type = type
        self.usage = usage

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
        # 资源占用新加
        usage=[
                Usage('ProcessorUsage', 50 * rand),
                Usage('MemoryUsage', 50 * rand),
                Usage('MemBandUsage', 40 * rand),
                Usage('NetBandUpUsage', 55 * rand),
                Usage('NetBandDownUsage', 20 * rand),
                Usage('IOPSUsage', 20 * rand),
                Usage('StorageUsage', 20 * rand),
            ],
        software_env=random.choice(['Linux','Windows']),
        ):
        self.processor = processor
        self.memory = memory
        self.network = network
        self.usage = usage
        self.software_env=software_env
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
    def getUsage(self, type) -> str:
        for u in self.usage:
            if(u.type==type):
                return u.usage
    def getSoftwareenv(self):
        return self.software_env

class Node:
    def __init__(self, uri ,id, priority:int, unit_prize,
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
                 CPUThread=[16,32,64],
                 gpu_supported_interface_names_version=[
                     GPU_Supported_Interface_Names_Version('CUDA','10.0'),
                     GPU_Supported_Interface_Names_Version('OPenCL','2.0')
                 ],
                 Operand_Types=['FP','TP','INT','BF'],
                 Memory_Attributes=[
                     Memory_Attributes('1','奇偶校验'),
                     Memory_Attributes('2','循环冗余校验'),
                     Memory_Attributes('3','纠错码')
                 ],
                 Memory_Specifications=[
                     Memory_Specifications(20*rand,25*rand,rand,'DDR3',4),
                     Memory_Specifications(23*rand,15*rand,rand,'DDR5',8),
                 ],
                 Communicate_Specifications=[
                     Communicate_Specifications(5 * rand, 3 * rand, rand, 1000 * rand, 10 * rand, 5 * rand, rand * 2,'TCP/IP'),
                     Communicate_Specifications(5 * rand, 3 * rand, rand, 1000 * rand, 10 * rand, 5 * rand, rand * 2,'UDP'),
                     Communicate_Specifications(5 * rand, 3 * rand, rand, 1000 * rand, 10 * rand, 5 * rand, rand * 2,'Http')
                 ],
                 Storage_Specifications=[
                     Storage_Specifications(20 * rand, 25 * rand, rand,5,20*rand),
                     Storage_Specifications(20 * rand, 25 * rand, rand, 4, 30 * rand),
                     Storage_Specifications(20 * rand, 25 * rand, rand, 3, 40 * rand)
                 ],
                 Terminal=[
                     Terminal('Mobil',200*rand),
                     Terminal('Pad', 200 * rand),
                     Terminal('PC', 200 * rand),
                 ],
                 No_Terminal=[
                     No_Terminal(200*rand,rand*10,rand*3,rand*5,rand*7,rand*4,rand*2),
                     No_Terminal(200*rand,rand*10,rand*3,rand*5,rand*7,rand*4,rand*2),
                     No_Terminal(200*rand,rand*10,rand*3,rand*5,rand*7,rand*4,rand*2),
                 ],



                safety = 'soso'):
        self.uri = uri
        self.id = id
        self.priority = priority
        self.unit_prize=unit_prize
        self.config = config
        self.computerpower = computerpower
        self.safety = safety
        self.CPUThread = CPUThread
        self.Operand_Types=Operand_Types
        self.Memory_Attributes=Memory_Attributes
        self.Memory_Specifications=Memory_Specifications
        self.Communicate_Specifications=Communicate_Specifications
        self.Storage_Specifications=Storage_Specifications
        self.Terminal=Terminal
        self.No_Terminal=No_Terminal
        self.gpu_supported_interface_names_version=gpu_supported_interface_names_version

   
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

    def getCPU_Specifications(
        self, type
    )->str:
        if type =='Accelerated_Instruction':
            return random.choice(list(CPU_Accelerated_Instruction)).value
        elif type =='Base_Frequency_Of_Core':
            return 5.0*rand
        elif type =='Number_Of_Cores':
            return random.randint(2,8)
        elif type =='Architecture':
            return random.choice(list(CPU_Architecture)).value
        elif type =='L1_Cache':
            return 3*rand
        elif type =='L2_Cache':
            return 2*rand
        elif type =='L3_Cache':
            return 3*rand
        elif type =='Bus':
            return 5*rand
        elif type =='Number_Of_Threads':
            return random.choice(self.CPUThread)
        elif type == 'ID':
            return random.randint(1,5)

    def getGPU_Specifications(
        self, type
    )->str:
        if type =='Graphics_Memory_size':
            return 10*rand
        elif type =='Graphics_Memory_Bandwidth':
            return 3.0*rand
        elif type =='clock_frequency':
            return random.randint(10,18)*rand
        elif type =='Supported_Interface_Name':
            return random.choice(self.gpu_supported_interface_names_version).name
        elif type =='Supported_Interface_Version':
            return random.choice(self.gpu_supported_interface_names_version).version
        elif type =='Number_of_Stream_Processors':
            return random.randint(2000,4000)
        elif type =='ID':
            return random.randint(1,5)

    def getSpeed_Attributes(
            self,type
    )->str:
        if type =='FLOPS':
            return 3.5*rand
        if type =='Operand_Types':
            return random.choice(self.Operand_Types)
        if type =='number_digit':
            return random.choice([16,32,64])

    def getMemory_Attributes(
            self,type
    )->str:
        num = random.randint(0, 2)
        if type =='ID':
            return self.Memory_Attributes[num].ID
        if type =='Correction':
            return self.Memory_Attributes[num].Correction

    def getMemory_Specifications(
            self,type
    )->str:
        num=random.randint(0,1)
        if type =='容量':
            return self.Memory_Specifications[num].size
        if type =='内存带宽':
            return self.Memory_Specifications[num].memory_bandwidth
        if type =='延迟':
            return self.Memory_Specifications[num].latency
        if type =='类型':
            return self.Memory_Specifications[num].type
        if type =='通道数':
            return self.Memory_Specifications[num].channel_number

    def getCommunicate_Attributes(
            self,type
    )->str:
        num = random.randint(0, 1)
        if type == 'ID':
            return num

    def getCommunicate_Specifications(
            self,type
    )->str:
        num = random.randint(0, 2)
        if type == '带宽上行':
            return self.Communicate_Specifications[num].up_bandwidth
        if type == '带宽下行':
            return self.Communicate_Specifications[num].down_bandwidth
        if type == '时延':
            return self.Communicate_Specifications[num].latency
        if type == 'FIB转发速率':
            return self.Communicate_Specifications[num].FIB_speed
        if type == 'IPSec速率':
            return self.Communicate_Specifications[num].IPsec_speed
        if type == '虚拟网络带宽':
            return self.Communicate_Specifications[num].Virtual_bandwidth
        if type == '防火墙损耗':
            return self.Communicate_Specifications[num].Firewall_Loss
        if type == '支持的网络协议':
            return self.Communicate_Specifications[num].network_protocol

    def getStorage_Attributes(
            self, type
    ) -> str:
        num = random.randint(0, 2)
        if type == 'ID':
            return num

    def getStorage_Specifications(
            self,type
    )->str:
        num = random.randint(0, 2)
        if type == '容量':
            return self.Storage_Specifications[num].size
        if type == '存储带宽':
            return self.Storage_Specifications[num].storage_bandwidth
        if type == 'IOPS':
            return self.Storage_Specifications[num].IOPS
        if type == '备份数量':
            return self.Storage_Specifications[num].Backup_num
        if type == '可靠性':
            return self.Storage_Specifications[num].reliability

    def getTerminal_Attributes(
            self, type
    ) -> str:
        num = random.randint(0, 1)
        if type == 'type':
            return num
        if type == '类型':
            return self.Terminal[random.randint(0,2)].type
        if type == '续航时长':
            return self.Terminal[random.randint(0, 2)].duration
        if type == '能效':
            return self.No_Terminal[random.randint(0,2)].energy_efficiency
        if type == '经度-度':
            return self.No_Terminal[random.randint(0,2)].x1
        if type == '经度-分':
            return self.No_Terminal[random.randint(0,2)].x2
        if type == '经度-秒':
            return self.No_Terminal[random.randint(0,2)].x3
        if type == '纬度-度':
            return self.No_Terminal[random.randint(0,2)].y1
        if type == '纬度-分':
            return self.No_Terminal[random.randint(0,2)].y2
        if type == '纬度-秒':
            return self.No_Terminal[random.randint(0,2)].y3















    
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
        Node = Node('/8080/Servers','c1', random.randint(1,3),random.uniform(100,200), ResourceConfig(), ),
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
