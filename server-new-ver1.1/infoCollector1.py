#!/usr/bin/python3
#-*- coding:utf-8 -*-
############################
# File Name: infoCollector.py
# Author: taowang
# mail: wangtao573@bistu.edu.cn or 907993189@qq.com
# Create Time: 2023/3/23 21:51:37
############################
import subprocess
import platform
import psutil
import cpuinfo
import pynvml

def update(topics, values):
    pass

""" CPU INFO """
def getCPUInfo():
    CPUINFO = cpuinfo.get_cpu_info()['brand_raw']
    return CPUINFO

def getCPUFLOPS():
    """ TODO GET CPUINFO AND traverse the list """
    pass 

def getCPUCount():
    cpu_count = psutil.cpu_count()  # 逻辑核心数
    """ TODO  how to get cpu count """
    return cpu_count

def getCPUCore():
    cpu_core = psutil.cpu_count(logical=False)  # 物理核心数
    return cpu_core

def getCPUPercent():
    cpu_percent = psutil.cpu_percent(percpu=True)  # 各个cpu
    for i in range(len(cpu_percent)):
        print(f"第 {i} 张卡的使用率为：{cpu_percent[i]}")
        # yield i, cpu_percent[i]

def getCPUFrequence():
    cpu_freq = psutil.cpu_freq()  # CPU频率

    print(f"当前CPU频率: {cpu_freq.current:.2f} MHz")
    print(f"最小CPU频率: {cpu_freq.min:.2f} MHz")
    print(f"最大CPU频率: {cpu_freq.max:.2f} MHz")
    return round(cpu_freq.current, 2), round(cpu_freq.min, 2), round(cpu_freq.max, 2)

""" CPU INFO END """

""" GPU INFO """
def getGPUCount():
    pynvml.nvmlInit()  # 初始化
    gpu_device_count = pynvml.nvmlDeviceGetCount()  # 获取Nvidia GPU块数
    pynvml.nvmlShutdown()  # 关闭管理工具
    return gpu_device_count

def getGPUInfo():
    pynvml.nvmlInit()  # 初始化
    gpu_device_count = pynvml.nvmlDeviceGetCount()  # 获取Nvidia GPU块数
    UNIT = 1024*1024
    for gpu_index in range(gpu_device_count):
        handle = pynvml.nvmlDeviceGetHandleByIndex(gpu_index)  # 获取GPU i的handle，后续通过handle来处理
        memery_info = pynvml.nvmlDeviceGetMemoryInfo(handle)  # 通过handle获取GPU 的信息
        # gpu_name = str(pynvml.nvmlDeviceGetName(handle), encoding='utf-8')
        gpu_name = str(pynvml.nvmlDeviceGetName(handle))
        gpu_temperature = pynvml.nvmlDeviceGetTemperature(handle, 0)
        # gpu_fan_speed = pynvml.nvmlDeviceGetFanSpeed(handle)
        gpu_power_state = pynvml.nvmlDeviceGetPowerState(handle)
        gpu_util_rate = pynvml.nvmlDeviceGetUtilizationRates(handle).gpu
        gpu_memory_rate = pynvml.nvmlDeviceGetUtilizationRates(handle).memory

        print(f"第 %d 张卡：{gpu_index}")
        print(f"显卡名：{gpu_name}")
        print(f"内存总容量：{memery_info.total / UNIT} MB")
        print(f"使用容量：{memery_info.total / UNIT}MB")
        print(f"剩余容量：{memery_info.total / UNIT}MB")
        print(f"显存空闲率：{memery_info.free / memery_info.total}")
        print(f"温度：{gpu_temperature}摄氏度")
        # print(f"风扇速率：{gpu_fan_speed}")
        print(f"供电水平：{gpu_power_state}")
        print(f"gpu计算核心满速使用率：{gpu_util_rate}")
        print(f"gpu内存读写满速使用率：{gpu_memory_rate}")
        print(f"内存占用率：{memery_info.used / memery_info.total}")

        # yield gpu_index, gpu_name, gpu_util_rate, gpu_memory_rate, memery_info.total / UNIT
    pynvml.nvmlShutdown()  # 关闭管理工具

def getGPUUtil():
    pynvml.nvmlInit()  # 初始化
    gpu_device_count = pynvml.nvmlDeviceGetCount()  # 获取Nvidia GPU块数
    UNIT = 1024*1024
    for gpu_index in range(gpu_device_count):
        handle = pynvml.nvmlDeviceGetHandleByIndex(gpu_index)  # 获取GPU i的handle，后续通过handle来处理
        memery_info = pynvml.nvmlDeviceGetMemoryInfo(handle)  # 通过handle获取GPU 的信息

        print(f"第 {gpu_index} 张卡的使用率为：{pynvml.nvmlDeviceGetUtilizationRates(handle).gpu}")

        # yield gpu_index, pynvml.nvmlDeviceGetUtilizationRates(handle).gpu  # memery_info.used / memery_info.total
    pynvml.nvmlShutdown()  # 关闭管理工具

def getGPUFLOPS():
    """ TODO GET GPUINFO AND traverse the list """
    pass

""" GPU INFO END """


""" MEM INFO """
def getMEMInfo():
    # total_memory = 0
    # free_memory = 0
    # if platform.system().lower() == 'linux':
    #     # 获取内存容量和可用内存
    #     mem_result = subprocess.run(['free', '-m'], capture_output=True, text=True)
    #     mem_output = mem_result.stdout.strip().split('\n')[1].split()
    #     total_memory = float(mem_output[1])
    #     free_memory = float(mem_output[3])
    #     # print('内存容量: %d MB' % total_memory)
    #     # print('可用内存: %d MB' % free_memory)
    # return round(total_memory, 2), round(free_memory, 2)
    memory_info = psutil.virtual_memory()
    total_memory = memory_info.total  # 总内存
    available_memory = memory_info.available  # 可用内存
    used_memory = memory_info.used  # 已用内存
    memory_percent = memory_info.percent  # 内存使用率

    print(f"总内存: {total_memory / (1024 ** 3):.2f} GB")
    print(f"可用内存: {available_memory / (1024 ** 3):.2f} GB")
    print(f"已用内存: {used_memory / (1024 ** 3):.2f} GB")
    print(f"内存使用率: {memory_percent}%")
    return total_memory, available_memory, used_memory

""" MEM END """

""" DISK INFO """
def getDiskInfo():
    # total_size = 0
    # total_iops = 0
    # io_rate = 0
    # if platform.system().lower() == 'linux':
    #     # 获取硬盘容量
    #     df_result = subprocess.run(['df', '-h'], capture_output=True, text=True)
    #     df_output = df_result.stdout.strip().split('\n')[1:]
    #     total_size = 0
    #     for line in df_output:
    #         if line.split()[1][-1] == 'M':
    #             total_size += float(line.split()[1][:-1]) / 1024
    #         else:
    #             total_size += float(line.split()[1][:-1])
    #     #print('磁盘容量: %.2f GB' % total_size)
    #     # 获取硬盘IOPS
    #     iostat_result = subprocess.run(['iostat', '-d', '1', '1'], capture_output=True, text=True)
    #     iostat_output = iostat_result.stdout.strip().split('\n')[3:]
    #     total_iops = 0
    #     for line in iostat_output:
    #         total_iops += float(line.split()[1])
    #     #print('IOPS: %.2f' % total_iops)
    #     # 获取硬盘吞吐量
    #     io_rate = total_iops * 512 / 1024  # 512 为扇区大小
    #     #print('磁盘吞吐量: %.2f MB' % io_rate)
    # return round(total_size, 2), round(total_iops, 2), round(io_rate, 2)
    # 获取外存（硬盘）信息
    disk_info = psutil.disk_usage('/')
    total_disk = disk_info.total  # 总外存
    used_disk = disk_info.used  # 已用外存
    free_disk = disk_info.free  # 空闲外存
    disk_percent = disk_info.percent  # 外存使用率

    print(f"总外存: {total_disk / (1024 ** 3):.2f} GB")
    print(f"已用外存: {used_disk / (1024 ** 3):.2f} GB")
    print(f"空闲外存: {free_disk / (1024 ** 3):.2f} GB")
    print(f"外存使用率: {disk_percent}%")
    return total_disk, free_disk, used_disk

def getIOPS():
    total_iops = 0
    io_rate = 0
    if platform.system().lower() == 'linux':
        # 获取磁盘IOPS信息的命令
        command = ["iostat", "-dx", "1", "2"]  # 运行两个周期，以忽略启动时的初始统计数据

        # 执行命令并捕获输出
        result = subprocess.run(command, capture_output=True, text=True)

        # 打印命令的输出结果
        print(result.stdout)
    elif platform.system().lower() == 'windows':
        # 获取磁盘IOPS信息的命令
        command = [
            "typeperf",
            r"\PhysicalDisk(_Total)\Disk Reads/sec",
            r"\PhysicalDisk(_Total)\Disk Writes/sec",
            "-sc", "1"
        ]

        # 执行命令并捕获输出
        result = subprocess.run(command, capture_output=True, text=True)

        # 打印命令的输出结果
        print(result.stdout)
    return total_iops, io_rate
""" DISK END """


""" CACHE INFO"""
def getCacheInfo():
    cached_size = 0
    if platform.system().lower() == 'linux':
        with open('/proc/meminfo', 'r') as f:
            for line in f:
                if 'Cached' in line:
                    _, cached_size, _ = line.partition(':')
                    cached_size = cached_size.strip().split()[0]
                    cached_size =  int(cached_size) * 1024  # 转换成字节

    print(f"缓存大小: {cached_size / (1024 ** 3):.2f} GB")

    return cached_size / (1024 ** 3)


def getNetInfo():
    pass
