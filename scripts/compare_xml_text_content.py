#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
2つのXMLファイルを比較し、テキスト内容の欠落がないか検証するスクリプト
表の順序と数も検証します。
"""

import sys
import argparse
from lxml import etree
from pathlib import Path

def get_all_texts(tree: etree._ElementTree) -> set:
    """
    XMLツリーからすべてのテキストコンテンツを抽出し、セットとして返す。
    空白文字のみのテキストは除外する。
    """
    texts = set()
    for element in tree.iter():
        if element.text:
            text = element.text.strip()
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

def get_table_sequence(tree: etree._ElementTree) -> list:
    """
    XMLツリーからTableStruct要素を文書順序で取得し、表の識別子のリストとして返す。
    同じ内容のTableStructが複数ある場合でも、位置情報を含めることで区別できるようにする。
    
    Returns:
        表の識別子（内容 + 位置情報）のリスト
    """
    tables = []
    # 文書順序でTableStructを取得
    for elem in tree.getroot().iter():
        if elem.tag == 'TableStruct':
            # 表全体のテキストを取得
            texts = []
            for sub in elem.iter():
                if sub.text and sub.text.strip():
                    texts.append(sub.text.strip())
            
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

def main():
    parser = argparse.ArgumentParser(
        description="Compare two XML files to check for missing text content."
    )
    parser.add_argument('original_file', help='Original XML file (before conversion)')
    parser.add_argument('final_file', help='Final XML file (after conversion)')
    parser.add_argument('--report_file', help='Path to save the comparison report', default='xml_comparison_report.txt')

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

    original_texts = get_all_texts(original_tree)
    final_texts = get_all_texts(final_tree)

    print(f"Found {len(original_texts)} unique text elements in the original file.")
    print(f"Found {len(final_texts)} unique text elements in the final file.")

    missing_texts = original_texts - final_texts

    # 表の順序と数を検証
    original_tables = get_table_sequence(original_tree)
    final_tables = get_table_sequence(final_tree)

    print("-" * 80)
    print(f"Found {len(original_tables)} tables in the original file.")
    print(f"Found {len(final_tables)} tables in the final file.")

    table_order_errors = []
    table_count_error = None

    # 表の数の検証
    if len(original_tables) != len(final_tables):
        table_count_error = f"❌ Error: Table count mismatch. Original: {len(original_tables)}, Final: {len(final_tables)}"
        print(table_count_error)
    else:
        # 表の順序の検証
        for i in range(len(original_tables)):
            if original_tables[i] != final_tables[i]:
                table_order_errors.append({
                    'index': i + 1,
                    'original': original_tables[i][:100],
                    'final': final_tables[i][:100]
                })
        
        if table_order_errors:
            print(f"❌ Error: Found {len(table_order_errors)} table(s) with order mismatch.")
            for error in table_order_errors[:5]:  # 最初の5つのエラーのみ表示
                print(f"  Position {error['index']}:")
                print(f"    Original: {error['original']}...")
                print(f"    Final:    {error['final']}...")
            if len(table_order_errors) > 5:
                print(f"  ... and {len(table_order_errors) - 5} more order mismatches")
        else:
            print("✅ Table order is correct.")

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
        
        # 表の検証結果
        f.write("=" * 80 + "\n")
        f.write("Table Validation Results\n")
        f.write("=" * 80 + "\n\n")
        
        if table_count_error:
            has_errors = True
            f.write(table_count_error + "\n\n")
        
        if table_order_errors:
            has_errors = True
            f.write(f"❌ Error: Found {len(table_order_errors)} table(s) with order mismatch.\n\n")
            f.write("Table order mismatches:\n")
            f.write("-" * 30 + "\n")
            for error in table_order_errors:
                f.write(f"Position {error['index']}:\n")
                f.write(f"  Original: {error['original']}\n")
                f.write(f"  Final:    {error['final']}\n\n")
        elif not table_count_error:
            f.write("✅ Table order is correct.\n")
        
        print(f"A detailed report has been saved to: {report_path}")

    print("=" * 80)

    # エラーがある場合は1を返す
    return 0 if not missing_texts and not table_count_error and not table_order_errors else 1

if __name__ == '__main__':
    sys.exit(main())
