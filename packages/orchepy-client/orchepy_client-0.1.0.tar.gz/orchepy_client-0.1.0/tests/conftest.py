import pytest


@pytest.fixture
def asyncio_backend() -> str:
    return "asyncio"
