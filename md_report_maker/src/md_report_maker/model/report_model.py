"""データモデルモジュール。

レポートのデータ管理、テンプレート展開、ファイルの読み書きを担当する。
"""

import json
import os
import string
from pathlib import Path


class ReportModel:
    """レポートデータの管理を行うモデルクラス。

    status.jsonからのデータ読み込み、マークダウン本文の生成、
    ファイルの保存・読み込みを担当する。
    """

    # レポートセクションのキー一覧
    SECTION_KEYS: list[str] = [
        "CLASS_NO",
        "MY_INFO",
        "APP_SPEC_DESCRIBE",
        "APP_IMAGE",
        "WORK_FLOW",
        "MY_WEEKLY_REPORT",
        "THANKS2MEMBER",
        "MY_THOUGHTS_AND_NEXT_WORKS",
        "REFERENCES",
    ]

    # 必須フィールド（basic_info内）
    REQUIRED_BASIC_FIELDS: list[str] = [
        "CLASS_NO",
        "MY_ID",
        "MY_NAME",
        "GROUP_ID",
        "LEADER_ID",
        "LEADER_NAME",
    ]

    def __init__(self, config_path: str = "status.json") -> None:
        """モデルを初期化する。

        Args:
            config_path: 設定ファイルのパス（デフォルト: "status.json"）
        """
        self._config_path: str = config_path
        self._status: dict = {}
        self._basic_info: dict = {}
        self._history: dict = {}
        self._load_config(config_path)

    def _load_config(self, config_path: str) -> None:
        """設定ファイルを読み込む。

        Args:
            config_path: 設定ファイルのパス

        Raises:
            FileNotFoundError: 設定ファイルが存在しない場合
            ValueError: 設定ファイルの形式が不正な場合
        """
        if not os.path.isfile(config_path):
            raise FileNotFoundError(
                f"設定ファイルが見つかりません: {config_path}\n"
                f"config/status_orig.jsonを参考にstatus.jsonを作成してください。"
            )

        try:
            with open(config_path, encoding="utf-8") as f:
                self._status = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"設定ファイルのJSON形式が不正です: {e}")

        # basic_infoとhistoryがそれぞれ存在するか確認し、存在しない場合は空の辞書を設定
        if "basic_info" not in self._status:
            self._status["basic_info"] = {}
        if "history" not in self._status:
            self._status["history"] = {}

        self._basic_info = self._status["basic_info"]
        self._history = self._status["history"]

        # historyが空の場合はデフォルトテンプレートを設定
        if not self._history:
            self._initialize_history()
        # REFERENCESが存在しない場合は追加（既存データとの互換性）
        if "REFERENCES" not in self._history:
            self._history["REFERENCES"] = self._template_references()

    def _initialize_history(self) -> None:
        """historyセクションにデフォルトテンプレートを設定する。"""
        self._history["MY_INFO"] = self._template_my_info()
        self._history["APP_SPEC_DESCRIBE"] = self._template_app_spec_describe()
        self._history["APP_IMAGE"] = self._template_app_image()
        self._history["WORK_FLOW"] = self._template_work_flow()
        self._history["MY_WEEKLY_REPORT"] = self._template_my_weekly_report()
        self._history["THANKS2MEMBER"] = self._template_thanks2member()
        self._history["MY_THOUGHTS_AND_NEXT_WORKS"] = (
            self._template_my_thoughts_and_next_works()
        )
        self._history["REFERENCES"] = self._template_references()

    def get_body(self) -> str:
        """マークダウン形式のレポート本文を生成する。

        テンプレートを2段階で展開する：
        1. historyセクションの変数を展開
        2. basic_infoセクションの変数を展開

        Returns:
            マークダウン形式の文字列
        """
        template = string.Template(self._report_template())
        body = template.safe_substitute(self._history)
        template = string.Template(body)
        body = template.safe_substitute(self._basic_info)
        return body

    def get_section(self, key: str) -> str:
        """指定されたキーのセクション値を取得する。

        Args:
            key: セクションキー（SECTION_KEYSの要素）

        Returns:
            セクションの文字列値

        Raises:
            KeyError: 無効なキーが指定された場合
        """
        if key not in self.SECTION_KEYS:
            raise KeyError(f"無効なセクションキー: {key}")

        if key == "CLASS_NO":
            return str(self._basic_info.get("CLASS_NO", ""))
        return self._history.get(key, "")

    def set_section(self, key: str, value: str) -> None:
        """指定されたキーのセクション値を設定する。

        Args:
            key: セクションキー（SECTION_KEYSの要素）
            value: 設定する文字列値

        Raises:
            KeyError: 無効なキーが指定された場合
        """
        if key not in self.SECTION_KEYS:
            raise KeyError(f"無効なセクションキー: {key}")

        if key == "CLASS_NO":
            self._basic_info["CLASS_NO"] = int(value)
        else:
            self._history[key] = value

    def get_section_keys(self) -> list[str]:
        """利用可能なセクションキーの一覧を取得する。

        Returns:
            セクションキーのリスト
        """
        return list(self.SECTION_KEYS)

    def save_report(self, markdown_text: str, file_path: str | None = None) -> str:
        """マークダウン形式でレポートを保存する。

        Args:
            markdown_text: 保存するマークダウンテキスト
            file_path: 保存先パス（Noneの場合、デフォルト名を生成）

        Returns:
            保存したファイルのパス
        """
        if file_path is None:
            file_path = self._default_report_filename()
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(markdown_text)
        return file_path

    def save_status(self, file_path: str | None = None) -> str:
        """現在の状態をJSONファイルに保存する。

        Args:
            file_path: 保存先パス（Noneの場合、設定ファイルを上書き）

        Returns:
            保存したファイルのパス
        """
        # statusディクショナリを最新状態に同期
        self._status["basic_info"] = self._basic_info
        self._status["history"] = self._history

        target_path = file_path if file_path is not None else self._config_path
        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(self._status, f, indent=4, ensure_ascii=False)
        return target_path

    def load_status(self, file_path: str) -> None:
        """JSONファイルから状態を読み込む。

        Args:
            file_path: 読み込むファイルのパス
        """
        self._load_config(file_path)

    def validate_basic_info(self) -> list[str]:
        """basic_infoの必須フィールドを検証する。

        Returns:
            不足しているフィールド名のリスト（空なら問題なし）
        """
        missing = []
        for field in self.REQUIRED_BASIC_FIELDS:
            if field not in self._basic_info or not self._basic_info[field]:
                missing.append(field)
        return missing

    def _default_report_filename(self) -> str:
        """デフォルトのレポートファイル名を生成する。

        Returns:
            ファイル名（例: "K23999愛知太郎.md"）
        """
        my_id = self._basic_info.get("MY_ID", "unknown")
        my_name = self._basic_info.get("MY_NAME", "unknown")
        return f"{my_id}{my_name}.md"

    # --- テンプレート生成メソッド ---

    def _report_template(self) -> str:
        """レポート全体のテンプレートを返す。"""
        return """\
# オブジェクト指向プログラミングおよび演習 第$CLASS_NO回進捗レポート

## 作成者情報
$MY_INFO

## 仕様
$APP_SPEC_DESCRIBE

## アプリ完成イメージ
$APP_IMAGE

## 作業分担
$WORK_FLOW

## 作業報告
$MY_WEEKLY_REPORT

## グループ内でお世話になった人2〜3名を理由とともに挙げる
$THANKS2MEMBER

## 振り返り（感想含む）と次回までの作業予定
$MY_THOUGHTS_AND_NEXT_WORKS

## 参考文献
$REFERENCES
"""

    def _template_my_info(self) -> str:
        """作成者情報のテンプレートを返す。"""
        ret = """\
- 学籍番号：$MY_ID
- 氏名：$MY_NAME
- グループ：$GROUP_ID
    - メンバー
        - $LEADER_ID $LEADER_NAME（チームリーダー）
"""
        for i in range(1, 9):
            member_id_key = f"MEMBER_ID_{i}"
            if member_id_key in self._basic_info:
                ret += f"        - ${member_id_key} ${member_id_key.replace('ID', 'NAME')}\n"
        return ret

    @staticmethod
    def _template_app_spec_describe() -> str:
        """仕様セクションのデフォルトテンプレートを返す。"""
        return """\
- flaskを使ったフォトアルバム
- 画像をアップロードできる
- アップロードした画像にタグをつけられる
- アップロードした画像にコメントを書ける
- 画像検索ページでタグやコメントから画像を検索できる
- CSSで画面を見やすくする
"""

    @staticmethod
    def _template_app_image() -> str:
        """アプリ完成イメージのデフォルトテンプレートを返す。"""
        return """\
- ここにトップページの手書きいらすと（top_page.jpegもMoodleへアップロードした）
- ここに画像リストページの手書きイラスト(image_list_page.jpeg)
- ここに画像アップロードページの手書きいらすと(upload_page.jpeg)
- ここに画像検索ページの手書きイラスト(search_page.jpeg)
"""

    def _template_work_flow(self) -> str:
        """作業分担のテンプレートを返す。"""
        return """\
- 画像をアップロードできる（担当：$MEMBER_ID_3 $MEMBER_NAME_3）
- アップロードした画像にタグをつけられる（主担当：$MEMBER_ID_1 $MEMBER_NAME_1，副担当：$MEMBER_ID_2 $MEMBER_NAME_2）
- アップロードした画像にコメントを書ける（主担当：$MEMBER_ID_2 $MEMBER_NAME_2，副担当：$MEMBER_ID_1 $MEMBER_NAME_1）
- 画像検索ページでタグやコメントから画像を検索できる（担当：$MEMBER_ID_4 $MEMBER_NAME_4）
- CSSで画面を見やすくする（担当：$MEMBER_ID_5 $MEMBER_NAME_5）
"""

    @staticmethod
    def _template_my_weekly_report() -> str:
        """週次報告のデフォルトテンプレートを返す。"""
        return """\
- (これはサンプルです)
- 画像を保管する仕様を愛知花子と話あって決めた
- 保管した画像がWebページに表示されるところまで愛知花子と共同作業して作った
    - プルリクエストへのリンク
    - 上のプルリクエストがマージされた
"""

    def _template_thanks2member(self) -> str:
        """メンバー感謝のテンプレートを返す。"""
        return """\
- 画像処理のベースプログラム実装を一緒にした($MEMBER_ID_2 $MEMBER_NAME_2)
- プルリクエストを処理してくれた（$MEMBER_ID_1 $MEMBER_NAME_1）
- 調べ物を手伝ってくれた($MEMBER_ID_5 $MEMBER_NAME_5)
"""

    @staticmethod
    def _template_my_thoughts_and_next_works() -> str:
        """振り返りのデフォルトテンプレートを返す。"""
        return """\
- 計画通りに作業は進んでいる
- 画像を取り扱う共通仕様は愛知花子と共同で作成したが，来週からは作業を分担してすすめる
"""

    @staticmethod
    def _template_references() -> str:
        """参考文献のデフォルトテンプレートを返す。"""
        return """\
- (ここに参考文献を記載)
"""
