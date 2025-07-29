import asyncio
from asyncio import ProactorEventLoop

import uvicorn
from fastapi import FastAPI, HTTPException
from starlette.responses import RedirectResponse
from uvicorn import Config, Server
# 添加缓存支持
from functools import lru_cache
from spider import InfoSpider
from playwright.sync_api import sync_playwright

### TODO: 两种请求方法如下    1. 根据编号查询   2. 根据qrcode解码值
"""
http://localhost:8000/item/C16133
http://localhost:8000/qrdecode/{on:SO24051710142,pc:C16780,pm:CL21A476MQYNNNE,qty:20,mc:null,cc:1,pdi:114326866,hp:0}
http://127.0.0.1:8000/url/C8734
"""
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
app = FastAPI()
info = InfoSpider()


@app.get("/url/{cid}")
async def redirect_to_item(cid: str):
    """
    接收CID参数，调用search_page_spider函数获取URL，然后重定向
    使用LRU缓存提高性能，避免重复查询相同的CID

    参数:
    - cid: 组件ID，如 C1792111

    返回:
    - 重定向到对应的商品页面
    """
    try:
        # 输入验证：确保CID格式正确（可选）
        if not cid.startswith('C') or len(cid) < 2:
            raise HTTPException(status_code=400, detail="CID格式不正确，应该以C开头")

        # 调用带缓存的函数获取URL
        target_url,__ = info.cached_search_page_spider(cid)

        # 检查返回的URL是否有效
        if not target_url:
            raise HTTPException(status_code=404, detail=f"未找到CID {cid} 对应的链接")

        # 验证URL格式（可选）
        if not target_url.startswith(('http://', 'https://')):
            raise HTTPException(status_code=500, detail="获取到的URL格式不正确")

        # 使用302重定向到目标URL
        return RedirectResponse(url=target_url, status_code=302)

    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        # 处理其他异常
        raise HTTPException(status_code=500, detail=f"处理请求时出错: {str(e)}")

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

if __name__ == '__main__':
   uvicorn.run(app='main:app', host="0.0.0.0", port=8000, reload=True)

