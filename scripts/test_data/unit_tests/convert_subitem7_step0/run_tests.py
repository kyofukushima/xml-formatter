#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
convert_subitem7_step0.py の単体テスト実行スクリプト
"""

import sys
import os
import subprocess
import difflib
import json
import shutil
from pathlib import Path
from lxml import etree

def normalize_xml(xml_content):
    """XMLを正規化して比較しやすくする"""
    # XML宣言を除去
    if xml_content.startswith('<?xml'):
        xml_content = xml_content.split('?>', 1)[1].strip()

    root = etree.fromstring(xml_content)
    return etree.tostring(root, encoding='unicode', pretty_print=True)

def enable_split_mode_for_test(test_name):
    """並列分割モードのテストケースの場合、設定を有効化"""
    # image_list_split_mode を必要とするテストケース
    image_split_tests = ['31_image_list_split_mode_basic',
                         '32_image_list_split_mode_formula_variables']

    if test_name not in image_split_tests:
        return None, None

    # 設定ファイルのパス
    script_dir = Path(__file__).parent.parent.parent.parent
    config_path = script_dir / "config" / "label_config.json"
    backup_path = config_path.with_suffix('.json.backup')

    try:
        # 設定ファイルを読み込む
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # バックアップを作成
        shutil.copy2(config_path, backup_path)

        # 設定を有効化
        if 'conversion_behaviors' in config:
            if 'image_list_split_mode' in config['conversion_behaviors']:
                config['conversion_behaviors']['image_list_split_mode']['enabled'] = True
            if 'no_column_text_split_mode' in config['conversion_behaviors']:
                config['conversion_behaviors']['no_column_text_split_mode']['enabled'] = True

        # 設定ファイルを書き込む
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        return config_path, backup_path
    except Exception as e:
        print(f"⚠️ 設定ファイルの変更に失敗しました: {e}")
        return None, None

def restore_config(config_path, backup_path):
    """設定ファイルを元に戻す"""
    if config_path is None or backup_path is None:
        return

    try:
        if backup_path.exists():
            shutil.copy2(backup_path, config_path)
            backup_path.unlink()
    except Exception as e:
        print(f"⚠️ 設定ファイルの復元に失敗しました: {e}")

def run_test(test_dir):
    """単一のテストケースを実行"""
    test_name = test_dir.name
    input_file = test_dir / "input.xml"
    expected_file = test_dir / "expected.xml"

    print(f"\n=== テスト実行: {test_name} ===")

    if not input_file.exists():
        print(f"❌ input.xml が見つかりません: {input_file}")
        return False

    if not expected_file.exists():
        print(f"❌ expected.xml が見つかりません: {expected_file}")
        return False

    # 並列分割モードのテストケースの場合、設定を有効化
    config_path, backup_path = enable_split_mode_for_test(test_name)

    # convert_subitem7_step0.py を実行（出力を標準出力にリダイレクト）
    # スクリプトのパスを現在のワークスペースに合わせて設定
    script_dir = Path(__file__).parent.parent.parent.parent
    script_path = script_dir / "convert_subitem7_step0.py"

    try:
        # テストディレクトリ内にoutput.xmlを作成
        output_file = test_dir / "output.xml"

        result = subprocess.run([
            sys.executable, str(script_path),
            str(input_file),
            str(output_file)
        ], capture_output=True, text=True, timeout=30)

        if result.returncode != 0:
            print(f"❌ スクリプト実行エラー (終了コード: {result.returncode})")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False

        print(f"✅ スクリプト実行成功 - 出力: {output_file}")

        # 出力ファイルの内容を読み込む
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                actual_content = f.read()
        except Exception as e:
            print(f"❌ 出力ファイル読み込みエラー: {e}")
            return False

        # 期待ファイルの読み込み
        try:
            with open(expected_file, 'r', encoding='utf-8') as f:
                expected_content = f.read()
        except Exception as e:
            print(f"❌ 期待ファイルの読み込みエラー: {e}")
            return False

        # XML正規化
        try:
            actual_normalized = normalize_xml(actual_content)
            expected_normalized = normalize_xml(expected_content)

            if actual_normalized == expected_normalized:
                print("✅ テスト成功: 出力が期待値と一致します")
                return True
            else:
                print("❌ テスト失敗: 出力が期待値と一致しません")
                print("\n差分:")
                diff = difflib.unified_diff(
                    expected_normalized.splitlines(keepends=True),
                    actual_normalized.splitlines(keepends=True),
                    fromfile='expected.xml',
                    tofile='output.xml'
                )
                print(''.join(diff))
                return False

        except etree.XMLSyntaxError as e:
            print(f"❌ XML構文エラー: {e}")
            print("出力内容:")
            print(actual_content)
            return False

    except subprocess.TimeoutExpired:
        print("❌ スクリプト実行がタイムアウトしました")
        return False
    except Exception as e:
        print(f"❌ 予期せぬエラー: {e}")
        return False
    finally:
        # 設定ファイルを元に戻す（成功時も失敗時も必ず実行）
        restore_config(config_path, backup_path)

def main():
    """メイン関数"""
    test_root = Path(__file__).parent

    print("convert_subitem7_step0.py 単体テスト実行")
    print("=" * 50)

    # テストケースの収集
    test_dirs = []
    for item in test_root.iterdir():
        if item.is_dir() and item.name.startswith(('01_', '27_', '28_', '29_', '02_', '03_', '04_', '05_', '06_', '07_', '08_', '09_', '10_', '11_', '12_', '13_', '14_', '15_','16_','17_','18_','19_','20_','21_','22_','23_','24_','25_', '26_', '26_', '31_', '32_')):
            test_dirs.append(item)

    test_dirs.sort()

    total_tests = len(test_dirs)
    passed_tests = 0

    for test_dir in test_dirs:
        if run_test(test_dir):
            passed_tests += 1

    print("\n" + "=" * 50)
    print(f"テスト結果: {passed_tests}/{total_tests} 成功")

    if passed_tests == total_tests:
        print("🎉 すべてのテストが成功しました！")
        return 0
    else:
        print("⚠️ 一部のテストが失敗しました。")
        return 1

if __name__ == '__main__':
    sys.exit(main())
