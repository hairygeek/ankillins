import pytest

from ankillins.client import Collins

@pytest.fixture()
def collins_client():
    return Collins()

