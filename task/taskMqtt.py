from paho.mqtt import client as mqtt_client

class MqttAgent():
    def __init__(
            self,
            keepalive: int,
            broker: str,
            clientID: str,
            port: int,
            topics: list,
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