import os

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
            os.system('start /B python rec\\rec.py')
            process = max(psutil.process_iter(['pid', 'name']), key=lambda x: x.create_time())
            node, created = Node.objects.get_or_create(name='rec', IPaddress='127.0.0.1', port=18083, keepalive=60, pid=process.pid) #
            node.save()
            # os.system('start /B python task\\taskAgent.py')
            # print(created)
            # print("已启动rec")
        nodes = Node.objects.all()
        for node in nodes:
            if not check_pid_exists(node.pid):
                node.status = 0
                node.save()
        return context


def check_pid_exists(pid):
    if pid == -1:
        return False
    try:
        process = psutil.Process(pid)
        return process.is_running()
    except psutil.NoSuchProcess:
        return False


class NodeCreate(CreateView):
    form_class = NodeCreateForm
    model = Node
    template_name = 'node_info/node_create1.html'
    success_url = reverse_lazy('node_info:node_list')


#    def get_context_data(self, **kwargs):
#        context =

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
    f.close()
    # s = io.StringIO(response.text)
    parser_data = xml_to_data('node_info/templates/node_info/system_info.xml')
    # print(parser_data)
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
    f = open('node_info/templates/node_info/res_info.xml', 'r', encoding='utf-8')
    attack_method = f.read()
    ## TODO 用xml方式读取内容， 并且组织成合适的结构传入html模板中
    attack_method = attack_method.split('\n')
    # attack_method = list(dict.fromkeys(attack_method))  ## 这里是去重
    f.close()
    f = open('node_info/templates/node_info/res_info.xml', 'r', encoding='utf-8')
    tmp = f.read()
    f.close()
    # s = io.StringIO(response.text)
    parser_data = xml_to_data('node_info/templates/node_info/res_info.xml')
    # print(parser_data)
    return render(request, 'node_info/base_info.html', {"attack_method": attack_method, 'sys': parser_data})

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
    exists = check_pid_exists(node.pid)
    if not exists:
        pattern = r"edge\d+"
        import re
        if re.match(pattern, name):
            suffix = name[-1]
            # suffix = int(suffix) + 1
            os.system('start /B python server-new-ver1.1\\serverAgent_edge.py --clientID ' + name + ' --url ' + \
                      suffix + '@edge --ID e' + suffix)
        else:
            os.system('start /B python server-new-ver1.1\\serverAgent.py --clientID ' + name)
        # 保存子进程的PID
        process = max(psutil.process_iter(['pid', 'name']), key=lambda x: x.create_time())
        node, created = Node.objects.get_or_create(name=name)
        # print('pid', process.pid)
        node.pid = process.pid
        node.status = 1
        node.save()
        print('启动pid:', process.pid)
        messages.error(request, '节点启动成功')
        return HttpResponseRedirect(reverse('node_info:node_list'))
        # return HttpResponse("节点启动成功")
    else:
        messages.error(request, '节点正在运行')
        return HttpResponseRedirect(reverse('node_info:node_list'))
        # return HttpResponse("节点正在运行")


def ServerStop(request, *args, **kwargs):
    name = request.POST.get('button_name')
    node = Node.objects.get(name=name)
    node.status = 0
    node.save()
    exists = check_pid_exists(node.pid)
    if exists:
        # 停止进程rec和node
        rec_node = Node.objects.get(name='rec')
        # print("停止PID:", node.pid)
        os.system('taskkill /pid ' + str(node.pid) + ' /f /t')
        os.system('taskkill /pid ' + str(rec_node.pid) + ' /f /t')
        os.system('start /B python rec\\rec.py')
        process = max(psutil.process_iter(['pid', 'name']), key=lambda x: x.create_time())
        rec_node.pid = process.pid
        rec_node.status = 1
        rec_node.save()
        # return HttpResponse("节点停止成功")
        messages.error(request, '节点停止成功')
        return HttpResponseRedirect(reverse('node_info:node_list'))
    else:
        # return HttpResponse("节点未运行")
        messages.error(request, '节点未运行')
        return HttpResponseRedirect(reverse('node_info:node_list'))

def ServerDelete(request):
    name = request.POST.get('button_name')
    node = Node.objects.get(name=name)
    exists = check_pid_exists(node.pid)
    if exists:
        rec_node = Node.objects.get(name='rec')
        # print("停止PID:", node.pid)
        os.system('taskkill /pid ' + str(node.pid) + ' /f /t')
        os.system('taskkill /pid ' + str(rec_node.pid) + ' /f /t')
        os.system('start /B python rec\\rec.py')
        process = max(psutil.process_iter(['pid', 'name']), key=lambda x: x.create_time())
        node, created = Node.objects.get_or_create(name='rec')
        node.pid = process.pid
        node.save()
    Node.objects.filter(name=name).delete()
    # return redirect("http://127.0.0.1:8000")
    return HttpResponseRedirect(reverse('node_info:node_list'))

@csrf_exempt
def SysStatusFile1(request, *args, **kwargs):
    parser_data = xml_to_data('node_info/templates/node_info/system_info.xml')
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
        os.system('start /B python task\\taskAgent.py')
        # 保存子进程的PID
        process = max(psutil.process_iter(['pid', 'name']), key=lambda x: x.create_time())
        node, created = Node.objects.get_or_create(name=name)
        # print('pid', process.pid)
        node.pid = process.pid
        node.status = 1
        node.save()
        print('启动pid:', process.pid)
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
    exists = check_pid_exists(node.pid)
    if exists:
        # 停止进程rec和node
        rec_node = Node.objects.get(name='rec')
        # print("停止PID:", node.pid)
        os.system('taskkill /pid ' + str(node.pid) + ' /f /t')
        os.system('taskkill /pid ' + str(rec_node.pid) + ' /f /t')
        os.system('start /B python rec\\rec.py')
        process = max(psutil.process_iter(['pid', 'name']), key=lambda x: x.create_time())
        node, created = Node.objects.get_or_create(name='rec')
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

