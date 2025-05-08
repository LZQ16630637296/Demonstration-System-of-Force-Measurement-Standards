import argparse
import os
import sys
import time

import psutil as psutil
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, CreateView, DetailView
from django.views import View
from node_info.models import Node
from node_info.forms import NodeCreateForm
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse, reverse_lazy
import xml.etree.ElementTree as ET
import io
from rest_framework_xml.parsers import XMLParser
import subprocess
from paho.mqtt import client as mqtt_client
import xmltodict

parser = argparse.ArgumentParser(description='')
parser.add_argument('--broker', type=str, default='127.0.0.1')
parser.add_argument('--port', type=int, default=1883)
parser.add_argument('--keepalive', type=int, default=60)
parser.add_argument('--timeslot', type=int, default=4)
parser.add_argument('--clientID', type=str, default='server')
args = parser.parse_known_args()[0]
brokerIP = args.broker
port = args.port
keepalive = args.keepalive
clientID = args.clientID
timeslot = args.timeslot
print(args)

topics = [
    'mqtt/server/start',
    'mqtt/server/stop',
    'mqtt/server/delete',
]

python_interpreter_path = "C:\\Users\\28395\\AppData\\Local\\Programs\\Python\\Python312\\python.exe"

# Create your views here.
class NodeList(ListView):
    model = Node
    template_name = 'node_info/node_info.html'

    # template_name = 'node_info/system_info.xml'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        # 运行 rec.py
        node = Node.objects.get(name='rec')  # rec.py运行后也作为一个node节点存放在数据库中
        exists = check_pid_exists(node.pid)
        # print(node.pid)
        if not exists:
            Node.objects.filter(name='rec').delete()
            # 使用subprocess.Popen来启动脚本
            process = subprocess.Popen([python_interpreter_path, 'rec/rec.py'], start_new_session=True)
            node, created = Node.objects.get_or_create(name='rec', IPaddress='127.0.0.1', port=18083, keepalive=60, pid=process.pid) #
            node.save()
            print("rec的pid为：", node.pid)
            nodes = Node.objects.all()
            for node in nodes:
                node.status = 0
                if node.name == 'edge2':
                    node.delete()
                else:
                    node.save()
        return context


def check_pid_exists(pid):
    if pid == -1:
        return False
    print("pid正在运行！：", pid)
    try:
        process = psutil.Process(pid)
        return process.is_running() and process.status() != psutil.STATUS_ZOMBIE
    except psutil.NoSuchProcess:
        return False


class NodeCreate(CreateView):
    form_class = NodeCreateForm
    model = Node
    template_name = 'node_info/node_create1.html'
    success_url = reverse_lazy('node_info:node_list')


def SysStatus(request, *args, **kwargs):
    template_name = 'node_info/system_info.xml'
    # return render_to_response(template_name, mimetype="application/xml")
    # return render(request, template_name)
    return HttpResponse(open("node_info/templates/node_info/system_info.xml", "rb"), content_type="text/xml")


class NodeDetail(DetailView):
    model = Node
    template_name = 'node_info/node_detail.html'


def SysStatusFile(request, *args, **kwargs):
    # f = open('node_info/templates/node_info/system_info.xml', 'r', encoding='utf-8')
    f = open('node_info/templates/node_info/task_info.xml', 'r', encoding='utf-8')
    attack_method = f.read()
    ## TODO 用xml方式读取内容， 并且组织成合适的结构传入html模板中
    attack_method = attack_method.split('\n')
    # attack_method = list(dict.fromkeys(attack_method))  ## 这里是去重
    f.close()
    f = open('node_info/templates/node_info/system_info.xml', 'r', encoding='utf-8')
    tmp = f.read()
    # s = io.StringIO(response.text)
    parser_data = xml_to_data2('node_info/templates/node_info/system_info.xml')
    f.close()
    return render(request, 'node_info/system_info.html', {"attack_method": attack_method, 'sys': parser_data})
def TaskStatusFile(request, *args, **kwargs):
    # f = open('node_info/templates/node_info/system_info.xml', 'r', encoding='utf-8')
    f = open('node_info/templates/node_info/task_info.xml', 'r', encoding='utf-8')
    attack_method = f.read()
    ## TODO 用xml方式读取内容， 并且组织成合适的结构传入html模板中
    attack_method = attack_method.split('\n')
    # attack_method = list(dict.fromkeys(attack_method))  ## 这里是去重
    f.close()
    f = open('node_info/templates/node_info/task_info.xml', 'r', encoding='utf-8')
    tmp = f.read()
    f.close()
    # s = io.StringIO(response.text)
    parser_data = xml_to_data('node_info/templates/node_info/task_info.xml')
    # print(parser_data)
    return render(request, 'node_info/task_info.html', {"attack_method": attack_method, 'task': parser_data})

def ResBaseFile(request, *args, **kwargs):
    # f = open('node_info/templates/node_info/base_info.xml', 'r', encoding='utf-8')
    f = open('node_info/templates/node_info/system_info.xml', 'r', encoding='utf-8')
    attack_method = f.read()
    ## TODO 用xml方式读取内容， 并且组织成合适的结构传入html模板中
    attack_method = attack_method.split('\n')
    # attack_method = list(dict.fromkeys(attack_method))  ## 这里是去重
    # s = io.StringIO(response.text)
    parser_data = xml_to_data('node_info/templates/node_info/system_info.xml')
    f.close()
    # print(parser_data)
    #return render(request, 'node_info/base_info.html', {"attack_method": attack_method, 'sys': parser_data})
    return render(request, 'node_info/res_info.html', {"attack_method": attack_method, 'sys': parser_data})

def ResultFile(request, *args, **kwargs):
    f = open('node_info/templates/node_info/task_off_res1.xml', 'r', encoding='utf-8')
    attack_method = f.read()
    ## TODO 用xml方式读取内容， 并且组织成合适的结构传入html模板中
    attack_method = attack_method.split('\n')
    # attack_method = list(dict.fromkeys(attack_method))  ## 这里是去重
    f.close()
    f = open('node_info/templates/node_info/task_off_res1.xml', 'r', encoding='utf-8')
    tmp = f.read()
    f.close()
    # s = io.StringIO(response.text)
    parser_data = xml_to_data('node_info/templates/node_info/task_off_res1.xml')
    # print(parser_data)
    return render(request, 'node_info/task_off_res1.html', {"attack_method": attack_method, 'sys': parser_data})

def ServerStart(request, *args, **kwargs):
    name = request.POST.get('button_name')
    node = Node.objects.get(name=name)
    print(name, node.name, node.status, node.pid, node.port, node.IPaddress)
    if node.status == 0:  # 表示该节点为接受模式
        # 连接mqtt
        server = ServerAgent(
            keepalive=keepalive,
            broker=brokerIP,
            port=port,
            clientID='to' + name,
            topics=topics,
        )
        msg = name + ":start"
        server.run(topics[0], msg)

        # 更改节点状态
        node.status = 1  # 更改节点为发送模式
        node.save()
        # node = Node.objects.get(name=name)
        # print(name, node.name, node.status, node.pid, node.port, node.IPaddress)
        messages.error(request, '节点启动成功')
        return HttpResponseRedirect(reverse('node_info:node_list'))
        # return HttpResponse("节点启动成功")
    else:
        messages.error(request, '节点正在运行')
        return HttpResponseRedirect(reverse('node_info:node_list'))


def ServerStop(request, *args, **kwargs):
    name = request.POST.get('button_name')
    node = Node.objects.get(name=name)
    if node.status == 1:
        # 连接mqtt
        server = ServerAgent(
            keepalive=keepalive,
            broker=brokerIP,
            port=port,
            clientID='to' + name,
            topics=topics,
        )
        msg = name + ":stop"
        server.run(topics[1], msg)
        # 更改节点状态
        node.status = 0  # 更改节点为发送模式
        node.save()

        # 重开rec，使xml中的信息更新
        rec_node = Node.objects.get(name='rec')
        print("rec的pid为：", rec_node.pid)
        # os.system('taskkill /pid ' + str(rec_node.pid) + ' /f /t') 
        # subprocess.run(['kill -9', str(rec_node.pid)], check=True)  
        try:  
            # subprocess.check_call(["kill", "-9", str(rec_node.pid)])    
            os.system(f'kill -9 {rec_node.pid}')
        except subprocess.CalledProcessError:  
            pass
        
        process = subprocess.Popen([python_interpreter_path, 'rec/rec.py'], start_new_session=True)
        rec_node.pid = process.pid
        rec_node.save()
        print("rec的pid为：", rec_node.pid)
        messages.error(request, '节点停止成功')
        return HttpResponseRedirect(reverse('node_info:node_list'))
    else:
        # return HttpResponse("节点未运行")
        messages.error(request, '节点未运行')
        return HttpResponseRedirect(reverse('node_info:node_list'))


def ServerDelete(request):
    name = request.POST.get('button_name')
    node = Node.objects.get(name=name)

    # 连接 MQTT
    server = ServerAgent(
        keepalive=keepalive,
        broker=brokerIP,
        port=port,
        clientID='to' + name,
        topics=topics,
    )
    msg = name + ":delete"
    server.run(topics[2], msg)

    # 查找 name='rec' 的记录，如果不存在则创建
    rec_node, created = Node.objects.update_or_create(
        name='rec',
        defaults={
            'pid': -1,
            'keepalive': 60,
            'IPaddress': '127.0.0.1',
            'port': '8080',
            'status': 0,
        }
    )

    try:
        os.system(f'kill -9 {rec_node.pid}')
    except subprocess.CalledProcessError:
        pass

    process = subprocess.Popen([python_interpreter_path, 'rec/rec.py'], start_new_session=True)

    # 更新 rec_node 的 pid
    rec_node.pid = process.pid
    rec_node.save()

    Node.objects.filter(name=name).delete()
    return HttpResponseRedirect(reverse('node_info:node_list'))

@csrf_exempt
def SysStatusFile1(request, *args, **kwargs):
    parser_data = xml_to_data2('node_info/templates/node_info/system_info.xml')
    print(parser_data,'9999')
    from django.http import JsonResponse
    return JsonResponse({'sys': parser_data})


@csrf_exempt
def TaskStatusFile1(request, *args, **kwargs):
    parser_data = xml_to_data('node_info/templates/node_info/task_info.xml')
    from django.http import JsonResponse
    return JsonResponse({'task': parser_data})

@csrf_exempt
def ResBaseFile1(request, *args, **kwargs):
    parser_data = xml_to_data('node_info/templates/node_info/res_info.xml')
    from django.http import JsonResponse
    return JsonResponse({'sys': parser_data})

@csrf_exempt
def ResultFile1(request, *args, **kwargs):
    parser_data = xml_to_data('node_info/templates/node_info/task_off_res1.xml')
    from django.http import JsonResponse
    return JsonResponse({'task': parser_data})

def TaskStart(request, *args, **kwargs):
    name = request.POST.get('button_name')
    node = Node.objects.get(name=name)
    exists = check_pid_exists(node.pid)
    if not exists:
        process = subprocess.Popen([python_interpreter_path, 'task/taskAgent.py'], start_new_session=True)
        node, created = Node.objects.get_or_create(name=name)
        # os.system('start /B python task/taskAgent.py')
        # # 保存子进程的PID
        # process = max(psutil.process_iter(['pid', 'name']), key=lambda x: x.create_time())
        # node, created = Node.objects.get_or_create(name=name)
        # # print('pid', process.pid)
        node.pid = process.pid
        node.status = 1
        node.save()
        print('启动任务pid:', process.pid)
        messages.error(request, '自动发送任务启动成功')
        return HttpResponseRedirect(reverse('node_info:node_list'))
    else:
        messages.error(request, '正在发送任务')
        return HttpResponseRedirect(reverse('node_info:node_list'))

def TaskStop(request, *args, **kwargs):
    name = request.POST.get('button_name')
    # 获取进程的PID
    node, created = Node.objects.get_or_create(name=name)
    node.status = 0
    node.save()
    exists = check_pid_exists(node.pid)
    if exists:
        # 停止进程rec和node
        rec_node = Node.objects.get(name='rec')
        print("停止PID:", node.pid)
        # os.system('taskkill /pid ' + str(node.pid) + ' /f /t')
        # os.system('taskkill /pid ' + str(rec_node.pid) + ' /f /t')
        # subprocess.run(['kill -9', str(node.pid)], check=True)  
        # subprocess.run(['kill -9', str(rec_node.pid)], check=True) 
        try:  
            # subprocess.check_call(["kill", "-9", str(node.pid)])    
            os.system(f'kill -9 {node.pid}')
        except subprocess.CalledProcessError:  
            pass
        try:  
            # subprocess.check_call(["kill", "-9", str(rec_node.pid)])  
            os.system(f'kill -9 {rec_node.pid}')  
        except subprocess.CalledProcessError:  
            pass


        process = subprocess.Popen([python_interpreter_path, 'rec/rec.py'], start_new_session=True)
        node, created = Node.objects.get_or_create(name='rec')
        # os.system('start /B python rec/rec.py')
        # process = max(psutil.process_iter(['pid', 'name']), key=lambda x: x.create_time())
        # node, created = Node.objects.get_or_create(name='rec')
        node.pid = process.pid
        node.status = 0
        node.save()
        # return HttpResponse("节点停止成功")
        messages.error(request, '节点停止成功')
        return HttpResponseRedirect(reverse('node_info:node_list'))
    else:
        # return HttpResponse("节点未运行")
        messages.error(request, '节点未运行')
        return HttpResponseRedirect(reverse('node_info:node_list'))


def Echart(request, *args, **kwargs):
    return render(request, 'node_info/echart.html')

@csrf_exempt
def TaskStatusPos(request, *args, **kwargs):
    parser_data = xml_to_data('node_info/templates/node_info/task_off_res.xml')
    # print(parser_data)

    data = []
    # data.append({'name': 'cloud', 'category': '服务器'})
    # data.append({'name': 'edge1', 'category': '服务器'})
    # data.append({'name': 'edge2', 'category': '服务器'})
    nodes = Node.objects.all()
    for node in nodes:
        if node.name != 'rec' and node.name != 'taskStart' and node.name != 'taskStop' and node.status == 1:
            data.append({'name': node.name, 'category': '服务器'})
    link = []
    if parser_data is not None:
        for k, v in parser_data['offloadingRes'].items():
            data.append({'name': k, 'category': '子任务'})
            server_ = {'name': v, 'category': '服务器'}
            if server_ not in data:
                data.append(server_)
            link.append({'source': v, 'target': k, 'name': 'offloading'})
    ## TODO
    ## REQ : 1. <服务器， 子任务>
    ## 所有服务器节点    {'name': 'node_cloud', 'category': '服务器'}
    ## 所有子任务       {'name': 'task1', 'category': '子任务'}
    ## 关系            {'source':'node_cloud', 'target' : 'task1', 'name':''}
    # data = []
    # data = [{'name': 'node_cloud', 'category': '服务器'}, {'name': 'node_edge', 'category': '服务器'}, {'name': 'task1', 'category': '子任务'}]
    # link = [{'source':'node_cloud', 'target' : 'task1', 'name':'offloading'}]
    data = {'data':data, 'link':link}
    # return render(request, 'node_info/system_info.html', {"attack_method": attack_method, 'sys': parser_data})
    from django.http import JsonResponse
    return JsonResponse({'data': data})


# 判断xml文件是否为空
def xml_to_data(file_path):
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        if len(root) == 0:
            is_empty = True
        else:
            is_empty = False
    except ET.ParseError:
        is_empty = True
    if is_empty:
        return ''
    else:
        return XMLParser().parse(file_path)


def modify_keys(d):
    """
    递归地修改字典的键名。
    如果键名的第一个字符是 '@'，则去掉它。
    """
    if not isinstance(d, dict):
        return d

    modified_dict = {}
    for k, v in d.items():
        new_key = k.lstrip('@')  # 去掉键名开头的 '@' 字符
        if isinstance(v, dict):
            # 如果值是另一个字典，则递归地修改它
            modified_dict[new_key] = modify_keys(v)
        elif isinstance(v, list):
            # 如果值是列表，则递归地处理列表中的每个元素（假设元素也是字典）
            modified_list = []
            for item in v:
                if isinstance(item, dict):
                    modified_list.append(modify_keys(item))
                else:
                    modified_list.append(item)
            modified_dict[new_key] = modified_list
        else:
            # 对于非字典和非列表的值，直接存储
            modified_dict[new_key] = v

    return modified_dict
def xml_to_data2(file_path):
    # 读取 XML 文件的内容
    with open(file_path, 'r', encoding='utf-8') as xml_file:
        xml_content = xml_file.read()

    # 使用 xmltodict.parse() 解析 XML 内容
    parsed_dict = xmltodict.parse(xml_content)

    # 修改字典的键名
    modified_dict = modify_keys(parsed_dict)

    return modified_dict

# 连接mqtt
class ServerAgent():
    def __init__(
            self,
            keepalive: int,
            broker: str,
            clientID: str,
            port: int,
            topics: list = topics,
    ) -> object:
        self.client = None
        self.topics = topics
        self.keepalive = keepalive
        self.broker = broker
        self.port = port
        self.clientID = clientID

    def connect_mqtt(
            self,
    ):
        '''连接mqtt代理服务器'''
        def on_connect(client, userdata, flags, rc):
            '''连接回调函数'''
            # 响应状态码为0表示连接成功
            if rc == 0:
                print(self.clientID, "Connected to MQTT OK!")
            else:
                print("Failed to connect, return code %d\n", rc)

        # 连接mqtt代理服务器，并获取连接引用
        self.client = mqtt_client.Client(self.clientID)
        self.client.on_connect = on_connect
        self.client.connect(self.broker, self.port, self.keepalive)

    def subscribe(
            self,
    ):
        '''订阅主题并接收消息'''
        def on_message(client, userdata, msg):
            print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
            topic = msg.topic
            if topic == 'mqtt/server/start':
                # 启动节点，开启mqtt的发送模式，开始发送设备的信息
                pass
            elif topic == 'mqtt/server/stop':
                # 停止节点，停止发送设备的信息，只接受信息
                pass
            elif topic == 'mqtt/server/delete':
                # 删除节点
                pass

            '''订阅消息回调函数'''

        # 订阅指定消息主题
        for topic in self.virtual_topics:
            self.client.subscribe(topic)
            # print(topic)
        for topic in self.server_topics:
            self.client.subscribe(topic)
        self.client.on_message = on_message

    def disconnect_mqtt(self):
        '''关闭mqtt连接'''
        self.client.disconnect()
        print("Disconnected from MQTT")

    def run(
            self,
            topic,
            msg,
    ):
        # 连接mqtt
        self.connect_mqtt()
        # 运行一个线程来自动调用loop()处理网络事件, 非阻塞
        self.client.loop_start()
        """ 负责发布指定消息到对应的topic """
        result = self.client.publish(topic, msg)
        status = result[0]
        if status == 0:
            print(f"Send `{msg}` to topic `{topic}`")
        else:
            print(f"Failed to send message to topic {topic}")
        # 断开连接
        self.disconnect_mqtt()
