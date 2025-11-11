# coding:utf-8
import sys
import typing
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QRect, QUrl
from PyQt5.QtGui import QIcon, QPainter, QImage, QBrush, QColor, QFont, QDesktopServices, QPen
from PyQt5.QtWidgets import QApplication, QFrame, QStackedWidget, QHBoxLayout, QLabel, QVBoxLayout

from qfluentwidgets import (NavigationInterface, NavigationItemPosition, NavigationWidget, MessageBox,
                            isDarkTheme, setTheme, Theme, qrouter, TransparentToolButton, BodyLabel,
                            TransparentDropDownPushButton)
from qfluentwidgets import FluentIcon as FIF
from qframelesswindow import FramelessWindow, TitleBar
from ctypes import cast
from ctypes.wintypes import LPRECT, MSG
from ..app.common.style_sheet import StyleSheet
# import win32api
import win32con
import win32gui
from PyQt5.QtCore import Qt, QSize, QRect
from PyQt5.QtGui import QCloseEvent, QCursor
from PyQt5.QtWidgets import QApplication, QWidget
# from ..titlebar import TitleBar
from qframelesswindow.utils import win32_utils as win_utils
from qframelesswindow.utils.win32_utils import Taskbar
from qframelesswindow.windows.c_structures import LPNCCALCSIZE_PARAMS
from qframelesswindow.windows.window_effect import WindowsWindowEffect
from qframelesswindow.windows import AcrylicWindow
from functools import partial


class WindowsFramelessWindow(QWidget):
    """  Frameless window for Windows system """

    BORDER_WIDTH = 5

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.windowEffect = WindowsWindowEffect(self)
        self._isSystemButtonVisible = False
        self._isResizeEnabled = True

        # self.updateFrameless()

        # solve issue #5
        # self.windowHandle().screenChanged.connect(self.__onScreenChanged)

        # self.resize(500, 500)
        # self.titleBar.raise_()

    def updateFrameless(self):
        """ update frameless window """
        if not win_utils.isWin7():
            self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        elif self.parent():
            self.setWindowFlags(self.parent().windowFlags(
            ) | Qt.FramelessWindowHint | Qt.WindowMinMaxButtonsHint)
        else:
            self.setWindowFlags(Qt.FramelessWindowHint |
                                Qt.WindowMinMaxButtonsHint)

        # add DWM shadow and window animation
        self.windowEffect.addWindowAnimation(self.winId())
        if not isinstance(self, AcrylicWindow):
            self.windowEffect.addShadowEffect(self.winId())

    def setResizeEnabled(self, isEnabled: bool):
        """ set whether resizing is enabled """
        self._isResizeEnabled = isEnabled

    def isSystemButtonVisible(self):
        """ Returns whether the system title bar button is visible """
        return self._isSystemButtonVisible

    def setSystemTitleBarButtonVisible(self, isVisible):
        """ set the visibility of system title bar button, only works for macOS """
        pass

    def systemTitleBarRect(self, size: QSize) -> QRect:
        """ Returns the system title bar rect, only works for macOS

        Parameters
        ----------
        size: QSize
            original system title bar rect
        """
        return QRect(0, 0, size.width(), size.height())

    def nativeEvent(self, eventType, message):
        """ Handle the Windows message """
        msg = MSG.from_address(message.__int__())
        if not msg.hWnd:
            return super().nativeEvent(eventType, message)

        if msg.message == win32con.WM_NCHITTEST and self._isResizeEnabled:
            pos = QCursor.pos()
            xPos = pos.x() - self.x()
            yPos = pos.y() - self.y()
            w = self.frameGeometry().width()
            h = self.frameGeometry().height()

            # fixes issue https://github.com/zhiyiYo/PyQt-Frameless-Window/issues/98
            bw = 0 if win_utils.isMaximized(msg.hWnd) or win_utils.isFullScreen(
                msg.hWnd) else self.BORDER_WIDTH
            lx = xPos < bw
            rx = xPos > w - bw
            ty = yPos < bw
            by = yPos > h - bw
            if lx and ty:
                return True, win32con.HTTOPLEFT
            elif rx and by:
                return True, win32con.HTBOTTOMRIGHT
            elif rx and ty:
                return True, win32con.HTTOPRIGHT
            elif lx and by:
                return True, win32con.HTBOTTOMLEFT
            elif ty:
                return True, win32con.HTTOP
            elif by:
                return True, win32con.HTBOTTOM
            elif lx:
                return True, win32con.HTLEFT
            elif rx:
                return True, win32con.HTRIGHT
        elif msg.message == win32con.WM_NCCALCSIZE:
            if msg.wParam:
                rect = cast(msg.lParam, LPNCCALCSIZE_PARAMS).contents.rgrc[0]
            else:
                rect = cast(msg.lParam, LPRECT).contents

            isMax = win_utils.isMaximized(msg.hWnd)
            isFull = win_utils.isFullScreen(msg.hWnd)

            # adjust the size of client rect
            if isMax and not isFull:
                ty = win_utils.getResizeBorderThickness(msg.hWnd, False)
                rect.top += ty
                rect.bottom -= ty

                tx = win_utils.getResizeBorderThickness(msg.hWnd, True)
                rect.left += tx
                rect.right -= tx

            # handle the situation that an auto-hide taskbar is enabled
            if (isMax or isFull) and Taskbar.isAutoHide():
                position = Taskbar.getPosition(msg.hWnd)
                if position == Taskbar.LEFT:
                    rect.top += Taskbar.AUTO_HIDE_THICKNESS
                elif position == Taskbar.BOTTOM:
                    rect.bottom -= Taskbar.AUTO_HIDE_THICKNESS
                elif position == Taskbar.LEFT:
                    rect.left += Taskbar.AUTO_HIDE_THICKNESS
                elif position == Taskbar.RIGHT:
                    rect.right -= Taskbar.AUTO_HIDE_THICKNESS

            result = 0 if not msg.wParam else win32con.WVR_REDRAW
            return True, result

        return super().nativeEvent(eventType, message)

    def __onScreenChanged(self):
        hWnd = int(self.windowHandle().winId())
        win32gui.SetWindowPos(hWnd, None, 0, 0, 0, 0, win32con.SWP_NOMOVE |
                              win32con.SWP_NOSIZE | win32con.SWP_FRAMECHANGED)


class Widget(QFrame):

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.setObjectName(text.replace(' ', '-'))
        self.label = QLabel(text, self)
        self.label.setAlignment(Qt.AlignCenter)
        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.addWidget(self.label, 1, Qt.AlignCenter)

        # leave some space for title bar
        self.hBoxLayout.setContentsMargins(0, 32, 0, 0)


class AvatarWidget(NavigationWidget):
    """ Avatar widget """

    def __init__(self, parent=None):
        super().__init__(isSelectable=False, parent=parent)
        self.avatar = QImage('resource/shoko.png').scaled(
            24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(
            QPainter.SmoothPixmapTransform | QPainter.Antialiasing)

        painter.setPen(Qt.NoPen)

        if self.isPressed:
            painter.setOpacity(0.7)

        # draw background
        if self.isEnter:
            c = 255 if isDarkTheme() else 0
            painter.setBrush(QColor(c, c, c, 10))
            painter.drawRoundedRect(self.rect(), 5, 5)

        # draw avatar
        painter.setBrush(QBrush(self.avatar))
        painter.translate(8, 6)
        painter.drawEllipse(0, 0, 24, 24)
        painter.translate(-8, -6)

        if not self.isCompacted:
            painter.setPen(Qt.white if isDarkTheme() else Qt.black)
            font = QFont('Segoe UI')
            font.setPixelSize(14)
            painter.setFont(font)
            painter.drawText(QRect(44, 0, 255, 36), Qt.AlignVCenter, 'zhiyiYo')


class CustomTitleBar(TitleBar):
    """ Title bar with icon and title """

    def __init__(self, parent):
        super().__init__(parent)
        # add window icon
        self.iconLabel = QLabel(self)
        self.iconLabel.setFixedSize(18, 18)
        self.hBoxLayout.insertSpacing(0, 10)
        self.hBoxLayout.insertWidget(
            1, self.iconLabel, 0, Qt.AlignLeft | Qt.AlignBottom)
        self.window().windowIconChanged.connect(self.setIcon)

        # add title label
        self.titleLabel = QLabel(self)
        self.hBoxLayout.insertWidget(
            2, self.titleLabel, 0, Qt.AlignLeft | Qt.AlignBottom)
        self.titleLabel.setObjectName('titleLabel')
        self.window().windowTitleChanged.connect(self.setTitle)

    def setTitle(self, title):
        self.titleLabel.setText(title)
        self.titleLabel.adjustSize()

    def setIcon(self, icon):
        self.iconLabel.setPixmap(QIcon(icon).pixmap(18, 18))


class SidebarInfoInterface(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.ChartMdiAreaWidget = parent
        # self.setTitleBar(CustomTitleBar(self))

        # use dark theme mode
        # setTheme(Theme.DARK)
        # self.setWindowFlags(Qt.MSWindowsFixedSizeDialogHint |
        #                     Qt.WindowStaysOnTopHint)

        self.hBoxLayout = QHBoxLayout(self)
        self.navigationInterface = NavigationInterface(
            self, showMenuButton=False, showReturnButton=False)
        self.setFixedWidth(48)
        # self.stackWidget = QStackedWidget(self)
        # initialize layout
        self.initLayout()

    def set_stackWidget(self, *widget: QStackedWidget):
        self.stackWidget = widget[0]
        # self.stackWidget.adjustSize()
        # create sub interface
        # widget[1]  # Widget('Search Interface', self)
        self.searchInterface = QuoteToolBar(widget[1], self)
        self.musicInterface = Widget('Music Interface', self)
        self.videoInterface = Widget('Video Interface', self)
        self.folderInterface = Widget('Folder Interface', self)
        self.settingInterface = Widget('Setting Interface', self)

        # add items to navigation interface
        self.initNavigation()
        self.initWindow()
        # StyleSheet.NAVIGATION_VIEW_INTERFACE.apply(self)

    def initLayout(self):
        # self.hBoxLayout.setSpacing(0)
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        # self.hBoxLayout.addWidget(self.stackWidget)
        # self.hBoxLayout.setStretchFactor(self.stackWidget, 1)
        self.hBoxLayout.addWidget(self.navigationInterface)
        self.navigationInterface.panel.vBoxLayout.setContentsMargins(
            0, 5, 0, 5)
        self.navigationInterface.panel.topLayout.setContentsMargins(0, 0, 0, 0)
        self.navigationInterface.panel.bottomLayout.setContentsMargins(
            0, 0, 0, 0)
        self.navigationInterface.panel.scrollLayout.setContentsMargins(
            0, 0, 0, 0)
        self.navigationInterface.panel.vBoxLayout.setSpacing(4)
        self.navigationInterface.panel.topLayout.setSpacing(4)
        self.navigationInterface.panel.bottomLayout.setSpacing(4)
        self.navigationInterface.panel.scrollLayout.setSpacing(4)

        # self.titleBar.raise_()
        # self.navigationInterface.displayModeChanged.connect(
        #    self.titleBar.raise_)

    def initNavigation(self):
        # enable acrylic effect
        # self.navigationInterface.setAcrylicEnabled(True)
        self._count = 1
        self.addSubInterface(self.searchInterface, FIF.SEARCH, "MarketPage")
        self.addSubInterface(self.musicInterface, FIF.MUSIC, 'Music library')
        self.addSubInterface(self.videoInterface, FIF.VIDEO, 'Video library')

        self.navigationInterface.addSeparator()

        # add navigation items to scroll area
        self.addSubInterface(self.folderInterface, FIF.FOLDER,
                             'Folder library', NavigationItemPosition.SCROLL)
        # for i in range(1, 21):
        #     self.navigationInterface.addItem(
        #         f'folder{i}',
        #         FIF.FOLDER,
        #         f'Folder {i}',
        #         lambda: print('Folder clicked'),
        #         position=NavigationItemPosition.SCROLL
        #     )

        # add custom widget to bottom
        # self.navigationInterface.addWidget(
        #     routeKey='avatar',
        #     widget=AvatarWidget(),
        #     onClick=self.showMessageBox,
        #     position=NavigationItemPosition.BOTTOM
        # )

        self.addSubInterface(self.settingInterface, FIF.SETTING,
                             'Settings', NavigationItemPosition.BOTTOM)

        #!IMPORTANT: don't forget to set the default route key
        qrouter.setDefaultRouteKey(
            self.stackWidget, self.searchInterface.objectName())

        # set the maximum width
        # self.navigationInterface.setExpandWidth(300)
        self._last_index = 1

        self.stackWidget.currentChanged.connect(self.onCurrentInterfaceChanged)
        # self.stackWidget.setCurrentIndex(1)
        self.stackWidget.setCurrentWidget(self.searchInterface)
        # self.stackWidget.hide()

    def initWindow(self):
        # self.resize(900, 700)
        # self.setWindowIcon(QIcon('resource/logo.png'))
        # self.setWindowTitle('PyQt-Fluent-Widgets')
        # self.titleBar.setAttribute(Qt.WA_StyledBackground)

        # desktop = QApplication.desktop().availableGeometry()
        # w, h = desktop.width(), desktop.height()
        # self.move(w//2 - self.width()//2, h//2 - self.height()//2)

        # self.setQss()
        ...

    def addSubInterface(self, interface, icon, text: str, position=NavigationItemPosition.TOP):
        """ add sub interface """
        setattr(interface, "_index", self._count)
        self._count += 1
        self.stackWidget.addWidget(interface)
        self.navigationInterface.addItem(
            routeKey=interface.objectName(),
            icon=icon,
            text=text,
            onClick=partial(self.switchTo, widget=interface),
            position=position,
            tooltip=text
        )

    # def setQss(self):
    #     color = 'dark' if isDarkTheme() else 'light'
    #     with open(f'resource/{color}/demo.qss', encoding='utf-8') as f:
    #         self.setStyleSheet(f.read())

    def switchTo(self, widget):
        splitter = self.ChartMdiAreaWidget.mdi_info_splitter
        if not splitter.mdi_info_splitter_sizes:
            splitter.mdi_info_splitter_sizes = [
                self.ChartMdiAreaWidget.width()-290, 290]
        if self._last_index == widget._index:

            sizes = splitter.sizes()
            if sizes[1] > 0:
                splitter.setSizes([1, 0])
            else:
                splitter.setSizes(splitter.mdi_info_splitter_sizes)
        self.stackWidget.setCurrentWidget(widget)
        # self._last_index = index

    def onCurrentInterfaceChanged(self, index):
        widget = self.stackWidget.widget(index)
        self.navigationInterface.setCurrentItem(widget.objectName())
        qrouter.push(self.stackWidget, widget.objectName())
        self._last_index = widget._index
        splitter = self.ChartMdiAreaWidget.mdi_info_splitter
        splitter.setSizes(splitter.mdi_info_splitter_sizes)
        # if self.stackWidget.isHidden():
        #     self.stackWidget.show()

    def showMessageBox(self):
        ...
        # w = MessageBox(
        #     '支持作者🥰',
        #     '个人开发不易，如果这个项目帮助到了您，可以考虑请作者喝一瓶快乐水🥤。您的支持就是作者开发和维护项目的动力🚀',
        #     self
        # )
        # w.yesButton.setText('来啦老弟')
        # w.cancelButton.setText('下次一定')

        # if w.exec():
        #     QDesktopServices.openUrl(QUrl("https://afdian.net/a/zhiyiYo"))


class ToolBar(QWidget):
    def __init__(self, name: str, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.setFixedHeight(32)
        hlayout = QHBoxLayout(self)
        self.tool = TransparentToolButton(FIF.CHEVRON_RIGHT_MED)
        # self.tool.setFixedHeight(20)
        self.tool.setIconSize(QSize(16, 16))
        self.tool._ischeck = False
        label = BodyLabel(name)
        hlayout.addWidget(self.tool)
        hlayout.addWidget(label)
        hlayout.setContentsMargins(2, 4, 2, 4)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        c = 255 if isDarkTheme() else 0
        pen = QPen(QColor(c, c, c, 15))
        pen.setCosmetic(True)
        painter.setPen(pen)
        painter.drawRect(1, 1, self.width()-2, self.height()-2)


class SettingBar(QWidget):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        qsize = QSize(16, 16)
        self.setFixedHeight(34)
        hlayout = QHBoxLayout(self)
        self.tool = TransparentToolButton(FIF.CHEVRON_RIGHT_MED)
        self.table = TransparentDropDownPushButton("自选表")
        self.setting = TransparentToolButton(FIF.MORE)
        self.setting.setToolTip("设置")
        self.setting.setIconSize(qsize)
        self.single = TransparentToolButton(FIF.PIE_SINGLE)
        self.single.setToolTip("高级视图")
        self.single.setIconSize(qsize)
        self.addto = TransparentToolButton(FIF.ADD)
        self.addto.setToolTip("添加商品代码")
        self.addto.setIconSize(qsize)
        self.tool.setIconSize(qsize)
        self.tool._ischeck = False
        hlayout.addWidget(self.tool)
        hlayout.addWidget(self.table)
        hlayout.addStretch(1)
        hlayout.addWidget(self.addto, alignment=Qt.AlignRight)
        hlayout.addWidget(self.single, alignment=Qt.AlignRight)
        hlayout.addWidget(self.setting, alignment=Qt.AlignRight)
        hlayout.setContentsMargins(2, 4, 2, 4)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        c = 255 if isDarkTheme() else 0
        pen = QPen(QColor(c, c, c, 15))
        pen.setCosmetic(True)
        painter.setPen(pen)
        painter.drawRect(1, 1, self.width()-2, self.height()-2)


class QuoteToolBar(QWidget):
    def __init__(self, widgets: dict[str, QWidget], parent: QWidget = None) -> None:
        super().__init__(parent)
        self.vlayout = QVBoxLayout(self)
        self.settingbar = SettingBar(self)
        self.vlayout.addWidget(self.settingbar)
        self.vlayout.addSpacing(1)
        self.add_widget(widgets)

    def add_widget(self, widgets: dict[str, QWidget]):
        for name, widget in widgets.items():
            vlayout = QVBoxLayout()
            toolbar = ToolBar(name)
            vlayout.addWidget(toolbar)
            vlayout.addSpacing(1)
            vlayout.addWidget(widget)
            vlayout.setContentsMargins(0, 0, 0, 0)
            toolbar.tool.clicked.connect(
                partial(self.click_tool, tool=toolbar.tool, widget=widget))
            self.vlayout.addLayout(vlayout)

        self.vlayout.addWidget(QWidget(self))
        self.vlayout.setContentsMargins(0, 0, 0, 0)

    def click_tool(self, tool: TransparentToolButton, widget: QWidget):
        if tool._ischeck:
            tool.setIcon(FIF.CHEVRON_DOWN_MED)
            widget.show()
        else:
            tool.setIcon(FIF.CHEVRON_RIGHT_MED)
            widget.hide()
        tool._ischeck = not tool._ischeck

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        c = 255 if isDarkTheme() else 0
        pen = QPen(QColor(c, c, c, 15))
        pen.setCosmetic(True)
        painter.setPen(pen)
        painter.drawRect(1, 1, self.width()-2, self.height()-2)
