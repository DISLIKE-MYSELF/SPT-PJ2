from typing import Set
from utils.Coverage import Location

class Seed:
    """Represent an input with additional attributes"""

    def __init__(self, data: str, _coverage: Set[Location], path_id: str = "") -> None:
        """Initialize from seed data"""
        self.data = data
        self.coverage: Set[Location] = _coverage
        self.energy = 0.0
        self.path_id = path_id  # 新增路径ID属性

    def __str__(self) -> str:
        """Returns data as string representation of the seed"""
        return self.data

    __repr__ = __str__
