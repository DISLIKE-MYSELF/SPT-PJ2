import math
import random
import struct
from typing import Any


def insert_random_character(s: str) -> str:
    pos = random.randint(0, len(s))  # 包含 len(s)，允许插在末尾
    rand_char = chr(random.randint(32, 127))
    return s[:pos] + rand_char + s[pos:]


def flip_random_bits(s: str) -> str:
    if not s:
        return s

    N = random.choice([1, 2, 4])
    total_bits = len(s) * 8
    if total_bits < N:
        return s  # 不足 N 位

    bit_pos = random.randint(0, total_bits - N)
    byte_index = bit_pos // 8
    bit_offset = bit_pos % 8

    b = bytearray(s.encode('latin1'))
    for i in range(N):
        current_bit_pos = bit_pos + i
        idx = current_bit_pos // 8
        offset = current_bit_pos % 8
        b[idx] ^= 1 << offset

    return b.decode('latin1', errors='ignore')


def arithmetic_random_bytes(s: str) -> str:
    if not s:
        return s

    N = random.choice([1, 2, 4])
    if len(s) < N:
        return s

    pos = random.randint(0, len(s) - N)
    b = bytearray(s.encode('latin1'))

    for i in range(N):
        num = b[pos + i]
        delta = random.randint(-35, 35)
        b[pos + i] = (num + delta) % 256  # 保证在合法 byte 范围内

    return b.decode('latin1', errors='ignore')


def interesting_random_bytes(s: str) -> str:
    if not s:
        return s

    interesting_1 = [0, 1, 16, 32, 64, 100, 127, 128, 255]
    interesting_2 = [0, 256, 512, 1024, 0x7FFF, 0x8000, 0xFFFF]
    interesting_4 = [0x00000000, 0x7FFFFFFF, 0x80000000, 0xFFFFFFFF]

    N = random.choice([1, 2, 4])
    if len(s) < N:
        return s

    pos = random.randint(0, len(s) - N)
    b = bytearray(s.encode('latin1'))

    if N == 1:
        val = random.choice(interesting_1)
        b[pos] = val % 256
    elif N == 2:
        val = random.choice(interesting_2)
        for i in range(2):
            b[pos + i] = (val >> (8 * i)) & 0xFF
    elif N == 4:
        val = random.choice(interesting_4)
        for i in range(4):
            b[pos + i] = (val >> (8 * i)) & 0xFF

    return b.decode('latin1', errors='ignore')



def havoc_random_insert(s: str):
    """
    基于 AFL 变异算法策略中的 random havoc 实现随机插入
    随机选取一个位置，插入一段的内容，其中 75% 的概率是插入原文中的任意一段随机长度的内容，25% 的概率是插入一段随机长度的 bytes
    """
    # TODO
    return s

def havoc_random_insert(s: str) -> str:
    pos = random.randint(0, len(s))
    insert_len = random.randint(1, 10)
    if random.random() < 0.75 and len(s) > 0:
        start = random.randint(0, len(s) - 1)
        end = min(len(s), start + insert_len)
        snippet = s[start:end]
    else:
        snippet = ''.join(chr(random.randint(32, 127)) for _ in range(insert_len))

    return s[:pos] + snippet + s[pos:]

def havoc_random_replace(s: str) -> str:
    if len(s) == 0:
        return s

    replace_len = random.randint(1, min(10, len(s)))
    pos = random.randint(0, len(s) - replace_len)
    if random.random() < 0.75 and len(s) > replace_len:
        start = random.randint(0, len(s) - replace_len)
        snippet = s[start:start + replace_len]
    else:
        snippet = ''.join(chr(random.randint(32, 127)) for _ in range(replace_len))

    return s[:pos] + snippet + s[pos + replace_len:]


def delete_random_chunk(s: str) -> str:
    """
    随机删除 s 中的一段内容（chunk deletion），模拟字段缺失或数据截断等情况
    删除长度为 [1, min(10, len(s))]，位置随机
    """
    if len(s) == 0:
        return s

    delete_len = random.randint(1, min(10, len(s)))
    pos = random.randint(0, len(s) - delete_len)

    return s[:pos] + s[pos + delete_len:]



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
            delete_random_chunk
        ]

    def mutate(self, inp: Any) -> Any:
        mutator = random.choice(self.mutators)
        return mutator(inp)
