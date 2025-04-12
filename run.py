import sys

from PyQt5.QtWidgets import QApplication, QMessageBox

from gui.main_window import MainWindows


class MyApplication(QApplication):
    def notify(self, receiver, event):
        """异常处理函数"""
        try:
            return super().notify(receiver, event)
        except Exception as e:
            message = f"An exception of type {type(e).__name__} occurred.\n{e}"
            QMessageBox.critical(None, "Error", message)
            return False

def handle_exception(exc_type, exc_value, exc_traceback):
    """异常处理函数"""
    message = f"An exception of type {exc_type.__name__} occurred.\n{exc_value}"
    QMessageBox.critical(None, "Error", message)

sys.excepthook = handle_exception

if __name__ == '__main__':
    # 初始化

    app = MyApplication(sys.argv)
    window = MainWindows()

    # 日志控件初始化
    # logger_init(window.tb_log_view, file_name=f"logs/{time.strftime('%Y%m%d-%H%M%S')}.log")

    window.show()
    sys.exit(app.exec_())

# print(open("./config.json", "r", ).read())