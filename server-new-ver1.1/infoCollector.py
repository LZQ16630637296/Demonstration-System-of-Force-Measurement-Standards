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
import time
import psutil
# import cpuinfo
import pynvml
import re

def update(topics, values):
    pass

""" CPU INFO """

def getCPUInfo():
    if platform.system() == 'Windows':
        command = "wmic cpu get name"
        output = subprocess.check_output(command, shell=True).decode("utf-8")
        for line in output.strip().split('\n')[1:]:
            return line.strip()
    elif platform.system() == 'Linux':
        command = "cat /proc/cpuinfo | grep 'model name' | uniq"
        output = subprocess.check_output(command, shell=True).decode("utf-8")
        return output.strip().split(':')[1].strip()
    elif platform.system() == 'Darwin':
        command = "sysctl -n machdep.cpu.brand_string"
        output = subprocess.check_output(command, shell=True).decode("utf-8")
        return output.strip()
    else:
        return "Unsupported platform"
    
# def getCPUInfo():
#     # CPUINFO = cpuinfo.get_cpu_info()['brand_raw']
#     # CPUINFO = psutil.cpu_info().brand
#     # print(CPUINFO)
#     CPUINFO = platform.processor() 
#     return CPUINFO

# intel 7th-12th + X-series
CPU_dict = {
    "i9-12900T": "358.4",
    "i7-12700T": "268.8",
    "i5-12600T": "201.6",
    "i5-12500T": "192",
    "i5-12400T": "172.8",
    "i3-12300T": "147.2",
    "i3-12300": "224",
    "i3-12100T": "140.8",
    "i9-12900K": "819.2",
    "i7-12700K": "691.2",
    "i5-12600K": "592",
    "i9-12900KF": "819.2",
    "i7-12700KF": "691.2",
    "i5-12600KF": "592",
    "i9-12900E": "588.8",
    "i9-12900TE": "281.6",
    "i7-12700E": "403.2",
    "i7-12700TE": "268.8",
    "i3-12100TE": "134.4",
    "i3-12100E": "204.8",
    "i5-12500TE": "182.4",
    "i5-12500E": "278.4",
    "i9-12900": "614.4",
    "i7-12700": "403.2",
    "i9-12900F": "614.4",
    "i7-12700F": "403.2",
    "i5-12600": "316.8",
    "i5-12400": "240",
    "i3-12100": "211.2",
    "i5-12400F": "240",
    "i3-12100F": "211.2",
    "i5-12450H": "256",
    "i5-12500H": "480",
    "i5-12600H": "518.4",
    "i7-12650H": "368",
    "i7-12700H": "515.2",
    "i7-12800H": "537.6",
    "i9-12900HK": "560",
    "i9-12900H": "560",
    "i7-1280P": "403.2",
    "i7-1260P": "403.2",
    "i7-1270P": "422.4",
    "i5-1250P": "326.4",
    "i5-1240P": "326.4",
    "i5-1250PE": "326.4",
    "i7-1270PE": "345.6",
    "i5-12600HE": "480",
    "i7-12800HE": "537.6",
    "i3-1220PE": "192",
    "i3-12300HE": "243.2",
    "i7-1265U": "288",
    "i7-1255U": "272",
    "i5-1235U": "208",
    "i3-1215U": "115.2",
    "i3-1220P": "240",
    "i3-1210U": "96",
    "i5-1230U": "160",
    "i7-1250U": "176",
    "i7-1260U": "176",
    "i5-1245U": "256",
    "i5-1240U": "176",
    "i9-12900KS": "870.4",
    "i7-1265UE": "272",
    "i5-1245UE": "240",
    "i3-1215UE": "115.2",
    "i5-1145G7": "166.4",
    "i7-1180G7": "83.2",
    "i5-1140G7": "70.4",
    "i7-11375H": "211.2",
    "i7-11370H": "211.2",
    "i5-11300H": "198.4",
    "i9-11900T": "192",
    "i7-11700T": "179.2",
    "i5-11600T": "163.2",
    "i5-11500T": "144",
    "i5-11400T": "124.8",
    "i7-1195G7": "185.6",
    "i5-1155G7": "160",
    "i5-11320H": "204.8",
    "i7-11390H": "217.6",
    "i9-11980HK": "332.8",
    "i5-11260H": "249.6",
    "i5-11400H": "259.2",
    "i5-11500H": "278.4",
    "i7-11800H": "294.4",
    "i7-11850H": "320",
    "i9-11950H": "332.8",
    "i9-11900H": "320",
    "i7-11600H": "278.4",
    "i5-11600": "268.8",
    "i9-11900F": "320",
    "i7-11700F": "320",
    "i5-11600KF": "374.4",
    "i5-11400F": "249.6",
    "i9-11900KF": "448",
    "i7-11700KF": "460.8",
    "i5-11500": "259.2",
    "i5-11400": "249.6",
    "i9-11900": "320",
    "i7-11700K": "460.8",
    "i7-11700": "320",
    "i5-11600K": "374.4",
    "i9-11900K": "448",
    "i9-11900KB": "422.4",
    "i7-11700B": "409.6",
    "i5-11500B": "316.8",
    "i3-11100B": "230.4",
    "i7-11850HE": "332.8",
    "i5-11500HE": "249.6",
    "i3-11100HE": "153.6",
    "i5-11300H": "198.4",
    "i7-11370H": "211.2",
    "i7-11375H": "211.2",
    "i3-1120G4": "70.4",
    "i3-1125G4": "128",
    "i7-1185G7": "192",
    "i7-1165G7": "179.2",
    "i3-1115GRE": "96",
    "i3-1115G4E": "96",
    "i5-1145GRE": "166.4",
    "i5-1145G7E": "166.4",
    "i7-1185GRE": "179.2",
    "i7-1185G7E": "179.2",
    "i3-1110G4": "57.6",
    "i5-1130G7": "70.4",
    "i5-1140G7": "70.4",
    "i7-1160G7": "76.8",
    "i7-1180G7": "83.2",
    "i3-1115G4": "96",
    "i5-1135G7": "153.6",
    "i5-1145G7": "166.4",
    "i3-10105T": "192",
    "i3-10100Y": "41.6",
    "i3-10105F": "236.8",
    "i3-10305": "243.2",
    "i3-10105": "236.8",
    "i7-10710U": "105.6",
    "i7-1065G7": "83.2",
    "i7-10510U": "115.2",
    "i7-10510Y": "76.8",
    "i5-1035G7": "76.8",
    "i5-1035G4": "70.4",
    "i5-1035G1": "64",
    "i5-10310Y": "70.4",
    "i5-10210Y": "64",
    "i5-10210U": "102.4",
    "i3-10110U": "67.2",
    "i3-10110Y": "32",
    "i3-1005G1": "38.4",
    "i3-10100Y": "41.6",
    "i9-10850K": "576",
    "i5-10500H": "240",
    "i7-10870H": "281.6",
    "i5-10200H": "153.6",
    "i9-10910": "576",
    "i3-10100F": "230.4",
    "i5-10500E": "297.6",
    "i7-10700E": "371.2",
    "i7-10700TE": "256",
    "i9-10900E": "448",
    "i9-10900TE": "288",
    "i5-10400": "278.4",
    "i7-10700": "371.2",
    "i5-10600K": "393.6",
    "i9-10900K": "592",
    "i9-10885H": "307.2",
    "i9-10900KF": "592",
    "i9-10900F": "448",
    "i5-10400F": "278.4",
    "i7-10700F": "371.2",
    "i7-10700KF": "486.4",
    "i5-10600KF": "393.6",
    "i9-10900": "448",
    "i7-10700K": "486.4",
    "i3-10100": "230.4",
    "i3-10300": "236.8",
    "i5-10500": "297.6",
    "i5-10600": "316.8",
    "i3-10320": "243.2",
    "i7-10875H": "294.4",
    "i5-10310U": "108.8",
    "i7-10610U": "115.2",
    "i7-10810U": "105.6",
    "i9-10900T": "304",
    "i9-10980HK": "307.2",
    "i5-10400H": "166.4",
    "i7-10750H": "249.6",
    "i7-10850H": "259.2",
    "i5-10300H": "160",
    "i7-10700T": "256",
    "i3-10100TE": "147.2",
    "i3-10100E": "204.8",
    "i5-10500TE": "220.8",
    "i3-10100T": "192",
    "i3-10300T": "192",
    "i5-10400T": "192",
    "i5-10500T": "220.8",
    "i5-10600T": "230.4",
    "i3-1000NG4": "35.2",
    "i5-1038NG7": "128",
    "i7-1068NG7": "147.2",
    "i5-1030NG7": "51.2",
    "i7-1060NG7": "64",
    "i3-1000G4": "35.2",
    "i7-1060G7": "64",
    "i3-1000G1": "35.2",
    "i9-9900KS": "512",
    "i7-9850HE": "259.2",
    "i7-9700E": "332.8",
    "i7-9700TE": "230.4",
    "i5-9300HF": "153.6",
    "i3-9100HL": "102.4",
    "i3-9100TE": "140.8",
    "i9-9900T": "268.8",
    "i9-9900": "396.8",
    "i9-9980HK": "307.2",
    "i9-9880H": "294.4",
    "i9-9900KF": "460.8",
    "i9-9900K": "460.8",
    "i7-9750HF": "249.6",
    "i7-9850H": "249.6",
    "i7-9750H": "249.6",
    "i7-9700T": "256",
    "i7-9700F": "384",
    "i7-9700": "384",
    "i7-9700K": "460.8",
    "i7-9700KF": "460.8",
    "i5-9600T": "220.8",
    "i5-9600": "297.6",
    "i5-9500T": "211.2",
    "i5-9500F": "288",
    "i5-9500": "288",
    "i5-9400T": "172.8",
    "i5-9400H": "160",
    "i5-9300H": "153.6",
    "i5-9600K": "355.2",
    "i5-9600KF": "355.2",
    "i5-9400F": "278.4",
    "i5-9400": "278.4",
    "i3-9350K": "256",
    "i3-9320": "236.8",
    "i3-9300T": "204.8",
    "i3-9300": "236.8",
    "i3-9100T": "198.4",
    "i3-9100F": "230.4",
    "i3-9100": "230.4",
    "i3-9350KF": "256",
    "i7-8665UE": "108.8",
    "i5-8365UE": "102.4",
    "i3-8145UE": "70.4",
    "i7-8557U": "108.8",
    "i5-8257U": "89.6",
    "i9-8950HK": "278.4",
    "i7-8665U": "121.6",
    "i7-8850H": "249.6",
    "i7-8809G": "198.4",
    "i7-8709G": "198.4",
    "i7-8706G": "198.4",
    "i7-8705G": "198.4",
    "i7-8750H": "211.2",
    "i7-8700T": "230.4",
    "i7-8700K": "355.2",
    "i7-8700B": "307.2",
    "i7-8700": "307.2",
    "i7-8565U": "115.2",
    "i7-8650U": "121.6",
    "i7-8559U": "179.2",
    "i7-8550U": "115.2",
    "i7-8500Y": "48",
    "i7-8086K": "384",
    "i5-8365U": "102.4",
    "i5-8310Y": "51.2",
    "i5-8600T": "220.8",
    "i5-8600K": "345.6",
    "i5-8600": "297.6",
    "i5-8500T": "201.6",
    "i5-8500B": "288",
    "i5-8500": "288",
    "i5-8400T": "163.2",
    "i5-8400H": "160",
    "i5-8400B": "268.8",
    "i5-8400": "268.8",
    "i5-8350U": "108.8",
    "i5-8305G": "179.2",
    "i5-8300H": "147.2",
    "i5-8269U": "166.4",
    "i5-8265U": "102.4",
    "i5-8259U": "147.2",
    "i5-8250U": "102.4",
    "i5-8210Y": "51.2",
    "i5-8200Y": "41.6",
    "i3-8350K": "256",
    "i3-8300": "236.8",
    "i3-8300T": "204.8",
    "i3-8145U": "67.2",
    "i3-8130U": "70.4",
    "i3-8109U": "96",
    "i3-8100": "230.4",
    "i3-8100B": "230.4",
    "i3-8100H": "192",
    "i3-8100T": "198.4",
    "m3-8100Y": "35.2",
    "i7-7920HQ": "198.4",
    "i7-7820HQ": "185.6",
    "i7-7820HK": "185.6",
    "i7-7820EQ": "192",
    "i7-7700HQ": "179.2",
    "i7-7700": "230.4",
    "i7-7700K": "268.8",
    "i7-7700T": "185.6",
    "i7-7660U": "80",
    "i7-7600U": "89.6",
    "i7-7567U": "112",
    "i7-7560U": "76.8",
    "i7-7500U": "86.4",
    "i7-7Y75": "41.6",
    "i5-7600K": "243.2",
    "i5-7600T": "179.2",
    "i5-7600": "224",
    "i5-7500": "217.6",
    "i5-7500T": "172.8",
    "i5-7442EQ": "134.4",
    "i5-7440HQ": "179.2",
    "i5-7440EQ": "185.6",
    "i5-7400T": "153.6",
    "i5-7400": "192",
    "i5-7360U": "73.6",
    "i5-7300U": "83.2",
    "i5-7300HQ": "160",
    "i5-7287U": "105.6",
    "i5-7267U": "99.2",
    "i5-7260U": "70.4",
    "i5-7200U": "80",
    "i5-7Y54": "38.4",
    "i5-7Y57": "38.4",
    "i3-7350K": "134.4",
    "i3-7320": "131.2",
    "i3-7300": "128",
    "i3-7300T": "112",
    "i3-7130U": "86.4",
    "i3-7102E": "67.2",
    "i3-7101E": "124.8",
    "i3-7101TE": "108.8",
    "i3-7100T": "108.8",
    "i3-7100E": "92.8",
    "i3-7100": "124.8",
    "i3-7167U": "89.6",
    "i3-7100U": "76.8",
    "i3-7100H": "96",
    "i3-7020U": "73.6",
    "M3-7Y30": "32",
    "M3-7Y32": "35.2",

    "i9-10980XE": "604.8",
    "i9-10940X": "537.6",
    "i9-10920X": "460.8",
    "i9-10900X": "432",
    "i9-9980XE": "1209.6",
    "i9-7980XE": "1152",
    "i9-9960X": "1177.6",
    "i9-9940X": "1075.2",
    "i9-9920X": "921.6",
    "i9-9900X": "864",
    "i9-9820X": "864",
    "i9-7960X": "1075.2",
    "i9-7940X": "1075.2",
    "i9-7920X": "844.8",
    "i9-7900X": "800",
    "i7-9800X": "742.4",
    "i7-7820X": "691.2",
    "i7-7800X": "576",
    "i7-7740X": "275.2",
    "i5-7640X": "256",
    "i7-6950X": "480",
    "i7-6900K": "409.6",
    "i7-6850K": "345.6",
    "i7-6800K": "326.4",
    "i7-5960X": "384",
    "i7-5930K": "336",
    "i7-5820K": "316.8",
    "i7-4960X": "172.8",
    "i7-4940MX": "198.4",
    "i7-4930K": "163.2",
    "i7-4930MX": "192",
    "i7-4820K": "118.4",
    "i7-3970X": "168",
    "i7-3960X": "158.4",
    "i7-3940XM": "96",
    "i7-3930K": "153.6",
    "i7-3920XM": "92.8",
    "i7-3820": "115.2",
    "ARMv8":"13.9"

}

def getCPUFLOPS():
    cpu_info = getCPUInfo()
    pattern = r"i\d-[0-9A-Za-z]+"
    pattern1 = r"ARMv\d[0-9A-Za-z]+"
    cpu_name = re.search(pattern, cpu_info)
    if cpu_name is None:
        cpu_name = re.search(pattern1, cpu_info)
    # print('cpuname:',cpu_name)
    # print(f"cpu的flops：{flops} GFLOPS")
    if cpu_name:
        flops = CPU_dict.get(cpu_name.group())
        return float(flops)
    else:
        return 0
        # return flops

def getCPUCount():
    cpu_count = psutil.cpu_count()  # 逻辑核心数
    """ TODO  how to get cpu count """
    return cpu_count

def getCPUCore():
    cpu_core = psutil.cpu_count(logical=False)  # 物理核心数
    return cpu_core

def getCPUPercent():
    cpu_percent = psutil.cpu_percent(percpu=True)  # 各个cpu
    # for i in range(len(cpu_percent)):
    #     print(f"第 {i} 张卡的使用率为：{cpu_percent[i]}")
    #     # yield i, cpu_percent[i]
    return cpu_percent
        

def getCPUFrequence():
    cpu_freq = psutil.cpu_freq()  # CPU频率

    # print(f"当前CPU频率: {cpu_freq.current:.2f} MHz")
    # print(f"最小CPU频率: {cpu_freq.min:.2f} MHz")
    # print(f"最大CPU频率: {cpu_freq.max:.2f} MHz")
    return round(cpu_freq.current, 2), round(cpu_freq.min, 2), round(cpu_freq.max, 2)

""" CPU INFO END """

""" GPU INFO """
def getGPUCount():
    pynvml.nvmlInit()  # 初始化
    gpu_device_count = pynvml.nvmlDeviceGetCount()  # 获取Nvidia GPU块数
    pynvml.nvmlShutdown()  # 关闭管理工具
    return gpu_device_count

def getGPUInfo():
    try:
        pynvml.nvmlInit()  # 初始化
        gpu_device_count = pynvml.nvmlDeviceGetCount()  # 获取Nvidia GPU块数
        UNIT = 1024*1024
        G_flops = 0
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

            # print(f"第 {gpu_index} 张卡")
            # print(f"显卡名：{gpu_name}")
            # print(f"内存总容量：{memery_info.total / UNIT} MB")
            # print(f"使用容量：{(memery_info.total -memery_info.free) / UNIT} MB")
            # print(f"剩余容量：{memery_info.free / UNIT} MB")
            # print(f"显存空闲率：{memery_info.free / memery_info.total}")
            # print(f"温度：{gpu_temperature} 摄氏度")
            # # print(f"风扇速率：{gpu_fan_speed}")
            # print(f"供电水平：{gpu_power_state}")
            # print(f"gpu计算核心满速使用率：{gpu_util_rate}")
            # print(f"gpu内存读写满速使用率：{gpu_memory_rate}")
            # print(f"内存占用率：{memery_info.used / memery_info.total}")

            flops = getGPUFLOPS(gpu_name)
            G_flops += flops

            # yield gpu_index, gpu_name, gpu_util_rate, gpu_memory_rate, memery_info.total / UNIT
        pynvml.nvmlShutdown()  # 关闭管理工具
        # print(f"gpu的flops：{G_flops} TFLOPS")
    except Exception as e:
        return 0
    return G_flops

def getGPUPercent():
    percent = []
    try:
        pynvml.nvmlInit()  # 初始化
        gpu_device_count = pynvml.nvmlDeviceGetCount()  # 获取Nvidia GPU块数
        UNIT = 1024*1024
        
        for gpu_index in range(gpu_device_count):
            handle = pynvml.nvmlDeviceGetHandleByIndex(gpu_index)  # 获取GPU i的handle，后续通过handle来处理
            memery_info = pynvml.nvmlDeviceGetMemoryInfo(handle)  # 通过handle获取GPU 的信息

            # print(f"第 {gpu_index} 张卡的使用率为：{pynvml.nvmlDeviceGetUtilizationRates(handle).gpu}")
            percent[gpu_index] = pynvml.nvmlDeviceGetUtilizationRates(handle).gpu

            # yield gpu_index, pynvml.nvmlDeviceGetUtilizationRates(handle).gpu  # memery_info.used / memery_info.total
        pynvml.nvmlShutdown()  # 关闭管理工具
    except Exception as e:
        return [0]
    return percent

GPU_dict = {"NVIDIA GeForce GTX 950": "1.57 TFLOPS",
   "NVIDIA T600 Laptop GPU": "2.5 TFLOPS",
   "Valve Steam Deck (AMD RDNA2 1.6GHz)": "1.6 TFLOPS",
   "SONY PlayStation 4": "1.84 TFLOPS",
   "NVIDIA GeForce GTX 1050": "1.862 TFLOPS",
   "AMD Radeon HD 7850": "1.946 TFLOPS",
   "GeForce GTX 1050 Ti": "2.138 TFLOPS",
   "NVIDIA GeForce GTX 960": "2.3 TFLOPS",
   "NVIDIA GeForce GTX 580": "2.37 TFLOPS",
   "NVIDIA GeForce GTX 680": "3.09 TFLOPS",
   "AMD Radeon R9 380": "3.48 TFLOPS",
   "NVIDIA GeForce GTX 970": "3.49 TFLOPS",
   "Microsoft Xbox Series S": "4 TFLOPS",
   "SONY PlayStation 4 Pro": "4.2 TFLOPS",
   "AMD Radeon HD 7970 GHz Edition": "4.3 TFLOPS",
   "NVIDIA GeForce GTX 1060": "4.4 TFLOPS",
   "NVIDIA GeForce GTX Titan": "4.5 TFLOPS",
   "NVIDIA GeForce GTX 980": "4.6 TFLOPS",
   "AMD Radeon HD 6990": "4.98 TFLOPS",
   "NVIDIA GeForce GTX 780Ti": "5 TFLOPS",
   "AMD Radeon RX 570": "5.095 TFLOPS",
   "AMD Radeon R9 390": "5.1 TFLOPS",
   "AMD Radeon RX 480": "5.1 TFLOPS",
   "NVIDIA GeForce GTX 1660 Ti": "5.5 TFLOPS",
   "NVIDIA GeForce GTX 980 Ti": "5.6 TFLOPS",
   "AMD Radeon R9 290X": "5.6 TFLOPS",
   "Microsoft Xbox One X": "6 TFLOPS",
   "NVIDIA GeForce GTX 1070": "6 TFLOPS",
   "AMD Radeon RX 580": "6.175 TFLOPS",
   "NVIDIA GeForce RTX 2060": "6.5 TFLOPS",
   "NVIDIA GeForce GTX Titan X": "7 TFLOPS",
   "AMD Radeon RX 590": "7.119 TFLOPS",
   "NVIDIA GeForce RTX 2060 Super": "7.2 TFLOPS",
   "NVIDIA GeForce RTX 2070": "7.5 TFLOPS",
   "AMD Radeon RX 5700": "7.949 TFLOPS",
   "NVIDIA GeForce GTX Titan Z": "8.1 TFLOPS",
   "NVIDIA GeForce GTX 1070 ti": "8.168 TFLOPS",
   "AMD Radeon R9 Nano": "8.19 TFLOPS",
   "AMD Radeon HD 7990": "8.2 TFLOPS",
   "AMD Radeon R9 FURY X": "8.602 TFLOPS",
   "NVIDIA GeForce GTX 1080": "9 TFLOPS",
   "NVIDIA GeForce RTX 2070 Super": "9.1 TFLOPS",
   "NVIDIA Tesla P100": "9.5 TFLOPS",
   "AMD Radeon RX 5700 XT": "9.754 TFLOPS",
   "NVIDIA GeForce RTX 2080": "10.1 TFLOPS",
   "SONY PlayStation 5": "10.3 TFLOPS",
   "AMD Radeon RX 6700": "10.37 TFLOPS",
   "AMD Radeon RX Vega 56": "10.54 TFLOPS",
   "NVIDIA Titan X": "11 TFLOPS",
   "NVIDIA GeForce RTX 2080 Super": "11.2 TFLOPS",
   "AMD Radeon R9 295X2": "11.46 TFLOPS",
   "NVIDIA GeForce GTX 1080 Ti": "11.5 TFLOPS",
   "Microsoft Xbox Series X": "12.155 TFLOPS",
   "AMD Radeon RX Vega 64": "12.66 TFLOPS",
   "NVIDIA GeForce RTX 3060": "12.8 TFLOPS",
   "AMD Radeon RX 6700 XT": "13.21 TFLOPS",
   "NVIDIA GeForce RTX 2080 Ti": "13.45 TFLOPS",
   "NVIDIA Tesla V100": "14.1 TFLOPS",
   "NVIDIA Titan V": "14.9 TFLOPS",
   "AMD Radeon RX 6800": "16.17 TFLOPS",
   "NVIDIA GeForce RTX 3060 Ti": "16.2 TFLOPS",
   "NVIDIA Titan RTX": "16.31 TFLOPS",
   "NVIDIA GeForce RTX 3070": "20.3 TFLOPS",
   "AMD Radeon RX 6800 XT": "20.74 TFLOPS",
   "AMD Radeon RX 6900 XT": "23.04 TFLOPS",
   "NVIDIA GeForce RTX 3080": "29.8 TFLOPS",
   "NVIDIA GeForce RTX 3080 Ti": "34.1 TFLOPS",
   "NVIDIA GeForce RTX 3090": "35.7 TFLOPS",
   "NVIDIA Orin NX Developer Kit":"30 TFLOPS"
   }

def getGPUFLOPS(gpu_name):
    """ TODO GET GPUINFO AND traverse the list """
    flops = GPU_dict.get(gpu_name)
    match = re.search(r"([\d.]+)\s+", flops)
    # flops = float(match.group(1))
    if flops:
        return float(match.group(1))
    else:
        return 0
    # return flops

""" GPU INFO END """


""" MEM INFO """
def getMEMInfo():
    memory_info = psutil.virtual_memory()
    total_memory = memory_info.total  # 总内存
    available_memory = memory_info.available  # 可用内存
    used_memory = memory_info.used  # 已用内存
    memory_percent = memory_info.percent  # 内存使用率

    # print(f"总内存: {total_memory / (1024 ** 3):.2f} GB")
    # print(f"可用内存: {available_memory / (1024 ** 3):.2f} GB")
    # print(f"已用内存: {used_memory / (1024 ** 3):.2f} GB")
    # print(f"内存使用率: {memory_percent}%")
    return total_memory / (1024 ** 3), available_memory / (1024 ** 3), used_memory / (1024 ** 3)

""" MEM END """

""" DISK INFO """
def getDiskInfo():
    # 获取外存（硬盘）信息
    disk_info = psutil.disk_usage('/')
    total_disk = disk_info.total  # 总外存
    used_disk = disk_info.used  # 已用外存
    free_disk = disk_info.free  # 空闲外存
    disk_percent = disk_info.percent  # 外存使用率

    # print(f"总外存: {total_disk / (1024 ** 3):.2f} GB")
    # print(f"已用外存: {used_disk / (1024 ** 3):.2f} GB")
    # print(f"空闲外存: {free_disk / (1024 ** 3):.2f} GB")
    # print(f"外存使用率: {disk_percent}%")
    return total_disk/ (1024 ** 3), free_disk/ (1024 ** 3), used_disk/ (1024 ** 3)

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
        # print(result.stdout)
    return total_iops, io_rate
""" DISK END """


""" CACHE INFO"""
def getCacheInfo():
    cached_size = 0
    if platform.system().lower() == 'linux':
        with open('/proc/meminfo', 'r') as f:
            for line in f:
                if 'Cache' in line and "SwapCached" not in line:
                    # print('cache开始')
                    # print(line)
                    # print('cache结束')
                    # _, cached_size, _ = line.partition(':')
                    # cached_size = cached_size.strip().split()[0]

                    
                    match = re.search(r'\d+', line)
                    cached_size = int(match.group())
                    # cached_size =  int(cached_size) *1024   

    # print(f"缓存大小: {cached_size / (1024 ** 3):.2f} GB")

    return cached_size / (1024 ** 3)


def getNetInfo():
    # 获取网络IO信息
    net_io = psutil.net_io_counters()

    # 当前接收的字节数
    current_bytes_recv = net_io.bytes_recv
    # print(current_bytes_recv)
    # 当前发送的字节数
    current_bytes_sent = net_io.bytes_sent
    # print(current_bytes_sent)

    time.sleep(0.1)
    time_interval = 0.1
    # 一段时间后再次获取网络IO信息i
    # 这里可以加入适当的延时，例如time.sleep(1)
    # 再次获取网络IO信息
    net_io = psutil.net_io_counters()
    # print(net_io)

    # 计算网络吞吐量
    # 接收的字节数差值除以时间间隔（秒）得到接收速率，单位为字节/秒
    recv_speed = (net_io.bytes_recv - current_bytes_recv) / time_interval
    # 发送的字节数差值除以时间间隔（秒）得到发送速率，单位为字节/秒
    sent_speed = (net_io.bytes_sent - current_bytes_sent) / time_interval

    # # 输出结果
    # print("当前接收速率: ", recv_speed, "B/s")
    # print("当前发送速率: ", sent_speed, "B/s")
    stats = psutil.net_if_stats()# 获取网络接口信息, 返回json，各个key的snicstats中的speed属性有用
    # print('stats:', stats)
    # print('stats:', stats['以太网'])
    return sent_speed/ (1024 ** 2), recv_speed/ (1024 ** 2)

