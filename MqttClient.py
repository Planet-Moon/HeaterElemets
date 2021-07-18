import paho.mqtt.client as mqtt

class MqttClient:
    def __init__(self, ipAddress, port=1883):
        self._client = mqtt.Client()
        self._ipAddress = ipAddress
        self._port = port
        self._client.connect_async(self._ipAddress, self._port)
        self._client.loop_start()
        self.topic_prefix = ""

    def publish(self,payload,topic="",qos=0,retain=False):
        _topic = self.topic_prefix
        if topic:
            _topic += "/"+topic
        return self._client.publish(_topic, payload, qos, retain)
