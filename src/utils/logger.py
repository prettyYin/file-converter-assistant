"""日志模块 — 支持中文日志和文件轮转"""
import logging
import os
import sys
from logging.handlers import RotatingFileHandler

_logger: logging.Logger | None = None


def setup_logger() -> logging.Logger:
    """初始化日志系统"""
    global _logger
    if _logger is not None:
        return _logger

    _logger = logging.getLogger("FileConverter")
    _logger.setLevel(logging.DEBUG)

    # 日志文件路径：打包后写到 exe 同目录，开发时写到项目根目录
    if getattr(sys, "frozen", False):
        log_dir = os.path.dirname(sys.executable)
    else:
        log_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    log_path = os.path.join(log_dir, "converter.log")

    # 文件处理器（轮转，最大 5MB，保留 3 个备份）
    try:
        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=5 * 1024 * 1024,
            backupCount=3,
            encoding="utf-8",
        )
    except (OSError, PermissionError):
        # 目录不可写时退回到临时目录
        import tempfile
        log_path = os.path.join(tempfile.gettempdir(), "converter.log")
        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=5 * 1024 * 1024,
            backupCount=3,
            encoding="utf-8",
        )
    file_handler.setLevel(logging.DEBUG)

    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # 格式
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    _logger.addHandler(file_handler)
    _logger.addHandler(console_handler)

    return _logger


def get_logger() -> logging.Logger:
    """获取日志器实例"""
    global _logger
    if _logger is None:
        return setup_logger()
    return _logger
