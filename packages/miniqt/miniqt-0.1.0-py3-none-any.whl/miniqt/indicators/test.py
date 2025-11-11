from qtpy.QtWebEngineWidgets import *
from PyQt5.QtWidgets import QWidget, QHBoxLayout
# from qtpy.QtWebChannel import *
from qtpy.QtCore import QUrl
from pathlib import Path


class MonacoWidget_(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        layout = QHBoxLayout(self)
        layout.addWidget(MonacoWidget(self))
        layout.setContentsMargins(10, 0, 10, 0)
        self.adjustSize()


class MonacoWidget(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        filename = Path(__file__).parent / 'index.html'
        self.load(QUrl.fromLocalFile(
            r'D:\owen\owenrl\minibt\Plots\bokeh_plot.html'))
