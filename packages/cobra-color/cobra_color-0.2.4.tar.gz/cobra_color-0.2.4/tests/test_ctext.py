# tests/test_ctext.py
from cobra_color import ctext


def test_ctext():
    for i in range(0, 256):
        a = ctext("\u2588", fg=(0, 0, i))
        assert isinstance(a, str)
        print(a, end="")
        if (i + 1) % 32 == 0:
            print()
