'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-08-24 08:47:24
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-08-27 12:32:53
FilePath: /mss_diting/app/diting/quote_futu.py
Description: Futu行情引擎

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''

import asyncio, os
import pandas as pd
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv
from futu import OpenQuoteContext, SubType, MarketState

from .quote_base import BaseQuoteEngine
from .db_sqlite import get_rules
from .models import QuoteOHLC


# 加载环境变量
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=BASE_DIR / ".." / ".env")
FUTU_API_HOST = os.getenv("FUTU_API_HOST", "127.0.0.1")
FUTU_API_PORT = int(os.getenv("FUTU_API_PORT", "21111"))
QUOTE_INTERVAL = int(os.getenv("QUOTE_INTERVAL", "60"))  # 行情轮询间隔，单位秒

class FutuEngine(BaseQuoteEngine):
    def __init__(self):
        super().__init__("FUTU")
        self._symbols = set()
        self._ctx = None
    
    def _subscribe(self):
        if self._symbols and self._ctx:
            sub_list = list(self._symbols)
            ret, err = self._ctx.subscribe(sub_list, [SubType.QUOTE])
            if ret == 0:
                logger.info(f"[{self.name}] 实时订阅标的 {sub_list}")
            else:
                logger.error(f"[{self.name}] 实时订阅异常: {err}")
        else:
            logger.warning(f"[{self.name}] 没有标的可供订阅")
    
    def start(self, loop: asyncio.AbstractEventLoop):
        if self._running:
            logger.warning(f"[{self.name}] 已经在运行")
            return
        super().start(loop)
        self._ctx = OpenQuoteContext(host=FUTU_API_HOST, port=FUTU_API_PORT)
        logger.info(f"[{self.name}] Loaded {self._symbols} from rules")
        self._subscribe()

    def stop(self):
        if not self._running:
            logger.warning(f"[{self.name}] 未运行")
            return
        if self._ctx:
            self._ctx.close()
            self._ctx = None
        super().stop()
        logger.info(f"[{self.name}] 停止运行")

    async def loop(self):
        # 动态加载规则对应的股票列表并进行订阅
        if not self._symbols:
            logger.warning(f"[{self.name}] 没有任何标的")
            await asyncio.sleep(QUOTE_INTERVAL*2)
            return
        
        if not self._ctx:
            logger.error(f"[{self.name}] 行情上下文未初始化")
            await asyncio.sleep(QUOTE_INTERVAL*2)
            return
        
        # 检查是否是开市时间
        symbols = []
        ret, market_status = self._ctx.get_market_state(list(self._symbols))
        if ret == 0 and isinstance(market_status, pd.DataFrame) and not market_status.empty:
            # 获取所有股票的市场状态
            for _, row in market_status.iterrows():
                if row['market_state'] == MarketState.MORNING or row['market_state'] == MarketState.AFTERNOON:
                    symbols.append(row['code'])
        if not symbols:
            logger.warning(f"[{self.name}] 当前非交易时间 {self._symbols}")
            await asyncio.sleep(QUOTE_INTERVAL*2)
            return

        ret, data = self._ctx.get_stock_quote(symbols)
        if ret == 0 and isinstance(data, pd.DataFrame) and not data.empty:
            logger.debug(f"[{self.name}] 拉取行情 {len(data)} 条")

            quotes = []
            for _, row in data.iterrows():
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
            logger.error(f"[{self.name}] 拉取行情失败: {data}")
