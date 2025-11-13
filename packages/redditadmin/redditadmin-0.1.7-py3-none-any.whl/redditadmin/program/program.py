import logging
import time
from abc import ABCMeta, abstractmethod
from typing import Callable


class Program(metaclass=ABCMeta):
    """Encapsulates a simple program/script"""

    @property
    @abstractmethod
    def program_name(self):
        ...

    @abstractmethod
    def execute(self, *args, **kwargs):
        """Execute the program"""
        ...


class RecurringProgram(Program, metaclass=ABCMeta):
    """Encapsulates a looping program type"""

    @abstractmethod
    def _run_nature_core(self, *args, **kwargs):
        """Run core program"""
        ...


class AbstractProgram(Program, metaclass=ABCMeta):

    def __init__(self, program_name: str):
        self.__program_name = program_name
        self._programLogger = logging.getLogger(
            program_name
        )

    @property
    def program_name(self):
        return self.__program_name


class AbstractRecurringProgram(RecurringProgram, AbstractProgram, metaclass=ABCMeta):

    def __init__(
            self,
            program_name: str,
            stop_condition: Callable[..., bool],
            cooldown: float = 0
    ):
        super().__init__(program_name=program_name)
        self._stopCondition = stop_condition
        self._cooldown = cooldown

    def execute(self, *args, **kwargs):
        while not self._stopCondition():
            self._run_nature_core(*args, **kwargs)
            if self._cooldown and self._cooldown > 0:
                time.sleep(self._cooldown)
