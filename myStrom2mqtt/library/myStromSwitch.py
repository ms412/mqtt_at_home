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


__app__ = "myStrom Switch"
__VERSION__ = "0.7"
__DATE__ = "19.07.2017"
__author__ = "Markus Schiesser"
__contact__ = "M.Schiesser@gmail.com"
__copyright__ = "Copyright (C) 2017 Markus Schiesser"
__license__ = 'GPL v3'


import requests
import time
import json
from threading import Thread

class switch(object):
    def __init__(self,config,log):

        self._config = config
        self._log = log
        self._url= 'http://'+ self._config.get('IP',None)
        self._switch = 0
        self._state = ''
        self._power = 0.0
        self._energy = 0.0
        self._t0 = time.time()

    def __del__(self):
        _msg = 'Kill myself' + __app__ + 'switch object'
        self._log.error(_msg)

    def _status(self):
    #    info ="""{"power":0.0,"relay": false}"""
     #   result = json.loads(info)
        _state = 'OK'

        try:
            r = requests.get(self._url + '/report',timeout = 5)
#            print(r.text)
            msg = 'Get Status' + str(self._url) + str(r.json())
            self._log.debug(msg)
            _state = 'OK'

            return (_state,r.json())
        except requests.Timeout:
            msg = 'TIMEOUT' + str(self._url)
            self._log.error(msg)
            _state = 'TIMEOUT'
           # print('TIMEOUT')
        except requests.exceptions.ConnectionError:
            msg = 'CONNECTION Error' + str(self._url)
            self._log.error(msg)
            _state = 'CONNECTION ERROR'
          #  print('CONNECTION Error')
        #    print('state',_state)
        return (_state,json.loads("""{"power":0.0,"relay": false}"""))

    def getStatus(self):
        _result = 0
        _state, _value = self._status()
      #  print('status',_state, _value)
        if 'OK' in _state:
            self._switch = _value['relay']
            self._power = float(_value['power'])
            _t1 = time.time() - self._t0
          #  self._t0 = time.time()
          #  print(_t1,self._power)
            self._energy = self._power * _t1 / 3600 / 1000
        else:
 #           print('STATE2',_state)
            self._state = _state

        return _result

    def getPower(self):
        return self._power

    def getEnergy(self):
        return self._energy

    def getSwitch(self):
      #  print('switch', self._switch)
        _result = 'UNKOWN'

        if self._switch:
            _result = 'ON'
        else:
            _result = 'OFF'
        return _result


    def getState(self):
        return self._state

    def setSwitch(self,state):
        if not 'LOCK' == self._config.get('SWITCH','UNLOCK').upper():
 #           print('switch is not in lock mode')
            msg = 'Set Status' + str(self._url) + str(state)
            self._log.debug(msg)

            if 'ON'in state:
                _url = self._url + '/relay?state=1'
            else:
                _url = self._url + '/relay?state=0'
           # print('requests',_url)
            try:
                requests.get(_url,timeout=5)
            except requests.Timeout:
     #           print('TIMEOUT')
                msg = 'TIMEOUT cannot set state' + str(self._url) + str(state)
                self._log.error(msg)
            except requests.exceptions.ConnectionError:
                msg = 'CONNECTION Error' + str(self._url)
                self._log.error(msg)

          #  r = requests.get(self._url + '/report', timeout=5)
        else:
           # print('switch is in lock mode no change')
            msg = 'Node in LOCK mode cannot write to Node' + str(self._url) + str(state)
            self._log.warning(msg)
       # print('test0',r.json())
        return True



class switchwrapper(Thread):
    def __init__(self,config,broker,loghandle):
        Thread.__init__(self)

       # print('switchwrapper',config)

        self._broker = broker
        self._config = config
        self._log = loghandle

        msg = 'Start ' + __app__ +' ' +  __VERSION__ + ' ' +  __DATE__
        self._log.info(msg)

        msg = 'Configuration' + str(config)
        self._log.debug(msg)

        self._processId = {}

        self.config()

    def __del__(self):
        _msg = 'Kill myself' + __app__ +'switchwrapper'
        self._log.error(_msg)

    def config(self):

        for key,item in self._config.items():
        #    print('print',key,item.get('IP', None),item.get('MAC',None))
            self._processId[key] = switch(item,self._log)

#            print(self._processId[key].getStatus())

            #subscribe callback of mqtt
            _key = str(key + '/SWITCH')
            self._broker.callback(_key,self.msg_snk)

            msg = 'Create Switch Object and connect to a Broker Channel: ' + str(_key)
            self._log.debug(msg)

        return

    def msg_snk(self,mqttc, obj,payload):
       # print('received from mqtt',obj,msg.topic,msg.payload)
        _topic_split = payload.topic.split('/')
        _key_topic = _topic_split[-1]
        if 'SWITCH' == _key_topic:
            _msg = 'Received SWITCH command from Broker'
            self._log.debug(_msg)
            self.cmd_switch(payload.topic, payload.payload)
        else:
         #   print('command not found:',_key_topic)
            _msg = 'Received UNKNOWN command from Broker' + str(_key_topic)
            self._log.error(_msg)

        return True

    def cmd_switch(self,topic,payload):
        _topic_split = topic.split('/')
        _key_topic = _topic_split[-2]
       # print('_topic_key', _key_topic)
        for key,item in self._processId.items():
            if key in _key_topic:
               # print(key,_key_topic,payload)
                msg = 'Command: ' + str(payload) + 'for Item: ' + str(_key_topic)
                self._log.info(msg)
                self._processId[key].setSwitch(str(payload))
              #  self._processId[key].getStatus()
                self.update(key,self._processId[key])

    def update(self,topic,obj):
        obj.getStatus()
        _msg = {}
     #   _topic = str(topic + '/SWITCH')
      #  self._broker.publish(_topic, obj.getSwitch())

       # _topic = str(topic + '/POWER')
       # self._broker.publish(_topic, obj.getPower())

        #_topic = str(topic + '/ENERGY')
        #self._broker.publish(_topic, obj.getEnergy())

        _msg['SWITCH'] = obj.getSwitch()
        _msg['POWER'] = obj.getPower()
        _msg['ENERGY'] = obj.getEnergy()
        _msg['DATE'] = time.time()
        _msg['STATE'] = obj.getState()

        _topic = str(topic + '/STATUS')
        self._broker.publish(_topic, json.dumps(_msg, ensure_ascii=False))


        return True

    def run(self):
       # print('START Thread Switch')
        msg = __app__ + 'start broker as thread'
        self._log.debug(msg)
#
        while(True):
          #  print('test')
            for key,item in self._processId.items():
                self.update(key,item)
                time.sleep(15)

        return

