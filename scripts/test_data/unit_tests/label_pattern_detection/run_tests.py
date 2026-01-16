#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
label_pattern_detection の単体テスト実行スクリプト

List要素をItem、Subitem1、Subitem2などに変換する処理をテストします。
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

    # コメントノードを除去
    for comment in root.xpath('//comment()'):
        comment.getparent().remove(comment)

    # 空のテキストノードを除去（インデントや改行のみのノード）
    for element in root.iter():
        if element.text and element.text.strip() == '':
            element.text = None
        if element.tail and element.tail.strip() == '':
            element.tail = None

    # 空の要素を除去（タイトルやセンテンスが空の場合）
    for element in root.iter():
        if element.tag in ['ItemTitle', 'ItemSentence', 'Subitem1Title', 'Subitem1Sentence', 'Subitem2Title', 'Subitem2Sentence']:
            # 子要素がない場合や空のテキストの場合
            has_content = False
            if element.text and element.text.strip():
                has_content = True
            if len(element) > 0:
                # Sentence要素がある場合
                for child in element:
                    if child.tag == 'Sentence' and child.text and child.text.strip():
                        has_content = True
                        break

            if not has_content:
                element.getparent().remove(element)

    return etree.tostring(root, encoding='unicode', pretty_print=True)

def run_conversion_pipeline(input_file, output_file):
    """
    変換パイプラインを実行
    List -> Item -> Subitem1 -> Subitem2 の順に変換
    """
    scripts_dir = Path(__file__).resolve().parent.parent.parent.parent
    temp_files = []
    
    try:
        # Step 1: List -> Item (convert_item_step0.py)
        temp_item = Path(output_file).parent / f"temp_item_{Path(output_file).stem}.xml"
        temp_files.append(temp_item)
        
        script_item = scripts_dir / "convert_item_step0.py"
        if not script_item.exists():
            print(f"❌ スクリプトが見つかりません: {script_item}")
            return False
        
        result = subprocess.run([
            sys.executable, str(script_item),
            str(input_file),
            str(temp_item)
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            print(f"❌ convert_item_step0.py 実行エラー (終了コード: {result.returncode})")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
        
        # Step 2: Item内のList -> Subitem1 (convert_subitem1_step0.py)
        temp_subitem1 = Path(output_file).parent / f"temp_subitem1_{Path(output_file).stem}.xml"
        temp_files.append(temp_subitem1)
        
        script_subitem1 = scripts_dir / "convert_subitem1_step0.py"
        if not script_subitem1.exists():
            print(f"❌ スクリプトが見つかりません: {script_subitem1}")
            return False
        
        result = subprocess.run([
            sys.executable, str(script_subitem1),
            str(temp_item),
            str(temp_subitem1)
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            print(f"❌ convert_subitem1_step0.py 実行エラー (終了コード: {result.returncode})")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
        
        # Step 3: Subitem1内のList -> Subitem2 (convert_subitem2_step0.py)
        script_subitem2 = scripts_dir / "convert_subitem2_step0.py"
        if not script_subitem2.exists():
            print(f"❌ スクリプトが見つかりません: {script_subitem2}")
            return False
        
        result = subprocess.run([
            sys.executable, str(script_subitem2),
            str(temp_subitem1),
            str(output_file)
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            print(f"❌ convert_subitem2_step0.py 実行エラー (終了コード: {result.returncode})")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
        
        return True
        
    finally:
        # 一時ファイルを削除
        for temp_file in temp_files:
            if temp_file.exists():
                try:
                    temp_file.unlink()
                except Exception as e:
                    print(f"⚠️ 一時ファイル削除エラー: {temp_file} - {e}")

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

    # テストディレクトリ内にoutput.xmlを作成
    output_file = test_dir / "output.xml"

    # 変換パイプラインを実行
    if not run_conversion_pipeline(input_file, output_file):
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
                tofile='output.xml',
                lineterm=''
            )
            print(''.join(diff))
            return False

    except etree.XMLSyntaxError as e:
        print(f"❌ XML構文エラー: {e}")
        print("出力内容:")
        print(actual_content)
        return False

def main():
    """メイン関数"""
    test_root = Path(__file__).parent

    print("label_pattern_detection 単体テスト実行")
    print("=" * 50)

    # テストケースの収集
    test_dirs = []
    for item in test_root.iterdir():
        if item.is_dir() and item.name.startswith(('01_', '02_', '03_', '04_', '05_', '06_', '07_', '08_', '09_', '10_', '11_', '12_', '13_')):
            test_dirs.append(item)

    test_dirs.sort()

    total_tests = len(test_dirs)
    passed_tests = 0
    failed_tests = []

    for test_dir in test_dirs:
        if run_test(test_dir):
            passed_tests += 1
        else:
            failed_tests.append(test_dir.name)

    print("\n" + "=" * 50)
    print(f"テスト結果: {passed_tests}/{total_tests} 成功")

    if passed_tests == total_tests:
        print("🎉 すべてのテストが成功しました！")
        return 0
    else:
        print("⚠️ 一部のテストが失敗しました。")
        if failed_tests:
            print(f"失敗したテスト: {', '.join(failed_tests)}")
        return 1

if __name__ == '__main__':
    sys.exit(main())

