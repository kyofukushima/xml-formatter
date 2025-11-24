#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import argparse
import re
from pathlib import Path
from lxml import etree
from typing import Optional, Tuple, List
from copy import deepcopy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from convert_subitem2_step0 import (
    format_xml_lxml,
    is_subject_name_bracket,
    is_instruction_bracket,
    get_list_columns,
    get_list_text,
    create_empty_subitem2,
    renumber_subitem2s
)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils.label_utils import get_hierarchy_level, is_label
sys.path.pop(0)


def is_container_subitem2(subitem2_elem: etree.Element) -> bool:
    if subitem2_elem is None or subitem2_elem.tag != 'Subitem2':
        return False
    subitem2_title = subitem2_elem.find('Subitem2Title')
    subitem2_sentence = subitem2_elem.find('Subitem2Sentence/Sentence')
    is_title_empty = (subitem2_title is None) or (not subitem2_title.text and len(subitem2_title) == 0)
    is_sentence_empty = (subitem2_sentence is None) or (not subitem2_sentence.text and len(subitem2_sentence) == 0)
    return is_title_empty and is_sentence_empty


def find_split_point(container_subitem2: etree.Element) -> int:
    for i, child in enumerate(container_subitem2):
        if child.tag == 'List':
            col1_sentence, _, col_count = get_list_columns(child)
            col1_text = "".join(col1_sentence.itertext()).strip() if col1_sentence is not None else ""
            list_text = get_list_text(child)
            if (col_count >= 1 and col1_text and is_label(col1_text)) or \
               (list_text and is_subject_name_bracket(list_text)) or \
               (list_text and is_instruction_bracket(list_text)):
                return i
    return -1


def process_elements_into_subitem2s(elements_to_process: List[etree.Element]) -> List[etree.Element]:
    if not elements_to_process:
        return []
    new_container_subitem2 = create_empty_subitem2()
    for elem in elements_to_process:
        new_container_subitem2.append(deepcopy(elem))
    return [new_container_subitem2]


def fix_container_subitem2(subitem1: etree.Element) -> bool:
    all_children = list(subitem1)
    first_subitem2_index = -1
    for i, child in enumerate(all_children):
        if child.tag == 'Subitem2':
            first_subitem2_index = i
            break
    if first_subitem2_index == -1:
        return False

    siblings_to_process = all_children[first_subitem2_index:]
    if not siblings_to_process:
        return False

    container_subitem2 = siblings_to_process[0]
    if not is_container_subitem2(container_subitem2):
        return False

    split_index = find_split_point(container_subitem2)
    if split_index == -1:
        return False

    print(f"  - Found container subitem2 to split in parent Subitem1")

    prefix_children = all_children[:first_subitem2_index]
    trailing_siblings = [deepcopy(s) for s in siblings_to_process[1:]]
    
    children_of_container = list(container_subitem2)
    elements_before_split = children_of_container[:split_index]
    elements_after_split = children_of_container[split_index:]

    container_subitem2.clear()
    for elem in elements_before_split:
        container_subitem2.append(elem)

    new_subitem2s = process_elements_into_subitem2s(elements_after_split)

    final_children = prefix_children + [container_subitem2] + new_subitem2s + trailing_siblings
    
    for child in list(subitem1):
        subitem1.remove(child)
        
    for child in final_children:
        subitem1.append(deepcopy(child))
        
    return True


def main():
    parser = argparse.ArgumentParser(
        description='Subitem2要素補正ロジック（処理3）実装スクリプト',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('input_file', help='入力XMLファイル (convert_subitem2_step0.pyの出力)')
    parser.add_argument('output_file', nargs='?', help='出力XMLファイル（デフォルト: <input>_subitem2_step1.xml）')
    
    args = parser.parse_args()
    
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"エラー: 入力ファイルが見つかりません: {args.input_file}", file=sys.stderr)
        return 1
        
    output_path = Path(args.output_file) if args.output_file else input_path.parent / f"{input_path.stem}_subitem2_step1.xml"

    print("=" * 80)
    print("【Subitem2要素補正ロジック（処理3）】")
    print("=" * 80)
    print(f"入力ファイル: {input_path}")

    try:
        tree = etree.parse(str(input_path))
    except Exception as e:
        print(f"エラー: XMLファイルの読み込みに失敗しました: {e}", file=sys.stderr)
        return 1

    root = tree.getroot()
    all_subitem1s = root.xpath('.//Subitem1')
    
    made_any_changes = False
    for subitem1 in all_subitem1s:
        if fix_container_subitem2(subitem1):
            made_any_changes = True

    if made_any_changes:
        renumber_subitem2s(tree)

    format_xml_lxml(tree, str(output_path))
    
    print(f"\n出力ファイル: {output_path}")
    print("  ✅ 処理完了")
    print("=" * 80)

    return 0


if __name__ == '__main__':
    sys.exit(main())