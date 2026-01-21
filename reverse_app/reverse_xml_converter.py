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
from typing import Optional, Tuple, Dict, List as ListType
from copy import deepcopy


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
    """要素のセンテンステキストを取得（最初のSentence要素のみ）"""
    sentence_elem = element.find(f'{config.sentence_tag}/Sentence')
    if sentence_elem is not None:
        return "".join(sentence_elem.itertext()).strip()
    return ""


def get_element_sentence_element(element, config: ReverseConversionConfig) -> Optional[etree.Element]:
    """要素のSentence要素全体を取得（Ruby要素などの子要素構造を保持）"""
    sentence_elem = element.find(f'{config.sentence_tag}/Sentence')
    return sentence_elem


def get_element_sentence_elements(element, config: ReverseConversionConfig) -> ListType[etree.Element]:
    """要素のSentence要素内のすべてのSentence要素を取得"""
    sentence_container = element.find(config.sentence_tag)
    if sentence_container is not None:
        sentences = sentence_container.findall('Sentence')
        return sentences
    return []


def get_element_sentence_columns(element, config: ReverseConversionConfig) -> ListType[etree.Element]:
    """要素のSentence内のすべてのColumn要素を取得"""
    sentence_elem = element.find(config.sentence_tag)
    if sentence_elem is not None:
        columns = sentence_elem.findall('Column')
        return columns
    return []


def has_title(element, config: ReverseConversionConfig) -> bool:
    """要素にタイトルがあるかチェック"""
    title_text = get_element_title_text(element, config)
    return bool(title_text.strip())


def create_list_element_with_columns(title_text: str, sentence_text: str, sentence_elem: Optional[etree.Element] = None) -> etree.Element:
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
    
    # Sentence要素全体をコピー（Ruby要素などの子要素構造を保持）
    if sentence_elem is not None:
        sentence2.text = sentence_elem.text
        for child in sentence_elem:
            sentence2.append(deepcopy(child))
        # 属性をコピー
        for attr_name, attr_value in sentence_elem.attrib.items():
            if attr_name != 'Num':  # Num属性は既に設定済みなのでスキップ
                sentence2.set(attr_name, attr_value)
    else:
        sentence2.text = sentence_text

    return list_elem


def create_list_element_with_columns_and_multiple_sentences(title_text: str, sentence_elements: ListType[etree.Element]) -> etree.Element:
    """タイトルと複数のSentence要素を持つ2カラムのList要素を作成"""
    list_elem = etree.Element('List')
    list_sentence = etree.SubElement(list_elem, 'ListSentence')

    # Column 1: Title
    col1 = etree.SubElement(list_sentence, 'Column', Num='1')
    sentence1 = etree.SubElement(col1, 'Sentence', Num='1')
    sentence1.text = title_text

    # Column 2: 複数のSentence要素
    col2 = etree.SubElement(list_sentence, 'Column', Num='2')
    for idx, sentence_elem in enumerate(sentence_elements, start=1):
        # Sentence要素を作成（Num属性は後で設定）
        sentence = etree.SubElement(col2, 'Sentence')
        # Sentence要素全体をコピー（Ruby要素などの子要素構造を保持）
        if sentence_elem is not None:
            sentence.text = sentence_elem.text
            for child in sentence_elem:
                sentence.append(deepcopy(child))
            # 元の属性を先にコピー（順序を保持）
            for attr_name, attr_value in sentence_elem.attrib.items():
                sentence.set(attr_name, attr_value)
            # Num属性を更新（既に存在する場合は上書き）
            sentence.set('Num', str(idx))
        else:
            sentence.set('Num', str(idx))

    return list_elem


def create_list_element_with_title_and_multiple_columns(title_text: str, columns: ListType[etree.Element]) -> etree.Element:
    """タイトルと複数のColumn要素を持つList要素を作成"""
    list_elem = etree.Element('List')
    list_sentence = etree.SubElement(list_elem, 'ListSentence')

    # Column 1: Title
    col1 = etree.SubElement(list_sentence, 'Column', Num='1')
    sentence1 = etree.SubElement(col1, 'Sentence', Num='1')
    sentence1.text = title_text

    # Column 2以降: 元のColumn要素をコピー
    for idx, column in enumerate(columns, start=2):
        new_column = deepcopy(column)
        new_column.set('Num', str(idx))
        list_sentence.append(new_column)

    return list_elem


def create_list_element_with_multiple_columns(columns: ListType[etree.Element]) -> etree.Element:
    """複数のColumn要素を持つList要素を作成（タイトルなし）"""
    list_elem = etree.Element('List')
    list_sentence = etree.SubElement(list_elem, 'ListSentence')

    # すべてのColumn要素をコピー
    for idx, column in enumerate(columns, start=1):
        new_column = deepcopy(column)
        new_column.set('Num', str(idx))
        list_sentence.append(new_column)

    return list_elem


def create_list_element_no_columns(sentence_text: str, sentence_elem: Optional[etree.Element] = None) -> etree.Element:
    """ColumnなしのList要素を作成"""
    list_elem = etree.Element('List')
    list_sentence = etree.SubElement(list_elem, 'ListSentence')
    sentence = etree.SubElement(list_sentence, 'Sentence', Num='1')
    
    # Sentence要素全体をコピー（Ruby要素などの子要素構造を保持）
    if sentence_elem is not None:
        sentence.text = sentence_elem.text
        for child in sentence_elem:
            sentence.append(deepcopy(child))
        # 属性をコピー
        for attr_name, attr_value in sentence_elem.attrib.items():
            if attr_name != 'Num':  # Num属性は既に設定済みなのでスキップ
                sentence.set(attr_name, attr_value)
    else:
        sentence.text = sentence_text
    
    return list_elem


def create_list_element_with_column_and_multiple_sentences(sentence_elements: ListType[etree.Element]) -> etree.Element:
    """タイトルなしで、1つのColumn内に複数のSentence要素を持つList要素を作成"""
    list_elem = etree.Element('List')
    list_sentence = etree.SubElement(list_elem, 'ListSentence')
    
    # Column Num="1"に複数のSentence要素を配置
    col1 = etree.SubElement(list_sentence, 'Column', Num='1')
    for idx, sentence_elem in enumerate(sentence_elements, start=1):
        # Sentence要素を作成（Num属性は後で設定）
        sentence = etree.SubElement(col1, 'Sentence')
        # Sentence要素全体をコピー（Ruby要素などの子要素構造を保持）
        if sentence_elem is not None:
            sentence.text = sentence_elem.text
            for child in sentence_elem:
                sentence.append(deepcopy(child))
            # 元の属性を先にコピー（順序を保持）
            for attr_name, attr_value in sentence_elem.attrib.items():
                sentence.set(attr_name, attr_value)
            # Num属性を更新（既に存在する場合は上書き）
            sentence.set('Num', str(idx))
        else:
            sentence.set('Num', str(idx))
    
    return list_elem


def convert_child_to_list(child_elem, config: ReverseConversionConfig, stats) -> Tuple[ListType[etree.Element], ListType]:
    """
    子要素をList要素に変換
    返り値: (変換されたList要素のリスト, 子要素内の子要素（孫要素）のリスト)、または([], [])（変換不要の場合）
    """
    if child_elem.tag != config.child_tag:
        return [], []

    title_text = get_element_title_text(child_elem, config)
    sentence_text = get_element_sentence_text(child_elem, config)
    sentence_elem = get_element_sentence_element(child_elem, config)
    sentence_elements = get_element_sentence_elements(child_elem, config)
    columns = get_element_sentence_columns(child_elem, config)

    # 子要素内の子要素（孫要素）を取得（List要素やその他の要素）
    # パイプラインでは内側から外側へ順番に処理するため、
    # この時点で子要素内の子要素は既にList要素に変換されている可能性がある
    child_children = []
    for grandchild in list(child_elem):
        # TitleとSentence以外の要素（既に変換されたList要素やその他の要素）を保持
        if grandchild.tag != config.title_tag and grandchild.tag != config.sentence_tag:
            child_children.append(deepcopy(grandchild))

    list_elements = []

    # 複数のColumn要素がある場合の処理
    if len(columns) > 0:
        if title_text:
            # ケース3: タイトルがあり、複数のColumn要素がある場合
            list_elem = create_list_element_with_title_and_multiple_columns(title_text, columns)
            list_elements.append(list_elem)
            stats['CONVERTED_WITH_TITLE'] += 1
        else:
            # ケース4: タイトルが空で、複数のColumn要素がある場合
            list_elem = create_list_element_with_multiple_columns(columns)
            list_elements.append(list_elem)
            stats['CONVERTED_NO_TITLE'] += 1
    else:
        # 複数のSentence要素がある場合の処理
        if len(sentence_elements) > 1:
            if title_text:
                # ケース5: タイトルがあり、複数のSentence要素がある場合
                # すべてのSentence要素を1つのColumn内に配置
                list_elem = create_list_element_with_columns_and_multiple_sentences(title_text, sentence_elements)
                list_elements.append(list_elem)
                stats['CONVERTED_WITH_TITLE'] += 1
            else:
                # ケース6: タイトルが空で、複数のSentence要素がある場合
                # 1つのList要素のColumn内に複数のSentence要素を配置
                list_elem = create_list_element_with_column_and_multiple_sentences(sentence_elements)
                list_elements.append(list_elem)
                stats['CONVERTED_NO_TITLE'] += 1
        else:
            # 通常のケース: Column要素がなく、Sentence要素が1つのみの場合
            if title_text:
                # ケース1: タイトルがある場合（2カラムList）
                list_elem = create_list_element_with_columns(title_text, sentence_text, sentence_elem)
                list_elements.append(list_elem)
                stats['CONVERTED_WITH_TITLE'] += 1
            else:
                # ケース2: タイトルがない場合（ColumnなしList）
                list_elem = create_list_element_no_columns(sentence_text, sentence_elem)
                list_elements.append(list_elem)
                stats['CONVERTED_NO_TITLE'] += 1

    return list_elements, child_children


def process_parent_element(parent_elem, config: ReverseConversionConfig, stats) -> bool:
    """
    親要素内の子要素をList要素に変換
    """
    # Item要素を処理する場合、親要素のタグに関係なく処理する
    # （Paragraph, AppdxTable, その他の要素に対応）
    if config.child_tag == 'Item':
        # 直接の子要素としてItem要素があるかチェック
        has_item_child = any(child.tag == config.child_tag for child in parent_elem)
        if not has_item_child:
            return False
    elif parent_elem.tag != config.parent_tag:
        return False

    made_changes = False
    new_children = []

    # 親要素の既存の子要素を取得
    for child in list(parent_elem):
        if child.tag == config.child_tag:
            # 子要素をListに変換
            list_elements, child_children = convert_child_to_list(child, config, stats)
            if len(list_elements) > 0:
                # 複数のList要素を追加
                for list_elem in list_elements:
                    new_children.append(list_elem)
                # 子要素内の子要素（孫要素）をList要素の後に追加
                # これにより、階層構造がフラットなList要素の並びに変換される
                for grandchild in child_children:
                    new_children.append(grandchild)
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
    if config.child_tag == 'Item':
        # Item要素を子要素として持つすべての要素を処理対象にする
        # Paragraph, AppdxTable, その他の要素に対応
        parent_elements = root.xpath(f'.//*[{config.child_tag}]')
        # 重複を除去（子要素が親要素としても含まれる可能性があるため）
        seen = set()
        unique_parents = []
        for elem in parent_elements:
            elem_id = id(elem)
            if elem_id not in seen:
                seen.add(elem_id)
                unique_parents.append(elem)
        parent_elements = unique_parents
    elif config.parent_tag == 'Paragraph':
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


def main_with_config(config: ReverseConversionConfig, description: str, default_output_suffix: str):
    """
    共通のmain()関数
    
    Args:
        config: 逆変換設定
        description: スクリプトの説明
        default_output_suffix: デフォルトの出力ファイル名のサフィックス（例: '_reverse_item.xml'）
    """
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f'''
使用例:
  python3 {config.script_name}.py input.xml
  python3 {config.script_name}.py input.xml output.xml
        '''
    )

    parser.add_argument('input_file', help='入力XMLファイル')
    parser.add_argument('output_file', nargs='?', help=f'出力XMLファイル（デフォルト: {default_output_suffix}）')

    args = parser.parse_args()

    input_path = Path(args.input_file)

    if not input_path.exists():
        print(f"エラー: 入力ファイルが見つかりません: {args.input_file}", file=sys.stderr)
        return 1

    output_path = Path(args.output_file) if args.output_file else input_path.parent / f"{input_path.stem}{default_output_suffix}"

    return process_xml_file(input_path, output_path, config)
