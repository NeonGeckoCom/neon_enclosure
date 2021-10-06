# Copyright 2017 Mycroft AI Inc.
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

from .interface import *


class EnclosureMark2(Enclosure):
    def __init__(self):
        LOG.info('** Initialize EnclosureMark2 **')
        super().__init__("mark2")
        self.display_bus_client = None
        self.finished_loading = False
        self.active_screen = 'loading'
        self.paused_screen = None
        self.is_pairing = False
        self.active_until_stopped = None
        self.reserved_led = 10
        self.mute_led = 11
        self.chaseLedThread = None
        self.pulseLedThread = None

        self.system_volume = 0.5   # pulse audio master system volume
        # if you want to do anything with the system volume
        # (ala pulseaudio, etc) do it here!
        self.current_volume = 0.5  # hardware/board level volume

        # TODO these need to come from a config value
        self.m2enc = HardwareEnclosure("Mark2", "sj201r4")
        self.m2enc.client_volume_handler = self.async_volume_handler

        # start the temperature monitor thread
        self.temperatureMonitorThread = temperatureMonitorThread(self.m2enc.fan, self.m2enc.leds, self.m2enc.palette)
        self.temperatureMonitorThread.start()

        self.m2enc.leds.set_leds([
                self.m2enc.palette.BLACK,
                self.m2enc.palette.BLACK,
                self.m2enc.palette.BLACK,
                self.m2enc.palette.BLACK,
                self.m2enc.palette.BLACK,
                self.m2enc.palette.BLACK,
                self.m2enc.palette.BLACK,
                self.m2enc.palette.BLACK,
                self.m2enc.palette.BLACK,
                self.m2enc.palette.BLACK
                ])

        self.m2enc.leds._set_led_with_brightness(
            self.reserved_led,
            self.m2enc.palette.MAGENTA,
            0.5)

        # set mute led based on reality
        mute_led_color = self.m2enc.palette.GREEN
        if self.m2enc.switches.SW_MUTE == 1:
            mute_led_color = self.m2enc.palette.RED

        self.m2enc.leds._set_led_with_brightness(
            self.mute_led,
            mute_led_color,
            1.0)

        self.default_caps = EnclosureCapabilities()

        LOG.info('** EnclosureMark2 initalized **')

    def async_volume_handler(self, vol):
        LOG.error("ASYNC SET VOL PASSED IN %s" % (vol,))
        if vol > 1.0:
            vol = vol / 10
        self.current_volume = vol
        LOG.error("ASYNC SET VOL TO %s" % (self.current_volume,))
        # notify anybody listening on the bus who cares
        self.bus.emit(Message("hardware.volume", {
            "volume": self.current_volume}, context={"source": ["enclosure"]}))

    def _define_event_handlers(self):
        """Assign methods to act upon message bus events."""
        super()._define_event_handlers()
        # self.bus.on('mycroft.volume.set', self.on_volume_set)
        # self.bus.on('mycroft.volume.get', self.on_volume_get)
        # self.bus.on('mycroft.volume.duck', self.on_volume_duck)
        # self.bus.on('mycroft.volume.unduck', self.on_volume_unduck)
        self.bus.on('recognizer_loop:record_begin', self.handle_start_recording)
        self.bus.on('recognizer_loop:record_end', self.handle_stop_recording)
        self.bus.on('recognizer_loop:audio_output_end', self.handle_end_audio)
        self.bus.on('mycroft.speech.recognition.unknown', self.handle_end_audio)
        self.bus.on('mycroft.stop.handled', self.handle_end_audio)
        self.bus.on('mycroft.capabilities.get', self.on_capabilities_get)

    def handle_start_recording(self, _):
        LOG.debug("Gathering speech stuff")
        if self.pulseLedThread is None:
            self.pulseLedThread = pulseLedThread(self.m2enc.leds, self.m2enc.palette)
            self.pulseLedThread.start()

    def handle_stop_recording(self, _):
        background_color = self.m2enc.palette.BLUE
        foreground_color = self.m2enc.palette.BLACK
        LOG.debug("Got spoken stuff")
        if self.pulseLedThread is not None:
            self.pulseLedThread.exit_flag = True
            self.pulseLedThread.join()
            self.pulseLedThread = None
        if self.chaseLedThread is None:
            self.chaseLedThread = chaseLedThread(self.m2enc.leds, background_color, foreground_color)
            self.chaseLedThread.start()

    def handle_end_audio(self, _):
        LOG.debug("Finished playing audio")
        if self.chaseLedThread is not None:
            self.chaseLedThread.exit_flag = True
            self.chaseLedThread.join()
            self.chaseLedThread = None

    def on_volume_duck(self, message):
        # TODO duck it anyway using set vol
        LOG.warning("Mark2 volume duck deprecated! use volume set instead.")
        self.m2enc.hardware_volume.set_volume(float(0.1))  # TODO make configurable 'duck_vol'

    def on_volume_unduck(self, message):
        # TODO duck it anyway using set vol
        LOG.warning("Mark2 volume unduck deprecated! use volume set instead.")
        self.m2enc.hardware_volume.set_volume(float(self.current_volume))

    def on_volume_set(self, message):
        self.current_volume = message.data.get("percent", self.current_volume)
        LOG.info('Mark2:interface.py set volume to %s' %
                 (self.current_volume,))
        self.m2enc.hardware_volume.set_volume(float(self.current_volume))

        # notify anybody listening on the bus who cares
        self.bus.emit(Message("hardware.volume", {
            "volume": self.current_volume}, context={"source": ["enclosure"]}))

    def on_volume_get(self, message):
        self.current_volume = self.m2enc.hardware_volume.get_volume()

        if self.current_volume > 1.0:
            self.current_volume = self.current_volume / 10

        LOG.info('Mark2:interface.py get and emit volume %s' %
                 (self.current_volume,))
        self.bus.emit(
            message.response(
                data={'percent': self.current_volume, 'muted': False}))

    def on_volume_mute(self, message):
        pass

    def on_capabilities_get(self, message):
        LOG.info('Mark2:interface.py get capabilities requested')

        self.bus.emit(
            message.response(
                data={
                    'default': self.default_caps.caps,
                    'extra': self.m2enc.capabilities,
                    'board_type': self.m2enc.board_type,
                    'leds': self.m2enc.leds.capabilities,
                    'volume': self.m2enc.hardware_volume.capabilities,
                    'switches': self.m2enc.switches.capabilities
                    }
                ))

    def terminate(self):
        self.m2enc.leds._set_led(10, (0, 0, 0))  # blank out reserved led
        self.m2enc.leds._set_led(11, (0, 0, 0))  # BUG set to real value!
        self.m2enc.terminate()
