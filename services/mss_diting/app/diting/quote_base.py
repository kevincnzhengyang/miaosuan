'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-08-24 07:47:28
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-08-25 20:52:44
FilePath: /mss_diting/app/diting/quote_base.py
Description: 行情基类

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''


import asyncio, json, requests
from abc import ABC, abstractmethod
from loguru import logger
from typing import List

from .models import *
from .db_sqlite import add_trigger, get_rules
from .quote_rule import eval_rule

# ----------------- 引擎基类 -----------------
class BaseQuoteEngine(ABC):
    def __init__(self, name: str):
        self.name = name
        self._task = None
        self._running = False

    async def _safe_loop(self):
        logger.info(f"[{self.name}] Engine running...")
        while self._running:
            try:
                await self.loop()
            except Exception as e:
                logger.warning(f"[{self.name}] Error: {e}, restarting in 5s")
                await asyncio.sleep(5)
        logger.info(f"[{self.name}] Engine stopped")

    @abstractmethod
    async def loop(self):
        """子类必须实现行情轮询逻辑"""
        pass

    def start(self, loop: asyncio.AbstractEventLoop):
        if not self._running:
            logger.info(f"[{self.name}] Engine starting...")
            self._running = True
            self._task = loop.create_task(self._safe_loop())

    def stop(self):
        self._running = False
        if self._task:
            logger.info(f"[{self.name}] Engine stopping...")
            self._task.cancel()

    def is_running(self):
        return self._running and not self._task.done() if self._task else False
    
    def eval_rules_trigger(self, rules: List[dict], quote: QuoteOHLC):
        ohlc = quote.model_dump()
        for rule in rules:
            if eval_rule(rule["rule_json"], ohlc):
                logger.info(f"规则触发: {rule['name']} {quote.symbol} @ {ohlc}")
                trigger = Trigger(
                    rule_id=rule['id'],
                    symbol=quote.symbol,
                    message=f"规则触发: {rule['name']} {quote.symbol} @ {ohlc}",
                )
                add_trigger(trigger)
                # 这里可以添加调用 webhook + tag 的逻辑
                try:
                    payload = {
                        "rule_name": rule['name'],
                        "symbol": quote.symbol,
                        "ohlc": ohlc,
                        "tag": rule['tag'],
                    }
                    headers = {'Content-Type': 'application/json'}
                    response = requests.post(rule['webhook_url'], data=json.dumps(payload), headers=headers, timeout=5)
                    if response.status_code == 200:
                        logger.info(f"Webhook 调用成功: {rule['webhook_url']}")
                    else:
                        logger.error(f"Webhook 调用失败: {rule['webhook_url']} 状态码: {response.status_code}")
                except Exception as e:
                    logger.error(f"Webhook 调用异常: {e}")
            else:
                logger.debug(f"规则未触发: {rule['name']} {quote.symbol} @ {ohlc}")


    def check_rules(self, quotes: List[QuoteOHLC]):
        # 实时获得所有规则，防止运行期规则变更被忽略
        rows = get_rules(only_valid=True)
        if not rows:
            logger.warning("没有可用规则，跳过检查")
            return
        
        # 将规则按 symbol 分类
        rules = dict()
        for row in rows:
            rule = dict(row)
            # 将 rule_json 从字符串转换为字典
            rule["rule_json"] = json.loads(row["rule_json"])
            if rule["symbol"] in rules.keys():
                rules[rule["symbol"]].append(rule)
            else:
                rules[rule["symbol"]] = [rule]
        
        # 检查每个行情数据是否触发对应规则
        for quote in quotes:
            if quote.symbol in rules.keys():
                self.eval_rules_trigger(rules[quote.symbol], quote)
                