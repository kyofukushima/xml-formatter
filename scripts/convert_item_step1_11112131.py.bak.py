#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Item要素補正ロジック（処理3）実装スクリプト

convert_item_step0.pyによって生成されたXMLを走査し、特定の「コンテナItem」を分割・補正する。

処理フロー：
1. ParagraphSentenceの直後にある、空のItem（コンテナItem）を特定する。
2. コンテナItem内を走査し、最初に登場する「分割対象のList」（ラベル付き or 括弧付き）を見つける。
3. 分割対象のListが見つかった場合、その手前でItemを分割する。
4. 分割対象のList以降の要素は、`convert_item_step0.py`のロジックを再利用して、新しいItem要素群として再構成する。
5. 元のコンテナItemの後に、新しく生成されたItem要素群を挿入する。
6. 最後にParagraph内の全Itemの番号を再採番する。

参照:
- scripts/education_script/reports/ITEM_LOGIC_SPECIFICATION.md (処理3)
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


def is_container_item(item_elem: etree.Element) -> bool:
    """Itemが空のコンテナかチェック"""
    if item_elem is None or item_elem.tag != 'Item':
        return False
        
    item_title = item_elem.find('ItemTitle')
    item_sentence = item_elem.find('ItemSentence/Sentence')
    
    # タイトルと文章が両方とも空かチェック
    is_title_empty = (item_title is None) or (not item_title.text and len(item_title) == 0)
    is_sentence_empty = (item_sentence is None) or (not item_sentence.text and len(item_sentence) == 0)
    
    return is_title_empty and is_sentence_empty


def find_split_point(container_item: etree.Element) -> int:
    """コンテナItem内の分割点のインデックスを返す"""
    for i, child in enumerate(container_item):
        if child.tag == 'List':
            col1_sentence, _, col_count = get_list_columns(child)
            col1_text = "".join(col1_sentence.itertext()).strip() if col1_sentence is not None else ""
            
            list_text = get_list_text(child)

            # 分割対象のListかチェック
            if (col_count >= 1 and col1_text and is_label(col1_text)) or \
               (list_text and is_subject_name_bracket(list_text)) or \
               (list_text and is_instruction_bracket(list_text)):
                return i # 分割点のインデックスを返す
    return -1 # 分割点なし

def is_section_heading_list(list_elem: etree.Element) -> bool:
    """
    Listが〔科目名〕パターンの見出しかどうか判定
    
    判定条件:
    - ListSentence/Sentence のテキストが 〔 で始まり 〕 で終わる
    - Column が存在しない（または Column が1つのみで内容が見出し）
    
    Args:
        list_elem: 判定対象のList要素
        
    Returns:
        bool: 科目見出しの場合True
    """
    if list_elem is None or list_elem.tag != 'List':
        return False
    
    # ListSentence内のSentenceを取得
    list_sentence = list_elem.find('.//ListSentence')
    if list_sentence is None:
        return False
    
    # Columnがある場合は対象外
    columns = list_sentence.findall('.//Column')
    if columns and len(columns) > 1:
        return False
    
    # Sentenceのテキストを取得
    sentences = list_sentence.findall('.//Sentence')
    if not sentences:
        return False
    
    # 最初のSentenceのテキストをチェック
    first_sentence = sentences[0]
    text = first_sentence.text.strip() if first_sentence.text else ""
    
    # 〔で始まり〕で終わるパターンかチェック
    if text.startswith('〔') and text.endswith('〕'):
        return True
    
    return False


def extract_section_heading_from_item(item_elem: etree.Element) -> List[Tuple[int, etree.Element]]:
    """
    Item要素内のListを走査し、〔科目名〕パターンのListを抽出
    
    Args:
        item_elem: 走査対象のItem要素
        
    Returns:
        List[Tuple[int, etree.Element]]: (インデックス, List要素) のリスト
    """
    section_headings = []
    
    for i, child in enumerate(item_elem):
        if child.tag == 'List' and is_section_heading_list(child):
            section_headings.append((i, child))
    
    return section_headings


def process_elements_into_items(elements_to_process: List[etree.Element], stats: dict, script_name: str) -> List[etree.Element]:
    """
    要素のリストを、新しい単一のコンテナItemに格納して返す
    """
    if not elements_to_process:
        return []

    # 新しい空のコンテナItemを作成
    # create_item_from_element は、引数がListでない場合、空のItemを作成して要素を追加するロジックを持たないため、
    # ここでは直接 create_empty_item を呼び出すのが適切。
    # ただし、最初の要素を create_item_from_element に渡してItem化し、残りをappendする方が元の設計思想に近い。
    # 今回のユーザーの期待値は「新しいコンテナにすべてを移動」なので、よりシンプルな実装を選択する。
    
    new_container_item = create_empty_item()
    
    # 分割点以降のすべての要素を、新しいコンテナItemにそのまま移動
    for elem in elements_to_process:
        new_container_item.append(deepcopy(elem))
        
    # このスクリプトはあくまで分割が主目的であり、分割後の要素のItem化は後続のスクリプトに委ねるべきかもしれないが、
    # ユーザーの期待値と「処理3の再実行は不要」という仕様に基づき、ここではコンテナ化のみを行う。
    # statsのカウントは、このスクリプトの責務を考えると不要かもしれないが、一旦残す。
    # 例えば、分割のきっかけとなった要素の種類をカウントするなど。
    # 今回の修正では、この関数内でのstatsの更新は行わない。

    return [new_container_item]


def fix_container_item(paragraph: etree.Element, stats: dict, script_name: str) -> bool:
    """
    Paragraph内のコンテナItemを探索し、分割処理を行う
    """
    para_sentence = paragraph.find('ParagraphSentence')
    if para_sentence is None:
        return False

    all_children = list(paragraph)
    try:
        ps_index = all_children.index(para_sentence)
    except ValueError:
        return False # ParagraphSentence が見つからない(通常発生しない)

    siblings_to_process = all_children[ps_index + 1:]
    if not siblings_to_process:
        return False

    container_item = siblings_to_process[0]
    if not is_container_item(container_item):
        return False

    split_index = find_split_point(container_item)
    if split_index == -1:
        return False

    print(f"  - Found container item to split in Paragraph Num='{paragraph.get('Num', '')}'")

    # --- Define all pieces before modification ---
    prefix_children = all_children[:ps_index + 1]
    trailing_siblings = siblings_to_process[1:]
    
    children_of_container = list(container_item)
    elements_before_split = children_of_container[:split_index]
    elements_after_split = children_of_container[split_index:]

    # --- Create new elements from the pieces ---
    # Modify container
    container_item.clear()
    for elem in elements_before_split:
        container_item.append(elem)

    # Create new items from the split part
    new_items = process_elements_into_items(elements_after_split, stats, script_name)

    # --- Assemble final list of children ---
    final_children = prefix_children + [container_item] + new_items + trailing_siblings
    
    # --- Rebuild the paragraph ---
    # Clear paragraph while preserving attributes
    for child in list(paragraph):
        paragraph.remove(child)
        
    # Append deep copies of all final children to be safe
    for child in final_children:
        paragraph.append(deepcopy(child))
        
    return True

def split_item_by_section_headings(item_elem: etree.Element) -> List[etree.Element]:
    """
    Item要素内の〔科目名〕パターンで分割し、複数のItem要素を生成
    
    Args:
        item_elem: 分割対象のItem要素
        
    Returns:
        List[etree.Element]: 分割後のItem要素のリスト
    """
    section_headings = extract_section_heading_from_item(item_elem)
    
    # 〔科目名〕パターンが見つからない場合は元のItemをそのまま返す
    if not section_headings:
        return [item_elem]
    
    result_items = []
    children = list(item_elem)
    current_start = 0
    
    for heading_index, heading_list in section_headings:
        # 見出しの前までの要素を処理
        if heading_index > current_start:
            # 前のセクションの要素を元のItemに保持
            if not result_items:
                # 最初のセクション（元のItemを再利用）
                new_item = item_elem
                new_item.clear()
                # 元のItemの属性をコピー
                for key, value in item_elem.attrib.items():
                    new_item.set(key, value)
                
                # 前の要素を追加
                for child in children[current_start:heading_index]:
                    new_item.append(deepcopy(child))
                
                result_items.append(new_item)
        
        # 〔科目名〕見出しを新しいItemとして作成
        section_item = etree.Element('Item')
        section_item_title = etree.SubElement(section_item, 'ItemTitle')
        section_item_sentence = etree.SubElement(section_item, 'ItemSentence')
        
        # ListSentence内のSentenceを取得してItemSentenceに変換
        list_sentence = heading_list.find('.//ListSentence')
        if list_sentence is not None:
            for sentence in list_sentence.findall('.//Sentence'):
                section_item_sentence.append(deepcopy(sentence))
        
        result_items.append(section_item)
        
        current_start = heading_index + 1
    
    # 最後のセクション以降の要素を処理
    if current_start < len(children):
        last_item = create_empty_item()
        for child in children[current_start:]:
            last_item.append(deepcopy(child))
        result_items.append(last_item)
    
    return result_items


def process_section_headings_in_paragraph(paragraph: etree.Element) -> bool:
    """
    Paragraph内のすべてのItemを走査し、〔科目名〕パターンで分割
    
    Args:
        paragraph: 処理対象のParagraph要素
        
    Returns:
        bool: 分割処理が実行された場合True
    """
    all_items = list(paragraph.findall('.//Item'))
    
    if not all_items:
        return False
    
    made_changes = False
    new_items = []
    
    for item in all_items:
        # 各Itemを分割処理
        split_items = split_item_by_section_headings(item)
        
        if len(split_items) > 1:
            made_changes = True
            print(f"  - Split Item Num='{item.get('Num', '')}' into {len(split_items)} items (section headings detected)")
        
        new_items.extend(split_items)
    
    if made_changes:
        # Paragraph内のItemを置き換え
        for item in all_items:
            paragraph.remove(item)
        
        for new_item in new_items:
            paragraph.append(new_item)
    
    return made_changes



def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description='Item要素補正ロジック（処理3）実装スクリプト',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('input_file', help='入力XMLファイル (convert_item_step0.pyの出力)')
    parser.add_argument('output_file', nargs='?', help='出力XMLファイル（デフォルト: <input>_item_step1.xml）')
    
    args = parser.parse_args()
    
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"エラー: 入力ファイルが見つかりません: {args.input_file}", file=sys.stderr)
        return 1
        
    output_path = Path(args.output_file) if args.output_file else input_path.parent / f"{input_path.stem}_item_step1.xml"

    print("=" * 80)
    print("【Item要素補正ロジック（処理3）】")
    print("  仕様書: scripts/education_script/reports/ITEM_LOGIC_SPECIFICATION.md (処理3)")
    print("=" * 80)
    print(f"入力ファイル: {input_path}")

    script_name = Path(__file__).name

    try:
        tree = etree.parse(str(input_path))
    except Exception as e:
        print(f"エラー: XMLファイルの読み込みに失敗しました: {e}", file=sys.stderr)
        return 1

    # 統計情報はstep0から引き継ぐが、このスクリプトでの変換分をカウント
    stats = {
        CONVERTED_LABELED_LIST_TO_ITEM: 0,
        CONVERTED_NO_COLUMN_LIST: 0,
        CONVERTED_SUBJECT_NAME_LIST: 0,
        CONVERTED_INSTRUCTION_LIST: 0,
        CONVERTED_NON_LIST_TO_ITEM: 0,
    }

    root = tree.getroot()
    all_paragraphs = root.xpath('.//Paragraph')
    
    made_any_changes = False
    for paragraph in all_paragraphs:
        # 1つのParagraphで1回分割が起きたら終了
        if fix_container_item(paragraph, stats, script_name):
            made_any_changes = True

    # ★★★ 追加：〔科目名〕パターンの分割処理 ★★★
    print("\n【〔科目名〕パターンの分割処理】")
    section_heading_changes = False
    for paragraph in all_paragraphs:
        if process_section_headings_in_paragraph(paragraph):
            section_heading_changes = True
    
    if section_heading_changes:
        print("  ✅ 〔科目名〕パターンによる分割が実行されました")
        made_any_changes = True
    else:
        print("  - 〔科目名〕パターンは見つかりませんでした")
    # ★★★ 追加終了 ★★★

    if made_any_changes:
        print("\n補正処理による変換統計:")
        print(f"  - ラベル付きListからのItem化: {stats[CONVERTED_LABELED_LIST_TO_ITEM]}箇所")
        print(f"  - 科目名ListからのItem化: {stats[CONVERTED_SUBJECT_NAME_LIST]}箇所")
        print(f"  - 指導項目ListからのItem化: {stats[CONVERTED_INSTRUCTION_LIST]}箇所")
    else:
        print("\n補正処理は実行されませんでした。")

    # 変更があった場合のみ再採番
    if made_any_changes:
        renumber_items(tree)

    format_xml_lxml(tree, str(output_path))
    
    print(f"\n出力ファイル: {output_path}")
    print("  ✅ 処理完了")
    print("=" * 80)

    return 0


if __name__ == '__main__':
    sys.exit(main())
