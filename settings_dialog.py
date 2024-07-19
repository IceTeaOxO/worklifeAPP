import json
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QTimeEdit, QLabel, QMessageBox, QTableWidget, QTableWidgetItem, QAbstractItemView, QComboBox, QFileDialog, QDialog, QGridLayout, QHBoxLayout, QLineEdit
import add_reminder_dialog
from add_reminder_dialog import AddReminderDialog


class SettingsDialog(QDialog):
    def __init__(self, parent, reminders):
        super().__init__(parent)
        self.init_UI()
        self.reminders = reminders

    def init_UI(self):
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
        self.add_dialog = AddReminderDialog(self)
        # self.add_dialog.exec()
        if self.add_dialog.exec() == QDialog.DialogCode.Accepted:
            self.populate_table()  # 更新表格顯示
        # add_dialog = AddReminderDialog(self)
        # if add_dialog.exec() == QMessageBox.StandardButton.Ok:
        #     new_reminder = {
        #         "time": add_dialog.time_edit.time().toString("hh:mm:ss"),
        #         "action": add_dialog.action_edit.text(),
        #         "type": add_dialog.type_combo.currentText(),
        #         "image": add_dialog.image_edit.text(),
        #     }
        #     self.parent().reminders.append(new_reminder)  # 將新提醒添加到父類別的提醒列表
        #     self.populate_table()  # 更新表格顯示
        #     self.save_reminders_to_json()  # 保存到 JSON

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
