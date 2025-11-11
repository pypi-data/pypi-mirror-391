import typing
from PyQt5 import QtCore
from PyQt5.QtWidgets import QTextEdit, QWidget, QVBoxLayout, QAction, QMdiArea, QMdiSubWindow, QHBoxLayout
from qfluentwidgets import RoundMenu, PushButton, FluentWindow, SplitFluentWindow, MSFluentWindow
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt
from ..chart.chart import WeightCharts


class DemoWin(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.initUI()

    def initUI(self):
        # 将窗口设置为动图大小
        self.count = 0
        self.adjustSize()
        layout = QVBoxLayout(self)
        menubar = QWidget()
        menubar.setFixedHeight(40)
        menubar_layout = QHBoxLayout(menubar)
        self.butoon = PushButton("SubWin")
        self.butoon.setMaximumWidth(100)
        self.butoon.clicked.connect(lambda: self.createMenu())
        menubar_layout.addWidget(self.butoon, alignment=Qt.AlignLeft)
        self.mdi = QMdiArea()
        #
        self.mdi.setActivationOrder(
            QMdiArea.ActivationHistoryOrder)  # StackingOrder)
        self.mdi.setTabsMovable(True)
        layout.addWidget(menubar)
        layout.addWidget(self.mdi)
        layout.setContentsMargins(0, 0, 0, 0)
        # bar = self.menuBar()
        # file = bar.addMenu("SubWin")
        # file.addAction("New")
        # file.addAction("Cascade")
        # file.addAction("Tiled")

        # file.triggered.connect(self.windowAction)

        # self.setCentralWidget(self.mdi)

        # 添加窗口标题
        # self.setWindowTitle("SubWindowDemo")

    def createMenu(self):
        menu = RoundMenu(parent=self)

        # add actions
        logaction = QAction("New")
        menu.addAction(logaction)

        logaction1 = QAction("Cascade")
        menu.addAction(logaction1)

        logaction2 = QAction("Tiled")
        menu.addAction(logaction2)

        logaction3 = QAction("Test")
        menu.addAction(logaction3)
        menu.triggered.connect(self.windowAction)

        # menu.addAction(Action(FIF.CUT, self.tr('Cut')))

        # # add sub menu
        # submenu = RoundMenu(self.tr("Add to"), self)
        # submenu.setIcon(FIF.ADD)
        # submenu.addActions([
        #     Action(FIF.VIDEO, self.tr('Video')),
        #     Action(FIF.MUSIC, self.tr('Music')),
        # ])
        # menu.addMenu(submenu)

        # # add actions
        # menu.addActions([
        #     Action(FIF.PASTE, self.tr('Paste')),
        #     Action(FIF.CANCEL, self.tr('Undo'))
        # ])

        # # add separator
        # menu.addSeparator()
        # menu.addAction(QAction(self.tr('Select all')))

        # # insert actions
        # menu.insertAction(
        #     menu.actions()[-1], Action(FIF.SETTING, self.tr('Settings')))
        # menu.insertActions(
        #     menu.actions()[-1],
        #     [
        #         Action(FIF.HELP, self.tr('Help')),
        #         Action(FIF.FEEDBACK, self.tr('Feedback'))
        #     ]
        # )
        # x = self.searchButton.width() - menu.width()
        pos = QCursor.pos()  # self.searchButton.pos()  # QPoint(x, self.searchButton.height())
        # pos.setX(pos.x()+45)
        # pos.setY(pos.y()+self.height()-5)
        self.butoon.mapToGlobal(pos)
        menu.exec(pos, ani=True)

    def windowAction(self, q):
        # 当点击菜单栏中的New时，新建一个子窗口
        if q.text() == "New":
            # 为子窗口计数
            self.count = self.count + 1
            # 创建一个子窗口
            sub = QMdiSubWindow()
            sub.setWindowFlag(Qt.FramelessWindowHint)
            # 为子窗口添加一个TextEdit控件
            sub.setWidget(WeightCharts(self))
            self.mdi.addSubWindow(sub)
            sub.show()
        # elif q.text() == "Cascade":  # 当点击菜单栏中的Cascade时，堆叠子窗口
        #     self.mdi.cascadeSubWindows()
        # elif q.text() == "Tiled":  # 当点击菜单栏中的Tiled时，平铺子窗口
            self.mdi.tileSubWindows()
        elif q.text() == "Cascade":
            self.mdi.currentSubWindow().showMaximized()
        elif q.text() == "Tiled":
            self.mdi.tileSubWindows()
        elif q.text() == "Test":
            self.mdi.removeSubWindow(self.mdi.currentSubWindow())
            # self.mdi.setTabsMovable(True)
