#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LineBreak付きColumn保護（--preserve-linebreak-list）の単体テスト実行スクリプト

convert_item_step0.py を対象に、列記保護判定の動作を検証する。

各テストケースディレクトリの構成:
  input.xml    - 入力XML
  expected.xml - 期待される出力XML
  args.txt     - (オプション) スクリプトへの追加引数（例: --preserve-enumeration）
                 ファイルがない場合はフラグなし（従来動作）で実行される
"""

import sys
import subprocess
import difflib
import tempfile
import os
from pathlib import Path
from lxml import etree


def normalize_xml(xml_content):
    """XMLを正規化して比較しやすくする"""
    # XML宣言を除去
    if xml_content.startswith('<?xml'):
        xml_content = xml_content.split('?>', 1)[1].strip()

    root = etree.fromstring(xml_content.encode('utf-8'))
    return etree.tostring(root, encoding='unicode', pretty_print=True)


def run_test(test_dir):
    """単一のテストケースを実行"""
    test_name = test_dir.name
    input_file = test_dir / "input.xml"
    expected_file = test_dir / "expected.xml"
    args_file = test_dir / "args.txt"

    print(f"\n=== テスト実行: {test_name} ===")

    if not input_file.exists():
        print(f"❌ input.xml が見つかりません: {input_file}")
        return False

    if not expected_file.exists():
        print(f"❌ expected.xml が見つかりません: {expected_file}")
        return False

    # 追加引数の読み込み
    extra_args = []
    if args_file.exists():
        extra_args = args_file.read_text(encoding='utf-8').split()
        print(f"追加引数: {' '.join(extra_args)}")

    # convert_item_step0.py を実行
    script_path = Path(__file__).parent.parent.parent.parent / "convert_item_step0.py"

    try:
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.xml', delete=False) as temp_file:
            temp_output_path = temp_file.name

        result = subprocess.run([
            sys.executable, str(script_path),
            str(input_file),
            temp_output_path
        ] + extra_args, capture_output=True, text=True, timeout=60)

        if result.returncode != 0:
            print(f"❌ スクリプト実行エラー (終了コード: {result.returncode})")
            print("STDOUT:", result.stdout[:500])
            print("STDERR:", result.stderr[:500])
            return False

        print("✅ スクリプト実行成功")

        try:
            with open(temp_output_path, 'r', encoding='utf-8') as f:
                actual_content = f.read()
        except Exception as e:
            print(f"❌ 一時ファイル読み込みエラー: {e}")
            return False
        finally:
            try:
                os.unlink(temp_output_path)
            except OSError:
                pass

        try:
            with open(expected_file, 'r', encoding='utf-8') as f:
                expected_content = f.read()
        except Exception as e:
            print(f"❌ 期待ファイルの読み込みエラー: {e}")
            return False

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

    print("LineBreak付きColumn保護（--preserve-linebreak-list）単体テスト実行")
    print("=" * 50)

    test_dirs = sorted(
        item for item in test_root.iterdir()
        if item.is_dir() and item.name[:2].isdigit()
    )

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
