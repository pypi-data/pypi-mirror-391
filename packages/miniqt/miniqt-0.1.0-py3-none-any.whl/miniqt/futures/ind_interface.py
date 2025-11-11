# coding:utf-8
from __future__ import annotations
from qfluentwidgets.components.widgets.menu import ShortcutMenuItemDelegate, SmoothScrollDelegate, MenuAnimationManager
import sys
from pathlib import Path
from PyQt5 import QtCore, QtGui

from PyQt5.QtCore import pyqtSignal, Qt, QPoint, QSize, QUrl, QRect, QPropertyAnimation, pyqtProperty, QRectF
from PyQt5.QtGui import QIcon, QFont, QColor, QPainter, QDesktopServices, QCursor, QWheelEvent, QPainterPath, QMouseEvent, QPen
from PyQt5.QtWidgets import QToolButton, QListWidget, QWidgetAction, QApplication, QWidget, QHBoxLayout, QVBoxLayout, QTreeWidgetItem, QTreeWidgetItemIterator, QFrame

from qfluentwidgets import (ColorPickerButton, CommandBarView, CardWidget, setTheme, Theme, IconWidget, BodyLabel, CaptionLabel, PushButton,
                            TransparentToolButton, FluentIcon, RoundMenu, Action, ElevatedCardWidget, AvatarWidget,
                            ImageLabel, isDarkTheme, FlowLayout, MSFluentTitleBar, SimpleCardWidget, TreeWidget, FluentWindow,
                            HeaderCardWidget, InfoBarIcon, HyperlinkLabel, HorizontalFlipView, SingleDirectionScrollArea,
                            PrimaryPushButton, TitleLabel, PillPushButton, setFont, ScrollArea, TransparentDropDownPushButton,
                            VerticalSeparator, LineEdit, MSFluentWindow, NavigationItemPosition, GroupHeaderCardWidget,
                            ComboBox, SearchLineEdit, ToolButton, CommandBar, ColorDialog, FlowLayout)
from qfluentwidgets.common.style_sheet import FluentStyleSheet, themeColor, ThemeColor
from qfluentwidgets.components.widgets.command_bar import CommandViewMenu, MenuAnimationType, CommandViewBar
from qfluentwidgets.components.widgets.acrylic_label import AcrylicBrush
from qfluentwidgets.common.overload import singledispatchmethod
from ..utils import Icons, Union, partial, Iterable
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets.common.icon import FluentIconBase, drawIcon, isDarkTheme, Theme, toQIcon, Icon
from ..app.common.style_sheet import StyleSheet
from ..utils import Color, Indicator_Dict
from typing_extensions import Literal, Callable, TYPE_CHECKING
# from utils import MyColorDialog
if TYPE_CHECKING:
    from ..app.view.main_window import MainWindow
    from .futures_interface import FuturesInterface, QTimer, QtimerExplorer
LINE_STYLE: Literal['solid', 'dotted',
                    'dashed', 'large_dashed', 'sparse_dotted'] = ['solid', 'dotted',
                                                                  'dashed', 'large_dashed', 'sparse_dotted']


def isWin11():
    return sys.platform == 'win32' and sys.getwindowsversion().build >= 22000


if isWin11():
    from qframelesswindow import AcrylicWindow as Window
else:
    from qframelesswindow import FramelessWindow as Window


def mousePressEvent(self, e):
    self.func()


class HyperlinkButton(PushButton):
    """ Hyperlink button

    Constructors
    ------------
    * HyperlinkButton(`parent`: QWidget = None)
    * HyperlinkButton(`url`: str, `text`: str, `parent`: QWidget = None,
                      `icon`: QIcon | str | FluentIconBase = None)
    """

    @singledispatchmethod
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self._url = QUrl()
        FluentStyleSheet.BUTTON.apply(self)
        self.setCursor(Qt.PointingHandCursor)
        setFont(self)
        self.clicked.connect(self._onClicked)

    @__init__.register
    def _(self, text: str, parent: QWidget = None, icon: Union[QIcon, FluentIconBase, str] = None):
        self.__init__(parent)
        self.setText(text)
        # self.url.setUrl(url)
        self.setIcon(icon)

    @__init__.register
    def _(self, icon: QIcon, url: str, text: str, parent: QWidget = None):
        self.__init__(url, text, parent, icon)

    @__init__.register
    def _(self, icon: FluentIconBase, url: str, text: str, parent: QWidget = None):
        self.__init__(url, text, parent, icon)

    def getUrl(self):
        return self._url

    def setUrl(self, url: Union[str, QUrl]):
        self._url = QUrl(url)

    def _onClicked(self):
        ...
        # if self.getUrl().isValid():
        #     QDesktopServices.openUrl(self.getUrl())

    def _drawIcon(self, icon, painter, rect, state=QIcon.Off):
        if isinstance(icon, FluentIconBase) and self.isEnabled():
            icon = icon.icon(color=themeColor())
        elif not self.isEnabled():
            painter.setOpacity(0.786 if isDarkTheme() else 0.9)
            if isinstance(icon, FluentIconBase):
                icon = icon.icon(Theme.DARK)

        drawIcon(icon, painter, rect, state)

    url = pyqtProperty(QUrl, getUrl, setUrl)


class MicaWindow(Window):

    def __init__(self):
        super().__init__()
        # self.setTitleBar(MSFluentTitleBar(self))
        if isWin11():
            self.windowEffect.setMicaEffect(self.winId(), isDarkTheme())


class ProfileCard(QWidget):
    """ Profile card """

    def __init__(self, avatarPath: str, name: str, email: str, parent=None, FuturesInterface: FuturesInterface = None):
        super().__init__(parent=parent)
        self.FuturesInterface = FuturesInterface
        self.avatar = AvatarWidget(avatarPath, self)
        self.nameLabel = BodyLabel(name, self)
        self.emailLabel = CaptionLabel(email, self)
        self.logoutButton = HyperlinkButton('技术指标', self)

        color = QColor(206, 206, 206) if isDarkTheme() else QColor(96, 96, 96)
        self.emailLabel.setStyleSheet('QLabel{color: '+color.name()+'}')

        color = QColor(255, 255, 255) if isDarkTheme() else QColor(0, 0, 0)
        self.nameLabel.setStyleSheet('QLabel{color: '+color.name()+'}')
        setFont(self.logoutButton, 13)

        self.setFixedSize(384, 82)
        self.avatar.setRadius(24)
        self.avatar.move(2, 6)
        self.nameLabel.move(64, 13)
        self.emailLabel.move(64, 32)
        self.logoutButton.move(52, 48)


class _Menu(RoundMenu):
    def __init__(self, title="", parent=None):
        super().__init__(title, parent=parent)
        # self.hBoxLayout.removeWidget(self.view)
        # self.view.deleteLater()
        # self.view = MenuActionListWidget(self)
        # self.hBoxLayout.addWidget(self.view, 1, Qt.AlignCenter)
        # self.view.itemClicked.connect(self._onItemClicked)
        # self.view.itemEntered.connect(self._onItemEntered)

    def __initWidgets(self):
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint |
                            Qt.NoDropShadowWindowHint)
        # self.setWindowFlags(Qt.FramelessWindowHint)
        # self.setAttribute(Qt.WA_MacShowFocusRect, False)
        # self.setAttribute(Qt.WA_OpaquePaintEvent)
        self.setAutoFillBackground(True)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMouseTracking(True)

        self.timer.setSingleShot(True)
        self.timer.setInterval(400)
        self.timer.timeout.connect(self._onShowMenuTimeOut)

        # self.setShadowEffect()
        self.hBoxLayout.addWidget(self.view, 1, Qt.AlignCenter)

        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        FluentStyleSheet.MENU.apply(self)

        self.view.itemClicked.connect(self._onItemClicked)
        self.view.itemEntered.connect(self._onItemEntered)

    def setShadowEffect(self, blurRadius=30, offset=(0, 8), color=QColor(0, 0, 0, 30)):
        ...


class ColorButton(QToolButton):
    """ Color picker button """

    colorChanged = pyqtSignal(QColor)

    def __init__(self, color: QColor, title: str, parent: IndicatorItemWidget = None, qtimer: QTimer = None, indname="", enableAlpha=False):
        super().__init__(parent=parent)
        self.IndicatorItemWidget = parent
        self.qtimer = qtimer
        self.indname = indname
        self.title = title
        self.enableAlpha = enableAlpha
        # self.setFixedSize(96, 32)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.setColor(color)
        self.setCursor(Qt.PointingHandCursor)
        self.clicked.connect(self.__showColorDialog)

    def __showColorDialog(self):
        """ show color dialog """
        Menu = _Menu(
            "color", parent=self.IndicatorItemWidget.FuturesInterface)
        Menu.setStyleSheet("background: transparent;")
        Menu.setFocusPolicy(Qt.NoFocus)
        ww = QWidget()
        ww.setWindowFlags(Qt.FramelessWindowHint |
                          Qt.NoDropShadowWindowHint | Qt.Tool)
        ww.setAutoFillBackground(True)
        ww.setAttribute(Qt.WA_TranslucentBackground)
        ww.setStyleSheet("background: transparent;")
        ww.setFocusPolicy(Qt.NoFocus)
        ww._layout = QHBoxLayout(ww)

        self.colordialogwin = ColorDialog(self.color, self.title,
                                          self.IndicatorItemWidget.FuturesInterface.currentwidget, self.enableAlpha)
        self.colordialogwin.hexLineEdit.move(120, 381)
        self.colordialogwin.colorbutton: TransparentToolButton = TransparentToolButton(
            FIF.ADD, self.colordialogwin)
        self.colordialogwin.colorbutton.clicked.connect(self.showColorDialog)
        self.colordialogwin.colorbutton.setToolTip("其它颜色")
        self.colordialogwin.colorbutton.setFixedWidth(40)
        self.colordialogwin.colorbutton.move(364, 415)
        self.colordialogwin.colorChanged.connect(
            partial(self.__onColorChanged, menu=Menu))
        ww._layout.addWidget(self.colordialogwin)
        ww._layout.setContentsMargins(0, 0, 0, 0)

        ww.setFixedSize(528, 696)
        Menu.view.setViewportMargins(0, 0, 0, 0)
        Menu.view.setFocusPolicy(Qt.NoFocus)
        Menu.view.setFrameShape(QFrame.NoFrame)
        Menu.view.setStyleSheet(
            "background: transparent;")
        Menu.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        Menu.addWidget(ww)
        Menu.setFixedSize(528, 696)

        pos = QCursor.pos()
        pos.setX(pos.x()-100)
        pos.setY(pos.y()+30)
        Menu.exec(pos)

    def showColorDialog(self):
        Menu = RoundMenu("style", parent=self)
        for i, color in enumerate(Color):
            if i % 30 == 0:
                menu = RoundMenu(f"color{int(i/30)}", Menu)
                # menu.triggered.connect(
                #     partial(self.color_connect, name=name, qtimer=qtimer))
                Menu.addMenu(menu)
            action = QWidgetAction(menu)
            w = PillPushButton(color)
            w.clicked.connect(
                partial(self.__onColorChanged, color=color, menu=Menu, menu_=menu))
            # w.clicked.connect(partial(self.color_connect, menu=menu, action=action,
            #                   color=color, name=name, qtimer=qtimer))
            w.setStyleSheet(f"background-color:{color}")
            action.setDefaultWidget(w)
            menu.addAction(action)
        pos = QCursor.pos()
        pos.setX(pos.x()+20)
        pos.setY(pos.y()-100)
        Menu.exec(pos)

    def __onColorChanged(self, color, menu=None, menu_=None):
        """ color changed slot """
        self.setColor(color)
        self.colorChanged.emit(self.color)
        if menu_ is not None:
            self.colordialogwin.hexLineEdit.setText(color)
            menu_._hideMenu(True)
        menu._hideMenu(True)

    def setColor(self, color):
        """ set color """
        self.color = QColor(color)
        self.update()

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing)
        pc = QColor(255, 255, 255, 10) if isDarkTheme(
        ) else QColor(234, 234, 234)
        painter.setPen(pc)

        color = QColor(self.color)
        if not self.enableAlpha:
            color.setAlpha(255)

        painter.setBrush(color)
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 5, 5)


class IndicatorItemWidget(QWidget):  # CardWidget):
    # , FuturesInterface=None) -> None:
    def __init__(self, parent: FuturesInterface = None, menu: IndMenu = None, height=20):
        super().__init__(parent)
        self._borderRadius = 0
        self._count = 0
        self._height = height
        # self.setFixedHeight(self._height)
        # self.mode = mode
        # self.qtimer = qtimer
        self.menu = menu
        self.FuturesInterface = parent
        self.vlayout = QVBoxLayout(self)
        self.bars: list[list[QWidget]] = []
        self._initItems()
        self.key_on = False
        # self.adjustSize()
        self.default_params = {}
        self.params = {}

    def creat_indicator_bar(self, mode, qtimer: QTimer):
        bars = []
        main = mode == "M"
        w = 26
        for _, line in qtimer.lines.items():

            bar = CommandBar(self)
            bar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
            bar.setFixedHeight(self._height)
            mode = TransparentToolButton(FIF.TAG if main else FIF.FLAG)
            mode.setToolTip("主图" if main else "副图")
            # mode.setFixedSize(self._height, self._height)
            mode.setFixedWidth(w)
            bar.addWidget(mode)
            name = BodyLabel(line.name)
            name.setAlignment(Qt.AlignVCenter)
            name.setToolTip(line.name)
            name.setFixedWidth(100)
            # name.setFixedWidth(1self._height)
            # name.setFixedHeight(self._height)
            bar.addWidget(name)
            bar.addSeparator()
            # bar.addAction(Action(self.tr(line.name)))
            # color = TransparentToolButton(FluentIcon.PALETTE)
            color = ColorButton(
                QColor(line.color), '选择指标颜色', self, qtimer, line.name, enableAlpha=True)
            color.colorChanged.connect(
                partial(self.color_connect, name=line.name, qtimer=qtimer))
            color.setFixedSize(w, self._height)
            # color.colorChanged.connect(lambda color: print(color))
            # color.setFixedWidth(w)
            # color.clicked.connect(
            #     partial(self.showColorDialog, name=line.name, qtimer=qtimer, button=color))
            color.setToolTip("颜色")
            # color.setFixedSize(self._height, self._height)
            color.setStyleSheet(f"background-color:{line.color}")
            bar.addWidget(color)
            style = TransparentToolButton(FluentIcon.ALIGNMENT)
            style.setFixedWidth(w)
            style.clicked.connect(
                partial(self.showStyleMenu, name=line.name, qtimer=qtimer))
            style.setToolTip("线型")
            # style.setFixedSize(self._height, self._height)
            bar.addWidget(style)
            width = TransparentToolButton(FluentIcon.REMOVE)
            width.setFixedWidth(w)
            width.clicked.connect(
                partial(self.showWidthMenu, name=line.name, qtimer=qtimer))
            width.setToolTip("线型大小")
            # width.setFixedSize(self._height, self._height)
            bar.addWidget(width)
            params = TransparentToolButton(FluentIcon.SETTING)
            params.setFixedWidth(w)
            params.clicked.connect(
                partial(self.showParamsDialog, name=line.name, qtimer=qtimer))
            params.setToolTip("参数")
            bar.addWidget(params)
            code = TransparentToolButton(FluentIcon.CODE)
            code.setToolTip("代码")
            code.setFixedWidth(w)
            code.clicked.connect(
                partial(self.FuturesInterface.currentwidget._test, qtimer=qtimer, menu=self.menu))
            bar.addWidget(code)
            delind = TransparentToolButton(FluentIcon.DELETE)
            delind.setFixedWidth(w)
            delind.setToolTip("删除")
            delind.clicked.connect(
                partial(self.del_indicator, bar=bar, key=qtimer if main else qtimer.id))
            bar.addWidget(delind)
            hide = TransparentToolButton(FluentIcon.VIEW)
            hide.setFixedWidth(w)
            hide._isshow = True
            hide.clicked.connect(
                partial(self.showHideDialog, line, button=hide))
            hide.setToolTip("隐藏")
            # params.setFixedSize(self._height, self._height)
            bar.addWidget(hide)
            bars.append(bar)
            self._count += 1
        self.bars.append(bars)
        return bars

    def del_indicator(self, bar: QWidget, key):
        # item = self.vlayout.itemAt(self.vlayout.indexOf(bar))
        # self.vlayout.removeItem(item)
        # item.widget().deleteLater()
        for i, bars in enumerate(self.bars):
            if bar in bars:
                for b in bars:
                    self.vlayout.removeWidget(b)
                    b.deleteLater()
                    self._count -= 1
                break
        self.bars.pop(i)
        # self.setFixedHeight(self._count*(self._height+14))
        # self.menu.view.setFixedHeight(self.menu.height()-self._height-14)
        # self.menu.adjustSize()
        # self.menu.view.adjustSize()
        if not self._count:
            self.menu.removeAction(self)
        if isinstance(key, int):
            self.FuturesInterface.currentwidget.current_chart_widget.delete_subchart(
                key)
        else:
            self.FuturesInterface.currentwidget.current_chart_widget.deltet_main_indicator(
                key)

        # self.menu.update()

    def _initItems(self):
        qtimer_explorer: QtimerExplorer = self.FuturesInterface.currentwidget.current_chart_widget.qtimer_explorer

        # self.vlayout.addWidget(self.creat_indicator_bar(
        #     "K", qtimer_explorer.kline_qtimer))

        for _, qtimer in qtimer_explorer.main_ind_qtimer.items():
            for bar in self.creat_indicator_bar("M", qtimer):
                self.vlayout.addWidget(bar)

        for qtimer in qtimer_explorer.subchart_ind_qtimers:
            for bar in self.creat_indicator_bar("S", qtimer):
                self.vlayout.addWidget(bar)
        self.vlayout.setContentsMargins(0, 0, 0, 0)
        # self.vlayout.setSpacing(6)
        # self.adjustSize()
        self.setFixedHeight(self._count*(self._height+14))

    @property
    def light_chart_widget(self):
        return self.FuturesInterface.currentwidget.current_chart_widget

    def reload(self):
        if self.key_on:
            light_chart_widget = self.light_chart_widget
            qtimer_explorer = light_chart_widget.qtimer_explorer
            for _, v in qtimer_explorer.main_ind_qtimer.items():
                if v.setting:
                    light_chart_widget._lines_main_style(v)
                    # qtimer_explorer.chart._qtimers.update(
                    #     {f"{v.indname}_{v.id}": timer})
            for v in qtimer_explorer.subchart_ind_qtimers:
                if v.setting:
                    light_chart_widget._lines_sub_style(v)
                    # qtimer_explorer._charts.update({self.chart_num: subchart})
        # if self.default_params!=self.params:
        if hasattr(self, "paramscard"):
            self.paramscard.run()

    def showColorDialog(self, name, qtimer: QTimer, button):
        Menu = RoundMenu("style", parent=self.FuturesInterface)
        # w = ColorDialog(self.color, self.tr(
        #     'Choose ')+self.title, self.window(), self.enableAlpha)
        # w.colorChanged.connect(w.__onColorChanged)

        for i, color in enumerate(Color):
            if i % 30 == 0:
                menu = RoundMenu(f"color{int(i/30)}", Menu)
                # menu.triggered.connect(
                #     partial(self.color_connect, name=name, qtimer=qtimer))
                Menu.addMenu(menu)
            action = QWidgetAction(menu)
            w = PillPushButton(color)
            w.clicked.connect(partial(self.color_connect, menu=menu, button=button,
                              color=color, name=name, qtimer=qtimer))
            w.setStyleSheet(f"background-color:{color}")
            action.setDefaultWidget(w)
            menu.addAction(action)
        pos = QCursor.pos()
        pos.setX(pos.x()-10)
        pos.setY(pos.y()+20)
        Menu.exec(pos)
        return Menu

    def color_connect(self, color, name=None, qtimer: QTimer = None):
        color = color.name()
        if qtimer.lines[name].color != color:
            qtimer.setting = True
            self.key_on = True
            qtimer.lines[name].color = color
            # button.setStyleSheet(f"background-color:{color}")
            # menu._hideMenu(True)

    def showStyleMenu(self, name, qtimer: QTimer):
        Menu = RoundMenu("style", parent=self.FuturesInterface)
        Menu.addActions([Action(FluentIcon.ALIGNMENT, self.tr(
            style), checkable=True) for style in LINE_STYLE])
        for action in Menu.actions():
            action.setChecked(qtimer.lines[name].style == action.text())
        Menu.triggered.connect(
            partial(self.style_connect, name=name, qtimer=qtimer))
        pos = QCursor.pos()
        pos.setX(pos.x()-10)
        pos.setY(pos.y()+20)
        Menu.exec(pos)
        return Menu

    def style_connect(self, action: Action, name, qtimer: QTimer):
        if qtimer.lines[name].style != action.text():
            qtimer.setting = True
            self.key_on = True
            qtimer.lines[name].style = action.text()

    def showWidthMenu(self, name, qtimer: QTimer):
        Menu = RoundMenu("width", parent=self.FuturesInterface)
        Menu.addActions([Action(FluentIcon.REMOVE, str(i),
                        checkable=True) for i in range(1, 11)])
        for action in Menu.actions():
            action.setChecked(qtimer.lines[name].width == action.text())
        Menu.triggered.connect(
            partial(self.width_connect, name=name, qtimer=qtimer))
        pos = QCursor.pos()
        pos.setX(pos.x()-10)
        pos.setY(pos.y()+20)
        Menu.exec(pos)
        return Menu

    def width_connect(self, action: Action, name, qtimer: QTimer):
        if qtimer.lines[name].width != action.text():
            qtimer.setting = True
            self.key_on = True
            qtimer.lines[name].width = action.text()

    def showParamsDialog(self, name, qtimer: QTimer):
        menu = IndMenu(name, parent=self.FuturesInterface)
        self.paramscard = ParamsProfileCard(
            qtimer, self.FuturesInterface, menu)
        # self.default_params=deepcopy(self.paramscard.params)
        # menu.setfunc(self.paramscard.run)
        menu.addWidget(self.paramscard, selectable=False)
        pos = QCursor.pos()
        pos.setX(pos.x()-10)
        pos.setY(pos.y()+20)
        menu.exec(pos)

    def showHideDialog(self, line, button):
        button._isshow = not button._isshow
        line._toggle_data(button._isshow)
        button.setIcon(FIF.VIEW if button._isshow else FIF.HIDE)
        button.setToolTip("隐藏" if button._isshow else "显示")


class AppCard(CardWidget):
    """ App card """

    def __init__(self, icon, title, height, parent: Ind_Card = None):
        super().__init__(parent)
        self._height = height
        self.FuturesInterface = parent.FuturesInterface
        self.iconWidget = IconWidget(icon)
        self.titleLabel = BodyLabel(title, self)
        # self.contentLabel = CaptionLabel(content, self)
        # self.openButton = PushButton('打开', self)
        self.moreButton = ToolButton(FluentIcon.MORE, self)
        # self.moreButton = TransparentDropDownPushButton(
        #     "", self, FluentIcon.MORE)
        self.moreButton.clicked.connect(self.createCustomWidgetMenu)

        self.hBoxLayout = QHBoxLayout(self)
        self.vBoxLayout = QVBoxLayout()

        self.setFixedHeight(height)
        # self.setMaximumWidth(128)
        self.iconWidget.setFixedSize(height, height)
        # self.contentLabel.setTextColor("#606060", "#d2d2d2")
        # self.openButton.setFixedWidth(80)

        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout.setSpacing(2)
        self.hBoxLayout.addWidget(self.iconWidget)

        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.addWidget(self.titleLabel, 0, Qt.AlignVCenter)
        # self.vBoxLayout.addWidget(self.contentLabel, 0, Qt.AlignVCenter)
        self.vBoxLayout.setAlignment(Qt.AlignVCenter)
        self.hBoxLayout.addLayout(self.vBoxLayout)

        self.hBoxLayout.addStretch(1)
        # self.hBoxLayout.addWidget(self.openButton, 0, Qt.AlignRight)
        self.hBoxLayout.addWidget(self.moreButton, 0, Qt.AlignRight)

        self.moreButton.setFixedSize(height, height)
        # self.moreButton.clicked.connect(self.onMoreButtonClicked)

    def onMoreButtonClicked(self):
        menu = RoundMenu(parent=self)
        menu.addAction(Action(FluentIcon.SHARE, '共享', self))
        menu.addAction(Action(FluentIcon.CHAT, '写评论', self))
        menu.addAction(Action(FluentIcon.PIN, '固定到任务栏', self))

        x = (self.moreButton.width() - menu.width()) // 2 + 10
        pos = self.moreButton.mapToGlobal(QPoint(x, self.moreButton.height()))
        menu.exec(pos)

    def createCustomWidgetMenu(self):
        menu = IndMenu(parent=self.FuturesInterface)

        # add custom widget
        card = ProfileCard(':/gallery/images/logo.png',
                           self.tr('miniqt'), '407841129@qq.com', menu, self.FuturesInterface)
        menu.addWidget(card, selectable=False)
        if self.FuturesInterface.currentwidget.current_chart_widget.qtimer_explorer.ishasindictor:
            menu.addSeparator()
            indwidget = IndicatorItemWidget(
                self.FuturesInterface, menu, self._height)
            menu.setfunc(indwidget.reload)
            menu.addWidget(indwidget)
        else:
            menu.setfunc(lambda: ...)
        # menu.addActions([
        #     Action(FIF.PEOPLE, self.tr('Manage account profile')),
        #     Action(FIF.SHOPPING_CART, self.tr('Payment method')),
        #     Action(FIF.CODE, self.tr('Redemption code and gift card')),
        # ])
        menu.addSeparator()
        menu.addAction(Action(FIF.SETTING, self.tr('Settings')))
        # x = (self.moreButton.width() - menu.width()) + 10
        # pos = self.moreButton.mapToGlobal(QPoint(x, self.moreButton.height()))
        pos = QCursor.pos()
        pos.setX(pos.x()-60)
        pos.setY(pos.y()+self._height/2)
        menu.exec(pos)


class IndicatorInterface(CardWidget):
    """ App card """

    def __init__(self, icon=FIF.SCROLL, title="常用指标", parent: CommonIndicatorCard = None):
        super().__init__(parent)
        self._height = parent._height
        height = self._height
        self.setMaximumWidth(200)
        self.CommonIndicatorCard = parent
        # self.GalleryInterface = parent.indicator
        self.FuturesInterface: FuturesInterface = parent.FuturesInterface
        self.bottom_button = PillPushButton(
            icon, "筛选", self)  # IconWidget(icon)
        self.bottom_button.clicked.connect(self.open_bottom_widget)
        # self.bottom_button.setAlignment(Qt.AlignVCenter)
        # self.iconWidget.setFixedSize(20, 20)

        self.titleLabel = BodyLabel(self)
        self.titleLabel.setAlignment(Qt.AlignVCenter)
        self.titleLabel.setText(title)
        # self.contentLabel = CaptionLabel(content, self)
        # self.openButton = PushButton('打开', self)
        self.moreButton = ToolButton(FluentIcon.MORE, self)
        self.moreButton.setFixedHeight(30)
        # self.moreButton = TransparentDropDownPushButton(
        #     "", self, FluentIcon.MORE)
        self.moreButton.clicked.connect(self.createCustomWidgetMenu)
        self.hBoxLayout = QHBoxLayout(self)
        self.vBoxLayout = QVBoxLayout()

        self.setFixedHeight(height)
        # self.setMaximumWidth(128)
        # self.iconWidget.setFixedSize(height, height)
        # self.contentLabel.setTextColor("#606060", "#d2d2d2")
        # self.openButton.setFixedWidth(80)

        self.hBoxLayout.setContentsMargins(2, 2, 2, 2)
        self.hBoxLayout.setSpacing(2)
        self.hBoxLayout.addWidget(self.bottom_button)

        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.addWidget(self.titleLabel, 0, Qt.AlignLeft)
        # self.vBoxLayout.addWidget(self.contentLabel, 0, Qt.AlignVCenter)
        self.vBoxLayout.setAlignment(Qt.AlignLeft)
        self.hBoxLayout.addLayout(self.vBoxLayout)

        self.hBoxLayout.addStretch(1)
        # self.hBoxLayout.addWidget(self.openButton, 0, Qt.AlignRight)
        self.hBoxLayout.addWidget(self.moreButton, 0, Qt.AlignLeft)

        self.moreButton.setFixedSize(height, height)
        self.splitter_sizes = []
        # self.moreButton.clicked.connect(self.onMoreButtonClicked)

    def open_bottom_widget(self):
        splitter = self.FuturesInterface.currentwidget.mdi_bottom_splitter
        if splitter.sizes()[1] > 0:
            splitter.setSizes([1, 0])
            self.bottom_button.setChecked(False)
        else:
            self.bottom_button.setChecked(True)
            if splitter.mdi_bottom_splitter_sizes[1] > 0:
                splitter.setSizes(splitter.mdi_bottom_splitter_sizes)
                return
            splitter.setSizes([4, 1])

    def onMoreButtonClicked(self):
        menu = RoundMenu(parent=self)
        menu.addAction(Action(FluentIcon.SHARE, '共享', self))
        menu.addAction(Action(FluentIcon.CHAT, '写评论', self))
        menu.addAction(Action(FluentIcon.PIN, '固定到任务栏', self))

        x = (self.moreButton.width() - menu.width()) // 2 + 10
        pos = self.moreButton.mapToGlobal(QPoint(x, self.moreButton.height()))
        menu.exec(pos)

    def createCustomWidgetMenu(self):
        menu = IndMenu(parent=self.FuturesInterface)
        self.tree = IndicatorTreeWidget(
            self.FuturesInterface, self.CommonIndicatorCard)
        menu.setfunc(self.tree.reload_indicators)
        menu.addWidget(self.tree)
        # ...
        # self.w = TreeFrame(self, True)
        # self.w.show()
        # menu = IndMenu(parent=self.FuturesInterface)

        # # add custom widget
        # card = ProfileCard(':/gallery/images/logo.png',
        #                    self.tr('miniqt'), '407841129@qq.com', menu, self.FuturesInterface)
        # menu.addWidget(card, selectable=False)
        # if self.FuturesInterface.currentwidget.current_chart_widget.qtimer_explorer.ishasindictor:
        #     menu.addSeparator()
        #     indwidget = IndicatorItemWidget(
        #         self.FuturesInterface, self._height)
        #     menu.setfunc(indwidget.reload)
        #     menu.addWidget(indwidget)
        # else:
        #     menu.setfunc(lambda: ...)
        # # menu.addActions([
        # #     Action(FIF.PEOPLE, self.tr('Manage account profile')),
        # #     Action(FIF.SHOPPING_CART, self.tr('Payment method')),
        # #     Action(FIF.CODE, self.tr('Redemption code and gift card')),
        # # ])
        # menu.addSeparator()
        # menu.addAction(Action(FIF.SETTING, self.tr('Settings')))
        # # x = (self.moreButton.width() - menu.width()) + 10
        # # pos = self.moreButton.mapToGlobal(QPoint(x, self.moreButton.height()))
        pos = QCursor.pos()
        pos.setX(max(pos.x()-160, 10))
        pos.setY(max(pos.y()-735, 100))
        menu.exec(pos)


class CommonIndicatorCard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._height = 40
        self.setFixedHeight(self._height)
        self.LightChartWidget = parent
        self.FuturesInterface: FuturesInterface = parent.FuturesInterface

        # self.setMinimumWidth(400)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 3)
        layout.setAlignment(Qt.AlignLeft)
        self.interface = IndicatorInterface(parent=self)
        self.indicator = GalleryInterface(self)
        layout.addWidget(self.interface)  # , alignment=Qt.AlignLeft)
        layout.addWidget(self.indicator)  # , alignment=Qt.AlignLeft)

        # StyleSheet.GALLERY_INTERFACE.apply(self)

    def reload_indicators(self):
        self.indicator.reload_indicators()
        # card = widget if widget else AppCard(icon, title, self._height, self)

        # self.hlayout.addWidget(AppCard(icon, title, self._height, self), alignment=Qt.AlignLeft)
    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        c = 255 if isDarkTheme() else 0
        pen = QPen(QColor(c, c, c, 15))
        pen.setCosmetic(True)
        painter.setPen(pen)
        # painter.setPen(QColor(60, 60, 60, 15) if isDarkTheme() else QColor(
        #     215, 215, 215, 15))  # , QColor(60, 60, 60))  # Qt.grey)
        # painter.drawRect(1, 1, self.width(), 0.5)
        painter.drawRect(1, 1, self.width()-2, self.height()-2)
        # painter.drawLine(0, self.height()-2, self.width(), self.height()-2)


class Ind_Card(QWidget):
    """ Gallery interface """

    def __init__(self, parent=None, FuturesInterface: FuturesInterface = None):
        """
        Parameters
        ----------
        title: str
            The title of gallery

        subtitle: str
            The subtitle of gallery

        parent: QWidget
            parent widget
        """
        super().__init__(parent=parent)
        self.LightChartWidget = parent
        self.FuturesInterface = FuturesInterface
        self._height = 20
        self.setMinimumWidth(420)
        # self.setFixedHeight(self._height)
        # self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowMinimizeButtonHint |
        #                     Qt.WindowSystemMenuHint | Qt.WindowMaximizeButtonHint)
        # self.setAttribute(Qt.WA_TranslucentBackground)
        # self._layout = QVBoxLayout(self)
        # self._layout.setContentsMargins(0, 0, 0, 0)
        # FlowLayout(self)  # , animation)(self)
        self.vBoxLayout = QHBoxLayout(self)
        # self.indlistlayout = QHBoxLayout()
        # self.vBoxLayout.setSpacing(1)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        # self.vBoxLayout.setVerticalSpacing(2)
        # self.vBoxLayout.setHorizontalSpacing(2)
        self.vBoxLayout.setAlignment(Qt.AlignLeft)
        # self.indlayout = QVBoxLayout()
        # self.indlayout.setContentsMargins(0, 0, 0, 0)

        # suffix = ":/qfluentwidgets/images/controls"
        # self.addCard(f":/qfluentwidgets/images/logo.png",
        #              "PyQt-Fluent-Widgets", 'Shokokawaii Inc.')
        # self.addCard(f"{suffix}/TitleBar.png",
        #              "PyQt-Frameless-Window", 'Shokokawaii Inc.')
        # self.addCard(f"{suffix}/RatingControl.png",
        #              "反馈中心", 'Microsoft Corporation')
        # self.addCard(f"{suffix}/Checkbox.png",
        #              "Microsoft 使用技巧", 'Microsoft Corporation')
        # self.addCard(f"{suffix}/Pivot.png", "MSN 天气", 'Microsoft Corporation')
        # self.addCard(f"{suffix}/MediaPlayerElement.png",
        #              "电影和电视", 'Microsoft Corporation')
        # self.addCard(f"{suffix}/PersonPicture.png",
        #              "照片", 'Microsoft Corporation')

        self.addCard(FIF.MARKET,
                     "指标")
        # self._layout.addLayout(self.vBoxLayout)
        # self._layout.addLayout(self.indlayout)
        # self.setMinimumHeight(height)
        # self.adjustSize()
        # self.createWidget()
        # self.indlistlayout.addWidget(self.createWidget())
        # self.vBoxLayout.addLayout(self.indlistlayout)
        # self.vBoxLayout.addStretch(100)
        # for i in range(10):
        #     self.addCard(Icons.angle_up(), f'test{i}')

        # self.addCard(Icons.line_chart_line(),
        #              "PyQt-Frameless-Window", 'Shokokawaii Inc.')
        # self.addCard(Icons.line_chart_line(),
        #              "反馈中心", 'Microsoft Corporation')
        # self.addCard(Icons.line_chart_line(),
        #              "Microsoft 使用技巧", 'Microsoft Corporation')
        # self.addCard(Icons.line_chart_line(),
        #              "MSN 天气", 'Microsoft Corporation')
        # self.addCard(Icons.line_chart_line(),
        #              "电影和电视", 'Microsoft Corporation')
        # self.addCard(Icons.line_chart_line(),
        #              "照片", 'Microsoft Corporation')
        self.draggable = False
        self.offset = None

    def addCard(self, icon=None, title=None, widget=None):
        card = widget if widget else AppCard(icon, title, self._height, self)

        self.vBoxLayout.addWidget(card, alignment=Qt.AlignLeft)
        # return card.height()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.draggable = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.draggable:
            # event.
            self.move(event.globalPos() +
                      self.LightChartWidget._pos - self.offset)  #

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.draggable = False

    def createWidget(self, animation=False):
        texts = [
            self.tr('Star Platinum'), self.tr('Hierophant Green'),
            self.tr('Silver Chariot'), self.tr('Crazy diamond'),
            self.tr("Heaven's Door"), self.tr('Killer Queen'),
            self.tr("Gold Experience"), self.tr('Sticky Fingers'),
            self.tr("Sex Pistols"), self.tr('Dirty Deeds Done Dirt Cheap'),
            self.tr('Star Platinum'), self.tr('Hierophant Green'),
            self.tr('Silver Chariot'), self.tr('Crazy diamond'),
            self.tr("Heaven's Door"), self.tr('Killer Queen'),
            self.tr("Gold Experience"), self.tr('Sticky Fingers'),
            self.tr("Sex Pistols"), self.tr('Dirty Deeds Done Dirt Cheap'),
        ]

        # widget = ScrollArea()
        # layout = FlowLayout(widget, animation)

        # layout.setContentsMargins(0, 0, 0, 0)
        # layout.setVerticalSpacing(2)
        # layout.setHorizontalSpacing(2)

        for text in texts:
            self.vBoxLayout.addWidget(PushButton(text))
        # return widget
    # def enableTransparentBackground(self):
    #     self.setStyleSheet("QScrollArea{border: none; background: transparent}")

    #     # if self.widget():
    #     #     self.widget().setStyleSheet("QWidget{background: transparent}")


class GalleryInterface(ScrollArea):
    """ Gallery interface """

    def __init__(self, parent: CommonIndicatorCard = None):
        """
        Parameters
        ----------
        title: str
            The title of gallery

        subtitle: str
            The subtitle of gallery

        parent: QWidget
            parent widget
        """
        super().__init__(parent=parent)
        self.FuturesInterface: FuturesInterface = parent.FuturesInterface
        self.IndicatorInterface = parent.interface
        self._height = 35  # parent._height
        self.setFixedHeight(self._height)
        self.view = QWidget(self)
        self.view.setFixedHeight(self._height)
        # self.toolBar = ToolBar(title, subtitle, self)
        self.vBoxLayout = QHBoxLayout(self.view)

        # self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # self.setViewportMargins(0, self.toolBar.height(), 0, 0)
        self.setWidget(self.view)
        self.setWidgetResizable(True)
        self.addExampleCard(self.FuturesInterface._default_indicators)
        # self.vBoxLayout.setSpacing(30)
        self.vBoxLayout.setAlignment(Qt.AlignLeft)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)

        self.view.setObjectName('view')
        StyleSheet.GALLERY_INTERFACE.apply(self)

    # title, widget, sourcePath: str, stretch=0):

    def addExampleCard(self, indicators: list[str]):
        # card = ExampleCard(title, widget, sourcePath, stretch, self.view)
        if indicators:
            for name in indicators:
                cls, ind = name.split(".")
                button = PushButton(ind)
                button.setToolTip(cls)
                button.clicked.connect(
                    partial(self.FuturesInterface.add_indicator, indcls=cls, indname=ind))
                self.vBoxLayout.addWidget(button, 0, Qt.AlignLeft)
        # self.vBoxLayout.addWidget(card, 0, Qt.AlignLeft)

    def reload_indicators(self):
        for i in list(range(self.vBoxLayout.count()))[::-1]:
            item = self.vBoxLayout.itemAt(i)
            self.vBoxLayout.removeItem(item)
            item.widget().deleteLater()
        # for button in self.vBoxLayout.findChildren(PushButton):
        #     self.vBoxLayout.removeWidget(button)
        #     button.deleteLater()
        self.addExampleCard(self.FuturesInterface._default_indicators)

    def scrollToCard(self, index: int):
        """ scroll to example card """
        w = self.vBoxLayout.itemAt(index).widget()
        self.verticalScrollBar().setValue(w.y())

    def resizeEvent(self, e):
        super().resizeEvent(e)
        # self.toolBar.resize(self.width(), self.toolBar.height())

    def keyPressEvent(self, e):
        if e.key() in [Qt.Key_Left, Qt.Key_Right]:
            return

        return super().keyPressEvent(e)

    def wheelEvent(self, e: QWheelEvent):
        if e.angleDelta().x() != 0:
            return

        self.scrollDelagate.horizonSmoothScroll.wheelEvent(e)
        e.setAccepted(True)


class IndMenu(RoundMenu):
    def __init__(self, title="", parent=None):
        super().__init__(title=title, parent=parent)
        self.func = lambda: ...
        self._test_on = True

    def setfunc(self, func):
        self.func = func

    def mousePressEvent(self, e):
        if self._test_on:
            w = self.childAt(e.pos())
            if (w is not self.view) and (not self.view.isAncestorOf(w)):
                self._hideMenu(True)
                self.func()


class ParamsCard(CardWidget):
    """ App card """

    def __init__(self, key, value, parent: ParamsProfileCard = None):
        super().__init__(parent=None)
        self.ParamsProfileCard = parent
        self.key = key
        self.default_value = value
        self.setWindowFlags(Qt.WindowMaximizeButtonHint |
                            Qt.MSWindowsFixedSizeDialogHint | Qt.WindowStaysOnTopHint)
        # self.iconWidget = IconWidget(icon)
        self.titleLabel = BodyLabel(key, self)
        self.titleLabel.setFixedWidth(100)
        # self.contentLabel = CaptionLabel(content, self)
        self.edit = LineEdit(self)  # PushButton('打开', self)
        self.edit.setText(str(value))
        self.edit.setAlignment(Qt.AlignCenter)
        self.edit.textChanged.connect(parent.textchang)
        # self.moreButton = TransparentToolButton(FluentIcon.MORE, self)

        self.hBoxLayout = QHBoxLayout(self)
        self.vBoxLayout = QVBoxLayout()

        self.setFixedHeight(self.edit.height()+8)
        # self.iconWidget.setFixedSize(48, 48)
        # self.contentLabel.setTextColor("#606060", "#d2d2d2")
        self.edit.setMinimumWidth(80)

        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        # self.hBoxLayout.setSpacing(15)
        self.hBoxLayout.addWidget(self.titleLabel)

        # self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        # self.vBoxLayout.setSpacing(0)
        # self.vBoxLayout.addWidget(self.titleLabel, 0, Qt.AlignVCenter)
        # self.vBoxLayout.addWidget(self.contentLabel, 0, Qt.AlignVCenter)
        # self.vBoxLayout.setAlignment(Qt.AlignVCenter)
        # self.hBoxLayout.addLayout(self.vBoxLayout)

        self.hBoxLayout.addStretch(1)
        self.hBoxLayout.addWidget(self.edit, 0, Qt.AlignRight)
        # self.hBoxLayout.addWidget(self.moreButton, 0, Qt.AlignRight)

        # self.moreButton.setFixedSize(32, 32)
        # self.moreButton.clicked.connect(self.onMoreButtonClicked)
    # def textchang(self):
    #     """获取更新的参数"""
    #     value = self.edit.text().strip()
    #     if not value:
    #         return
    #     for v in ["none", "true", "false"]:
    #         if value.lower() == v:
    #             value = v.capitalize()
    #     try:
    #         exec(f"params = {value}", locals())
    #     except:
    #         return value
    #     self.ParamsProfileCard.params[self.key]= locals()["params"]


class ParamsProfileCard(QWidget):
    """ Profile card """

    def __init__(self, object, FuturesInterface: FuturesInterface = None, menu=None, height=20):
        super().__init__(parent=FuturesInterface)
        self.menu = menu
        self._object = object
        self.ContractDataSet = FuturesInterface.currentwidget.current_chart_widget.ContractDataSet
        self.is_qtimer = hasattr(object, "indwindow_params")
        # if self.is_qtimer:
        #     indname = object.indname
        #     doc = object.doc
        # else:
        #     indname = object.candles_style
        #     doc = object.candles_func.__doc__
        self.params = object.indwindow_params if self.is_qtimer else self.ContractDataSet.candles_params
        self.is_changed = False
        self._height = height
        self.vlayout = QVBoxLayout(self)
        self.vlayout.setSpacing(2)
        self.edits: list[LineEdit] = []
        for k, v in self.params.items():
            card = ParamsCard(k, v, self)
            self.edits.append(card.edit)
            self.vlayout.addWidget(card)
        self.vlayout.setContentsMargins(0, 0, 0, 0)
        self.adjustSize()

    def keyPressEvent(self, even) -> None:
        """按下确定键关闭窗口"""
        if even.key() == Qt.Key_Enter:
            # self.run()
            self.menu._hideMenu(True)
        return super().keyPressEvent(even)

    def __get_params(self,  value: str, default):
        """获取更新的参数"""
        value = value.strip()
        if not value:
            return default
        for v in ["none", "true", "false"]:
            if value.lower() == v:
                value = v.capitalize()
        try:
            exec(f"params = {value}", locals())
        except:
            return value
        return locals()["params"]

    def run(self):
        """关闭窗口更换参数"""
        if self.is_changed:
            new_params = dict()
            params = self._object.indwindow_params if self.is_qtimer else self.ContractDataSet.candles_params
            for (k, v), new in zip(params.items(), [edit.text() for edit in self.edits]):
                new_params.update({k: self.__get_params(new, v)})
            if new_params:
                try:
                    if self.is_qtimer:
                        if "follow" in new_params:
                            self._object.follow = new_params.pop("follow")
                        self._object.replace_params(new_params)
                        self.ContractDataSet.params_lenght = self._object.max_params_lenght
                    else:
                        self._object.change_candles_params(new_params)
                except:
                    ...

    def textchang(self):
        self.is_changed = True


class TreeWidgetItem(QTreeWidgetItem):
    def __init__(self, strings: list[str], indclass: str = "") -> None:
        super().__init__(strings)
        self._indclass = indclass

    @property
    def indname(self) -> str:
        return self.text(0)

    @property
    def indclass(self) -> str:
        return self._indclass

    @property
    def indclass_indname(self) -> str:
        if self._indclass:
            return f"{self._indclass}.{self.text(0)}"
        return ""


class IndicatorTreeWidget(TreeWidget):
    """ Tree widget """

    def __init__(self, parent: FuturesInterface = None, CommonIndicatorCard: CommonIndicatorCard = None, height=720):
        super().__init__(parent=parent)
        self.setFixedSize(360, height)
        self.FuturesInterface = parent
        self.CommonIndicatorCard = CommonIndicatorCard
        self.item_keys = list(Indicator_Dict.keys())
        self.item_values = list(Indicator_Dict.values())
        self._default_indicators: set = parent._default_indicators
        self._init_indicators = list(self._default_indicators)
        # self._default_indclass: set = set()
        self._indclassitems: list[TreeWidgetItem] = []
        self._indclassitemsstate = []
        self._inditems: list[list[TreeWidgetItem]] = []
        self._inditemsstate: list[list] = []
        for i, (k, v) in enumerate(Indicator_Dict.items()):
            item = TreeWidgetItem([k,])
            inditems = [TreeWidgetItem([value,], k) for value in v]
            self._inditems.append(inditems)
            item.addChildren(self._inditems[-1])
            self.addTopLevelItem(item)
            if not i:
                item.setExpanded(True)
                item.setSelected(True)
                self.last_select_item = item
                # self.last_select_item_check = Qt.Unchecked
            self._indclassitems.append(item)
            self._indclassitemsstate.append(Qt.Unchecked)
        self.setHeaderHidden(True)
        self.setFixedSize(340, height-20)
        # self.clicked.connect(self._onclicked)
        # self.itemChanged.connect(
        #     lambda item, column: print(item.text(0), column))
        self.setEnableCheck()
        for items in self._inditems:
            check = []
            for item in items:
                check.append(item.checkState(0))
            self._inditemsstate.append(check)

        # print(self.invisibleRootItem())
        self.itemClicked.connect(self._onclicked)

    @property
    def default_indicators(self) -> set:
        return self._default_indicators

    @default_indicators.setter
    def default_indicators(self, value: set):
        if not isinstance(value, set):
            return
        self._default_indicators = value

    def state_reversed(self, state):
        return Qt.Unchecked if state == Qt.Checked else Qt.Checked

    def get_item_index(self, item) -> tuple[int]:
        for i, items in enumerate(self._inditems):
            if item in items:
                j = items.index(item)
                break
        return i, j

    def _onclicked(self, item: TreeWidgetItem, column: int):
        if not item:
            return
        state = item.checkState(0)
        name = item.indclass_indname
        # 点击相同item
        if self.last_select_item is item:
            # 如果是类指标item
            if item.indname in self.item_keys:
                self.setIndicatorClassCheck(item)
            # 如果是指标item
            else:
                # 找到item所在位置
                i, j = self.get_item_index(item)
                # 如果点击前后state状态一致（点击非复选框位置），将切换状态
                if self._inditemsstate[i][j] == state:
                    item.setCheckState(0, self.state_reversed(state))
                # 如果点击item中的复选框，则保持点击后的状态
                # 记录当前指标item中的state状态，并修改默认指标
                state = item.checkState(0)
                self._inditemsstate[i][j] = state
                if state == Qt.Checked:
                    self._default_indicators.add(name)
                else:
                    if name in self._default_indicators:
                        self._default_indicators.remove(name)
            return

        # 点击不相同item
        # 上一次选择的item改变选择状态
        self.last_select_item.setSelected(False)
        # 如果当前item没被选中，则选中
        if not item.isSelected():
            item.setSelected(True)
        # state = item.checkState(0)
        # 记录最后一次点击的item
        self.last_select_item = item
        # 如果是指标item
        if item.indname not in self.item_keys:
            # 找到item所在位置
            i, j = self.get_item_index(item)
            # 如果点击前后state状态一致（点击非复选框位置），将切换状态
            if self._inditemsstate[i][j] == state:
                item.setCheckState(0, self.state_reversed(state))
            # 如果点击item中的复选框，则保持点击后的状态
            # 记录当前指标item中的state状态，并修改默认指标
            state = item.checkState(0)
            self._inditemsstate[i][j] = state
            if state == Qt.Checked:
                self._default_indicators.add(name)
            else:
                if name in self._default_indicators:
                    self._default_indicators.remove(name)
            return
        # 如果是类指标item
        self.setIndicatorClassCheck(item)

    def setIndicatorClassCheck(self, item: TreeWidgetItem):
        state = item.checkState(0)
        index = self._indclassitems.index(item)
        # 直接点击类指标item复选框，则当前状态发生变化时，点击非复选框位置则保持不变
        if self._indclassitemsstate[index] != state:
            # name = item.text(0)
            it = QTreeWidgetItemIterator(self)
            # 在同一类中选定所有指标
            indclass = item.indname
            indlist = [f"{indclass}.{ind}" for ind in Indicator_Dict[indclass]]
            # 记录默认指标
            if state == Qt.Checked:
                self._default_indicators = self._default_indicators.union(
                    set(indlist))
                # self._default_indclass.add(name)
            else:
                self._default_indicators = self._default_indicators.difference(
                    set(indlist))
                # self._default_indclass.remove(name)
            while (it.value()):
                _item = it.value()
                if _item.indclass_indname in indlist:
                    _item.setCheckState(0, state)
                it += 1
            self._indclassitemsstate[index] = state
            self._inditemsstate[index] = [state for _ in self._inditems[index]]

    def setEnableCheck(self):
        it = QTreeWidgetItemIterator(self)
        while (it.value()):
            # it.value().setCheckState(0, int(it.value().text(0) in self._default_indicators))
            if it.value().indclass_indname in self._default_indicators:
                it.value().setCheckState(0, Qt.Checked)
            else:
                it.value().setCheckState(0, Qt.Unchecked)
            it += 1

    def reload_indicators(self):
        if set(self._init_indicators) != self._default_indicators:
            self.FuturesInterface._default_indicators = self._default_indicators
            self.CommonIndicatorCard.reload_indicators()
