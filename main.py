import uvicorn
from fastapi import FastAPI
from spider import InfoSpider

### TODO: 两种请求方法如下    1. 根据编号查询   2. 根据qrcode解码值
"""
http://localhost:8080/item/C16781
http://localhost:8080/qrdecode/{on:SO24051710142,pc:C16780,pm:CL21A476MQYNNNE,qty:20,mc:null,cc:1,pdi:114326866,hp:0}
"""

app = FastAPI()


@app.get("/")
def read_root():
    print(app.openapi())
    return {"Hello": "World"}


# 根据编号查询（方便快速查询，后面应该有地方会用到）
@app.get("/item/{item_id}")
def read_item(item_id: str):
    return info.get_info(0, item_id)


# 根据解码值查询
@app.get("/qrdecode/{qrdecode_str}")
def read_item(qrdecode_str: str):
    return info.get_info(1, qrdecode_str)


if __name__ == "__main__":
    info = InfoSpider()
    uvicorn.run(app, host="0.0.0.0", port=8080)
