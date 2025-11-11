# coding:utf-8
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPixmap, QPainter, QColor, QBrush, QPainterPath, QLinearGradient, QPen
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame
from qfluentwidgets import ScrollArea, isDarkTheme, FluentIcon, StrongBodyLabel, BodyLabel, ToolTipFilter, toggleTheme, TitleLabel, CaptionLabel, PushButton, ToolButton
from ..app.common.config import cfg, HELP_URL, REPO_URL, EXAMPLE_URL, FEEDBACK_URL
from ..app.common.icon import Icon, FluentIconBase
from ..app.components.link_card import LinkCardView
# from .sample_card import SampleCardView
from ..app.common.style_sheet import StyleSheet
# from ..monaco.monaco_widget import MonacoEditor
from ..futures.Editor import MonacoEditor
from ..chart.chart import ChartWidget
from ..app.common.signal_bus import signalBus


class SeparatorWidget(QWidget):
    """ Seperator widget """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setFixedSize(6, 16)

    def paintEvent(self, e):
        painter = QPainter(self)
        pen = QPen(1)
        pen.setCosmetic(True)
        c = QColor(255, 255, 255, 21) if isDarkTheme() else QColor(0, 0, 0, 15)
        pen.setColor(c)
        painter.setPen(pen)

        x = self.width() // 2
        painter.drawLine(x, 0, x, self.height())


class ExampleCard(QWidget):
    """ Example card """

    def __init__(self, title, widget: QWidget, sourcePath, stretch=0, parent=None):
        super().__init__(parent=parent)
        self.parent_widget = parent
        self.widget = widget
        # if isinstance(widget, WeightCharts):
        #     self.widget.setMinimumSize(900, 600)
        self.stretch = stretch

        self.titleLabel = StrongBodyLabel(title, self)
        self.card = QFrame(self)

        self.sourceWidget = QFrame(self.card)
        self.sourcePath = sourcePath
        self.sourcePathLabel = BodyLabel(
            self.tr('Source code'), self.sourceWidget)
        # self.linkIcon = IconWidget(FluentIcon.LINK, self.sourceWidget)

        self.vBoxLayout = QVBoxLayout(self)
        self.cardLayout = QVBoxLayout(self.card)
        self.topLayout = QHBoxLayout()
        # self.bottomLayout = QHBoxLayout(self.sourceWidget)

        self.__initWidget()

    def __initWidget(self):
        # self.linkIcon.setFixedSize(16, 16)
        self.__initLayout()

        self.sourceWidget.setCursor(Qt.PointingHandCursor)
        self.sourceWidget.installEventFilter(self)

        self.card.setObjectName('card')
        self.sourceWidget.setObjectName('sourceWidget')

    def __initLayout(self):
        self.vBoxLayout.setSizeConstraint(QVBoxLayout.SetMinimumSize)
        self.cardLayout.setSizeConstraint(QVBoxLayout.SetMinimumSize)
        self.topLayout.setSizeConstraint(QHBoxLayout.SetMinimumSize)

        self.vBoxLayout.setSpacing(12)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.topLayout.setContentsMargins(12, 12, 12, 12)
        # self.bottomLayout.setContentsMargins(18, 18, 18, 18)
        self.cardLayout.setContentsMargins(0, 0, 0, 0)

        self.vBoxLayout.addWidget(self.titleLabel, 0, Qt.AlignTop)
        self.vBoxLayout.addWidget(self.card, 0, Qt.AlignTop)
        self.vBoxLayout.setAlignment(Qt.AlignTop)

        self.cardLayout.setSpacing(0)
        self.cardLayout.setAlignment(Qt.AlignTop)
        self.cardLayout.addLayout(self.topLayout, 0)
        self.cardLayout.addWidget(self.sourceWidget, 0, Qt.AlignBottom)

        self.widget.setParent(self.card)
        self.topLayout.addWidget(self.widget)
        if self.stretch == 0:
            self.topLayout.addStretch(1)

        self.widget.show()

        # self.bottomLayout.addWidget(self.sourcePathLabel, 0, Qt.AlignLeft)
        # self.bottomLayout.addStretch(1)
        # self.bottomLayout.addWidget(self.linkIcon, 0, Qt.AlignRight)
        # self.bottomLayout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

    def eventFilter(self, obj, e):
        # if obj is self.sourceWidget:
        #     if e.type() == QEvent.MouseButtonRelease:
        #         QDesktopServices.openUrl(QUrl(self.sourcePath))

        return super().eventFilter(obj, e)


class BannerWidget(QWidget):
    """ Banner widget """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setFixedHeight(136)

        self.vBoxLayout = QVBoxLayout(self)
        self.galleryLabel = QLabel('Fluent Gallery', self)
        self.banner = QPixmap(':/gallery/images/header1.png')
        self.toolbar = ToolBar(self)
        # self.linkCardView = LinkCardView(self)

        self.galleryLabel.setObjectName('galleryLabel')

        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.setContentsMargins(0, 20, 0, 0)
        self.vBoxLayout.addWidget(self.galleryLabel)
        self.vBoxLayout.addWidget(self.toolbar)
        # self.vBoxLayout.addWidget(self.linkCardView, 1, Qt.AlignBottom)
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


class ToolBar(QWidget):
    """ Tool bar """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.parent_widget = parent
        # self.titleLabel = TitleLabel(title, self)
        # self.subtitleLabel = CaptionLabel(subtitle, self)
        # self.titleLabel.setMinimumWidth(300)
        # self.subtitleLabel.setMinimumWidth(300)

        self.documentButton = PushButton(
            self.tr('Documentation'), self, FluentIcon.DOCUMENT)
        self.sourceButton = PushButton(
            self.tr('Source'), self, FluentIcon.GITHUB)
        self.themeButton = ToolButton(FluentIcon.CONSTRACT, self)
        self.separator = SeparatorWidget(self)
        self.supportButton = ToolButton(FluentIcon.HEART, self)
        self.feedbackButton = ToolButton(FluentIcon.FEEDBACK, self)

        self.vBoxLayout = QVBoxLayout(self)
        self.buttonLayout = QHBoxLayout()

        self.__initWidget()

    def __initWidget(self):
        self.setFixedHeight(60)
        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.setContentsMargins(36, 0, 36, 0)  # 36, 22, 36, 12)
        # self.vBoxLayout.addWidget(self.titleLabel)
        # self.vBoxLayout.addSpacing(4)
        # self.vBoxLayout.addWidget(self.subtitleLabel)
        # self.vBoxLayout.addSpacing(4)
        self.vBoxLayout.addLayout(self.buttonLayout, 1)
        self.vBoxLayout.setAlignment(Qt.AlignTop)

        # self.buttonLayout.setSpacing(4)
        self.buttonLayout.setContentsMargins(0, 0, 0, 0)
        self.buttonLayout.addWidget(self.documentButton, 0, Qt.AlignLeft)
        self.buttonLayout.addWidget(self.sourceButton, 0, Qt.AlignLeft)
        self.buttonLayout.addStretch(1)
        self.buttonLayout.addWidget(self.themeButton, 0, Qt.AlignRight)
        self.buttonLayout.addWidget(self.separator, 0, Qt.AlignRight)
        self.buttonLayout.addWidget(self.supportButton, 0, Qt.AlignRight)
        self.buttonLayout.addWidget(self.feedbackButton, 0, Qt.AlignRight)
        self.buttonLayout.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        self.themeButton.installEventFilter(ToolTipFilter(self.themeButton))
        self.supportButton.installEventFilter(
            ToolTipFilter(self.supportButton))
        self.feedbackButton.installEventFilter(
            ToolTipFilter(self.feedbackButton))
        self.themeButton.setToolTip(self.tr('Toggle theme'))
        self.supportButton.setToolTip(self.tr('Support me'))
        self.feedbackButton.setToolTip(self.tr('Send feedback'))

        self.themeButton.clicked.connect(lambda: toggleTheme(True))
        self.supportButton.clicked.connect(signalBus.supportSignal)
        # self.documentButton.clicked.connect(
        #     lambda: QDesktopServices.openUrl(QUrl(HELP_URL)))
        # self.sourceButton.clicked.connect(
        #     lambda: QDesktopServices.openUrl(QUrl(EXAMPLE_URL)))
        # self.feedbackButton.clicked.connect(
        #     lambda: QDesktopServices.openUrl(QUrl(FEEDBACK_URL)))
        self.feedbackButton.clicked.connect(lambda x: print(
            self.parent_widget.width(), self.parent_widget.height()))
        # self.subtitleLabel.setTextColor(
        #     QColor(96, 96, 96), QColor(216, 216, 216))


class _HomeInterface_(ScrollArea):
    """ Home interface """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.parent_widget = parent
        self.banner = BannerWidget(self)

        self.view = QWidget(self)
        self.vBoxLayout = QVBoxLayout(self.view)

        self.__initWidget()
        self.loadSamples()

    def __initWidget(self):
        self.view.setObjectName('view')
        self.setObjectName('_homeInterface_')
        StyleSheet.HOME_INTERFACE.apply(self)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWidget(self.view)
        self.setWidgetResizable(True)

        self.vBoxLayout.setContentsMargins(0, 0, 0, 36)
        self.vBoxLayout.setSpacing(40)
        self.vBoxLayout.addWidget(self.banner)
        # self.vBoxLayout.addWidget(self.toolbar)
        self.vBoxLayout.setAlignment(Qt.AlignTop)

    def addExampleCard(self, title, widget, sourcePath: str, stretch=0):
        card = ExampleCard(title, widget, sourcePath, stretch, self.view)
        self.vBoxLayout.addWidget(card)  # , 0, Qt.AlignTop)
        return card

    def resize_(self) -> None:
        for widget in self.findChildren(ExampleCard):
            if isinstance(widget.widget, CaptionLabel):
                widget.widget.setMinimumWidth(
                    self.parent_widget.width()-100)
            else:
                widget.widget.setMinimumSize(
                    self.parent_widget.width()-100, min(self.parent_widget.height()-50, 600))

    def loadSamples(self):
        """ load samples """
        # basic input samples
        self.addExampleCard(
            title=self.tr('指标'),
            widget=ChartWidget(self, self.parent_widget.conset),
            # widget=CalendarPicker(self),
            sourcePath='https://github.com/zhiyiYo/PyQt-Fluent-Widgets/blob/master/examples/date_time/calendar_picker/demo.py'
        )

        # w = CalendarPicker(self)
        w = CaptionLabel(self)
        w.setTextInteractionFlags(Qt.TextSelectableByMouse)
        w.setText(
            """## Steel Ball Run \n * Johnny Joestar 🦄 \n * Gyro Zeppeli 🐴 \n
            ## Steel Ball Run \n * Johnny Joestar 🦄 \n * Gyro Zeppeli 🐴 \n
            ## Steel Ball Run \n * Johnny Joestar 🦄 \n * Gyro Zeppeli 🐴 \n
            ## Steel Ball Run \n * Johnny Joestar 🦄 \n * Gyro Zeppeli 🐴 \n""")
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
            widget=MonacoEditor(self),  # DatePicker(self),
            sourcePath='https://github.com/zhiyiYo/PyQt-Fluent-Widgets/blob/master/examples/date_time/time_picker/demo.py'
        )
        self.resize_()
        # basicInputView = SampleCardView(
        #     self.tr("Basic input samples"), self.view)
        # for i in range(3):
        #     basicInputView.addIndCard('ind1', self.tr('Getting started'),
        #                               self.tr('An overview of app development options and samples.'))
        # basicInputView.addSampleCard(
        #     icon=":/gallery/images/controls/Button.png",
        #     title="Button",
        #     content=self.tr(
        #         "A control that responds to user input and emit clicked signal."),
        #     routeKey="basicInputInterface",
        #     index=0
        # )
        # basicInputView.addSampleCard(
        #     icon=":/gallery/images/controls/Checkbox.png",
        #     title="CheckBox",
        #     content=self.tr("A control that a user can select or clear."),
        #     routeKey="basicInputInterface",
        #     index=8
        # )
        # basicInputView.addSampleCard(
        #     icon=":/gallery/images/controls/ComboBox.png",
        #     title="ComboBox",
        #     content=self.tr(
        #         "A drop-down list of items a user can select from."),
        #     routeKey="basicInputInterface",
        #     index=10
        # )
        # basicInputView.addSampleCard(
        #     icon=":/gallery/images/controls/DropDownButton.png",
        #     title="DropDownButton",
        #     content=self.tr(
        #         "A button that displays a flyout of choices when clicked."),
        #     routeKey="basicInputInterface",
        #     index=12
        # )
        # basicInputView.addSampleCard(
        #     icon=":/gallery/images/controls/HyperlinkButton.png",
        #     title="HyperlinkButton",
        #     content=self.tr(
        #         "A button that appears as hyperlink text, and can navigate to a URI or handle a Click event."),
        #     routeKey="basicInputInterface",
        #     index=18
        # )
        # basicInputView.addSampleCard(
        #     icon=":/gallery/images/controls/RadioButton.png",
        #     title="RadioButton",
        #     content=self.tr(
        #         "A control that allows a user to select a single option from a group of options."),
        #     routeKey="basicInputInterface",
        #     index=19
        # )
        # basicInputView.addSampleCard(
        #     icon=":/gallery/images/controls/Slider.png",
        #     title="Slider",
        #     content=self.tr(
        #         "A control that lets the user select from a range of values by moving a Thumb control along a track."),
        #     routeKey="basicInputInterface",
        #     index=20
        # )
        # basicInputView.addSampleCard(
        #     icon=":/gallery/images/controls/SplitButton.png",
        #     title="SplitButton",
        #     content=self.tr(
        #         "A two-part button that displays a flyout when its secondary part is clicked."),
        #     routeKey="basicInputInterface",
        #     index=21
        # )
        # basicInputView.addSampleCard(
        #     icon=":/gallery/images/controls/ToggleSwitch.png",
        #     title="SwitchButton",
        #     content=self.tr(
        #         "A switch that can be toggled between 2 states."),
        #     routeKey="basicInputInterface",
        #     index=25
        # )
        # basicInputView.addSampleCard(
        #     icon=":/gallery/images/controls/ToggleButton.png",
        #     title="ToggleButton",
        #     content=self.tr(
        #         "A button that can be switched between two states like a CheckBox."),
        #     routeKey="basicInputInterface",
        #     index=26
        # )
        # self.vBoxLayout.addWidget(basicInputView)

        # # date time samples
        # dateTimeView = SampleCardView(
        #     self.tr('Date & time samples'), self.view)
        # dateTimeView.addSampleCard(
        #     icon=":/gallery/images/controls/CalendarDatePicker.png",
        #     title="CalendarPicker",
        #     content=self.tr(
        #         "A control that lets a user pick a date value using a calendar."),
        #     routeKey="dateTimeInterface",
        #     index=0
        # )
        # dateTimeView.addSampleCard(
        #     icon=":/gallery/images/controls/DatePicker.png",
        #     title="DatePicker",
        #     content=self.tr("A control that lets a user pick a date value."),
        #     routeKey="dateTimeInterface",
        #     index=2
        # )
        # dateTimeView.addSampleCard(
        #     icon=":/gallery/images/controls/TimePicker.png",
        #     title="TimePicker",
        #     content=self.tr(
        #         "A configurable control that lets a user pick a time value."),
        #     routeKey="dateTimeInterface",
        #     index=4
        # )
        # self.vBoxLayout.addWidget(dateTimeView)

        # # dialog samples
        # dialogView = SampleCardView(self.tr('Dialog samples'), self.view)
        # dialogView.addSampleCard(
        #     icon=":/gallery/images/controls/Flyout.png",
        #     title="Dialog",
        #     content=self.tr("A frameless message dialog."),
        #     routeKey="dialogInterface",
        #     index=0
        # )
        # dialogView.addSampleCard(
        #     icon=":/gallery/images/controls/ContentDialog.png",
        #     title="MessageBox",
        #     content=self.tr("A message dialog with mask."),
        #     routeKey="dialogInterface",
        #     index=1
        # )
        # dialogView.addSampleCard(
        #     icon=":/gallery/images/controls/ColorPicker.png",
        #     title="ColorDialog",
        #     content=self.tr("A dialog that allows user to select color."),
        #     routeKey="dialogInterface",
        #     index=2
        # )
        # dialogView.addSampleCard(
        #     icon=":/gallery/images/controls/Flyout.png",
        #     title="Flyout",
        #     content=self.tr(
        #         "Shows contextual information and enables user interaction."),
        #     routeKey="dialogInterface",
        #     index=3
        # )
        # dialogView.addSampleCard(
        #     icon=":/gallery/images/controls/TeachingTip.png",
        #     title="TeachingTip",
        #     content=self.tr(
        #         "A content-rich flyout for guiding users and enabling teaching moments."),
        #     routeKey="dialogInterface",
        #     index=5
        # )
        # self.vBoxLayout.addWidget(dialogView)

        # # layout samples
        # layoutView = SampleCardView(self.tr('Layout samples'), self.view)
        # layoutView.addSampleCard(
        #     icon=":/gallery/images/controls/Grid.png",
        #     title="FlowLayout",
        #     content=self.tr(
        #         "A layout arranges components in a left-to-right flow, wrapping to the next row when the current row is full."),
        #     routeKey="layoutInterface",
        #     index=0
        # )
        # self.vBoxLayout.addWidget(layoutView)

        # # material samples
        # materialView = SampleCardView(self.tr('Material samples'), self.view)
        # materialView.addSampleCard(
        #     icon=":/gallery/images/controls/Acrylic.png",
        #     title="AcrylicLabel",
        #     content=self.tr(
        #         "A translucent material recommended for panel background."),
        #     routeKey="materialInterface",
        #     index=0
        # )
        # self.vBoxLayout.addWidget(materialView)

        # # menu samples
        # menuView = SampleCardView(
        #     self.tr('Menu & toolbars samples'), self.view)
        # menuView.addSampleCard(
        #     icon=":/gallery/images/controls/MenuFlyout.png",
        #     title="RoundMenu",
        #     content=self.tr(
        #         "Shows a contextual list of simple commands or options."),
        #     routeKey="menuInterface",
        #     index=0
        # )
        # menuView.addSampleCard(
        #     icon=":/gallery/images/controls/CommandBar.png",
        #     title="CommandBar",
        #     content=self.tr(
        #         "Shows a contextual list of simple commands or options."),
        #     routeKey="menuInterface",
        #     index=2
        # )
        # menuView.addSampleCard(
        #     icon=":/gallery/images/controls/CommandBarFlyout.png",
        #     title="CommandBarFlyout",
        #     content=self.tr(
        #         "A mini-toolbar displaying proactive commands, and an optional menu of commands."),
        #     routeKey="menuInterface",
        #     index=3
        # )
        # self.vBoxLayout.addWidget(menuView)

        # # navigation
        # navigationView = SampleCardView(self.tr('Navigation'), self.view)
        # navigationView.addSampleCard(
        #     icon=":/gallery/images/controls/BreadcrumbBar.png",
        #     title="BreadcrumbBar",
        #     content=self.tr(
        #         "Shows the trail of navigation taken to the current location."),
        #     routeKey="navigationViewInterface",
        #     index=0
        # )
        # navigationView.addSampleCard(
        #     icon=":/gallery/images/controls/Pivot.png",
        #     title="Pivot",
        #     content=self.tr(
        #         "Presents information from different sources in a tabbed view."),
        #     routeKey="navigationViewInterface",
        #     index=1
        # )
        # navigationView.addSampleCard(
        #     icon=":/gallery/images/controls/TabView.png",
        #     title="TabView",
        #     content=self.tr(
        #         "Presents information from different sources in a tabbed view."),
        #     routeKey="navigationViewInterface",
        #     index=3
        # )
        # self.vBoxLayout.addWidget(navigationView)

        # # scroll samples
        # scrollView = SampleCardView(self.tr('Scrolling samples'), self.view)
        # scrollView.addSampleCard(
        #     icon=":/gallery/images/controls/ScrollViewer.png",
        #     title="ScrollArea",
        #     content=self.tr(
        #         "A container control that lets the user pan and zoom its content smoothly."),
        #     routeKey="scrollInterface",
        #     index=0
        # )
        # scrollView.addSampleCard(
        #     icon=":/gallery/images/controls/PipsPager.png",
        #     title="PipsPager",
        #     content=self.tr(
        #         "A control to let the user navigate through a paginated collection when the page numbers do not need to be visually known."),
        #     routeKey="scrollInterface",
        #     index=3
        # )
        # self.vBoxLayout.addWidget(scrollView)

        # # state info samples
        # stateInfoView = SampleCardView(
        #     self.tr('Status & info samples'), self.view)
        # stateInfoView.addSampleCard(
        #     icon=":/gallery/images/controls/ProgressRing.png",
        #     title="StateToolTip",
        #     content=self.tr(
        #         "Shows the apps progress on a task, or that the app is performing ongoing work that does block user interaction."),
        #     routeKey="statusInfoInterface",
        #     index=0
        # )
        # stateInfoView.addSampleCard(
        #     icon=":/gallery/images/controls/InfoBadge.png",
        #     title="InfoBadge",
        #     content=self.tr(
        #         "An non-intrusive Ul to display notifications or bring focus to an area."),
        #     routeKey="statusInfoInterface",
        #     index=3
        # )
        # stateInfoView.addSampleCard(
        #     icon=":/gallery/images/controls/InfoBar.png",
        #     title="InfoBar",
        #     content=self.tr(
        #         "An inline message to display app-wide status change information."),
        #     routeKey="statusInfoInterface",
        #     index=4
        # )
        # stateInfoView.addSampleCard(
        #     icon=":/gallery/images/controls/ProgressBar.png",
        #     title="ProgressBar",
        #     content=self.tr(
        #         "Shows the apps progress on a task, or that the app is performing ongoing work that doesn't block user interaction."),
        #     routeKey="statusInfoInterface",
        #     index=8
        # )
        # stateInfoView.addSampleCard(
        #     icon=":/gallery/images/controls/ProgressRing.png",
        #     title="ProgressRing",
        #     content=self.tr(
        #         "Shows the apps progress on a task, or that the app is performing ongoing work that doesn't block user interaction."),
        #     routeKey="statusInfoInterface",
        #     index=10
        # )
        # stateInfoView.addSampleCard(
        #     icon=":/gallery/images/controls/ToolTip.png",
        #     title="ToolTip",
        #     content=self.tr(
        #         "Displays information for an element in a pop-up window."),
        #     routeKey="statusInfoInterface",
        #     index=1
        # )
        # self.vBoxLayout.addWidget(stateInfoView)

        # # text samples
        # textView = SampleCardView(self.tr('Text samples'), self.view)
        # textView.addSampleCard(
        #     icon=":/gallery/images/controls/TextBox.png",
        #     title="LineEdit",
        #     content=self.tr("A single-line plain text field."),
        #     routeKey="textInterface",
        #     index=0
        # )
        # textView.addSampleCard(
        #     icon=":/gallery/images/controls/PasswordBox.png",
        #     title="PasswordLineEdit",
        #     content=self.tr("A control for entering passwords."),
        #     routeKey="textInterface",
        #     index=2
        # )
        # textView.addSampleCard(
        #     icon=":/gallery/images/controls/NumberBox.png",
        #     title="SpinBox",
        #     content=self.tr(
        #         "A text control used for numeric input and evaluation of algebraic equations."),
        #     routeKey="textInterface",
        #     index=3
        # )
        # textView.addSampleCard(
        #     icon=":/gallery/images/controls/RichEditBox.png",
        #     title="TextEdit",
        #     content=self.tr(
        #         "A rich text editing control that supports formatted text, hyperlinks, and other rich content."),
        #     routeKey="textInterface",
        #     index=8
        # )
        # self.vBoxLayout.addWidget(textView)

        # # view samples
        # collectionView = SampleCardView(self.tr('View samples'), self.view)
        # collectionView.addSampleCard(
        #     icon=":/gallery/images/controls/ListView.png",
        #     title="ListView",
        #     content=self.tr(
        #         "A control that presents a collection of items in a vertical list."),
        #     routeKey="viewInterface",
        #     index=0
        # )
        # collectionView.addSampleCard(
        #     icon=":/gallery/images/controls/DataGrid.png",
        #     title="TableView",
        #     content=self.tr(
        #         "The DataGrid control provides a flexible way to display a collection of data in rows and columns."),
        #     routeKey="viewInterface",
        #     index=1
        # )
        # collectionView.addSampleCard(
        #     icon=":/gallery/images/controls/TreeView.png",
        #     title="TreeView",
        #     content=self.tr(
        #         "The TreeView control is a hierarchical list pattern with expanding and collapsing nodes that contain nested items."),
        #     routeKey="viewInterface",
        #     index=2
        # )
        # collectionView.addSampleCard(
        #     icon=":/gallery/images/controls/FlipView.png",
        #     title="FlipView",
        #     content=self.tr(
        #         "Presents a collection of items that the user can flip through,one item at a time."),
        #     routeKey="viewInterface",
        #     index=4
        # )
        # self.vBoxLayout.addWidget(collectionView)
