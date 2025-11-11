from PyQt5 import QtGui
import pandas as pd
from lightweight_charts.widgets import QtChart
from minibt import FILED, np, dataframe
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QWidget, QStackedWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame, QSizePolicy, QMainWindow, QActionGroup, QSplitter, QBoxLayout
from PyQt5.QtCore import QThread, pyqtSignal, QTimer, Qt, QSize
from qfluentwidgets.common.config import qconfig, Theme
from qfluentwidgets import (Pivot, qrouter, SegmentedWidget, TabBar, CheckBox, ComboBox, CommandBar, setFont, MenuIndicatorType, CheckableMenu,
                            TabCloseButtonDisplayMode, BodyLabel, SpinBox, BreadcrumbBar, Action, TransparentDropDownPushButton, TransparentToolButton,
                            SegmentedToggleToolWidget, FluentIcon, TableWidget, TransparentPushButton, RoundMenu)
from qfluentwidgets import FluentIcon as FIF
import win32gui
from .ind_interface import Ind_Card
from ..app.common.style_sheet import StyleSheet
from ..utils import Icons
from ..chart.chart import LightWeightCharts, ChartMdiAreaWidget
# from ..monaco.monaco_widget import MonacoEditor
from ..futures.Editor import MonacoEditor


def on_new_bar(chart):
    print('New bar event!')


def on_timeframe_selection(chart):
    print(f'Selected timeframe of {chart.topbar["timeframe"].value}')


def on_horizontal_line_move(chart, line):
    print(f'Horizontal line moved to: {line.price}')


class ChartSplitWidget(QWidget):
    def __init__(self, parent=None, ContractSet=None) -> None:
        super().__init__(parent)
        self.parent_widget = parent
        self.ContractSet = ContractSet
        self.setObjectName('ChartWidget')
        qvlayout = QVBoxLayout(self)
        self.splitter = QSplitter(Qt.Vertical)

        self.splitter.setHandleWidth(1)
        self._chart = ChartWidget(self)
        self.stackedWidget = QStackedWidget(self)
        self._init_widget()
        self.splitter.addWidget(self._chart)
        self.splitter.addWidget(self.stackedWidget)
        self.splitter.setFixedHeight(0)
        qvlayout.addWidget(self.splitter)
        qvlayout.setContentsMargins(0, 0, 0, 0)
        self.set_state()
        self.splitter.setSizes([1, 0])

    def _init_widget(self):
        self.songInterface = MonacoEditor(self)
        self.albumInterface = QLabel('Album Interface', self)
        self.artistInterface = QLabel('Artist Interface', self)

        # add items to pivot
        self.addSubInterface(self.songInterface,
                             'songInterface', self.tr('Song'))
        self.addSubInterface(self.albumInterface,
                             'albumInterface', self.tr('Album'))
        self.addSubInterface(self.artistInterface,
                             'artistInterface', self.tr('Artist'))

        self.stackedWidget.currentChanged.connect(self.onCurrentIndexChanged)
        self.stackedWidget.setCurrentWidget(self.songInterface)
        # self._chart.pivot.setCurrentItem(self.songInterface.objectName())
        for _, item in self._chart.pivot.items.items():
            item.clicked.connect(self.on_button)
        self._button_index = 0
        self._stackedWidget_index = 0
        qrouter.setDefaultRouteKey(
            self.stackedWidget, self.songInterface.objectName())
        self.splittererStyle(qconfig.theme == Theme.DARK)

    def set_state(self):
        self.splitter_sizes = self.splitter.saveState()

    def splittererStyle(self, dark=True):
        if dark:
            self.splitter.setStyleSheet(
                "QSplitter::handle {background-color: gray}")
        else:
            self.splitter.setStyleSheet(
                "QSplitter::handle {background-color: lightgray}")

    def addSubInterface(self, widget: QWidget, objectName, text):
        widget.setObjectName(objectName)
        # widget.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.stackedWidget.addWidget(widget)
        self._chart.pivot.addItem(
            routeKey=objectName,
            text=text,
            onClick=lambda: self.stackedWidget.setCurrentWidget(widget)
        )

    def on_button(self):
        if self._button_index == self._stackedWidget_index:
            if all(self.splitter.sizes()):
                self.set_state()
                self.splitter.setSizes([1, 0])
            else:
                self.splitter.restoreState(
                    self.splitter_sizes)
        self._button_index = self._stackedWidget_index

    def onCurrentIndexChanged(self, index):
        self._stackedWidget_index = index
        if not all(self.splitter.sizes()):
            self.splitter.restoreState(
                self.splitter_sizes)
        widget = self.stackedWidget.widget(index)
        self._chart.pivot.setCurrentItem(widget.objectName())
        qrouter.push(self.stackedWidget, widget.objectName())

    def setChartStyle(self, dark=True):
        self._chart.chart.setChartStyle(dark)


class ChartWidget(QWidget):
    def __init__(self, parent=None, ContractSet=None) -> None:
        super().__init__(parent)
        self.parent_widget = parent
        self.ContractSet = ContractSet
        self.adjustSize()
        qvlayout = QVBoxLayout(self)
        self.setObjectName('_ChartWidget')
        self.chart = ChartMdiAreaWidget(parent)
        self.ind_card = Ind_Card(self)
        self.ind_card.setObjectName('ind_card')
        self.tool_bar = self.createCommandBar()
        self.pivot = SegmentedWidget(self)  # Pivot(self)
        self.pivot.setFixedHeight(30)

        qvlayout.addWidget(self.tool_bar)
        # qvlayout.addWidget(self.ind_card)
        qvlayout.addSpacing(1)
        qvlayout.addWidget(self.chart)
        qvlayout.addWidget(self.pivot, 0, Qt.AlignLeft)
        qvlayout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        qvlayout.setContentsMargins(0, 0, 0, 0)
        StyleSheet.NAVIGATION_VIEW_INTERFACE.apply(self)
        # self.chart.QtChartQWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        # self.chart.QtChartQWidget.customContextMenuRequested.connect(
        #     self.create_chart_menu)

    # def create_chart_menu(self, event):
    #     ikunMenu = RoundMenu(parent=self)
    #     ikunMenus: list[RoundMenu] = []
    #     for i in range(4):
    #         ikunMenus.append(RoundMenu(f'{i}', parent=self))

    #         ikunMenus[-1].addActions([
    #             Action(self.tr('Sing')),
    #             Action(self.tr('Jump')),
    #             Action(self.tr("Rap")),
    #         ])
    #         ikunMenus[-1].addSeparator()
    #         ikunMenus[-1].addAction(Action(self.tr('Music')))
    #         ikunMenu.addMenu(ikunMenus[-1])
    #     ikunMenu.exec_(QCursor.pos())

    # def checkWindow(self):
    #     # 查找
    #     hwnd = win32gui.FindWindow('test', None)
    #     if not hwnd:
    #         return
    #     # 获取位置
    #     rect = win32gui.GetWindowRect(hwnd)
    #     self.ind_card.move(rect[2], rect[1])

    def createCommandBar(self):
        # create actions
        self.createTimeAction = Action(
            FIF.CALENDAR, self.tr('Create Date'), checkable=True)
        self.shootTimeAction = Action(
            FIF.CAMERA, self.tr('Shooting Date'), checkable=True)
        self.modifiedTimeAction = Action(
            FIF.EDIT, self.tr('Modified time'), checkable=True)
        self.nameAction = Action(FIF.FONT, self.tr('Name'), checkable=True)
        self.actionGroup1 = QActionGroup(self)
        self.actionGroup1.addAction(self.createTimeAction)
        self.actionGroup1.addAction(self.shootTimeAction)
        self.actionGroup1.addAction(self.modifiedTimeAction)
        self.actionGroup1.addAction(self.nameAction)

        self.ascendAction = Action(
            FIF.UP, self.tr('Ascending'), checkable=True)
        self.descendAction = Action(
            FIF.DOWN, self.tr('Descending'), checkable=True)
        self.actionGroup2 = QActionGroup(self)
        self.actionGroup2.addAction(self.ascendAction)
        self.actionGroup2.addAction(self.descendAction)

        self.shootTimeAction.setChecked(True)
        self.ascendAction.setChecked(True)

        bar = CommandBar(self)
        bar.setFixedHeight(30)
        bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        bar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        bar._insertWidgetToLayout(-1, self.ind_card)
        bar.addActions([
            Action(FIF.ADD, self.tr('Add')),
            Action(FIF.ROTATE, self.tr('Rotate')),
            Action(FIF.ZOOM_IN, self.tr('Zoom in')),
            Action(FIF.ZOOM_OUT, self.tr('Zoom out')),
        ])
        bar.addSeparator()
        bar.addActions([
            Action(FIF.EDIT, self.tr('Edit'), checkable=True),
            Action(FIF.INFO, self.tr('Info')),
            Action(FIF.DELETE, self.tr('Delete')),
            Action(FIF.SHARE, self.tr('Share'))
        ])

        # add custom widget
        button = TransparentDropDownPushButton(
            self.tr('Sort'), self, FIF.SCROLL)
        button.setMenu(self.createCheckableMenu())
        button.setFixedHeight(30)
        setFont(button, 12)
        bar.addWidget(button)

        bar.addHiddenActions([
            Action(FIF.SETTING, self.tr('Settings'), shortcut='Ctrl+I'),
        ])
        return bar

    def createCheckableMenu(self, pos=None):
        menu = CheckableMenu(
            parent=self, indicatorType=MenuIndicatorType.RADIO)

        menu.addActions([
            self.createTimeAction, self.shootTimeAction,
            self.modifiedTimeAction, self.nameAction
        ])
        menu.addSeparator()
        menu.addActions([self.ascendAction, self.descendAction])

        if pos is not None:
            menu.exec(pos, ani=True)

        return menu
