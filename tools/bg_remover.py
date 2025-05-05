#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
背景透過処理モジュール - rembgライブラリを利用
"""

import os
import sys
import time
import traceback
from pathlib import Path
from PIL import Image

class BackgroundRemover:
    """
    背景透過処理クラス
    rembgライブラリを使用して画像の背景を透過させる
    """

    def __init__(self):
        """初期化"""
        self.rembg_loaded = False
        self.model_downloaded = False
        self.last_error = None

        # rembgのロード
        try:
            from rembg import remove
            self.remove = remove
            self.rembg_loaded = True
        except ImportError:
            self.last_error = "rembgライブラリがインストールされていません。\n" \
                              "pip install rembg を実行してインストールしてください。"
        except Exception as e:
            self.last_error = f"rembgライブラリのロード中にエラーが発生しました：{str(e)}"

    def process(self, image):
        """
        背景透過処理を実行

        Args:
            image: PIL.Image オブジェクト

        Returns:
            背景が透過された PIL.Image オブジェクト
            エラーが発生した場合は元の画像を返す
        """
        if not self.rembg_loaded:
            print(self.last_error)
            return image

        try:
            # 処理を実行
            start_time = time.time()
            result = self.remove(image)
            process_time = time.time() - start_time

            print(f"背景透過処理完了: {process_time:.2f}秒")
            self.model_downloaded = True

            return result

        except Exception as e:
            error_msg = f"背景透過処理中にエラーが発生しました: {str(e)}\n{traceback.format_exc()}"
            print(error_msg)
            self.last_error = error_msg

            # エラーが発生した場合は元の画像を返す
            return image

    def get_last_error(self):
        """最後に発生したエラーメッセージを返す"""
        return self.last_error

    def is_ready(self):
        """背景透過処理が実行可能かどうかを返す"""
        return self.rembg_loaded