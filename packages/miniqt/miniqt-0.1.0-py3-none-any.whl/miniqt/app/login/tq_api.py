
from __future__ import annotations
from tqsdk import TqApi as tqapi
from tqsdk.objs import Quote
from typing import Optional, Any, Callable
from typing_extensions import Literal
from iteration_utilities import flatten
from dataclasses import dataclass
from pandas import DataFrame, merge, Series
from ...utils import MiniqtDataBase, Quout_Left_Dict, Quout_Right_Dict


class TqApiBase:
    api: tqapi
    data_lenght: int = 10000
    _exchange_id: list[str] = ["SHFE", "DCE", "CZCE", "CFFEX", "INE", "GFEX"]
    quote_table_name: list[str] = ["合约中文名", "交易所合约代码", "最新价", "买一价", "买一量",
                                   "卖一价", "卖一量", "涨停价", "跌停价", "涨跌", "涨跌幅", "成交量",
                                   "开盘价", "最高价", "最低价", "昨收盘价", "昨结算价", "价格变动单位"]
    mini_quote_table_name: list[str] = ["代码", "最新价", "涨跌幅"]
    quote_table_file: list[str] = ["instrument_name", "instrument_id", "last_price", "bid_price1", "bid_volume1",
                                   "ask_price1", "ask_volume1", "upper_limit", "lower_limit", "volume",
                                   "open", "highest", "lowest", "pre_close", "pre_settlement", "price_tick"]
    mini_quote_table_file: list[str] = ["instrument_id", "last_price", "open"]
    quote_table_update_file: list[str] = ["last_price", "bid_price1", "bid_volume1", "ask_price1",
                                          "ask_volume1", "volume", "open", "highest", "lowest"]
    mini_quote_table_update_file: list[str] = ["last_price", "open"]
    quote_left_dict = Quout_Left_Dict
    quote_left_dict_update_file: list[str] = list(Quout_Left_Dict.keys())[:20]
    quote_right_dict = Quout_Right_Dict
    quote_right_dict_update_file: list[str] = list(
        Quout_Right_Dict.keys())[:10]

    # 主力合约
    _main_contract: Optional[list[str]] = None
    _main_contract_quote: dict[str, Quote] = {}
    # 夜盘主力合约
    _main_contract_night: Optional[list[str]] = None
    _main_contract_night_quote: dict[str, Quote] = {}
    # 主连合约
    _cont_contract: Optional[list[str]] = None
    _cont_contract_quote: dict[str, Quote] = {}
    # 指数合约
    _index_contract: Optional[list[str]] = None
    _index_contract_quote: dict[str, Quote] = {}

    @property
    def exchange_id(self) -> list[str]:
        """交易所"""
        return self._exchange_id

    @property
    def main_contract(self) -> list[str]:
        """主力合约"""
        if MiniqtDataBase.isupdate:
            main_contract = []
            for id in self._exchange_id:
                main_contract.append(
                    self.api.query_cont_quotes(exchange_id=id))
            self._main_contract = list(flatten(main_contract))

            MiniqtDataBase.set_value("main_contract", self._main_contract)
        else:
            self._main_contract = MiniqtDataBase.get_value("main_contract")

        if not self._main_contract_quote:
            for contract in self._main_contract:
                self._main_contract_quote.update(
                    {contract: self.api.get_quote(contract)})
        return self._main_contract

    def contract_info_df(self, atr: str) -> DataFrame:
        if not hasattr(self, f"_{atr}_df"):
            contract_dict: dict = getattr(self, f"_{atr}_quote")
            _id, name = [], []
            for _, quote in contract_dict.items():
                name.append(quote.instrument_name)
                _id.append(quote.instrument_id)
            return DataFrame(dict(contract_name=_id, contract_info=name))
        return getattr(self, f"_{atr}_df")

    @property
    def main_contract_night(self):
        """夜盘主力合约"""
        if not self._main_contract_night:
            main_contract_night = []
            for id in self._exchange_id:
                main_contract_night.append(
                    self.api.query_cont_quotes(exchange_id=id, has_night=True))
            self._main_contract_night = list(flatten(main_contract_night))
        return self._main_contract_night

    @property
    def cont_contract(self):
        """主连合约"""
        if not self._cont_contract:
            cont_contract = []
            for id in self.exchange_id:
                cont_contract.append(self.api.query_quotes(
                    ins_class="CONT", exchange_id=id))
            self._cont_contract = list(flatten(cont_contract))
        return self._cont_contract

    @property
    def index_contract(self):
        "指数合约"
        if not self._index_contract:
            index_contract = []
            for id in self.exchange_id:
                index_contract.append(self.api.query_quotes(
                    ins_class="INDEX", exchange_id=id))
            self._index_contract = list(flatten(index_contract))
        return self._index_contract


class TqApi(TqApiBase):
    """天勤api及数据功能
    """

    def __init__(self, name: str, api: tqapi) -> None:
        self.api = api
        self.account_name = name
        self.quote_table_update_file_index: list[int] = [
            self.quote_table_file.index(file) if i < 5 else self.quote_table_file.index(file)+2 for i, file in enumerate(self.quote_table_update_file)]
        self.quote_table_update_file_index.insert(5, 9)
        self.quote_table_update_file_index.insert(6, 10)
        self.mini_quote_table_update_file_index = [1, 2]
        # self.api.query_symbol_ranking
        # CFFEX: 中金所 * SHFE: 上期所 * DCE: 大商所 * CZCE: 郑商所 * INE: 能源交易所(原油) * GFEX: 广州期货交易所

        # self.api.get_quote
        # ["合约中文名", "合约代码", "最新价", "买一价", "买一量",
        #  "卖一价", "卖一量", "涨停价", "跌停价", "涨跌", "涨跌幅", "成交量",
        #  "开盘价", "最高价", "最低价", "昨收盘价", "昨结算价", "价格变动单位"]
        # ["instrument_name", "instrument_id", "last_price", "bid_price1", "bid_volume1",
        #  "ask_price1", "ask_volume1", "upper_limit", "lower_limit", "", "", "volume",
        #  "open", "highest", "lowest", "pre_close", "pre_settlement", "price_tick"]
        # self.api.get_quote_list
        # self.api.get_kline_serial
        # self.api.get_tick_serial
        # self.api.get_trading_calendar
        # self.api.get_account
        # self.api.get_position
        # self.api.create_task
        # self.api.register_update_notify
        # self.api.query_cont_quotes
        # self.api.query_symbol_info
        # self.api.query_quotes

    def get_quote_datas(self, name: str = "", mini: bool = False) -> list[list[Any]]:
        """ # 获取行情数据

        >>> 获取["instrument_name", "instrument_id", "last_price", "bid_price1", "bid_volume1",
            "ask_price1", "ask_volume1", "upper_limit", "lower_limit", "volume",
            "open", "highest", "lowest", "pre_close", "pre_settlement", "price_tick"]行情数据
            对"涨跌"和"涨跌幅"进行计算，并返回最新数据

        Args:
            >>> name (str, optional): 合约组合的名称. Defaults to "".

        Returns:
            >>> list[list[Any]]
        """
        contract = getattr(self, name)
        files = self.mini_quote_table_file if mini else self.quote_table_file
        # contract = getattr(self, name)
        if contract:
            contract_dict: dict = getattr(self, f"_{name}_quote")

            datas = []
            # for symbol in contract:
            for _, quote in contract_dict.items():
                # quote = contract_dict.get(symbol)
                data = []
                for file in files:
                    d = getattr(quote, file)
                    if d != d or not d or d == float("nan"):
                        d = 0.
                    elif isinstance(d, float):
                        d = round(d, 2)
                    data.append(d)
                if mini:
                    if data[1] and data[2]:
                        t1 = data[1]-data[2]
                        t2 = 100.*t1/data[2]
                    else:
                        t2 = 0.
                    data[2] = round(t2, 2)
                else:
                    if data[2] and data[10]:
                        t1 = data[2]-data[10]
                        t2 = 100.*t1/data[10]
                    else:
                        t1, t2 = 0., 0.
                    data.insert(9, round(t1, 2))
                    # data = list(map(str, data))
                    data.insert(10, round(t2, 2))  # f"{t2:.2f}%")
                datas.append(data)
            return datas

    def update_quote_datas(self, vertical_contract: list[str] = None, name: str = "", mini: bool = False) -> list[list[float]]:
        """ # 更新行情数据

        >>> 获取["last_price", "bid_price1", "bid_volume1", "ask_price1",
            "ask_volume1", "volume", "open", "highest", "lowest"]行情数据
            对"涨跌"和"涨跌幅"进行计算，并返回最新数据

        Args:
            >>> vertical_contract (list[str], optional): 行情界面可视的合约. Defaults to None.
                name (str, optional): 更新合约组合的名称. Defaults to "".

        Returns:
            >>> list[list[float]]
        """
        _files = self.mini_quote_table_update_file if mini else self.quote_table_update_file
        contract_dict: dict = getattr(self, f"_{name}_quote")
        datas = []
        for symbol in vertical_contract:
            # for symbol, quote in contract_dict.items():
            quote = contract_dict.get(symbol)
            data = []
            for file in _files:
                d = getattr(quote, file)

                if d != d or not d or d == float("nan"):
                    d = 0.
                elif isinstance(d, float):
                    d = round(d, 2)
                data.append(d)
            if mini:
                if data[0] and data[1]:
                    t1 = data[0]-data[1]
                    t2 = 100.*t1/data[1]
                else:
                    t2 = 0.
                data[1] = round(t2, 2)
            else:
                if data[0] and data[6]:
                    t1 = data[0]-data[6]
                    t2 = 100.*t1/data[6]
                else:
                    t1, t2 = 0., 0.
                data.insert(5, round(t1, 2))
                # data = list(map(str, data))
                data.insert(6, round(t2, 2))  # f"{t2:.2f}%")
            datas.append(data)
        return datas

    def contract_set(self, symbol: str, duration_seconds: int) -> ContractDataSet | str:
        try:
            quote = self.api.get_quote(symbol)
            kline = self.api.get_kline_serial(
                symbol, duration_seconds, self.data_lenght)
            tick = self.api.get_tick_serial(symbol)
        except Exception as e:
            return e
        return ContractDataSet(self.api, symbol, duration_seconds, quote, kline, tick)

    def contract_set_replace(self, contract_set: ContractDataSet, symbol: str, duration_seconds: int) -> ContractDataSet:
        if contract_set.symbol != symbol:
            return self.contract_set(symbol, duration_seconds)
        else:
            if contract_set.duration_seconds != duration_seconds:
                kline = self.api.get_kline_serial(
                    symbol, duration_seconds, self.data_lenght)
                contract_set.kline = kline
                contract_set.duration_seconds = duration_seconds
            return contract_set

    @property
    def wait_update(self) -> bool:
        return self.api.wait_update(deadline=60)

    def close(self) -> None:
        self.api.close()

    def copy(self) -> TqApi:
        self.api.is_changing
        return TqApi(self.api.copy())

    def __eq__(self, other: TqApi) -> bool:
        if not isinstance(other, TqApi):
            return False
        return self.account_name == other.account_name

    # def _query_cont_quotes


@dataclass
class ContractDataSet:
    api: tqapi
    symbol: str
    duration_seconds: int
    quote: Quote
    kline: DataFrame
    tick: DataFrame

    def __post_init__(self):
        self._df = self.kline.copy()
        self._df.drop(index=self._df.shape[0]-1, inplace=True)
        self._candles_params: dict = {}
        self._default_lenght = len(self._df)
        self._params_lenght: int = min(100, self._default_lenght)
        self._candles_style: Literal["Candlestick", "Heikin_Ashi_Candles",
                                     "Linear_Regression_Candles"] = "Candlestick"
        self._is_candles_style: bool = False
        self._follow_kline: bool = False
        # self._candles_func: Callable = None

    @property
    def lenght(self) -> int:
        """Kline数据长度"""
        return self.data.shape[0]

    @property
    def params_lenght(self) -> int:
        """指标计算中截取数据的最大长度"""
        return self._params_lenght

    @params_lenght.setter
    def params_lenght(self, value: int) -> None:
        value = abs(value)+100
        self._params_lenght = max(value, self._params_lenght)

    def set_candles_style(self, style: str):
        self._candles_style = style
        self._is_candles_style = style != "Candlestick"

    def candles_func(self, data: DataFrame) -> Callable:
        return getattr(data.ta, self._candles_style)

    def candles_data(self, data: DataFrame, follow: bool = True) -> DataFrame:
        if self._is_candles_style and self._follow_kline and follow:
            return getattr(data.ta, self._candles_style)(**self._candles_params)
        return data

    def candles_kline(self, data: DataFrame) -> DataFrame:
        if self._is_candles_style:
            return getattr(data.ta, self._candles_style)(**self._candles_params)
        return data

    def get_data(self, follow: bool = True) -> DataFrame:
        """合并后的数据,用于指标计算\\
        _follow_kline为真是返回风格K线数据\\
        反之返回原始K线"""
        data = merge(self._df, self.kline, how="outer")
        data = self.candles_data(data, follow)
        return data[['datetime', 'open', 'high', 'low', 'close', 'volume']]

    def get_update_data(self, lenght: int = 0, follow: bool = True) -> DataFrame:
        """返回截取后的kline,用于指标计算

        # arg:
            >>> lenght (int) : 数据停止更新到最新数据的K线数, default 0"""
        lenght = min([self._params_lenght+lenght, self._default_lenght])
        data = self.kline.iloc[-lenght:]
        data.reset_index(drop=True, inplace=True)
        data = self.candles_data(data, follow)
        return data[['datetime', 'open', 'high', 'low', 'close', 'volume']]

    @property
    def all_kline(self) -> DataFrame:
        """全部K线数据,返回原始K线或风格K线\\
        is_candles_style="Candlestick"时返回原始K线数据\\
        反之,返回风格K线数据"""
        data = merge(self._df, self.kline, how="outer")
        data = self.candles_kline(data)
        data['time'] = data.datetime
        return data[['time', 'open', 'high', 'low', 'close', 'volume']]

    def update_kline(self, lenght: int = 0) -> DataFrame:
        """返回截取后的kline,用于K线更新

        # arg:
            >>> lenght (int) : 数据停止更新到最新数据的K线数, default 0"""
        lenght = min([self._params_lenght+lenght, self._default_lenght])
        data = self.kline.iloc[-lenght:]
        data.reset_index(drop=True, inplace=True)
        data = self.candles_kline(data)
        data["time"] = data.datetime
        return data[['time', 'open', 'high', 'low', 'close', 'volume']]

    @property
    def is_quote_changing(self) -> bool:
        """quote最新价是否有更新"""
        return self.api.is_changing(self.quote, "last_price")

    @property
    def is_kline_changing(self) -> bool:
        """k线周期是否有更新"""
        return self.api.is_changing(self.kline, "datetime")

    def is_changing(self, arg: Literal["quote", "kline", "tick"], key: str) -> bool:
        """对quote, kline, tick关键字段key判断是否有更新"""
        return self.api.is_changing(getattr(self, arg), key)

    @property
    def wait_update(self) -> bool:
        """
        >>> return self.api.wait_update(deadline=60)"""
        return self.api.wait_update(deadline=60)

    @property
    def candles_params(self) -> dict:
        return self._candles_params

    @candles_params.setter
    def candles_params(self, value: dict):
        self._candles_params = value

    def __imul__(self, other: ContractDataSet) -> ContractDataSet:
        other._candles_params = self._candles_params
        other._default_lenght = self._default_lenght
        other._params_lenght = self._params_lenght
        other._candles_style = self._candles_style
        other._is_candles_style = self._is_candles_style
        other._follow_kline = self._follow_kline
        return other

    def __eq__(self, other: ContractDataSet) -> bool:
        if not isinstance(other, ContractDataSet):
            return False
        return self.symbol == other.symbol and self.duration_seconds == other.duration_seconds
