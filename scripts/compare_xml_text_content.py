#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
2つのXMLファイルを比較し、テキスト内容の欠落がないか検証するスクリプト

以下も併せて検証します。
- 表（TableStruct）の順序と数
- 図（Fig）の文書順と数
- テキストを持たない構造要素（TableStruct/FigStruct/StyleStruct/Fig）の数

Fig等は自身にテキストを持たないため、テキスト比較だけでは欠落も複製も
検出できない。専用の検証を行う。
"""

import re
import sys
import difflib
import argparse
from lxml import etree
from pathlib import Path

def normalize_spaces(text: str) -> str:
    """全角スペース（U+3000）と半角スペースをすべて除去する"""
    return text.replace('　', '').replace(' ', '')


def get_all_texts(tree: etree._ElementTree, ignore_spaces: bool = False) -> set:
    """
    XMLツリーからすべてのテキストコンテンツを抽出し、セットとして返す。
    空白文字のみのテキストは除外する。

    Args:
        ignore_spaces: Trueの場合、テキスト中の全角・半角スペースを
            除去してから比較用セットに追加する
    """
    texts = set()
    for element in tree.iter():
        if element.text:
            text = element.text.strip()
            if ignore_spaces:
                text = normalize_spaces(text)
            if text:
                texts.add(text)
    return texts

def get_element_context_text(elem: etree._Element, max_length: int = 50) -> str:
    """
    要素のコンテキスト（テキスト）を取得する
    
    Args:
        elem: 要素
        max_length: 最大文字数
    
    Returns:
        要素のテキスト（最初のSentence要素のテキスト、または要素のテキスト）
    """
    # Sentence要素を探す
    sentence = elem.find('.//Sentence')
    if sentence is not None and sentence.text:
        text = sentence.text.strip()
        return text[:max_length] if len(text) > max_length else text
    
    # 要素自体のテキスト
    if elem.text:
        text = elem.text.strip()
        return text[:max_length] if len(text) > max_length else text
    
    return ""

def get_table_sequence(tree: etree._ElementTree, ignore_spaces: bool = False) -> list:
    """
    XMLツリーからTableStruct要素を文書順序で取得し、表の識別子のリストとして返す。
    同じ内容のTableStructが複数ある場合でも、位置情報を含めることで区別できるようにする。

    Args:
        ignore_spaces: Trueの場合、表の内容テキスト中の全角・半角スペースを
            除去してから識別子を作成する

    Returns:
        表の識別子（内容 + 位置情報）のリスト
    """
    tables = []
    # 文書順序でTableStructを取得
    for elem in tree.getroot().iter():
        if elem.tag == 'TableStruct':
            # 表全体のテキストを取得
            # TableStructTitle（表１等）はマークアップによって表の内外どちらにも
            # 置かれ得るため、内容比較からは除外する
            texts = []
            for sub in elem.iter():
                if sub.tag == 'TableStructTitle' or \
                        any(a.tag == 'TableStructTitle'
                            for a in sub.iterancestors()):
                    continue
                if sub.text and sub.text.strip():
                    text = sub.text.strip()
                    if ignore_spaces:
                        text = normalize_spaces(text)
                    if text:
                        texts.append(text)
            
            # 表の内容識別用に最初の10個のテキストを使用
            content_id = ' | '.join(texts[:10]) if texts else ""
            
            # 位置情報を取得
            parent = elem.getparent()
            if parent is not None:
                siblings = list(parent)
                table_index = siblings.index(elem)
                
                # 親要素の情報
                parent_tag = parent.tag
                parent_info = parent_tag
                
                # 親要素のタイトルやNum属性を取得
                if parent_tag == 'Paragraph':
                    para_num = parent.find('ParagraphNum')
                    if para_num is not None and para_num.text:
                        parent_info = f"{parent_tag}[{para_num.text.strip()}]"
                elif parent_tag.startswith('Subitem') or parent_tag == 'Item':
                    title_elem = parent.find(f'{parent_tag}Title')
                    if title_elem is not None and title_elem.text:
                        parent_info = f"{parent_tag}[{title_elem.text.strip()[:20]}]"
                    elif parent.get('Num'):
                        parent_info = f"{parent_tag}[Num={parent.get('Num')}]"
                
                # 前後の要素の情報を取得
                context_parts = []
                
                # 前の要素
                if table_index > 0:
                    prev_elem = siblings[table_index - 1]
                    prev_text = get_element_context_text(prev_elem, max_length=30)
                    if prev_text:
                        context_parts.append(f"prev:{prev_elem.tag}[{prev_text}]")
                
                # 次の要素
                if table_index < len(siblings) - 1:
                    next_elem = siblings[table_index + 1]
                    next_text = get_element_context_text(next_elem, max_length=30)
                    if next_text:
                        context_parts.append(f"next:{next_elem.tag}[{next_text}]")
                
                # 位置情報を含めた識別子を作成
                context_str = ' | '.join(context_parts) if context_parts else ""
                if context_str:
                    table_id = f"{content_id} | POS:{parent_info}[{table_index}] | {context_str}"
                else:
                    table_id = f"{content_id} | POS:{parent_info}[{table_index}]"
            else:
                # 親要素がない場合（通常は発生しない）
                table_id = content_id if content_id else "EMPTY_TABLE"
            
            tables.append(table_id)
    return tables

# テキストを持たないため、テキスト比較では欠落・複製を検出できない構造要素。
# 数と文書順を専用に検証する。
STRUCT_TAGS = ['TableStruct', 'FigStruct', 'StyleStruct', 'Fig']


def get_fig_sequence(tree: etree._ElementTree) -> list:
    """XMLツリーからFig要素を文書順序で取得し、識別子のリストとして返す。

    Fig要素は ``<Fig src="./pict/xxx.jpg"/>`` のようにテキストを持たないため、
    テキスト比較（get_all_texts / compare_text_order）では欠落も複製も検出
    できない。src属性を識別子として文書順に並べ、元ファイルと完全一致
    （数・順序の両方）することを検証するために使用する。

    Returns:
        Figの識別子（src属性）のリスト
    """
    figs = []
    for elem in tree.getroot().iter():
        if elem.tag == 'Fig':
            src = (elem.get('src') or '').strip()
            figs.append(src if src else "EMPTY_FIG_SRC")
    return figs


def get_struct_counts(tree: etree._ElementTree) -> dict:
    """テキストを持たない構造要素の出現数を数える。

    TableStruct/FigStruct/StyleStruct/Fig は自身にテキストを持たないため、
    集合ベースのテキスト比較では増減が素通りする。要素数の増減を直接
    検証するために使用する。

    Returns:
        {タグ名: 出現数} の辞書
    """
    counts = {tag: 0 for tag in STRUCT_TAGS}
    for elem in tree.getroot().iter():
        if elem.tag in counts:
            counts[elem.tag] += 1
    return counts


def get_full_document_text(tree: etree._ElementTree) -> str:
    """文書順の全テキストを連結し、空白（全角スペース含む）を除去して返す

    マークアップ変換ではラベルと本文の区切りスペースが要素分割により
    消えるため、順序比較は常に空白を無視した文字列で行う。
    """
    text = ''.join(tree.getroot().itertext())
    return normalize_spaces(''.join(text.split()))


def compare_text_order(original_tree: etree._ElementTree,
                       final_tree: etree._ElementTree,
                       max_issues: int = 20) -> list:
    """文書順の全文比較で、テキストの欠落・順序の入れ替わりを検出する。

    set比較（get_all_texts）は断片の存在しか見ないため、順序の入れ替わりや
    重複断片の片方欠落を検出できない。ここでは全文を文書順に連結した
    文字列同士を比較し、元ファイルのテキストが同じ順序で残っているかを検証する。

    マークアップ変換で正当に発生する差分は許容する:
      - 区切りスペースの消失（空白除去で吸収）
      - Article分割時のParagraphNum複製等による「挿入」(insert)

    一方、「削除」(delete)・「置換」(replace)は、テキストの欠落または
    順序の入れ替わり（移動元からの消失）を意味するためエラーとする。

    Returns:
        検出された問題のリスト。各要素は
        {'kind': 'reordered'|'missing', 'position': int,
         'fragment': str, 'context': str} の辞書。
    """
    a = get_full_document_text(original_tree)
    b = get_full_document_text(final_tree)
    if a == b:
        return []

    # 極端に大きい文書ではSequenceMatcherが遅くなるため、
    # 最初の差分位置のみ報告する簡易モードにフォールバックする
    if max(len(a), len(b)) > 300_000:
        pos = next((i for i in range(min(len(a), len(b))) if a[i] != b[i]),
                   min(len(a), len(b)))
        return [{
            'kind': 'missing',
            'position': pos,
            'fragment': a[pos:pos + 80],
            'context': a[max(0, pos - 40):pos],
        }]

    issues = []
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag not in ('delete', 'replace'):
            continue
        fragment = a[i1:i2]
        # 断片が最終ファイルの別の場所に存在すれば「順序の入れ替わり」、
        # 存在しなければ「欠落」
        probe = fragment[:40]
        kind = 'reordered' if probe and probe in b else 'missing'
        issues.append({
            'kind': kind,
            'position': i1,
            'fragment': fragment[:80],
            'context': a[max(0, i1 - 40):i1],
        })
        if len(issues) >= max_issues:
            break
    return issues


def main():
    parser = argparse.ArgumentParser(
        description="Compare two XML files to check for missing text content."
    )
    parser.add_argument('original_file', help='Original XML file (before conversion)')
    parser.add_argument('final_file', help='Final XML file (after conversion)')
    parser.add_argument('--report_file', help='Path to save the comparison report', default='xml_comparison_report.txt')
    parser.add_argument('--ignore-spaces', action='store_true',
                        help='全角・半角スペースの有無を無視して比較する')

    args = parser.parse_args()

    original_path = Path(args.original_file)
    final_path = Path(args.final_file)
    report_path = Path(args.report_file)

    if not original_path.exists():
        print(f"Error: Original file not found at {original_path}")
        sys.exit(1)
    if not final_path.exists():
        print(f"Error: Final file not found at {final_path}")
        sys.exit(1)

    print("=" * 80)
    print("XML Text Content Comparison")
    print("=" * 80)
    print(f"Original file: {original_path}")
    print(f"Final file   : {final_path}")
    print("-" * 80)

    try:
        original_tree = etree.parse(str(original_path))
        final_tree = etree.parse(str(final_path))
    except etree.XMLSyntaxError as e:
        print(f"Error parsing XML: {e}")
        sys.exit(1)

    if args.ignore_spaces:
        print("Mode: 全角・半角スペースの有無を無視して比較")

    original_texts = get_all_texts(original_tree)
    final_texts = get_all_texts(final_tree)

    print(f"Found {len(original_texts)} unique text elements in the original file.")
    print(f"Found {len(final_texts)} unique text elements in the final file.")

    # --ignore-spaces時はスペースを除去した形で照合する
    if args.ignore_spaces:
        norm = normalize_spaces
    else:
        norm = lambda t: t  # noqa: E731
    final_norm_texts = {n for n in (norm(t) for t in final_texts) if n}

    def is_present(fragment: str) -> bool:
        """テキスト片が最終ファイルに存在するか（完全一致または部分文字列）

        部分文字列一致は、変換過程で複数のColumn/Sentenceが全角スペース
        結合などで1つのSentenceにまとめられる場合（結合）に対応する。
        """
        n = norm(fragment)
        if not n:
            return True
        if n in final_norm_texts:
            return True
        return any(n in final_text for final_text in final_norm_texts)

    def can_cover_by_split(text: str) -> bool:
        """分割フォールバック: テキストをスペース位置で複数の断片に分割し、
        すべての断片が最終ファイルの要素テキストと完全一致する分割方法が
        存在するかを判定する（動的計画法）。

        「①　本文」のようなラベル＋本文の1要素が、マークアップにより
        Title要素と本文Sentenceに分割される場合に対応する。本文中に
        スペースが残るケース（「（ｉ）　排水管　共用配管との…」等）も、
        任意の分割位置の組合せで照合する。断片の照合は完全一致のみとし、
        単なるスペース挿入の差（例:「屋内 階段」→「屋内階段」）を
        ここで許容しないようにする。
        """
        separators = list(re.finditer(r'[　 ]+', text))
        if not separators:
            return False
        # 断片の開始/終了候補位置（先頭、各スペース区切り、末尾）
        starts = [0] + [m.end() for m in separators]
        ends = [m.start() for m in separators] + [len(text)]

        memo = {}

        def feasible(start_idx: int) -> bool:
            """starts[start_idx]以降の残り全体を要素テキストで被覆できるか"""
            if start_idx == len(starts):
                return True
            if start_idx in memo:
                return memo[start_idx]
            result = False
            for end_idx in range(start_idx, len(ends)):
                piece = text[starts[start_idx]:ends[end_idx]]
                n = norm(piece)
                if not n:
                    # 空断片（連続スペース等）は読み飛ばす
                    if feasible(end_idx + 1):
                        result = True
                        break
                    continue
                if n in final_norm_texts and feasible(end_idx + 1):
                    result = True
                    break
            memo[start_idx] = result
            return result

        # 全体を1断片とみなす被覆（=分割なし）は is_present で判定済みのため、
        # ここでは少なくとも1箇所で分割される被覆のみが成立し得る
        # （全体一致なら is_present が True になっている）
        return feasible(0)

    missing_texts = set()
    for text in original_texts:
        if is_present(text):
            continue
        if can_cover_by_split(text):
            continue
        missing_texts.add(text)

    # 文書順の全文比較（順序の入れ替わり・重複断片の欠落を検出）
    order_issues = compare_text_order(original_tree, final_tree)

    print("-" * 80)
    if not order_issues:
        print("✅ Text order is correct.")
    else:
        reordered = [x for x in order_issues if x['kind'] == 'reordered']
        lost = [x for x in order_issues if x['kind'] == 'missing']
        print(f"❌ Error: Found {len(order_issues)} text order/content issue(s) "
              f"(reordered: {len(reordered)}, missing: {len(lost)}).")
        for issue in order_issues[:5]:
            kind_label = '順序入れ替わり' if issue['kind'] == 'reordered' else '欠落'
            print(f"  [{kind_label}] 位置 {issue['position']}:")
            print(f"    直前の文脈: …{issue['context']}")
            print(f"    対象テキスト: {issue['fragment']}…")
        if len(order_issues) > 5:
            print(f"  ... and {len(order_issues) - 5} more issues")

    # 表の順序と数を検証
    original_tables = get_table_sequence(original_tree, ignore_spaces=args.ignore_spaces)
    final_tables = get_table_sequence(final_tree, ignore_spaces=args.ignore_spaces)

    print("-" * 80)
    print(f"Found {len(original_tables)} tables in the original file.")
    print(f"Found {len(final_tables)} tables in the final file.")

    table_order_errors = []
    table_position_warnings = []
    table_count_error = None

    # 表の数の検証
    if len(original_tables) != len(final_tables):
        table_count_error = f"❌ Error: Table count mismatch. Original: {len(original_tables)}, Final: {len(final_tables)}"
        print(table_count_error)
    else:
        # 表の内容のみで順序を検証（位置情報を除く）
        original_content = [t.split(' | POS:')[0] for t in original_tables]
        final_content = [t.split(' | POS:')[0] for t in final_tables]
        
        # 内容の順序が一致しているか確認
        content_order_match = original_content == final_content
        
        # 位置情報を含めた詳細な比較
        for i in range(len(original_tables)):
            if original_tables[i] != final_tables[i]:
                # 内容が同じかどうかを確認
                if original_content[i] == final_content[i]:
                    # 内容は同じだが位置情報が異なる場合は警告
                    table_position_warnings.append({
                        'index': i + 1,
                        'original': original_tables[i][:150],
                        'final': final_tables[i][:150]
                    })
                else:
                    # 内容が異なる場合はエラー
                    table_order_errors.append({
                        'index': i + 1,
                        'original': original_tables[i][:100],
                        'final': final_tables[i][:100]
                    })
        
        # 結果の表示
        if table_order_errors:
            print(f"❌ Error: Found {len(table_order_errors)} table(s) with content order mismatch.")
            for error in table_order_errors[:5]:  # 最初の5つのエラーのみ表示
                print(f"  Position {error['index']}:")
                print(f"    Original: {error['original']}...")
                print(f"    Final:    {error['final']}...")
            if len(table_order_errors) > 5:
                print(f"  ... and {len(table_order_errors) - 5} more content order mismatches")
        elif table_position_warnings:
            # 位置情報の違いは警告として表示（内容の順序は一致している）
            print(f"✅ Table content order is correct.")
            print(f"⚠️  Warning: Found {len(table_position_warnings)} table(s) with position changes (this is normal after conversion).")
            if len(table_position_warnings) <= 5:
                for warning in table_position_warnings:
                    print(f"  Position {warning['index']}:")
                    print(f"    Original: {warning['original']}...")
                    print(f"    Final:    {warning['final']}...")
            else:
                for warning in table_position_warnings[:3]:
                    print(f"  Position {warning['index']}:")
                    print(f"    Original: {warning['original']}...")
                    print(f"    Final:    {warning['final']}...")
                print(f"  ... and {len(table_position_warnings) - 3} more position changes")
        else:
            print("✅ Table order is correct.")

    # 図（Fig）の順序と数を検証
    # Figはテキストを持たないため、上のテキスト比較では欠落も複製も検出できない
    original_figs = get_fig_sequence(original_tree)
    final_figs = get_fig_sequence(final_tree)

    print("-" * 80)
    print(f"Found {len(original_figs)} figures in the original file.")
    print(f"Found {len(final_figs)} figures in the final file.")

    fig_count_error = None
    fig_order_errors = []

    if len(original_figs) != len(final_figs):
        fig_count_error = (f"❌ Error: Figure count mismatch. "
                           f"Original: {len(original_figs)}, Final: {len(final_figs)}")
        print(fig_count_error)
        # 数が違う場合でも、どのFigがずれたのかを併せて報告する
        for i in range(min(len(original_figs), len(final_figs))):
            if original_figs[i] != final_figs[i]:
                fig_order_errors.append({
                    'index': i + 1,
                    'original': original_figs[i],
                    'final': final_figs[i],
                })
                break
    else:
        for i in range(len(original_figs)):
            if original_figs[i] != final_figs[i]:
                fig_order_errors.append({
                    'index': i + 1,
                    'original': original_figs[i],
                    'final': final_figs[i],
                })

    if fig_order_errors:
        print(f"❌ Error: Found {len(fig_order_errors)} figure(s) with order mismatch.")
        for error in fig_order_errors[:5]:
            print(f"  Position {error['index']}:")
            print(f"    Original: {error['original']}")
            print(f"    Final:    {error['final']}")
        if len(fig_order_errors) > 5:
            print(f"  ... and {len(fig_order_errors) - 5} more figure order mismatches")
    elif not fig_count_error:
        print("✅ Figure order is correct.")

    # テキストを持たない構造要素の数を検証
    # （TableStruct/FigStruct/StyleStruct/Fig の欠落・複製はテキスト比較では素通りする）
    original_counts = get_struct_counts(original_tree)
    final_counts = get_struct_counts(final_tree)

    print("-" * 80)
    struct_count_errors = []
    for tag in STRUCT_TAGS:
        if original_counts[tag] != final_counts[tag]:
            struct_count_errors.append({
                'tag': tag,
                'original': original_counts[tag],
                'final': final_counts[tag],
            })

    if struct_count_errors:
        print(f"❌ Error: Found {len(struct_count_errors)} struct element count mismatch(es).")
        for error in struct_count_errors:
            diff = error['final'] - error['original']
            direction = '複製' if diff > 0 else '欠落'
            print(f"  {error['tag']}: Original {error['original']} → "
                  f"Final {error['final']} ({diff:+d}: {direction})")
    else:
        summary = ', '.join(f"{tag}={original_counts[tag]}" for tag in STRUCT_TAGS)
        print(f"✅ Struct element counts are correct. ({summary})")

    print("-" * 80)

    # レポートファイルに書き込み
    has_errors = False
    with report_path.open('w', encoding='utf-8') as f:
        # テキスト内容の検証結果
        if not missing_texts:
            success_message = "✅ Success: All text content from the original file is present in the final file."
            print(success_message)
            f.write(success_message + "\n\n")
        else:
            has_errors = True
            error_message = f"❌ Error: Found {len(missing_texts)} text elements missing from the final file."
            print(error_message)
            f.write(error_message + "\n\n")
            f.write("Missing text elements:\n")
            f.write("-" * 30 + "\n")
            for i, text in enumerate(sorted(list(missing_texts))):
                f.write(f"{i+1}: {text}\n")
            f.write("\n")
        
        # 文書順の全文比較の結果
        f.write("=" * 80 + "\n")
        f.write("Text Order Validation Results\n")
        f.write("=" * 80 + "\n\n")

        if not order_issues:
            f.write("✅ Text order is correct.\n\n")
        else:
            has_errors = True
            reordered = [x for x in order_issues if x['kind'] == 'reordered']
            lost = [x for x in order_issues if x['kind'] == 'missing']
            f.write(f"❌ Error: Found {len(order_issues)} text order/content issue(s) "
                    f"(reordered: {len(reordered)}, missing: {len(lost)}).\n\n")
            f.write("Text order/content issues:\n")
            f.write("-" * 30 + "\n")
            for issue in order_issues:
                kind_label = '順序入れ替わり' if issue['kind'] == 'reordered' else '欠落'
                f.write(f"[{kind_label}] 位置 {issue['position']}:\n")
                f.write(f"  直前の文脈: …{issue['context']}\n")
                f.write(f"  対象テキスト: {issue['fragment']}…\n\n")

        # 表の検証結果
        f.write("=" * 80 + "\n")
        f.write("Table Validation Results\n")
        f.write("=" * 80 + "\n\n")
        
        if table_count_error:
            has_errors = True
            f.write(table_count_error + "\n\n")
        
        if table_order_errors:
            has_errors = True
            f.write(f"❌ Error: Found {len(table_order_errors)} table(s) with content order mismatch.\n\n")
            f.write("Table content order mismatches:\n")
            f.write("-" * 30 + "\n")
            for error in table_order_errors:
                f.write(f"Position {error['index']}:\n")
                f.write(f"  Original: {error['original']}\n")
                f.write(f"  Final:    {error['final']}\n\n")
        elif table_position_warnings:
            f.write("✅ Table content order is correct.\n\n")
            f.write(f"⚠️  Warning: Found {len(table_position_warnings)} table(s) with position changes.\n")
            f.write("This is normal after conversion (tables may move to different parent elements).\n\n")
            f.write("Table position changes:\n")
            f.write("-" * 30 + "\n")
            for warning in table_position_warnings[:10]:  # 最初の10個のみ表示
                f.write(f"Position {warning['index']}:\n")
                f.write(f"  Original: {warning['original']}\n")
                f.write(f"  Final:    {warning['final']}\n\n")
            if len(table_position_warnings) > 10:
                f.write(f"... and {len(table_position_warnings) - 10} more position changes\n\n")
        elif not table_count_error:
            f.write("✅ Table order is correct.\n")
        
        # 図の検証結果
        f.write("=" * 80 + "\n")
        f.write("Figure Validation Results\n")
        f.write("=" * 80 + "\n\n")

        if fig_count_error:
            has_errors = True
            f.write(fig_count_error + "\n\n")

        if fig_order_errors:
            has_errors = True
            f.write(f"❌ Error: Found {len(fig_order_errors)} figure(s) with order mismatch.\n\n")
            f.write("Figure order mismatches:\n")
            f.write("-" * 30 + "\n")
            for error in fig_order_errors:
                f.write(f"Position {error['index']}:\n")
                f.write(f"  Original: {error['original']}\n")
                f.write(f"  Final:    {error['final']}\n\n")
        elif not fig_count_error:
            f.write("✅ Figure order is correct.\n\n")

        # 構造要素数の検証結果
        f.write("=" * 80 + "\n")
        f.write("Struct Element Count Validation Results\n")
        f.write("=" * 80 + "\n\n")

        if struct_count_errors:
            has_errors = True
            f.write(f"❌ Error: Found {len(struct_count_errors)} struct element "
                    f"count mismatch(es).\n\n")
            f.write("Struct element count mismatches:\n")
            f.write("-" * 30 + "\n")
            for error in struct_count_errors:
                diff = error['final'] - error['original']
                direction = '複製' if diff > 0 else '欠落'
                f.write(f"{error['tag']}: Original {error['original']} → "
                        f"Final {error['final']} ({diff:+d}: {direction})\n")
            f.write("\n")
        else:
            f.write("✅ Struct element counts are correct.\n")
            for tag in STRUCT_TAGS:
                f.write(f"  {tag}: {original_counts[tag]}\n")
            f.write("\n")

        print(f"A detailed report has been saved to: {report_path}")

    print("=" * 80)

    # エラーがある場合は1を返す（位置情報の違いは警告のみなので、エラーとして扱わない）
    return 0 if (not missing_texts and not order_issues
                 and not table_count_error and not table_order_errors
                 and not fig_count_error and not fig_order_errors
                 and not struct_count_errors) else 1

if __name__ == '__main__':
    sys.exit(main())
