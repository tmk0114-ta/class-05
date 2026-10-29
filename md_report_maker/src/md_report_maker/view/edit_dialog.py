"""セクション編集ダイアログ。

各レポートセクションのテキストを編集するためのモーダルダイアログ。
"""

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QTextEdit,
    QDialogButtonBox,
)


class EditDialog(QDialog):
    """セクション編集用のモーダルダイアログ。

    セクション名と初期テキストを受け取り、
    編集後のテキストを返す。
    """

    def __init__(self, section_name: str, initial_text: str, parent=None) -> None:
        """編集ダイアログを初期化する。

        Args:
            section_name: 編集するセクションの名前
            initial_text: 初期テキスト
            parent: 親ウィジェット
        """
        super().__init__(parent)
        self._section_name: str = section_name
        self._setup_ui(initial_text)

    def _setup_ui(self, initial_text: str) -> None:
        """UIコンポーネントを配置する。

        Args:
            initial_text: 初期テキスト
        """
        self.setWindowTitle(f"Edit: {self._section_name}")
        layout = QVBoxLayout()

        self._text_edit = QTextEdit()
        self._text_edit.setPlainText(initial_text)
        self._resize_text_edit()
        layout.addWidget(self._text_edit)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def _resize_text_edit(self) -> None:
        """テキストエディットのサイズを調整する。"""
        num_lines = self._text_edit.document().lineCount()
        text_lines = self._text_edit.toPlainText().splitlines()
        if text_lines:
            max_line_length = max(len(line) for line in text_lines)
            width = (
                self._text_edit.fontMetrics().horizontalAdvance("あ")
                * max_line_length
                + 10
            )
            self._text_edit.setMinimumWidth(width)
        self._text_edit.setMinimumHeight(
            self.fontMetrics().height() * max(num_lines, 1)
        )

    def get_text(self) -> str:
        """編集後のテキストを取得する。

        Returns:
            編集後のplain text
        """
        return self._text_edit.toPlainText()

    @property
    def section_name(self) -> str:
        """セクション名を取得する。

        Returns:
            セクション名
        """
        return self._section_name
