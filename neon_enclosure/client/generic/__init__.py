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

from mycroft_bus_client import Message
from neon_utils import LOG

from neon_enclosure.components.display_manager import \
    init_display_manager_bus_connection
from neon_enclosure.client.base import Enclosure

LOG.name = "neon-enclosure"


class EnclosureGeneric(Enclosure):
    """
    Serves as a communication interface between a simple text frontend and
    Mycroft Core.  This is used for Picroft or other headless systems,
    and/or for users of the CLI.
    """

    def __init__(self):
        super().__init__("generic")

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
