#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Paragraph修正ロジック4 - ParagraphSentence内のラベルを分割する

前提として、Paragraph修正ロジック3の処理済みであること

処理１ ParagraphNumの直下以外にParagraphSentenceが存在する場合
全角スペースでテキストを分割し、リスト要素に変換する
"""

import sys
import argparse
from pathlib import Path
from lxml import etree

# 親ディレクトリのutils/をインポートパスに追加
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.label_utils import is_label
from utils.xml_utils import save_xml_with_indent

def split_paragraph_sentences(tree, stats):
    """ParagraphSentence内のラベルとテキストを分割してList要素に変換する"""
    root = tree.getroot()
    # 親要素を特定するためのマップを作成
    parent_map = {c: p for p in root.iter() for c in p}
    
    # 変換対象となるParagraphSentenceをすべて見つける
    candidates = []
    for ps_elem in root.xpath('.//ParagraphSentence'):
        sentence_elem = ps_elem.find('Sentence')
        if sentence_elem is not None and sentence_elem.text:
            text = sentence_elem.text.strip()
            # 全角スペースで分割
            parts = text.split('　', 1)
            if len(parts) == 2:
                label, content = parts
                # 分割した前半が項目ラベルか判定
                if is_label(label.strip()):
                    candidates.append((ps_elem, label.strip(), content.strip()))

    if not candidates:
        print("変換対象のParagraphSentenceが見つかりませんでした。")
        return

    # 見つけた候補を変換
    for ps_elem, label, content in candidates:
        parent = parent_map.get(ps_elem)
        if parent is None:
            continue

        # 新しいList要素を構築
        new_list = etree.Element('List')
        list_sentence = etree.SubElement(new_list, 'ListSentence')
        
        col1 = etree.SubElement(list_sentence, 'Column', Num='1')
        sent1 = etree.SubElement(col1, 'Sentence', Num='1')
        sent1.text = label
        
        col2 = etree.SubElement(list_sentence, 'Column', Num='2')
        sent2 = etree.SubElement(col2, 'Sentence', Num='1')
        sent2.text = content
        
        # ParagraphSentenceを新しいList要素で置き換え
        parent.replace(ps_elem, new_list)
        stats['split_sentences'] += 1

def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description='Paragraph特化スクリプト - 処理4 (ParagraphSentence分割)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
使用例:
  python3 convert_paragraph_step4.py input.xml
  python3 convert_paragraph_step4.py input.xml output.xml
'''
    )
    parser.add_argument('input_file', help='入力XMLファイル（処理3実行済み）')
    parser.add_argument('output_file', nargs='?', help='出力XMLファイル（デフォルト: <input>_paragraph_step4.xml）')
    
    args = parser.parse_args()
    
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"エラー: 入力ファイルが見つかりません: {args.input_file}", file=sys.stderr)
        return 1
        
    output_path = Path(args.output_file) if args.output_file else input_path.parent / f"{input_path.stem}_step4.xml"

    print("=" * 80)
    print("【Paragraph要素特化型変換 - 処理4: ParagraphSentence内のラベル分割】")
    print("=" * 80)
    print(f"入力ファイル: {input_path}")

    try:
        tree = etree.parse(str(input_path))
    except Exception as e:
        print(f"エラー: XMLファイルの読み込みに失敗しました: {e}", file=sys.stderr)
        return 1

    stats = {
        'split_sentences': 0,
    }

    # 変換処理を実行
    split_paragraph_sentences(tree, stats)

    print("\n変換統計:")
    print(f"  - 分割されたParagraphSentence: {stats['split_sentences']}箇所")

    # XMLファイルに保存（整形済み）
    save_xml_with_indent(tree, output_path)
    
    print(f"\n出力ファイル: {output_path}")
    print("  ✅ インデント済み")
    print("=" * 80)

    return 0

if __name__ == '__main__':
    sys.exit(main())
