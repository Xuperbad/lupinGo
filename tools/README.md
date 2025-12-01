# 羊了个羊关卡工具

本目录包含关卡生成器和可视化验证工具。

## 📦 依赖安装

```bash
# 可视化GUI模式需要（可选）
pip install pygame
```

## 🎮 关卡生成器 (level_generator.py)

生成保证100%可解的关卡配置。

### 基本用法

```bash
# 生成一个普通难度关卡
python tools/level_generator.py

# 指定难度
python tools/level_generator.py -d easy      # 简单
python tools/level_generator.py -d normal    # 普通（默认）
python tools/level_generator.py -d hard      # 困难
python tools/level_generator.py -d hell      # 地狱
```

### 参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| `-d, --difficulty` | 难度级别 | `-d hard` |
| `-n, --count` | 生成数量 | `-n 5` |
| `-v, --verify` | 验证可解性 | `-v` |
| `--stats` | 显示统计信息 | `--stats` |

### 示例

```bash
# 生成5个困难关卡，显示统计和验证结果，并保存到文件
python tools/level_generator.py -d hell -n 5 --stats -v -o levels_hell.txt

# 生成关卡并保存到文件
python tools/level_generator.py -d hell > level.txt
```

### 难度配置

| 难度   | 层数 | 类型数 | 总卡片数 |
| ------ | ---- | ------ | -------- |
| easy   | 2    | 4      | 24       |
| normal | 3    | 5      | 45       |
| hard   | 4    | 6      | 54       |
| hell   | 5    | 8      | 72       |

### 难度参数说明

难度由三个核心参数控制：

| 参数             | 含义               | 说明                           |
| ---------------- | ------------------ | ------------------------------ |
| `layers`         | 层数               | 关卡堆叠层数，z=0 为最底层     |
| `type_count`     | 卡片类型数量       | 不同类型的卡片种类数           |
| `cards_per_type` | 每种类型的组数     | 每种类型有几组，每组固定3张    |

**总卡片数计算公式**：
```
总卡片数 = type_count × cards_per_type × 3
```

**示例**：`layers=5, type_count=4, cards_per_type=2`
- 5层堆叠
- 4种卡片类型（0, 1, 2, 3）
- 每种类型 2组 × 3张 = 6张
- 总共 4 × 6 = 24 张卡片

**难度影响**：
| 参数增大       | 影响                                   |
| -------------- | -------------------------------------- |
| `layers` ↑     | 遮挡关系更复杂，需要更多步骤解锁底层   |
| `type_count` ↑ | 匹配更难，槽位更容易满                 |
| `cards_per_type` ↑ | 卡片总数增加，关卡更长            |

### 输出格式

```
{[z, y, x, type], [z, y, x, type], ...}
```

- `z`: 层级（0为最底层）
- `y`: Y坐标（行）
- `x`: X坐标（列）
- `type`: 卡片类型

---

## 🔍 可视化工具 (level_visualizer.py)

可视化展示关卡配置，支持文本和图形两种模式。

### 基本用法

```bash
# 直接输入关卡字符串
python tools/level_visualizer.py "{[0, 2, 4, 3], [1, 1, 5, 2]}"

# 从文件读取
python tools/level_visualizer.py -f level.txt

# 模拟游戏过程
python tools/level_visualizer.py -f level.txt -s

# 图形界面模式（需要pygame）
python tools/level_visualizer.py -f level.txt --gui
```

### 参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| `level` | 关卡配置字符串 | `"{[0,2,4,3]}"` |
| `-f, --file` | 从文件读取 | `-f level.txt` |
| `-s, --simulate` | 模拟游戏过程 | `-s` |
| `--gui` | 图形界面模式 | `--gui` |

### 文本模式输出说明

```
--- 第 1 层 (10 张卡片) ---
    0 1 2 3 4 5 6 7 8 91011
 0 · · · · · 2 2 · 0 0 · ·
 1 · · · · · 2 2 · 0 0 · ·
```

- **大写/数字**: 可点击的卡片
- **小写**: 被遮挡的卡片
- **·**: 空位
- 每张卡片显示为 2×2 区域

### GUI模式操作

| 按键 | 功能 |
|------|------|
| ↑ | 查看上一层 |
| ↓ | 查看下一层 |
| ESC | 退出 |

---

## 🔄 组合使用

```bash
# 先生成关卡保存到文件
python tools/level_generator.py -d hard > level.txt

# 再可视化验证
python tools/level_visualizer.py -f level.txt -s

# 或使用GUI模式
python tools/level_visualizer.py -f level.txt --gui

# 或直接玩默认的 level.txt
python tools/level_player.py

# 取第一行测试
python tools/level_player.py levels_normal.txt
```

> ⚠️ 注意：使用 `-f level.txt` 前，必须先生成 level.txt 文件

---

## 📐 规则说明

1. **卡片占位**: 每张卡片占据 2×2 格子
2. **网格大小**: 12×12（卡片坐标范围 0-10）
3. **遮挡规则**: 上层卡片遮挡其下方 2×2 区域内的所有卡片
4. **消除规则**: 3张同类型卡片消除
5. **槽位限制**: 7个槽位
6. **可解性**: 生成器采用逆向生成法，保证100%可解

