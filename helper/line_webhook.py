'''
Author: kevincnzhengyang kevin.cn.zhengyang@gmail.com
Date: 2025-08-26 18:14:39
LastEditors: kevincnzhengyang kevin.cn.zhengyang@gmail.com
LastEditTime: 2025-08-26 18:14:53
FilePath: /mss_chuanyin/app/webhook.py
Description: 

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''
from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/line/webhook")
async def line_webhook(request: Request):
    body = await request.json()
    print("收到 LINE Webhook:", body)

    # 取出 userId
    if "events" in body and len(body["events"]) > 0:
        source = body["events"][0]["source"]
        if "userId" in source:
            print("用户 ID:", source["userId"])

    return {"status": "ok"}