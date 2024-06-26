# NEON AI (TM) SOFTWARE, Software Development Kit & Application Framework
# All trademark and other rights reserved by their respective owners
# Copyright 2008-2022 Neongecko.com Inc.
# Contributors: Daniel McKnight, Guy Daniels, Elon Gasper, Richard Leeds,
# Regina Bloomstine, Casimiro Ferreira, Andrii Pernatii, Kirill Hrymailo
# BSD-3 License
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS  BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS;  OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE,  EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import unittest
from unittest.mock import patch, Mock

from ovos_utils.messagebus import FakeBus
from click.testing import CliRunner

from neon_enclosure.service import NeonHardwareAbstractionLayer
from neon_enclosure.admin.service import NeonAdminHardwareAbstractionLayer


class TestEnclosureService(unittest.TestCase):
    bus = FakeBus()

    def test_enclosure_service(self):
        alive = Mock()
        started = Mock()
        ready = Mock()
        stopping = Mock()
        service = NeonHardwareAbstractionLayer(alive_hook=alive,
                                               started_hook=started,
                                               ready_hook=ready,
                                               stopping_hook=stopping,
                                               daemonic=True,
                                               bus=self.bus)
        alive.assert_called_once()
        started.assert_not_called()
        ready.assert_not_called()
        stopping.assert_not_called()

        service.start()
        service.started.wait()

        alive.assert_called_once()
        started.assert_called_once()
        ready.assert_called_once()
        stopping.assert_not_called()

        service.shutdown()
        stopping.assert_called_once()


class TestAdminEnclosureService(unittest.TestCase):
    bus = FakeBus()

    def test_enclosure_service(self):
        alive = Mock()
        started = Mock()
        ready = Mock()
        stopping = Mock()
        service = NeonAdminHardwareAbstractionLayer(alive_hook=alive,
                                                    started_hook=started,
                                                    ready_hook=ready,
                                                    stopping_hook=stopping,
                                                    daemonic=True,
                                                    bus=self.bus)
        alive.assert_called_once()
        started.assert_not_called()
        ready.assert_not_called()
        stopping.assert_not_called()

        service.start()
        service.started.wait()

        alive.assert_called_once()
        started.assert_called_once()
        ready.assert_called_once()
        stopping.assert_not_called()

        service.shutdown()
        stopping.assert_called_once()


class TestCLI(unittest.TestCase):
    runner = CliRunner()

    @patch("neon_enclosure.cli.init_config_dir")
    @patch("neon_enclosure.__main__.main")
    def test_run(self, main, init_config):
        from neon_enclosure.cli import run
        self.runner.invoke(run)
        init_config.assert_called_once()
        main.assert_called_once()

    @patch("os.geteuid")
    @patch("neon_enclosure.cli.init_config_dir")
    @patch("neon_enclosure.admin.__main__.main")
    def test_run_admin(self, main, init_config, get_id):
        from neon_enclosure.cli import run_admin
        # Non-root
        get_id.return_value = 100
        self.runner.invoke(run_admin)
        init_config.assert_not_called()
        main.assert_not_called()

        # Root
        get_id.return_value = 0
        self.runner.invoke(run_admin)
        init_config.assert_called_once()
        main.assert_called_once()


if __name__ == '__main__':
    unittest.main()
