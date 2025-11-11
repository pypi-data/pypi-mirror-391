import sys

from PyQt5.QtCore import Qt, QTranslator, QLocale, QRect
from PyQt5.QtGui import QIcon, QPixmap, QColor, QImage
from PyQt5.QtWidgets import QApplication
from qfluentwidgets import setThemeColor, FluentTranslator, setTheme, Theme, SplitTitleBar, isDarkTheme
from .Ui_LoginWindow import Ui_Form
# from typing import TYPE_CHECKING
# if TYPE_CHECKING:
from ..view.main_window import CustomTitleBar


def isWin11():
    return sys.platform == 'win32' and sys.getwindowsversion().build >= 22000


if isWin11():
    from qframelesswindow import AcrylicWindow as Window
else:
    from qframelesswindow import FramelessWindow as Window


class LoginWindow(Window, Ui_Form):

    def __init__(self, parent: CustomTitleBar, is_stock: bool = True):
        super().__init__()
        # self.titleBar.window().close()
        self.customtitlebar = parent
        self.main_window = parent.main_window
        self.setupUi(self, is_stock)
        # setTheme(Theme.DARK)
        setThemeColor('#28afe9')

        self.setTitleBar(SplitTitleBar(self))
        self.titleBar.raise_()

        self.label.setScaledContents(False)
        self.setWindowTitle('PyQt-Fluent-Widget')
        self.setWindowIcon(QIcon(self.logo_path))
        self.resize(1000, 650)

        self.windowEffect.setMicaEffect(self.winId(), isDarkMode=isDarkTheme())
        if not isWin11():
            color = QColor(25, 33, 42) if isDarkTheme(
            ) else QColor(240, 244, 249)
            self.setStyleSheet(f"LoginWindow{{background: {color.name()}}}")

        if sys.platform == "darwin":
            self.setSystemTitleBarButtonVisible(True)
            self.titleBar.minBtn.hide()
            self.titleBar.maxBtn.hide()
            self.titleBar.closeBtn.hide()

        self.titleBar.titleLabel.setStyleSheet("""
            QLabel{
                background: transparent;
                font: 13px 'Segoe UI';
                padding: 0 4px;
                color: white
            }
        """)

        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        pixmap = QPixmap(QImage(self.background_path)).scaled(
            self.label.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        self.label.setPixmap(pixmap)

    def systemTitleBarRect(self, size):
        """ Returns the system title bar rect, only works for macOS """
        return QRect(size.width() - 75, 0, 75, size.height())

    def closeEvent(self, e):
        super().closeEvent(e)
        if not self.is_stock:
            currentwidget = self.main_window.stackedWidget.currentWidget()
            if hasattr(currentwidget, "connect_api") and hasattr(currentwidget, "_isredy") and not currentwidget._isredy:
                currentwidget.connect_api()


# if __name__ == '__main__':
#     # enable dpi scale
#     QApplication.setHighDpiScaleFactorRoundingPolicy(
#         Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
#     QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
#     QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

#     app = QApplication(sys.argv)

#     # Internationalization
#     translator = FluentTranslator(QLocale())
#     app.installTranslator(translator)

#     w = LoginWindow()
#     w.show()
#     app.exec_()
