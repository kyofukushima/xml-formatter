#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
空Title要素の除去スクリプト

変換処理では、Item/Subitem1～10の生成時にTitleが無い場合でも空のTitle要素
（<ItemTitle/>等）を挿入している。XMLスキーマ（kokuji20250320.xsd）上、
ItemTitle/Subitem1Title～Subitem10Titleはいずれもオプション（minOccurs="0"）
であるため、最終出力からは空のTitle要素を省略する後処理を行う。

除去対象:
  - ItemTitle / Subitem1Title ～ Subitem10Title のうち、
    以下をすべて満たすもの
      * テキスト内容が空（空白のみを含む）
      * 子要素（Ruby等）を持たない
      * 属性を持たない

注意:
  - 変換パイプラインの内部処理は「空のTitle要素」の有無を判定に使用している
    ため、本スクリプトは必ずパイプラインの最終段（後処理）として実行すること
  - 入力XMLの整形（インデント等）は変更しない

使用方法:
    python postprocess_remove_empty_titles.py input.xml output.xml
"""

import sys
import argparse
from pathlib import Path
from lxml import etree

# 除去対象のTitle要素タグ
TARGET_TITLE_TAGS = ['ItemTitle'] + [f'Subitem{i}Title' for i in range(1, 11)]


def is_empty_title(title_elem) -> bool:
    """Title要素が「空」（テキストなし・子要素なし・属性なし）かどうか"""
    if len(title_elem) > 0:
        return False
    if title_elem.attrib:
        return False
    return not ''.join(title_elem.itertext()).strip()


def remove_element_keep_formatting(elem):
    """整形（インデント）を崩さないように要素を削除する

    削除する要素のtail（次要素の手前までの空白）を、直前の位置に引き継ぐ。
    Title要素は親の先頭子要素であるため、通常は親のtextに引き継がれる。
    """
    parent = elem.getparent()
    prev = elem.getprevious()
    if prev is not None:
        prev.tail = elem.tail
    else:
        parent.text = elem.tail
    parent.remove(elem)


def remove_empty_titles(root) -> dict:
    """空のTitle要素を除去し、タグごとの除去数を返す"""
    removed = {}
    for tag in TARGET_TITLE_TAGS:
        count = 0
        for title_elem in root.findall(f'.//{tag}'):
            if is_empty_title(title_elem):
                remove_element_keep_formatting(title_elem)
                count += 1
        if count > 0:
            removed[tag] = count
    return removed


def process_xml_file(input_path, output_path):
    """XMLファイルを処理する"""
    print("=" * 80)
    print("【空Title要素の除去】")
    print("=" * 80)
    print(f"入力ファイル: {input_path}")

    try:
        tree = etree.parse(str(input_path))
    except Exception as e:
        print(f"エラー: XMLファイルの読み込みに失敗しました: {e}", file=sys.stderr)
        return 1

    root = tree.getroot()
    removed = remove_empty_titles(root)

    # 入力の整形を維持したまま書き出す（再インデントしない）
    tree.write(
        str(output_path),
        encoding='utf-8',
        xml_declaration=True,
        pretty_print=False
    )

    total = sum(removed.values())
    print(f"\n処理統計:")
    print(f" - 除去した空Title要素: {total}箇所")
    for tag, count in removed.items():
        print(f"   - {tag}: {count}箇所")
    print(f"\n出力ファイル: {output_path}")
    print("=" * 80)

    return 0


def main():
    parser = argparse.ArgumentParser(
        description='空Title要素の除去スクリプト',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
使用例:
  python postprocess_remove_empty_titles.py input.xml output.xml
        '''
    )
    parser.add_argument('input_file', help='入力XMLファイル')
    parser.add_argument('output_file', help='出力XMLファイル')

    args = parser.parse_args()

    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"エラー: 入力ファイルが見つかりません: {args.input_file}", file=sys.stderr)
        return 1

    return process_xml_file(input_path, Path(args.output_file))


if __name__ == '__main__':
    sys.exit(main())
