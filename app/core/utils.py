from enum import Enum

from aiohttp.web import json_response as aiohttp_json_response


def error_json_response(
    http_status: int,
    status: str = "error",
    message: str | None = None,
    data: dict | None = None,
):
    return aiohttp_json_response(
        data={
            "status": status,
            "message": message,
            "data": data,
        },
        status=http_status,
    )


class BetterEnum(Enum):
    def __str__(self):
        return str(self.value)

    def __eq__(self, other):
        return str(self) == str(other)

    def __hash__(self):
        return hash(str(self))
