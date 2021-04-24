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

from neon_enclosure.enclosure.audio.audio_system import AudioSystem
import alsaaudio


class AlsaAudio(AudioSystem):
    def __init__(self):
        self.alsa = alsaaudio.Mixer()

    def set_volume(self, vol: int):
        self.alsa.setvolume(vol)

    def get_volume(self) -> int:
        levels = self.alsa.getvolume()
        volume = sum(levels) / len(levels)
        return volume

    def set_mute(self, mute: bool):
        self.alsa.setmute(mute)

    def get_mute_state(self) -> bool:
        return any([i for i in self.alsa.getmute() if i == 1])

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
