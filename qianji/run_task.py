import pandas as pd
from core.workflow import TaskWorkflowQLib
from concurrent.futures import ThreadPoolExecutor

# 任务列表，每个任务独立 task_id 和数据文件
tasks = [
    {"task_id": "task_001", "file": "data/raw/AAPL.parquet"},
    {"task_id": "task_002", "file": "data/raw/MSFT.parquet"},
    {"task_id": "task_003", "file": "data/raw/GOOG.parquet"},
]

def run_task(t):
    df = pd.read_parquet(t["file"])
    workflow = TaskWorkflowQLib(t["task_id"], df)
    metrics = workflow.run()
    print(f"{t['task_id']} 完成, metrics={metrics}")

if __name__=="__main__":
    # 多任务并行执行
    with ThreadPoolExecutor(max_workers=len(tasks)) as executor:
        executor.map(run_task, tasks)
