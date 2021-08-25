# NEON AI (TM) SOFTWARE, Software Development Kit & Application Development System
# All trademark and other rights reserved by their respective owners
# Copyright 2008-2021 Neongecko.com Inc.
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

import time

from mycroft_bus_client import Message
from neon_utils.logger import LOG

from neon_enclosure.enclosure.display_manager import \
    init_display_manager_bus_connection
from neon_enclosure.client.enclosure.base import Enclosure

try:
    from neon_enclosure.enclosure.audio.pulse_audio import PulseAudio
except ImportError:  # Catch missing pulsectl module
    PulseAudio = None
except OSError as e:
    LOG.error(e)
    PulseAudio = None

try:
    from neon_enclosure.enclosure.audio.alsa_audio import AlsaAudio
except ImportError:
    AlsaAudio = None


try:
    from neon_enclosure.enclosure.audio.alsa_audio import AlsaAudio
except ImportError:
    AlsaAudio = None


class EnclosureLinux(Enclosure):
    """
    Serves as a communication interface between a simple text frontend and
    Mycroft Core.  This is used for Picroft or other headless systems,
    and/or for users of the CLI.
    """
    def __init__(self):
        super().__init__("linux")
        self._backend = "pulsectl"  # TODO: Read from preference
        if not PulseAudio:
            if AlsaAudio:
                self._backend = "alsa"
            else:
                raise ImportError("No pulse or alsa backend available!")

        if self._backend == "pulsectl":
            self.audio_system = PulseAudio()
        elif self._backend == "alsa":
            self.audio_system = AlsaAudio()
        else:
            raise ValueError(f"Invalid audio backend defined: {self._backend}")

        self._default_duck = 0.3
        self._pre_duck_level = self.audio_system.get_volume()
        self._pre_mute_level = self.audio_system.get_volume()

        # initiates the web sockets on display manager
        # NOTE: this is a temporary place to connect the display manager
        init_display_manager_bus_connection()

    def on_volume_set(self, message):
        """
        Handler for "mycroft.volume.set". Sets volume and emits hardware.volume to notify other listeners of change.
        :param message: Message associated with request
        """
        new_volume = message.data.get("percent", self.audio_system.get_volume()/100)  # 0.0-1.0
        if new_volume > 1.0:
            new_volume = 1.0
        elif new_volume < 0.0:
            new_volume = 0.0
        self.audio_system.set_volume(round(100 * float(new_volume)))
        # notify anybody listening on the bus who cares
        self.bus.emit(Message("hardware.volume", {
            "volume": new_volume}, context={"source": ["enclosure"]}))

    def on_volume_get(self, message):
        """
        Handler for "mycroft.volume.get". Emits a response with the current volume percent and mute status.
        :param message: Message associated with request
        :return:
        """
        self.bus.emit(
            message.response(
                data={'percent': self.audio_system.get_volume()/100, 'muted': self.audio_system.get_mute_state()}))

    def on_volume_mute(self, message):
        """
        Handler for "mycroft.volume.mute". Toggles mute status depending on message.data['mute'].
        :param message: Message associated with request.
        """
        if message.data.get("mute", False):
            self._pre_mute_level = self.audio_system.get_volume()
            self.audio_system.set_mute(True)
        else:
            self.audio_system.set_mute(False)
            self.audio_system.set_volume(self._pre_mute_level)

    def on_volume_duck(self, message):
        """
        Handler for "mycroft.volume.duck".
        :param message: Message associated with request
        :return:
        """
        self._pre_duck_level = self.audio_system.get_volume()
        duck_scalar = float(message.data.get("duck_scalar")) or self._default_duck
        new_vol = self._pre_duck_level * duck_scalar
        self.audio_system.set_volume(round(new_vol))

    def on_volume_unduck(self, message):
        """
        Handler for "mycroft.volume.unduck".
        :param message: Message associated with request
        :return:
        """
        self.audio_system.set_volume(self._pre_duck_level)

    def speak(self, text):
        self.bus.emit(Message("speak", {'utterance': text}))
