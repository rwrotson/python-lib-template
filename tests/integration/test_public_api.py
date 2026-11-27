import pytest

import my_lib


@pytest.mark.enable_socket
def test_greet_end_to_end() -> None:
    assert my_lib.greet("World") == "Hello, World!"
