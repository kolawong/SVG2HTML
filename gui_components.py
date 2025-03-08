#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GUI组件模块

包含SVG2HTML GUI应用程序的界面组件创建和布局。
"""

import os
import platform
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QComboBox, QSpinBox, QCheckBox, QGroupBox, QFormLayout, 
    QSplitter, QFrame, QSizePolicy, QTabWidget, QTextEdit,
    QProgressBar, QAction, QToolBar, QLineEdit, QStyle,
    QRadioButton, QButtonGroup, QFileDialog, QApplication
)
from PyQt5.QtCore import Qt, QSize, QSettings
from PyQt5.QtGui import QColor, QPalette, QFont
from PyQt5.QtWebEngineWidgets import QWebEngineView

# 样式常量 - 浅色模式
LIGHT_THEME = {
    "DARK_PRIMARY": "#1976D2",  # 主色调（深蓝）
    "LIGHT_PRIMARY": "#BBDEFB",  # 浅色调
    "ACCENT_COLOR": "#FF5722",  # 强调色（橙色）
    "PRIMARY_TEXT": "#212121",  # 主文本色
    "SECONDARY_TEXT": "#757575",  # 次文本色
    "DIVIDER_COLOR": "#BDBDBD",  # 分隔线颜色
    "BACKGROUND_COLOR": "#F5F5F5",  # 背景色
    "CARD_COLOR": "#FFFFFF",  # 卡片色
    "HOVER_COLOR": "#E3F2FD",  # 悬停色
    "PRESSED_COLOR": "#BBDEFB",  # 按下色
    "BUTTON_TEXT": "#212121",  # 按钮文本色
    "BUTTON_BORDER": "#BDBDBD",  # 按钮边框色
}

# 样式常量 - 深色模式
DARK_THEME = {
    "DARK_PRIMARY": "#2196F3",  # 主色调（蓝色）
    "LIGHT_PRIMARY": "#1E3A5F",  # 浅色调
    "ACCENT_COLOR": "#FF9800",  # 强调色（橙色）
    "PRIMARY_TEXT": "#FFFFFF",  # 主文本色
    "SECONDARY_TEXT": "#B0BEC5",  # 次文本色
    "DIVIDER_COLOR": "#546E7A",  # 分隔线颜色
    "BACKGROUND_COLOR": "#121212",  # 背景色
    "CARD_COLOR": "#1E1E1E",  # 卡片色
    "HOVER_COLOR": "#2C2C2C",  # 悬停色
    "PRESSED_COLOR": "#383838",  # 按下色
    "BUTTON_TEXT": "#FFFFFF",  # 按钮文本色
    "BUTTON_BORDER": "#546E7A",  # 按钮边框色
}

def is_dark_mode():
    """检测系统是否处于深色模式"""
    # 首先检查用户设置
    app_settings = QSettings("SVG2HTML", "SVG2HTML 转换工具")
    user_setting = app_settings.value("use_dark_theme", None)
    
    # 如果用户已设置主题，则使用用户设置
    if user_setting is not None:
        return bool(user_setting)
    
    # 否则检测系统主题
    if platform.system() == "Darwin":  # macOS
        try:
            # 尝试读取macOS的深色模式设置
            settings = QSettings("Apple", "")
            style = settings.value("AppleInterfaceStyle", "")
            return style == "Dark"
        except:
            pass
    
    # 如果无法检测或不是macOS，则使用应用程序调色板判断
    app = QApplication.instance()
    if app:
        palette = app.palette()
        bg_color = palette.color(QPalette.Window)
        # 如果背景色较暗，则认为是深色模式
        return bg_color.lightness() < 128
    
    return False

def get_theme():
    """获取当前主题"""
    return DARK_THEME if is_dark_mode() else LIGHT_THEME

def apply_global_styles(window):
    """应用全局样式"""
    # 获取当前主题
    theme = get_theme()
    
    # 创建应用程序调色板
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(theme["BACKGROUND_COLOR"]))
    palette.setColor(QPalette.WindowText, QColor(theme["PRIMARY_TEXT"]))
    palette.setColor(QPalette.Base, QColor(theme["CARD_COLOR"]))
    palette.setColor(QPalette.AlternateBase, QColor(theme["LIGHT_PRIMARY"]))
    palette.setColor(QPalette.ToolTipBase, QColor(theme["DARK_PRIMARY"]))
    palette.setColor(QPalette.ToolTipText, QColor(theme["PRIMARY_TEXT"]))
    palette.setColor(QPalette.Text, QColor(theme["PRIMARY_TEXT"]))
    palette.setColor(QPalette.Button, QColor(theme["CARD_COLOR"]))
    palette.setColor(QPalette.ButtonText, QColor(theme["PRIMARY_TEXT"]))
    palette.setColor(QPalette.Link, QColor(theme["DARK_PRIMARY"]))
    palette.setColor(QPalette.Highlight, QColor(theme["DARK_PRIMARY"]))
    palette.setColor(QPalette.HighlightedText, QColor(theme["PRIMARY_TEXT"]))
    
    # 应用调色板
    window.setPalette(palette)
    
    # 设置全局样式表
    window.setStyleSheet(f"""
        QMainWindow, QDialog, QWidget {{
            background-color: {theme["BACKGROUND_COLOR"]};
            color: {theme["PRIMARY_TEXT"]};
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }}
        
        QTabWidget::pane {{
            border: 1px solid {theme["DIVIDER_COLOR"]};
            border-radius: 8px;
            background-color: {theme["CARD_COLOR"]};
            top: -1px;
        }}
        
        QTabBar::tab {{
            background-color: {theme["LIGHT_PRIMARY"]};
            color: {theme["PRIMARY_TEXT"]};
            border: 1px solid {theme["DIVIDER_COLOR"]};
            border-bottom: none;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            padding: 10px 16px;
            margin-right: 4px;
            font-weight: 500;
        }}
        
        QTabBar::tab:selected {{
            background-color: {theme["CARD_COLOR"]};
            border-bottom: 2px solid {theme["DARK_PRIMARY"]};
        }}
        
        QTabBar::tab:hover {{
            background-color: {theme["HOVER_COLOR"]};
        }}
        
        QGroupBox {{
            background-color: {theme["CARD_COLOR"]};
            border: 1px solid {theme["DIVIDER_COLOR"]};
            border-radius: 8px;
            margin-top: 24px;
            padding-top: 28px;
            font-weight: 500;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 12px;
            top: 8px;
            color: {theme["DARK_PRIMARY"]};
            font-weight: bold;
            font-size: 14px;
        }}
        
        QComboBox, QSpinBox, QLineEdit {{
            border: 1px solid {theme["DIVIDER_COLOR"]};
            border-radius: 6px;
            padding: 8px;
            background-color: {theme["CARD_COLOR"]};
            selection-background-color: {theme["DARK_PRIMARY"]};
            color: {theme["PRIMARY_TEXT"]};
            min-height: 24px;
        }}
        
        QComboBox:hover, QSpinBox:hover, QLineEdit:hover {{
            border: 1px solid {theme["SECONDARY_TEXT"]};
            background-color: {theme["HOVER_COLOR"]};
        }}
        
        QComboBox:focus, QSpinBox:focus, QLineEdit:focus {{
            border: 2px solid {theme["DARK_PRIMARY"]};
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 24px;
        }}
        
        QComboBox::down-arrow {{
            image: url(down-arrow.png);
            width: 12px;
            height: 12px;
        }}
        
        QCheckBox {{
            spacing: 10px;
            color: {theme["PRIMARY_TEXT"]};
        }}
        
        QCheckBox::indicator {{
            width: 20px;
            height: 20px;
            border: 1px solid {theme["DIVIDER_COLOR"]};
            border-radius: 4px;
            background-color: {theme["CARD_COLOR"]};
        }}
        
        QCheckBox::indicator:checked {{
            background-color: {theme["DARK_PRIMARY"]};
            border: 1px solid {theme["DARK_PRIMARY"]};
            image: url(check.png);
        }}
        
        QCheckBox::indicator:hover {{
            border: 1px solid {theme["DARK_PRIMARY"]};
        }}
        
        QRadioButton {{
            spacing: 10px;
            color: {theme["PRIMARY_TEXT"]};
        }}
        
        QRadioButton::indicator {{
            width: 20px;
            height: 20px;
            border: 1px solid {theme["DIVIDER_COLOR"]};
            border-radius: 10px;
            background-color: {theme["CARD_COLOR"]};
        }}
        
        QRadioButton::indicator:checked {{
            background-color: {theme["CARD_COLOR"]};
            border: 2px solid {theme["DARK_PRIMARY"]};
        }}
        
        QRadioButton::indicator:checked::before {{
            content: "";
            display: block;
            width: 10px;
            height: 10px;
            border-radius: 5px;
            background-color: {theme["DARK_PRIMARY"]};
            margin: 4px;
        }}
        
        QRadioButton::indicator:hover {{
            border: 1px solid {theme["DARK_PRIMARY"]};
        }}
        
        QProgressBar {{
            border: none;
            border-radius: 4px;
            text-align: center;
            background-color: {theme["BACKGROUND_COLOR"]};
            color: {theme["PRIMARY_TEXT"]};
            height: 8px;
        }}
        
        QProgressBar::chunk {{
            background-color: {theme["DARK_PRIMARY"]};
            border-radius: 4px;
        }}
        
        QStatusBar {{
            background-color: {theme["CARD_COLOR"]};
            color: {theme["PRIMARY_TEXT"]};
            border-top: 1px solid {theme["DIVIDER_COLOR"]};
            padding: 4px;
            min-height: 24px;
        }}
        
        QSplitter::handle {{
            background-color: {theme["DIVIDER_COLOR"]};
            width: 1px;
            height: 1px;
        }}
        
        QScrollBar:vertical {{
            border: none;
            background-color: {theme["BACKGROUND_COLOR"]};
            width: 12px;
            margin: 0px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {theme["DIVIDER_COLOR"]};
            border-radius: 6px;
            min-height: 30px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {theme["SECONDARY_TEXT"]};
        }}
        
        QScrollBar:horizontal {{
            border: none;
            background-color: {theme["BACKGROUND_COLOR"]};
            height: 12px;
            margin: 0px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:horizontal {{
            background-color: {theme["DIVIDER_COLOR"]};
            border-radius: 6px;
            min-width: 30px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background-color: {theme["SECONDARY_TEXT"]};
        }}
        
        QPushButton {{
            background-color: {theme["CARD_COLOR"]};
            color: {theme["BUTTON_TEXT"]};
            border: 1px solid {theme["BUTTON_BORDER"]};
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: 500;
            min-height: 20px;
        }}
        
        QPushButton:hover {{
            background-color: {theme["HOVER_COLOR"]};
            border: 1px solid {theme["DARK_PRIMARY"]};
        }}
        
        QPushButton:pressed {{
            background-color: {theme["PRESSED_COLOR"]};
        }}
        
        QPushButton[class="primary"] {{
            background-color: {theme["DARK_PRIMARY"]};
            color: white;
            border: none;
            font-weight: bold;
        }}
        
        QPushButton[class="primary"]:hover {{
            background-color: #1565C0;
        }}
        
        QPushButton[class="primary"]:pressed {{
            background-color: #0D47A1;
        }}
        
        QLabel {{
            color: {theme["PRIMARY_TEXT"]};
        }}
        
        QLabel[class="title"] {{
            font-size: 18px;
            font-weight: bold;
            color: {theme["DARK_PRIMARY"]};
            margin-bottom: 8px;
        }}
        
        QLabel[class="subtitle"] {{
            font-size: 14px;
            color: {theme["SECONDARY_TEXT"]};
        }}
        
        QToolBar {{
            background-color: {theme["CARD_COLOR"]};
            border-bottom: 1px solid {theme["DIVIDER_COLOR"]};
            spacing: 6px;
            padding: 4px;
        }}
        
        QToolButton {{
            background-color: transparent;
            border: none;
            border-radius: 4px;
            padding: 4px;
        }}
        
        QToolButton:hover {{
            background-color: {theme["HOVER_COLOR"]};
        }}
        
        QToolButton:pressed {{
            background-color: {theme["PRESSED_COLOR"]};
        }}
        
        QTextEdit {{
            background-color: {theme["CARD_COLOR"]};
            color: {theme["PRIMARY_TEXT"]};
            border: 1px solid {theme["DIVIDER_COLOR"]};
            border-radius: 6px;
            selection-background-color: {theme["DARK_PRIMARY"]};
            selection-color: white;
            padding: 8px;
        }}
    """)


def create_toolbar(window):
    """创建工具栏"""
    toolbar = QToolBar()
    toolbar.setMovable(False)
    toolbar.setIconSize(QSize(24, 24))
    toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
    window.addToolBar(toolbar)
    
    # 打开文件按钮
    open_file_action = QAction(window.style().standardIcon(QStyle.SP_FileIcon), "打开SVG文件", window)
    open_file_action.triggered.connect(window.open_input_file_dialog)
    toolbar.addAction(open_file_action)
    
    # 打开目录按钮
    open_dir_action = QAction(window.style().standardIcon(QStyle.SP_DirIcon), "打开目录", window)
    open_dir_action.triggered.connect(window.open_input_dir_dialog)
    toolbar.addAction(open_dir_action)
    
    toolbar.addSeparator()
    
    # 转换按钮
    convert_action = QAction(window.style().standardIcon(QStyle.SP_ArrowRight), "转换", window)
    convert_action.triggered.connect(window.start_conversion)
    toolbar.addAction(convert_action)
    
    # 批量转换按钮
    batch_convert_action = QAction(window.style().standardIcon(QStyle.SP_DirLinkIcon), "批量转换", window)
    batch_convert_action.triggered.connect(window.start_batch_conversion)
    toolbar.addAction(batch_convert_action)
    
    toolbar.addSeparator()
    
    # 查看输出按钮
    view_output_action = QAction(window.style().standardIcon(QStyle.SP_FileDialogContentsView), "查看输出", window)
    view_output_action.triggered.connect(window.open_output_file)
    toolbar.addAction(view_output_action)
    
    # 帮助按钮
    help_action = QAction(window.style().standardIcon(QStyle.SP_DialogHelpButton), "帮助", window)
    help_action.triggered.connect(window.show_help)
    toolbar.addAction(help_action)
    
    # 将空白区域填充到工具栏右侧
    spacer = QWidget()
    spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
    toolbar.addWidget(spacer)
    
    # 主题切换按钮
    theme_action = QAction("切换主题", window)
    theme_action.triggered.connect(window.toggle_theme)
    toolbar.addAction(theme_action)
    
    # 关于按钮
    about_action = QAction(window.style().standardIcon(QStyle.SP_MessageBoxInformation), "关于", window)
    about_action.triggered.connect(window.show_about)
    toolbar.addAction(about_action)
    
    return toolbar


def create_left_panel(window, layout):
    """创建左侧面板"""
    # 文件选择组
    file_group = QGroupBox("文件选择")
    file_layout = QFormLayout()
    file_group.setLayout(file_layout)
    
    # SVG文件输入
    svg_file_layout = QHBoxLayout()
    window.svg_file_input = QLineEdit()
    window.svg_file_input.setPlaceholderText("选择SVG文件...")
    window.svg_file_input.textChanged.connect(window.svg_file_input_changed)
    svg_file_browse = QPushButton("浏览...")
    svg_file_browse.clicked.connect(window.open_input_file_dialog)
    svg_file_layout.addWidget(window.svg_file_input)
    svg_file_layout.addWidget(svg_file_browse)
    file_layout.addRow("SVG文件:", svg_file_layout)
    
    # HTML文件输出
    html_file_layout = QHBoxLayout()
    window.html_file_input = QLineEdit()
    window.html_file_input.setPlaceholderText("选择HTML输出文件...")
    window.html_file_input.textChanged.connect(window.html_file_input_changed)
    html_file_browse = QPushButton("浏览...")
    html_file_browse.clicked.connect(lambda: window.open_output_file_dialog())
    html_file_layout.addWidget(window.html_file_input)
    html_file_layout.addWidget(html_file_browse)
    file_layout.addRow("HTML文件:", html_file_layout)
    
    # 批量转换选项
    batch_layout = QHBoxLayout()
    window.batch_mode_check = QCheckBox("批量转换")
    window.batch_mode_check.stateChanged.connect(window.batch_mode_changed)
    batch_layout.addWidget(window.batch_mode_check)
    file_layout.addRow("", batch_layout)
    
    # 目录选择（批量模式）
    window.dir_widget = QWidget()
    dir_layout = QVBoxLayout(window.dir_widget)
    dir_layout.setContentsMargins(0, 0, 0, 0)
    
    # 输入目录
    input_dir_layout = QHBoxLayout()
    window.input_dir_input = QLineEdit()
    window.input_dir_input.setPlaceholderText("选择SVG输入目录...")
    input_dir_browse = QPushButton("浏览...")
    input_dir_browse.clicked.connect(window.open_input_dir_dialog)
    input_dir_layout.addWidget(window.input_dir_input)
    input_dir_layout.addWidget(input_dir_browse)
    dir_layout.addLayout(input_dir_layout)
    
    # 输出目录
    output_dir_layout = QHBoxLayout()
    window.output_dir_input = QLineEdit()
    window.output_dir_input.setPlaceholderText("选择HTML输出目录...")
    output_dir_browse = QPushButton("浏览...")
    output_dir_browse.clicked.connect(lambda: window.open_output_dir_dialog())
    output_dir_layout.addWidget(window.output_dir_input)
    output_dir_layout.addWidget(output_dir_browse)
    dir_layout.addLayout(output_dir_layout)
    
    file_layout.addRow("", window.dir_widget)
    window.dir_widget.setVisible(False)
    
    # 转换选项组
    options_group = QGroupBox("转换选项")
    options_layout = QFormLayout()
    options_group.setLayout(options_layout)
    
    # 转换模式
    window.mode_combo = QComboBox()
    window.mode_combo.addItems(["embed", "convert"])
    window.mode_combo.setToolTip("embed: 将SVG嵌入HTML\nconvert: 将SVG转换为HTML+CSS")
    options_layout.addRow("转换模式:", window.mode_combo)
    
    # 精度设置
    window.precision_spin = QSpinBox()
    window.precision_spin.setRange(0, 6)
    window.precision_spin.setValue(2)
    window.precision_spin.setToolTip("数值精度（小数点后位数）")
    options_layout.addRow("精度:", window.precision_spin)
    
    # 保留文本选项
    window.preserve_text_check = QCheckBox("保留文本特性")
    window.preserve_text_check.setChecked(True)
    window.preserve_text_check.setToolTip("保持文本为文本，不转为路径")
    options_layout.addRow("", window.preserve_text_check)
    
    # 添加包装元素选项
    window.add_wrapper_check = QCheckBox("添加HTML包装元素")
    window.add_wrapper_check.setChecked(True)
    window.add_wrapper_check.setToolTip("在SVG外添加HTML包装元素")
    options_layout.addRow("", window.add_wrapper_check)
    
    # 转换按钮
    convert_button = QPushButton("开始转换")
    convert_button.setProperty("class", "primary")
    convert_button.clicked.connect(window.start_conversion)
    
    # 批量转换按钮
    batch_convert_button = QPushButton("开始批量转换")
    batch_convert_button.setProperty("class", "primary")
    batch_convert_button.clicked.connect(window.start_batch_conversion)
    window.batch_convert_button = batch_convert_button
    window.batch_convert_button.setVisible(False)
    
    # 添加组件到布局
    layout.addWidget(file_group)
    layout.addWidget(options_group)
    layout.addWidget(convert_button)
    layout.addWidget(batch_convert_button)
    layout.addStretch()


def create_right_panel(window, layout):
    """创建右侧面板"""
    # 创建预览标签
    preview_label = QLabel("预览")
    preview_label.setProperty("class", "title")
    layout.addWidget(preview_label)
    
    # 创建预览标签页
    preview_tabs = QTabWidget()
    layout.addWidget(preview_tabs)
    
    # SVG预览
    window.svg_preview = QWebEngineView()
    preview_tabs.addTab(window.svg_preview, "SVG")
    
    # HTML预览
    window.html_preview = QWebEngineView()
    preview_tabs.addTab(window.html_preview, "HTML")
    
    # 代码预览
    window.code_preview = QTextEdit()
    window.code_preview.setReadOnly(True)
    window.code_preview.setFont(QFont("Menlo", 12))  # 使用更现代的等宽字体
    preview_tabs.addTab(window.code_preview, "代码")
    
    # 更新预览按钮
    update_preview_button = QPushButton("更新预览")
    update_preview_button.clicked.connect(window.update_preview)
    layout.addWidget(update_preview_button) 