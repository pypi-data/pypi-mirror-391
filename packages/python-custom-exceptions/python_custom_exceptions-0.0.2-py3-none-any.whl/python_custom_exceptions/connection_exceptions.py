from python_custom_exceptions.base_custom_exception import BaseCustomException, DiagnosticInfo


class ConnectionException(BaseCustomException):
    def __init__(
        self,
        host: str | None,
        message: str | None = None,
        diagnostic_info: dict | DiagnosticInfo | None = None,
    ) -> None:
        message = (
            (
                f'Connection failed: Unable to establish a connection to the remote host ["{host}"]. '
                f"Please check your credentials, network status, and host availability."
            )
            if not message
            else message
        )

        super().__init__(
            message_with_marking_dynamic_variables=message,
            diagnostic_info=diagnostic_info,
        )
