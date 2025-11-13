# -*- coding: utf-8 -*-

import concurrent.futures
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Dict, List
from .pluginsexecutor import AbstractPluginsExecutor, PluginsExecutorInitializationError
from .redditinterfacefactory import RedditInterfaceFactory
from .plugin import Plugin


class AsynchronousPluginsExecutor(AbstractPluginsExecutor):
    """
    Executes multiple plugins in different threads
    """

    __executor: ThreadPoolExecutor
    __plugins: Dict[str, Plugin]
    __executedPrograms: Dict[str, Future]

    def __init__(
            self,
            plugins: List[Plugin],
            reddit_interface_factory: RedditInterfaceFactory,
            executor=ThreadPoolExecutor(),
    ):
        super().__init__("Asynchronous Plugins Executor")
        self.__executor = executor
        self.__plugins = dict(
            map(
                lambda plugin: (plugin.get_program_command(), plugin), plugins
            )
        )
        self.__executedPrograms = {}
        self.__redditInterfaceFactory = reddit_interface_factory
        self.__initialize_plugins_executor()

    def __initialize_plugins_executor(self):
        """Initialize the plugins executor"""

        self._pluginsExecutorLogger.debug('Initializing Plugins Executor')

        try:
            # Retrieving initial program commands
            self._pluginsExecutorLogger.debug(
                "Retrieving initial program commands"
            )

            # Executing initial program commands 
            self._pluginsExecutorLogger.debug(
                "Executing initial program commands"
            )
            self.__execute_programs()

        # Handle in case the program executor fails to initialize
        except PluginsExecutorInitializationError as ex:
            self._pluginsExecutorLogger.critical(
                "A terminal error occurred while initializing the Programs "
                "Executor. Error(s): " + str(ex)
            )
            raise ex

        self._isPluginsExecutorShutDown = False
        self._pluginsExecutorLogger.info(
            "Programs Executor initialized"
        )

    def execute_program(self, program_command):

        # Confirm if shut down first
        if self._inform_if_shut_down():
            return

        # Checking if there are duplicate running programs
        if program_command in self.__executedPrograms.keys():
            if not self.__executedPrograms[program_command].done():
                self._pluginsExecutorLogger.warning(
                    "Did not run the '{}' program command "
                    "because an identical command is"
                    " still running".format(program_command)
                )
                return

        # Generating an asynchronous worker thread for the program
        try:
            task = self.__executor.submit(
                self.__process_program,
                program_command
            )
        except RuntimeError:
            self._pluginsExecutorLogger.error(
                "Failed to execute '{}' because the executor is "
                "shutting down or is shut down".format(program_command)
            )
            return

        try:

            raise task.exception(0.1)

        # Add to running program if task was started successfully
        # TODO: To be revised
        except (concurrent.futures.TimeoutError, _PluginExecutionCompletedException):

            self.__executedPrograms[program_command] = task

        # Handle if provided program could not be parsed
        except ValueError as ex:
            self._pluginsExecutorLogger.error(
                "Did not run the '{}' program command "
                "because there was an error parsing the "
                "program command. Error(s): {}".format(
                    program_command, str(ex.args)
                )
            )

        # Handle if plugins task failed to run
        except TypeError as ex:
            self._pluginsExecutorLogger.error(
                "Failed to run the plugins '{}'. Error: {}".format(
                    program_command, str(ex.args)
                ), exc_info=True
            )

    def __execute_programs(self):
        """Execute multiple programs"""

        # Confirm if shut down first
        if self._inform_if_shut_down():
            return

        for program_command in self.__plugins.keys():
            self.execute_program(program_command)

    def __process_program(self, program_command):
        """Synthesize the provided program"""

        program_command_breakdown = program_command.split()
        program_name = program_command_breakdown[0]

        try:

            if program_name in self.__plugins.keys():
                reddit_interface = self.__redditInterfaceFactory.get_reddit_interface()
                self._pluginsExecutorLogger.info(
                    "Running program '{}'".format(program_name)
                )
                self.__plugins[program_name].get_program(reddit_interface).execute()

                # Completion message determination
                if self.is_shut_down():
                    self._pluginsExecutorLogger.info(
                        "{} program instance successfully shut down".format(
                            program_name
                        )
                    )
                else:
                    self._pluginsExecutorLogger.info(
                        "{} program instance completed".format(
                            program_name
                        )
                    )
                raise _PluginExecutionCompletedException

            # Raise error if provided program does not exist
            else:
                raise ValueError(
                    "Program '{}' is not recognized".format(program_name)
                )

        # Handle if provided program not found
        except (ValueError, _PluginExecutionCompletedException) as ex:
            raise ex

        # Handle if unexpected exception crashes a program TODO: Revisit
        except Exception as ex:
            self._pluginsExecutorLogger.error(
                "An unexpected error just caused the '{}' "
                "program to crash. Error: {}".format(
                    program_name, str(ex.args)
                ), exc_info=True
            )

    def get_program_statuses(self):

        program_statuses = \
            {
                program: ("RUNNING" if not task.done() else "DONE")
                for (program, task) in self.__executedPrograms.items()
            }
        return program_statuses

    def shut_down(self, wait: bool = True):

        super().shut_down()
        for plugin in self.__plugins.values():
            plugin.shut_down()
        self.__executor.shutdown(wait)
        self._pluginsExecutorLogger.info(
            "Programs executor successfully shut down"
        )


class _PluginExecutionCompletedException(Exception):
    """
    Raised to signal to executor that plugins
    execution was successfully completed
    """
