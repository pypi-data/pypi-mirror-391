from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtWidgets import QWidget, QTextBrowser
from PyQt5.QtGui import QTextCursor
import sys
# https://blog.csdn.net/weixin_45775701/article/details/106847426


class Emittingstr(QObject):
    textWritten = pyqtSignal(str)  # 定义一个发送str的信号

    def write(self, text):
        self.textWritten.emit(str(text))


class ControlBoard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 下面将输出重定向到textBrowser中
        self.textBrowser = QTextBrowser(self)
        self.textBrowser.setObjectName("textBrowser")
        sys.stdout = Emittingstr(textWritten=self.outputWritten)
        sys.stderr = Emittingstr(textWritten=self.outputWritten)

    def outputWritten(self, text):
        cursor = self.textBrowser.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.textBrowser.setTextCursor(cursor)
        self.textBrowser.ensureCursorVisible()
