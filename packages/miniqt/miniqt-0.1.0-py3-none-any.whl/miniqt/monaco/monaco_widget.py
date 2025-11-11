from qtpy.QtCore import QObject, Signal, Slot, Property, QUrl, Qt
from qtpy.QtWebEngineWidgets import *
from qtpy.QtWebChannel import *

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSizePolicy,  QActionGroup
from qfluentwidgets import (CommandBar, setFont, MenuIndicatorType,
                            CheckableMenu, Action, TransparentDropDownPushButton,)
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import FluentIcon as FIF

from pathlib import Path
import json
# https://github.com/brijeshb42/monaco-themes/blob/master/themes/Monokai.json


class BaseBridge(QObject):
    initialized = Signal()
    sendDataChanged = Signal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.active = False
        self.queue = []

    def send_to_js(self, name, value):
        if self.active:
            data = json.dumps(value)
            self.sendDataChanged.emit(name, data)
        else:
            self.queue.append((name, value))

    @Slot(str, str)
    def receive_from_js(self, name, value):
        data = json.loads(value)
        self.setProperty(name, data)

    @Slot()
    def init(self):
        self.initialized.emit()
        self.active = True
        for name, value in self.queue:
            self.send_to_js(name, value)

        self.queue.clear()


class EditorBridge(BaseBridge):
    valueChanged = Signal()
    languageChanged = Signal()
    themeChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._value = ''
        self._language = ''
        self._theme = ''

    def getValue(self):
        return self._value

    def setValue(self, value):
        self._value = value
        self.valueChanged.emit()

    def getLanguage(self):
        return self._language

    def setLanguage(self, language):
        self._language = language
        self.languageChanged.emit()

    def getTheme(self):
        return self._theme

    def setTheme(self, theme):
        self._theme = theme
        self.themeChanged.emit()

    value = Property(str, fget=getValue, fset=setValue, notify=valueChanged)
    language = Property(str, fget=getLanguage,
                        fset=setLanguage, notify=languageChanged)
    theme = Property(str, fget=getTheme, fset=setTheme, notify=themeChanged)


index = Path(__file__).parent / 'index.html'

with open(index) as f:
    raw_html = f.read()


class MonacoPage(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, message, line, source):
        pass


class MonacoWidget(QWebEngineView):
    initialized = Signal()
    textChanged = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        page = MonacoPage(parent=self)
        self.setPage(page)

        filename = Path(__file__).parent / 'index.html'
        self.setHtml(raw_html, QUrl.fromLocalFile(filename.as_posix()))

        self._channel = QWebChannel(self)
        self._bridge = EditorBridge()

        self.page().setWebChannel(self._channel)
        self._channel.registerObject('bridge', self._bridge)

        self._bridge.initialized.connect(self.initialized)
        self._bridge.valueChanged.connect(
            lambda: self.textChanged.emit(self._bridge.value))

    def text(self):
        return self._bridge.value

    def setText(self, text):
        self._bridge.send_to_js('value', text)

    def language(self):
        return self._bridge.language

    def setLanguage(self, language):
        self._bridge.send_to_js('language', language)

    def theme(self):
        return self._bridge.theme

    def setTheme(self, theme):
        self._bridge.send_to_js('theme', theme)


# class MonacoEditor(QWidget):
#     def __init__(self, parent=None):
#         super().__init__(parent=parent)
#         hlayout = QVBoxLayout(self)
#         self.toolbar = self.createCommandBar()
#         self.editor = MonacoWidget()
#         self.editor.setText("FOX")
#         self.editor.setTheme("vs-dark")
#         self.editor.setLanguage("python")
#         hlayout.addWidget(self.toolbar)
#         hlayout.addWidget(self.editor)
#         hlayout.setContentsMargins(0, 0, 0, 0)

#     def createCommandBar(self):
#         # create actions
#         self.createTimeAction = Action(
#             FIF.CALENDAR, self.tr('Create Date'), checkable=True)
#         self.shootTimeAction = Action(
#             FIF.CAMERA, self.tr('Shooting Date'), checkable=True)
#         self.modifiedTimeAction = Action(
#             FIF.EDIT, self.tr('Modified time'), checkable=True)
#         self.nameAction = Action(FIF.FONT, self.tr('Name'), checkable=True)
#         self.actionGroup1 = QActionGroup(self)
#         self.actionGroup1.addAction(self.createTimeAction)
#         self.actionGroup1.addAction(self.shootTimeAction)
#         self.actionGroup1.addAction(self.modifiedTimeAction)
#         self.actionGroup1.addAction(self.nameAction)

#         self.ascendAction = Action(
#             FIF.UP, self.tr('Ascending'), checkable=True)
#         self.descendAction = Action(
#             FIF.DOWN, self.tr('Descending'), checkable=True)
#         self.actionGroup2 = QActionGroup(self)
#         self.actionGroup2.addAction(self.ascendAction)
#         self.actionGroup2.addAction(self.descendAction)

#         self.shootTimeAction.setChecked(True)
#         self.ascendAction.setChecked(True)

#         bar = CommandBar(self)
#         bar.setFixedHeight(30)
#         bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
#         bar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
#         bar.addActions([
#             Action(FIF.ADD, self.tr('Add')),
#             Action(FIF.ROTATE, self.tr('Rotate')),
#             Action(FIF.ZOOM_IN, self.tr('Zoom in')),
#             Action(FIF.ZOOM_OUT, self.tr('Zoom out')),
#         ])
#         bar.addSeparator()
#         bar.addActions([
#             Action(FIF.EDIT, self.tr('Edit'), checkable=True),
#             Action(FIF.INFO, self.tr('Info')),
#             Action(FIF.DELETE, self.tr('Delete')),
#             Action(FIF.SHARE, self.tr('Share'))
#         ])

#         # add custom widget
#         button = TransparentDropDownPushButton(
#             self.tr('Sort'), self, FIF.SCROLL)
#         button.setMenu(self.createCheckableMenu())
#         button.setFixedHeight(30)
#         setFont(button, 12)
#         bar.addWidget(button)

#         bar.addHiddenActions([
#             Action(FIF.SETTING, self.tr('Settings'), shortcut='Ctrl+I'),
#         ])
#         return bar

#     def createCheckableMenu(self, pos=None):
#         menu = CheckableMenu(
#             parent=self, indicatorType=MenuIndicatorType.RADIO)

#         menu.addActions([
#             self.createTimeAction, self.shootTimeAction,
#             self.modifiedTimeAction, self.nameAction
#         ])
#         menu.addSeparator()
#         menu.addActions([self.ascendAction, self.descendAction])

#         if pos is not None:
#             menu.exec(pos, ani=True)

#         return menu
