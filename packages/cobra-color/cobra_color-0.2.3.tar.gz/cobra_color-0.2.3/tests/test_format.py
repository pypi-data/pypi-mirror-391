# import pytest
import sys
sys.path.insert(0, "./src")

from cobra_color import fmt_dict, fmt_list



d = {"a": 2, "b": [1, 2, 3, {"c": 4, "d": [5, 6, 7]}], "e": {"f": 8, "g": 9}}

l = [1, 2, 3, {"a": 4, "b": [5, 6, 7]}, [8, 9, 10], ""]


class A:
    def __init__(self):
        self.a = 1
        self._b = 2
        self.__c = 3

class B(A):
    def __init__(self):
        super().__init__()
        self.d = 4
        self._e = 5
        self.__f = 6

b = B()




fmt_dict(b, omits=["b"], title="Test Dict Print")

# list_print(l)

print(1)


