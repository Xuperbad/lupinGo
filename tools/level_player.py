#!/usr/bin/env python3
"""
羊了个羊可交互游戏
用于手动验证关卡是否可通关
"""

import re
import sys
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import pygame


# 颜色配置
COLORS = [
    (255, 99, 71),    # 0 红
    (50, 205, 50),    # 1 绿
    (65, 105, 225),   # 2 蓝
    (255, 215, 0),    # 3 黄
    (255, 105, 180),  # 4 粉
    (0, 206, 209),    # 5 青
    (255, 165, 0),    # 6 橙
    (138, 43, 226),   # 7 紫
    (127, 255, 0),    # 8 黄绿
    (220, 20, 60),    # 9 深红
]


class Card:
    def __init__(self, z, y, x, card_type):
        self.z = z
        self.y = y
        self.x = x
        self.type = card_type
        self.removed = False


def parse_level(level_str):
    pattern = r'\[(\d+),\s*(\d+),\s*(\d+),\s*(\d+)\]'
    matches = re.findall(pattern, level_str)
    cards = []
    for match in matches:
        z, y, x, card_type = map(int, match)
        cards.append(Card(z, y, x, card_type))
    return cards


def is_blocked(card, all_cards):
    """检查卡片是否被遮挡"""
    for other in all_cards:
        if other.removed:
            continue
        if other.z > card.z:
            if abs(other.x - card.x) < 2 and abs(other.y - card.y) < 2:
                return True
    return False


class Game:
    def __init__(self, cards):
        self.cards = cards
        self.slot = []  # 槽位，最多7张
        self.max_slot = 7
        self.game_over = False
        self.win = False
        
        # 界面设置
        self.cell_size = 35
        self.grid_size = 12
        self.margin = 50
        self.slot_height = 80
        self.info_width = 150
        
        self.width = self.grid_size * self.cell_size + self.margin * 2 + self.info_width
        self.height = self.grid_size * self.cell_size + self.margin * 2 + self.slot_height
        
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("羊了个羊 - 点击卡片消除")
        self.font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 22)
        
    def get_card_rect(self, card):
        """获取卡片的屏幕矩形"""
        x = self.margin + card.x * self.cell_size
        y = self.margin + card.y * self.cell_size
        # 根据层级添加偏移，产生3D效果
        offset = card.z * 3
        return pygame.Rect(x - offset, y - offset, 
                          self.cell_size * 2 - 2, self.cell_size * 2 - 2)
    
    def get_clickable_cards(self):
        """获取所有可点击的卡片（未被遮挡）"""
        clickable = []
        for card in self.cards:
            if not card.removed and not is_blocked(card, self.cards):
                clickable.append(card)
        return clickable
    
    def click_card(self, card):
        """点击卡片"""
        if card.removed or is_blocked(card, self.cards):
            return
        
        # 移除卡片并放入槽位
        card.removed = True
        self.slot.append(card)
        
        # 检查是否能消除（3张同类型）
        self.check_eliminate()
        
        # 检查游戏状态
        self.check_game_state()
    
    def check_eliminate(self):
        """检查并消除3张同类型"""
        type_count = {}
        for c in self.slot:
            type_count[c.type] = type_count.get(c.type, 0) + 1
        
        for t, count in type_count.items():
            if count >= 3:
                # 消除3张
                removed = 0
                new_slot = []
                for c in self.slot:
                    if c.type == t and removed < 3:
                        removed += 1
                    else:
                        new_slot.append(c)
                self.slot = new_slot
                break
    
    def check_game_state(self):
        """检查游戏是否结束"""
        remaining = [c for c in self.cards if not c.removed]
        
        if len(remaining) == 0 and len(self.slot) == 0:
            self.win = True
            self.game_over = True
        elif len(self.slot) >= self.max_slot:
            self.game_over = True
            self.win = False
    
    def draw(self):
        self.screen.fill((50, 50, 50))
        
        # 按层级从低到高绘制卡片
        sorted_cards = sorted([c for c in self.cards if not c.removed], key=lambda c: c.z)
        clickable = self.get_clickable_cards()
        
        for card in sorted_cards:
            rect = self.get_card_rect(card)
            color = COLORS[card.type % len(COLORS)]
            
            # 被遮挡的卡片变暗
            if card not in clickable:
                color = tuple(c // 2 for c in color)
            
            # 绘制卡片阴影
            shadow_rect = rect.copy()
            shadow_rect.x += 3
            shadow_rect.y += 3
            pygame.draw.rect(self.screen, (30, 30, 30), shadow_rect, border_radius=5)
            
            # 绘制卡片
            pygame.draw.rect(self.screen, color, rect, border_radius=5)
            pygame.draw.rect(self.screen, (255, 255, 255), rect, 2, border_radius=5)
            
            # 显示类型数字
            text = self.font.render(str(card.type), True, (255, 255, 255))
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)

        # 绘制槽位区域
        slot_y = self.margin + self.grid_size * self.cell_size + 10
        slot_width = 50
        pygame.draw.rect(self.screen, (70, 70, 70),
                        (self.margin, slot_y, slot_width * self.max_slot + 10, 60),
                        border_radius=8)

        # 绘制槽位中的卡片
        for i, card in enumerate(self.slot):
            x = self.margin + 5 + i * slot_width
            rect = pygame.Rect(x, slot_y + 5, slot_width - 5, 50)
            color = COLORS[card.type % len(COLORS)]
            pygame.draw.rect(self.screen, color, rect, border_radius=5)
            pygame.draw.rect(self.screen, (255, 255, 255), rect, 2, border_radius=5)
            text = self.font.render(str(card.type), True, (255, 255, 255))
            self.screen.blit(text, text.get_rect(center=rect.center))

        # 绘制空槽位边框
        for i in range(len(self.slot), self.max_slot):
            x = self.margin + 5 + i * slot_width
            rect = pygame.Rect(x, slot_y + 5, slot_width - 5, 50)
            pygame.draw.rect(self.screen, (100, 100, 100), rect, 2, border_radius=5)

        # 绘制信息面板
        info_x = self.margin + self.grid_size * self.cell_size + 20
        remaining = len([c for c in self.cards if not c.removed])

        info_texts = [
            f"剩余: {remaining}",
            f"槽位: {len(self.slot)}/{self.max_slot}",
            "",
            "点击卡片消除",
            "3张同类型消除",
            "",
            "按 R 重新开始",
            "按 ESC 退出",
        ]

        for i, text in enumerate(info_texts):
            surf = self.small_font.render(text, True, (200, 200, 200))
            self.screen.blit(surf, (info_x, self.margin + i * 22))

        # 游戏结束提示
        if self.game_over:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            if self.win:
                msg = "恭喜通关!"
                color = (50, 255, 50)
            else:
                msg = "游戏失败 - 槽位已满"
                color = (255, 50, 50)

            text = pygame.font.Font(None, 48).render(msg, True, color)
            rect = text.get_rect(center=(self.width // 2, self.height // 2))
            self.screen.blit(text, rect)

            hint = self.small_font.render("按 R 重新开始", True, (200, 200, 200))
            self.screen.blit(hint, hint.get_rect(center=(self.width // 2, self.height // 2 + 40)))

        pygame.display.flip()

    def handle_click(self, pos):
        """处理鼠标点击"""
        if self.game_over:
            return

        clickable = self.get_clickable_cards()
        # 从顶层开始检查（z值大的优先）
        for card in sorted(clickable, key=lambda c: -c.z):
            rect = self.get_card_rect(card)
            if rect.collidepoint(pos):
                self.click_card(card)
                break

    def reset(self):
        """重置游戏"""
        for card in self.cards:
            card.removed = False
        self.slot = []
        self.game_over = False
        self.win = False

    def run(self):
        clock = pygame.time.Clock()
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_r:
                        self.reset()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # 左键
                        self.handle_click(event.pos)

            self.draw()
            clock.tick(60)

        pygame.quit()


def main():
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "level.txt"

    # 读取关卡
    level_str = None
    for encoding in ['utf-8', 'utf-8-sig', 'utf-16', 'gbk', 'latin-1']:
        try:
            with open(filename, 'r', encoding=encoding) as f:
                level_str = f.read().strip()
            break
        except (UnicodeDecodeError, UnicodeError, FileNotFoundError):
            continue

    if not level_str:
        print(f"错误: 无法读取文件 {filename}")
        print("用法: python level_player.py [关卡文件]")
        sys.exit(1)

    cards = parse_level(level_str)
    if not cards:
        print("错误: 无法解析关卡数据")
        sys.exit(1)

    print(f"加载关卡: {len(cards)} 张卡片")
    game = Game(cards)
    game.run()


if __name__ == "__main__":
    main()

