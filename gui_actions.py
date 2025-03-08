#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GUI动作模块

包含SVG2HTML GUI应用程序的事件处理和动作。
"""

import os
import sys
import webbrowser
from pathlib import Path
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QApplication
from PyQt5.QtCore import QUrl, Qt


def open_input_file_dialog(window):
    """打开输入文件对话框"""
    file_path, _ = QFileDialog.getOpenFileName(
        window,
        "选择SVG文件",
        window.input_file or os.path.expanduser("~"),
        "SVG文件 (*.svg);;所有文件 (*.*)"
    )
    
    if file_path:
        window.input_file = file_path
        window.svg_file_input.setText(file_path)
        
        # 自动生成输出文件路径
        if not window.output_file:
            output_path = os.path.splitext(file_path)[0] + ".html"
            window.output_file = output_path
            window.html_file_input.setText(output_path)
        
        # 更新预览
        window.preview_timer.start(500)


def open_output_file_dialog(window):
    """打开输出文件对话框"""
    file_path, _ = QFileDialog.getSaveFileName(
        window,
        "选择HTML输出文件",
        window.output_file or os.path.expanduser("~"),
        "HTML文件 (*.html);;所有文件 (*.*)"
    )
    
    if file_path:
        window.output_file = file_path
        window.html_file_input.setText(file_path)


def open_input_dir_dialog(window):
    """打开输入目录对话框"""
    dir_path = QFileDialog.getExistingDirectory(
        window,
        "选择SVG输入目录",
        window.input_dir or os.path.expanduser("~"),
        QFileDialog.ShowDirsOnly
    )
    
    if dir_path:
        window.input_dir = dir_path
        window.input_dir_input.setText(dir_path)
        
        # 自动生成输出目录路径
        if not window.output_dir:
            output_dir = os.path.join(os.path.dirname(dir_path), "html_output")
            window.output_dir = output_dir
            window.output_dir_input.setText(output_dir)


def open_output_dir_dialog(window):
    """打开输出目录对话框"""
    dir_path = QFileDialog.getExistingDirectory(
        window,
        "选择HTML输出目录",
        window.output_dir or os.path.expanduser("~"),
        QFileDialog.ShowDirsOnly
    )
    
    if dir_path:
        window.output_dir = dir_path
        window.output_dir_input.setText(dir_path)


def start_conversion(window):
    """开始转换"""
    # 检查输入文件
    if not window.input_file or not os.path.isfile(window.input_file):
        QMessageBox.warning(window, "错误", "请选择有效的SVG输入文件")
        return
    
    # 检查输出文件
    if not window.output_file:
        QMessageBox.warning(window, "错误", "请指定HTML输出文件")
        return
    
    # 获取转换选项
    mode = window.mode_combo.currentText()
    precision = window.precision_spin.value()
    preserve_text = window.preserve_text_check.isChecked()
    add_wrapper = window.add_wrapper_check.isChecked()
    
    # 显示进度条
    window.progress_bar.setVisible(True)
    window.progress_bar.setValue(0)
    window.status_bar.showMessage("正在转换...")
    
    # 导入ConversionWorker类
    from svg2html_gui import ConversionWorker
    
    # 创建并启动转换线程
    window.conversion_thread = ConversionWorker(
        input_path=window.input_file,
        output_path=window.output_file,
        mode=mode,
        preserve_text=preserve_text,
        add_wrapper=add_wrapper,
        precision=precision,
        is_batch=False
    )
    
    window.conversion_thread.progress_updated.connect(window.progress_bar.setValue)
    window.conversion_thread.conversion_complete.connect(conversion_finished)
    window.conversion_thread.start()


def start_batch_conversion(window):
    """开始批量转换"""
    # 检查输入目录
    if not window.input_dir or not os.path.isdir(window.input_dir):
        QMessageBox.warning(window, "错误", "请选择有效的SVG输入目录")
        return
    
    # 检查输出目录
    if not window.output_dir:
        QMessageBox.warning(window, "错误", "请指定HTML输出目录")
        return
    
    # 获取转换选项
    mode = window.mode_combo.currentText()
    precision = window.precision_spin.value()
    preserve_text = window.preserve_text_check.isChecked()
    add_wrapper = window.add_wrapper_check.isChecked()
    
    # 显示进度条
    window.progress_bar.setVisible(True)
    window.progress_bar.setValue(0)
    window.status_bar.showMessage("正在批量转换...")
    
    # 导入ConversionWorker类
    from svg2html_gui import ConversionWorker
    
    # 创建并启动转换线程
    window.conversion_thread = ConversionWorker(
        input_path=window.input_dir,
        output_path=window.output_dir,
        mode=mode,
        preserve_text=preserve_text,
        add_wrapper=add_wrapper,
        precision=precision,
        is_batch=True
    )
    
    window.conversion_thread.progress_updated.connect(window.progress_bar.setValue)
    window.conversion_thread.conversion_complete.connect(conversion_finished)
    window.conversion_thread.start()


def conversion_finished(success, message):
    """转换完成回调"""
    # 获取窗口实例
    window = QApplication.activeWindow()
    if not window:
        return
    
    # 隐藏进度条
    window.progress_bar.setVisible(False)
    
    # 更新状态栏
    window.status_bar.showMessage(message)
    
    # 显示结果对话框
    if success:
        QMessageBox.information(window, "转换完成", message)
        
        # 更新预览
        window.preview_timer.start(500)
    else:
        QMessageBox.critical(window, "转换失败", message)


def open_output_file(window):
    """打开输出文件"""
    if window.is_batch_mode:
        # 打开输出目录
        if window.output_dir and os.path.isdir(window.output_dir):
            url = QUrl.fromLocalFile(window.output_dir)
            webbrowser.open(url.toString())
    else:
        # 打开输出文件
        if window.output_file and os.path.isfile(window.output_file):
            url = QUrl.fromLocalFile(window.output_file)
            webbrowser.open(url.toString())


def show_help(window):
    """显示帮助信息"""
    help_text = """
    <h2>SVG2HTML 转换工具使用帮助</h2>
    
    <h3>基本用法</h3>
    <ol>
        <li>点击"打开SVG文件"按钮选择要转换的SVG文件</li>
        <li>指定HTML输出文件路径</li>
        <li>选择转换选项</li>
        <li>点击"开始转换"按钮</li>
    </ol>
    
    <h3>批量转换</h3>
    <ol>
        <li>勾选"批量转换"选项</li>
        <li>选择包含SVG文件的输入目录</li>
        <li>指定HTML输出目录</li>
        <li>点击"开始批量转换"按钮</li>
    </ol>
    
    <h3>转换选项</h3>
    <ul>
        <li><b>转换模式</b>: 
            <ul>
                <li><b>embed</b>: 将SVG直接嵌入HTML中，100%保留原始外观</li>
                <li><b>convert</b>: 将SVG元素转换为HTML+CSS元素，便于AI理解和操作</li>
            </ul>
        </li>
        <li><b>精度</b>: 数值精度（小数点后位数）</li>
        <li><b>保留文本特性</b>: 保持文本为文本，不转为路径</li>
        <li><b>添加HTML包装元素</b>: 在SVG外添加HTML包装元素</li>
    </ul>
    
    <h3>预览功能</h3>
    <p>转换前后可以在右侧预览面板查看SVG和HTML的效果，以及生成的HTML代码。</p>
    """
    
    msg_box = QMessageBox(window)
    msg_box.setWindowTitle("使用帮助")
    msg_box.setTextFormat(Qt.RichText)
    msg_box.setText(help_text)
    msg_box.setIcon(QMessageBox.Information)
    msg_box.exec_()


def show_about(window):
    """显示关于信息"""
    about_text = f"""
    <h2>SVG2HTML 转换工具</h2>
    <p>版本: {window.APP_VERSION}</p>
    
    <p>这是一个将SVG文件转换为HTML格式的工具，便于AI进行理解和处理以开发前端应用。</p>
    
    <h3>功能特点</h3>
    <ul>
        <li>两种转换模式：嵌入和转换</li>
        <li>完整保留SVG元素的位置和布局</li>
        <li>保持文本为文本（不转为路径）</li>
        <li>保持原始字体类型和大小</li>
        <li>支持批量转换多个SVG文件</li>
        <li>实时预览功能</li>
    </ul>
    
    <p>© 2023 SVG2HTML. 保留所有权利。</p>
    """
    
    msg_box = QMessageBox(window)
    msg_box.setWindowTitle("关于")
    msg_box.setTextFormat(Qt.RichText)
    msg_box.setText(about_text)
    msg_box.setIcon(QMessageBox.Information)
    msg_box.exec_()


def svg_file_input_changed(window):
    """SVG文件输入变化"""
    window.input_file = window.svg_file_input.text()
    window.preview_timer.start(500)


def html_file_input_changed(window):
    """HTML文件输入变化"""
    window.output_file = window.html_file_input.text()


def batch_mode_changed(window, state):
    """批量模式变化"""
    is_batch = state == Qt.Checked
    window.is_batch_mode = is_batch
    
    # 切换UI显示
    window.svg_file_input.setEnabled(not is_batch)
    window.html_file_input.setEnabled(not is_batch)
    window.dir_widget.setVisible(is_batch)
    
    # 切换按钮显示
    window.findChild(QPushButton, "开始转换").setVisible(not is_batch)
    window.batch_convert_button.setVisible(is_batch) 