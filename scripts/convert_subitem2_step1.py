#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Subitem2要素補正ロジック（処理3）実装スクリプト - 修正版 v2

【修正内容 v2】
1. 順序保持の問題を修正
   - item.remove() + item.append() による順序破壊を修正
   - Item直下の子要素を順序通り処理し、順序を保持して再構築

2. 仕様書に準拠した処理対象の限定
   - 処理対象：ItemSentenceの直後の最初のSubitem2のみ
   - それ以外のSubitem2は処理しない

3. 分割回数の制限
   - 仕様書通り「1回分割で終了」を実装
   - Subitem2内で最初に見つかった分割対象（科目名括弧またはColumnありList）で分割

【元の仕様】
- 科目名括弧（〔医療と社会〕など）のみを分割対象とする
- 指導項目括弧（〔指導項目〕）は分割対象外とする

convert_subitem2_step0.pyによって生成されたXMLを走査し、特定の「コンテナSubitem2」を分割・補正する。
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
from utils.label_utils import get_hierarchy_level, is_label
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
CONVERTED_LABELED_LIST_TO_SUBITEM2 = 'CONVERTED_LABELED_LIST_TO_SUBITEM2'
CONVERTED_NO_COLUMN_LIST_TO_SUBITEM2 = 'CONVERTED_NO_COLUMN_LIST_TO_SUBITEM2'
CONVERTED_SUBJECT_NAME_LIST_TO_SUBITEM2 = 'CONVERTED_SUBJECT_NAME_LIST_TO_SUBITEM2'
CONVERTED_INSTRUCTION_LIST_TO_SUBITEM2 = 'CONVERTED_INSTRUCTION_LIST_TO_SUBITEM2'
CONVERTED_GRADE_SINGLE_LIST_TO_SUBITEM2 = 'CONVERTED_GRADE_SINGLE_LIST_TO_SUBITEM2'
CONVERTED_GRADE_DOUBLE_LIST_TO_SUBITEM2 = 'CONVERTED_GRADE_DOUBLE_LIST_TO_SUBITEM2'
CONVERTED_NON_LIST_TO_SUBITEM2 = 'CONVERTED_NON_LIST_TO_SUBITEM2'

# ============================================================================
# Subitem2固有の処理対象取得関数
# ============================================================================

def get_first_subitem2_after_subitem1_sentence(subitem1: etree.Element) -> Optional[etree.Element]:
    """
    Subitem1Sentenceの直後の最初のSubitem2要素を取得

    convert_subitem1_step1.pyに合わせた条件：
    - Subitem1Titleが存在するがテキストが空の場合のみ処理対象（コンテナSubitem1）
    - Subitem1要素内の、Subitem1Sentenceのすぐ次の弟要素のSubitem2要素である
    - 最初のSubitem2のみを対象とする
    """
    # Subitem1Titleが存在するがテキストが空であることを確認（コンテナSubitem1）
    subitem1_title = subitem1.find('.//Subitem1Title')
    if subitem1_title is None or subitem1_title.text:
        return None

    subitem1_sentence = subitem1.find('.//Subitem1Sentence')
    if subitem1_sentence is None:
        return None

    # configを作成
    config = ConversionConfig(
        parent_tag='Subitem1',
        child_tag='Subitem2',
        title_tag='Subitem2Title',
        sentence_tag='Subitem2Sentence',
        column_condition_min=1,
        supported_types=['labeled', 'subject_name', 'instruction', 'grade_single', 'grade_double'],
        script_name='convert_subitem2_step1',
        skip_empty_parent=True
    )

    # 共通関数を使用
    return get_first_child_after_parent_sentence(subitem1, config)




# ============================================================================
# Subitem2固有の分割ポイント検出関数
# ============================================================================

def find_first_split_point_for_subitem2(subitem2_elem: etree.Element, config: ConversionConfig) -> Optional[Tuple[int, str]]:
    """
    Subitem2要素内で最初の分割ポイントを検出

    仕様書準拠：科目名括弧のみを分割対象とする
    """
    children = list(subitem2_elem)

    # Subitem2Sentenceを探す
    subitem2_sentence_index = -1
    for i, child in enumerate(children):
        if child.tag == 'Subitem2Sentence':
            subitem2_sentence_index = i
            break

    if subitem2_sentence_index == -1:
        return None

    # Subitem2Sentenceの次の弟要素を確認
    for i in range(subitem2_sentence_index + 1, len(children)):
        child = children[i]
        if child.tag == 'List':
            # ColumnありListはスキップ（分割対象外）
            col1_sentence, col2_sentence, column_count = get_list_columns(child)
            if column_count > 0:
                return (i, 'column_list')  # ColumnありListは分割対象

            # ColumnなしListの場合、科目名括弧のみをチェック
            list_sentence = child.find('.//ListSentence')
            if list_sentence is not None:
                sentences = list_sentence.findall('.//Sentence')
                if sentences:
                    first_sentence = sentences[0]
                    text = "".join(first_sentence.itertext()).strip()

                    # 科目名括弧の場合のみ分割対象
                    if (is_subject_name_bracket(text) or
                        is_grade_single_bracket(text) or
                        is_grade_double_bracket(text)):
                        return (i, 'bracket')  # 括弧の下で分割

                    # 科目名括弧でない場合、分割対象外
                    else:
                        return None  # 分割なし
            break  # 最初のListのみチェック

    return None




# ============================================================================
# Item全体を順序保持して処理（Subitem2用）
# ============================================================================

def process_item_with_order_preservation_for_subitem2(item: etree.Element, stats: dict, script_name: str) -> bool:
    """
    Item要素を順序を保持しながら処理（Subitem2用）

    仕様書の要件：
    1. Subitem1Sentenceの直後の最初のSubitem2のみを対象
    2. 分割は1回のみ
    3. 元の順序を完全に保持

    処理フロー：
    1. Item内のSubitem1をチェックし、Subitem1Sentenceの直後の最初のコンテナSubitem2を取得
    2. Subitem2内で最初の分割ポイントを検出
    3. 分割ポイントが見つかった場合、Subitem2を2つに分割
    4. Subitem1全体を順序を保持して再構築
    """
    # configを作成
    config = ConversionConfig(
        parent_tag='Subitem1',
        child_tag='Subitem2',
        title_tag='Subitem2Title',
        sentence_tag='Subitem2Sentence',
        column_condition_min=1,
        supported_types=['labeled', 'subject_name', 'instruction', 'grade_single', 'grade_double'],
        script_name='convert_subitem2_step1',
        skip_empty_parent=True
    )

    # Item内のすべてのSubitem1をチェック
    subitem1s = item.findall('.//Subitem1')
    processed_any = False

    for subitem1 in subitem1s:
        # Subitem1内の最初のSubitem2を取得
        target_subitem2 = get_first_subitem2_after_subitem1_sentence(subitem1)

        if target_subitem2 is None:
            continue

        # 最初の分割ポイントを検出
        split_result = find_first_split_point_for_subitem2(target_subitem2, config)

        if split_result is None:
            continue

        split_index, split_type = split_result

        # Subitem2を分割
        original_subitem2, new_subitem2 = split_element_at_point(target_subitem2, split_index, config)

        print(f"  - Split Subitem2 Num='{target_subitem2.get('Num', '')}' at index {split_index} (type: {split_type})")

        # Subitem1全体を順序を保持して再構築
        subitem1_children = list(subitem1)
        new_subitem1_children = []

        for child in subitem1_children:
            if child is target_subitem2:
                # 元のSubitem2を分割後の2つのSubitem2に置き換え
                new_subitem1_children.append(original_subitem2)
                new_subitem1_children.append(new_subitem2)
            else:
                # その他の要素はそのまま保持
                new_subitem1_children.append(child)

        # Subitem1を再構築（属性を保持）
        original_attrs = dict(subitem1.attrib)
        subitem1.clear()
        subitem1.attrib.update(original_attrs)

        for child in new_subitem1_children:
            subitem1.append(child)

        processed_any = True

    return processed_any


# ============================================================================
# 【修正版】after_splitの要素をSubitem2化する処理
# ============================================================================

def process_elements_into_subitem2s(elements: List[etree.Element], stats: dict, config) -> List[etree.Element]:
    """
    要素リストをSubitem2要素に変換

    fix_container_subitem2用の補助関数
    元のconvert_subitem2_step0.pyから呼び出される関数を使用
    """
    if not elements:
        return []

    result_subitem2s = []
    i = 0

    while i < len(elements):
        subitem2, _ = create_element_from_list(elements[i], config, stats)
        if subitem2 is not None:
            result_subitem2s.append(subitem2)
        i += 1

    return result_subitem2s


def find_split_point_for_column_list(subitem2_elem: etree.Element) -> Optional[int]:
    """ColumnありListを探す関数"""
    children = list(subitem2_elem)
    for i, child in enumerate(children):
        if child.tag != 'List':
            continue

        col1_sentence, col2_sentence, column_count = get_list_columns(child)
        if column_count > 0:
            return i

    return None


def fix_container_subitem2(item: etree.Element, stats: dict, script_name: str) -> bool:
    """
    コンテナSubitem2補正処理（共通化版）
    """
    # configを作成
    config = ConversionConfig(
        parent_tag='Subitem1',
        child_tag='Subitem2',
        title_tag='Subitem2Title',
        sentence_tag='Subitem2Sentence',
        column_condition_min=1,
        supported_types=['labeled', 'subject_name', 'instruction', 'grade_single', 'grade_double'],
        script_name='convert_subitem2_step1',
        skip_empty_parent=True
    )

    # Item内のすべてのSubitem1をチェック
    subitem1s = item.findall('.//Subitem1')
    processed_any = False

    for subitem1 in subitem1s:
        # Subitem1内の最初のSubitem2を取得
        target_subitem2 = get_first_subitem2_after_subitem1_sentence(subitem1)

        if target_subitem2 is None:
            continue

        if not is_container_element(target_subitem2, config):
            continue

        # 最初のColumnありListを探す
        split_point = find_split_point_for_column_list(target_subitem2)

        if split_point is None:
            continue

        print(f"  - Split Subitem2 Num='{target_subitem2.get('Num', '')}' at index {split_point} (type: column_list)")

        # 分割処理
        original_subitem2, new_subitem2 = split_element_at_point(target_subitem2, split_point, config)

        # Subitem1全体を順序を保持して再構築
        subitem1_children = list(subitem1)
        new_subitem1_children = []

        for child in subitem1_children:
            if child is target_subitem2:
                new_subitem1_children.append(original_subitem2)
                new_subitem1_children.append(new_subitem2)
            else:
                new_subitem1_children.append(child)

        # Subitem1を再構築（属性を保持）
        original_attrs = dict(subitem1.attrib)
        subitem1.clear()
        subitem1.attrib.update(original_attrs)

        for child in new_subitem1_children:
            subitem1.append(child)

        processed_any = True

    return processed_any


# ============================================================================
# main関数（修正版）
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Subitem2要素補正処理（科目名括弧による分割） - 修正版 v2"
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
    print("  2. 処理対象をItemTitle/ItemSentenceが空でない場合に限定")
    print("  3. 分割対象：ColumnありListまたはColumnなしList（スキップ対象以外）")

    tree = etree.parse(str(input_path))
    all_items = tree.xpath('//Item')

    print(f"\n処理対象Item数: {len(all_items)}")

    # ============================================================================
    # Subitem2分割処理
    # ============================================================================
    print("\n【Subitem2分割処理】")
    print("  ※ ItemTitle/ItemSentenceが空でない場合、Subitem2Title/Subitem2Sentenceが空の場合に実行")
    print("  ※ 分割対象：ColumnなしList（指導項目・科目名・学年でない場合）またはColumnありList")

    stats = {
        CONVERTED_LABELED_LIST_TO_SUBITEM2: 0,
        CONVERTED_NO_COLUMN_LIST_TO_SUBITEM2: 0,
        CONVERTED_SUBJECT_NAME_LIST_TO_SUBITEM2: 0,
        CONVERTED_INSTRUCTION_LIST_TO_SUBITEM2: 0,
        CONVERTED_GRADE_SINGLE_LIST_TO_SUBITEM2: 0,
        CONVERTED_GRADE_DOUBLE_LIST_TO_SUBITEM2: 0,
        CONVERTED_NON_LIST_TO_SUBITEM2: 0,
        'SKIPPED_DUE_TO_EMPTY_PARENT': 0
    }

    made_any_changes = False
    processed_count = 0

    for item in all_items:
        if process_item_with_order_preservation_for_subitem2(item, stats, script_name):
            made_any_changes = True
            processed_count += 1

    if made_any_changes:
        print(f"  ✅ {processed_count}個のItemでSubitem2分割を実行しました")
    else:
        print("  - 分割対象のSubitem2は見つかりませんでした")

    # ============================================================================
    # Subitem2番号の再採番
    # ============================================================================
    if made_any_changes:
        print("\n【Subitem2番号再採番】")
        from xml_converter import ConversionConfig, renumber_elements
        config = ConversionConfig(
            parent_tag='Subitem1',
            child_tag='Subitem2',
            title_tag='Subitem2Title',
            sentence_tag='Subitem2Sentence',
            column_condition_min=1,
            supported_types=['labeled', 'subject_name', 'instruction', 'grade_single', 'grade_double'],
            script_name='convert_subitem2_step1',
            skip_empty_parent=True
        )
        renumber_elements(tree, config)
        print("  ✅ Subitem2番号を再採番しました")

    # ============================================================================
    # 出力
    # ============================================================================
    print("\n【処理統計】")
    if made_any_changes:
        print(f"  - Subitem2分割: {processed_count}個のItem")
        print(f"  - Subitem2番号再採番: 実行")
    else:
        print("  - 補正処理は実行されませんでした")

    format_xml_lxml(tree, str(output_path))

    print(f"\n出力ファイル: {output_path}")
    print("  ✅ 処理完了")
    print("=" * 80)

    return 0


if __name__ == '__main__':
    sys.exit(main())
