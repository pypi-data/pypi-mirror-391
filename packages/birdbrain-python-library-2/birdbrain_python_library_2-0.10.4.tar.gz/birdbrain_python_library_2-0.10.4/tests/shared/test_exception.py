import pytest

from birdbrain.exception import Exception
from birdbrain.hummingbird import Hummingbird

def test_exception():
    exception = Exception("MESSAGE")

    assert str(exception) == "MESSAGE"

def test_exception_stop_all():
    hummingbird = Hummingbird('A')

    exception = Exception("STOP", hummingbird)

    assert str(exception) == "STOP"
