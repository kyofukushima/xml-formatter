#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
別表（AppdxTable）等の Num 属性付与スクリプト（後処理）

変換パイプラインは AppdxTable の Num 属性を扱わないため、逆変換由来の XML など
Num のない AppdxTable がそのまま出力される。このスクリプトは出力 XML の AppdxTable
（オプションで AppdxNote 等の付録系要素）に Num を付与する。

付与方式（--mode）:
  title       タイトル序数方式（デフォルト）。AppdxTableTitle の序数から決める。
                「別表第一」→ Num="1"、「別表第２」→ Num="2"、「別記第二十」→ Num="20"
              スキーマ上 Num は xs:positiveInteger のため、枝番付きのタイトル
              （「別表第三の一の二」。"3_1_2" を表せない）には付与せず、
              序数が読み取れないタイトル（「別表」のみ等）も付与しない。
              いずれも実行ログに「未付与」として行番号付きで出力する。
              ただし序数のないタイトルでも、その要素が文書内に 1 つだけなら Num="1" とする。
              同じ序数が複数の要素に付く場合（「別表第一」と「別記第一」の併存等）は
              付与したうえで「重複」として実行ログに出力する。
  sequential  出現順連番方式。文書内の同じ要素を出現順に 1, 2, 3 … と振る。
              枝番付きタイトルが混在する告示（別表第三の一の二 等）向け。

既存 Num の扱い:
  デフォルトでは Num がない・正の整数でない（Num="0" 等）要素にだけ付与し、
  有効な Num が既に付いている要素は変更しない（繰り返し実行しても結果は同じ）。
  既存の有効な Num が方式による値と異なる場合は「要確認」として実行ログに出力する。
  --overwrite 指定時は、有効な Num も方式に従って振り直す。

対象要素（--elements）:
  デフォルトは AppdxTable のみ。カンマ区切りで AppdxNote, AppdxStyle, AppdxFormat,
  AppdxFig, SupplProvisionAppdxTable, SupplProvisionAppdxStyle（いずれも Num が
  positiveInteger の付録系要素）に広げられる。タイトル要素は「<要素名>Title」とみなす。

注意:
  - 入力 XML の整形（インデント等）とテキスト内容は変更しない（属性のみ）

使用方法:
    python postprocess_appdxtable_num.py input.xml output.xml
    python postprocess_appdxtable_num.py input.xml output.xml --mode sequential
    python postprocess_appdxtable_num.py input.xml output.xml --overwrite
    python postprocess_appdxtable_num.py input.xml output.xml --elements AppdxTable,AppdxNote
"""

import sys
import re
import argparse
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from lxml import etree

MODE_TITLE = 'title'
MODE_SEQUENTIAL = 'sequential'
MODES = (MODE_TITLE, MODE_SEQUENTIAL)

DEFAULT_ELEMENTS = ['AppdxTable']
# スキーマ上 Num が xs:positiveInteger で、<要素名>Title を持つ付録系要素
SUPPORTED_ELEMENTS = [
    'AppdxTable', 'AppdxNote', 'AppdxStyle', 'AppdxFormat', 'AppdxFig',
    'SupplProvisionAppdxTable', 'SupplProvisionAppdxStyle',
]

_ZEN2HAN = str.maketrans('０１２３４５６７８９', '0123456789')
_KANJI_DIGITS = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
                 '六': 6, '七': 7, '八': 8, '九': 9}
_KANJI_UNITS = {'十': 10, '百': 100, '千': 1000}

_ARABIC = r'[0-9０-９]+'
_KANJI = r'[一二三四五六七八九十百千]+'
_NUM = rf'(?:{_ARABIC}|{_KANJI})'
# 「別表第一」「別表１」「別記第二十」「付録第２」「別表第三の一の二」…
#   呼称（数字・「第」以外の文字列）→ 任意の「第」→ 序数 → 枝番（任意）→ 以降は任意
_TITLE_ORDINAL_RE = re.compile(
    rf'^[\s　]*(?P<label>[^0-9０-９一二三四五六七八九十百千第\s　]*)[\s　]*第?[\s　]*'
    rf'(?P<num>{_NUM})'
    rf'(?P<branch>(?:[\s　]*[のノ][\s　]*{_NUM})*)'
)


def _kanji_to_int(text: str) -> Optional[int]:
    """漢数字（十・百・千の合成を含む）を整数に変換する。解釈できなければ None

    「一二」のような位取り表記は序数として扱わず None を返す。
    """
    result = 0
    current = 0
    last_unit = float('inf')
    for ch in text:
        if ch in _KANJI_DIGITS:
            if current != 0:
                return None
            current = _KANJI_DIGITS[ch]
        elif ch in _KANJI_UNITS:
            unit = _KANJI_UNITS[ch]
            if unit >= last_unit:
                return None
            last_unit = unit
            result += (current if current != 0 else 1) * unit
            current = 0
        else:
            return None
    total = result + current
    return total if total > 0 else None


def _number_to_int(text: str) -> Optional[int]:
    text = text.translate(_ZEN2HAN)
    if text.isdigit():
        num = int(text)
        return num if num > 0 else None
    return _kanji_to_int(text)


def parse_title_ordinal(title: Optional[str]) -> Tuple[Optional[int], bool]:
    """タイトルから序数を読み取る

    Returns:
        (序数, 枝番付きか)
        序数が読み取れない場合は (None, False)。
        枝番付き（「別表第三の一の二」）の場合は (3, True) のように先頭の序数と True を返す。
    """
    if not title:
        return (None, False)
    m = _TITLE_ORDINAL_RE.match(title)
    if not m:
        return (None, False)
    num = _number_to_int(m.group('num'))
    if num is None:
        return (None, False)
    return (num, bool(m.group('branch')))


def is_valid_num(value: Optional[str]) -> bool:
    """Num 属性値がスキーマ上有効（正の整数）か"""
    return bool(value) and value.isdigit() and int(value) > 0


def _title_text(elem: etree._Element, tag: str) -> str:
    title = elem.find(f'{tag}Title')
    return "".join(title.itertext()).strip() if title is not None else ''


def assign_nums(root: etree._Element, elements: List[str], mode: str = MODE_TITLE,
                overwrite: bool = False) -> Dict[str, list]:
    """対象要素の Num 属性を付与する

    Returns:
        結果の辞書:
          assigned      付与した (要素名, 行番号, タイトル, Num)
          unassigned    付与できなかった (要素名, 行番号, タイトル, 理由)
          mismatched    既存の有効な Num が方式による値と異なるが変更しなかった
                        (要素名, 行番号, タイトル, 既存Num, 方式による値)
          duplicated    同じ Num が複数の要素に付いた (要素名, Num, 件数)
          kept          既存の有効な Num を変更しなかった件数（要素名ごと）
    """
    if mode not in MODES:
        raise ValueError(f'unknown mode: {mode}')
    result = {'assigned': [], 'unassigned': [], 'mismatched': [], 'duplicated': [], 'kept': Counter()}

    for tag in elements:
        targets = list(root.iter(tag))
        if not targets:
            continue

        # 方式ごとに、各要素の「あるべき Num」を決める（None は付与不可）
        desired: List[Tuple[Optional[str], str]] = []
        if mode == MODE_SEQUENTIAL:
            desired = [(str(i), '') for i in range(1, len(targets) + 1)]
        else:
            for elem in targets:
                num, has_branch = parse_title_ordinal(_title_text(elem, tag))
                if num is None:
                    if len(targets) == 1:
                        desired.append(('1', ''))
                    else:
                        desired.append((None, 'タイトルから序数を読み取れない'))
                elif has_branch:
                    desired.append((None, '枝番付きのタイトル（Num は正の整数のみ）'))
                else:
                    desired.append((str(num), ''))

        for elem, (value, reason) in zip(targets, desired):
            title = _title_text(elem, tag)
            current = elem.get('Num')
            if is_valid_num(current) and not overwrite:
                result['kept'][tag] += 1
                if value is not None and value != current:
                    result['mismatched'].append((tag, elem.sourceline, title, current, value))
                continue
            if value is None:
                result['unassigned'].append((tag, elem.sourceline, title, reason))
                continue
            elem.set('Num', value)
            result['assigned'].append((tag, elem.sourceline, title, value))

        counts = Counter(e.get('Num') for e in targets if is_valid_num(e.get('Num')))
        for value, count in sorted(counts.items(), key=lambda kv: int(kv[0])):
            if count > 1:
                result['duplicated'].append((tag, value, count))

    return result


def process_file(input_path: Path, output_path: Path, mode: str = MODE_TITLE,
                 overwrite: bool = False, elements: Optional[List[str]] = None) -> int:
    elements = elements or DEFAULT_ELEMENTS
    print("=" * 80)
    print("【別表（AppdxTable）Num 属性付与】")
    print("=" * 80)
    print(f"入力ファイル: {input_path}")
    print(f"付与方式: {'タイトル序数' if mode == MODE_TITLE else '出現順連番'}")
    print(f"既存Numの上書き: {'あり' if overwrite else 'なし'}")
    print(f"対象要素: {', '.join(elements)}")

    try:
        tree = etree.parse(str(input_path))
    except Exception as e:
        print(f"エラー: XMLファイルの読み込みに失敗しました: {e}", file=sys.stderr)
        return 1

    result = assign_nums(tree.getroot(), elements, mode=mode, overwrite=overwrite)

    # 入力の整形を維持したまま書き出す（再インデントしない）
    tree.write(str(output_path), encoding='utf-8', xml_declaration=True, pretty_print=False)

    total = sum(len(list(tree.getroot().iter(tag))) for tag in elements)
    print(f"\n処理統計:")
    print(f" - 対象要素数: {total}箇所")
    print(f" - 付与実施: {len(result['assigned'])}箇所")
    kept = sum(result['kept'].values())
    if kept:
        print(f" - 既存Numを維持: {kept}箇所")
    if result['unassigned']:
        print(f" - 未付与: {len(result['unassigned'])}箇所")
        for tag, line, title, reason in result['unassigned']:
            print(f"     - {input_path.name}:{line} <{tag}> {title or '（タイトルなし）'} … {reason}")
    if result['mismatched']:
        print(f" - 要確認（既存Numが方式による値と異なる。--overwrite で振り直し可）: {len(result['mismatched'])}箇所")
        for tag, line, title, current, value in result['mismatched']:
            print(f"     - {input_path.name}:{line} <{tag}> {title} 既存 Num=\"{current}\" / 方式 Num=\"{value}\"")
    if result['duplicated']:
        print(f" - 重複（同じNumが複数の要素に付与）: {len(result['duplicated'])}件")
        for tag, value, count in result['duplicated']:
            print(f"     - <{tag}> Num=\"{value}\" × {count}")
    print(f"\n出力ファイル: {output_path}")
    print("=" * 80)
    return 0


def main():
    parser = argparse.ArgumentParser(
        description='別表（AppdxTable）等の Num 属性を付与する後処理',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
例:
  python postprocess_appdxtable_num.py input.xml output.xml
  python postprocess_appdxtable_num.py input.xml output.xml --mode sequential
  python postprocess_appdxtable_num.py input.xml output.xml --overwrite
  python postprocess_appdxtable_num.py input.xml output.xml --elements AppdxTable,AppdxNote
"""
    )
    parser.add_argument('input_file', help='入力XMLファイル')
    parser.add_argument('output_file', help='出力XMLファイル')
    parser.add_argument('--mode', choices=list(MODES), default=MODE_TITLE,
                        help='付与方式: title=タイトル序数（デフォルト）、sequential=出現順連番')
    parser.add_argument('--overwrite', action='store_true',
                        help='既存の有効な Num も方式に従って振り直す')
    parser.add_argument('--elements', default=','.join(DEFAULT_ELEMENTS),
                        help=f'対象要素（カンマ区切り。既定: AppdxTable。指定可: {", ".join(SUPPORTED_ELEMENTS)}）')
    args = parser.parse_args()

    input_path = Path(args.input_file)
    output_path = Path(args.output_file)
    if not input_path.exists():
        print(f"エラー: 入力ファイルが見つかりません: {input_path}", file=sys.stderr)
        return 1
    elements = [e.strip() for e in args.elements.split(',') if e.strip()]
    unknown = [e for e in elements if e not in SUPPORTED_ELEMENTS]
    if unknown:
        print(f"エラー: 対象外の要素が指定されました: {', '.join(unknown)}"
              f"（指定可: {', '.join(SUPPORTED_ELEMENTS)}）", file=sys.stderr)
        return 1
    return process_file(input_path, output_path, mode=args.mode,
                        overwrite=args.overwrite, elements=elements)


if __name__ == '__main__':
    sys.exit(main())
