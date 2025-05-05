#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
トリミング処理モジュール
"""

import traceback
from PIL import Image

class TrimTool:
    """トリミング処理クラス"""

    def __init__(self):
        """初期化"""
        self.last_area = None  # 最後に処理したエリア

    def process(self, image, area):
        """
        トリミング処理を適用

        Args:
            image: PIL.Image オブジェクト
            area: トリミング領域 (x1, y1, x2, y2)

        Returns:
            トリミングされた PIL.Image オブジェクト
        """
        if not image or not area:
            return image

        # 領域の保存
        self.last_area = area

        try:
            # 選択領域が画像の範囲内にあることを確認
            img_width, img_height = image.size
            x1, y1, x2, y2 = area

            # 座標を画像内に制限
            x1 = max(0, min(x1, img_width-1))
            y1 = max(0, min(y1, img_height-1))
            x2 = max(0, min(x2, img_width))
            y2 = max(0, min(y2, img_height))

            # 矩形の幅と高さが0以上であることを確認
            if x2 <= x1 or y2 <= y1:
                print("無効なトリミング領域です")
                return image

            # トリミング実行
            trimmed = image.crop((x1, y1, x2, y2))

            return trimmed

        except Exception as e:
            print(f"トリミング処理中にエラーが発生しました: {str(e)}\n{traceback.format_exc()}")
            # エラーが発生した場合は元の画像を返す
            return image

    def apply_last_settings(self, image):
        """
        前回の設定で再度トリミング処理を適用

        Args:
            image: PIL.Image オブジェクト

        Returns:
            トリミングされた PIL.Image オブジェクト
        """
        if self.last_area and image:
            return self.process(image, self.last_area)
        return image