import asyncio
from asyncio import ProactorEventLoop

import uvicorn
from fastapi import FastAPI, HTTPException
from uvicorn import Config, Server

from spider import InfoSpider
from playwright.sync_api import sync_playwright

### TODO: 两种请求方法如下    1. 根据编号查询   2. 根据qrcode解码值
"""
http://localhost:8080/item/C16133
http://localhost:8080/qrdecode/{on:SO24051710142,pc:C16780,pm:CL21A476MQYNNNE,qty:20,mc:null,cc:1,pdi:114326866,hp:0}
"""

app = FastAPI()
info = InfoSpider()


@app.get("/")
def get_test():
    print(app.openapi())
    return {"Hello": "World"}


# 根据编号查询（方便快速查询，后面应该有地方会用到）
@app.get("/item/{CID}")
def get_info(CID: str):
    result = info.main_getInfo(0, CID)
    if result is None:
        raise HTTPException(status_code=406, detail=info.errorMessage)
    return result


# 根据解码值查询
@app.get("/qrdecode/{qrdecode_str}")
def get_info(qrdecode_str: str):
    result = info.main_getInfo(1, qrdecode_str)
    if result is None:
        raise HTTPException(status_code=406, detail=info.errorMessage)
    return result


# 根据url查询
@app.get("/component_picture/{PID}")
def get_info(PID: str):
    result = info.component_picture_spider(PID)
    if result is None:
        raise HTTPException(status_code=406, detail=info.errorMessage)
    return result


class ProactorServer(uvicorn.Server):
    def run(self, sockets=None):
        loop = ProactorEventLoop()
        asyncio.set_event_loop(loop)  # since this is the default in Python 3.10, explicit selection can also be omitted
        asyncio.run(self.serve(sockets=sockets))


if __name__ == '__main__':
    config = uvicorn.Config(app=app, host="0.0.0.0", port=8000, reload=True)
    server = ProactorServer(config=config)
    server.run()

