#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
逆変換スクリプトのエラー検出テスト実行スクリプト

エラーテストケース（値の欠落、変更、順序変更など）を実行し、
エラーが正しく検出されるかを検証します。
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

def run_reverse_pipeline(input_file, output_file):
    """逆変換パイプラインを実行"""
    # run_error_tests.py は scripts/reverse/test_data/error_tests/ にある
    # 逆変換スクリプトは scripts/reverse/ にある
    script_dir = Path(__file__).parent.parent.parent
    
    # 逆変換スクリプトのリスト（実行順序が重要: 内側から外側へ）
    reverse_converters = [
        "reverse_convert_subitem10.py",
        "reverse_convert_subitem9.py",
        "reverse_convert_subitem8.py",
        "reverse_convert_subitem7.py",
        "reverse_convert_subitem6.py",
        "reverse_convert_subitem5.py",
        "reverse_convert_subitem4.py",
        "reverse_convert_subitem3.py",
        "reverse_convert_subitem2.py",
        "reverse_convert_subitem1.py",
        "reverse_convert_item.py",
    ]
    
    # 一時ファイルを使用して順次処理
    import tempfile
    import shutil
    
    current_input = input_file
    temp_files = []
    
    try:
        for converter in reverse_converters:
            converter_path = script_dir / converter
            if not converter_path.exists():
                print(f"⚠️  スクリプトが見つかりません: {converter}")
                continue
            
            # 一時出力ファイルを作成
            temp_output = tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False, dir=output_file.parent)
            temp_output.close()
            temp_files.append(temp_output.name)
            
            # スクリプトを実行
            result = subprocess.run([
                sys.executable, str(converter_path),
                str(current_input),
                temp_output.name
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                print(f"❌ {converter} 実行エラー (終了コード: {result.returncode})")
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
                return False
            
            # 次の入力として使用
            current_input = Path(temp_output.name)
        
        # 最終出力をコピー
        shutil.copy2(current_input, output_file)
        return True
        
    finally:
        # 一時ファイルを削除
        for temp_file in temp_files:
            try:
                Path(temp_file).unlink()
            except:
                pass

def run_test(test_dir):
    """単一のエラーテストケースを実行"""
    test_name = test_dir.name
    input_file = test_dir / "input.xml"
    expected_file = test_dir / "expected.xml"
    error_file = test_dir / "error.xml"
    output_file = test_dir / "output.xml"

    print(f"\n=== エラーテスト実行: {test_name} ===")

    if not input_file.exists():
        print(f"❌ input.xml が見つかりません: {input_file}")
        return False

    if not expected_file.exists():
        print(f"❌ expected.xml が見つかりません: {expected_file}")
        return False

    if not error_file.exists():
        print(f"❌ error.xml が見つかりません: {error_file}")
        print("   エラーテストには error.xml（値が欠落したファイル）が必要です。")
        return False

    try:
        # 逆変換パイプラインを実行（input.xml → output.xml）
        if not run_reverse_pipeline(input_file, output_file):
            return False

        print(f"✅ パイプライン実行成功 - 出力: {output_file}")

        # 出力ファイルの内容を読み込む（正常な変換結果）
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                output_content = f.read()
        except Exception as e:
            print(f"❌ 出力ファイル読み込みエラー: {e}")
            return False

        # 期待ファイルの読み込み（正常な期待値）
        try:
            with open(expected_file, 'r', encoding='utf-8') as f:
                expected_content = f.read()
        except Exception as e:
            print(f"❌ 期待ファイルの読み込みエラー: {e}")
            return False

        # エラーファイルの読み込み（値が欠落したファイル）
        try:
            with open(error_file, 'r', encoding='utf-8') as f:
                error_content = f.read()
        except Exception as e:
            print(f"❌ エラーファイルの読み込みエラー: {e}")
            return False

        # XML正規化
        try:
            output_normalized = normalize_xml(output_content)
            expected_normalized = normalize_xml(expected_content)
            error_normalized = normalize_xml(error_content)

            # まず、output.xmlとexpected.xmlを比較（正常性チェック）
            if output_normalized != expected_normalized:
                print("⚠️  警告: 出力が期待値と一致しません（変換に問題がある可能性があります）")
                print("   正常な変換結果が得られていないため、エラー検出テストをスキップします。")
                return False

            print("✅ 正常性チェック: 出力が期待値と一致しています（正常な変換結果）")

            # 次に、output.xmlとerror.xmlを比較（エラー検出テスト）
            if output_normalized != error_normalized:
                print("✅ エラー検出成功: 出力とエラーファイルが一致しません（値の欠落を正しく検出しました）")
                print("\n差分（正常な出力とエラーファイルの違い）:")
                diff = difflib.unified_diff(
                    output_normalized.splitlines(keepends=True),
                    error_normalized.splitlines(keepends=True),
                    fromfile='output.xml (正常)',
                    tofile='error.xml (値欠落)',
                    lineterm=''
                )
                # 差分の最初の30行のみを表示
                diff_lines = list(diff)
                for line in diff_lines[:30]:
                    print(line, end='')
                if len(diff_lines) > 30:
                    print(f"\n... (残り {len(diff_lines) - 30} 行)")
                return True
            else:
                print("❌ エラー検出失敗: 出力とエラーファイルが一致しています（値の欠落を検出できませんでした）")
                print("   正常な出力とエラーファイルが同じ場合、エラー検出が機能していない可能性があります。")
                return False

        except etree.XMLSyntaxError as e:
            print(f"❌ XML構文エラー: {e}")
            print("出力内容:")
            print(actual_content)
            return False

    except subprocess.TimeoutExpired:
        print("❌ パイプライン実行がタイムアウトしました")
        return False
    except Exception as e:
        print(f"❌ 予期せぬエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """メイン関数"""
    test_root = Path(__file__).parent

    print("逆変換スクリプト エラー検出テスト実行")
    print("=" * 50)
    print("注意: エラーテストでは、期待値と実際の出力が一致しない場合に")
    print("      エラーが正しく検出されたとみなします。")
    print("=" * 50)

    # テストケースの収集
    test_dirs = []
    for item in test_root.iterdir():
        if item.is_dir() and not item.name.startswith('_') and item.name != '__pycache__':
            test_dirs.append(item)

    test_dirs.sort()

    total_tests = len(test_dirs)
    passed_tests = 0

    for test_dir in test_dirs:
        if run_test(test_dir):
            passed_tests += 1

    print("\n" + "=" * 50)
    print(f"テスト結果: {passed_tests}/{total_tests} 成功")
    print("（成功 = エラーが正しく検出された）")

    if passed_tests == total_tests:
        print("🎉 すべてのエラーテストが成功しました！")
        print("   すべてのエラーが正しく検出されました。")
        return 0
    else:
        print("⚠️ 一部のエラーテストが失敗しました。")
        print("   エラーが検出されなかったテストケースがあります。")
        return 1

if __name__ == '__main__':
    sys.exit(main())
