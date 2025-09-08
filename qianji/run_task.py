import os, qlib
import pandas as pd
from loguru import logger
from dotenv import load_dotenv
from pathlib import Path
from qlib.constant import REG_CN
from concurrent.futures import ThreadPoolExecutor

from core.workflow import TaskWorkflowQLib
from core.task_model import load_tasks

# 加载环境变量
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=BASE_DIR / ".env")
LOG_FILE = os.getenv("LOG_FILE", "qianji.log")
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")
DATA_DIR = os.path.expanduser(os.getenv("DATA_DIR", "~/Quanter/qlib_data"))
RECS_DIR = os.path.join(DATA_DIR, "recs")

# 初始化路径
os.makedirs(RECS_DIR, exist_ok=True)

# 记录日志到文件，日志文件超过500MB自动轮转
logger.add(LOG_FILE, level=LOG_LEVEL, rotation="50 MB", retention=5)

# 初始化QLib
qlib.init(provider_uri=DATA_DIR, region=REG_CN)


def _execute_task(t):
    TaskWorkflowQLib(DATA_DIR, RECS_DIR).run(
        t['task_id'], t['model'], t['instrument'], 
        t['start'], t['end'])

def run_tasks() -> None:
    res, tasks = load_tasks()
    if not res or 0 == len(tasks):
        logger.error("加载任务文件失败！")
        return
    
    # 多任务并行执行
    with ThreadPoolExecutor(max_workers = len(tasks)) as executor:
        executor.map(_execute_task, tasks)
