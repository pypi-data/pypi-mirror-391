# coding:utf-8
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPixmap, QPainter, QColor, QBrush, QPainterPath, QLinearGradient
from PyQt5.QtWidgets import QStyle, QWidget, QVBoxLayout, QLabel, QHBoxLayout
from qfluentwidgets.common.config import qconfig, Theme
from qfluentwidgets import ScrollArea, isDarkTheme, FluentIcon, LargeTitleLabel, PipsPager, PipsScrollButtonDisplayMode, HorizontalPipsPager, FlowLayout, PushButton, TransparentToolButton
from ..app.common.config import cfg, HELP_URL, REPO_URL, EXAMPLE_URL, FEEDBACK_URL
from ..app.common.icon import Icon, FluentIconBase
from .home import LinkCardView, LinkCard, SampleCardView
from ..app.common.style_sheet import StyleSheet
from ..app.components.link_card import LinkCardView as _LinkCardView


class _IndicatorsInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        layout = QVBoxLayout(self)
        # self.banner = BannerWidget(self)
        self.ind_card_ = IndicatorsInterface(self)
        self.page = Demo()
        # layout.addWidget(self.banner)
        layout.addWidget(self.ind_card_)
        layout.addWidget(self.page)
        layout.setContentsMargins(0, 0, 0, 0)


class Demo(QWidget):

    def __init__(self):
        super().__init__()
        # setTheme(Theme.DARK)
        # self.setStyleSheet('Demo{background:rgb(32,32,32)}')
        self.setFixedHeight(50)
        # self.vPager = VerticalPipsPager(self)
        self.hPager = HorizontalPipsPager(self)
        self.hPager.setMaximumWidth(200)

        # set the number of page
        self.hPager.setPageNumber(15)
        # self.vPager.setPageNumber(15)

        # set the number of displayed pips
        self.hPager.setVisibleNumber(8)
        self.hPager.setNextButtonDisplayMode(
            PipsScrollButtonDisplayMode.ALWAYS)
        self.hPager.setPreviousButtonDisplayMode(
            PipsScrollButtonDisplayMode.ALWAYS)

        # set the display mode of scroll button
        # self.vPager.setNextButtonDisplayMode(PipsScrollButtonDisplayMode.ALWAYS)
        # self.vPager.setPreviousButtonDisplayMode(PipsScrollButtonDisplayMode.ON_HOVER)
        self.first_button = PushButton("第一页", self)
        self.prev_button = PushButton("上一页", self)
        self.next_button = PushButton("下一页", self)
        self.last_button = PushButton("最后页", self)
        layout = QHBoxLayout(self)
        # layout.addSpacing(1)
        layout.addStretch(10)
        layout.addWidget(self.first_button)
        layout.addWidget(self.prev_button)
        layout.addWidget(self.hPager)
        layout.addWidget(self.next_button)
        layout.addWidget(self.last_button)
        # layout.addSpacing(1)
        layout.addStretch(10)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignVCenter)
        # self.layout().addWidget(self.vPager)

        # self.resize(500, 500)


class BannerWidget(QWidget):
    """ Banner widget """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setFixedHeight(336)

        self.vBoxLayout = QVBoxLayout(self)
        self.galleryLabel = QLabel('Fluent Gallery', self)
        self.banner = QPixmap(':/gallery/images/header1.png')
        self.linkCardView = _LinkCardView(self)

        self.galleryLabel.setObjectName('galleryLabel')

        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.setContentsMargins(0, 20, 0, 0)
        self.vBoxLayout.addWidget(self.galleryLabel)
        self.vBoxLayout.addWidget(self.linkCardView, 1, Qt.AlignBottom)
        self.vBoxLayout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        self.linkCardView.addCard(
            ':/gallery/images/logo.png',
            self.tr('Getting started'),
            self.tr('An overview of app development options and samples.'),
            HELP_URL
        )

        self.linkCardView.addCard(
            FluentIcon.GITHUB,
            self.tr('GitHub repo'),
            self.tr(
                'The latest fluent design controls and styles for your applications.'),
            REPO_URL
        )

        self.linkCardView.addCard(
            FluentIcon.CODE,
            self.tr('Code samples'),
            self.tr(
                'Find samples that demonstrate specific tasks, features and APIs.'),
            EXAMPLE_URL
        )

        self.linkCardView.addCard(
            FluentIcon.FEEDBACK,
            self.tr('Send feedback'),
            self.tr('Help us improve PyQt-Fluent-Widgets by providing feedback.'),
            FEEDBACK_URL
        )
        StyleSheet.HOME_INTERFACE.apply(self)

    def paintEvent(self, e):
        super().paintEvent(e)
        painter = QPainter(self)
        painter.setRenderHints(
            QPainter.SmoothPixmapTransform | QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)

        path = QPainterPath()
        path.setFillRule(Qt.WindingFill)
        w, h = self.width(), self.height()
        path.addRoundedRect(QRectF(0, 0, w, h), 10, 10)
        path.addRect(QRectF(0, h-50, 50, 50))
        path.addRect(QRectF(w-50, 0, 50, 50))
        path.addRect(QRectF(w-50, h-50, 50, 50))
        path = path.simplified()

        # init linear gradient effect
        gradient = QLinearGradient(0, 0, 0, h)

        # draw background color
        if not isDarkTheme():
            gradient.setColorAt(0, QColor(207, 216, 228, 255))
            gradient.setColorAt(1, QColor(207, 216, 228, 0))
        else:
            gradient.setColorAt(0, QColor(0, 0, 0, 255))
            gradient.setColorAt(1, QColor(0, 0, 0, 0))

        painter.fillPath(path, QBrush(gradient))

        # draw banner image
        pixmap = self.banner.scaled(
            self.size(), transformMode=Qt.SmoothTransformation)
        painter.fillPath(path, QBrush(pixmap))


class IndicatorsInterface(ScrollArea):
    """ Home interface """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        # self.banner = BannerWidget(self)
        self.view = QWidget(self)
        # layout = QVBoxLayout(self)
        self.vBoxLayout = FlowLayout(self.view)

        # layout.addWidget(self.banner)
        # layout.addLayout(self.vBoxLayout)
        # layout.setContentsMargins(0, 0, 0, 0)

        self.__initWidget()
        self.loadSamples()

    def __initWidget(self):
        self.view.setObjectName('view')
        self.setObjectName('IndicatorsInterface')

        # self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # self.setWidget(self.banner)
        self.setWidget(self.view)
        self.setWidgetResizable(True)
        # self.setWidget(self.view)
        # self.setWidgetResizable(True)
        # self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.vBoxLayout.setContentsMargins(26, 26, 26, 26)
        self.vBoxLayout.setSpacing(40)
        # self.vBoxLayout.addWidget(self.banner)
        self.vBoxLayout.setAlignment(Qt.AlignTop)

        self.set_style(qconfig.theme == Theme.DARK)
        StyleSheet.LINK_CARD.apply(self.view)

    def loadSamples(self):
        # self.linkCardView = LinkCardView(self.view)
        for i in range(20):
            self.addCard(
                "ind1",
                self.tr('Getting started'),
                self.tr('An overview of app development options and samples.'),
            )
        # self.vBoxLayout.addWidget(self.linkCardView)

    def addCard(self, icon, title, content):
        """ add link card """
        card = LinkCard(icon, title, content, self.view)
        self.vBoxLayout.addWidget(card)  # , 0, Qt.AlignLeft)

    def set_style(self, dark) -> None:
        if dark:
            self.setStyleSheet(
                "ScrollArea {background-color: rgb(66, 66, 66)}")
            # rgba(39, 39, 39, 0.95)  gray  rgba(249, 249, 249, 0.95)  lightgray
        else:
            self.setStyleSheet(
                "ScrollArea {background-color: rgb(208, 208, 208)}")
