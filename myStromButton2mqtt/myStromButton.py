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


__app__ = "myStrom Button"
__VERSION__ = "0.4"
__DATE__ = "14.09.2017"
__author__ = "Markus Schiesser"
__contact__ = "M.Schiesser@gmail.com"
__copyright__ = "Copyright (C) 2017 Markus Schiesser"
__license__ = 'GPL v3'

import sys
import cherrypy
import paho.mqtt.client as mqtt
from configobj import ConfigObj
from library.httpd import httpd
from library.logger import logger


class myStromButton(object):
    def __init__(self,config):
        self._configfile = config
        self._mqttCfg = {}
        self._mqttCfg['HOST']='192.168.2.50'
        self._mqttCfg['PORT']= 1883

    def readConfig(self):
        _cfg = ConfigObj(self._configfile)

        self._logCfg = _cfg.get('LOGGING')
        self._mqttCfg = _cfg.get('MQTT')
        return True

    def startLogging(self):
     #   print('Logging',self._logCfg)
        self._log = logger('MYSTROMBUTTON2MQTT')
        self._log.handle(self._logCfg.get('LOGMODE'),self._logCfg)
        self._log.level(self._logCfg.get('LOGLEVEL','DEBUG'))
        return True

    def mqttPublish(self,topic,payload):
        self._host = str(self._mqttCfg.get('HOST', 'localhost'))
        self._port = int(self._mqttCfg.get('PORT', 1883))
        self._publish = str(self._mqttCfg.get('PUBLISH', '/PUBLISH'))
        _topic = str(self._publish + '/' + topic)

    #    print(_topic)
        self._mqttc = mqtt.Client()

        self._mqttc.connect(self._host,self._port,60)
        self._mqttc.publish(_topic, payload)
        # print('cc',channel,msg)
        self._mqttc.loop(2)
        self._mqttc.disconnect()
        return True

    def httpd(self):
        _httpdCfg = {}
        _httpdCfg['server.socket_host'] = str('0.0.0.0')
        _httpdCfg['server.socket_port'] = int(80)

        cherrypy.config.update(_httpdCfg)

        _httpd = httpd()
        _httpd.register_callback(self.httpdCallback)
        print('config', cherrypy.config)
        cherrypy.tree.mount(_httpd,'/')
        cherrypy.engine.start()
        return True

    def httpdCallback(self,mode,adresse):
   #     print('test',mode,adresse)
        _topic = str(adresse + '/' + mode)
        self.mqttPublish(_topic,'ON')


if __name__ == '__main__':

    if len(sys.argv) == 2:
        configfile = sys.argv[1]
    else:
        configfile = '/opt/myStromButton/myStromButton2mqtt.cfg'
    #    configfile = 'C:/Users/tgdscm41/PycharmProjects/Raspberry/vcontrold2mqtt/vcontrold2mqtt.cfg'
        #configfile =  '/home/pi/m2m/S02mqtt.cfg'

    myStromButton = myStromButton(configfile)
    myStromButton.readConfig()
    myStromButton.startLogging()
    myStromButton.httpd()
