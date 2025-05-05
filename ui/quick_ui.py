
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QuickSnap - GUIモジュール
"""

import os
import io
import PySimpleGUI as sg
import PIL.Image
from PIL import ImageTk

class QuickEditorGUI:
    """クイック画像エディタのGUIクラス"""

    def __init__(self, event_handler):
        """
        GUIの初期化

        Args:
            event_handler: GUIイベントを処理するコールバック関数
        """
        # テーマ設定
        sg.theme('LightGrey1')

        # 初期ウィンドウサイズ
        self.window_size = (800, 600)
        self.image_display_size = (780, 480)

        # イベントハンドラー
        self.event_handler = event_handler

        # 現在のモード
        self.current_mode = None

        # ウィンドウの作成
        self.window = self._create_window()

        # 画像表示用の変数
        self.image_element = self.window['画像表示']
        self.displayed_image = None
        self.original_size = None

    def _create_window(self):
        """ウィンドウレイアウトの作成"""
        # メニューバー
        menu_def = [
            ['ファイル', ['開く', 'クリップボードから貼り付け', '---', '保存', 'コピー', '---', '終了']],
            ['編集', ['背景透過', 'モザイク', '塗りつぶし', 'トリミング', '---', '元に戻す']],
            ['変換', ['左回転', '右回転', '水平反転', '垂直反転']],
            ['ヘルプ', ['使い方', 'バージョン情報']]
        ]

        # 画像表示エリア
        image_area = [
            [sg.Image(key='画像表示', size=self.image_display_size, background_color='#F0F0F0', pad=(0, 0))]
        ]

        # 操作ボタンエリア
        buttons_row = [
            sg.Button('📁 開く', key='開く', size=(8, 1)),
            sg.Button('🧊 背景透過', key='背景透過', size=(10, 1)),
            sg.Button('🔲 モザイク', key='モザイク', size=(9, 1)),
            sg.Button('🟥 塗り', key='塗りつぶし', size=(7, 1)),
            sg.Button('✂️ トリム', key='トリム', size=(9, 1)),
            sg.Button('↩️ 回転', key='回転メニュー', size=(8, 1), button_color=('black', '#E0E0E0')),
            sg.Button('💾 保存', key='保存', size=(8, 1), button_color=('black', '#E0E0E0')),
            sg.Button('📋 コピー', key='コピー', size=(8, 1), button_color=('black', '#E0E0E0'))
        ]

        # モザイク・塗りつぶし・回転のオプションフレーム (最初は非表示)
        mosaic_options = [
            [sg.Text('強度:'), sg.Slider(range=(1, 50), default_value=10, orientation='h', size=(20, 15), key='モザイク強度')]
        ]

        paint_options = [
            [sg.Text('色:'), sg.ColorChooserButton('色を選択', key='色選択ボタン', target='色選択'), sg.Input('#FF0000', key='色選択', size=(8, 1))]
        ]

        rotation_options = [
            [sg.Button('左に90°', key='左回転'), sg.Button('右に90°', key='右回転'), sg.Button('左右反転', key='水平反転'), sg.Button('上下反転', key='垂直反転')]
        ]

        # オプションフレーム
        options_frame = [
            [sg.Frame('モザイクオプション', mosaic_options, key='モザイクオプション', visible=False, font='Default 10')],
            [sg.Frame('塗りつぶしオプション', paint_options, key='塗りつぶしオプション', visible=False, font='Default 10')],
            [sg.Frame('回転・反転', rotation_options, key='回転オプション', visible=False, font='Default 10')]
        ]

        # ステータスバー
        status_bar = [
            [sg.Text('準備完了', key='ステータス', size=(60, 1), justification='left', relief=sg.RELIEF_SUNKEN)]
        ]

        # 全体レイアウト
        layout = [
            [sg.Menu(menu_def)],
            [sg.Column(image_area, key='画像エリア', justification='center', element_justification='center')],
            [sg.HorizontalSeparator()],
            [sg.Column([buttons_row], justification='center', element_justification='center', pad=(0, 10))],
            [sg.Column(options_frame, key='オプションエリア', justification='center', element_justification='center', visible=True)],
            [sg.Column(status_bar, justification='left', element_justification='left')]
        ]

        # ウィンドウの作成
        window = sg.Window(
            'QuickSnap - クイック画像エディタ',
            layout,
            size=self.window_size,
            resizable=True,
            finalize=True,
            return_keyboard_events=True,
            icon=self._get_default_icon()
        )

        # 画像ドラッグ&ドロップを有効化
        window['画像表示'].bind('<Button-1>', '画像クリック')
        window['画像表示'].bind('<ButtonRelease-1>', '画像クリックリリース')
        window['画像表示'].bind('<B1-Motion>', '画像ドラッグ')

        # クリップボードショートカット (Ctrl+V)
        window.bind('<Control-v>', 'ペースト')

        return window

    def _get_default_icon(self):
        """デフォルトのアイコンデータを返す (64x64 PNG)"""
        # シンプルなアイコンを作成
        img = PIL.Image.new('RGBA', (64, 64), color=(240, 240, 240, 0))
        # TODO: もっとかっこいいアイコンに置き換える
        with io.BytesIO() as output:
            img.save(output, format="PNG")
            return output.getvalue()

    def run(self):
        """GUIイベントループの実行"""
        # 選択領域の追跡用変数
        start_pos = None

        while True:
            event, values = self.window.read(timeout=100)

            # イベントハンドラーにイベントを渡す
            if not self.event_handler(event, values):
                break

            # 画像の選択開始
            if event == '画像クリック' and self.displayed_image and self.current_mode in ['mosaic', 'paint', 'trim']:
                start_pos = values['画像クリック']
                # 選択開始イベントを送信
                self.event_handler('選択開始', {'選択開始': start_pos})

            # 画像のドラッグ中
            elif event == '画像ドラッグ' and start_pos and self.current_mode in ['mosaic', 'paint', 'trim']:
                # ドラッグ中の視覚的フィードバック（将来的に実装）
                pass

            # 画像の選択終了
            elif event == '画像クリックリリース' and start_pos and self.current_mode in ['mosaic', 'paint', 'trim']:
                end_pos = values['画像クリックリリース']
                # 選択終了イベントを送信
                self.event_handler('選択終了', {'選択終了': end_pos})
                start_pos = None

            # 回転メニューの表示/非表示
            elif event == '回転メニュー':
                visible = not self.window['回転オプション'].visible
                self.window['回転オプション'].update(visible=visible)

            # モザイク強度変更時
            elif event == 'モザイク強度' and self.current_mode == 'mosaic':
                self.event_handler('モザイク強度', {'モザイク強度': values['モザイク強度']})

            # 色選択
            elif event == '色選択ボタン' or (event == '色選択' and values['色選択'] != ''):
                self.event_handler('色選択', {'色選択': values['色選択']})

        self.window.close()

    def update_image(self, image):
        """
        表示画像の更新

        Args:
            image: PIL.Image オブジェクト
        """
        if image:
            self.displayed_image = image
            self.original_size = image.size

            # 画像をリサイズして表示
            display_image = self._resize_image_to_fit(image, self.image_display_size)
            photo_img = ImageTk.PhotoImage(display_image)

            self.image_element.update(data=photo_img)
            self.window['ステータス'].update(f'画像サイズ: {image.width}x{image.height} ピクセル')

    def update_mode(self, mode):
        """
        編集モードの更新と関連UIの表示/非表示

        Args:
            mode: 'mosaic', 'paint', 'trim' のいずれか
        """
        self.current_mode = mode

        # 各オプションパネルの表示/非表示を切り替え
        self.window['モザイクオプション'].update(visible=(mode == 'mosaic'))
        self.window['塗りつぶしオプション'].update(visible=(mode == 'paint'))
        self.window['回転オプション'].update(visible=False)

        # モードに応じたステータス表示
        mode_texts = {
            'mosaic': '範囲を選択してモザイクを適用します',
            'paint': '範囲を選択して色を塗ります',
            'trim': '範囲を選択してトリミングします'
        }
        self.window['ステータス'].update(mode_texts.get(mode, '準備完了'))

    def get_file_path(self):
        """ファイル選択ダイアログを表示し、選択されたパスを返す"""
        file_path = sg.popup_get_file(
            '画像ファイルを選択',
            file_types=(
                ('画像ファイル', '*.png;*.jpg;*.jpeg;*.bmp;*.gif'),
                ('すべてのファイル', '*.*')
            ),
            no_window=True
        )
        return file_path

    def get_save_path(self, initial_dir=''):
        """保存ダイアログを表示し、保存先パスを返す"""
        file_path = sg.popup_get_file(
            '画像を保存',
            save_as=True,
            file_types=(
                ('PNG画像', '*.png'),
                ('JPEG画像', '*.jpg'),
                ('BMP画像', '*.bmp'),
                ('GIF画像', '*.gif'),
                ('すべてのファイル', '*.*')
            ),
            default_extension='.png',
            default_path=initial_dir,
            no_window=True
        )
        return file_path

    def get_mosaic_strength(self):
        """モザイク強度の値を取得"""
        return self.window['モザイク強度'].get()

    def show_info(self, message):
        """情報メッセージを表示"""
        self.window['ステータス'].update(message)

    def show_error(self, message):
        """エラーメッセージをポップアップ表示"""
        sg.popup_error(message, title='エラー')

    def show_processing(self, message):
        """処理中表示の更新"""
        self.window['ステータス'].update(message)
        self.window.refresh()

    def hide_processing(self):
        """処理中表示の非表示"""
        self.window['ステータス'].update('処理完了')

    def _resize_image_to_fit(self, image, max_size):
        """
        画像をウィンドウサイズに合わせてリサイズ

        Args:
            image: PIL.Image オブジェクト
            max_size: 最大サイズ (width, height)

        Returns:
            リサイズされた PIL.Image オブジェクト
        """
        img_width, img_height = image.size
        max_width, max_height = max_size

        # アスペクト比を保持したままリサイズ
        scale = min(max_width / img_width, max_height / img_height)

        if scale < 1:  # リサイズが必要な場合のみ
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            return image.resize((new_width, new_height), PIL.Image.LANCZOS)
        else:
            return image