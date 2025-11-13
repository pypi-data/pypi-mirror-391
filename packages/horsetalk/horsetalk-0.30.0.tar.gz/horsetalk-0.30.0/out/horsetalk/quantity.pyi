from _typeshed import Incomplete
from pint import UnitRegistry
from typing import Self

ureg: UnitRegistry
Q_: Incomplete

class HorsetalkQuantity(Q_):
    REGEX: str
    def __new__(cls, *args, **kwargs) -> Self: ...
    def __getattr__(self, attr): ...
