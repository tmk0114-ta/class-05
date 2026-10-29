"""MainWindowの単体テスト。

メインウィンドウのUI生成に関するテスト。
"""

import pytest

from md_report_maker.model.report_model import ReportModel
from md_report_maker.controller.app_controller import AppController
from md_report_maker.view.main_window import MainWindow


class TestMainWindow:
    """MainWindowクラスに関するテスト。"""

    @pytest.fixture
    def model(self, temp_status_file: str):
        """ReportModelのフィクスチャ。"""
        return ReportModel(temp_status_file)

    @pytest.fixture
    def controller(self, model: ReportModel):
        """AppControllerのフィクスチャ。"""
        return AppController(model)

    @pytest.fixture
    def window(self, qt_app, controller: AppController):
        """MainWindowのフィクスチャ。"""
        return MainWindow(controller)

    def test_window_title(self, window: MainWindow) -> None:
        """ウィンドウタイトルが設定されていること。"""
        assert window.windowTitle() == "Markdown Report Maker"

    def test_has_central_widget(self, window: MainWindow) -> None:
        """セントラルウィジェットが設定されていること。"""
        assert window.centralWidget() is not None

    def test_section_buttons_created(self, window: MainWindow) -> None:
        """セクション編集ボタンが作成されていること。"""
        assert hasattr(window, "_section_buttons")

    def test_pdf_button_exists(self, window: MainWindow) -> None:
        """PDFエクスポートボタンが存在すること（改修2）。"""
        assert hasattr(window, "_pdf_btn")
        assert window._pdf_btn.text() == "Save as PDF"
