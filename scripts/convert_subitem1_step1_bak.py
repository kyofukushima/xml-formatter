#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Subitem1要素補正ロジック（処理3）実装スクリプト

convert_subitem1_step0.pyによって生成されたXMLを走査し、特定の「コンテナSubitem1」を分割・補正する。

処理フロー：
1. Itemの直後にある、空のSubitem1（コンテナSubitem1）を特定する。
2. コンテナSubitem1内を走査し、最初に登場する「分割対象のList」（ラベル付き or 括弧付き）を見つける。
3. 分割対象のListが見つかった場合、その手前でSubitem1を分割する。
4. 分割対象のList以降の要素は、`convert_subitem1_step0.py`のロジックを再利用して、新しいSubitem1要素群として再構成する。
5. 元のコンテナSubitem1の後に、新しく生成されたSubitem1要素群を挿入する。
6. 最後にItem内の全Subitem1の番号を再採番する。

参照:
- scripts/education_script/reports/SUBITEM1_LOGIC_SPECIFICATION.md (処理3)
"""

import sys
import argparse
import re
from pathlib import Path
from lxml import etree
from typing import Optional, Tuple, List
from copy import deepcopy

# 親ディレクトリのutils/とstep0の関数をインポート
sys.path.insert(0, str(Path(__file__).resolve().parent))
from convert_subitem1_step0 import (
    format_xml_lxml,
    is_subject_name_bracket,
    is_instruction_bracket,
    get_list_columns,
    get_list_text,
    create_empty_subitem1,
    renumber_subitem1s
)
# label_utilsはconvert_subitem1_step0にはないので直接インポート
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils.label_utils import get_hierarchy_level, is_label
sys.path.pop(0)


def is_container_subitem1(subitem1_elem: etree.Element) -> bool:
    """Subitem1が空のコンテナかチェック"""
    if subitem1_elem is None or subitem1_elem.tag != 'Subitem1':
        return False
        
    subitem1_title = subitem1_elem.find('Subitem1Title')
    subitem1_sentence = subitem1_elem.find('Subitem1Sentence/Sentence')
    
    is_title_empty = (subitem1_title is None) or (not subitem1_title.text and len(subitem1_title) == 0)
    is_sentence_empty = (subitem1_sentence is None) or (not subitem1_sentence.text and len(subitem1_sentence) == 0)
    
    return is_title_empty and is_sentence_empty


def find_split_point(container_subitem1: etree.Element) -> int:
    """コンテナSubitem1内の分割点のインデックスを返す"""
    for i, child in enumerate(container_subitem1):
        if child.tag == 'List':
            col1_sentence, _, col_count = get_list_columns(child)
            col1_text = "".join(col1_sentence.itertext()).strip() if col1_sentence is not None else ""
            
            list_text = get_list_text(child)

            if (col_count >= 1 and col1_text and is_label(col1_text)) or \
               (list_text and is_subject_name_bracket(list_text)) or \
               (list_text and is_instruction_bracket(list_text)):
                return i
    return -1


def process_elements_into_subitem1s(elements_to_process: List[etree.Element]) -> List[etree.Element]:
    """
    要素のリストを、新しい単一のコンテナSubitem1に格納して返す
    """
    if not elements_to_process:
        return []

    new_container_subitem1 = create_empty_subitem1()
    
    for elem in elements_to_process:
        new_container_subitem1.append(deepcopy(elem))
        
    return [new_container_subitem1]


def fix_container_subitem1(item: etree.Element) -> bool:
    """
    Item内のコンテナSubitem1を探索し、分割処理を行う
    """
    all_children = list(item)
    
    first_subitem1_index = -1
    for i, child in enumerate(all_children):
        if child.tag == 'Subitem1':
            first_subitem1_index = i
            break
    
    if first_subitem1_index == -1:
        return False

    siblings_to_process = all_children[first_subitem1_index:]
    if not siblings_to_process:
        return False

    container_subitem1 = siblings_to_process[0]
    if not is_container_subitem1(container_subitem1):
        return False

    split_index = find_split_point(container_subitem1)
    if split_index == -1:
        return False

    print(f"  - Found container subitem1 to split in parent Item")

    prefix_children = all_children[:first_subitem1_index]
    trailing_siblings = [deepcopy(s) for s in siblings_to_process[1:]]
    
    children_of_container = list(container_subitem1)
    elements_before_split = children_of_container[:split_index]
    elements_after_split = children_of_container[split_index:]

    container_subitem1.clear()
    for elem in elements_before_split:
        container_subitem1.append(elem)

    new_subitem1s = process_elements_into_subitem1s(elements_after_split)

    final_children = prefix_children + [container_subitem1] + new_subitem1s + trailing_siblings
    
    for child in list(item):
        item.remove(child)
        
    for child in final_children:
        item.append(deepcopy(child))
        
    return True


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description='Subitem1要素補正ロジック（処理3）実装スクリプト',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('input_file', help='入力XMLファイル (convert_subitem1_step0.pyの出力)')
    parser.add_argument('output_file', nargs='?', help='出力XMLファイル（デフォルト: <input>_subitem1_step1.xml）')
    
    args = parser.parse_args()
    
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"エラー: 入力ファイルが見つかりません: {args.input_file}", file=sys.stderr)
        return 1
        
    output_path = Path(args.output_file) if args.output_file else input_path.parent / f"{input_path.stem}_subitem1_step1.xml"

    print("=" * 80)
    print("【Subitem1要素補正ロジック（処理3）】")
    print("=" * 80)
    print(f"入力ファイル: {input_path}")

    try:
        tree = etree.parse(str(input_path))
    except Exception as e:
        print(f"エラー: XMLファイルの読み込みに失敗しました: {e}", file=sys.stderr)
        return 1

    root = tree.getroot()
    all_items = root.xpath('.//Item')
    
    made_any_changes = False
    for item in all_items:
        if fix_container_subitem1(item):
            made_any_changes = True

    if made_any_changes:
        renumber_subitem1s(tree)

    format_xml_lxml(tree, str(output_path))
    
    print(f"\n出力ファイル: {output_path}")
    print("  ✅ 処理完了")
    print("=" * 80)

    return 0


if __name__ == '__main__':
    sys.exit(main())