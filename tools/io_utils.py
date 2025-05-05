#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
画像入出力ユーティリティ
"""

import os
import io
import sys
import traceback
from pathlib import Path
from PIL import Image, UnidentifiedImageError

class ImageIO:
    """画像の読み込み・保存を扱うクラス"""

    def __init__(self):
        """初期化"""
        # クリップボード操作用
        self.clipboard_available = False
        try:
            import pyperclip
            self.pyperclip = pyperclip
            self.clipboard_available = True
        except ImportError:
            print("pyperclipがインストールされていません。クリップボード機能は無効です。")
        except Exception as e:
            print(f"クリップボード機能の初期化エラー: {str(e)}")

        # OpenCV (クリップボード画像取得用)
        self.cv2_available = False
        try:
            import cv2
            import numpy as np
            self.cv2 = cv2
            self.np = np
            self.cv2_available = True
        except ImportError:
            print("OpenCVがインストールされていません。一部の機能が制限されます。")
        except Exception as e:
            print(f"OpenCVの初期化エラー: {str(e)}")

    def load_from_file(self, file_path):
        """
        ファイルから画像を読み込む

        Args:
            file_path: 画像ファイルのパス

        Returns:
            PIL.Image オブジェクト、失敗時は None
        """
        try:
            if not os.path.exists(file_path):
                print(f"ファイルが存在しません: {file_path}")
                return None

            image = Image.open(file_path)

            # PNG、GIF以外はRGBA変換を行わない
            if image.format == "PNG" or image.format == "GIF":
                if image.mode != 'RGBA':
                    image = image.convert('RGBA')
            elif image.mode != 'RGB':
                image = image.convert('RGB')

            return image

        except UnidentifiedImageError:
            print(f"サポートされていない画像形式です: {file_path}")
            return None
        except Exception as e:
            print(f"画像読み込みエラー: {str(e)}\n{traceback.format_exc()}")
            return None

    def load_from_clipboard(self):
        """
        クリップボードから画像を読み込む

        Returns:
            PIL.Image オブジェクト、失敗時は None
        """
        # 方法1: OpenCVを使用する方法（推奨）
        if self.cv2_available:
            try:
                import win32clipboard

                win32clipboard.OpenClipboard()
                try:
                    if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_DIB):
                        data = win32clipboard.GetClipboardData(win32clipboard.CF_DIB)

                        # DIBからBMPへ変換
                        bmp_header = b'\x42\x4D' + len(data).to_bytes(4, byteorder='little') + b'\x00\x00\x00\x00\x36\x00\x00\x00'
                        bmp_data = bmp_header + data[14:]

                        # BytesIOでPIL Imageに変換
                        image = Image.open(io.BytesIO(bmp_data))
                        return image
                finally:
                    win32clipboard.CloseClipboard()
            except ImportError:
                print("win32clipboardがインストールされていません。")
            except Exception as e:
                print(f"クリップボードからの画像読み込みエラー (OpenCV): {str(e)}")

        # 方法2: PILとTkinterを使用する方法（フォールバック）
        try:
            import tkinter as tk

            root = tk.Tk()
            root.withdraw()  # ウィンドウを表示しない

            try:
                image = ImageGrab.grabclipboard()
                if isinstance(image, Image.Image):
                    return image
            except Exception as e:
                print(f"クリップボードからの画像読み込みエラー (PIL): {str(e)}")
            finally:
                root.destroy()

        except ImportError:
            print("tkinterがインストールされていません。")
        except Exception as e:
            print(f"クリップボードからの画像読み込みエラー: {str(e)}")

        print("クリップボードから画像を読み込めませんでした。")
        return None

    def save_to_file(self, image, file_path):
        """
        画像をファイルに保存

        Args:
            image: PIL.Image オブジェクト
            file_path: 保存先のパス

        Returns:
            成功時は True、失敗時は False
        """
        try:
            # ファイルの拡張子から保存形式を決定
            format_map = {
                '.png': 'PNG',
                '.jpg': 'JPEG',
                '.jpeg': 'JPEG',
                '.bmp': 'BMP',
                '.gif': 'GIF'
            }

            file_ext = os.path.splitext(file_path)[1].lower()
            save_format = format_map.get(file_ext, 'PNG')

            # RGB/RGBAモードの適切な変換
            if save_format == 'JPEG' and image.mode == 'RGBA':
                # JPEGはアルファチャンネルをサポートしていないのでRGBに変換
                image = image.convert('RGB')

            # 保存実行
            image.save(file_path, format=save_format)
            print(f"画像を保存しました: {file_path}")
            return True

        except Exception as e:
            print(f"画像保存エラー: {str(e)}\n{traceback.format_exc()}")
            return False

    def copy_to_clipboard(self, image):
        """
        画像をクリップボードにコピー

        Args:
            image: PIL.Image オブジェクト

        Returns:
            成功時は True、失敗時は False
        """
        if not self.clipboard_available:
            print("クリップボード機能がインストールされていません")
            return False

        try:
            # Windows環境の場合
            if sys.platform == 'win32':
                try:
                    import win32clipboard
                    from io import BytesIO

                    # PNGとしてバイトストリームに保存
                    output = BytesIO()
                    image.convert('RGB').save(output, 'BMP')
                    data = output.getvalue()[14:]  # BMPヘッダーを除く
                    output.close()

                    # クリップボードに貼り付け
                    win32clipboard.OpenClipboard()
                    win32clipboard.EmptyClipboard()
                    win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
                    win32clipboard.CloseClipboard()

                    return True
                except ImportError:
                    print("win32clipboardがインストールされていません")

            # macOSの場合
            elif sys.platform == 'darwin':
                try:
                    import subprocess
                    from tempfile import NamedTemporaryFile

                    # 一時ファイルに保存
                    with NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                        temp_filename = temp_file.name

                    image.save(temp_filename, 'PNG')

                    # pbcopyコマンドでクリップボードにコピー
                    subprocess.run(['osascript', '-e',
                        f'set the clipboard to (read (POSIX file "{temp_filename}") as TIFF picture)'])

                    # 一時ファイルを削除
                    os.unlink(temp_filename)

                    return True
                except Exception as e:
                    print(f"macOSクリップボードエラー: {str(e)}")

            # Linux環境の場合 (xclipが必要)
            elif sys.platform.startswith('linux'):
                try:
                    import subprocess
                    from tempfile import NamedTemporaryFile

                    # 一時ファイルに保存
                    with NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                        temp_filename = temp_file.name

                    image.save(temp_filename, 'PNG')

                    # xclipコマンドでクリップボードにコピー
                    subprocess.run(['xclip', '-selection', 'clipboard',
                                    '-target', 'image/png', '-i', temp_filename])

                    # 一時ファイルを削除
                    os.unlink(temp_filename)

                    return True
                except Exception as e:
                    print(f"Linuxクリップボードエラー: {str(e)}")

            print(f"このプラットフォームではクリップボードへの画像コピーに対応していません: {sys.platform}")
            return False

        except Exception as e:
            print(f"クリップボードコピーエラー: {str(e)}\n{traceback.format_exc()}")
            return False
