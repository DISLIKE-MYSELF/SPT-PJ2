# PJ2 - 模糊测试（Fuzzing）实验报告

软件质量保障与测试 

## 一、分工情况

|  姓名  |    学号     |                           工作内容                           | 分工占比自评 |
| :----: | :---------: | :----------------------------------------------------------: | :----------: |
| 李佳磊 | 22302010024 |   Mutator 模块负责人：完善 6 个基础变异器，新增一个变异器    |     25%      |
| 薛浩南 | 22302010068 | PowerSchedule 模块负责人：实现 PathPowerSchedule 和一个新策略 |     25%      |
| 刘育麟 | 22302010046 | 实验负责人：运行 Sample1~4 测试，收集 crash 与 covered line，保存为 .pkl |     25%      |
| 赏宸宇 | 22300240010 | 工具优化 & 报告负责人：实现输入持久化机制、索引配置表；撰写报告 |     25%      |

---

## 二、Mutator

在本章中，阐述各个 Mutator 的代码及其实现思路，涵盖 AFL 中经典的 bitflip、arithmetic、havoc、interesting 等变异策略，以及一个自行设计的新 Mutator。

---

1. **insert\_random\_character**

   ```python
   def insert_random_character(s: str) -> str:
       b = bytearray(s.encode('utf-8', errors='ignore'))
       pos = random.randint(0, len(b))
       b.insert(pos, random.randint(32, 127))
       return b.decode('utf-8', errors='ignore')
   ```
   
   **实现思路**：该 Mutator 随机选择字符串中的一个位置 `pos`，并插入一个 ASCII 范围内的随机字符（32\~127，对应可打印字符）。该策略模拟了“增加字段”或“额外符号”类的数据扰动，是 `random havoc` 中常见的一种。

---

2. **flip\_random\_bits**

   ```python
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
   ```
   
   **实现思路**：该 Mutator 实现了类似 AFL 的 bitflip 策略，随机选择相邻的 1、2 或 4 位（bit）进行翻转。通过这种方式，可以测试程序对细微二进制变动的鲁棒性，尤其是协议解析或二进制处理函数的健壮性。

---

3. **arithmetic\_random\_bytes**

   ```python
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
   ```
   
   **实现思路**：模仿 AFL 的 `arithmetic` 变异策略。该函数选择 N 个字节（1、2 或 4），对它们分别添加一个随机值（\[-35, 35]），通过增减某些字节来发现程序中因整数溢出、边界值错误导致的问题。

---

4. **interesting\_random\_bytes**

   ```python
   
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
   
   
   ```
   
   **实现思路**：实现了 AFL 中的 `interesting values` 变异策略。使用对目标程序可能构成“危险输入”的值（如 0、最大值、符号边界等）替换随机位置的字节，常用于探测整数边界条件问题、分支覆盖等漏洞。

---

5. **havoc\_random\_insert**

   ```python
   
   
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
   
   ```
   
   **实现思路**：基于 AFL 的 `havoc` 策略，执行随机插入操作。插入内容有 75% 的概率来自原始字符串的某一段，25% 的概率为随机生成的 ASCII 内容，能有效增加输入多样性，测试不同路径。

---

6. **havoc\_random\_replace**

   ```python
   
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
   
   
   ```
   
   **实现思路**：同样基于 AFL 的 `havoc` 机制，进行随机替换。将字符串中一段内容替换为原文中的片段或随机生成的字符，用于模拟真实通信中被破坏的字段数据。

---

7. **delete\_random\_chunk**（新增）

   ```python
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
   
   ```
   
   **实现思路**：该 Mutator 是新增的，灵感来自 `chunk deletion` 策略。其作用是从输入中删除一段随机长度（最多 10 字符）的字符串，用于模拟输入被截断、缺失字段等场景，有助于暴露解析函数的健壮性问题。

---
## 三、Schedule

```
在本章中，阐述新增编写的 Schedule 的实现思路
```

1. **PathPowerSchedule**
```python
class PathPowerSchedule(PowerSchedule):
    def __init__(self, power: float = 1.0) -> None:
        super().__init__()
        self.path_frequency: Dict[str, int] = {}
        self.power = power

    def assign_energy(self, population: Sequence[Seed]) -> None:
        self.path_frequency.clear()
        for seed in population:
            path_id = getattr(seed, "path_id", None)
            if path_id is None:
                continue
            self.path_frequency[path_id] = self.path_frequency.get(path_id, 0) + 1

        total_energy = 0.0
        energies = []
        for seed in population:
            freq = self.path_frequency.get(getattr(seed, "path_id", ""), 1)
            energy = (1.0 / freq) ** self.power
            energies.append(energy)
            total_energy += energy

        for seed, energy in zip(population, energies):
            seed.energy = energy / total_energy if total_energy > 0 else 0.0
```
**实现思路**：基于路径覆盖稀缺性动态分配能量的调度策略。该方案通过统计种子触发的路径ID频率构建观测体系，针对每个种子计算能量时采用逆向频率指数加权算法：

- 路径追踪：利用path_id字段统计各路径在种群中的出现次数，记录低频路径特征
- 能量计算：将能量值设定为路径频率倒数的power次方（公式：$energy = (1/freq)^power$），当power > 1时放大低频路径优势，0 < power < 1时缩小差异
- 归一化分配：将所有种子的能量值归一化为概率分布，确保总能量为1

2.**RandomSchedule**

```python
class RandomSchedule(PowerSchedule):
    def __init__(self) -> None:
        super().__init__()

    def assign_energy(self, population: Sequence[Seed]) -> None:
        if not population:
            return
        energy = 1.0 / len(population)
        for seed in population:
            seed.energy = energy

    def choose_seed(self, population: Sequence[Seed]) -> Seed:
        if not population:
            raise ValueError("Population is empty")
        return random.choice(population)
```
**实现思路**：基于完全随机原则的基准调度策略。该方案采用无差别分配机制实现以下特性：

- 均等能量分配：将总能量均匀分配给所有种子（公式：energy = 1 / population_size），确保每个种子在初始阶段具有相同的选择概率
- 随机选择机制：通过`random.choice`函数进行无偏随机选择，消除任何启发式策略的导向性
- 零状态依赖：不追踪路径覆盖、变异层级等状态信息，决策过程完全独立于历史数据

## 四、新增功能实现介绍

`介绍你们在实现将 input 动态存储本地的过程中的设计思路以及实现效果`
