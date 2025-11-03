import math
from dataclasses import dataclass
import random


@dataclass
class Dot:
    x: int
    y: int

    def __init__(self, x: int, y: int):
        self._x = abs(x)
        self._y = abs(y)

    def __sub__(self, other) -> float:
        return Dot(self._x + other.x, self._y + other.y).len

    def __add__(self, other) -> float:
        return Dot(self._x + other.x, self._y + other.y).len

    def __str__(self): return f"{self._x} {self._y}"

    def make_random(self, l_x: int=10, l_y: int=10):
        l_x, l_y = abs(l_x), abs(l_y)
        self._x += random.randint(-l_x, l_x)
        self._y += random.randint(-l_y, l_y)
        return self

    @property
    def x(self) -> int: return self._x

    @property
    def y(self) -> int: return self._y

    @x.setter
    def x(self, value: int): self._x = abs(value)

    @y.setter
    def y(self, value: int): self._y = abs(value)

    @property
    def len(self) -> float:
        return math.sqrt(self._x ** 2 + self._y ** 2)
