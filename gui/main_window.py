import json
import os
import threading
import time

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QMenu, QAction

from utils.s_yi_ban import SyiBan
from utils.logging_utils import QTextBrowserHandler, logger
from view.main_windows import Ui_MainWindow


class MainWindows(QMainWindow, Ui_MainWindow):
    config_path = "./data/config.json"

    def __init__(self):
        super(MainWindows, self).__init__()
        self.log_handler = None
        self.setupUi(self)
        self.init_log()
        self.init_listener()
        self.init_table()
        self.load_config()

    def init_listener(self):
        self.btn_add_account.clicked.connect(self.add_account)
        self.btn_get_dsapi.clicked.connect(self.get_dsapi)
        self.btn_run.clicked.connect(self.run_spider)
    def init_log(self):
        self.log_handler = QTextBrowserHandler(self.tb_log)
        logger.addHandler(self.log_handler)

    def init_table(self):
        # 设置 QTableWidget 的选择行为为整行选择
        self.tw_account.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        # 设置右键菜单
        self.tw_account.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tw_account.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, pos):
        """显示右键菜单"""
        menu = QMenu(self.tw_account)
        delete_action = QAction("删除选中行", self)
        delete_action.triggered.connect(self.delete_selected_row)
        menu.addAction(delete_action)
        menu.exec_(self.tw_account.viewport().mapToGlobal(pos))

    def delete_selected_row(self):
        """删除选中的行"""
        selected_row = self.tw_account.currentRow()
        if selected_row != -1:
            self.tw_account.removeRow(selected_row)
            logger.info(f"删除了第 {selected_row + 1} 行")
            self.save_config()

    def add_account(self):
        """添加账户到表格中"""
        username = self.le_username.text()
        password = self.le_password.text()
        rows = self.tw_account.rowCount()
        self.tw_account.setRowCount(rows + 1)
        u_item = QtWidgets.QTableWidgetItem()
        u_item.setText(username)
        p_item = QtWidgets.QTableWidgetItem()
        p_item.setText(password)
        self.tw_account.setItem(rows, 0, u_item)
        self.tw_account.setItem(rows, 1, p_item)
        logger.info(f"添加了账户：用户名={username}, 密码={password}")
        self.save_config()

    def get_config(self):
        accounts = []
        for row in range(self.tw_account.rowCount()):
            username = self.tw_account.item(row, 0).text()
            password = self.tw_account.item(row, 1).text()
            accounts.append({"username": username, "password": password})
        ds_api = self.le_dsapi.text()
        driver_type = self.cb_driver.currentText()
        run_time = self.sp_run_time.value()
        sleep_time = self.sp_sleep_time.value()
        post_type = self.le_post_type.text()
        post_board = self.le_post_board.text()
        title_pre = self.le_title_pre.text()
        config = {
            "accounts": accounts,
            "ds_api": ds_api,
            "driver_type": driver_type,
            "run_time": run_time,
            "sleep_time": sleep_time,
            "post_type": post_type,
            "post_board": post_board,
            "title_pre": title_pre,
        }
        return config

    def save_config(self):
        config = self.get_config()
        print(config)
        if not os.path.exists("./data"):
            os.mkdir("./data")
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
        logger.info("保存配置成功!")

    def get_dsapi(self):
        import webbrowser
        webbrowser.open("https://platform.deepseek.com/usage")
        logger.info("已打开浏览器，请在浏览器中获取key!")

    def load_config(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                accounts = config["accounts"]
                ds_api = config["ds_api"]
                driver_type = config["driver_type"]
                run_time = config["run_time"]
                sleep_time = config["sleep_time"]
                post_type = config["post_type"]
                post_board = config["post_board"]
                title_pre = config["title_pre"]
                self.tw_account.setRowCount(len(accounts))
                for index in range(len(accounts)):
                    username = accounts[index]["username"]
                    password = accounts[index]["password"]
                    u_item = QtWidgets.QTableWidgetItem()
                    u_item.setText(username)
                    p_item = QtWidgets.QTableWidgetItem()
                    p_item.setText(password)
                    self.tw_account.setItem(index, 0, u_item)
                    self.tw_account.setItem(index, 1, p_item)
                self.le_dsapi.setText(ds_api)
                self.cb_driver.setCurrentText(driver_type)
                self.sp_sleep_time.setValue(sleep_time)
                self.sp_run_time.setValue(run_time)
                self.le_title_pre.setText(title_pre)
                self.le_post_board.setText(post_board)
                self.le_post_type.setText(post_type)
                logger.info("从文件加载配置完成!")

    def run_spider(self):
        self.save_config()

        def run():
            config = self.get_config()
            accounts = config["accounts"]
            ds_api = config["ds_api"]
            driver_type = config["driver_type"]
            run_time = config["run_time"]
            sleep_time = config["sleep_time"]
            post_type = config["post_type"]
            post_board = config["post_board"]
            title_pre = config["title_pre"]
            for account in accounts:
                username = account["username"]
                password = account["password"]
                yiban = SyiBan(username, password, driver_type=driver_type)
                for cnt in range(run_time):
                    logger.info(f"{username}第{cnt + 1}次发帖已开始!")
                    post = yiban.post(ds_api, post_type, post_board, title_pre)
                    if post is not None:
                        rowcount = self.tw_out.rowCount()
                        self.tw_out.setRowCount(rowcount + 1)
                        title = QtWidgets.QTableWidgetItem()
                        title.setText(post["title"])
                        time_item = QtWidgets.QTableWidgetItem()
                        time_item.setText(post["time"])
                        url = QtWidgets.QTableWidgetItem()
                        url.setText(post["url"])
                        self.tw_out.setItem(rowcount, 0, title)
                        self.tw_out.setItem(rowcount, 1, time_item)
                        self.tw_out.setItem(rowcount, 2, url)

                    if cnt < run_time - 1:
                        logger.warning(f"由于易班发帖限制，{sleep_time}秒后继续下一次发帖...")
                        for remaining in range(sleep_time, 0, -1):
                            logger.info(f"剩余等待时间: {remaining}秒")
                            time.sleep(1)
                        logger.info("等待结束，继续执行下一个任务")

        thread = threading.Thread(target=run)
        thread.start()
