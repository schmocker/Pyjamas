from core.util import Input, Output, Property
from core.supermodel import Supermodel
import paho.mqtt.client as mqtt
import json


class Model(Supermodel):
    def __init__(self, uuid, name: str):
        super(Model, self).__init__(uuid, name)

        self.inputs['data'] = Input(name='Data', unit='any', info='Data to be published must be convertible to json')

        self.properties['host'] = Property('iot.eclipse.org', str, name='Broker Address', unit='-', info='string')
        self.properties['port'] = Property(1883, int, name='Broker Port', unit='-', info='int, usually 1883 for MQTT')
        self.properties['topic'] = Property('pyjamas', str, name='Topic', unit='-', info='string')

        self.client = None
        self.host = None
        self.port = None
        self.topic = None
        self.keepalive = 60

    async def func_birth(self):
        self.client = mqtt.Client()
        self.host = self.get_property('host')
        self.port = self.get_property('port')
        try:
            self.port = int(self.port)
        except Exception as e:
            print(f"MQTT: could parse port to int {self.port}, set to defailt 1883 ({e})")
            self.port = 1883
        self.topic = self.get_property('topic')

        await self.reconnect()




    async def func_amend(self, keys=[]):
        print('amend')
        if 'host' in keys or 'port' in keys:
            self.host = self.get_property('host')
            self.port = self.get_property('port')
            try:
                self.port = int(self.port)
            except Exception as e:
                print(f"MQTT: could parse port to int {self.port}, set to defailt 1883 ({e})")
                self.port = 1883
            await self.reconnect()

        if 'topic' in keys:
            self.topic = self.get_property('topic')

    async def func_peri(self, prep_to_peri=None):
        try:
            data = await self.get_input("data")
            data = json.dumps(data)
            self.client.publish(self.topic, data)
        except Exception as e:
            print(f"MQTT: could not sent data to {self.host}:{self.port}/{self.topic} ({e})")

    async def func_death(self):
        self.client.disconnect()

    async def reconnect(self):

        try:
            self.client.loop_stop()
            self.client.disconnect()
            self.client.connect(self.host, self.port, self.keepalive)
            self.client.loop_start()
        except Exception as e:
            print(f"MQTT: could not connect to {self.host}:{self.port} ({e})")


if __name__=='__main__':
    inputs = {
        'data': 1
    }

    properties = {
        'host': '147.86.10.49',
        'port': 50100,
        'topic': 'pyjamas/values'
    }

    outputs = Model.test(inputs, properties)

    print(outputs)
