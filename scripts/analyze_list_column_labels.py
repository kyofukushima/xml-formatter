#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
List要素のColumnの1番目の値を分析し、ラベルの種類として新規作成が必要かどうかを判定するスクリプト
"""

import sys
import json
from pathlib import Path
from lxml import etree
from collections import defaultdict
from typing import Dict, List, Set, Tuple

# scripts/utils/をインポートパスに追加
script_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(script_dir))

from utils.label_utils import LabelConfig


def extract_column1_values(xml_path: str) -> List[Tuple[str, int]]:
    """
    XMLファイルからList要素のColumnの1番目の値を抽出
    
    Returns:
        List[Tuple[str, int]]: (Column1の値, 行番号)のリスト
    """
    tree = etree.parse(xml_path)
    root = tree.getroot()
    
    results = []
    
    # すべてのList要素を検索
    for list_elem in root.iter('List'):
        columns = list_elem.findall('.//Column[@Num="1"]')
        
        for col in columns:
            # Column内のSentence要素からテキストを取得
            sentence = col.find('.//Sentence')
            if sentence is not None:
                # すべてのテキストを結合
                text = "".join(sentence.itertext()).strip()
                if text:
                    # 行番号を取得
                    line_no = sentence.sourceline if hasattr(sentence, 'sourceline') else None
                    results.append((text, line_no))
    
    return results


def analyze_labels(column1_values: List[Tuple[str, int]], label_config: LabelConfig) -> Dict:
    """
    Column1の値をラベルパターンと照合して分析
    
    Returns:
        Dict: 分析結果
    """
    # ラベルIDごとの出現回数
    label_counts: Dict[str, int] = defaultdict(int)
    
    # マッチしない値のリスト
    unmatched_values: List[Tuple[str, int]] = []
    
    # 各値に対してラベルIDを判定
    for value, line_no in column1_values:
        label_id = label_config.detect_label_id(value)
        
        if label_id:
            label_counts[label_id] += 1
        else:
            unmatched_values.append((value, line_no))
    
    return {
        'label_counts': dict(label_counts),
        'unmatched_values': unmatched_values,
        'total_count': len(column1_values),
        'matched_count': len(column1_values) - len(unmatched_values),
        'unmatched_count': len(unmatched_values)
    }


def check_new_labels_needed(analysis_result: Dict, label_config: LabelConfig) -> Dict:
    """
    新規ラベル作成が必要かどうかを判定
    
    Returns:
        Dict: 判定結果
    """
    unmatched_values = analysis_result['unmatched_values']
    
    # マッチしない値の種類を集計
    unique_unmatched = {}
    for value, line_no in unmatched_values:
        if value not in unique_unmatched:
            unique_unmatched[value] = []
        unique_unmatched[value].append(line_no)
    
    # パターン分析（どのようなパターンがマッチしていないか）
    pattern_analysis = []
    
    for value, line_nos in unique_unmatched.items():
        # 詳細なパターン分析
        pattern_type = "unknown"
        suggested_pattern = None
        
        # 全角小文字アルファベット + ）
        if re.match(r'^[ａ-ｚ]）$', value):
            pattern_type = "全角小文字アルファベット + ）"
            suggested_pattern = f"^[（(][ａ-ｚ]+[）)]$"  # 既存のparen_fullwidth_lowercase_alphabetに類似
        # 全角数字 + ）
        elif re.match(r'^[０-９]+）$', value):
            pattern_type = "全角数字 + ）"
            suggested_pattern = f"^[（(][０-９]+[）)]$"  # 既存のparen_fullwidth_numberに類似
        # 注記 + 数字
        elif re.match(r'^注記[０-９]+$', value):
            pattern_type = "注記 + 数字"
            suggested_pattern = f"^注記[０-９]+$"
        # ドット区切りの数字（例：４．１、４．２．１）
        elif re.match(r'^[０-９]+[．.][０-９]+([．.][０-９]+)*$', value):
            pattern_type = "ドット区切り数字（例：４．１）"
            suggested_pattern = r"^[０-９]+([．.][０-９]+)+$"
        # 通常の文（ラベルではない可能性）
        elif len(value) > 10:
            pattern_type = "通常の文（ラベルではない可能性）"
        # 括弧パターン
        elif value.startswith('（') and value.endswith('）'):
            pattern_type = "括弧パターン（全角）"
        elif value.startswith('(') and value.endswith(')'):
            pattern_type = "括弧パターン（半角）"
        elif value.startswith('〔') and value.endswith('〕'):
            pattern_type = "角括弧パターン（全角）"
        elif value.startswith('【') and value.endswith('】'):
            pattern_type = "二重角括弧パターン"
        elif value.startswith('［') and value.endswith('］'):
            pattern_type = "角括弧パターン（全角）"
        # 数字のみ
        elif re.match(r'^[０-９]+$', value):
            pattern_type = "全角数字"
        elif re.match(r'^[0-9]+$', value):
            pattern_type = "半角数字"
        elif re.match(r'^[一二三四五六七八九十百千]+$', value):
            pattern_type = "漢数字"
        # アルファベットのみ
        elif re.match(r'^[ａ-ｚ]+$', value):
            pattern_type = "全角小文字アルファベット"
        elif re.match(r'^[Ａ-Ｚ]+$', value):
            pattern_type = "全角大文字アルファベット"
        elif re.match(r'^[a-z]+$', value):
            pattern_type = "半角小文字アルファベット"
        elif re.match(r'^[A-Z]+$', value):
            pattern_type = "半角大文字アルファベット"
        elif re.match(r'^[ア-ヴ]+$', value):
            pattern_type = "カタカナ"
        
        pattern_analysis.append({
            'value': value,
            'pattern_type': pattern_type,
            'suggested_pattern': suggested_pattern,
            'occurrences': len(line_nos),
            'line_numbers': line_nos[:5]  # 最初の5つの行番号のみ表示
        })
    
    return {
        'needs_new_labels': len(unique_unmatched) > 0,
        'unique_unmatched_count': len(unique_unmatched),
        'pattern_analysis': pattern_analysis
    }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='List要素のColumnの1番目の値を分析し、ラベルの種類として新規作成が必要かどうかを判定'
    )
    parser.add_argument(
        'xml_file',
        type=str,
        help='分析対象のXMLファイルパス'
    )
    parser.add_argument(
        '--config',
        type=str,
        default=None,
        help='ラベル設定ファイルのパス（デフォルト: scripts/config/label_config.json）'
    )
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='結果をJSONファイルに出力するパス（オプション）'
    )
    
    args = parser.parse_args()
    
    # ラベル設定を読み込み
    if args.config:
        label_config = LabelConfig(args.config)
    else:
        label_config = LabelConfig()
    
    # XMLファイルからColumn1の値を抽出
    print(f"XMLファイルを読み込み中: {args.xml_file}")
    column1_values = extract_column1_values(args.xml_file)
    print(f"Column1の値が{len(column1_values)}個見つかりました。\n")
    
    # ラベル分析
    analysis_result = analyze_labels(column1_values, label_config)
    
    # 新規ラベル作成の必要性を判定
    new_labels_check = check_new_labels_needed(analysis_result, label_config)
    
    # 結果を表示
    print("=" * 80)
    print("分析結果")
    print("=" * 80)
    print(f"\n総数: {analysis_result['total_count']}")
    print(f"マッチした数: {analysis_result['matched_count']}")
    print(f"マッチしなかった数: {analysis_result['unmatched_count']}")
    
    print("\n" + "-" * 80)
    print("ラベルID別の出現回数:")
    print("-" * 80)
    for label_id, count in sorted(analysis_result['label_counts'].items(), key=lambda x: -x[1]):
        label_def = label_config.config['label_definitions'].get(label_id, {})
        label_name = label_def.get('name', label_id)
        print(f"  {label_id:40s} ({label_name:30s}): {count:3d}回")
    
    print("\n" + "-" * 80)
    print("新規ラベル作成の必要性:")
    print("-" * 80)
    if new_labels_check['needs_new_labels']:
        print(f"  ⚠️  新規ラベル作成が必要です（{new_labels_check['unique_unmatched_count']}種類の値がマッチしませんでした）")
        print("\n  マッチしなかった値のパターン分析:")
        for item in new_labels_check['pattern_analysis']:
            print(f"\n    値: {item['value']}")
            print(f"    パターンタイプ: {item['pattern_type']}")
            if item.get('suggested_pattern'):
                print(f"    推奨パターン: {item['suggested_pattern']}")
            print(f"    出現回数: {item['occurrences']}")
            if item['line_numbers']:
                print(f"    行番号（例）: {', '.join(map(str, item['line_numbers']))}")
    else:
        print("  ✅ すべての値が既存のラベルパターンにマッチしています。新規作成は不要です。")
    
    # JSONファイルに出力
    if args.output:
        output_data = {
            'analysis_result': analysis_result,
            'new_labels_check': new_labels_check
        }
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        print(f"\n結果をJSONファイルに出力しました: {args.output}")


if __name__ == '__main__':
    import re
    main()
