#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
逆変換後のXMLファイルの順序検証スクリプト

逆変換前後のXMLファイルを比較し、XMLファイル上で登場する値の順番が
変わっていないことを検証します。

使用方法:
    python3 verify_reverse_order.py <元のXMLファイル> <逆変換後のXMLファイル> [--report <レポートファイル>]

例:
    python3 verify_reverse_order.py input.xml output.xml
    python3 verify_reverse_order.py input.xml output.xml --report order_report.txt
"""

import sys
import argparse
from pathlib import Path
from lxml import etree
from typing import List, Tuple, Optional


def extract_texts_in_order(tree: etree._ElementTree) -> List[Tuple[str, str]]:
    """
    XMLツリーからすべてのテキストノードを順番に抽出します。
    
    Args:
        tree: XMLツリー
        
    Returns:
        テキストとその要素タグのタプルのリスト（順序保持）
    """
    texts = []
    
    def traverse(element):
        """要素を順番に走査してテキストを抽出"""
        # 要素の直接のテキスト
        if element.text:
            text = element.text.strip()
            if text:
                texts.append((text, element.tag))
        
        # 子要素を順番に処理
        for child in element:
            traverse(child)
            
            # 子要素の後のテキスト（tail）
            if child.tail:
                tail_text = child.tail.strip()
                if tail_text:
                    texts.append((tail_text, element.tag))
    
    traverse(tree.getroot())
    return texts


def compare_text_order(
    original_texts: List[Tuple[str, str]],
    converted_texts: List[Tuple[str, str]]
) -> Tuple[bool, List[str]]:
    """
    2つのテキストリストの順序を比較します。
    
    Args:
        original_texts: 元のXMLファイルのテキストリスト
        converted_texts: 逆変換後のXMLファイルのテキストリスト
        
    Returns:
        (順序が一致しているか, 差異のレポート)
    """
    report = []
    is_order_preserved = True
    
    # テキストの数が異なる場合
    if len(original_texts) != len(converted_texts):
        report.append(f"⚠️  テキストの数が異なります:")
        report.append(f"   元のファイル: {len(original_texts)}個")
        report.append(f"   逆変換後: {len(converted_texts)}個")
        is_order_preserved = False
    
    # 順序の比較
    mismatches = []
    min_len = min(len(original_texts), len(converted_texts))
    
    for i in range(min_len):
        orig_text, orig_tag = original_texts[i]
        conv_text, conv_tag = converted_texts[i]
        
        if orig_text != conv_text:
            mismatches.append({
                'index': i + 1,
                'original': (orig_text, orig_tag),
                'converted': (conv_text, conv_tag)
            })
            is_order_preserved = False
    
    if mismatches:
        report.append(f"\n❌ 順序の不一致が {len(mismatches)} 箇所で検出されました:")
        report.append("-" * 80)
        
        # 最初の10件を表示
        display_count = min(10, len(mismatches))
        for i, mismatch in enumerate(mismatches[:display_count]):
            orig_text, orig_tag = mismatch['original']
            conv_text, conv_tag = mismatch['converted']
            report.append(f"\n位置 {mismatch['index']}:")
            report.append(f"  元のファイル: [{orig_tag}] {orig_text[:50]}{'...' if len(orig_text) > 50 else ''}")
            report.append(f"  逆変換後:     [{conv_tag}] {conv_text[:50]}{'...' if len(conv_text) > 50 else ''}")
        
        if len(mismatches) > display_count:
            report.append(f"\n... 他 {len(mismatches) - display_count} 件の不一致があります")
    
    return is_order_preserved, report


def generate_summary_report(
    original_texts: List[Tuple[str, str]],
    converted_texts: List[Tuple[str, str]],
    is_order_preserved: bool,
    details: List[str]
) -> str:
    """
    検証レポートを生成します。
    
    Args:
        original_texts: 元のXMLファイルのテキストリスト
        converted_texts: 逆変換後のXMLファイルのテキストリスト
        is_order_preserved: 順序が保持されているか
        details: 詳細な差異情報
        
    Returns:
        レポート文字列
    """
    report = []
    report.append("=" * 80)
    report.append("逆変換順序検証レポート")
    report.append("=" * 80)
    report.append("")
    
    # 統計情報
    report.append("統計情報:")
    report.append("-" * 80)
    report.append(f"元のファイルのテキスト数: {len(original_texts)}")
    report.append(f"逆変換後のテキスト数: {len(converted_texts)}")
    report.append("")
    
    # 結果サマリー
    report.append("検証結果:")
    report.append("-" * 80)
    if is_order_preserved:
        report.append("✅ 成功: XMLファイル上で登場する値の順番は保持されています。")
    else:
        report.append("❌ 失敗: XMLファイル上で登場する値の順番に変更が検出されました。")
    report.append("")
    
    # 詳細情報
    if details:
        report.append("詳細:")
        report.append("-" * 80)
        report.extend(details)
        report.append("")
    
    report.append("=" * 80)
    
    return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(
        description="逆変換前後のXMLファイルの順序を検証します",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
例:
  python3 verify_reverse_order.py input.xml output.xml
  python3 verify_reverse_order.py input.xml output.xml --report order_report.txt
        """
    )
    parser.add_argument(
        'original_file',
        help='元のXMLファイル（逆変換前）'
    )
    parser.add_argument(
        'converted_file',
        help='逆変換後のXMLファイル'
    )
    parser.add_argument(
        '--report',
        help='レポートを保存するファイルパス（デフォルト: reverse_order_report.txt）',
        default='reverse_order_report.txt'
    )
    
    args = parser.parse_args()
    
    original_path = Path(args.original_file)
    converted_path = Path(args.converted_file)
    report_path = Path(args.report)
    
    # ファイルの存在確認
    if not original_path.exists():
        print(f"❌ エラー: 元のファイルが見つかりません: {original_path}", file=sys.stderr)
        sys.exit(1)
    
    if not converted_path.exists():
        print(f"❌ エラー: 逆変換後のファイルが見つかりません: {converted_path}", file=sys.stderr)
        sys.exit(1)
    
    print("=" * 80)
    print("逆変換順序検証")
    print("=" * 80)
    print(f"元のファイル: {original_path}")
    print(f"逆変換後:     {converted_path}")
    print("-" * 80)
    
    try:
        # XMLファイルのパース
        print("XMLファイルを読み込み中...")
        original_tree = etree.parse(str(original_path))
        converted_tree = etree.parse(str(converted_path))
        
        # テキストの抽出
        print("テキストを抽出中...")
        original_texts = extract_texts_in_order(original_tree)
        converted_texts = extract_texts_in_order(converted_tree)
        
        print(f"元のファイルから {len(original_texts)} 個のテキストを抽出")
        print(f"逆変換後から {len(converted_texts)} 個のテキストを抽出")
        print("-" * 80)
        
        # 順序の比較
        print("順序を比較中...")
        is_order_preserved, details = compare_text_order(original_texts, converted_texts)
        
        # レポートの生成
        report = generate_summary_report(
            original_texts,
            converted_texts,
            is_order_preserved,
            details
        )
        
        # レポートの表示と保存
        print("\n" + report)
        
        with report_path.open('w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\nレポートを保存しました: {report_path}")
        print("=" * 80)
        
        # 終了コード
        sys.exit(0 if is_order_preserved else 1)
        
    except etree.XMLSyntaxError as e:
        print(f"❌ XMLパースエラー: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
