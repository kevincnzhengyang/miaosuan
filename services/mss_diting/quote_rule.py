'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-08-25 09:27:37
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-09-12 21:21:22
FilePath: /miaosuan2/services/mss_diting/quote_rule.py
Description: JSON 规则处理

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''
from datamodels.vm_rule import OPS

# -------------------------
# 规则执行函数
# -------------------------
def eval_rule(rule: dict, snapshot: dict) -> bool:
    # 条件节点
    if "field" in rule:
        field = rule["field"]
        op = OPS[rule["op"]]
        value = rule["value"]
        return op(snapshot[field], value)

    # 逻辑节点
    elif "logic" in rule:
        logic = rule["logic"].upper()
        results = [eval_rule(cond, snapshot) for cond in rule.get("conditions", [])]

        if logic == "AND":
            return all(results)
        elif logic == "OR":
            return any(results)
        elif logic == "NOT":
            if len(results) != 1:
                raise ValueError("NOT must have exactly one condition")
            return not results[0]
    else:
        raise ValueError("Invalid rule format")
    return False
