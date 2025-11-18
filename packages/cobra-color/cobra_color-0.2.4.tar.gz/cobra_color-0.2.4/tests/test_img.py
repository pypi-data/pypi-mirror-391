# tests/test_img.py
from cobra_color.draw import fmt_image
from pathlib import Path


def test_fmt_image():
    data_path = Path(__file__).parent / "assets" / "eagle.jpg"
    result = fmt_image(
        str(data_path),
        mode="half-color",
        height=30
    )
    assert isinstance(result, str)


def test_fmt_image_ascii():
    data_path = Path(__file__).parent / "assets" / "eagle.jpg"
    result = fmt_image(
        str(data_path),
        mode="ascii",
        height=30
    )
    assert isinstance(result, str)
