from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QAbstractItemView, QDesktopWidget, QHeaderView, QTableWidgetItem, QVBoxLayout)
from qfluentwidgets import TableWidget, LineEdit, FluentWindow
import qtawesome as qta
from ..utils import Indicator_Info, IndicatorClass


class tablewidget(TableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        font = QFont()
        font.setPointSize(12)
        self.setFont(font)
        self.setFixedWidth(280)
        self.setSelectionBehavior(
            QAbstractItemView.SelectRows)  # 设置不可选择单个单元格，只可选择一行。
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 禁止编辑
        # 序号进行隐藏table.verticalHeader().setVisible(False)#序号进行隐藏
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setVisible(False)  # 隐藏表头
        self.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)  # 铺满整个QTableWidget控件
        self.setColumnCount(2)  # 设置表格一共有三列
        # self.setHorizontalHeaderLabels(['代码','名称'])#设置表头文字
        self.setEditTriggers(
            QAbstractItemView.NoEditTriggers)  # 设置表格不可更改
        self.setSortingEnabled(False)  # 设置表头不可排序
        self.resizeColumnsToContents()
        self.doubleClicked.connect(parent.doubleclick)


class KeyElfWindow_(FluentWindow):
    """键盘精灵"""

    def __init__(self, parent, text: str) -> None:
        super().__init__()
        self.hBoxLayout.removeWidget(self.navigationInterface)
        self.navigationInterface.deleteLater()
        self.hBoxLayout.removeWidget(self.stackedWidget)
        self.stackedWidget.deleteLater()
        self.hBoxLayout.removeItem(self.widgetLayout)
        self.titleBar.buttonLayout.removeWidget(self.titleBar.maxBtn)
        self.titleBar.maxBtn.deleteLater()
        self.titleBar.buttonLayout.removeWidget(self.titleBar.minBtn)
        self.titleBar.minBtn.deleteLater()
        height = self.titleBar.maxBtn.height()
        self.titleBar.titleLabel.setText(self.tr('键盘精灵'))
        self.titleBar.iconLabel.setPixmap(
            qta.icon('fa.keyboard-o', color='cyan').pixmap(self.titleBar.iconLabel.size()))
        self.ChartMdiAreaWidget = parent  # 市场窗口
        self.AllMarkeContractDf = parent.FuturesInterface.tq_api.contract_info_df(
            "main_contract")
        self.IndDf = Indicator_Info
        self.currentRow = None
        self.setWindowFlags(Qt.MSWindowsFixedSizeDialogHint |
                            Qt.WindowStaysOnTopHint)
        # self.setWindowFlags(Qt.WindowMaximizeButtonHint |
        #                     Qt.MSWindowsFixedSizeDialogHint | Qt.WindowStaysOnTopHint)
        # self.setWindowTitle('键盘精灵')
        self.setFixedSize(280, 450)
        # self.setWindowIcon(qta.icon('fa.keyboard-o', color='cyan'))

        vlayout = QVBoxLayout()
        # self.createKeyTableWidget()
        self.keytable = tablewidget(self)
        self.symboledit = MyQLineEdit(self)
        self.symboledit.setFixedHeight(height)
        self.symboledit.setText(text)
        vlayout.addWidget(self.symboledit)
        vlayout.addWidget(self.keytable)
        vlayout.setContentsMargins(5, height, 5, 5)
        vlayout.setSpacing(5)

        self.hBoxLayout.addLayout(vlayout)
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.desktop = QDesktopWidget()
        self.move((self.desktop.availableGeometry().width()-self.width()-5),
                  self.desktop.availableGeometry().height()-self.height()-5)  # 初始化位置到右下角
        self.symboledit.setFocus()
        self.symboledit.setCursorPosition(len(text))
        self.titleBar.setFixedHeight(height)
        self.hBoxLayout.insertSpacing(0, 0)
        self.widgetLayout.setContentsMargins(0, height, 0, 0)
        self.show()

    def doubleclick(self):
        row = self.keytable.currentRow()
        name: str = self.keytable.item(row, 0).text()
        name = name.strip()
        if not name:
            return
        light_chart = self.ChartMdiAreaWidget.current_chart_widget
        if "." in name:
            light_chart.replace_symbol(
                self.ChartMdiAreaWidget.FuturesInterface.main_window.tq_api.contract_set(name, light_chart.cycle))
        else:
            indclsname = self.keytable.item(row, 1).text()
            indcls = getattr(IndicatorClass, indclsname).value
            light_chart._add_indicator(indcls, name)
        self.close()

    def keyPressEvent(self, QKeyEvent):
        if QKeyEvent.key() == Qt.Key_Enter or QKeyEvent.key() == 16777220:
            if self.symboledit.text():
                if self.keytable.rowCount() > 0:
                    self.doubleclick()
            else:
                self.close()
        elif QKeyEvent.key() == Qt.Key_Down:
            if self.keytable.rowCount() > 1:
                row = self.keytable.currentRow()
                self.keytable.selectRow(min(row+1, self.keytable.rowCount()))
        elif QKeyEvent.key() == Qt.Key_Up:
            if self.keytable.rowCount() > 1:
                row = self.keytable.currentRow()
                self.keytable.selectRow(max(row-1, 0))
        elif QKeyEvent.key() == Qt.Key_Left or QKeyEvent.key() == Qt.Key_Right:
            self.symboledit.setFocus()
            self.symboledit.setCursorPosition(len(self.symboledit.text()))

    def closeEvent(self, e) -> None:
        self.ChartMdiAreaWidget.mdi.keyon = True
        return super().closeEvent(e)
        # self.marketwin.keyon = True  # 打开键盘精灵时为false，关闭时要赋值true，避免多次打开键盘精灵


class MyQLineEdit(LineEdit):
    def __init__(self, keywin: KeyElfWindow_):
        super().__init__()
        self.setFixedHeight(28)
        self.keywin = keywin
        self.df = keywin.AllMarkeContractDf
        self.keytable = keywin.keytable
        self.contract_name = self.df.contract_name.apply(lambda x: x.lower())
        self.contract_info = self.df.contract_info
        self.inddf = keywin.IndDf
        self.ind_name = keywin.IndDf.ind_name.apply(lambda x: x.lower())
        self.ind_info = keywin.IndDf.ind_info.apply(lambda x: x.lower())
        self.textChanged.connect(self.textChang)

    def textChang(self):
        text = self.text()
        text = text.lower()
        if " " in text:
            text = text.strip()
            self.setText(text)
        if text:
            items1 = self.df[self.contract_name.str.contains(
                text)].values.tolist()
            if not items1:
                items1 = self.df[self.contract_info.str.contains(
                    text)].values.tolist()
            items2 = self.inddf[self.ind_name.str.contains(
                text)].values.tolist()
            if not items2:
                items2 = self.inddf[self.ind_info.str.contains(
                    text)].values.tolist()
            items = items1+items2
            if items:
                self.setData(items)
                self.keytable.selectRow(0)
                # self.end(True)
                # self.setCursorPosition(len(text))
                # self.setFocus()

                # cursor = self.cursor()
                return
        self.removeRow()

    def setData(self, items, reset=True):
        '''设置表格数据
        items : np.array or list
        reset : 是否重置'''
        if reset:
            self.removeRow()
        for item in items:
            row = self.keytable.rowCount()
            self.keytable.insertRow(row)
            for j in range(len(item)):
                item_ = QTableWidgetItem(str(item[j]))
                item_.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)  # 居中
                self.keytable.setItem(row, j, item_)

    def removeRow(self):
        """删除所有行"""
        count = self.keytable.rowCount()
        if count > 0:
            for row in range(count)[::-1]:
                self.keytable.removeRow(row)
