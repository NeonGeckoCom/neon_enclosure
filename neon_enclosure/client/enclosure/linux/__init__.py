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
from neon_enclosure.enclosure.audio.alsa_audio import AlsaAudio

try:
    from neon_enclosure.enclosure.audio.pulse_audio import PulseAudio
except ImportError:  # Catch missing pulsectl module
    PulseAudio = None

from mycroft.util import connected


class EnclosureLinux(Enclosure):
    """
    Serves as a communication interface between a simple text frontend and
    Mycroft Core.  This is used for Picroft or other headless systems,
    and/or for users of the CLI.
    """
    def __init__(self):
        super().__init__()
        self._backend = "pulsectl"  # TODO: Read from preference
        if not PulseAudio:
            self._backend = "alsa"

        if self._backend == "pulsectl":
            self.audio_system = PulseAudio()
        else:
            self.audio_system = AlsaAudio()
        # Notifications from mycroft-core
        self.bus.on('enclosure.notify.no_internet', self.on_no_internet)
        # TODO: this requires the Enclosure to be up and running before the training is complete.
        self.bus.on('mycroft.skills.trained', self.is_device_ready)

        self._define_event_handlers()
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

    def is_device_ready(self, message):
        # Bus service assumed to be alive if messages sent and received
        # Enclosure assumed to be alive if this method is running
        services = {'audio': False, 'speech': False, 'skills': False}
        is_ready = self.check_services_ready(services)

        if is_ready:
            LOG.info("Mycroft is all loaded and ready to roll!")
            self.bus.emit(Message('mycroft.ready'))

        return is_ready

    def check_services_ready(self, services):
        """Report if all specified services are ready.

        services (iterable): service names to check.
        """
        for ser in services:
            services[ser] = False
            response = self.bus.wait_for_response(Message(
                                'mycroft.{}.is_ready'.format(ser)), timeout=60)
            if response and response.data['status']:
                services[ser] = True
        return all([services[ser] for ser in services])

    def on_no_internet(self, event=None):
        if connected():
            # One last check to see if connection was established
            return

        if time.time() - Enclosure._last_internet_notification < 30:
            # don't bother the user with multiple notifications with 30 secs
            return

        Enclosure._last_internet_notification = time.time()

    def speak(self, text):
        self.bus.emit(Message("speak", {'utterance': text}))

    def _define_event_handlers(self):
        """Assign methods to act upon message bus events."""
        self.bus.on('mycroft.volume.set', self.on_volume_set)
        self.bus.on('mycroft.volume.get', self.on_volume_get)
        self.bus.on('mycroft.volume.mute', self.on_volume_mute)
        self.bus.on('mycroft.volume.duck', self.on_volume_duck)
        self.bus.on('mycroft.volume.unduck', self.on_volume_unduck)
