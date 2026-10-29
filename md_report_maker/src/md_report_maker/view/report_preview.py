"""レポートプレビューウィジェット。

マークダウン形式のレポートテキストを読み取り専用で表示する。
"""

from PySide6.QtWidgets import QTextEdit


class ReportPreview(QTextEdit):
    """レポートプレビュー表示ウィジェット。

    読み取り専用でマークダウンテキストを表示し、
    内容に基づいて自動でサイズを調整する。
    """

    def __init__(self) -> None:
        """プレビューウィジェットを初期化する。"""
        super().__init__()
        self.setReadOnly(True)

    def set_report(self, markdown_text: str) -> None:
        """レポートテキストを設定して表示する。

        Args:
            markdown_text: マークダウン形式のテキスト
        """
        self.setMarkdown(markdown_text)
        self.auto_resize()

    def auto_resize(self) -> None:
        """表示内容に基づいてウィジェットサイズを調整する。"""
        num_lines = self.document().lineCount()
        if num_lines == 0:
            return

        text_lines = self.toPlainText().splitlines()
        if not text_lines:
            return

        max_line_length = max(len(line) for line in text_lines)
        width = (
            self.fontMetrics().horizontalAdvance("あ") + 2
        ) * max_line_length + 10

        self.setMinimumWidth(width)
        self.setMinimumHeight(self.fontMetrics().height() * num_lines)
