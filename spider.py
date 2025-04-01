import requests
from lxml import etree  # 对已经获得的数据作预处理
import re
import json
import urllib.parse
import re

from playwright.sync_api import sync_playwright

from eda_svg import pcb_svg, process_svgs
from playwright.async_api import async_playwright


# 获取价格信息
def format_price_data(data_list):
    formatted_output = []
    for item in data_list:
        sp_number = item["spNumber"]
        product_price = item["productPrice"]

        # 按照要求格式化: "spNumber+：productPrice"
        formatted_line = f"{sp_number}+：{product_price}"
        formatted_output.append(formatted_line)

    # 用换行符连接所有行
    return "\n".join(formatted_output)


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
        match = re.search(r'([^/]+\.pdf)', url)
        if match:
            return match.group(1)
        else:
            return "数据手册《未知名称》"


def get_product_parameters(code):
    # if not code.xpath('//div/div/main/div/div[1]/div/div[1]/div[2]/div/section'):
    #     return None
    # section_element = code.xpath('//div/div/main/div/div[1]/div/div[1]/div[2]/div/section')[0]
    features = extract_features_from_etree(code)
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

        # with sync_playwright() as p:
        #     browser = p.chromium.launch()
        #     ua = (
        #         "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        #     )
        #     page = browser.new_page(user_agent=ua)
        #     page.goto(url, wait_until="domcontentloaded")
        #     print(page.title())
        #     html_content = page.content()
        #     browser.close()

        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
        }
        html_content = requests.get(url, headers=headers).text

        data = etree.HTML(html_content)
        pid = data.xpath('//div[@id="shop-list"]/table[1]/@pid')

        if pid:
            print(f"The pid value is: {pid[0]}")
            return "https://item.szlcsc.com/" + pid[0] + ".html", pid
        else:
            print("No pid found about CID: " + CID)
            return None, None

    # 元器件详情页面信息爬取
    def component_page_spider(self, page_url, CID):

        # with sync_playwright() as p:
        #     browser = p.chromium.launch()
        #     ua = (
        #         "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        #     )
        #     page = browser.new_page(user_agent=ua)
        #     page.goto(page_url, wait_until="domcontentloaded")
        #     print(page.title())
        #     html_content = page.content()
        #     browser.close()

        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
        }
        html_content = requests.get(page_url, headers=headers).text
        data = etree.HTML(html_content)

        # 首先确定这个信息是否正确,CID校验
        for index in range(0, 9):
            if index == 9:
                self.errorMessage = "在搜索页面中无法找到该器件"
                return None
            if not data.xpath(
                    f'/html/body/div[1]/div/main/div/div/section[1]/div[2]/div[3]/dl/div[{index}]/dd/text()'):
                continue
            if data.xpath(f'/html/body/div[1]/div/main/div/div/section[1]/div[2]/div[3]/dl/div[{index}]/dd/text()')[
                0] == CID:
                print("CID校验成功")
                break

        # print(etree.tostring(data, pretty_print=True).decode())
        # 读取商品参数

        info_dic = {}
        # 其他具体信息获取
        # detail = data.xpath('/html/body/div[1]/div/main/div/div/section[1]/div[2]/div[3]/dl')[0]
        lis = data.xpath('//div[@class="flex mt-[16px]"]')
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
        more_data = data.xpath('/html/body/script[1]')[0].text
        more_data = json.loads(more_data)
        info_dic["价格"] = format_price_data(
            more_data["props"]["pageProps"]["webData"]["productRecord"]["entireProductPriceList"])
        info_dic["库存"] = "广东仓：" + str(
            more_data["props"]["pageProps"]["webData"]["gdWarehouseStockNumber"]) + "\n江苏仓：" + str(
            more_data["props"]["pageProps"]["webData"]["jsWarehouseStockNumber"])
        un_water_mark_image_urls_str = more_data['props']['pageProps']['webData']['productRecord'][
            'luceneBreviaryImageUrls']
        un_water_mark_image_urls = un_water_mark_image_urls_str.split("\u003c$\u003e")
        info_dic['图片链接'] = un_water_mark_image_urls

        if '描述' not in info_dic:
            if more_data['props']['pageProps']['webData']['productRecord']['productName'] is not None:
                info_dic['描述'] = more_data['props']['pageProps']['webData']['productRecord']['productName']
        # 提取pdfFileUrl
        try:
            pdf_file_url = \
                more_data['props']['pageProps']['webData']['productRecord']['fileTypeVOList'][0]['detailVOList'][0][
                    'fileUrl']
        except:
            pdf_file_url = None
        if pdf_file_url is None:
            try:
                pdf_file_url = \
                    data.xpath('/html/body/div/div/main/div/div[1]/div/div[1]/div[3]/div/div/div/a[2]')[0].attrib[
                        'href']
                info_dic['数据手册名称'] = decode_filename_from_url(pdf_file_url)
                info_dic['数据手册'] = pdf_file_url.split('?')[0]
            except:
                info_dic['数据手册名称'] = ""
                info_dic['数据手册'] = ""
        # 提取unWaterMarkImageUrls，使用'$\u003e'作为分隔符
        else:
            info_dic['数据手册'] = "https://atta.szlcsc.com/" + pdf_file_url
            info_dic['数据手册名称'] = decode_filename_from_url(pdf_file_url)

        return info_dic

    def component_picture_spider(self, PID: str):
        url = 'https://item.szlcsc.com/product/jpg_' + str(PID) + '.html'

        # with sync_playwright() as p:
        #     browser = p.chromium.launch()
        #     ua = (
        #         "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        #     )
        #     page = browser.new_page(user_agent=ua)
        #     page.goto(url, wait_until="domcontentloaded")
        #     html_content = page.content()
        #     browser.close()
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
        }
        html_content = requests.get(url, headers=headers).text
        data = etree.HTML(html_content)

        # print(etree.tostring(data, pretty_print=True).decode())
        img_links = []
        section_element = data.xpath('/html/body/div[1]/div/div/div/div/section[1]/div/div[2]/div')[0]
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

        component_page_url, pid = self.search_page_spider(CID)
        if component_page_url is None:  # 检查链接是否存在
            self.errorMessage = "在搜索页面中无法找到该器件"
            return None

        # Using regex to extract the digits before '.html'
        match = re.search(r'/(\d+)\.html', component_page_url)

        # Extracted number
        PID = match.group(1) if match else None

        print(PID)
        component_info = self.component_page_spider(component_page_url, CID)
        if component_info is None:
            return None

        # 旧的获取图片API
        # picture_info = self.component_picture_spider(PID)
        # if picture_info is None:
        #     component_info['图片链接'] = "无图片"
        # else:
        #     component_info['图片链接'] = picture_info

        sch_svg_code, pcb_svg_code = process_svgs(CID)
        if sch_svg_code is None:
            component_info['sch_svg'] = [""]
        else:
            component_info['sch_svg'] = sch_svg_code
        if pcb_svg_code is None:
            component_info['pcb_svg'] = [""]
        else:
            component_info['pcb_svg'] = pcb_svg_code

        component_info['PID'] = pid[0]
        return component_info


if __name__ == "__main__":
    info = InfoSpider()
    print(info.component_page_spider("https://item.szlcsc.com/16815.html", "16815"))
