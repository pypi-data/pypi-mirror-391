# coding: utf-8
from __future__ import annotations
from typing import TYPE_CHECKING
import sys
# from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QUrl, QSize, QPoint, Qt
from PyQt5.QtGui import QIcon, QDesktopServices, QColor, QCursor
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QAction

from qfluentwidgets import (NavigationAvatarWidget, NavigationItemPosition, MessageBox, FluentWindow, MSFluentTitleBar, RoundMenu, Action, PushButton,
                            SplashScreen, isDarkTheme, TransparentToolButton, TabBar, TransparentDropDownToolButton, qrouter)
from qfluentwidgets import FluentIcon as FIF

from .gallery_interface import GalleryInterface
from .home_interface import HomeInterface
from .basic_input_interface import BasicInputInterface
# from ...indicators.indicators_interface import IndicatorsInterface, _IndicatorsInterface
from .date_time_interface import DateTimeInterface
from .dialog_interface import DialogInterface
from .layout_interface import LayoutInterface
from .icon_interface import IconInterface
from .material_interface import MaterialInterface
from .menu_interface import MenuInterface
from .navigation_view_interface import NavigationViewInterface
from .scroll_interface import ScrollInterface
from .status_info_interface import StatusInfoInterface
from .setting_interface import SettingInterface
from .text_interface import TextInterface
from .view_interface import ViewInterface
from ..common.config import ZH_SUPPORT_URL, EN_SUPPORT_URL, cfg
from ..common.icon import Icon
from ..common.signal_bus import signalBus
from ..common.translator import Translator
from ..common import resource
from ...utils import Icons, MiniqtDataBase  # , Api, UpdateThread

#
from ...futures.futures_interface import FuturesInterface, Callable
from ...futures.chart_widget import ChartWidget
from ...indicators.home import IndicatorsInterface
from ...indicators.new_view import _DateTimeInterface
from ...indicators._new_view import _HomeInterface_
from ...indicators.test import MonacoWidget_
# from ...chart.chart import QMdiArea_WeightCharts
from functools import partial
from qfluentwidgets.common.config import qconfig, Theme

Icons.setColor(isDarkTheme())
if TYPE_CHECKING:
    from pytdx.hq import TdxHq_API
    from ..login.tq_api import TqApi


class CustomTitleBar(MSFluentTitleBar):
    """ Title bar with icon and title """

    def __init__(self, parent: MainWindow, width: int):
        super().__init__(parent)
        self.main_window = parent
        self.qobject: dict[str, QWidget] = dict()
        self.tabCount = 1
        self.setFixedHeight(width)
        self.iconLabel.setFixedSize(24, 24)
        # self.setMouseTracking(True)

        # add buttons
        self.toolButtonLayout = QHBoxLayout()
        color = QColor(206, 206, 206) if isDarkTheme() else QColor(96, 96, 96)
        # self.searchButton = TransparentToolButton(
        #     FIF.SEARCH_MIRROR.icon(color=color), self)
        self.searchButton = PushButton(self.tr('菜单'))
        self.searchButton.clicked.connect(lambda: self.createMenu())
        self.forwardButton = TransparentToolButton(
            FIF.RIGHT_ARROW.icon(color=color), self)
        self.backButton = TransparentToolButton(
            FIF.LEFT_ARROW.icon(color=color), self)

        self.forwardButton.setDisabled(True)
        self.toolButtonLayout.setContentsMargins(20, 0, 20, 0)
        self.toolButtonLayout.setSpacing(15)
        self.toolButtonLayout.addWidget(self.searchButton)
        self.toolButtonLayout.addWidget(self.backButton)
        self.toolButtonLayout.addWidget(self.forwardButton)
        self.hBoxLayout.insertLayout(4, self.toolButtonLayout)

        # add tab bar
        self.tabBar = TabBar(self)
        self.tabBar.itemLayout.setContentsMargins(0, 0, 0, 0)
        # self.tabBar.itemLayout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.tabBar.setFixedHeight(width-2)
        self.tabBar.setTabMaximumWidth(220)

        self.tabBar.setMovable(True)
        self.tabBar.setScrollable(True)
        self.tabBar.setTabShadowEnabled(True)
        self.tabBar.setTabSelectedBackgroundColor(
            QColor(255, 255, 255, 125), QColor(255, 255, 255, 50))
        # self.tabBar.setScrollable(True)
        # self.tabBar.setCloseButtonDisplayMode(TabCloseButtonDisplayMode.ON_HOVER)

        self.tabBar.tabCloseRequested.connect(self.tabBar.removeTab)
        self.tabBar.currentChanged.connect(
            lambda i: print(self.tabBar.tabText(i)))

        self.hBoxLayout.insertWidget(5, self.tabBar, 1)
        self.hBoxLayout.setStretch(6, 0)

        # add avatar
        self.avatar = TransparentDropDownToolButton(
            FIF.CONSTRACT, self)
        self.avatar.setIconSize(QSize(20, 20))
        self.avatar.setFixedHeight(width-2)
        self.hBoxLayout.insertWidget(7, self.avatar, 0, Qt.AlignRight)
        self.hBoxLayout.insertSpacing(8, 0)  # 20)

        self.connectSignalToSlot()
        # self.maxBtn.clicked.disconnect(self.__toggleMaxState)
        # self.maxBtn.clicked.connect(self._toggleMaxState)

        # qrouter.setDefaultRouteKey(
        #     self.stackedWidget, self.songInterface.objectName())
    def setIcon(self, icon):
        self.iconLabel.setPixmap(QIcon(icon).pixmap(24, 24))

    def canDrag(self, pos: QPoint):
        if not super().canDrag(pos):
            return False

        pos.setX(pos.x() - self.tabBar.x())
        return not self.tabBar.tabRegion().contains(pos)

    def addSubInterface(self, widget: QWidget, objectName, text, icon):
        widget.setObjectName(objectName)
        # widget.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.main_window.stackedWidget.addWidget(widget)
        self.tabBar.addTab(
            routeKey=objectName,
            text=text,
            icon=icon,
            onClick=lambda: self.main_window.stackedWidget.setCurrentWidget(
                widget)
        )

    def addTab(self, widget: QWidget):
        # text = f'硝子酱一级棒卡哇伊×{self.tabCount}'
        # self.addSubInterface(QLabel('🥰 ' + text), text,
        #                      text, ':/gallery/images/Smiling_with_heart.png')
        # self.charts.append(ChartWidget(self))

        # self.addSubInterface(
        #     # qta.icon('ri.truck-fill', color='cyan'))
        #     self.charts[-1], 'test', 'test', Icons.stock_fill())
        # self.tabCount += 1
        # self.parent_widget.stackedWidget.setCurrentWidget(self.charts[-1])
        # for item in self.tabBar.items:
        #     item.borderRadius = 0
        #     item.setFixedHeight(30)
        # _DateTimeInterface(self))
        # self.charts.append(MonacoWidget_(self.parent_widget))
        # self.parent_widget.conset = self.parent_widget.tq_api.contract_set(
        #     "SHFE.ni2412", 60)
        # self.charts.append(_HomeInterface_(self.parent_widget))
        # from ...chart.test import DemoWin
        # self.charts.append(QMdiArea_WeightCharts(self))
        name = widget.objectName()
        self.qobject.update({name: widget})
        self.addSubInterface(
            # qta.icon('ri.truck-fill', color='cyan'))
            widget, name, name, Icons.stock_fill())
        self.tabCount += 1
        self.main_window.stackedWidget.setCurrentWidget(widget)
        ...

    def connectSignalToSlot(self):
        # self.movableCheckBox.stateChanged.connect(
        #     lambda: self.tabBar.setMovable(self.movableCheckBox.isChecked()))
        # self.scrollableCheckBox.stateChanged.connect(
        #     lambda: self.tabBar.setScrollable(self.scrollableCheckBox.isChecked()))
        # self.shadowEnabledCheckBox.stateChanged.connect(
        #     lambda: self.tabBar.setTabShadowEnabled(self.shadowEnabledCheckBox.isChecked()))

        # self.tabMaxWidthSpinBox.valueChanged.connect(
        #     self.tabBar.setTabMaximumWidth)

        # self.tabBar.tabAddRequested.connect(self.addTab)
        self.tabBar.tabCloseRequested.connect(self.removeTab)

        self.main_window.stackedWidget.currentChanged.connect(
            self.onCurrentIndexChanged)

    def onDisplayModeChanged(self, index):
        mode = self.closeDisplayModeComboBox.itemData(index)
        self.tabBar.setCloseButtonDisplayMode(mode)

    def onCurrentIndexChanged(self, index):
        widget = self.main_window.stackedWidget.widget(index)
        if not widget:
            return

        self.tabBar.setCurrentTab(widget.objectName())
        qrouter.push(self.main_window.stackedWidget, widget.objectName())

    def removeTab(self, index):
        item = self.tabBar.tabItem(index)
        # widget=self.qobject.get(item.routeKey())
        # widget = self.findChild(ChartWidget, item.routeKey())
        # if widget:
        # self.charts.pop(self.charts.index(widget))
        widget = self.qobject.pop(item.routeKey())
        if widget:
            self.main_window.stackedWidget.removeWidget(widget)
            self.tabBar.removeTab(index)
            widget.deleteLater()

    def get_allChartWidgets(self) -> ChartWidget:
        widgets = []
        for item in self.tabBar.items:
            widget = self.findChild(ChartWidget, item.routeKey())
            if widget:
                widgets.append(widget)
        return widgets

    def setChartsStyle(self, dark=True):
        widgets: ChartWidget = self.get_allChartWidgets()
        if widgets:
            for widget in widgets:
                widget.setChartStyle(dark)

    def login(self, is_stock):
        from ..login.LoginWindow import LoginWindow
        w = LoginWindow(self, is_stock)
        w.show()

    def createMenu(self):
        menu = RoundMenu(parent=self)

        # add actions
        logaction = Action(FIF.COPY, self.tr('期货登录'))
        logaction.triggered.connect(partial(self.login, is_stock=False))
        menu.addAction(logaction)
        cut = Action(FIF.CUT, self.tr('股票登录'))
        cut.triggered.connect(partial(self.login, is_stock=True))
        menu.addAction(cut)
        menu.addSeparator()

        # add sub menu
        submenu = RoundMenu(self.tr("Add to"), self)

        submenu.setIcon(FIF.ADD)
        submenu.addActions([
            Action(FIF.VIDEO, self.tr('Video')),
            Action(FIF.MUSIC, self.tr('Music')),
        ])
        menu.addMenu(submenu)

        # add actions
        menu.addActions([
            Action(FIF.PASTE, self.tr('Paste')),
            Action(FIF.CANCEL, self.tr('Undo'))
        ])

        # add separator
        menu.addSeparator()
        menu.addAction(QAction(self.tr('Select all')))

        # insert actions
        menu.insertAction(
            menu.actions()[-1], Action(FIF.SETTING, self.tr('Settings')))
        menu.insertActions(
            menu.actions()[-1],
            [
                Action(FIF.HELP, self.tr('Help')),
                Action(FIF.FEEDBACK, self.tr('Feedback'))
            ]
        )
        # x = self.searchButton.width() - menu.width()
        pos = QCursor.pos()  # self.searchButton.pos()  # QPoint(x, self.searchButton.height())
        # pos.setX(pos.x()+45)
        # pos.setY(pos.y()+self.height()-5)
        self.searchButton.mapToGlobal(pos)
        menu.exec(pos, ani=True)


class MainWindow(FluentWindow):
    tq_api: TqApi | None = None
    pytdx_api: TdxHq_API | None = None

    def __init__(self):
        super().__init__()
        # from tqsdk import TqApi, TqAuth, TqKq
        # from ..login.tq_api import TqApi as tqapi
        # api = TqApi(
        #     TqKq(), auth=TqAuth("owenlovehellen", "owen2553832"))
        # self.tq_api = tqapi(api)
        # self.tq_update = UpdateThread(self, partial(
        #     self.tq_api.api.wait_update, deadline=60))
        # self.tq_update.finished.connect(self.init_datas)
        # self.tq_update.start()
        self.title_height = 36
        self.setTitleBar(CustomTitleBar(self, self.title_height))
        self.titleBar: CustomTitleBar
        self.tabBar = self.titleBar.tabBar
        self.initWindow()

        # create sub interface
        self.homeInterface = HomeInterface(self)
        self.futuresinterface = FuturesInterface(self)
        self.indicatorsinterface = IndicatorsInterface(self)
        self.dateTimeInterface = DateTimeInterface(self)
        self.dialogInterface = DialogInterface(self)
        self.layoutInterface = LayoutInterface(self)
        self.menuInterface = MenuInterface(self)
        self.materialInterface = MaterialInterface(self)
        self.navigationViewInterface = NavigationViewInterface(self)
        self.scrollInterface = ScrollInterface(self)
        self.statusInfoInterface = StatusInfoInterface(self)
        self.settingInterface = SettingInterface(self)
        self.textInterface = TextInterface(self)
        self.viewInterface = ViewInterface(self)

        # enable acrylic effect
        self.navigationInterface.setAcrylicEnabled(True)

        self.connectSignalToSlot()

        # add items to navigation interface
        self.initNavigation()
        self.splashScreen.finish()
        # self.setFixedHeight(35)
        self.widgetLayout.setContentsMargins(0, self.title_height, 0, 0)
        # self.futuresinterface._init_chart_()

        # self.showMaximized()
        # self.setMouseTracking(True)

    def connectSignalToSlot(self):
        signalBus.micaEnableChanged.connect(self.setMicaEffectEnabled)
        signalBus.switchToSampleCard.connect(self.switchToSample)
        signalBus.supportSignal.connect(self.onSupport)

    def initNavigation(self):
        # add navigation items
        t = Translator()
        self.addSubInterface(self.homeInterface, FIF.HOME, self.tr('Home'))
        self.addSubInterface(self.futuresinterface,
                             Icon.EMOJI_TAB_SYMBOLS, t.icons)
        self.navigationInterface.addSeparator()

        pos = NavigationItemPosition.SCROLL
        self.addSubInterface(self.indicatorsinterface,
                             FIF.CHECKBOX, t.basicInput, pos)
        self.addSubInterface(self.dateTimeInterface,
                             FIF.DATE_TIME, t.dateTime, pos)
        self.addSubInterface(self.dialogInterface, FIF.MESSAGE, t.dialogs, pos)
        self.addSubInterface(self.layoutInterface, FIF.LAYOUT, t.layout, pos)
        self.addSubInterface(self.materialInterface,
                             FIF.PALETTE, t.material, pos)
        self.addSubInterface(self.menuInterface, Icon.MENU, t.menus, pos)
        self.addSubInterface(self.navigationViewInterface,
                             FIF.MENU, t.navigation, pos)
        self.addSubInterface(self.scrollInterface, FIF.SCROLL, t.scroll, pos)
        self.addSubInterface(self.statusInfoInterface,
                             FIF.CHAT, t.statusInfo, pos)
        self.addSubInterface(self.textInterface, Icon.TEXT, t.text, pos)
        self.addSubInterface(self.viewInterface, Icon.GRID, t.view, pos)

        # add custom widget to bottom
        self.navigationInterface.addItem(
            routeKey='price',
            icon=Icon.PRICE,
            text=t.price,
            onClick=self.onSupport,
            selectable=False,
            tooltip=t.price,
            position=NavigationItemPosition.BOTTOM
        )
        self.addSubInterface(
            self.settingInterface, FIF.SETTING, self.tr('Settings'), NavigationItemPosition.BOTTOM)
        # self.stackedWidget.setCurrentIndex(1)
        self.stackedWidget.setCurrentIndex(0)
        self.navigationInterface.setCurrentItem(
            self.stackedWidget.widget(0).objectName())
        self.stackedWidget.currentChanged.connect(
            self.stackedWidget_currentChanged)

    def stackedWidget_currentChanged(self):
        currentwidget = self.stackedWidget.currentWidget()
        if hasattr(currentwidget, "connect_api") and hasattr(currentwidget, "_isredy") and not currentwidget._isredy:
            if not self.tq_api:
                self.titleBar.login(False)
            else:
                currentwidget.connect_api()

    def initWindow(self):
        self.resize(1200, 780)
        self.setMinimumWidth(760)
        self.setWindowIcon(QIcon(':/gallery/images/logo.png'))
        self.setWindowTitle('MiniQt')

        self.setMicaEffectEnabled(cfg.get(cfg.micaEnabled))

        # create splash screen
        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(106, 106))
        self.splashScreen.raise_()

        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)
        self.show()
        QApplication.processEvents()

    def onSupport(self):
        language = cfg.get(cfg.language).value
        if language.name() == "zh_CN":
            QDesktopServices.openUrl(QUrl(ZH_SUPPORT_URL))
        else:
            QDesktopServices.openUrl(QUrl(EN_SUPPORT_URL))

    def addTab(self, widget: QWidget | Callable):
        if isinstance(widget, Callable):
            widget = widget()
        self.titleBar.addTab(widget)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if hasattr(self, 'splashScreen'):
            self.splashScreen.resize(self.size())

        # widgets = []
        # for item in self.tabBar.items:
        #     widget = self.findChild(
        #         _HomeInterface_, item.routeKey())
        #     if widget:
        #         widgets.append(widget)
        # if widgets:
        #     for widget in widgets:
        #         widget.resize_()

    def switchToSample(self, routeKey, index):
        """ switch to sample """
        interfaces = self.findChildren(GalleryInterface)
        for w in interfaces:
            if w.objectName() == routeKey:
                self.stackedWidget.setCurrentWidget(w, False)
                w.scrollToCard(index)

    def closeEvent(self, e):
        MiniqtDataBase.set_value("default_indicators",
                                 self.futuresinterface._default_indicators)
        if self.pytdx_api:
            self.pytdx_api.close()
        if self.tq_api:
            self.futuresinterface.timer_stop()
            self.tq_api.close()

        # with MiniqtDataBase as base:
        #     for table in base.tables:
        #         base.table(table)

        return super().closeEvent(e)

    def return_history(self):
        self.navigationInterface.panel.history.pop()

    def keyPressEvent(self, e) -> None:
        if e.key() == Qt.Key_Escape:
            self.navigationInterface.panel.history.pop()
        return super().keyPressEvent(e)
