from birdbrain.constant import Constant
from birdbrain.finch import Finch
from birdbrain.hummingbird import Hummingbird
from birdbrain.tasks import Tasks


# package name "BirdBrain" no longer supported...use "birdbrain" instead


def test_instantiating_devices_old_way():
    from birdbrain import Constant, Finch, Hummingbird, Tasks

    Constant()
    Finch('B')
    Hummingbird('A')
    Tasks()

    Constant()
    Finch('B')
    Hummingbird('A')
    Tasks()

    assert Constant().LEFT == 'L'

