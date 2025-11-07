'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-08-24 08:47:24
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-11-07 08:45:17
FilePath: /miaosuan/services/mss_diting/quote_futu.py
Description: Futu行情引擎

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''

import asyncio, datetime
import pandas as pd
from loguru import logger
from futu import OpenQuoteContext, SubType, MarketState

from config.settings import settings
from .quote_base import BaseQuoteEngine
from datamodels.dm_quote import QuoteOHLC
from helper.ip_owner import is_chinese_mainland
from helper.account_futu import futu_sync_group
from helper.hist_futu import futu_update_daily
from services.mss_qianji.ta_daily import ta_daily_analysis


class FutuEngine(BaseQuoteEngine):
    def __init__(self):
        super().__init__("FUTU")
        self._symbols = set()
        self._ctx = None

    def _filter_symbols(self):
        logger.debug(f"[{self.name}] 过滤标的")
        # 因FutuOpenAPI的A股数据服务检查IP归属地，所以需要去掉SH和SZ
        if not is_chinese_mainland():
            symbols = []
            for s in self._symbols:
                if s.split(".")[0] in ["SH", "SZ"]:
                    continue
                else:
                    symbols.append(s)
            self._symbols = set(symbols)
            logger.info(f"[{self.name}] 过滤后标的{self._symbols}")
            # 重新订阅
            self._subscribe()
    
    def _subscribe(self):
        if self._symbols and self._ctx:
            self._ctx.unsubscribe_all()  # 取消所有订阅
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
        self._ctx = OpenQuoteContext(host=settings.FUTU_API_HOST, port=settings.FUTU_API_PORT)
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
            await asyncio.sleep(settings.QUOTE_INTERVAL*2)
            return
        
        if not self._ctx:
            logger.error(f"[{self.name}] 行情上下文未初始化")
            await asyncio.sleep(settings.QUOTE_INTERVAL*2)
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
            await asyncio.sleep(settings.QUOTE_INTERVAL*2)
            return
        logger.debug(f"[{self.name}] 尝试获取行情: {symbols}")
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
            await self.check_rules(quotes)
            logger.info(f"[{self.name}] 拉取行情成功: {len(data)}")
        else:
            logger.error(f"[{self.name}] 拉取行情失败: ret={ret}")

    async def update_daily(self):
        # 每日同步账户分组信息
        await futu_sync_group(settings.FUTU_GROUP_QUANTER)
        await futu_sync_group(settings.FUTU_GROUP_INDUSTRY, enable=False)

        # 每日更新时，重新加载规则与标的
        super()._load_symbols_rules()

        self._subscribe()     # 订阅最新标的

        # 下载历史数据，更新本地CSV文件
        futu_update_daily()

        # 更新分析报告
        await ta_daily_analysis()

    async def update_weekly(self):
        pass
