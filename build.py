"""PyInstaller 打包脚本 — 生成单个 .exe 文件"""
import PyInstaller.__main__
import os
import sys


def build():
    """构建可执行文件"""
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # 收集 Tesseract 数据文件
    tesseract_dir = os.path.join(base_dir, "assets", "tesseract")
    tesseract_data = []
    if os.path.exists(tesseract_dir):
        tesseract_data.append(f"--add-data={tesseract_dir};tesseract")

    args = [
        os.path.join(base_dir, "main.py"),
        "--name=文件全能转化助手",
        "--onefile",
        "--windowed",
        f"--icon={os.path.join(base_dir, 'assets', 'icon.ico')}" if os.path.exists(os.path.join(base_dir, "assets", "icon.ico")) else "",
        f"--add-data={os.path.join(base_dir, 'assets', 'styles')};assets/styles",
        f"--add-data={os.path.join(base_dir, 'assets', 'icon.ico')};assets",
        f"--add-data={os.path.join(base_dir, 'assets', 'icon.png')};assets",
        "--hidden-import=pymupdf",
        "--hidden-import=pytesseract",
        "--hidden-import=python-docx",
        "--hidden-import=python-pptx",
        "--hidden-import=openpyxl",
        "--hidden-import=win32com",
        "--hidden-import=win32com.client",
        "--hidden-import=pythoncom",
        "--hidden-import=reportlab",
        "--hidden-import=PIL",
        "--hidden-import=PIL.Image",
        "--hidden-import=numpy",
        "--hidden-import=PySide6",
        "--collect-all=pymupdf",
        "--collect-all=PySide6",
        "--clean",
        "--noconfirm",
    ]

    # 去掉空字符串参数
    args = [a for a in args if a]
    args.extend(tesseract_data)

    PyInstaller.__main__.run(args)


if __name__ == "__main__":
    build()
