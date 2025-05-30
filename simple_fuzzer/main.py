import os
import time

from fuzzer.PathGreyBoxFuzzer import PathGreyBoxFuzzer
from runner.FunctionCoverageRunner import FunctionCoverageRunner
from schedule.PathPowerSchedule import PathPowerSchedule
from samples.Samples import sample1, sample2, sample3, sample4
from utils.ObjectUtils import dump_object, load_object


class Result:
    def __init__(self, coverage, crashes, start_time, end_time):
        self.covered_line = coverage
        self.crashes = crashes
        self.start_time = start_time
        self.end_time = end_time

    def __str__(self):
        return (
            f"Covered Lines: {self.covered_line}, "
            f"Crashes Num: {len(self.crashes)}, "
            f"Start Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.start_time))}, "
            f"End Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.end_time))}"
        )


if __name__ == "__main__":
    # 选择样例程序和对应的语料库
    sample_program = sample4
    corpus_path = "corpus/corpus_4"

    f_runner = FunctionCoverageRunner(sample_program)
    seeds = load_object(corpus_path)

    schedule = PathPowerSchedule(power=5)
    grey_fuzzer = PathGreyBoxFuzzer(seeds=seeds, schedule=schedule, is_print=True)

    start_time = time.time()
    grey_fuzzer.runs(f_runner, run_time=7200)
    end_time = time.time()

    res = Result(
        coverage=grey_fuzzer.covered_line,
        crashes=set(grey_fuzzer.crash_map.values()),
        start_time=start_time,
        end_time=end_time,
    )

    output_dir = "_result"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "Sample-4.pkl")

    dump_object(output_file, res)
    print(load_object(output_file))
