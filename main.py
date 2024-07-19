import sys
import json
from datetime import datetime
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QTimeEdit, QLabel, QMessageBox, QTableWidget, QTableWidgetItem, QAbstractItemView, QComboBox, QFileDialog, QDialog, QGridLayout, QHBoxLayout, QLineEdit
from PyQt6.QtCore import QTimer, QTime, Qt, QUrl
from PyQt6.QtGui import QMovie, QPixmap
from PyQt6.QtMultimedia import QMediaPlayer

class ReminderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("定時提醒APP")
        self.setGeometry(100, 100, 600, 400)

        # 建立主要佈局
        main_layout = QVBoxLayout()
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # 建立開始按鈕
        self.start_button = QPushButton("開始")
        self.start_button.clicked.connect(self.start_reminder)
        main_layout.addWidget(self.start_button)

        # 建立設定按鈕
        self.setting_button = QPushButton("設定")
        self.setting_button.clicked.connect(self.open_settings)
        main_layout.addWidget(self.setting_button)

        # 建立定時器
        self.timer = QTimer()
        self.timer.timeout.connect(self.show_reminder)

        # 初始化設定
        self.load_reminders_from_json()

    def load_reminders_from_json(self):
        """
        從 JSON 檔案中讀取提醒事件並初始化。
        """
        try:
            with open("reminders.json", "r") as f:
                data = json.load(f)
                self.reminders = [QTime.fromString(item["time"], "hh:mm:ss") for item in data]
                self.reminder_actions = {QTime.fromString(item["time"], "hh:mm:ss"): item["action"] for item in data}
                self.reminder_types = {QTime.fromString(item["time"], "hh:mm:ss"): item["type"] for item in data}
                self.reminder_images = {QTime.fromString(item["time"], "hh:mm:ss"): item["image"] for item in data}
        except FileNotFoundError:
            self.reminders = []
            self.reminder_actions = {}
            self.reminder_types = {}
            self.reminder_images = {}

    def start_reminder(self):
        """
        開始提醒功能。
        如果有設定好的提醒事件,則依序啟動定時器並顯示提醒。
        如果沒有設定任何提醒事件,則顯示提示訊息。
        """
        if self.reminders:
            for reminder in self.reminders:
                self.timer.start(reminder.secsTo(QTime.currentTime()) * 1000)
                self.show_reminder(reminder)
        else:
            QMessageBox.information(self, "提醒", "尚未設定任何提醒事件")

    def show_reminder(self, reminder=None):
        """
        顯示提醒。
        如果有設定好的提醒事件,則依序彈出提醒。
        根據提醒類型,顯示彈窗提醒或彈幕提醒。
        """
        if self.reminders:
            if not reminder:
                reminder = self.reminders.pop(0)
            reminder_type = self.reminder_types[reminder]
            if reminder_type == "彈窗":
                self.show_popup_reminder(reminder)
            elif reminder_type == "彈幕":
                self.show_banner_reminder(reminder)
            self.timer.start(reminder.secsTo(QTime.currentTime()) * 1000)

    def show_popup_reminder(self, reminder):
        """
        顯示彈窗提醒。
        根據設定,顯示文字提醒或文字加動畫提醒。
        """
        reminder_message = self.reminder_actions[reminder]
        reminder_image = self.reminder_images.get(reminder, None)
        if reminder_image:
            movie = QMovie(reminder_image)
            movie.start()
            QMessageBox.information(self, "提醒", reminder_message, QMessageBox.StandardButton.Ok, QLabel(parent=self).setMovie(movie))
        else:
            QMessageBox.information(self, "提醒", reminder_message, QMessageBox.StandardButton.Ok)

    def show_banner_reminder(self, reminder):
        """
        顯示彈幕提醒。
        根據設定,播放音效或動畫,並顯示文字提醒。
        """
        reminder_message = self.reminder_actions[reminder]
        reminder_image = self.reminder_images.get(reminder, None)
        if reminder_image:
            # 使用 QMediaPlayer 播放提醒音效或動畫
            media_player = QMediaPlayer()
            media_player.setSource(QUrl.fromLocalFile(reminder_image))
            media_player.play()
        QMessageBox.information(self, "提醒", reminder_message, QMessageBox.StandardButton.Ok)

    def open_settings(self):
        """
        開啟設定對話框,管理提醒事件。
        從 SettingsDialog 獲取更新後的提醒事件資料,並更新 ReminderApp 中的相應屬性。
        """
        settings_dialog = SettingsDialog(self.reminders, self.reminder_actions, self.reminder_types, self.reminder_images, self)
        if settings_dialog.exec() == QMessageBox.StandardButton.Ok:
            self.reminders = settings_dialog.reminders
            self.reminder_actions = settings_dialog.reminder_actions
            self.reminder_types = settings_dialog.reminder_types
            self.reminder_images = settings_dialog.reminder_images
            self.save_reminders_to_json()

    def save_reminders_to_json(self):
        """
        將提醒事件資料保存到 JSON 檔案中。
        """
        data = [
            {"time": reminder.toString("hh:mm:ss"), "action": self.reminder_actions[reminder], "type": self.reminder_types[reminder], "image": self.reminder_images.get(reminder, "")}
            for reminder in self.reminders
        ]
        with open("reminders.json", "w") as f:
            json.dump(data, f, indent=4)

class SettingsDialog(QDialog):
    def __init__(self, reminders, reminder_actions, reminder_types, reminder_images, parent=None):
        super().__init__(parent)
        self.setWindowTitle("設定提醒")
        self.setGeometry(100, 100, 600, 400)

        # 建立主要佈局
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # 建立表格
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["時間", "提醒內容", "提醒類型", "提醒圖片"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        main_layout.addWidget(self.table)

        # 建立按鈕
        button_layout = QGridLayout()
        add_button = QPushButton("新增")
        add_button.clicked.connect(self.add_reminder)
        delete_button = QPushButton("刪除")
        delete_button.clicked.connect(self.delete_reminder)
        ok_button = QPushButton("確定")
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(add_button, 0, 0)
        button_layout.addWidget(delete_button, 0, 1)
        button_layout.addWidget(ok_button, 0, 2)
        main_layout.addLayout(button_layout)

        # 初始化表格
        self.reminders = reminders
        self.reminder_actions = reminder_actions
        self.reminder_types = reminder_types
        self.reminder_images = reminder_images
        self.populate_table()

    def populate_table(self):
        """
        將現有的提醒事件填充到表格中。
        """
        self.table.setRowCount(len(self.reminders))
        for i, reminder in enumerate(self.reminders):
            time_item = QTableWidgetItem(reminder.toString("hh:mm:ss"))
            action_item = QTableWidgetItem(self.reminder_actions[reminder])
            type_item = QTableWidgetItem(self.reminder_types[reminder])
            image_item = QTableWidgetItem(self.reminder_images.get(reminder, ""))
            self.table.setItem(i, 0, time_item)
            self.table.setItem(i, 1, action_item)
            self.table.setItem(i, 2, type_item)
            self.table.setItem(i, 3, image_item)

    def add_reminder(self):
        """
        新增提醒事件。
        """
        add_dialog = AddReminderDialog(self)
        if add_dialog.exec() == QMessageBox.StandardButton.Ok:
            reminder_time = add_dialog.time_edit.time()
            reminder_action = add_dialog.action_edit.text()
            reminder_type = add_dialog.type_combo.currentText()
            reminder_image = add_dialog.image_edit.text()

            self.reminders.append(reminder_time)
            self.reminder_actions[reminder_time] = reminder_action
            self.reminder_types[reminder_time] = reminder_type
            self.reminder_images[reminder_time] = reminder_image

            self.populate_table()

    def delete_reminder(self):
        """
        刪除選中的提醒事件。
        """
        selected_rows = self.table.selectionModel().selectedRows()
        for row in reversed(selected_rows):
            reminder = self.reminders.pop(row.row())
            del self.reminder_actions[reminder]
            del self.reminder_types[reminder]
            del self.reminder_images[reminder]
        self.populate_table()

class AddReminderDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
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
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        main_layout.addLayout(button_layout)

    def select_image(self):
        """
        選擇提醒圖片。
        """
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("Image files (*.png *.jpg *.gif)")
        if file_dialog.exec() == QFileDialog.AcceptMode.AcceptOpen:
            selected_file = file_dialog.selectedFiles()[0]
            self.image_edit.setText(selected_file)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    reminder_app = ReminderApp()
    reminder_app.show()
    sys.exit(app.exec())