#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Subitem1要素補正ロジック（処理3）実装スクリプト - 修正版 v2

【修正内容 v2】
1. 順序保持の問題を修正
   - item.remove() + item.append() による順序破壊を修正
   - Item直下の子要素を順序通り処理し、順序を保持して再構築
   
2. 仕様書に準拠した処理対象の限定
   - 処理対象：ItemSentenceの直後の最初のSubitem1のみ
   - それ以外のSubitem1は処理しない

3. 分割回数の制限
   - 仕様書通り「1回分割で終了」を実装
   - Subitem1内で最初に見つかった分割対象（科目名括弧またはColumnありList）で分割

【元の仕様】
- 科目名括弧（〔医療と社会〕など）のみを分割対象とする
- 指導項目括弧（〔指導項目〕）は分割対象外とする

convert_subitem1_step0.pyによって生成されたXMLを走査し、特定の「コンテナSubitem1」を分割・補正する。
"""

import sys
import argparse
import re
from pathlib import Path
from lxml import etree
from typing import Optional, Tuple, List
from copy import deepcopy

# 共通モジュールをインポート
from xml_converter import (
    format_xml_lxml,
    create_empty_element,
    create_element_from_list,
    renumber_elements,
    ConversionConfig,
    get_list_columns,
    get_list_text,
    is_container_element,
    get_first_child_after_parent_sentence,
    split_element_at_point,
    process_parent_with_order_preservation,
    find_split_point_common
)
from utils.label_utils import get_hierarchy_level, is_label
from utils.bracket_utils import (
    is_subject_name_bracket,
    is_instruction_bracket,
    is_grade_single_bracket,
    is_grade_double_bracket
)

# 統計定数
CONVERTED_LABELED_LIST_TO_SUBITEM1 = 'CONVERTED_LABELED_LIST_TO_SUBITEM1'
CONVERTED_NO_COLUMN_LIST_TO_SUBITEM1 = 'CONVERTED_NO_COLUMN_LIST_TO_SUBITEM1'
CONVERTED_SUBJECT_NAME_LIST_TO_SUBITEM1 = 'CONVERTED_SUBJECT_NAME_LIST_TO_SUBITEM1'
CONVERTED_INSTRUCTION_LIST_TO_SUBITEM1 = 'CONVERTED_INSTRUCTION_LIST_TO_SUBITEM1'
CONVERTED_GRADE_SINGLE_LIST_TO_SUBITEM1 = 'CONVERTED_GRADE_SINGLE_LIST_TO_SUBITEM1'
CONVERTED_GRADE_DOUBLE_LIST_TO_SUBITEM1 = 'CONVERTED_GRADE_DOUBLE_LIST_TO_SUBITEM1'
CONVERTED_NON_LIST_TO_SUBITEM1 = 'CONVERTED_NON_LIST_TO_SUBITEM1'

# ============================================================================
# Subitem1固有の分割ポイント検出関数
# ============================================================================

def find_first_split_point_for_subitem1(subitem1_elem: etree.Element, config: ConversionConfig) -> Optional[Tuple[int, str]]:
    """
    Subitem1要素内で最初の分割ポイントを検出

    共通関数を使用し、科目名括弧のみを対象とする
    """
    return find_split_point_common(subitem1_elem, config, subject_bracket_only=True)


# ============================================================================
# 【修正版】after_splitの要素をSubitem1化する処理
# ============================================================================

def process_elements_into_subitem1s(elements: List[etree.Element], stats: dict, config: ConversionConfig) -> List[etree.Element]:
    """
    要素リストをSubitem1要素に変換

    fix_container_subitem1用の補助関数
    共通モジュールの関数を使用
    """
    if not elements:
        return []

    result_subitem1s = []
    i = 0

    while i < len(elements):
        subitem1, _ = create_element_from_list(elements[i], config, stats)
        if subitem1 is not None:
            result_subitem1s.append(subitem1)
        i += 1

    return result_subitem1s


def find_split_point_for_column_list(subitem1_elem: etree.Element) -> Optional[int]:
    """ColumnありListを探す関数"""
    children = list(subitem1_elem)
    for i, child in enumerate(children):
        if child.tag != 'List':
            continue

        col1_sentence, col2_sentence, column_count = get_list_columns(child)
        if column_count > 0:
            return i

    return None


def fix_container_subitem1(item: etree.Element, stats: dict, script_name: str) -> bool:
    """
    コンテナSubitem1補正処理（共通化版）
    """
    # configを作成
    config = ConversionConfig(
        parent_tag='Item',
        child_tag='Subitem1',
        title_tag='Subitem1Title',
        sentence_tag='Subitem1Sentence',
        column_condition_min=1,
        supported_types=['labeled', 'subject_name', 'instruction', 'grade_single', 'grade_double'],
        script_name='convert_subitem1_step1',
        skip_empty_parent=True
    )

    # 処理対象のSubitem1要素を取得
    target_subitem1 = get_first_child_after_parent_sentence(item, config)
    
    if target_subitem1 is None:
        return False
    
    if not is_container_element(target_subitem1, config):
        return False
    
    # 最初のColumnありListを探す
    split_point = find_split_point_for_column_list(target_subitem1)
    
    if split_point is None:
        return False

    # 分割処理
    original_subitem1, new_subitem1 = split_element_at_point(target_subitem1, split_point, config)
    
    # Item全体を順序を保持して再構築
    item_children = list(item)
    new_item_children = []
    
    for child in item_children:
        if child is target_subitem1:
            new_item_children.append(original_subitem1)
            new_item_children.append(new_subitem1)
        else:
            new_item_children.append(child)
    
    # Itemを再構築
    attrib = dict(item.attrib)
    item.clear()
    
    for key, value in attrib.items():
        item.set(key, value)
    
    for child in new_item_children:
        item.append(child)
    
    return True


# ============================================================================
# main関数（修正版）
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Subitem1要素補正処理（科目名括弧による分割） - 修正版 v2"
    )
    parser.add_argument('input_file', help='入力XMLファイル')
    parser.add_argument('output_file', help='出力XMLファイル')

    args = parser.parse_args()

    input_path = Path(args.input_file)
    output_path = Path(args.output_file)

    script_name = Path(__file__).name

    print("=" * 80)
    print(f"【{script_name}】実行開始（修正版 v2）")
    print("=" * 80)
    print(f"入力ファイル: {input_path}")
    print(f"出力ファイル: {output_path}")
    print()
    print("【修正内容】")
    print("  1. 順序保持の問題を修正")
    print("  2. 処理対象を最初のSubitem1のみに限定（仕様書準拠）")
    print("  3. 分割回数を1回に制限（仕様書準拠）")

    tree = etree.parse(str(input_path))
    all_items = tree.xpath('//Item')

    print(f"\n処理対象Item数: {len(all_items)}")

    # ============================================================================
    # ステップ1: コンテナSubitem1補正処理
    # ============================================================================
    print("\n【ステップ1：コンテナSubitem1補正処理】")
    stats = {
        CONVERTED_LABELED_LIST_TO_SUBITEM1: 0,
        CONVERTED_NO_COLUMN_LIST_TO_SUBITEM1: 0,
        CONVERTED_SUBJECT_NAME_LIST_TO_SUBITEM1: 0,
        CONVERTED_INSTRUCTION_LIST_TO_SUBITEM1: 0,
        CONVERTED_NON_LIST_TO_SUBITEM1: 0
    }

    made_any_changes = False
    processed_count = 0
    
    for item in all_items:
        if fix_container_subitem1(item, stats, script_name):
            made_any_changes = True
            processed_count += 1

    if made_any_changes:
        print(f"  ✅ {processed_count}個のItemでSubitem1分割を実行しました")
    else:
        print("  - 分割対象のSubitem1は見つかりませんでした")

    # ============================================================================
    # ステップ2：科目名括弧による分割処理
    # ============================================================================
    print("\n【ステップ2：科目名括弧による分割処理】")
    print("  ※ 仕様書準拠：最初のSubitem1のみ対象、1回分割で終了")

    subject_name_bracket_changes = False
    processed_count_step2 = 0
    
    # configを作成
    config = ConversionConfig(
        parent_tag='Item',
        child_tag='Subitem1',
        title_tag='Subitem1Title',
        sentence_tag='Subitem1Sentence',
        column_condition_min=1,
        supported_types=['labeled', 'subject_name', 'instruction', 'grade_single', 'grade_double'],
        script_name='convert_subitem1_step1',
        skip_empty_parent=True
    )
    
    for item in all_items:
        if process_parent_with_order_preservation(item, stats, script_name, config, lambda elem: find_first_split_point_for_subitem1(elem, config)):
            subject_name_bracket_changes = True
            processed_count_step2 += 1

    if subject_name_bracket_changes:
        print(f"  ✅ {processed_count_step2}個のItemで科目名括弧による分割を実行しました")
        made_any_changes = True
    else:
        print("  - 科目名括弧は見つかりませんでした")

    # ============================================================================
    # ステップ3: Subitem1番号の再採番
    # ============================================================================
    if made_any_changes:
        print("\n【ステップ3：Subitem1番号再採番】")
        config = ConversionConfig(
            parent_tag='Item',
            child_tag='Subitem1',
            title_tag='Subitem1Title',
            sentence_tag='Subitem1Sentence',
            column_condition_min=1,
            supported_types=['labeled', 'subject_name', 'instruction', 'grade_single', 'grade_double'],
            script_name='convert_subitem1_step1',
            skip_empty_parent=True
        )
        renumber_elements(tree, config)
        print("  ✅ Subitem1番号を再採番しました")

    # ============================================================================
    # 出力
    # ============================================================================
    print("\n【処理統計】")
    if made_any_changes:
        print(f"  - ステップ1（コンテナSubitem1分割）: {processed_count}個のItem")
        print(f"  - ステップ2（科目名括弧分割）: {processed_count_step2}個のItem")
        print(f"  - ステップ3（Subitem1番号再採番）: 実行")
    else:
        print("  - 補正処理は実行されませんでした")

    format_xml_lxml(tree, str(output_path))

    print(f"\n出力ファイル: {output_path}")
    print("  ✅ 処理完了")
    print("=" * 80)

    return 0


if __name__ == '__main__':
    sys.exit(main())
