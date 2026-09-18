#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
二重パーレン（((N))）の丸数字正規化スクリプト

「((21))」「（（２１））」のように丸括弧を二重にした番号表記を、
対応する丸数字（①〜⑳、㉑〜㉟、㊱〜㊿）に置き換える前処理。
協力会社ツール（変換ツール_V2.py）の normalize_double_paren と同等の処理。

対象:
  文書内のすべてのテキストノード（要素の text と tail）。見出しのラベルだけで
  なく、本文中の参照（「（（２１））に掲げる…」）も同じ表記に揃える。
範囲:
  1〜50。0、51以上、3桁以上の番号は変換せずそのまま残す。
  括弧は全角「（）」・半角「()」のどちらでも可（混在も可）。
  括弧と数字の間の空白は無視する。
冪等:
  既に丸数字になっている箇所は対象外のため、再実行しても変化しない。
整形:
  入力XMLのインデント等は変更しない。

使用方法:
    python normalize_double_paren.py input.xml output.xml
"""

import sys
import re
import argparse
from collections import Counter
from pathlib import Path
from lxml import etree

# 二重パーレン番号: （（２１）） / ((21)) / ( (21) ) 等
DOUBLE_PAREN_RE = re.compile(r'[（(]\s*[（(]\s*([0-9０-９]{1,2})\s*[）)]\s*[）)]')

MIN_NUMBER = 1
MAX_NUMBER = 50

_ZEN2HAN = str.maketrans('０１２３４５６７８９', '0123456789')


def circled_number(n):
    """1〜50 の整数を丸数字1文字に変換する。範囲外は None"""
    if 1 <= n <= 20:
        return chr(0x2460 + n - 1)      # ①〜⑳
    if 21 <= n <= 35:
        return chr(0x3251 + n - 21)     # ㉑〜㉟
    if 36 <= n <= 50:
        return chr(0x32B1 + n - 36)     # ㊱〜㊿
    return None


def normalize_text(text, stats=None):
    """文字列中の二重パーレン番号を丸数字に置換して返す

    stats を渡すと 'replaced'（置換数）、'pairs'（元表記→丸数字の Counter）、
    'skipped'（範囲外で未変換の表記の Counter）を加算する。
    """
    if not text or not DOUBLE_PAREN_RE.search(text):
        return text

    def _replace(m):
        n = int(m.group(1).translate(_ZEN2HAN))
        circled = circled_number(n)
        if circled is None:
            if stats is not None:
                stats['skipped'][m.group(0)] += 1
            return m.group(0)
        if stats is not None:
            stats['replaced'] += 1
            stats['pairs'][(m.group(0), circled)] += 1
        return circled

    return DOUBLE_PAREN_RE.sub(_replace, text)


def new_stats():
    return {'replaced': 0, 'pairs': Counter(), 'skipped': Counter()}


def normalize_tree(root, stats=None):
    """ツリー内のすべてのテキストノードを正規化する。置換数を返す"""
    if stats is None:
        stats = new_stats()
    for node in root.iter():
        # 要素のテキストのみ対象（コメント・処理命令の中身は変更しない）。
        # tail は直後の本文テキストなのでノード種別によらず対象にする。
        if isinstance(node.tag, str) and node.text:
            node.text = normalize_text(node.text, stats)
        if node.tail:
            node.tail = normalize_text(node.tail, stats)
    return stats['replaced']


def process_xml_file(input_path, output_path):
    print("=" * 80)
    print("【二重パーレンの丸数字正規化】")
    print("=" * 80)
    print(f"入力ファイル: {input_path}")

    parser = etree.XMLParser(remove_blank_text=False, resolve_entities=False)
    tree = etree.parse(str(input_path), parser)
    root = tree.getroot()

    stats = new_stats()
    normalize_tree(root, stats)

    # 入力の整形を維持したまま書き出す（再インデントしない）
    tree.write(
        str(output_path),
        encoding='utf-8',
        xml_declaration=True,
        pretty_print=False
    )

    print(f"\n処理統計:")
    print(f" - 正規化実施: {stats['replaced']}箇所")
    if stats['pairs']:
        print(" - 内訳:")
        for (before, after), count in sorted(stats['pairs'].items(),
                                             key=lambda kv: (kv[0][1], kv[0][0])):
            print(f"     {before} → {after} : {count}箇所")
    if stats['skipped']:
        total_skipped = sum(stats['skipped'].values())
        print(f" - 範囲外（{MIN_NUMBER}〜{MAX_NUMBER}以外）のため未変換: {total_skipped}箇所")
        for before, count in sorted(stats['skipped'].items()):
            print(f"     {before} : {count}箇所")
    print(f"\n出力ファイル: {output_path}")
    print("=" * 80)
    return 0


def main():
    parser = argparse.ArgumentParser(
        description='二重パーレン（((N))）を丸数字（①〜㊿）に正規化する',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
使用例:
  python normalize_double_paren.py input.xml output.xml
        '''
    )
    parser.add_argument('input_file', help='入力XMLファイル')
    parser.add_argument('output_file', help='出力XMLファイル')
    args = parser.parse_args()

    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"エラー: 入力ファイルが見つかりません: {args.input_file}", file=sys.stderr)
        return 1
    output_path = Path(args.output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        return process_xml_file(input_path, output_path)
    except etree.XMLSyntaxError as e:
        print(f"エラー: XMLの解析に失敗しました: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
