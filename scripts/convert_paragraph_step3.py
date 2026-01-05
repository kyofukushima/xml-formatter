#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Paragraph特化スクリプト - 処理3 (Paragraph分割)

- 処理2-2: ParagraphSentenceの次のList要素が項目ラベル付きの場合
  - ParagraphNumと同じ階層レベルの場合、Paragraphを分割する

前提条件:
- Paragraph特化スクリプト - 処理2 実行済み

参照:
- logic2_3_Paragraph_split.md (新規作成予定)
- 旧 logic2_3_Paragraph_textitem.md の処理2-2
"""

import sys
import argparse
import re
from pathlib import Path
from lxml import etree

# scripts/utils/をインポートパスに追加
script_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(script_dir))

from utils.label_utils import detect_label_id, is_label

def format_xml_lxml(tree, output_path):
    """
    lxmlのElementTreeをインデント整形して保存
    """
    # 文字列化と再パースで空白ノードを正規化し、indent()で確実に整形する
    clean_root = etree.fromstring(etree.tostring(tree.getroot()))
    etree.indent(clean_root, space="  ", level=0)
    new_tree = etree.ElementTree(clean_root)
    
    new_tree.write(
        output_path,
        encoding='utf-8',
        xml_declaration=True,
        pretty_print=False
    )

def get_list_info(list_element):
    """List要素からラベル、内容、Column数を取得する"""
    columns = list_element.findall('.//Column')
    label_text = None
    content_sentence = None

    if len(columns) == 0:
        pass
    elif len(columns) == 2:
        label_elem = columns[0].find('.//Sentence')
        if label_elem is not None and label_elem.text:
            label_text = label_elem.text.strip()
        content_sentence = columns[1].find('.//Sentence')
    
    return label_text, content_sentence, len(columns)

def find_split_point(paragraph):
    """Paragraphの分割点を返す"""
    para_sentence = paragraph.find('ParagraphSentence')
    if not para_sentence:
        return None

    para_num_elem = paragraph.find('ParagraphNum')
    para_num_text = para_num_elem.text.strip() if para_num_elem is not None and para_num_elem.text else ""
    para_label_id = detect_label_id(para_num_text)
    if para_label_id is None:
        return None

    children = list(paragraph)
    try:
        ps_index = children.index(para_sentence)
    except ValueError:
        return None

    for i in range(ps_index + 1, len(children)):
        elem = children[i]
        if elem.tag == 'List':
            label_text, _, col_num = get_list_info(elem)
            if col_num == 2 and label_text and is_label(label_text):
                list_label_id = detect_label_id(label_text)
                if list_label_id == para_label_id:
                    return elem
    return None

def renumber_elements(tree):
    """ParagraphとItemのNumを再採番する"""
    root = tree.getroot()
    
    parents = {p for p in root.xpath('.//Paragraph/..')}
    for parent in parents:
        paragraphs = parent.findall('Paragraph')
        for i, para in enumerate(paragraphs):
            para.set('Num', str(i + 1))

    for paragraph in root.xpath('.//Paragraph'):
        items = paragraph.findall('Item')
        for i, item in enumerate(items):
            item.set('Num', str(i + 1))

def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description='Paragraph特化スクリプト - 処理3 (Paragraph分割)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
使用例:
  python3 convert_paragraph_step3.py input.xml
  python3 convert_paragraph_step3.py input.xml output.xml
  python3 convert_paragraph_step3.py input.xml --verification
'''
    )
    parser.add_argument('input_file', help='入力XMLファイル（処理2実行済み）')
    parser.add_argument('output_file', nargs='?', help='出力XMLファイル（デフォルト: <input>_paragraph_step4.xml）')
    parser.add_argument('--verification', action='store_true', help='変更箇所にコメントを挿入する検証モードを有効にする')
    
    args = parser.parse_args()
    
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"エラー: 入力ファイルが見つかりません: {args.input_file}", file=sys.stderr)
        return 1
        
    output_path = Path(args.output_file) if args.output_file else input_path.parent / f"{input_path.stem}_step3.xml"

    print("=" * 80)
    print("【Paragraph要素特化型変換 - 処理3: Paragraph分割】")
    print("=" * 80)
    print(f"入力ファイル: {input_path}")

    script_name = Path(__file__).name

    try:
        tree = etree.parse(str(input_path))
    except Exception as e:
        print(f"エラー: XMLファイルの読み込みに失敗しました: {e}", file=sys.stderr)
        return 1

    stats = {
        'split_paragraph': 0,
    }

    root = tree.getroot()
    parents = {c: p for p in root.iter() for c in p}
    all_paragraphs = root.xpath('.//Paragraph')
    i = 0
    while i < len(all_paragraphs):
        paragraph = all_paragraphs[i]
        
        parent = parents.get(paragraph)
        split_list_elem = find_split_point(paragraph)
        
        if parent is not None and split_list_elem is not None:
            if args.verification:
                before_str = etree.tostring(paragraph, pretty_print=True, encoding='unicode')
                comment_text = f"\n*** {script_name}: SPLIT Paragraph ***\n{before_str}\n"
                comment = etree.Comment(comment_text)
                paragraph.addprevious(comment)

            stats['split_paragraph'] += 1
            
            label_text, content_sentence, _ = get_list_info(split_list_elem)
            new_para = etree.Element('Paragraph')
            new_para_num = etree.SubElement(new_para, 'ParagraphNum')
            new_para_num.text = label_text
            new_para_sentence = etree.SubElement(new_para, 'ParagraphSentence')
            if content_sentence is not None:
                new_para_sentence.append(etree.fromstring(etree.tostring(content_sentence)))
            else:
                etree.SubElement(new_para_sentence, 'Sentence')

            original_children = list(paragraph)
            split_index = original_children.index(split_list_elem)
            
            children_to_move = original_children[split_index + 1:]
            for child in children_to_move:
                new_para.append(child)
            
            del paragraph[split_index:]
            
            para_index_in_parent = list(parent).index(paragraph)
            parent.insert(para_index_in_parent + 1, new_para)
            
            all_paragraphs.insert(i + 1, new_para)
            parents[new_para] = parent
        
        i += 1
    
    renumber_elements(tree)

    print("\n変換統計:")
    print(f"  - Paragraph分割: {stats['split_paragraph']}回")

    format_xml_lxml(tree, str(output_path))
    
    print(f"\n出力ファイル: {output_path}")
    print("  ✅ インデント・再採番済み")
    print("=" * 80)

    return 0

if __name__ == '__main__':
    sys.exit(main())
