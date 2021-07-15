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

from abc import abstractmethod
from mycroft_bus_client import MessageBusClient
from neon_utils.configuration_utils import get_mycroft_compatible_config


class Enclosure:
    def __init__(self):
        # Load full config
        config = get_mycroft_compatible_config()
        self.lang = config['lang']
        self.config = config.get("enclosure")
        # LOG.info(config)
        config["gui_websocket"] = config.get("gui_websocket", {"host": "0.0.0.0",
                                                               "base_port": 18181,
                                                               "route": "/gui",
                                                               "ssl": False})
        config['gui_websocket']["base_port"] = config["gui_websocket"].get("base_port",
                                                                           config["gui_websocket"].get("port", 18181))

        self.global_config = config

        # Create Message Bus Client
        self.bus = MessageBusClient()

        # self.gui = create_gui_service(self, config['gui_websocket'])
        # This datastore holds the data associated with the GUI provider. Data
        # is stored in Namespaces, so you can have:
        # self.datastore["namespace"]["name"] = value
        # Typically the namespace is a meaningless identifier, but there is a
        # special "SYSTEM" namespace.
        self.datastore = {}

        # self.loaded is a list, each element consists of a namespace named
        # tuple.
        # The namespace namedtuple has the properties "name" and "pages"
        # The name contains the namespace name as a string and pages is a
        # mutable list of loaded pages.
        #
        # [Namespace name, [List of loaded qml pages]]
        # [
        # ["SKILL_NAME", ["page1.qml, "page2.qml", ... , "pageN.qml"]
        # [...]
        # ]
        self.loaded = []  # list of lists in order.
        self.explicit_move = True  # Set to true to send reorder commands

        # Listen for new GUI clients to announce themselves on the main bus
        self.active_namespaces = []

    def run(self):
        """Start the Enclosure after it has been constructed."""
        # Allow exceptions to be raised to the Enclosure Service
        # if they may cause the Service to fail.
        self.bus.run_in_thread()

    def stop(self):
        """Perform any enclosure shutdown processes."""
        pass

    @abstractmethod
    def on_volume_set(self, message):
        """
        Handler for "mycroft.volume.set".
        """

    @abstractmethod
    def on_volume_get(self, message):
        """
        Handler for "mycroft.volume.get".
        """

    @abstractmethod
    def on_volume_mute(self, message):
        """
        Handler for "mycroft.volume.mute".
        """

    @abstractmethod
    def on_volume_duck(self, message):
        """
        Handler for "mycroft.volume.duck".
        """

    @abstractmethod
    def on_volume_unduck(self, message):
        """
        Handler for "mycroft.volume.unduck".
        """

    def _define_event_handlers(self):
        """Assign methods to act upon message bus events."""
        self.bus.on('mycroft.volume.set', self.on_volume_set)
        self.bus.on('mycroft.volume.get', self.on_volume_get)
        self.bus.on('mycroft.volume.mute', self.on_volume_mute)
        self.bus.on('mycroft.volume.duck', self.on_volume_duck)
        self.bus.on('mycroft.volume.unduck', self.on_volume_unduck)
