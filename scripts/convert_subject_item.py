#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
科目名Item要素の構造変換スクリプト

括弧書き科目名（〔...〕または【...】）を持つItem要素の直後のItem要素を
Subitem1として科目名Itemの中に取り込む。

処理タイミング: item_step1の後、subitem1_step0の前
"""

import sys
import argparse
import re
from pathlib import Path
from lxml import etree
from copy import deepcopy


def format_xml_lxml(tree, output_path):
    """lxmlのElementTreeをインデント整形して保存"""
    clean_root = etree.fromstring(etree.tostring(tree.getroot()))
    etree.indent(clean_root, space="    ", level=0)
    new_tree = etree.ElementTree(clean_root)
    new_tree.write(
        output_path,
        encoding='utf-8',
        xml_declaration=True,
        pretty_print=False
    )


def is_subject_name_bracket(text: str) -> bool:
    """テキストが括弧付き科目名かチェック（〔...〕または【...】）"""
    if not text:
        return False
    text = text.strip()
    return bool(re.match(r'^[〔【].+[〕】]$', text))


def is_subject_item(item_elem) -> bool:
    """Item要素が科目名Itemかチェック"""
    item_sentence = item_elem.find('ItemSentence/Sentence')
    if item_sentence is None:
        return False
    
    sentence_text = "".join(item_sentence.itertext()).strip()
    return is_subject_name_bracket(sentence_text)


def convert_item_to_subitem1(item_elem):
    """Item要素をSubitem1要素に変換"""
    subitem1 = etree.Element('Subitem1')
    
    # ItemTitleをSubitem1Titleに変換
    item_title = item_elem.find('ItemTitle')
    subitem1_title = etree.SubElement(subitem1, 'Subitem1Title')
    if item_title is not None and item_title.text:
        subitem1_title.text = item_title.text
        for child in item_title:
            subitem1_title.append(deepcopy(child))
    
    # ItemSentenceをSubitem1Sentenceに変換
    item_sentence = item_elem.find('ItemSentence')
    subitem1_sentence = etree.SubElement(subitem1, 'Subitem1Sentence')
    if item_sentence is not None:
        for child in item_sentence:
            subitem1_sentence.append(deepcopy(child))
    
    # 既存のSubitem1要素があればコピー
    for child in item_elem:
        if child.tag == 'Subitem1':
            subitem1.append(deepcopy(child))
        elif child.tag in ['List', 'TableStruct', 'FigStruct', 'StyleStruct']:
            subitem1.append(deepcopy(child))
    
    return subitem1


def process_paragraph(paragraph, stats):
    """Paragraph要素内の科目名Item要素を処理"""
    items = paragraph.findall('Item')
    if not items:
        return False
    
    made_changes = False
    subject_items = []
    
    # 科目名Item要素を検出
    for i, item in enumerate(items):
        if is_subject_item(item):
            subject_items.append((i, item))
    
    if not subject_items:
        return False
    
    # 各科目名Itemについて処理
    for i, (subject_index, subject_item) in enumerate(subject_items):
        # 次の科目名Itemのインデックスを取得
        next_subject_index = subject_items[i + 1][0] if i + 1 < len(subject_items) else len(items)
        
        # 科目名Itemの直後から次の科目名Itemまでの Item要素を収集
        items_to_convert = []
        for j in range(subject_index + 1, next_subject_index):
            items_to_convert.append(items[j])
        
        if items_to_convert:
            # 各Itemを Subitem1に変換して科目名Itemに追加
            for item_to_convert in items_to_convert:
                subitem1 = convert_item_to_subitem1(item_to_convert)
                subject_item.append(subitem1)
                made_changes = True
                stats['converted_items'] += 1
            
            # 変換したItem要素を親から削除
            for item_to_convert in items_to_convert:
                paragraph.remove(item_to_convert)
                stats['removed_items'] += 1
    
    # Item要素のNum属性を再採番
    remaining_items = paragraph.findall('Item')
    for i, item in enumerate(remaining_items):
        item.set('Num', str(i + 1))
    
    # Subitem1のNum属性を再採番
    for item in remaining_items:
        subitems = item.findall('Subitem1')
        for i, subitem in enumerate(subitems):
            subitem.set('Num', str(i + 1))
    
    return made_changes


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description='科目名Item要素の構造変換スクリプト',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
使用例:
python3 convert_subject_item.py input.xml
python3 convert_subject_item.py input.xml output.xml

処理内容:
括弧書き科目名（〔...〕または【...】）を持つItem要素の直後のItem要素を
Subitem1として科目名Itemの中に取り込む。
'''
    )

    parser.add_argument('input_file', help='入力XMLファイル')
    parser.add_argument('output_file', nargs='?', help='出力XMLファイル（デフォルト: _subject.xml）')

    args = parser.parse_args()

    input_path = Path(args.input_file)

    if not input_path.exists():
        print(f"エラー: 入力ファイルが見つかりません: {args.input_file}", file=sys.stderr)
        return 1

    output_path = Path(args.output_file) if args.output_file else input_path.parent / f"{input_path.stem}_subject.xml"

    print("=" * 80)
    print("【科目名Item要素の構造変換】")
    print("=" * 80)
    print(f"入力ファイル: {input_path}")

    try:
        tree = etree.parse(str(input_path))
    except Exception as e:
        print(f"エラー: XMLファイルの読み込みに失敗しました: {e}", file=sys.stderr)
        return 1

    stats = {
        'converted_items': 0,
        'removed_items': 0,
    }

    root = tree.getroot()
    all_paragraphs = root.xpath('.//Paragraph')

    for paragraph in all_paragraphs:
        process_paragraph(paragraph, stats)

    print("\n変換統計:")
    print(f" - 科目名Itemに取り込まれたItem要素: {stats['converted_items']}個")
    print(f" - 削除されたItem要素: {stats['removed_items']}個")

    format_xml_lxml(tree, str(output_path))

    print(f"\n出力ファイル: {output_path}")
    print(" ✅ インデント・再採番済み")
    print("=" * 80)

    return 0


if __name__ == '__main__':
    sys.exit(main())
