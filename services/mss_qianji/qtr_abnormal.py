'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-09-12 18:04:49
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-10-14 11:01:15
FilePath: /miaosuan/services/mss_qianji/qtr_abnormal.py
Description: 市场异常交易监控规则

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''
import json
import pandas as pd
from qlib.data import D
from datetime import datetime, timedelta
from loguru import logger


from config.settings import settings
from datamodels.dm_rule import Rule
from datamodels.dm_equity import Equity
from localdb.db_qianshou import get_equities
from localdb.db_diting import get_rules_by_symbol_rule, add_rule, update_rule


ABNR_RULE = "__ABNR_RULE"


def _update_equity(rec: dict) -> None:
    # 准备新的规则
    rule_defs = {"logic": "OR",
                 "conditions": [
                    # 成交量大于2倍MA5
                    {"field": "volume", "op": ">=", "value": rec['$HLY_VMA5_II']},
                    # 单日波动大于5%
                    {"field": "pct_amp", "op": ">=", "value": 5.0},
                    # 价格高于散逸区上限
                    {"field": "high", "op": ">=", "value": rec['$HLY_ESC_UPPER']},
                    # 价格低于散逸区下限
                    {"field": "low", "op": "<=", "value": rec['$HLY_ESC_LOWER']},
                    # 价格高于引力区上限且涨幅大于3%
                    {"logic": "AND", 
                    "conditions": [
                        {"field": "high", "op": ">", "value": rec['$HLY_ATT_UPPER']},
                        {"field": "pct_chg", "op": ">=", "value": 3.0},
                    ]},
                    # 价格低于引力区下限且跌幅大于3%
                    {"logic": "AND", 
                    "conditions": [
                        {"field": "low", "op": "<", "value": rec['$HLY_ATT_LOWER']},
                        {"field": "pct_chg", "op": "<=", "value": -3.0},
                    ]},
                 ]}

    # 获取已有的规则
    row = get_rules_by_symbol_rule(ABNR_RULE, rec['instrument'])
    if row is None:
        rid = add_rule(Rule(name=ABNR_RULE,
                            symbol=rec['instrument'],
                            brokers='FUTU',
                            rule_json=json.dumps(rule_defs),
                            webhook_url=f'http://localhost:{settings.API_PORT}/chuanyin/notify',
                            tag='重大异常交易信号'))
    else:
        rid = update_rule(rule_id=row['id'], 
                          rule=Rule(name=ABNR_RULE,
                                    symbol=rec['instrument'],
                                    brokers='FUTU',
                                    rule_json=json.dumps(rule_defs),
                                    webhook_url=f'http://localhost:{settings.API_PORT}/chuanyin/notify',
                                    tag='重大异常交易信号'))
    logger.info(f"更新监控规则{rec['instrument']}@{rid}:{rule_defs}")

def update_rule_of_equities() -> None:
    # 获取当前星期天数
    today = datetime.today()
    weekday = today.weekday()
    if weekday > 4:
        # weekend
        logger.info(f"周末不需要进行规则监控{weekday}")
        return
    if weekday == 0:
        # 周一，取上周五的数据
        daystr = (today - timedelta(days=3)).strftime("%Y-%m-%d")
    else:
        # 周二到周五，取前一天数据
        daystr = (today - timedelta(days=1)).strftime("%Y-%m-%d")
    
    logger.info(f"更新规则@{daystr}")

    # 获取所有标的股票
    rows = get_equities()
    if 0 == len(rows):
        logger.info(f"没有关注的股票")
        return
    symbols = []
    for e in [Equity(**row) for row in rows]:
        symbols.append(e.to_futu_symbol())
    
    # 加载标的股票的技术指标
    df = D.features(instruments=symbols, 
                    fields=['$ATR14', '$HLY_VMA5_II',
                            '$HLY_ATT_UPPER', '$HLY_ATT_LOWER', 
                            '$HLY_ESC_UPPER', '$HLY_ESC_LOWER'], 
                    start_time=daystr, 
                    end_time=daystr)
    if len(df) == 0:
        logger.error(f"{symbols}没有参考技术指标@{daystr}")
        return
    df = df.reset_index()
    
    # 逐个更新规则
    for r in df.to_dict(orient='records'):
        _update_equity(r)
