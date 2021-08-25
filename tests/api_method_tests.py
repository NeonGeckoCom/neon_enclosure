# NEON AI (TM) SOFTWARE, Software Development Kit & Application Development System
# All trademark and other rights reserved by their respective owners
# Copyright 2008-2021 Neongecko.com Inc.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
# following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions
#    and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions
#    and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote
#    products derived from this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
# USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from time import sleep, time

import os
import sys
import unittest

from multiprocessing import Process

from mycroft_bus_client import MessageBusClient, Message
from neon_utils.configuration_utils import get_neon_local_config
from neon_utils.logger import LOG
from mycroft.messagebus.service.__main__ import main as messagebus_service

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from neon_enclosure.client.enclosure.__main__ import main as neon_enclosure_main

TEST_CONFIG = get_neon_local_config(os.path.dirname(__file__))
TEST_CONFIG["devVars"]["devType"] = "generic"
# TODO: Define some testing enclosure with mock audio DM


class TestAPIMethods(unittest.TestCase):
    bus_thread = None
    enclosure_thread = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.bus_thread = Process(target=messagebus_service, daemon=False)
        cls.enclosure_thread = Process(target=neon_enclosure_main, kwargs={"config": {"platform": "generic"}},
                                       daemon=False)
        cls.bus_thread.start()
        cls.enclosure_thread.start()
        cls.bus = MessageBusClient()
        cls.bus.run_in_thread()
        while not cls.bus.started_running:
            sleep(1)
        alive = False
        while not alive:
            message = cls.bus.wait_for_response(Message("mycroft.enclosure.is_ready"))
            if message:
                alive = message.data.get("status")

    @classmethod
    def tearDownClass(cls) -> None:
        super(TestAPIMethods, cls).tearDownClass()
        cls.bus_thread.terminate()
        cls.enclosure_thread.terminate()
        try:
            if cls.bus_thread.is_alive():
                cls.bus_thread.kill()
            if cls.enclosure_thread.is_alive():
                cls.enclosure_thread.kill()
        except Exception as e:
            LOG.error(e)

    def test_get_enclosure(self):
        resp = self.bus.wait_for_response(Message("neon.get_enclosure"))
        self.assertIsInstance(resp, Message)
        self.assertEqual(resp.data["enclosure"], "generic")


if __name__ == '__main__':
    unittest.main()
