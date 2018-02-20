#!/usr/bin/env python3
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


__app__ = "myStrom Bulb"
__VERSION__ = "0.4"
__DATE__ = "19.07.2017"
__author__ = "Markus Schiesser"
__contact__ = "M.Schiesser@gmail.com"
__copyright__ = "Copyright (C) 2017 Markus Schiesser"
__license__ = 'GPL v3'


import requests
import time
import json
from threading import Thread


class bulb(object):
    def __init__(self,ip,mac,log):
       # self._ip = ip
      # self._mac = mac
        self._log = log
        print('bulb class',ip, mac)
        self._url = 'http://'+ ip +'/api/v1/device/'+ mac

        self._payload = {'action': 'on'}

    def post(self,payload):
        r = requests.post(self._url,data=payload)
        print(r.text)

    def switch(self,value):
        payload = {'action': value}
        print(payload)
        self.post(payload)


    def color(self,white = None,red = None,green = None,blue = None):
        _w_mask = 0xFF000000
        _r_mask = 0x00FF0000
        _g_mask = 0x0000FF00
        _b_mask = 0x000000FF

        self.mode('rgb')
        status = self.status()
        for each in status:
            color = int(status[each]['color'],16)
            print('current color',hex(color))

        if not white:
            white = (color & _w_mask) >> 24

        if not red:
            red = (color & _r_mask)  >> 16

        if not green:
            green = (color & _g_mask) >> 8

        if not blue:
            blue = (color & _b_mask) >> 0

        print('color',hex(white),hex(red),hex(green),hex(blue))

        _new_c = (color & ~(_w_mask) |(white << 24))
        _new_c = (_new_c & ~(_r_mask) |(red << 16))
        _new_c = (_new_c & ~(_g_mask) |(green << 8))
        _new_c = (_new_c & ~(_b_mask) |(blue << 0))

      #  print('new color', '{:02x}'.format(_new_c))
        payload = {'color':  '{:02x}'.format(_new_c)}
        print(payload)
        self.post(payload)


    def status(self):
        r = requests.get(self._url)
        print(r.text)
        return r.json()

    def mode(self,mode):
        payload = {'mode': mode}
        self.post(payload)

    def on_status(self,mode):
        status = self.status()
        for each in status:
            on_status = bool(status[each]['on'])
            #print('current color',power)

        return on_status

    def power(self):
        status = self.status()
        for each in status:
            power = int(status[each]['power'])
            print('current color',power)

        return power

    def dimmer(self,value):
        payload = {'ramp': (value*1000)}
        print(payload)
        self.post(payload)

    def rampUp(self,timeout,start=0,end=100):

        step = end - start
        steps = timeout / step
        print(step,steps)

        count = 0
        while count < step:
            self.dimmer(count)
            count = count + 1
            time.sleep(steps)


class bulbwrapper(Thread):
    def __init__(self, config, broker, loghandle):
        Thread.__init__(self)

        print('bulbwrapper', config)

        self._broker = broker
        self._config = config
        self._log = loghandle

        msg = 'Start ' + __app__ + ' ' + __VERSION__ + ' ' + __DATE__
        self._log.info(msg)

        msg = 'Configuration' + str(config)
        self._log.debug(msg)

        self._processId = {}

        self.config()

    def config(self):

        for key, item in self._config.items():
            #    print('print',key,item.get('IP', None),item.get('MAC',None))
            self._processId[key] = bulb(item, self._log)

            #            print(self._processId[key].getStatus())

            # subscribe callback of mqtt
            _key = str(key + '/BULB')
            self._broker.callback(_key, self.msg_snk)

            msg = 'Create Switch Object and connect to a Broker Channel: ' + str(_key)
            self._log.debug(msg)

        return

        def msg_snk(self, mqttc, obj, msg):
            # print('received from mqtt',obj,msg.topic,msg.payload)
            _topic_split = msg.topic.split('/')
            _key_topic = _topic_split[-1]
            if 'SWITCH' == _key_topic:
                self.cmd_switch(msg.topic, msg.payload)
                msg = 'Received SWITCH command from Broker'
                self._log.debug(msg)
            else:
                #   print('command not found:',_key_topic)
                msg = 'Received UNKNOWN command from Broker' + str(_key_topic)
                self._log.error(msg)

            return True

        def cmd_switch(self, topic, payload):
            _topic_split = topic.split('/')
            _key_topic = _topic_split[-2]
            # print('_topic_key', _key_topic)
            for key, item in self._processId.items():
                if key in _key_topic:
                    # print(key,_key_topic,payload)
                    msg = 'Command: ' + str(payload) + 'for Item: ' + str(_key_topic)
                    self._processId[key].setSwitch(str(payload))
                    self._processId[key].getStatus()
                    self.update(key, self._processId[key])

        def update(self, topic, obj):
            obj.getStatus()
            _topic = str(topic + '/SWITCH')
            self._broker.publish(_topic, obj.getSwitch())

            _topic = str(topic + '/POWER')
            self._broker.publish(_topic, obj.getPower())

            return True

        def run(self):
            # print('START Thread Switch')
            msg = __app__ + 'start broker as thread'
            self._log.debug(msg)
            #
            while (True):
                #  print('test')
                for key, item in self._processId.items():
                    self.update(key, item)
                    time.sleep(5)

            return




    def __init__(self,config,broker,loghandle):
        Thread.__init__(self)

        print('bulbwrappter',config)

        self._broker = broker
        self._config = config
        self._log = loghandle

        self._processId = {}

        self.start()

    def start(self):

        for key,item in self._config.items():
        #    print('print',key,item.get('IP', None),item.get('MAC',None))
            self._processId[key] = bulb(item.get('IP', None),item.get('MAC',None))

 #       print('processId',self._processId)
#        self._broker.publish('test','123')

    def update(self,channel,msg):

        return

    def run(self):

        while(True):
            print('test')
            for key,item in self._processId.items():
                # read power status
               # if item.on_status:
                #publish ligh status On/Off
                self._broker.publish(key,item.on_status)
                #publish power consumption
                self._broker.publish(key,item.power())



if __name__ == '__main__':
    print('main')
    b = bulb('192.168.2.112','5CCF7FA0B919')
    b.test_1(red=0xff, green=0xEE)
    b.switch('on')
    b.status()
    b.color(red = 255, white = 255)
    #b.switch('on')

    b.status()
    time.sleep(15)
    b.switch('off')


