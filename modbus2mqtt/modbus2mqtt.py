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


__app__ = "Modbus2mqtt Adapter"
__VERSION__ = "0.95"
__DATE__ = "19.02.2018"
__author__ = "Markus Schiesser"
__contact__ = "M.Schiesser@gmail.com"
__copyright__ = "Copyright (C) 2017 Markus Schiesser"
__license__ = 'GPL v3'

import os
import sys
import time
from configobj import ConfigObj

#sys.path.append('C:/Users/tgdscm41/PycharmProjects/mqtt@home')

#from library.ds18b20 import ds18b20
#from library.devicereader import devicereader
#from library.configfile import configfile
from library.mqttclient import mqttclient
#from library.logging import logger
from library.loghandler import loghandler
from library.mgr_modbus import mgr_modbus


class manager(object):
    def __init__(self,configfile='./modbus2mqtt.cfg'):
       # self._log = loghandler('ONEWIRE')
        self._configfile = configfile

        self._mqttclient = None

        self._cfg_log = None
        self._cfg_mqtt = None
        self._cfg_modbus = None
        self._cfg_device = None


    def __del__(self):
        _msg = 'Kill myself' + __app__
        self._log.error(_msg)

    def readConfig(self):
        _config = ConfigObj(self._configfile)

        if bool(_config) is False:
            print('ERROR config file not found',self._configfile)
            sys.exit()

        _config = ConfigObj(self._configfile)
        print(_config)
        self._cfg_log = _config.get('LOGGING',None)
        self._cfg_mqtt = _config.get('BROKER',None)
        self._cfg_modbus = _config.get('MODBUS',None)
        self._cfg_device = _config.get('DEVICE',None)
      #  print(self._logcfg)
        return True

    def startLogger(self):
        self._log = loghandler('MODBUS')
        self._log.handle(self._cfg_log.get('LOGMODE'),self._cfg_log)
        self._log.level(self._cfg_log.get('LOGLEVEL', 'DEBUG'))
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


    def readModbus(self):
        _resultList = {}
        for devicename,item in self._cfg_device.items():
           # print(key,item['CONFIG']['MODBUSID'])
            print(devicename)
#            item = dict(item)
 #           print('item',item,type(item),item.get('CONFIG'),item['CONFIG']['MODBUSID'])

            self._cfg_modbus['DEVICEID']=item['CONFIG']['MODBUSID']
            self._mgr = mgr_modbus(self._cfg_modbus)
            self._mgr.setup()
           # _channel = item.get('PUBLISH','/OPENAHB/AC')
        #    print(item)
            _result = {}
            for key,item in item['CALLS'].items():
                print('data',key, item)
             #   value =0
                value = self._mgr.read(item)
               # value  = 0
                if value is not None:
                    _result[key]= value

            print('Result',_result,devicename)
            self.publishData(devicename,_result)
            _resultList[devicename]=_result
        print(_resultList)
        return _resultList

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

    def stopMqttClient(self):
        self._log.debug('Disconnect from Mqtt Server')
        self._mqttclient.disconnect()

   # def publishData(self,channel,data):
    #    mqttc = mqttpush(self._mqttbroker)
     #   main_channel = self._mqttbroker.get('PUBLISH','/OPENHAB')

      #  for item, measurement in data.items():
       #     _channel = main_channel + '/' + channel + '/' + item
        #    self._log.debug('channel: %s, mesage %s'% (_channel,measurement))
         #   mqttc.publish(_channel,measurement)

       # return True

    def run(self):
#        self.startSystem()
        self.readConfig()
        self.startLogger()

        self._log.info('Startup, %s %s %s'% ( __app__, __VERSION__, __DATE__) )

        self.startMqttClient()
        _data = self.readModbus()
        self.publishData(_data)
        time.sleep(5)
        self.stopMqttClient()
       # self.publishData(data)


if __name__ == '__main__':

    if len(sys.argv) == 2:
        configfile = sys.argv[1]
    else:
        configfile ='./modbus2mqtt.cfg'

    mgr_handle = manager(configfile)
    mgr_handle.run()

