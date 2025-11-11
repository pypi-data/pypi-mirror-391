
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget,  QVBoxLayout, QSizePolicy, QActionGroup
from qfluentwidgets import (CommandBar, setFont, MenuIndicatorType, CheckableMenu,
                            Action, TransparentDropDownPushButton, isDarkTheme)
from qfluentwidgets import FluentIcon as FIF
# from .chart_interface import ChartSplitWidget
from ..monaco import MonacoWidget
from qfluentwidgets import FluentIcon as FIF
# https://aydk.site/example/layout.html


class MonacoEditor(QWidget):
    def __init__(self, parent=None, code: str = ""):
        super().__init__(parent=parent)
        hlayout = QVBoxLayout(self)
        self.toolbar = self.createCommandBar()
        self.editor = MonacoWidget()
        self.editor.setText(code)
        # self.editor.setTheme("vs-dark")
        self.settheme()
        self.editor.setLanguage("python")
        hlayout.addWidget(self.toolbar)
        hlayout.addWidget(self.editor)
        hlayout.setContentsMargins(0, 0, 0, 0)

    def settheme(self):
        self.editor.setTheme("vs-dark" if isDarkTheme() else "vs")

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
