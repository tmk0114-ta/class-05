"""Viewパッケージ。

UIコンポーネントを管理する。
循環インポートを避けるため、lazy importを採用。
"""

from .report_preview import ReportPreview
from .edit_dialog import EditDialog

__all__ = ["ReportPreview", "EditDialog", "MainWindow"]


def __getattr__(name: str):
    if name == "MainWindow":
        from .main_window import MainWindow

        return MainWindow
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
