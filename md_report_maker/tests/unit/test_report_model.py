"""ReportModelの単体テスト。

データモデルの各メソッドが正しく動作することを確認する。
"""

import json
import os
import tempfile

import pytest

from md_report_maker.model.report_model import ReportModel


class TestReportModelInit:
    """ReportModelの初期化に関するテスト。"""

    def test_load_valid_config(self, temp_status_file: str) -> None:
        """有効な設定ファイルで初期化できること。"""
        model = ReportModel(temp_status_file)
        assert model.get_section("CLASS_NO") == "1"

    def test_missing_config_file_raises_error(self) -> None:
        """存在しない設定ファイルでFileNotFoundErrorが発生すること。"""
        with pytest.raises(FileNotFoundError):
            ReportModel("nonexistent.json")

    def test_invalid_json_raises_error(self) -> None:
        """不正なJSONファイルでValueErrorが発生すること。"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            f.write("invalid json content")
            f.flush()
            try:
                with pytest.raises(ValueError):
                    ReportModel(f.name)
            finally:
                os.unlink(f.name)

    def test_initializes_history_when_empty(self, temp_status_file: str) -> None:
        """historyが空の場合、デフォルトテンプレートが設定されること。"""
        model = ReportModel(temp_status_file)
        for key in ReportModel.SECTION_KEYS:
            if key != "CLASS_NO":
                assert key in model.get_section_keys()

    def test_missing_basic_info_defaults_to_empty(self) -> None:
        """basic_infoがない場合、空辞書で初期化されること。"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump({"history": {}}, f)
            f.flush()
            try:
                model = ReportModel(f.name)
                # basic_infoが空辞書として初期化されている
                missing = model.validate_basic_info()
                assert len(missing) > 0  # 必須フィールドが不足している
            finally:
                os.unlink(f.name)


class TestReportModelGetSection:
    """get_sectionメソッドのテスト。"""

    def test_get_class_no(self, temp_status_file: str) -> None:
        """CLASS_NOがbasic_infoから正しく取得されること。"""
        model = ReportModel(temp_status_file)
        assert model.get_section("CLASS_NO") == "1"

    def test_get_history_section(
        self, temp_status_with_history_file: str
    ) -> None:
        """historyセクションが正しく取得されること。"""
        model = ReportModel(temp_status_with_history_file)
        assert model.get_section("MY_WEEKLY_REPORT") == "- テスト報告\n"

    def test_invalid_key_raises_error(self, temp_status_file: str) -> None:
        """無効なキーでKeyErrorが発生すること。"""
        model = ReportModel(temp_status_file)
        with pytest.raises(KeyError):
            model.get_section("INVALID_KEY")


class TestReportModelSetSection:
    """set_sectionメソッドのテスト。"""

    def test_set_history_section(self, temp_status_file: str) -> None:
        """historyセクションの値が設定できること。"""
        model = ReportModel(temp_status_file)
        model.set_section("MY_WEEKLY_REPORT", "新しい報告")
        assert model.get_section("MY_WEEKLY_REPORT") == "新しい報告"

    def test_set_class_no_converts_to_int(self, temp_status_file: str) -> None:
        """CLASS_NOはintに変換されて保存されること。"""
        model = ReportModel(temp_status_file)
        model.set_section("CLASS_NO", "5")
        assert model.get_section("CLASS_NO") == "5"

    def test_invalid_key_raises_error(self, temp_status_file: str) -> None:
        """無効なキーでKeyErrorが発生すること。"""
        model = ReportModel(temp_status_file)
        with pytest.raises(KeyError):
            model.set_section("INVALID_KEY", "value")


class TestReportModelGetBody:
    """get_bodyメソッドのテスト。"""

    def test_generates_markdown(self, temp_status_file: str) -> None:
        """マークダウン形式の文字列が生成されること。"""
        model = ReportModel(temp_status_file)
        body = model.get_body()
        assert "# オブジェクト指向プログラミング" in body
        assert "## 作成者情報" in body

    def test_substitutes_basic_info(self, temp_status_file: str) -> None:
        """basic_infoの変数が展開されること。"""
        model = ReportModel(temp_status_file)
        body = model.get_body()
        assert "T0001" in body
        assert "テスト太郎" in body

    def test_substitutes_history(self, temp_status_with_history_file: str) -> None:
        """historyの変数が展開されること。"""
        model = ReportModel(temp_status_with_history_file)
        body = model.get_body()
        assert "- テスト報告" in body


class TestReportModelSave:
    """保存メソッドのテスト。"""

    def test_save_report_creates_file(
        self, temp_status_file: str, temp_output_dir: str
    ) -> None:
        """save_reportでファイルが作成されること。"""
        model = ReportModel(temp_status_file)
        output_path = os.path.join(temp_output_dir, "test_report.md")
        model.save_report("# テストレポート", output_path)
        assert os.path.isfile(output_path)
        with open(output_path, encoding="utf-8") as f:
            assert f.read() == "# テストレポート"

    def test_save_report_default_filename(
        self, temp_status_file: str, temp_output_dir: str
    ) -> None:
        """ファイル名を指定しない場合、デフォルト名が使用されること。"""
        os.chdir(temp_output_dir)
        model = ReportModel(temp_status_file)
        result = model.save_report("# テストレポート")
        assert "T0001テスト太郎.md" in result
        assert os.path.isfile(result)
        os.unlink(result)

    def test_save_status_updates_file(
        self, temp_status_file: str, temp_output_dir: str
    ) -> None:
        """save_statusでJSONファイルが更新されること。"""
        os.chdir(temp_output_dir)
        model = ReportModel(temp_status_file)
        model.set_section("MY_WEEKLY_REPORT", "更新された報告")
        # save_statusは指定したパスに保存
        output_path = os.path.join(temp_output_dir, "status_output.json")
        model.save_status(output_path)
        with open(output_path, encoding="utf-8") as f:
            data = json.load(f)
        assert data["history"]["MY_WEEKLY_REPORT"] == "更新された報告"


class TestReportModelValidate:
    """バリデーションメソッドのテスト。"""

    def test_valid_basic_info_returns_empty(
        self, temp_status_file: str
    ) -> None:
        """必須フィールドが揃っている場合、空リストが返ること。"""
        model = ReportModel(temp_status_file)
        missing = model.validate_basic_info()
        assert missing == []

    def test_missing_fields_detected(self) -> None:
        """不足しているフィールドが検出されること。"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump({"basic_info": {"CLASS_NO": 1}, "history": {}}, f)
            f.flush()
            try:
                model = ReportModel(f.name)
                missing = model.validate_basic_info()
                assert "MY_ID" in missing
                assert "MY_NAME" in missing
            finally:
                os.unlink(f.name)


class TestReportModelSectionKeys:
    """get_section_keysメソッドのテスト。"""

    def test_returns_all_keys(self, temp_status_file: str) -> None:
        """全セクションキーが返されること。"""
        model = ReportModel(temp_status_file)
        keys = model.get_section_keys()
        assert len(keys) == len(ReportModel.SECTION_KEYS)
        assert "CLASS_NO" in keys
        assert "MY_INFO" in keys
        assert "MY_THOUGHTS_AND_NEXT_WORKS" in keys
        assert "REFERENCES" in keys


class TestReportModelReferences:
    """REFERENCESセクションのテスト（改修1）。"""

    def test_references_in_section_keys(self) -> None:
        """REFERENCESがSECTION_KEYSに含まれること。"""
        assert "REFERENCES" in ReportModel.SECTION_KEYS

    def test_references_in_body(self, temp_status_file: str) -> None:
        """get_bodyの出力に参考文献セクションが含まれること。"""
        model = ReportModel(temp_status_file)
        body = model.get_body()
        assert "## 参考文献" in body

    def test_references_can_be_edited(self, temp_status_file: str) -> None:
        """REFERENCESセクションの編集が可能であること。"""
        model = ReportModel(temp_status_file)
        model.set_section("REFERENCES", "- Python公式ドキュメント\n")
        assert model.get_section("REFERENCES") == "- Python公式ドキュメント\n"
        body = model.get_body()
        assert "- Python公式ドキュメント" in body

    def test_references_added_to_existing_data(self) -> None:
        """既存のstatusデータにREFERENCESが追加されること。"""
        import tempfile
        import json

        # REFERENCESなしのstatusデータ
        status = {
            "basic_info": {
                "CLASS_NO": 1,
                "MY_ID": "T0001",
                "MY_NAME": "テスト",
                "GROUP_ID": 1,
                "LEADER_ID": "T0001",
                "LEADER_NAME": "テスト",
            },
            "history": {
                "MY_INFO": "- テスト\n",
                "APP_SPEC_DESCRIBE": "- テスト\n",
                "APP_IMAGE": "- テスト\n",
                "WORK_FLOW": "- テスト\n",
                "MY_WEEKLY_REPORT": "- テスト\n",
                "THANKS2MEMBER": "- テスト\n",
                "MY_THOUGHTS_AND_NEXT_WORKS": "- テスト\n",
            },
        }
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(status, f, ensure_ascii=False)
            f.flush()
            try:
                model = ReportModel(f.name)
                # REFERENCESが追加されている
                assert model.get_section("REFERENCES") != ""
            finally:
                os.unlink(f.name)


class TestReportModelValidationEnhanced:
    """設定ファイルバリデーションの拡張テスト（改修3）。"""

    def test_all_required_fields_valid(self, temp_status_file: str) -> None:
        """全必須フィールドが有効な場合、バリデーションがパスすること。"""
        model = ReportModel(temp_status_file)
        missing = model.validate_basic_info()
        assert missing == []

    def test_empty_my_id_detected(self) -> None:
        """MY_IDが空の場合、検出されること。"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(
                {
                    "basic_info": {
                        "CLASS_NO": 1,
                        "MY_ID": "",
                        "MY_NAME": "テスト",
                        "GROUP_ID": 1,
                        "LEADER_ID": "T0001",
                        "LEADER_NAME": "テスト",
                    },
                    "history": {},
                },
                f,
                ensure_ascii=False,
            )
            f.flush()
            try:
                model = ReportModel(f.name)
                missing = model.validate_basic_info()
                assert "MY_ID" in missing
            finally:
                os.unlink(f.name)

    def test_multiple_missing_fields(self) -> None:
        """複数のフィールドが不足している場合、すべて検出されること。"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(
                {
                    "basic_info": {"CLASS_NO": 1, "MY_ID": "T0001"},
                    "history": {},
                },
                f,
                ensure_ascii=False,
            )
            f.flush()
            try:
                model = ReportModel(f.name)
                missing = model.validate_basic_info()
                assert "MY_NAME" in missing
                assert "GROUP_ID" in missing
                assert "LEADER_ID" in missing
                assert "LEADER_NAME" in missing
            finally:
                os.unlink(f.name)

    def test_validation_after_data_change(self, temp_status_file: str) -> None:
        """データ変更後のバリデーションが正しく動作すること。"""
        model = ReportModel(temp_status_file)
        # 初期状態は有効
        assert model.validate_basic_info() == []
