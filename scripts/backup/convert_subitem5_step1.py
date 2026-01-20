#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Subitem5要素補正ロジック（処理3）実装スクリプト - 修正版 v2

【修正内容 v2】
1. 順序保持の問題を修正
   - subitem4.remove() + subitem4.append() による順序破壊を修正
   - Subitem4直下の子要素を順序通り処理し、順序を保持して再構築

2. 仕様書に準拠した処理対象の限定
   - 処理対象：Subitem4Sentenceの直後の最初のSubitem5のみ
   - それ以外のSubitem5は処理しない

3. 分割回数の制限
   - 仕様書通り「1回分割で終了」を実装
   - Subitem5内で最初に見つかった分割対象（科目名括弧またはColumnありList）で分割

【元の仕様】
- 科目名括弧（〔医療と社会〕など）のみを分割対象とする
- 指導項目括弧（〔指導項目〕）は分割対象外とする

convert_subitem5_step0.pyによって生成されたXMLを走査し、特定の「コンテナSubitem5」を分割・補正する。
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
CONVERTED_LABELED_LIST_TO_SUBITEM5 = 'CONVERTED_LABELED_LIST_TO_SUBITEM5'
CONVERTED_NO_COLUMN_LIST_TO_SUBITEM5 = 'CONVERTED_NO_COLUMN_LIST_TO_SUBITEM5'
CONVERTED_SUBJECT_NAME_LIST_TO_SUBITEM5 = 'CONVERTED_SUBJECT_NAME_LIST_TO_SUBITEM5'
CONVERTED_INSTRUCTION_LIST_TO_SUBITEM5 = 'CONVERTED_INSTRUCTION_LIST_TO_SUBITEM5'
CONVERTED_GRADE_SINGLE_LIST_TO_SUBITEM5 = 'CONVERTED_GRADE_SINGLE_LIST_TO_SUBITEM5'
CONVERTED_GRADE_DOUBLE_LIST_TO_SUBITEM5 = 'CONVERTED_GRADE_DOUBLE_LIST_TO_SUBITEM5'
CONVERTED_NON_LIST_TO_SUBITEM5 = 'CONVERTED_NON_LIST_TO_SUBITEM5'

# ============================================================================
# Subitem5固有の処理対象取得関数
# ============================================================================

def get_first_subitem5_after_subitem4_sentence(subitem4: etree.Element) -> Optional[etree.Element]:
    """
    Subitem4Sentenceの直後の最初のSubitem5要素を取得

    Subitem4要素内の、Subitem4Sentenceのすぐ次の弟要素のSubitem5要素である
    最初のSubitem5のみを対象とする（コンテナSubitem5である必要がある）
    """
    subitem4_sentence = subitem4.find('.//Subitem4Sentence')
    if subitem4_sentence is None:
        return None

    # configを作成
    config = ConversionConfig(
        parent_tag='Subitem4',
        child_tag='Subitem5',
        title_tag='Subitem5Title',
        sentence_tag='Subitem5Sentence',
        column_condition_min=1,
        supported_types=['labeled', 'subject_name', 'instruction', 'grade_single', 'grade_double'],
        script_name='convert_subitem5_step1',
        skip_empty_parent=True
    )

    # 共通関数を使用（コンテナSubitem5を取得）
    return get_first_child_after_parent_sentence(subitem4, config)


# ============================================================================
# Subitem5固有の分割ポイント検出関数
# ============================================================================

def find_first_split_point_for_subitem5(subitem5_elem: etree.Element, config: ConversionConfig) -> Optional[Tuple[int, str]]:
    """
    Subitem5要素内で最初の分割ポイントを検出

    共通関数を使用し、ColumnなしListのみを対象とする
    """
    return find_split_point_common(subitem5_elem, config, subject_bracket_only=True)


# ============================================================================
# Subitem4全体を順序保持して処理（Subitem5用）
# ============================================================================

def process_subitem4_with_order_preservation_for_subitem5(subitem4: etree.Element, stats: dict, script_name: str) -> bool:
    """
    Subitem4要素を順序を保持しながら処理（Subitem5用）

    仕様書の要件：
    1. Subitem4Sentenceの直後の最初のSubitem5のみを対象
    2. 分割は1回のみ
    3. 元の順序を完全に保持

    処理フロー：
    1. Subitem4Sentenceの直後の最初のコンテナSubitem5を取得
    2. Subitem5内で最初の分割ポイントを検出
    3. 分割ポイントが見つかった場合、Subitem5を2つに分割
    4. Subitem4全体を順序を保持して再構築
    """
    # configを作成
    config = ConversionConfig(
        parent_tag='Subitem4',
        child_tag='Subitem5',
        title_tag='Subitem5Title',
        sentence_tag='Subitem5Sentence',
        column_condition_min=1,
        supported_types=['labeled', 'subject_name', 'instruction', 'grade_single', 'grade_double'],
        script_name='convert_subitem5_step1',
        skip_empty_parent=True
    )

    # Subitem4内の最初のSubitem5を取得
    target_subitem5 = get_first_subitem5_after_subitem4_sentence(subitem4)

    if target_subitem5 is None:
        return False

    # 最初の分割ポイントを検出
    split_result = find_first_split_point_for_subitem5(target_subitem5, config)

    if split_result is None:
        return False

    split_index, split_type = split_result

    # Subitem5を分割
    original_subitem5, new_subitem5 = split_element_at_point(target_subitem5, split_index, config)

    print(f"  - Split Subitem5 Num='{target_subitem5.get('Num', '')}' at index {split_index} (type: {split_type})")

    # Subitem4全体を順序を保持して再構築
    subitem4_children = list(subitem4)
    new_subitem4_children = []

    for child in subitem4_children:
        if child is target_subitem5:
            # 元のSubitem5を分割後の2つのSubitem5に置き換え
            new_subitem4_children.append(original_subitem5)
            new_subitem4_children.append(new_subitem5)
        else:
            # その他の要素はそのまま保持
            new_subitem4_children.append(child)

    # Subitem4を再構築（属性を保持）
    original_attrs = dict(subitem4.attrib)
    subitem4.clear()
    subitem4.attrib.update(original_attrs)

    for child in new_subitem4_children:
        subitem4.append(child)

    return True


def find_split_point_for_column_list(subitem5_elem: etree.Element) -> Optional[int]:
    """ColumnありListを探す関数"""
    children = list(subitem5_elem)
    for i, child in enumerate(children):
        if child.tag != 'List':
            continue

        col1_sentence, col2_sentence, column_count = get_list_columns(child)
        if column_count > 0:
            return i

    return None


def fix_container_subitem5(subitem4: etree.Element, stats: dict, script_name: str) -> bool:
    """
    コンテナSubitem5補正処理（共通化版）
    """
    # configを作成
    config = ConversionConfig(
        parent_tag='Subitem4',
        child_tag='Subitem5',
        title_tag='Subitem5Title',
        sentence_tag='Subitem5Sentence',
        column_condition_min=1,
        supported_types=['labeled', 'subject_name', 'instruction', 'grade_single', 'grade_double'],
        script_name='convert_subitem5_step1',
        skip_empty_parent=True
    )

    # Subitem4内の最初のSubitem5を取得
    target_subitem5 = get_first_subitem5_after_subitem4_sentence(subitem4)

    if target_subitem5 is None:
        return False

    if not is_container_element(target_subitem5, config):
        return False

    # 最初のColumnありListを探す
    split_point = find_split_point_for_column_list(target_subitem5)

    if split_point is None:
        return False

    print(f"  - Split Subitem5 Num='{target_subitem5.get('Num', '')}' at index {split_point} (type: column_list)")

    # 分割処理
    original_subitem5, new_subitem5 = split_element_at_point(target_subitem5, split_point, config)

    # Subitem4全体を順序を保持して再構築
    subitem4_children = list(subitem4)
    new_subitem4_children = []

    for child in subitem4_children:
        if child is target_subitem5:
            new_subitem4_children.append(original_subitem5)
            new_subitem4_children.append(new_subitem5)
        else:
            new_subitem4_children.append(child)

    # Subitem4を再構築（属性を保持）
    original_attrs = dict(subitem4.attrib)
    subitem4.clear()
    subitem4.attrib.update(original_attrs)

    for child in new_subitem4_children:
        subitem4.append(child)

    return True


# ============================================================================
# main関数（修正版）
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Subitem5要素補正処理（科目名括弧による分割） - 修正版 v2"
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
    print("  2. 処理対象をSubitem4Title/Subitem4Sentenceが空でない場合に限定")
    print("  3. 分割対象：ColumnありListまたはColumnなしList（スキップ対象以外）")

    tree = etree.parse(str(input_path))
    all_subitem4s = tree.xpath('//Subitem4')

    print(f"\n処理対象Subitem4数: {len(all_subitem4s)}")

    # ============================================================================
    # Subitem5分割処理
    # ============================================================================
    print("\n【Subitem5分割処理】")
    print("  ※ Subitem4Title/Subitem4Sentenceが空でない場合、Subitem5Title/Subitem5Sentenceが空の場合に実行")
    print("  ※ 分割対象：ColumnなしList（指導項目・科目名・学年でない場合）またはColumnありList")

    stats = {
        CONVERTED_LABELED_LIST_TO_SUBITEM5: 0,
        CONVERTED_NO_COLUMN_LIST_TO_SUBITEM5: 0,
        CONVERTED_SUBJECT_NAME_LIST_TO_SUBITEM5: 0,
        CONVERTED_INSTRUCTION_LIST_TO_SUBITEM5: 0,
        CONVERTED_GRADE_SINGLE_LIST_TO_SUBITEM5: 0,
        CONVERTED_GRADE_DOUBLE_LIST_TO_SUBITEM5: 0,
        CONVERTED_NON_LIST_TO_SUBITEM5: 0,
        'SKIPPED_DUE_TO_EMPTY_PARENT': 0
    }

    made_any_changes = False
    processed_count = 0

    for subitem4 in all_subitem4s:
        if process_subitem4_with_order_preservation_for_subitem5(subitem4, stats, script_name):
            made_any_changes = True
            processed_count += 1

    if made_any_changes:
        print(f"  ✅ {processed_count}個のSubitem4でSubitem5分割を実行しました")
    else:
        print("  - 分割対象のSubitem5は見つかりませんでした")

    # ============================================================================
    # Subitem5番号の再採番
    # ============================================================================
    if made_any_changes:
        print("\n【Subitem5番号再採番】")
        from xml_converter import renumber_elements
        config = ConversionConfig(
            parent_tag='Subitem4',
            child_tag='Subitem5',
            title_tag='Subitem5Title',
            sentence_tag='Subitem5Sentence',
            column_condition_min=1,
            supported_types=['labeled', 'subject_name', 'instruction', 'grade_single', 'grade_double'],
            script_name='convert_subitem5_step1',
            skip_empty_parent=True
        )
        renumber_elements(tree, config)
        print("  ✅ Subitem5番号を再採番しました")

    # ============================================================================
    # 出力
    # ============================================================================
    print("\n【処理統計】")
    if made_any_changes:
        print(f"  - Subitem5分割: {processed_count}個のSubitem4")
        print(f"  - Subitem5番号再採番: 実行")
    else:
        print("  - 補正処理は実行されませんでした")

    format_xml_lxml(tree, str(output_path))

    print(f"\n出力ファイル: {output_path}")
    print("  ✅ 処理完了")
    print("=" * 80)

    return 0


if __name__ == '__main__':
    sys.exit(main())

