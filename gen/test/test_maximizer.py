from utils.maximizer import Maximizer


def test_maximizer():
    m = Maximizer()
    m.update(3)
    assert m.get() == 3
    m.update(1)
    assert m.get() == 3
    m.update(10)
    assert m.get() == 10
