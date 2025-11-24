#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Item要素補正ロジック（処理3）実装スクリプト - 修正版

【修正内容】
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

# 親ディレクトリのutils/とstep0の関数をインポート
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils.label_utils import get_hierarchy_level, is_label
sys.path.pop(0)

sys.path.insert(0, str(Path(__file__).resolve().parent))
from convert_item_step0 import (
    format_xml_lxml,
    is_subject_name_bracket,
    is_instruction_bracket,
    get_list_columns,
    get_list_text,
    create_item_from_element,
    create_empty_item,
    are_same_hierarchy,
    renumber_items,
    CONVERTED_LABELED_LIST_TO_ITEM,
    CONVERTED_NO_COLUMN_LIST,
    CONVERTED_SUBJECT_NAME_LIST,
    CONVERTED_INSTRUCTION_LIST,
    CONVERTED_NON_LIST_TO_ITEM
)

# ============================================================================
# 既存の関数（変更なし）
# ============================================================================

def is_container_item(item_elem: etree.Element) -> bool:
    """既存の関数（変更なし）"""
    if item_elem is None or item_elem.tag != 'Item':
        return False

    item_title = item_elem.find('.//ItemTitle')
    if item_title is None or item_title.text:
        return False

    item_sentence = item_elem.find('.//ItemSentence')
    if item_sentence is None:
        return False

    return True


def find_split_point(item_elem: etree.Element) -> Optional[int]:
    """既存の関数（変更なし）"""
    children = list(item_elem)
    for i, child in enumerate(children):
        if child.tag != 'List':
            continue

        columns = get_list_columns(child)
        if columns and len(columns) > 0:
            return i

    return None


def process_elements_into_items(elements: List[etree.Element], stats: dict) -> List[etree.Element]:
    """既存の関数（変更なし）"""
    if not elements:
        return []

    result_items = []
    i = 0

    while i < len(elements):
        item, _ = create_item_from_element(elements[i], stats)
        if item is not None:
            result_items.append(item)
        i += 1

    return result_items


def fix_container_item(paragraph: etree.Element, stats: dict, script_name: str) -> bool:
    """既存の関数（変更なし）"""
    all_items = list(paragraph.findall('.//Item'))

    for item in all_items:
        if not is_container_item(item):
            continue

        split_point = find_split_point(item)
        if split_point is None:
            continue

        children = list(item)
        before_split = children[:split_point]
        after_split = children[split_point:]

        item.clear()
        for key, value in all_items[0].attrib.items():
            item.set(key, value)

        for elem in before_split:
            item.append(elem)

        new_items = process_elements_into_items(after_split, stats)
        item_index = list(paragraph).index(item)

        for new_item in new_items:
            paragraph.insert(item_index + 1, new_item)
            item_index += 1

        return True

    return False


# ============================================================================
# 【修正版】科目名括弧のみの判定関数
# ============================================================================

def is_subject_name_bracket_only(sentence_elem: etree.Element) -> bool:
    """
    判定：Sentenceが「科目名括弧のみ」パターンかどうか

    科目名括弧: 〔医療と社会〕、〔人体の構造と機能〕 など
    指導項目括弧: 〔指導項目〕、〔指導項目〕の（１）... など

    例：
      ✓ 〔医療と社会〕
      ✓ 〔人体の構造と機能〕
      ✗ 〔指導項目〕
      ✗ 〔指導項目〕の（１）...
    """
    if sentence_elem is None or sentence_elem.tag != 'Sentence':
        return False

    text = sentence_elem.text.strip() if sentence_elem.text else ""

    # 最小条件：〔で始まり〕で終わる
    if not (text.startswith('〔') and text.endswith('〕')):
        return False

    # 〔...〕の中身を抽出
    bracketed = text[1:-1]

    # 指導項目括弧パターンを除外
    if bracketed == '指導項目':
        return False

    if '指導項目' in bracketed and 'の' in bracketed:
        return False

    # 科目名括弧と判定
    return True


# ============================================================================
# 【修正版】Item内の科目名括弧Listを抽出
# ============================================================================

def extract_subject_name_brackets_from_item(item_elem: etree.Element) -> List[Tuple[int, etree.Element]]:
    """
    Item要素内のListを走査し、「科目名括弧のみ」のListを抽出

    重要：
    - 「科目名括弧のみ」のListのみを対象
    - 「指導項目括弧」のListは除外
    """
    subject_brackets = []

    for i, child in enumerate(item_elem):
        if child.tag != 'List':
            continue

        list_sentence = child.find('.//ListSentence')
        if list_sentence is None:
            continue

        sentences = list_sentence.findall('.//Sentence')
        if not sentences:
            continue

        # 最初のSentenceをチェック
        first_sentence = sentences[0]

        # 【重要】科目名括弧のみかチェック（指導項目括弧は除外）
        if is_subject_name_bracket_only(first_sentence):
            subject_brackets.append((i, child))

    return subject_brackets


# ============================================================================
# 【修正版】Item分割処理
# ============================================================================

def split_item_by_subject_name_brackets(item_elem: etree.Element) -> List[etree.Element]:
    """
    Item要素内の「科目名括弧のみ」で分割し、複数のItem要素を生成
    """
    subject_brackets = extract_subject_name_brackets_from_item(item_elem)

    if not subject_brackets:
        return [item_elem]

    result_items = []
    children = list(item_elem)
    current_start = 0

    for bracket_index, bracket_list in subject_brackets:
        # 括弧の前までの要素を処理
        if bracket_index > current_start:
            if not result_items:
                # 最初のセクション（元のItemを再利用）
                new_item = deepcopy(item_elem)
                new_item.clear()
                for key, value in item_elem.attrib.items():
                    new_item.set(key, value)

                for child in children[current_start:bracket_index]:
                    new_item.append(deepcopy(child))

                result_items.append(new_item)

        # 「科目名括弧のみ」を新しいItemとして作成
        subject_item = etree.Element('Item')
        subject_item_title = etree.SubElement(subject_item, 'ItemTitle')
        subject_item_sentence = etree.SubElement(subject_item, 'ItemSentence')

        list_sentence = bracket_list.find('.//ListSentence')
        if list_sentence is not None:
            for sentence in list_sentence.findall('.//Sentence'):
                subject_item_sentence.append(deepcopy(sentence))

        result_items.append(subject_item)

        current_start = bracket_index + 1

    # 最後のセクション以降の要素を処理
    if current_start < len(children):
        last_item = create_empty_item()
        for child in children[current_start:]:
            last_item.append(deepcopy(child))
        result_items.append(last_item)

    return result_items


# ============================================================================
# 【修正版】Paragraph単位での処理
# ============================================================================

def process_subject_name_brackets_in_paragraph(paragraph: etree.Element) -> bool:
    """
    Paragraph内のすべてのItemを走査し、「科目名括弧」で分割

    重要：指導項目括弧（〔指導項目〕）では分割しない
    """
    all_items = list(paragraph.findall('.//Item'))

    if not all_items:
        return False

    made_changes = False
    new_items = []

    for item in all_items:
        split_items = split_item_by_subject_name_brackets(item)

        if len(split_items) > 1:
            made_changes = True
            print(f"  - Split Item Num='{item.get('Num', '')}' into {len(split_items)} items (subject name brackets detected)")

        new_items.extend(split_items)

    if made_changes:
        for item in all_items:
            paragraph.remove(item)

        for new_item in new_items:
            paragraph.append(new_item)

    return made_changes


# ============================================================================
# main関数（修正版）
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Item要素補正処理（科目名括弧による分割）"
    )
    parser.add_argument('input_file', help='入力XMLファイル')
    parser.add_argument('output_file', help='出力XMLファイル')

    args = parser.parse_args()

    input_path = Path(args.input_file)
    output_path = Path(args.output_file)

    script_name = Path(__file__).name

    print("=" * 80)
    print(f"【{script_name}】実行開始")
    print("=" * 80)
    print(f"入力ファイル: {input_path}")
    print(f"出力ファイル: {output_path}")

    tree = etree.parse(str(input_path))
    all_paragraphs = tree.xpath('//Paragraph')

    print(f"\n処理対象Paragraph数: {len(all_paragraphs)}")

    # ============================================================================
    # ステップ1: 既存の補正処理（コンテナItem分割）
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
    for paragraph in all_paragraphs:
        if fix_container_item(paragraph, stats, script_name):
            made_any_changes = True

    # ============================================================================
    # ステップ2: 【修正版】科目名括弧による分割処理
    # ============================================================================
    print("\n【ステップ2：科目名括弧（Subject Name Bracket）の分割処理】")
    print("  ※ 指導項目括弧（〔指導項目〕）は分割対象外")

    subject_name_bracket_changes = False
    for paragraph in all_paragraphs:
        if process_subject_name_brackets_in_paragraph(paragraph):
            subject_name_bracket_changes = True

    if subject_name_bracket_changes:
        print("  ✅ 科目名括弧による分割が実行されました")
        made_any_changes = True
    else:
        print("  - 科目名括弧は見つかりませんでした")

    # ============================================================================
    # ステップ3: Item番号の再採番
    # ============================================================================
    if made_any_changes:
        print("\n【ステップ3：Item番号再採番】")
        renumber_items(tree)
        print("  ✅ Item番号を再採番しました")

    # ============================================================================
    # 出力
    # ============================================================================
    print("\n【処理統計】")
    if made_any_changes:
        print(f"  - コンテナItem分割: 実行")
        print(f"  - 科目名括弧分割: {'実行' if subject_name_bracket_changes else '不要'}")
    else:
        print("  - 補正処理は実行されませんでした")

    format_xml_lxml(tree, str(output_path))

    print(f"\n出力ファイル: {output_path}")
    print("  ✅ 処理完了")
    print("=" * 80)

    return 0


if __name__ == '__main__':
    sys.exit(main())
