
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QuickSnap - クイック画像加工ツール
"""

import os
import sys
import json
import traceback
from pathlib import Path

# アプリケーションのルートパスを設定
ROOT_DIR = Path(__file__).parent
TOOLS_DIR = ROOT_DIR / "tools"
UI_DIR = ROOT_DIR / "ui"
SETTINGS_FILE = ROOT_DIR / "settings.json"

# パスをシステムパスに追加
sys.path.insert(0, str(ROOT_DIR))

# UIとツールモジュールをインポート
from ui.quick_ui import QuickEditorGUI
from tools.io_utils import ImageIO
from tools.bg_remover import BackgroundRemover
from tools.mosaic import MosaicTool
from tools.painter import PaintTool
from tools.trimmer import TrimTool

class QuickImageEditor:
    """QuickSnapアプリケーションのメインクラス"""

    def __init__(self):
        """初期化"""
        # 設定をロード
        self.settings = self._load_settings()

        # 各ツールの初期化
        self.image_io = ImageIO()
        self.bg_remover = BackgroundRemover()
        self.mosaic_tool = MosaicTool()
        self.paint_tool = PaintTool()
        self.trim_tool = TrimTool()

        # GUIの初期化
        self.gui = QuickEditorGUI(self._handle_events)

        # 現在の画像とモード
        self.current_image = None
        self.original_image = None
        self.current_mode = None
        self.selection_area = None

    def run(self):
        """アプリケーションの実行"""
        try:
            # GUIイベントループを開始
            self.gui.run()
        except Exception as e:
            error_msg = f"エラーが発生しました: {str(e)}\n{traceback.format_exc()}"
            self.gui.show_error(error_msg)
            print(error_msg)
        finally:
            # 設定を保存
            self._save_settings()

    def _handle_events(self, event, values):
        """GUIイベントハンドラー"""
        try:
            # ファイル読み込み関連イベント
            if event == "開く":
                self._load_image_from_file()
            elif event == "ペースト" or event == "クリップボード":
                self._load_image_from_clipboard()
            elif event == "ドロップ":
                self._load_image_from_drop(values.get("ドロップ", ""))

            # 画像処理モード選択
            elif event == "背景透過":
                self._process_bg_remove()
            elif event == "モザイク":
                self._set_mode("mosaic")
            elif event == "塗りつぶし":
                self._set_mode("paint")
            elif event == "トリム":
                self._set_mode("trim")

            # 回転・反転
            elif event == "左回転":
                self._rotate_image(90)
            elif event == "右回転":
                self._rotate_image(-90)
            elif event == "水平反転":
                self._flip_image("horizontal")
            elif event == "垂直反転":
                self._flip_image("vertical")

            # 保存関連
            elif event == "保存":
                self._save_image()
            elif event == "コピー":
                self._copy_to_clipboard()

            # 選択領域関連
            elif event == "選択開始":
                self.selection_area = values.get("選択開始")
            elif event == "選択終了":
                end_pos = values.get("選択終了")
                if self.selection_area and end_pos:
                    self._process_selection(self.selection_area, end_pos)

            # モザイク強度変更
            elif event == "モザイク強度":
                if self.current_mode == "mosaic" and self.selection_area:
                    strength = values.get("モザイク強度", 10)
                    self._apply_mosaic(strength)

            # 色選択
            elif event == "色選択":
                if self.current_mode == "paint":
                    color = values.get("色選択")
                    self.paint_tool.set_color(color)

            # 終了イベント
            elif event in (None, "終了"):
                return False

        except Exception as e:
            error_msg = f"操作中にエラーが発生しました: {str(e)}"
            self.gui.show_error(error_msg)
            print(error_msg, traceback.format_exc())

        return True

    def _load_image_from_file(self):
        """ファイル選択から画像を読み込む"""
        file_path = self.gui.get_file_path()
        if file_path:
            image = self.image_io.load_from_file(file_path)
            if image:
                self._set_current_image(image)
                self.settings["last_directory"] = os.path.dirname(file_path)

    def _load_image_from_clipboard(self):
        """クリップボードから画像を読み込む"""
        image = self.image_io.load_from_clipboard()
        if image:
            self._set_current_image(image)

    def _load_image_from_drop(self, file_path):
        """ドラッグ&ドロップから画像を読み込む"""
        if file_path and os.path.isfile(file_path):
            image = self.image_io.load_from_file(file_path)
            if image:
                self._set_current_image(image)
                self.settings["last_directory"] = os.path.dirname(file_path)

    def _set_current_image(self, image):
        """現在の画像を設定し、GUIを更新"""
        self.current_image = image
        self.original_image = image.copy()
        self.gui.update_image(image)
        self.current_mode = None
        self.selection_area = None

    def _set_mode(self, mode):
        """編集モードを設定"""
        self.current_mode = mode
        self.selection_area = None
        # モード変更時にGUIの状態を更新
        self.gui.update_mode(mode)

    def _process_bg_remove(self):
        """背景透過処理を適用"""
        if self.current_image:
            self.gui.show_processing("背景透過処理中...")
            result = self.bg_remover.process(self.current_image)
            self.current_image = result
            self.gui.update_image(result)
            self.gui.hide_processing()

    def _process_selection(self, start_pos, end_pos):
        """選択領域に対する処理を実行"""
        if not self.current_image or not self.current_mode:
            return

        # 選択領域の座標を正規化
        x1, y1 = min(start_pos[0], end_pos[0]), min(start_pos[1], end_pos[1])
        x2, y2 = max(start_pos[0], end_pos[0]), max(start_pos[1], end_pos[1])

        if x1 == x2 or y1 == y2:  # 有効な領域がない
            return

        area = (x1, y1, x2, y2)

        # 各モードに応じた処理
        if self.current_mode == "mosaic":
            strength = self.gui.get_mosaic_strength()
            self._apply_mosaic(strength, area)
        elif self.current_mode == "paint":
            self._apply_paint(area)
        elif self.current_mode == "trim":
            self._apply_trim(area)

    def _apply_mosaic(self, strength, area=None):
        """モザイク処理を適用"""
        if self.current_image:
            if area:
                result = self.mosaic_tool.process(self.current_image, area, strength)
            else:
                # 以前の選択領域に新しい強度を適用
                result = self.mosaic_tool.process(
                    self.current_image,
                    self.mosaic_tool.last_area,
                    strength
                )
            self.current_image = result
            self.gui.update_image(result)

    def _apply_paint(self, area):
        """塗りつぶし処理を適用"""
        if self.current_image:
            color = self.paint_tool.get_color()
            result = self.paint_tool.process(self.current_image, area, color)
            self.current_image = result
            self.gui.update_image(result)

    def _apply_trim(self, area):
        """トリミング処理を適用"""
        if self.current_image:
            result = self.trim_tool.process(self.current_image, area)
            self.current_image = result
            self.gui.update_image(result)

    def _rotate_image(self, angle):
        """画像を回転"""
        if self.current_image:
            from PIL import Image
            rotated = self.current_image.rotate(angle, expand=True)
            self.current_image = rotated
            self.gui.update_image(rotated)

    def _flip_image(self, direction):
        """画像を反転"""
        if self.current_image:
            from PIL import Image
            if direction == "horizontal":
                flipped = self.current_image.transpose(Image.FLIP_LEFT_RIGHT)
            else:
                flipped = self.current_image.transpose(Image.FLIP_TOP_BOTTOM)
            self.current_image = flipped
            self.gui.update_image(flipped)

    def _save_image(self):
        """画像をファイルに保存"""
        if self.current_image:
            file_path = self.gui.get_save_path(
                initial_dir=self.settings.get("last_directory", "")
            )
            if file_path:
                success = self.image_io.save_to_file(self.current_image, file_path)
                if success:
                    self.gui.show_info(f"画像を保存しました: {file_path}")
                    self.settings["last_directory"] = os.path.dirname(file_path)

    def _copy_to_clipboard(self):
        """画像をクリップボードにコピー"""
        if self.current_image:
            success = self.image_io.copy_to_clipboard(self.current_image)
            if success:
                self.gui.show_info("画像をクリップボードにコピーしました")

    def _load_settings(self):
        """設定をJSONファイルから読み込む"""
        default_settings = {
            "last_directory": "",
            "default_save_format": "png",
            "window_size": (800, 600)
        }

        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"設定読み込みエラー: {e}")

        return default_settings

    def _save_settings(self):
        """設定をJSONファイルに保存"""
        try:
            with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"設定保存エラー: {e}")

if __name__ == "__main__":
    # 必要なディレクトリが存在することを確認
    os.makedirs(TOOLS_DIR, exist_ok=True)
    os.makedirs(UI_DIR, exist_ok=True)

    # アプリケーションを起動
    app = QuickImageEditor()
    app.run()