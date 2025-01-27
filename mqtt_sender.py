from paho.mqtt import client as mqtt


class MqttSender:   
    def __init__(self,broker,port, user=None, password=None):
        self.client = mqtt.Client()
        self.broker = broker
        self.port = port
        if user and password:
            self.client.username_pw_set(user, password)

    def connect(self):
        try:
            self.client.connect(self.broker, self.port)
            print(f"Connected to MQTT broker:{self.broker} by port:{self.port}")
        except Exception:
            print(f"Connection failed due to {Exception} error")
    
    def publish(self, topic, message):
        try:
            self.client.publish(topic, message)
            print(f"Message:{message} published under the topic: {topic}")
        except Exception:
            print(f"Publishing failed due to {Exception} error")

    def subscribe(self, topic, callback):
        try:
            self.client.subscribe(topic)
            self.client.on_message = callback
            print(f"Subscribed to topic: {topic}")
        except Exception:
            print(f"Failed due to error: {Exception}")

    def sub_loop(self):
        try:
            self.client.loop_start()
        except Exception as e:
            print(f"Error in loop: {e}")
