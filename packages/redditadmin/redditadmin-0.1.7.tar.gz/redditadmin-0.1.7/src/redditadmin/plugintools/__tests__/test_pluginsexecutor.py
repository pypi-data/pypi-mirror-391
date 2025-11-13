from typing import Dict
from ..pluginsexecutor import AbstractPluginsExecutor


class AbstractPluginsExecutorTestClass(AbstractPluginsExecutor):

    def get_program_statuses(self) -> Dict[str, str]:
        pass

    def execute_program(self, program_command):
        pass


class TestAbstractPluginsExecutor:

    def test_is_not_shutdown(self):
        plugins_executor_name = "random_stuff"
        test_instance = AbstractPluginsExecutorTestClass(plugins_executor_name=plugins_executor_name)
        assert not test_instance.is_shut_down()

    def test_is_shutdown(self):
        plugins_executor_name = "random_stuff"
        test_instance = AbstractPluginsExecutorTestClass(plugins_executor_name=plugins_executor_name)
        assert not test_instance.is_shut_down()
        test_instance.shut_down()
        assert test_instance.is_shut_down()
