import os
import re
import glob

class devicereader(object):
    def __init__(self,basedir,deviceid,devicefile):
        self._basedir =os.path.join('c:', os.sep, basedir)
        self._deviceid = deviceid
        self._devicefile = devicefile

    def readdevice(self):
        result = {}
        for name in os.listdir(self._basedir):
            pathname = os.path.join(os.sep, self._basedir, name)
            if os.path.isdir(pathname):
           #     print('Path:',pathname)
                temp = os.path.join(self._basedir + '/' + self._deviceid)
            #    print('Temp',temp)
            #    print('Test1', glob.glob(temp))
            #    print('Test', glob.glob('/sys/bus/w1/devices/28*'))
              #  p = re.compile('(self._deviceid)*')
               # print('match',p.match(str(pathname)))
              #  if p.match(str(pathname)):
           #     for device in glob.glob('/sys/bus/w1/devices/28*'):

              #  print('path', os.path.basename(os.path.normpath(pathname)))
                deviceId = os.path.basename(os.path.normpath(pathname))
                device_file = os.path.join(os.sep, pathname, self._devicefile)
             #   print('devicefile',device_file,pathname,self._devicefile)
                result[deviceId]=device_file
        return result

    def readfile(self, filename):
        try:
            with open(filename)as fh:
                lines = fh.readlines()
                fh.close()
        except:
            lines = None
            print('failed open file:', filename)

        return lines

