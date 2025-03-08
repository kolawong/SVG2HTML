#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SVG2HTML GUI应用程序

图形界面版本的SVG到HTML转换工具，提供高质量的用户界面和实时预览功能。
"""

import os
import sys
import tempfile
from pathlib import Path
from typing import Optional, List, Tuple, Dict, Any
import webbrowser

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QFileDialog, QComboBox, QSpinBox, 
    QCheckBox, QGroupBox, QFormLayout, QStatusBar, QSplitter, 
    QFrame, QSizePolicy, QMessageBox, QTabWidget, QTextEdit,
    QProgressBar, QAction, QMenu, QToolBar, QLineEdit, QStyle,
    QRadioButton, QButtonGroup
)
from PyQt5.QtCore import Qt, QUrl, QSize, QThread, pyqtSignal, QSettings, QTimer
from PyQt5.QtGui import QIcon, QFont, QPixmap, QColor, QPalette, QDesktopServices
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage

# 导入我们的SVG转换模块
from svg2html import SVG2HTML

# 导入GUI组件和动作
from gui_components import create_left_panel, create_right_panel, create_toolbar, apply_global_styles, is_dark_mode
from gui_actions import (
    open_input_file_dialog, open_input_dir_dialog, start_conversion, 
    start_batch_conversion, open_output_file, show_help, show_about,
    svg_file_input_changed, html_file_input_changed,
    batch_mode_changed
)
from gui_preview import update_preview

# 设置应用程序信息
APP_NAME = "SVG2HTML 转换工具"
APP_VERSION = "1.0.0"
APP_ORG = "SVG2HTML"
APP_DOMAIN = "svg2html.app"

# 设置高DPI支持
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

# 样式常量
DARK_PRIMARY = "#1976D2"  # 主色调（深蓝）
LIGHT_PRIMARY = "#BBDEFB"  # 浅色调
ACCENT_COLOR = "#FF5722"  # 强调色（橙色）
PRIMARY_TEXT = "#212121"  # 主文本色
SECONDARY_TEXT = "#757575"  # 次文本色
DIVIDER_COLOR = "#BDBDBD"  # 分隔线颜色
BACKGROUND_COLOR = "#F5F5F5"  # 背景色
CARD_COLOR = "#FFFFFF"  # 卡片色


# 转换工作线程
class ConversionWorker(QThread):
    """转换工作线程，避免GUI卡顿"""
    
    # 信号定义
    progress_updated = pyqtSignal(int)
    conversion_complete = pyqtSignal(bool, str)
    
    def __init__(self, 
                 input_path: str, 
                 output_path: str, 
                 mode: str = "embed", 
                 preserve_text: bool = True,
                 add_wrapper: bool = True,
                 precision: int = 2,
                 is_batch: bool = False):
        """初始化转换工作线程"""
        super().__init__()
        self.input_path = input_path
        self.output_path = output_path
        self.mode = mode
        self.preserve_text = preserve_text
        self.add_wrapper = add_wrapper
        self.precision = precision
        self.is_batch = is_batch
        
    def run(self):
        """执行转换任务"""
        try:
            # 创建转换器
            converter = SVG2HTML(
                preserve_text=self.preserve_text,
                add_wrapper=self.add_wrapper,
                conversion_mode=self.mode,
                precision=self.precision
            )
            
            if self.is_batch:
                # 批量转换目录
                success, fail = converter.convert_directory(self.input_path, self.output_path)
                self.conversion_complete.emit(True, f"批量转换完成: {success}个成功, {fail}个失败")
            else:
                # 转换单个文件
                result = converter.convert_file(self.input_path, self.output_path)
                self.conversion_complete.emit(result, "转换成功" if result else "转换失败")
                
        except Exception as e:
            self.conversion_complete.emit(False, f"转换错误: {str(e)}")


class SVG2HTMLGUI(QMainWindow):
    """SVG2HTML图形界面类"""
    
    def __init__(self):
        super().__init__()
        
        # 初始化窗口属性
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setMinimumSize(1200, 800)
        self.setWindowIcon(QApplication.style().standardIcon(QStyle.SP_DesktopIcon))
        
        # 初始化变量
        self.input_file = ""
        self.output_file = ""
        self.input_dir = ""
        self.output_dir = ""
        self.temp_preview_file = None
        self.is_batch_mode = False
        self.preview_timer = QTimer()
        self.preview_timer.setSingleShot(True)
        self.preview_timer.timeout.connect(self.update_preview)
        
        # 创建设置对象
        self.settings = QSettings(APP_ORG, APP_NAME)
        
        # 绑定动作方法
        self.bind_actions()
        
        # 应用全局样式
        apply_global_styles(self)
        
        # 初始化UI
        self.init_ui()
        
        # 加载设置
        self.load_settings()
    
    def init_ui(self):
        """初始化用户界面"""
        # 创建中心控件
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        # 创建工具栏
        self.toolbar = create_toolbar(self)
        
        # 创建主分割器
        main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(main_splitter)
        
        # 左侧面板
        left_panel = QWidget()
        left_panel.setMaximumWidth(400)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 10, 0)
        
        # 右侧面板
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 0, 0, 0)
        
        # 添加面板到分割器
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(right_panel)
        
        # 设置分割器初始比例
        main_splitter.setSizes([400, 800])
        
        # 创建左侧面板内容
        create_left_panel(self, left_layout)
        
        # 创建右侧面板内容
        create_right_panel(self, right_layout)
        
        # 创建状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # 创建进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        # 设置状态提示
        self.status_bar.showMessage("准备就绪")
    
    def update_preview(self):
        """更新预览"""
        update_preview(self)
    
    def load_settings(self):
        """加载设置"""
        # 加载上次使用的目录
        self.input_file = self.settings.value("last_input_file", "")
        self.output_file = self.settings.value("last_output_file", "")
        self.input_dir = self.settings.value("last_input_dir", "")
        self.output_dir = self.settings.value("last_output_dir", "")
        
        # 加载转换设置
        mode = self.settings.value("conversion_mode", "embed")
        if hasattr(self, 'mode_combo') and self.mode_combo:
            index = self.mode_combo.findText(mode)
            if index >= 0:
                self.mode_combo.setCurrentIndex(index)
        
        precision = self.settings.value("precision", 2, type=int)
        if hasattr(self, 'precision_spin') and self.precision_spin:
            self.precision_spin.setValue(precision)
        
        preserve_text = self.settings.value("preserve_text", True, type=bool)
        if hasattr(self, 'preserve_text_check') and self.preserve_text_check:
            self.preserve_text_check.setChecked(preserve_text)
        
        add_wrapper = self.settings.value("add_wrapper", True, type=bool)
        if hasattr(self, 'add_wrapper_check') and self.add_wrapper_check:
            self.add_wrapper_check.setChecked(add_wrapper)
    
    def save_settings(self):
        """保存设置"""
        # 保存上次使用的目录
        self.settings.setValue("last_input_file", self.input_file)
        self.settings.setValue("last_output_file", self.output_file)
        self.settings.setValue("last_input_dir", self.input_dir)
        self.settings.setValue("last_output_dir", self.output_dir)
        
        # 保存转换设置
        if hasattr(self, 'mode_combo') and self.mode_combo:
            self.settings.setValue("conversion_mode", self.mode_combo.currentText())
        
        if hasattr(self, 'precision_spin') and self.precision_spin:
            self.settings.setValue("precision", self.precision_spin.value())
        
        if hasattr(self, 'preserve_text_check') and self.preserve_text_check:
            self.settings.setValue("preserve_text", self.preserve_text_check.isChecked())
        
        if hasattr(self, 'add_wrapper_check') and self.add_wrapper_check:
            self.settings.setValue("add_wrapper", self.add_wrapper_check.isChecked())
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        # 保存设置
        self.save_settings()
        
        # 清理临时文件
        if self.temp_preview_file and os.path.exists(self.temp_preview_file):
            try:
                os.remove(self.temp_preview_file)
            except:
                pass
        
        # 接受关闭事件
        event.accept()

    def bind_actions(self):
        """绑定动作方法"""
        # 导入动作函数
        from gui_actions import (
            open_input_file_dialog, open_output_file_dialog, 
            open_input_dir_dialog, open_output_dir_dialog,
            start_conversion, start_batch_conversion, 
            open_output_file, show_help, show_about,
            svg_file_input_changed, html_file_input_changed,
            batch_mode_changed
        )
        
        # 绑定文件对话框动作
        self.open_input_file_dialog = lambda: open_input_file_dialog(self)
        self.open_output_file_dialog = lambda: open_output_file_dialog(self)
        self.open_input_dir_dialog = lambda: open_input_dir_dialog(self)
        self.open_output_dir_dialog = lambda: open_output_dir_dialog(self)
        
        # 绑定转换动作
        self.start_conversion = lambda: start_conversion(self)
        self.start_batch_conversion = lambda: start_batch_conversion(self)
        
        # 绑定其他动作
        self.open_output_file = lambda: open_output_file(self)
        self.show_help = lambda: show_help(self)
        self.show_about = lambda: show_about(self)
        
        # 绑定输入变化事件
        self.svg_file_input_changed = lambda: svg_file_input_changed(self)
        self.html_file_input_changed = lambda: html_file_input_changed(self)
        self.batch_mode_changed = lambda state: batch_mode_changed(self, state)
        
        # 绑定主题切换
        self.toggle_theme = self._toggle_theme
    
    def _toggle_theme(self):
        """切换深色/浅色主题"""
        # 导入主题相关函数
        from gui_components import apply_global_styles
        
        # 保存当前主题设置
        settings = QSettings(APP_ORG, APP_NAME)
        current_is_dark = is_dark_mode()
        settings.setValue("use_dark_theme", not current_is_dark)
        
        # 重新应用样式
        apply_global_styles(self)
        
        # 更新状态栏消息
        theme_name = "深色" if not current_is_dark else "浅色"
        self.status_bar.showMessage(f"已切换到{theme_name}主题")


def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName(APP_ORG)
    app.setOrganizationDomain(APP_DOMAIN)
    
    window = SVG2HTMLGUI()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main() 