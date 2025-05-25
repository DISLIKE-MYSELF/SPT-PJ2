from typing import Dict, Sequence
from schedule.PowerSchedule import PowerSchedule
from utils.Seed import Seed


class PathPowerSchedule(PowerSchedule):
    def __init__(self, power: float = 1.0) -> None:
        super().__init__()
        # 记录路径频率，key 为路径ID字符串，value 为频率
        self.path_frequency: Dict[str, int] = {}
        self.power = power  # 能量分配的指数权重

    def assign_energy(self, population: Sequence[Seed]) -> None:
        """
        为每个 Seed 分配能量，能量和路径频率的倒数成正比。
        频率越低，能量越大。使用指数调整差异大小。
        """
        # 重新统计路径频率
        self.path_frequency.clear()
        for seed in population:
            path_id = getattr(seed, "path_id", None)
            if path_id is None:
                # 如果 Seed 没有 path_id，可以考虑赋默认值或跳过
                continue
            self.path_frequency[path_id] = self.path_frequency.get(path_id, 0) + 1

        # 计算能量总和，用于归一化
        total_energy = 0.0
        energies = []
        for seed in population:
            freq = self.path_frequency.get(getattr(seed, "path_id", ""), 1)
            energy = (1.0 / freq) ** self.power  # 指数加权
            energies.append(energy)
            total_energy += energy

        # 分配归一化后的能量
        for seed, energy in zip(population, energies):
            seed.energy = energy / total_energy if total_energy > 0 else 0.0
