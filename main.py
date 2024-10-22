import uvicorn
from fastapi import FastAPI
from spider import InfoSpider

### TODO: 两种请求方法如下    1. 根据编号查询   2. 根据qrcode解码值
"""
http://localhost:8080/item/C16781
http://localhost:8080/qrdecode/{on:SO24051710142,pc:C16780,pm:CL21A476MQYNNNE,qty:20,mc:null,cc:1,pdi:114326866,hp:0}
"""

app = FastAPI()
info = InfoSpider()

@app.get("/")
def get_test():
    print(app.openapi())
    return {"Hello": "World"}


# 根据编号查询（方便快速查询，后面应该有地方会用到）
@app.get("/item/{item_id}")
def get_info(item_id: str):
    return info.get_info(0, item_id)


# 根据解码值查询
@app.get("/qrdecode/{qrdecode_str}")
def get_info(qrdecode_str: str):
    return info.get_info(1, qrdecode_str)


# # 根据url查询
# @app.get("/url/")
# def get_info(url: str):
#     return info.get_info(2, url)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
