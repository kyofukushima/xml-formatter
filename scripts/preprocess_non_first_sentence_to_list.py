#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sentence要素内のラベル分割処理 - 階層汎用版

Paragraph、Item、Subitem1-5要素内のSentence要素で、
タイトル要素の直後以外のSentence要素内のラベルを分割してList要素に変換する。

処理対象:
- Paragraph要素内の2つ目以降（ParagraphNumの次以外）のParagraphSentence要素
- Item要素内の2つ目以降（ItemTitleの次以外）のItemSentence要素
- Subitem1要素内の2つ目以降（Subitem1Titleの次以外）のSubitem1Sentence要素
- Subitem2-5要素も同様に処理
"""

import sys
import argparse
from pathlib import Path
from lxml import etree
from typing import List, Tuple, Optional

# scripts/utils/をインポートパスに追加
script_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(script_dir))

from utils.label_utils import is_label
from utils import save_xml_with_indent

# 処理対象となる要素タイプの設定
ELEMENT_CONFIGS = [
    # (親要素タグ, タイトル要素タグ, Sentence要素タグ, 統計キー名)
    ('Paragraph', 'ParagraphNum', 'ParagraphSentence', 'paragraph_sentences'),
    ('Item', 'ItemTitle', 'ItemSentence', 'item_sentences'),
    ('Subitem1', 'Subitem1Title', 'Subitem1Sentence', 'subitem1_sentences'),
    ('Subitem2', 'Subitem2Title', 'Subitem2Sentence', 'subitem2_sentences'),
    ('Subitem3', 'Subitem3Title', 'Subitem3Sentence', 'subitem3_sentences'),
    ('Subitem4', 'Subitem4Title', 'Subitem4Sentence', 'subitem4_sentences'),
    ('Subitem5', 'Subitem5Title', 'Subitem5Sentence', 'subitem5_sentences'),
]

def split_sentences_in_element(parent_elem: etree.Element, title_tag: str, 
                               sentence_tag: str, stats: dict) -> List[Tuple[etree.Element, str, str]]:
    """指定された親要素内のSentence要素を検索して変換候補を返す
    
    Args:
        parent_elem: 親要素（Paragraph, Item, Subitem1-5など）
        title_tag: タイトル要素のタグ名（ParagraphNum, ItemTitle, Subitem1Titleなど）
        sentence_tag: Sentence要素のタグ名（ParagraphSentence, ItemSentenceなど）
        stats: 統計情報を格納する辞書
    
    Returns:
        List[Tuple[etree.Element, str, str]]: (Sentence要素, ラベル, 内容)のリスト
    """
    candidates = []
    
    # 親要素の子要素を順番に取得
    children = list(parent_elem)
    
    # タイトル要素を探す
    title_elem = parent_elem.find(title_tag)
    title_index = -1
    if title_elem is not None:
        try:
            title_index = children.index(title_elem)
        except ValueError:
            title_index = -1
    
    # 最初のSentence要素のインデックスを特定
    # タイトル要素が存在する場合: タイトル要素の直後のSentence要素
    # タイトル要素が存在しない場合: 最初のSentence要素
    first_sentence_index = -1
    
    if title_index >= 0:
        # タイトル要素の直後の要素を探す
        for i in range(title_index + 1, len(children)):
            if children[i].tag == sentence_tag:
                first_sentence_index = i
                break
    else:
        # タイトル要素が存在しない場合、最初のSentence要素をスキップ対象とする
        for i, child in enumerate(children):
            if child.tag == sentence_tag:
                first_sentence_index = i
                break
    
    # Sentence要素を処理対象とする
    for i, child in enumerate(children):
        if child.tag == sentence_tag:
            # 最初のSentence要素はスキップ
            if i == first_sentence_index:
                continue
            
            sentence_elem = child.find('Sentence')
            if sentence_elem is not None and sentence_elem.text:
                text = sentence_elem.text.strip()
                # 全角スペースで分割
                parts = text.split('　', 1)
                if len(parts) == 2:
                    label, content = parts
                    # 分割した前半が項目ラベルか判定
                    if is_label(label.strip()):
                        candidates.append((child, label.strip(), content.strip()))
    
    return candidates

def convert_sentence_to_list(sentence_elem: etree.Element, label: str, content: str, 
                            parent: etree.Element) -> None:
    """Sentence要素をList要素に変換して置き換える
    
    Args:
        sentence_elem: 変換対象のSentence要素
        label: ラベル文字列
        content: 内容文字列
        parent: 親要素
    """
    # 新しいList要素を構築
    new_list = etree.Element('List')
    list_sentence = etree.SubElement(new_list, 'ListSentence')
    
    col1 = etree.SubElement(list_sentence, 'Column', Num='1')
    sent1 = etree.SubElement(col1, 'Sentence', Num='1')
    sent1.text = label
    
    col2 = etree.SubElement(list_sentence, 'Column', Num='2')
    sent2 = etree.SubElement(col2, 'Sentence', Num='1')
    sent2.text = content
    
    # Sentence要素を新しいList要素で置き換え
    parent.replace(sentence_elem, new_list)

def split_sentences_in_tree(tree, stats):
    """XMLツリー全体のSentence要素を処理してList要素に変換する
    
    各階層（Paragraph, Item, Subitem1-5）に対して処理を実行する。
    """
    root = tree.getroot()
    # 親要素を特定するためのマップを作成
    parent_map = {c: p for p in root.iter() for c in p}
    
    # 各要素タイプに対して処理を実行
    for parent_tag, title_tag, sentence_tag, stat_key in ELEMENT_CONFIGS:
        # 統計情報を初期化
        if stat_key not in stats:
            stats[stat_key] = 0
        
        # 該当する親要素をすべて検索
        for parent_elem in root.xpath(f'.//{parent_tag}'):
            # 変換候補を取得
            candidates = split_sentences_in_element(parent_elem, title_tag, sentence_tag, stats)
            
            # 見つけた候補を変換
            for sentence_elem, label, content in candidates:
                parent = parent_map.get(sentence_elem)
                if parent is None:
                    continue
                
                convert_sentence_to_list(sentence_elem, label, content, parent)
                stats[stat_key] += 1
                stats['total_sentences'] += 1

def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description='前処理: 2個目以降のSentence要素をList要素に変換',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
処理対象:
  - Paragraph要素内のParagraphSentence要素（ParagraphNumの直後以外）
  - Item要素内のItemSentence要素（ItemTitleの直後以外）
  - Subitem1-5要素内のSubitem1-5Sentence要素（各Titleの直後以外）

各要素タイプで、タイトル要素の直後のSentence要素（1個目）以外を変換対象とします。
ラベル＋全角スペース＋テキストの形式をList要素に変換します。

使用例:
  python3 preprocess_non_first_sentence_to_list.py input.xml
  python3 preprocess_non_first_sentence_to_list.py input.xml output.xml
'''
    )
    parser.add_argument('input_file', help='入力XMLファイル')
    parser.add_argument('output_file', nargs='?', help='出力XMLファイル（デフォルト: <input>_non_first_sentence_to_list.xml）')
    
    args = parser.parse_args()
    
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"エラー: 入力ファイルが見つかりません: {args.input_file}", file=sys.stderr)
        return 1
        
    output_path = Path(args.output_file) if args.output_file else input_path.parent / f"{input_path.stem}_non_first_sentence_to_list.xml"

    print("=" * 80)
    print("【前処理: 2個目以降のSentence要素をList要素に変換】")
    print("=" * 80)
    print(f"入力ファイル: {input_path}")

    try:
        tree = etree.parse(str(input_path))
    except Exception as e:
        print(f"エラー: XMLファイルの読み込みに失敗しました: {e}", file=sys.stderr)
        return 1

    stats = {
        'total_sentences': 0,
    }

    # 変換処理を実行
    split_sentences_in_tree(tree, stats)

    print("\n変換統計:")
    if stats['total_sentences'] == 0:
        print("  変換対象のSentence要素が見つかりませんでした。")
    else:
        for parent_tag, title_tag, sentence_tag, stat_key in ELEMENT_CONFIGS:
            count = stats.get(stat_key, 0)
            if count > 0:
                print(f"  - 分割された{sentence_tag}: {count}箇所")
        print(f"  - 合計: {stats['total_sentences']}箇所")

    # XMLファイルに保存（整形済み）
    save_xml_with_indent(tree, output_path)
    
    print(f"\n出力ファイル: {output_path}")
    print("  ✅ インデント済み")
    print("=" * 80)

    return 0

if __name__ == '__main__':
    sys.exit(main())
