import math
import random
import struct
from typing import Any, Callable, Tuple


def insert_random_character(s: str) -> str:
    b = bytearray(s.encode('utf-8', errors='ignore'))
    pos = random.randint(0, len(b))
    b.insert(pos, random.randint(32, 127))
    return b.decode('utf-8', errors='ignore')


def flip_random_bits(s: str) -> str:
    b = bytearray(s.encode('utf-8', errors='ignore'))
    N = random.choice([1, 2, 4])
    bit_len = len(b) * 8
    if bit_len < N:
        return s
    bit_pos = random.randint(0, bit_len - N)
    for i in range(N):
        byte_idx = (bit_pos + i) // 8
        bit_idx = (bit_pos + i) % 8
        b[byte_idx] ^= (1 << bit_idx)
    return b.decode('utf-8', errors='ignore')


def arithmetic_random_bytes(s: str) -> str:
    b = bytearray(s.encode('utf-8', errors='ignore'))
    N = random.choice([1, 2, 4])
    if len(b) < N:
        return s
    pos = random.randint(0, len(b) - N)
    for i in range(N):
        delta = random.randint(-35, 35)
        b[pos + i] = (b[pos + i] + delta) % 256
    return b.decode('utf-8', errors='ignore')


def interesting_random_bytes(s: str) -> str:
    interesting_1 = [0, 1, 255, 127]
    interesting_2 = [0, 1, 255, 256, 32767, 65535]
    interesting_4 = [0, 1, 255, 4294967295]

    b = bytearray(s.encode('utf-8', errors='ignore'))
    N = random.choice([1, 2, 4])
    if len(b) < N:
        return s
    pos = random.randint(0, len(b) - N)
    if N == 1:
        val = random.choice(interesting_1)
        b[pos] = val % 256
    elif N == 2:
        val = random.choice(interesting_2)
        val_bytes = val.to_bytes(2, byteorder='little', signed=False)
        b[pos:pos+2] = val_bytes
    else:
        val = random.choice(interesting_4)
        val_bytes = val.to_bytes(4, byteorder='little', signed=False)
        b[pos:pos+4] = val_bytes
    return b.decode('utf-8', errors='ignore')


def delete_random_character(s: str) -> str:
    """
    删除 s 中的一个随机 byte，避免删除多字节字符的一部分导致乱码。
    """
    b = bytearray(s.encode('utf-8', errors='ignore'))
    if len(b) == 0:
        return s
    pos = random.randint(0, len(b) - 1)
    del b[pos]
    return b.decode('utf-8', errors='ignore')


def havoc_random_insert(s: str) -> str:
    b = bytearray(s.encode('utf-8', errors='ignore'))
    pos = random.randint(0, len(b))
    if random.random() < 0.75 and len(b) > 0:
        start = random.randint(0, len(b) - 1)
        end = random.randint(start, len(b))
        segment = b[start:end]
    else:
        segment = bytearray(random.randint(1, 10))
        for i in range(len(segment)):
            segment[i] = random.randint(32, 127)
    b[pos:pos] = segment
    return b.decode('utf-8', errors='ignore')


def havoc_random_replace(s: str) -> str:
    b = bytearray(s.encode('utf-8', errors='ignore'))
    if len(b) == 0:
        return s
    start = random.randint(0, len(b) - 1)
    max_len = len(b) - start
    replace_len = random.randint(1, min(10, max_len))
    if random.random() < 0.75 and len(b) > 1:
        src_start = random.randint(0, len(b) - 1)
        src_end = random.randint(src_start, len(b))
        segment = b[src_start:src_end]
    else:
        segment = bytearray(random.randint(1, replace_len))
        for i in range(len(segment)):
            segment[i] = random.randint(32, 127)
    b[start:start+replace_len] = segment[:replace_len]
    return b.decode('utf-8', errors='ignore')


class Mutator:

    def __init__(self) -> None:
        """Constructor"""
        self.mutators = [
            insert_random_character,
            flip_random_bits,
            arithmetic_random_bytes,
            interesting_random_bytes,
            havoc_random_insert,
            havoc_random_replace,
            delete_random_character  # 新增的 Mutator
        ]

    def mutate(self, inp: Any) -> Tuple[str, str]:
        mutator = random.choice(self.mutators)
        return mutator(inp)


def test_mutator():
    mutator = Mutator()
    test_inputs = [
        "hello world!",         # 英文
        "你好，世界！",           # 中文
        "测试 test 123",        # 中英文混合
        "",                     # 空字符串
        "特殊字符：★☆♥♦♣♠",    # 特殊字符
    ]

    for i, inp in enumerate(test_inputs):
        print(f"\nTest case {i + 1}: 原始输入 -> {repr(inp)}")
        for _ in range(5):
            mutated = mutator.mutate(inp)
            print(f"  -> 变异结果: {repr(mutated)} ")


if __name__ == '__main__':
    test_mutator()
