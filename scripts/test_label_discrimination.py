#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
括弧付きローマ数字、科目名、括弧付きアルファベットの判別を確認するスクリプト
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple

def load_config(config_path: Path) -> Dict:
    """設定ファイルを読み込む"""
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def detect_label_id(text: str, config: Dict) -> Tuple[str, str, str]:
    """テキストからラベルIDを判定し、詳細情報を返す"""
    pattern_priority = config.get('pattern_priority', [])
    label_definitions = config.get('label_definitions', {})
    
    text = text.strip()
    
    for label_id in pattern_priority:
        if label_id not in label_definitions:
            continue
        definition = label_definitions[label_id]
        patterns = definition.get('patterns', [])
        
        for pattern_str in patterns:
            try:
                pattern = re.compile(pattern_str)
                if pattern.match(text):
                    return (
                        label_id,
                        definition.get('name', ''),
                        pattern_str
                    )
            except re.error:
                pass
    
    return ("unknown", "不明", "")

def main():
    script_dir = Path(__file__).parent
    config_path = script_dir / "config" / "label_config.json"
    
    config = load_config(config_path)
    
    # テストケース
    test_cases = [
        # 括弧付きローマ数字
        ("（ｉ）", "paren_roman", "括弧付きローマ数字"),
        ("（ｉｉ）", "paren_roman", "括弧付きローマ数字"),
        ("（ｉｉｉ）", "paren_roman", "括弧付きローマ数字"),
        ("(i)", "paren_roman", "括弧付きローマ数字"),
        ("(ii)", "paren_roman", "括弧付きローマ数字"),
        ("(iii)", "paren_roman", "括弧付きローマ数字"),
        
        # 括弧付きアルファベット（小文字）
        ("（a）", "paren_lowercase_alphabet", "括弧付き小文字アルファベット"),
        ("（b）", "paren_lowercase_alphabet", "括弧付き小文字アルファベット"),
        ("（c）", "paren_lowercase_alphabet", "括弧付き小文字アルファベット"),
        ("(a)", "paren_lowercase_alphabet", "括弧付き小文字アルファベット"),
        ("(b)", "paren_lowercase_alphabet", "括弧付き小文字アルファベット"),
        ("(c)", "paren_lowercase_alphabet", "括弧付き小文字アルファベット"),
        
        # 括弧付きアルファベット（全角小文字）
        ("（ａ）", "paren_fullwidth_lowercase_alphabet", "括弧付き全角小文字アルファベット"),
        ("（ｂ）", "paren_fullwidth_lowercase_alphabet", "括弧付き全角小文字アルファベット"),
        ("（ｃ）", "paren_fullwidth_lowercase_alphabet", "括弧付き全角小文字アルファベット"),
        
        # 科目名
        ("（科目名）", "subject_label", "括弧科目名"),
        ("（医療と社会）", "subject_label", "括弧科目名"),
        ("〔医療と社会〕", "subject_label", "括弧科目名"),
        ("【医療と社会】", "subject_label", "括弧科目名"),
        ("［善悪の判断，自律，自由と責任］", "subject_label", "括弧科目名"),
        
        # その他の括弧パターン（比較用）
        ("（１）", "paren_fullwidth_number", "括弧全角数字"),
        ("（ア）", "paren_katakana", "括弧カタカナ"),
    ]
    
    print("=" * 80)
    print("括弧付きローマ数字・科目名・括弧付きアルファベットの判別確認")
    print("=" * 80)
    print()
    
    results = []
    all_correct = True
    
    for test_text, expected_label_id, description in test_cases:
        label_id, label_name, pattern = detect_label_id(test_text, config)
        is_correct = label_id == expected_label_id
        if not is_correct:
            all_correct = False
        
        status = "✓" if is_correct else "✗"
        results.append({
            'text': test_text,
            'expected': expected_label_id,
            'actual': label_id,
            'name': label_name,
            'pattern': pattern,
            'description': description,
            'correct': is_correct
        })
        
        print(f"{status} '{test_text}'")
        print(f"    期待: {expected_label_id} ({description})")
        print(f"    実際: {label_id} ({label_name})")
        if not is_correct:
            print(f"    ⚠️  不一致！")
        print()
    
    print("=" * 80)
    print("\n【判別結果のまとめ】")
    print("-" * 80)
    
    # カテゴリ別に集計
    categories = {
        "括弧付きローマ数字": [],
        "括弧付き小文字アルファベット": [],
        "括弧付き全角小文字アルファベット": [],
        "括弧科目名": [],
        "その他": []
    }
    
    for result in results:
        desc = result['description']
        if desc in categories:
            categories[desc].append(result)
        else:
            categories["その他"].append(result)
    
    for category, items in categories.items():
        if not items:
            continue
        correct_count = sum(1 for item in items if item['correct'])
        total_count = len(items)
        print(f"\n{category}: {correct_count}/{total_count} 正解")
        if correct_count < total_count:
            print("  不一致のケース:")
            for item in items:
                if not item['correct']:
                    print(f"    '{item['text']}' → 期待: {item['expected']}, 実際: {item['actual']}")
    
    print("\n" + "=" * 80)
    if all_correct:
        print("\n✓ すべてのテストケースが正しく判別されました！")
    else:
        print("\n✗ 一部のテストケースで判別に問題があります。")
    
    # 特に重要な判別の確認
    print("\n【重要な判別の確認】")
    print("-" * 80)
    critical_tests = [
        ("（ｉ）", "paren_roman", "ローマ数字"),
        ("（a）", "paren_lowercase_alphabet", "小文字アルファベット"),
        ("（ａ）", "paren_fullwidth_lowercase_alphabet", "全角小文字アルファベット"),
        ("（科目名）", "subject_label", "科目名"),
    ]
    
    for test_text, expected_label_id, test_name in critical_tests:
        label_id, label_name, pattern = detect_label_id(test_text, config)
        status = "✓" if label_id == expected_label_id else "✗"
        print(f"{status} '{test_text}' ({test_name})")
        print(f"    → {label_id} ({label_name})")
        if label_id != expected_label_id:
            print(f"    ⚠️  期待: {expected_label_id}")

if __name__ == "__main__":
    main()
























