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
from neon_utils import LOG

from neon_enclosure.enclosure.audio.audio_system import AudioSystem
import pulsectl


class PulseAudio(AudioSystem):
    def __init__(self):
        self.pulse = pulsectl.Pulse("OVOS-Enclosure")
        self._sink = self.pulse.sink_list()[0]  # TODO: Better method for this DM

    @staticmethod
    def _translate_level(level: int) -> float:
        return float(level/100)

    def set_volume(self, vol: int):
        try:
            self.pulse.volume_set_all_chans(self._sink, self._translate_level(vol))
        except Exception as e:
            LOG.error(e)

    def get_volume(self) -> int:
        try:
            volume = 100 * self.pulse.volume_get_all_chans(self._sink)
            return volume
        except Exception as e:
            LOG.error(e)
            return -1

    def set_mute(self, mute: bool):
        self.pulse.mute(self._sink, mute)

    def get_mute_state(self) -> bool:
        return self._sink.mute == 1

    def set_input_level(self, level: int):
        pass

    def get_input_level(self) -> int:
        pass

    def set_input_mute(self, mute: bool):
        pass

    def get_input_mute(self) -> bool:
        pass

    def set_program_volume(self, program: str, level: int):
        pass

    def get_program_volume(self, program: str) -> int:
        pass
