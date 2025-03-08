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
        转换单个SVG文件到HTML
        
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
            
            # 转换SVG到HTML
            html_content = self.convert_svg_to_html(svg_content)
            
            # 写入输出文件
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
                
            print(f"成功转换: {input_path} -> {output_path}")
            return True
        except Exception as e:
            print(f"转换失败 {input_path}: {str(e)}")
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
        min_x, min_y, vb_width, vb_height = (float(vb_parts[i]) if i < len(vb_parts) else 0 for i in range(4))
        
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
            if tag_name in ['svg', 'defs', 'style']:
                continue
                
            element_id += 1
            element_class = f'svg-element-{element_id}'
            
            # 提取元素的样式和位置
            element_css = self._extract_element_style(element, tag_name, min_x, min_y, vb_width, vb_height, width, height)
            
            if element_css:
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
            css_rule = f"{selector} {{ {'; '.join(f'{k}: {v}' for k, v in properties.items())}; }}"
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
        从SVG元素中提取CSS样式
        
        Args:
            element: SVG元素
            tag_name: 元素标签名
            min_x, min_y, vb_width, vb_height: viewBox参数
            svg_width, svg_height: SVG尺寸
            
        Returns:
            str: CSS样式字符串
        """
        css_props = []
        
        # 基本样式
        css_props.append("position: absolute;")
        
        # 从元素属性和样式中提取CSS属性
        style_attr = element.get('style', '')
        if style_attr:
            # 解析内联样式
            style_dict = self._parse_style_attr(style_attr)
            for key, value in style_dict.items():
                css_key = self._convert_svg_style_to_css(key)
                if css_key:
                    css_props.append(f"{css_key}: {value};")
        
        # 处理位置和尺寸
        if tag_name == 'rect':
            x = self._get_float_attr(element, 'x', 0)
            y = self._get_float_attr(element, 'y', 0)
            width = self._get_float_attr(element, 'width', 0)
            height = self._get_float_attr(element, 'height', 0)
            rx = self._get_float_attr(element, 'rx', 0)
            ry = self._get_float_attr(element, 'ry', 0)
            
            css_props.append(f"left: {self._fmt(x)}px;")
            css_props.append(f"top: {self._fmt(y)}px;")
            css_props.append(f"width: {self._fmt(width)}px;")
            css_props.append(f"height: {self._fmt(height)}px;")
            
            if rx > 0 or ry > 0:
                border_radius = max(rx, ry)
                css_props.append(f"border-radius: {self._fmt(border_radius)}px;")
            
            # 背景颜色
            fill = element.get('fill', 'none')
            if fill and fill.lower() != 'none':
                css_props.append(f"background-color: {fill};")
            
            # 边框
            stroke = element.get('stroke')
            stroke_width = self._get_float_attr(element, 'stroke-width', 1)
            if stroke and stroke.lower() != 'none':
                css_props.append(f"border: {self._fmt(stroke_width)}px solid {stroke};")
                
        elif tag_name == 'circle':
            cx = self._get_float_attr(element, 'cx', 0)
            cy = self._get_float_attr(element, 'cy', 0)
            r = self._get_float_attr(element, 'r', 0)
            
            css_props.append(f"left: {self._fmt(cx - r)}px;")
            css_props.append(f"top: {self._fmt(cy - r)}px;")
            css_props.append(f"width: {self._fmt(2 * r)}px;")
            css_props.append(f"height: {self._fmt(2 * r)}px;")
            css_props.append(f"border-radius: 50%;")
            
            # 背景颜色
            fill = element.get('fill', 'none')
            if fill and fill.lower() != 'none':
                css_props.append(f"background-color: {fill};")
            
            # 边框
            stroke = element.get('stroke')
            stroke_width = self._get_float_attr(element, 'stroke-width', 1)
            if stroke and stroke.lower() != 'none':
                css_props.append(f"border: {self._fmt(stroke_width)}px solid {stroke};")
                
        elif tag_name == 'ellipse':
            # 添加椭圆支持
            cx = self._get_float_attr(element, 'cx', 0)
            cy = self._get_float_attr(element, 'cy', 0)
            rx = self._get_float_attr(element, 'rx', 0)
            ry = self._get_float_attr(element, 'ry', 0)
            
            css_props.append(f"left: {self._fmt(cx - rx)}px;")
            css_props.append(f"top: {self._fmt(cy - ry)}px;")
            css_props.append(f"width: {self._fmt(2 * rx)}px;")
            css_props.append(f"height: {self._fmt(2 * ry)}px;")
            css_props.append(f"border-radius: 50%;")
            
            # 背景颜色
            fill = element.get('fill', 'none')
            if fill and fill.lower() != 'none':
                css_props.append(f"background-color: {fill};")
            
            # 边框
            stroke = element.get('stroke')
            stroke_width = self._get_float_attr(element, 'stroke-width', 1)
            if stroke and stroke.lower() != 'none':
                css_props.append(f"border: {self._fmt(stroke_width)}px solid {stroke};")
                
        elif tag_name == 'line':
            x1 = self._get_float_attr(element, 'x1', 0)
            y1 = self._get_float_attr(element, 'y1', 0)
            x2 = self._get_float_attr(element, 'x2', 0)
            y2 = self._get_float_attr(element, 'y2', 0)
            
            width = abs(x2 - x1)
            height = abs(y2 - y1)
            angle = 0
            
            if width > 0 or height > 0:
                angle = round(180 * (1 if y2 > y1 else -1) * (0 if width == 0 else 
                             (90 if height == 0 else (180 / 3.14159) * 
                              (1 if x2 > x1 else -1) * (1 if y2 > y1 else -1) * 
                              (3.14159 / 2 - abs(self._atan2(y2 - y1, x2 - x1))))
                             ), 2)
            
            # 线条是从左上角到右下角
            origin_x = min(x1, x2)
            origin_y = min(y1, y2)
            
            # 如果线条是水平的
            if abs(y1 - y2) < 0.01:
                css_props.append(f"left: {self._fmt(origin_x)}px;")
                css_props.append(f"top: {self._fmt(y1 - self._get_float_attr(element, 'stroke-width', 1) / 2)}px;")
                css_props.append(f"width: {self._fmt(width)}px;")
                css_props.append(f"height: {self._fmt(self._get_float_attr(element, 'stroke-width', 1))}px;")
            
            # 如果线条是垂直的
            elif abs(x1 - x2) < 0.01:
                css_props.append(f"left: {self._fmt(x1 - self._get_float_attr(element, 'stroke-width', 1) / 2)}px;")
                css_props.append(f"top: {self._fmt(origin_y)}px;")
                css_props.append(f"width: {self._fmt(self._get_float_attr(element, 'stroke-width', 1))}px;")
                css_props.append(f"height: {self._fmt(height)}px;")
            
            # 如果线条是倾斜的
            else:
                length = (((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5)
                css_props.append(f"left: {self._fmt(x1)}px;")
                css_props.append(f"top: {self._fmt(y1)}px;")
                css_props.append(f"width: {self._fmt(length)}px;")
                css_props.append(f"height: {self._fmt(self._get_float_attr(element, 'stroke-width', 1))}px;")
                css_props.append(f"transform-origin: 0 0;")
                css_props.append(f"transform: rotate({angle}deg);")
            
            # 线条颜色
            stroke = element.get('stroke', 'black')
            css_props.append(f"background-color: {stroke};")
            
        elif tag_name == 'polyline' or tag_name == 'polygon':
            # 添加折线和多边形支持
            points_str = element.get('points', '')
            if not points_str:
                return ' '.join(css_props)
                
            # 解析点坐标
            points = []
            for point in points_str.split():
                if ',' in point:
                    x, y = point.split(',')
                    try:
                        points.append((float(x), float(y)))
                    except ValueError:
                        continue
            
            if not points:
                return ' '.join(css_props)
                
            # 计算边界框
            min_x = min(p[0] for p in points)
            min_y = min(p[1] for p in points)
            max_x = max(p[0] for p in points)
            max_y = max(p[1] for p in points)
            
            css_props.append(f"left: {self._fmt(min_x)}px;")
            css_props.append(f"top: {self._fmt(min_y)}px;")
            css_props.append(f"width: {self._fmt(max_x - min_x)}px;")
            css_props.append(f"height: {self._fmt(max_y - min_y)}px;")
            
            # 对于多边形，添加背景色
            if tag_name == 'polygon':
                fill = element.get('fill', 'none')
                if fill and fill.lower() != 'none':
                    css_props.append(f"background-color: {fill};")
                    
                    # 创建一个多边形形状的CSS clip-path
                    normalized_points = []
                    for x, y in points:
                        nx = (x - min_x) / (max_x - min_x) * 100
                        ny = (y - min_y) / (max_y - min_y) * 100
                        normalized_points.append(f"{self._fmt(nx)}% {self._fmt(ny)}%")
                    
                    clip_path = f"polygon({', '.join(normalized_points)})"
                    css_props.append(f"clip-path: {clip_path};")
            
            # 边框
            stroke = element.get('stroke')
            stroke_width = self._get_float_attr(element, 'stroke-width', 1)
            if stroke and stroke.lower() != 'none':
                if tag_name == 'polygon':
                    css_props.append(f"border: {self._fmt(stroke_width)}px solid {stroke};")
                else:
                    # 对于折线，使用背景色模拟线条
                    css_props.append(f"background-color: transparent;")
                    css_props.append(f"border: none;")
                    
                    # 创建一个自定义属性来存储点信息，用于JavaScript处理
                    points_data = ' '.join(f"{self._fmt(x)},{self._fmt(y)}" for x, y in points)
                    css_props.append(f"--polyline-points: '{points_data}';")
                    css_props.append(f"--polyline-stroke: '{stroke}';")
                    css_props.append(f"--polyline-stroke-width: '{self._fmt(stroke_width)}';")
            
        elif tag_name == 'text':
            x = self._get_float_attr(element, 'x', 0)
            y = self._get_float_attr(element, 'y', 0)
            
            css_props.append(f"left: {self._fmt(x)}px;")
            css_props.append(f"top: {self._fmt(y - self._get_text_height(element))}px;")
            
            # 文本属性
            font_family = element.get('font-family', 'sans-serif')
            font_size = element.get('font-size', '16px')
            fill = element.get('fill', 'black')
            
            css_props.append(f"font-family: {font_family};")
            css_props.append(f"font-size: {font_size};")
            css_props.append(f"color: {fill};")
            
            # 文本锚点
            text_anchor = element.get('text-anchor', 'start')
            if text_anchor == 'middle':
                css_props.append("text-align: center;")
            elif text_anchor == 'end':
                css_props.append("text-align: right;")
                
            # 变换
            transform = element.get('transform', '')
            if transform:
                css_transform = self._convert_svg_transform_to_css(transform)
                if css_transform:
                    css_props.append(f"transform: {css_transform};")
        
        elif tag_name == 'path':
            # 路径转换为边框，这里使用改进的路径处理
            stroke = element.get('stroke', 'none')
            fill = element.get('fill', 'none')
            d = element.get('d', '')
            
            # 计算路径边界
            path_bounds = self._calculate_path_bounds(d)
            if path_bounds:
                x, y, width, height = path_bounds
                css_props.append(f"left: {self._fmt(x)}px;")
                css_props.append(f"top: {self._fmt(y)}px;")
                css_props.append(f"width: {self._fmt(width)}px;")
                css_props.append(f"height: {self._fmt(height)}px;")
                
                # 如果有填充色
                if fill and fill.lower() != 'none':
                    css_props.append(f"background-color: {fill};")
                    
                    # 存储路径数据用于可能的JavaScript处理
                    css_props.append(f"--path-data: '{d}';")
                
                # 如果有描边
                if stroke and stroke.lower() != 'none':
                    stroke_width = self._get_float_attr(element, 'stroke-width', 1)
                    css_props.append(f"border: {self._fmt(stroke_width)}px solid {stroke};")
        
        return ' '.join(css_props)
    
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
            
        elif tag_name == 'text':
            html_element = doc.new_tag('div')
            html_element['class'] = f"{element_class} svg-element"
            html_element['data-type'] = 'text'
            
            # 获取文本内容
            text_content = svg_element.string or ''.join(t.string or '' for t in svg_element.find_all(text=True))
            html_element.string = text_content
            
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
            path_data: 路径数据字符串
            
        Returns:
            Optional[Tuple[float, float, float, float]]: (x, y, width, height)
        """
        if not path_data:
            return None
            
        try:
            # 使用svgpathtools解析路径
            path = svgpathtools.parse_path(path_data)
            
            # 如果路径为空，返回None
            if not path:
                return None
                
            # 计算路径的边界框
            xmin, xmax, ymin, ymax = path.bbox()
            
            return (xmin, ymin, xmax - xmin, ymax - ymin)
        except Exception:
            # 如果解析失败，回退到简单的正则表达式方法
            numbers = re.findall(r'[-+]?\d*\.\d+|[-+]?\d+', path_data)
            points = []
            
            for i in range(0, len(numbers) - 1, 2):
                try:
                    x, y = float(numbers[i]), float(numbers[i + 1])
                    points.append((x, y))
                except (ValueError, IndexError):
                    continue
            
            if not points:
                return None
                
            # 计算边界框
            min_x = min(p[0] for p in points)
            min_y = min(p[1] for p in points)
            max_x = max(p[0] for p in points)
            max_y = max(p[1] for p in points)
            
            return (min_x, min_y, max_x - min_x, max_y - min_y)
    
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
        # 复制原始样式
        optimized = {selector: props.copy() for selector, props in element_styles.items()}
        
        # 查找公共样式
        common_styles = {}
        all_selectors = list(element_styles.keys())
        
        # 按元素类型分组
        element_types = {}
        for selector in all_selectors:
            # 从类名中提取元素类型
            if '-' in selector:
                element_type = selector.split('-')[1]
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
                type_selector = f".svg-element[data-type='{element_type}']"
                common_styles[type_selector] = common_props
                
                # 从原始样式中移除公共属性
                for selector in selectors:
                    for prop in common_props:
                        if prop in optimized[selector]:
                            del optimized[selector][prop]
        
        # 合并结果
        optimized.update(common_styles)
        
        return optimized
    
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
                    path.setAttribute('fill', 'inherit');
                    path.setAttribute('stroke', 'inherit');
                    
                    svg.appendChild(path);
                    element.appendChild(svg);
                }
            });
        });
        """


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