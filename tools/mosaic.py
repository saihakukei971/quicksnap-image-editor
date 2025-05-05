#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
モザイク処理モジュール
"""

import traceback
from PIL import Image

class MosaicTool:
    """モザイク処理クラス"""

    def __init__(self):
        """初期化"""
        self.last_area = None  # 最後に処理したエリア
        self.last_strength = 10  # デフォルトのモザイク強度

    def process(self, image, area, strength=None):
        """
        モザイク処理を適用

        Args:
            image: PIL.Image オブジェクト
            area: モザイクを適用する領域 (x1, y1, x2, y2)
            strength: モザイクの強度 (1-50)

        Returns:
            モザイク処理された PIL.Image オブジェクト
        """
        if not image or not area:
            return image

        # 強度が指定されていない場合は前回の値か初期値を使用
        if strength is None:
            strength = self.last_strength
        else:
            self.last_strength = strength

        # 領域の保存
        self.last_area = area

        try:
            # 画像のコピーを作成
            result = image.copy()

            # 領域を切り出し
            x1, y1, x2, y2 = area
            region = result.crop(area)

            # モザイク処理
            # 縮小サイズの計算（強度に応じて調整）
            scale_factor = max(1, int(50 / strength))
            small_size = (max(1, (x2 - x1) // scale_factor), max(1, (y2 - y1) // scale_factor))

            # 縮小してから拡大することでモザイク効果を得る
            small_img = region.resize(small_size, Image.NEAREST)
            mosaic_region = small_img.resize((x2 - x1, y2 - y1), Image.NEAREST)

            # 元の画像に貼り付け
            result.paste(mosaic_region, (x1, y1))

            return result

        except Exception as e:
            print(f"モザイク処理中にエラーが発生しました: {str(e)}\n{traceback.format_exc()}")
            # エラーが発生した場合は元の画像を返す
            return image

    def apply_last_settings(self, image):
        """
        前回の設定で再度モザイク処理を適用

        Args:
            image: PIL.Image オブジェクト

        Returns:
            モザイク処理された PIL.Image オブジェクト
        """
        if self.last_area and image:
            return self.process(image, self.last_area, self.last_strength)
        return image
