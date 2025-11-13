import logging
from abc import ABCMeta, abstractmethod
from typing import TypeVar, Generic

from ..program.program import Program
from ..utility.redditinterface import RedditInterface
from ..utility.miscellaneous import InitializationError

T = TypeVar("T", bound=Program)


class Plugin(Generic[T], metaclass=ABCMeta):
    """
    Generates multiple instances of a specific program
    """

    @abstractmethod
    def get_program(self, reddit_interface: RedditInterface) -> T:
        """Get new program instance"""
        ...

    @abstractmethod
    def get_program_command(self) -> str:
        """Get the program command string"""
        ...

    @abstractmethod
    def is_shut_down(self) -> bool:
        """Check if plugins is shut down"""
        ...

    @abstractmethod
    def shut_down(self):
        """Shut down the plugins"""
        ...


class AbstractPlugin(Plugin[T], metaclass=ABCMeta):

    _programCommand: str
    _pluginLogger: logging.Logger
    _isPluginShutDown: bool

    def __init__(
            self,
            program_command: str,
    ):
        self._programCommand = program_command
        self._pluginLogger = logging.getLogger(
            program_command
        )
        self._isPluginShutDown = False

    def get_program_command(self) -> str:
        return self._programCommand

    def is_shut_down(self) -> bool:
        return self._isPluginShutDown

    def shut_down(self):
        self._isPluginShutDown = True

    def __eq__(self, value) -> bool:
        return isinstance(value, Plugin) and \
               self.get_program_command() == value.get_program_command()


class PluginInitializationError(InitializationError):
    """
    Raised when initialization of a plugins module fails
    """

    def __init__(self, *args):
        super().__init__(*args)
