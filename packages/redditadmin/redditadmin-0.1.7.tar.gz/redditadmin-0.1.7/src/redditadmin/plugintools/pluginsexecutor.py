# -*- coding: utf-8 -*-

import logging
from abc import ABCMeta, abstractmethod
from typing import Dict

from ..utility.miscellaneous import InitializationError


class PluginsExecutor(metaclass=ABCMeta):
    """
    Executes plugins
    """

    @abstractmethod
    def execute_program(self, program_command):
        """Execute the provided program command"""
        ...

    @abstractmethod
    def get_program_statuses(self) -> Dict[str, str]:
        """Get the executed program statuses"""
        ...

    @abstractmethod
    def shut_down(self, *args):
        """Shut down the plugins executor"""
        ...

    @abstractmethod
    def is_shut_down(self) -> bool:
        """Check if the Plugins Executor is shut down"""
        ...


class AbstractPluginsExecutor(PluginsExecutor, metaclass=ABCMeta):

    _isPluginsExecutorShutDown: bool
    _pluginsExecutorLogger: logging.Logger

    def __init__(self, plugins_executor_name: str):
        self._pluginsExecutorLogger = logging.getLogger(
            plugins_executor_name
        )
        self._isPluginsExecutorShutDown = False

    def shut_down(self, *args):

        self._isPluginsExecutorShutDown = True

    def is_shut_down(self) -> bool:

        return self._isPluginsExecutorShutDown

    def _inform_if_shut_down(self):
        """
        Convenience method to check shutdown status and log
        if plugins executor is shut down
        """

        if self._isPluginsExecutorShutDown:
            self._pluginsExecutorLogger.warning(
                "The plugins executor cannot execute any more program "
                "after it has been shut down"
            )


class PluginsExecutorInitializationError(InitializationError):
    """
    Raised when initialization of a Plugins Executor module fails
    """

    def __init__(self, *args):
        super().__init__(*args)
