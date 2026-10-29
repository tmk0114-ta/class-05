"""メインウィンドウ。

レポート編集アプリのメインウィンドウ。
左パネルに編集ボタン、右パネルにプレビューを表示する。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QGridLayout,
    QVBoxLayout,
    QGroupBox,
    QHBoxLayout,
    QPushButton,
)

from .report_preview import ReportPreview

if TYPE_CHECKING:
    from ..controller.app_controller import AppController


class MainWindow(QMainWindow):
    """メインウィンドウクラス。

    左パネルにセクション編集ボタンと保存ボタン、
    右パネルにレポートプレビューを表示する。
    """

    def __init__(self, controller: AppController) -> None:
        """メインウィンドウを初期化する。

        Args:
            controller: アプリケーションコントローラー
        """
        super().__init__()
        self._controller: AppController = controller
        self._setup_ui()

    def _setup_ui(self) -> None:
        """UIコンポーネントを配置する。"""
        self.setWindowTitle("Markdown Report Maker")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 左パネル
        left_panel = self._create_left_panel()

        # 右パネル（プレビュー）
        self._preview = ReportPreview()

        # グリッドレイアウト
        layout = QGridLayout()
        layout.addWidget(left_panel, 0, 0)
        layout.addWidget(self._preview, 0, 1)
        central_widget.setLayout(layout)

        # 初期表示
        self.update_preview()

    def _create_left_panel(self) -> QWidget:
        """左パネルを作成する。

        Returns:
            左パネルウィジェット
        """
        container = QWidget()
        layout = QVBoxLayout()

        # セクション編集ボタン
        section_layout = QVBoxLayout()
        section_keys = self._controller.get_section_keys()
        self._section_buttons: dict[str, QPushButton] = {}

        for key in section_keys:
            btn = QPushButton(key)
            btn.clicked.connect(lambda checked, k=key: self._on_edit_section(k))
            self._section_buttons[key] = btn
            section_layout.addWidget(btn)

        section_group = QGroupBox()
        section_group.setLayout(section_layout)
        layout.addWidget(section_group)

        # 保存ボタン
        save_layout = QHBoxLayout()

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(lambda: self._on_save(True))
        self._style_save_button(save_btn)
        save_layout.addWidget(save_btn)

        save_no_hist_btn = QPushButton("Save without history")
        save_no_hist_btn.clicked.connect(lambda: self._on_save(False))
        self._style_save_button(save_no_hist_btn)
        save_layout.addWidget(save_no_hist_btn)

        layout.addLayout(save_layout)

        # PDFエクスポートボタン（改修2）
        pdf_layout = QHBoxLayout()
        self._pdf_btn = QPushButton("Save as PDF")
        self._pdf_btn.clicked.connect(self._on_export_pdf)
        self._style_save_button(self._pdf_btn)
        pdf_layout.addWidget(self._pdf_btn)
        layout.addLayout(pdf_layout)
        container.setLayout(layout)
        return container

    def _style_save_button(self, button: QPushButton) -> None:
        """保存ボタンのスタイルを設定する。

        Args:
            button: スタイルを設定するボタン
        """
        button.setStyleSheet(
            "QPushButton {background-color: #4169e1; "
            "color: yellow; "
            "border-radius: 3px;} "
            "QPushButton:pressed {background: #000080}"
        )

    def _on_edit_section(self, section_key: str) -> None:
        """セクション編集ボタンがクリックされたときの処理。

        Args:
            section_key: 編集するセクションのキー
        """
        self._controller.handle_edit_section(section_key, self._preview)

    def _on_save(self, with_history: bool) -> None:
        """保存ボタンがクリックされたときの処理。

        Args:
            with_history: 履歴を保存するかどうか
        """
        self._controller.handle_save(with_history, self._preview)

    def _on_export_pdf(self) -> None:
        """PDFエクスポートボタンがクリックされたときの処理。"""
        self._controller.export_pdf()

    def update_preview(self) -> None:
        """プレビューを表示を更新する。"""
        body = self._controller.get_model().get_body()
        self._preview.set_report(body)
        # コンソールにも出力
        print(self._preview.toMarkdown())
