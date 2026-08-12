#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
文頭全角スペース補填/除去スクリプト

告示データ整備方針・告示マークアップ修正案資料に基づき、段落冒頭の1字下げを
全角スペース（U+3000）の補填で再現する後処理を行う。

対象（addモードで挿入、removeモードで先頭1文字の全角スペースを除去）:
  1. Title要素が空（または不在）のItem/Subitem1～10の、
     直下の*Sentence要素内の先頭Sentence冒頭
     ※Title（番号）があるものは対象外（パターン6のSubitem2Title例外に対応）
  2. LineBreak="true"のColumn要素内の先頭Sentence冒頭
     （同一要素内でColumn改行された二段目以降の段落）
  3. List/ListSentence内の先頭Sentence冒頭（--include-list指定時のみ。
     資料上「要確認」のためデフォルトでは対象外）

除外（addモード時に挿入しないもの）:
  a. 既に全角スペースで始まるSentence（冪等）
  b. テキストを一切含まないSentence（空行防止用の空要素、
     QuoteStruct/Fig等の数式画像のみのSentence）、および冒頭が
     ArithFormula/QuoteStruct/Figで始まるSentence（算式の表示行）
  c. 変数定義行・数式行（「Ｅ：…」「ｎ：…」等の記号定義の羅列、
     「ＥＭ＝αＭ×Ａ…」等のテキストで書かれた数式。
     コンテナ全体のテキストが「短い記号列＋『：』または『＝』」で
     始まる形状で判定。--include-vardef 指定時は除外しない）
  d. 「（」で始まるSentence（--exclude-paren 指定時のみ。
     「（注）…」等の括弧書きを字下げ対象とするかは告示ごとの
     官報体裁に依存するため選択式）

注意:
  - Sentence冒頭がRuby等のインライン要素の場合（text=None）は、
    要素の前にテキストとして全角スペースを設定する
  - 入力XMLの整形（インデント等）は変更しない

使用方法:
    python postprocess_fullwidth_space.py input.xml output.xml [--mode add|remove] [--include-list] [--include-vardef] [--exclude-paren]
"""

import sys
import re
import argparse
from pathlib import Path
from lxml import etree

FULLWIDTH_SPACE = '　'

# Title要素が空の場合に対象となる階層要素
HIERARCHY_TAGS = ['Item'] + [f'Subitem{i}' for i in range(1, 11)]

# 変数定義行・数式行の形状: 記号（全角/半角英数字・ギリシャ文字）で始まり、
# 句読点を挟まず20文字以内に「：」（変数定義。例: ＥＡＣ，ＡＨＵ，ｄ，ｉ：…）
# または「＝」（テキストで書かれた数式。例: ＥＭ＝αＭ×Ａ…）が現れる
# ※<Sub>/<Sup>の添え字は展開して連結したテキストに対して判定する
VARDEF_SHAPE_RE = re.compile(r'^[Ａ-Ｚａ-ｚ０-９A-Za-z0-9Α-Ωα-ω][^、。：＝]{0,19}[：＝]')

# 変数定義行の文脈: 先行する説明文（例: この式において、Ｅ…は、
# それぞれ次の数値を表すものとする。）
FORMULA_CONTEXT_RE = re.compile(r'(この|これらの)式において')

# Sentence冒頭がこれらの要素の場合は数式・図の表示行のため補填しない
# （ArithFormula: 算式、QuoteStruct/Fig: 数式画像等）
FORMULA_BLOCK_TAGS = {'ArithFormula', 'QuoteStruct', 'Fig'}

# --exclude-paren 指定時に除外する文頭の括弧（全角・半角）
PAREN_CHARS = ('（', '(')


def _first_direct_sentence(container):
    """コンテナ直下の最初のSentence要素を返す（Column内は対象外）"""
    for child in container:
        if child.tag == 'Sentence':
            return child
    return None


def _title_is_empty(element, tag):
    """階層要素のTitleが空（または不在）かどうか"""
    title_elem = element.find(f'{tag}Title')
    if title_elem is None:
        return True
    return not ''.join(title_elem.itertext()).strip()


def _is_inside_list(element):
    """要素がList（ListSentence）内にあるかどうか"""
    parent = element.getparent()
    while parent is not None:
        if parent.tag == 'ListSentence':
            return True
        parent = parent.getparent()
    return False


def _flatten_text(element):
    """要素配下の全テキストを連結して返す（Sub/Sup等の添え字も展開）"""
    if element is None:
        return ''
    return ''.join(element.itertext())


def _is_vardef_shape(container):
    """コンテナ全体のテキストが変数定義行の形状かどうか"""
    text = _flatten_text(container).strip()
    return bool(VARDEF_SHAPE_RE.match(text))


def _sentence_container(element):
    """階層要素の*Sentenceコンテナを返す"""
    if element.tag in HIERARCHY_TAGS:
        return element.find(f'{element.tag}Sentence')
    return None


def _has_formula_context(element):
    """先行文脈に「（この|これらの）式において」の説明文があるかどうか

    変数定義行は「この式において…」の子要素として現れる場合と
    兄弟要素として続く場合があるため、直近数階層について
    親要素自身の本文と先行兄弟の本文を確認する。
    """
    node = element
    for _ in range(3):
        for sibling in node.itersiblings(preceding=True):
            if FORMULA_CONTEXT_RE.search(_flatten_text(_sentence_container(sibling))):
                return True
        parent = node.getparent()
        if parent is None:
            return False
        if FORMULA_CONTEXT_RE.search(_flatten_text(_sentence_container(parent))):
            return True
        node = parent
    return False


def collect_target_sentences(root, include_list=False, include_vardef=False):
    """補填/除去の対象となるSentence要素を収集する

    Returns:
        (targets, excluded_vardefs)
        targets: 対象Sentenceのリスト
        excluded_vardefs: 変数定義行として除外した (Sentence, 文脈あり) のリスト
    """
    targets = []
    excluded_vardefs = []
    seen = set()

    def add(sentence):
        if sentence is not None and id(sentence) not in seen:
            seen.add(id(sentence))
            targets.append(sentence)

    # 1. Title要素が空のItem/Subitem1～10
    for tag in HIERARCHY_TAGS:
        for element in root.iter(tag):
            if not _title_is_empty(element, tag):
                continue
            container = element.find(f'{tag}Sentence')
            if container is None:
                continue
            sentence = _first_direct_sentence(container)
            if sentence is None:
                continue
            if not include_vardef and _is_vardef_shape(container):
                if id(sentence) not in seen:
                    seen.add(id(sentence))
                    excluded_vardefs.append(
                        (sentence, _has_formula_context(element))
                    )
                continue
            add(sentence)

    # 2. LineBreak="true"のColumn（List内はinclude_list指定時のみ）
    for column in root.iter('Column'):
        if column.get('LineBreak') != 'true':
            continue
        if _is_inside_list(column) and not include_list:
            continue
        add(_first_direct_sentence(column))

    # 3. List/ListSentence直下の先頭Sentence（オプション）
    if include_list:
        for list_sentence in root.iter('ListSentence'):
            add(_first_direct_sentence(list_sentence))

    return targets, excluded_vardefs


def is_insertable(sentence):
    """Sentenceが補填可能かどうか（除外条件・冪等性の共通判定）"""
    # テキストを一切含まないSentenceには挿入しない
    # （空行防止用の空要素、QuoteStruct/Fig等の数式画像のみのSentence）
    flat = _flatten_text(sentence)
    if not flat.strip():
        return False

    # 冒頭が算式・数式画像（ArithFormula/QuoteStruct/Fig）のSentenceは
    # 数式の表示行のため補填しない
    if (sentence.text is None or not sentence.text.strip()) and len(sentence) > 0 \
            and sentence[0].tag in FORMULA_BLOCK_TAGS:
        return False

    # 整形用のASCII空白のみを除いて冪等性を判定
    # （lstrip()の引数なし呼び出しは全角スペース自体も除去してしまうため不可）
    if flat.lstrip(' \t\r\n').startswith(FULLWIDTH_SPACE):
        return False

    return True


def add_fullwidth_space(sentence):
    """Sentence冒頭に全角スペースを挿入する（冪等）。挿入したらTrue"""
    if not is_insertable(sentence):
        return False

    text = sentence.text
    if text is None or not text.strip(' \t\r\n'):
        # 冒頭がRuby等のインライン要素の場合: 要素の前にテキストとして挿入
        # （text が整形用の空白のみの場合も同様に先頭へ挿入する）
        sentence.text = FULLWIDTH_SPACE + (text or '')
        return True

    if text.startswith(FULLWIDTH_SPACE):
        return False

    sentence.text = FULLWIDTH_SPACE + text
    return True


def starts_with_paren(sentence):
    """Sentenceの可視テキストが「（」で始まるかどうか（--exclude-paren用）"""
    flat = _flatten_text(sentence).lstrip(' \t\r\n')
    return flat.startswith(PAREN_CHARS)


def remove_fullwidth_space(sentence):
    """Sentence冒頭の全角スペースを1文字除去する。除去したらTrue"""
    text = sentence.text
    if text and text.startswith(FULLWIDTH_SPACE):
        sentence.text = text[1:]
        return True
    return False


def process_xml_file(input_path, output_path, mode='add', include_list=False,
                     include_vardef=False, exclude_paren=False):
    """XMLファイルを処理する"""
    print("=" * 80)
    action = "補填" if mode == 'add' else "除去"
    print(f"【文頭全角スペース{action}】")
    print("=" * 80)
    print(f"入力ファイル: {input_path}")
    print(f"List内Sentenceを対象: {'はい' if include_list else 'いいえ'}")
    if mode == 'add':
        print(f"変数定義行を対象: {'はい' if include_vardef else 'いいえ'}")
        print(f"「（」始まりを対象: {'いいえ' if exclude_paren else 'はい'}")

    try:
        tree = etree.parse(str(input_path))
    except Exception as e:
        print(f"エラー: XMLファイルの読み込みに失敗しました: {e}", file=sys.stderr)
        return 1

    root = tree.getroot()
    # removeモードでは旧仕様で挿入済みのスペースも確実に除去できるよう、
    # 変数定義行も対象に含める
    targets, excluded_vardefs = collect_target_sentences(
        root,
        include_list=include_list,
        include_vardef=include_vardef or mode == 'remove'
    )

    changed = 0
    excluded_parens = 0
    for sentence in targets:
        if mode == 'add':
            # removeモードでは括弧始まり除外を適用しない
            # （--exclude-paren なしで補填済みのスペースも除去できるようにする）
            if exclude_paren and is_insertable(sentence) \
                    and starts_with_paren(sentence):
                excluded_parens += 1
                continue
            if add_fullwidth_space(sentence):
                changed += 1
        else:
            if remove_fullwidth_space(sentence):
                changed += 1

    # 入力の整形を維持したまま書き出す（再インデントしない）
    tree.write(
        str(output_path),
        encoding='utf-8',
        xml_declaration=True,
        pretty_print=False
    )

    print(f"\n処理統計:")
    print(f" - 対象Sentence数: {len(targets)}箇所")
    print(f" - {action}実施: {changed}箇所")
    if excluded_parens:
        print(f" - 「（」始まりとして除外: {excluded_parens}箇所")
    if excluded_vardefs:
        print(f" - 変数定義行として除外: {len(excluded_vardefs)}箇所")
        # 先行文脈（「この式において」等）が見つからないものは判定根拠が
        # テキスト形状のみのため、要確認として行番号を出力する
        unconfirmed = [s for s, has_ctx in excluded_vardefs if not has_ctx]
        if unconfirmed:
            print(f"   ※うち要確認（式の説明文脈なし）: {len(unconfirmed)}箇所")
            for sentence in unconfirmed:
                excerpt = _flatten_text(sentence).strip()[:30]
                print(f"     - {input_path.name}:{sentence.sourceline} {excerpt}")
    print(f"\n出力ファイル: {output_path}")
    print("=" * 80)

    return 0


def main():
    parser = argparse.ArgumentParser(
        description='文頭全角スペース補填/除去スクリプト',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
使用例:
  python postprocess_fullwidth_space.py input.xml output.xml
  python postprocess_fullwidth_space.py input.xml output.xml --mode remove
  python postprocess_fullwidth_space.py input.xml output.xml --include-list
  python postprocess_fullwidth_space.py input.xml output.xml --include-vardef
        '''
    )
    parser.add_argument('input_file', help='入力XMLファイル')
    parser.add_argument('output_file', help='出力XMLファイル')
    parser.add_argument('--mode', choices=['add', 'remove'], default='add',
                        help='add: 全角スペースを挿入（デフォルト）, remove: 除去')
    parser.add_argument('--include-list', action='store_true',
                        help='List/ListSentence内のSentenceも対象にする（デフォルト: 対象外）')
    parser.add_argument('--include-vardef',
                        action='store_true',
                        help='変数定義行・数式行（「Ｅ：…」「Ｅ＝…」等）も挿入対象にする'
                             '（デフォルト: 除外）')
    parser.add_argument('--exclude-paren',
                        action='store_true',
                        help='「（」で始まるSentence（「（注）…」等）を挿入対象から除外する'
                             '（デフォルト: 対象に含める）')

    args = parser.parse_args()

    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"エラー: 入力ファイルが見つかりません: {args.input_file}", file=sys.stderr)
        return 1

    return process_xml_file(
        input_path,
        Path(args.output_file),
        mode=args.mode,
        include_list=args.include_list,
        include_vardef=args.include_vardef,
        exclude_paren=args.exclude_paren
    )


if __name__ == '__main__':
    sys.exit(main())
