import sys
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QGridLayout,
    QVBoxLayout,
    QGroupBox,
    QHBoxLayout,
    QPushButton,
    QTextEdit,
    QDialog,
    QDialogButtonBox,
)
from my_report.template_model import report_model


class MDReportMakerApp(QMainWindow):
    """
    マークダウン記法でレポートを作成するアプリ（主に表示機能）
    - 利用前にstatus_orig.jsonを参考にstatus.jsonファイルを作成してください
    - 左側のボタンを押して編集画面を表示
    - 右側の表示で内容を確認
    - saveボタンで内容をレポートをファイルに保存（履歴も保存）
    - save without historyボタンでレポートをファイルに保存（履歴は更新しない）
    """

    def __init__(self, my_model: report_model):
        super().__init__()
        self.report_model = my_model
        self.setWindowTitle("Markdown Report Maker")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # 左パネル
        left_panel_layout = QVBoxLayout()
        v_layout = QVBoxLayout()
        self.input_buttons = [
            InputButton(key, self) for key in report_model.KEY_LIST
        ]
        for btn in self.input_buttons:
            v_layout.addWidget(btn)
        q_group = QGroupBox()
        q_group.setLayout(v_layout)
        left_panel_layout.addWidget(q_group)

        h_layout = QHBoxLayout()
        self.save_buttons = [
            SaveButton(label, self)
            for label in ["Save", "Save without history"]
        ]
        for btn in self.save_buttons:
            h_layout.addWidget(btn)
        left_panel_layout.addLayout(h_layout)

        # 右パネル（プレビュー）
        self.report_window = MDTextEdit(self)
        self.report_window.setReadOnly(True)

        # グリッドレイアウト
        layout = QGridLayout()
        layout.addLayout(left_panel_layout, 0, 0)
        layout.addWidget(self.report_window, 0, 1)
        self.central_widget.setLayout(layout)

        self.report_window.update_text_edit()
        print(self.report_window.toMarkdown())


class MDTextEdit(QTextEdit):
    """レポートプレビュー表示ウィジェット"""

    def __init__(self, main_window: MDReportMakerApp):
        super().__init__()
        self.main_window = main_window

    def update_text_edit(self) -> None:
        self.main_window.report_window.setMarkdown(
            self.main_window.report_model.get_body()
        )
        self.resize_text_edit()

    def resize_text_edit(self):
        num_lines = self.document().lineCount()
        max_line_length = max(
            len(line) for line in self.toPlainText().splitlines()
        )
        width = (
            self.fontMetrics().horizontalAdvance("あ") + 2
        ) * max_line_length + 10

        self.setMinimumWidth(width)
        self.setMinimumHeight(self.fontMetrics().height() * num_lines)


class InputButton(QPushButton):
    """各セクションの編集ボタン"""

    def __init__(self, init_text: str, main_window: MDReportMakerApp):
        super().__init__(init_text)
        self.main_window = main_window
        self.clicked.connect(self.__button_dialog)

    def __button_dialog(self):
        b_index = report_model.KEY_LIST.index(self.text())
        print(b_index)

        dialog = QDialog(self)
        dialog.setWindowTitle(f"This is a QDialog for {self.text()}")
        layout = QVBoxLayout()

        self.text_edit = QTextEdit()
        self.text_edit.setPlainText(
            self.main_window.report_model.get_text_by_key(self.text())
        )
        num_lines = self.text_edit.document().lineCount()
        max_line_length = max(
            len(line) for line in self.text_edit.toPlainText().splitlines()
        )
        width = (
            self.text_edit.fontMetrics().horizontalAdvance("あ")
            * max_line_length
            + 10
        )
        self.text_edit.setMinimumWidth(width)
        self.text_edit.setMinimumHeight(
            self.fontMetrics().height() * num_lines
        )
        self.text_edit.textChanged.connect(self.__update_dialog_text)
        layout.addWidget(self.text_edit)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        button_box.accepted.connect(dialog.accept)
        layout.addWidget(button_box)

        dialog.setLayout(layout)
        dialog.exec()

    def __update_dialog_text(self):
        self.main_window.report_model.set_text_by_key(
            self.text(), self.text_edit.toPlainText()
        )
        self.main_window.report_window.update_text_edit()
        if report_model.KEY_LIST.index(self.text()) > 2:
            self.main_window.report_window.verticalScrollBar().setValue(
                self.main_window.report_window.verticalScrollBar().maximum()
            )


class SaveButton(QPushButton):
    """
    編集後のマークダウンファイルを保存するボタン
    """

    def __init__(self, initial_text: str, main_window: MDReportMakerApp):
        super().__init__(initial_text)
        self.main_window = main_window
        self.setStyleSheet(
            "SaveButton {background-color: #4169e1; "
            "color: yellow; "
            "border-radius: 3px;} "
            "SaveButton:pressed {background: #000080}"
        )
        self.clicked.connect(self.__click)

    def __click(self):
        rm = self.main_window.report_model
        if self.text() == self.main_window.save_buttons[0].text():
            print(f"{self.text()} button is pushed")
            rm.save_file(self.main_window.report_window.toMarkdown())
        else:
            print(f"{self.text()} button is pushed")
            rm.save_file_without_history(
                self.main_window.report_window.toMarkdown()
            )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mw = MDReportMakerApp(report_model())
    mw.show()
    app.exec()
