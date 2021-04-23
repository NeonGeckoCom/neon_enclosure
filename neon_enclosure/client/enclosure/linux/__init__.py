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
import alsaaudio
from mycroft_bus_client import Message
from neon_utils.logger import LOG

from neon_enclosure.enclosure.display_manager import \
    init_display_manager_bus_connection

from mycroft.util import connected

from neon_enclosure.client.enclosure.base import Enclosure


class EnclosureLinux(Enclosure):
    """
    Serves as a communication interface between a simple text frontend and
    Mycroft Core.  This is used for Picroft or other headless systems,
    and/or for users of the CLI.
    """

    _last_internet_notification = 0

    def __init__(self):
        super().__init__()
        self.alsa = alsaaudio.Mixer()
        # Notifications from mycroft-core
        self.bus.on('enclosure.notify.no_internet', self.on_no_internet)
        # TODO: this requires the Enclosure to be up and running before the training is complete.
        self.bus.on('mycroft.skills.trained', self.is_device_ready)

        self._define_event_handlers()
        self._default_duck = 0.3
        self._pre_duck_level = self._get_alsa_avg_output()
        self._pre_mute_level = self._get_alsa_avg_output()

        # initiates the web sockets on display manager
        # NOTE: this is a temporary place to connect the display manager
        init_display_manager_bus_connection()

    def _get_alsa_avg_output(self) -> float:
        """
        Gets the average audio output level from ALSA
        :return: average volume
        """
        levels = self.alsa.getvolume()
        volume = sum(levels) / len(levels)
        return volume

    def _get_alsa_mute_status(self) -> bool:
        """
        Gets the mute status from ALSA
        :return: True if audio output is muted
        """
        return any([i for i in self.alsa.getmute() if i == 1])

    def on_volume_set(self, message):
        """
        Handler for "mycroft.volume.set". Sets volume and emits hardware.volume to notify other listeners of change.
        :param message: Message associated with request
        """
        new_volume = message.data.get("percent", self._get_alsa_avg_output())
        self.alsa.setvolume(round(float(new_volume)))
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
                data={'percent': self._get_alsa_avg_output(), 'muted': self._get_alsa_mute_status()}))

    def on_volume_mute(self, message):
        """
        Handler for "mycroft.volume.mute". Toggles mute status depending on message.data['mute'].
        :param message: Message associated with request.
        """
        if message.data.get("mute", False):
            self._pre_mute_level = self._get_alsa_avg_output()
            self.alsa.setmute(True)
        else:
            self.alsa.setmute(False)
            self.alsa.setvolume(self._pre_mute_level)

    def on_volume_duck(self, message):
        """
        Handler for "mycroft.volume.duck".
        :param message: Message associated with request
        :return:
        """
        self._pre_duck_level = self._get_alsa_avg_output()
        duck_scalar = float(message.data.get("duck_scalar")) or self._default_duck
        new_vol = self._pre_duck_level * duck_scalar
        self.alsa.setvolume(new_vol)

    def on_volume_unduck(self, message):
        """
        Handler for "mycroft.volume.unduck".
        :param message: Message associated with request
        :return:
        """
        self.alsa.setvolume(self._pre_duck_level)

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
