# coding:utf-8
from typing import Iterable, List, Tuple, Union

from PyQt5.QtCore import Qt, pyqtSignal, QSize, QRectF, QRect, QPoint, QEvent
from PyQt5.QtGui import QPixmap, QPainter, QColor, QFont, QHoverEvent, QPainterPath, QPen
from PyQt5.QtWidgets import QAction, QLayoutItem, QWidget, QFrame, QHBoxLayout, QApplication
from qfluentwidgets import ColorDialog, TransparentToolButton
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets.common.font import setFont
# from qfluentwidgets.common.icon import FluentIcon, Icon, Action
# from qfluentwidgets.common.style_sheet import isDarkTheme
from qfluentwidgets.components.widgets.menu import RoundMenu, MenuAnimationType
# from qfluentwidgets.components.widgets.button import TransparentToggleToolButton
# from qfluentwidgets.components.widgets.tool_tip import ToolTipFilter
# from qfluentwidgets.components.widgets.flyout import FlyoutViewBase, Flyout
from qfluentwidgets.components.widgets.command_bar import MoreActionsButton, CommandSeparator, CommandButton, CommandMenu, isDarkTheme
from PyQt5.QtWidgets import QSplitterHandle, QStyle, QStylePainter, QStyleOptionButton, QWidget
# from ...common.font import setFont
# from ...common.icon import FluentIcon, Icon, Action
# from ...common.style_sheet import isDarkTheme
# from .menu import RoundMenu, MenuAnimationType
# from .button import TransparentToggleToolButton
# from .tool_tip import ToolTipFilter
# from .flyout import FlyoutViewBase, Flyout


class myqwidget(QWidget):
    def __init__(self, parent=...) -> None:
        super().__init__(parent)

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
        # painter.drawRect(1, self.height()-6, self.width()-1, 1)
        painter.drawLine(0, self.height()-2, self.width(), self.height()-2)


class MyCommandBar(QFrame):
    """ Command bar """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._widgets = []  # type: List[QWidget]
        self._hiddenWidgets = []  # type: List[QWidget]
        self._hiddenActions = []  # type: List[QAction]

        self._menuAnimation = MenuAnimationType.DROP_DOWN
        self._toolButtonStyle = Qt.ToolButtonIconOnly
        self._iconSize = QSize(16, 16)
        self._isButtonTight = False
        self._spacing = 0

        self.moreButton = MoreActionsButton(self)
        self.moreButton.clicked.connect(self._showMoreActionsMenu)
        self.moreButton.hide()

        setFont(self, 12)
        self.setAttribute(Qt.WA_TranslucentBackground)

    def setSpaing(self, spacing: int):
        if spacing == self._spacing:
            return

        self._spacing = spacing
        self.updateGeometry()

    def spacing(self):
        return self._spacing

    def addAction(self, action: QAction):
        """ add action

        Parameters
        ----------
        action: QAction
            the action to add
        """
        if action in self.actions():
            return

        button = self._createButton(action)
        self._insertWidgetToLayout(-1, button)
        super().addAction(action)
        return button

    def addActions(self, actions: Iterable[QAction]):
        for action in actions:
            self.addAction(action)

    def addHiddenAction(self, action: QAction):
        """ add hidden action """
        if action in self.actions():
            return

        self._hiddenActions.append(action)
        self.updateGeometry()
        super().addAction(action)

    def addHiddenActions(self, actions: List[QAction]):
        """ add hidden action """
        for action in actions:
            self.addHiddenAction(action)

    def insertAction(self, before: QAction, action: QAction):
        if before not in self.actions():
            return

        index = self.actions().index(before)
        button = self._createButton(action)
        self._insertWidgetToLayout(index, button)
        super().insertAction(before, action)
        return button

    def addSeparator(self):
        self.insertSeparator(-1)

    def insertSeparator(self, index: int):
        self._insertWidgetToLayout(index, CommandSeparator(self))

    def addWidget(self, widget: QWidget):
        """ add widget to command bar """
        self._insertWidgetToLayout(-1, widget)

    def removeAction(self, action: QAction):
        if action not in self.actions():
            return

        for w in self.commandButtons:
            if w.action() is action:
                self._widgets.remove(w)
                w.hide()
                w.deleteLater()
                break

        self.updateGeometry()

    def removeWidget(self, widget: QWidget):
        if widget not in self._widgets:
            return

        self._widgets.remove(widget)
        self.updateGeometry()

    def removeHiddenAction(self, action: QAction):
        if action in self._hiddenActions:
            self._hiddenActions.remove(action)

    def setToolButtonStyle(self, style: Qt.ToolButtonStyle):
        """ set the style of tool button """
        if self.toolButtonStyle() == style:
            return

        self._toolButtonStyle = style
        for w in self.commandButtons:
            w.setToolButtonStyle(style)

    def toolButtonStyle(self):
        return self._toolButtonStyle

    def setButtonTight(self, isTight: bool):
        if self.isButtonTight() == isTight:
            return

        self._isButtonTight = isTight

        for w in self.commandButtons:
            w.setTight(isTight)

        self.updateGeometry()

    def isButtonTight(self):
        return self._isButtonTight

    def setIconSize(self, size: QSize):
        if size == self._iconSize:
            return

        self._iconSize = size
        for w in self.commandButtons:
            w.setIconSize(size)

    def iconSize(self):
        return self._iconSize

    def resizeEvent(self, e):
        self.updateGeometry()

    def _createButton(self, action: QAction):
        """ create command button """
        button = CommandButton(self)
        button.setAction(action)
        button.setToolButtonStyle(self.toolButtonStyle())
        button.setTight(self.isButtonTight())
        button.setIconSize(self.iconSize())
        button.setFont(self.font())
        return button

    def _insertWidgetToLayout(self, index: int, widget: QWidget):
        """ add widget to layout """
        widget.setParent(self)
        widget.show()

        if index < 0:
            self._widgets.append(widget)
        else:
            self._widgets.insert(index, widget)

        self.setFixedHeight(max(w.height() for w in self._widgets))
        self.updateGeometry()

    def minimumSizeHint(self) -> QSize:
        return self.moreButton.size()

    def updateGeometry(self):
        self._hiddenWidgets.clear()
        self.moreButton.hide()

        visibles = self._visibleWidgets()
        x = self.contentsMargins().left()
        h = self.height()

        for widget in visibles:
            widget.show()
            widget.move(x, (h - widget.height()) // 2)
            x += (widget.width() + self.spacing())

        # show more actions button
        if self._hiddenActions or len(visibles) < len(self._widgets):
            self.moreButton.show()
            self.moreButton.move(x, (h - self.moreButton.height()) // 2)

        for widget in self._widgets[len(visibles):]:
            widget.hide()
            self._hiddenWidgets.append(widget)

    def _visibleWidgets(self) -> List[QWidget]:
        """ return the visible widgets in layout """
        # have enough spacing to show all widgets
        if self.suitableWidth() <= self.width():
            return self._widgets

        w = self.moreButton.width()
        for index, widget in enumerate(self._widgets):
            w += widget.width()
            if index > 0:
                w += self.spacing()

            if w > self.width():
                break

        return self._widgets[:index]

    def suitableWidth(self):
        widths = [w.width() for w in self._widgets]
        if self._hiddenActions:
            widths.append(self.moreButton.width())

        return sum(widths) + self.spacing() * max(len(widths) - 1, 0)

    def resizeToSuitableWidth(self):
        self.setFixedWidth(self.suitableWidth())

    def setFont(self, font: QFont):
        super().setFont(font)
        for button in self.commandButtons:
            button.setFont(font)

    @property
    def commandButtons(self):
        return [w for w in self._widgets if isinstance(w, CommandButton)]

    def setMenuDropDown(self, down: bool):
        """ set the animation direction of more actions menu """
        if down:
            self._menuAnimation = MenuAnimationType.DROP_DOWN
        else:
            self._menuAnimation = MenuAnimationType.PULL_UP

    def isMenuDropDown(self):
        return self._menuAnimation == MenuAnimationType.DROP_DOWN

    def _showMoreActionsMenu(self):
        """ show more actions menu """
        self.moreButton.clearState()

        actions = self._hiddenActions.copy()

        for w in reversed(self._hiddenWidgets):
            if isinstance(w, CommandButton):
                actions.insert(0, w.action())

        menu = CommandMenu(self)
        menu.addActions(actions)

        x = -menu.width() + menu.layout().contentsMargins().right() + \
            self.moreButton.width() + 18
        if self._menuAnimation == MenuAnimationType.DROP_DOWN:
            y = self.moreButton.height()
        else:
            y = -5

        pos = self.moreButton.mapToGlobal(QPoint(x, y))
        menu.exec(pos, aniType=self._menuAnimation)


class MyColorDialog(ColorDialog):
    """ Color dialog """

    def __init__(self, color, title: str, parent=None, enableAlpha=False):
        """
        Parameters
        ----------
        color: `QColor` | `GlobalColor` | str
            initial color

        title: str
            the title of dialog

        parent: QWidget
            parent widget

        enableAlpha: bool
            whether to enable the alpha channel
        """
        super().__init__(color, title, parent, enableAlpha)

        self.hexLineEdit.move(120, 381)
        self.colorbutton = TransparentToolButton(FIF.ADD, self)
        self.hexLineEdit.move(206, 381)


# class CollapsibleSplitterHandle(QSplitterHandle):
#     def __init__(self, orientation=False, parent=None):
#         super(CollapsibleSplitterHandle, self).__init__(orientation, parent)
#         self.collapsed = False
#         self.arrow_button_size = 8
#         parent.splitterMoved.connect(self.updateGeometry)

#     def paintEvent(self, event):
#         painter = QStylePainter(self)
#         opt = QStyleOptionButton()

#         rect = self.rect()
#         opt.rect = QRect(0, 0, self.arrow_button_size, self.arrow_button_size)
#         opt.state = QStyle.State_Enabled | QStyle.State_Active | QStyle.State_Horizontal
#         opt.iconSize = QSize(self.arrow_button_size, self.arrow_button_size)

#         if self.collapsed:
#             opt.icon = self.style().standardIcon(QStyle.SP_TitleBarUnshadeButton)
#         else:
#             opt.icon = self.style().standardIcon(QStyle.SP_TitleBarShadeButton)

#         painter.drawControl(QStyle.CE_PushButton, opt)

#     def mouseReleaseEvent(self, event):
#         if event.button() == Qt.LeftButton:
#             if self.collapsed:
#                 self.collapsed = False
#                 self.parent().restoreState(self.parent().saved_state)
#             else:
#                 self.collapsed = True
#                 self.parent().saved_state = self.parent().saveState()
#                 self.parent().setSizes(
#                     [self.arrow_button_size, self.parent().sizes()[1]])

#             self.update()
