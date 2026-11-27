import logging

from my_lib.core.errors import InvalidInputError
from my_lib.core.log_fields import LOG_FIELDS

logger = logging.getLogger(__name__)


def greet(name: str) -> str:
    """Build a greeting for a non-empty name."""
    if not name.strip():
        raise InvalidInputError("name must not be empty")
    logger.debug("greeting", extra={LOG_FIELDS: {"name": name}})
    return f"Hello, {name}!"
