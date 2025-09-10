import os
import pandas as pd
from qlib.data import D


class DataManager:
    def __init__(self, data_dir: str, recs_dir: str):
        self.data_dir = data_dir
        self.recs_dir = recs_dir
        self.task_dir = ""
    
    def set_task_id(self, task_id: str):
        self.task_dir = os.path.join(self.recs_dir, task_id)
        os.makedirs(self.task_dir, exist_ok=True)

    def load_market_data(self, instrument: str, 
                         start_time: str, end_time: str):
        fields = ["$close", "$volume"]
        df = D.features(instruments=[instrument], 
                        fields=fields, 
                        start_time=start_time, 
                        end_time=end_time)
        return df

    def save_to_parquet(self, df: pd.DataFrame, name: str):
        df.to_parquet(os.path.join(self.task_dir, f"{name}.parquet"))
