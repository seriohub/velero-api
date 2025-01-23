import logging
import typing as t
# from uvicorn.config import LOGGING_CONFIG


class EndpointFilter(logging.Filter):
    def __init__(
        self,
        path: str,
        *args: t.Any,
        **kwargs: t.Any,
    ):
        super().__init__(*args, **kwargs)
        self._path = path

    def filter(self, record: logging.LogRecord) -> bool:
        return record.getMessage().find(self._path) == -1


# LOGGING_CONFIG["formatters"]["default"]["fmt"] = "%(levelprefix)s %(asctime)s [%(name)s] %(message)s"
# LOGGING_CONFIG["formatters"]["access"]["fmt"] = "%(levelprefix)s %(asctime)s [%(name)s] %(message)s"
uvicorn_logger = logging.getLogger("uvicorn.access")
uvicorn_logger.addFilter(EndpointFilter(path="/stats/in-progress"))
