"""AppControllerの単体テスト。

コントローラーの処理に関するテスト。
"""

import os
import pytest

from md_report_maker.model.report_model import ReportModel
from md_report_maker.controller.app_controller import AppController


class TestAppController:
    """AppControllerクラスに関するテスト。"""

    @pytest.fixture
    def model(self, temp_status_file: str):
        """ReportModelのフィクスチャ。"""
        return ReportModel(temp_status_file)

    @pytest.fixture
    def controller(self, model: ReportModel):
        """AppControllerのフィクスチャ。"""
        return AppController(model)

    def test_get_model_returns_model(self, controller: AppController) -> None:
        """get_modelがModelを返すこと。"""
        assert controller.get_model() is not None
        assert isinstance(controller.get_model(), ReportModel)

    def test_get_section_keys(self, controller: AppController) -> None:
        """get_section_keysがキー一覧を返すこと。"""
        keys = controller.get_section_keys()
        assert len(keys) > 0
        assert "CLASS_NO" in keys

    def test_export_pdf_creates_file(
        self, controller: AppController, temp_output_dir: str
    ) -> None:
        """export_pdfがファイルを作成すること。"""
        os.chdir(temp_output_dir)
        output_path = controller.export_pdf()
        assert os.path.isfile(output_path)
        assert output_path.endswith(".pdf")
        os.unlink(output_path)

    def test_export_pdf_custom_path(
        self, controller: AppController, temp_output_dir: str
    ) -> None:
        """export_pdfでカスタムパスを指定できること。"""
        custom_path = os.path.join(temp_output_dir, "custom.pdf")
        result = controller.export_pdf(custom_path)
        assert result == custom_path
        assert os.path.isfile(custom_path)
        os.unlink(custom_path)
