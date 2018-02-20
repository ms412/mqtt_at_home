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


__app__ = "Modbus Manager"
__VERSION__ = "0.2"
__DATE__ = "19.02.2018"
__author__ = "Markus Schiesser"
__contact__ = "M.Schiesser@gmail.com"
__copyright__ = "Copyright (C) 2018 Markus Schiesser"
__license__ = 'GPL v3'

import minimalmodbus

from library.loghandler import loghandler

class mgr_modbus(object):
    def __init__(self,config):

        self._log = loghandler()

#        print('config', config)

        self._interface = str(config.get('INTERFACE','/dev/ttyUSB0'))
        self._baudrate = int(config.get('BAUDRATE',9800))
        self._deviceID = int(config.get('DEVICEID',0))

        self._if = None

    def __del__(self):
        _msg = 'Kill myself' + __app__
        self._log.error(_msg)

    def setup(self):
        self._if = minimalmodbus.Instrument(self._interface,self._deviceID)
        self._if.serial.baudrate = self._baudrate
        self._if.timeout = 0.8
        self._if.debug = False
        return True

    def read(self,data):
     #   print('test',self._if)
        _type,value,size = data
        if 'int' in _type:
           # print('type int',value)
      #      print('read int',value,int(size))
            value = self._if.read_register(int(value,16),int(size))
         #   value = '8'
        elif 'str' in _type:
       #     print('type string',value,size)
          #  value ='TEST'
            value = self._if.read_string(int(value,16),int(size))
        elif 'float' in _type:
            value = self._if.read_float(int(value,16),functioncode=4, numberOfRegisters=2)
        else:
            value = None

        return value


       # print(typ,value,size)


