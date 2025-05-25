import time
from typing import List, Tuple, Any
from runner.Runner import Runner
from fuzzer.GreyBoxFuzzer import GreyBoxFuzzer
from schedule.PathPowerSchedule import PathPowerSchedule
from runner.FunctionCoverageRunner import FunctionCoverageRunner


class PathGreyBoxFuzzer(GreyBoxFuzzer):
    """基于路径频率的模糊测试器"""

    def __init__(self, seeds: List, schedule: PathPowerSchedule, is_print: bool):
        super().__init__(seeds, schedule, False)

        self.path_frequency = {}  # key: path_id, value: 执行次数
        self.last_new_path_time = self.start_time
        self.last_unique_crash_time = self.start_time
        self.is_print = is_print

        print("""
┌───────────────────────┬───────────────────────┬───────────────────────┬───────────────────┬───────────────────┬────────────────┬───────────────────┐
│        Run Time       │     Last New Path     │    Last Uniq Crash    │    Total Execs    │    Total Paths    │  Uniq Crashes  │   Covered Lines   │
├───────────────────────┼───────────────────────┼───────────────────────┼───────────────────┼───────────────────┼────────────────┼───────────────────┤""")

    def print_stats(self):
        def format_seconds(seconds):
            hours = int(seconds) // 3600
            minutes = int(seconds % 3600) // 60
            remaining_seconds = int(seconds) % 60
            return f"{hours:02d}:{minutes:02d}:{remaining_seconds:02d}"

        template = """│{runtime}│{path_time}│{crash_time}│{total_exec}│{total_path}│{uniq_crash}│{covered_line}│
├───────────────────────┼───────────────────────┼───────────────────────┼───────────────────┼───────────────────┼────────────────┼───────────────────┤"""
        template = template.format(
            runtime=format_seconds(time.time() - self.start_time).center(23),
            path_time=format_seconds(self.last_new_path_time - self.start_time).center(23),
            crash_time=format_seconds(self.last_unique_crash_time - self.start_time).center(23),
            total_exec=str(self.total_execs).center(19),
            total_path=str(len(self.path_frequency)).center(19),
            uniq_crash=str(len(set(self.crash_map.values()))).center(16),
            covered_line=str(len(self.covered_line)).center(19)
        )
        print(template)

    def run(self, runner: FunctionCoverageRunner) -> Tuple[Any, str]:
        """执行一次测试，并更新路径频率信息"""

        result, outcome, path_id = super().run(runner)

        # 假设 result 中含有路径ID属性
        # path_id = getattr(result, 'path_id', None)
        if path_id is not None:
            if path_id not in self.path_frequency:
                self.path_frequency[path_id] = 0
                self.last_new_path_time = time.time()
            self.path_frequency[path_id] += 1

        # 更新调度器的路径频率
        if hasattr(self.schedule, 'update_path_frequency'):
            self.schedule.update_path_frequency(self.path_frequency)

        # 检测崩溃并更新时间戳
        if outcome == Runner.FAIL:
            self.last_unique_crash_time = time.time()
            self.crash_map[self.inp] = result

        if self.is_print:
            self.print_stats()

        return result, outcome
