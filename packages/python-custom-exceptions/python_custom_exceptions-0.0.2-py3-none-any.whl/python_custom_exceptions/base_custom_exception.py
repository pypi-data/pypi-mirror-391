import json
from dataclasses import is_dataclass
from json import dumps
from typing import TypedDict

from python_base_toolkit.utils.data_serialization import default_serialize


class DiagnosticInfo(TypedDict): ...


def serialize_data(obj: object) -> dict:
    return json.loads(json.dumps(obj, default=default_serialize))


def get_full_exception_message(content: dict) -> str:
    return (
        f'{content["message"]}\n\nCustom Exception Raised!\n'
        f"{dumps(content, indent=4, sort_keys=False, default=str)}"
    )


class BaseCustomException(Exception):
    def __init__(
        self,
        message_with_marking_dynamic_variables: str,
        diagnostic_info: dict | DiagnosticInfo | None = None,
    ) -> None:
        if is_dataclass(diagnostic_info):
            diagnostic_info = diagnostic_info.__dict__

        self.exception_type = type(self).__name__
        self.message = message_with_marking_dynamic_variables
        self.diagnostic_info = diagnostic_info or {}

    def __str__(self) -> str:
        exception_content = {
            "exception_type": self.exception_type,
            "message": self.message,
            "diagnostic_info": self.diagnostic_info,
        }
        # return get_full_exception_message(exception_content)
        return dumps(exception_content, indent=4, sort_keys=False, default=str)

    def __repr__(self) -> str:
        return self.__str__()
