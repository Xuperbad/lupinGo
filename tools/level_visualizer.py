#!/usr/bin/env python3
"""
羊了个羊关卡可视化验证工具
支持文本和图形两种可视化模式
"""

import re
import sys
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional


@dataclass
class Card:
    """卡片数据结构"""
    z: int
    y: int
    x: int
    type: int
    
    def occupies(self) -> List[Tuple[int, int]]:
        """返回卡片占据的4个格子坐标 (x, y)"""
        return [
            (self.x, self.y),
            (self.x + 1, self.y),
            (self.x, self.y + 1),
            (self.x + 1, self.y + 1),
        ]


def parse_level(level_str: str) -> List[Card]:
    """解析关卡字符串"""
    # 移除花括号和空格
    level_str = level_str.strip().strip('{}')
    
    # 匹配 [z, y, x, type] 格式
    pattern = r'\[(\d+),\s*(\d+),\s*(\d+),\s*(\d+)\]'
    matches = re.findall(pattern, level_str)
    
    cards = []
    for match in matches:
        z, y, x, card_type = map(int, match)
        cards.append(Card(z=z, y=y, x=x, type=card_type))
    
    return cards


def is_blocked(card: Card, all_cards: List[Card]) -> bool:
    """检查卡片是否被遮挡"""
    for other in all_cards:
        if other.z > card.z:
            if abs(other.x - card.x) < 2 and abs(other.y - card.y) < 2:
                return True
    return False


class TextVisualizer:
    """文本可视化器"""
    
    GRID_SIZE = 12
    TYPE_CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    
    def __init__(self, cards: List[Card]):
        self.cards = cards
        self.max_z = max(c.z for c in cards) if cards else 0
        
    def render_layer(self, z: int) -> List[str]:
        """渲染单层"""
        # 创建空网格
        grid = [['·' for _ in range(self.GRID_SIZE)] for _ in range(self.GRID_SIZE)]
        
        # 获取该层卡片
        layer_cards = [c for c in self.cards if c.z == z]
        
        for card in layer_cards:
            char = self.TYPE_CHARS[card.type % len(self.TYPE_CHARS)]
            blocked = is_blocked(card, self.cards)
            
            # 用方框标记卡片区域
            for dx, dy in [(0, 0), (1, 0), (0, 1), (1, 1)]:
                nx, ny = card.x + dx, card.y + dy
                if 0 <= nx < self.GRID_SIZE and 0 <= ny < self.GRID_SIZE:
                    if blocked:
                        grid[ny][nx] = char.lower()  # 被遮挡用小写
                    else:
                        grid[ny][nx] = char  # 可点击用大写
        
        return grid
    
    def render(self) -> str:
        """渲染所有层"""
        output = []
        output.append("=" * 50)
        output.append("关卡可视化 (大写=可点击, 小写=被遮挡, ·=空)")
        output.append("=" * 50)
        
        # 统计信息
        total = len(self.cards)
        types = len(set(c.type for c in self.cards))
        clickable = sum(1 for c in self.cards if not is_blocked(c, self.cards))
        output.append(f"总卡片: {total} | 类型数: {types} | 层数: {self.max_z + 1} | 可点击: {clickable}")
        output.append("")
        
        # 从顶层到底层渲染
        for z in range(self.max_z, -1, -1):
            layer_cards = [c for c in self.cards if c.z == z]
            output.append(f"--- 第 {z} 层 ({len(layer_cards)} 张卡片) ---")
            
            grid = self.render_layer(z)
            
            # 添加坐标轴
            output.append("   " + "".join(f"{i:2}" for i in range(self.GRID_SIZE)))
            for y, row in enumerate(grid):
                output.append(f"{y:2} " + " ".join(row))
            output.append("")
        
        # 类型统计
        output.append("--- 类型统计 ---")
        type_count: Dict[int, int] = {}
        for c in self.cards:
            type_count[c.type] = type_count.get(c.type, 0) + 1
        
        for t in sorted(type_count.keys()):
            char = self.TYPE_CHARS[t % len(self.TYPE_CHARS)]
            count = type_count[t]
            status = "✓" if count % 3 == 0 else "✗"
            output.append(f"  类型 {char}: {count} 张 {status}")
        
        return "\n".join(output)


def simulate_game(cards: List[Card]) -> Tuple[bool, List[str]]:
    """模拟游戏过程，返回(是否可解, 步骤日志)"""
    import random
    
    remaining = cards.copy()
    slot: List[Card] = []
    log: List[str] = []
    step = 0
    SLOT_SIZE = 7
    
    while remaining:
        # 找出所有可点击的卡片
        clickable = []
        for card in remaining:
            if not is_blocked(card, remaining):
                clickable.append(card)
        
        if not clickable:
            log.append(f"步骤 {step}: ❌ 无可点击卡片，卡死!")
            return False, log
        
        # 选择策略：优先能消除的
        best_card = None
        for card in clickable:
            same_in_slot = sum(1 for c in slot if c.type == card.type)
            if same_in_slot == 2:
                best_card = card
                break
        
        if not best_card:
            for card in clickable:
                same_in_slot = sum(1 for c in slot if c.type == card.type)
                if same_in_slot == 1:
                    best_card = card
                    break
        
        if not best_card:
            best_card = random.choice(clickable)
        
        # 点击
        remaining.remove(best_card)
        slot.append(best_card)
        step += 1
        
        char = TextVisualizer.TYPE_CHARS[best_card.type]
        log.append(f"步骤 {step}: 点击 [{best_card.z},{best_card.y},{best_card.x}] 类型{char} -> 槽位[{len(slot)}]")
        
        # 检查消除
        type_count = {}
        for c in slot:
            type_count[c.type] = type_count.get(c.type, 0) + 1
        
        for t, count in type_count.items():
            if count >= 3:
                char = TextVisualizer.TYPE_CHARS[t]
                slot = [c for c in slot if c.type != t][:len(slot)-3] + [c for c in slot if c.type != t][len(slot)-3:]
                # 正确移除3张
                new_slot = []
                removed = 0
                for c in slot:
                    if c.type == t and removed < 3:
                        removed += 1
                    else:
                        new_slot.append(c)
                slot = new_slot
                log.append(f"       ✨ 消除类型 {char}!")
                break
        
        if len(slot) > SLOT_SIZE:
            log.append(f"步骤 {step}: ❌ 槽位已满 ({len(slot)})，游戏失败!")
            return False, log
    
    if len(slot) == 0:
        log.append(f"🎉 恭喜通关! 共 {step} 步")
        return True, log
    else:
        log.append(f"❌ 剩余槽位卡片: {len(slot)}")
        return False, log


def visualize(level_str: str, show_simulation: bool = False) -> str:
    """可视化关卡字符串"""
    cards = parse_level(level_str)
    if not cards:
        return "错误: 无法解析关卡数据"

    viz = TextVisualizer(cards)
    output = viz.render()

    if show_simulation:
        output += "\n\n" + "=" * 50
        output += "\n模拟游戏过程"
        output += "\n" + "=" * 50 + "\n"

        success, log = simulate_game(cards)
        output += "\n".join(log)

    return output


def main():
    import argparse

    parser = argparse.ArgumentParser(description="羊了个羊关卡可视化工具")
    parser.add_argument("level", nargs="?", help="关卡配置字符串")
    parser.add_argument("-f", "--file", help="从文件读取关卡")
    parser.add_argument("-s", "--simulate", action="store_true", help="模拟游戏过程")
    parser.add_argument("--gui", action="store_true", help="使用图形界面(需要pygame)")

    args = parser.parse_args()

    # 获取关卡数据
    level_str = None

    if args.level:
        level_str = args.level
    elif args.file:
        # 尝试多种编码
        for encoding in ['utf-8', 'utf-8-sig', 'utf-16', 'gbk', 'latin-1']:
            try:
                with open(args.file, 'r', encoding=encoding) as f:
                    level_str = f.read().strip()
                break
            except (UnicodeDecodeError, UnicodeError):
                continue
        else:
            print(f"错误: 无法读取文件 {args.file}")
            sys.exit(1)
    else:
        # 从标准输入读取
        print("请输入关卡配置 (输入后按Enter):")
        level_str = input().strip()

    if not level_str:
        print("错误: 未提供关卡数据")
        sys.exit(1)

    if args.gui:
        try:
            cards = parse_level(level_str)
            gui_visualize(cards)
        except ImportError:
            print("GUI模式需要安装pygame: pip install pygame")
            sys.exit(1)
    else:
        result = visualize(level_str, show_simulation=args.simulate)
        print(result)


def gui_visualize(cards: List[Card]):
    """使用pygame进行图形化可视化"""
    try:
        import warnings
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        import pygame
    except ImportError:
        print("需要安装pygame: pip install pygame")
        return

    pygame.init()

    # 窗口设置
    CELL_SIZE = 40
    GRID_SIZE = 12
    MARGIN = 50
    INFO_WIDTH = 200
    WIDTH = GRID_SIZE * CELL_SIZE + MARGIN * 2 + INFO_WIDTH
    HEIGHT = GRID_SIZE * CELL_SIZE + MARGIN * 2

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("关卡可视化")

    # 颜色
    COLORS = [
        (255, 99, 71),    # 红
        (50, 205, 50),    # 绿
        (65, 105, 225),   # 蓝
        (255, 215, 0),    # 黄
        (255, 105, 180),  # 粉
        (0, 206, 209),    # 青
        (255, 165, 0),    # 橙
        (138, 43, 226),   # 紫
        (127, 255, 0),    # 黄绿
        (220, 20, 60),    # 深红
    ]

    max_z = max(c.z for c in cards) if cards else 0
    current_z = max_z

    font = pygame.font.Font(None, 24)
    small_font = pygame.font.Font(None, 20)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    current_z = min(current_z + 1, max_z)
                elif event.key == pygame.K_DOWN:
                    current_z = max(current_z - 1, 0)
                elif event.key == pygame.K_ESCAPE:
                    running = False

        screen.fill((40, 40, 40))

        # 绘制网格
        for i in range(GRID_SIZE + 1):
            pygame.draw.line(screen, (80, 80, 80),
                           (MARGIN + i * CELL_SIZE, MARGIN),
                           (MARGIN + i * CELL_SIZE, MARGIN + GRID_SIZE * CELL_SIZE))
            pygame.draw.line(screen, (80, 80, 80),
                           (MARGIN, MARGIN + i * CELL_SIZE),
                           (MARGIN + GRID_SIZE * CELL_SIZE, MARGIN + i * CELL_SIZE))

        # 绘制卡片
        layer_cards = [c for c in cards if c.z == current_z]
        for card in layer_cards:
            color = COLORS[card.type % len(COLORS)]
            blocked = is_blocked(card, cards)

            if blocked:
                color = tuple(c // 2 for c in color)  # 变暗

            rect = pygame.Rect(
                MARGIN + card.x * CELL_SIZE + 2,
                MARGIN + card.y * CELL_SIZE + 2,
                CELL_SIZE * 2 - 4,
                CELL_SIZE * 2 - 4
            )
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (255, 255, 255), rect, 2)

            # 显示类型
            text = font.render(str(card.type), True, (255, 255, 255))
            text_rect = text.get_rect(center=rect.center)
            screen.blit(text, text_rect)

        # 信息面板
        info_x = MARGIN + GRID_SIZE * CELL_SIZE + 20
        info_y = MARGIN

        title = font.render(f"Layer {current_z}/{max_z}", True, (255, 255, 255))
        screen.blit(title, (info_x, info_y))

        info_y += 30
        help_text = small_font.render("↑↓: Switch Layer", True, (180, 180, 180))
        screen.blit(help_text, (info_x, info_y))

        info_y += 20
        help_text2 = small_font.render("ESC: Exit", True, (180, 180, 180))
        screen.blit(help_text2, (info_x, info_y))

        info_y += 40
        stats = small_font.render(f"Total: {len(cards)}", True, (200, 200, 200))
        screen.blit(stats, (info_x, info_y))

        info_y += 20
        stats2 = small_font.render(f"This layer: {len(layer_cards)}", True, (200, 200, 200))
        screen.blit(stats2, (info_x, info_y))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()

