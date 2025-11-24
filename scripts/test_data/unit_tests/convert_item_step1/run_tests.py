#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
convert_item_step1.py の単体テスト実行スクリプト
"""

import sys
import os
import subprocess
import difflib
from pathlib import Path
from lxml import etree

def normalize_xml(xml_content):
    """XMLを正規化して比較しやすくする"""
    # XML宣言を除去
    if xml_content.startswith('<?xml'):
        xml_content = xml_content.split('?>', 1)[1].strip()

    root = etree.fromstring(xml_content)
    return etree.tostring(root, encoding='unicode', pretty_print=True)

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

    # convert_item_step1.py を実行（出力を標準出力にリダイレクト）
    script_path = Path("/Users/fukushima/Documents/xml_anken/education_xml/scripts/convert_item_step1.py")

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

def main():
    """メイン関数"""
    test_root = Path(__file__).parent

    print("convert_item_step1.py 単体テスト実行")
    print("=" * 50)

    # テストケースの収集
    test_dirs = []
    for item in test_root.iterdir():
        if item.is_dir() and item.name.startswith(('01_', '02_', '03_', '04_', '05_', '06_', '07_', '08_')):
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
