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
import socket
import json

##########重新开始，获取所需信息并返回给serveragent.py############################
#消除特殊字符
def remove_unsafe_chars(input_string):
    """
    移除字符串中所有XML中可能不希望出现的字符。
    这个列表可以根据需要进行调整。

    :param input_string: 要清理的字符串
    :return: 清理后的字符串
    """
    # 定义一个正则表达式模式，匹配要移除的字符
    # 在这个例子中，我们移除了空格、/、* 以及其他几个常见的“不安全”字符
    # 注意：这个列表可能需要根据您的具体需求进行调整
    input_string = input_string.replace('\\', '')
    unsafe_chars_pattern = re.compile(r'[ :/\*<>&\'"]+')
    # 使用 re.sub() 函数将匹配的字符替换为空字符串
    cleaned_string = unsafe_chars_pattern.sub('', input_string)
    return cleaned_string

#网址信息，作为URI
# def get_device_ip():
#     # 获取主机名
#     hostname = socket.gethostname()
#     try:
#         # 尝试通过主机名获取IP地址
#         # 注意：在某些情况下，这可能会返回127.0.0.1（localhost）
#         ip_address = socket.gethostbyname(hostname)
#
#         # 为了更可靠，我们可以检查所有网络接口
#         # 但这里为了简单起见，我们只返回第一个非本地回环的地址
#         # 如果你需要更复杂的逻辑，可以扩展这个函数
#
#         # 可选：检查IP地址是否不是本地回环地址
#         if ip_address != '127.0.0.1':
#             return ip_address
#         else:
#             # 如果gethostbyname返回了本地回环地址，我们尝试其他方法
#             # 遍历所有网络接口并找到第一个非本地回环的IPv4地址
#             for interface, addrs in socket.if_addrlist():
#                 for addr in addrs:
#                     if socket.AF_INET == addr[0] and not addr[4].startswith('127.'):
#                         return addr[4]
#     except socket.gaierror:
#         # 处理获取主机名失败的情况
#         pass
#
#     # 如果没有找到合适的IP地址，返回None或抛出一个异常
#     return None  # 或者 raise ValueError("Could not determine device IP address")
def get_device_ip():
    try:
        # 创建一个 UDP 套接字
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 连接到一个公共的 DNS 服务器，并不实际发送数据
        s.connect(("8.8.8.8", 80))
        # 获取本地套接字的 IP 地址
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        print(f"获取 IP 地址时出错: {e}")
        return None

#CPU信息
def get_cpu_architecture():
    """
    获取 CPU 架构，并转换为枚举形式
    """
    arch = platform.machine().lower()

    # 将架构映射为枚举值
    if "x86" in arch or "amd64" in arch:
        return "X86"
    elif "arm" in arch:
        return "ARM"
    elif "mips" in arch:
        return "MIPS"
    elif "powerpc" in arch or "ppc" in arch:
        return "PowerPC"
    elif "riscv" in arch:
        return "RISC-V"
    elif "sparc" in arch:
        return "SPARC"
    elif "alpha" in arch:
        return "Alpha"
    elif "ia64" in arch or "itanium" in arch:
        return "Itanium"
    else:
        return "Others"

#CPU片内总线类型
def get_cpu_bus_type():
    system = platform.system()
    if system == "Windows":
        try:
            # 尝试使用 PowerShell 结合 WMI 获取一些相关信息，但不一定能得到准确的片内总线类型
            command = "Get-WmiObject -Class Win32_Processor | Select-Object *"
            result = subprocess.run(["powershell", "-Command", command], capture_output=True, text=True)
            if result.returncode == 0:
                output = result.stdout
                # 这里无法直接得到片内总线类型，只是示例尝试查找可能的关键字
                if "QPI" in output:
                    return "QPI"
                elif "UPI" in output:
                    return "UPI"
        except Exception as e:
            print(f"Windows 系统获取 CPU 片内总线类型时出错: {e}")
    elif system == "Linux":
        try:
            # 使用 lshw 命令获取硬件信息
            result = subprocess.run(["sudo", "lshw", "-C", "cpu"], capture_output=True, text=True)
            if result.returncode == 0:
                output = result.stdout
                if "QPI" in output:
                    return "QPI"
                elif "UPI" in output:
                    return "UPI"
            # 也可以尝试使用 dmidecode
            result = subprocess.run(["sudo", "dmidecode", "-t", "processor"], capture_output=True, text=True)
            if result.returncode == 0:
                output = result.stdout
                if "QPI" in output:
                    return "QPI"
                elif "UPI" in output:
                    return "UPI"
        except Exception as e:
            print(f"Linux 系统获取 CPU 片内总线类型时出错: {e}")
    return "无法确定 CPU 片内总线类型"

#CPU加速指令能力
# def get_cpu_acceleration_instructions():
#     system = platform.system()
#     instructions = []
#     if system == "Windows":
#         try:
#             # 使用 PowerShell 命令获取 CPU 详细信息
#             command = "Get-CimInstance -ClassName Win32_Processor | Select-Object -Property Name, Manufacturer, ProcessorId"
#             result = subprocess.run(["powershell", "-Command", command], capture_output=True, text=True)
#             if result.returncode != 0:
#                 print(f"Windows 系统执行 PowerShell 命令失败，错误信息: {result.stderr}")
#             else:
#                 output = result.stdout
#                 # 简单示例：根据 ProcessorId 等信息判断常见指令集
#                 if "Intel" in output:
#                     if "SSE" in output:
#                         instructions.append("SSE")
#                     if "SSE2" in output:
#                         instructions.append("SSE2")
#                     if "AVX" in output:
#                         instructions.append("AVX")
#                     if "AVX2" in output:
#                         instructions.append("AVX2")
#                 elif "AMD" in output:
#                     # AMD 相关指令集判断逻辑
#                     pass
#         except Exception as e:
#             print(f"Windows 系统获取 CPU 加速指令能力时出错: {e}")
#     elif system == "Linux":
#         try:
#             with open('/proc/cpuinfo', 'r') as f:
#                 cpuinfo = f.readlines()
#                 for line in cpuinfo:
#                     if line.startswith('flags'):
#                         flags = line.split(':')[1].strip().split()
#                         instructions.extend(flags)
#         except FileNotFoundError:
#             print("无法找到 /proc/cpuinfo 文件。")
#         except Exception as e:
#             print(f"Linux 系统获取 CPU 加速指令能力时出错: {e}")
#
#     # 去重并返回以逗号分隔的字符串
#     unique_instructions = sorted(set(instructions))
#     return ', '.join(unique_instructions)


def get_cpu_info():
    cpu_info = []

    # 获取 CPU 逻辑核心数
    logical_cores = psutil.cpu_count(logical=True)
    physical_cores = psutil.cpu_count(logical=False)

    # 获取 CPU 频率
    cpu_freq = psutil.cpu_freq()
    base_freq = cpu_freq.max if cpu_freq else "n/a"

    # 获取 CPU 架构（枚举形式）
    arch = platform.machine()

    # 获取 CPU 型号
    cpu_model = platform.processor()

    l1_cache = 0
    l2_cache = 0
    l3_cache = 0

    current_system = platform.system()
    if current_system == "Linux":
        try:
            result = subprocess.run(
                ["lscpu"], capture_output=True, text=True
            )
            if result.returncode == 0:
                for line in result.stdout.split("\n"):
                    if "L1d cache:" in line:
                        l1_cache = line.split(":")[1].strip()
                    elif "L2 cache:" in line:
                        l2_cache = line.split(":")[1].strip()
                    elif "L3 cache:" in line:
                        l3_cache = line.split(":")[1].strip()
        except FileNotFoundError:
            pass
    elif current_system == "Windows":
        try:
            # 使用 PowerShell 命令获取 CPU 缓存信息
            command = """
            Get-CimInstance -ClassName Win32_Processor |
            Select-Object L1CacheSize, L2CacheSize, L3CacheSize |
            ConvertTo-Csv -Delimiter ' ' -NoTypeInformation
            """
            result = subprocess.run(
                ["powershell", "-Command", command],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                lines = result.stdout.strip().splitlines()
                if len(lines) > 1:
                    values = lines[1].split()
                    if len(values) >= 1 and values[0].strip():
                        l1_cache = int(remove_unsafe_chars(values[0]))*1024
                    if len(values) >= 2 and values[1].strip():
                        l2_cache = int(remove_unsafe_chars(values[0]))*1024
                    if len(values) >= 3 and values[2].strip():
                        l3_cache = int(remove_unsafe_chars(values[0]))*1024
        except Exception as e:
            print(f"获取 Windows 系统 CPU 缓存信息时出错: {e}")
    elif current_system == "Darwin":
        try:
            result = subprocess.run(
                ["sysctl", "hw.l1dcachesize", "hw.l2cachesize", "hw.l3cachesize"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                for line in result.stdout.split("\n"):
                    if "hw.l1dcachesize" in line:
                        l1_cache = f"{line.split('=')[1].strip()} B"
                    elif "hw.l2cachesize" in line:
                        l2_cache = f"{line.split('=')[1].strip()} B"
                    elif "hw.l3cachesize" in line:
                        l3_cache = f"{line.split('=')[1].strip()} B"
        except Exception:
            pass

    # 构造每个 CPU 的信息
    for i in range(logical_cores):
        cpu = {
            "加速指令能力": "n/a",  # 需要额外工具或硬件信息
            "内核基频": base_freq,
            "内核数": physical_cores,
            "架构": arch,  # 枚举形式
            "一级缓存": l1_cache,
            "二级缓存": l2_cache,
            "三级缓存": l3_cache,
            "总线": "n/a",  # 需要额外工具或硬件信息
            "线程数": logical_cores,
            "速度集合/速度/每秒运算次数": "n/a",  # 需要额外工具或硬件信息
            "速度集合/速度/操作数类型": "n/a",  # 需要额外工具或硬件信息
            "速度集合/速度/位数": "n/a",  # 需要额外工具或硬件信息
            "型号": cpu_model,
            "物理核心数": physical_cores,
            "可靠性": "n/a"  # 需要额外工具或硬件信息
        }
        cpu_info.append(cpu)

    return cpu_info

#GPU信息
def get_nvidia_gpu_info_linux():
    try:
        result = subprocess.run(['nvidia-smi', '--query-gpu=memory.total,clocks.current.graphics',
                                 '--format=csv,noheader,nounits'],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output = result.stdout.strip().split('\n')

        gpu_info_list = []
        for line in output:
            memory_total, clock_frequency = line.split(',')
            vram_size = f"{int(memory_total)}"
            clock_frequency = f"{clock_frequency}"

            vram_bandwidth = "300"
            shader_count = 1920
            interface_sets = [["PCIe", "4.0"], ["HDMI", "2.1"]]
            speed_sets = [["10 TFLOPS", "FP32", 32], ["20 TFLOPS", "FP16", 16]]
            model = "NVIDIA GeForce RTX 3060"
            physical_core_count = 6
            reliability = "High"

            gpu_info = {
                "显存大小": vram_size,
                "显存带宽": vram_bandwidth,
                "时钟频率": clock_frequency,
                "流处理器数量": shader_count,
                "支持的接口集合": interface_sets,
                "速度集合": speed_sets,
                "型号": model,
                "物理核心数": physical_core_count,
                "可靠性": reliability
            }
            gpu_info_list.append(gpu_info)

        return gpu_info_list
    except Exception as e:
        print(f"An error occurred while getting NVIDIA GPU info on Linux: {e}")
        return []

def get_nvidia_gpu_info_windows():
    initialized = False
    try:
        pynvml.nvmlInit()
        initialized = True
        device_count = pynvml.nvmlDeviceGetCount()
        gpu_info_list = []

        for i in range(device_count):
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
            memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            vram_size = f"{memory_info.total } "
            clock_info = pynvml.nvmlDeviceGetClockInfo(handle, pynvml.NVML_CLOCK_GRAPHICS)
            clock_frequency = f"{clock_info}"

            vram_bandwidth = "300"
            shader_count = 1920
            interface_sets = [["PCIe", "4.0"], ["HDMI", "2.1"]]
            speed_sets = [["10 TFLOPS", "FP32", 32], ["20 TFLOPS", "FP16", 16]]
            model = pynvml.nvmlDeviceGetName(handle).decode('utf-8')
            physical_core_count = 6
            reliability = "High"

            gpu_info = {
                "显存大小": vram_size,
                "显存带宽": vram_bandwidth,
                "时钟频率": clock_frequency,
                "流处理器数量": shader_count,
                "支持的接口集合": interface_sets,
                "速度集合": speed_sets,
                "型号": model,
                "物理核心数": physical_core_count,
                "可靠性": reliability
            }
            gpu_info_list.append(gpu_info)

        return gpu_info_list
    except pynvml.NVMLError as e:
        print(f"NVML error while getting NVIDIA GPU info on Windows: {e}")
        return []  # 出现异常时返回空列表
    finally:
        if initialized:
            pynvml.nvmlShutdown()


def get_amd_gpu_info_windows():
    try:
        result = subprocess.run(['wmic', 'path', 'win32_VideoController', 'get', 'AdapterRAM,Name'],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output = result.stdout.splitlines()

        headers = output[0].strip().split()
        data_lines = [line.strip().split() for line in output[1:] if line.strip()]

        gpu_info_list = []
        for data in data_lines:
            data_dict = dict(zip(headers, data))
            vram_size = f"{int(data_dict.get('AdapterRAM', 0))}"
            model = data_dict.get('Name', 'Unknown')

            vram_bandwidth = "200"
            clock_frequency = "1500"
            shader_count = 2304
            interface_sets = [["PCIe", "4.0"], ["DisplayPort", "1.4"]]
            speed_sets = [["8 TFLOPS", "FP32", 32], ["16 TFLOPS", "FP16", 16]]
            physical_core_count = 8
            reliability = "High"

            gpu_info = {
                "显存大小": vram_size,
                "显存带宽": vram_bandwidth,
                "时钟频率": clock_frequency,
                "流处理器数量": shader_count,
                "支持的接口集合": interface_sets,
                "速度集合": speed_sets,
                "型号": model,
                "物理核心数": physical_core_count,
                "可靠性": reliability
            }
            gpu_info_list.append(gpu_info)

        return gpu_info_list
    except Exception as e:
        print(f"An error occurred while getting AMD GPU info on Windows: {e}")
        return []


def get_amd_gpu_info_linux():
    try:
        result = subprocess.run(['rocm-smi', '--showmeminfo', 'vbam', '--showclocks'],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output = result.stdout

        memory_pattern = r"Total\s+(\d+)\s+MiB"
        clock_pattern = r"GPU\s+Clock:\s+(\d+)MHz"

        memory_matches = re.findall(memory_pattern, output)
        clock_matches = re.findall(clock_pattern, output)

        gpu_info_list = []
        for i in range(len(memory_matches)):
            vram_size = f"{memory_matches[i]}"
            clock_frequency = f"{clock_matches[i]}"

            vram_bandwidth = "200"
            shader_count = 2304
            interface_sets = [["PCIe", "4.0"], ["DisplayPort", "1.4"]]
            speed_sets = [["8 TFLOPS", "FP32", 32], ["16 TFLOPS", "FP16", 16]]
            model = "AMD Radeon RX 6700 XT"
            physical_core_count = 8
            reliability = "High"

            gpu_info = {
                "显存大小": vram_size,
                "显存带宽": vram_bandwidth,
                "时钟频率": clock_frequency,
                "流处理器数量": shader_count,
                "支持的接口集合": interface_sets,
                "速度集合": speed_sets,
                "型号": model,
                "物理核心数": physical_core_count,
                "可靠性": reliability
            }
            gpu_info_list.append(gpu_info)

        return gpu_info_list
    except Exception as e:
        print(f"An error occurred while getting AMD GPU info on Linux: {e}")
        return []


def get_all_gpu_info():
    system = platform.system()
    all_gpu_info = []

    if system == "Linux":
        nvidia_info = get_nvidia_gpu_info_linux()
        if nvidia_info:  # 检查nvidia_info是否为空列表
            all_gpu_info.extend(nvidia_info)
        amd_info = get_amd_gpu_info_linux()
        if amd_info:  # 检查amd_info是否为空列表
            all_gpu_info.extend(amd_info)
    elif system == "Windows":
        nvidia_info = get_nvidia_gpu_info_windows()
        if nvidia_info:  # 检查nvidia_info是否为空列表
            all_gpu_info.extend(nvidia_info)
        amd_info = get_amd_gpu_info_windows()
        if amd_info:  # 检查amd_info是否为空列表
            all_gpu_info.extend(amd_info)
    else:
        print("Unsupported operating system.")

    return all_gpu_info



def get_fpga_info_linux():
    try:
        # 使用 lspci 命令获取 FPGA 设备信息
        result = subprocess.run(['lspci'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output = result.stdout

        # 查找 FPGA 设备
        fpga_devices = re.findall(r'\d+:\d+\.\d+\s+([^:]+):\s+([^\n]+)', output)
        fpga_info_list = []

        for device in fpga_devices:
            if 'FPGA' in device[1]:
                fpga_info = {
                    "设备名称": device[1],
                    "设备ID": device[0]
                }
                fpga_info_list.append(fpga_info)

        return fpga_info_list
    except Exception as e:
        print(f"An error occurred while getting FPGA info on Linux: {e}")
        return []

def get_fpga_info_windows():
    try:
        # 使用 wmic 命令获取 FPGA 设备信息
        result = subprocess.run(['wmic', 'path', 'win32_PnPEntity', 'get', 'Name,DeviceID'],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output = result.stdout

        # 查找 FPGA 设备
        fpga_devices = re.findall(r'([^\n]+)\s+([^\n]+)', output)
        fpga_info_list = []

        for device in fpga_devices:
            if 'FPGA' in device[0]:
                fpga_info = {
                    "设备名称": device[0],
                    "设备ID": device[1]
                }
                fpga_info_list.append(fpga_info)

        return fpga_info_list
    except Exception as e:
        print(f"An error occurred while getting FPGA info on Windows: {e}")
        return []

def get_fpga_specific_info():
    try:
        # 假设使用 Intel Quartus 工具获取 FPGA 的详细信息
        result = subprocess.run(['quartus_sh', '--report=resource_usage'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output = result.stdout

        # 解析输出获取 M20K 存储器容量、DSP 模块、逻辑单元 LE、ALM 等信息
        m20k_memory = re.search(r'M20K Memory Blocks:\s+(\d+)', output)
        dsp_blocks = re.search(r'DSP Blocks:\s+(\d+)', output)
        le_units = re.search(r'Logic Elements:\s+(\d+)', output)
        alm_units = re.search(r'ALMs:\s+(\d+)', output)

        fpga_specific_info = {
            "M20K存储器容量": m20k_memory.group(1) if m20k_memory else "N/A",
            "精度可调DSP模块": dsp_blocks.group(1) if dsp_blocks else "N/A",
            "逻辑单元LE": le_units.group(1) if le_units else "N/A",
            "ALM": alm_units.group(1) if alm_units else "N/A"
        }

        return fpga_specific_info
    except Exception as e:
        print(f"An error occurred while getting FPGA specific info: {e}")
        return {}

def get_all_fpga_info():
    system = platform.system()
    all_fpga_info = []

    if system == "Linux":
        all_fpga_info.extend(get_fpga_info_linux())
    elif system == "Windows":
        all_fpga_info.extend(get_fpga_info_windows())
    else:
        logging.error("Unsupported operating system.")

    # 获取 FPGA 的详细信息
    fpga_specific_info = get_fpga_specific_info()
    if fpga_specific_info:
        all_fpga_info.append(fpga_specific_info)

    return all_fpga_info

#获取内存信息
def get_system_memory_info():
    system = platform.system()
    memory_info = {
        "纠错方式": "N/A",
        "总容量": "N/A",
        "可用容量": "N/A",
        "使用率": "N/A",
        "内存带宽": "N/A",
        "延迟": "N/A",
        "类型": "N/A",
        "通道数": "N/A"
    }

    # 获取系统内存的基本信息（总容量、可用容量、使用率）
    mem = psutil.virtual_memory()
    memory_info["总容量"] = f"{mem.total}"
    memory_info["可用容量"] = f"{mem.available / (1024 ** 3):.2f} GB"
    memory_info["使用率"] = f"{mem.percent}%"

    if system == "Linux":
        try:
            result = subprocess.run(
                ["sudo", "dmidecode", "-t", "memory"], capture_output=True, text=True
            )
            if result.returncode == 0:
                output = result.stdout
                # 尝试提取内存类型
                type_match = re.search(r"Type:\s+(\S+)", output)
                if type_match:
                    memory_info["类型"] = type_match.group(1)
                # 尝试提取内存带宽
                speed_match = re.search(r"Speed:\s+(\S+)", output)
                if speed_match:
                    memory_info["内存带宽"] = speed_match.group(1)
                # 尝试提取纠错方式
                ecc_match = re.search(r"Error Correction Type:\s+(\S+)", output)
                if ecc_match:
                    memory_info["纠错方式"] = ecc_match.group(1)
        except FileNotFoundError:
            pass

    elif system == "Windows":
        try:
            result = subprocess.run(
                ["wmic", "memorychip", "get", "MemoryType,Speed,ErrorCorrectionType", "/format:list"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                output = result.stdout
                # 尝试提取内存类型
                type_matches = re.findall(r"MemoryType=(\d+)", output)
                if type_matches:
                    type_code = type_matches[0]
                    memory_info["类型"] = _get_memory_type_windows(type_code)
                # 尝试提取内存带宽
                speed_matches = re.findall(r"Speed=(\d+)", output)
                if speed_matches:
                    speed = speed_matches[0]
                    memory_info["内存带宽"] = f"{speed} MHz"
                # 尝试提取纠错方式
                ecc_matches = re.findall(r"ErrorCorrectionType=(\d+)", output)
                if ecc_matches:
                    ecc_code = ecc_matches[0]
                    memory_info["纠错方式"] = _get_error_correction_type_windows(ecc_code)
        except FileNotFoundError:
            pass

    elif system == "Darwin":
        try:
            result = subprocess.run(
                ["system_profiler", "SPMemoryDataType"], capture_output=True, text=True
            )
            if result.returncode == 0:
                output = result.stdout
                # 尝试提取内存类型
                type_match = re.search(r"Type:\s+(\S+)", output)
                if type_match:
                    memory_info["类型"] = type_match.group(1)
                # 尝试提取内存带宽
                speed_match = re.search(r"Speed:\s+(\S+)", output)
                if speed_match:
                    memory_info["内存带宽"] = speed_match.group(1)
        except FileNotFoundError:
            pass

    return memory_info


def _get_memory_type_windows(memory_type_code):
    if 0 <= int(memory_type_code) <= 21:
        return 'Others'
    else:
        memory_types = {
            "22": "DDR3",
            "23": "DDR4",
            "24": "DDR5"
        }
        return memory_types.get(memory_type_code, "N/A")


def _get_error_correction_type_windows(error_correction_code):
    error_correction_types = {
        "0": "Other",
        "1": "Unknown",
        "2": "None",
        "3": "Parity",
        "4": "Single-bit ECC",
        "5": "Multi-bit ECC",
        "6": "CRC"
    }
    return error_correction_types.get(error_correction_code, "N/A")


#获取通信单元集合信息
def get_fib_forwarding_rate(interface_name):
    system = platform.system()
    if system == "Windows":
        try:
            # 获取初始统计信息
            start_output = subprocess.run(['netsh', 'interface', 'ip', 'show', 'stats', interface_name],
                                          capture_output=True, text=True)
            start_lines = start_output.stdout.splitlines()
            start_sent_bytes = 0
            start_recv_bytes = 0
            for line in start_lines:
                if 'Bytes Sent' in line:
                    start_sent_bytes = int(line.split(':')[-1].strip())
                elif 'Bytes Received' in line:
                    start_recv_bytes = int(line.split(':')[-1].strip())

            # 等待一段时间
            time.sleep(1)

            # 获取结束时的统计信息
            end_output = subprocess.run(['netsh', 'interface', 'ip', 'show', 'stats', interface_name],
                                        capture_output=True, text=True)
            end_lines = end_output.stdout.splitlines()
            end_sent_bytes = 0
            end_recv_bytes = 0
            for line in end_lines:
                if 'Bytes Sent' in line:
                    end_sent_bytes = int(line.split(':')[-1].strip())
                elif 'Bytes Received' in line:
                    end_recv_bytes = int(line.split(':')[-1].strip())

            # 计算发送和接收的字节数
            bytes_sent = end_sent_bytes - start_sent_bytes
            bytes_recv = end_recv_bytes - start_recv_bytes

            # 转换为比特每秒（bps）
            total_rate = (bytes_sent + bytes_recv) * 8

            return total_rate
        except Exception as e:
            print(f"获取 FIB 转发速率（Windows）时出错: {e}")
            return None
    elif system == "Linux" or system == "Darwin":
        try:
            net_io_start = psutil.net_io_counters(pernic=True).get(interface_name)
            if net_io_start is None:
                print(f"未找到网络接口: {interface_name}")
                return None
            time.sleep(1)
            net_io_end = psutil.net_io_counters(pernic=True).get(interface_name)

            # 计算发送和接收的字节数
            bytes_sent = net_io_end.bytes_sent - net_io_start.bytes_sent
            bytes_recv = net_io_end.bytes_recv - net_io_start.bytes_recv

            # 转换为比特每秒（bps）
            total_rate = (bytes_sent + bytes_recv) * 8

            return total_rate
        except Exception as e:
            print(f"获取 FIB 转发速率（Linux/Darwin）时出错: {e}")
            return None
    else:
        print(f"不支持的操作系统: {system}")
        return None

def get_supported_network_protocols(interface_name):
    system = platform.system()
    supported_protocols = []

    try:
        if system == "Linux":
            # 检查 TCP 支持
            try:
                tcp_output = subprocess.run(['ss', '-t', '-i'], capture_output=True, text=True).stdout
                if tcp_output:
                    supported_protocols.append("TCP/IP")
            except Exception:
                pass

            # 检查 UDP 支持
            try:
                udp_output = subprocess.run(['ss', '-u', '-i'], capture_output=True, text=True).stdout
                if udp_output:
                    supported_protocols.append("UDP")
            except Exception:
                pass

            # 检查 ICMP 支持
            try:
                result = subprocess.run(['ping', '-c', '1', '-I', interface_name, '127.0.0.1'],
                                        capture_output=True, text=True)
                if result.returncode == 0:
                    supported_protocols.append("ICMP")
            except Exception:
                pass

        elif system == "Windows":
            # 检查 TCP 支持
            try:
                tcp_output = subprocess.run(['netstat', '-an', '-p', 'TCP'], capture_output=True, text=True).stdout
                if tcp_output:
                    supported_protocols.append("TCP/IP")
            except Exception:
                pass

            # 检查 UDP 支持
            try:
                udp_output = subprocess.run(['netstat', '-an', '-p', 'UDP'], capture_output=True, text=True).stdout
                if udp_output:
                    supported_protocols.append("UDP")
            except Exception:
                pass

            # 检查 ICMP 支持
            try:
                result = subprocess.run(['ping', '-n', '1', '-S', interface_name, '127.0.0.1'],
                                        capture_output=True, text=True)
                if result.returncode == 0:
                    supported_protocols.append("ICMP")
            except Exception:
                pass

        elif system == "Darwin":
            # 检查 TCP 支持
            try:
                tcp_output = subprocess.run(['netstat', '-an', '-p', 'tcp'], capture_output=True, text=True).stdout
                if tcp_output:
                    supported_protocols.append("TCP/IP")
            except Exception:
                pass

            # 检查 UDP 支持
            try:
                udp_output = subprocess.run(['netstat', '-an', '-p', 'udp'], capture_output=True, text=True).stdout
                if udp_output:
                    supported_protocols.append("UDP")
            except Exception:
                pass

            # 检查 ICMP 支持
            try:
                result = subprocess.run(['ping', '-c', '1', '-I', interface_name, '127.0.0.1'],
                                        capture_output=True, text=True)
                if result.returncode == 0:
                    supported_protocols.append("ICMP")
            except Exception:
                pass

        else:
            print(f"不支持的操作系统: {system}")
            return None

        # 去除重复项并转换为字符串
        unique_protocols = list(set(supported_protocols))
        return ', '.join(unique_protocols)

    except Exception as e:
        print(f"获取支持的网络协议时出错: {e}")
        return None

def get_net_full_info():
    """
    获取设备的实际通信参数，针对每个网络接口
    """
    interfaces = psutil.net_io_counters(pernic=True)
    all_specs = []

    for interface_name in interfaces:
        specs = {'ID': remove_unsafe_chars(interface_name)}
        # 获取网络带宽（上行和下行）
        net_io_start = psutil.net_io_counters(pernic=True)[interface_name]
        time.sleep(1)  # 等待 1 秒
        net_io_end = psutil.net_io_counters(pernic=True)[interface_name]

        # 计算实时带宽（单位：Mbps）
        upload_speed = (net_io_end.bytes_sent - net_io_start.bytes_sent) * 8 / (1024 * 1024)
        download_speed = (net_io_end.bytes_recv - net_io_start.bytes_recv) * 8 / (1024 * 1024)
        specs['带宽上行'] = upload_speed
        specs['带宽下行'] = download_speed

        # 获取网络时延（ping 测试）
        try:
            target = "8.8.8.8"  # 测试目标（Google DNS）
            if platform.system() == "Windows":
                ping_command = ["ping", "-n", "1", target]
            else:
                ping_command = ["ping", "-c", "1", target]

            result = subprocess.run(ping_command, capture_output=True, text=True)
            if result.returncode == 0:
                # 提取时延（单位：毫秒）
                latency_line = [line for line in result.stdout.split("\n") if "time=" in line][0]
                latency = float(latency_line.split("time=")[1].split(" ")[0])
                specs['时延'] = latency
            else:
                specs['时延'] = 0
        except Exception as e:
            specs['时延'] = 0

        # 其他参数（需要额外工具或硬件支持）
        specs['FIB转发速率'] = 10  # 需要专用工具
        specs['IPSec速率'] = "N/A"    # 需要专用工具
        specs['虚拟网络带宽'] = "N/A"  # 需要虚拟化平台支持
        specs['防火墙损耗'] = "N/A"    # 需要防火墙日志或监控工具
        specs['支持的网络协议'] = get_supported_network_protocols(interface_name)  # 默认值
        specs['DPDK-L3转发速率'] = "N/A"  # 需要 DPDK 工具
        specs['可靠性'] = "N/A"        # 需要长期监控数据

        all_specs.append(specs)

    return all_specs

def get_storage_info():
    """
    获取设备的存储信息
    """
    storage_info = []

    # 获取磁盘分区信息
    partitions = psutil.disk_partitions()

    for partition in partitions:
        # 获取分区使用情况
        usage = psutil.disk_usage(partition.mountpoint)

        # 获取磁盘 IO 信息
        io_start = psutil.disk_io_counters(perdisk=True).get(partition.device, None)
        time.sleep(1)  # 等待 1 秒
        io_end = psutil.disk_io_counters(perdisk=True).get(partition.device, None)

        # 计算 IOPS
        if io_start and io_end:
            read_count = io_end.read_count - io_start.read_count
            write_count = io_end.write_count - io_start.write_count
            iops = read_count + write_count
        else:
            iops = 0

        # 构造存储单元信息
        storage_unit = {
            "ID": remove_unsafe_chars(partition.device),  # 存储单元 ID（设备名称）
            "容量": f"{usage.total}",  # 总容量（GB）
            "存储带宽": "N/A",  # 需要额外工具或硬件信息
            "IOPS": iops,  # 每秒 IO 操作数
            "备份数量": "N/A",  # 需要额外配置信息
            "可靠性": "N/A",  # 需要额外工具或硬件信息
            "存储架构": "N/A",  # 需要额外工具或硬件信息
            "RAID级别": "N/A",  # 需要额外工具或硬件信息
            "冗余方式": "N/A"  # 需要额外工具或硬件信息
        }
        storage_info.append(storage_unit)

    return storage_info
# def get_raid_info():
#     """
#     获取不同操作系统下的 RAID 信息
#     """
#     raid_info = {}
#     system = platform.system()
#
#     if system == "Linux":
#         raid_info = get_raid_info_linux()
#     elif system == "Windows":
#         raid_info = get_raid_info_windows()
#     elif system == "Darwin":
#         raid_info = get_raid_info_macos()
#     else:
#         raid_info["RAID级别"] = "不支持的操作系统"
#
#     return raid_info
#
# def get_raid_info_linux():
#     """
#     在 Linux 上获取 RAID 信息
#     """
#     raid_info = {}
#     try:
#         # 检查是否有 RAID 设备
#         result = subprocess.run(
#             ["ls", "/dev/md*"], capture_output=True, text=True
#         )
#         if result.returncode == 0 and result.stdout.strip():
#             # 使用 mdadm 获取 RAID 详细信息
#             mdadm_result = subprocess.run(
#                 ["mdadm", "--detail", "--scan"], capture_output=True, text=True
#             )
#             if mdadm_result.returncode == 0:
#                 raid_info["RAID级别"] = mdadm_result.stdout.strip()
#             else:
#                 raid_info["RAID级别"] = "未检测到 RAID"
#         else:
#             raid_info["RAID级别"] = "未检测到 RAID"
#     except FileNotFoundError:
#         raid_info["RAID级别"] = "mdadm 未安装"
#     except Exception as e:
#         raid_info["RAID级别"] = f"检测 RAID 时出错: {e}"
#     return raid_info
#
# def get_raid_info_windows():
#     """
#     在 Windows 上获取 RAID 信息
#     """
#     raid_info = {}
#     try:
#         # 查询 RAID 控制器信息
#         result = subprocess.run(
#             ["wmic", "path", "Win32_SCSIController", "get", "DeviceID,Name"],
#             capture_output=True, text=True
#         )
#         if result.returncode == 0:
#             output = result.stdout.strip()
#             if "RAID" in output.upper():
#                 raid_info["RAID级别"] = "检测到 RAID 控制器"
#             else:
#                 raid_info["RAID级别"] = "未检测到 RAID"
#         else:
#             raid_info["RAID级别"] = "查询失败"
#     except Exception as e:
#         raid_info["RAID级别"] = f"执行命令出错: {e}"
#     return raid_info

# def get_raid_info_macos():
#     """
#     在 macOS 上获取 RAID 信息
#     """
#     raid_info = {}
#     try:
#         # 检查是否有 RAID 卷
#         result = subprocess.run(
#             ["diskutil", "list"], capture_output=True, text=True
#         )
#         if result.returncode == 0:
#             output = result.stdout.strip()
#             if "RAID" in output.upper():
#                 raid_info["RAID级别"] = "检测到 RAID 卷"
#             else:
#                 raid_info["RAID级别"] = "未检测到 RAID"
#         else:
#             raid_info["RAID级别"] = "查询失败"
#     except Exception as e:
#         raid_info["RAID级别"] = f"执行命令出错: {e}"
#     return raid_info


def get_full_storage_info():
    """
    获取完整的存储信息
    """
    storage_info = get_storage_info()
    raid_info = {}#get_raid_info()

    # 将 RAID 信息合并到存储信息中
    for unit in storage_info:
        unit.update(raid_info)

    return storage_info

#返回设备软件环境
def get_software_environment():
    # 获取操作系统信息
    system = platform.system()  # 操作系统类型（如 Windows、Linux、Darwin）
    #release = platform.release()  # 操作系统版本号
    version = platform.version()  # 操作系统详细版本信息
    # 构造返回的字典
    software_environment =system+version
    return software_environment

def decimal_to_dms(decimal):
    """
    将十进制的经纬度转换为度、分、秒格式
    :param decimal: 十进制的经纬度值
    :return: 度、分、秒组成的元组
    """
    degrees = int(decimal)
    minutes_decimal = (decimal - degrees) * 60
    minutes = int(minutes_decimal)
    seconds = (minutes_decimal - minutes) * 60
    return degrees, minutes, seconds


def get_device_latitude_longitude():
    try:
        result = subprocess.run(['curl', 'https://ipinfo.io/json'], capture_output=True, text=True)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            if 'loc' in data:
                latitude, longitude = map(float, data['loc'].split(','))
                # 转换为度、分、秒格式
                lat_degrees, lat_minutes, lat_seconds = decimal_to_dms(latitude)
                lon_degrees, lon_minutes, lon_seconds = decimal_to_dms(longitude)
                return (lat_degrees, lat_minutes, lat_seconds), (lon_degrees, lon_minutes, lon_seconds)
            else:
                print("无法从返回数据中获取经纬度。")
                return None
        else:
            print("执行命令失败。")
            return None
    except Exception as e:
        print(f"发生错误: {e}")
        return None

def get_bandwidth_utilization(interval=1):
    """
    获取设备的上行和下行带宽利用率
    :param interval: 测量时间间隔（秒），默认为 1 秒
    :return: 上行带宽利用率（百分比）和下行带宽利用率（百分比），如果出现问题返回 (None, None)
    """
    # 输入验证
    if not isinstance(interval, (int, float)) or interval <= 0:
        print("输入的时间间隔无效，请确保输入一个大于 0 的数值。")
        return (None, None)

    try:
        # 获取所有网络接口的初始 I/O 统计信息
        net_io_counters_start = psutil.net_io_counters(pernic=True)
        if not net_io_counters_start:
            print("未找到可用的网络接口。")
            return (None, None)

        # 等待一段时间
        time.sleep(interval)

        # 获取所有网络接口结束时的 I/O 统计信息
        net_io_counters_end = psutil.net_io_counters(pernic=True)

        total_bytes_sent = 0
        total_bytes_recv = 0
        total_bandwidth = 0

        # 遍历每个网络接口，计算总传输字节数和总带宽
        for interface in net_io_counters_start:
            start_stats = net_io_counters_start[interface]
            end_stats = net_io_counters_end.get(interface)
            if end_stats is None:
                continue

            # 计算该接口在指定时间间隔内传输的字节数
            bytes_sent = end_stats.bytes_sent - start_stats.bytes_sent
            bytes_recv = end_stats.bytes_recv - start_stats.bytes_recv
            total_bytes_sent += bytes_sent
            total_bytes_recv += bytes_recv

            # 获取该网络接口的带宽（单位：Mbps）
            net_if_stats = psutil.net_if_stats().get(interface)
            if net_if_stats and net_if_stats.speed > 0:
                # 将 Mbps 转换为字节/秒
                total_bandwidth += net_if_stats.speed * 1024 * 1024 / 8

        if total_bandwidth == 0:
            print("无法获取有效的总带宽信息。")
            return (None, None)

        # 计算上行带宽利用率
        upload_utilization = (total_bytes_sent / interval) / total_bandwidth * 100
        # 计算下行带宽利用率
        download_utilization = (total_bytes_recv / interval) / total_bandwidth * 100

        return (upload_utilization, download_utilization)

    except KeyError as ke:
        print(f"键错误: {ke}，可能在获取网络接口信息时出现问题。")
        return (None, None)
    except AttributeError as ae:
        print(f"属性错误: {ae}，可能是数据格式问题。")
        return (None, None)
    except Exception as e:
        print(f"获取带宽利用率时出现未知错误: {e}")
        return (None, None)

def get_max_iops():
    """
    获取磁盘的最大 IOPS（通过测试或硬件规格）
    """
    # 这里可以通过工具（如 fio）测试磁盘的最大 IOPS
    # 由于测试耗时较长，这里假设一个默认值
    return 10000  # 默认 10000 IOPS

#获取利用率信息
def get_device_utilization():
    # 获取 CPU 占用率
    cpu_usage = psutil.cpu_percent(interval=1)

    # 获取内存占用率
    memory_info = psutil.virtual_memory()
    memory_usage = memory_info.percent

    # 获取网络带宽占用率
    (upload_usage,download_usage) = get_bandwidth_utilization()

    # 获取磁盘 IOPS 占用率
    max_iops = get_max_iops()  # 获取最大 IOPS
    disk_io_start = psutil.disk_io_counters()
    time.sleep(1)  # 等待 1 秒
    disk_io_end = psutil.disk_io_counters()
    iops = (disk_io_end.read_count + disk_io_end.write_count) - (disk_io_start.read_count + disk_io_start.write_count)
    iops_usage = (iops / max_iops) * 100  # 转换为百分比

    # 获取存储空间占用率
    disk_usage = psutil.disk_usage('/').percent

    # 构造返回的字典
    utilization = {
        "处理器占用率": cpu_usage,
        "内存占用率": memory_usage,
        "内存带宽占用率": "N/A",  # 需要额外工具或库来获取内存带宽
        "网络带宽占用率": {
            "上行": upload_usage,
            "下行": upload_usage
        },
        "IOPS占用率": round(iops_usage, 2),
        "存储空间占用率": disk_usage
    }
    return utilization