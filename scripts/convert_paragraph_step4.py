#!/usr/bin/env python3
"""
Paragraph特化スクリプト - 処理2（ParagraphNumの次のList要素の変換）

処理1: ParagraphNumの次のList要素が文章の場合
----------------------------------------------
List要素をParagraphSentence要素に変換する

処理2: ParagraphNumの次のList要素が項目ラベル付きの場合
--------------------------------------------------------
ラベルをParagraphNum要素に挿入し、テキストをParagraphSentence要素に変換する

前提条件:
- Paragraph特化スクリプト - 処理1（ParagraphNum補完）実行済み
- Article要素の処理が完了済み

参照:
- logic2_2_Paragraph_text.md の処理1、処理2
"""

import sys
import argparse
from pathlib import Path
from lxml import etree
import xml.etree.ElementTree as ET

# utilsディレクトリをインポートパスに追加（親ディレクトリのutils/を参照）
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.label_utils import is_label, is_paragraph_label

def format_xml_lxml(tree, output_path):
    """
    lxmlのElementTreeをインデント整形して保存
    """
    # etree.indent() を使って確実なインデントを行う
    etree.indent(tree.getroot(), space="  ", level=0)
    
    tree.write(
        output_path,
        encoding='utf-8',
        xml_declaration=True,
        pretty_print=False # indent() を使う場合、pretty_printはFalseにする
    )

from utils.label_utils import is_label, is_paragraph_label

def convert_list_after_paragraph_num(tree):
    """
    処理1と処理2: ParagraphNumの次のList要素を変換
    """
    root = tree.getroot()
    stats = {
        'total_paragraphs': 0,
        'converted_text_only': 0,
        'converted_with_label': 0,
        'skipped_no_list': 0,
        'skipped_has_paragraph_sentence': 0,
        'skipped_other': 0
    }
    
    paragraphs = root.xpath('.//Paragraph')
    stats['total_paragraphs'] = len(paragraphs)
    
    for paragraph in paragraphs:
        paragraph_num = paragraph.find('ParagraphNum')
        if paragraph_num is None:
            continue
        
        children = list(paragraph)
        paragraph_num_index = children.index(paragraph_num)
        
        if paragraph_num_index + 1 >= len(children):
            continue
        
        next_element = children[paragraph_num_index + 1]
        
        if next_element.tag == 'ParagraphSentence':
            stats['skipped_has_paragraph_sentence'] += 1
            continue
        
        if next_element.tag != 'List':
            stats['skipped_no_list'] += 1
            continue
        
        list_sentence = next_element.find('.//ListSentence')
        if list_sentence is None:
            stats['skipped_other'] += 1
            continue
        
        columns = list_sentence.findall('Column')
        
        if len(columns) == 0:
            success = _convert_list_to_paragraph_sentence_text_only(
                paragraph, next_element
            )
            if success:
                stats['converted_text_only'] += 1
            else:
                stats['skipped_other'] += 1
                
        elif len(columns) == 2:
            success = _convert_list_to_paragraph_sentence_with_label(
                paragraph, paragraph_num, next_element, columns
            )
            if success:
                stats['converted_with_label'] += 1
            else:
                stats['skipped_other'] += 1
        else:
            stats['skipped_other'] += 1
    
    return stats

def _convert_list_to_paragraph_sentence_text_only(paragraph, list_element):
    """
    処理1: List要素（文章のみ）をParagraphSentenceに変換
    """
    try:
        list_sentence = list_element.find('.//ListSentence')
        if list_sentence is None:
            return False

        # 1. 新しい要素を作成
        paragraph_sentence = etree.Element('ParagraphSentence')
        for sentence in list_sentence.findall('Sentence'):
            new_sentence = etree.Element('Sentence')
            new_sentence.text = sentence.text
            new_sentence.tail = sentence.tail
            for attr_name, attr_value in sentence.attrib.items():
                new_sentence.set(attr_name, attr_value)
            paragraph_sentence.append(new_sentence)

        # 2. 要素を置換
        original_tail = list_element.tail
        list_index = list(paragraph).index(list_element)
        paragraph.remove(list_element)
        
        current_index = list_index
        paragraph.insert(current_index, paragraph_sentence)
        
        # Restore the tail to maintain indentation
        paragraph_sentence.tail = original_tail
        
        return True
    except Exception as e:
        print(f"警告: 処理1の変換でエラー: {e}", file=sys.stderr)
        return False

def _convert_list_to_paragraph_sentence_with_label(paragraph, paragraph_num, list_element, columns):
    """
    処理2: List要素（ラベル + テキスト）をParagraphNum + ParagraphSentenceに変換
    """
    try:
        label_sentence = columns[0].find('.//Sentence')
        if label_sentence is None or label_sentence.text is None:
            return False
        
        label_text = label_sentence.text.strip()
        
        if not is_label(label_text) or not is_paragraph_label(label_text):
            return False
        
        content_sentence = columns[1].find('.//Sentence')
        if content_sentence is None:
            return False
        
        if paragraph_num.text is not None and paragraph_num.text.strip() != '':
            return False

        # 1. 新しい要素を作成
        paragraph_sentence = etree.Element('ParagraphSentence')
        new_sentence = etree.Element('Sentence')
        new_sentence.text = content_sentence.text
        new_sentence.tail = content_sentence.tail
        for attr_name, attr_value in content_sentence.attrib.items():
            new_sentence.set(attr_name, attr_value)
        paragraph_sentence.append(new_sentence)

        # 3. 要素を置換
        original_tail = list_element.tail
        list_index = list(paragraph).index(list_element)
        paragraph_num.text = label_text
        paragraph.remove(list_element)

        current_index = list_index
        paragraph.insert(current_index, paragraph_sentence)

        # Restore the tail to maintain indentation
        paragraph_sentence.tail = original_tail

        return True
    except Exception as e:
        print(f"警告: 処理2の変換でエラー: {e}", file=sys.stderr)
        return False

def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description='Paragraph特化スクリプト - 処理2（ParagraphNumの次のList要素変換）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # 基本的な使い方
  python3 convert_paragraph_step2.py test_input5_paragraph_step1.xml
  
  # 検証モードで実行
  python3 convert_paragraph_step2.py input.xml --verification

処理内容:
  - 処理1: ParagraphNumの次のList要素が文章の場合 → ParagraphSentence変換
  - 処理2: ParagraphNumの次のList要素がラベル付きの場合 → ParagraphNum + ParagraphSentence変換
        """
    )
    
    parser.add_argument('input_file', help='入力XMLファイル（処理1実行済み）')
    parser.add_argument('output_file', nargs='?', help='出力XMLファイル（デフォルト: <input>_paragraph_step2.xml）')
    
    args = parser.parse_args()
    
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"エラー: 入力ファイルが見つかりません: {args.input_file}")
        return 1
    
    if args.output_file:
        output_path = Path(args.output_file)
    else:
        output_path = input_path.parent / f"{input_path.stem}_paragraph_step2.xml"
    
    print("=" * 80)
    print("【Paragraph要素特化型変換 - 処理2: List要素変換】")
    print("=" * 80)
    print()
    


    try:
        tree = etree.parse(str(input_path))
    except Exception as e:
        print(f"エラー: XMLファイルの読み込みに失敗しました: {e}")
        return 1
    
    root = tree.getroot()
    paragraphs_before = len(root.xpath('.//Paragraph'))
    paragraph_sentences_before = len(root.xpath('.//Paragraph/ParagraphSentence'))
    lists_after_paragraph_num_before = len(root.xpath('.//Paragraph/ParagraphNum/following-sibling::List[1]'))
    
    print("処理前:")
    print(f"  - Paragraph要素: {paragraphs_before}個")
    print(f"  - ParagraphSentence要素: {paragraph_sentences_before}個")
    print(f"  - ParagraphNum直後のList要素: {lists_after_paragraph_num_before}個")
    print()
    
    stats = convert_list_after_paragraph_num(tree)
    
    paragraph_sentences_after = len(root.xpath('.//Paragraph/ParagraphSentence'))
    lists_after_paragraph_num_after = len(root.xpath('.//Paragraph/ParagraphNum/following-sibling::List[1]'))
    
    print("処理後:")
    print(f"  - Paragraph要素: {paragraphs_before}個")
    print(f"  - ParagraphSentence要素: {paragraph_sentences_after}個 (+{paragraph_sentences_after - paragraph_sentences_before})")
    print(f"  - ParagraphNum直後のList要素: {lists_after_paragraph_num_after}個 (-{lists_after_paragraph_num_before - lists_after_paragraph_num_after})")
    print()
    
    print("変換統計:")
    print(f"  - 処理したParagraph: {stats['total_paragraphs']}個")
    print(f"  - 処理1（文章のみ変換）: {stats['converted_text_only']}個")
    print(f"  - 処理2（ラベル付き変換）: {stats['converted_with_label']}個")
    print(f"  - スキップ（ParagraphSentence既存）: {stats['skipped_has_paragraph_sentence']}個")
    print(f"  - スキップ（List以外）: {stats['skipped_no_list']}個")
    print(f"  - スキップ（その他）: {stats['skipped_other']}個")
    print()
    
    format_xml_lxml(tree, str(output_path))
    
    print(f"出力ファイル: {output_path}")
    print("  ✅ インデント整形済み")
    print("  ✅ List要素変換済み")
    print("=" * 80)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())