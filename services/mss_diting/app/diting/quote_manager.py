'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-08-24 09:53:45
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-08-25 20:25:28
FilePath: /mss_diting/app/diting/quote_manager.py
Description: 行情管理器

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''

import asyncio, threading
from loguru import logger

from .quote_base import BaseQuoteEngine

# ---------- 管理者 ----------
class QuoteManager:
    def __init__(self):
        self.engines = {}
        self.loop: asyncio.AbstractEventLoop | None = None

    def register(self, engine: BaseQuoteEngine):
        self.engines[engine.name] = engine

    def start_all(self):
        if self.loop is None:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            logger.info("Event loop created for QuoteManager")
        
        for e in self.engines.values():
            e.start(self.loop)
        
        threading.Thread(target=self.loop.run_forever, daemon=True).start()

    def stop_all(self):
        for e in self.engines.values():
            e.stop()
        
        if self.loop and self.loop.is_running():
            self.loop.stop()
            self.loop.close()
            self.loop = None
            logger.info("Event loop closed for QuoteManager")

    def status(self):
        return {name: eng.is_running() for name, eng in self.engines.items()}


# 初始化管理者
manager = QuoteManager()
