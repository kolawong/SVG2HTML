#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GUI预览模块

包含SVG2HTML GUI应用程序的预览功能实现。
"""

import os
import tempfile
from PyQt5.QtCore import QUrl


def update_preview(window):
    """更新预览"""
    # 检查是否有输入文件
    if not window.input_file or not os.path.isfile(window.input_file):
        return
    
    # 更新SVG预览
    update_svg_preview(window, window.input_file)
    
    # 更新HTML预览
    if window.output_file and os.path.isfile(window.output_file):
        update_html_preview(window, window.output_file)
    else:
        # 创建临时HTML文件进行预览
        create_temp_preview(window)


def update_svg_preview(window, svg_file_path):
    """更新SVG预览"""
    if not svg_file_path or not os.path.isfile(svg_file_path):
        return
    
    # 加载SVG文件到预览窗口
    url = QUrl.fromLocalFile(svg_file_path)
    window.svg_preview.load(url)
    
    # 更新代码预览
    try:
        with open(svg_file_path, 'r', encoding='utf-8') as f:
            svg_content = f.read()
            window.code_preview.setPlainText(svg_content)
    except Exception as e:
        window.code_preview.setPlainText(f"无法读取SVG文件: {str(e)}")


def update_html_preview(window, html_file_path):
    """更新HTML预览"""
    if not html_file_path or not os.path.isfile(html_file_path):
        return
    
    # 加载HTML文件到预览窗口
    url = QUrl.fromLocalFile(html_file_path)
    window.html_preview.load(url)
    
    # 更新代码预览
    try:
        with open(html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
            window.code_preview.setPlainText(html_content)
    except Exception as e:
        window.code_preview.setPlainText(f"无法读取HTML文件: {str(e)}")


def create_temp_preview(window):
    """创建临时HTML文件进行预览"""
    # 检查输入文件
    if not window.input_file or not os.path.isfile(window.input_file):
        return
    
    try:
        # 获取转换选项
        mode = window.mode_combo.currentText()
        precision = window.precision_spin.value()
        preserve_text = window.preserve_text_check.isChecked()
        add_wrapper = window.add_wrapper_check.isChecked()
        
        # 创建临时文件
        fd, temp_file = tempfile.mkstemp(suffix='.html')
        os.close(fd)
        
        # 保存临时文件路径
        if window.temp_preview_file and os.path.exists(window.temp_preview_file):
            try:
                os.remove(window.temp_preview_file)
            except:
                pass
        window.temp_preview_file = temp_file
        
        # 创建转换器
        from svg2html import SVG2HTML
        converter = SVG2HTML(
            preserve_text=preserve_text,
            add_wrapper=add_wrapper,
            conversion_mode=mode,
            precision=precision
        )
        
        # 转换文件
        converter.convert_file(window.input_file, temp_file)
        
        # 更新HTML预览
        update_html_preview(window, temp_file)
        
    except Exception as e:
        window.status_bar.showMessage(f"预览生成失败: {str(e)}")
        window.code_preview.setPlainText(f"预览生成失败: {str(e)}") 