#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
2つのXMLファイルを比較し、テキスト内容の欠落がないか検証するスクリプト
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

    print("-" * 80)

    with report_path.open('w', encoding='utf-8') as f:
        if not missing_texts:
            success_message = "✅ Success: All text content from the original file is present in the final file."
            print(success_message)
            f.write(success_message + "\n")
        else:
            error_message = f"❌ Error: Found {len(missing_texts)} text elements missing from the final file."
            print(error_message)
            f.write(error_message + "\n\n")
            f.write("Missing text elements:\n")
            f.write("-" * 30 + "\n")
            for i, text in enumerate(sorted(list(missing_texts))):
                f.write(f"{i+1}: {text}\n")
            print(f"A detailed report has been saved to: {report_path}")

    print("=" * 80)

    return 0 if not missing_texts else 1

if __name__ == '__main__':
    sys.exit(main())
