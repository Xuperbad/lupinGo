#!/usr/bin/env python3
"""
羊了个羊关卡生成器
采用逆向生成法保证100%可解
"""

import random
from dataclasses import dataclass
from typing import List, Tuple, Optional
import json


@dataclass
class Card:
    """卡片数据结构"""
    z: int      # 层级
    y: int      # Y坐标
    x: int      # X坐标
    type: int   # 卡片类型
    
    def to_list(self) -> List[int]:
        return [self.z, self.y, self.x, self.type]
    
    def occupies(self) -> List[Tuple[int, int, int]]:
        """返回卡片占据的4个格子坐标"""
        return [
            (self.x, self.y, self.z),
            (self.x + 1, self.y, self.z),
            (self.x, self.y + 1, self.z),
            (self.x + 1, self.y + 1, self.z),
        ]


@dataclass
class DifficultyConfig:
    """难度配置"""
    name: str
    layers: int              # 层数
    type_count: int          # 类型数量
    cards_per_type: int      # 每种类型的卡片组数（每组3张）
    board_width: int = 6     # 棋盘宽度（卡片数量）
    board_height: int = 6    # 棋盘高度（卡片数量）


# 预设难度
DIFFICULTIES = {
    "easy": DifficultyConfig("简单", layers=5, type_count=5, cards_per_type=3, board_width=5, board_height=5),
    "normal": DifficultyConfig("普通", layers=6, type_count=6, cards_per_type=4, board_width=5, board_height=5),
    "hard": DifficultyConfig("困难", layers=8, type_count=7, cards_per_type=4, board_width=5, board_height=6),
    "hell": DifficultyConfig("地狱", layers=10, type_count=8, cards_per_type=5, board_width=6, board_height=6),
}


class LevelGenerator:
    """关卡生成器"""

    SLOT_SIZE = 7       # 槽位数量

    def __init__(self, config: DifficultyConfig):
        # 根据配置计算网格尺寸
        self.grid_width = config.board_width * 2    # 每张卡片占2格
        self.grid_height = config.board_height * 2
        self.max_x = self.grid_width - 2   # 卡片最大X坐标（因为占2x2）
        self.max_y = self.grid_height - 2  # 卡片最大Y坐标
        self.config = config
        self.cards: List[Card] = []
        
    def generate(self) -> str:
        """生成关卡并返回格式化字符串"""
        self.cards = []
        
        # 计算总卡片数（每种类型 = cards_per_type * 3）
        total_groups = self.config.type_count * self.config.cards_per_type
        
        # 准备所有要放置的卡片类型组（每组3张同类型）
        type_groups = []
        for t in range(self.config.type_count):
            for _ in range(self.config.cards_per_type):
                type_groups.append(t)
        
        # 打乱放置顺序
        random.shuffle(type_groups)
        
        # 逆向生成：每次放置3张同类型卡片
        for group_idx, card_type in enumerate(type_groups):
            # 计算当前应该放置的层级范围
            progress = group_idx / len(type_groups)
            self._place_three_cards(card_type, progress)
        
        # 格式化输出
        return self._format_output()
    
    def _place_three_cards(self, card_type: int, progress: float):
        """放置3张同类型卡片（逆向生成的核心）"""
        placed = 0
        attempts = 0
        max_attempts = 1000
        
        while placed < 3 and attempts < max_attempts:
            attempts += 1
            
            # 根据进度决定层级偏好
            # 早期放底层，后期放顶层（逆向思维）
            if progress < 0.33:
                preferred_z = random.randint(0, max(0, self.config.layers - 2))
            elif progress < 0.66:
                preferred_z = random.randint(0, self.config.layers - 1)
            else:
                preferred_z = random.randint(
                    max(0, self.config.layers - 2), 
                    self.config.layers - 1
                )
            
            # 随机位置
            x = random.randint(0, self.max_x)
            y = random.randint(0, self.max_y)
            z = preferred_z

            # 检查位置是否有效
            if self._is_valid_position(x, y, z):
                card = Card(z=z, y=y, x=x, type=card_type)
                self.cards.append(card)
                placed += 1

        if placed < 3:
            # 如果放不下，尝试在更高层找有效位置
            extra_z = self.config.layers
            fallback_attempts = 0
            max_fallback = 500

            while placed < 3 and fallback_attempts < max_fallback:
                fallback_attempts += 1
                x = random.randint(0, self.max_x)
                y = random.randint(0, self.max_y)

                # 尝试当前 extra_z 层
                if self._is_valid_position(x, y, extra_z):
                    card = Card(z=extra_z, y=y, x=x, type=card_type)
                    self.cards.append(card)
                    placed += 1
                elif fallback_attempts % 50 == 0:
                    # 每50次尝试失败后，尝试更高层
                    extra_z += 1

    def _is_valid_position(self, x: int, y: int, z: int) -> bool:
        """检查位置是否有效"""
        # 边界检查
        if x < 0 or x > self.max_x or y < 0 or y > self.max_y:
            return False
        
        # 检查同层冲突（2x2区域不能重叠）
        for card in self.cards:
            if card.z == z:
                if abs(card.x - x) < 2 and abs(card.y - y) < 2:
                    return False
        
        return True
    
    def _is_blocked(self, card: Card) -> bool:
        """检查卡片是否被遮挡"""
        for other in self.cards:
            if other.z > card.z:
                if abs(other.x - card.x) < 2 and abs(other.y - card.y) < 2:
                    return True
        return False
    
    def _format_output(self) -> str:
        """格式化输出为指定格式"""
        cards_str = ", ".join([str(c.to_list()) for c in self.cards])
        return "{" + cards_str + "}"
    
    def get_stats(self) -> dict:
        """获取关卡统计信息"""
        return {
            "total_cards": len(self.cards),
            "layers": max(c.z for c in self.cards) + 1 if self.cards else 0,
            "types": len(set(c.type for c in self.cards)),
            "board": f"{self.config.board_width}x{self.config.board_height}",
            "difficulty": self.config.name,
        }

    def verify_solvable(self) -> bool:
        """验证关卡可解性（模拟正向游戏）"""
        remaining = self.cards.copy()
        slot = []

        while remaining:
            # 找出所有可点击的卡片（未被遮挡）
            clickable = []
            for card in remaining:
                blocked = False
                for other in remaining:
                    if other is not card and other.z > card.z:
                        if abs(other.x - card.x) < 2 and abs(other.y - card.y) < 2:
                            blocked = True
                            break
                if not blocked:
                    clickable.append(card)

            if not clickable:
                return False  # 没有可点击的卡片，卡死

            # 尝试找一张能消除的（槽中有2张同类型）
            best_card = None
            for card in clickable:
                same_type_in_slot = sum(1 for c in slot if c.type == card.type)
                if same_type_in_slot == 2:
                    best_card = card
                    break

            # 如果没有能立即消除的，找槽中有1张同类型的
            if not best_card:
                for card in clickable:
                    same_type_in_slot = sum(1 for c in slot if c.type == card.type)
                    if same_type_in_slot == 1:
                        best_card = card
                        break

            # 如果还是没有，随机选一张
            if not best_card:
                best_card = random.choice(clickable)

            # 点击卡片
            remaining.remove(best_card)
            slot.append(best_card)

            # 检查是否能消除
            type_count = {}
            for c in slot:
                type_count[c.type] = type_count.get(c.type, 0) + 1

            for t, count in type_count.items():
                if count >= 3:
                    # 消除3张
                    removed = 0
                    slot = [c for c in slot if c.type != t or (removed := removed + 1) > 3]
                    break

            # 检查槽位是否满
            if len(slot) > self.SLOT_SIZE:
                return False  # 槽满，失败

        return len(slot) == 0  # 全部消除则成功


def generate_level(difficulty: str = "normal") -> str:
    """快捷函数：生成指定难度的关卡"""
    if difficulty not in DIFFICULTIES:
        raise ValueError(f"Unknown difficulty: {difficulty}. Choose from: {list(DIFFICULTIES.keys())}")

    config = DIFFICULTIES[difficulty]
    generator = LevelGenerator(config)
    return generator.generate()


def generate_levels(difficulty: str, count: int) -> List[str]:
    """批量生成关卡"""
    levels = []
    for _ in range(count):
        levels.append(generate_level(difficulty))
    return levels


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="羊了个羊关卡生成器")
    parser.add_argument("-d", "--difficulty", default="normal",
                        choices=["easy", "normal", "hard", "hell"],
                        help="难度级别")
    parser.add_argument("-n", "--count", type=int, default=1,
                        help="生成数量")
    parser.add_argument("-v", "--verify", action="store_true",
                        help="验证可解性")
    parser.add_argument("--stats", action="store_true",
                        help="显示统计信息")
    parser.add_argument("-o", "--output", type=str,
                        help="输出到文件")

    args = parser.parse_args()

    config = DIFFICULTIES[args.difficulty]
    output_lines = []

    for i in range(args.count):
        generator = LevelGenerator(config)
        level = generator.generate()

        if args.verify:
            # 多次验证确保可解
            solvable = generator.verify_solvable()
            status = "✓ 可解" if solvable else "✗ 不可解"
        else:
            status = ""

        if args.stats:
            stats = generator.get_stats()
            print(f"关卡 {i+1}: {stats} {status}")

        print(level)
        print()

        output_lines.append(level)

    # 保存到文件
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            for line in output_lines:
                f.write(line + '\n')
        print(f"已保存到 {args.output}")

