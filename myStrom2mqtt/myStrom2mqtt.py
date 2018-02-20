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


__app__ = "myStrom2mqtt2 Adapter"
__VERSION__ = "0.95"
__DATE__ = "19.02.2018"
__author__ = "Markus Schiesser"
__contact__ = "M.Schiesser@gmail.com"
__copyright__ = "Copyright (C) 2018 Markus Schiesser"
__license__ = 'GPL v3'


import sys
import time
import json

from configobj import ConfigObj
from library.mqttclient import mqttclient
from library.loghandler import loghandler
from library.myStromSwitch import switchwrapper

#from library.myStromBulb import bulbwrapper
#from library.myStromBulb import bulb


class manager(object):

    def __init__(self,configfile='./myStrom2mqtt.cfg'):

        self._configfile = configfile

        self._cfg_broker = None
        self._cfg_log = None
        self._cfg_device = None

        self._mqttc = None
        self._switchwrapper = None

    def __del__(self):
        _msg = 'Kill myself' + __app__
        self._log.error(_msg)

    def readConfig(self):

        _config = ConfigObj(self._configfile)

        if bool(_config) is False:
            print('ERROR config file not found',self._configfile)
            sys.exit()

        self._cfg_broker = _config.get('BROKER',None)
        self._cfg_log = _config.get('LOGGING',None)
        self._cfg_device = _config.get('DEVICE',None)
        self._cfg_switch = _config.get('SWITCH',None)
        return True

    def startLogger(self):
        self._log = loghandler('MYSTROM2MQTT')
      #  print('START Looger', self._cfg_log)
        self._log.handle(self._cfg_log.get('LOGMODE'),self._cfg_log)
        self._log.level(self._cfg_log.get('LOGLEVEL','DEBUG'))
        return True

    def startMqttClient(self):
        print('start broker', self._cfg_broker)
        self._mqttc = mqttclient(self._cfg_broker)
#        self._mqttc.subscribe(self._cfg_broker.get('SUBSCRIBE','/MYSTROM'))
     #   self._mqttc.callback('/TEST/#',self.callbackTest)
        return True

    #def start_broker(self):
    # self._mqttc.start()
   # def callbackTest(self, mqttc, obj, msg):

    #    print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
     #   msg = __app__ + 'message received' + str(msg.qos) + " " + str(msg.payload)
      #  self._log.debug(msg)



    def startDevices(self):
        print('Device config',self._cfg_device)
        _switch_cfg = self._cfg_device.get('SWITCH',None)
     #   _bulb_cfg = self._cfg_device.get('BULB', None)

        if _switch_cfg:
            #for item in _switch_cfg:
             #   print('SWITCH',item)
            self._switchwrapper = switchwrapper(self._cfg_device.get('SWITCH', None),self._mqttc,self._log)
            self._switchwrapper.start()

        #if _bulb_cfg:
       #     _bulbwrapper = bulbwrapper(self._cfg_device.get('BULB'),self._mqttc,self._log)
       #     _bulbwrapper.start()

        return True

    def thread_monitor(self):
        if self._mqttc.is_alive():
            _msg = 'Thread MQTT running'
            self._log.debug(_msg)
        else:
            _msg = 'Thread MQTT' + str(self._mqttc) + 'NOT running any more...Restart'
            self._log.critical(_msg)

            time.sleep(1)
#            self.config_broker()
            self.start_broker()

        if self._switchwrapper.is_alive():
            _msg = 'Thread SWITCHWRAPPER running'
            self._log.debug(_msg)
        else:
            _msg = 'Thread SWITCHWRAPPER ' + str(self._mqttc) + 'NOT running any more...Restart'
            self._log.critical(_msg)

            time.sleep(1)
            self._start_devices()

        return True


    def run(self):
        """
        Entry point, initiates components and loops forever...
        """
        self.readConfig()
        self.startLogger()
        # Log information
        msg = 'Start ' + __app__ +' ' +  __VERSION__ + ' ' +  __DATE__
        self._log.info(msg)


        self.startMqttClient()
    #    self.publish_test()
        self.startDevices()
#        self.start_broker()
        #test = 1
        while(True):
            time.sleep(30)
          #  self.thread_monitor()
        #    test = test+1

       # self._log.info('Startup, %s %s %s'% ( __app__, __VERSION__, __DATE__) )
#        self.start_gpio()


if __name__ == "__main__":

    if len(sys.argv) == 2:
        configfile = sys.argv[1]
    else:
        configfile = './myStrom2mqtt.cfg'

    mgr_handle = manager(configfile)
    mgr_handle.run()