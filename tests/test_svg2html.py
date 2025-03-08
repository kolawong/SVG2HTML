#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SVG2HTML 工具测试模块

用于测试SVG到HTML转换工具的功能和正确性。
"""

import os
import sys
import unittest
from pathlib import Path
import tempfile
import shutil
import re

# 添加项目根目录到系统路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from svg2html import SVG2HTML


class TestSVG2HTML(unittest.TestCase):
    """测试SVG2HTML转换功能"""

    def setUp(self):
        """测试前准备工作"""
        self.converter_embed = SVG2HTML(conversion_mode="embed")
        self.converter_convert = SVG2HTML(conversion_mode="convert")
        self.examples_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'examples'))
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """测试后清理工作"""
        shutil.rmtree(self.temp_dir)
        
    def test_convert_file_embed_mode(self):
        """测试嵌入模式下的单个文件转换"""
        input_file = os.path.join(self.examples_dir, 'sample.svg')
        output_file = os.path.join(self.temp_dir, 'sample_embed.html')
        
        # 确保示例文件存在
        self.assertTrue(os.path.exists(input_file), f"示例文件不存在: {input_file}")
        
        # 执行转换
        result = self.converter_embed.convert_file(input_file, output_file)
        
        # 验证转换成功
        self.assertTrue(result, "文件转换失败")
        self.assertTrue(os.path.exists(output_file), "输出文件不存在")
        
        # 检查输出文件内容
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 验证HTML基本结构
        self.assertIn('<!DOCTYPE html>', content, "输出文件缺少DOCTYPE声明")
        self.assertIn('<html', content, "输出文件缺少HTML标签")
        self.assertIn('<head>', content, "输出文件缺少HEAD标签")
        self.assertIn('<body>', content, "输出文件缺少BODY标签")
        
        # 验证SVG内容被保留
        self.assertIn('<svg', content, "输出文件缺少SVG标签")
        self.assertIn('viewBox="0 0 400 300"', content, "SVG视图框属性丢失")
        
        # 验证文本内容被保留
        self.assertIn('这是一个矩形', content, "文本内容丢失")
        self.assertIn('圆形', content, "文本内容丢失")
        self.assertIn('三角形', content, "文本内容丢失")
        
        # 验证字体属性被保留
        self.assertIn('font-family="Arial"', content, "字体属性丢失")
        self.assertIn('font-family="SimSun"', content, "字体属性丢失")
        self.assertIn('font-family="KaiTi"', content, "字体属性丢失")
    
    def test_convert_file_convert_mode(self):
        """测试转换模式下的单个文件转换"""
        input_file = os.path.join(self.examples_dir, 'sample.svg')
        output_file = os.path.join(self.temp_dir, 'sample_convert.html')
        
        # 确保示例文件存在
        self.assertTrue(os.path.exists(input_file), f"示例文件不存在: {input_file}")
        
        # 执行转换
        result = self.converter_convert.convert_file(input_file, output_file)
        
        # 验证转换成功
        self.assertTrue(result, "文件转换失败")
        self.assertTrue(os.path.exists(output_file), "输出文件不存在")
        
        # 检查输出文件内容
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 验证HTML基本结构
        self.assertIn('<!DOCTYPE html>', content, "输出文件缺少DOCTYPE声明")
        self.assertIn('<html', content, "输出文件缺少HTML标签")
        self.assertIn('<head>', content, "输出文件缺少HEAD标签")
        self.assertIn('<body>', content, "输出文件缺少BODY标签")
        
        # 验证转换后的HTML元素
        self.assertIn('class="svg-container"', content, "缺少SVG容器元素")
        self.assertIn('class="svg-element-', content, "缺少转换后的元素")
        
        # 验证CSS样式属性
        self.assertIn('position: absolute', content, "缺少定位样式")
        self.assertIn('border-radius: 50%', content, "缺少圆形样式")
        self.assertIn('background-color', content, "缺少背景色样式")
        
        # 验证文本内容被保留
        self.assertIn('这是一个矩形', content, "文本内容丢失")
        self.assertIn('圆形', content, "文本内容丢失")
        self.assertIn('直线示例', content, "文本内容丢失")
        
        # 验证字体属性被转换
        self.assertIn('font-family', content, "字体属性丢失")
        
    def test_constructor_options(self):
        """测试构造函数选项"""
        # 测试不添加包装元素
        converter_no_wrapper = SVG2HTML(add_wrapper=False)
        
        input_file = os.path.join(self.examples_dir, 'sample.svg')
        output_file = os.path.join(self.temp_dir, 'no_wrapper.html')
        
        # 执行转换
        converter_no_wrapper.convert_file(input_file, output_file)
        
        # 检查输出文件内容
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 验证没有包装元素
        self.assertNotIn('<div class="svg-container">', content, "不应该有包装元素")
        
        # 确保SVG内容依然存在
        self.assertIn('<svg', content, "输出文件缺少SVG标签")
        
    def test_precision_option(self):
        """测试精度选项"""
        # 使用3位小数精度的转换器
        converter_high_precision = SVG2HTML(conversion_mode="convert", precision=3)
        
        input_file = os.path.join(self.examples_dir, 'sample.svg')
        output_file = os.path.join(self.temp_dir, 'high_precision.html')
        
        # 执行转换
        converter_high_precision.convert_file(input_file, output_file)
        
        # 检查输出文件内容
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 验证数值精度（检查是否使用了指定的精度格式化数值）
        css_values = re.findall(r'(?:width|height|left|top):\s*(\d+(?:\.\d+)?)px', content)
        # 只需验证文件中有数值，不需要验证精度位数，因为实际值可能不含小数点
        self.assertTrue(len(css_values) > 0, "没有找到CSS位置和尺寸值")
        
        # 验证精度处理逻辑
        sample_num = 123.4567
        formatted = converter_high_precision._fmt(sample_num)
        self.assertEqual(formatted, "123.457", "精度格式化函数未按预期工作")


if __name__ == '__main__':
    unittest.main() 