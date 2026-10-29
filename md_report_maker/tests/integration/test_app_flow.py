"""結合テスト。

Model → Controller → View のデータフローを確認する。
"""

import os
import pytest

from md_report_maker.model.report_model import ReportModel
from md_report_maker.controller.app_controller import AppController


class TestAppFlow:
    """アプリ全体のデータフローに関するテスト。"""

    @pytest.fixture
    def model(self, temp_status_file: str):
        """ReportModelのフィクスチャ。"""
        return ReportModel(temp_status_file)

    @pytest.fixture
    def controller(self, model: ReportModel):
        """AppControllerのフィクスチャ。"""
        return AppController(model)

    def test_full_edit_and_save_flow(
        self, controller: AppController, temp_output_dir: str
    ) -> None:
        """編集 → 保存 のフルフローが動作すること。"""
        os.chdir(temp_output_dir)
        model = controller.get_model()

        # セクションの編集
        model.set_section("MY_WEEKLY_REPORT", "統合テスト報告")
        assert model.get_section("MY_WEEKLY_REPORT") == "統合テスト報告"

        # レポート本文の生成
        body = model.get_body()
        assert "統合テスト報告" in body

        # 保存
        report_path = model.save_report(body)
        assert os.path.isfile(report_path)
        os.unlink(report_path)

        status_path = model.save_status()
        assert os.path.isfile(status_path)

    def test_section_keys_available_through_controller(
        self, controller: AppController
    ) -> None:
        """コントローラーからセクションキーにアクセスできること。"""
        keys = controller.get_section_keys()
        assert len(keys) == len(ReportModel.SECTION_KEYS)

    def test_model_data_persists_through_save_load(
        self, temp_output_dir: str
    ) -> None:
        """保存 → 読み込みでデータが維持されること。"""
        os.chdir(temp_output_dir)
        # status.jsonを作成
        import json
        status_data = {
            "basic_info": {
                "CLASS_NO": 5,
                "MY_ID": "T9999",
                "MY_NAME": "永続テスト",
                "GROUP_ID": 9,
                "LEADER_ID": "T9999",
                "LEADER_NAME": "永続テスト",
            },
            "history": {"MY_WEEKLY_REPORT": "永続テスト報告"},
        }
        with open("status.json", "w", encoding="utf-8") as f:
            json.dump(status_data, f, ensure_ascii=False)

        # 読み込み
        model = ReportModel("status.json")
        assert model.get_section("CLASS_NO") == "5"
        assert model.get_section("MY_WEEKLY_REPORT") == "永続テスト報告"
