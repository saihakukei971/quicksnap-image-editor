#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QuickSnap - フォルダ初期化スクリプト
"""

import os
import sys
from pathlib import Path

def create_folder_structure():
    """必要なフォルダ構造を作成する"""
    root_dir = Path(__file__).parent
    
    # 作成するディレクトリのリスト
    directories = [
        root_dir / "tools",
        root_dir / "ui"
    ]
    
    # 各ディレクトリを作成
    for directory in directories:
        if not directory.exists():
            print(f"ディレクトリを作成: {directory}")
            directory.mkdir(parents=True, exist_ok=True)
            
            # 空の__init__.pyファイルを作成してパッケージとして認識させる
            init_file = directory / "__init__.py"
            if not init_file.exists():
                with open(init_file, 'w', encoding='utf-8') as f:
                    f.write('# -*- coding: utf-8 -*-\n')
        else:
            print(f"ディレクトリは既に存在: {directory}")

if __name__ == "__main__":
    print("QuickSnap - フォルダ構造を初期化します...")
    create_folder_structure()
    print("完了しました。")