import requests
from lxml import etree  # 对已经获得的数据作预处理
import re


class InfoSpider:
    def __init__(self):
        print("init")

    # 搜索页面
    def search_spider(self, url):
        headers = {
            "User_Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36"
        }
        res = requests.get(url, headers=headers).text
        data = etree.HTML(res)
        lists = data.xpath(
            '/html/body/div[7]/div/form/div[4]/div[1]/div[1]/div[4]/table/tbody/tr[1]/td/div[2]/div/div[1]/div[1]/ul[1]/li[1]/a/@href')
        # print(lists[0])
        return lists[0]

    # 元器件详情页面
    def page_spider(self, url):
        # 浏览器类型 模拟浏览器请求
        headers = {
            "User_Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36"
        }
        res = requests.get(url, headers=headers).text
        data = etree.HTML(res)

        # 具体信息获取
        info_dic = {
            '品牌名称': data.xpath('//div/div/main/div/div[1]/div/div[1]/div[1]/div[2]/div[3]/ul[1]/li[3]/a/text()')[0],
            '商品型号': data.xpath('//div/div/main/div/div[1]/div/div[1]/div[1]/div[2]/div[3]/ul[1]/li[4]/span/text()')[
                0],
            '商品编号': data.xpath('//div/div/main/div/div[1]/div/div[1]/div[1]/div[2]/div[3]/ul[1]/li[5]/span/text()')[
                0],
            '参数值': data.xpath('//div[1]/div/main/div/div[1]/div/div[1]/div[1]/div[2]/div[3]/ul[1]/li[1]/p/text()')[
                0], '商品封装':
                data.xpath('//div[1]/div/main/div/div[1]/div/div[1]/div[1]/div[2]/div[3]/ul[1]/li[6]/span/text()')[0],
            '商品毛重': data.xpath('//div/div/main/div/div[1]/div/div[1]/div[1]/div[2]/div[3]/ul[1]/li[8]/p[2]/text()')[
                0]}

        # print(lists[0])  # 类  0  1 2 3 4 5
        return info_dic

    # 二维码字符串
    def decoder(self, str):
        # 定义一个正则表达式来匹配'pc'后面的值
        pattern = r"pc:([^,}]+)"

        # 使用re.search()函数来查找匹配的值
        match = re.search(pattern, str)
        # print(match.group(1))
        return match.group(1)

    # 返回结果
    def get_info(self, option, data):
        # 1 qrdecode
        # 0 items
        if option:
            data = self.decoder(data)  # 解析编号出来
        search_url = 'https://so.szlcsc.com/global.html?k=' + str(data) + '&hot-key=AFC01-S24FCA-00&searchSource='
        # page_url = 'https://item.szlcsc.com/3266968.html?fromZone=s_s__%2522C2930025%2522'
        page_url = self.search_spider(search_url)
        # print(page_url)
        return self.page_spider(page_url)


if __name__ == "__main__":
    info = InfoSpider()
    code = info.get_info(1, "{on:SO24051710142,pc:C16780,pm:CL21A476MQYNNNE,qty:20,mc:null,cc:1,pdi:114326866,hp:0}")
    info.get_info(0, "C16780")
    print(code)
