"""EditDialogの単体テスト。

編集ダイアログの機能に関するテスト。
"""

import pytest

from md_report_maker.view.edit_dialog import EditDialog


class TestEditDialog:
    """EditDialogクラスに関するテスト。"""

    def test_initial_text_set(self, qt_app) -> None:
        """初期テキストが設定されていること。"""
        dialog = EditDialog("TEST_SECTION", "初期テキスト")
        assert dialog.get_text() == "初期テキスト"
        dialog.deleteLater()

    def test_text_can_be_modified(self, qt_app) -> None:
        """テキストが変更可能であること。"""
        dialog = EditDialog("TEST_SECTION", "初期")
        assert dialog.section_name == "TEST_SECTION"
        dialog.deleteLater()

    def test_section_name_property(self, qt_app) -> None:
        """セクション名が取得できること。"""
        dialog = EditDialog("MY_INFO", "テスト")
        assert dialog.section_name == "MY_INFO"
        dialog.deleteLater()

    def test_window_title(self, qt_app) -> None:
        """ダイアログタイトルが設定されていること。"""
        dialog = EditDialog("CLASS_NO", "1")
        assert dialog.windowTitle() == "Edit: CLASS_NO"
        dialog.deleteLater()
