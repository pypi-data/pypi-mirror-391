# tests/test_font.py
from cobra_color.draw import fmt_font, FontName


def test_fmt_font():
    result = fmt_font(
        "Hello, cobra-color!",
        font=FontName.LLDISCO,
        trim_border=True,
        mode="half-gray",
        font_size=10,
        fore_rgb=(255, 120, 0),
        back_rgb=(0, 120, 0)
    )
    assert isinstance(result, str)
