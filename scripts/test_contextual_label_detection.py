#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文脈依存のラベル判定テストスクリプト
"""

import sys
from pathlib import Path

# 親ディレクトリをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from utils.label_utils import (
    detect_label_id,
    is_roman_numeral,
    get_exclude_label_ids_for_context
)

def test_contextual_detection():
    """文脈依存のラベル判定をテスト"""
    
    print("=" * 80)
    print("文脈依存のラベル判定テスト")
    print("=" * 80)
    print()
    
    # テストケース: (最初の要素のラベル, 判定するラベル, 期待されるラベルID)
    test_cases = [
        # 最初がローマ数字パターンの場合: ローマ数字として扱う
        ("（i）", "（c）", "paren_roman", "ローマ数字"),
        ("（i）", "（ii）", "paren_roman", "ローマ数字"),
        ("（i）", "（iii）", "paren_roman", "ローマ数字"),
        ("（ｉ）", "（ｃ）", "paren_roman", "ローマ数字"),
        ("（ｉ）", "（ｉｉ）", "paren_roman", "ローマ数字"),
        ("（ｉ）", "（ｉｉｉ）", "paren_roman", "ローマ数字"),
        ("（ii）", "（c）", "paren_roman", "ローマ数字（最初がii）"),
        ("（ｉｉ）", "（ｃ）", "paren_roman", "ローマ数字（最初がｉｉ）"),
        ("（iii）", "（c）", "paren_roman", "ローマ数字（最初がiii）"),
        ("（ｉｉｉ）", "（ｃ）", "paren_roman", "ローマ数字（最初がｉｉｉ）"),
        ("（iv）", "（c）", "paren_roman", "ローマ数字（最初がiv）"),
        ("（ｖ）", "（ｃ）", "paren_roman", "ローマ数字（最初がｖ）"),
        
        # 最初が（a）の場合: アルファベットとして扱う（ローマ数字を除外）
        ("（a）", "（c）", "paren_lowercase_alphabet", "小文字アルファベット"),
        ("（a）", "（b）", "paren_lowercase_alphabet", "小文字アルファベット"),
        ("（a）", "（d）", "paren_lowercase_alphabet", "小文字アルファベット"),
        ("（ａ）", "（ｃ）", "paren_fullwidth_lowercase_alphabet", "全角小文字アルファベット"),
        ("（ａ）", "（ｂ）", "paren_fullwidth_lowercase_alphabet", "全角小文字アルファベット"),
        ("（ａ）", "（ｄ）", "paren_fullwidth_lowercase_alphabet", "全角小文字アルファベット"),
        
        # 最初が（A）の場合: アルファベットとして扱う（ローマ数字を除外）
        ("（A）", "（C）", "paren_uppercase_alphabet", "大文字アルファベット"),
        ("（Ａ）", "（Ｃ）", "paren_fullwidth_uppercase_alphabet", "全角大文字アルファベット"),
        
        # その他のケース
        ("（１）", "（c）", "paren_lowercase_alphabet", "小文字アルファベット（数字から始まる場合）"),
        ("（ア）", "（c）", "paren_lowercase_alphabet", "小文字アルファベット（カタカナから始まる場合）"),
        (None, "（c）", "paren_lowercase_alphabet", "小文字アルファベット（最初の要素なし）"),
    ]
    
    all_passed = True
    
    for first_label, test_label, expected_label_id, description in test_cases:
        # 除外リストを生成
        exclude_label_ids = get_exclude_label_ids_for_context(first_label)
        
        # ラベルを判定
        detected_label_id = detect_label_id(test_label, exclude_label_ids)
        
        # 結果を確認
        is_correct = detected_label_id == expected_label_id
        if not is_correct:
            all_passed = False
        
        status = "✓" if is_correct else "✗"
        
        print(f"{status} 最初の要素: '{first_label}' → 判定対象: '{test_label}'")
        print(f"    説明: {description}")
        print(f"    期待: {expected_label_id}")
        print(f"    実際: {detected_label_id}")
        print(f"    除外リスト: {exclude_label_ids}")
        
        if not is_correct:
            print(f"    ⚠️  不一致！")
        print()
    
    print("=" * 80)
    print("\n【重要な判別の確認】")
    print("-" * 80)
    
    # 特に重要なケースを再確認
    critical_cases = [
        ("（i）", "（c）", "paren_roman", "ローマ数字"),
        ("（ｉ）", "（ｃ）", "paren_roman", "ローマ数字（全角）"),
        ("（ii）", "（c）", "paren_roman", "ローマ数字（最初がii）"),
        ("（ａ）", "（ｃ）", "paren_fullwidth_lowercase_alphabet", "全角小文字アルファベット"),
        ("（a）", "（c）", "paren_lowercase_alphabet", "小文字アルファベット"),
    ]
    
    for first_label, test_label, expected_label_id, test_name in critical_cases:
        exclude_label_ids = get_exclude_label_ids_for_context(first_label)
        detected_label_id = detect_label_id(test_label, exclude_label_ids)
        status = "✓" if detected_label_id == expected_label_id else "✗"
        print(f"{status} '{test_label}' ({test_name})")
        print(f"    最初の要素: '{first_label}'")
        print(f"    → {detected_label_id} (期待: {expected_label_id})")
        if detected_label_id != expected_label_id:
            print(f"    ⚠️  不一致！")
    
    print("\n" + "=" * 80)
    if all_passed:
        print("\n✓ すべてのテストケースが正しく判別されました！")
    else:
        print("\n✗ 一部のテストケースで判別に問題があります。")
    print("=" * 80)

if __name__ == "__main__":
    test_contextual_detection()

