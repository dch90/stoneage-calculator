# ui_qt.py
import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QTextEdit,
    QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QCheckBox,
    QMainWindow, QTabWidget
)
from PySide6.QtGui import QShortcut, QKeySequence, QTextCharFormat, QColor, QTextCursor, QMovie, QIcon, QIntValidator
from PySide6.QtCore import Qt, QTimer

from pet_calculator import get_distribution_dict, pet_calculate, represent_s_pet, get_min_hp, formatted_distribution
from exp_calculator import calculate_exp_buff, calculate_time_for_lvl, format_result

# Load presets
pet_preset_data = {}
with open("pet_data.txt", encoding="utf-8") as f:
    for line in f:
        parts = line.strip().split("\t")
        if len(parts) == 6:
            key = parts[0]
            values = list(map(int, parts[1:]))
            pet_preset_data[key] = values

all_pet_labels = list(pet_preset_data.keys())

hunt_preset_data = {}
with open("hunt_data.txt", encoding="utf-8") as f:
    for line in f:
        parts = line.strip().split("\t")
        if len(parts) == 2:
            hunt_area = parts[0]
            exp = parts[1]
            hunt_preset_data[hunt_area] = exp

all_hunt_labels = list(hunt_preset_data.keys())

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
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Dropdown + search
        dropdown_layout = QHBoxLayout()
        dropdown_label = QLabel("페트 선택:")
        self.dropdown = QComboBox()
        self.dropdown.setEditable(True)
        self.dropdown.addItem("페트 고르기")
        self.dropdown.setItemData(0, 0, role=Qt.UserRole - 1)  # Make the placeholder unselectable
        self.dropdown.lineEdit().selectAll()
        self.dropdown.addItems(all_pet_labels)
        self.dropdown.setInsertPolicy(QComboBox.NoInsert)
        self.dropdown.currentTextChanged.connect(self.dropdown_schedule_search)
        
        # Search Timer
        self.dropdown_search_timer = QTimer()
        self.dropdown_search_timer.setSingleShot(True)
        self.dropdown_search_timer.timeout.connect(lambda: self.on_dropdown_select(self.dropdown.lineEdit().text()))

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

        # minimum pet hp
        row = QHBoxLayout()
        label = QLabel("최소 체력")
        self.min_hp_box = QLineEdit()
        self.min_hp_box.setReadOnly(True)
        row.addWidget(label)
        row.addWidget(self.min_hp_box)
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
        self.filter_switch.setChecked(True)
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
        self.search_box.textChanged.connect(self.schedule_search)
        layout.addWidget(self.search_box)

        # Search Timer
        self.result_search_timer = QTimer()
        self.result_search_timer.setSingleShot(True)
        self.result_search_timer.timeout.connect(lambda: self.highlight_matches(self.search_box.text()))

        # Add Ctrl+F hotkey for search using QShortcut
        search_shortcut = QShortcut(Qt.CTRL | Qt.Key_F, self)
        search_shortcut.activated.connect(self.focus_search_box)

        enter_shortcut = QShortcut(QKeySequence(Qt.Key_Return), self)
        enter_shortcut.activated.connect(
            lambda: self.on_dropdown_select(self.dropdown.currentText())
        )

        self.setLayout(layout)

    def focus_search_box(self):
        """Focus on the search text box when Ctrl+F is pressed."""
        self.search_box.setFocus()
        self.search_box.selectAll()

    def on_dropdown_select(self, text):
        if text in pet_preset_data:
            for i in range(5):
                self.entries[i].setText(str(pet_preset_data[text][i]))
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
            self.min_hp_box.setText("")
            self.image_label.clear()

    def dropdown_schedule_search(self):
        self.dropdown_search_timer.start(100)

    def schedule_search(self):
        self.result_search_timer.start(200)

    def highlight_matches(self, search_term):
        format = QTextCharFormat()
        format.setBackground(QColor("yellow"))  # Highlight color

        # Clear previous formatting
        self.result_box.selectAll()
        clear_format = QTextCharFormat()
        self.result_box.textCursor().setCharFormat(clear_format)

        if not search_term:
            return

        self.result_box.moveCursor(QTextCursor.Start)
        match_cursor = self.result_box.textCursor()
        found_first = False

        while True:
            match_cursor = self.result_box.document().find(search_term, match_cursor)
            if match_cursor.isNull():
                break

            match_cursor.mergeCharFormat(format)

            if not found_first:
                self.result_box.setTextCursor(match_cursor)
                self.result_box.ensureCursorVisible()

                # Scroll so that matched line is at the top
                layout = self.result_box.document().documentLayout()
                rect = layout.blockBoundingRect(match_cursor.block())
                top_position = rect.translated(0, -self.result_box.viewport().rect().top()).top()

                scroll_bar = self.result_box.verticalScrollBar()
                scroll_bar.setValue(int(top_position))

                found_first = True
    
    def calculate(self):
        try:
            values = [int(entry.text()) for entry in self.entries]
            distribution = get_distribution_dict(*values)
            calculated_chances = pet_calculate(distribution)
            self.result_box.setPlainText(
                formatted_distribution(
                    calculated_chances,
                    max_only=self.filter_switch.isChecked(),
                    sort_key="base_chance" if self.sort_switch.isChecked() else "encounter_chance"
                )
            )

            self.min_hp_box.setText(str(get_min_hp(calculated_chances)))
        except ValueError:
            self.result_box.setPlainText("잘못된 입력")

class ExpCalculatorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Dropdown + search
        dropdown_layout = QHBoxLayout()
        dropdown_label = QLabel("사냥터 선택:")
        self.dropdown = QComboBox()
        self.dropdown.setEditable(True)
        self.dropdown.addItems(all_hunt_labels)
        self.dropdown.setInsertPolicy(QComboBox.NoInsert)
        self.dropdown.currentTextChanged.connect(self.on_dropdown_select)

        dropdown_layout.addWidget(dropdown_label)
        dropdown_layout.addWidget(self.dropdown)
        layout.addLayout(dropdown_layout)

        # Entry fields
        entry_labels = ['시간당 경험치', '파티원 수', '아이템 배수(경구, 케이크)', '변템 +?%']
        for label_text in entry_labels:
            row = QHBoxLayout()
            label = QLabel(label_text)
            entry = QLineEdit()
            entry.setValidator(QIntValidator())
            row.addWidget(label)
            row.addWidget(entry)
            layout.addLayout(row)
            if label_text == "시간당 경험치":
                self.exp_hour = entry
                self.exp_hour.setText(hunt_preset_data["해변 다이노 도우미"])
            if label_text == "파티원 수":
                entry.setText("1")
                self.party_count = entry
                entry.setText("5")
            if label_text == "아이템 배수(경구, 케이크)":
                entry.setText("1")
                self.item_buff = entry
            if label_text == "변템 +?%":
                entry.setText("0")
                self.transform_item = entry

        
        # newbie item flag
        self.newbie_item_switch = SwitchButton("뉴비지원 나뭇가지 (경험치 +100%)")
        self.newbie_item_switch.setChecked(False)
        # self.filter_switch.stateChanged.connect(self.calculate)
        layout.addWidget(self.newbie_item_switch)

        # hero echo flag
        self.hero_echo_switch = SwitchButton("영웅의 메아리 (전체 경험치 x2)")
        self.hero_echo_switch.setChecked(False)
        # self.sort_switch.stateChanged.connect(self.calculate)
        layout.addWidget(self.hero_echo_switch)

        # Entry fields
        self.entries = []
        entry_labels = ['현재 레벨', '현재 경험치 %', '목표 레벨']
        for label_text in entry_labels:
            row = QHBoxLayout()
            label = QLabel(label_text)
            entry = QLineEdit()
            entry.setText("0")
            self.entries.append(entry)
            row.addWidget(label)
            row.addWidget(entry)
            layout.addLayout(row)
            if label_text in ['현재 레벨', '목표 레벨']:
                entry.setText("1")


        # Calculate button
        calc_btn = QPushButton("계산")
        calc_btn.clicked.connect(self.calculate)
        layout.addWidget(calc_btn)

        # Result box
        self.result_box = QTextEdit()
        self.result_box.setReadOnly(True)
        layout.addWidget(self.result_box)

        # layout.setSpacing(0.5)
        # layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def on_dropdown_select(self, text):
        if text in hunt_preset_data:
            self.exp_hour.setText(hunt_preset_data[text])

    def set_textbox_minmax(self, textbox: QLineEdit, min: str, max: str):
        if int(textbox.text()) < int(min): textbox.setText(min)
        elif int(textbox.text()) > int(max): textbox.setText(max)
    
    def set_textbox_minmax_float(self, textbox: QLineEdit, min: str, max: str):
        if float(textbox.text()) < float(min): textbox.setText(min)
        elif float(textbox.text()) > float(max): textbox.setText(max)

    def calculate(self):
        self.set_textbox_minmax(self.party_count, "1", "5")
        self.set_textbox_minmax(self.item_buff, "1", "999999999")
        self.set_textbox_minmax(self.transform_item, "0", "999999999")
        # current level
        self.set_textbox_minmax(self.entries[0], "1", "150")
        # percentage
        self.set_textbox_minmax_float(self.entries[1], "0", "100")
        #desired level
        self.set_textbox_minmax(self.entries[2], "1", "150")
        
        total_exp = calculate_exp_buff(
            exp=int(self.exp_hour.text()),
            transform_item=int(self.transform_item.text()),
            item_buff=int(self.item_buff.text()),
            party_count=int(self.party_count.text()),
            newbie_item=int(self.newbie_item_switch.isChecked()),
            hero_echo=int(self.hero_echo_switch.isChecked())
        )
        required_time_min = calculate_time_for_lvl(
            int(self.entries[0].text()),
            float(self.entries[1].text()),
            int(self.entries[2].text()),
            int(total_exp)
        )

        self.result_box.setPlainText(
            format_result(
                int(self.entries[0].text()),
                float(self.entries[1].text()),
                int(self.entries[2].text()),
                required_time_min,
                total_exp
            )
        )


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("latte 계산기 v1.3.1 - 스톤에이지 클래식서버")
        self.setWindowIcon(QIcon("아이콘.ico"))

        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # Add known tabs
        tab1 = PetCalculatorApp()
        tab2 = ExpCalculatorApp()

        self.tab_widget.addTab(tab1, "페트")
        self.tab_widget.addTab(tab2, "경험치")

        self.resize(500, 800)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PetCalculatorApp()
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
