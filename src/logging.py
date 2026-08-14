import inspect
import logging

_handler = logging.StreamHandler()
_handler.setFormatter(
    logging.Formatter("%(asctime)s [%(levelname)s] (Scope: %(scope)s) %(message)s")
)

base_logger = logging.getLogger("maketravo")
base_logger.setLevel(logging.INFO)
base_logger.addHandler(_handler)
base_logger.propagate = False


def scope_logger(scope: str | None = None) -> logging.LoggerAdapter:
    if scope is None:
        frame = inspect.stack()[1]
        module = inspect.getmodule(frame[0])
        scope = module.__name__ if module else "__unknown__"
    return logging.LoggerAdapter(base_logger, {"scope": scope})
