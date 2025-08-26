'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-08-24 08:47:24
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-08-26 16:10:19
FilePath: /mss_diting/app/diting/quote_futu.py
Description: Futu行情引擎

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''

import asyncio, os
import pandas as pd
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv
from futu import OpenQuoteContext, SubType

from .quote_base import BaseQuoteEngine
from .db_sqlite import get_rules
from .models import QuoteOHLC


# 加载环境变量
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=BASE_DIR / ".." / ".env")
FUTU_API_HOST = os.getenv("FUTU_API_HOST", "127.0.0.1")
FUTU_API_PORT = int(os.getenv("FUTU_API_PORT", "21111"))
FUTU_INTERVAL = int(os.getenv("FUTU_INTERVAL", "60"))  # 行情轮询间隔，单位秒

class FutuEngine(BaseQuoteEngine):
    def __init__(self):
        super().__init__("FutuEngine")
        self._symbols = set()
        self._ctx = None

    def _load_symbols(self) -> set:
        rules = get_rules(only_valid=True)
        symbols = set()
        for rule in rules:
            # logger.info(f"[{self.name}] Loaded rule: {rule['id']} {rule['symbol']} {rule['brokers']}")
            if 'FUTU' in rule['brokers'].upper().split(','):
                symbols.add(rule['symbol'])
        return symbols
    
    def _subscribe(self, symbols: set):
        if symbols and self._ctx:
            sub_list = list(symbols)
            ret, err = self._ctx.subscribe(sub_list, [SubType.QUOTE])
            if ret == 0:
                logger.info(f"[{self.name}] Subscribed to {sub_list}")
            else:
                logger.error(f"[{self.name}] Subscription error: {err}")
        else:
            logger.warning(f"[{self.name}] No symbols to subscribe")
    
    def start(self, loop: asyncio.AbstractEventLoop):
        if self._running:
            logger.warning(f"[{self.name}] Engine already running")
            return
        super().start(loop)
        self._ctx = OpenQuoteContext(host=FUTU_API_HOST, port=FUTU_API_PORT)
        self._symbols = self._load_symbols()
        logger.info(f"[{self.name}] Loaded {self._symbols} from rules")
        self._subscribe(self._symbols)

    def stop(self):
        if not self._running:
            logger.warning(f"[{self.name}] Engine not running")
            return
        if self._ctx:
            self._ctx.close()
            self._ctx = None
        super().stop()
        logger.info(f"[{self.name}] Engine stopped")

    async def loop(self):
        # 动态加载规则对应的股票列表并进行订阅
        symbols = self._load_symbols()
        new_symbols = symbols - self._symbols   # 只订阅新增的股票
        if new_symbols:
            logger.info(f"[{self.name}] New symbols to subscribe: {new_symbols}")
            self._subscribe(new_symbols)
            self._symbols.update(new_symbols)

        if not self._symbols:
            logger.warning(f"[{self.name}] No symbols to fetch, sleeping 5s")
            await asyncio.sleep(5)
            return
        
        if not self._ctx:
            logger.error(f"[{self.name}] Quote context not initialized")
            await asyncio.sleep(5)
            return
        
        ret, data = self._ctx.get_stock_quote(list(symbols))
        if ret == 0 and isinstance(data, pd.DataFrame) and not data.empty:
            logger.debug(f"[{self.name}] Fetched {len(data)} quotes")

            quotes = []
            for _, row in data.iterrows():
                # print(f"[{self.name}] Quote: {row}")
                quotes.append(QuoteOHLC(
                    symbol=row['code'],
                    open=row['open_price'],
                    high=row['high_price'],
                    low=row['low_price'],
                    close=row['last_price'],
                    pct_chg=row['last_price'] / row['prev_close_price'] * 100 - 100,
                    pct_amp=row['high_price'] / row['low_price'] * 100 - 100,
                    volume=int(row['volume'])
                ))
            self.check_rules(quotes)
        else:
            logger.error(f"[{self.name}] Fetch error: {data}")
        # 等待下一个轮询周期
        await asyncio.sleep(FUTU_INTERVAL)
