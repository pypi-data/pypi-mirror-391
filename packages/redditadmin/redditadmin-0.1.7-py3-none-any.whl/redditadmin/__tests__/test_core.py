import time
from concurrent.futures import ThreadPoolExecutor

from pytest_mock import MockFixture

from ..core import get_reddit_admin
from ..plugintools.plugin import Plugin
from ..program.program import Program
from ..utility.botcredentials import BotCredentials


class TestRedditAdmin:

    def test_run_plugins(self, mocker: MockFixture):

        program_1 = mocker.Mock(
            spec=Program
        )
        program_2 = mocker.Mock(
            spec=Program
        )
        program_3 = mocker.Mock(
            spec=Program
        )
        plugin_1 = mocker.Mock(
            spec=Plugin,
            get_program=lambda _: program_1,
            get_program_command=lambda: "Plugin_1",
            is_shut_down=lambda: False
        )
        plugin_2 = mocker.Mock(
            spec=Plugin,
            get_program=lambda _: program_2,
            get_program_command=lambda: "Plugin_2",
            is_shut_down=lambda: False
        )
        plugin_3 = mocker.Mock(
            spec=Plugin,
            get_program=lambda _: program_3,
            get_program_command=lambda: "Plugin_3",
            is_shut_down=lambda: False
        )

        reddit_admin = get_reddit_admin([
            plugin_1, plugin_2, plugin_3
        ])
        mocker.patch(
            'src.redditadmin.plugintools.redditinterfacefactory.is_reddit_authenticated',
            lambda _: True
        )
        bot_credentials = mocker.Mock(spec=BotCredentials)
        with ThreadPoolExecutor() as thread_pool_executor:
            thread_pool_executor.submit(
                reddit_admin.run,
                bot_credentials
            )
            time.sleep(5)
            reddit_admin.stop(wait=True)
            program_1.execute.assert_called_once()
            program_2.execute.assert_called_once()
            program_3.execute.assert_called_once()
            mocker.resetall()

    def test_stop(self, mocker: MockFixture):
        is_shutdown = False

        def looping_program():
            while not is_shutdown:
                time.sleep(1)

        program_1 = mocker.Mock(
            spec=Program,
            execute=looping_program
        )
        program_2 = mocker.Mock(
            spec=Program,
            execute=looping_program
        )
        program_3 = mocker.Mock(
            spec=Program,
            execute=looping_program
        )
        plugin_1 = mocker.Mock(
            spec=Plugin,
            get_program=lambda _: program_1,
            get_program_command=lambda: "Plugin_1",
            is_shut_down=lambda: is_shutdown
        )
        plugin_2 = mocker.Mock(
            spec=Plugin,
            get_program=lambda _: program_2,
            get_program_command=lambda: "Plugin_2",
            is_shut_down=lambda: is_shutdown
        )
        plugin_3 = mocker.Mock(
            spec=Plugin,
            get_program=lambda _: program_3,
            get_program_command=lambda: "Plugin_3",
            is_shut_down=lambda: is_shutdown
        )

        reddit_admin = get_reddit_admin([
            plugin_1, plugin_2, plugin_3
        ])
        mocker.patch(
            'src.redditadmin.plugintools.redditinterfacefactory.is_reddit_authenticated',
            lambda _: True
        )
        bot_credentials = mocker.Mock(spec=BotCredentials)
        with ThreadPoolExecutor() as thread_pool_executor:
            thread = thread_pool_executor.submit(
                reddit_admin.run,
                bot_credentials
            )
            time.sleep(5)
            assert thread.running()
            is_shutdown = True
            reddit_admin.stop(wait=True)
            time.sleep(2)
            assert thread.done()
