import random
from typing import Sequence
from schedule.PowerSchedule import PowerSchedule
from utils.Seed import Seed


class RandomSchedule(PowerSchedule):
    def __init__(self) -> None:
        super().__init__()

    def assign_energy(self, population: Sequence[Seed]) -> None:
        """随机调度，每个 Seed 能量均等分配"""
        if not population:
            return
        # 平均分配能量
        energy = 1.0 / len(population)
        for seed in population:
            seed.energy = energy

    def choose_seed(self, population: Sequence[Seed]) -> Seed:
        """随机选择一个 Seed"""
        if not population:
            raise ValueError("Population is empty")
        return random.choice(population)
