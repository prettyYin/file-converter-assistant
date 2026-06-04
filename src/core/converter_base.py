"""转换器抽象基类"""
from abc import ABC, abstractmethod
from typing import Optional
import threading
import os


class BaseConverter(ABC):
    """所有转换引擎的基类"""

    @abstractmethod
    def convert(
        self,
        input_path: str,
        output_dir: str,
        options: Optional[dict] = None,
        cancel_event: Optional[threading.Event] = None,
    ) -> str:
        """
        执行文件转换。

        Args:
            input_path: 输入文件路径
            output_dir: 输出目录
            options: 转换选项字典
            cancel_event: 取消事件，用于中断长时间操作

        Returns:
            输出文件的完整路径

        Raises:
            FileNotFoundError: 输入文件不存在
            ValueError: 输入文件格式不正确
            Exception: 转换过程中的其他错误
        """
        pass

    def _check_cancelled(self, cancel_event: Optional[threading.Event]) -> None:
        """检查是否已取消，若取消则抛出异常"""
        if cancel_event and cancel_event.is_set():
            raise InterruptedError("用户取消了转换操作")

    def _make_output_path(
        self,
        input_path: str,
        output_dir: str,
        new_extension: str,
        suffix: str = "",
    ) -> str:
        """生成输出文件路径，自动处理重名"""
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        if suffix:
            base_name = f"{base_name}_{suffix}"
        output_name = f"{base_name}{new_extension}"
        output_path = os.path.join(output_dir, output_name)

        # 如果文件已存在，添加数字后缀
        counter = 1
        while os.path.exists(output_path):
            output_name = f"{base_name}_{counter}{new_extension}"
            output_path = os.path.join(output_dir, output_name)
            counter += 1

        return output_path
