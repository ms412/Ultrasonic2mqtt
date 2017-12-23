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


__app__ = "onewire2mqtt Adapter"
__VERSION__ = "0.9"
__DATE__ = "04.04.2017"
__author__ = "Markus Schiesser"
__contact__ = "M.Schiesser@gmail.com"
__copyright__ = "Copyright (C) 2017 Markus Schiesser"
__license__ = 'GPL v3'

import os
from configobj import ConfigObj

from library.ds18b20 import ds18b20
from library.devicereader import devicereader
from library.configfile import configfile
import paho.mqtt.client as mqtt
#from library.mqttpush import mqttpush
#from library.logging import logger
from library.loghandler import loghandler


class manager(object):
    def __init__(self,configfile):
       # self._log = loghandler('ONEWIRE')
        self._configfile = configfile

        self._logcfg = None
        self._mqttbroker = None
        self._onewire = None

    def startSystem(self):
        os.system('modprobe w1-gpio')
        os.system('modprobe w1-therm')
        return True

    def readconfig(self):
        #_cfg = configfile(self._configfile)
        #_config = _cfg.openfile()
        _config = ConfigObj(self._configfile)
        self._logcfg = _config.get('LOGGING',None)
        self._mqttCfg = _config.get('BROKER',None)
        self._onewire = _config.get('ONEWIRE',None)
        print(self._onewire)
        return True

    def logger(self):
        self._log = loghandler('ONEWIRE')
        self._log.handle(self._logcfg.get('LOGMODE'),self._logcfg)
        return True

    def getData(self):
        result={}
        basedir = self._onewire.get('BASEDIR','/temp')
        devicefile = self._onewire.get('DEVICEFILE','w1_slave')
        deviceId = self._onewire.get('DEVICEID','28')
      #  print(basedir,devicefile,deviceId)

        ds = ds18b20()
        dr = devicereader(basedir,deviceId,devicefile)
        devices = dr.readdevice()
     #   print('devices found:', devices)
        for deviceId, deviceFile in devices.items():
         #   print(dr.readfile(deviceFile))
            data = dr.readfile(deviceFile)
            if data is not None:
                ds.readValue(data)
                result[deviceId]=ds.getCelsius()

        return result

    def mqttPublish(self,data):
        self._host = str(self._mqttCfg.get('HOST', 'localhost'))
        self._port = int(self._mqttCfg.get('PORT', 1883))
        main_channel = str(self._mqttCfg.get('PUBLISH', '/OPENHAB'))
  
        self._mqttc = mqtt.Client()
        self._mqttc.connect(self._host,self._port,60)

        for deviceId, measurement in data.items():
            _topic = main_channel + '/' + deviceId
            self._mqttc.publish(_topic, measurement)
        # print('cc',channel,msg)
            self._mqttc.loop(2)
            self._mqttc.disconnect()   

    def publishData(self,data):
        mqttc = mqttpush(self._mqttbroker)
        main_channel = self._mqttbroker.get('PUBLISH','/OPENHAB')

        for deviceId, measurement in data.items():
            channel = main_channel + '/' + deviceId
          #  print('channel',channel,deviceId)
            mqttc.publish(channel,measurement)

        return True

    def run(self):
        self.startSystem()
        self.readconfig()
        self.logger()

        self._log.info('Startup, %s %s %s' % (__app__, __VERSION__, __DATE__))

        data = self.getData()
        self._log.info(data)
    #    self.publishData(data)
        self.mqttPublish(data)



if __name__ == '__main__':
    mgr = manager('/home/pi/Onewire2mqtt/onewire2mqtt.cfg')
    mgr.run()
