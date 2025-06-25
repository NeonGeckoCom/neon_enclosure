# NEON AI (TM) SOFTWARE, Software Development Kit & Application Framework
# All trademark and other rights reserved by their respective owners
# Copyright 2008-2025 Neongecko.com Inc.
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
from time import time
from ovos_bus_client.message import Message
from ovos_utils.log import LOG
from ovos_utils.process_utils import ProcessState


class NeonHardwareAbstractionLayer(PHAL):
    def __init__(self, skill_id="neon.phal", **kwargs):
        LOG.info("Initializing PHAL")
        PHAL.__init__(self, skill_id=skill_id, **kwargs)
        self.status.set_alive()
        self.started = Event()
        self._status_from_bus_connection = False

    @property
    def config(self):
        from ovos_utils.log import log_deprecation
        log_deprecation("Reference `user_config`", "2.0.0")
        return self.user_config

    def check_health(self):
        """
        Check the health of the enclosure service and set an error state if the
        service is unhealthy.
        """
        if self.status.state not in (ProcessState.READY, ProcessState.ERROR):
            # Service is starting or stopping; skip health check
            LOG.debug(f"Skipping health check during startup or shutdown. status={self.status.state}")
            return
        try:
            self.bus.client.send(
                    Message("neon.enclosure.health_check",
                            context={"session": {"session_id": "default"}})
                    .serialize())
            if self._status_from_bus_connection:
                self.status.set_ready()
                self._status_from_bus_connection = False
        except Exception as e:
            LOG.error(f"Health check failed: {e}")
            # Log without setting an error state as the bus should reconnect
            self.status.set_error(f"Health check failed: {e}")
            self._status_from_bus_connection = True

    def start(self):
        LOG.debug("Starting PHAL")
        if self.user_config.get('wait_for_gui'):
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

    def shutdown(self):
        LOG.info("Shutting Down")
        try:
            PHAL.shutdown(self)
        except Exception as e:
            LOG.exception(e)
        # TODO: Below should be implemented in ovos-PHAL directly
        for service, clazz in self.drivers.items():
            try:
                if hasattr(clazz, 'shutdown'):
                    LOG.debug(f"Shutting Down {service}")
                    clazz.shutdown()
            except Exception as e:
                LOG.error(f"Error shutting down {service}: {e}")
            del clazz

