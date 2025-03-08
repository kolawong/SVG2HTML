# SVG转HTML工具

这个工具用于将SVG文件转换为HTML格式，保持原始SVG的所有视觉特性，便于AI进行理解和处理以开发前端应用。

## 功能特点

- 两种转换模式：
  - **嵌入模式(embed)**：将SVG直接嵌入到HTML中，100%保留原始外观
  - **转换模式(convert)**：将SVG元素转换为等效的HTML+CSS元素，便于AI理解和操作
- 完整保留SVG元素的位置和布局
- 保持文本为文本（不转为路径）
- 保持原始字体类型和大小
- 支持批量转换多个SVG文件
- 简单易用的命令行界面

## 安装

```bash
# 安装依赖
pip install -r requirements.txt
```

## 使用方法

### 基本用法

```bash
# 使用默认嵌入模式
python svg2html.py input.svg output.html

# 使用转换模式（SVG元素转为HTML+CSS）
python svg2html.py input.svg output.html --mode convert
```

### 批量转换

```bash
# 批量转换目录下的所有SVG文件（使用嵌入模式）
python svg2html.py --dir input_directory output_directory

# 批量转换目录下的所有SVG文件（使用转换模式）
python svg2html.py --dir input_directory output_directory --mode convert
```

## 参数说明

- `input.svg`: 输入的SVG文件路径
- `output.html`: 输出的HTML文件路径
- `--dir`: 批量转换目录下的所有SVG文件
- `--mode`: 转换模式，可选值：
  - `embed`：嵌入模式，将SVG直接嵌入HTML（默认）
  - `convert`：转换模式，将SVG元素转换为HTML+CSS元素
- `--precision`: 数值精度（小数点后位数，默认：2）
- `--no-text-preserve`: 不保留文本特性（默认保留）
- `--no-wrapper`: 不添加HTML包装元素（默认添加）

## 转换模式对比

### 嵌入模式 (--mode embed)

- 直接将SVG嵌入HTML中
- 100%保持原始SVG的外观和行为
- 简单快速，不会丢失任何SVG特性
- 适合需要精确保留SVG效果的场景

### 转换模式 (--mode convert)

- 将SVG元素转换为等效的HTML+CSS元素
- 矩形、圆形、线条等形状转换为div元素
- 文本元素转换为HTML文本元素
- 使用CSS定位保持元素位置与原SVG一致
- 便于AI理解和操作HTML结构
- 适合需要修改和交互的场景

## 工作原理

本工具通过以下步骤将SVG转换为HTML：

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

- 使用Python的xml库和BeautifulSoup解析SVG文件
- 通过DOM操作生成HTML
- 运用CSS确保元素定位与原SVG一致
- 使用cssutils库处理样式转换

## 项目结构

```
svg2html/
├── svg2html.py       # 主程序
├── requirements.txt  # 项目依赖
├── examples/         # 示例文件
└── tests/            # 测试用例
``` 