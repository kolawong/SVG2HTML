# SVG转HTML工具

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.6%2B-blue)](https://www.python.org/)

这个工具用于将SVG文件转换为HTML格式，保持原始SVG的所有视觉特性，便于AI进行理解和处理以开发前端应用。它支持两种转换模式，可以根据需求选择最适合的转换方式。

## 目录

- [功能特点](#功能特点)
- [安装](#安装)
- [使用方法](#使用方法)
  - [命令行使用](#命令行使用)
  - [GUI界面使用](#gui界面使用)
  - [批量转换](#批量转换)
- [参数说明](#参数说明)
- [转换模式对比](#转换模式对比)
- [工作原理](#工作原理)
- [技术实现](#技术实现)
- [示例](#示例)
- [贡献指南](#贡献指南)
- [许可证](#许可证)

## 功能特点

✨ **两种转换模式**
- **嵌入模式(embed)**：将SVG直接嵌入到HTML中，100%保留原始外观
- **转换模式(convert)**：将SVG元素转换为等效的HTML+CSS元素，便于AI理解和操作

🎯 **核心优势**
- 完整保留SVG元素的位置和布局
- 保持文本为文本（不转为路径）
- 保持原始字体类型和大小
- 支持批量转换多个SVG文件
- 提供命令行和GUI两种操作方式
- 转换结果精确，支持自定义精度

## 安装

### 环境要求
- Python 3.6+
- pip包管理器

### 安装步骤

1. 克隆仓库
```bash
git clone https://github.com/yourusername/svg2html.git
cd svg2html
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

## 使用方法

### 命令行使用

基本用法：
```bash
# 使用默认嵌入模式
python svg2html.py input.svg output.html

# 使用转换模式（SVG元素转为HTML+CSS）
python svg2html.py input.svg output.html --mode convert
```

### GUI界面使用

启动GUI界面：
```bash
python svg2html_gui.py
```

### 批量转换

```bash
# 批量转换目录下的所有SVG文件（使用嵌入模式）
python svg2html.py --dir input_directory output_directory

# 批量转换目录下的所有SVG文件（使用转换模式）
python svg2html.py --dir input_directory output_directory --mode convert
```

## 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `input.svg` | 输入的SVG文件路径 | - |
| `output.html` | 输出的HTML文件路径 | - |
| `--dir` | 批量转换目录下的所有SVG文件 | - |
| `--mode` | 转换模式：`embed`或`convert` | `embed` |
| `--precision` | 数值精度（小数点后位数） | 2 |
| `--no-text-preserve` | 不保留文本特性 | `False` |
| `--no-wrapper` | 不添加HTML包装元素 | `False` |

## 转换模式对比

### 嵌入模式 (--mode embed)

✅ **优点**
- 直接将SVG嵌入HTML中
- 100%保持原始SVG的外观和行为
- 简单快速，不会丢失任何SVG特性
- 适合需要精确保留SVG效果的场景

### 转换模式 (--mode convert)

✅ **优点**
- 将SVG元素转换为等效的HTML+CSS元素
- 矩形、圆形、线条等形状转换为div元素
- 文本元素转换为HTML文本元素
- 使用CSS定位保持元素位置与原SVG一致
- 便于AI理解和操作HTML结构
- 适合需要修改和交互的场景

## 工作原理

### 嵌入模式
1. 解析原始SVG文件结构
2. 创建包含完整HTML标签的文档
3. 将原始SVG内容嵌入HTML文档中
4. 添加必要的样式以确保正确显示

### 转换模式
1. 解析原始SVG文件结构
2. 分析每个SVG元素的类型、位置和样式
3. 将SVG元素转换为对应的HTML元素（主要是div和文本元素）
4. 为每个元素生成CSS样式，确保与原SVG位置和外观一致
5. 组装最终的HTML文档

## 技术实现

🛠 **核心技术**
- 使用Python的xml库和BeautifulSoup解析SVG文件
- 通过DOM操作生成HTML
- 运用CSS确保元素定位与原SVG一致
- 使用cssutils库处理样式转换

📦 **项目结构**
```
svg2html/
├── svg2html.py       # 主程序
├── svg2html_gui.py   # GUI界面程序
├── gui_components.py # GUI组件
├── gui_preview.py    # 预览功能
├── requirements.txt  # 项目依赖
├── examples/         # 示例文件
└── tests/           # 测试用例
```

## 示例

查看 [examples](examples/) 目录获取更多示例。

## 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本仓库
2. 创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详细信息。

---

如果您觉得这个工具有帮助，欢迎给个 ⭐️ Star！