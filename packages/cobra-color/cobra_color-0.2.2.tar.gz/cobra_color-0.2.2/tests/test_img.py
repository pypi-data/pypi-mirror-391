
import pytest
import sys
sys.path.insert(0, "./src")

from cobra_color.draw import fmt_image


print(fmt_image(
    "/data/tianzhen/my_projects/vanyarlearn/DRAFT/dec8c8639e61c08614e0e87a90f34221.jpg",
    mode="ascii",
    height=30
))


print(fmt_image(
    "/data/tianzhen/my_projects/vanyarlearn/DRAFT/dec8c8639e61c08614e0e87a90f34221.jpg",
    mode="half-color",
    height=30
))
