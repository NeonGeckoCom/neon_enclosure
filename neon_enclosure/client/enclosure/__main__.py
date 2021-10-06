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
#
"""Entrypoint for enclosure service.

This provides any "enclosure" specific functionality, for example GUI or
control over the Mark-1 Faceplate.
"""
from mycroft.util.process_utils import StatusCallbackMap, ProcessStatus

from neon_enclosure.util.hardware_capabilities import EnclosureCapabilities

from neon_utils.configuration_utils import get_neon_device_type
from ovos_utils import wait_for_exit_signal
from neon_utils import LOG

from mycroft.util import reset_sigint_handler


def on_ready():
    LOG.info("Enclosure started!")


def on_stopping():
    LOG.info('Enclosure is shutting down...')


def on_error(e='Unknown'):
    LOG.error('Enclosure failed: {}'.format(repr(e)))


def create_enclosure(platform):
    """Create an enclosure based on the provided platform string.

    Arguments:
        platform (str): platform name string

    Returns:
        Enclosure object
    """
    if platform == "mycroft_mark_2":
        LOG.info("Creating Mark II Enclosure")
        from neon_enclosure.client.enclosure.mark2 import EnclosureMark2
        enclosure = EnclosureMark2()
    elif platform in ("linux", "ubuntu"):
        from neon_enclosure.client.enclosure.linux import EnclosureLinux
        enclosure = EnclosureLinux()
    else:
        LOG.info("Creating generic enclosure, platform='{}'".format(platform))

        # TODO: Mechanism to load from elsewhere.  E.g. read a script path from
        # the mycroft.conf, then load/launch that script.
        from neon_enclosure.client.enclosure.generic import EnclosureGeneric
        enclosure = EnclosureGeneric()

    return enclosure


def main(ready_hook=on_ready, error_hook=on_error, stopping_hook=on_stopping, config: dict = None):
    """Launch one of the available enclosure implementations.

    This depends on the configured platform and can currently either be
    mycroft_mark_1 or mycroft_mark_2, if unconfigured a generic enclosure with
    only the GUI bus will be started.
    """
    # Read the system configuration
    # system_config = LocalConf(SYSTEM_CONFIG)
    # platform = system_config.get("enclosure", {}).get("platform")
    config = config or dict()
    platform = config.get("platform") or get_neon_device_type()
    enclosure = create_enclosure(platform)

    if enclosure:
        callbacks = StatusCallbackMap(on_ready=ready_hook, on_error=error_hook,
                                      on_stopping=stopping_hook)
        status = ProcessStatus('enclosure', enclosure.bus, callbacks)

        # crude attempt to deal with hardware beyond custom hat
        # note - if using a Mark2 you will also have
        # enclosure.m2enc.capabilities
        enclosure.default_caps = EnclosureCapabilities()

        LOG.info(f"{platform} Enclosure created")

        if platform == "mycroft_mark_2":
            LOG.info("Mark2 detected[%s], additional capabilities ===>%s" % (enclosure.m2enc.board_type,
                                                                             enclosure.m2enc.capabilities))
            LOG.info("Leds ===>%s" % (enclosure.m2enc.leds.capabilities))
            LOG.info("Volume ===>%s" % (enclosure.m2enc.hardware_volume.capabilities))
            LOG.info("Switches ===>%s" % (enclosure.m2enc.switches.capabilities))

        try:
            LOG.info("Starting Client Enclosure!")
            reset_sigint_handler()
            enclosure.run()
            status.set_ready()
            wait_for_exit_signal()
            enclosure.stop()
            status.set_stopping()
        except Exception as e:
            status.set_error(e)
    else:
        LOG.info("No enclosure available for this hardware, running headless")


if __name__ == "__main__":
    main()
