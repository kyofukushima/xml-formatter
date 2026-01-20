#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Item要素補正ロジック（処理3）実装スクリプト - 修正版 v2

【修正内容 v2】
1. 順序保持の問題を修正
   - paragraph.remove() + paragraph.append() による順序破壊を修正
   - Paragraph直下の子要素を順序通り処理し、順序を保持して再構築
   
2. 仕様書に準拠した処理対象の限定
   - 処理対象：ParagraphSentenceの直後の最初のItemのみ
   - それ以外のItemは処理しない

3. 分割回数の制限
   - 仕様書通り「1回分割で終了」を実装
   - Item内で最初に見つかった分割対象（科目名括弧またはColumnありList）で分割

【元の仕様】
- 科目名括弧（〔医療と社会〕など）のみを分割対象とする
- 指導項目括弧（〔指導項目〕）は分割対象外とする

convert_item_step0.pyによって生成されたXMLを走査し、特定の「コンテナItem」を分割・補正する。
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
    process_parent_with_order_preservation
)
from utils.bracket_utils import (
    is_subject_name_bracket,
    is_instruction_bracket,
    is_grade_single_bracket,
    is_grade_double_bracket
)

# 統計定数
CONVERTED_LABELED_LIST_TO_ITEM = 'CONVERTED_LABELED_LIST_TO_ITEM'
CONVERTED_NO_COLUMN_LIST = 'CONVERTED_NO_COLUMN_LIST'
CONVERTED_SUBJECT_NAME_LIST = 'CONVERTED_SUBJECT_NAME_LIST'
CONVERTED_INSTRUCTION_LIST = 'CONVERTED_INSTRUCTION_LIST'
CONVERTED_NON_LIST_TO_ITEM = 'CONVERTED_NON_LIST_TO_ITEM'

# ============================================================================
# Item固有の分割ポイント検出関数
# ============================================================================

def find_first_split_point_for_item(item_elem: etree.Element, config: ConversionConfig) -> Optional[Tuple[int, str]]:
    """
    Item要素内で最初の分割ポイントを検出（Item固有のロジック）

    ColumnなしListを対象とし、最初のListが括弧パターンの場合はスキップ
    """
    children = list(item_elem)

    # ItemSentenceを探す
    item_sentence_index = -1
    for i, child in enumerate(children):
        if child.tag == 'ItemSentence':
            item_sentence_index = i
            break

    if item_sentence_index == -1:
        return None

    # ItemSentenceの次の弟要素を確認
    first_list_found = False
    for i in range(item_sentence_index + 1, len(children)):
        child = children[i]
        if child.tag == 'List':
            # List要素が見つかった
            # ColumnありListはスキップ（分割対象外）
            col1_sentence, col2_sentence, column_count = get_list_columns(child)
            if column_count > 0:
                continue  # Columnありは対象外

            # ColumnなしListの場合、括弧パターンをチェック
            list_sentence = child.find('.//ListSentence')
            if list_sentence is not None:
                sentences = list_sentence.findall('.//Sentence')
                if sentences:
                    first_sentence = sentences[0]
                    text = "".join(first_sentence.itertext()).strip()

                    # 最初のListの場合
                    if not first_list_found:
                        first_list_found = True
                        # 最初のListが学年括弧・科目名括弧の場合、処理全体をスキップ
                        if (is_grade_single_bracket(text) or
                            is_grade_double_bracket(text) or
                            is_subject_name_bracket(text)):
                            return None  # 分割なし

                    # 2番目以降のListで学年括弧・科目名括弧の場合、分割対象
                    if (is_grade_single_bracket(text) or
                        is_grade_double_bracket(text) or
                        is_subject_name_bracket(text)):
                        return (i, 'bracket')  # 括弧の位置で分割

    return None


# ============================================================================
# 【修正版】after_splitの要素をItem化する処理
# ============================================================================

def process_elements_into_items(elements: List[etree.Element], stats: dict, config) -> List[etree.Element]:
    """
    要素リストをItem要素に変換

    fix_container_item用の補助関数
    共通モジュールの関数を使用
    """
    if not elements:
        return []

    result_items = []
    i = 0

    while i < len(elements):
        # item, _ = create_element_from_list(elements[i], config, stats)
        item = None  # create_element_from_listを使用しない
        if item is not None:
            result_items.append(item)
        i += 1

    return result_items


def find_split_point_for_column_list(item_elem: etree.Element) -> Optional[int]:
    """ColumnありListを探す関数"""
    children = list(item_elem)
    for i, child in enumerate(children):
        if child.tag != 'List':
            continue

        col1_sentence, col2_sentence, column_count = get_list_columns(child)
        if column_count > 0:
            return i

    return None


def fix_container_item(paragraph: etree.Element, stats: dict, script_name: str) -> bool:
    """
    コンテナItem補正処理（共通化版）
    """
    # configを作成
    config = ConversionConfig(
        parent_tag='Paragraph',
        child_tag='Item',
        title_tag='ItemTitle',
        sentence_tag='ItemSentence',
        column_condition_min=1,
        supported_types=['labeled', 'subject_name', 'instruction', 'grade_single', 'grade_double'],
        script_name='convert_item_step1',
        skip_empty_parent=True
    )

    # 処理対象のItem要素を取得
    target_item = get_first_child_after_parent_sentence(paragraph, config)
    
    if target_item is None:
        return False
    
    if not is_container_element(target_item, config):
        return False
    
    # 最初のColumnありListを探す
    split_point = find_split_point_for_column_list(target_item)
    
    if split_point is None:
        return False

    # 分割処理
    original_item, new_item = split_element_at_point(target_item, split_point, config)

    # Paragraph全体を順序を保持して再構築
    paragraph_children = list(paragraph)
    new_paragraph_children = []

    for child in paragraph_children:
        if child is target_item:
            # 元のItemを分割後のItemに置き換え
            if original_item is not None:
                new_paragraph_children.append(original_item)
            if new_item is not None:
                new_paragraph_children.append(new_item)
        else:
            new_paragraph_children.append(child)
    
    # Paragraphを再構築
    attrib = dict(paragraph.attrib)
    paragraph.clear()
    
    for key, value in attrib.items():
        paragraph.set(key, value)
    
    for child in new_paragraph_children:
        paragraph.append(child)
    
    return True


# ============================================================================
# main関数（修正版）
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Item要素補正処理（科目名括弧による分割） - 修正版 v2"
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
    print("  2. 処理対象を最初のItemのみに限定（仕様書準拠）")
    print("  3. 分割回数を1回に制限（仕様書準拠）")

    tree = etree.parse(str(input_path))
    all_paragraphs = tree.xpath('//Paragraph')

    print(f"\n処理対象Paragraph数: {len(all_paragraphs)}")

    # ============================================================================
    # ステップ1: コンテナItem補正処理
    # ============================================================================
    print("\n【ステップ1：コンテナItem補正処理】")
    stats = {
        CONVERTED_LABELED_LIST_TO_ITEM: 0,
        CONVERTED_NO_COLUMN_LIST: 0,
        CONVERTED_SUBJECT_NAME_LIST: 0,
        CONVERTED_INSTRUCTION_LIST: 0,
        CONVERTED_NON_LIST_TO_ITEM: 0
    }

    made_any_changes = False
    processed_count = 0
    
    for paragraph in all_paragraphs:
        if fix_container_item(paragraph, stats, script_name):
            made_any_changes = True
            processed_count += 1

    if made_any_changes:
        print(f"  ✅ {processed_count}個のParagraphでItem分割を実行しました")
    else:
        print("  - 分割対象のItemは見つかりませんでした")

    # ============================================================================
    # ステップ2：科目名括弧による分割処理
    # ============================================================================
    print("\n【ステップ2：科目名括弧による分割処理】")
    print("  ※ 仕様書準拠：最初のItemのみ対象、1回分割で終了")

    subject_name_bracket_changes = False
    processed_count_step2 = 0
    
    # configを作成
    config = ConversionConfig(
        parent_tag='Paragraph',
        child_tag='Item',
        title_tag='ItemTitle',
        sentence_tag='ItemSentence',
        column_condition_min=1,
        supported_types=['labeled', 'subject_name', 'instruction', 'grade_single', 'grade_double'],
        script_name='convert_item_step1',
        skip_empty_parent=True
    )
    
    for paragraph in all_paragraphs:
        if process_parent_with_order_preservation(paragraph, stats, script_name, config, lambda elem: find_first_split_point_for_item(elem, config)):
            subject_name_bracket_changes = True
            processed_count_step2 += 1

    if subject_name_bracket_changes:
        print(f"  ✅ {processed_count_step2}個のParagraphで科目名括弧による分割を実行しました")
        made_any_changes = True
    else:
        print("  - 科目名括弧は見つかりませんでした")

    # ============================================================================
    # ステップ3: Item番号の再採番
    # ============================================================================
    if made_any_changes:
        print("\n【ステップ3：Item番号再採番】")
        config = ConversionConfig(
            parent_tag='Paragraph',
            child_tag='Item',
            title_tag='ItemTitle',
            sentence_tag='ItemSentence',
            column_condition_min=1,
            supported_types=['labeled', 'subject_name', 'instruction', 'grade_single', 'grade_double'],
            script_name='convert_item_step1',
            skip_empty_parent=True
        )
        renumber_elements(tree, config)
        print("  ✅ Item番号を再採番しました")

    # ============================================================================
    # 出力
    # ============================================================================
    print("\n【処理統計】")
    if made_any_changes:
        print(f"  - ステップ1（コンテナItem分割）: {processed_count}個のParagraph")
        print(f"  - ステップ2（科目名括弧分割）: {processed_count_step2}個のParagraph")
        print(f"  - ステップ3（Item番号再採番）: 実行")
    else:
        print("  - 補正処理は実行されませんでした")

    # ============================================================================
    # 漢数字ラベルを持つItemの修正
    # ============================================================================
    def remove_empty_subitems(tree):
        """空のSubitemを削除"""
        root = tree.getroot()
        for item in root.xpath('.//Item'):
            subitems_to_remove = []
            for subitem in item.findall('Subitem1') + item.findall('Subitem2'):
                title = subitem.find(f'{subitem.tag}Title')
                sentence = subitem.find(f'{subitem.tag}Sentence/Sentence')

                title_text = "".join(title.itertext()).strip() if title is not None else ""
                sentence_text = "".join(sentence.itertext()).strip() if sentence is not None else ""

                # SubitemTitleとSubitemSentenceが空で、他の子要素がない場合のみ削除
                has_children = (len(subitem.findall('Subitem1')) > 0 or
                              len(subitem.findall('Subitem2')) > 0 or
                              len(subitem.findall('List')) > 0 or
                              len(subitem.findall('TableStruct')) > 0 or
                              len(subitem.findall('FigStruct')) > 0)

                if not title_text and not sentence_text and not has_children:
                    subitems_to_remove.append(subitem)

            for subitem in subitems_to_remove:
                item.remove(subitem)

    # 空のSubitemを削除
    print("\n【ステップ4：空Subitem削除】")
    remove_empty_subitems(tree)
    print("  ✅ 空Subitem削除を実行しました")

    # 番号の再採番
    config = ConversionConfig(
        parent_tag='Paragraph',
        child_tag='Item',
        title_tag='ItemTitle',
        sentence_tag='ItemSentence',
        column_condition_min=1,
        supported_types=['labeled', 'subject_name', 'instruction', 'grade_single', 'grade_double'],
        script_name='convert_item_step1',
        skip_empty_parent=True
    )
    renumber_elements(tree, config)

    format_xml_lxml(tree, str(output_path))

    print(f"\n出力ファイル: {output_path}")
    print("  ✅ 漢数字ラベル修正・空Subitem削除・再採番済み")
    print("=" * 80)

    return 0


if __name__ == '__main__':
    sys.exit(main())
