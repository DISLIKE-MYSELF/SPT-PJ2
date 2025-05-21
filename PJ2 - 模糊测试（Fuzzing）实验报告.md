# PJ2 - 模糊测试（Fuzzing）实验报告

软件质量保障与测试 

## 一、分工情况

| 姓名  |     学号      | 工作内容 | 分工占比自评 |
|:---:|:-----------:| :------: | :----------: |
| 李佳磊 | 22302010024 |      Mutator 模块负责人：完善 6 个基础变异器，新增一个变异器    |              |
|     |             |          |              |
|     |             |          |              |
|     |             |          |              |
|     |             |          |              |
|     |             |          |              |

---

## 二、Mutator

在本章中，阐述各个 Mutator 的代码及其实现思路，涵盖 AFL 中经典的 bitflip、arithmetic、havoc、interesting 等变异策略，以及一个自行设计的新 Mutator。

---

1. **insert\_random\_character**

   ```python
   def insert_random_character(s: str) -> str:
       pos = random.randint(0, len(s))
       byte = chr(random.randint(32, 127))
       return s[:pos] + byte + s[pos:]
   ```

   **实现思路**：该 Mutator 随机选择字符串中的一个位置 `pos`，并插入一个 ASCII 范围内的随机字符（32\~127，对应可打印字符）。该策略模拟了“增加字段”或“额外符号”类的数据扰动，是 `random havoc` 中常见的一种。

---

2. **flip\_random\_bits**

   ```python
   def flip_random_bits(s: str) -> str:
       if not s:
           return s
       n = random.choice([1, 2, 4])
       bit_len = len(s) * 8
       if bit_len < n:
           return s
       start_bit = random.randint(0, bit_len - n)
       b = bytearray(s.encode())
       for i in range(n):
           bit_index = start_bit + i
           byte_index = bit_index // 8
           bit_offset = bit_index % 8
           b[byte_index] ^= 1 << bit_offset
       return b.decode(errors='ignore')
   ```

   **实现思路**：该 Mutator 实现了类似 AFL 的 bitflip 策略，随机选择相邻的 1、2 或 4 位（bit）进行翻转。通过这种方式，可以测试程序对细微二进制变动的鲁棒性，尤其是协议解析或二进制处理函数的健壮性。

---

3. **arithmetic\_random\_bytes**

   ```python
   def arithmetic_random_bytes(s: str) -> str:
       if not s:
           return s
       n = random.choice([1, 2, 4])
       if len(s) < n:
           return s
       pos = random.randint(0, len(s) - n)
       b = bytearray(s.encode())
       for i in range(n):
           num = b[pos + i]
           delta = random.randint(-35, 35)
           b[pos + i] = (num + delta) % 256
       return b.decode(errors='ignore')
   ```

   **实现思路**：模仿 AFL 的 `arithmetic` 变异策略。该函数选择 N 个字节（1、2 或 4），对它们分别添加一个随机值（\[-35, 35]），通过增减某些字节来发现程序中因整数溢出、边界值错误导致的问题。

---

4. **interesting\_random\_bytes**

   ```python
   def interesting_random_bytes(s: str) -> str:
       interesting_values = {
           1: [0, 1, 0x7f, 0x80, 0xff],
           2: [0, 1, 0x7fff, 0x8000, 0xffff],
           4: [0, 1, 0x7fffffff, 0x80000000, 0xffffffff],
       }
       n = random.choice([1, 2, 4])
       if len(s) < n:
           return s
       pos = random.randint(0, len(s) - n)
       b = bytearray(s.encode())
       value = random.choice(interesting_values[n])
       value_bytes = value.to_bytes(n, byteorder='little', signed=False)
       b[pos:pos + n] = value_bytes
       return b.decode(errors='ignore')
   ```

   **实现思路**：实现了 AFL 中的 `interesting values` 变异策略。使用对目标程序可能构成“危险输入”的值（如 0、最大值、符号边界等）替换随机位置的字节，常用于探测整数边界条件问题、分支覆盖等漏洞。

---

5. **havoc\_random\_insert**

   ```python
   def havoc_random_insert(s: str) -> str:
       if not s:
           return s
       pos = random.randint(0, len(s))
       if random.random() < 0.75:
           start = random.randint(0, len(s) - 1)
           end = random.randint(start + 1, len(s))
           insert_chunk = s[start:end]
       else:
           insert_chunk = ''.join(chr(random.randint(32, 127)) for _ in range(random.randint(1, 8)))
       return s[:pos] + insert_chunk + s[pos:]
   ```

   **实现思路**：基于 AFL 的 `havoc` 策略，执行随机插入操作。插入内容有 75% 的概率来自原始字符串的某一段，25% 的概率为随机生成的 ASCII 内容，能有效增加输入多样性，测试不同路径。

---

6. **havoc\_random\_replace**

   ```python
   def havoc_random_replace(s: str) -> str:
       if not s:
           return s
       start = random.randint(0, len(s) - 1)
       end = random.randint(start + 1, min(len(s), start + 8))
       if random.random() < 0.75:
           sub_start = random.randint(0, len(s) - 1)
           sub_end = random.randint(sub_start + 1, len(s))
           replace_chunk = s[sub_start:sub_end]
       else:
           replace_chunk = ''.join(chr(random.randint(32, 127)) for _ in range(end - start))
       return s[:start] + replace_chunk + s[end:]
   ```

   **实现思路**：同样基于 AFL 的 `havoc` 机制，进行随机替换。将字符串中一段内容替换为原文中的片段或随机生成的字符，用于模拟真实通信中被破坏的字段数据。

---

7. **delete\_random\_chunk**（新增）

   ```python
   def delete_random_chunk(s: str) -> str:
       if len(s) == 0:
           return s
       delete_len = random.randint(1, min(10, len(s)))
       pos = random.randint(0, len(s) - delete_len)
       return s[:pos] + s[pos + delete_len:]
   ```

   **实现思路**：该 Mutator 是新增的，灵感来自 `chunk deletion` 策略。其作用是从输入中删除一段随机长度（最多 10 字符）的字符串，用于模拟输入被截断、缺失字段等场景，有助于暴露解析函数的健壮性问题。

---
## 三、Schedule

`在本章中，你需要阐述你新增编写的 Schedule 的实现思路,以下为示例`

1. LevelPowerSchedule

   ```python
   class LevelPowerSchedule(Schedule):
   
       def assign_energy(self, population: Sequence[Seed]) -> None:
           ...
   
   ```

   实现思路：基于种子变异的层级...

## 四、新增功能实现介绍

`介绍你们在实现将 input 动态存储本地的过程中的设计思路以及实现效果`
