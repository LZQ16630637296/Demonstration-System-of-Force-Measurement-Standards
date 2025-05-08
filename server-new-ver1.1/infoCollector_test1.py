from infoCollector import getCPUInfo, getCPUFLOPS, getCPUCount, getCPUCore, getCPUPercent, getGPUCount, getGPUInfo, \
    getNetInfo, getMEMInfo, getDiskInfo, getGPUUtil, getIOPS, getCacheInfo

print("cpu信息：", getCPUInfo())
print("cpu的flops：", getCPUFLOPS())
print("cpu个数：", getCPUCount())
print("cpu核心数：", getCPUCore())
print("cpu使用率：", getCPUPercent())
print("gpu信息：", getGPUInfo())
print("gpu数量：", getGPUCount())
print("gpu使用率：", getGPUUtil())
print("内存信息：", getMEMInfo()[0])
print("磁盘信息：", getDiskInfo())
print("IOPS信息：", getIOPS())
print("Cache信息：", getCacheInfo())
# getCPUPercent()
# getGPUInfo()
# getGPUUtil()
