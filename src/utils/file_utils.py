"""文件处理工具函数"""
import os


def validate_file(file_path: str, allowed_extensions: list[str] = None) -> bool:
    """验证文件是否存在且格式正确"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在：{file_path}")
    if not os.path.isfile(file_path):
        raise ValueError(f"路径不是文件：{file_path}")
    if os.path.getsize(file_path) == 0:
        raise ValueError(f"文件为空：{file_path}")
    if allowed_extensions:
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in allowed_extensions:
            raise ValueError(
                f"不支持的文件格式：{ext}，支持的格式：{', '.join(allowed_extensions)}"
            )
    return True


def safe_filename(filename: str) -> str:
    """清理文件名，移除不安全字符"""
    unsafe_chars = '<>:"/\\|?*'
    for char in unsafe_chars:
        filename = filename.replace(char, "_")
    # 限制长度
    if len(filename) > 200:
        name, ext = os.path.splitext(filename)
        filename = name[:200 - len(ext)] + ext
    return filename


def get_unique_path(file_path: str) -> str:
    """如果文件已存在，生成带数字后缀的唯一路径"""
    if not os.path.exists(file_path):
        return file_path

    directory = os.path.dirname(file_path)
    name, ext = os.path.splitext(os.path.basename(file_path))
    counter = 1
    while True:
        new_path = os.path.join(directory, f"{name}_{counter}{ext}")
        if not os.path.exists(new_path):
            return new_path
        counter += 1
