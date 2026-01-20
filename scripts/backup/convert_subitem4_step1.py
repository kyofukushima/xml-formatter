#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Subitem4要素補正ロジック（処理3）実装スクリプト - 修正版 v2

【修正内容 v2】
1. 順序保持の問題を修正
   - subitem3.remove() + subitem3.append() による順序破壊を修正
   - Subitem3直下の子要素を順序通り処理し、順序を保持して再構築

2. 仕様書に準拠した処理対象の限定
   - 処理対象：Subitem3Sentenceの直後の最初のSubitem4のみ
   - それ以外のSubitem4は処理しない

3. 分割回数の制限
   - 仕様書通り「1回分割で終了」を実装
   - Subitem4内で最初に見つかった分割対象（科目名括弧またはColumnありList）で分割

【元の仕様】
- 科目名括弧（〔医療と社会〕など）のみを分割対象とする
- 指導項目括弧（〔指導項目〕）は分割対象外とする

convert_subitem4_step0.pyによって生成されたXMLを走査し、特定の「コンテナSubitem4」を分割・補正する。
"""

import sys
import argparse
import re
from pathlib import Path
from lxml import etree
from typing import Optional, Tuple, List
from copy import deepcopy

# 親ディレクトリのutils/とstep0の関数をインポート
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils.label_utils import is_label
sys.path.pop(0)

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils.bracket_utils import (
    is_subject_name_bracket,
    is_instruction_bracket,
    is_grade_single_bracket,
    is_grade_double_bracket
)
# 共通モジュールをインポート
from xml_converter import (
    format_xml_lxml,
    create_empty_element,
    create_element_from_list,
    get_list_columns,
    get_list_text,
    is_container_element,
    get_first_child_after_parent_sentence,
    split_element_at_point,
    process_parent_with_order_preservation,
    find_split_point_common,
    ConversionConfig
)

# 統計定数
CONVERTED_LABELED_LIST_TO_SUBITEM4 = 'CONVERTED_LABELED_LIST_TO_SUBITEM4'
CONVERTED_NO_COLUMN_LIST_TO_SUBITEM4 = 'CONVERTED_NO_COLUMN_LIST_TO_SUBITEM4'
CONVERTED_SUBJECT_NAME_LIST_TO_SUBITEM4 = 'CONVERTED_SUBJECT_NAME_LIST_TO_SUBITEM4'
CONVERTED_INSTRUCTION_LIST_TO_SUBITEM4 = 'CONVERTED_INSTRUCTION_LIST_TO_SUBITEM4'
CONVERTED_GRADE_SINGLE_LIST_TO_SUBITEM4 = 'CONVERTED_GRADE_SINGLE_LIST_TO_SUBITEM4'
CONVERTED_GRADE_DOUBLE_LIST_TO_SUBITEM4 = 'CONVERTED_GRADE_DOUBLE_LIST_TO_SUBITEM4'
CONVERTED_NON_LIST_TO_SUBITEM4 = 'CONVERTED_NON_LIST_TO_SUBITEM4'

# ============================================================================
# Subitem4固有の処理対象取得関数
# ============================================================================

def get_first_subitem4_after_subitem3_sentence(subitem3: etree.Element) -> Optional[etree.Element]:
    """
    Subitem3Sentenceの直後の最初のSubitem4要素を取得

    Subitem3要素内の、Subitem3Sentenceのすぐ次の弟要素のSubitem4要素である
    最初のSubitem4のみを対象とする（コンテナSubitem4である必要がある）
    """
    subitem3_sentence = subitem3.find('.//Subitem3Sentence')
    if subitem3_sentence is None:
        return None

    # configを作成
    config = ConversionConfig(
        parent_tag='Subitem3',
        child_tag='Subitem4',
        title_tag='Subitem4Title',
        sentence_tag='Subitem4Sentence',
        column_condition_min=1,
        supported_types=['labeled', 'subject_name', 'instruction', 'grade_single', 'grade_double'],
        script_name='convert_subitem4_step1',
        skip_empty_parent=True
    )

    # 共通関数を使用（コンテナSubitem4を取得）
    return get_first_child_after_parent_sentence(subitem3, config)


# ============================================================================
# Subitem4固有の分割ポイント検出関数
# ============================================================================

def find_first_split_point_for_subitem4(subitem4_elem: etree.Element, config: ConversionConfig) -> Optional[Tuple[int, str]]:
    """
    Subitem4要素内で最初の分割ポイントを検出

    共通関数を使用し、ColumnなしListのみを対象とする
    """
    return find_split_point_common(subitem4_elem, config, subject_bracket_only=True)


# ============================================================================
# Subitem3全体を順序保持して処理（Subitem4用）
# ============================================================================

def process_subitem3_with_order_preservation_for_subitem4(subitem3: etree.Element, stats: dict, script_name: str) -> bool:
    """
    Subitem3要素を順序を保持しながら処理（Subitem4用）

    仕様書の要件：
    1. Subitem3Sentenceの直後の最初のSubitem4のみを対象
    2. 分割は1回のみ
    3. 元の順序を完全に保持

    処理フロー：
    1. Subitem3Sentenceの直後の最初のコンテナSubitem4を取得
    2. Subitem4内で最初の分割ポイントを検出
    3. 分割ポイントが見つかった場合、Subitem4を2つに分割
    4. Subitem3全体を順序を保持して再構築
    """
    # configを作成
    config = ConversionConfig(
        parent_tag='Subitem3',
        child_tag='Subitem4',
        title_tag='Subitem4Title',
        sentence_tag='Subitem4Sentence',
        column_condition_min=1,
        supported_types=['labeled', 'subject_name', 'instruction', 'grade_single', 'grade_double'],
        script_name='convert_subitem4_step1',
        skip_empty_parent=True
    )

    # Subitem3内の最初のSubitem4を取得
    target_subitem4 = get_first_subitem4_after_subitem3_sentence(subitem3)

    if target_subitem4 is None:
        return False

    # 最初の分割ポイントを検出
    split_result = find_first_split_point_for_subitem4(target_subitem4, config)

    if split_result is None:
        return False

    split_index, split_type = split_result

    # Subitem4を分割
    original_subitem4, new_subitem4 = split_element_at_point(target_subitem4, split_index, config)

    print(f"  - Split Subitem4 Num='{target_subitem4.get('Num', '')}' at index {split_index} (type: {split_type})")

    # Subitem3全体を順序を保持して再構築
    subitem3_children = list(subitem3)
    new_subitem3_children = []

    for child in subitem3_children:
        if child is target_subitem4:
            # 元のSubitem4を分割後の2つのSubitem4に置き換え
            new_subitem3_children.append(original_subitem4)
            new_subitem3_children.append(new_subitem4)
        else:
            # その他の要素はそのまま保持
            new_subitem3_children.append(child)

    # Subitem3を再構築（属性を保持）
    original_attrs = dict(subitem3.attrib)
    subitem3.clear()
    subitem3.attrib.update(original_attrs)

    for child in new_subitem3_children:
        subitem3.append(child)

    return True


def find_split_point_for_column_list(subitem4_elem: etree.Element) -> Optional[int]:
    """ColumnありListを探す関数"""
    children = list(subitem4_elem)
    for i, child in enumerate(children):
        if child.tag != 'List':
            continue

        col1_sentence, col2_sentence, column_count = get_list_columns(child)
        if column_count > 0:
            return i

    return None


def fix_container_subitem4(subitem3: etree.Element, stats: dict, script_name: str) -> bool:
    """
    コンテナSubitem4補正処理（共通化版）
    """
    # configを作成
    config = ConversionConfig(
        parent_tag='Subitem3',
        child_tag='Subitem4',
        title_tag='Subitem4Title',
        sentence_tag='Subitem4Sentence',
        column_condition_min=1,
        supported_types=['labeled', 'subject_name', 'instruction', 'grade_single', 'grade_double'],
        script_name='convert_subitem4_step1',
        skip_empty_parent=True
    )

    # Subitem3内の最初のSubitem4を取得
    target_subitem4 = get_first_subitem4_after_subitem3_sentence(subitem3)

    if target_subitem4 is None:
        return False

    if not is_container_element(target_subitem4, config):
        return False

    # 最初のColumnありListを探す
    split_point = find_split_point_for_column_list(target_subitem4)

    if split_point is None:
        return False

    print(f"  - Split Subitem4 Num='{target_subitem4.get('Num', '')}' at index {split_point} (type: column_list)")

    # 分割処理
    original_subitem4, new_subitem4 = split_element_at_point(target_subitem4, split_point, config)

    # Subitem3全体を順序を保持して再構築
    subitem3_children = list(subitem3)
    new_subitem3_children = []

    for child in subitem3_children:
        if child is target_subitem4:
            new_subitem3_children.append(original_subitem4)
            new_subitem3_children.append(new_subitem4)
        else:
            new_subitem3_children.append(child)

    # Subitem3を再構築（属性を保持）
    original_attrs = dict(subitem3.attrib)
    subitem3.clear()
    subitem3.attrib.update(original_attrs)

    for child in new_subitem3_children:
        subitem3.append(child)

    return True


# ============================================================================
# main関数（修正版）
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Subitem4要素補正処理（科目名括弧による分割） - 修正版 v2"
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
    print("  2. 処理対象をSubitem3Title/Subitem3Sentenceが空でない場合に限定")
    print("  3. 分割対象：ColumnありListまたはColumnなしList（スキップ対象以外）")

    tree = etree.parse(str(input_path))
    all_subitem3s = tree.xpath('//Subitem3')

    print(f"\n処理対象Subitem3数: {len(all_subitem3s)}")

    # ============================================================================
    # Subitem4分割処理
    # ============================================================================
    print("\n【Subitem4分割処理】")
    print("  ※ Subitem3Title/Subitem3Sentenceが空でない場合、Subitem4Title/Subitem4Sentenceが空の場合に実行")
    print("  ※ 分割対象：ColumnなしList（指導項目・科目名・学年でない場合）またはColumnありList")

    stats = {
        CONVERTED_LABELED_LIST_TO_SUBITEM4: 0,
        CONVERTED_NO_COLUMN_LIST_TO_SUBITEM4: 0,
        CONVERTED_SUBJECT_NAME_LIST_TO_SUBITEM4: 0,
        CONVERTED_INSTRUCTION_LIST_TO_SUBITEM4: 0,
        CONVERTED_GRADE_SINGLE_LIST_TO_SUBITEM4: 0,
        CONVERTED_GRADE_DOUBLE_LIST_TO_SUBITEM4: 0,
        CONVERTED_NON_LIST_TO_SUBITEM4: 0,
        'SKIPPED_DUE_TO_EMPTY_PARENT': 0
    }

    made_any_changes = False
    processed_count = 0

    for subitem3 in all_subitem3s:
        if process_subitem3_with_order_preservation_for_subitem4(subitem3, stats, script_name):
            made_any_changes = True
            processed_count += 1

    if made_any_changes:
        print(f"  ✅ {processed_count}個のSubitem3でSubitem4分割を実行しました")
    else:
        print("  - 分割対象のSubitem4は見つかりませんでした")

    # ============================================================================
    # Subitem4番号の再採番
    # ============================================================================
    if made_any_changes:
        print("\n【Subitem4番号再採番】")
        from xml_converter import renumber_elements
        config = ConversionConfig(
            parent_tag='Subitem3',
            child_tag='Subitem4',
            title_tag='Subitem4Title',
            sentence_tag='Subitem4Sentence',
            column_condition_min=1,
            supported_types=['labeled', 'subject_name', 'instruction', 'grade_single', 'grade_double'],
            script_name='convert_subitem4_step1',
            skip_empty_parent=True
        )
        renumber_elements(tree, config)
        print("  ✅ Subitem4番号を再採番しました")

    # ============================================================================
    # 出力
    # ============================================================================
    print("\n【処理統計】")
    if made_any_changes:
        print(f"  - Subitem4分割: {processed_count}個のSubitem3")
        print(f"  - Subitem4番号再採番: 実行")
    else:
        print("  - 補正処理は実行されませんでした")

    format_xml_lxml(tree, str(output_path))

    print(f"\n出力ファイル: {output_path}")
    print("  ✅ 処理完了")
    print("=" * 80)

    return 0


if __name__ == '__main__':
    sys.exit(main())

