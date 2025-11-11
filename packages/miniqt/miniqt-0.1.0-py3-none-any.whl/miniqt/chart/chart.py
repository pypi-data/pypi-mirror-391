from __future__ import annotations
from PyQt5 import QtGui
import pandas as pd
from lightweight_charts.widgets import QtChart
from minibt import FILED, np, dataframe
from PyQt5.QtWidgets import QMdiSubWindow, QSizePolicy, QActionGroup, QVBoxLayout, QWidget, QHBoxLayout, QMdiArea
from PyQt5.QtCore import QEvent, QObject, QThread, pyqtSignal, QTimer, Qt
from qfluentwidgets.common.config import qconfig, Theme
from qfluentwidgets import RoundMenu, setFont, Action, CommandBar, CheckableMenu, TransparentDropDownPushButton, MenuIndicatorType
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView
from minibt import dataframe
# from .indicators.ind_interface import Ind_Card
from ..futures.ind_interface import Ind_Card


def on_new_bar(chart):
    print('New bar event!')


def on_timeframe_selection(chart):
    print(f'Selected timeframe of {chart.topbar["timeframe"].value}')


def on_horizontal_line_move(chart, line):
    print(f'Horizontal line moved to: {line.price}')


class ChartWidget(QWidget):
    """
    parent:
    subwidget:QtChartQWidget
    """

    def __init__(self, parent, ContractSet=None) -> None:
        super().__init__(parent)
        self.parent_widget = parent
        # self.ContractSet=ContractSet
        self.adjustSize()
        layout = QHBoxLayout(self)
        self._chart = LightWeightCharts(parent.parent_widget, ContractSet)
        layout.addWidget(self._chart.QtChartQWidget)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setMouseTracking(True)

        self._chart.QtChartQWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self._chart.QtChartQWidget.customContextMenuRequested.connect(
            self.create_chart_menu)
        # self.mouseDoubleClickEvent = lambda self, a0: print("WeightCharts_")
        # self.chart.QtChartQWidget.mouseDoubleClickEvent = lambda self, a0:
        # self.chart.QtChartQWidget.mouseDoubleClickEvent = lambda self, a0: QWebEngineView.mouseDoubleClickEvent(self.chart.QtChartQWidget,
        #                                                                                                         a0), print(self.chart.QtChartQWidget.parentWidget()), self.chart.QtChartQWidget.parentWidget().parent_widget.showfull_chart()

    # def mouseDoubleClickEvent(self, a0) -> None:

    #     # self.parent_widget.showfull_chart()
    #     print(self.parentWidget())
    #     return super().mouseDoubleClickEvent(a0)

        # def eventFilter(self, a0: QObject, a1: QEvent) -> bool:
        #     if a1.type() == QEvent.mouseDoubleClickEvent:
        #         self.parent_widget.showfull_chart()
        #     return super().eventFilter(a0, a1)

    def create_chart_menu(self, event):
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
        ikunMenu.addSeparator()
        if self.parent_widget.count < 9:
            logaction = Action("增加图表")
            logaction.triggered.connect(self.parent_widget.add_chart)
            ikunMenu.addAction(logaction)
        if self.parent_widget.count > 1:
            logaction1 = Action(
                '恢复' if self.parent_widget.is_showMaximized else "最大化")
            logaction1.triggered.connect(self.parent_widget.showfull_chart)
            ikunMenu.addAction(logaction1)
            logaction2 = Action("关闭图表")
            logaction2.triggered.connect(self.parent_widget.close_chart)
            ikunMenu.addAction(logaction2)
        ikunMenu.exec_(QCursor.pos())


class ChartWidget_(QWidget):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        # self.parent_widget = parent
        layout = QHBoxLayout(self)
        self.chart = LightWeightCharts(self)
        layout.addWidget(self.chart.QtChartQWidget)
        layout.setContentsMargins(0, 0, 0, 0)
        self.adjustSize()


class LightWeightCharts:
    def __init__(self, parent: QWidget = None, ContractSet=None) -> None:
        self.parent_widget = parent
        self.ContractSet = ContractSet
        # self.stock: pd.DataFrame = pd.read_csv(
        #     r"D:\owen\owenrl\minibt\miniqt\chart\data.csv")
        self.init_chart()

    def init_chart(self):
        self.kline = self.ContractSet.kline
        self.tick = self.ContractSet.tick
        df = self.kline.copy()
        df['time'] = df.datetime  # pd.to_datetime(df.datetime)
        df = df[['time', 'open', 'high', 'low',
                 'close', 'volume']]
        self.charts = []
        self.chart = QtChart(self.parent_widget, toolbox=True)
        self.charts.append(self.chart)
        # self.chart.get_webview().mouseDoubleClickEvent = lambda self, a0: print("webview")
        # self.chart.get_webview().setMouseTracking(True)
        # self.chart.layout(background_color='rgb(249, 249, 249)', text_color='rgb(6, 6, 6)', font_size=14,
        #                  font_family = 'Microsoft YaHei')  # 'Helvetica')
        # self.chart.grid(color="rgb(229, 229, 229)")

        # self.chart.candle_style(up_color='#00ff55', down_color='#ed4807',
        #                         border_up_color='#FFFFFF', border_down_color='#FFFFFF',
        #                         wick_up_color='#FFFFFF', wick_down_color='#FFFFFF')

        # self.chart.volume_config(up_color='#00ff55', down_color='#ed4807')

        # self.chart.watermark('1D', color='rgba(180, 180, 240, 0.7)')

        # self.chart.crosshair(mode='normal', vert_color='#FFFFFF', vert_style='dotted',
        #                      horz_color='#FFFFFF', horz_style='dotted')

        # self.chart.legend(visible=True, font_size=14, color='rgb(6, 6, 6)')
        self.chart.webview.setContextMenuPolicy(Qt.NoContextMenu)
        # self.chart.web_channel.set
        self.chart.legend(True, text=self.ContractSet.symbol)
        # self.chart.events.new_bar += on_new_bar
        # lines = []
        # for i in range(1, 20):
        #     lines.append(self.chart.create_line(
        #         f'ma{i*10}', price_line=False, price_label=False))
        #     data_dict = pd.DataFrame({'time': df.time,
        #                               f'ma{i*10}': df.close.rolling(i*10).mean()})
        #     lines[-1].set(data_dict)

        # lines = self.chart.lines()
        # if lines:
        #     for line in lines:
        #         line.delete_legend()
        self.create_subchart()
        self.add_indicator(**dict(name="bbands", light_chart=True))
        # Literal['left', 'right', 'top', 'bottom']

        self.chart.set(df)
        self.setChartStyle(qconfig.theme == Theme.DARK)

    def data_loop(self, api):
        # print(self.chart._last_bar['time']-self.kline.datetime.iloc[-1])
        if api.is_changing(self.kline, "datetime"):
            for i in range(-2, 0):
                self.chart.update(self.kline.iloc[i])
        series = self.kline.iloc[-1][FILED.DV]
        series['price'] = self.tick.iloc[-1]["last_price"]
        series.index = FILED.TICK
        self.chart.update_from_tick(series)
        # ema10 = self.ema10.iloc[-1]
        # ema10['time'] = series["time"]
        # self.line.update(ema10)

    def add_indicator(self, **kwargs):
        name = kwargs.pop('name')
        kwargs.update(dict(light_chart=True))
        data = getattr(dataframe(self.kline.copy()[['datetime', 'open', 'high', 'low',
                                                    'close', 'volume']]), name)(**kwargs)[["time",  "bb_lower",  "bb_mid",  "bb_upper"]]
        for i, col in enumerate(data.columns):
            if i:
                line = self.chart.create_line(
                    col, price_line=False, price_label=False)
                line.set(data[["time", col]])
            # line.delete_legend()

    def __get_sizes(self):
        num_chart = len(self.charts)
        if num_chart > 1:
            num = round(1./(3+(num_chart-1)), 3)
            return [num if i else 1.-(num_chart-1)*num for i in range(num_chart)]
        else:
            return 1,

    def create_subchart(self):
        subchart = self.chart.create_subchart(
            'bottom', sync=True)
        subchart.legend(True)

        line1 = subchart.create_line(
            'ma', price_line=False, price_label=False)
        line1.set(pd.DataFrame(
            dict(time=self.kline.datetime, ma=self.kline.close.rolling(10).mean())))
        self.charts.append(subchart)
        num = len(self.charts)-1
        for i, (chart, size) in enumerate(zip(self.charts, self.__get_sizes())):
            chart.resize(1, size)
            if i == num:
                chart.time_scale(visible=True)
            else:
                chart.time_scale(visible=False)

    @property
    def QtChartQWidget(self):
        return self.chart.get_webview()

    def setChartStyle(self, dark=True):
        if dark:
            self.chart.layout(background_color='rgb(6, 6, 6)', text_color='rgb(249, 249, 249)', font_size=14,
                              font_family='Microsoft YaHei')  # 'Helvetica')
            self.chart.grid(color="rgb(26, 26, 26)")
            self.chart.legend(visible=True, font_size=14,
                              color='rgb(249, 249, 249)')
        else:

            self.chart.layout(background_color='rgb(249, 249, 249)', text_color='rgb(6, 6, 6)', font_size=14,
                              font_family='Microsoft YaHei')  # 'Helvetica')
            self.chart.grid(color="rgb(229, 229, 229)")
            self.chart.legend(visible=True, font_size=14, color='rgb(6, 6, 6)')


class ChartMdiAreaWidget(QWidget):
    def __init__(self, parent: QWidget = None, ContractSet=None) -> None:
        super().__init__(parent)
        self.parent_widget = parent
        self.ContractSet = ContractSet
        self.initUI()
        # self.setMouseTracking(True)
        # self.parentWidget().mouseDoubleClickEvent = lambda self, a0: print(self)

    def initUI(self):
        # 将窗口设置为动图大小
        self.count = 0
        self.is_showMaximized = False
        self.adjustSize()
        layout = QVBoxLayout(self)
        self.ind_card = Ind_Card(self)
        self.ind_card.setObjectName('ind_card')
        self.tool_bar = self.createCommandBar()
        self.mdi = QMdiArea()
        self.mdi.setActivationOrder(
            QMdiArea.ActivationHistoryOrder)  # StackingOrder)
        layout.addWidget(self.tool_bar)
        layout.addWidget(self.mdi)
        layout.setContentsMargins(0, 0, 0, 0)
        self.add_chart()
        # self.mdi.mouseDoubleClickEvent = lambda self, a0: print("mid")
        # self.mdi.setMouseTracking(True)

    def add_chart(self):
        self.count = self.count + 1
        # 创建一个子窗口
        sub = QMdiSubWindow()
        sub.setWindowFlag(Qt.FramelessWindowHint)
        # sub.mouseDoubleClickEvent = lambda self, a0: print("sub")
        # sub.setMouseTracking(True)
        # 为子窗口添加一个TextEdit控件
        sub.setWidget(ChartWidget(self, self.ContractSet))
        self.mdi.addSubWindow(sub)
        self.mdi.tileSubWindows()
        sub.show()

    def close_chart(self):
        if self.count > 1:
            if self.is_showMaximized:
                self.showfull_chart()
            self.mdi.removeSubWindow(self.mdi.currentSubWindow())
            self.mdi.tileSubWindows()
            self.count -= 1
            if self.count == 1:
                self.current_chart_widget._chart.chart.time_scale(visible=True)

    def showfull_chart(self):
        if self.count > 1:
            if self.is_showMaximized:
                self.mdi.tileSubWindows()
            else:
                self.mdi.currentSubWindow().showMaximized()
            self.is_showMaximized = not self.is_showMaximized

    @property
    def current_chart_widget(self) -> ChartWidget:
        return self.mdi.currentSubWindow().widget()

    @property
    def current_subwindow(self) -> QMdiSubWindow:
        return self.mdi.currentSubWindow()

    @property
    def chart(self) -> LightWeightCharts:
        return self.current_chart_widget._chart

    @property
    def chart_qWidget(self) -> QWebEngineView:
        return self.chart.QtChartQWidget

    # def mouseDoubleClickEvent(self, a0) -> None:

    #     print("ChartMdiAreaWidget")
    #     return super().mouseDoubleClickEvent(a0)
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
