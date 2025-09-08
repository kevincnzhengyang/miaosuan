'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-09-08 09:57:41
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-09-08 10:24:04
FilePath: /miaosuan/qianji/core/task_model.py
Description: 

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''
import os, json
from typing import Tuple
from loguru import logger
from pathlib import Path
from dotenv import load_dotenv
from jsonschema import validate, ValidationError, SchemaError

# 加载环境变量
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=BASE_DIR / ".." / ".env")
TASK_FILE = os.getenv("TASK_FILE", "tasks.json")  # 任务定义文件


# -------------------------
# JSON Schema 定义
# -------------------------
_task_schema = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "task_id": {
                "type": "string",
                "pattern": "^task_\\d{3}$"  # 验证task_id格式为task_后跟3位数字
            },
            "model": {
                "type": "string"
            },
            "instrument": {
                "type": "string"
            },
            "start": {
                "type": "string",
                "format": "date"  # 验证日期格式YYYY-MM-DD
            },
            "end": {
                "type": "string",
                "format": "date"  # 验证日期格式YYYY-MM-DD
            }
        },
        "required": ["task_id", "model", "instrument", "start", "end"],  # 必需的字段
        "additionalProperties": False  # 不允许额外的属性
    }
}

def _validate_json(json_data) -> bool:
    """验证JSON数据是否符合schema"""
    try:
        validate(instance=json_data, schema=_task_schema)
        logger.error("✅ JSON数据验证成功！")
        return True
    except ValidationError as e:
        logger.error(f"❌ JSON数据验证失败: {e.message}")
        logger.error(f"   路径: {list(e.absolute_path)}")
        return False
    except SchemaError as e:
        logger.error(f"❌ Schema定义有误: {e}")
        return False

def load_tasks() -> Tuple[bool, list]:
    """验证JSON文件是否符合schema"""
    try:
        with open(TASK_FILE, 'r', encoding='utf-8') as file:
            json_data = json.load(file)
        
        return _validate_json(json_data), json_data
        
    except FileNotFoundError:
        logger.error(f"❌ 文件未找到: {TASK_FILE}")
        return False, []
    except json.JSONDecodeError as e:
        logger.error(f"❌ JSON格式错误: {e}")
        return False, []
