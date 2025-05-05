#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QuickSnap - EXE作成スクリプト
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
import platform

def build_executable():
    """PyInstallerを使用してexeファイルを作成"""
    print("QuickSnap - EXEファイルを作成します...")
    
    # PyInstallerがインストールされているか確認
    try:
        import PyInstaller
    except ImportError:
        print("PyInstallerがインストールされていません。インストールします...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("PyInstallerのインストールが完了しました")
        except subprocess.CalledProcessError as e:
            print(f"エラー: PyInstallerのインストール中に問題が発生しました: {e}")
            return False
    
    root_dir = Path(__file__).parent
    dist_dir = root_dir / "dist"
    build_dir = root_dir / "build"
    
    # 既存のビルドディレクトリをクリア
    if dist_dir.exists():
        print("既存のdistディレクトリを削除します...")
        shutil.rmtree(dist_dir)
    if build_dir.exists():
        print("既存のbuildディレクトリを削除します...")
        shutil.rmtree(build_dir)
    
    # アイコンファイルの存在確認
    icon_file = root_dir / "icon.ico"
    icon_param = f"--icon={icon_file}" if icon_file.exists() else ""
    
    # PyInstallerコマンドを構築
    command = [
        sys.executable, "-m", "PyInstaller",
        "--name=QuickSnap",
        "--onefile",
        "--noconsole",
        "--clean",
        f"--add-data=ui{os.pathsep}ui",
        f"--add-data=tools{os.pathsep}tools",
    ]
    
    # アイコンがある場合は追加
    if icon_param:
        command.append(icon_param)
    
    # main.pyを追加
    command.append("main.py")
    
    print(f"実行コマンド: {' '.join(command)}")
    
    try:
        subprocess.check_call(command)
        print("\nEXEファイルの作成が完了しました!")
        exe_path = dist_dir / "QuickSnap.exe"
        if exe_path.exists():
            print(f"作成されたEXEファイル: {exe_path}")
            return True
        else:
            print("エラー: EXEファイルが見つかりません")
            return False
    except subprocess.CalledProcessError as e:
        print(f"エラー: EXEファイルの作成中に問題が発生しました: {e}")
        return False

def create_distribution_package():
    """配布用パッケージを作成"""
    root_dir = Path(__file__).parent
    dist_dir = root_dir / "dist"
    package_dir = root_dir / "QuickSnap_配布用"
    
    # 配布用ディレクトリを作成
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir()
    
    # EXEファイルをコピー
    exe_file = dist_dir / "QuickSnap.exe"
    if exe_file.exists():
        shutil.copy2(exe_file, package_dir)
    else:
        print("エラー: EXEファイルが見つかりません")
        return False
    
    # READMEをコピー
    readme_file = root_dir / "README.md"
    if readme_file.exists():
        shutil.copy2(readme_file, package_dir)
    
    # アイコンファイルをコピー
    icon_file = root_dir / "icon.ico"
    if icon_file.exists():
        shutil.copy2(icon_file, package_dir)
    
    print(f"\n配布用パッケージを作成しました: {package_dir}")
    print("以下のファイルが含まれています:")
    for file in package_dir.iterdir():
        print(f" - {file.name}")
    
    return True

if __name__ == "__main__":
    if platform.system() != "Windows":
        print("このスクリプトはWindows環境でのみ動作します")
        sys.exit(1)
    
    if build_executable():
        create_distribution_package()
    else:
        print("EXEファイルの作成に失敗しました")
        sys.exit(1)