
from __future__ import annotations
from PyQt5 import QtCore
import pynput
from qfluentwidgets.components.widgets.stacked_widget import PopUpAniStackedWidget
from qfluentwidgets.components.dialog_box import MessageBoxBase
from PyQt5.QtCore import Qt, pyqtSignal, QEasingCurve, QSize, QTimer, QCollator, QPoint
from PyQt5.QtGui import QBrush, QColor, QFont, QCursor, QPalette, QKeyEvent, QWheelEvent, QPainter, QIcon, QPen
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QPushButton, QMenu, QSplitter, QWidget, QStackedWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame, QSizePolicy, QActionGroup, QAbstractItemView, QTableWidgetItem, QHeaderView, QMdiSubWindow,  QMdiArea
from qfluentwidgets import (InfoBar, InfoBarPosition, Flyout, CommandBarView, Pivot, qrouter, SegmentedWidget, TabBar, CheckBox, ComboBox, CommandBar, setFont, MenuIndicatorType, CheckableMenu, RoundMenu, FluentTitleBar, SingleDirectionScrollArea,
                            TabCloseButtonDisplayMode, BodyLabel, SpinBox, BreadcrumbBar, Action, TransparentDropDownPushButton, TransparentToolButton, isDarkTheme, CardWidget, setCustomStyleSheet,
                            SegmentedToggleToolWidget, FluentIcon, TableWidget, LineEdit, FluentWindow, SubtitleLabel, TextEdit, PushButton, FluentBackgroundTheme, PillPushButton)
from qfluentwidgets import FluentIcon as FIF
from qframelesswindow import FramelessWindow, StandardTitleBar
from PyQt5.QtWebEngineWidgets import QWebEngineView
# from ..common.translator import Translator
from ..app.common.style_sheet import StyleSheet
# from minibt.miniqt.utils import Icons, Indicator_Dict
# from .chart_interface import ChartSplitWidget
# from minibt.miniqt.monaco import MonacoEditor
from .Editor import MonacoEditor
from lightweight_charts.widgets import QtChart
from lightweight_charts.abstract import Line, Candlestick, AbstractChart
from .ind_interface import Ind_Card, CommonIndicatorCard
from minibt import FILED, pd, deepcopy
from qfluentwidgets.common.config import qconfig, Theme
from qfluentwidgets.common.style_sheet import FluentStyleSheet
# from .chart_widget import ChartSplitWidget
from ..utils import (connec_thread, Constant, QtColors, WorkerThread, partial, Union, Callable, Any, Optional, MiniqtDataBase, Icons, Indicator_Dict,
                     reduce, Cycles, inspect, get_func_parameters, IndicatorClass, not_indicator_list, get_colors)
from typing_extensions import Literal
# from ..chart.chart import ChartMdiAreaWidget
from ..app.login.tq_api import ContractDataSet
from .KeyElfWindow import KeyElfWindow_
from .sidebar_info_interface import SidebarInfoInterface
from .utils import MyCommandBar, myqwidget
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..app.view.main_window import MainWindow


def get_line_info(self: Line) -> dict:
    return dict(name=self.name, color=self.color, style=self.style, width=int(self.width))


def set_line_info(self: Line, name="", color="", style="", width=""):
    self.name = name
    self.color = color
    self.style = style
    self.width = str(width)


Line.get_line_info: Callable = get_line_info
Line.set_line_info: Callable = set_line_info


def paintEvent(self, event):
    super().paintEvent(event)
    painter = QPainter(self)
    painter.setPen(QColor(60, 60, 60, 15) if isDarkTheme() else QColor(
        215, 215, 215, 15))  # , QColor(60, 60, 60))  # Qt.grey)
    painter.drawRect(0, 0, self.width(), 0.5)
    painter.drawRect(0, self.height()-3, self.width(), 0.5)
    # self.height())


class FuturesInterface(QWidget):
    """ Tab interface
    parent:main_window
    subqwidget:
        charts: list[ChartMdiAreaWidget]
        stackedWidget : QStackedWidget
        market_page : MarketPage"""

    def __init__(self, parent: MainWindow = None):
        super().__init__(parent=parent)
        self.setObjectName("FuturesInterface")
        self.main_window = parent
        # self.tq_api = parent.tq_api
        self._default_indicators = set(
            MiniqtDataBase.get_value("default_indicators"))
        self.quote_timer: Optional[QTimer] = None
        self.tabCount = 1
        self.tabBar = TabBar(self)
        self.tabBar.itemLayout.setContentsMargins(0, 0, 0, 0)
        # self.tabBar.addButton.setIcon(FIF.MORE)
        self.tabBar.addButton.clicked.disconnect()
        self.tabBar.addButton.clicked.connect(self.create_kline_menu)
        self.tabBar.setMovable(True)
        self.tabBar.setScrollable(True)
        self.tabBar.setTabShadowEnabled(True)
        self.stackedWidget = QStackedWidget(self)
        self.stackedWidget.adjustSize()
        self.vBoxLayout = QVBoxLayout(self)
        self.__initWidget()
        self._isredy = False
        # self.tabBar.setFixedHeight(36)

    @property
    def tq_api(self):
        return self.main_window.tq_api

    @property
    def pytdx_api(self):
        return self.main_window.pytdx_api

    def connect_api(self):
        if self.tq_api:
            futurestable: list[FuturesTable] = self.market_page.findChildren(
                FuturesTable)
            # self.threads: list[connec_thread] = []
            for table in futurestable:
                table._thread = connec_thread(table)
                table._thread.finished.connect(table.init_datas)
                table._thread.start()
                # self.threads.append(connec_thread(func=table.initWindow))
                # self.threads[-1].finished.connect(table.init_datas)
                # self.threads[-1].start()
            self._isredy = True

    def __initWidget(self):
        self.tabBar.setFixedHeight(30)
        self.tabBar.setTabMaximumWidth(200)
        self.vBoxLayout.addWidget(self.tabBar)
        self.vBoxLayout.addWidget(self.stackedWidget)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        # self.vBoxLayout.setAlignment(Qt.AlignTop)
        self.market_page = MarketPage(self)
        self.addSubInterface(self.market_page,
                             self.market_page.objectName(), self.tr('期货行情'), FIF.HOME_FILL)  # ':/gallery/images/MusicNote.png')
        self.stackedWidget.setCurrentIndex(0)
        StyleSheet.NAVIGATION_VIEW_INTERFACE.apply(self)
        self.connectSignalToSlot()
        qrouter.setDefaultRouteKey(
            self.stackedWidget, self.market_page.objectName())
        self.create_quote_timer()

    def connectSignalToSlot(self):
        self.tabBar.tabAddRequested.connect(self.addTab)
        self.tabBar.tabCloseRequested.connect(self.removeTab)
        self.stackedWidget.currentChanged.connect(self.onCurrentIndexChanged)

    @property
    def quote_table_widget(self):
        """返回行情窗口"""
        self.stackedWidget.currentWidget(self.stackedWidget.currentIndex)
        return self.stackedWidget.widget(0)

    def create_quote_timer(self, time=0):
        """创建行情QTimer"""
        if self.quote_timer is None:
            self.quote_timer = QTimer(self)
            self.quote_timer.timeout.connect(self.quote_loop)
            # self.quote_timer.start(time)

    @property
    def currentwidget(self) -> Union[MarketPage, ChartMdiAreaWidget]:
        """返回堆叠窗口当前窗口"""
        return self.stackedWidget.currentWidget()

    def add_indicator(self, indcls: str, indname: str):
        indcls = getattr(IndicatorClass, indcls)
        self.currentwidget.current_chart_widget._add_indicator(indcls, indname)

    def quote_loop(self):
        """行情更新函数"""
        if self.tq_api and self.tq_api.wait_update:
            widget = self.currentwidget
            if isinstance(widget, MarketPage):
                quote_widget = widget.currentwidget
                quote_widget.update_datas()
            else:
                # not widget.quote_table_widget.isHidden():
                # if widget.iscurrentwidget:
                if widget.mdi_info_splitter.sizes()[1] > 0:
                    if not widget.quote_table_widget.isHidden():
                        widget.quote_table_widget.currentwidget.update_datas()
                    if not widget.quote_widget.isHidden():
                        widget.quote_widget.update_quote_table()

    def addSubInterface(self, widget: QWidget, objectName, text, icon):
        """添加堆叠窗口"""
        widget.setObjectName(objectName)
        self.stackedWidget.addWidget(widget)
        self.tabBar.addTab(
            routeKey=objectName,
            text=text,
            icon=icon,
            onClick=lambda: self.stackedWidget.setCurrentWidget(widget)
        )

    # def onDisplayModeChanged(self, index):
    #     mode = self.closeDisplayModeComboBox.itemData(index)
    #     self.tabBar.setCloseButtonDisplayMode(mode)

    def onCurrentIndexChanged(self, index):
        """当前堆叠窗口索引发生变化时"""
        widget: Union[MarketPage,
                      ChartMdiAreaWidget] = self.stackedWidget.widget(index)
        if not widget:
            return

        # for mdi in self.get_allChartMdiAreaWidgets():
        #     mdi.iscurrentwidget = mdi is widget
        self.tabBar.setCurrentTab(widget.objectName())
        qrouter.push(self.stackedWidget, widget.objectName())

    def addTab(self, symbol: str = "", cycle: int = 60):
        """堆叠窗口增加子窗口"""
        if not symbol:
            widget: FuturesTable = self.market_page.stackedWidget.currentWidget()
            symbol = widget.item(widget.currentRow(), 1).text()
        if not self.trun_to_kline(symbol, cycle):
            contract = self.main_window.tq_api.contract_set(symbol, cycle)
            if isinstance(contract, str):
                InfoBar.success(
                    title=self.tr('TqTimeoutError'),
                    content=self.tr(contract),
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=2000,
                    parent=self
                )
            else:
                chart = ChartMdiAreaWidget(
                    self, contract)
                self.addSubInterface(
                    chart, f"{symbol}-{cycle}", f"{symbol}-{Cycles.cyclestring.get(cycle)}", Icons.stock_fill())
                self.tabCount += 1
                self.stackedWidget.setCurrentWidget(chart)

    def removeTab(self, index):
        """移除堆叠子窗口"""
        item = self.tabBar.tabItem(index)
        widget: ChartMdiAreaWidget = self.findChild(
            ChartMdiAreaWidget, item.routeKey())
        if widget:
            self.stackedWidget.removeWidget(widget)
            self.tabBar.removeTab(index)
            self.tabCount -= 1
            widget.deleteLater()

    def setTabName(self, name: str):
        self.tabBar.currentTab().setText(name)

    def get_allChartMdiAreaWidgets(self) -> list[ChartMdiAreaWidget]:
        """返回所有ChartMdiAreaWidget"""
        widgets = []
        for item in self.tabBar.items:
            widget = self.findChild(ChartMdiAreaWidget, item.routeKey())
            if widget:
                widgets.append(widget)
        return widgets

    def setChartsStyle(self, dark=True):
        """设置样式"""
        widgets = self.get_allChartMdiAreaWidgets()
        if widgets:
            for widget in widgets:
                widget.setChartStyle(dark)
        for i in range(self.market_page.stackedWidget.count()):
            self.market_page.stackedWidget.widget(i)._set_items_colors(dark)

        # for item in self.tabBar.itemLayout.children():
        #     item.setIcon(getattr(self.icons,item.objectName())())

    def timer_stop(self):
        """停止窗口下所有QTimer"""
        if self.quote_timer:
            self.quote_timer.stop()
        for widget in self.get_allChartMdiAreaWidgets():
            for lightchartwidget in widget.all_LightChartWidget():
                lightchartwidget.qtimer_explorer.stop_qtimer()

    def trun_to_kline(self, symbol: str, cycle: int = 0):
        """转到K线图"""
        for widget in self.get_allChartMdiAreaWidgets():
            connec = []
            connec.append(symbol in widget.symbols)
            connec.append(cycle > 0 and cycle in widget.cycles)
            if all(connec):
                self.stackedWidget.setCurrentWidget(widget)
                return True

    def create_kline_menu(self, event):
        """创建K线图菜单"""
        ikunMenu = RoundMenu(parent=self)
        ikunMenus: list[RoundMenu] = []
        for i in range(4):
            ikunMenus.append(RoundMenu(f'{i}', parent=self))

            ikunMenus[-1].addActions([
                Action(self.tr('Sing')),
                Action(self.tr('Jump')),
                Action(self.tr("Rap")),
            ])
            ikunMenus[-1].addSeparator()
            ikunMenus[-1].addAction(Action(self.tr('Music')))

            ikunMenu.addMenu(ikunMenus[-1])
        # ikunMenu.addSeparator()
        # if self.count < 9:
        #     logaction = Action("增加图表")
        #     logaction.triggered.connect(self.add_chart)
        #     ikunMenu.addAction(logaction)
        # if self.count > 1:
        #     logaction1 = Action(
        #         '恢复' if self.is_showMaximized else "最大化")
        #     logaction1.triggered.connect(self.showfull_chart)
        #     ikunMenu.addAction(logaction1)
        #     logaction2 = Action("关闭图表")
        #     logaction2.triggered.connect(self.close_chart)
        #     ikunMenu.addAction(logaction2)
        ikunMenu.exec_(QCursor.pos())


class SortItem(QTableWidgetItem):
    def __lt__(self, other: QTableWidgetItem) -> bool:
        try:
            return float(self.text()) < float(other.text())
        except:
            collator = QCollator()
            collator.setNumericMode(True)
            res = collator.compare(self.text(), other.text())
            return res < 0


class FuturesTable(TableWidget):

    def __init__(self, parent: FuturesInterface = None, name: str = "", mini=False, contractdataset: ContractDataSet = None):
        super().__init__(parent)
        self.FuturesInterface = parent
        self.main_window = parent.main_window
        self.mini = mini
        self.contractdataset = contractdataset
        self.isquote = isinstance(contractdataset, ContractDataSet)
        self.__ready = False
        self.setObjectName(name)
        font = self.horizontalHeader().font()  # 表格格式
        font.setBold(True)
        self.horizontalHeader().setFont(font)  # 表头加粗
        if self.mini or self.isquote:
            self.setFont(QFont('Times', 11))  # 设置字体
            self.verticalHeader().setVisible(False)
        else:
            self.adjustSize()
            self.verticalHeader().setVisible(True)
        self.setSelectionBehavior(
            QAbstractItemView.SelectRows)  # 设置不可选择单个单元格，只可选择一行。
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 禁止编辑
        # 序号进行隐藏table.verticalHeader().setVisible(False)#序号进行隐藏
        # self.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)  # 铺满整个QTableWidget控件

        # self.verticalHeader().setVisible(not self.isquote)  # 3False)
        self.setSortingEnabled(True)  # 设置表头不可排序

        self.setBorderVisible(True)
        self._default_color = QtColors.gold.value if qconfig.theme == Theme.DARK else QtColors.black.value
        self._items_index: list[int] = []
        self._flat_color = QtColors.white.value if qconfig.theme == Theme.DARK else QtColors.black.value
        if not (self.mini or self.isquote):
            self.setContextMenuPolicy(Qt.CustomContextMenu)
            self.customContextMenuRequested.connect(
                self.create_table_menu)
        self.cellDoubleClicked.connect(self.on_click_item)
        if self.isquote:
            # self.setBorderRadius(1)
            c = 255 if isDarkTheme() else 0
            qss = f"QTableView{{border-radius: {1}px}};{{border: 1px solid rgba({c},{c},{c},15)}};"
            setCustomStyleSheet(self, qss, qss)
            # self.setStyleSheet(
            #     f"QTableWidget{'{'}border: 1px solid rgba({c},{c},{c},15);{'}'}")
            # pen = QPen(QColor(c, c, c, 15), 1, Qt.SolidLine).style()
            # self.setGridStyle(pen)
        else:
            self.setBorderRadius(8)
            self.verticalScrollBar().valueChanged.connect(self.vertical_row_range)
        if self.main_window.tq_api:
            self._thread = connec_thread(self)
            self._thread.finished.connect(self.init_datas)
            self._thread.start()

    def initWindow(self) -> list:
        if self.mini:
            self.HeaderLabels = self.main_window.tq_api.mini_quote_table_name
            self.update_datas_index = self.main_window.tq_api.mini_quote_table_update_file_index
        elif self.isquote:
            self.HeaderLabels = ["字段", "值", "字段", "值"]
            self.update_datas_index = [1, 3]
            self.quote_left_dict_update_file = self.main_window.tq_api.quote_left_dict_update_file
            self.quote_right_dict_update_file = self.main_window.tq_api.quote_right_dict_update_file
            self.quote_left_dict = self.main_window.tq_api.quote_left_dict
            self.quote_right_dict = self.main_window.tq_api.quote_right_dict
        else:
            self.HeaderLabels = self.main_window.tq_api.quote_table_name
            self.update_datas_index = self.main_window.tq_api.quote_table_update_file_index

        self.columns_num = len(self.HeaderLabels)
        if self.isquote:
            self.datas_func = self.quote
            self.datas_update_func = self.update_quote_table
        else:
            self.datas_func: Callable = partial(
                self.main_window.tq_api.get_quote_datas, name=self.objectName(), mini=self.mini)
            self.datas_update_func: Callable = partial(
                self.main_window.tq_api.update_quote_datas, name=self.objectName(), mini=self.mini)

        # self.resizeColumnsToContents()
        # self._thread = WorkerThread(func=self.datas_func)
        # self._thread.finished.connect(self.init_datas)
        # self._thread.start()

        # self.init_datas(datas)

        return self.datas_func()

    def quote(self):
        quote = self.contractdataset.quote
        datas = []
        for (k, v), (_k, _v) in zip(self.quote_left_dict.items(), self.quote_right_dict.items()):
            datas.append([v, str(getattr(quote, k, "")),
                         _v, str(getattr(quote, _k, ""))])
        return datas

    def update_quote(self) -> tuple[list[str]]:
        quote = self.contractdataset.quote
        datas1, datas2 = [], []
        for k in self.quote_left_dict_update_file:
            datas1.append(str(getattr(quote, k, "")))
        for k in self.quote_right_dict_update_file:
            datas2.append(str(getattr(quote, k, "")))
        return datas1, datas2

    def reset_quote(self, dataset):
        self.contractdataset = dataset
        self.set_datas(self.quote())

    def _table_add_chart(self, symbol: str, cycle: int):
        self.FuturesInterface.addTab(symbol, cycle)

    def _mini_table_chart(self, symbol: str, cycle: int):
        ...

    def keypress(self, row=None, home=False, end=False) -> int:
        if home:
            row = 0
        if end:
            row = self.rowCount()-1
        if row is not None:
            cont = self.currentRow()
            row = (cont+row) % cont
        self.selectRow(row)

    def keyPressEvent(self, e: QKeyEvent) -> None:
        if e.key() == Qt.Key_PageUp:  # 上一只合约
            self.keypress(-1)
        elif e.key() == Qt.Key_PageDown:  # 下一只合约
            self.keypress(1)
        elif e.key() == Qt.Key_Home:  # 首只合约
            self.keypress(home=True)
        elif e.key() == Qt.Key_End:  # 最后一个合约
            self.keypress(end=True)
        return super().keyPressEvent(e)

    def create_table_menu(self, event):
        """行情窗口右键菜单"""
        row = self.rowAt(event.y())
        self.selectRow(row)
        Menu = RoundMenu(parent=self)
        cycle_dict = Cycles.__dict__
        indMenu = RoundMenu("周期", parent=self)
        Menu.addMenu(indMenu)
        for k, _ in cycle_dict.items():
            if not k.startswith("_"):
                indMenu.addAction(Action(self.tr(k)))
        indMenu.triggered.connect(lambda x: partial(
            self._table_add_chart, symbol=self.item(row, 1).text(), cycle=cycle_dict.get(x.text()))())

        Menu.exec_(QCursor.pos())

    def on_click_item(self, row, column):
        """双击事件"""
        item = self.item(row, self.symbol_code_col)
        symbol = item.text()
        if self.mini:
            widget = self.FuturesInterface.currentwidget
            for light_chart in widget.all_LightChartWidget():
                contract = self.FuturesInterface.main_window.tq_api.contract_set(
                    symbol, light_chart.cycle)
                if isinstance(contract, str):
                    InfoBar.success(
                        title=self.tr('TqTimeoutError'),
                        content=self.tr(contract),
                        orient=Qt.Horizontal,
                        isClosable=True,
                        position=InfoBarPosition.TOP,
                        duration=2000,
                        parent=self
                    )
                else:
                    light_chart.replace_symbol(contract)
                    self.FuturesInterface.currentwidget.quote_widget.reset_quote(
                        contract)

        else:
            if not self.FuturesInterface.trun_to_kline(symbol, 60):
                self.FuturesInterface.addTab(symbol)

    def vertical_row_range(self):
        """计算表格可见范围内的行序号"""
        pos = self.verticalScrollBar().sliderPosition()
        row = self.height()/self.column_height
        p = pos/self.column_height
        self.vertical_row = [round(p), round(row+p-1)]

    def init_datas(self, datas):
        """初始化表格"""
        self.setColumnCount(self.columns_num)
        if self.isquote or self.mini:
            self.horizontalHeader().setVisible(False)
        else:
            self.setHorizontalHeaderLabels(self.HeaderLabels)
        self.setRowCount(len(datas))
        if datas:
            self.set_datas(datas)
            self.selectRow(0)
            if not self.mini and self.FuturesInterface.quote_timer:
                self.FuturesInterface.quote_timer.start(0)
                self.FuturesInterface._isredy = True
            # self.FuturesInterface._isredy = True
            # if self.mini:
            #     self.horizontalHeader().setSectionResizeMode(
            #         QHeaderView.ResizeToContents)
            #     Width = []
            #     for i in range(3):
            #         Width.append(self.columnWidth(i))
            #     Width = sum(Width)+5
            #     self.setFixedWidth(Width)
            #     self.FuturesInterface.stackedWidget.currentWidget(
            #     ).quote_table_widget.setFixedWidth(Width)

    def set_datas(self, datas):
        """设置表格数据"""
        for i, data in enumerate(datas):
            for j, d in enumerate(data):
                item = SortItem(str(d))
                if self.mini:
                    if j in [1, 2]:
                        if d > 0.:
                            item.setForeground(QtColors.red.value)
                        elif d < 0.:
                            item.setForeground(QtColors.lime.value)
                        else:
                            item.setForeground(self._flat_color)
                    else:
                        item.setForeground(self._default_color)
                        self._items_index.append(j)
                elif self.isquote:
                    item.setForeground(self._default_color)
                    self._items_index.append(j)
                else:
                    if j == 7:
                        item.setForeground(QtColors.red.value)
                    elif j == 8:
                        item.setForeground(QtColors.lime.value)
                    elif j in [9, 10]:
                        if d > 0.:
                            item.setForeground(QtColors.red.value)
                        elif d < 0.:
                            item.setForeground(QtColors.lime.value)
                        else:
                            item.setForeground(self._flat_color)
                    else:
                        item.setForeground(self._default_color)
                        self._items_index.append(j)
                item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.setItem(i, j, item)
        self.__ready = True

        # self.viewport().update()

        if not self.isquote:
            self.column_height = self.verticalHeader().defaultSectionSize()
            self.vertical_row_range()

    def create_quote_timer(self):
        if not self.mini:
            self.FuturesInterface.create_quote_timer()

    def _set_items_colors(self, dark):
        self._default_color = QtColors.gold.value if dark else QtColors.black.value
        self._flat_color = QtColors.white.value if dark else QtColors.black.value
        for row in self._items_index:
            for col in range(self.colorCount()):
                item = self.item(row, col)
                if item:
                    item.setForeground(self._default_color)
        if self.isquote:
            c = 255 if isDarkTheme() else 0
            pen = QPen(QColor(c, c, c, 15), 1, Qt.SolidLine).style()
            self.setGridStyle(pen)

    @property
    def symbol_code_col(self) -> int:
        """返回合约代码所在的列序号"""
        return 0 if self.mini else 1

    def get_vertical_contract(self, start: int, end: int) -> list[str]:
        """获取表格可见范围内的所有合约代码"""
        return [self.item(i, self.symbol_code_col).text() for i in range(self.rowCount()) if start <= i <= end]

    def update_quote_table(self):
        if self.__ready:
            datas = self.update_quote()
            for col, ds in zip(self.update_datas_index, datas):
                for i, data in enumerate(ds):
                    item = self.item(i, col)
                    text = str(data)
                    if text != item.text():
                        font = item.font()
                        font.setBold(not font.bold())
                        item.setFont(font)
                    item.setText(text)
            self.viewport().update()

    def update_datas(self):
        """更新表格"""
        if self.__ready:
            start, end = self.vertical_row
            datas = self.datas_update_func(
                vertical_contract=self.get_vertical_contract(start, end))
            if datas:
                for i, data in zip(range(start, end+1), datas):
                    for j, d in zip(self.update_datas_index, data):
                        item = self.item(i, j)
                        text = str(d)
                        if text != item.text():
                            font = item.font()
                            font.setBold(not font.bold())
                            item.setFont(font)
                        item.setText(str(d))
                        if self.mini:
                            if d > 0.:
                                item.setForeground(QtColors.red.value)
                            elif d < 0.:
                                item.setForeground(QtColors.lime.value)
                            else:
                                item.setForeground(self._flat_color)
                        else:
                            if j in [9, 10]:
                                if d > 0.:
                                    item.setForeground(QtColors.red.value)
                                elif d < 0.:
                                    item.setForeground(QtColors.lime.value)
                                else:
                                    item.setForeground(self._flat_color)
                            else:
                                item.setForeground(self._default_color)
                self.viewport().update()


class PivotInterface(QWidget):
    """ Pivot interface """

    Nav = Pivot

    def __init__(self, parent: ChartMdiAreaWidget = None):
        super().__init__(parent=parent)
        self.ChartMdiAreaWidget = parent
        self.FuturesInterface: FuturesInterface = parent.FuturesInterface
        self.pivot = self.Nav(self)
        self.pivot.setFixedHeight(36)
        self.stackedWidget = QStackedWidget(self)
        vBoxLayout = QVBoxLayout(self)
        self.sift = QWidget(self)
        self.edit = MonacoEditor(self)
        self.backtesting = QWidget(self)
        self.playback = QWidget(self)
        self.trading = QWidget(self)
        self.addSubInterface(self.sift,
                             'sift', "筛选")
        self.addSubInterface(self.edit,
                             'edit', self.tr('编辑'))
        self.addSubInterface(self.backtesting,
                             'backtesting', self.tr('回测'))
        self.addSubInterface(self.playback,
                             'playback', self.tr('回放'))
        self.addSubInterface(self.trading,
                             'trading', self.tr('交易'))
        # self.pushbutton_min = TransparentToolButton(
        #     Icons.fa5s_minus())
        self.pushbutton_min = TransparentToolButton(
            FIF.MINIMIZE)
        self.pushbutton_min.clicked.connect(self.button_minsize)
        self.pushbutton_max = TransparentToolButton(
            FIF.FIT_PAGE)
        self._button_chcek = False
        self.pushbutton_max.clicked.connect(self.button_maxsize)
        layout = QHBoxLayout()
        layout.addWidget(self.pivot, alignment=Qt.AlignLeft)
        layout.addStretch(1)
        layout.addSpacing(1)
        # layout.addWidget(self.pushbutton_min,
        #                  alignment=Qt.AlignRight | Qt.AlignJustify)
        layout.addWidget(self.pushbutton_min,
                         alignment=Qt.AlignRight | Qt.AlignJustify)
        layout.addWidget(self.pushbutton_max,
                         alignment=Qt.AlignRight | Qt.AlignJustify)
        layout.setContentsMargins(0, 0, 0, 0)

        vBoxLayout.addLayout(layout)
        vBoxLayout.addWidget(self.stackedWidget)
        vBoxLayout.setContentsMargins(0, 0, 0, 0)
        vBoxLayout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        StyleSheet.NAVIGATION_VIEW_INTERFACE.apply(self)

        self.stackedWidget.currentChanged.connect(self.onCurrentIndexChanged)
        self.stackedWidget.setCurrentWidget(self.sift)
        self.pivot.setCurrentItem(self.sift.objectName())

        qrouter.setDefaultRouteKey(
            self.stackedWidget, self.sift.objectName())

    def button_minsize(self):
        sizes = self.ChartMdiAreaWidget.mdi_bottom_splitter.sizes()
        bottom_button = self.ChartMdiAreaWidget.ind_ScrollArea.interface.bottom_button
        if sizes[0] > 0:
            self.ChartMdiAreaWidget.mdi_bottom_splitter.setSizes([1, 0])
            bottom_button.setChecked(False)
        else:
            bottom_button.setChecked(True)

    def button_maxsize(self):
        self._button_chcek = not self._button_chcek
        splitter = self.ChartMdiAreaWidget.mdi_bottom_splitter
        if self._button_chcek:
            self.pushbutton_max.setIcon(FIF.BACK_TO_WINDOW)
            splitter.setSizes([0, 1])
        else:
            self.pushbutton_max.setIcon(FIF.FIT_PAGE)
            splitter.setSizes(splitter.mdi_bottom_splitter_sizes)

        # self.pivot.hBoxLayout.addLayout(layout)
        # self.pivot.hBoxLayout.addWidget(
        #     self.pushbutton_min, 0, Qt.AlignRight | Qt.AlignJustify)
        # self.pivot.hBoxLayout.addWidget(
        #     self.pushbutton_max, 0, Qt.AlignRight | Qt.AlignJustify)
        # self.pushbutton_max.clicked.connect(self._test)
        # self.pushbutton_min.clicked.connect(self._min)

    # def _test(self):
    #     if self.parent_widget.chart.isHidden():
    #         self.parent_widget.chart.show()
    #     else:
    #         self.parent_widget.chart.hide()
    #     if self.parent_widget.editor.isHidden():
    #         self.parent_widget.editor.show()

    # def _min(self):
    #     self.parent_widget.set_state()
    #     self.parent_widget.splitter.setSizes([1, 0])
    #     if self.parent_widget.chart.isHidden():
    #         self.parent_widget.chart.show()

    def addSubInterface(self, widget: QWidget, objectName, text):
        widget.setObjectName(objectName)
        widget.text = text
        self.stackedWidget.addWidget(widget)
        self.pivot.addItem(
            routeKey=objectName,
            text=text,
            onClick=lambda: self.stackedWidget.setCurrentWidget(widget)
        )

    def onCurrentIndexChanged(self, index):
        widget = self.stackedWidget.widget(index)
        name = widget.objectName()
        text = widget.text
        self.pivot.setCurrentItem(name)
        qrouter.push(self.stackedWidget, name)
        self.ChartMdiAreaWidget.ind_ScrollArea.interface.bottom_button.setText(
            text)


class MarketPage(QWidget):
    """
    parent:FuturesInterface
    subqwidget:
        stackedWidget : QStackedWidget
        pivot : SegmentedWidget
        main_contract_Interface = FuturesTable

    """

    def __init__(self, parent: FuturesInterface = None, mini=False) -> None:
        super().__init__(parent)
        self.setObjectName("MarketPage")
        layout = QVBoxLayout(self)
        self.FuturesInterface = parent
        self.stackedWidget = QStackedWidget(self)
        self.pivot = SegmentedWidget(self)

        layout.addWidget(self.stackedWidget)

        if mini:
            hlayout = QHBoxLayout()
            button = self.create_quote_menu()
            hlayout.addWidget(self.pivot, 0, Qt.AlignLeft)
            hlayout.addWidget(button, 1, Qt.AlignLeft)
            hlayout.setContentsMargins(0, 0, 0, 0)
            layout.addLayout(hlayout)
        else:
            # self.iscurrentwidget: bool = False
            hlayout = QHBoxLayout()
            self.morebutton = TransparentToolButton(FIF.MORE, self)
            hlayout.addWidget(self.pivot)
            hlayout.addWidget(self.morebutton, alignment=Qt.AlignRight)
            # layout.addWidget(self.pivot, 0, Qt.AlignLeft)
            hlayout.setContentsMargins(0, 0, 0, 0)
            layout.addLayout(hlayout)

        layout.setContentsMargins(0, 0, 0, 0)

        self.main_contract_Interface = FuturesTable(
            parent, "main_contract", mini)
        self.addSubInterface(self.main_contract_Interface,
                             "main_contract", "主力合约")

        self.stackedWidget.currentChanged.connect(self.onCurrentIndexChanged)
        self.stackedWidget.setCurrentWidget(self.main_contract_Interface)
        qrouter.setDefaultRouteKey(
            self.stackedWidget, self.main_contract_Interface.objectName())

    @property
    def currentwidget(self) -> FuturesTable:
        return self.stackedWidget.currentWidget()

    def create_quote_menu(self):
        """合约按钮"""
        button = TransparentDropDownPushButton(
            self.tr('合约'), self, FIF.SCROLL)
        button.setMenu(self.FuturesInterface.market_page.createCheckableMenu())
        button.setFixedHeight(30)
        setFont(button, 12)
        return button

    def createCheckableMenu(self, pos=None):
        """分类合约菜单"""
        menu = CheckableMenu(
            parent=self, indicatorType=MenuIndicatorType.RADIO)

        menu.addActions([
            Action("1"), Action("2")
        ])
        menu.addSeparator()
        menu.addActions([Action("3"), Action("4")])

        if pos is not None:
            menu.exec(pos, ani=True)

        return menu

    def all_market_table_widgets(self) -> list[FuturesTable]:
        """所有分类合约表格窗口"""
        return self.stackedWidget.findChildren(FuturesTable)

    def addSubInterface(self, widget: QWidget, objectName, text):
        widget.setObjectName(objectName)
        self.stackedWidget.addWidget(widget)
        self.pivot.addItem(
            routeKey=objectName,
            text=text,
            onClick=lambda: self.stackedWidget.setCurrentWidget(widget)
        )

    def onCurrentIndexChanged(self, index):
        widget = self.stackedWidget.widget(index)
        if not widget:
            return

        self.pivot.setCurrentItem(widget.objectName())
        qrouter.push(self.stackedWidget, widget.objectName())


class ChartSplitterWidget(QWidget):

    def __init__(self, parent: FuturesInterface = None, ContractDataSet: ContractDataSet = None) -> None:
        super().__init__(parent)
        self.setObjectName("ChartSplitterWidget")
        hlayout = QHBoxLayout(self)
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setHandleWidth(0)

        self.quote_table_widget = MarketPage(parent, True)
        self.chart_mdiarea_widget = ChartMdiAreaWidget(parent, ContractDataSet)
        self.splitter.addWidget(self.quote_table_widget)
        self.splitter.addWidget(self.chart_mdiarea_widget)
        hlayout.addWidget(self.splitter)
        hlayout.setContentsMargins(0, 0, 0, 0)
        self.splitter.setSizes([0, 1000])


class MdiArea(QMdiArea):
    def __init__(self, parent: ChartMdiAreaWidget | None = ...) -> None:
        super().__init__(parent)
        self.ChartMdiAreaWidget: ChartMdiAreaWidget = parent
        self.keyon = True
        # self._magnify = PushButton()
        self.pymouse = pynput.mouse.Controller()
        self.setMouseTracking(True)

    @property
    def markey_page(self) -> MarketPage:
        return self.ChartMdiAreaWidget.quote_table_widget

    @property
    def current_LightChartWidget(self) -> LightChartWidget:
        return self.ChartMdiAreaWidget.current_chart_widget

    def keyPressEvent(self, e: QKeyEvent) -> None:
        if e.key() == Qt.Key_Up:  # 放大K线
            # self.pymouse.scroll(10, 0)
            # pyautogui.scroll(10)
            self.pymouse.scroll(0, 10)
        elif e.key() == Qt.Key_Down:  # 缩放K线
            # self.pymouse.scroll(-10, 0)
            # pyautogui.scroll(-10)
            self.pymouse.scroll(0, -10)
        elif e.key() == Qt.Key_Left:  # 左移K线
            # thrend=WorkerThread(func=partial(move_releas,pos=50))
            # thrend.start()
            # x, y = self.pymouse.position
            # pydirectinput.position()
            # pydirectinput.mouseDown(button=pydirectinput.LEFT)
            # pydirectinput.moveTo(x-50, y)
            # pydirectinput.mouseUp(button=pydirectinput.LEFT)
            # pydirectinput.moveTo(x, y)
            # x,y = pyautogui.position()
            # old =QPoint(x,y)
            # new = QPoint(x+100, y)
            # QTest.mousePress(
            #     self, Qt.LeftButton, pos=old)
            # QTest.mouseMove(
            #     self, pos=new)
            # QTest.mouseRelease(
            #     self, Qt.LeftButton, pos=new)
            self.pymouse.press(pynput.mouse.Button.left)
            # 按下左键。

            self.pymouse.move(50, 0)
            # 右移50单位。

            # self.pymouse.move(0, 50)
            # 下移50单位。

            self.pymouse.release(pynput.mouse.Button.left)
        #     # position = pyautogui.position()

        #     # pyautogui.dragRel(position.x+100)
        #     # pyautogui.dragTo(position.x+100.,position.y)
        #     # pyautogui.mouseDown()
        #     # pyautogui.moveTo(position.x+100)
        #     # pyautogui.mouseUp()
        elif e.key() == Qt.Key_Right:  # 右移K线
            # x, y = self.pymouse.position
            # pydirectinput.leftClick()
            # pydirectinput.moveTo(x+50, y)
            # pydirectinput.moveRel(50, 0)
            # self.pymouse.release(pynput.mouse.Button.left)
            self.pymouse.press(pynput.mouse.Button.left)
            # 按下左键。

            self.pymouse.move(-50, 0)
            # 右移50单位。

            # self.pymouse.move(0, 50)
            # 下移50单位。

            self.pymouse.release(pynput.mouse.Button.left)
            # position = pyautogui.position()
            # old = QPoint(*position)
            # new = QPoint(position.x-100, position.y)
            # QTest.mousePress(
            #     self.current_LightChartWidget.QtChartQWidget, Qt.LeftButton, pos=old)
            # QTest.mouseMove(
            #     self.current_LightChartWidget.QtChartQWidget, pos=new)
            # QTest.mouseRelease(
            #     self.current_LightChartWidget.QtChartQWidget, Qt.LeftButton, pos=new)
        #     position = pyautogui.position()
        #     pyautogui.mouseDown(button='left')
        #     pyautogui.moveTo(position.x-100.)
        #     pyautogui.mouseUp(button='left')
        elif e.key() == Qt.Key_PageUp:  # 上一只合约
            self.markey_page.keypress(-1)
        elif e.key() == Qt.Key_PageDown:  # 下一只合约
            self.markey_page.keypress(1)
        elif e.key() == Qt.Key_Home:  # 首只合约
            self.markey_page(home=True)
        elif e.key() == Qt.Key_End:  # 最后一个合约
            self.markey_page(end=True)
        elif e.key() in Constant.KeyAlpha.value:  # 按下字母时，打开键盘精灵
            if self.keyon:  # 避免多次打开
                self.keyon = False
                text = Constant.Alpha.value[Constant.KeyAlpha.value.index(
                    e.key())]
                self.keyelfwin = KeyElfWindow_(self.ChartMdiAreaWidget, text)
        elif e.key() == Qt.Key_Escape:
            self.ChartMdiAreaWidget.FuturesInterface.main_window.return_history()
        return super().keyPressEvent(e)


class ChartMdiAreaWidget(QWidget):
    """图表区域窗口
    含行情表格、工具栏、图表"""

    def __init__(self, parent: FuturesInterface = None, ContractDataSet: ContractDataSet = None) -> None:
        super().__init__(parent)
        self.FuturesInterface = parent
        self.ContractDataSet = ContractDataSet
        self.indicators_dict = {}
        # self.iscurrentwidget: bool = False
        self.sub: list[QMdiSubWindow] = []
        self.initUI()

    def initUI(self):
        """初始化"""
        self.count = 0
        self.is_showMaximized = False
        self.adjustSize()
        hlayout = QVBoxLayout(self)
        self.ind_ScrollArea = CommonIndicatorCard(self)
        self.tool_bar, barwidget = self.createCommandBar()
        self.mdi = MdiArea(self)
        self.mdi.setActivationOrder(
            QMdiArea.ActivationHistoryOrder)
        self.widget1 = QWidget(self)
        self.widget2 = PivotInterface(self)
        layout = QVBoxLayout(self.widget1)
        layout.addWidget(self.mdi)
        layout.addWidget(self.ind_ScrollArea)
        layout.setContentsMargins(0, 0, 0, 0)
        self.mdi_bottom_splitter = QSplitter(Qt.Vertical)
        self.mdi_bottom_splitter.mdi_bottom_splitter_sizes = [4, 1]
        self.mdi_bottom_splitter.splitterMoved.connect(
            self.set_mdi_bottom_splitter_sizes)
        # self.mdi_bottom_splitter.setHandleWidth(10)
        # self.handle = CollapsibleSplitterHandle(
        #     parent=self.mdi_bottom_splitter)

        self.mdi_bottom_splitter.setHandleWidth(0)
        self.mdi_bottom_splitter.addWidget(self.widget1)
        self.mdi_bottom_splitter.addWidget(self.widget2)
        self.mdi_bottom_splitter.setSizes([1, 0])

        self.mdi_info_splitter = QSplitter(Qt.Horizontal)
        self.mdi_info_splitter.mdi_info_splitter_sizes = []
        self.mdi_info_splitter.splitterMoved.connect(
            self.set_mdi_info_splitter_sizes)
        self.mdi_info_splitter.setHandleWidth(0)
        self.sidebar_info = SidebarInfoInterface(self)
        self.info_stackWidget = QStackedWidget(self)
        self.quote_table_widget = MarketPage(self.FuturesInterface, True)
        self.quote_widget = FuturesTable(
            self.FuturesInterface, "quote", contractdataset=self.ContractDataSet)
        self.sidebar_info.set_stackWidget(
            self.info_stackWidget, {"期货": self.quote_table_widget, "Quote": self.quote_widget})
        self.mdi_info_splitter.addWidget(self.mdi_bottom_splitter)
        self.mdi_info_splitter.addWidget(self.info_stackWidget)
        self.mdi_info_splitter.setSizes([1, 0])
        self.mdi_info_splitter_info_interface = QWidget(self)
        misii_layout = QHBoxLayout(self.mdi_info_splitter_info_interface)
        misii_layout.addWidget(self.mdi_info_splitter)
        misii_layout.addWidget(self.sidebar_info)
        misii_layout.setContentsMargins(0, 0, 0, 0)

        # layout.addWidget(self.tool_bar)
        # layout.addWidget(self.mdi)

        # self.quote_table_widget.hide()
        # hlayout.addWidget(self.quote_table_widget)
        # hlayout.addWidget(self.tool_bar)
        hlayout.addWidget(barwidget)
        hlayout.addWidget(self.mdi_info_splitter_info_interface)
        hlayout.setContentsMargins(0, 0, 0, 0)
        self.mdi.setContextMenuPolicy(Qt.CustomContextMenu)
        self.mdi.customContextMenuRequested.connect(
            self.create_chart_menu)
        self.add_chart()
        self.fit_action = Action("全部数据视图")

    def set_mdi_bottom_splitter_sizes(self):
        sizes = self.mdi_bottom_splitter.sizes()
        self.mdi_bottom_splitter.mdi_bottom_splitter_sizes = sizes
        if sizes[1] > 0:
            if not self.ind_ScrollArea.interface.bottom_button.isChecked():
                self.ind_ScrollArea.interface.bottom_button.setChecked(True)
        else:
            if self.ind_ScrollArea.interface.bottom_button.isChecked():
                self.ind_ScrollArea.interface.bottom_button.setChecked(False)

    def set_mdi_info_splitter_sizes(self):
        sizes = self.mdi_info_splitter.sizes()
        self.mdi_info_splitter.mdi_info_splitter_sizes = sizes

        # if sizes[1]>0:
        #     if self.sidebar_info.stackWidget.isHidden():
        #         self.sidebar_info.stackWidget.show()
        # else:
        #     if not self.sidebar_info.stackWidget.isHidden():
        #         self.sidebar_info.stackWidget.hide()

    def add_chart(self, ContractDataSet: ContractDataSet = None):
        """增加K线窗口"""
        self.count = self.count + 1
        # 创建一个子窗口
        sub = QMdiSubWindow()
        sub.setWindowFlag(Qt.FramelessWindowHint)
        sub.setWidget(LightChartWidget(
            self.FuturesInterface, ContractDataSet if ContractDataSet else self.ContractDataSet))
        self.sub.append(sub)
        self.mdi.addSubWindow(sub)
        sub.show()
        # self.quote_table_widget.hide()
        self.mdi.tileSubWindows()

    def all_LightChartWidget(self) -> list[LightChartWidget]:
        """返回所有LightChartWidget窗口"""
        return self.mdi.findChildren(LightChartWidget)

    def close_chart(self, behind=None):
        """关闭子图表窗口,多图中可关闭"""
        if self.count > 1:
            if self.is_showMaximized:
                self.showfull_chart()
            sub = self.sub[-1] if behind else self.mdi.currentSubWindow()
            index = self.sub.index(sub)
            self.mdi.removeSubWindow(sub)
            self.sub.pop(index)
            self.mdi.tileSubWindows()
            self.count -= 1
            # if self.count == 1:
            #     self.current_qtchart.time_scale(visible=True)

    def showfull_chart(self):
        """子图表窗口最大化"""
        if self.count > 1:
            if self.is_showMaximized:
                self.mdi.tileSubWindows()
            else:
                self.mdi.currentSubWindow().showMaximized()
            self.is_showMaximized = not self.is_showMaximized

    @property
    def symbols(self) -> set:
        """窗口下所有图表合约的名称集合"""
        return set([chart.symbol for chart in self.all_LightChartWidget()])

    @property
    def cycles(self) -> set:
        """窗口下所有图表合约的周期集合"""
        return set([chart.cycle for chart in self.all_LightChartWidget()])

    @property
    def current_chart_widget(self) -> LightChartWidget:
        """当前图表窗口"""
        return self.mdi.currentSubWindow().widget()

    @property
    def current_subwindow(self) -> QMdiSubWindow:
        """当前区域窗口"""
        return self.mdi.currentSubWindow()

    @property
    def current_qtchart(self) -> QtChart:
        """当前窗口下的QtChart"""
        return self.current_chart_widget.chart

    @property
    def current_chart_qWidget(self) -> QWebEngineView:
        """当前窗口下的QtChart的widget"""
        return self.current_chart_widget.QtChartQWidget

    def createCommandBar(self):
        """创建工具栏"""
        # self.createTimeAction = Action(
        #     FIF.CALENDAR, self.tr('Create Date'), checkable=True)
        # self.shootTimeAction = Action(
        #     FIF.CAMERA, self.tr('Shooting Date'), checkable=True)
        # self.modifiedTimeAction = Action(
        #     FIF.EDIT, self.tr('Modified time'), checkable=True)
        # self.nameAction = Action(FIF.FONT, self.tr('Name'), checkable=True)
        # self.actionGroup1 = QActionGroup(self)
        # self.actionGroup1.addAction(self.createTimeAction)
        # self.actionGroup1.addAction(self.shootTimeAction)
        # self.actionGroup1.addAction(self.modifiedTimeAction)
        # self.actionGroup1.addAction(self.nameAction)

        # self.ascendAction = Action(
        #     FIF.UP, self.tr('Ascending'), checkable=True)
        # self.descendAction = Action(
        #     FIF.DOWN, self.tr('Descending'), checkable=True)
        # self.actionGroup2 = QActionGroup(self)
        # self.actionGroup2.addAction(self.ascendAction)
        # self.actionGroup2.addAction(self.descendAction)

        # self.shootTimeAction.setChecked(True)
        # self.ascendAction.setChecked(True)
        barwidget = myqwidget(self)
        barwidget.setFixedHeight(34)
        layout = QHBoxLayout(barwidget)
        layout.setContentsMargins(0, 2, 2, 2)
        bar = MyCommandBar(self)
        bar.setFixedHeight(30)
        bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        bar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        self.mini_quote_button = TransparentToolButton(FIF.LEFT_ARROW)
        self.mini_quote_button.setIconSize(QSize(16, 16))
        self.mini_quote_button.setToolTip("返回")
        self.mini_quote_button.clicked.connect(
            self.FuturesInterface.main_window.return_history)
        bar._insertWidgetToLayout(-1, self.mini_quote_button)
        # self.ind_card.addCard(widget=self.mini_quote_button)
        # self.ind_card.addCard(Icons.line_chart_line(),
        #                       "指标")
        # bar._insertWidgetToLayout(-1, self.ind_card)

        # add custom widget
        candles_button = TransparentDropDownPushButton(
            self.tr('K线'), self, Icons.stock_fill())
        candles_button.setMenu(self.create_candles_menu())
        candles_button.setFixedHeight(30)
        setFont(candles_button, 12)
        # for a in self.candles_actions:
        #     a.setChecked(a._candles_name ==
        #                  self.current_chart_widget._candles_style)
        bar.addWidget(candles_button)

        # add custom widget
        button = TransparentDropDownPushButton(
            self.tr('周期'), self, Icons.recycle())
        button.setMenu(self.create_cycle_menu())
        button.setFixedHeight(30)
        setFont(button, 12)
        bar.addWidget(button)

        # add custom widget
        ind_button = TransparentDropDownPushButton(
            self.tr('指标'), self, FIF.MARKET)
        ind_button.setMenu(self.create_indicator_menu())
        ind_button.setFixedHeight(30)
        setFont(ind_button, 12)
        bar.addWidget(ind_button)

        ind_layout = TransparentDropDownPushButton(
            self.tr('未命名'), self, FIF.APPLICATION)
        ind_layout.setFixedHeight(30)
        setFont(ind_layout, 12)

        # add custom widget
        multi_button = TransparentDropDownPushButton(
            self.tr('多周期'), self, FIF.TILES)
        multi_button.setFixedHeight(30)
        setFont(multi_button, 12)
        multi_button.setMenu(self.create_multi_menu())
        bar.addWidget(multi_button)

        # ind_button.setIcon(Icons.line_chart_line)
        bar.addSeparator()
        #
        # addaction = Action(FIF.ADD, self.tr('指标'), checkable=True)
        # addaction.setChecked(True)
        # addaction.triggered.connect(self.indicators_tool)
        # bar.addAction(addaction)

        edit = Action(FIF.EDIT, self.tr('工具'), checkable=True)
        edit.triggered.connect(self.toolbox)
        bar.addAction(edit)

        code = Action(FIF.CODE, "代码")
        # code.triggered.connect(self._test)
        bar.addAction(code)

        # bar.addActions([
        #     Action(FIF.ROTATE, self.tr('Rotate')),
        #     Action(FIF.ZOOM_IN, self.tr('Zoom in')),
        #     Action(FIF.ZOOM_OUT, self.tr('Zoom out')),
        # ])

        # bar.addActions([
        #     Action(FIF.INFO, self.tr('Info')),
        #     Action(FIF.DELETE, self.tr('Delete')),
        #     Action(FIF.SHARE, self.tr('Share'))
        # ])

        bar.addHiddenActions([
            Action(FIF.SETTING, self.tr('Settings'), shortcut='Ctrl+I'),
        ])
        # bar.addWidget(self.ind_card)

        camera = TransparentToolButton(FIF.CAMERA, self)
        camera.setToolTip("生成快照")
        camera.setFixedHeight(30)
        # test.setMaximumWidth(100)
        layout.addWidget(bar)  # , 10, alignment=Qt.AlignLeft)
        layout.addWidget(ind_layout, alignment=Qt.AlignRight)
        layout.addWidget(camera, alignment=Qt.AlignRight)
        # layout.setStretch(1, 0)
        layout.setContentsMargins(0, 0, 0, 0)
        return bar, barwidget

    def _test(self, qtimer, menu):
        monacoeditor = MonacoEditor(
            self.FuturesInterface, qtimer.codesource())
        menu._hideMenu(True)
        self.FuturesInterface.main_window.titleBar.addSubInterface(
            monacoeditor, qtimer.indname, qtimer.indname, Icons.line_chart_line())

    def indicators_tool(self):
        ...
        # if self.ind_ScrollArea.isHidden():
        #     self.ind_ScrollArea.show()
        # else:
        #     self.ind_ScrollArea.hide()

    def create_multi_menu(self):
        # 创建菜单
        menu = MultiCycleButton(
            parent=self, indicatorType=MenuIndicatorType.RADIO)
        cycle_actions = []
        key = self.ContractDataSet.symbol
        cycle = Cycles.get_multi_check(key)
        for k, v in Cycles.__dict__.items():
            if not k.startswith("_"):
                cycle_action = Action(self.tr(k), checkable=True)
                cycle_action.setChecked(v in cycle)
                cycle_action.multi_key = key
                cycle_action.cycle = v
                cycle_actions.append(cycle_action)
        menu.addActions(cycle_actions)
        action = Action('确定', checkable=False)
        menu.triggered.connect(self._checkAction)
        # 添加自定义的属性,判断该属性可以关闭菜单
        action.setProperty('canHide', True)
        menu.addSeparator()
        menu.addAction(action)
        return menu

    def _checkAction(self, action: Action):
        if action.text() == "确定":
            key = self.ContractDataSet.symbol
            cycle = sorted(Cycles.get_multi_check(key), reverse=True)

            count = self.count
            # print(cycle, count > len(cycle))
            contracts = [self.FuturesInterface.main_window.tq_api.contract_set(
                key, c) for i, c in enumerate(cycle)]
            if any([isinstance(contract, str) for contract in contracts]):
                InfoBar.success(
                    title=self.tr('TqTimeoutError'),
                    content=self.tr(contract),
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=2000,
                    parent=self.FuturesInterface
                )
            else:
                for i, contract in enumerate(contracts):
                    # ContractDataSet = self.FuturesInterface.main_window.tq_api.contract_set(
                    #     key, c)
                    # contract=self.FuturesInterface.main_window.tq_api.contract_set(symbol, light_chart.cycle)

                    if i < count:
                        self.sub[i].widget().replace_symbol(contract)
                    else:
                        self.add_chart(contract)
                if count > len(cycle):
                    for _ in range(count-len(cycle)):
                        self.close_chart(True)

            return
        key, cycle = action.multi_key, action.cycle
        cycle_set = Cycles.get_multi_check(key)
        if cycle in cycle_set:
            Cycles.delete_cycle(key, cycle)
        else:
            Cycles.set_cycle(key, cycle)

    def toolbox(self):
        """加载画图工具"""
        for widget in self.all_LightChartWidget():
            widget._is_toolbox = not widget._is_toolbox
            widget.chart_toolbox()

    def mini_quote_table_show(self):
        """行情窗口打开与收起"""
        ...
        # if self.quote_table_widget.isHidden():
        #     self.mini_quote_button.setIcon(FIF.LEFT_ARROW)
        #     self.mini_quote_button.setToolTip("收起行情")
        #     self.quote_table_widget.show()
        # else:
        #     self.mini_quote_button.setIcon(FIF.RIGHT_ARROW)
        #     self.mini_quote_button.setToolTip("打开行情")
        #     self.quote_table_widget.hide()

    def create_candles_menu(self, pos=None):
        menu = CheckableMenu(
            parent=self, indicatorType=MenuIndicatorType.RADIO)
        self.candles_actions: list[Action] = []
        style = ["Candlestick", "Heikin_Ashi_Candles",
                 "Linear_Regression_Candles"]
        for k in style:
            candles_action = Action(self.tr(k), checkable=True)
            candles_action._candles_name = k
            self.candles_actions.append(candles_action)
        menu.addActions(self.candles_actions)

        menu.addSeparator()
        action = Action(self.tr("指标跟随K线"), checkable=True)
        action.setProperty("followKline", True)
        self.candles_actions.append(action)
        menu.addAction(action)
        menu.triggered.connect(self.change_candles_style)
        self.candles_actions[0].setChecked(True)
        # menu.addActions([
        #     self.createTimeAction, self.shootTimeAction,
        #     self.modifiedTimeAction, self.nameAction
        # ])
        # menu.addSeparator()
        # menu.addActions([self.ascendAction, self.descendAction])

        if pos is not None:
            menu.exec(pos, ani=True)

        return menu

    def set_follow_action(self, value: bool):
        self.candles_actions[-1].setChecked(value)

    def change_candles_style(self, action: Action):
        if action.property("followKline"):
            for chart in self.all_LightChartWidget():
                chart.reload_data()

        else:
            for chart in self.all_LightChartWidget():
                chart.change_candles_style(
                    action._candles_name)
            for a in self.candles_actions:
                a.setChecked(a == action)

    def create_cycle_menu(self, pos=None):
        menu = CheckableMenu(
            parent=self, indicatorType=MenuIndicatorType.RADIO)
        cycle_actions = []
        for k, v in Cycles.__dict__.items():
            if not k.startswith("_"):
                cycle_action = Action(self.tr(k), checkable=True)
                cycle_action.cycle = v
                # cycle_action.multi_index=i
                cycle_actions.append(cycle_action)
        menu.addActions(cycle_actions)
        menu.triggered.connect(self.conversion_cycle)
        # menu.addActions([
        #     self.createTimeAction, self.shootTimeAction,
        #     self.modifiedTimeAction, self.nameAction
        # ])
        # menu.addSeparator()
        # menu.addActions([self.ascendAction, self.descendAction])

        if pos is not None:
            menu.exec(pos, ani=True)

        return menu

    def conversion_cycle(self, action: Action):
        symbol = self.current_chart_widget.symbol
        contract = self.FuturesInterface.main_window.tq_api.contract_set(
            symbol, action.cycle)
        if isinstance(contract, str):
            InfoBar.success(
                title=self.tr('TqTimeoutError'),
                content=self.tr(contract),
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self.FuturesInterface
            )
        else:
            self.current_chart_widget.replace_symbol(contract)

    def create_indicator_menu(self) -> RoundMenu:
        indMenu = RoundMenu("技术指标", parent=self)
        indMenus: list[RoundMenu] = []
        if not self.indicators_dict:
            for k, v in vars(IndicatorClass).items():
                if not k.startswith("_"):
                    inds = []
                    for k_, v_ in vars(v).items():
                        if isinstance(v_, Callable) and not k_.startswith("_") and k_ not in not_indicator_list:
                            inds.append(k_)
                    self.indicators_dict.update({k: inds})
        for k, v in self.indicators_dict.items():
            indMenus.append(RoundMenu(k, parent=self))
            indMenus[-1].addActions([
                Action(self.tr(name)) for name in v])
            indMenus[-1].triggered.connect(
                partial(self.add_indicator, indclsname=k))
            indMenu.addMenu(indMenus[-1])
        return indMenu

    def create_cycle_menu(self) -> RoundMenu:
        cyclemenu = RoundMenu("周期", parent=self)
        cycle_actions = []
        for k, v in Cycles.__dict__.items():
            if not k.startswith("_"):
                cycle_action = Action(self.tr(k))
                cycle_action.cycle = v
                cycle_actions.append(cycle_action)
        cyclemenu.addActions(cycle_actions)
        cyclemenu.triggered.connect(self.conversion_cycle)
        return cyclemenu

    def create_chart_menu(self, event):
        """右键菜单"""
        Menu = RoundMenu(parent=self)
        # K线设置

        # 技术指标
        indMenu = RoundMenu("技术指标", parent=self)
        Menu.addMenu(self.create_indicator_menu())
        indMenus: list[RoundMenu] = []
        if not self.indicators_dict:
            for k, v in vars(IndicatorClass).items():
                if not k.startswith("_"):
                    inds = []
                    for k_, v_ in vars(v).items():
                        if isinstance(v_, Callable) and not k_.startswith("_") and k_ not in not_indicator_list:
                            inds.append(k_)
                    self.indicators_dict.update({k: inds})
        for k, v in self.indicators_dict.items():
            indMenus.append(RoundMenu(k, parent=self))
            indMenus[-1].addActions([
                Action(self.tr(name)) for name in v])
            indMenus[-1].triggered.connect(
                partial(self.add_indicator, indclsname=k))
            indMenu.addMenu(indMenus[-1])
        cyclemenu = RoundMenu("周期", parent=self)
        Menu.addMenu(self.create_cycle_menu())
        cycle_actions = []
        for k, v in Cycles.__dict__.items():
            if not k.startswith("_"):
                cycle_action = Action(self.tr(k))
                cycle_action.cycle = v
                cycle_actions.append(cycle_action)
        cyclemenu.addActions(cycle_actions)
        cyclemenu.triggered.connect(self.conversion_cycle)

        self.fit_action.triggered.connect(self.fit)
        Menu.addAction(self.fit_action)
        watermark_action = Action(
            "删除水印" if self.current_chart_widget._is_watermark else "添加水印")
        watermark_action.triggered.connect(self.watermark)
        Menu.addAction(watermark_action)
        Menu.addSeparator()
        if self.count < 9:
            logaction = Action("增加图表")
            logaction.triggered.connect(self.add_chart)
            Menu.addAction(logaction)
        if self.count > 1:
            logaction1 = Action(
                '恢复' if self.is_showMaximized else "最大化")
            logaction1.triggered.connect(self.showfull_chart)
            Menu.addAction(logaction1)
            logaction2 = Action("关闭图表")
            logaction2.triggered.connect(self.close_chart)
            Menu.addAction(logaction2)
        # values = list(
        #     self.current_chart_widget.qtimer_explorer.charts.values())
        # if len(values) > 1:
        #     Menu.addSeparator()
        #     close_subchart = RoundMenu("关闭副图", parent=self)
        #     for value in values[1:]:
        #         name = value.name
        #         action = Action(str(name))
        #         action.name = name
        #         action._key = value._key
        #         close_subchart.addAction(action)
        #     close_subchart.triggered.connect(self.delelte_subchart)
        #     Menu.addMenu(close_subchart)
        # 指标参数设置与删除指标
        candle_setting = None
        ind_setting = None
        del_ind = None
        if self.current_chart_widget.candles_style != "Candlestick":
            if candle_setting is None:

                candle_setting = RoundMenu("K线参数")
                action = Action(self.current_chart_widget.candles_style)
                action._object = self.current_chart_widget
                candle_setting.addAction(action)
                candle_setting.triggered.connect(self.replace_params)
                Menu.addSeparator()
                Menu.addMenu(candle_setting)

        main_qtimers = self.current_chart_widget.chart._qtimers
        if main_qtimers:
            if ind_setting is None:
                ind_setting = RoundMenu("参数设置", parent=self)
            if del_ind is None:
                del_ind = RoundMenu("删除指标", parent=self)

            main = RoundMenu("主图指标")
            del_main = RoundMenu("主图指标")
            for _, v in main_qtimers.items():
                action = Action(v.indname)
                action._object = v
                main.addAction(action)
                del_action = Action(v.indname)
                del_action._object = v
                del_main.addAction(del_action)
            main.triggered.connect(self.replace_params)
            del_main.triggered.connect(self.del_main_indicator)
            ind_setting.addMenu(main)
            del_ind.addMenu(del_main)
        if len(self.current_chart_widget.qtimer_explorer.charts) > 1:
            if ind_setting is None:
                ind_setting = RoundMenu("参数设置", parent=self)
            if del_ind is None:
                del_ind = RoundMenu("删除指标", parent=self)
            sub = RoundMenu("副图指标")
            del_sub = RoundMenu("副图指标")
            for i, (name, subchart) in enumerate(self.current_chart_widget.qtimer_explorer.charts.items()):
                if i:
                    action = Action(subchart.name)
                    action._object = subchart._qtimer
                    sub.addAction(action)
                    del_action = Action(subchart.name)
                    del_action.name = name
                    del_action._key = subchart._key
                    del_sub.addAction(del_action)
            sub.triggered.connect(self.replace_params)
            del_sub.triggered.connect(self.del_sub_indicator)
            ind_setting.addMenu(sub)
            del_ind.addMenu(del_sub)

        if any([ind_setting, del_ind]) and not candle_setting:
            Menu.addSeparator()
        if ind_setting:
            Menu.addMenu(ind_setting)
        if del_ind:
            Menu.addMenu(del_ind)

        Menu.exec_(QCursor.pos())

    def del_main_indicator(self, action):
        self.current_chart_widget.deltet_main_indicator(action._object)

    def del_sub_indicator(self, action):
        self.current_chart_widget.delete_subchart(action._key)

    def replace_params(self, action):
        """指标更换参数"""
        self.ind_params_widget = IndicatorParamsWindow(
            action._object, self.current_chart_widget.ContractDataSet)
        self.ind_params_widget.show()
        self.ind_params_widget.setFixedSize(self.ind_params_widget.size())

    def fit(self):
        """全部数据视图"""
        text = self.fit_action.text()
        if text == "全部数据视图":
            widget = self.current_chart_widget
            for _, chart in widget.qtimer_explorer.charts.items():
                chart.fit()
            self.fit_action.setText("恢复正常视图")
        else:
            widget = self.current_chart_widget
            data = widget.kline
            start = data["datetime"].iloc[-min([300, data.shape[0]])]
            end = data["datetime"].iloc[-1]
            for _, chart in widget.qtimer_explorer.charts.items():
                chart.set_visible_range(start, end)
            self.fit_action.setText("全部数据视图")
        self.fit_action.triggered.disconnect()

    def watermark(self):
        """图表水印"""
        for widget in self.all_LightChartWidget():
            if widget._is_watermark:
                widget.chart.watermark("")
            else:
                widget.chart.watermark(widget.chart.name)
            widget._is_watermark = not widget._is_watermark

    def add_indicator(self, obj: Action, indclsname: str = ""):
        """添加指标"""
        indcls = getattr(IndicatorClass, indclsname)
        indname = obj.text()
        self.current_chart_widget._add_indicator(indcls, indname)

    def setChartStyle(self, dark=True):
        """设置样式"""
        for widget in self.all_LightChartWidget():
            widget.setChartStyle(dark)

        for button in self.findChildren(TransparentDropDownPushButton):
            if button.text() in ["K线", "周期"]:
                ...

    def delelte_subchart(self, action):
        """删除副图"""
        widget = self.current_chart_widget
        widget.delete_subchart(action._key)

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
        # painter.drawRect(1, self.height()-2, self.width(), 0.5)
        painter.drawRect(1, 1, self.width()-2, self.height()-2)


class LightChartWidget(QWidget):
    """tradingview python
    """
    lockback_index = 2

    def __init__(self, parent: FuturesInterface, ContractDataSet: ContractDataSet = None) -> None:
        super().__init__(parent)
        self.FuturesInterface = parent
        self.ContractDataSet = ContractDataSet
        self.last_bar_time: int = 1
        self._is_watermark: bool = False
        self._is_toolbox: bool = False
        self.init_chart()
        self.ind_card = Ind_Card(self, self.FuturesInterface)
        self.ind_card.setObjectName('ind_card')
        self.ind_card.move(100, 5)
        # self.getVisibleRange()

    @property
    def _pos(self):
        return self.mapFromGlobal(self.pos())

    def init_chart(self):
        """初始化"""
        self.adjustSize()
        self.hlayout = QHBoxLayout(self)
        self.create_chart()
        self.setChartStyle(qconfig.theme == Theme.DARK)
        self.hlayout.addWidget(self.QtChartQWidget)
        self.hlayout.setContentsMargins(0, 0, -2, 0)
        self.qtimer_explorer = QtimerExplorer(self)
        self.chart_ind_color = get_colors()

    @property
    def main_legend_params(self):
        return dict(text=self.ContractDataSet.symbol, color=self.legend_color, lines=True, font_size=12, color_based_on_candle=True)

    def sub_legend_params(self, name):
        return dict(text=name, color=self.legend_color, lines=True, font_size=12, color_based_on_candle=True)

    def on_range_change(self, chart, bars_before, bars_after):
        ...
        # print(f'Horizontal line moved to: {bars_before, bars_after}')

    def create_chart(self):
        """创建QtChart"""
        self.kline = self.ContractDataSet.kline
        self.tick = self.ContractDataSet.tick
        self.chart = QtChart(self.FuturesInterface, toolbox=self._is_toolbox,)
        self.chart.name = f"{self.symbol}-{Cycles.cyclestring.get(self.cycle)}"
        self.chart.webview.setContextMenuPolicy(Qt.NoContextMenu)
        self.chart.legend(
            True, **self.main_legend_params)
        self.chart.set(self.ContractDataSet.all_kline)
        self.chart.events.range_change += self.on_range_change

    @property
    def follow_kline(self) -> bool:
        return self.ContractDataSet._follow_kline

    @follow_kline.setter
    def follow_kline(self, value: bool):
        self.ContractDataSet._follow_kline = value

    @property
    def candles_style(self) -> Literal["Candlestick", "Heikin_Ashi_Candles", "Linear_Regression_Candles"]:
        return self.ContractDataSet._candles_style

    @candles_style.setter
    def candles_style(self, value: str):
        self.ContractDataSet._candles_style = value

    @property
    def is_candles_style(self) -> bool:
        return self.ContractDataSet._is_candles_style

    @is_candles_style.setter
    def is_candles_style(self, value: bool):
        self.ContractDataSet._is_candles_style = value

    def set_candles_style(self):
        ...

    @property
    def legend_color(self) -> str:
        return Icons.white if qconfig.theme == Theme.DARK else Icons.black

    def chart_toolbox(self):
        """加载画图工具,需重新加载"""
        self.qtimer_explorer.stop_qtimer()
        widget = self.QtChartQWidget
        self.hlayout.removeWidget(widget)
        old_chart_qtimers = self.chart._qtimers
        timers = self.qtimer_explorer.subchart_ind_qtimers
        self.create_chart()
        self.qtimer_explorer.replace_qtimer(self, old_chart_qtimers, timers)
        self.hlayout.addWidget(self.QtChartQWidget)
        widget.deleteLater()
        dark = qconfig.theme == Theme.DARK
        for _, v in self.qtimer_explorer.charts.items():
            self.setChartStyle(dark, v)
        for _, v in self.qtimer_explorer.subcharts.items():
            self.setChartStyle(dark, v)

    def get_data(self, follow: bool = True) -> pd.DataFrame:
        return self.ContractDataSet.get_data(follow)

    @property
    def all_kline(self) -> pd.DataFrame:
        return self.ContractDataSet.all_kline

    def reload_data(self):
        self.follow_kline = not self.follow_kline
        if self.ContractDataSet._is_candles_style:
            self.qtimer_explorer.stop_qtimer()
            self.qtimer_explorer.restart()

    def change_candles_style(self, style: str):
        """改变K线风格"""
        if style == "Candlestick" and self.candles_style != "Candlestick":
            self.qtimer_explorer.stop_qtimer()
            self.ContractDataSet.set_candles_style(style)
            # self.FuturesInterface.currentwidget.candles_actions[-1].setChecked(
            #     False)
            # kline = self.ContractDataSet.data
            self.chart.set(self.all_kline)
            self.qtimer_explorer.restart()
            # self.candles_style = style
            # self.is_candles_style = False
            return
        if style != self.candles_style:
            self.qtimer_explorer.stop_qtimer()
            self.ContractDataSet.set_candles_style(style)

            # kline = self.ContractDataSet.all_kline
            # self.candles_func = getattr(kline.ta, style)
            # self.ContractDataSet.candles_params = get_func_parameters(
            #     self.candles_func)
            # data = self.candles_func(**self.ContractDataSet.candles_params)
            # data = self.__add_columns(data, kline)
            self.chart.set(self.all_kline)
            self.qtimer_explorer.restart()
            # self.candles_style = style

    def change_candles_params(self, params: dict):
        """改变K线风格参数"""
        self.qtimer_explorer.stop_qtimer()
        self.ContractDataSet.candles_params = params
        # kline = self.ContractDataSet.all_kline
        # data = self.candles_func(**params)
        # data = self.__add_columns(data, kline)
        self.chart.set(self.all_kline)
        self.qtimer_explorer.restart()

    def replace_symbol(self, ContractDataSet: ContractDataSet):
        """更换合约"""
        if self.ContractDataSet != ContractDataSet:
            self.qtimer_explorer.stop_qtimer()
            self.ContractDataSet *= ContractDataSet
            self.kline = self.ContractDataSet.kline
            self.tick = self.ContractDataSet.tick
            self.chart.name = f"{self.symbol}-{Cycles.cyclestring.get(self.cycle)}"
            self.chart.legend(
                True, **self.main_legend_params)
            # if self.is_candles_style:
            #     kline = self.candles_conversion_data(
            #         self.ContractDataSet.all_kline)
            # else:
            #     kline = self.ContractDataSet.all_kline
            self.chart.set(self.all_kline)
            self.qtimer_explorer.restart()
            if self._is_watermark:
                self.chart.watermark(self.chart.name)
            self.FuturesInterface.setTabName(self.chart.name)

    @property
    def record_last_bar_time(self) -> None:
        """K线记录最后更新的时间,ns(纳秒)"""
        self.last_bar_time = self.chart._last_bar["time"]

    @property
    def symbol(self) -> str:
        """合约名称"""
        return self.ContractDataSet.symbol

    @property
    def cycle(self) -> int:
        """周期"""
        return self.ContractDataSet.duration_seconds

    # @property
    # def iscurrentwidget(self) -> bool:
    #     """判断是否是当前页面,非当前页面不更新,减少资源消耗"""
    #     return self.FuturesInterface.stackedWidget.currentWidget().iscurrentwidget

    def kline_update(self):
        """K线更新函数"""
        if self.ContractDataSet.wait_update:  # self.iscurrentwidget and
            chang = self.is_changing(
                self.chart, self.kline["datetime"].iloc[-1])
            # if self.is_candles_style:
            #     kline = self.candles_conversion_data(
            #         self.ContractDataSet.update_kline(chang))
            #     series = kline.iloc[-1][FILED.TV]
            # else:
            #     kline = self.kline
            kline = self.ContractDataSet.update_kline(chang)
            series = kline.iloc[-1][FILED.TV]
            if chang:
                for i in range(-self.lockback_index-chang, 0):
                    self.chart.update(kline.iloc[i])

            series['price'] = self.tick.iloc[-1]["last_price"]
            series.index = FILED.TICK
            self.chart.update_from_tick(series)

    def is_changing(self, obj: Union[Candlestick, Line], ns) -> int:
        """判断是否更新,获取最新时间与图表最后更新时间的差转化为需要更新数据的K线数量"""
        return int((ns*1e-9-obj._last_bar["time"])/self.cycle)

    def timer_func(self, indcls: Callable, indname: str, lines: dict[str, Line], params: dict):
        """qtimer更新指标函数"""
        if self.ContractDataSet.wait_update and self.ContractDataSet.is_quote_changing:  # self.iscurrentwidget and
            follow = params.get("follow", True)
            for i, (name, line) in enumerate(lines.items()):
                if not i:
                    chang = self.is_changing(
                        line, self.kline["datetime"].iloc[-1])
                    data = getattr(
                        indcls(self.ContractDataSet.get_update_data(chang, follow)), indname)(**params)
                d = data[["time", name]]
                if chang:
                    for j in range(-self.lockback_index-chang, 0):
                        line.update(d.iloc[j])
                else:
                    line.update(d.iloc[-1])

    def _add_indicator(self, indcls: Callable, indname: str, params: dict = {}):
        """添加指标"""
        kline = self.ContractDataSet.get_data()
        indicator = getattr(indcls(kline), indname)
        doc = indicator.__doc__
        data = indicator(
            **{**params, "light_chart": True})
        if self.follow_kline:
            params.update({"follow": True})
        data_overlap = data.category == "overlap" or data.overlap
        overlap = params.get("overlap", data_overlap)
        lines: dict = {}
        sub_col = ["time",]
        laps = []
        if overlap:
            lower, highest = kline.low.min(), kline.high.max()
            for i, col in enumerate(data.columns):
                if i:
                    lap = data[col].apply(lambda x: lower < x < highest).any()
                    laps.append(lap)
                    if lap:
                        color = next(self.chart_ind_color)
                        style = 'solid'
                        width = 2
                        line = self.chart.create_line(
                            col, color=color, style=style, width=width, price_line=False, price_label=False)
                        line.set_line_info(col, color, style, width)
                        line.set(data[["time", col]])
                        lines.update({col: line})
                    else:
                        sub_col.append(col)
            if len(sub_col) > 1:
                params.update({"overlap": True})
            index = len(self.chart._qtimers)
            name = f"{indname}_{index}"
            timer = Timer(self, index, indcls, indname,
                          lines, deepcopy(params), doc)

            # self.ind_card.addInd("M", timer)
            self.ContractDataSet.params_lenght = timer.max_params_lenght
            self.qtimer_explorer.main_ind_qtimer.update(
                {name: timer})
        else:
            if "overlap" in params and params["overlap"] != data_overlap:
                lower, highest = kline.low.min(), kline.high.max()
                for i, col in enumerate(data.columns):
                    if i:
                        lap = data[col].apply(
                            lambda x: lower < x < highest).any()
                        laps.append(lap)
                        if overlap and lap:
                            color = next(self.chart_ind_color)
                            style = 'solid'
                            width = 2
                            line = self.chart.create_line(
                                col, color=color, style=style, width=width, price_line=False, price_label=False)
                            line.set_line_info(col, color, style, width)
                            line.set(data[["time", col]])
                            lines.update({col: line})
                        else:
                            sub_col.append(col)
                params = params.update({"overlap": False})
                data = data[sub_col]
            self.create_subchart(data, indcls, indname, params, doc)

    def _reload_indicator(self, indcls: Callable, indname: str, lines: dict[str, Line], params: dict):
        """更换指标"""
        follow = params.get("follow", True)
        data = getattr(indcls(self.ContractDataSet.get_data(
            follow=follow)), indname)(**params)
        for name, line in lines.items():
            line.set(data[["time", name]])

    def _resizes(self):
        """指标窗口高度设置,主图占3,副图占1"""
        num_chart = len(self.qtimer_explorer.charts)-1
        if num_chart >= 1:
            num = round(1./(3+num_chart), 3)
            for i, (_, chart) in enumerate(self.qtimer_explorer.charts.items()):
                size = num if i else 1.-num_chart*num
                chart.resize(1., size)
            for _, subchart in self.qtimer_explorer.subcharts.items():
                if subchart._height:
                    subchart.resize(1., 0.)
        else:
            self.chart.resize(1, 1)

    def _lines_main_style(self, timer: Timer):
        timer.stop()
        indcls = timer.indcls
        indname = timer.indname
        params = timer._params
        kline = self.ContractDataSet.get_data(timer.follow)
        indicator = getattr(indcls(kline), indname)
        data = indicator(**params)
        lower, highest = kline.low.min(), kline.high.max()
        lines: dict = {}
        for i, col in enumerate(data.columns):
            if i:
                overlap = data[col].apply(lambda x: lower < x < highest).any()
                if overlap:
                    params = timer.lines[col].get_line_info()
                    _line = timer.lines.pop(col)
                    _line.delete()
                    line = self.chart.create_line(
                        price_line=False, price_label=False, **params)
                    line.set_line_info(**params)
                    line.set(data[["time", col]])
                    lines.update({col: line})
        timer.restart(lines)
        return timer

    def _lines_sub_style(self, timer: Timer):
        timer.stop()
        subchart = self.qtimer_explorer.charts[timer.id]
        indcls = timer.indcls
        indname = timer.indname
        params = timer._params
        kline = self.ContractDataSet.get_data(timer.follow)
        indicator = getattr(indcls(kline), indname)
        data = indicator(**params)
        lower, highest = kline.low.min(), kline.high.max()
        lines: dict = {}
        for i, col in enumerate(data.columns):
            if i:
                overlap = data[col].apply(lambda x: lower < x < highest).any()
                if not overlap:
                    params = timer.lines[col].get_line_info()
                    _line = timer.lines.pop(col)
                    _line.delete()
                    line = subchart.create_line(
                        price_line=False, price_label=False, **params)
                    line.set_line_info(**params)
                    line.set(data[["time", col]])
                    lines.update({col: line})
        # subchart.name = indname
        timer.restart(lines)
        # subchart._qtimer = timer
        return subchart

    def _reload_main(self, timer: Timer):
        """重新加载主图指标"""
        indcls = timer.indcls
        indname = timer.indname
        params = timer._params
        kline = self.ContractDataSet.get_data(timer.follow)
        indicator = getattr(indcls(kline), indname)
        data = indicator(**params)
        lower, highest = kline.low.min(), kline.high.max()
        lines: dict = {}
        for i, col in enumerate(data.columns):
            if i:
                overlap = data[col].apply(lambda x: lower < x < highest).any()
                if overlap:
                    params = timer.lines[col].get_line_info()
                    line = self.chart.create_line(
                        price_line=False, price_label=False, **params)
                    line.set_line_info(**params)
                    line.set(data[["time", col]])
                    lines.update({col: line})
        timer.restart(lines)
        return timer

    def _reload_sub(self, timer: Timer):
        """重新加载副图指标"""
        self.qtimer_explorer.chart_num += 1
        subchart = self.chart.create_subchart(
            'bottom', sync=True)
        subchart._key = self.qtimer_explorer.chart_num
        subchart.legend(True, **self.sub_legend_params(timer.indname))
        self.qtimer_explorer.charts.update(
            {self.qtimer_explorer.chart_num: subchart})
        indcls = timer.indcls
        indname = timer.indname
        params = timer._params
        kline = self.ContractDataSet.get_data(timer.follow)
        indicator = getattr(indcls(kline), indname)
        data = indicator(**params)
        lower, highest = kline.low.min(), kline.high.max()
        lines: dict = {}
        for i, col in enumerate(data.columns):
            if i:
                overlap = data[col].apply(lambda x: lower < x < highest).any()
                if not overlap:
                    params = timer.lines[col].get_line_info()
                    line = subchart.create_line(
                        price_line=False, price_label=False, **params)
                    line.set_line_info(**params)
                    line.set(data[["time", col]])
                    lines.update({col: line})
        subchart.name = indname
        timer.restart(lines)
        subchart._qtimer = timer
        return subchart

    def create_subchart(self, data: pd.DataFrame, indcls: Callable, indname: str, params: dict, doc: str) -> dict[str, Line]:
        """创建副图指标"""
        params = {}
        if self.qtimer_explorer.subcharts:
            key = list(self.qtimer_explorer.subcharts.keys())[0]
            subchart = self.qtimer_explorer.subcharts.pop(key)
            self.qtimer_explorer.charts.update({key: subchart})
            self.qtimer_explorer.charts = dict(
                sorted(self.qtimer_explorer.charts.items(), key=lambda x: x[0]))
        else:
            self.qtimer_explorer.chart_num += 1
            subchart = self.chart.create_subchart(
                'bottom', sync=True)
            subchart._key = self.qtimer_explorer.chart_num
            subchart.legend(True, **self.sub_legend_params(indname))
            self.qtimer_explorer.charts.update(
                {self.qtimer_explorer.chart_num: subchart})
            self.setChartStyle(qconfig.theme == Theme.DARK, subchart)
        lines: dict = {}
        subchart.name = indname
        subchart.chart_ind_color = get_colors()
        for i, col in enumerate(data.columns):
            if i:
                color = next(subchart.chart_ind_color)
                style = 'solid'
                width = 2
                line = subchart.create_line(
                    col, color=color, style=style, width=width, price_line=False, price_label=False)
                line.set_line_info(col, color, style, width)
                line.set(data[["time", col]])
                lines.update({col: line})
        subchart._qtimer = Timer(
            self, subchart._key, indcls, indname, lines, deepcopy(params), doc)
        self.ContractDataSet.params_lenght = subchart._qtimer.max_params_lenght
        self._resizes()

    def delete_subchart(self, index: int):
        """删除指标副图"""
        chart = self.qtimer_explorer.charts.pop(index)
        chart._qtimer.stop()
        for line in chart._lines:
            line.delete()
        self.qtimer_explorer.subcharts.update({index: chart})
        self.qtimer_explorer.charts = dict(
            sorted(self.qtimer_explorer.charts.items(), key=lambda x: x[0]))
        self.qtimer_explorer.subcharts = dict(
            sorted(self.qtimer_explorer.subcharts.items(), key=lambda x: x[0]))
        self._resizes()

    def deltet_main_indicator(self, qtimer: Timer):
        qtimer.stop()
        [line.delete() for _, line in qtimer.lines.items()]
        self.chart._qtimers.pop(qtimer.dict_name)
        new_qtimers = {}
        for i, (_, v) in enumerate(self.chart._qtimers.items()):
            name = f"{v.indname}_{i}"
            v.id = i
            new_qtimers.update({name: v})
        self.chart._qtimers = new_qtimers

    @property
    def QtChartQWidget(self):
        """QtChart对应widget窗口"""
        return self.chart.get_webview()

    def setChartStyle(self, dark=True, chart: AbstractChart = None):
        """更换风格"""
        chart = chart if chart else self.chart
        if dark:
            chart.layout(background_color='rgb(6, 6, 6)', text_color='rgb(249, 249, 249)', font_size=12,
                         font_family='Microsoft YaHei')  # 'Helvetica')
            chart.grid(color="rgb(26, 26, 26)")
            # params={**self.legend_params,"color":'rgb(249, 249, 249)'}

        else:

            chart.layout(background_color='rgb(249, 249, 249)', text_color='rgb(6, 6, 6)', font_size=12,
                         font_family='Microsoft YaHei')  # 'Helvetica')
            chart.grid(color="rgb(229, 229, 229)")
            # params={**self.legend_params,"color":'rgb(6, 6, 6)'}
        chart.legend(True, **(self.main_legend_params if chart ==
                     self.chart else self.sub_legend_params(chart.name)))

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        c = 255 if isDarkTheme() else 0
        pen = QPen(QColor(c, c, c, 60))
        pen.setCosmetic(True)
        painter.setPen(pen)
        # painter.setPen(QColor(60, 60, 60, 15) if isDarkTheme() else QColor(
        #     215, 215, 215, 15))  # , QColor(60, 60, 60))  # Qt.grey)
        # painter.drawRect(1, 1, self.width(), 0.5)
        # painter.drawRect(1, self.height()-2, self.width(), 0.5)
        painter.drawRect(1, 1, self.width()-2, self.height()-2)


class KlineTimer(QTimer):
    def __init__(self, parent: LightChartWidget, name: str = "",  indcls: Callable = None, params: dict = {}) -> None:
        super().__init__(parent)
        self.LightChartWidget = parent
        self.setObjectName(name)
        self.name = name
        self.indcls = indcls
        self.params = params


class Timer(QTimer):
    def __init__(self, parent: LightChartWidget, id: int, indcls: Callable, indname: str, lines: dict[str, Line], params: dict, doc: str) -> None:
        super().__init__(parent)
        self.LightChartWidget = parent
        self.setObjectName(indname)
        self.id = id
        self.indcls = indcls
        self.indname = indname
        self.lines = lines
        self._follow: bool = True
        self.setting: bool = False
        # 指标参数
        self.params = params
        self.doc = doc
        self.func: Callable = parent.timer_func
        self._reload_indicator: Callable = parent._reload_indicator
        for k, v in inspect.signature(getattr(indcls, indname)).parameters.items():
            if k not in self.params and k not in ["self", "kwargs"]:
                self.params.update({k: v.default})
        func = partial(self.func, indcls=self.indcls,
                       indname=self.indname, lines=self.lines, params=self._params)
        self.timeout.connect(func)
        self.start(0)

    @property
    def follow_kline(self) -> bool:
        return self.LightChartWidget.follow_kline

    @property
    def follow(self) -> bool:
        return self._follow

    @follow.setter
    def follow(self, value: bool) -> None:
        self._follow = value

    @property
    def indwindow_params(self) -> dict:
        """指标窗口参数"""
        if self.follow_kline:
            return {**self.params, "follow": self._follow}
        return self.params

    @property
    def _params(self) -> dict:
        """指标参数"""
        if self.follow_kline:
            return {**self.params, "follow": self._follow, "light_chart": True}
        return {**self.params, "light_chart": True}

    @property
    def max_params_lenght(self) -> int:
        d = [v for _, v in self.params.items() if isinstance(v, int)]
        return max(d) if d else 100

    def set_line_info(self, name, color, style, width):
        if name in self.lines:
            self.setting = True
            self.lines[name].set_line_info(name, color, style, width)

    def get_line_info(self, name):
        if name in self.lines:
            self.setting = True
            return self.lines[name].get_line_info()

    def replace_params(self, params: Optional[dict] = {}):
        """重载"""
        if params:
            self.params = {**self.params, **params}
        func = partial(self.func, indcls=self.indcls,
                       indname=self.indname, lines=self.lines, params=self._params)
        if self.isActive():
            self.stop()
        self.timeout.disconnect()
        self._reload_indicator(self.indcls, self.indname,
                               self.lines, self._params)
        self.timeout.connect(func)
        self.start(0)

    def restart(self, lines):
        """指标替换"""
        self.lines = lines
        self.replace_params()

    @property
    def dict_name(self):
        return f"{self.indname}_{self.id}"

    def codesource(self) -> str:
        from minibt.ta import BtFunc, pta
        for v in [BtFunc, pta]:
            try:
                return inspect.getsource(getattr(v, self.indname))
            except:
                ...
        return ""


class AppCard(CardWidget):
    """ App card """

    def __init__(self, key, value, func: Callable, index: int, parent=None):
        super().__init__(parent)
        # self.iconWidget = IconWidget(icon)
        self.titleLabel = BodyLabel(key, self)
        # self.contentLabel = CaptionLabel(content, self)
        self.edit = LineEdit(self)  # PushButton('打开', self)
        self.edit.setText(str(value))
        self.edit.setAlignment(Qt.AlignCenter)
        self.edit.textChanged.connect(
            partial(func, default=str(value), index=index))
        # self.moreButton = TransparentToolButton(FluentIcon.MORE, self)

        self.hBoxLayout = QHBoxLayout(self)
        self.vBoxLayout = QVBoxLayout()

        self.setFixedHeight(self.edit.height()+8)
        # self.iconWidget.setFixedSize(48, 48)
        # self.contentLabel.setTextColor("#606060", "#d2d2d2")
        self.edit.setMinimumWidth(120)

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


class IndicatorParamsWindow(FluentWindow):
    def __init__(self, object: Timer | LightChartWidget, ContractDataSet: ContractDataSet):
        super().__init__(parent=None)
        self.is_qtimer = isinstance(object, Timer)
        if self.is_qtimer:
            indname = object.indname
            doc = object.doc
        else:
            indname = object.candles_style
            doc = object.candles_func.__doc__

        # self.setTitleBar(FluentTitleBar(self))
        # self.titleBar.resize(200, 32)
        # self.titleBar.setFixedHeight(32)
        self.titleBar.setTitle(indname)
        self.titleBar.setIcon(Icons.line_chart_line())
        self.titleBar.titleLabel.setToolTip(doc)
        self.hBoxLayout.removeWidget(self.navigationInterface)
        self.navigationInterface.deleteLater()
        self.hBoxLayout.removeWidget(self.stackedWidget)
        self.stackedWidget.deleteLater()
        self.hBoxLayout.removeItem(self.widgetLayout)
        self.widgetLayout.deleteLater()
        # self.hBoxLayout = QHBoxLayout(self)
        height = self.titleBar.maxBtn.height()
        vlayout = QVBoxLayout()
        vlayout.setSpacing(2)
        vlayout.setContentsMargins(0, 0, 0, 0)
        vlayout.setAlignment(Qt.AlignTop)

        self.titleBar.buttonLayout.removeWidget(self.titleBar.maxBtn)
        self.titleBar.maxBtn.deleteLater()
        self.titleBar.buttonLayout.removeWidget(self.titleBar.minBtn)
        self.titleBar.minBtn.deleteLater()
        # self.titleBar.titleLabel.setText(self.tr(indname))
        # self.titleBar.titleLabel.setToolTip(doc)
        # self.titleBar.iconLabel.setPixmap(
        #     Icons.line_chart_line().pixmap(self.titleBar.iconLabel.size()))
        self.setWindowFlags(Qt.MSWindowsFixedSizeDialogHint |
                            Qt.WindowStaysOnTopHint)

        self._object = object
        self.ContractDataSet = ContractDataSet
        self.edits: list[LineEdit] = []

        params = object.indwindow_params if self.is_qtimer else self.ContractDataSet.candles_params
        self.is_changeds = [False,]*len(params)
        for i, (k, v) in enumerate(params.items()):
            card = AppCard(k, v, self._params_changed, i)
            self.edits.append(card.edit)
            vlayout.addWidget(card)
            # layout = QHBoxLayout()
            # label = BodyLabel(k)
            # label.setMinimumWidth(120)
            # label.setAlignment(Qt.AlignCenter)
            # # label.setStyleSheet("color:cyan")
            # layout.addWidget(label)
            # lineEdit = LineEdit(self)
            # self.edits.append(lineEdit)
            # lineEdit.setMinimumWidth(120)
            # lineEdit.setAlignment(Qt.AlignCenter)
            # lineEdit.setText(str(v))
            # lineEdit.setClearButtonEnabled(True)
            # layout.addSpacing(10)
            # layout.addWidget(lineEdit)
            # layout.setContentsMargins(10, 10, 10, 10)
            # vlayout.addLayout(layout)
            # lineEdit.textChanged.connect(self._params_changed)
        # _vlayout.addLayout(vlayout)
        # _vlayout.setContentsMargins(10, height, 0, 0)
        self.hBoxLayout.addLayout(vlayout)
        self.hBoxLayout.setContentsMargins(5, height, 5, 5)
        self.titleBar.setFixedHeight(height)
        # self.widgetLayout.setContentsMargins(0, height, 0, 0)
        self.adjustSize()
        # self.setStyleSheet("background: rgb(32, 32, 32)" if isDarkTheme(
        # ) else "background: rgb(243, 243, 243)")
        # (243, 243, 243), QColor(32, 32, 32)
        # StyleSheet.NAVIGATION_VIEW_INTERFACE.apply(self)

    # def show_doc(self):
    #     class DOC(QWidget):
    #         def __init__(self, parent: QWidget | None = ..., timer: Timer = None) -> None:
    #             super().__init__(parent)
    #             layout = QVBoxLayout(self)
    #             label = SubtitleLabel(self.tr(timer.indname), self)
    #             edit = TextEdit(self)
    #             edit.setText(timer.doc)
    #             layout.addWidget(label)
    #             layout.addWidget(edit)
    #             self.adjustSize()
    #     self.dowwindow = DOC(self.FuturesInterface, self.qtimer)
    #     self.dowwindow.show()

    def _params_changed(self, text: str, default: str, index: int):
        """参数是否有更换"""
        self.is_changeds[index] = text == default

    def __get_params(self,  value: str, default: Any):
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

    def closeEvent(self, e):
        """关闭窗口更换参数"""
        if any(self.is_changeds):
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
        return super().closeEvent(e)

    def keyPressEvent(self, even) -> None:
        """按下确定键关闭窗口"""
        if even.key() == Qt.Key_Enter:
            self.close()
        return super().keyPressEvent(even)


class QtimerExplorer(object):
    """qtimer指标管理器"""

    def __init__(self, parent: LightChartWidget):
        self.light_chart_widget = parent
        self._init()

    def _init(self):
        self.chart_num: int = 0
        setattr(self.chart, "_qtimers", dict())
        self._kline_qtimer: Timer = None
        self.create_kline_timer()
        # {0:QtChart,1:AbstractChart,2:AbstractChart...}
        # QtChart->_qtimers:(dict[str,Timer])->{indname_id:_qtimer}
        # AbstractChart->_qtimer：(Timer)
        self._charts: dict[int, QtChart] = {}
        self._charts.update({self.chart_num: self.chart})
        # {..,3:AbstractChart,...}
        self._subcharts: dict[int, AbstractChart] = {}

    @property
    def chart(self) -> QtChart:
        """主图QtChart"""
        return self.light_chart_widget.chart

    @property
    def kline_qtimer(self) -> Timer:
        """K线qtimer"""
        return self._kline_qtimer

    @property
    def charts(self) -> dict[int, QtChart]:
        """所有QtChart,包括主副图"""
        return self._charts

    @charts.setter
    def charts(self, value: dict):
        self._charts = value

    @property
    def subcharts(self) -> dict[int, AbstractChart]:
        """隐藏的副图AbstractChart"""
        return self._subcharts

    @subcharts.setter
    def subcharts(self, value: dict):
        self._subcharts = value

    @property
    def subchart_ind_qtimers(self) -> list[Timer]:
        """副图指标所有qtimer"""
        return [v._qtimer for v in list(self._charts.values())[1:]]

    @property
    def main_ind_qtimer(self) -> dict[str, Timer]:
        """主图指标qtimer"""
        return self.chart._qtimers

    @property
    def ishasindictor(self) -> bool:
        return len(self._charts) > 1 or self.chart._qtimers

    def create_kline_timer(self, time=0):
        """k线qtimer"""
        if self._kline_qtimer and self._kline_qtimer.isActive():
            self._kline_qtimer.stop()
            self._kline_qtimer.disconnect()
        self._kline_qtimer = QTimer(self.light_chart_widget)
        self._kline_qtimer.timeout.connect(
            self.light_chart_widget.kline_update)
        self._kline_qtimer.start(time)

    def stop_qtimer(self):
        """停止所有qtimer"""
        if self._kline_qtimer:
            self._kline_qtimer.stop()
        for _, v in self.main_ind_qtimer.items():
            v.stop()
        for v in self.subchart_ind_qtimers:
            v.stop()

    def start_qtimer(self):
        """开始所有qtimer"""
        if self._kline_qtimer:
            self._kline_qtimer.start(0)
        for _, v in self.main_ind_qtimer.items():
            v.start(0)
        for v in self.subchart_ind_qtimers:
            v.start(0)

    def restart(self):
        """qtimer重新启动"""
        if self._kline_qtimer:
            self._kline_qtimer.start(0)
        for _, v in self.main_ind_qtimer.items():
            v.replace_params()
        for v in self.subchart_ind_qtimers:
            v.replace_params()

    def replace_qtimer(self, parent: LightChartWidget, qtimers: dict[int, Timer], subtimers: list[Timer]):
        """用于加载图表画图工具

        Args:
            parent (LightChartWidget): widget
            qtimers (dict[int, Timer]): 主图qtimer
            subtimers (list[Timer]): 副图qtimer
        """
        self.light_chart_widget = parent
        self.chart_num = 0
        setattr(self.chart, "_qtimers", dict())
        self._kline_qtimer: Timer = None
        self.create_kline_timer()
        self._charts: dict[int, QtChart] = {}
        self._charts.update({self.chart_num: self.chart})
        self._subcharts: dict[int, QtChart] = {}
        # self.chart._qtimers=qtimers
        for _, v in qtimers.items():
            timer = self.light_chart_widget._reload_main(v)
            self.chart._qtimers.update({f"{v.indname}_{v.id}": timer})
        for v in subtimers:
            subchart = self.light_chart_widget._reload_sub(v)
            self._charts.update({self.chart_num: subchart})
        self.light_chart_widget._resizes()


class MultiCycleButton(CheckableMenu):
    def __init__(self, title="", parent=None, indicatorType=MenuIndicatorType.CHECK):
        super().__init__(title, parent, indicatorType)

    def _onItemClicked(self, item):
        action: Action = item.data(Qt.UserRole)
        if action not in self._actions or not action.isEnabled():
            return

        if self.view.itemWidget(item) and not action.property('selectable'):
            return
        if action.property('canHide'):
            self._hideMenu(False)

            if not self.isSubMenu:
                action.trigger()
                return

            # close parent menu
            self._closeParentMenu()
            action.trigger()
            return
        action.trigger()


class Window(FramelessWindow):

    def __init__(self):
        super().__init__()
        self.setTitleBar(StandardTitleBar(self))


# class BottomInterface(QWidget):
#     def __init__(self, parent: QWidget | None = ...) -> None:
#         super().__init__(parent)
#         layout=QVBoxLayout(self)
#         layout.addLayout(self.create_interface_bar())


#     def create_interface_bar(self):
#         layout=QHBoxLayout()
#         for i in range(5):
#             layout.addWidget(PillPushButton(f"test{i}",self))
#         layout.setSpacing(1)
#         layout.addWidget(PillPushButton(f"test{i+1}",self))
#         layout.setContentsMargins(0,0,0,0)
#         return layout
#     def create_stackWidget(self):
#         self.stackewidget=QStackedWidget(self)
#         self.
