from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton, QTimeEdit, QFileDialog
from PyQt6.QtCore import QTime
import json

class AddReminderDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_UI()

    def init_UI(self):
        self.setWindowTitle("新增提醒")
        self.setGeometry(100, 100, 400, 200)

        # 建立主要佈局
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # 建立時間選擇器
        time_layout = QHBoxLayout()
        time_label = QLabel("時間:")
        self.time_edit = QTimeEdit()
        self.time_edit.setTime(QTime.currentTime())
        time_layout.addWidget(time_label)
        time_layout.addWidget(self.time_edit)
        main_layout.addLayout(time_layout)

        # 建立提醒內容輸入框
        action_layout = QHBoxLayout()
        action_label = QLabel("提醒內容:")
        self.action_edit = QLineEdit()
        action_layout.addWidget(action_label)
        action_layout.addWidget(self.action_edit)
        main_layout.addLayout(action_layout)

        # 建立提醒類型選擇框
        type_layout = QHBoxLayout()
        type_label = QLabel("提醒類型:")
        self.type_combo = QComboBox()
        self.type_combo.addItems(["彈窗", "彈幕"])
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.type_combo)
        main_layout.addLayout(type_layout)

        # 建立提醒圖片輸入框
        image_layout = QHBoxLayout()
        image_label = QLabel("提醒圖片:")
        self.image_edit = QLineEdit()
        image_button = QPushButton("瀏覽")
        image_button.clicked.connect(self.select_image)
        image_layout.addWidget(image_label)
        image_layout.addWidget(self.image_edit)
        image_layout.addWidget(image_button)
        main_layout.addLayout(image_layout)

        # 建立確定和取消按鈕
        button_layout = QHBoxLayout()
        ok_button = QPushButton("確定")
        ok_button.clicked.connect(self.save_reminder)  # 儲存提醒
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        main_layout.addLayout(button_layout)

    def select_image(self):
        """
        選擇提醒圖片。
        """
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("Image files (*.png *.jpg *.gif)")
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)

        if file_dialog.exec() == QFileDialog.AcceptMode.AcceptOpen:
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                self.image_edit.setText(selected_files[0])  # 顯示選擇的圖片路徑

    def save_reminder(self):
        """
        儲存提醒到 JSON 檔案。
        """
        reminder = {
            'time': self.time_edit.time().toString("HH:mm:ss"),
            'action': self.action_edit.text(),
            'type': self.type_combo.currentText(),
            'image': self.image_edit.text()
        }

        # 讀取現有的提醒檔案
        try:
            with open('reminders.json', 'r', encoding='utf-8') as file:
                reminders = json.load(file)
        except FileNotFoundError:
            reminders = []

        reminders.append(reminder)

        # 儲存回 JSON 檔案
        with open('reminders.json', 'w', encoding='utf-8') as file:
            json.dump(reminders, file, ensure_ascii=False, indent=4)

        self.accept()  # 關閉對話框
