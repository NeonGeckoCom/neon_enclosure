# Copyright 2019 Mycroft AI Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""Define the enclosure interface for Mark II devices."""
import time
import threading

from neon_enclosure.client.base import Enclosure
from neon_enclosure.components.hardware_enclosure import HardwareEnclosure
from neon_enclosure.util.hardware_capabilities import EnclosureCapabilities

from mycroft_bus_client import Message
from neon_utils import LOG


class temperatureMonitorThread(threading.Thread):
    def __init__(self, fan_obj, led_obj, pal_obj):
        self.fan_obj = fan_obj
        self.led_obj = led_obj
        self.pal_obj = pal_obj
        self.exit_flag = False
        threading.Thread.__init__(self)

    def run(self):
        LOG.debug("temperature monitor thread started")
        while not self.exit_flag:
            time.sleep(60)

            LOG.info("CPU temperature is %s" % (self.fan_obj.get_cpu_temp(),))

            # TODO make this ratiometric
            current_temperature = self.fan_obj.get_cpu_temp()
            if current_temperature < 50.0:
                # anything below 122F we are fine
                self.fan_obj.set_fan_speed(0)
                LOG.debug("Fan turned off")
                self.led_obj._set_led(10, self.pal_obj.BLUE)
                continue

            if current_temperature > 50.0 and current_temperature < 60.0:
                # 122 - 140F we run fan at 25%
                self.fan_obj.set_fan_speed(25)
                LOG.debug("Fan set to 25%")
                self.led_obj._set_led(10, self.pal_obj.MAGENTA)
                continue

            if current_temperature > 60.0 and current_temperature <= 70.0:
                # 140 - 160F we run fan at 50%
                self.fan_obj.set_fan_speed(50)
                LOG.debug("Fan set to 50%")
                self.led_obj._set_led(10, self.pal_obj.BURNT_ORANGE)
                continue

            if current_temperature > 70.0:
                # > 160F we run fan at 100%
                self.fan_obj.set_fan_speed(100)
                LOG.debug("Fan set to 100%")
                self.led_obj._set_led(10, self.pal_obj.RED)
                continue


class pulseLedThread(threading.Thread):
    def __init__(self, led_obj, pal_obj):
        self.led_obj = led_obj
        self.pal_obj = pal_obj
        self.exit_flag = False
        self.color_tup = self.pal_obj.MYCROFT_GREEN
        self.delay = 0.1
        self.brightness = 100
        self.step_size = 5
        threading.Thread.__init__(self)

    def run(self):
        LOG.debug("pulse thread started")
        self.tmp_leds = []
        for x in range(0,10):
            self.tmp_leds.append( self.color_tup )

        self.led_obj.brightness = self.brightness / 100
        self.led_obj.set_leds( self.tmp_leds )

        while not self.exit_flag:

            if (self.brightness + self.step_size) > 100:
                self.brightness = self.brightness - self.step_size
                self.step_size = self.step_size * -1

            elif (self.brightness + self.step_size) < 0:
                self.brightness = self.brightness - self.step_size
                self.step_size = self.step_size * -1

            else:
                self.brightness += self.step_size

            self.led_obj.brightness = self.brightness / 100
            self.led_obj.set_leds( self.tmp_leds )

            time.sleep(self.delay)

        LOG.debug("pulse thread stopped")
        self.led_obj.brightness = 1.0
        self.led_obj.fill( self.pal_obj.BLACK )


class chaseLedThread(threading.Thread):
    def __init__(self, led_obj, background_color, foreground_color):
        self.led_obj = led_obj
        self.bkgnd_col = background_color
        self.fgnd_col = foreground_color
        self.exit_flag = False
        self.color_tup = foreground_color
        self.delay = 0.1
        tmp_leds = []
        for indx in range(0,10):
            tmp_leds.append(self.bkgnd_col)

        self.led_obj.set_leds(tmp_leds)
        threading.Thread.__init__(self)

    def run(self):
        LOG.debug("chase thread started")
        chase_ctr = 0
        while not self.exit_flag:
            chase_ctr += 1
            LOG.error("chase thread %s" % (chase_ctr,))
            for x in range(0,10):
                self.led_obj.set_led(x, self.fgnd_col)
                time.sleep(self.delay)
                self.led_obj.set_led(x, self.bkgnd_col)
            if chase_ctr > 10:
                self.exit_flag = True

        LOG.debug("chase thread stopped")
        self.led_obj.fill( (0,0,0) )

