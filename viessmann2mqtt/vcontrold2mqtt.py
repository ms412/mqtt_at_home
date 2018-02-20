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


__app__ = "vcontrold2mqtt Adapter"
__VERSION__ = "0.8"
__DATE__ = "20.02.2018"
__author__ = "Markus Schiesser"
__contact__ = "M.Schiesser@gmail.com"
__copyright__ = "Copyright (C) 2017 Markus Schiesser"
__license__ = 'GPL v3'


import sys
import time
import json
import paho.mqtt.client as mqtt
from configobj import ConfigObj
from library.logger import logger
from library.vcontrold import vcontrold


class manager(object):

    def __init__(self,configfile='vcontrold2mqtt.cfg'):

        self._configfile = configfile

        self._cfg_broker = None
        self._cfg_log = None
        self._cfg_vclient = None
        self._cfg_commands = None

        self._mqttc = None
        self._vclient = None

        self._state = 'NOTCONNECTED'

        self._result ={}

    def readConfig(self):
      #  print(self._cfg_file)
        _cfg = ConfigObj(self._configfile)

        self._cfg_broker = _cfg.get('BROKER',None)
        self._cfg_log = _cfg.get('LOGGING',None)
        self._cfg_vcontrold = _cfg.get('VCONTROLD',None)
        self._cfg_commands = _cfg.get('COMMANDS',None)
       # print(self._cfg_commands)
        return True

    def startLogger(self):
        self._log = logger('VCONTROL2MQTT')
        self._log.handle(self._cfg_log.get('LOGMODE'),self._cfg_log)
        self._log.level(self._cfg_log.get('LOGLEVEL','DEBUG'))
        return True

    def startMqttClient(self):
        self._log.debug('Connect from Mqtt Server')
        self._mqttclient = mqttclient(self._cfg_mqtt)
        self._mqttclient.connect()
        _counter = 0
        while not self._mqttclient.is_connected():
            time.sleep(2)
            _counter = _counter + 1
            if _counter > 5:
                self._log.error('Cannot connect to Broker')
                sys.exit()

    def readVcontrold(self):
        print('read')
        self._vcontrold = vcontrold(self._cfg_vcontrold, self._log)
        self._vcontrold.connect()

        for item in self._cfg_commands.get('COMMANDLIST'):
            value = self._vcontrold._read(item)

            self._result[item]=str(value)
            print('TEST', item,value)
            self._log.debug('Read from Heating: %s , %s'% (item,str(value)))

            #self.mqttPublish(item,str(value))

    def publishData(self,data):
        for key,item in data.items():
            self._mqttclient.publish(key,item)
            _timeout = 0
            try:
                while not self._mqttclient.is_published():
                    time.sleep(2)
                    _timeout = _timeout + 1
                    if _timeout > 5:
                        raise TimeoutError
            except TimeoutError:
                self._log.error('Cannot publish Data - Timeout - %s %s '%(key,item))
                pass

        return True

    def OldpublishData(self):
        self._host = str(self._cfg_broker.get('HOST', 'localhost'))
        self._port = int(self._cfg_broker.get('PORT', 1883))
        self._publish = str(self._cfg_broker.get('PUBLISH', '/PUBLISH'))
        self._mqttc = mqtt.Client()

        self._mqttc.connect(self._host,self._port,60)
        for key,value in self._result.items():
            _topic = str(self._publish + '/' + key)

    #    print(_topic)
            print('Publish:', _topic, value)
            self._log.debug('Publish: %s , %s'% ( _topic, str(value)))
            self._mqttc.publish(_topic, value)
        # print('cc',channel,msg)
        self._mqttc.loop(2)
        self._mqttc.disconnect()
        return True

    def stopMqttClient(self):
        self._log.debug('Disconnect from Mqtt Server')
        self._mqttclient.disconnect()
        return True

    def run(self):
        """
        Entry point, initiates components and loops forever...
        """
        self.readConfig()
     #  print('ooo')
        self.startLogger()
      #  print('loger')
        # Log information
        msg = 'Start ' + __app__ +' ' +  __VERSION__ + ' ' +  __DATE__
        self._log.info(msg)

        self.startMqttClient()
        self.readVcontrold()
        self.mqttPublish()
        time.sleep(5)
        self.stopMqttClient()




if __name__ == "__main__":

    if len(sys.argv) == 2:
        configfile = sys.argv[1]
    else:
        configfile = './vcontrold2mqtt.cfg'

    mgr_handle = manager(configfile)
    mgr_handle.run()
