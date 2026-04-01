#!/usr/bin/env python3
"""
羊了个羊关卡生成器。
采用逆向生成思路，尽量保证生成出的关卡可解。
"""

from __future__ import annotations

import argparse
import random
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class Card:
    z: int
    y: int
    x: int
    type: int

    def to_list(self) -> List[int]:
        return [self.z, self.y, self.x, self.type]

    def occupies(self) -> List[Tuple[int, int, int]]:
        return [
            (self.x, self.y, self.z),
            (self.x + 1, self.y, self.z),
            (self.x, self.y + 1, self.z),
            (self.x + 1, self.y + 1, self.z),
        ]


@dataclass
class DifficultyConfig:
    name: str
    layers: int
    type_count: int
    cards_per_type: int
    board_width: int = 6
    board_height: int = 6


DIFFICULTIES = {
    "easy": DifficultyConfig("easy", layers=5, type_count=5, cards_per_type=3, board_width=5, board_height=5),
    "normal": DifficultyConfig("normal", layers=6, type_count=6, cards_per_type=4, board_width=5, board_height=5),
    "hard": DifficultyConfig("hard", layers=8, type_count=7, cards_per_type=4, board_width=5, board_height=6),
    "hell": DifficultyConfig("hell", layers=10, type_count=8, cards_per_type=5, board_width=6, board_height=6),
}


class LevelGenerator:
    SLOT_SIZE = 7

    def __init__(self, config: DifficultyConfig):
        self.grid_width = config.board_width * 2
        self.grid_height = config.board_height * 2
        self.max_x = self.grid_width - 2
        self.max_y = self.grid_height - 2
        self.config = config
        self.cards: List[Card] = []

    def generate(self) -> str:
        self.cards = []

        type_groups: List[int] = []
        for card_type in range(self.config.type_count):
            for _ in range(self.config.cards_per_type):
                type_groups.append(card_type)

        random.shuffle(type_groups)

        for group_index, card_type in enumerate(type_groups):
            progress = group_index / len(type_groups)
            self._place_three_cards(card_type, progress)

        return self._format_output()

    def _place_three_cards(self, card_type: int, progress: float) -> None:
        placed = 0
        attempts = 0
        max_attempts = 1000

        while placed < 3 and attempts < max_attempts:
            attempts += 1

            if progress < 0.33:
                preferred_z = random.randint(0, max(0, self.config.layers - 2))
            elif progress < 0.66:
                preferred_z = random.randint(0, self.config.layers - 1)
            else:
                preferred_z = random.randint(max(0, self.config.layers - 2), self.config.layers - 1)

            x = random.randint(0, self.max_x)
            y = random.randint(0, self.max_y)

            if self._is_valid_position(x, y, preferred_z):
                self.cards.append(Card(z=preferred_z, y=y, x=x, type=card_type))
                placed += 1

        if placed >= 3:
            return

        extra_z = self.config.layers
        fallback_attempts = 0
        max_fallback = 500

        while placed < 3 and fallback_attempts < max_fallback:
            fallback_attempts += 1
            x = random.randint(0, self.max_x)
            y = random.randint(0, self.max_y)

            if self._is_valid_position(x, y, extra_z):
                self.cards.append(Card(z=extra_z, y=y, x=x, type=card_type))
                placed += 1
            elif fallback_attempts % 50 == 0:
                extra_z += 1

    def _is_valid_position(self, x: int, y: int, z: int) -> bool:
        if x < 0 or x > self.max_x or y < 0 or y > self.max_y:
            return False

        for card in self.cards:
            if card.z == z and abs(card.x - x) < 2 and abs(card.y - y) < 2:
                return False

        return True

    def _format_output(self) -> str:
        cards_str = ", ".join(str(card.to_list()) for card in self.cards)
        return "{" + cards_str + "}"

    def get_stats(self) -> dict:
        return {
            "total_cards": len(self.cards),
            "layers": max(card.z for card in self.cards) + 1 if self.cards else 0,
            "types": len({card.type for card in self.cards}),
            "board": f"{self.config.board_width}x{self.config.board_height}",
            "difficulty": self.config.name,
        }

    def verify_solvable(self) -> bool:
        remaining = self.cards.copy()
        slot: List[Card] = []

        while remaining:
            clickable: List[Card] = []
            for card in remaining:
                blocked = False
                for other in remaining:
                    if other is card:
                        continue
                    if other.z > card.z and abs(other.x - card.x) < 2 and abs(other.y - card.y) < 2:
                        blocked = True
                        break
                if not blocked:
                    clickable.append(card)

            if not clickable:
                return False

            best_card = None
            for card in clickable:
                if sum(1 for item in slot if item.type == card.type) == 2:
                    best_card = card
                    break

            if best_card is None:
                for card in clickable:
                    if sum(1 for item in slot if item.type == card.type) == 1:
                        best_card = card
                        break

            if best_card is None:
                best_card = random.choice(clickable)

            remaining.remove(best_card)
            slot.append(best_card)

            type_count = {}
            for card in slot:
                type_count[card.type] = type_count.get(card.type, 0) + 1

            for card_type, count in type_count.items():
                if count >= 3:
                    removed = 0
                    slot = [card for card in slot if card.type != card_type or (removed := removed + 1) > 3]
                    break

            if len(slot) > self.SLOT_SIZE:
                return False

        return len(slot) == 0


def generate_level(difficulty: str = "normal") -> str:
    if difficulty not in DIFFICULTIES:
        raise ValueError(f"Unknown difficulty: {difficulty}. Choose from: {list(DIFFICULTIES.keys())}")

    generator = LevelGenerator(DIFFICULTIES[difficulty])
    return generator.generate()


def generate_levels(difficulty: str, count: int) -> List[str]:
    return [generate_level(difficulty) for _ in range(count)]


def main() -> None:
    parser = argparse.ArgumentParser(description="羊了个羊关卡生成器")
    parser.add_argument("-d", "--difficulty", default="normal", choices=list(DIFFICULTIES.keys()), help="难度级别")
    parser.add_argument("-n", "--count", type=int, default=1, help="生成数量")
    parser.add_argument("-v", "--verify", action="store_true", help="验证可解性")
    parser.add_argument("--stats", action="store_true", help="显示统计信息")
    parser.add_argument("-o", "--output", type=str, help="输出到文件")
    args = parser.parse_args()

    output_lines: List[str] = []

    for index in range(args.count):
        generator = LevelGenerator(DIFFICULTIES[args.difficulty])
        level = generator.generate()

        status = ""
        if args.verify:
            solvable = generator.verify_solvable()
            status = "[OK] solvable" if solvable else "[FAIL] unsolvable"

        if args.stats:
            print(f"Level {index + 1}: {generator.get_stats()} {status}".rstrip())

        print(level)
        print()
        output_lines.append(level)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as file:
            for line in output_lines:
                file.write(line + "\n")
        print(f"Saved to {args.output}")


if __name__ == "__main__":
    main()
