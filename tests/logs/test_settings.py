import pytest
from pydantic import ValidationError

from my_lib.logs import LogSettings


@pytest.mark.parametrize(
    "file_name", ["", ".", "..", "../outside.log", "nested/app.log", "a\\b.log"]
)
def test_log_file_name_must_be_a_basename(file_name: str) -> None:
    with pytest.raises(ValidationError, match="basename"):
        LogSettings(file_name=file_name)
