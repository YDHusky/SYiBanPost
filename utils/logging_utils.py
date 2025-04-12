import logging
import os
import time

from PyQt5.QtWidgets import QTextBrowser

if not os.path.exists('logs'):
    os.mkdir('logs')
# 设置全局的日志记录格式和日志等级
logging.basicConfig(format="%(asctime)s %(name)s %(levelname)s %(message)s", level=logging.INFO,
                    filename=f'./logs/log-{str(time.time())}.log', filemode='w',
                    datefmt='%d/%m/%Y %H:%M:%S')


class QTextBrowserHandler(logging.Handler):
    """
    接收一个参数 text_browser，它是一个 PyQt5 的 QTextBrowser 控件，特征是不可编辑的文本框，适合用来记录日志。
    """
    def __init__(self, text_browser: QTextBrowser):
        super().__init__()
        self.text_browser = text_browser

        # 给此 handler 定义日志的格式
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        self.setFormatter(formatter)

    def emit(self, record):
        """日志处理函数，格式化日志数据后，写入到 QTextBrowser 控件中"""
        try:
            # 获取日志级别
            level = record.levelname
            # 根据日志级别设置颜色

            if level == "DEBUG":
                color = "blue"
            elif level == "INFO":
                color = "black"
            elif level == "WARNING":
                color = "orange"
            elif level == "ERROR":
                color = "red"
            elif level == "CRITICAL":
                color = "purple"
            else:
                color = "black"

            # 格式化日志消息并添加颜色
            msg = f"<font color='{color}'>{self.format(record)}</font>"
            self.text_browser.append(msg)
        except Exception as e:
            # 如果出现异常，记录到全局日志
            logger.error(e)


# 创建一个 logger 实例，其他模块引用该实例来记录日志
logger = logging.getLogger()