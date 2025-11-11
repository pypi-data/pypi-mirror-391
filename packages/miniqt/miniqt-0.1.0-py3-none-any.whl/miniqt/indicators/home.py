# coding:utf-8
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPixmap, QPainter, QColor, QBrush, QPainterPath, QLinearGradient

from ..app.common.config import cfg, HELP_URL, REPO_URL, EXAMPLE_URL, FEEDBACK_URL
# from ..app.common.icon import Icon, FluentIconBase
# from ..app.components.link_card import LinkCardView
from ..app.common.style_sheet import StyleSheet
from PyQt5.QtWidgets import QWidget, QFrame, QLabel, QVBoxLayout, QHBoxLayout
from ..app.common.signal_bus import signalBus
from qfluentwidgets import IconWidget, FluentIcon, TextWrap, SingleDirectionScrollArea, FlowLayout, HorizontalPipsPager, HorizontalFlipView, ScrollArea, isDarkTheme, CardWidget, TransparentPushButton
# from qfluentwidgets.components.widgets.acrylic_label import AcrylicLabel
from pathlib import Path
import os
from ..utils import IndicatorClass, not_indicator_list, Callable, partial
from .new import IindicatorsInfo


class BannerWidget(QWidget):
    """ Banner widget """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setFixedHeight(136)

        self.vBoxLayout = QVBoxLayout(self)
        self.galleryLabel = QLabel('技术指标', self)
        self.banner = QPixmap(':/gallery/images/header1.png')
        self.linkCardView = LinkCardView(self)

        self.galleryLabel.setObjectName('galleryLabel')

        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.setContentsMargins(0, 20, 0, 0)
        self.vBoxLayout.addWidget(self.galleryLabel)
        self.vBoxLayout.addWidget(self.linkCardView, 1, Qt.AlignBottom)
        self.vBoxLayout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        # self.linkCardView.addCard(
        #     ':/gallery/images/logo.png',
        #     self.tr('Getting started'),
        #     self.tr('An overview of app development options and samples.'),
        #     HELP_URL
        # )

        # self.linkCardView.addCard(
        #     FluentIcon.GITHUB,
        #     self.tr('GitHub repo'),
        #     self.tr(
        #         'The latest fluent design controls and styles for your applications.'),
        #     REPO_URL
        # )

        # self.linkCardView.addCard(
        #     FluentIcon.CODE,
        #     self.tr('Code samples'),
        #     self.tr(
        #         'Find samples that demonstrate specific tasks, features and APIs.'),
        #     EXAMPLE_URL
        # )

        # self.linkCardView.addCard(
        #     FluentIcon.FEEDBACK,
        #     self.tr('Send feedback'),
        #     self.tr('Help us improve PyQt-Fluent-Widgets by providing feedback.'),
        #     FEEDBACK_URL
        # )

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
        self.main_window: QWidget = parent
        self.banner = BannerWidget(self)
        self.view = QWidget(self)
        self.vBoxLayout = QVBoxLayout(self.view)
        self.__initWidget()
        self.loadSamples()

    def addTab(self, widget: QWidget):
        self.main_window.addTab(widget)

    def __initWidget(self):
        self.view.setObjectName('view')
        self.setObjectName("IndicatorsInterface")
        StyleSheet.HOME_INTERFACE.apply(self)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWidget(self.view)
        self.setWidgetResizable(True)

        self.vBoxLayout.setContentsMargins(0, 0, 0, 36)
        self.vBoxLayout.setSpacing(40)
        self.vBoxLayout.addWidget(self.banner)
        self.vBoxLayout.setAlignment(Qt.AlignTop)

    def loadSamples(self):
        """ load samples """
        # basic input samples
        self.indicators_dict: dict[str, Callable] = dict()
        for k, v in vars(IndicatorClass).items():
            if not k.startswith("_"):
                inds = []
                for k_, v_ in vars(v).items():
                    if isinstance(v_, Callable) and not k_.startswith("_") and k_ not in not_indicator_list:
                        inds.append(v_)
                self.indicators_dict.update({k: inds})
        basicInputView = SampleCardView(
            self.tr("PandasTa"), self)
        ind = list(self.indicators_dict.values())[0]
        for i in range(3):
            basicInputView.addIndCard(ind[i])
        self.vBoxLayout.addWidget(basicInputView)

    def sample_card_view(self, key):
        return self.findChildren(SampleCardView, key)


class SampleCardView(QWidget):
    """ Sample card view """

    def __init__(self, title: str, parent: IndicatorsInterface = None):
        super().__init__(parent=parent.view)
        self.setObjectName(title)
        self.IndicatorsInterface = parent
        self.titleLabel = QLabel(title, self)
        self.titleLabel.setMaximumWidth(300)
        layout = QHBoxLayout()
        self.vBoxLayout = QVBoxLayout(self)
        self.more_butoon = TransparentPushButton('更多...')
        self.more_butoon.setMaximumWidth(200)
        self.flowLayout = FlowLayout()

        layout.addWidget(self.titleLabel)
        layout.addWidget(self.more_butoon)
        layout.addStretch(1)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignLeft)

        self.vBoxLayout.setContentsMargins(36, 0, 36, 0)
        self.vBoxLayout.setSpacing(10)
        self.flowLayout.setContentsMargins(0, 0, 0, 0)
        self.flowLayout.setHorizontalSpacing(12)
        self.flowLayout.setVerticalSpacing(12)

        # self.vBoxLayout.addWidget(self.titleLabel)
        self.vBoxLayout.addLayout(layout)
        self.vBoxLayout.addLayout(self.flowLayout, 1)

        self.titleLabel.setObjectName('viewTitleLabel')
        StyleSheet.SAMPLE_CARD.apply(self)

    def addSampleCard(self, icon, title, content, routeKey, index):
        """ add sample card """
        card = SampleCard(icon, title, content, routeKey, index, self)
        self.flowLayout.addWidget(card)

    def addIndCard(self, indicator: Callable):
        card = LinkCard(indicator, self, self.IndicatorsInterface)
        self.flowLayout.addWidget(card)  # , 0, Qt.AlignLeft)


class SampleCard(CardWidget):
    """ Sample card """

    def __init__(self, icon, title, content, routeKey, index, parent=None):
        super().__init__(parent=parent)
        self.index = index
        self.routekey = routeKey

        self.iconWidget = IconWidget(icon, self)
        self.titleLabel = QLabel(title, self)
        self.contentLabel = QLabel(TextWrap.wrap(content, 45, False)[0], self)

        self.hBoxLayout = QHBoxLayout(self)
        self.vBoxLayout = QVBoxLayout()

        self.setFixedSize(360, 90)
        self.iconWidget.setFixedSize(48, 48)

        self.hBoxLayout.setSpacing(28)
        self.hBoxLayout.setContentsMargins(20, 0, 0, 0)
        self.vBoxLayout.setSpacing(2)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setAlignment(Qt.AlignVCenter)

        self.hBoxLayout.setAlignment(Qt.AlignVCenter)
        self.hBoxLayout.addWidget(self.iconWidget)
        self.hBoxLayout.addLayout(self.vBoxLayout)
        self.vBoxLayout.addStretch(1)
        self.vBoxLayout.addWidget(self.titleLabel)
        self.vBoxLayout.addWidget(self.contentLabel)
        self.vBoxLayout.addStretch(1)

        self.titleLabel.setObjectName('titleLabel')
        self.contentLabel.setObjectName('contentLabel')

    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)
        signalBus.switchToSampleCard.emit(self.routekey, self.index)


class Ind_(QWidget):

    def __init__(self, parent=None, height: int = 0):
        super().__init__()
        self.parent_widget = parent
        # setTheme(Theme.DARK)
        # self.setStyleSheet('Demo{background:rgb(32,32,32)}')

        self.flipView = HorizontalFlipView(self)
        self.pager = HorizontalPipsPager(self)

        # change aspect ratio mode
        self.flipView.setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatio)

        # adjust view size
        # self.flipView.setItemSize(QSize(320, 180))
        # self.flipView.setFixedSize(QSize(320, 180))

        # NOTE: use custom delegate
        # self.flipView.setItemDelegate(CustomFlipItemDelegate(self.flipView))

        # add images
        path = os.path.join(os.getcwd(), 'minibt', 'miniqt',
                            'indicators', 'resource', "ind1")  # self.parent_widget.ind_name)
        self.flipView.addImages(
            [str(i) for i in Path(path).glob('*')])
        self.pager.setPageNumber(self.flipView.count())

        # adjust border radius
        # self.flipView.setBorderRadius(15)
        # self.flipView.setFixedSize(QSize(710, 270))
        # self.flipView.setSpacing(15)

        self.pager.currentIndexChanged.connect(self.flipView.setCurrentIndex)
        self.flipView.currentIndexChanged.connect(self.pager.setCurrentIndex)

        # self.flipView.setCurrentIndex(2)

        self.setLayout(QVBoxLayout(self))
        self.layout().addWidget(self.flipView, 0, Qt.AlignCenter)
        self.layout().addWidget(self.pager, 0, Qt.AlignCenter)
        self.layout().setAlignment(Qt.AlignCenter)
        self.layout().setSpacing(20)
        # self.adjustSize()
        self.setMaximumHeight(height)


class LinkCard(CardWidget):

    def __init__(self, indicator: Callable, parent: SampleCardView = None, IndicatorsInterface: IndicatorsInterface = None):  # , func: Callable
        super().__init__(parent=parent)
        # self.url = QUrl(url)
        # self.func = partial(func, widget=IindicatorsInfo)
        self.SampleCardView = parent
        self.IndicatorsInterface = IndicatorsInterface
        self.indicator = indicator
        self.indname = indicator.__name__
        self.inddoc = indicator.__doc__
        self.routekey = self.indname
        if not self.inddoc:
            self.inddoc = "无介绍"
        # self.setFixedSize(580, 500)
        width = 580  # int((self.IndicatorsInterface.width()-120)/3.)
        height = 280  # int(width*0.85)
        # h1 = self.height()-height

        self.iconWidget = Ind_(self, height)  # IconWidget(icon, self)
        # self.iconWidget.setMaximumHeight(h1)
        # self.iconWidget.adjustSize()
        self.titleLabel = QLabel(self.indname, self)
        h2 = 180-self.titleLabel.height()
        self.contentLabel = QLabel(
            TextWrap.wrap(self.inddoc, 28, False)[0], self)
        self.contentLabel.setMaximumHeight(h2)
        # self.urlWidget = IconWidget(FluentIcon.LINK, self)
        self.setFixedWidth(width)

        self.__initWidget()
        # self.urlWidget.move(self.width()-40, self.height()-40)

    def __initWidget(self):
        self.setCursor(Qt.PointingHandCursor)

        # self.iconWidget.setFixedSize(54, 54)
        # self.urlWidget.setFixedSize(16, 16)

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.setContentsMargins(24, 24, 0, 13)
        self.vBoxLayout.addWidget(self.iconWidget)
        self.vBoxLayout.addSpacing(16)
        self.vBoxLayout.addWidget(self.titleLabel)
        self.vBoxLayout.addSpacing(8)
        self.vBoxLayout.addWidget(self.contentLabel)
        self.vBoxLayout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        self.titleLabel.setObjectName('titleLabel')
        self.contentLabel.setObjectName('contentLabel')

    def mouseReleaseEvent(self, e):
        self.IndicatorsInterface.main_window.addTab(IindicatorsInfo())
        super().mouseReleaseEvent(e)
        # QDesktopServices.openUrl(self.url)


class LinkCardView(SingleDirectionScrollArea):  # SingleDirectionScrollArea):
    """ Link card view """

    def __init__(self, parent=None):
        super().__init__(parent, Qt.Horizontal)
        # self.setFixedSize(660, 900)
        # self.setFixedHeight(900)
        # self.adjustSize()
        self.view = QWidget(self)
        self.view.adjustSize()
        self.hBoxLayout = FlowLayout(self.view)  # QHBoxLayout(self.view)

        self.hBoxLayout.setContentsMargins(36, 0, 0, 0)
        self.hBoxLayout.setSpacing(12)
        self.hBoxLayout.setAlignment(Qt.AlignLeft)

        self.setWidget(self.view)
        self.setWidgetResizable(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.view.setObjectName('view')
        StyleSheet.LINK_CARD.apply(self)

    def addCard(self, icon, title, content):
        """ add link card """
        card = LinkCard(icon, title, content, self.view)
        self.hBoxLayout.addWidget(card)  # , 0, Qt.AlignLeft)
