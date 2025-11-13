from ..plugin import AbstractPlugin, T
from ...utility.redditinterface import RedditInterface


class AbstractPluginTestClass(AbstractPlugin):

    def __init__(self, program_command: str):
        super().__init__(program_command)

    def get_program(self, reddit_interface: RedditInterface) -> T:
        pass


class TestAbstractPlugin:

    def test_program_command(self):
        program_command = "testprgoramcommand"
        test_instance = AbstractPluginTestClass(program_command=program_command)
        assert test_instance.get_program_command() == program_command

    def test_is_not_shutdown(self):
        program_command = "random_stuff"
        test_instance = AbstractPluginTestClass(program_command=program_command)
        assert not test_instance.is_shut_down()

    def test_is_shutdown(self):
        program_command = "random_stuff"
        test_instance = AbstractPluginTestClass(program_command=program_command)
        assert not test_instance.is_shut_down()
        test_instance.shut_down()
        assert test_instance.is_shut_down()

    def test_equality(self):
        program_command1 = "thisnthat"
        program_command2 = "thatnthatnthis"
        test_instance1 = AbstractPluginTestClass(program_command=program_command1)
        test_instance2 = AbstractPluginTestClass(program_command=program_command1)
        test_instance3 = AbstractPluginTestClass(program_command=program_command2)

        assert test_instance1 == test_instance2
        assert test_instance1 != test_instance3
