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

from abc import ABC, abstractmethod


class AudioSystem(ABC):
    """
    ABC for software-based audio controls
    """

    # Audio Output Controls
    @abstractmethod
    def set_volume(self, vol: int):
        """
        Sets the volume to the requested level
        :param vol: int(0,100) level to set output to
        """
        return

    @abstractmethod
    def get_volume(self) -> int:
        """
        Returns the current output level as an int
        :return: int(0,100) current output level
        """
        return -1

    @abstractmethod
    def set_mute(self, mute: bool):
        """
        Sets the audio output mute status
        :param mute: True to mute, False to unmute
        """
        return

    @abstractmethod
    def get_mute_state(self) -> bool:
        """
        Returns the current audio output mute state
        :return: True if output is muted
        """
        return False

    # Audio Input Controls
    @abstractmethod
    def set_input_level(self, level: int):
        """
        Sets the microphone input to the requested level. 
        :param level: int(0,100) level to set input to
        """
        return

    @abstractmethod
    def get_input_level(self) -> int:
        """
        Returns the currnet input level as an int
        :return: int(0,100) current input level
        """
        return -1

    @abstractmethod
    def set_input_mute(self, mute: bool):
        """
        Sets the audio input mute state
        :param mute: True to mute, False to unmute
        """
        return

    @abstractmethod
    def get_input_mute(self) -> bool:
        """
        Returns the current audio input mute state
        :return: True if input is muted
        """
        return False

    # Application Controls
    @abstractmethod
    def set_program_volume(self, program: str, level: int):
        """
        Sets the audio output level of the specified program
        :param program: Name of program/sink
        :param level: int(0,100) level to set program output to
        """
        return

    @abstractmethod
    def get_program_volume(self, program: str) -> int:
        """
        Gets the audio output level of the specified program
        :param program: Name of program/sink
        :return: int(0,100) level of program output, -1 if program not found
        """
        return -1
