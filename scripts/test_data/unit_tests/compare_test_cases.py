#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
convert_item_step0とconvert_subitem1_step0のテストケースを比較するスクリプト

内容が同じで、階層のみが異なるかをチェックします。
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import sys


def normalize_xml_text(text: Optional[str]) -> str:
    """XMLテキストを正規化"""
    if text is None:
        return ""
    return text.strip()


def extract_text_content(elem: ET.Element) -> str:
    """要素のテキスト内容を抽出（タグ名を除く）"""
    texts = []
    
    # 要素自体のテキスト
    if elem.text:
        texts.append(normalize_xml_text(elem.text))
    
    # 子要素のテキストを再帰的に取得
    for child in elem:
        child_text = extract_text_content(child)
        if child_text:
            texts.append(child_text)
        # tailテキストも取得
        if child.tail:
            texts.append(normalize_xml_text(child.tail))
    
    return " ".join(filter(None, texts))


def compare_xml_structure(item_elem: ET.Element, subitem_elem: ET.Element, path: str = "") -> List[str]:
    """XML構造を比較して、内容が同じで階層のみが異なるかをチェック"""
    issues = []
    
    # タグ名のマッピング（Item -> Subitem1）
    tag_mapping = {
        'Item': 'Subitem1',
        'ItemTitle': 'Subitem1Title',
        'ItemSentence': 'Subitem1Sentence',
    }
    
    # テキスト内容を比較
    item_text = extract_text_content(item_elem)
    subitem_text = extract_text_content(subitem_elem)
    
    # タグ名を正規化して比較
    item_tag = item_elem.tag
    expected_subitem_tag = tag_mapping.get(item_tag, item_tag)
    subitem_tag = subitem_elem.tag
    
    if expected_subitem_tag != subitem_tag:
        issues.append(f"{path}: タグ名が異なります - 期待: {expected_subitem_tag}, 実際: {subitem_tag}")
    
    # 子要素を比較
    item_children = list(item_elem)
    subitem_children = list(subitem_elem)
    
    # ItemTitleとItemSentenceを除外して比較（これらは変換される）
    item_filtered = [c for c in item_children if c.tag not in ['ItemTitle', 'ItemSentence']]
    subitem_filtered = [c for c in subitem_children if c.tag not in ['Subitem1Title', 'Subitem1Sentence']]
    
    # List要素の数を比較
    item_lists = [c for c in item_children if c.tag == 'List']
    subitem_lists = [c for c in subitem_children if c.tag == 'List']
    
    if len(item_lists) != len(subitem_lists):
        issues.append(f"{path}: List要素の数が異なります - Item: {len(item_lists)}, Subitem1: {len(subitem_lists)}")
    
    # 各List要素を比較
    for i, (item_list, subitem_list) in enumerate(zip(item_lists, subitem_lists)):
        list_path = f"{path}/List[{i}]"
        list_issues = compare_list_elements(item_list, subitem_list, list_path)
        issues.extend(list_issues)
    
    # その他の子要素を比較（Subitem1, Subitem2など）
    item_other = [c for c in item_children if c.tag not in ['ItemTitle', 'ItemSentence', 'List']]
    subitem_other = [c for c in subitem_children if c.tag not in ['Subitem1Title', 'Subitem1Sentence', 'List']]
    
    if len(item_other) != len(subitem_other):
        issues.append(f"{path}: その他の子要素の数が異なります - Item: {len(item_other)}, Subitem1: {len(subitem_other)}")
    
    return issues


def compare_list_elements(item_list: ET.Element, subitem_list: ET.Element, path: str) -> List[str]:
    """List要素を比較"""
    issues = []
    
    item_sentences = item_list.findall('ListSentence')
    subitem_sentences = subitem_list.findall('ListSentence')
    
    if len(item_sentences) != len(subitem_sentences):
        issues.append(f"{path}: ListSentence要素の数が異なります")
        return issues
    
    for i, (item_sentence, subitem_sentence) in enumerate(zip(item_sentences, subitem_sentences)):
        sentence_path = f"{path}/ListSentence[{i}]"
        
        item_columns = item_sentence.findall('Column')
        subitem_columns = subitem_sentence.findall('Column')
        
        if len(item_columns) != len(subitem_columns):
            issues.append(f"{sentence_path}: Column要素の数が異なります - Item: {len(item_columns)}, Subitem1: {len(subitem_columns)}")
            continue
        
        # Column要素を比較
        for j, (item_col, subitem_col) in enumerate(zip(item_columns, subitem_columns)):
            col_path = f"{sentence_path}/Column[{j}]"
            
            item_col_text = extract_text_content(item_col)
            subitem_col_text = extract_text_content(subitem_col)
            
            # Column Num="1"の場合はラベルが変更される可能性があるので、警告のみ
            if item_col.get('Num') == '1':
                if item_col_text != subitem_col_text:
                    issues.append(f"{col_path}: ラベルが変更されています - Item: '{item_col_text}', Subitem1: '{subitem_col_text}' (これは変換ロジックによる変更の可能性があります)")
            else:
                if item_col_text != subitem_col_text:
                    issues.append(f"{col_path}: 内容が異なります - Item: '{item_col_text}', Subitem1: '{subitem_col_text}'")
        
        # ColumnなしのListSentenceの場合
        item_sentence_text = extract_text_content(item_sentence)
        subitem_sentence_text = extract_text_content(subitem_sentence)
        if item_sentence_text and not item_columns:
            if item_sentence_text != subitem_sentence_text:
                issues.append(f"{sentence_path}: 内容が異なります - Item: '{item_sentence_text}', Subitem1: '{subitem_sentence_text}'")
    
    return issues


def compare_test_case(test_case_name: str, base_dir: Path) -> Tuple[bool, List[str]]:
    """1つのテストケースを比較"""
    item_dir = base_dir / 'convert_item_step0' / test_case_name
    subitem_dir = base_dir / 'test_generated' / 'convert_subitem1_step0' / test_case_name
    
    issues = []
    
    # input.xmlを比較
    item_input = item_dir / 'input.xml'
    subitem_input = subitem_dir / 'input.xml'
    
    if not item_input.exists():
        issues.append(f"  input.xml: 元のファイルが見つかりません: {item_input}")
    elif not subitem_input.exists():
        issues.append(f"  input.xml: 生成されたファイルが見つかりません: {subitem_input}")
    else:
        try:
            item_input_tree = ET.parse(item_input)
            subitem_input_tree = ET.parse(subitem_input)
            
            item_input_root = item_input_tree.getroot()
            subitem_input_root = subitem_input_tree.getroot()
            
            # Paragraph要素を比較
            item_paragraph = item_input_root.find('.//Paragraph')
            subitem_paragraph = subitem_input_root.find('.//Paragraph')
            
            if item_paragraph is None:
                issues.append(f"  input.xml: Item側にParagraph要素が見つかりません")
            elif subitem_paragraph is None:
                issues.append(f"  input.xml: Subitem1側にParagraph要素が見つかりません")
            else:
                # List要素を比較
                item_lists = item_paragraph.findall('List')
                subitem_item = subitem_paragraph.find('Item')
                
                if subitem_item is None:
                    issues.append(f"  input.xml: Subitem1側にItem要素が見つかりません")
                else:
                    subitem_lists = subitem_item.findall('List')
                    
                    if len(item_lists) != len(subitem_lists):
                        issues.append(f"  input.xml: List要素の数が異なります - Item: {len(item_lists)}, Subitem1: {len(subitem_lists)}")
                    else:
                        for i, (item_list, subitem_list) in enumerate(zip(item_lists, subitem_lists)):
                            list_issues = compare_list_elements(item_list, subitem_list, f"input.xml/List[{i}]")
                            issues.extend([f"  {issue}" for issue in list_issues])
        except Exception as e:
            issues.append(f"  input.xml: 比較中にエラーが発生しました: {e}")
    
    # expected.xmlを比較
    item_expected = item_dir / 'expected.xml'
    subitem_expected = subitem_dir / 'expected.xml'
    
    if not item_expected.exists():
        issues.append(f"  expected.xml: 元のファイルが見つかりません: {item_expected}")
    elif not subitem_expected.exists():
        issues.append(f"  expected.xml: 生成されたファイルが見つかりません: {subitem_expected}")
    else:
        try:
            item_expected_tree = ET.parse(item_expected)
            subitem_expected_tree = ET.parse(subitem_expected)
            
            item_expected_root = item_expected_tree.getroot()
            subitem_expected_root = subitem_expected_tree.getroot()
            
            # Paragraph要素を取得
            item_paragraph = item_expected_root.find('.//Paragraph')
            subitem_paragraph = subitem_expected_root.find('.//Paragraph')
            
            if item_paragraph is None:
                issues.append(f"  expected.xml: Item側にParagraph要素が見つかりません")
            elif subitem_paragraph is None:
                issues.append(f"  expected.xml: Subitem1側にParagraph要素が見つかりません")
            else:
                # Item要素を取得
                item_items = item_paragraph.findall('Item')
                subitem_item = subitem_paragraph.find('Item')
                
                if len(item_items) == 0:
                    issues.append(f"  expected.xml: Item側にItem要素が見つかりません")
                elif subitem_item is None:
                    issues.append(f"  expected.xml: Subitem1側にItem要素が見つかりません")
                else:
                    # Subitem1要素を取得
                    subitem_subitems = subitem_item.findall('Subitem1')
                    
                    if len(item_items) != len(subitem_subitems):
                        issues.append(f"  expected.xml: Item要素の数が異なります - Item: {len(item_items)}, Subitem1: {len(subitem_subitems)}")
                    else:
                        for i, (item_item, subitem_subitem) in enumerate(zip(item_items, subitem_subitems)):
                            item_issues = compare_xml_structure(item_item, subitem_subitem, f"expected.xml/Item[{i}]")
                            issues.extend([f"  {issue}" for issue in item_issues])
        except Exception as e:
            issues.append(f"  expected.xml: 比較中にエラーが発生しました: {e}")
    
    return len(issues) == 0, issues


def main():
    """メイン関数"""
    base_dir = Path(__file__).parent
    
    item_dir = base_dir / 'convert_item_step0'
    if not item_dir.exists():
        print(f"エラー: {item_dir} が見つかりません", file=sys.stderr)
        return 1
    
    # テストケース一覧を取得
    test_cases = []
    for item in item_dir.iterdir():
        if item.is_dir() and not item.name.startswith('_') and item.name != 'test_generated':
            test_cases.append(item.name)
    
    test_cases = sorted(test_cases)
    
    print(f"テストケース数: {len(test_cases)}\n")
    
    all_passed = True
    total_issues = 0
    
    for test_case_name in test_cases:
        print(f"チェック中: {test_case_name}")
        passed, issues = compare_test_case(test_case_name, base_dir)
        
        if passed:
            print(f"  ✓ OK\n")
        else:
            all_passed = False
            total_issues += len(issues)
            print(f"  ✗ 問題が見つかりました ({len(issues)}件):")
            for issue in issues:
                print(f"    {issue}")
            print()
    
    print("=" * 80)
    if all_passed:
        print("✓ すべてのテストケースが正しく生成されています")
        return 0
    else:
        print(f"✗ {len(test_cases)}個のテストケース中、{total_issues}件の問題が見つかりました")
        return 1


if __name__ == '__main__':
    sys.exit(main())










