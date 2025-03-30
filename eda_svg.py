import base64
import xml.etree.ElementTree as ET

import cairosvg
# import cairosvg
import requests
from lxml import etree as et

import os
import glob


def pcb_svg(svg_code: str, index: int):
    # 注册SVG命名空间，避免输出时出现ns0前缀
    ET.register_namespace('', 'http://www.w3.org/2000/svg')

    # 解析SVG内容
    root = ET.fromstring(svg_code)

    # 定义SVG命名空间
    ns = {'svg': 'http://www.w3.org/2000/svg'}
    # 查找所有符合条件的 <g> 元素
    part_pads = root.findall('.//svg:g[@c_partid="part_pad"][@c_etype="pinpart"]', ns)

    # 创建新的 <g> 元素，使用SVG命名空间
    g_nets = ET.Element('{http://www.w3.org/2000/svg}g', attrib={
        'id': 'gNets',
        'pointer-events': 'none',
        'font-size': '1',
        'stroke-width': '0.005',
        'text-anchor': 'middle',
        'fill': '#FFFFFF',
        'stroke': '#000000'  # 设定描边颜色
    })

    # 添加初始的 <text> 元素
    ET.SubElement(g_nets, '{http://www.w3.org/2000/svg}text', attrib={
        'id': 'textTemp',
        'dy': '0.35em',
        'x': '0',
        'y': '0'
    })

    # 遍历所有找到的 <g> 元素，提取信息并创建新的 <text> 元素
    for part_pad in part_pads:
        c_origin = part_pad.get('c_origin')
        number = part_pad.get('number')
        if c_origin and number:
            x, y = c_origin.split(',')
            text_elem = ET.SubElement(g_nets, '{http://www.w3.org/2000/svg}text', attrib={
                'id': 'textTemp',
                'dy': '0.35em',
                'x': x.strip(),
                'y': y.strip()
            })
            text_elem.text = number

    # 将生成的 <g> 元素插入到原始SVG的根元素中
    root.append(g_nets)

    # 将修改后的SVG树转换为字符串
    new_svg_content = ET.tostring(root, encoding='unicode')

    cairosvg.svg2png(bytestring=new_svg_content, write_to="output.png", scale=20.0)
    with open("output.png", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

    return encoded_string


def sch_svg(svg_code: str, index: int):
    # Parse the SVG code with lxml.etree
    try:
        parser = et.XMLParser(ns_clean=True, recover=True)
        root = et.fromstring(svg_code.encode('utf-8'), parser)
    except et.XMLSyntaxError:
        # If there is a parsing error, return the input as is
        return svg_code

    # Handle namespaces
    nsmap = root.nsmap.copy()
    if None in nsmap:
        nsmap['svg'] = nsmap[None]
        del nsmap[None]
    else:
        nsmap.setdefault('svg', 'http://www.w3.org/2000/svg')

    # Find all <g> elements with c_partid="part_pin" and c_etype="pinpart"
    xpath_expr = './/svg:g[@c_partid="part_pin"][@c_etype="pinpart"]'
    g_elements = root.xpath(xpath_expr, namespaces=nsmap)

    if not g_elements:
        # If no matching <g> elements are found, return the input as is
        return svg_code

    # For each matching <g> element, modify child <text> elements
    for g in g_elements:
        # Find all child <text> elements
        text_elements = g.xpath('.//svg:text', namespaces=nsmap)
        for text_elem in text_elements:
            # Remove the display="none" attribute if it exists
            if 'display' in text_elem.attrib:
                del text_elem.attrib['display']
            # Change the font-size to "4pt"
            text_elem.attrib['font-size'] = '4pt'

    # Serialize the modified XML tree back to a string
    modified_svg = et.tostring(root, encoding='utf-8', xml_declaration=False).decode('utf-8')

    # # 将新的SVG内容保存到文件中
    # with open('./doc/sch'+str(index)+'.svg', 'w', encoding='utf-8') as f:
    #     f.write(modified_svg)
    # print("新的SVG代码已保存到 ./doc/sch"+str(index)+".svg文件中。")
    cairosvg.svg2png(bytestring=modified_svg, write_to="output.png", scale=20.0)
    with open("output.png", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

    return encoded_string


def get_svgs(product_code: str):
    url = f"https://lceda.cn/api/products/{product_code}/svgs"
    try:
        response = requests.get(url)
        data = response.json()

        if not data.get('success', False):
            return None

        svg_dict = {}
        for item in data.get('result', []):
            doc_type = item.get('docType')
            svg_content = item.get('svg')
            if doc_type is not None and svg_content is not None:
                svg_dict.setdefault(doc_type, []).append(svg_content)

        return svg_dict if svg_dict else None

    except Exception:
        return None


def process_svgs(product_code):
    svg_data = get_svgs(product_code)
    if svg_data is None:
        print("Failed to retrieve SVG data.")
        return None, None

    sch = {}
    pcb = {}

    # Process docType 6 or fallback to docType 2 for sch_svg
    if 6 in svg_data:
        for idx, svg in enumerate(svg_data[6], start=1):
            sch_svg_code = sch_svg(svg, idx)
            sch[idx] = sch_svg_code
    elif 2 in svg_data:
        for idx, svg in enumerate(svg_data[2], start=1):
            sch_svg_code = sch_svg(svg, idx)
            sch[idx] = sch_svg_code

    # Process docType 5 for pcb_svg
    if 4 in svg_data:
        for idx, svg in enumerate(svg_data[4], start=1):
            pcb_svg_code = pcb_svg(svg, idx)
            pcb[idx] = pcb_svg_code

    return sch, pcb


if __name__ == '__main__':

    # 删除doc文件夹下的所有文件
    # 设置文件夹路径
    folder_path = './doc'
    # 查找doc文件夹中的所有文件
    files = glob.glob(os.path.join(folder_path, '*'))
    # 删除所有文件
    for file in files:
        try:
            os.remove(file)
            print(f"Deleted: {file}")
        except Exception as e:
            print(f"Error deleting {file}: {e}")

    product_code = "C569043"
    sch_dict, pcb_dict = process_svgs(product_code)
    print("Schematic SVGs:", sch_dict)
    print("PCB SVGs:", pcb_dict)
