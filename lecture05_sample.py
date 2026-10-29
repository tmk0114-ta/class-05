import sys

from PySide6 import QtGui
from PySide6.QtWidgets import QApplication, QGridLayout, QPushButton, QWidget


class GameButton(QPushButton):
    """
    ○×ゲーム用のボタンクラス

    ボタン自身の表示状態とゲーム全体の状態を共有しながら
    クリック時の処理や勝敗判定を行う
    """

    def __init__(self, status: dict) -> None:
        """
        ボタンを初期化

        Parameters
        ----------
        status : dict
            ゲーム全体で共有する状態情報
        """
        super().__init__()

        self.status = status
        self.buttons: list["GameButton"] = []

        self.setFont(QtGui.QFont("Arial", 40))
        self.clicked.connect(self.__click)

    def set_buttons(self, buttons: list["GameButton"]) -> None:
        """
        全てのボタンへの参照を保存

        Parameters
        ----------
        buttons : list[GameButton]
            盤面上の全ボタン
        """
        self.buttons = buttons

    def __click(self) -> None:
        """
        ボタンがクリックされたときの処理

        ◯×マークを配置し勝敗判定を実行した後
        次のプレイヤーへターンを移す
        """
        # マス目にマークがあるなら更新しない
        """implemet me"""

        # 現在のプレイヤーのマークを配置
        self.setText(
            self.status["marks"][self.status["next"]]
        )

        # 勝敗判定
        self.__check_win()

        # 次のプレイヤーへ交代
        self.status["next"] = 1 - self.status["next"]

    def __check_win(self) -> None:
        """
        勝敗判定を実行

        横・縦・斜めの全8パターンについて確認
        """
        patterns = [
            [0, 1, 2],
            [3, 4, 5],
            [6, 7, 8],
            [0, 3, 6],
            [1, 4, 7],
            [2, 5, 8],
            [0, 4, 8],
            [2, 4, 6],
        ]

        # ToDO: Debugのため最初のpatternのみ確認
        for pattern in patterns[:1]:
            self.__check_a_line(pattern)

    def __check_a_line(self, pattern: list[int]) -> None:
        """
        指定された3マスについて勝敗判定

        Parameters
        ----------
        pattern : list[int]
            判定対象となるマス番号のリスト
        """
        btns: list[GameButton] = [
            self.buttons[i] for i in pattern
        ]

        result = [btn.text() for btn in btns]

        # ○の勝利
        if result[0] == result[1] == result[2] == self.status["marks"][0]:
            print(f"{self.status['marks'][0]}の勝ち")

            for btn in btns:
                btn.setStyleSheet("color: #ff0000;")

        # ×の勝利
        """implement me"""


class MainWidget(QWidget):
    """
    ◯×並べアプリのメインウィンドウ
    """

    def __init__(self) -> None:
        """
        画面およびゲーム状態を初期化
        """
        super().__init__()

        self.__game_init()

        # ボタン生成
        self.buttons = [
            GameButton(self.game_status)
            for _ in range(9)
        ]

        # 各ボタンへ全ボタンの参照を渡す
        for btn in self.buttons:
            btn.set_buttons(self.buttons)

        # グリッドレイアウト構築
        layout = QGridLayout()

        for row in range(3):
            for col in range(3):
                layout.addWidget(
                    self.buttons[row * 3 + col],
                    row,
                    col,
                )

        self.setLayout(layout)

    def __game_init(self) -> None:
        """
        ゲーム状態を初期化

        game_status["marks"]
            プレイヤーのマーク一覧

        game_status["next"]
            次の手番プレイヤー
        """
        self.game_status = {
            "marks": ["○", "×"],
            "next": 0,
        }


if __name__ == "__main__":
    app = QApplication(sys.argv)

    main_widget = MainWidget()
    main_widget.show()

    app.exec()