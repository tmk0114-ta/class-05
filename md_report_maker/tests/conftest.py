"""共有フィクスチャ。

テスト全体で使用するpytestフィクスチャを定義する。
"""

import json
import os
import tempfile
from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication


@pytest.fixture(scope="session")
def qt_app():
    """セッションスコープのQApplicationフィクスチャ。"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    app.quit()


@pytest.fixture
def sample_basic_info() -> dict:
    """テスト用のbasic_infoデータ。"""
    return {
        "CLASS_NO": 1,
        "MY_ID": "T0001",
        "MY_NAME": "テスト太郎",
        "GROUP_ID": 1,
        "LEADER_ID": "T0001",
        "LEADER_NAME": "テスト太郎",
        "MEMBER_ID_1": "T0001",
        "MEMBER_NAME_1": "テスト太郎",
        "MEMBER_ID_2": "T0002",
        "MEMBER_NAME_2": "テスト花子",
        "MEMBER_ID_3": "T0003",
        "MEMBER_NAME_3": "テスト三郎",
        "MEMBER_ID_4": "T0004",
        "MEMBER_NAME_4": "テスト四郎",
        "MEMBER_ID_5": "T0005",
        "MEMBER_NAME_5": "テスト五郎",
    }


@pytest.fixture
def sample_status(sample_basic_info: dict) -> dict:
    """テスト用のstatusデータ（historyなし）。"""
    return {
        "basic_info": sample_basic_info,
        "history": {},
    }


@pytest.fixture
def sample_status_with_history(sample_basic_info: dict) -> dict:
    """テスト用のstatusデータ（historyあり）。"""
    return {
        "basic_info": sample_basic_info,
        "history": {
            "MY_INFO": "- 学籍番号：T0001\n- 氏名：テスト太郎\n",
            "APP_SPEC_DESCRIBE": "- テスト仕様\n",
            "APP_IMAGE": "- テストイメージ\n",
            "WORK_FLOW": "- テスト作業分担\n",
            "MY_WEEKLY_REPORT": "- テスト報告\n",
            "THANKS2MEMBER": "- テスト感謝\n",
            "MY_THOUGHTS_AND_NEXT_WORKS": "- テスト振り返り\n",
        },
    }


@pytest.fixture
def temp_status_file(sample_status: dict) -> str:
    """一時的なstatus.jsonファイルのパスを返す。

    テスト終了後に自動的に削除される。
    """
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    ) as f:
        json.dump(sample_status, f, ensure_ascii=False)
        f.flush()
        yield f.name
    os.unlink(f.name)


@pytest.fixture
def temp_status_with_history_file(sample_status_with_history: dict) -> str:
    """history付きの一時的なstatus.jsonファイルのパスを返す。"""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    ) as f:
        json.dump(sample_status_with_history, f, ensure_ascii=False)
        f.flush()
        yield f.name
    os.unlink(f.name)


@pytest.fixture
def temp_output_dir() -> str:
    """一時的な出力ディレクトリのパスを返す。

    テスト終了後に自動的に削除される。
    """
    with tempfile.TemporaryDirectory() as d:
        yield d
