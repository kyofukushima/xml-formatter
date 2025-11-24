#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
逆XML変換モジュール

Paragraph~subitem要素をList要素に変換する共通ロジック
xml_converter.pyの逆方向処理を実装
"""

import sys
import argparse
import re
from pathlib import Path
from lxml import etree
from typing import Optional, Tuple, Dict, List
from copy import deepcopy

# 親ディレクトリのutils/をインポートパスに追加
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.label_utils import is_label


class ReverseConversionConfig:
    """逆変換設定を管理するクラス"""
    def __init__(self,
                 parent_tag: str,           # 親要素タグ (Paragraph/Item/Subitem1)
                 child_tag: str,            # 子要素タグ (Item/Subitem1/Subitem2)
                 title_tag: str,            # タイトル要素タグ
                 sentence_tag: str,         # センテンス要素タグ
                 script_name: str):         # スクリプト名
        self.parent_tag = parent_tag
        self.child_tag = child_tag
        self.title_tag = title_tag
        self.sentence_tag = sentence_tag
        self.script_name = script_name


def format_xml_lxml(tree, output_path):
    """lxmlのElementTreeをインデント整形して保存"""
    clean_root = etree.fromstring(etree.tostring(tree.getroot()))
    etree.indent(clean_root, space="  ", level=0)
    new_tree = etree.ElementTree(clean_root)
    new_tree.write(
        output_path,
        encoding='utf-8',
        xml_declaration=True,
        pretty_print=False
    )


def get_element_title_text(element, config: ReverseConversionConfig) -> str:
    """要素のタイトルテキストを取得"""
    title_elem = element.find(config.title_tag)
    if title_elem is not None:
        return "".join(title_elem.itertext()).strip()
    return ""


def get_element_sentence_text(element, config: ReverseConversionConfig) -> str:
    """要素のセンテンステキストを取得"""
    sentence_elem = element.find(f'{config.sentence_tag}/Sentence')
    if sentence_elem is not None:
        return "".join(sentence_elem.itertext()).strip()
    return ""


def has_title(element, config: ReverseConversionConfig) -> bool:
    """要素にタイトルがあるかチェック"""
    title_text = get_element_title_text(element, config)
    return bool(title_text.strip())


def create_list_element_with_columns(title_text: str, sentence_text: str) -> etree.Element:
    """2カラムのList要素を作成"""
    list_elem = etree.Element('List')
    list_sentence = etree.SubElement(list_elem, 'ListSentence')

    # Column 1: Title
    col1 = etree.SubElement(list_sentence, 'Column', Num='1')
    sentence1 = etree.SubElement(col1, 'Sentence', Num='1')
    sentence1.text = title_text

    # Column 2: Sentence content
    col2 = etree.SubElement(list_sentence, 'Column', Num='2')
    sentence2 = etree.SubElement(col2, 'Sentence', Num='1')
    sentence2.text = sentence_text

    return list_elem


def create_list_element_no_columns(sentence_text: str) -> etree.Element:
    """ColumnなしのList要素を作成"""
    list_elem = etree.Element('List')
    list_sentence = etree.SubElement(list_elem, 'ListSentence')
    sentence = etree.SubElement(list_sentence, 'Sentence', Num='1')
    sentence.text = sentence_text
    return list_elem


def convert_child_to_list(child_elem, config: ReverseConversionConfig, stats) -> Optional[etree.Element]:
    """
    子要素をList要素に変換
    返り値: 変換されたList要素、またはNone（変換不要の場合）
    """
    if child_elem.tag != config.child_tag:
        return None

    title_text = get_element_title_text(child_elem, config)
    sentence_text = get_element_sentence_text(child_elem, config)

    # タイトルがある場合は2カラムList、ない場合はColumnなしList
    if title_text:
        list_elem = create_list_element_with_columns(title_text, sentence_text)
        stats['CONVERTED_WITH_TITLE'] += 1
        return list_elem
    else:
        list_elem = create_list_element_no_columns(sentence_text)
        stats['CONVERTED_NO_TITLE'] += 1
        return list_elem


def process_parent_element(parent_elem, config: ReverseConversionConfig, stats) -> bool:
    """
    親要素内の子要素をList要素に変換
    """
    if parent_elem.tag != config.parent_tag:
        return False

    made_changes = False
    new_children = []

    # 親要素の既存の子要素を取得
    for child in list(parent_elem):
        if child.tag == config.child_tag:
            # 子要素をListに変換
            list_elem = convert_child_to_list(child, config, stats)
            if list_elem is not None:
                new_children.append(list_elem)
                made_changes = True
            else:
                new_children.append(child)
        else:
            # List要素やその他の要素はそのまま
            new_children.append(child)

    # 子要素を置き換え
    if made_changes:
        # 既存の子要素をクリア
        for child in list(parent_elem):
            parent_elem.remove(child)

        # 新しい子要素を追加
        for new_child in new_children:
            parent_elem.append(new_child)

    return made_changes


def process_xml_file(input_path: Path, output_path: Path, config: ReverseConversionConfig) -> int:
    """XMLファイルを処理"""
    print("=" * 80)
    print(f"【{config.parent_tag} → List 逆変換】")
    print("=" * 80)
    print(f"入力ファイル: {input_path}")

    try:
        tree = etree.parse(str(input_path))
    except Exception as e:
        print(f"エラー: XMLファイルの読み込みに失敗しました: {e}", file=sys.stderr)
        return 1

    stats = {
        'CONVERTED_WITH_TITLE': 0,
        'CONVERTED_NO_TITLE': 0
    }

    root = tree.getroot()

    # 処理対象の親要素を取得
    if config.parent_tag == 'Paragraph':
        # ドキュメント内の全Paragraph要素を処理
        parent_elements = root.xpath('.//Paragraph')
    else:
        # 指定された親要素内の子要素を処理
        parent_elements = root.xpath(f'.//{config.parent_tag}')

    total_changes = 0
    for parent_elem in parent_elements:
        if process_parent_element(parent_elem, config, stats):
            total_changes += 1

    print("\n変換統計:")
    print(f" - タイトルあり → 2カラムList: {stats['CONVERTED_WITH_TITLE']}箇所")
    print(f" - タイトルなし → ColumnなしList: {stats['CONVERTED_NO_TITLE']}箇所")
    print(f" - 変更された親要素数: {total_changes}箇所")

    format_xml_lxml(tree, str(output_path))

    print(f"\n出力ファイル: {output_path}")
    print(" ✅ インデント整形済み")
    print("=" * 80)

    return 0
