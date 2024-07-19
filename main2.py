import sys
import json
import time
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QMessageBox
from PyQt6.QtCore import QTimer, QTime
import settings_dialog


class ReminderApp(QWidget):
    def __init__(self, reminders):
        super().__init__()
        self.reminders = reminders  # 儲存提醒列表
        self.initUI()  # 初始化介面

    def initUI(self):
        self.setWindowTitle('提醒 APP')  # 設定視窗標題
        self.setGeometry(100, 100, 300, 200)  # 設定視窗大小和位置

        # 創建開始按鈕
        self.start_button = QPushButton('開始', self)
        self.start_button.clicked.connect(self.startTimer)  # 連接按鈕點擊事件
        self.start_button.resize(100, 30)  # 設定按鈕大小
        self.start_button.move(100, 50)  # 設定按鈕位置

        # 創建設定按鈕
        self.start_button = QPushButton('設定', self)
        self.start_button.clicked.connect(self.openSettings)  # 連接按鈕點擊事件
        self.start_button.resize(100, 30)  # 設定按鈕大小
        self.start_button.move(100, 100)  # 設定按鈕位置

    def openSettings(self):
        # 創建設定對話框
        self.settings_dialog = settings_dialog.SettingsDialog(self, self.reminders)
        self.settings_dialog.exec()


    def startTimer(self):
        # 創建一個計時器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.checkReminders)  # 連接計時器超時事件
        self.timer.start(1000)  # 每秒檢查一次

    def checkReminders(self):
        # 獲取當前時間
        current_time = QTime.currentTime().toString("HH:mm:ss")
        for reminder in self.reminders:
            # 檢查當前時間是否與提醒時間相符
            if reminder['time'] == current_time:
                self.showReminder(reminder)  # 顯示提醒

    def showReminder(self, reminder):
        # 根據提醒類型顯示彈窗
        if reminder['type'] == '彈窗':
            msg = QMessageBox()  # 創建彈窗
            msg.setIcon(QMessageBox.Icon.Information)  # 設定圖示
            msg.setText(reminder['action'])  # 設定提醒內容
            if reminder['image']:
                msg.setInformativeText(f"查看圖片: {reminder['image']}")  # 顯示圖片資訊
            msg.setWindowTitle("提醒")  # 設定彈窗標題
            msg.exec()  # 顯示彈窗

if __name__ == '__main__':
    # JSON 資料
    # 從 reminder.json 檔案讀取 JSON 資料
    with open('reminders.json', 'r', encoding='utf-8') as file:
        reminders = json.load(file)  # 將 JSON 資料轉換為 Python 物件

    app = QApplication(sys.argv)  # 創建應用程式實例
    reminder_app = ReminderApp(reminders)  # 創建提醒 APP 實例
    reminder_app.show()  # 顯示應用程式視窗
    sys.exit(app.exec())  # 執行應用程式並等待結束
