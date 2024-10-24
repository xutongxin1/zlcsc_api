import requests
from lxml import etree  # 对已经获得的数据作预处理
import re
import json
import urllib.parse
import re

# 从元器件详情页面提取特征
def extract_features_from_etree(section_element):
    """
    Extract features from the given section element.

    Args:
        section_element (etree.Element): The section element from which to extract features.

    Returns:
        dict: A dictionary containing the extracted features.
    """
    features = {}
    # 找到所有 class 为 'ant-table-tbody' 的 tbody 元素
    tbodies = section_element.xpath(".//tbody[@class='ant-table-tbody']")
    for tbody in tbodies:
        # 找到所有 tr 元素
        trs = tbody.xpath(".//tr")
        for tr in trs:
            # 找到所有 td 元素
            tds = tr.xpath(".//td")
            if len(tds) >= 3:
                # 提取属性和参数值
                attribute_td = tds[1]
                value_td = tds[2]
                attribute = ''.join(attribute_td.itertext()).strip()
                value = ''.join(value_td.itertext()).strip()
                features[attribute] = value
    return features

# 从数据手册链接中提取文件名
def decode_filename_from_url(url):
    """
    Decode the filename from the given URL.

    Args:
        url (str): The URL from which to decode the filename.

    Returns:
        str: The decoded filename, or None if not found.
    """
    # 解析URL并提取查询参数
    parsed_url = urllib.parse.urlparse(url)
    query_params = urllib.parse.parse_qs(parsed_url.query)

    # 文件名在'response-content-disposition'参数中
    if 'response-content-disposition' in query_params:
        # 从content disposition中提取'filename'部分
        content_disposition = query_params['response-content-disposition'][0]
        filename = content_disposition.split('filename=')[-1]
        # 解码文件名
        decoded_filename = urllib.parse.unquote(filename)
        return decoded_filename
    else:
        return None

class InfoSpider:
    def __init__(self):
        print("init")

    # 从搜索页面获取第一个元器件的详情页面
    def search_page_spider(self, CID):
        url = 'https://so.szlcsc.com/global.html?k=' + str(CID) + '&hot-key=AFC01-S24FCA-00&searchSource='
        headers = {
            "User_Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36"
        }
        res = requests.get(url, headers=headers).text
        data = etree.HTML(res)
        lists = data.xpath(
            '/html/body/div[7]/div/form/div[4]/div[1]/div[1]/div[4]/table/tbody/tr[1]/td/div[2]/div/div[1]/div[1]/ul[1]/li[1]/a/@href')
        # print(lists[0])
        if len(lists) == 0:
            return None
        return lists[0]

    # 元器件详情页面信息爬取
    def component_page_spider(self, page_url):

        # 浏览器类型 模拟浏览器请求
        headers = {
            "User_Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36"
        }
        res = requests.get(page_url, headers=headers).text
        data = etree.HTML(res)
        # print(etree.tostring(data, pretty_print=True).decode())
        section_element = data.xpath('//div/div/main/div/div[1]/div/div[1]/div[2]/div/section')[0]

        features = self.extract_features_from_etree(section_element)

        productParameters = "；".join([f"{key}：{value}" for key, value in features.items()])
        productParameters += "；"
        print(productParameters)
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
                0],
            '数据手册': data.xpath('//div/div/main/div/div[1]/div/div[1]/div[3]/div/div/div/a[2]')[0].attrib['href'],
            '数据手册名称': self.decode_filename_from_url(
                data.xpath('//div/div/main/div/div[1]/div/div[1]/div[3]/div/div/div/a[2]')[0].attrib['href']),
            '商品详细': productParameters
        }

        # print(lists[0])  # 类  0  1 2 3 4 5
        return info_dic

    def component_picture_spider(self, CID):
        url = 'https://item.szlcsc.com/product/jpg_' + str(CID) + '.html'
        headers = {
            "User_Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36"
        }
        res = requests.get(url, headers=headers).text
        data = etree.HTML(res)
        # print(etree.tostring(data, pretty_print=True).decode())
        section_element = data.xpath('//div/div/main/div/div[1]/div/div[1]/div[2]/div/section')[0]

    # 二维码字符串解析出有效编号
    def decode_RWM(self, str):
        # 定义一个正则表达式来匹配'pc'后面的值
        pattern = r"pc:([^,}]+)"

        # 使用re.search()函数来查找匹配的值
        match = re.search(pattern, str)
        # print(match.group(1))
        return match.group(1)

    # 主函数，返回json结果
    def main_getInfo(self, option: int, data):
        # 1 qrdecode
        # 0 items
        CID: str = "C123131231"
        if option == 1:  # 如果使用的是二维码输入
            CID = self.decode_RWM(data)  # 解析编号出来
        elif option == 0:
            CID = data

        # else:
        #     page_url = data
        # Input URL

        page_url = self.search_page_spider(CID)
        if page_url is None:  # 检查链接是否存在
            return None
        if not page_url.startswith("https://item.szlcsc.com/"):
            return None
        url = "https://item.szlcsc.com/324135.html?fromZone=l_c__%2522catalog%2522"

        # Using regex to extract the digits before '.html'
        match = re.search(r'/(\d+)\.html', url)

        # Extracted number
        PID = match.group(1) if match else None

        print(page_url)
        pageInfo = self.component_page_spider(page_url)

        return pageInfo


if __name__ == "__main__":
    info = InfoSpider()
    code = info.main_getInfo(1,
                             "{on:SO24051710142,pc:C16780,pm:CL21A476MQYNNNE,qty:20,mc:null,cc:1,pdi:114326866,hp:0}")
    info.main_getInfo(0, "C16780")
    print(code)
