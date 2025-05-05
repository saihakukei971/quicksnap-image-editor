#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
塗りつぶし処理モジュール
"""

import traceback
from PIL import Image, ImageDraw

class PaintTool:
    """塗りつぶし処理クラス"""

    def __init__(self):
        """初期化"""
        self.color = '#FF0000'  # デフォルト色（赤）
        self.last_area = None  # 最後に処理したエリア

    def set_color(self, color):
        """
        塗りつぶし色を設定

        Args:
            color: カラーコード（例: '#FF0000'）
        """
        self.color = color

    def get_color(self):
        """現在の塗りつぶし色を取得"""
        return self.color

    def process(self, image, area, color=None):
        """
        塗りつぶし処理を適用

        Args:
            image: PIL.Image オブジェクト
            area: 塗りつぶし領域 (x1, y1, x2, y2)
            color: カラーコード（指定がない場合は現在の色を使用）

        Returns:
            塗りつぶし処理された PIL.Image オブジェクト
        """
        if not image or not area:
            return image

        # 色が指定されていない場合は現在の色を使用
        if color is None:
            color = self.color

        # 領域の保存
        self.last_area = area

        try:
            # 画像のコピーを作成し、アルファチャンネルを確保
            if image.mode != 'RGBA':
                result = image.convert('RGBA')
            else:
                result = image.copy()

            # 描画オブジェクト作成
            draw = ImageDraw.Draw(result)

            # 色の解析
            try:
                # 16進カラーコードをRGBAに変換
                if color.startswith('#'):
                    if len(color) == 7:  # #RRGGBB
                        r = int(color[1:3], 16)
                        g = int(color[3:5], 16)
                        b = int(color[5:7], 16)
                        a = 255
                    elif len(color) == 9:  # #RRGGBBAA
                        r = int(color[1:3], 16)
                        g = int(color[3:5], 16)
                        b = int(color[5:7], 16)
                        a = int(color[7:9], 16)
                    else:
                        r, g, b, a = 255, 0, 0, 255  # デフォルト赤
                else:
                    r, g, b, a = 255, 0, 0, 255  # デフォルト赤
            except:
                r, g, b, a = 255, 0, 0, 255  # エラー時はデフォルト赤

            # 矩形を塗りつぶし
            draw.rectangle(area, fill=(r, g, b, a))

            return result

        except Exception as e:
            print(f"塗りつぶし処理中にエラーが発生しました: {str(e)}\n{traceback.format_exc()}")
            # エラーが発生した場合は元の画像を返す
            return image

    def apply_last_settings(self, image):
        """
        前回の設定で再度塗りつぶし処理を適用

        Args:
            image: PIL.Image オブジェクト

        Returns:
            塗りつぶし処理された PIL.Image オブジェクト
        """
        if self.last_area and image:
            return self.process(image, self.last_area, self.color)
        return image