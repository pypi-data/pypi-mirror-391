import time
from typing import Callable
import threading

import pandas as pd
from pandas import DataFrame
from xtquant import xtdata

from .event import Event, EventEngine, EVENT_TIMER
from .event.event_type import EVENT_ALL_TICK


class MarketEngine:
    """行情引擎: 实时行情推送服务"""

    def __init__(self, event_engine: EventEngine | None = None, is_verbose: bool = False, output: Callable = print):

        if event_engine is None:
            event_engine = EventEngine(interval=3)
        self.event_engine = event_engine

        if is_verbose:
            pd.set_option('expand_frame_repr', False)  # 当列太多时不换行
            pd.set_option('display.max_rows', 5000)  # 最多显示数据的行数

        self.is_verbose = is_verbose
        self.output = output

        # 订阅标的列表
        self.subscribed_xt_symbols: set[str] = set()
        self._lock = threading.Lock()

        self.event_engine.register(EVENT_TIMER, self.on_timer)

    def subscribe_all(self, callback: Callable):
        """订阅全市场"""

        def on_all_tick(event: "Event"):
            df: DataFrame = event.edata
            callback(df)

        # 注册市场数据处理器
        self.event_engine.register(EVENT_ALL_TICK, on_all_tick)

    def subscribe(self, xt_symbols: str | list[str], callback: Callable):
        """订阅标的"""

        def func(event: Event):
            data_dict = event.edata

            callback(data_dict)

        if isinstance(xt_symbols, str):
            xt_symbols = [xt_symbols]

        with self._lock:
            for xt_symbol in xt_symbols:
                if xt_symbol not in self.subscribed_xt_symbols:
                    self.subscribed_xt_symbols.add(xt_symbol)

                    event_type = f"{EVENT_ALL_TICK}{xt_symbol}"
                    self.event_engine.register(event_type, func)

                    self.output(fr"订阅标的：{xt_symbol}")

    def unsubscribe(self, xt_symbols: str | list[str]):
        """取消订阅"""
        if isinstance(xt_symbols, str):
            xt_symbols = [xt_symbols]

        with self._lock:
            for xt_symbol in xt_symbols:
                if xt_symbol in self.subscribed_xt_symbols:
                    self.subscribed_xt_symbols.discard(xt_symbol)
                    self.output(fr"取消订阅标的：{xt_symbol}")

    def get_subscribed(self) -> list[str]:
        """获取当前订阅列表"""
        with self._lock:
            return sorted(self.subscribed_xt_symbols)

    def subscribe_sector(self, sector_name: str):
        """todo: 订阅板块所有成分股: """

    def on_timer(self, event: Event):
        """定时触发逻辑"""
        try:
            # 获取股票列表
            stock_list = xtdata.get_stock_list_in_sector("沪深A股")

            # 获取行情数据
            data_dict: dict = xtdata.get_full_tick(stock_list)

            # 转换为DataFrame
            data_df = (
                DataFrame.from_dict(data_dict)
                .T.reset_index()
                .rename(columns={'index': '证券代码'})
            )

            # 推送事件: 全市场数据
            event = Event(EVENT_ALL_TICK, data_df)
            self.event_engine.put(event)

            # 推送事件: 订阅标的数据
            self.handle_singe_tick(data_dict)

        except Exception as e:
            self.output(fr"获取全推行情数据失败：{e}")

    def handle_singe_tick(self, data_dict: dict):
        with self._lock:
            subs = list(self.subscribed_xt_symbols)

        for xt_symbol in subs:
            if xt_symbol in data_dict:
                tick_data = data_dict[xt_symbol]

                # 构造事件类型
                event_type = f"{EVENT_ALL_TICK}{xt_symbol}"
                event = Event(event_type, tick_data)
                self.event_engine.put(event)

    def run_forever(self):
        try:
            while True:
                time.sleep(2)
        except KeyboardInterrupt:
            self.output(f"行情引擎被手动中断")
        except Exception as e:
            self.output(f"行情引擎运行异常：{e}")
        finally:
            self.event_engine.stop()

    def start(self):
        # 启动事件引擎
        self.event_engine.start()
