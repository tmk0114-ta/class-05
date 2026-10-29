"""Markdown Report Maker - エントリポイント。

アプリの起動処理を行う。
"""

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from .model.report_model import ReportModel
from .controller.app_controller import AppController


def main() -> None:
    """アプリケーションのメインエントリーポイント。"""
    app = QApplication(sys.argv)

    # 設定ファイルのパス
    config_path = "status.json"

    try:
        model = ReportModel(config_path)
    except FileNotFoundError as e:
        print(e)
        sys.exit(1)
    except ValueError as e:
        print(e)
        sys.exit(1)

    controller = AppController(model)
    window = controller.create_window()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
