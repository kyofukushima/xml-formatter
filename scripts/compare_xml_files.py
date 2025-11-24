#!/usr/bin/env python3
"""
XMLファイル比較スクリプト
スクリプト実行前後のXMLファイルを比較し、値の改変や順序の変更を検出します。
"""

import sys
import os
from xml.etree import ElementTree as ET
from collections import defaultdict
import difflib

class XMLComparator:
    def __init__(self, file1, file2):
        self.file1 = file1
        self.file2 = file2
        self.differences = []
        self.element_counts = defaultdict(lambda: {'file1': 0, 'file2': 0})

    def parse_xml(self, file_path):
        """XMLファイルをパース"""
        try:
            tree = ET.parse(file_path)
            return tree.getroot()
        except Exception as e:
            print(f"XMLパースエラー ({file_path}): {e}")
            sys.exit(1)

    def get_element_path(self, element):
        """要素のXPath風パスを取得"""
        path = []
        current = element
        while current is not None:
            if current.tag:
                tag = current.tag
                if 'Num' in current.attrib:
                    tag += f"[@Num='{current.attrib['Num']}']"
                path.insert(0, tag)
            current = current.getparent() if hasattr(current, 'getparent') else None
        return '/'.join(path)

    def normalize_text(self, text):
        """テキストの正規化"""
        if text is None:
            return ""
        return text.strip()

    def compare_elements_recursive(self, elem1, elem2, path=""):
        """要素を再帰的に比較"""
        current_path = f"{path}/{elem1.tag}" if path else elem1.tag

        # 要素数のカウント
        self.element_counts[elem1.tag]['file1'] += 1
        self.element_counts[elem2.tag]['file2'] += 1

        # タグ名の比較
        if elem1.tag != elem2.tag:
            self.differences.append({
                'type': 'tag_mismatch',
                'path': current_path,
                'file1_tag': elem1.tag,
                'file2_tag': elem2.tag
            })

        # 属性の比較
        attrs1 = dict(elem1.attrib)
        attrs2 = dict(elem2.attrib)

        if attrs1 != attrs2:
            self.differences.append({
                'type': 'attribute_difference',
                'path': current_path,
                'file1_attrs': attrs1,
                'file2_attrs': attrs2
            })

        # テキストの比較
        text1 = self.normalize_text(elem1.text)
        text2 = self.normalize_text(elem2.text)

        if text1 != text2:
            self.differences.append({
                'type': 'text_difference',
                'path': current_path,
                'file1_text': text1,
                'file2_text': text2
            })
            print(f"TEXT_DIFFERENCE detected: {current_path}")
            print(f"  File1: {text1[:50]}{'...' if len(text1) > 50 else ''}")
            print(f"  File2: {text2[:50]}{'...' if len(text2) > 50 else ''}")


        # 子要素数の比較
        children1 = list(elem1)
        children2 = list(elem2)

        if len(children1) != len(children2):
            self.differences.append({
                'type': 'children_count_mismatch',
                'path': current_path,
                'file1_count': len(children1),
                'file2_count': len(children2)
            })
            return

        # 子要素の比較
        for i, (child1, child2) in enumerate(zip(children1, children2)):
            child_path = f"{current_path}[{i+1}]"
            self.compare_elements_recursive(child1, child2, child_path)

    def compare_structure_order(self, root1, root2):
        """構造の順序を比較"""
        def get_structure_list(element, path=""):
            structures = []
            current_path = f"{path}/{element.tag}" if path else element.tag
            structures.append(current_path)

            for i, child in enumerate(element):
                structures.extend(get_structure_list(child, current_path))
            return structures

        struct1 = get_structure_list(root1)
        struct2 = get_structure_list(root2)

        if struct1 != struct2:
            # 順序の違いを検出
            diff = list(difflib.unified_diff(struct1, struct2, lineterm=''))
            if diff:
                self.differences.append({
                    'type': 'structure_order_difference',
                    'details': '\n'.join(diff)
                })

    def compare_text_content(self, root1, root2):
        """テキスト内容の包括的な比較"""
        def collect_all_text(element, path=""):
            texts = []
            current_path = f"{path}/{element.tag}" if path else element.tag

            # テキストノードの収集
            if element.text and element.text.strip():
                texts.append({
                    'path': current_path,
                    'text': element.text.strip(),
                    'tag': element.tag
                })

            # 子要素の再帰処理
            for child in element:
                texts.extend(collect_all_text(child, current_path))

            return texts

        texts1 = collect_all_text(root1)
        texts2 = collect_all_text(root2)

        # テキスト内容の比較
        text_diffs = []
        for text1 in texts1:
            # 同じパスのテキストを探す
            matching_text = None
            for text2 in texts2:
                if text1['path'] == text2['path']:
                    matching_text = text2
                    break

            if matching_text and text1['text'] != matching_text['text']:
                text_diffs.append({
                    'type': 'text_content_difference',
                    'path': text1['path'],
                    'file1_text': text1['text'],
                    'file2_text': matching_text['text']
                })

        return text_diffs

    def generate_report(self):
        """比較レポートを生成"""
        report = []
        report.append("=" * 80)
        report.append("XMLファイル比較レポート")
        report.append("=" * 80)
        report.append(f"ファイル1: {self.file1}")
        report.append(f"ファイル2: {self.file2}")
        report.append("")

        # 構造比較の結果
        root1 = ET.parse(self.file1).getroot()
        root2 = ET.parse(self.file2).getroot()
        text_diffs = self.compare_text_content(root1, root2)

        if not self.differences and not text_diffs:
            report.append("✓ 差異は検出されませんでした。")
            return "\n".join(report)

        # すべての差異を統合
        all_diffs = self.differences + text_diffs
        report.append(f"検出された差異: {len(all_diffs)}件")
        report.append("")

        for i, diff in enumerate(all_diffs, 1):
            report.append(f"{i}. {diff['type'].upper()}")
            report.append(f"   パス: {diff.get('path', 'N/A')}")

            if diff['type'] == 'tag_mismatch':
                report.append(f"   ファイル1: {diff['file1_tag']}")
                report.append(f"   ファイル2: {diff['file2_tag']}")
            elif diff['type'] == 'attribute_difference':
                report.append(f"   ファイル1属性: {diff['file1_attrs']}")
                report.append(f"   ファイル2属性: {diff['file2_attrs']}")
            elif diff['type'] == 'text_difference':
                report.append(f"   ファイル1テキスト: {diff['file1_text'][:100]}{'...' if len(diff['file1_text']) > 100 else ''}")
                report.append(f"   ファイル2テキスト: {diff['file2_text'][:100]}{'...' if len(diff['file2_text']) > 100 else ''}")
            elif diff['type'] == 'children_count_mismatch':
                report.append(f"   ファイル1子要素数: {diff['file1_count']}")
                report.append(f"   ファイル2子要素数: {diff['file2_count']}")
            elif diff['type'] == 'structure_order_difference':
                report.append("   構造順序の違い:")
                report.append("   " + "\n   ".join(diff['details'].split('\n')[:20]))  # 最初の20行のみ
                if len(diff['details'].split('\n')) > 20:
                    report.append("   ... (続き省略)")
            elif diff['type'] == 'text_content_difference':
                report.append(f"   ファイル1テキスト: {diff['file1_text'][:100]}{'...' if len(diff['file1_text']) > 100 else ''}")
                report.append(f"   ファイル2テキスト: {diff['file2_text'][:100]}{'...' if len(diff['file2_text']) > 100 else ''}")

            report.append("")

        # 要素数のサマリー
        report.append("要素数サマリー:")
        report.append("-" * 40)
        for tag, counts in sorted(self.element_counts.items()):
            if counts['file1'] != counts['file2']:
                report.append(f"{tag}: ファイル1={counts['file1']}, ファイル2={counts['file2']}")

        return "\n".join(report)

    def compare(self):
        """比較を実行"""
        print("XMLファイルを比較中...")

        root1 = self.parse_xml(self.file1)
        root2 = self.parse_xml(self.file2)

        # 構造順序の比較
        self.compare_structure_order(root1, root2)

        # 詳細比較
        self.compare_elements_recursive(root1, root2)

        return self.generate_report()

def main():
    # 直接ファイルパスを指定（ブラケットを含むファイル名のエスケープ問題回避）
    file1 = "/Users/fukushima/Documents/xml_anken/education_xml/input/H29null[2400]063_H29null[2400]063_R020401_1.xml"
    file2 = "/Users/fukushima/Documents/xml_anken/education_xml/output/H29null[2400]063_H29null[2400]063_R020401_1-final.xml"

    # コマンドライン引数が指定された場合はそちらを使用
    if len(sys.argv) >= 3:
        file1 = sys.argv[1]
        file2 = sys.argv[2]

    if not os.path.exists(file1):
        print(f"ファイルが見つかりません: {file1}")
        sys.exit(1)

    if not os.path.exists(file2):
        print(f"ファイルが見つかりません: {file2}")
        sys.exit(1)

    comparator = XMLComparator(file1, file2)
    report = comparator.compare()

    print(report)

    # レポートをファイルに保存
    report_file = "xml_comparison_report.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\nレポートを保存しました: {report_file}")

if __name__ == "__main__":
    main()
