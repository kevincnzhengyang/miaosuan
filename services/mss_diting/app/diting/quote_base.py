'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-08-24 07:47:28
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-08-27 12:25:20
FilePath: /mss_diting/app/diting/quote_base.py
Description: 行情基类

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''


import os, asyncio, json, requests
from abc import ABC, abstractmethod
from loguru import logger
from typing import List
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime, timedelta

from .models import *
from .db_sqlite import add_trigger, get_rules
from .quote_rule import eval_rule


# 加载环境变量
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=BASE_DIR / ".." / ".env")
QUOTE_INTERVAL = int(os.getenv("QUOTE_INTERVAL", "60"))  # 行情轮询间隔，单位秒
COOLING_CYCLE = int(os.getenv("COOLING_CYCLE", "10"))  # 规则冷却周期，单位次数

# ----------------- 引擎基类 -----------------
class BaseQuoteEngine(ABC):
    def __init__(self, name: str):
        self.name = name
        self._task = None
        self._running = False
        self._symbols = set()
        self._rules = dict()
        self._update_counter = 0
        self._updated = "1970-01-01 00:00:00"  # 上次规则更新的时间

    def _load_symbols_rules(self):
        last_update = self._updated
        self._updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 加载所有规则
        self._rules = dict()
        for row in get_rules(only_valid=True):
            rule = dict(row)
            # 将 rule_json 从字符串转换为字典
            rule["rule_json"] = json.loads(row["rule_json"])
            # 给触发标记一个初始值
            rule["_invoked"] = False
            if rule["symbol"] in self._rules.keys():
                self._rules[rule["symbol"]].append(rule)
            else:
                self._rules[rule["symbol"]] = [rule]
        self._symbols = set(self._rules.keys())
        logger.info(f"[{self.name}] 更新规则与标的@ {last_update}")

    
            
    async def _safe_loop(self):
        logger.info(f"[{self.name}] 开始运行...")
        while self._running:
            try:
                self._update_counter += 1
                # 冷却周期到期，进行更新
                if self._update_counter >= COOLING_CYCLE:
                    self._update_counter = 0
                    self._load_symbols_rules()
                await self.loop()
            except Exception as e:
                logger.warning(f"[{self.name}] 异常: {e}")
            await asyncio.sleep(QUOTE_INTERVAL)
        logger.info(f"[{self.name}] 运行已停止")

    @abstractmethod
    async def loop(self):
        """子类必须实现行情轮询逻辑"""
        pass

    def start(self, loop: asyncio.AbstractEventLoop):
        if not self._running:
            logger.info(f"[{self.name}] 开始运行...")
            self._load_symbols_rules()  # 初始加载规则
            self._running = True
            self._task = loop.create_task(self._safe_loop())

    def stop(self):
        self._running = False
        if self._task:
            logger.info(f"[{self.name}] 尝试停止...")
            self._task.cancel()

    def is_running(self):
        return self._running and not self._task.done() if self._task else False

    def eval_rules_trigger(self, rules: List[dict], quote: QuoteOHLC):
        # 评估规则是否触发
        ohlc = quote.model_dump()
        for rule in rules:
            if rule.get("_invoked", False):
                # 规则在冷却周期内，跳过
                logger.debug(f"规则冷却中，跳过: {rule['name']} {quote.symbol} @ {ohlc}")
                continue
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
                        "name": rule['name'],
                        "symbol": quote.symbol,
                        "ohlc": ohlc,
                        "tag": rule['tag'],
                    }
                    headers = {'Content-Type': 'application/json'}
                    response = requests.post(rule['webhook_url'], data=json.dumps(payload), headers=headers, timeout=5)
                    if response.status_code == 200:
                        logger.info(f"Webhook 调用成功: {rule['webhook_url']}")
                        rule['_invoked'] = True  # 标记为已触发
                    else:
                        logger.error(f"Webhook 调用失败: {rule['webhook_url']} 状态码: {response.status_code}")
                except Exception as e:
                    logger.error(f"Webhook 调用异常: {e}")
            else:
                logger.debug(f"规则未触发: {rule['name']} {quote.symbol} @ {ohlc}")


    def check_rules(self, quotes: List[QuoteOHLC]):
        # 检查每个行情数据是否触发对应规则
        for quote in quotes:
            if quote.symbol in self._symbols:
                self.eval_rules_trigger(self._rules[quote.symbol], quote)
                