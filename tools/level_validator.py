#!/usr/bin/env python3
"""
关卡配置验证脚本
检查：
1. 同层卡片是否重叠
2. 卡片坐标是否越界
3. 每种类型卡片数是否为3的倍数
"""

import re
import sys
from collections import defaultdict


def parse_level(level_str):
    """解析关卡字符串"""
    pattern = r'\[(\d+),\s*(\d+),\s*(\d+),\s*(\d+)\]'
    matches = re.findall(pattern, level_str)
    cards = []
    for match in matches:
        z, y, x, card_type = map(int, match)
        cards.append({'z': z, 'y': y, 'x': x, 'type': card_type})
    return cards


def validate_level(cards):
    """验证关卡配置"""
    errors = []
    warnings = []
    
    # 1. 检查坐标越界（卡片占2x2，所以最大坐标是10）
    for i, card in enumerate(cards):
        if card['x'] < 0 or card['x'] > 10:
            errors.append(f"卡片 {i+1} [{card['z']},{card['y']},{card['x']},{card['type']}]: X坐标越界 (应为0-10)")
        if card['y'] < 0 or card['y'] > 10:
            errors.append(f"卡片 {i+1} [{card['z']},{card['y']},{card['x']},{card['type']}]: Y坐标越界 (应为0-10)")
    
    # 2. 检查同层重叠
    layers = defaultdict(list)
    for i, card in enumerate(cards):
        layers[card['z']].append((i, card))
    
    for z, layer_cards in layers.items():
        # 检查该层每对卡片是否重叠
        for i in range(len(layer_cards)):
            for j in range(i + 1, len(layer_cards)):
                idx1, card1 = layer_cards[i]
                idx2, card2 = layer_cards[j]
                
                # 两张卡片重叠条件：2x2区域有交集
                # 即 |x1 - x2| < 2 且 |y1 - y2| < 2
                if abs(card1['x'] - card2['x']) < 2 and abs(card1['y'] - card2['y']) < 2:
                    errors.append(
                        f"第 {z} 层重叠: "
                        f"卡片 {idx1+1} [{card1['z']},{card1['y']},{card1['x']},{card1['type']}] 与 "
                        f"卡片 {idx2+1} [{card2['z']},{card2['y']},{card2['x']},{card2['type']}]"
                    )
    
    # 3. 检查类型数量是否为3的倍数
    type_count = defaultdict(int)
    for card in cards:
        type_count[card['type']] += 1
    
    for t, count in sorted(type_count.items()):
        if count % 3 != 0:
            errors.append(f"类型 {t}: 共 {count} 张，不是3的倍数，无法完全消除!")
        else:
            warnings.append(f"类型 {t}: 共 {count} 张 ✓")
    
    return errors, warnings


def main():
    # 读取文件
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "level.txt"
    
    # 尝试多种编码
    level_str = None
    for encoding in ['utf-8', 'utf-8-sig', 'utf-16', 'gbk', 'latin-1']:
        try:
            with open(filename, 'r', encoding=encoding) as f:
                level_str = f.read().strip()
            break
        except (UnicodeDecodeError, UnicodeError):
            continue
    
    if not level_str:
        print(f"错误: 无法读取文件 {filename}")
        sys.exit(1)
    
    cards = parse_level(level_str)
    print(f"解析到 {len(cards)} 张卡片")
    print(f"层数: {max(c['z'] for c in cards) + 1}")
    print(f"类型数: {len(set(c['type'] for c in cards))}")
    print()
    
    errors, warnings = validate_level(cards)
    
    # 输出警告（类型统计）
    print("=== 类型统计 ===")
    for w in warnings:
        print(w)
    print()
    
    # 输出错误
    if errors:
        print(f"=== 发现 {len(errors)} 个错误 ===")
        for e in errors:
            print(f"❌ {e}")
        sys.exit(1)
    else:
        print("✅ 验证通过，无异常!")


if __name__ == "__main__":
    main()

