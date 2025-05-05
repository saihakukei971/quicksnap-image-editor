#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QuickSnap - セットアップスクリプト
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def setup_environment():
    """環境のセットアップ"""
    print("QuickSnap - セットアップを開始します...")

    # 必要なディレクトリの作成
    create_directories()

    # 依存関係のインストール
    install_dependencies()

    print("\nセットアップが完了しました！")
    print("QuickSnapを起動するには以下のコマンドを実行してください:")
    print("python main.py")

def create_directories():
    """必要なディレクトリ構造を作成"""
    directories = [
        "tools",
        "ui"
    ]

    root_dir = Path(__file__).parent

    for directory in directories:
        dir_path = root_dir / directory
        if not dir_path.exists():
            print(f"ディレクトリを作成: {directory}")
            dir_path.mkdir(parents=True)
        else:
            print(f"ディレクトリは既に存在: {directory}")

def install_dependencies():
    """必要なパッケージをインストール"""
    print("\n依存パッケージをインストールしています...")

    requirements_file = Path(__file__).parent / "requirements.txt"

    if not requirements_file.exists():
        print("エラー: requirements.txtが見つかりません")
        return False

    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)])
        print("依存パッケージのインストールが完了しました")
        return True
    except subprocess.CalledProcessError as e:
        print(f"エラー: パッケージのインストール中に問題が発生しました: {e}")
        return False

def check_python_version():
    """Pythonバージョンの確認"""
    major, minor, _ = sys.version_info[:3]
    if major < 3 or (major == 3 and minor < 8):
        print(f"警告: QuickSnapはPython 3.8以上が必要です。現在のバージョン: {platform.python_version()}")
        return False
    return True

if __name__ == "__main__":
    if check_python_version():
        setup_environment()
    else:
        print("Python 3.8以上をインストールしてから再度実行してください。")
        sys.exit(1)