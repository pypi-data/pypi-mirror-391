from __future__ import annotations

# import pydirectinput
import qtawesome as qta
from PyQt5.QtCore import QObject, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtWidgets import QWidget, QPushButton
from functools import partial, reduce
from typing import Callable, Union, Any, Optional, Iterable
from tqsdk import TqApi
from enum import Enum
from dataclasses import dataclass
from itertools import cycle
import inspect
from .MiniqtDataBase import *
not_indicator_list = ["xsignals", "tsignals", "above", "below", "cross", "cross_up",
                      "cross_down", "strategy", "cdl_pattern", "cdl_z", "Any", "All",
                      "Where", 'line_trhend', "abc", "insidebar"]
# https://zhuanlan.zhihu.com/p/697127601


MiniqtDataBase = MiniqtDataBase()


class Api:
    pytdx_api = None
    tq_api: TqApi = None


class Constant(Enum):
    KeyAlpha = list(range(65, 91, 1))
    Alpha = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l',
             'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']


@dataclass
class _Cycles:
    S1: int = 1
    S3: int = 3
    S5: int = 5
    S10: int = 10
    S15: int = 15
    S30: int = 30
    M1: int = 60
    M3: int = 180
    M5: int = 300
    M10: int = 600
    M15: int = 900
    M30: int = 1800
    H1: int = 3600
    H2: int = 7200
    H4: int = 14400
    D1: int = 60*60*24
    _ALL: np.ndarray = np.array([1, 3, 5, 10, 15, 30, 60, 180, 300,
                                 600, 900, 1800, 3600, 7200, 14400, 60*60*24])

    def __post_init__(self):
        self._cyclestring = {}
        self.__dict__ = {k: v for k,
                         v in self.__dict__.items() if not k.startswith("_")}
        self._cyclestring: dict = {
            v: f"{k[1:]}{k[0]}" for k, v in self.__dict__.items()}
        self._check_dict: dict[str, set[int]] = {}
        self._cycle_lenght = len(self._ALL)

    @property
    def cyclestring(self) -> dict[int, str]:
        return self._cyclestring

    @property
    def check_dict(self) -> dict:
        return self._check_dict

    @check_dict.setter
    def check_dict(self, value: dict):
        self._check_dict.update(value)

    def create_multi_check(self, key: str):
        self._check_dict.update({key: set()})

    def delete_multi_check(self, key: str) -> set[int]:
        return self._check_dict.pop(key)

    def set_cycle(self, key, cycle) -> None:
        if key not in self._check_dict:
            self.create_multi_check(key)
        self._check_dict[key].add(cycle)

    def delete_cycle(self, key, cycle) -> None:
        self._check_dict[key] -= {cycle, }

    def get_multi_check(self, key: str) -> set[int]:
        if key not in self._check_dict:
            self.create_multi_check(key)
        return self._check_dict[key]


Cycles: _Cycles = _Cycles()


Colors: list[str] = ['fuchsia', 'lime', 'olive', 'blue', 'purple', 'silver', 'teal', 'aqua',
                     'green', 'maroon', 'navy', 'red']  # , 'yellow', 'white' , 'black', 'gray']


def get_colors() -> cycle:
    return cycle(Colors)


class QtColors(Enum):
    red = QBrush(QColor("red"))
    lime = QBrush(QColor("lime"))
    white = QBrush(QColor("white"))
    gold = QBrush(QColor("gold"))
    grey = QBrush(QColor("grey"))
    black = QBrush(QColor("black"))


class Icons:
    white = "white"
    black = "black"
    cyan = "cyan"
    color = "white"
    widgets: list[QPushButton] = []

    @classmethod
    def setColor(cls, dark: bool) -> Icons:
        cls.color = cls.white if dark else cls.black
        cls.setIcon()
        return cls

    @classmethod
    def addWidget(cls, widget: QPushButton):
        cls.widgets.append(widget)

    @classmethod
    def setIcon(cls):
        if cls.widgets:
            for widget in cls.widgets:
                widget.setIcon(getattr(Icons, widget.objectName())())

    @staticmethod
    def get_icon(names, **kwargs):
        return qta.icon(names, **kwargs)

    @classmethod
    def stock_line(cls):
        return qta.icon('ri.stock-line', color=cls.color)

    @classmethod
    def stock_fill(cls):
        return qta.icon('ri.stock-fill', color=cls.color)

    @classmethod
    def angle_up(cls):
        return qta.icon('fa.angle-up', color=cls.color)

    @classmethod
    def angle_down(cls):
        return qta.icon('fa.angle-down', color=cls.color)

    @classmethod
    def line_chart_line(cls):
        return qta.icon('ri.line-chart-line', color=cls.color)

    @classmethod
    def fa5s_minus(cls):
        return qta.icon('fa5s.minus', color=cls.color)

    @classmethod
    def window_maximize(cls):
        return qta.icon('fa5s.window-maximize', color=cls.color)

    @classmethod
    def color_mode(cls):
        return qta.icon('msc.color-mode', color=cls.color)

    @classmethod
    def recycle(cls):
        return qta.icon('mdi6.recycle', color=cls.color)


# def Timer(parent: QWidget, updatafunc, start: bool = True, time=0):
#     '''计时器'''
#     timer = QTimer(parent)
#     timer.timeout.connect(updatafunc)
#     if start:
#         timer.start(time)
#     return timer
class connec_thread(QThread):
    finished = pyqtSignal(list)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._parent = parent

    def run(self):
        self.finished.emit(self._parent.initWindow())


class WorkerThread(QThread):
    finished = pyqtSignal(list)

    def __init__(self, parent=None, func: Callable = None) -> None:
        super().__init__(parent)
        self.func = func

    def run(self):
        self.finished.emit(self.func())


class UpdateThread(QThread):
    finished = pyqtSignal(bool)

    def __init__(self, parent=None, func: Callable = None) -> None:
        super().__init__(parent)
        self.func = func

    def run(self):
        self.finished.emit(self.func())


def get_func_parameters(func: Callable) -> dict:
    return {k: v.default for k, v in inspect.signature(func).parameters.items() if k not in ["self", "kwargs"]}


def get_indicator_info() -> tuple[pd.DataFrame, dict[str, list[str]]]:
    name, info = [], []

    d = {}
    # for k, v in IndicatorClass.__members__.items():
    for k, v in vars(IndicatorClass).items():

        if not k.startswith("_"):
            value = []
            for k_, v_ in vars(v).items():
                if isinstance(v_, Callable) and not k_.startswith("_") and k_ not in not_indicator_list:
                    name.append(k_)
                    info.append(k)
                    value.append(k_)
            else:
                d.update({k: value})
    return pd.DataFrame(dict(ind_name=name, ind_info=info)), d


Indicator_Info, Indicator_Dict = get_indicator_info()


# def move_releas(pos):
#     x, y = pydirectinput.position()
#     pydirectinput.mouseDown(button=pydirectinput.LEFT)
#     pydirectinput.moveTo(x-pos, y)
#     pydirectinput.mouseUp(button=pydirectinput.LEFT)
#     pydirectinput.moveTo(x, y)
#     return True
Color = ["#FFFAFA", "#F8F8FF", "#F5F5F5", "#DCDCDC", "#FFFAF0", "#FDF5E6", "#FAF0E6", "#FAEBD7", "#FFEFD5",
         "#FFEBCD", "#FFE4C4", "#FFDAB9", "#FFDEAD", "#FFE4B5", "#FFF8DC", "#FFFFF0", "#FFFACD", "#FFF5EE",
         "#F0FFF0", "#F5FFFA", "#F0FFFF", "#F0F8FF", "#E6E6FA", "#FFF0F5", "#FFE4E1", "#FFFFFF", "#000000",
         "#2F4F4F", "#696969", "#708090", "#778899", "#BEBEBE", "#D3D3D3", "#191970", "#000080", "#6495ED",
         "#483D8B", "#6A5ACD", "#7B68EE", "#8470FF", "#0000CD", "#4169E1", "#0000FF", "#1E90FF", "#00BFFF",
         "#87CEEB", "#87CEFA", "#4682B4", "#B0C4DE", "#ADD8E6", "#B0E0E6", "#AFEEEE", "#00CED1", "#48D1CC",
         "#40E0D0", "#00FFFF", "#E0FFFF", "#5F9EA0", "#66CDAA", "#7FFFD4", "#006400", "#556B2F", "#8FBC8F",
         "#2E8B57", "#3CB371", "#20B2AA", "#98FB98", "#00FF7F", "#7CFC00", "#00FF00", "#7FFF00", "#00FA9A",
         "#ADFF2F", "#32CD32", "#9ACD32", "#228B22", "#6B8E23", "#BDB76B", "#EEE8AA", "#FAFAD2", "#FFFFE0",
         "#FFFF00", "#FFD700", "#EEDD82", "#DAA520", "#B8860B", "#BC8F8F", "#CD5C5C", "#8B4513", "#A0522D",
         "#CD853F", "#DEB887", "#F5F5DC", "#F5DEB3", "#F4A460", "#D2B48C", "#D2691E", "#B22222", "#A52A2A",
         "#E9967A", "#FA8072", "#FFA07A", "#FFA500", "#FF8C00", "#FF7F50", "#F08080", "#FF6347", "#FF4500",
         "#FF0000", "#FF69B4", "#FF1493", "#FFC0CB", "#FFB6C1", "#DB7093", "#B03060", "#C71585", "#D02090",
         "#FF00FF", "#EE82EE", "#DDA0DD", "#DA70D6", "#BA55D3", "#9932CC", "#9400D3", "#8A2BE2", "#A020F0",
         "#9370DB", "#D8BFD8", "#FFFAFA", "#EEE9E9", "#CDC9C9", "#8B8989", "#FFF5EE", "#EEE5DE", "#CDC5BF",
         "#8B8682", "#FFEFDB", "#EEDFCC", "#CDC0B0", "#8B8378", "#FFE4C4", "#EED5B7", "#CDB79E", "#8B7D6B",
         "#FFDAB9", "#EECBAD", "#CDAF95", "#8B7765", "#FFDEAD", "#EECFA1", "#CDB38B", "#8B795E", "#FFFACD",
         "#EEE9BF", "#CDC9A5", "#8B8970", "#FFF8DC", "#EEE8CD", "#CDC8B1", "#8B8878", "#FFFFF0", "#EEEEE0",
         "#CDCDC1", "#8B8B83", "#F0FFF0", "#E0EEE0", "#C1CDC1", "#838B83", "#FFF0F5", "#EEE0E5", "#CDC1C5",
         "#8B8386", "#FFE4E1", "#EED5D2", "#CDB7B5", "#8B7D7B", "#F0FFFF", "#E0EEEE", "#C1CDCD", "#838B8B",
         "#836FFF", "#7A67EE", "#6959CD", "#473C8B", "#4876FF", "#436EEE", "#3A5FCD", "#27408B", "#0000FF",
         "#0000EE", "#0000CD", "#00008B", "#1E90FF", "#1C86EE", "#1874CD", "#104E8B", "#63B8FF", "#5CACEE",
         "#4F94CD", "#36648B", "#00BFFF", "#00B2EE", "#009ACD", "#00688B", "#87CEFF", "#7EC0EE", "#6CA6CD",
         "#4A708B", "#B0E2FF", "#A4D3EE", "#8DB6CD", "#607B8B", "#C6E2FF", "#B9D3EE", "#9FB6CD", "#6C7B8B",
         "#CAE1FF", "#BCD2EE", "#A2B5CD", "#6E7B8B", "#BFEFFF", "#B2DFEE", "#9AC0CD", "#68838B", "#E0FFFF",
         "#D1EEEE", "#B4CDCD", "#7A8B8B", "#BBFFFF", "#AEEEEE", "#96CDCD", "#668B8B", "#98F5FF", "#8EE5EE",
         "#7AC5CD", "#53868B", "#00F5FF", "#00E5EE", "#00C5CD", "#00868B", "#00FFFF", "#00EEEE", "#00CDCD",
         "#008B8B", "#97FFFF", "#8DEEEE", "#79CDCD", "#528B8B", "#7FFFD4", "#76EEC6", "#66CDAA", "#458B74",
         "#C1FFC1", "#B4EEB4", "#9BCD9B", "#698B69", "#54FF9F", "#4EEE94", "#43CD80", "#2E8B57", "#9AFF9A",
         "#90EE90", "#7CCD7C", "#548B54", "#00FF7F", "#00EE76", "#00CD66", "#008B45", "#00FF00", "#00EE00",
         "#00CD00", "#008B00", "#7FFF00", "#76EE00", "#66CD00", "#458B00", "#C0FF3E", "#B3EE3A", "#9ACD32",
         "#698B22", "#CAFF70", "#BCEE68", "#A2CD5A", "#6E8B3D", "#FFF68F", "#EEE685", "#CDC673", "#8B864E",
         "#FFEC8B", "#EEDC82", "#CDBE70", "#8B814C", "#FFFFE0", "#EEEED1", "#CDCDB4", "#8B8B7A", "#FFFF00",
         "#EEEE00", "#CDCD00", "#8B8B00", "#FFD700", "#EEC900", "#CDAD00", "#8B7500", "#FFC125", "#EEB422",
         "#CD9B1D", "#8B6914", "#FFB90F", "#EEAD0E", "#CD950C", "#8B658B", "#FFC1C1", "#EEB4B4", "#CD9B9B",
         "#8B6969", "#FF6A6A", "#EE6363", "#CD5555", "#8B3A3A", "#FF8247", "#EE7942", "#CD6839", "#8B4726",
         "#FFD39B", "#EEC591", "#CDAA7D", "#8B7355", "#FFE7BA", "#EED8AE", "#CDBA96", "#8B7E66", "#FFA54F",
         "#EE9A49", "#CD853F", "#8B5A2B", "#FF7F24", "#EE7621", "#CD661D", "#8B4513", "#FF3030", "#EE2C2C",
         "#CD2626", "#8B1A1A", "#FF4040", "#EE3B3B", "#CD3333", "#8B2323", "#FF8C69", "#EE8262", "#CD7054",
         "#8B4C39", "#FFA07A", "#EE9572", "#CD8162", "#8B5742", "#FFA500", "#EE9A00", "#CD8500", "#8B5A00",
         "#FF7F00", "#EE7600", "#CD6600", "#8B4500", "#FF7256", "#EE6A50", "#CD5B45", "#8B3E2F", "#FF6347",
         "#EE5C42", "#CD4F39", "#8B3626", "#FF4500", "#EE4000", "#CD3700", "#8B2500", "#FF0000", "#EE0000",
         "#CD0000", "#8B0000", "#FF1493", "#EE1289", "#CD1076", "#8B0A50", "#FF6EB4", "#EE6AA7", "#CD6090",
         "#8B3A62", "#FFB5C5", "#EEA9B8", "#CD919E", "#8B636C", "#FFAEB9", "#EEA2AD", "#CD8C95", "#8B5F65",
         "#FF82AB", "#EE799F", "#CD6889", "#8B475D", "#FF34B3", "#EE30A7", "#CD2990", "#8B1C62", "#FF3E96",
         "#EE3A8C", "#CD3278", "#8B2252", "#FF00FF", "#EE00EE", "#CD00CD", "#8B008B", "#FF83FA", "#EE7AE9",
         "#CD69C9", "#8B4789", "#FFBBFF", "#EEAEEE", "#CD96CD", "#8B668B", "#E066FF", "#D15FEE", "#B452CD",
         "#7A378B", "#BF3EFF", "#B23AEE", "#9A32CD", "#68228B", "#9B30FF", "#912CEE", "#7D26CD", "#551A8B",
         "#AB82FF", "#9F79EE", "#8968CD", "#5D478B", "#FFE1FF", "#EED2EE", "#CDB5CD", "#8B7B8B", "#1C1C1C",
         "#363636", "#4F4F4F", "#696969", "#828282", "#9C9C9C", "#B5B5B5", "#CFCFCF", "#E8E8E8", "#A9A9A9",
         "#00008B", "#008B8B", "#8B008B", "#8B0000", "#90EE90"]


Quout_Left_Dict = {
    "ask_price5": "卖五价",
    "ask_price4": "卖四价",
    "ask_price3": "卖三价",
    "ask_price2": "卖二价",
    "ask_price1": "卖一价",
    "bid_price1": "买一价",
    "bid_price2": "买二价",
    "bid_price3": "买三价",
    "bid_price4": "买四价",
    "bid_price5": "买五价",
    "last_price": "最新价",
    "highest": "当日最高价",
    "lowest": "当日最低价",
    "open": "开盘价",
    "close": "收盘价",
    "average":  "当日均价",
    "volume": "成交量",
    "amount": "成交额",
    "open_interest": "持仓量",
    "settlement":  "结算价",
    "upper_limit":  "涨停价",
    "lower_limit":  "跌停价",
    "pre_open_interest":  "昨持仓量",
    "pre_settlement":  "昨结算价",
    "pre_close":  "昨收盘价",
    "price_tick":  "合约价格变动单位",
    "price_decs": "合约价格小数位数",
    "volume_multiple": "合约乘数",
    "max_limit_order_volume": "最大限价单手数",
    "max_market_order_volume": "最大市价单手数",
    "min_limit_order_volume": "最小限价单手数",
    "min_market_order_volume": "最小市价单手数",
    "underlying_symbol": "标的合约",

}

Quout_Right_Dict = {
    "ask_volume5": "卖五量",
    "ask_volume4": "卖四量",
    "ask_volume3": "卖三量",
    "ask_volume2": "卖二量",
    "ask_volume1": "卖一量",
    "bid_volume1": "买一量",
    "bid_volume2": "买二量",
    "bid_volume3": "买三量",
    "bid_volume4": "买四量",
    "bid_volume5": "买五量",
    "strike_price": "行权价",
    "ins_class": "合约类型",
    "instrument_id":  "合约代码",
    "instrument_name":  "合约中文名",
    "exchange_id": "交易所代码",
    "expired": "合约是否已下市",
    "trading_time":  "交易时间段",
    "expire_datetime": "到期具体日",  # ，以秒为单位的 timestamp 值
    "delivery_year": " 期货交割日年份",  # ，只对期货品种有效。期权推荐使用最后行权日年份
    "delivery_month":  "期货交割日月份",  # ，只对期货品种有效。期权推荐使用最后行权日月份
    "last_exercise_datetime": "期权最后行权日",  # ，以秒为单位的 timestamp 值
    "exercise_year": "期权最后行权日年份",  # ，只对期权品种有效。
    "exercise_month":  "期权最后行权日月份",  # ，只对期权品种有效。
    "option_class": "期权行权方式",  # ，看涨:'CALL'，看跌:'PUT'
    "exercise_type":  "期权行权方式",  # ，美式:'A'，欧式:'E'
    "product_id": "品种代码",
    "iopv": "ETF实时单位基金净值",
    "public_float_share_quantity": "日流通股数",  # ，只对证券产品有效。
    "stock_dividend_ratio": " 除权表",  # ["20190601,0.15","20200107,0.2"…]
    "cash_dividend_ratio": "除息表",  # ["20190601,0.15","20200107,0.2"…]
    "expire_rest_days":  "距离到期日的剩余天数",
    "commission": "手续费",
    "margin": "保证金",
}
