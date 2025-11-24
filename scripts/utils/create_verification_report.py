#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XML変換検証レポート生成スクリプト

2つのXMLファイルを比較し、構造が変更されたParagraph要素を検出して、
変更前と変更後の内容をMarkdown形式のレポートに出力します。
"""

import argparse
from pathlib import Path
from lxml import etree

def parse_xml(file_path):
    """XMLファイルをパースしてlxmlのElementTreeを返す"""
    try:
        tree = etree.parse(str(file_path))
        return tree
    except Exception as e:
        print(f"エラー: XMLファイルの読み込みに失敗しました: {file_path}")
        print(e)
        return None

def compare_paragraphs(original_tree, transformed_tree):
    """
    2つのXMLツリーのParagraph要素を比較し、変更があったもののリストを返す
    """
    changed_paragraphs = []
    
    # Paragraph要素をNum属性でマッピング
    original_paragraphs = {p.get('Num'): p for p in original_tree.xpath('.//Paragraph')}
    transformed_paragraphs = {p.get('Num'): p for p in transformed_tree.xpath('.//Paragraph')}

    for num, original_paragraph in original_paragraphs.items():
        if num in transformed_paragraphs:
            transformed_paragraph = transformed_paragraphs[num]
            
            # 要素を文字列に変換して比較（インデントや空白は無視）
            original_str = etree.tostring(original_paragraph, pretty_print=True, encoding='unicode')
            transformed_str = etree.tostring(transformed_paragraph, pretty_print=True, encoding='unicode')
            
            if original_str != transformed_str:
                changed_paragraphs.append({
                    'num': num,
                    'before_el': original_paragraph,
                    'after_el': transformed_paragraph
                })
                
    return changed_paragraphs

def write_report(report_path, original_file, transformed_file, changed_paragraphs):
    """
    Markdown形式でレポートを書き出す
    """
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"# XML変換検証レポート\n\n")
        f.write(f"**元ファイル:** `{original_file.name}`\n")
        f.write(f"**変換後ファイル:** `{transformed_file.name}`\n\n")
        f.write("---\n\n")
        
        if not changed_paragraphs:
            f.write("変更されたParagraph要素は見つかりませんでした。\n")
            return

        f.write(f"## 変更が検出されたParagraph要素 ({len(changed_paragraphs)}件)\n\n")
        
        for item in changed_paragraphs:
            f.write(f'### Paragraph Num="{item["num"]}"\n\n')
            
            f.write("#### 変更前\n")
            f.write("```xml\n")
            before_el = item['before_el']
            etree.indent(before_el, space="  ")
            before_str = etree.tostring(before_el, encoding='unicode', pretty_print=False)
            f.write(before_str.strip() + '\n')
            f.write("```\n\n")
            
            f.write("#### 変更後\n")
            f.write("```xml\n")
            after_el = item['after_el']
            etree.indent(after_el, space="  ")
            after_str = etree.tostring(after_el, encoding='unicode', pretty_print=False)
            f.write(after_str.strip() + '\n')
            f.write("```\n\n")
            f.write("---\n\n")

def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='2つのXMLファイルを比較し、変更されたParagraphのレポートを生成します。')
    parser.add_argument('original_file', help='変換前のXMLファイル')
    parser.add_argument('transformed_file', help='変換後のXMLファイル')
    parser.add_argument('report_path', help='出力するMarkdownレポートのパス')
    
    args = parser.parse_args()
    
    original_path = Path(args.original_file)
    transformed_path = Path(args.transformed_file)
    report_path = Path(args.report_path)
    
    if not original_path.exists() or not transformed_path.exists():
        print("エラー: 指定されたXMLファイルが見つかりません。")
        return

    print(f"比較中: {original_path.name} -> {transformed_path.name}")

    original_tree = parse_xml(original_path)
    transformed_tree = parse_xml(transformed_path)
    
    if original_tree is None or transformed_tree is None:
        return
        
    changed_items = compare_paragraphs(original_tree, transformed_tree)
    
    write_report(report_path, original_path, transformed_path, changed_items)
    
    print(f"レポートが生成されました: {report_path}")

if __name__ == '__main__':
    main()
