"""アプリケーションコントローラー。

ModelとViewの統合、イベントハンドリングを担当する。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtWidgets import QTextEdit

from ..model.report_model import ReportModel
from ..view.edit_dialog import EditDialog

if TYPE_CHECKING:
    from ..view.main_window import MainWindow


class AppController:
    """アプリケーションコントローラー。

    ModelとViewの間の仲介役として、
    ユーザー操作を受け付けてModelの更新やViewの再描画を行う。
    """

    def __init__(self, model: ReportModel) -> None:
        """コントローラーを初期化する。

        Args:
            model: レポートデータモデル
        """
        self._model: ReportModel = model

    def get_model(self) -> ReportModel:
        """保持しているModelを取得する。

        Returns:
            ReportModelのインスタンス
        """
        return self._model

    def get_section_keys(self) -> list[str]:
        """利用可能なセクションキーの一覧を取得する。

        Returns:
            セクションキーのリスト
        """
        return self._model.get_section_keys()

    def create_window(self) -> MainWindow:
        """メインウィンドウを作成する。

        Returns:
            MainWindowのインスタンス
        """
        from ..view.main_window import MainWindow

        return MainWindow(self)

    def handle_edit_section(
        self, section_key: str, preview: QTextEdit | None = None
    ) -> None:
        """セクション編集の処理を行う。

        編集ダイアログを表示し、ユーザーの入力をModelに反映する。

        Args:
            section_key: 編集するセクションのキー
            preview: プレビューウィジェット（Noneの場合更新しない）
        """
        initial_text = self._model.get_section(section_key)
        dialog = EditDialog(section_key, initial_text)
        result = dialog.exec()

        if result == dialog.DialogCode.Accepted:
            new_text = dialog.get_text()
            self._model.set_section(section_key, new_text)
            if preview is not None:
                preview.set_report(self._model.get_body())

    def handle_save(
        self,
        with_history: bool,
        preview: QTextEdit | None = None,
    ) -> None:
        """保存処理を行う。

        Args:
            with_history: 履歴（status.json）も保存するかどうか
            preview: プレビューウィジェット（マークダウンテキスト取得用）
        """
        markdown_text = ""
        if preview is not None:
            markdown_text = preview.toMarkdown()
        else:
            markdown_text = self._model.get_body()

        # レポートの保存
        self._model.save_report(markdown_text)
        print(f"Report saved: {self._model._default_report_filename()}")

        # 履歴の保存（オプション）
        if with_history:
            self._model.save_status()
            print("Status saved: status.json")

    def export_pdf(self, output_path: str | None = None) -> str:
        """レポートをPDF形式でエクスポートする。

        現在の実装ではマークダウンテキストをPDFとして保存する（簡易実装）。
        本格的なPDF変換には追加のライブラリ（weasyprint等）が必要。

        Args:
            output_path: 出力パス（Noneの場合、デフォルト名に.pdfを付与）

        Returns:
            保存したファイルのパス
        """
        if output_path is None:
            default_name = self._model._default_report_filename()
            output_path = default_name.rsplit(".", 1)[0] + ".pdf"

        # 簡易実装: マークダウンテキストをUTF-8で保存（拡張子を.pdfに）
        # 本格的なPDF変換には weasyprint 等のライブラリが必要
        markdown_text = self._model.get_body()
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"% PDF Export (Markdown Source)\n\n{markdown_text}")

        print(f"PDF exported: {output_path}")
        return output_path
