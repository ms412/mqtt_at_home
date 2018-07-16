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


__app__ = "serial2mqtt Adapter"
__VERSION__ = "0.95"
__DATE__ = "16.07.2018"
__author__ = "Markus Schiesser"
__contact__ = "M.Schiesser@gmail.com"
__copyright__ = "Copyright (C) 2018 Markus Schiesser"
__license__ = 'GPL v3'

from configobj import ConfigObj
#from library.sr04 import sr04
import paho.mqtt.client as mqtt
import os
import time
import sys
import serial
#import io
#from library.configfile import configfile
#from library.mqttpush import mqttpush
from library.loghandler import loghandler


class manager(object):

    def __init__(self,configfile='ultrasonic2mqtt.cfg'):
        self._configfile = configfile

        self._general = None
        self._mqttbroker = None
        self._ultrasonic = None

        self._msg = {}

    def readConfig(self):
     #   _cfg = configfile(self._configfile)
      #  _config = _cfg.openfile()
        _config = ConfigObj(self._configfile)
        self._logcfg = _config.get('LOGGING',None)
        self._mqttCfg = _config.get('BROKER',None)
        self._serial = _config.get('SERIAL',None)
        return True

    def startLogger(self):
        print(self._logcfg)
        self._log = loghandler('SERIAL2MQTT')
        self._log.handle(self._logcfg.get('LOGMODE'),self._logcfg)
        return True

    def startMeasure(self):

        for k1,v1 in self._serial.items():
            port = v1.get('PORT','/dev/ttyUSB0')
            baudrate = v1.get('BAUDRATE',38400)
            port = serial.Serial(port, baudrate, timeout=3.0)
            self._log.debug('Serial Port configuration %s' % (port))
            port.flush()

            for k2,v2 in v1.items():
                if isinstance(v2,dict):

                    print('V2',k2,v2)
                    _preset = float(v2.get('PRESET'))
                    _item = int(v2.get('ITEM'))

                    number = port.write(b'$?\n')
                    time.sleep(1)
                    self._log.debug('Write %s bytes to Port %s' % (number, port.name))

                    _rcv = port.readline()
                    _str = _rcv.decode('ASCII')
                    _list = _str.split(';')

                    self._log.debug('Received data %s'%(_str))
                    _topic = k1 + '/' + k2
                    print('_topic',_topic,_list)
                    _value = float(_list[_item])

                    self._msg[_topic]= _value + _preset



        self._log.debug('Result %s' % (self._msg))

        return self._msg

    def mqttPublish(self,data):
        self._host = str(self._mqttCfg.get('HOST', 'localhost'))
        self._port = int(self._mqttCfg.get('PORT', 1883))
        main_channel = str(self._mqttCfg.get('PUBLISH', '/OPENHAB'))
        self._mqttc = mqtt.Client(str(os.getpid()), clean_session=True)
  
      #  self._mqttc = mqtt.Client()
        self._mqttc.connect(self._host,self._port,60)

        for deviceId, measurement in data.items():
            _topic = main_channel + '/' + deviceId
            self._mqttc.publish(_topic, measurement)
            print('cc',_topic, measurement)
            self._mqttc.loop(2)


        self._mqttc.disconnect()



        return True

    def publishData(self,data):
        mqttc = mqttpush(self._mqttbroker)
        main_channel = self._mqttbroker.get('PUBLISH','/OPENHAB')

        for deviceId, measurement in data.items():
            channel = main_channel + '/' + deviceId
          #  print('channel',channel,deviceId)
            mqttc.publish(channel,measurement)

        return True

    def run(self):
        self.readConfig()
        self.startLogger()
        self._log.info('Startup, %s %s %s' % (__app__, __VERSION__, __DATE__))
      #  self._log.info('Start Reading Valuse')
        data = self.startMeasure()
        print('DAten',data)
        self._log.info(data)
      #  self.publishData(data)
        self.mqttPublish(data)



if __name__ == '__main__':

    if len(sys.argv) == 2:
        configfile = sys.argv[1]
    else:
        configfile = './serial2mqtt.cfg'

    mgr_handle = manager(configfile)
    mgr_handle.run()
