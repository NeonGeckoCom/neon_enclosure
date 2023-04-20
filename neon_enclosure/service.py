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
from threading import Event

from ovos_PHAL import PHAL
from ovos_plugin_manager.phal import find_phal_plugins
from time import time
from mycroft_bus_client import Message
from ovos_utils.log import LOG


class NeonHardwareAbstractionLayer(PHAL):
    def __init__(self, *args, **kwargs):
        LOG.info(f"Initializing PHAL")
        super().__init__(*args, **kwargs)
        self.status.set_alive()
        self.started = Event()
        self.config = self.config or dict()  # TODO: Fixed in ovos_PHAL 0.0.5a1

    def start(self):
        LOG.info("Starting PHAL")
        if self.config.get('wait_for_gui'):
            LOG.info("Waiting for GUI Service to start")
            timeout = time() + 30
            while time() < timeout:
                resp = self.bus.wait_for_response(Message('mycroft.gui.is_alive'))
                if resp and resp.data.get('status'):
                    LOG.debug('GUI Service is alive')
                    break
        PHAL.start(self)
        LOG.info("Started PHAL")
        self.started.set()

    def load_plugins(self):
        for name, plug in find_phal_plugins().items():
            LOG.info(f"Loading {name}")
            config = self.config.get(name) or {}
            try:
                if hasattr(plug, "validator"):
                    enabled = plug.validator.validate(config)
                else:
                    enabled = config.get("enabled")
            except Exception as e:
                LOG.exception(e)
                enabled = False
            if enabled:
                try:
                    self.drivers[name] = plug(bus=self.bus, config=config)
                    LOG.info(f"PHAL plugin loaded: {name}")
                except Exception:
                    LOG.exception(f"failed to load PHAL plugin: {name}")
                    continue
