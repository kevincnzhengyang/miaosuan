
import json, sqlite3
from typing import Any
from loguru import logger

from config.settings import settings
from datamodels.dm_rule import Rule, Trigger
from datamodels.vm_rule import validate_rule


def add_rule(rule: Rule) -> Any:
    # 插入数据库前校验规则
    validate_rule(json.loads(rule.rule_json)) 

    conn = sqlite3.connect(settings.DB_FILE)
    cur = conn.cursor()
    cur.execute("INSERT INTO rules(name,symbol,brokers,rule_json,webhook_url,tag,note,enabled,updated_at) VALUES(?,?,?,?,?,?,?,?,CURRENT_TIMESTAMP)",
                (rule.name, rule.symbol, rule.brokers, rule.rule_json, rule.webhook_url, rule.tag, rule.note, int(rule.enabled)))
    conn.commit()
    rule_id = cur.lastrowid
    conn.close()
    return rule_id

def get_rules(only_valid: bool = True) -> list[Any]:
    conn = sqlite3.connect(settings.DB_FILE)
    conn.row_factory = sqlite3.Row
    if only_valid:
        rows = conn.execute("SELECT * FROM rules WHERE enabled=1").fetchall()
    else:
        rows = conn.execute("SELECT * FROM rules").fetchall()
    conn.close()
    return rows

def get_updated_rules(since: str) -> list[Any]:
    conn = sqlite3.connect(settings.DB_FILE)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM rules WHERE updated_at > ? AND enabled=1", (since,)).fetchall()
    conn.close()
    return rows

def get_rules_by_symbol(symbol: str, only_valid: bool = True) -> list[Any]:
    conn = sqlite3.connect(settings.DB_FILE)
    conn.row_factory = sqlite3.Row
    if only_valid:
        rows = conn.execute("SELECT * FROM rules WHERE symbol=? AND enabled=1", (symbol,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM rules WHERE symbol=?", (symbol,)).fetchall()
    conn.close()
    return rows

def get_rules_by_symbol_rule(rule: str, symbol: str, only_valid: bool = True) -> Any:
    conn = sqlite3.connect(settings.DB_FILE)
    conn.row_factory = sqlite3.Row
    if only_valid:
        rows = conn.execute("SELECT * FROM rules WHERE name=? AND symbol=? AND enabled=1", 
                            (rule, symbol,)).fetchone()
    else:
        rows = conn.execute("SELECT * FROM rules WHERE name=? AND symbol=?", 
                            (rule, symbol,)).fetchone()
    conn.close()
    return rows

def get_rule(rule_id: int) -> Any:
    conn = sqlite3.connect(settings.DB_FILE)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM rules WHERE id=?", (rule_id,)).fetchone()
    conn.close()
    return row

def update_rule(rule_id: int, rule: Rule) -> Any:
    # 插入数据库前校验规则
    validate_rule(json.loads(rule.rule_json)) 
    
    conn = sqlite3.connect(settings.DB_FILE)
    conn.execute("UPDATE rules SET name=?,symbol=?,brokers=?,rule_json=?,webhook_url=?,tag=?,note=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",
                 (rule.name, rule.symbol, rule.brokers, rule.rule_json, rule.webhook_url, rule.tag, rule.note, rule_id))
    conn.commit()
    conn.close()
    return rule_id

def delete_rule(rule_id: int) -> None:
    conn = sqlite3.connect(settings.DB_FILE)
    conn.execute("UPDATE rules SET enabled=0 WHERE id=?", (rule_id,))
    conn.commit()
    conn.close()

def purge_rule(rule_id: int) -> None:
    conn = sqlite3.connect(settings.DB_FILE)
    conn.execute("DELETE FROM rules WHERE id=?", (rule_id,))
    conn.commit()
    conn.close()

def add_trigger(trigger: Trigger) -> Any:
    conn = sqlite3.connect(settings.DB_FILE)
    cur = conn.cursor()
    cur.execute("INSERT INTO triggers(rule_id,symbol,message) VALUES(?,?,?)",
                (trigger.rule_id, trigger.symbol, trigger.message))
    conn.commit()
    trigger_id = cur.lastrowid
    conn.close()
    return trigger_id

def get_triggers(limit: int = 100) -> list[Any]:
    conn = sqlite3.connect(settings.DB_FILE)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM triggers ORDER BY ts DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return rows

def get_triggers_by_rule_id(rule_id: int, limit: int = 100) -> list[Any]:
    conn = sqlite3.connect(settings.DB_FILE)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM triggers WHERE rule_id=? ORDER BY ts DESC LIMIT ?", (rule_id, limit)).fetchall()
    conn.close()
    return rows

def get_triggers_by_symbol(symbol: str, limit: int = 100) -> list[Any]:
    conn = sqlite3.connect(settings.DB_FILE)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM triggers WHERE symbol=? ORDER BY ts DESC LIMIT ?", (symbol, limit)).fetchall()
    conn.close()
    return rows

def delete_trigger(trigger_id: int) -> None:
    conn = sqlite3.connect(settings.DB_FILE)
    conn.execute("DELETE FROM triggers WHERE id=?", (trigger_id,))
    conn.commit()
    conn.close()

def clear_triggers() -> None:
    conn = sqlite3.connect(settings.DB_FILE)
    conn.execute("DELETE FROM triggers")
    conn.commit()
    conn.close()
