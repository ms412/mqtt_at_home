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


__app__ = "vClient"
__VERSION__ = "0.1"
__DATE__ = "23.07.2017"
__author__ = "Markus Schiesser"
__contact__ = "M.Schiesser@gmail.com"
__copyright__ = "Copyright (C) 2017 Markus Schiesser"
__license__ = 'GPL v3'

import telnetlib
import time
from library.logger import logger


class vcontrold(object):
    def __init__(self,config,loghandle):
        print('vcontrol',config,loghandle)

        self._config = config
        self._log = logger()

        self._host = config.get('HOST','localhost')
        self._port = config.get('PORT',3002)

        self._tn_handle = None
        print('vcontrol',loghandle)

    def connect(self):
        result = False
        try:
            self._tn_handle = telnetlib.Telnet(self._host, self._port,10)
            #self._tn_handle.read_until('vctrld>',5)
            _msg = 'Connected to vClient ' + self._host
            self._log.debug(_msg)
            result = True
        except:
            _msg = 'failed to connect to vcontrol demon' + self._host + str(self._port)
            self._log.debug(_msg)
            return result


        try:
            response = self._tn_handle.read_until(b"vctrld>", 10)
        except EOFError as e:
            print('No Responce from demon', e)
          #  print('tttt')

        return result

    def _close(self):
        self._tn_handle.write('quit\n')
        return True

    def _read(self,command):
        print('read',command)
       # self._tn_handle.write(command + "\n")
        self._tn_handle.write(command.encode('ascii') + b"\n")
        reply = self._tn_handle.read_until(b"vctrld>", 5).strip(b"\nvctrld>")
        string1 = reply.decode("utf-8")
        print('star',string1)
        liststring1 = string1.split(' ', 1)
        print('output', command, liststring1)
        d = {'VALUE': liststring1[0], 'Type': liststring1[-1]}

        #  value = self._tn_handle.read_until("vctrld>")
        #return d
        return liststring1[0]


    def readValues(self,commands):
        print('commands',commands)
        result = {}
        for item in commands:
         #   print(item)
            result[item] = self._read(item)
            time.sleep(1)
            print(result)

        return result
