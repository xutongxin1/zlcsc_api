import xml.etree.ElementTree as ET

def add_pcb_svg(svg_code:str):
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
        'stroke-width': '0.02',
        'text-anchor': 'middle',
        'fill': '#FFFFFF'
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

    # 将新的SVG内容保存到文件中
    with open('output.svg', 'w', encoding='utf-8') as f:
        f.write(new_svg_content)

    print("新的SVG代码已保存到 output.svg 文件中。")
    return new_svg_content

if __name__ == '__main__':
    svg_content = '''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="6.96mm" height="6.071mm" viewBox="3986.3 2988 27.4 23.9"><title></title><style type="text/css">
*[layerid="1"] {stroke:#FF0000;fill:#FF0000;}
*[layerid="2"] {stroke:#0000FF;fill:#0000FF;}
*[layerid="3"] {stroke:#FFCC00;fill:#FFCC00;}
*[layerid="4"] {stroke:#66CC33;fill:#66CC33;}
*[layerid="5"] {stroke:#808080;fill:#808080;}
*[layerid="6"] {stroke:#800000;fill:#800000;}
*[layerid="7"] {stroke:#800080;fill:#800080;stroke-opacity:0.7;fill-opacity:0.7;}
*[layerid="8"] {stroke:#AA00FF;fill:#AA00FF;stroke-opacity:0.7;fill-opacity:0.7;}
*[layerid="9"] {stroke:#6464FF;fill:#6464FF;}
*[layerid="10"] {stroke:#FF00FF;fill:#FF00FF;}
*[layerid="11"] {stroke:#FFFFFF;fill:#FFFFFF;stroke-opacity:0.5;fill-opacity:0.5;}
*[layerid="12"] {stroke:#FFFFFF;fill:#FFFFFF;}
*[layerid="13"] {stroke:#33CC99;fill:#33CC99;}
*[layerid="14"] {stroke:#5555FF;fill:#5555FF;}
*[layerid="15"] {stroke:#F022F0;fill:#F022F0;}
*[layerid="19"] {stroke:#66CCFF;fill:#66CCFF;}
*[layerid="21"] {stroke:#800000;fill:#800000;}
*[layerid="22"] {stroke:#008000;fill:#008000;}
*[layerid="23"] {stroke:#00FF00;fill:#00FF00;}
*[layerid="24"] {stroke:#BC8E00;fill:#BC8E00;}
*[layerid="25"] {stroke:#70DBFA;fill:#70DBFA;}
*[layerid="26"] {stroke:#00CC66;fill:#00CC66;}
*[layerid="27"] {stroke:#9966FF;fill:#9966FF;}
*[layerid="28"] {stroke:#800080;fill:#800080;}
*[layerid="29"] {stroke:#008080;fill:#008080;}
*[layerid="30"] {stroke:#15935F;fill:#15935F;}
*[layerid="31"] {stroke:#000080;fill:#000080;}
*[layerid="32"] {stroke:#00B400;fill:#00B400;}
*[layerid="33"] {stroke:#2E4756;fill:#2E4756;}
*[layerid="34"] {stroke:#99842F;fill:#99842F;}
*[layerid="35"] {stroke:#FFFFAA;fill:#FFFFAA;}
*[layerid="36"] {stroke:#99842F;fill:#99842F;}
*[layerid="37"] {stroke:#2E4756;fill:#2E4756;}
*[layerid="38"] {stroke:#3535FF;fill:#3535FF;}
*[layerid="39"] {stroke:#8000BC;fill:#8000BC;}
*[layerid="40"] {stroke:#43AE5F;fill:#43AE5F;}
*[layerid="41"] {stroke:#C3ECCE;fill:#C3ECCE;}
*[layerid="42"] {stroke:#728978;fill:#728978;}
*[layerid="43"] {stroke:#39503F;fill:#39503F;}
*[layerid="44"] {stroke:#0C715D;fill:#0C715D;}
*[layerid="45"] {stroke:#5A8A80;fill:#5A8A80;}
*[layerid="46"] {stroke:#2B937E;fill:#2B937E;}
*[layerid="47"] {stroke:#23999D;fill:#23999D;}
*[layerid="48"] {stroke:#45B4E3;fill:#45B4E3;}
*[layerid="49"] {stroke:#215DA1;fill:#215DA1;}
*[layerid="50"] {stroke:#4564D7;fill:#4564D7;}
*[layerid="51"] {stroke:#6969E9;fill:#6969E9;}
*[layerid="52"] {stroke:#9069E9;fill:#9069E9;}
*[layerid="99"] {stroke:#00CCCC;fill:#00CCCC;stroke-opacity:0.6;fill-opacity:0.6;}
*[layerid="100"] {stroke:#CC9999;fill:#CC9999;}
*[layerid="101"] {stroke:#66FFCC;fill:#66FFCC;}
*[layerid="Hole"] {stroke:#222222;fill:#222222;}
*[layerid="DRCError"] {stroke:#FAD609;fill:#FAD609;}
*[fill="none"] {fill: none;}
*[stroke="none"] {stroke: none;}
path, polyline, polygon, line {stroke-linecap:round;}
g[c_partid="part_pad"][layerid="1"] ellipse:not([c_padid]) {fill:#FF0000;}
g[c_partid="part_pad"][layerid="1"]  polygon:not([c_padid]) {fill:#FF0000;}
g[c_partid="part_pad"][layerid="1"]  polyline:not([c_padid]) {stroke:#FF0000;}
g[c_partid="part_pad"][layerid="1"]  circle {fill:#FF0000;}
g[c_partid="part_pad"][layerid="2"]  ellipse:not([c_padid]) {fill:#0000FF;}
g[c_partid="part_pad"][layerid="2"]  polygon:not([c_padid]) {fill:#0000FF;}
g[c_partid="part_pad"][layerid="2"]  polyline:not([c_padid]) {stroke:#0000FF;}
g[c_partid="part_pad"][layerid="2"]  circle {fill:#0000FF;}
g[c_partid="part_pad"][layerid="11"]  ellipse:not([c_padid]) {fill:#FFFFFF;}
g[c_partid="part_pad"][layerid="11"]  polygon:not([c_padid]) {fill:#FFFFFF;}
g[c_partid="part_pad"][layerid="11"]  polyline:not([c_padid]) {stroke:#FFFFFF;}
g[c_partid="part_pad"][layerid="11"]  circle {fill:#FFFFFF;}
g[c_partid="part_pad"][layerid] > circle[c_padhole] {fill: #222222;}
g[c_partid="part_pad"][layerid] > polyline[c_padhole] {stroke:#222222;}
g[c_partid="part_via"][layerid] > * + circle {fill: #222222;}
g[c_partid="part_pad"] > polygon[c_padid] {stroke-linejoin: miter;stroke-miterlimit: 100;}
g[c_partid="part_hole"] > circle {fill: #222222;}path, polyline, polygon {stroke-linejoin:round;}
rect, circle, ellipse, polyline, line, polygon, path {shape-rendering:crispEdges;}
</style>
<rect x="3986.3" y="2988" width="27.4" height="23.9" fill="#000000" stroke="none"/><g c_origin="4000,3000" c_para="package`R0402`pre`R?`Contributor`lcsc`link`https://item.szlcsc.com/323315.html`3DModel`R0402_L1.0-W0.5-H0.5`" c_transformList=""  xmlns="http://www.w3.org/2000/svg"><path d="M 4000.5315 3000.9055 L 4000.5315 2999.0945 L 4000.6890 2998.9370 L 4002.6600 2998.9370 L 4002.8175 2999.0945 L 4002.8175 3000.9055 L 4002.6600 3001.0630 L 4000.6890 3001.0630 Z " stroke-width="0"  c_shapetype="line" net="" type="solid" layerid="5" id="gge1003" locked="0" c_teardrop="" c_targetpad="" c_targetwire="" /><path d="M 3999.4685 3000.9055 L 3999.4685 2999.0945 L 3999.3110 2998.9370 L 3997.3400 2998.9370 L 3997.1825 2999.0945 L 3997.1825 3000.9055 L 3997.3400 3001.0630 L 3999.3110 3001.0630 Z " stroke-width="0"  c_shapetype="line" net="" type="solid" layerid="5" id="gge1005" locked="0" c_teardrop="" c_targetpad="" c_targetwire="" /><g c_partid="part_pad" c_etype="pinpart" c_origin="4001.7,3000" layerid="1" number="2" net="" plated ="Y" c_shapetype="group" id="gge1002" locked="0" c_rotation="0" c_width="2.227" c_height="2.126" title="" c_shape="RECT" pasteExpansion="-393.7008" solderExpansion="0.2000"><polygon points="4000.591 3001.063 4000.591 2998.937 4002.818 2998.937 4002.818 3001.063" layerid="7" stroke-width="0.4" c_padid="gge1002" /><polygon points="4000.591 3001.063 4000.591 2998.937 4002.818 2998.937 4002.818 3001.063" layerid="5" stroke-width="-787.4016" c_padid="gge1002" /><polygon points="4000.591 3001.063 4000.591 2998.937 4002.818 2998.937 4002.818 3001.063" stroke-width="0" /><circle c_padhole="1" cx="4001.7040" cy="3000.0000" r="0" stroke-width="0" /></g><g c_partid="part_pad" c_etype="pinpart" c_origin="3998.3,3000" layerid="1" number="1" net="" plated ="Y" c_shapetype="group" id="gge1004" locked="0" c_rotation="0" c_width="2.227" c_height="2.126" title="" c_shape="RECT" pasteExpansion="-393.7008" solderExpansion="0.2000"><polygon points="3999.409 3001.063 3999.409 2998.937 3997.183 2998.937 3997.183 3001.063" layerid="7" stroke-width="0.4" c_padid="gge1004" /><polygon points="3999.409 3001.063 3999.409 2998.937 3997.183 2998.937 3997.183 3001.063" layerid="5" stroke-width="-787.4016" c_padid="gge1004" /><polygon points="3999.409 3001.063 3999.409 2998.937 3997.183 2998.937 3997.183 3001.063" stroke-width="0" /><circle c_padhole="1" cx="3998.2960" cy="3000.0000" r="0" stroke-width="0" /></g><polyline points="3999.109 3001.963 3996.283 3001.963 3996.283 2998.037 3999.109 2998.037" stroke-width="0.6" c_shapetype="line" stroke-linecap="round" fill="none" layerid="3" net="" id="gge1007" /><polyline points="4000.891 3001.963 4003.718 3001.963 4003.718 2998.037 4000.891 2998.037" stroke-width="0.6" c_shapetype="line" stroke-linecap="round" fill="none" layerid="3" net="" id="gge1006" /></g></svg>'''
    add_pcb_svg(svg_content)

