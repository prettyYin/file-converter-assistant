# 文件全能转化助手

一款全能的文件格式转换桌面工具，支持 PDF、Word、PPT、Excel、图片等格式之间的互相转换。

## 支持的转换类型（共 13 种）

### PDF 转 Office
- **PDF → Word** — 将 PDF 转换为可编辑的 Word 文档
- **PDF → PPT** — 将 PDF 转换为演示文稿
- **PDF → Excel** — 提取 PDF 中的表格到 Excel

### PDF 处理
- **PDF → 长图** — 将所有页面垂直拼接为一张长图
- **PDF → 逐页图片** — 每页导出为单独的图片文件
- **PDF 拆分** — 按页码范围拆分为多个文件
- **PDF 合并** — 将多个 PDF 合并为一个文件

### Office 转 PDF
- **Word → PDF** — 将 Word 文档转换为 PDF（需安装 Office）
- **PPT → PDF** — 将演示文稿转换为 PDF（需安装 Office）
- **Excel → PDF** — 将表格转换为 PDF（需安装 Office）

### 图片处理
- **图片 → Word** — OCR 识别图片中的文字导出为 Word
- **图片 → Excel** — OCR 识别图片中的表格导出为 Excel
- **图片 → PDF** — 将多张图片合并为 PDF

## 系统要求

- Windows 10 或更高版本
- Python 3.10+（源码运行）
- Microsoft Office（Office 转 PDF 功能需要，可选）

## 快速开始

### 方式一：源码运行

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 安装 Tesseract OCR（图片转 Word/Excel 需要）
# 下载地址：https://github.com/UB-Mannheim/tesseract/wiki
# 安装时勾选中文语言包

# 3. 运行
python main.py
```

### 方式二：打包为 EXE

```bash
python build.py
# 生成的 .exe 文件位于 dist/ 目录
```

## 项目结构

```
converter tool/
├── main.py              # 入口
├── requirements.txt     # Python 依赖
├── build.py             # PyInstaller 打包脚本
├── assets/
│   ├── styles/theme.qss # UI 主题样式
│   └── tesseract/       # Tesseract OCR（可选捆绑）
├── src/
│   ├── app.py           # QApplication 初始化
│   ├── main_window.py   # 主窗口
│   ├── ui/              # UI 组件
│   ├── core/            # 核心模块（转换器基类、工作线程等）
│   ├── engines/         # 13 个转换引擎
│   └── utils/           # 工具函数
└── tests/               # 测试
```

## 技术栈

- **UI 框架**：PySide6（Qt for Python）
- **PDF 引擎**：PyMuPDF
- **Office 文档**：python-docx、python-pptx、openpyxl
- **OCR**：Tesseract + pytesseract
- **Office 自动化**：pywin32 (COM)
- **打包**：PyInstaller

## 许可证

MIT License
