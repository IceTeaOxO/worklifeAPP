import sys
import json
from datetime import datetime
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QTimeEdit, QLabel, QMessageBox, QTableWidget, QTableWidgetItem, QAbstractItemView, QComboBox, QFileDialog, QDialog, QGridLayout, QHBoxLayout, QLineEdit
from PyQt6.QtCore import QTimer, QTime, Qt, QUrl
from PyQt6.QtGui import QMovie
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

        # 初始化定時器
        self.timer = QTimer()
        self.timer.timeout.connect(self.show_reminder)

        # 加載提醒事件
        self.load_reminders_from_json()

    def load_reminders_from_json(self):
        """
        從 JSON 檔案中讀取提醒事件並初始化。
        """
        try:
            with open("reminders.json", "r") as f:
                self.reminders = json.load(f)
        except FileNotFoundError:
            self.reminders = []

    def start_reminder(self):
        """
        開始提醒功能。
        如果有設定好的提醒事件,則依序啟動定時器並顯示提醒。
        如果沒有設定任何提醒事件,則顯示提示訊息。
        """
        if self.reminders:
            for reminder in self.reminders:
                reminder_time = QTime.fromString(reminder["time"], "hh:mm:ss")
                self.timer.start(reminder_time.secsTo(QTime.currentTime()) * 1000)
                self.show_reminder(reminder)
        else:
            QMessageBox.information(self, "提醒", "尚未設定任何提醒事件")

    def show_reminder(self, reminder):
        """
        顯示提醒。
        根據提醒類型,顯示彈窗提醒或彈幕提醒。
        """
        reminder_type = reminder["type"]
        reminder_message = reminder["action"]
        reminder_image = reminder.get("image", None)

        if reminder_type == "彈窗":
            self.show_popup_reminder(reminder_message, reminder_image)
        elif reminder_type == "彈幕":
            self.show_banner_reminder(reminder_message, reminder_image)

    def show_popup_reminder(self, reminder_message, reminder_image):
        """
        顯示彈窗提醒。
        根據設定,顯示文字提醒或文字加動畫提醒。
        """
        if reminder_image:
            movie = QMovie(reminder_image)
            movie.start()
            QMessageBox.information(self, "提醒", reminder_message, QMessageBox.StandardButton.Ok, QLabel(parent=self).setMovie(movie))
        else:
            QMessageBox.information(self, "提醒", reminder_message, QMessageBox.StandardButton.Ok)

    def show_banner_reminder(self, reminder_message, reminder_image):
        """
        顯示彈幕提醒。
        根據設定,播放音效或動畫,並顯示文字提醒。
        """
        if reminder_image:
            media_player = QMediaPlayer()
            media_player.setSource(QUrl.fromLocalFile(reminder_image))
            media_player.play()
        QMessageBox.information(self, "提醒", reminder_message, QMessageBox.StandardButton.Ok)

    def open_settings(self):
        """
        開啟設定對話框,管理提醒事件。
        """
        settings_dialog = SettingsDialog(self)
        settings_dialog.exec()  # 使用 exec() 來顯示對話框並等待用戶操作

class SettingsDialog(QDialog):
    def __init__(self, parent):
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
        self.populate_table()

    def populate_table(self):
        """
        將現有的提醒事件填充到表格中。
        """
        self.table.setRowCount(0)  # 清空表格
        reminders = self.parent().reminders  # 獲取父類別的提醒事件
        for reminder in reminders:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            self.table.setItem(row_position, 0, QTableWidgetItem(reminder["time"]))
            self.table.setItem(row_position, 1, QTableWidgetItem(reminder["action"]))
            self.table.setItem(row_position, 2, QTableWidgetItem(reminder["type"]))
            self.table.setItem(row_position, 3, QTableWidgetItem(reminder.get("image", "")))

    def add_reminder(self):
        """
        新增提醒事件。
        """
        add_dialog = AddReminderDialog(self)
        if add_dialog.exec() == QMessageBox.StandardButton.Ok:
            new_reminder = {
                "time": add_dialog.time_edit.time().toString("hh:mm:ss"),
                "action": add_dialog.action_edit.text(),
                "type": add_dialog.type_combo.currentText(),
                "image": add_dialog.image_edit.text(),
            }
            self.parent().reminders.append(new_reminder)  # 將新提醒添加到父類別的提醒列表
            self.populate_table()  # 更新表格顯示
            self.save_reminders_to_json()  # 保存到 JSON

    def delete_reminder(self):
        """
        刪除選中的提醒事件。
        """
        selected_rows = self.table.selectionModel().selectedRows()
        for row in reversed(selected_rows):
            del self.parent().reminders[row.row()]  # 刪除父類別中的提醒事件
        self.populate_table()  # 更新表格顯示
        self.save_reminders_to_json()  # 保存到 JSON

    def save_reminders_to_json(self):
        """
        將提醒事件資料保存到 JSON 檔案中。
        """
        with open("reminders.json", "w") as f:
            json.dump(self.parent().reminders, f, indent=4)  # 將父類別的提醒列表寫入 JSON

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
