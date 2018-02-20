import os
import re
import time

class ds18b20(object):
    def __init__(self):
        self._temperature = 0

    def readValue(self, lines):
        result = False
        print(lines)

        for x in range (3):
            if lines[0].strip()[-3:] != 'YES':
                print('error')
                time.sleep(0.2)
            else:
                equals_pos = lines[1].find('t=')
                if equals_pos != -1:
                    temp_string = lines[1][equals_pos + 2:]
                    self._temperature = float(temp_string) / 1000.0
                    reslut = True
        return result

    def getCelsius(self):
        return self._temperature

    def getFahreinheit(self):
        return self._temperature *9.0 / 5.0 +32


   # while True:
    #print(read_temp())
    #time.sleep(1)
