#!/usr/bin/env python3
"""
Simple GUI wrapper for the level generator using PyQt5.
"""

from __future__ import annotations

import sys

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from level_generator import DIFFICULTIES, DifficultyConfig, LevelGenerator


PRESET_LABELS = {
    "easy": "简单",
    "normal": "普通",
    "hard": "困难",
    "hell": "地狱",
}


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("关卡生成器")
        self.resize(960, 760)
        self._build_ui()
        self._apply_preset("normal")

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        top_row = QHBoxLayout()
        top_row.addWidget(QLabel("预设难度"))
        self.difficulty_box = QComboBox()
        for key in ("easy", "normal", "hard", "hell"):
            self.difficulty_box.addItem(PRESET_LABELS[key], key)
        self.difficulty_box.currentIndexChanged.connect(self._on_preset_changed)
        top_row.addWidget(self.difficulty_box)

        top_row.addSpacing(16)
        top_row.addWidget(QLabel("生成数量"))
        self.count_box = QSpinBox()
        self.count_box.setRange(1, 200)
        self.count_box.setValue(1)
        top_row.addWidget(self.count_box)
        top_row.addStretch(1)
        layout.addLayout(top_row)

        param_grid = QGridLayout()
        param_grid.setHorizontalSpacing(12)
        param_grid.setVerticalSpacing(8)

        self.layers_box = self._create_spinbox(1, 50)
        self.type_count_box = self._create_spinbox(1, 50)
        self.cards_per_type_box = self._create_spinbox(1, 50)
        self.board_width_box = self._create_spinbox(1, 20)
        self.board_height_box = self._create_spinbox(1, 20)

        param_grid.addWidget(QLabel("层数 layers"), 0, 0)
        param_grid.addWidget(self.layers_box, 0, 1)
        param_grid.addWidget(QLabel("类型数 type_count"), 0, 2)
        param_grid.addWidget(self.type_count_box, 0, 3)
        param_grid.addWidget(QLabel("每类组数 cards_per_type"), 1, 0)
        param_grid.addWidget(self.cards_per_type_box, 1, 1)
        param_grid.addWidget(QLabel("棋盘宽 board_width"), 1, 2)
        param_grid.addWidget(self.board_width_box, 1, 3)
        param_grid.addWidget(QLabel("棋盘高 board_height"), 2, 0)
        param_grid.addWidget(self.board_height_box, 2, 1)

        layout.addLayout(param_grid)

        check_row = QHBoxLayout()
        self.verify_check = QCheckBox("验证可解性")
        self.verify_check.setChecked(True)
        check_row.addWidget(self.verify_check)

        self.stats_check = QCheckBox("显示统计信息")
        self.stats_check.setChecked(True)
        check_row.addWidget(self.stats_check)
        check_row.addStretch(1)
        layout.addLayout(check_row)

        self.hint_label = QLabel()
        self.hint_label.setWordWrap(True)
        layout.addWidget(self.hint_label)

        self.output = QPlainTextEdit()
        self.output.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.output.setFont(QFont("Consolas", 10))

        button_row = QHBoxLayout()
        generate_button = QPushButton("生成")
        generate_button.clicked.connect(self.generate_levels)
        button_row.addWidget(generate_button)

        copy_button = QPushButton("复制结果")
        copy_button.clicked.connect(self.copy_output)
        button_row.addWidget(copy_button)

        clear_button = QPushButton("清空")
        clear_button.clicked.connect(self.output.clear)
        button_row.addWidget(clear_button)
        button_row.addStretch(1)
        layout.addLayout(button_row)

        layout.addWidget(self.output, 1)

    def _create_spinbox(self, minimum: int, maximum: int) -> QSpinBox:
        box = QSpinBox()
        box.setRange(minimum, maximum)
        box.valueChanged.connect(self._update_hint)
        return box

    def _on_preset_changed(self) -> None:
        self._apply_preset(self.difficulty_box.currentData())

    def _apply_preset(self, key: str) -> None:
        config = DIFFICULTIES[key]
        for widget, value in (
            (self.layers_box, config.layers),
            (self.type_count_box, config.type_count),
            (self.cards_per_type_box, config.cards_per_type),
            (self.board_width_box, config.board_width),
            (self.board_height_box, config.board_height),
        ):
            widget.blockSignals(True)
            widget.setValue(value)
            widget.blockSignals(False)
        self._update_hint()

    def _current_config(self) -> DifficultyConfig:
        preset_key = self.difficulty_box.currentData()
        preset_name = PRESET_LABELS.get(preset_key, preset_key)
        return DifficultyConfig(
            name=preset_name,
            layers=self.layers_box.value(),
            type_count=self.type_count_box.value(),
            cards_per_type=self.cards_per_type_box.value(),
            board_width=self.board_width_box.value(),
            board_height=self.board_height_box.value(),
        )

    def _update_hint(self) -> None:
        config = self._current_config()
        total_cards = config.type_count * config.cards_per_type * 3
        self.hint_label.setText(
            "当前参数: "
            f"层数={config.layers}，"
            f"类型数={config.type_count}，"
            f"每类组数={config.cards_per_type}，"
            f"棋盘={config.board_width}x{config.board_height}，"
            f"总卡片数={total_cards}"
        )

    def generate_levels(self) -> None:
        count = self.count_box.value()
        config = self._current_config()

        sections: list[str] = []
        try:
            for index in range(count):
                generator = LevelGenerator(config)
                level = generator.generate()

                lines = [f"=== 关卡 {index + 1} ==="]
                if self.verify_check.isChecked():
                    lines.append(f"验证: {'可解' if generator.verify_solvable() else '不可解'}")
                if self.stats_check.isChecked():
                    stats = generator.get_stats()
                    lines.append(
                        "统计: "
                        f"总卡片={stats['total_cards']}, "
                        f"层数={stats['layers']}, "
                        f"类型数={stats['types']}, "
                        f"棋盘={stats['board']}, "
                        f"配置名={stats['difficulty']}"
                    )
                lines.append(level)
                sections.append("\n".join(lines))
        except Exception as exc:
            QMessageBox.critical(self, "生成失败", str(exc))
            return

        self.output.setPlainText("\n\n".join(sections))

    def copy_output(self) -> None:
        content = self.output.toPlainText().strip()
        if not content:
            QMessageBox.information(self, "提示", "当前没有可复制的内容")
            return

        QApplication.clipboard().setText(content)
        QMessageBox.information(self, "提示", "结果已复制到剪贴板")


def main() -> None:
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
