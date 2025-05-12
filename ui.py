# ui_qt.py
import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QTextEdit,
    QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QCheckBox
)
from PySide6.QtGui import QShortcut, QKeySequence, QTextCharFormat, QColor, QTextCursor, QMovie, QIcon
from PySide6.QtCore import Qt

from calculator import pet_calculate, represent_s_pet

# Load presets
preset_data = {}
with open("data.txt", encoding="utf-8") as f:
    for line in f:
        parts = line.strip().split("\t")
        if len(parts) == 6:
            key = parts[0]
            values = list(map(int, parts[1:]))
            preset_data[key] = values

all_labels = list(preset_data.keys())

class SwitchButton(QCheckBox):
    def __init__(self, label="", parent=None):
        super().__init__(label, parent)
        self.setTristate(False)
        self.setStyleSheet("""
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
            }
            QCheckBox::indicator:unchecked {
                background-color: #ccc;
                border-radius: 10px;
            }
            QCheckBox::indicator:checked {
                background-color: #87CEEB;
                border-radius: 10px;
            }
        """)

class PetCalculatorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("스톤에이지 클래식서버 - 1레벨 페트 확률 계산기")
        self.setWindowIcon(QIcon("icon.ico"))
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Dropdown + search
        dropdown_layout = QHBoxLayout()
        dropdown_label = QLabel("페트 선택:")
        self.dropdown = QComboBox()
        self.dropdown.setEditable(True)
        self.dropdown.addItems(all_labels)
        self.dropdown.setInsertPolicy(QComboBox.NoInsert)
        self.dropdown.currentTextChanged.connect(self.on_dropdown_select)

        dropdown_layout.addWidget(dropdown_label)
        dropdown_layout.addWidget(self.dropdown)
        layout.addLayout(dropdown_layout)

        # Image box
        self.image_label = QLabel()
        self.image_label.setFixedSize(200, 200)  # Adjust size as needed
        self.image_label.setScaledContents(False)

        self.image_layout = QHBoxLayout()
        self.image_layout.addStretch()                 # Left spacer
        self.image_layout.addWidget(self.image_label)  # Your image (GIF) label
        self.image_layout.addStretch()                 # Right spacer
        layout.addLayout(self.image_layout)            # Add to main layout

        # Entry fields
        self.entries = []
        entry_labels = ['초기계수', '체력', '공격', '방어', '순발']
        for label_text in entry_labels:
            row = QHBoxLayout()
            label = QLabel(label_text)
            entry = QLineEdit()
            self.entries.append(entry)
            row.addWidget(label)
            row.addWidget(entry)
            layout.addLayout(row)

        # Representative S level Pet
        row = QHBoxLayout()
        label = QLabel("정석")
        self.represent_box = QLineEdit()
        self.represent_box.setReadOnly(True)
        row.addWidget(label)
        row.addWidget(self.represent_box)
        layout.addLayout(row)

        # Result label
        layout.addWidget(QLabel("레벨1 페트 확률 결과:"))

        # Result box
        self.result_box = QTextEdit()
        self.result_box.setReadOnly(True)
        layout.addWidget(self.result_box)

        # Calculate button
        calc_btn = QPushButton("계산")
        calc_btn.clicked.connect(self.calculate)
        layout.addWidget(calc_btn)

        # Sorting
        # Base sort
        self.filter_switch = SwitchButton("맥스 베이스 초기만 보기")
        self.filter_switch.stateChanged.connect(self.calculate)
        layout.addWidget(self.filter_switch)

        # Encounter sort
        self.sort_switch = SwitchButton("베이스 확률 정렬")
        self.sort_switch.setChecked(True)
        self.sort_switch.stateChanged.connect(self.calculate)
        layout.addWidget(self.sort_switch)

        # Search functionality
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Ctrl+F 눌러 검색...")
        self.search_box.textChanged.connect(self.highlight_matches)
        layout.addWidget(self.search_box)

        # Add Ctrl+F hotkey for search using QShortcut
        search_shortcut = QShortcut(Qt.CTRL | Qt.Key_F, self)
        search_shortcut.activated.connect(self.focus_search_box)

        enter_shortcut = QShortcut(QKeySequence(Qt.Key_Return), self)
        enter_shortcut.activated.connect(
            lambda: self.on_dropdown_select(self.dropdown.currentText())
        )

        self.resize(500, 800)
        self.setLayout(layout)

    def focus_search_box(self):
        """Focus on the search text box when Ctrl+F is pressed."""
        self.search_box.selectAll()
        self.search_box.setFocus()

    def on_dropdown_select(self, text):
        if text in preset_data:
            for i in range(5):
                self.entries[i].setText(str(preset_data[text][i]))
            values = [int(entry.text()) for entry in self.entries]
            self.represent_box.setText(str(represent_s_pet(*values)))
            self.calculate()
            
            # Update image
            image_path = f"Picture/{text}.gif"
            image_gif = QMovie(image_path)
            image_gif.setScaledSize(self.image_label.size()/ 1.5)

            if not image_gif.isValid():
                self.image_label.clear()
            else:
                self.image_label.setMovie(image_gif)
                image_gif.start()

        else:
            self.result_box.setPlainText("")
            for i in range(5):
                self.entries[i].setText("")
            self.represent_box.setText("")
            self.image_label.clear()

    def highlight_matches(self, search_term):
        cursor = self.result_box.textCursor()
        format = QTextCharFormat()
        format.setBackground(QColor("yellow"))  # Highlight color

        # Clear previous formatting
        self.result_box.selectAll()
        clear_format = QTextCharFormat()
        self.result_box.textCursor().setCharFormat(clear_format)

        if not search_term:
            return

        # Start at the beginning
        self.result_box.moveCursor(QTextCursor.Start)

        # Search and highlight matches
        match_cursor = self.result_box.textCursor()
        found_first = False

        while True:
            match_cursor = self.result_box.document().find(search_term, match_cursor)

            if match_cursor.isNull():
                break

            match_cursor.mergeCharFormat(format)

            if not found_first:
                self.result_box.setTextCursor(match_cursor)
                found_first = True
    
    def calculate(self):
        try:
            values = [int(entry.text()) for entry in self.entries]
            self.result_box.setPlainText(
                pet_calculate(
                    *values,
                    max_only=self.filter_switch.isChecked(),
                    sort_key="base_chance" if self.sort_switch.isChecked() else "encounter_chance"
                )
            )
        except ValueError:
            self.result_box.setPlainText("잘못된 입력")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PetCalculatorApp()
    window.show()
    sys.exit(app.exec())
