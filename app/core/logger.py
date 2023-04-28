import logging
import typing

if typing.TYPE_CHECKING:
    from app.core.application import Application


def setup_logging(_: "Application") -> None:
    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s",
        level=logging.INFO,
        datefmt="%d.%m.%Y %H:%M:%S",
    )
