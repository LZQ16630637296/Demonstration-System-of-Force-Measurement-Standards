import argparse
import time

from paho.mqtt import client as mqtt_client


parser = argparse.ArgumentParser(description='')
parser.add_argument('--broker', type=str, default='127.0.0.1')
parser.add_argument('--port', type=int, default=1883)
parser.add_argument('--keepalive', type=int, default=60)
parser.add_argument('--timeslot', type=int, default=4)
parser.add_argument('--clientID', type=str, default='rec')
args = parser.parse_known_args()[0]
brokerIP = args.broker
port = args.port
keepalive = args.keepalive
clientID = args.clientID
timeslot = args.timeslot
print(args)

topics = []
python_interpreter_path = "C:\\Work\\边缘计算\\Edge-IMDE\\venv\\Scripts\\python.exe"

# 连接mqtt
class ServerAgent():
    def __init__(
            self,
            keepalive: int,
            broker: str,
            clientID: str,
            port: int,
            topics: list = [
                'mqtt/system/FLOPS',
            ],
            task_ctl: list = [
                'mqtt/task/class'
            ],
    ) -> object:
        self.client = None
        self.topics = topics
        self.ctl = task_ctl
        self.keepalive = keepalive
        self.broker = broker
        self.port = port
        self.clientID = clientID
        self.msg = {}
        self.task_list = []

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

    def publish(
            self,
    ):
        '''发布消息'''
        time.sleep(timeslot)
        while True:
            tc = input('输入任务类型 : ')
            """ TODO- 发一个任务 """
            self.msg = tc
            # print(type(self.msg))
            topic = self.ctl[0]
            result = self.client.publish(topic, self.msg)
            status = result[0]
            if status == 0:
                print(f"Send `{self.msg}` to topic `{topic}`")
            else:
                print(f"Failed to send message to topic {topic}")

    def subscribe(
            self,
    ):
        '''订阅主题并接收消息'''

        def on_message(client, userdata, msg):
            # print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
            topic = msg.topic
            """ TODO  REALITY  INFO  CALLBACK 
            elif topic == 'NEW':
                具体处理逻辑
                pass
            ....
            """
            if topic == 'mqtt/subtask/model/operand':
                pass
            elif topic == 'NEW':
                pass
            # print('tmpmsg',tmpmsg)

        # 订阅指定消息主题
        for topic in self.topics:
            self.client.subscribe(topic)
            # print(topic)
        self.client.on_message = on_message

    def run(
            self,
    ):
        '''运行'''
        self.connect_mqtt()
        """ 接受各种检测信息 """
        self.subscribe()
        # 运行一个线程来自动调用loop()处理网络事件, 非阻塞
        # self.client.loop_start()
        self.client.loop_forever()
        # self.publish()


if __name__ == '__main__':
    server = ServerAgent(
        keepalive=keepalive,
        broker=brokerIP,
        port=port,
        clientID=clientID,
        topics=topics,
    )

    server.run()