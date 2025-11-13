from typing import Callable

import pytest
from ..streamprocessingprogram import AbstractStreamProcessingProgram, StreamFactory


class AbstractStreamProcessingProgramTestClass(AbstractStreamProcessingProgram):

    def __init__(self, stream_factory: StreamFactory, stop_condition: Callable[..., bool], program_name: str):
        super().__init__(stream_factory, stop_condition, program_name)

    def _run_nature_core(self, *args, **kwargs):
        self._stop_condition = True


class TestAbstractStreamProcessingProgram:

    def test_something(self):
        assert True
