#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import zipfile
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont
import io
import shutil
import re
import datetime

class OFDToPNG:
    def __init__(self, ofd_path, output_dir):
        self.ofd_path = ofd_path
        self.output_dir = output_dir
        self.temp_dir = os.path.join(self.output_dir, 'temp')
        self.doc_id = 'Doc_0'
        self.tax_id_coordinates = []  # 存储购买方和销售方税号的坐标信息
        
        # 创建输出目录
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def unzip_ofd(self):
        """解压OFD文件"""
        with zipfile.ZipFile(self.ofd_path, 'r') as zf:
            zf.extractall(self.temp_dir)
    
    def parse_namespace(self, root):
        """获取XML的命名空间"""
        return root.tag.split('}')[0][1:]
    
    def extract_tax_id_coordinates(self):
        """从OFD的XML文件中提取购买方和销售方税号的坐标"""
        # 匹配税号模式：支持15位旧版税号、17位税号、18位统一社会信用代码和20位税号
        # 15位旧版税号：纯数字
        # 17位税号：纯数字或最后一位为X/x
        # 18位统一社会信用代码：18位，包含数字和大写字母
        # 20位税号：纯数字
        tax_pattern = re.compile(r'[0-9A-Z]{18}|\d{15}|\d{17}[\dXx]|\d{17}|\d{20}', re.IGNORECASE)
        
        # 获取文档信息
        doc_info = self.parse_document()
        ns = doc_info['ns']
        page_count = doc_info['page_count']
        
        # 遍历所有页面
        for page_index in range(page_count):
            # 页面目录
            page_dir = os.path.join(self.temp_dir, self.doc_id, 'Pages', f'Page_{page_index}')
            content_xml_path = os.path.join(page_dir, 'Content.xml')
            
            if not os.path.exists(content_xml_path):
                continue
            
            # 解析页面内容
            tree = ET.parse(content_xml_path)
            root = tree.getroot()
            
            # 遍历所有文本对象
            for text_obj in root.findall(f'.//{{{ns}}}TextObject'):
                boundary = text_obj.attrib.get('Boundary', '')
                if not boundary:
                    continue
                
                # 解析边界坐标
                try:
                    x0, y0, width, height = map(float, boundary.split())
                except ValueError:
                    continue
                
                # 获取所有文本元素并合并文本内容（支持同一文本对象内的税号分拆）
                text_codes = text_obj.findall(f'.//{{{ns}}}TextCode')
                if not text_codes:
                    continue
                
                # 合并当前TextObject下所有TextCode的文本内容
                combined_text = ''.join([tc.text.strip() if tc.text else '' for tc in text_codes])
                
                # 清理文本内容：移除控制字符和空白字符
                combined_text = re.sub(r'[\x00-\x1F\x7F]', '', combined_text)
                combined_text = re.sub(r'\s+', '', combined_text)
                
                # 检查是否包含税号
                if combined_text and tax_pattern.search(combined_text):
                    # 如果当前TextObject包含税号，则遍历所有TextCode并记录坐标
                    for text_code in text_codes:
                        x_attr = text_code.attrib.get('X', '0')
                        y_attr = text_code.attrib.get('Y', '0')
                        
                        try:
                            x = float(x_attr)
                            y = float(y_attr)
                        except ValueError:
                            continue
                        
                        text = text_code.text.strip() if text_code.text else ''
                        if not text:  # 跳过空文本元素
                            continue
                        
                        # 存储税号的坐标信息（四舍五入到四位小数避免浮点精度问题）
                        self.tax_id_coordinates.append((round(x0, 4), round(y0, 4), round(x, 4), round(y, 4)))

    def parse_document(self):
        """解析OFD文档结构"""
        # 解析OFD.xml
        ofd_xml_path = os.path.join(self.temp_dir, 'OFD.xml')
        if not os.path.exists(ofd_xml_path):
            raise Exception('OFD.xml文件不存在')
        
        tree = ET.parse(ofd_xml_path)
        root = tree.getroot()
        ns = self.parse_namespace(root)
        
        # 从OFD.xml中提取DocBody ID
        doc_body = root.find(f'.//{{{ns}}}DocBody')
        if doc_body is not None:
            self.doc_id = doc_body.attrib.get('ID', 'Doc_0')  # 默认值仍为'Doc_0'
        
        # 解析Document.xml
        doc_xml_path = os.path.join(self.temp_dir, self.doc_id, 'Document.xml')
        if not os.path.exists(doc_xml_path):
            raise Exception('Document.xml文件不存在')
        
        doc_tree = ET.parse(doc_xml_path)
        doc_root = doc_tree.getroot()
        
        # 获取页面数量
        pages = doc_root.findall(f'.//{{{ns}}}Page')
        page_count = len(pages)
        
        # 解析页面尺寸
        page_dir = os.path.join(self.temp_dir, self.doc_id, 'Pages', 'Page_0')
        content_xml_path = os.path.join(page_dir, 'Content.xml')
        if not os.path.exists(content_xml_path):
            raise Exception('Content.xml文件不存在')
        
        content_tree = ET.parse(content_xml_path)
        content_root = content_tree.getroot()
        
        # 获取页面尺寸
        physical_box = content_root.find(f'.//{{{ns}}}PhysicalBox')
        if physical_box is None:
            physical_box = content_root.find(f'.//{{{ns}}}Area/{{{ns}}}PhysicalBox')
        
        # 如果在Content.xml中未找到，尝试在Document.xml的CommonData中查找
        if physical_box is None:
            common_data = doc_root.find(f'.//{{{ns}}}CommonData')
            if common_data is not None:
                physical_box = common_data.find(f'.//{{{ns}}}PhysicalBox')
                if physical_box is None:
                    physical_box = common_data.find(f'.//{{{ns}}}Area/{{{ns}}}PhysicalBox')
        
        if physical_box is None:
            raise Exception('PhysicalBox未找到')
            
        box = physical_box.text.strip()
        x0, y0, width, height = map(float, box.split())
        
        return {
            'page_count': page_count,
            'page_width': width,
            'page_height': height,
            'ns': ns
        }
    
    def draw_page_content(self, page_index, page_width, page_height, ns):
        """绘制页面内容"""
        # 页面目录
        page_dir = os.path.join(self.temp_dir, self.doc_id, 'Pages', f'Page_{page_index}')
        content_xml_path = os.path.join(page_dir, 'Content.xml')
        
        if not os.path.exists(content_xml_path):
            raise Exception(f'Page_{page_index}/Content.xml文件不存在')
        
        # 解析页面内容
        tree = ET.parse(content_xml_path)
        root = tree.getroot()
        
        # 创建图像
        dpi = 300
        scale = dpi / 25.4  # 转换为像素
        img_width = int(page_width * scale)
        img_height = int(page_height * scale)
        
        image = Image.new('RGB', (img_width, img_height), 'white')
        draw = ImageDraw.Draw(image)
        
        # 设置默认字体
        font = None
        try:
            # 尝试使用Windows系统中的黑体字体
            font_path = "C:\\Windows\\Fonts\\simhei.ttf"
            font = ImageFont.truetype(font_path, int(3.175 * scale))
        except:
            try:
                # 尝试其他常见路径或字体名称
                font = ImageFont.truetype('simhei.ttf', int(3.175 * scale))
            except:
                try:
                    # 尝试使用宋体
                    font_path = "C:\\Windows\\Fonts\\simsun.ttc"
                    font = ImageFont.truetype(font_path, int(3.175 * scale))
                except:
                    # 回退到默认字体
                    font = ImageFont.load_default()
        
        # 处理模板内容
        document_xml_path = os.path.join(self.temp_dir, self.doc_id, 'Document.xml')
        if os.path.exists(document_xml_path):
            # 解析Document.xml以获取模板位置
            doc_tree = ET.parse(document_xml_path)
            doc_root = doc_tree.getroot()
            
            # 查找TemplatePage元素
            template_page = doc_root.find(f'.//{{{ns}}}CommonData/{{{ns}}}TemplatePage')
            if template_page is not None and 'BaseLoc' in template_page.attrib:
                template_base_loc = template_page.attrib['BaseLoc']
                template_xml_path = os.path.join(self.temp_dir, self.doc_id, template_base_loc)
                
                if os.path.exists(template_xml_path):
                    # 解析模板内容
                    template_tree = ET.parse(template_xml_path)
                    template_root = template_tree.getroot()
                    
                    # 绘制模板中的所有图层
                    template_content = template_root.find(f'.//{{{ns}}}Content')
                    if template_content is not None:
                        template_layers = template_content.findall(f'.//{{{ns}}}Layer')
                        for layer in template_layers:
                            self.draw_all_objects(layer, draw, image, scale, font, img_width, img_height, ns)
        
        # 处理页面内容的所有图层
        content = root.find(f'.//{{{ns}}}Content')
        if content is not None:
            layers = content.findall(f'.//{{{ns}}}Layer')
            for layer in layers:
                # 绘制所有对象，包括直接子对象和嵌套对象
                self.draw_all_objects(layer, draw, image, scale, font, img_width, img_height, ns)
        
        return image
    
    def draw_all_objects(self, parent, draw, image, scale, font, img_width, img_height, ns):
        """绘制所有类型的对象，确保线条在文本下方"""
        if parent is None:
            return
        
        # 绘制路径对象（线条）
        path_objects = parent.findall(f'.//{{{ns}}}PathObject')
        for path_obj in path_objects:
            self.draw_path_object(path_obj, draw, scale, img_width, img_height, ns)
        
        # 绘制文本对象
        text_objects = parent.findall(f'.//{{{ns}}}TextObject')
        for text_obj in text_objects:
            self.draw_text_object(text_obj, draw, scale, font, img_width, img_height, ns)
        
        # 绘制图像对象
        img_objects = parent.findall(f'.//{{{ns}}}ImageObject')
        for img_obj in img_objects:
            self.draw_image_object(img_obj, image, scale, img_width, img_height, ns)
        
        # 绘制数学公式对象
        math_objects = parent.findall(f'.//{{{ns}}}OFDMathML')
        for math_obj in math_objects:
            self.draw_math_object(math_obj, draw, scale, font, img_width, img_height, ns)
    
    def draw_math_object(self, math_obj, draw, scale, font, img_width, img_height, ns):
        """绘制数学公式对象"""
        # OFDMathML暂时无法直接绘制，这里只记录日志
        pass
    
    def get_font(self, font_family, size, scale):
        """获取指定大小的字体"""
        font_size_px = int(size * scale)
        
        # 尝试多种字体路径，使用原始字符串避免转义问题
        font_paths = []
        if font_family:
            font_paths.append(os.path.join(self.font_dir, font_family + '.ttf'))
            font_paths.append(os.path.join(self.font_dir, font_family + '.ttc'))
        # 尝试使用系统中常见的中文字体
        font_paths.extend([
            r"C:\Windows\Fonts\msyh.ttc",    # 微软雅黑 - 支持¥符号
            r"C:\Windows\Fonts\simsun.ttc",    # 宋体 - 支持¥符号
            r"C:\Windows\Fonts\arial.ttf",     # Arial - 支持¥符号
            r"C:\Windows\Fonts\simhei.ttf",     # 黑体 - 可能不支持¥符号
            "msyh.ttc",
            "simsun.ttc",
            "arial.ttf",
            "simhei.ttf"
        ])
        
        # 尝试加载字体
        for font_path in font_paths:
            try:
                if os.path.exists(font_path) or "Windows\\Fonts" in font_path:
                    # 对于系统字体路径，直接尝试加载
                    font = ImageFont.truetype(font_path, font_size_px)
                    return font
            except Exception as e:
                continue
        
        # 回退到默认字体
        return ImageFont.load_default()
    
    def draw_text_object(self, text_obj, draw, scale, font, img_width, img_height, ns):
        """绘制文本对象"""
        boundary = text_obj.attrib.get('Boundary')
        if boundary is None:
            return
            
        x0, y0, w, h = map(float, boundary.split())
        font_size = float(text_obj.attrib.get('Size', 3.175))
        
        # 解析颜色
        fill_color = 'black'
        stroke_color = None
        
        # 获取绘制参数
        draw_params = text_obj.find(f'.//{{{ns}}}DrawParam')
        if draw_params is not None:
            # 获取填充颜色
            fill_elem = draw_params.find(f'.//{{{ns}}}Fill')
            if fill_elem is not None:
                color_elem = fill_elem.find(f'.//{{{ns}}}Color')
                if color_elem is not None:
                    color_value = color_elem.attrib.get('Value', '').strip()
                    if color_value:
                        # OFD颜色格式：RGB或CMYK，如"1.0 1.0 1.0"（白色）或"0.0 0.0 0.0"（黑色）
                        color_parts = list(map(float, color_value.split()))
                        if len(color_parts) >= 3:
                            # 转换为0-255范围
                            r = int(color_parts[0] * 255)
                            g = int(color_parts[1] * 255)
                            b = int(color_parts[2] * 255)
                            fill_color = (r, g, b)
        
        # 遍历所有文本代码
        text_codes = text_obj.findall(f'.//{{{ns}}}TextCode')
        for text_code in text_codes:
            text = text_code.text.strip() if text_code.text else ''
            if not text:
                continue
            x = float(text_code.attrib.get('X', 0))
            y = float(text_code.attrib.get('Y', 0))
            
            abs_x = (x0 + x) * scale
            abs_y = int((y0 + y - 4) * scale)  # 将所有文本向上移动5个单位
            
            # 检查是否为税号文本对象（根据文本内容识别）
            # 检查当前文本对象是否为预提取的税号坐标
            current_coords = (round(x0, 4), round(y0, 4), round(x, 4), round(y, 4))
            adjusted_font_size = font_size  # 保存原始字体大小
            
            if current_coords in self.tax_id_coordinates:
                abs_x += 5 * scale  # 向右偏移5毫米（调整税号位置）
                adjusted_font_size *= 0.8  # 缩小字体大小20%
            # 密码区文本过长，缩小字体大小20%
            if len(text) > 100:
                adjusted_font_size *= 0.8

            # 获取当前文本的字体
            current_font = self.get_font('', adjusted_font_size, scale)
            
            # 获取Boundary宽度，即文本可以显示的最大宽度
            max_width = w * scale  # 转换为图片像素宽度
            
            # 如果max_width太小或为0，直接绘制整个文本
            if max_width <= 0:
                # 获取当前文本的字体
                current_font = self.get_font('', adjusted_font_size, scale)
                
                # 绘制文本
                if stroke_color is not None:
                    # 有描边，使用描边参数
                    draw.text(
                        (abs_x, abs_y), 
                        text, 
                        fill=fill_color, 
                        font=current_font,
                        stroke_fill=stroke_color,
                        stroke_width=1
                    )
                else:
                    # 没有描边
                    draw.text(
                        (abs_x, abs_y), 
                        text, 
                        fill=fill_color, 
                        font=current_font
                    )
                continue
            
            # 自动换行逻辑
            def wrap_text(text, font, max_width):
                lines = []
                
                # 如果文本为空，返回空列表
                if not text:
                    return lines
                
                # 如果单行文本宽度不超过max_width，直接返回
                if font.getbbox(text)[2] <= max_width:
                    lines.append(text)
                    return lines
                
                # 尝试按单词分割
                words = text.split()
                if not words:
                    lines.append(text)
                    return lines
                
                # 按单词逐词添加，直到超过max_width
                current_line = words[0]
                
                for word in words[1:]:
                    test_line = current_line + ' ' + word
                    width = font.getbbox(test_line)[2]
                    
                    if width <= max_width:
                        current_line = test_line
                    else:
                        lines.append(current_line)
                        current_line = word
                
                # 添加最后一行
                lines.append(current_line)
                return lines
            
            # 尝试按字符分割（对于非空格分隔的长文本）
            def wrap_text_by_char(text, font, max_width):
                lines = []
                if not text:
                    return lines
                
                current_line = ''
                for char in text:
                    test_line = current_line + char
                    width = font.getbbox(test_line)[2]
                    
                    if width <= max_width:
                        current_line = test_line
                    else:
                        if current_line:
                            lines.append(current_line)
                            current_line = char
                
                if current_line:
                    lines.append(current_line)
                    
                return lines
            
            # 检查是否为密码区或地址电话字段（仅对这些字段应用换行处理）
            # 密码区通常是长文本（超过100字符），地址电话字段可能包含特定标识
            need_line_break = False
            if len(text) > 100: 
                need_line_break = True
            
            if need_line_break:
                # print(f"需要换行处理的文本：{text}")
                # 获取当前文本的字体
                current_font = self.get_font('', adjusted_font_size, scale)
                
                # 密码区处理：每28个字符换一行
                if len(text) > 100:
                    # print(f"处理密码区文本：{text}")
                    lines = [text[i:i+28] for i in range(0, len(text), 28)]
                else:
                    # 普通长文本处理
                    # 先尝试按单词分割
                    lines = wrap_text(text, current_font, max_width)
                    # 如果按单词分割后仍有单行超过max_width，尝试按字符分割
                    if len(lines) == 1 and current_font.getbbox(lines[0])[2] > max_width:
                       lines = wrap_text_by_char(text, current_font, max_width)

                # 计算行高（使用字体的实际高度）
                # 获取字体的边界框来确定行高
                bbox = current_font.getbbox('A')
                line_height = bbox[3] - bbox[1]  # 字体高度：底部 - 顶部
                
                # 绘制每行文本，添加行间距
                for i, line in enumerate(lines):
                    line = line.strip()  # 去除每行前后的空白
                    if not line:
                        continue  # 跳过空行
                    
                    # 计算当前行的Y坐标，添加行间距
                    line_y = abs_y + (i * (line_height + line_height * 0.5))  # 添加20%的行间距
                    
                    # 绘制文本
                    if stroke_color is not None:
                        # 有描边，使用描边参数
                        draw.text(
                            (abs_x, line_y), 
                            line, 
                            fill=fill_color, 
                            font=current_font,
                            stroke_fill=stroke_color,
                            stroke_width=1
                        )
                    else:
                        # 没有描边
                        draw.text(
                            (abs_x, line_y), 
                            line, 
                            fill=fill_color, 
                            font=current_font
                        )
            else:
                # 对于其他字段，不应用换行处理，直接绘制整个文本
                # 获取当前文本的字体
                current_font = self.get_font('', adjusted_font_size, scale)
                
                # 绘制文本
                if stroke_color is not None:
                    # 有描边，使用描边参数
                    draw.text(
                        (abs_x, abs_y), 
                        text, 
                        fill=fill_color, 
                        font=current_font,
                        stroke_fill=stroke_color,
                        stroke_width=1
                    )
                else:
                    # 没有描边
                    draw.text(
                        (abs_x, abs_y), 
                        text, 
                        fill=fill_color, 
                        font=current_font
                    )
    
    def draw_image_object(self, img_obj, image, scale, img_width, img_height, ns):
        """绘制图像对象"""
        # 获取边界
        boundary = img_obj.attrib.get('Boundary')
        if boundary is None:
            return
            
        x0, y0, w, h = map(float, boundary.split())
        
        # 获取资源ID
        resource_id = img_obj.attrib.get('ResourceID')
        if resource_id is None:
            return
            
        # 查找图像资源
        img_path = os.path.join(self.temp_dir, self.doc_id, 'Res', f'image_{resource_id}.png')
        if not os.path.exists(img_path):
            return
            
        # 打开图像
        with Image.open(img_path) as img:
            # 计算缩放比例
            img_width_org, img_height_org = img.size
            scale_w = (w * scale) / img_width_org
            scale_h = (h * scale) / img_height_org
            
            # 调整图像大小
            new_width = int(img_width_org * scale_w)
            new_height = int(img_height_org * scale_h)
            resized_img = img.resize((new_width, new_height))
            
            # 计算位置
            abs_x = int(x0 * scale)
            abs_y = int(y0 * scale)
            
            # 粘贴图像
            image.paste(resized_img, (abs_x, abs_y))
    
    def draw_path_object(self, path_obj, draw, scale, img_width, img_height, ns):
        """绘制路径对象"""
        # 获取边界
        boundary = path_obj.attrib.get('Boundary')
        if boundary is None:
            return
            
        # 解析PathData
        path_data = path_obj.find(f'.//{{{ns}}}PathData')
        if path_data is not None:
            paths = path_data.findall(f'.//{{{ns}}}Path')
            for path in paths:
                data = path.attrib.get('Data', '').strip()
                if not data:
                    continue
                    
                # 解析路径数据
                commands = self.parse_path_data(data)
                if not commands:
                    continue
                    
                # 转换为像素坐标并翻转Y轴（OFD原点在左下角，PIL在左上角）
                pixel_commands = []
                for cmd, points in commands:
                    pixel_points = []
                    for x, y in points:
                        px = int(x * scale)
                        py = int(img_height - (y * scale))  # 翻转Y轴
                        pixel_points.append((px, py))
                    pixel_commands.append((cmd, pixel_points))
                
                # 绘制路径
                self.draw_path_commands(pixel_commands, draw)
        else:
            # 绘制简单矩形作为回退
            x0, y0, w, h = map(float, boundary.split())
            abs_x0 = int(x0 * scale)
            abs_y0 = int(y0 * scale)
            abs_x1 = int((x0 + w) * scale)
            abs_y1 = int((y0 + h) * scale)
            draw.rectangle([abs_x0, abs_y0, abs_x1, abs_y1], outline='black')
    
    def parse_path_data(self, path_data):
        """解析路径数据，支持SVG路径命令和Bezier曲线(B命令)"""
        if not path_data:
            return []
        
        import re
        # 分割命令和参数，支持B/b命令
        tokens = re.findall(r'[MmHhVvLlZzBb]|[-+]?\d*\.?\d+', path_data)
        if not tokens:
            return []
        
        commands = []
        current_cmd = None
        i = 0
        
        # 跟踪当前位置
        current_pos = [0.0, 0.0]
        
        while i < len(tokens):
            token = tokens[i]
            if token in 'MmHhVvLlZzBb':
                current_cmd = token
                i += 1
            else:
                # 获取参数
                params = []
                while i < len(tokens) and tokens[i] not in 'MmHhVvLlZzBb':
                    params.append(float(tokens[i]))
                    i += 1
                
                if current_cmd is None:
                    continue
                
                # 处理命令
                if current_cmd in 'Mm':
                    # Move to command
                    j = 0
                    while j < len(params) - 1:
                        x = params[j]
                        y = params[j+1]
                        if current_cmd.islower():
                            # 相对坐标
                            x += current_pos[0]
                            y += current_pos[1]
                        commands.append((current_cmd.upper(), [(x, y)]))
                        current_pos = [x, y]
                        j += 2
                elif current_cmd in 'Ll':
                    # Line to command
                    j = 0
                    while j < len(params) - 1:
                        x = params[j]
                        y = params[j+1]
                        if current_cmd.islower():
                            # 相对坐标
                            x += current_pos[0]
                            y += current_pos[1]
                        commands.append((current_cmd.upper(), [(x, y)]))
                        current_pos = [x, y]
                        j += 2
                elif current_cmd in 'Hh':
                    # Horizontal line
                    for x in params:
                        if current_cmd.islower():
                            x += current_pos[0]
                        y = current_pos[1]
                        commands.append(('L', [(x, y)]))
                        current_pos = [x, y]
                elif current_cmd in 'Vv':
                    # Vertical line
                    for y in params:
                        if current_cmd.islower():
                            y += current_pos[1]
                        x = current_pos[0]
                        commands.append(('L', [(x, y)]))
                        current_pos = [x, y]
                elif current_cmd in 'Zz':
                    # Close path
                    commands.append(('Z', []))
                elif current_cmd in 'Bb':
                    # Bezier curve command (B: cubic Bezier)
                    j = 0
                    while j < len(params) - 5:  # 需要6个参数（cp1x, cp1y, cp2x, cp2y, endx, endy）
                        cp1x = params[j]
                        cp1y = params[j+1]
                        cp2x = params[j+2]
                        cp2y = params[j+3]
                        endx = params[j+4]
                        endy = params[j+5]
                        if current_cmd.islower():
                            # 相对坐标
                            cp1x += current_pos[0]
                            cp1y += current_pos[1]
                            cp2x += current_pos[0]
                            cp2y += current_pos[1]
                            endx += current_pos[0]
                            endy += current_pos[1]
                        commands.append((current_cmd.upper(), [(cp1x, cp1y), (cp2x, cp2y), (endx, endy)]))
                        current_pos = [endx, endy]
                        j += 6
        
        return commands
    
    def process_vector_object(self, vector_obj, draw, image, scale, font, img_width, img_height, ns):
        """处理矢量对象"""
        if vector_obj is None:
            return
            
        # 处理矢量对象内部的路径对象（线条）
        path_objects = vector_obj.findall(f'.//{{{ns}}}PathObject')
        for path_obj in path_objects:
            self.draw_path_object(path_obj, draw, scale, img_width, img_height, ns)
        
        # 处理矢量对象内部的文本对象
        text_objects = vector_obj.findall(f'.//{{{ns}}}TextObject')
        for text_obj in text_objects:
            self.draw_text_object(text_obj, draw, scale, font, img_width, img_height, ns)
        
        # 处理矢量对象内部的图像对象
        img_objects = vector_obj.findall(f'.//{{{ns}}}ImageObject')
        for img_obj in img_objects:
            self.draw_image_object(img_obj, image, scale, img_width, img_height, ns)
        
        # 递归处理嵌套的矢量对象
        nested_vectors = vector_obj.findall(f'.//{{{ns}}}VectorObject')
        for nested_vector in nested_vectors:
            self.process_vector_object(nested_vector, draw, image, scale, font, img_width, img_height, ns)
        
        # 处理矢量对象内部的组合对象
        composite_objects = vector_obj.findall(f'.//{{{ns}}}CompositeObject')
        for comp_obj in composite_objects:
            self.process_vector_object(comp_obj, draw, image, scale, font, img_width, img_height, ns)
    
    def draw_path_commands(self, commands, draw):
        """绘制路径命令，支持Bezier曲线(B命令)"""
        if not commands:
            return
            
        current_pos = None
        start_pos = None
        
        for cmd, points in commands:
            if cmd == 'Z':
                # Close path
                if current_pos is not None and start_pos is not None:
                    draw.line([current_pos, start_pos], fill='black')
                    current_pos = start_pos
                continue
                
            if not points:
                continue
                
            if cmd == 'M':
                # Move to new position (start of subpath)
                current_pos = points[0]
                start_pos = current_pos
            elif cmd == 'L':
                # Draw line
                if current_pos is not None:
                    for p in points:
                        draw.line([current_pos, p], fill='black')
                        current_pos = p
            elif cmd == 'B':
                # 绘制三次贝塞尔曲线
                if current_pos is None:
                    continue
                    
                for i in range(len(points) // 3):  # 每3个点为一组贝塞尔曲线参数
                    cp1, cp2, end_pos = points[i*3], points[i*3+1], points[i*3+2]
                    
                    # 使用多段直线近似贝塞尔曲线
                    num_segments = 10  # 近似精度（段数）
                    for t in range(num_segments):
                        t0 = t / num_segments
                        t1 = 1.0 - t0
                        
                        # 三次贝塞尔曲线公式
                        x = (t1**3) * current_pos[0] + 3 * (t1**2) * t0 * cp1[0] + 3 * t1 * (t0**2) * cp2[0] + (t0**3) * end_pos[0]
                        y = (t1**3) * current_pos[1] + 3 * (t1**2) * t0 * cp1[1] + 3 * t1 * (t0**2) * cp2[1] + (t0**3) * end_pos[1]
                        
                        if t == 0:
                            prev_point = (x, y)
                        else:
                            current_point = (x, y)
                            draw.line([prev_point, current_point], fill='black')
                            prev_point = current_point
                    
                    # 更新当前位置到曲线终点
                    current_pos = end_pos
        
        return


def convert_file(ofd_path, output_dir=None):
    """顶层函数：转换单个 OFD 文件到 PNG（用于对外 API）。

    这个函数使用类 `OFDToPNG` 的解析与绘制方法，生成 PNG 到 `output_dir`。
    如果未提供 `output_dir`，会在 ofd 同目录下创建临时输出目录 `temp_output_{base_name}`。
    返回生成的 PNG 路径列表（相对或绝对，取决于传入的 output_dir）。
    """
    # 获取文件名
    base_name = os.path.splitext(os.path.basename(ofd_path))[0]
    # 检测文件是否存在
    if not os.path.exists(ofd_path):
        raise FileNotFoundError(f'文件不存在，请检查传入的 {ofd_path}文件名是否正确？')
    # 创建输出目录
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(ofd_path) or '.', f'temp_output_{base_name}')

    # 清理并创建输出目录
    if os.path.exists(output_dir):
        try:
            shutil.rmtree(output_dir)
        except Exception:
            pass
    os.makedirs(output_dir, exist_ok=True)

    conv = OFDToPNG(ofd_path, output_dir)

    # 执行转换流程（使用类的现有方法）
    conv.unzip_ofd()
    conv.extract_tax_id_coordinates()
    doc_info = conv.parse_document()

    page_count = doc_info['page_count']
    page_width = doc_info['page_width']
    page_height = doc_info['page_height']
    ns = doc_info['ns']

    results = []
    for page_index in range(page_count):
        image = conv.draw_page_content(page_index, page_width, page_height, ns)
        out_path = os.path.join(output_dir, f'page_{page_index + 1}.png')
        image.save(out_path, dpi=(300, 300), format='PNG')
        results.append(out_path)

    # 清理临时解包目录
    try:
        shutil.rmtree(conv.temp_dir, ignore_errors=True)
    except Exception:
        pass

    return results


def convert_folder(input_dir):
    """批量转换指定目录及其所有子目录中的OFD文件到PNG，每个包含OFD文件的目录会创建img文件夹存储结果"""
    import os
    # 检测输入目录是否存在
    if not os.path.isdir(input_dir):
        raise NotADirectoryError(f"输入目录不存在: {input_dir}")
    
    # 递归遍历所有目录和子目录
    for root, dirs, files in os.walk(input_dir):
        # 检查当前目录是否包含OFD文件
        ofd_files = [f for f in files if f.endswith('.ofd')]
        if not ofd_files:
            continue  # 当前目录没有OFD文件，跳过

        # 在当前目录创建img文件夹
        output_dir = os.path.join(root, 'img')
        os.makedirs(output_dir, exist_ok=True)

        # 处理当前目录中的每个OFD文件
        for filename in ofd_files:
            # 获取开始时间
            start_time = datetime.datetime.now()
            # 获取文件名（不包含后缀）
            base_name = os.path.splitext(filename)[0]

            # 构建OFD文件路径
            ofd_path = os.path.join(root, filename)
            # 打印转换时间和文件路径
            print(f"--->正在转换文件: {ofd_path},请稍等待...")

            # 创建唯一的临时输出目录
            temp_output = os.path.join(root, f'temp_output_{base_name}')

            try:
                # 调用顶层 convert_file 生成 PNG 到临时目录
                pngs = convert_file(ofd_path, temp_output)

                # 遍历临时输出目录中的图片文件，按更稳健的方式解析页面编号并移动
                for img_filename in os.listdir(temp_output):
                    if img_filename.endswith('.png'):
                        name_no_ext = os.path.splitext(img_filename)[0]
                        if '_' in name_no_ext:
                            page_num = name_no_ext.rsplit('_', 1)[1]
                        else:
                            page_num = name_no_ext

                        # 构建新的图片文件名
                        new_img_filename = f'{base_name}_{page_num}.png'

                        # 构建源和目标路径
                        src_path = os.path.join(temp_output, img_filename)
                        dst_path = os.path.join(output_dir, new_img_filename)

                        # 移动并替换图片
                        os.replace(src_path, dst_path)
                        # 打印图片路径和图片名称和开始时间到转换时间的差，精确到毫秒，比如：125ms
                        print(f"************************已转换并保存图片: {output_dir}\{new_img_filename} ->转换时间: {(datetime.datetime.now() - start_time).total_seconds() * 1000:.0f}ms")
                        

            except Exception as e:
                print(f'转换文件 {os.path.join(root, filename)} 失败: {str(e)}')
            finally:
                # 清理临时目录
                if os.path.exists(temp_output):
                    try:
                        shutil.rmtree(temp_output)
                    except Exception as cleanup_e:
                        print(f'清理临时目录 {temp_output} 失败: {str(cleanup_e)}')

    print('批量转换完成！')