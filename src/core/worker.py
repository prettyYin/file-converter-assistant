"""转换工作线程 — 在后台执行转换，不阻塞 UI"""
import threading
import traceback

from PySide6.QtCore import QThread, Signal

from src.core.models import ConversionResult
from src.core.converter_base import BaseConverter


class ConversionWorker(QThread):
    """后台转换工作线程"""

    # 信号
    progress = Signal(int, int)          # (current, total)
    file_completed = Signal(ConversionResult)
    error_occurred = Signal(str)
    finished = Signal(list)              # list[ConversionResult]

    def __init__(
        self,
        engine_class: type[BaseConverter],
        files: list[str],
        output_dir: str,
        options: dict = None,
    ):
        super().__init__()
        self.engine_class = engine_class
        self.files = files
        self.output_dir = output_dir
        self.options = options or {}
        self._cancel_event = threading.Event()

    def cancel(self):
        """取消转换"""
        self._cancel_event.set()

    def run(self):
        """在工作线程中执行转换"""
        results: list[ConversionResult] = []
        total = len(self.files)

        for i, file_path in enumerate(self.files):
            if self._cancel_event.is_set():
                break

            try:
                engine = self.engine_class()
                output_path = engine.convert(
                    input_path=file_path,
                    output_dir=self.output_dir,
                    options=self.options,
                    cancel_event=self._cancel_event,
                )
                result = ConversionResult(
                    success=True,
                    input_path=file_path,
                    output_path=output_path,
                )
            except InterruptedError:
                # 用户取消
                break
            except Exception as e:
                traceback.print_exc()
                result = ConversionResult(
                    success=False,
                    input_path=file_path,
                    error_message=str(e),
                )

            results.append(result)
            self.file_completed.emit(result)
            self.progress.emit(i + 1, total)

        self.finished.emit(results)
