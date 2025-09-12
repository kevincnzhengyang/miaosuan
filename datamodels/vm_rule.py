'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-09-12 21:20:30
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-09-12 21:20:50
FilePath: /miaosuan2/datamodels/vm_rule.py
Description: 

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''
import operator
from jsonschema import validate, ValidationError

# -------------------------
# 运算符
# -------------------------
OPS = {
    ">": operator.gt,
    "<": operator.lt,
    "=": operator.eq,
    ">=": operator.ge,
    "<=": operator.le,
    "!=": operator.ne
}

VALID_LOGICS = {"AND", "OR", "NOT"}

# 白名单（行情字段）
VALID_FIELDS = {"open", "high", "low", "close", "volume", "amplitude", "pct_change"}

# -------------------------
# JSON Schema 定义
# -------------------------
RULE_SCHEMA = {
    "type": "object",
    "anyOf": [
        # 条件节点
        {
            "properties": {
                "field": {"type": "string", "enum": list(VALID_FIELDS)},
                "op": {"type": "string", "enum": list(OPS.keys())},
                "value": {"type": ["number", "string", "boolean"]}
            },
            "required": ["field", "op", "value"],
            "additionalProperties": False
        },
        # 逻辑节点
        {
            "properties": {
                "logic": {"type": "string", "enum": list(VALID_LOGICS)},
                "conditions": {"type": "array", "items": {"$ref": "#"}}
            },
            "required": ["logic", "conditions"],
            "additionalProperties": False
        }
    ]
}

# -------------------------
# 校验函数
# -------------------------
def validate_rule(rule: dict) -> bool:
    try:
        validate(instance=rule, schema=RULE_SCHEMA)
    except ValidationError as e:
        raise ValueError(f"Invalid rule: {e.message}")
    return True
