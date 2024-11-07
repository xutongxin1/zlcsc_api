import requests
from lxml import etree  # 对已经获得的数据作预处理
import re
import json
import urllib.parse
import re

from eda_svg import pcb_svg, process_svgs


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


def get_product_parameters(code):
    if not code.xpath('//div/div/main/div/div[1]/div/div[1]/div[2]/div/section'):
        return None
    section_element = code.xpath('//div/div/main/div/div[1]/div/div[1]/div[2]/div/section')[0]
    features = extract_features_from_etree(section_element)
    product_parameters = "；".join([f"{key}：{value}" for key, value in features.items()])
    product_parameters += "；"
    return product_parameters


class InfoSpider:
    errorMessage: str = "无法搜索到该器件"

    def __init__(self):
        print("init")

    # 从搜索页面获取第一个元器件的详情页面
    def search_page_spider(self, CID):
        url = 'https://so.szlcsc.com/global.html?k=' + str(CID)
        headers = {
            "Referer": "https://so.szlcsc.com/",
            "User_Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36"
        }
        res = requests.get(url, headers=headers).text
        data = etree.HTML(res)
        lists = data.xpath(
            '/html/body/div[7]/div/form/div[4]/div[1]/div[1]/div[4]/table/tbody/tr[1]/td/div[2]/div/div[1]/div[1]/ul[1]/li[1]/a/@href')
        # print(lists[0])
        if len(lists) == 0:  # 如果没这个链接
            return None
        return lists[0]

    # 元器件详情页面信息爬取
    def component_page_spider(self, page_url, CID):

        # 浏览器类型 模拟浏览器请求
        headers = {
            "User_Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36"
        }
        res = requests.get(page_url, headers=headers).text
        data = etree.HTML(res)

        # 首先确定这个信息是否正确
        for index in range(4, 8):
            if data.xpath(
                    f'/html/body/div/div/main/div/div[1]/div/div[1]/div[1]/div[2]/div[3]/ul[1]/li[{index}]/span/text()')[
                0] == CID:
                break
            if index == 6:
                self.errorMessage = "在搜索页面中无法找到该器件"
                return None

        # print(etree.tostring(data, pretty_print=True).decode())
        # 读取商品参数

        info_dic = {}
        # 其他具体信息获取
        detail = data.xpath('//div/div/main/div/div[1]/div/div[1]/div[1]/div[2]/div[3]')[0]
        lis = detail.xpath('//li[@class="flex mt-[16px]"]')
        for li in lis:
            # 获取标签元素（可能是<p>或<span>）
            label_elem = li.xpath('.//*[contains(@class, "text-[#69788A] w-[70px]")]')[0]
            label = ''.join(label_elem.xpath('.//text()')).strip()

            # 获取值部分的所有文本，排除标签文本
            all_texts = li.xpath('.//text()')
            label_texts = label_elem.xpath('.//text()')
            value_texts = [t.strip() for t in all_texts if t.strip() and t not in label_texts]
            value = ''.join(value_texts).strip()

            # 将结果添加到字典
            if label == "网友设计参考":
                continue
            info_dic[label] = value

        product_parameters = get_product_parameters(data)
        if product_parameters is not None:
            info_dic['商品参数'] = product_parameters
        else:
            info_dic['商品参数'] = "参数完善中"

        info_dic['数据手册'] = data.xpath('//div/div/main/div/div[1]/div/div[1]/div[3]/div/div/div/a[2]')[0].attrib[
            'href']
        info_dic['数据手册名称'] = decode_filename_from_url(
            data.xpath('//div/div/main/div/div[1]/div/div[1]/div[3]/div/div/div/a[2]')[0].attrib['href'])

        return info_dic

    def component_picture_spider(self, PID: str):
        url = 'https://item.szlcsc.com/product/jpg_' + str(PID) + '.html'
        headers = {
            "User_Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36"
        }
        res = requests.get(url, headers=headers).text
        data = etree.HTML(res)
        # print(etree.tostring(data, pretty_print=True).decode())
        img_links = []
        section_element = data.xpath('/html/body/div/div/div/div/section/div/div[1]/ul')[0]
        if len(section_element) == 0:
            return None
        for ul in section_element:
            # 在每个 ul 下查找 img 标签，并提取 src 属性
            img_src = ul.xpath(".//img/@src")
            img_links.extend(img_src)
        return img_links

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
        CID: str = ""
        if option == 1:  # 如果使用的是二维码输入
            CID = self.decode_RWM(data)  # 解析编号出来
        elif option == 0:
            CID = data

        # else:
        #     component_page_url = data
        # Input URL

        component_page_url = self.search_page_spider(CID)
        if component_page_url is None:  # 检查链接是否存在
            self.errorMessage = "在搜索页面中无法找到该器件"
            return None
        if not component_page_url.startswith("https://item.szlcsc.com/"):
            self.errorMessage = "搜索失败，意外错误"
            return None

        # Using regex to extract the digits before '.html'
        match = re.search(r'/(\d+)\.html', component_page_url)

        # Extracted number
        PID = match.group(1) if match else None

        print(PID)
        component_info = self.component_page_spider(component_page_url, CID)
        if component_info is None:
            return None
        picture_info = self.component_picture_spider(PID)
        if picture_info is None:
            component_info['图片链接'] = "无图片"
        else:
            component_info['图片链接'] = picture_info

        sch_svg_code, pcb_svg_code = process_svgs(CID)
        if sch_svg_code is None:
            component_info['sch_svg'] = "未绘制库"
        else:
            component_info['sch_svg'] = sch_svg_code
        if pcb_svg_code is None:
            component_info['pcb_svg'] = "未绘制库"
        else:
            component_info['pcb_svg'] = pcb_svg_code

        return component_info


if __name__ == "__main__":
    info = InfoSpider()
    code = info.main_getInfo(1,
                             "{on:SO24051710142,pc:C16780,pm:CL21A476MQYNNNE,qty:20,mc:null,cc:1,pdi:114326866,hp:0}")
    info.main_getInfo(0, "C16780")
    print(code)
