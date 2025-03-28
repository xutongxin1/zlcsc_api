from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import logging
import asyncio

app = FastAPI()

# 配置 CORS
origins = [
    "*",  # 开发阶段允许所有来源，生产环境建议指定具体来源
    # "http://example.com",
    # "https://example.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # 允许的来源
    allow_credentials=True,
    allow_methods=["*"],              # 允许的 HTTP 方法
    allow_headers=["*"],              # 允许的 HTTP 头
)

# 配置日志记录
logging.basicConfig(
    filename="console_logs.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

@app.post("/log")
async def receive_log(request: Request):
    try:
        log_data = await request.json()
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    required_fields = {"method", "arguments", "timestamp", "url"}
    if not required_fields.issubset(log_data.keys()):
        raise HTTPException(status_code=400, detail="Missing fields in log data")

    method = log_data.get("method")
    arguments = log_data.get("arguments")
    timestamp = log_data.get("timestamp")
    url = log_data.get("url")

    log_message = f"URL: {url} | {method.upper()}: {' '.join(map(str, arguments))}"

    if method in ["log", "info"]:
        logging.info(log_message)
    elif method == "warn":
        logging.warning(log_message)
    elif method == "error":
        logging.error(log_message)
    elif method == "debug":
        logging.debug(log_message)
    else:
        logging.info(log_message)


    return JSONResponse(content={"status": "success"})