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

from abc import abstractmethod
from collections import namedtuple
from threading import Lock
from mycroft_bus_client import MessageBusClient, Message
from neon_utils import LOG
from neon_utils.configuration_utils import get_mycroft_compatible_config
from neon_utils.net_utils import check_online

Namespace = namedtuple('Namespace', ['name', 'pages'])
write_lock = Lock()
namespace_lock = Lock()

RESERVED_KEYS = ['__from', '__idle']


def _get_page_data(message):
    """ Extract page related data from a message.

    Args:
        message: messagebus message object
    Returns:
        tuple (page, namespace, index)
    Raises:
        ValueError if value is missing.
    """
    data = message.data
    # Note:  'page' can be either a string or a list of strings
    if 'page' not in data:
        raise ValueError("Page missing in data")
    if 'index' in data:
        index = data['index']
    else:
        index = 0
    page = data.get("page", "")
    namespace = data.get("__from", "")
    return page, namespace, index


class Enclosure:
    def __init__(self, enclosure_type: str):
        # Load full config
        config = get_mycroft_compatible_config()
        self.lang = config['lang']
        self.config = config.get("enclosure")
        self.enclosure_type = enclosure_type

        self.global_config = config

        # Create Message Bus Client
        self.bus = MessageBusClient()

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

        # TODO: this requires the Enclosure to be up and running before the training is complete.
        self.bus.once('mycroft.skills.trained', self.is_device_ready)

        self._define_event_handlers()

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

    def on_get_enclosure(self, message):
        """
        Handler for "neon.get_enclosure"
        """
        self.bus.emit(message.response({"enclosure": self.enclosure_type}))

    @staticmethod
    def on_no_internet(_):
        """
        Handler for "enclosure.notify.no_internet
        """
        if check_online():
            # One last check to see if connection was established
            return

        if time.time() - Enclosure._last_internet_notification < 30:
            # don't bother the user with multiple notifications with 30 secs
            return

        Enclosure._last_internet_notification = time.time()

    def is_device_ready(self, _):
        is_ready = False
        # Bus service assumed to be alive if messages sent and received
        # Enclosure assumed to be alive if this method is running
        services = {'audio': False, 'speech': False, 'skills': False}
        start = time.monotonic()
        while not is_ready:
            is_ready = self.check_services_ready(services)
            if is_ready:
                break
            elif time.monotonic() - start >= 60:
                raise Exception(f'Timeout waiting for services start. services={services}')
            else:
                time.sleep(3)

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
                                'mycroft.{}.is_ready'.format(ser)))
            if response and response.data['status']:
                services[ser] = True
        return all([services[ser] for ser in services])

    def _define_event_handlers(self):
        """Assign methods to act upon message bus events."""
        self.bus.on('mycroft.volume.set', self.on_volume_set)
        self.bus.on('mycroft.volume.get', self.on_volume_get)
        self.bus.on('mycroft.volume.mute', self.on_volume_mute)
        self.bus.on('mycroft.volume.duck', self.on_volume_duck)
        self.bus.on('mycroft.volume.unduck', self.on_volume_unduck)

        # Notifications from mycroft-core
        self.bus.on('enclosure.notify.no_internet', self.on_no_internet)

        self.bus.on('neon.get_enclosure', self.on_get_enclosure)
