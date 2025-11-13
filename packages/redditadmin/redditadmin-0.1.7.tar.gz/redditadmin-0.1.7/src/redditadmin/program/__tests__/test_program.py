import time
from typing import Callable
from pytest_mock import MockFixture

from ..program import AbstractProgram, AbstractRecurringProgram


class AbstractProgramTestClass(AbstractProgram):

    def __init__(self, program_name: str):
        super().__init__(program_name)

    def execute(self, *args, **kwargs):
        pass


class AbstractRecurringProgramTestClass(AbstractRecurringProgram):

    def __init__(self, program_name: str, stop_condition: Callable[..., bool], cooldown: float = 0):
        super().__init__(
            program_name=program_name,
            stop_condition=stop_condition,
            cooldown=cooldown
        )

    # TODO: Tidy this up
    def _run_nature_core(self, *args, **kwargs):
        self._stopCondition = lambda: True


class TestAbstractProgram:
    """Tests for AbstractProgram"""

    def test_program_name(self):
        program_name = "TestName123"
        test_instance = AbstractProgramTestClass(program_name=program_name)
        assert test_instance.program_name == program_name


class TestAbstractRecurringProgram:
    """Tests for AbstractRecurringProgram"""

    def test_program_name(self):
        program_name = "321Testing"
        stop_condition = lambda: True
        cooldown = 1
        test_instance = AbstractRecurringProgramTestClass(
            program_name=program_name,
            stop_condition=stop_condition,
            cooldown=cooldown
        )
        assert test_instance.program_name == program_name

    def test_execute_stop_true(self, mocker: MockFixture):
        program_name = "offfgkg"
        stop_condition = lambda: True
        cooldown = 1
        test_instance = AbstractRecurringProgramTestClass(
            program_name=program_name,
            stop_condition=stop_condition,
            cooldown=cooldown
        )
        spy = mocker.spy(test_instance, "_run_nature_core")
        test_instance.execute()
        spy.assert_not_called()

    def test_execute_stop_false(self, mocker: MockFixture):
        program_name = "lalala"
        stop_condition = lambda: False
        cooldown = 1
        test_instance = AbstractRecurringProgramTestClass(
            program_name=program_name,
            stop_condition=stop_condition,
            cooldown=cooldown
        )
        spy = mocker.spy(test_instance, "_run_nature_core")
        test_instance.execute()
        spy.assert_called()

    def test_execute_cooldown(self, mocker: MockFixture):
        program_name = "ooolala"
        stop_condition = lambda: False
        cooldown = 2
        test_instance = AbstractRecurringProgramTestClass(
            program_name=program_name,
            stop_condition=stop_condition,
            cooldown=cooldown
        )
        spy = mocker.spy(time, "sleep")
        test_instance.execute()
        spy.assert_called_once_with(cooldown)
