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

import time
from threading import Timer
from mycroft_bus_client import Message
from ovos_utils.log import LOG
import mycroft.dialog
from mycroft.api import has_been_paired
from mycroft.audio import wait_while_speaking
from neon_enclosure.enclosure.display_manager import \
    init_display_manager_bus_connection
from mycroft.util import connected

from neon_enclosure.client.enclosure.base import Enclosure

LOG.name = "neon-enclosure"


class EnclosureGeneric(Enclosure):
    """
    Serves as a communication interface between a simple text frontend and
    Mycroft Core.  This is used for Picroft or other headless systems,
    and/or for users of the CLI.
    """

    def __init__(self):
        super().__init__("generic")
        # TODO: this requires the Enclosure to be up and running before the
        # training is complete.
        self.bus.on('mycroft.skills.trained', self.is_device_ready)

        # initiates the web sockets on display manager
        # NOTE: this is a temporary place to connect the display manager
        init_display_manager_bus_connection()

    def on_volume_set(self, message):
        self.bus.emit(Message("hardware.volume", {
            "volume": None,
            "error": "Not Implemented"}, context={"source": ["enclosure"]}))

    def on_volume_get(self, message):
        self.bus.emit(
            message.response(
                data={'percent': None, 'muted': False, "error": "Not Implemented"}))

    def on_volume_mute(self, message):
        pass

    def on_volume_duck(self, message):
        pass

    def on_volume_unduck(self, message):
        pass

    _last_internet_notification = 0

    def speak(self, text):
        self.bus.emit(Message("speak", {'utterance': text}))

    def _handle_pairing_complete(self, _):
        """
        Handler for 'mycroft.paired', unmutes the mic after the pairing is
        complete.
        """
        self.bus.emit(Message("mycroft.mic.unmute"))

    def _do_net_check(self):
        # TODO: This should live in the derived Enclosure, e.g. EnclosureMark1
        LOG.info("Checking internet connection")
        if not connected():  # and self.conn_monitor is None:
            if has_been_paired():
                # TODO: Enclosure/localization
                self.speak("This unit is not connected to the Internet. "
                           "Either plug in a network cable or setup your "
                           "wifi connection.")
            else:
                # Begin the unit startup process, this is the first time it
                # is being run with factory defaults.

                # TODO: This logic should be in EnclosureMark1
                # TODO: Enclosure/localization

                # Don't listen to mic during this out-of-box experience
                self.bus.emit(Message("mycroft.mic.mute"))
                # Setup handler to unmute mic at the end of on boarding
                # i.e. after pairing is complete
                self.bus.once('mycroft.paired', self._handle_pairing_complete)

                self.speak(mycroft.dialog.get('mycroft.intro'))
                wait_while_speaking()
                time.sleep(2)  # a pause sounds better than just jumping in

                # Kick off wifi-setup automatically
                data = {'allow_timeout': False, 'lang': self.lang}
                self.bus.emit(Message('system.wifi.setup', data))
