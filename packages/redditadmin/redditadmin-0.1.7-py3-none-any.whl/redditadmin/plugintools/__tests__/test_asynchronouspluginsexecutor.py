import time
from concurrent.futures import ThreadPoolExecutor
from typing import List

from pytest_mock import MockFixture

from ..asynchronouspluginsexecutor import AsynchronousPluginsExecutor
from ..plugin import Plugin
from ...program.program import AbstractRecurringProgram
from ..redditinterfacefactory import RedditInterfaceFactory


class RecurringProgramTestClass(AbstractRecurringProgram):
    def __init__(self, program_name: str, stop_condition):
        super().__init__(program_name, stop_condition)

    def _run_nature_core(self, *args, **kwargs):
        pass


class TestAsynchronousPluginsExecutor:

    def test_is_not_shutdown(self, mocker):
        plugins = mocker.MagicMock(spec=List[Plugin])
        reddit_interface_factory = mocker.Mock(spec=RedditInterfaceFactory)
        test_instance = AsynchronousPluginsExecutor(
            plugins=plugins,
            reddit_interface_factory=reddit_interface_factory
        )
        assert not test_instance.is_shut_down()

    def test_is_shutdown(self, mocker: MockFixture):
        plugins = mocker.MagicMock(spec=List[Plugin])
        reddit_interface_factory = mocker.Mock(spec=RedditInterfaceFactory)
        test_instance = AsynchronousPluginsExecutor(
            plugins=plugins,
            reddit_interface_factory=reddit_interface_factory
        )
        assert not test_instance.is_shut_down()
        test_instance.shut_down()
        assert test_instance.is_shut_down()

    def test_execute_program_shut_down(self, mocker):

        shutdown_flag = False
        program_command = "testprogramcommand"
        plugin = mocker.Mock(spec=Plugin)
        plugin.configure_mock(**{
            "get_program_command": lambda: program_command,
            "get_program": lambda _: RecurringProgramTestClass(
                program_name=program_command,
                stop_condition=lambda: shutdown_flag
            )
        })
        reddit_interface_factory = mocker.Mock(spec=RedditInterfaceFactory)
        test_instance = AsynchronousPluginsExecutor(
            plugins=[plugin],
            reddit_interface_factory=reddit_interface_factory,
            executor=ThreadPoolExecutor()
        )
        assert test_instance.get_program_statuses()[program_command] == "RUNNING"
        shutdown_flag = True
        test_instance.shut_down()
        assert test_instance.get_program_statuses()[program_command] == "DONE"
        shutdown_flag = False
        test_instance.execute_program(program_command)
        assert test_instance.get_program_statuses()[program_command] == "DONE"

    def test_execute_program_available(self, mocker):
        program_command = "testprogramcommand"
        plugin = mocker.Mock(spec=Plugin)
        plugin.configure_mock(**{"get_program_command": lambda: program_command})
        reddit_interface_factory = mocker.Mock(spec=RedditInterfaceFactory)
        test_instance = AsynchronousPluginsExecutor(
            plugins=[plugin],
            reddit_interface_factory=reddit_interface_factory,
            executor=ThreadPoolExecutor()
        )
        test_instance.execute_program(program_command)  # TODO: Errrrm...
        assert program_command in test_instance.get_program_statuses()

    def test_execute_program_unavailable(self, mocker):
        available_program_command = "testprogramcommand"
        unavailable_program_command = "unavailbleprogramcommand"
        plugin = mocker.Mock(spec=Plugin)
        plugin.configure_mock(**{"get_program_command": lambda: available_program_command})
        reddit_interface_factory = mocker.Mock(spec=RedditInterfaceFactory)
        test_instance = AsynchronousPluginsExecutor(
            plugins=[plugin],
            reddit_interface_factory=reddit_interface_factory,
            executor=ThreadPoolExecutor()
        )
        test_instance.execute_program(unavailable_program_command)
        assert unavailable_program_command not in test_instance.get_program_statuses()

    def test_asynchronous_execution(self, mocker):

        shutdown_flag = False
        program_command_1 = "program1"
        program_command_2 = "program2"
        program_command_3 = "program3"

        reddit_interface_factory = mocker.Mock(spec=RedditInterfaceFactory)
        plugin_1 = mocker.Mock(spec=Plugin)
        plugin_2 = mocker.Mock(spec=Plugin)
        plugin_3 = mocker.Mock(spec=Plugin)

        plugin_1.configure_mock(**{
            "get_program_command": lambda: program_command_1,
            "get_program": lambda _: RecurringProgramTestClass(
                program_name=program_command_1,
                stop_condition=lambda: shutdown_flag
            )
        })
        plugin_2.configure_mock(**{
            "get_program_command": lambda: program_command_2,
            "get_program": lambda _: RecurringProgramTestClass(
                program_name=program_command_2,
                stop_condition=lambda: shutdown_flag
            )
        })
        plugin_3.configure_mock(**{
            "get_program_command": lambda: program_command_3,
            "get_program": lambda _: RecurringProgramTestClass(
                program_name=program_command_3,
                stop_condition=lambda: shutdown_flag
            )
        })

        test_instance = AsynchronousPluginsExecutor(
            plugins=[plugin_1, plugin_2, plugin_3],
            reddit_interface_factory=reddit_interface_factory,
            executor=ThreadPoolExecutor()
        )

        for program_command in [program_command_1, program_command_2, program_command_3]:
            assert test_instance.get_program_statuses()[program_command] == "RUNNING"

        shutdown_flag = True

    def test_get_program_statuses(self, mocker):
        shutdown_flag_1 = False
        shutdown_flag_2 = False

        program_command_1 = "program1"
        program_command_2 = "program2"

        reddit_interface_factory = mocker.Mock(spec=RedditInterfaceFactory)
        plugin_1 = mocker.Mock(spec=Plugin)
        plugin_2 = mocker.Mock(spec=Plugin)

        plugin_1.configure_mock(**{
            "get_program_command": lambda: program_command_1,
            "get_program": lambda _: RecurringProgramTestClass(
                program_name=program_command_1,
                stop_condition=lambda: shutdown_flag_1
            )
        })
        plugin_2.configure_mock(**{
            "get_program_command": lambda: program_command_2,
            "get_program": lambda _: RecurringProgramTestClass(
                program_name=program_command_2,
                stop_condition=lambda: shutdown_flag_2
            )
        })

        test_instance = AsynchronousPluginsExecutor(
            plugins=[plugin_1, plugin_2],
            reddit_interface_factory=reddit_interface_factory,
            executor=ThreadPoolExecutor()
        )

        assert test_instance.get_program_statuses()[program_command_1] == "RUNNING"
        assert test_instance.get_program_statuses()[program_command_2] == "RUNNING"

        shutdown_flag_1 = True
        time.sleep(1)
        assert test_instance.get_program_statuses()[program_command_1] == "DONE"
        assert test_instance.get_program_statuses()[program_command_2] == "RUNNING"

        shutdown_flag_2 = True
        time.sleep(1)
        assert test_instance.get_program_statuses()[program_command_1] == "DONE"
        assert test_instance.get_program_statuses()[program_command_2] == "DONE"
