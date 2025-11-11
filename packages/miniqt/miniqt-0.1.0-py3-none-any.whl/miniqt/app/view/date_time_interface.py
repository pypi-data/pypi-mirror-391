# coding:utf-8
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from qfluentwidgets import DatePicker, TimePicker, AMTimePicker, ZhDatePicker, CalendarPicker, TextEdit

from .gallery_interface import GalleryInterface
from ..common.translator import Translator
from ..view.gallery_interface import ExampleCard
from ...chart.chart import ChartWidget
from ...monaco.monaco_widget import MonacoWidget
from ...futures.Editor import MonacoEditor


class DateTimeInterface(GalleryInterface):
    """ Date time interface """

    def __init__(self, parent=None):
        self.parent_widget = parent
        t = Translator()
        super().__init__(
            title=t.dateTime,
            subtitle='qfluentwidgets.components.time_picker',
            parent=parent
        )
        self.setObjectName('dateTimeInterface')

        # calendar picker
        self.addExampleCard(
            title=self.tr('A simple CalendarPicker'),
            # widget=WeightCharts(self),
            widget=CalendarPicker(self),
            sourcePath='https://github.com/zhiyiYo/PyQt-Fluent-Widgets/blob/master/examples/date_time/calendar_picker/demo.py'
        )

        # w = CalendarPicker(self)
        w = QLabel(self)
        w.setText(
            "## Steel Ball Run \n * Johnny Joestar 🦄 \n * Gyro Zeppeli 🐴 ")
        # w.setDateFormat(Qt.TextDate)
        self.addExampleCard(
            title=self.tr('A CalendarPicker in another format'),
            widget=w,
            sourcePath='https://github.com/zhiyiYo/PyQt-Fluent-Widgets/blob/master/examples/date_time/calendar_picker/demo.py'
        )

        # date picker
        # monacoeditor = MonacoWidget(self)
        # monacoeditor.setFixedHeight()
        self.addExampleCard(
            title=self.tr('A simple DatePicker'),
            widget=MonacoWidget(self),  # DatePicker(self),
            sourcePath='https://github.com/zhiyiYo/PyQt-Fluent-Widgets/blob/master/examples/date_time/time_picker/demo.py'
        )

        # self.addExampleCard(
        #     title=self.tr('A DatePicker in another format'),
        #     widget=ZhDatePicker(self),
        #     sourcePath='https://github.com/zhiyiYo/PyQt-Fluent-Widgets/blob/master/examples/date_time/time_picker/demo.py'
        # )

        # # AM/PM time picker
        # self.addExampleCard(
        #     title=self.tr('A simple TimePicker'),
        #     widget=AMTimePicker(self),
        #     sourcePath='https://github.com/zhiyiYo/PyQt-Fluent-Widgets/blob/master/examples/date_time/time_picker/demo.py'
        # )

        # # 24 hours time picker
        # self.addExampleCard(
        #     title=self.tr('A TimePicker using a 24-hour clock'),
        #     widget=TimePicker(self),
        #     sourcePath='https://github.com/zhiyiYo/PyQt-Fluent-Widgets/blob/master/examples/date_time/time_picker/demo.py'
        # )

        # # 24 hours time picker
        # self.addExampleCard(
        #     title=self.tr('A TimePicker with seconds column'),
        #     widget=TimePicker(self, True),
        #     sourcePath='https://github.com/zhiyiYo/PyQt-Fluent-Widgets/blob/master/examples/date_time/time_picker/demo.py'
        # )

        for widget in self.findChildren(ExampleCard):
            if isinstance(widget.widget, ChartWidget):
                widget.widget.setMinimumSize(
                    max(self.parent_widget.width()-200, 1200), max(self.parent_widget.height()-50, 600))
            if isinstance(widget.widget, MonacoEditor):
                widget.widget.setMinimumSize(
                    max(self.parent_widget.width()-200, 1200), max(self.parent_widget.height()-50, 600))
            # widget.card.hide()
