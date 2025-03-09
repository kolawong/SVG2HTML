#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SVG到HTML转换工具

该工具用于将SVG文件转换为HTML格式，同时保持元素位置、
文本内容、字体和大小不变。适用于AI前端开发辅助工具。
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Optional, List, Tuple, Dict, Any
import re
import uuid
from bs4 import BeautifulSoup
from lxml import etree
import cssutils
import logging
import svgpathtools  # 添加SVG路径处理库

# 禁用cssutils的日志
cssutils.log.setLevel(logging.CRITICAL)


class SVG2HTML:
    """SVG到HTML转换器类"""

    def __init__(self, 
                 preserve_text: bool = True, 
                 add_wrapper: bool = True,
                 conversion_mode: str = "embed",
                 precision: int = 2):
        """
        初始化转换器
        
        Args:
            preserve_text: 是否保留文本（不转为路径）
            add_wrapper: 是否添加HTML包装元素
            conversion_mode: 转换模式，"embed"表示嵌入SVG，"convert"表示转换为HTML+CSS
            precision: 数值精度（小数点后位数）
        """
        self.preserve_text = preserve_text
        self.add_wrapper = add_wrapper
        self.conversion_mode = conversion_mode
        self.precision = precision
        
    def convert_file(self, input_path: str, output_path: str) -> bool:
        """
        转换单个SVG文件为HTML
        
        Args:
            input_path: 输入SVG文件路径
            output_path: 输出HTML文件路径
            
        Returns:
            bool: 转换是否成功
        """
        try:
            # 读取SVG文件
            with open(input_path, 'r', encoding='utf-8') as f:
                svg_content = f.read()
            
            # 转换为HTML
            html_content = self.convert_svg_to_html(svg_content)
            
            # 写入HTML文件
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
                
            print(f"转换成功: {input_path} -> {output_path}")
            return True
            
        except Exception as e:
            import traceback
            print(f"转换失败 {input_path}: {str(e)}")
            traceback.print_exc()
            return False
    
    def convert_directory(self, input_dir: str, output_dir: str) -> Tuple[int, int]:
        """
        批量转换目录中的所有SVG文件
        
        Args:
            input_dir: 输入目录
            output_dir: 输出目录
            
        Returns:
            Tuple[int, int]: (成功数量, 失败数量)
        """
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        success_count = 0
        fail_count = 0
        
        # 遍历目录中的所有.svg文件
        for root, _, files in os.walk(input_dir):
            for file in files:
                if file.lower().endswith('.svg'):
                    # 构建输入输出路径
                    rel_path = os.path.relpath(os.path.join(root, file), input_dir)
                    input_file = os.path.join(root, file)
                    output_file = os.path.join(output_dir, rel_path.replace('.svg', '.html'))
                    
                    # 确保输出文件的目录存在
                    os.makedirs(os.path.dirname(output_file), exist_ok=True)
                    
                    # 转换文件
                    if self.convert_file(input_file, output_file):
                        success_count += 1
                    else:
                        fail_count += 1
        
        return success_count, fail_count
    
    def convert_svg_to_html(self, svg_content: str) -> str:
        """
        将SVG内容转换为HTML
        
        Args:
            svg_content: SVG文件内容
            
        Returns:
            str: 生成的HTML内容
        """
        # 根据转换模式选择不同的转换方法
        if self.conversion_mode.lower() == "embed":
            return self._convert_svg_to_html_embed(svg_content)
        elif self.conversion_mode.lower() == "convert":
            return self._convert_svg_to_html_full(svg_content)
        else:
            raise ValueError(f"未知的转换模式: {self.conversion_mode}")
    
    def _convert_svg_to_html_embed(self, svg_content: str) -> str:
        """
        将SVG嵌入到HTML中（简单模式）
        
        Args:
            svg_content: SVG文件内容
            
        Returns:
            str: 生成的HTML内容
        """
        # 解析SVG
        soup = BeautifulSoup(svg_content, 'xml')
        svg_tag = soup.find('svg')
        
        if not svg_tag:
            raise ValueError("无效的SVG文件：找不到<svg>标签")
        
        # 获取SVG属性
        width = svg_tag.get('width', '100%')
        height = svg_tag.get('height', '100%')
        viewBox = svg_tag.get('viewBox', '')
        
        # 创建HTML头部
        html_parts = []
        html_parts.append(f'<!DOCTYPE html>\n<html lang="zh-CN">\n<head>\n')
        html_parts.append(f'  <meta charset="UTF-8">\n')
        html_parts.append(f'  <meta name="viewport" content="width=device-width, initial-scale=1.0">\n')
        html_parts.append(f'  <title>SVG转换HTML</title>\n')
        html_parts.append(f'  <style>\n')
        html_parts.append(f'    body, html {{ margin: 0; padding: 0; overflow: hidden; }}\n')
        html_parts.append(f'    .svg-container {{ width: 100%; height: 100%; }}\n')
        html_parts.append(f'  </style>\n')
        html_parts.append(f'</head>\n<body>\n')
        
        # 添加HTML包装元素（可选）
        if self.add_wrapper:
            html_parts.append(f'<div class="svg-container">\n')
        
        # 直接嵌入SVG内容，确保保持所有属性
        # 这种方法保留了所有元素的位置、字体和大小
        html_parts.append(svg_content)
        
        # 结束HTML包装元素和文档
        if self.add_wrapper:
            html_parts.append(f'</div>\n')
        html_parts.append(f'</body>\n</html>')
        
        return ''.join(html_parts)
    
    def _convert_svg_to_html_full(self, svg_content: str) -> str:
        """
        将SVG完全转换为HTML+CSS（高级模式）
        
        Args:
            svg_content: SVG文件内容
            
        Returns:
            str: 生成的HTML内容
        """
        # 解析SVG
        soup = BeautifulSoup(svg_content, 'xml')
        svg_tag = soup.find('svg')
        
        if not svg_tag:
            raise ValueError("无效的SVG文件：找不到<svg>标签")
        
        # 获取SVG属性
        width = self._extract_dimension(svg_tag.get('width', '100%'))
        height = self._extract_dimension(svg_tag.get('height', '100%'))
        viewBox = svg_tag.get('viewBox', '')
        
        # 解析viewBox
        vb_parts = viewBox.split() if viewBox else []
        if len(vb_parts) >= 4:
            min_x, min_y, vb_width, vb_height = (float(vb_parts[i]) for i in range(4))
        else:
            # 如果没有viewBox或格式不正确，使用默认值
            min_x, min_y = 0, 0
            vb_width = float(svg_tag.get('width', '100').replace('px', '')) if svg_tag.get('width') else 100
            vb_height = float(svg_tag.get('height', '100').replace('px', '')) if svg_tag.get('height') else 100
        
        # 提取渐变定义
        gradients = {}
        for gradient in svg_tag.find_all(['linearGradient', 'radialGradient']):
            gradient_id = gradient.get('id')
            if gradient_id:
                gradients[f"url(#{gradient_id})"] = self._convert_gradient_to_css(gradient)
        
        # 创建HTML文档结构
        html_doc = BeautifulSoup('<!DOCTYPE html><html><head></head><body></body></html>', 'html.parser')
        
        # 添加头部信息
        head = html_doc.head
        meta_charset = html_doc.new_tag('meta')
        meta_charset['charset'] = 'UTF-8'
        head.append(meta_charset)
        
        meta_viewport = html_doc.new_tag('meta')
        meta_viewport['name'] = 'viewport'
        meta_viewport['content'] = 'width=device-width, initial-scale=1.0'
        head.append(meta_viewport)
        
        title = html_doc.new_tag('title')
        title.string = 'SVG转换HTML'
        head.append(title)
        
        # 创建样式标签
        style = html_doc.new_tag('style')
        css = []
        css.append('body, html { margin: 0; padding: 0; }')
        css.append('.svg-container { position: relative; width: %s; height: %s; overflow: hidden; }' % (width, height))
        css.append('.svg-element { position: absolute; }')
        
        # 主容器
        container = html_doc.new_tag('div')
        container['class'] = 'svg-container'
        html_doc.body.append(container)
        
        # 处理SVG元素
        element_id = 0
        element_styles = {}  # 用于存储元素样式，以便后续优化
        
        for element in svg_tag.find_all(True):
            tag_name = element.name
            
            # 跳过非元素节点
            if tag_name in ['svg', 'defs', 'style', 'linearGradient', 'radialGradient', 'stop']:
                continue
                
            element_id += 1
            element_class = f'svg-element-{element_id}'
            
            # 提取元素的样式和位置
            element_css = self._extract_element_style(element, tag_name, min_x, min_y, vb_width, vb_height, width, height)
            
            if element_css:
                # 替换渐变引用
                for gradient_id, gradient_css in gradients.items():
                    if gradient_id in element_css:
                        element_css = element_css.replace(gradient_id, gradient_css)
                
                # 存储样式以便后续优化
                element_styles[element_class] = self._parse_css_properties(element_css)
                
                # 创建HTML元素
                html_element = self._create_html_element(html_doc, element, tag_name, element_class)
                if html_element:
                    container.append(html_element)
        
        # 优化CSS
        optimized_css = self._optimize_css(element_styles)
        
        # 将优化后的CSS添加到样式表
        for selector, properties in optimized_css.items():
            if not properties:  # 跳过空属性
                continue
                
            if selector.startswith('.'):
                css_rule = f"{selector} {{ {'; '.join(f'{k}: {v}' for k, v in properties.items())} }}"
            elif selector.startswith('['):
                css_rule = f".svg-element{selector} {{ {'; '.join(f'{k}: {v}' for k, v in properties.items())} }}"
            else:
                css_rule = f".{selector} {{ {'; '.join(f'{k}: {v}' for k, v in properties.items())} }}"
            css.append(css_rule)
        
        # 添加折线和路径的JavaScript处理
        js_code = self._generate_path_js()
        if js_code:
            script = html_doc.new_tag('script')
            script.string = js_code
            head.append(script)
        
        # 设置CSS样式
        style.string = '\n'.join(css)
        head.append(style)
        
        # 返回完整的HTML
        return str(html_doc)
    
    def _extract_dimension(self, value: str) -> str:
        """
        从SVG维度值中提取数值和单位
        
        Args:
            value: SVG维度值（如'100px', '50%'等）
            
        Returns:
            str: 处理后的值
        """
        # 如果只是数字，添加px单位
        if value and value.replace('.', '', 1).isdigit():
            return f"{value}px"
        return value
    
    def _extract_element_style(self, element, tag_name, min_x, min_y, vb_width, vb_height, svg_width, svg_height) -> str:
        """
        提取元素的样式和位置
        
        Args:
            element: SVG元素
            tag_name: 元素标签名
            min_x, min_y, vb_width, vb_height: viewBox参数
            svg_width, svg_height: SVG尺寸
            
        Returns:
            str: CSS样式字符串
        """
        try:
            css_props = []
            
            # 获取元素的位置和尺寸
            if tag_name == 'rect':
                x = self._get_float_attr(element, 'x')
                y = self._get_float_attr(element, 'y')
                width = self._get_float_attr(element, 'width')
                height = self._get_float_attr(element, 'height')
                rx = self._get_float_attr(element, 'rx')
                ry = self._get_float_attr(element, 'ry', rx)  # 如果ry未指定，使用rx
                
                # 转换为CSS属性
                css_props.append(f"left: {self._fmt(x - min_x)}px")
                css_props.append(f"top: {self._fmt(y - min_y)}px")
                css_props.append(f"width: {self._fmt(width)}px")
                css_props.append(f"height: {self._fmt(height)}px")
                
                if rx > 0 or ry > 0:
                    if rx == ry:
                        css_props.append(f"border-radius: {self._fmt(rx)}px")
                    else:
                        css_props.append(f"border-radius: {self._fmt(rx)}px {self._fmt(ry)}px")
            
            elif tag_name == 'circle':
                cx = self._get_float_attr(element, 'cx')
                cy = self._get_float_attr(element, 'cy')
                r = self._get_float_attr(element, 'r')
                
                # 转换为CSS属性
                css_props.append(f"left: {self._fmt(cx - r - min_x)}px")
                css_props.append(f"top: {self._fmt(cy - r - min_y)}px")
                css_props.append(f"width: {self._fmt(r * 2)}px")
                css_props.append(f"height: {self._fmt(r * 2)}px")
                css_props.append("border-radius: 50%")
            
            elif tag_name == 'ellipse':
                cx = self._get_float_attr(element, 'cx')
                cy = self._get_float_attr(element, 'cy')
                rx = self._get_float_attr(element, 'rx')
                ry = self._get_float_attr(element, 'ry')
                
                # 转换为CSS属性
                css_props.append(f"left: {self._fmt(cx - rx - min_x)}px")
                css_props.append(f"top: {self._fmt(cy - ry - min_y)}px")
                css_props.append(f"width: {self._fmt(rx * 2)}px")
                css_props.append(f"height: {self._fmt(ry * 2)}px")
                css_props.append("border-radius: 50%")
            
            elif tag_name == 'line':
                x1 = self._get_float_attr(element, 'x1')
                y1 = self._get_float_attr(element, 'y1')
                x2 = self._get_float_attr(element, 'x2')
                y2 = self._get_float_attr(element, 'y2')
                
                # 计算线段的长度和角度
                length = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
                angle = self._atan2(y2 - y1, x2 - x1) * 180 / 3.14159
                
                # 转换为CSS属性
                css_props.append(f"left: {self._fmt(x1 - min_x)}px")
                css_props.append(f"top: {self._fmt(y1 - min_y)}px")
                css_props.append(f"width: {self._fmt(length)}px")
                css_props.append(f"height: 0")
                css_props.append(f"transform: rotate({angle}deg)")
                css_props.append("transform-origin: 0 0")
            
            elif tag_name == 'polyline' or tag_name == 'polygon':
                points = element.get('points', '')
                
                # 解析点坐标
                point_list = []
                for point in points.split():
                    if ',' in point:
                        try:
                            x, y = point.split(',')
                            point_list.append((float(x), float(y)))
                        except ValueError:
                            continue
                
                if point_list:
                    # 计算边界框
                    min_point_x = min(p[0] for p in point_list)
                    min_point_y = min(p[1] for p in point_list)
                    max_point_x = max(p[0] for p in point_list)
                    max_point_y = max(p[1] for p in point_list)
                    
                    # 转换为CSS属性
                    css_props.append(f"left: {self._fmt(min_point_x - min_x)}px")
                    css_props.append(f"top: {self._fmt(min_point_y - min_y)}px")
                    css_props.append(f"width: {self._fmt(max_point_x - min_point_x)}px")
                    css_props.append(f"height: {self._fmt(max_point_y - min_point_y)}px")
                    
                    # 对于polygon，可以使用clip-path
                    if tag_name == 'polygon':
                        # 创建相对于边界框的点
                        relative_points = []
                        for x, y in point_list:
                            rel_x = (x - min_point_x) / (max_point_x - min_point_x) * 100 if max_point_x > min_point_x else 0
                            rel_y = (y - min_point_y) / (max_point_y - min_point_y) * 100 if max_point_y > min_point_y else 0
                            relative_points.append(f"{self._fmt(rel_x)}% {self._fmt(rel_y)}%")
                        
                        css_props.append(f"clip-path: polygon({', '.join(relative_points)})")
                    
                    # 对于polyline，存储点数据以便JavaScript处理
                    if tag_name == 'polyline':
                        # 调整点坐标相对于元素左上角
                        adjusted_points = []
                        for x, y in point_list:
                            adj_x = x - min_point_x
                            adj_y = y - min_point_y
                            adjusted_points.append(f"{self._fmt(adj_x)},{self._fmt(adj_y)}")
                        
                        css_props.append(f"--polyline-points: '{' '.join(adjusted_points)}'")
                        
                        # 添加描边属性
                        stroke = element.get('stroke', 'black')
                        stroke_width = element.get('stroke-width', '1')
                        css_props.append(f"--polyline-stroke: '{stroke}'")
                        css_props.append(f"--polyline-stroke-width: '{stroke_width}'")
            
            elif tag_name == 'path':
                path_data = element.get('d', '')
                
                # 计算路径的边界框
                bounds = self._calculate_path_bounds(path_data)
                
                if bounds:
                    path_min_x, path_min_y, path_max_x, path_max_y = bounds
                    
                    # 转换为CSS属性
                    css_props.append(f"left: {self._fmt(path_min_x - min_x)}px")
                    css_props.append(f"top: {self._fmt(path_min_y - min_y)}px")
                    css_props.append(f"width: {self._fmt(path_max_x - path_min_x)}px")
                    css_props.append(f"height: {self._fmt(path_max_y - path_min_y)}px")
                    
                    # 存储路径数据以便JavaScript处理
                    css_props.append(f"--path-data: '{path_data}'")
            
            elif tag_name == 'text':
                x = self._get_float_attr(element, 'x')
                y = self._get_float_attr(element, 'y')
                
                # 获取文本高度
                text_height = self._get_text_height(element)
                
                # 转换为CSS属性
                css_props.append(f"left: {self._fmt(x - min_x)}px")
                css_props.append(f"top: {self._fmt(y - min_y - text_height)}px")
                
                # 添加字体属性
                font_family = element.get('font-family', 'sans-serif')
                font_size = element.get('font-size', '16')
                css_props.append(f"font-family: {font_family}")
                css_props.append(f"font-size: {font_size}")
            
            # 处理通用样式属性
            fill = element.get('fill')
            if fill and fill != 'none':
                # 检查是否是渐变引用
                if fill.startswith('url(#'):
                    css_props.append(f"background-color: {fill}")
                else:
                    css_props.append(f"background-color: {fill}")
            elif fill == 'none':
                css_props.append("background-color: transparent")
            
            stroke = element.get('stroke')
            if stroke and stroke != 'none':
                stroke_width = element.get('stroke-width', '1')
                css_props.append(f"border: {stroke_width}px solid {stroke}")
            
            # 处理style属性
            style_attr = element.get('style', '')
            if style_attr:
                css_props.append(self._convert_svg_style_to_css(style_attr))
            
            # 处理transform属性
            transform = element.get('transform', '')
            if transform:
                css_props.append(self._convert_svg_transform_to_css(transform))
            
            return '; '.join(css_props)
        except Exception as e:
            import traceback
            print(f"提取元素样式失败 {tag_name}: {str(e)}")
            traceback.print_exc()
            return ""
    
    def _create_html_element(self, doc, svg_element, tag_name, element_class):
        """
        创建对应的HTML元素
        
        Args:
            doc: BeautifulSoup文档
            svg_element: SVG元素
            tag_name: 元素标签名
            element_class: 元素CSS类名
            
        Returns:
            BeautifulSoup标签对象
        """
        html_element = None
        
        if tag_name in ['rect', 'circle', 'ellipse', 'line', 'path', 'polygon', 'polyline']:
            html_element = doc.new_tag('div')
            html_element['class'] = f"{element_class} svg-element"
            html_element['data-type'] = tag_name
            
            # 处理填充和描边颜色
            fill = svg_element.get('fill')
            if fill and fill != 'none':
                # 检查是否是渐变引用
                if fill.startswith('url(#'):
                    # 获取渐变ID
                    gradient_id = fill[5:-1]  # 去掉url(# 和 )
                    # 查找对应的渐变元素
                    gradient = svg_element.find_parent('svg').find(id=gradient_id)
                    if gradient:
                        # 转换为CSS渐变
                        css_gradient = self._convert_gradient_to_css(gradient)
                        html_element['style'] = f"background: {css_gradient};"
                    else:
                        html_element['style'] = f"background-color: {fill};"
                else:
                    html_element['style'] = f"background-color: {fill};"
            
            # 对于路径和折线，添加原始数据
            if tag_name == 'path':
                path_data = svg_element.get('d', '')
                if path_data:
                    if 'style' in html_element.attrs:
                        html_element['style'] += f" --path-data: '{path_data}';"
                    else:
                        html_element['style'] = f"--path-data: '{path_data}';"
            
            elif tag_name == 'polyline':
                points = svg_element.get('points', '')
                if points:
                    if 'style' in html_element.attrs:
                        html_element['style'] += f" --polyline-points: '{points}';"
                    else:
                        html_element['style'] = f"--polyline-points: '{points}';"
                    
                    stroke = svg_element.get('stroke', 'black')
                    stroke_width = svg_element.get('stroke-width', '1')
                    html_element['style'] += f" --polyline-stroke: '{stroke}'; --polyline-stroke-width: '{stroke_width}';"
            
            elif tag_name == 'polygon':
                points = svg_element.get('points', '')
                if points:
                    # 解析点坐标
                    point_list = []
                    for point in points.split():
                        if ',' in point:
                            try:
                                x, y = point.split(',')
                                point_list.append((float(x), float(y)))
                            except ValueError:
                                continue
                    
                    if point_list:
                        # 计算边界框
                        min_point_x = min(p[0] for p in point_list)
                        min_point_y = min(p[1] for p in point_list)
                        max_point_x = max(p[0] for p in point_list)
                        max_point_y = max(p[1] for p in point_list)
                        
                        # 创建相对于边界框的点
                        relative_points = []
                        for x, y in point_list:
                            rel_x = (x - min_point_x) / (max_point_x - min_point_x) * 100 if max_point_x > min_point_x else 0
                            rel_y = (y - min_point_y) / (max_point_y - min_point_y) * 100 if max_point_y > min_point_y else 0
                            relative_points.append(f"{self._fmt(rel_x)}% {self._fmt(rel_y)}%")
                        
                        # 添加clip-path属性
                        if 'style' in html_element.attrs:
                            html_element['style'] += f" clip-path: polygon({', '.join(relative_points)});"
                        else:
                            html_element['style'] = f"clip-path: polygon({', '.join(relative_points)});"
        
        elif tag_name == 'text':
            html_element = doc.new_tag('div')
            html_element['class'] = f"{element_class} svg-element"
            html_element['data-type'] = 'text'
            
            # 获取文本内容
            text_content = svg_element.string or ''.join(t.string or '' for t in svg_element.find_all(string=True))
            html_element.string = text_content
            
            # 处理文本颜色
            fill = svg_element.get('fill', '#000000')
            if fill and fill != 'none':
                html_element['style'] = f"color: {fill};"
        
        elif tag_name == 'foreignObject':
            # 处理foreignObject元素
            html_element = doc.new_tag('div')
            html_element['class'] = f"{element_class} svg-element"
            html_element['data-type'] = 'foreignObject'
            
            # 直接提取内部HTML
            inner_html = ''.join(str(c) for c in svg_element.children)
            temp_soup = BeautifulSoup(inner_html, 'html.parser')
            for child in temp_soup.children:
                if child.name:
                    html_element.append(child)
        
        return html_element
    
    def _parse_style_attr(self, style_attr: str) -> Dict[str, str]:
        """
        解析SVG样式属性字符串
        
        Args:
            style_attr: 样式属性字符串
            
        Returns:
            Dict[str, str]: 样式字典
        """
        style_dict = {}
        if not style_attr:
            return style_dict
            
        parts = style_attr.split(';')
        for part in parts:
            if ':' in part:
                key, value = part.split(':', 1)
                style_dict[key.strip()] = value.strip()
                
        return style_dict
    
    def _convert_svg_style_to_css(self, svg_style: str) -> str:
        """
        将SVG样式名称转换为CSS样式名称
        
        Args:
            svg_style: SVG样式名称
            
        Returns:
            str: CSS样式名称
        """
        # SVG到CSS样式映射
        style_map = {
            'fill': 'background-color',
            'fill-opacity': 'opacity',
            'stroke': 'border-color',
            'stroke-width': 'border-width',
            'stroke-opacity': 'border-opacity',
            'font-family': 'font-family',
            'font-size': 'font-size',
            'text-anchor': 'text-align'
        }
        
        return style_map.get(svg_style, svg_style)
    
    def _convert_svg_transform_to_css(self, transform: str) -> str:
        """
        将SVG变换转换为CSS变换
        
        Args:
            transform: SVG变换字符串
            
        Returns:
            str: CSS变换字符串
        """
        # 简单处理旋转变换
        if 'rotate' in transform:
            match = re.search(r'rotate\(([^,]+)(?:,([^,]+),([^)]+))?\)', transform)
            if match:
                angle = match.group(1)
                if match.group(2) and match.group(3):
                    cx, cy = match.group(2), match.group(3)
                    return f"rotate({angle}deg) translate({cx}px, {cy}px) rotate(-{angle}deg) translate(-{cx}px, -{cy}px)"
                else:
                    return f"rotate({angle}deg)"
        
        # 简单处理平移变换
        elif 'translate' in transform:
            match = re.search(r'translate\(([^,]+)(?:,([^)]+))?\)', transform)
            if match:
                tx = match.group(1)
                ty = match.group(2) if match.group(2) else '0'
                return f"translate({tx}px, {ty}px)"
        
        # 简单处理缩放变换
        elif 'scale' in transform:
            match = re.search(r'scale\(([^,]+)(?:,([^)]+))?\)', transform)
            if match:
                sx = match.group(1)
                sy = match.group(2) if match.group(2) else sx
                return f"scale({sx}, {sy})"
        
        return transform  # 如果无法处理，返回原字符串
    
    def _calculate_path_bounds(self, path_data: str) -> Optional[Tuple[float, float, float, float]]:
        """
        计算SVG路径的边界框
        
        Args:
            path_data: SVG路径数据
            
        Returns:
            Optional[Tuple[float, float, float, float]]: 边界框 (min_x, min_y, max_x, max_y)
        """
        try:
            # 尝试使用svgpathtools库解析路径
            try:
                from svgpathtools import parse_path
                path = parse_path(path_data)
                
                # 获取路径的边界框
                if path:
                    bbox = path.bbox()
                    return (bbox[0], bbox[1], bbox[2], bbox[3])
            except (ImportError, ValueError, IndexError) as e:
                print(f"使用svgpathtools解析路径失败: {str(e)}")
                # 如果svgpathtools解析失败，回退到正则表达式方法
                pass
                
            # 使用正则表达式提取路径中的坐标
            import re
            
            # 提取所有数字对
            coords = re.findall(r'([+-]?\d*\.?\d+)[,\s]([+-]?\d*\.?\d+)', path_data)
            
            if not coords:
                return None
                
            # 转换为浮点数
            points = [(float(x), float(y)) for x, y in coords]
            
            # 计算边界框
            min_x = min(p[0] for p in points)
            min_y = min(p[1] for p in points)
            max_x = max(p[0] for p in points)
            max_y = max(p[1] for p in points)
            
            return (min_x, min_y, max_x, max_y)
            
        except Exception as e:
            print(f"计算路径边界框失败: {str(e)}")
            # 返回一个默认的边界框
            return (0, 0, 100, 100)
    
    def _get_float_attr(self, element, attr_name: str, default: float = 0) -> float:
        """
        获取元素属性的浮点值
        
        Args:
            element: SVG元素
            attr_name: 属性名
            default: 默认值
            
        Returns:
            float: 属性值
        """
        value = element.get(attr_name, str(default))
        try:
            # 移除单位后转换为浮点数
            value = re.sub(r'[a-z%]+$', '', value)
            return float(value)
        except ValueError:
            return default
    
    def _get_text_height(self, element) -> float:
        """
        计算文本元素的高度
        
        Args:
            element: 文本元素
            
        Returns:
            float: 文本高度
        """
        font_size = self._get_float_attr(element, 'font-size', 16)
        # 简单估算：字体大小的1.2倍作为文本高度
        return font_size * 1.2
    
    def _fmt(self, value: float) -> str:
        """
        格式化浮点数，控制精度
        
        Args:
            value: 浮点数
            
        Returns:
            str: 格式化后的字符串
        """
        return format(value, f'.{self.precision}f').rstrip('0').rstrip('.')
        
    def _atan2(self, y: float, x: float) -> float:
        """
        计算反正切值
        
        Args:
            y: Y坐标
            x: X坐标
            
        Returns:
            float: 反正切值
        """
        if x == 0:
            return 1.5707963267948966 if y > 0 else -1.5707963267948966
        return round(float(y) / float(x), 8) if x != 0 else 0
    
    def _parse_css_properties(self, css_string: str) -> Dict[str, str]:
        """
        解析CSS属性字符串为字典
        
        Args:
            css_string: CSS属性字符串
            
        Returns:
            Dict[str, str]: CSS属性字典
        """
        properties = {}
        for prop in css_string.split(';'):
            if not prop.strip():
                continue
            
            if ':' in prop:
                key, value = prop.split(':', 1)
                properties[key.strip()] = value.strip()
        
        return properties
    
    def _optimize_css(self, element_styles: Dict[str, Dict[str, str]]) -> Dict[str, Dict[str, str]]:
        """
        优化CSS，提取公共样式
        
        Args:
            element_styles: 元素样式字典
            
        Returns:
            Dict[str, Dict[str, str]]: 优化后的CSS
        """
        try:
            # 复制原始样式
            optimized = {selector: props.copy() for selector, props in element_styles.items()}
            
            # 查找公共样式
            common_styles = {}
            all_selectors = list(element_styles.keys())
            
            # 按元素类型分组
            element_types = {}
            for selector in all_selectors:
                # 从类名中提取元素类型
                if '-' in selector and 'element' in selector:
                    parts = selector.split('-')
                    if len(parts) >= 2 and 'element' in parts[0]:
                        element_type = parts[1]  # 例如：svg-element-7 -> 7
                        if element_type not in element_types:
                            element_types[element_type] = []
                        element_types[element_type].append(selector)
            
            # 为每种元素类型创建公共样式
            for element_type, selectors in element_types.items():
                if len(selectors) < 2:
                    continue
                    
                # 查找这种元素类型的所有选择器中的公共属性
                common_props = {}
                first_selector = selectors[0]
                first_props = element_styles[first_selector]
                
                for prop, value in first_props.items():
                    # 检查是否所有选择器都有相同的属性值
                    if all(element_styles[sel].get(prop) == value for sel in selectors):
                        common_props[prop] = value
                
                # 如果有公共属性，创建一个新的选择器
                if common_props:
                    type_selector = f"[data-type='{element_type}']"
                    common_styles[type_selector] = common_props
                    
                    # 从原始样式中移除公共属性
                    for selector in selectors:
                        for prop in common_props:
                            if prop in optimized[selector]:
                                del optimized[selector][prop]
            
            # 合并结果
            optimized.update(common_styles)
            
            return optimized
        except Exception as e:
            import traceback
            print(f"优化CSS失败: {str(e)}")
            traceback.print_exc()
            return element_styles  # 如果优化失败，返回原始样式
    
    def _generate_path_js(self) -> str:
        """
        生成处理路径和折线的JavaScript代码
        
        Returns:
            str: JavaScript代码
        """
        return """
        document.addEventListener('DOMContentLoaded', function() {
            // 处理折线
            var polylines = document.querySelectorAll('[data-type="polyline"]');
            polylines.forEach(function(element) {
                var points = element.style.getPropertyValue('--polyline-points');
                var stroke = element.style.getPropertyValue('--polyline-stroke');
                var strokeWidth = element.style.getPropertyValue('--polyline-stroke-width');
                
                if (points && stroke) {
                    // 创建SVG元素来绘制折线
                    var svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
                    svg.setAttribute('width', '100%');
                    svg.setAttribute('height', '100%');
                    svg.style.position = 'absolute';
                    svg.style.top = '0';
                    svg.style.left = '0';
                    
                    var polyline = document.createElementNS('http://www.w3.org/2000/svg', 'polyline');
                    polyline.setAttribute('points', points.replace(/'/g, ''));
                    polyline.setAttribute('stroke', stroke.replace(/'/g, ''));
                    polyline.setAttribute('stroke-width', strokeWidth.replace(/'/g, ''));
                    polyline.setAttribute('fill', 'none');
                    
                    svg.appendChild(polyline);
                    element.appendChild(svg);
                }
            });
            
            // 处理路径
            var paths = document.querySelectorAll('[data-type="path"]');
            paths.forEach(function(element) {
                var pathData = element.style.getPropertyValue('--path-data');
                var fill = window.getComputedStyle(element).backgroundColor;
                var stroke = window.getComputedStyle(element).borderColor;
                var strokeWidth = window.getComputedStyle(element).borderWidth;
                
                if (pathData) {
                    // 创建SVG元素来绘制路径
                    var svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
                    svg.setAttribute('width', '100%');
                    svg.setAttribute('height', '100%');
                    svg.style.position = 'absolute';
                    svg.style.top = '0';
                    svg.style.left = '0';
                    
                    var path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
                    path.setAttribute('d', pathData.replace(/'/g, ''));
                    
                    // 设置填充和描边
                    if (fill && fill !== 'rgba(0, 0, 0, 0)') {
                        path.setAttribute('fill', fill);
                    } else {
                        path.setAttribute('fill', 'none');
                    }
                    
                    if (stroke && stroke !== 'rgba(0, 0, 0, 0)' && strokeWidth && strokeWidth !== '0px') {
                        path.setAttribute('stroke', stroke);
                        path.setAttribute('stroke-width', strokeWidth);
                    }
                    
                    svg.appendChild(path);
                    element.appendChild(svg);
                }
            });
            
            // 处理多边形
            var polygons = document.querySelectorAll('[data-type="polygon"]');
            polygons.forEach(function(element) {
                // 确保背景色正确应用
                var fill = window.getComputedStyle(element).backgroundColor;
                if (fill === 'rgba(0, 0, 0, 0)' || fill === 'transparent') {
                    // 如果没有背景色，尝试应用一个默认颜色
                    element.style.backgroundColor = '#000000';
                }
            });
        });
        """
    
    def _convert_gradient_to_css(self, gradient) -> str:
        """
        将SVG渐变转换为CSS渐变
        
        Args:
            gradient: SVG渐变元素
            
        Returns:
            str: CSS渐变字符串
        """
        gradient_type = gradient.name
        
        if gradient_type == 'linearGradient':
            # 获取渐变属性
            x1 = gradient.get('x1', '0%')
            y1 = gradient.get('y1', '0%')
            x2 = gradient.get('x2', '100%')
            y2 = gradient.get('y2', '100%')
            
            # 创建CSS线性渐变
            css_gradient = f"linear-gradient({self._calculate_angle(x1, y1, x2, y2)}"
            
            # 添加渐变停止点
            stops = []
            for stop in gradient.find_all('stop'):
                offset = stop.get('offset', '0%')
                color = stop.get('stop-color', '#000')
                opacity = stop.get('stop-opacity', '1')
                
                # 如果颜色不包含透明度，且透明度不是1，则添加透明度
                if 'rgba' not in color.lower() and opacity != '1':
                    # 将十六进制颜色转换为RGB
                    if color.startswith('#'):
                        r, g, b = self._hex_to_rgb(color)
                        color = f"rgba({r}, {g}, {b}, {opacity})"
                
                stops.append(f"{color} {offset}")
            
            css_gradient += ", " + ", ".join(stops) + ")"
            return css_gradient
            
        elif gradient_type == 'radialGradient':
            # 获取渐变属性
            cx = gradient.get('cx', '50%')
            cy = gradient.get('cy', '50%')
            r = gradient.get('r', '50%')
            fx = gradient.get('fx', cx)
            fy = gradient.get('fy', cy)
            
            # 创建CSS径向渐变
            css_gradient = f"radial-gradient(circle at {cx} {cy}"
            
            # 添加渐变停止点
            stops = []
            for stop in gradient.find_all('stop'):
                offset = stop.get('offset', '0%')
                color = stop.get('stop-color', '#000')
                opacity = stop.get('stop-opacity', '1')
                
                # 如果颜色不包含透明度，且透明度不是1，则添加透明度
                if 'rgba' not in color.lower() and opacity != '1':
                    # 将十六进制颜色转换为RGB
                    if color.startswith('#'):
                        r, g, b = self._hex_to_rgb(color)
                        color = f"rgba({r}, {g}, {b}, {opacity})"
                
                stops.append(f"{color} {offset}")
            
            css_gradient += ", " + ", ".join(stops) + ")"
            return css_gradient
            
        return ""
    
    def _calculate_angle(self, x1, y1, x2, y2) -> str:
        """
        计算线性渐变的角度
        
        Args:
            x1, y1, x2, y2: 渐变的起点和终点坐标
            
        Returns:
            str: 角度字符串
        """
        # 将百分比转换为数值
        x1_val = float(x1.rstrip('%')) if '%' in x1 else float(x1)
        y1_val = float(y1.rstrip('%')) if '%' in y1 else float(y1)
        x2_val = float(x2.rstrip('%')) if '%' in x2 else float(x2)
        y2_val = float(y2.rstrip('%')) if '%' in y2 else float(y2)
        
        # 计算角度（弧度）
        angle_rad = self._atan2(y2_val - y1_val, x2_val - x1_val)
        
        # 转换为度数（CSS渐变角度是顺时针的，而atan2是逆时针的）
        angle_deg = (90 - angle_rad * 180 / 3.14159) % 360
        
        return f"{angle_deg:.1f}deg"
    
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """
        将十六进制颜色转换为RGB
        
        Args:
            hex_color: 十六进制颜色字符串
            
        Returns:
            Tuple[int, int, int]: RGB颜色值
        """
        hex_color = hex_color.lstrip('#')
        
        if len(hex_color) == 3:
            hex_color = ''.join([c*2 for c in hex_color])
            
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        return r, g, b


def parse_arguments() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='将SVG文件转换为HTML，保持元素位置和文本属性')
    
    # 添加命令行参数
    parser.add_argument('input', help='输入的SVG文件或目录')
    parser.add_argument('output', help='输出的HTML文件或目录')
    parser.add_argument('--dir', action='store_true', help='批量转换目录中的所有SVG文件')
    parser.add_argument('--no-text-preserve', action='store_true', help='不保留文本特性（默认保留）')
    parser.add_argument('--no-wrapper', action='store_true', help='不添加HTML包装元素（默认添加）')
    parser.add_argument('--mode', choices=['embed', 'convert'], default='embed', 
                        help='转换模式：embed-嵌入SVG，convert-转换为HTML+CSS（默认：embed）')
    parser.add_argument('--precision', type=int, default=2, help='数值精度（小数点后位数，默认：2）')
    
    return parser.parse_args()


def main():
    """主函数"""
    args = parse_arguments()
    
    # 创建转换器
    converter = SVG2HTML(
        preserve_text=not args.no_text_preserve,
        add_wrapper=not args.no_wrapper,
        conversion_mode=args.mode,
        precision=args.precision
    )
    
    # 根据参数执行转换
    if args.dir:
        # 批量转换目录
        success, fail = converter.convert_directory(args.input, args.output)
        print(f"转换完成：{success}个成功，{fail}个失败")
    else:
        # 转换单个文件
        if converter.convert_file(args.input, args.output):
            print("转换成功！")
            sys.exit(0)
        else:
            print("转换失败！")
            sys.exit(1)


if __name__ == "__main__":
    main() 