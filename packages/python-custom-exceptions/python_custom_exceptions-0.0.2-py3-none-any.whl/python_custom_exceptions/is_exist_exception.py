from python_custom_exceptions.base_custom_exception import BaseCustomException, DiagnosticInfo


class IsExistException(BaseCustomException):
    def __init__(
        self,
        subject: str,
        diagnostic_info: dict | DiagnosticInfo | None = None,
    ) -> None:
        message = f"[{subject}] is exists"
        super().__init__(
            message_with_marking_dynamic_variables=message,
            diagnostic_info=diagnostic_info,
        )


class IsNotExistException(BaseCustomException):
    def __init__(
        self,
        subject: str,
        diagnostic_info: dict | DiagnosticInfo | None = None,
    ) -> None:
        message = f"[{subject}] is not exists"
        super().__init__(
            message_with_marking_dynamic_variables=message,
            diagnostic_info=diagnostic_info,
        )
