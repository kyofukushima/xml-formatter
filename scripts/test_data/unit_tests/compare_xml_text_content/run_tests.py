#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
compare_xml_text_content.py の単体テスト実行スクリプト
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
    original_file = test_dir / "input_original.xml"
    final_correct_file = test_dir / "input_final_correct.xml"
    final_incorrect_file = test_dir / "input_final_incorrect.xml"

    print(f"\n=== テスト実行: {test_name} ===")

    if not original_file.exists():
        print(f"❌ input_original.xml が見つかりません: {original_file}")
        return False

    script_dir = Path(__file__).parent.parent.parent.parent
    script_path = script_dir / "compare_xml_text_content.py"

    # テストケース1: 順序が正しい場合
    if final_correct_file.exists():
        print("\n--- テストケース1: 順序が正しい場合 ---")
        result = subprocess.run([
            sys.executable, str(script_path),
            str(original_file),
            str(final_correct_file)
        ], capture_output=True, text=True, timeout=60)

        if result.returncode == 0:
            print("✅ テスト成功: 順序が正しい場合に検証が成功しました")
        else:
            print("❌ テスト失敗: 順序が正しい場合に検証が失敗しました")
            print("STDOUT:", result.stdout[:500])
            print("STDERR:", result.stderr[:500])
            return False

    # テストケース2: 順序が間違っている場合
    if final_incorrect_file.exists():
        print("\n--- テストケース2: 順序が間違っている場合 ---")
        result = subprocess.run([
            sys.executable, str(script_path),
            str(original_file),
            str(final_incorrect_file)
        ], capture_output=True, text=True, timeout=60)

        if result.returncode != 0:
            print("✅ テスト成功: 順序が間違っている場合に検証が失敗しました（期待通り）")
            if "order mismatch" in result.stdout or "順序" in result.stdout:
                print("✅ 順序の違いが検知されました")
            else:
                print("⚠️ 順序の違いが検知されていません（改善が必要）")
        else:
            print("❌ テスト失敗: 順序が間違っている場合に検証が成功しました（問題あり）")
            print("STDOUT:", result.stdout[:500])
            return False

    return True

def main():
    """メイン関数"""
    test_root = Path(__file__).parent

    print("compare_xml_text_content.py 単体テスト実行")
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
