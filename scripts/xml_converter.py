#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
共通XML変換モジュール

convert_item_step0.py, convert_subitem1_step0.py, convert_subitem2_step0.py の共通ロジック
subitem1のロジックを基準として実装（学年チェック含む）
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

from utils.label_utils import get_hierarchy_level, is_label, detect_label_id, get_number_type, get_alphabet_type, is_valid_label_id
from utils.bracket_utils import is_subject_name_bracket, is_instruction_bracket, is_grade_single_bracket, is_grade_double_bracket


class ConversionConfig:
    """変換設定を管理するクラス"""
    def __init__(self,
                 parent_tag: str,           # 親要素タグ (Paragraph/Item/Subitem1)
                 child_tag: str,            # 子要素タグ (Item/Subitem1/Subitem2)
                 title_tag: str,            # タイトル要素タグ
                 sentence_tag: str,         # センテンス要素タグ
                 column_condition_min: int, # Column数の最小条件
                 supported_types: List[str], # サポートするタイプリスト
                 script_name: str,          # スクリプト名
                 skip_empty_parent: bool = False):  # 親要素空チェックを行うか
        self.parent_tag = parent_tag
        self.child_tag = child_tag
        self.title_tag = title_tag
        self.sentence_tag = sentence_tag
        self.column_condition_min = column_condition_min
        self.supported_types = supported_types
        self.script_name = script_name
        self.skip_empty_parent = skip_empty_parent


def is_grade_pattern(text: str) -> bool:
    """テキストが学年パターンかチェック（〔第...学年...〕形式）"""
    if not text:
        return False
    text = text.strip()
    return bool(re.match(r'^[〔【]第.+学年.*[〕】]$', text))


def count_grades(text: str) -> int:
    """学年パターンのテキストから学年数をカウント"""
    if not text or not is_grade_pattern(text):
        return 0

    # 「第X学年」パターンをカウント
    grade_pattern = r'第\d+学年'
    matches = re.findall(grade_pattern, text)
    return len(matches)


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


def is_kanji_number_label(text: str) -> bool:
    """漢数字ラベルかどうかを判定（一, 二などの漢数字）"""
    return text in ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十']


def is_parent_empty(parent_elem, config: ConversionConfig) -> bool:
    """
    親要素が空（Title空 + Sentence空）かチェック
    """
    if parent_elem is None:
        return False

    if config.parent_tag == 'Paragraph':
        # Paragraphの場合：ParagraphNumとParagraphSentenceが空かチェック
        num_elem = parent_elem.find('ParagraphNum')
        sentence_elem = parent_elem.find('ParagraphSentence/Sentence')

        # ParagraphNumが空かチェック
        num_text = "".join(num_elem.itertext()).strip() if num_elem is not None else ""
        num_empty = not num_text

        # ParagraphSentenceが空かチェック
        sentence_text = "".join(sentence_elem.itertext()).strip() if sentence_elem is not None else ""
        sentence_empty = not sentence_text

        return num_empty and sentence_empty

    elif config.parent_tag == 'Item':
        title = parent_elem.find('ItemTitle')
        sentence = parent_elem.find('ItemSentence/Sentence')
    elif config.parent_tag == 'Subitem1':
        title = parent_elem.find('Subitem1Title')
        sentence = parent_elem.find('Subitem1Sentence/Sentence')
    else:
        return False

    # Titleが空かチェック
    title_text = "".join(title.itertext()).strip() if title is not None else ""
    title_empty = not title_text

    # Sentenceが空かチェック
    sentence_text = "".join(sentence.itertext()).strip() if sentence is not None else ""
    sentence_empty = not sentence_text

    return title_empty and sentence_empty


def get_list_columns(list_elem) -> Tuple[Optional[etree.Element], Optional[etree.Element], int]:
    """
    List要素からColumnのSentence要素を取得
    返り値: (1つ目のColumnのSentence要素, 2つ目のColumnのSentence要素, Column数)
    """
    columns = list_elem.findall('.//Column')
    col1_sentence = None
    col2_sentence = None
    if len(columns) >= 1:
        col1_sentence = columns[0].find('.//Sentence')
    if len(columns) >= 2:
        col2_sentence = columns[1].find('.//Sentence')
    return col1_sentence, col2_sentence, len(columns)


def get_list_text(list_elem) -> Optional[str]:
    """ColumnなしList要素からテキストを取得"""
    columns = list_elem.findall('.//Column')
    if len(columns) > 0:
        return None
    sentence = list_elem.find('.//Sentence')
    if sentence is not None:
        return "".join(sentence.itertext()).strip()
    return None


def is_list_element(element) -> bool:
    """要素がList要素かチェック"""
    return element.tag == 'List'


def create_empty_element(config: ConversionConfig) -> etree.Element:
    """空の子要素を作成"""
    element = etree.Element(config.child_tag)
    etree.SubElement(element, config.title_tag)
    sentence_elem = etree.SubElement(element, config.sentence_tag)
    sentence = etree.SubElement(sentence_elem, 'Sentence', Num='1')
    sentence.text = ''
    return element


def create_element_with_title_and_sentence(title_sentence_elem: Optional[etree.Element],
                                         content_sentence_elem: Optional[etree.Element],
                                         config: ConversionConfig) -> etree.Element:
    """タイトルとセンテンスを持つ子要素を作成"""
    element = etree.Element(config.child_tag)
    title_elem = etree.SubElement(element, config.title_tag)
    if title_sentence_elem is not None:
        title_elem.text = title_sentence_elem.text
        for child in title_sentence_elem:
            title_elem.append(deepcopy(child))
    sentence_elem = etree.SubElement(element, config.sentence_tag)
    if content_sentence_elem is not None:
        sentence_elem.append(deepcopy(content_sentence_elem))
    else:
        etree.SubElement(sentence_elem, 'Sentence', Num='1')
    return element


def create_element_from_list(element, config: ConversionConfig, stats) -> Tuple[Optional[etree.Element], str]:
    """
    指定された要素を子要素化する
    返り値: (作成された子要素, コメントテキスト)
    """
    child_elem = None
    comment_text = ""

    if element.tag == 'List':
        col1_sentence, col2_sentence, col_count = get_list_columns(element)
        col1_text = "".join(col1_sentence.itertext()).strip() if col1_sentence is not None else ""

        # Columnが3つ以上の場合、そのまま取り込む（TableStructやColumnなしListと同様）
        if col_count > 2:
            child_elem = create_empty_element(config)
            sentence_elem = child_elem.find(config.sentence_tag)
            if sentence_elem is not None:
                sentence_index = child_elem.index(sentence_elem)
                child_elem.insert(sentence_index + 1, deepcopy(element))
            else:
                child_elem.append(deepcopy(element))
            comment_text = f"*** {config.script_name}: [処理1-分岐1-1] Column3つ以上 List -> {config.child_tag}内List ***"
            stats[f'CONVERTED_MULTI_COLUMN_LIST_TO_{config.child_tag.upper()}'] = stats.get(f'CONVERTED_MULTI_COLUMN_LIST_TO_{config.child_tag.upper()}', 0) + 1
        # Column条件はconfigによる（Columnが2つ以下の場合のみ）
        elif col_count >= config.column_condition_min and col1_text and (is_label(col1_text) or is_kanji_number_label(col1_text)):
            child_elem = create_element_with_title_and_sentence(col1_sentence, col2_sentence, config)
            if is_kanji_number_label(col1_text):
                comment_text = f"*** {config.script_name}: [処理1-分岐1] 漢数字ラベル Columnあり List -> {config.child_tag} ***"
                stats[f'CONVERTED_KANJI_LABELED_LIST_TO_{config.child_tag.upper()}'] += 1
            else:
                comment_text = f"*** {config.script_name}: [処理1-分岐1] Columnあり List -> {config.child_tag} ***"
                stats[f'CONVERTED_LABELED_LIST_TO_{config.child_tag.upper()}'] += 1
        else:
            list_text = get_list_text(element)

            # 学年パターン（subitem1基準のロジック）
            if 'grade' in config.supported_types and list_text and is_subject_name_bracket(list_text) and is_grade_pattern(list_text):
                child_elem = create_empty_element(config)
                child_elem.find(f'{config.sentence_tag}/Sentence').text = list_text
                comment_text = f"*** {config.script_name}: [処理1-分岐2-1] 学年 List -> {config.child_tag} ***"
                stats[f'CONVERTED_GRADE_LIST_TO_{config.child_tag.upper()}'] += 1
            elif 'grade_double' in config.supported_types and list_text and is_grade_double_bracket(list_text):
                child_elem = create_empty_element(config)
                child_elem.find(f'{config.sentence_tag}/Sentence').text = list_text
                comment_text = f"*** {config.script_name}: [処理1-分岐2-1-1] 学年（2つ記載） List -> {config.child_tag} ***"
                stats[f'CONVERTED_GRADE_DOUBLE_LIST_TO_{config.child_tag.upper()}'] += 1
            elif 'grade_single' in config.supported_types and list_text and is_grade_single_bracket(list_text):
                child_elem = create_empty_element(config)
                child_elem.find(f'{config.sentence_tag}/Sentence').text = list_text
                comment_text = f"*** {config.script_name}: [処理1-分岐2-1-2] 学年（1つ記載） List -> {config.child_tag} ***"
                stats[f'CONVERTED_GRADE_SINGLE_LIST_TO_{config.child_tag.upper()}'] += 1
            elif list_text and is_subject_name_bracket(list_text):
                child_elem = create_empty_element(config)
                child_elem.find(f'{config.sentence_tag}/Sentence').text = list_text
                comment_text = f"*** {config.script_name}: [処理1-分岐2-2] 括弧付き科目名 List -> {config.child_tag} ***"
                stats[f'CONVERTED_SUBJECT_NAME_LIST_TO_{config.child_tag.upper()}'] += 1
            elif list_text and is_instruction_bracket(list_text):
                child_elem = create_empty_element(config)
                child_elem.find(f'{config.sentence_tag}/Sentence').text = list_text
                comment_text = f"*** {config.script_name}: [処理1-分岐2-3] 括弧付き指導項目 List -> {config.child_tag} ***"
                stats[f'CONVERTED_INSTRUCTION_LIST_TO_{config.child_tag.upper()}'] += 1
            elif list_text:
                child_elem = create_empty_element(config)
                sentence_elem = child_elem.find(config.sentence_tag)
                if sentence_elem is not None:
                    sentence_index = child_elem.index(sentence_elem)
                    child_elem.insert(sentence_index + 1, deepcopy(element))
                else:
                    child_elem.append(deepcopy(element))
                comment_text = f"*** {config.script_name}: [処理1-分岐2-4] ColumnなしList -> {config.child_tag}内List ***"
                stats[f'CONVERTED_NO_COLUMN_LIST_TO_{config.child_tag.upper()}'] += 1
            else:
                child_elem = create_empty_element(config)
                sentence_elem = child_elem.find(config.sentence_tag)
                if sentence_elem is not None:
                    sentence_index = child_elem.index(sentence_elem)
                    child_elem.insert(sentence_index + 1, deepcopy(element))
                else:
                    child_elem.append(deepcopy(element))
                comment_text = f"*** {config.script_name}: [処理1-分岐2-4] ColumnなしList -> {config.child_tag}内List (Fallback) ***"
                stats[f'CONVERTED_NO_COLUMN_LIST_TO_{config.child_tag.upper()}'] += 1

    elif element.tag in ['TableStruct', 'FigStruct', 'StyleStruct']:
        child_elem = create_empty_element(config)
        sentence_elem = child_elem.find(config.sentence_tag)
        if sentence_elem is not None:
            sentence_index = child_elem.index(sentence_elem)
            child_elem.insert(sentence_index + 1, deepcopy(element))
        else:
            child_elem.append(deepcopy(element))
        comment_text = f"*** {config.script_name}: [処理1-分岐3] {element.tag} -> {config.child_tag}内要素 ***"
        stats[f'CONVERTED_NON_LIST_TO_{config.child_tag.upper()}'] += 1

    return child_elem, comment_text


def get_element_type(element, config: ConversionConfig):
    """
    子要素のタイプを判定
    """
    if element is None:
        return 'other'

    title = element.find(config.title_tag)
    title_text = "".join(title.itertext()).strip() if title is not None else ""

    sentence = element.find(f'{config.sentence_tag}/Sentence')
    sentence_text = "".join(sentence.itertext()).strip() if sentence is not None else ""

    if title_text and is_label(title_text):
        return 'labeled'

    # gradeパターンの判定を先に（subject_nameよりも）
    if 'grade' in config.supported_types and is_subject_name_bracket(sentence_text) and is_grade_pattern(sentence_text):
        return 'grade'
    if 'grade_double' in config.supported_types and is_grade_double_bracket(sentence_text):
        return 'grade_double'
    if 'grade_single' in config.supported_types and is_grade_single_bracket(sentence_text):
        return 'grade_single'

    if is_subject_name_bracket(sentence_text):
        return 'subject_name'
    if is_instruction_bracket(sentence_text):
        return 'instruction'
    return 'other'


def get_list_type(list_elem, config: ConversionConfig):
    """List要素のタイプを判定"""
    col1_sentence, _, col_count = get_list_columns(list_elem)
    col1_text = "".join(col1_sentence.itertext()).strip() if col1_sentence is not None else ""
    list_text = get_list_text(list_elem)

    if col_count >= config.column_condition_min and col1_text and is_label(col1_text):
        return 'labeled'

    # gradeパターンの判定を先に
    if 'grade' in config.supported_types and list_text and is_subject_name_bracket(list_text) and is_grade_pattern(list_text):
        return 'grade'
    if 'grade_double' in config.supported_types and list_text and is_grade_double_bracket(list_text):
        return 'grade_double'
    if 'grade_single' in config.supported_types and list_text and is_grade_single_bracket(list_text):
        return 'grade_single'

    if list_text and is_subject_name_bracket(list_text):
        return 'subject_name'
    if list_text and is_instruction_bracket(list_text):
        return 'instruction'
    return 'no_column_text'


def are_same_hierarchy(current_elem, list_elem, config: ConversionConfig) -> bool:
    """
    階層判定（subitem1のロジックを基準）
    """
    if current_elem is None:
        return False

    current_type = get_element_type(current_elem, config)
    list_type = get_list_type(list_elem, config)

    # ColumnありListの場合はcol1_textを使用
    col1_sentence, _, col_count = get_list_columns(list_elem)
    if col_count >= config.column_condition_min:
        list_title_text = "".join(col1_sentence.itertext()).strip() if col1_sentence is not None else ""
    else:
        list_title_text = get_list_text(list_elem) or ""

    # 学年パターン同士は学年数が同じ場合に分割
    if ((current_type in ['grade', 'grade_single', 'grade_double'] and list_type in ['grade', 'grade_single', 'grade_double'])
        and ('grade' in config.supported_types or ('grade_single' in config.supported_types and 'grade_double' in config.supported_types))):

        current_sentence = current_elem.find(f'{config.sentence_tag}/Sentence')
        current_grade_count = count_grades("".join(current_sentence.itertext()).strip()) if current_sentence is not None else 0
        list_grade_count = count_grades(get_list_text(list_elem) or "")

        if current_grade_count == list_grade_count:
            return True
        else:
            return False

    if current_type == 'other' and list_type in [t for t in config.supported_types if t != 'grade']:
        return True

    if current_type == 'labeled' and list_type == 'labeled':
        current_title_text = "".join(current_elem.find(config.title_tag).itertext()).strip()
        current_label_id = detect_label_id(current_title_text)
        list_label_id = detect_label_id(list_title_text)

        # ラベルIDが取得できない場合は異なる階層
        if current_label_id is None or list_label_id is None:
            return False

        # ラベルIDが異なる場合は異なる階層
        if current_label_id != list_label_id:
            return False

        # ラベルIDが同じ場合でも、数字パターンの場合は全角/半角/漢数字、括弧の種類を区別
        if current_label_id in ['number', 'paren_number', 'double_paren_number']:
            current_number_type = get_number_type(current_title_text)
            list_number_type = get_number_type(list_title_text)
            # 数字の種類が異なる場合は異なる階層
            if current_number_type != list_number_type:
                return False
            # 数字の種類が同じ場合は同じ階層
            return True

        # アルファベットパターンの場合は大文字/小文字、全角/半角、括弧の種類を区別
        if current_label_id in ['alphabet', 'paren_alphabet', 'double_paren_alphabet']:
            current_alphabet_type = get_alphabet_type(current_title_text)
            list_alphabet_type = get_alphabet_type(list_title_text)
            # アルファベットの種類が異なる場合は異なる階層
            if current_alphabet_type != list_alphabet_type:
                return False
            # アルファベットの種類が同じ場合は同じ階層
            return True

        # ラベルIDが同じで、上記以外の場合は同じ階層
        return True

    if current_type == 'subject_name' and list_type == 'subject_name':
        return True  # 分割（科目名同士は分割）

    if current_type == 'grade' and list_type == 'grade':
        return True

    if current_type == 'instruction' and list_type == 'instruction':
        return True

    # convert_item_step0.pyのロジックに合わせるための追加ルール
    # subject_name, grade, instructionタイプのItemの後には、
    # labeled, grade, instruction, no_column_textタイプのListが取り込まれる
    if current_type in ['subject_name', 'grade', 'instruction'] and list_type in ['labeled', 'instruction', 'grade', 'no_column_text']:
        return False  # 取り込み

    return False


def process_elements_recursive(parent_elem, config: ConversionConfig, stats) -> bool:
    """
    親要素内のList要素を再帰的に子要素に変換
    """
    parent_sentence = parent_elem.find(f'{config.parent_tag}Sentence')
    if parent_sentence is None:
        return False

    siblings = list(parent_sentence.itersiblings())
    if not siblings:
        return False

    # 処理モードの定義
    LOOKING_FOR_FIRST_CHILD = 0
    NORMAL_PROCESSING = 1

    current_mode = LOOKING_FOR_FIRST_CHILD
    last_child = None
    made_changes = False

    # 親要素のSentenceの次の要素から処理を開始
    children_to_process = list(siblings)
    new_children = []

    for child in children_to_process:
        if current_mode == LOOKING_FOR_FIRST_CHILD:
            if is_list_element(child):
                # 親要素が空の場合は常にList要素をそのまま追加（スキップ）
                if config.skip_empty_parent and is_parent_empty(parent_elem, config):
                    new_children.append(child)
                    stats[f'SKIPPED_DUE_TO_EMPTY_PARENT'] += 1
                    current_mode = NORMAL_PROCESSING
                    continue

                col1_sentence, _, col_count = get_list_columns(child)
                col1_text = "".join(col1_sentence.itertext()).strip() if col1_sentence is not None else ""
                list_text = get_list_text(child)


                if col_count == 0:  # ColumnなしList
                    # LOOKING_FOR_FIRST_CHILDモードでもColumnなしListを常に処理
                    new_child, comment = create_element_from_list(child, config, stats)
                    if new_child is not None:
                        last_child = new_child
                        new_children.append(last_child)
                        made_changes = True
                    else:
                        new_children.append(child)
                    current_mode = NORMAL_PROCESSING
                else:  # ColumnありList
                    new_child, comment = create_element_from_list(child, config, stats)
                    if new_child is not None:
                        last_child = new_child
                        new_children.append(last_child)
                        made_changes = True
                    else:
                        new_children.append(child)
                    current_mode = NORMAL_PROCESSING

            elif child.tag in ['TableStruct', 'FigStruct', 'StyleStruct']:
                current_mode = NORMAL_PROCESSING
                new_child = create_empty_element(config)
                new_child.append(child)
                last_child = new_child
                new_children.append(last_child)
                made_changes = True
                current_mode = NORMAL_PROCESSING

            elif hasattr(child, 'tag') and isinstance(child.tag, str) and config.child_tag in child.tag:  # 既存の子要素
                last_child = child
                new_children.append(child)
                current_mode = NORMAL_PROCESSING
            else:
                new_children.append(child)
                current_mode = NORMAL_PROCESSING

        elif current_mode == NORMAL_PROCESSING:
            if is_list_element(child):
                col1_sentence, _, col_count = get_list_columns(child)

                # 親要素が空の場合は常にList要素をそのまま追加（スキップ）
                if config.skip_empty_parent and is_parent_empty(parent_elem, config):
                    new_children.append(child)
                    stats[f'SKIPPED_DUE_TO_EMPTY_PARENT'] += 1
                    continue

                # ColumnなしListはスキップ（convert_subitem1_step0.py, convert_subitem2_step0.py用）
                # if col_count == 0:
                #     new_children.append(child)
                #     continue

                if last_child is None:
                    # 最初の要素の場合はcreate_element_from_listを使用
                    new_child, comment = create_element_from_list(child, config, stats)
                    if new_child is not None:
                        last_child = new_child
                        new_children.append(last_child)
                        made_changes = True
                    else:
                        new_child = create_empty_element(config)
                        new_child.append(child)
                        last_child = new_child
                        new_children.append(last_child)
                        made_changes = True
                elif are_same_hierarchy(last_child, child, config):
                    new_child, comment = create_element_from_list(child, config, stats)
                    if new_child is not None:
                        last_child = new_child
                        new_children.append(last_child)
                        made_changes = True
                    else:
                        new_children.append(child)
                else:
                    if last_child is not None:
                        last_child.append(child)
                        made_changes = True
                    else:
                        new_children.append(child)

            elif child.tag in ['TableStruct', 'FigStruct', 'StyleStruct']:
                if last_child is not None:
                    last_child.append(child)
                    made_changes = True
                else:
                    new_children.append(child)

            elif hasattr(child, 'tag') and isinstance(child.tag, str) and config.child_tag in child.tag:  # 既存の子要素
                last_child = child
                new_children.append(child)
            else:
                new_children.append(child)

    # 元の親要素の子要素をクリアし、新しい子要素を追加
    original_attrs = dict(parent_elem.attrib)

    # Paragraphの場合、ParagraphNumを保持する
    if config.parent_tag == 'Paragraph':
        parent_title_elem_copy = deepcopy(parent_elem.find('ParagraphNum')) if parent_elem.find('ParagraphNum') is not None else None
    else:
        parent_title_elem_copy = deepcopy(parent_elem.find(config.parent_tag + 'Title')) if parent_elem.find(config.parent_tag + 'Title') is not None else None

    parent_elem.clear()
    parent_elem.attrib.update(original_attrs)

    if parent_title_elem_copy is not None:
        parent_elem.append(parent_title_elem_copy)

    if parent_sentence is not None:
        parent_elem.append(parent_sentence)

    for new_child in new_children:
        parent_elem.append(new_child)

    return made_changes


def renumber_elements(tree, config: ConversionConfig):
    """子要素のNum属性を再採番"""
    root = tree.getroot()
    for parent in root.xpath(f'.//{config.parent_tag}'):
        children = parent.findall(config.child_tag)
        for i, child in enumerate(children):
            child.set('Num', str(i + 1))


def process_xml_file(input_path: Path, output_path: Path, config: ConversionConfig) -> int:
    """XMLファイルを処理"""
    print("=" * 80)
    print(f"【{config.child_tag}要素変換ロジック実装】")
    print("=" * 80)
    print(f"入力ファイル: {input_path}")

    try:
        tree = etree.parse(str(input_path))
    except Exception as e:
        print(f"エラー: XMLファイルの読み込みに失敗しました: {e}", file=sys.stderr)
        return 1

    stats = {}
    # 統計キーを動的に生成
    stat_keys = [
        f'CONVERTED_LABELED_LIST_TO_{config.child_tag.upper()}',
        f'CONVERTED_KANJI_LABELED_LIST_TO_{config.child_tag.upper()}',
        f'CONVERTED_MULTI_COLUMN_LIST_TO_{config.child_tag.upper()}',
        f'CONVERTED_NO_COLUMN_LIST_TO_{config.child_tag.upper()}',
        f'CONVERTED_SUBJECT_NAME_LIST_TO_{config.child_tag.upper()}',
        f'CONVERTED_INSTRUCTION_LIST_TO_{config.child_tag.upper()}',
        f'CONVERTED_NON_LIST_TO_{config.child_tag.upper()}',
        f'SKIPPED_DUE_TO_EMPTY_PARENT'
    ]

    if 'grade' in config.supported_types:
        stat_keys.append(f'CONVERTED_GRADE_LIST_TO_{config.child_tag.upper()}')
    if 'grade_single' in config.supported_types:
        stat_keys.extend([
            f'CONVERTED_GRADE_SINGLE_LIST_TO_{config.child_tag.upper()}',
            f'CONVERTED_GRADE_DOUBLE_LIST_TO_{config.child_tag.upper()}'
        ])

    for key in stat_keys:
        stats[key] = 0

    root = tree.getroot()
    parent_elements = root.xpath(f'.//{config.parent_tag}')

    for parent_elem in parent_elements:
        process_elements_recursive(parent_elem, config, stats)

    renumber_elements(tree, config)

    print("\n変換統計:")
    for key, value in stats.items():
        if value > 0:
            # 統計キーから説明を生成
            if 'KANJI_LABELED' in key:
                desc = "漢数字ラベルColumnありList"
            elif 'MULTI_COLUMN' in key:
                desc = "Column3つ以上List"
            elif 'LABELED' in key and 'KANJI' not in key:
                desc = "ColumnありList"
            elif 'GRADE_DOUBLE' in key:
                desc = "学年（2つ記載）"
            elif 'GRADE_SINGLE' in key:
                desc = "学年（1つ記載）"
            elif 'GRADE' in key and 'DOUBLE' not in key and 'SINGLE' not in key:
                desc = "学年"
            elif 'SUBJECT_NAME' in key:
                desc = "括弧付き科目名"
            elif 'INSTRUCTION' in key:
                desc = "括弧付き指導項目"
            elif 'NO_COLUMN' in key:
                desc = "ColumnなしList"
            elif 'NON_LIST' in key:
                desc = "非List要素"
            elif 'SKIPPED' in key:
                desc = "スキップ（親が空のため）"
            else:
                desc = key
            print(f" - {desc}: {value}箇所")

    format_xml_lxml(tree, str(output_path))

    print(f"\n出力ファイル: {output_path}")
    print(" ✅ インデント・再採番済み")
    print("=" * 80)

    return 0


# ============================================================================
# step1スクリプト用共通関数
# ============================================================================

def is_subject_name_bracket_only(sentence_elem: etree.Element) -> bool:
    """
    判定：Sentenceが「科目名括弧のみ」パターンかどうか

    科目名括弧: 〔医療と社会〕、〔人体の構造と機能〕 など
    指導項目括弧: 〔指導項目〕、〔指導項目〕の（１）... など

    例：
      ✓ 〔医療と社会〕
      ✓ 〔人体の構造と機能〕
      ✗ 〔指導項目〕
      ✗ 〔指導項目〕の（１）...
    """
    if sentence_elem is None or sentence_elem.tag != 'Sentence':
        return False

    text = sentence_elem.text.strip() if sentence_elem.text else ""

    # 最小条件：〔で始まり〕で終わる
    if not (text.startswith('〔') and text.endswith('〕')):
        return False

    # 〔...〕の中身を抽出
    bracketed = text[1:-1]

    # 指導項目括弧パターンを除外
    if bracketed == '指導項目':
        return False

    if '指導項目' in bracketed and 'の' in bracketed:
        return False

    # 科目名括弧と判定
    return True


def is_container_element(elem: etree.Element, config: ConversionConfig) -> bool:
    """
    コンテナ要素かどうかを判定（共通化版）

    コンテナ要素：
    - Titleが存在するがテキストが空
    - Sentenceが存在する
    - Itemの場合は、Sentence内のテキストが空であることを確認
    """
    if elem is None or elem.tag != config.child_tag:
        return False

    title_elem = elem.find(f'.//{config.title_tag}')
    if title_elem is None or title_elem.text:
        return False

    sentence_elem = elem.find(f'.//{config.sentence_tag}')
    if sentence_elem is None:
        return False

    # Itemの場合は、Sentence内のSentence要素のテキストが空であることを確認
    if config.child_tag == 'Item':
        sentences = sentence_elem.findall('.//Sentence')
        if not sentences or any(sentence.text for sentence in sentences):
            return False

    return True


def get_first_child_after_parent_sentence(parent_elem: etree.Element, config: ConversionConfig) -> Optional[etree.Element]:
    """
    親要素のSentenceの直後の最初の子要素を取得（共通化版）

    仕様書の要件：
    - 親要素内の、親Sentenceのすぐ次の弟要素の子要素である
    - 最初の子要素のみを対象とする
    - コンテナ要素である必要がある
    """
    children = list(parent_elem)

    # 親Sentenceを探す
    parent_sentence_tag = f'{config.parent_tag}Sentence'
    parent_sentence_index = -1
    for i, child in enumerate(children):
        if child.tag == parent_sentence_tag:
            parent_sentence_index = i
            break

    if parent_sentence_index == -1:
        return None

    # 親Sentenceの次の弟要素を確認
    for i in range(parent_sentence_index + 1, len(children)):
        child = children[i]
        if child.tag == config.child_tag:
            # コンテナ要素かどうか確認
            if is_container_element(child, config):
                return child
            else:
                # 子要素が見つかったがコンテナ要素でない場合は処理しない
                return None

    return None


def split_element_at_point(elem: etree.Element, split_index: int, config: ConversionConfig) -> Tuple[etree.Element, etree.Element]:
    """
    要素を指定された位置で2つに分割（共通化版）

    仕様書の要件：
    - 分割は1回のみ
    - 元の要素と新しい要素の2つを生成

    Args:
        elem: 分割する要素
        split_index: 分割位置（この位置以降が新しい要素に移動）
        config: 変換設定

    Returns:
        (元の要素, 新しい要素)
    """
    children = list(elem)
    before_split = children[:split_index]
    after_split = children[split_index:]

    # 元の要素を再構築
    original_elem = etree.Element(config.child_tag)
    # 属性をコピー
    for key, value in elem.attrib.items():
        original_elem.set(key, value)

    # before_splitの要素を追加
    for child_elem in before_split:
        original_elem.append(deepcopy(child_elem))

    # 新しい要素を作成
    new_elem = create_empty_element(config)

    # after_splitの要素を追加
    for child_elem in after_split:
        new_elem.append(deepcopy(child_elem))

    return original_elem, new_elem


def find_split_point_common(elem: etree.Element, config: ConversionConfig, column_target: int = 0, skip_bracket_check: bool = False, subject_bracket_only: bool = False) -> Optional[Tuple[int, str]]:
    """
    共通の分割ポイント検出関数

    Args:
        elem: 処理対象要素（Item, Subitem1, Subitem2）
        config: 変換設定
        column_target: 対象とするcolumn_count（0:列なし, 1:1列のみ, etc）
        skip_bracket_check: 括弧チェックをスキップするかどうか
        subject_bracket_only: 科目名括弧のみを対象とするかどうか

    Returns:
        (index, split_type) または None
    """
    children = list(elem)

    if subject_bracket_only:
        # 科目名括弧・学年括弧を対象とする場合（subitem1_step1）
        for i, child in enumerate(children):
            if child.tag != 'List':
                continue

            # ColumnありListはスキップ（既に処理済み）
            col1_sentence, col2_sentence, column_count = get_list_columns(child)
            if column_count > 0:
                continue

            # 科目名括弧・学年括弧をチェック
            list_sentence = child.find('.//ListSentence')
            if list_sentence is not None:
                sentences = list_sentence.findall('.//Sentence')
                if sentences:
                    first_sentence = sentences[0]
                    if (is_subject_name_bracket_only(first_sentence) or
                        is_grade_single_bracket(first_sentence.text if first_sentence.text else "") or
                        is_grade_double_bracket(first_sentence.text if first_sentence.text else "")):
                        return (i + 1, 'bracket')  # 括弧の下で分割

    elif column_target == 0:
        # ColumnなしListを対象とする場合（subitem2_step1）
        for i, child in enumerate(children):
            if child.tag != 'List':
                continue

            # ColumnありListはスキップ
            col1_sentence, col2_sentence, column_count = get_list_columns(child)
            if column_count > 0:
                continue

            # ColumnなしListの場合、スキップ対象でないかをチェック
            if not skip_bracket_check:
                list_sentence = child.find('.//ListSentence')
                if list_sentence is not None:
                    sentences = list_sentence.findall('.//Sentence')
                    if sentences:
                        first_sentence = sentences[0]
                        if is_subject_name_bracket_only(first_sentence):
                            continue  # 科目名括弧はスキップ

            # Columnなしでかつスキップ対象でない場合、分割対象
            return (i, 'no_column_list')

    elif column_target == 1:
        # Column1つListを対象とする場合（item_step1）
        for i, child in enumerate(children):
            if child.tag != 'List':
                continue

            col1_sentence, col2_sentence, column_count = get_list_columns(child)
            if column_count == 1:
                return (i, 'column_list')

            # 科目名括弧はスキップ
            if not skip_bracket_check:
                list_sentence = child.find('.//ListSentence')
                if list_sentence is not None:
                    sentences = list_sentence.findall('.//Sentence')
                    if sentences:
                        first_sentence = sentences[0]
                        if is_subject_name_bracket_only(first_sentence):
                            continue

    return None


def process_parent_with_order_preservation(parent_elem: etree.Element, stats: dict, script_name: str, config: ConversionConfig, find_split_func) -> bool:
    """
    親要素を順序を保持しながら処理（共通化版）

    仕様書の要件：
    1. 親Sentenceの直後の最初の子要素のみを対象
    2. 分割は1回のみ
    3. 元の順序を完全に保持

    処理フロー：
    1. 親Sentenceの直後の最初のコンテナ子要素を取得
    2. 子要素内で最初の分割ポイントを検出
    3. 分割ポイントが見つかった場合、子要素を2つに分割
    4. 親要素全体を順序を保持して再構築

    Args:
        parent_elem: 親要素（Paragraph, Item, Subitem1）
        stats: 統計情報
        script_name: スクリプト名
        config: 変換設定
        find_split_func: 分割ポイント検出関数（要素を受け取り、Optional[Tuple[int, str]]を返す）

    Returns:
        処理が実行された場合True、そうでない場合False
    """
    # 処理対象の子要素を取得
    target_child = get_first_child_after_parent_sentence(parent_elem, config)

    if target_child is None:
        return False

    # 最初の分割ポイントを検出
    split_result = find_split_func(target_child)

    if split_result is None:
        return False

    split_index, split_type = split_result

    # 子要素を分割
    original_child, new_child = split_element_at_point(target_child, split_index, config)

    print(f"  - Split {config.child_tag} Num='{target_child.get('Num', '')}' at index {split_index} (type: {split_type})")

    # 親要素全体を順序を保持して再構築
    children = list(parent_elem)
    new_children = []

    for child in children:
        if child is target_child:
            # 元の子要素を分割後の2つの子要素に置き換え
            if original_child is not None:
                new_children.append(original_child)
            if new_child is not None:
                new_children.append(new_child)
        else:
            # その他の要素はそのまま保持
            new_children.append(child)

    # 親要素を再構築
    attrib = dict(parent_elem.attrib)
    parent_elem.clear()

    for key, value in attrib.items():
        parent_elem.set(key, value)

    for child in new_children:
        parent_elem.append(child)

    return True
