from pytest import raises
from prawcore import ServerError, RequestException
from pytest_mock import MockFixture
from requests import Response

from ..decorators import consumestransientapierrors


class TestDecorators:

    def test_consumestransientapierrors(self, mocker: MockFixture):

        response_mock = mocker.Mock(spec=Response)
        response_mock.configure_mock(**{
            "status_code": "500"
        })
        exception_mock = mocker.Mock(spec=Exception)

        error_1 = ServerError(response_mock)
        error_2 = RequestException(
            original_exception=exception_mock,
            request_args=("", ""),
            request_kwargs=dict([("lalala", True)])
        )
        error_3 = AttributeError
        break_flag = False

        @consumestransientapierrors(timeout=0)
        def error_test(error):
            nonlocal break_flag
            if break_flag:
                return
            break_flag = True
            raise error

        error_test(error_1)
        break_flag = False
        error_test(error_2)
        break_flag = False

        with raises(error_3):
            error_test(error_3)
