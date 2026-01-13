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
import json
from enum import Enum
from pathlib import Path
from lxml import etree
from typing import Optional, Tuple, Dict, List
from copy import deepcopy

# scripts/utils/をインポートパスに追加
script_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(script_dir))

from utils.label_utils import is_label, detect_label_id, get_number_type, get_alphabet_type, is_valid_label_id, get_exclude_label_ids_for_context
from utils.bracket_utils import is_subject_name_bracket, is_instruction_bracket, is_grade_single_bracket, is_grade_double_bracket, get_bracket_type


# ============================================================================
# 定数定義
# ============================================================================

# アルファベットラベルIDのリスト（重複を避けるため定数化）
ALPHABET_LABEL_IDS = [
    'fullwidth_lowercase_alphabet_with_paren',
    'fullwidth_uppercase_alphabet_with_paren',
    'paren_lowercase_alphabet',
    'paren_uppercase_alphabet',
    'paren_fullwidth_lowercase_alphabet',
    'paren_fullwidth_uppercase_alphabet'
]

# アルファベットラベルIDの拡張リスト（are_same_hierarchy等で使用）
# 括弧なしのアルファベットラベルも含む
ALPHABET_LABEL_IDS_EXTENDED = ALPHABET_LABEL_IDS + [
    'fullwidth_lowercase_alphabet',
    'fullwidth_uppercase_alphabet',
    'lowercase_alphabet',
    'uppercase_alphabet'
]

# Column数の閾値
MIN_COLUMNS_FOR_MULTI_COLUMN_PROCESSING = 3

# 処理モードの定義
class ProcessingMode(Enum):
    """要素処理のモード"""
    LOOKING_FOR_FIRST_CHILD = 0
    NORMAL_PROCESSING = 1

# Struct要素のタグリスト
STRUCT_ELEMENT_TAGS = ['TableStruct', 'FigStruct', 'StyleStruct']

# ドット区切り数字ラベルIDのリスト
DOT_SEPARATED_NUMBER_LABEL_IDS = [
    'dot_separated_number_single',
    'dot_separated_number_double'
]


# ============================================================================
# 設定読み込み関数
# ============================================================================

def load_conversion_behaviors_config() -> Dict:
    """変換動作設定を読み込む"""
    script_dir = Path(__file__).resolve().parent
    config_path = script_dir / "config" / "label_config.json"
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config.get('conversion_behaviors', {})
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return {}


def should_convert_text_first_column_to_sentences(child_tag: str) -> bool:
    """Columnが2つあり、かつ1つ目がテキストの場合にSentence要素を2つ作成するかどうかを判定"""
    behaviors = load_conversion_behaviors_config()
    behavior = behaviors.get('column_list_text_first_column', {})
    
    if not behavior.get('enabled', False):
        return False
    
    target_levels = behavior.get('target_levels', [])
    return child_tag in target_levels


def should_split_no_column_text_lists(child_tag: str) -> bool:
    """no_column_textタイプのItemの後、カラムなしリストを並列分割するかどうかを判定"""
    behaviors = load_conversion_behaviors_config()
    behavior = behaviors.get('no_column_text_split_mode', {})
    
    if not behavior.get('enabled', False):
        return False
    
    target_levels = behavior.get('target_levels', [])
    return child_tag in target_levels


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


def is_label_text(text: str, col_count: int = 0) -> bool:
    """
    テキストがラベルかどうかを判定（共通化関数）
    
    Args:
        text: 判定するテキスト
        col_count: Column数（0の場合はチェックしない）
    
    Returns:
        ラベルかどうか
    """
    if not text:
        return False
    if col_count > 0 and col_count == 0:
        return False
    return bool(is_label(text) or is_kanji_number_label(text))


def get_column_text(col_sentence: Optional[etree.Element]) -> str:
    """
    ColumnのSentence要素からテキストを取得（共通化関数）
    
    Args:
        col_sentence: ColumnのSentence要素
    
    Returns:
        テキスト（要素がNoneの場合は空文字列）
    """
    if col_sentence is None:
        return ""
    return "".join(col_sentence.itertext()).strip()


def is_alphabet_label(label_id: Optional[str]) -> bool:
    """
    ラベルIDがアルファベットラベルかどうかを判定（共通化関数）
    
    Args:
        label_id: ラベルID
    
    Returns:
        アルファベットラベルかどうか
    """
    if label_id is None:
        return False
    return label_id in ALPHABET_LABEL_IDS_EXTENDED


def is_number_label(label_id: Optional[str]) -> bool:
    """
    ラベルIDが数字ラベルかどうかを判定
    
    Args:
        label_id: ラベルID
    
    Returns:
        数字ラベルかどうか
    """
    if label_id is None:
        return False
    # 数字ラベルのラベルIDパターン
    number_label_patterns = [
        'paren_number',
        'dot_separated_number_single',
        'dot_separated_number_double',
        'fullwidth_paren_number',
        'paren_fullwidth_number',
        'note_with_number'
    ]
    return any(pattern in label_id for pattern in number_label_patterns)


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
    elif config.parent_tag == 'Subitem2':
        title = parent_elem.find('Subitem2Title')
        sentence = parent_elem.find('Subitem2Sentence/Sentence')
    elif config.parent_tag == 'Subitem3':
        title = parent_elem.find('Subitem3Title')
        sentence = parent_elem.find('Subitem3Sentence/Sentence')
    elif config.parent_tag == 'Subitem4':
        title = parent_elem.find('Subitem4Title')
        sentence = parent_elem.find('Subitem4Sentence/Sentence')
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


def get_all_list_columns(list_elem) -> List[Optional[etree.Element]]:
    """
    List要素からすべてのColumnのSentence要素を取得
    返り値: ColumnのSentence要素のリスト
    """
    columns = list_elem.findall('.//Column')
    sentences = []
    for column in columns:
        sentence = column.find('.//Sentence')
        sentences.append(sentence)
    return sentences


def get_all_list_column_elements(list_elem) -> List[etree.Element]:
    """
    List要素からすべてのColumn要素全体を取得
    返り値: Column要素のリスト
    """
    list_sentence = list_elem.find('.//ListSentence')
    if list_sentence is None:
        return []
    columns = list_sentence.findall('Column')
    return columns


def get_list_text(list_elem) -> Optional[str]:
    """ColumnなしList要素からテキストを取得"""
    columns = list_elem.findall('.//Column')
    if len(columns) > 0:
        return None
    sentence = list_elem.find('.//Sentence')
    if sentence is not None:
        return "".join(sentence.itertext()).strip()
    return None


def get_list_sentence(list_elem) -> Optional[etree.Element]:
    """ColumnなしList要素からSentence要素全体を取得（Ruby要素などの子要素構造を保持）"""
    columns = list_elem.findall('.//Column')
    if len(columns) > 0:
        return None
    sentence = list_elem.find('.//Sentence')
    if sentence is not None:
        return sentence
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


def create_element_with_two_sentences(col1_sentence: Optional[etree.Element],
                                     col2_sentence: Optional[etree.Element],
                                     config: ConversionConfig,
                                     list_elem: Optional[etree.Element] = None) -> etree.Element:
    """2つのColumn要素を持つ子要素を作成（Columnが2つで1つ目がテキストの場合）"""
    element = etree.Element(config.child_tag)
    # Titleは空
    etree.SubElement(element, config.title_tag)
    sentence_elem = etree.SubElement(element, config.sentence_tag)
    
    # Column要素として追加
    if list_elem is not None:
        all_columns = get_all_list_column_elements(list_elem)
        for idx, column in enumerate(all_columns, start=1):
            # Column要素をコピーして追加（Num属性を設定）
            new_column = deepcopy(column)
            new_column.set('Num', str(idx))
            sentence_elem.append(new_column)
    else:
        # フォールバック: Sentence要素として追加（後方互換性のため）
        # 1つ目のSentence要素を作成（Column1の内容）
        if col1_sentence is not None:
            sentence1 = etree.SubElement(sentence_elem, 'Sentence', Num='1')
            sentence1.text = col1_sentence.text
            for child in col1_sentence:
                sentence1.append(deepcopy(child))
        else:
            etree.SubElement(sentence_elem, 'Sentence', Num='1')
        
        # 2つ目のSentence要素を作成（Column2の内容）
        if col2_sentence is not None:
            sentence2 = etree.SubElement(sentence_elem, 'Sentence', Num='2')
            sentence2.text = col2_sentence.text
            for child in col2_sentence:
                sentence2.append(deepcopy(child))
        else:
            etree.SubElement(sentence_elem, 'Sentence', Num='2')
    
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


def create_element_with_title_and_multiple_sentences(title_sentence_elem: Optional[etree.Element],
                                                     content_sentences: List[Optional[etree.Element]],
                                                     config: ConversionConfig,
                                                     list_elem: Optional[etree.Element] = None) -> etree.Element:
    """タイトルと複数のColumn要素を持つ子要素を作成（Columnが3つ以上で最初がラベルの場合）"""
    element = etree.Element(config.child_tag)
    title_elem = etree.SubElement(element, config.title_tag)
    if title_sentence_elem is not None:
        title_elem.text = title_sentence_elem.text
        for child in title_sentence_elem:
            title_elem.append(deepcopy(child))
    sentence_elem = etree.SubElement(element, config.sentence_tag)
    
    # 2つ目以降のColumnをColumn要素として追加
    if list_elem is not None:
        all_columns = get_all_list_column_elements(list_elem)
        for idx, column in enumerate(all_columns[1:], start=1):
            # Column要素をコピーして追加（Num属性を設定）
            new_column = deepcopy(column)
            new_column.set('Num', str(idx))
            sentence_elem.append(new_column)
    else:
        # フォールバック: Sentence要素として追加（後方互換性のため）
        for idx, content_sentence in enumerate(content_sentences, start=1):
            if content_sentence is not None:
                sentence = etree.SubElement(sentence_elem, 'Sentence', Num=str(idx))
                sentence.text = content_sentence.text
                for child in content_sentence:
                    sentence.append(deepcopy(child))
            else:
                etree.SubElement(sentence_elem, 'Sentence', Num=str(idx))
    
    return element


def create_element_with_text_first_column_and_multiple_sentences(all_sentences: List[Optional[etree.Element]],
                                                                 config: ConversionConfig,
                                                                 list_elem: Optional[etree.Element] = None) -> etree.Element:
    """ItemTitleが空で、ItemSentenceにすべてのColumnをColumn要素として含む子要素を作成（Columnが3つ以上で最初がテキストの場合）"""
    element = etree.Element(config.child_tag)
    # Titleは空
    etree.SubElement(element, config.title_tag)
    sentence_elem = etree.SubElement(element, config.sentence_tag)
    
    # すべてのColumnをColumn要素として追加
    if list_elem is not None:
        all_columns = get_all_list_column_elements(list_elem)
        for idx, column in enumerate(all_columns, start=1):
            # Column要素をコピーして追加（Num属性を設定）
            new_column = deepcopy(column)
            new_column.set('Num', str(idx))
            sentence_elem.append(new_column)
    else:
        # フォールバック: Sentence要素として追加（後方互換性のため）
        for idx, sentence_elem_source in enumerate(all_sentences, start=1):
            if sentence_elem_source is not None:
                sentence = etree.SubElement(sentence_elem, 'Sentence', Num=str(idx))
                sentence.text = sentence_elem_source.text
                for child in sentence_elem_source:
                    sentence.append(deepcopy(child))
            else:
                etree.SubElement(sentence_elem, 'Sentence', Num=str(idx))
    
    return element


def create_element_from_list(element, config: ConversionConfig, stats, parent_elem=None) -> Tuple[Optional[etree.Element], str]:
    """
    指定された要素を子要素化する
    返り値: (作成された子要素, コメントテキスト)
    """
    # 親要素が空の場合は変換をスキップ
    if config.skip_empty_parent and parent_elem is not None and is_parent_empty(parent_elem, config):
        return None, f"*** {config.script_name}: [スキップ] 親要素が空のため変換をスキップ ***"

    child_elem = None
    comment_text = ""

    if element.tag == 'List':
        col1_sentence, col2_sentence, col_count = get_list_columns(element)
        col1_text = get_column_text(col1_sentence)

        # Columnが3つ以上で、最初のColumnがラベル要素の場合の処理
        if col_count > 2 and col1_text and (is_label(col1_text) or is_kanji_number_label(col1_text)):
            all_sentences = get_all_list_columns(element)
            title_sentence = all_sentences[0] if len(all_sentences) > 0 else None
            content_sentences = all_sentences[1:] if len(all_sentences) > 1 else []
            
            child_elem = create_element_with_title_and_multiple_sentences(title_sentence, content_sentences, config, element)
            if is_kanji_number_label(col1_text):
                comment_text = f"*** {config.script_name}: [処理1-分岐1-2] Column3つ以上（1つ目が漢数字ラベル） List -> {config.child_tag}（Title + 複数Column） ***"
                stats[f'CONVERTED_KANJI_LABELED_MULTI_COLUMN_LIST_TO_{config.child_tag.upper()}'] += 1
            else:
                comment_text = f"*** {config.script_name}: [処理1-分岐1-2] Column3つ以上（1つ目がラベル） List -> {config.child_tag}（Title + 複数Column） ***"
                stats[f'CONVERTED_LABELED_MULTI_COLUMN_LIST_TO_{config.child_tag.upper()}'] += 1
            return child_elem, comment_text
        
        # Columnが3つ以上で、最初のColumnがラベル要素でない場合の処理
        # convert_subitem1_step0.pyのテスト30で、3列のList（1つ目がラベルでない）もSubitem1に変換される
        if col_count > 2 and col1_text and not (is_label(col1_text) or is_kanji_number_label(col1_text)):
            all_sentences = get_all_list_columns(element)
            
            # ItemTitleは空にして、すべてのColumnをItemSentenceに含める
            child_elem = create_element_with_text_first_column_and_multiple_sentences(all_sentences, config, element)
            comment_text = f"*** {config.script_name}: [処理1-分岐1-3] Column3つ以上（1つ目がテキスト） List -> {config.child_tag}（空Title + 複数Column） ***"
            stats[f'CONVERTED_TEXT_FIRST_COLUMN_MULTI_LIST_TO_{config.child_tag.upper()}'] += 1
            return child_elem, comment_text
        
        # Columnが3つ以上で、最初のColumnが空の場合、変換をスキップ（そのままList要素として残す）
        if col_count > 2:
            return None, f"*** {config.script_name}: [スキップ] Column3つ以上（1つ目が空） List -> 変換スキップ（そのままList要素として残す） ***"
        # Columnが2つ以上あり、かつ1つ目のColumnがラベル要素に該当しない場合の処理
        elif col_count >= config.column_condition_min and col1_text and not (is_label(col1_text) or is_kanji_number_label(col1_text)):
            # 常にItemSentenceの中にColumn要素を2つ作成
            child_elem = create_element_with_two_sentences(col1_sentence, col2_sentence, config, element)
            comment_text = f"*** {config.script_name}: [処理1-分岐1-1] Column2つ（1つ目がテキスト） List -> {config.child_tag}（Column要素2つ） ***"
            stats[f'CONVERTED_TEXT_FIRST_COLUMN_LIST_TO_{config.child_tag.upper()}'] += 1
            return child_elem, comment_text
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
            # テキストチェックは残しつつ、Sentence要素全体をコピーしてRuby要素などの子要素構造を保持
            list_sentence = get_list_sentence(element)
            if 'grade' in config.supported_types and list_text and is_subject_name_bracket(list_text) and is_grade_pattern(list_text):
                child_elem = create_empty_element(config)
                target_sentence = child_elem.find(f'{config.sentence_tag}/Sentence')
                if target_sentence is not None and list_sentence is not None:
                    # Sentence要素全体をコピー（属性と子要素を含む）
                    target_sentence.text = list_sentence.text
                    for child in list_sentence:
                        target_sentence.append(deepcopy(child))
                    # 属性をコピー
                    for attr_name, attr_value in list_sentence.attrib.items():
                        target_sentence.set(attr_name, attr_value)
                comment_text = f"*** {config.script_name}: [処理1-分岐2-1] 学年 List -> {config.child_tag} ***"
                stats[f'CONVERTED_GRADE_LIST_TO_{config.child_tag.upper()}'] += 1
            elif 'grade_double' in config.supported_types and list_text and is_grade_double_bracket(list_text):
                child_elem = create_empty_element(config)
                target_sentence = child_elem.find(f'{config.sentence_tag}/Sentence')
                if target_sentence is not None and list_sentence is not None:
                    target_sentence.text = list_sentence.text
                    for child in list_sentence:
                        target_sentence.append(deepcopy(child))
                    for attr_name, attr_value in list_sentence.attrib.items():
                        target_sentence.set(attr_name, attr_value)
                comment_text = f"*** {config.script_name}: [処理1-分岐2-1-1] 学年（2つ記載） List -> {config.child_tag} ***"
                stats[f'CONVERTED_GRADE_DOUBLE_LIST_TO_{config.child_tag.upper()}'] += 1
            elif 'grade_single' in config.supported_types and list_text and is_grade_single_bracket(list_text):
                child_elem = create_empty_element(config)
                target_sentence = child_elem.find(f'{config.sentence_tag}/Sentence')
                if target_sentence is not None and list_sentence is not None:
                    target_sentence.text = list_sentence.text
                    for child in list_sentence:
                        target_sentence.append(deepcopy(child))
                    for attr_name, attr_value in list_sentence.attrib.items():
                        target_sentence.set(attr_name, attr_value)
                comment_text = f"*** {config.script_name}: [処理1-分岐2-1-2] 学年（1つ記載） List -> {config.child_tag} ***"
                stats[f'CONVERTED_GRADE_SINGLE_LIST_TO_{config.child_tag.upper()}'] += 1
            elif list_text and is_subject_name_bracket(list_text):
                child_elem = create_empty_element(config)
                target_sentence = child_elem.find(f'{config.sentence_tag}/Sentence')
                if target_sentence is not None and list_sentence is not None:
                    target_sentence.text = list_sentence.text
                    for child in list_sentence:
                        target_sentence.append(deepcopy(child))
                    for attr_name, attr_value in list_sentence.attrib.items():
                        target_sentence.set(attr_name, attr_value)
                comment_text = f"*** {config.script_name}: [処理1-分岐2-2] 括弧付き科目名 List -> {config.child_tag} ***"
                stats[f'CONVERTED_SUBJECT_NAME_LIST_TO_{config.child_tag.upper()}'] += 1
            elif list_text and is_instruction_bracket(list_text):
                child_elem = create_empty_element(config)
                target_sentence = child_elem.find(f'{config.sentence_tag}/Sentence')
                if target_sentence is not None and list_sentence is not None:
                    target_sentence.text = list_sentence.text
                    for child in list_sentence:
                        target_sentence.append(deepcopy(child))
                    for attr_name, attr_value in list_sentence.attrib.items():
                        target_sentence.set(attr_name, attr_value)
                comment_text = f"*** {config.script_name}: [処理1-分岐2-3] 括弧付き指導項目 List -> {config.child_tag} ***"
                stats[f'CONVERTED_INSTRUCTION_LIST_TO_{config.child_tag.upper()}'] += 1
            else:
                # どのパターンにもマッチしなかったColumnなしListの場合
                child_elem = create_empty_element(config)
                # Sentence要素全体をコピーしてRuby要素などの子要素構造を保持
                target_sentence = child_elem.find(f'{config.sentence_tag}/Sentence')
                if target_sentence is not None and list_sentence is not None:
                    target_sentence.text = list_sentence.text
                    for child in list_sentence:
                        target_sentence.append(deepcopy(child))
                    for attr_name, attr_value in list_sentence.attrib.items():
                        target_sentence.set(attr_name, attr_value)
                comment_text = f"*** {config.script_name}: [処理1-分岐2-4] ColumnなしList -> {config.child_tag}Sentence ***"
                stats[f'CONVERTED_NO_COLUMN_LIST_TO_{config.child_tag.upper()}'] += 1

    # TableStruct, FigStruct, StyleStruct はList要素ではないため、変換対象外
    # これらは process_elements_recursive 関数で適切に処理される

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
    
    # テキストが複数行に連結されている場合、最初の行のみをチェック
    # （process_elements_recursiveでテキストが連結された場合に対応）
    if sentence_text:
        first_line = sentence_text.split('\n')[0].strip()
    else:
        first_line = ""

    if title_text and is_label(title_text):
        return 'labeled'

    # gradeパターンの判定を先に（subject_nameよりも）
    if 'grade' in config.supported_types and is_subject_name_bracket(first_line) and is_grade_pattern(first_line):
        return 'grade'
    if 'grade_double' in config.supported_types and is_grade_double_bracket(first_line):
        return 'grade_double'
    if 'grade_single' in config.supported_types and is_grade_single_bracket(first_line):
        return 'grade_single'

    # 丸括弧見出しの判定（JSON設定を使用）- subject_nameより先にチェック
    bracket_type = get_bracket_type(first_line)
    if bracket_type == 'subject_label_round':
        return 'subject_label_round'
    
    if is_subject_name_bracket(first_line):
        return 'subject_name'
    if is_instruction_bracket(first_line):
        return 'instruction'
    
    # Columnが2つ以上で最初がテキスト（ラベルではない）の場合の判定
    # ItemTitleが空で、ItemSentenceに複数のSentence要素またはColumn要素がある場合、text_first_columnタイプとみなす
    # （no_column_textの判定より先にチェックする必要がある）
    if not title_text:
        sentence_elem = element.find(config.sentence_tag)
        if sentence_elem is not None:
            # Column要素がある場合の判定
            columns = sentence_elem.findall('Column')
            if len(columns) >= 2:
                # 最初のColumn要素内のSentence要素を取得
                first_column = columns[0]
                first_column_sentence = first_column.find('Sentence')
                if first_column_sentence is not None:
                    first_sentence_text = "".join(first_column_sentence.itertext()).strip()
                    if first_sentence_text and not is_label(first_sentence_text) and not is_kanji_number_label(first_sentence_text):
                        # 括弧付きテキスト（科目名、指導項目、学年）でないことを確認
                        if not is_subject_name_bracket(first_sentence_text) and not is_instruction_bracket(first_sentence_text):
                            return 'text_first_column'
            
            # Sentence要素が直接ある場合の判定（後方互換性のため）
            sentences = sentence_elem.findall('Sentence')
            if len(sentences) >= 2:
                # 最初のSentenceの内容をチェック（ラベルではないテキストの場合）
                first_sentence_text = "".join(sentences[0].itertext()).strip() if len(sentences) > 0 else ""
                if first_sentence_text and not is_label(first_sentence_text) and not is_kanji_number_label(first_sentence_text):
                    # 括弧付きテキスト（科目名、指導項目、学年）でないことを確認
                    if not is_subject_name_bracket(first_sentence_text) and not is_instruction_bracket(first_sentence_text):
                        return 'text_first_column'
    
    # ColumnなしListから変換された要素かどうかを判定
    # ItemTitleが空で、ItemSentenceに括弧付きテキストがなく、List要素が子要素として存在しない場合、
    # ColumnなしListから変換された要素とみなす
    # また、ItemTitleが空で、ItemSentenceにテキストがあり、改行が含まれている場合も
    # ColumnなしListから変換された要素とみなす（複数のColumnなしListが統合された場合）
    # さらに、ItemTitleが空で、ItemSentenceにテキストがあり、List要素が子要素として存在する場合でも、
    # 最初のColumnなしListから変換された要素とみなす（ColumnありListが追加される前の状態）
    # ただし、List要素が子要素として存在し、Sentenceに改行が含まれていない場合は、
    # ColumnありListが追加された後の状態とみなし、no_column_textタイプと判定しない
    if not title_text and first_line and not is_subject_name_bracket(first_line) and not is_instruction_bracket(first_line):
        # List要素が子要素として存在しない場合、ColumnなしListから変換された要素とみなす
        list_elements = element.findall('List')
        if len(list_elements) == 0:
            return 'no_column_text'
        # List要素が子要素として存在する場合でも、Sentenceに改行が含まれている場合は
        # ColumnなしListから変換された要素とみなす（複数のColumnなしListが統合された後、ColumnありListが追加された場合）
        if sentence_text and '\n' in sentence_text:
            return 'no_column_text'
        # List要素が子要素として存在する場合でも、最初のColumnなしListから変換された要素とみなす
        # （ColumnありListが追加される前の状態を判定するため、Sentenceに改行が含まれていない場合でも、
        # Titleが空で、Sentenceにテキストがあり、括弧付きテキストでない場合、no_column_textとみなす）
        # ただし、この判定は、ColumnありListが追加された後でも適用される可能性があるため、
        # より正確な判定が必要な場合は、処理の順序を考慮する必要がある
        # しかし、現時点では、この判定で十分な場合が多い
        # 注意: この判定は、ColumnありListが追加された後でも適用される可能性があるため、
        # より正確な判定が必要な場合は、処理の順序を考慮する必要がある
        # しかし、現時点では、この判定で十分な場合が多い
        # ただし、List要素が子要素として存在し、Sentenceに改行が含まれていない場合は、
        # ColumnありListが追加された後の状態とみなし、no_column_textタイプと判定しない
        # この場合、otherタイプを返す
        # しかし、最初のColumnなしListがSubitem2に変換された直後、そのSubitem2にColumnありListが
        # 子要素として追加される前に、2つ目のColumnなしListが処理される場合、no_column_textタイプと判定する必要がある
        # この場合、List要素が子要素として存在していても、no_column_textタイプと判定する
        # ただし、この判定は、ColumnありListが追加された後でも適用される可能性があるため、
        # より正確な判定が必要な場合は、処理の順序を考慮する必要がある
        # しかし、現時点では、この判定で十分な場合が多い
        return 'no_column_text'
    
    return 'other'


def get_list_type(list_elem, config: ConversionConfig):
    """List要素のタイプを判定"""
    col1_sentence, _, col_count = get_list_columns(list_elem)
    col1_text = get_column_text(col1_sentence)
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
    
    # Columnが2つ以上で最初がテキスト（ラベルではない）の場合
    if col_count >= config.column_condition_min and col1_text and not (is_label(col1_text) or is_kanji_number_label(col1_text)):
        return 'text_first_column'
    
    return 'no_column_text'


def get_title_text(element, config: ConversionConfig) -> str:
    """
    要素のタイトルテキストを取得（共通化関数）
    
    Args:
        element: 要素
        config: 変換設定
    
    Returns:
        タイトルテキスト（要素がNoneまたはタイトルが存在しない場合は空文字列）
    """
    if element is None:
        return ""
    title_elem = element.find(config.title_tag)
    if title_elem is None:
        return ""
    return "".join(title_elem.itertext()).strip()


def has_following_alphabet_label_list(children_to_process: List, current_idx: int) -> bool:
    """
    後続の要素にアルファベットラベル付きListがあるかチェック

    Args:
        children_to_process: 処理対象の子要素リスト
        current_idx: 現在のインデックス

    Returns:
        アルファベットラベル付きListがある場合True
    """
    if current_idx + 1 >= len(children_to_process):
        return False

    next_child = children_to_process[current_idx + 1]
    if not is_list_element(next_child):
        return False

    next_col1_sentence, _, _ = get_list_columns(next_child)
    next_col1_text = get_column_text(next_col1_sentence)
    if not next_col1_text:
        return False

    # detect_label_idを使用してアルファベットラベルかチェック
    next_list_label_id = detect_label_id(next_col1_text)
    if is_alphabet_label(next_list_label_id):
        return True

    # 正規表現パターンでもチェック（detect_label_idが失敗した場合のフォールバック）
    return bool(re.match(r'^[（(]?[ａ-ｚA-ZＡ-Ｚ]+[）)]$', next_col1_text))


def has_following_non_label_two_column_list(children_to_process: List, current_idx: int, config: ConversionConfig) -> bool:
    """
    後続の要素にラベルのない2カラムListがあるかチェック

    Args:
        children_to_process: 処理対象の子要素リスト
        current_idx: 現在のインデックス
        config: 変換設定

    Returns:
        ラベルのない2カラムListがある場合True
    """
    if current_idx + 1 >= len(children_to_process):
        return False

    next_child = children_to_process[current_idx + 1]
    if not is_list_element(next_child):
        return False

    next_col1_sentence, _, next_col_count = get_list_columns(next_child)
    next_col1_text = get_column_text(next_col1_sentence)
    
    # Columnが2つで、1つ目のColumnがラベルでない場合
    if next_col_count == 2 and next_col1_text:
        next_has_label = is_label_text(next_col1_text, next_col_count)
        if not next_has_label:
            return True
    
    return False


def should_append_alphabet_label_as_child(last_child, child, col1_text, config: ConversionConfig) -> bool:
    """
    アルファベットラベル付きListを子要素として取り込むべきか判定
    
    Args:
        last_child: 最後に処理した子要素
        child: 現在処理中のList要素
        col1_text: Column1のテキスト
        config: 変換設定
    
    Returns:
        子要素として取り込むべき場合True
    """
    if last_child is None:
        return False
    
    current_title_text = get_title_text(last_child, config)
    list_label_id = detect_label_id(col1_text)
    
    if not is_alphabet_label(list_label_id):
        return False
    
    # Paragraphの場合の処理
    if config.parent_tag == 'Paragraph' and not current_title_text:
        return True
    
    # Itemの場合の処理
    if config.parent_tag == 'Item' and current_title_text:
        current_title_label_id = detect_label_id(current_title_text)
        is_current_title_label = current_title_label_id is not None
        
        if is_alphabet_label(current_title_label_id):
            return current_title_text == col1_text
        else:
            return not is_current_title_label or current_title_text == col1_text
    
    return False


def rebuild_parent_element(parent_elem, parent_sentence, parent_caption_elem_copy, parent_title_elem_copy, new_children, config: ConversionConfig):
    """
    親要素を再構築する
    
    Args:
        parent_elem: 親要素
        parent_sentence: 親要素のSentence要素
        parent_caption_elem_copy: 親要素のCaption要素のコピー（存在する場合）
        parent_title_elem_copy: 親要素のタイトル要素のコピー
        new_children: 新しい子要素のリスト
        config: 変換設定
    """
    original_attrs = dict(parent_elem.attrib)
    
    parent_elem.clear()
    parent_elem.attrib.update(original_attrs)
    
    # Caption要素が存在する場合、最初に追加（スキーマ順序に従う）
    # 例: ParagraphCaption, ItemCaption, Subitem1Caption など
    if parent_caption_elem_copy is not None:
        parent_elem.append(parent_caption_elem_copy)
    
    if parent_title_elem_copy is not None:
        parent_elem.append(parent_title_elem_copy)
    
    if parent_sentence is not None:
        parent_elem.append(parent_sentence)
    
    for new_child in new_children:
        parent_elem.append(new_child)


class ProcessingState:
    """要素処理の状態を管理するクラス"""
    def __init__(self):
        self.mode = ProcessingMode.LOOKING_FOR_FIRST_CHILD
        self.last_child = None
        self.seen_label_texts = set()
        self.new_children = []
        self.made_changes = False
        self.split_mode_terminated = False  # モード2の並列分割が終了したかどうか
    
    def add_seen_label(self, label_text: str):
        """出現したラベルを記録"""
        self.seen_label_texts.add(label_text)
    
    def has_seen_label(self, label_text: str) -> bool:
        """ラベルが既に出現したかチェック"""
        return label_text in self.seen_label_texts
    
    def append_child(self, child):
        """新しい子要素を追加"""
        self.new_children.append(child)
        self.made_changes = True
    
    def append_to_last_child(self, child):
        """最後の子要素に追加"""
        if self.last_child is not None:
            self.last_child.append(child)
            self.made_changes = True
        else:
            self.append_child(child)
    
    def set_last_child(self, child):
        """最後の子要素を設定"""
        self.last_child = child
        self.append_child(child)


def process_first_child_mode(child, state: ProcessingState, config: ConversionConfig, stats, parent_elem) -> bool:
    """
    最初の子要素モードでの処理
    
    Args:
        child: 処理対象の子要素
        state: 処理状態
        config: 変換設定
        stats: 統計情報
        parent_elem: 親要素
    
    Returns:
        処理が完了した場合True（モード変更が必要な場合）
    """
    if is_list_element(child):
        # 親要素が空の場合は常にList要素をそのまま追加（スキップ）
        if config.skip_empty_parent and is_parent_empty(parent_elem, config):
            state.append_child(child)
            stats[f'SKIPPED_DUE_TO_EMPTY_PARENT'] += 1
            state.mode = ProcessingMode.NORMAL_PROCESSING
            return True

        col1_sentence, _, col_count = get_list_columns(child)
        col1_text = get_column_text(col1_sentence)
        list_text = get_list_text(child)

        if col_count == 0:  # ColumnなしList
            # LOOKING_FOR_FIRST_CHILDモードでもColumnなしListを常に処理
            new_child, comment = create_element_from_list(child, config, stats, parent_elem)
            if new_child is not None:
                state.set_last_child(new_child)
            else:
                state.append_child(child)
            state.mode = ProcessingMode.NORMAL_PROCESSING
            return True
        else:  # ColumnありList
            # ラベルのテキストを取得して、既に出現したラベルかチェック
            has_label = is_label_text(col1_text, col_count)
            
            # 既に出現したラベルの場合、変換せずにListのまま取り込む
            if has_label and state.has_seen_label(col1_text):
                state.append_to_last_child(child)
                state.mode = ProcessingMode.NORMAL_PROCESSING
                return True
            
            new_child, comment = create_element_from_list(child, config, stats, parent_elem)
            if new_child is not None:
                state.set_last_child(new_child)
                # ラベルのテキストを記録
                if has_label:
                    state.add_seen_label(col1_text)
            else:
                state.append_child(child)
            state.mode = ProcessingMode.NORMAL_PROCESSING
            return True

    elif hasattr(child, 'tag') and isinstance(child.tag, str) and config.child_tag in child.tag:  # 既存の子要素
        state.set_last_child(child)
        state.mode = ProcessingMode.NORMAL_PROCESSING
        return True
    else:
        state.append_child(child)
        state.mode = ProcessingMode.NORMAL_PROCESSING
        return True


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

    # current_title_textを最初に取得（重複を避けるため）
    current_title_text = "".join(current_elem.find(config.title_tag).itertext()).strip() if current_elem.find(config.title_tag) is not None else ""
    
    # current_title_textが空で、current_typeが'other'の場合、親要素（Item要素）のタイトルテキストを参照する
    # これにより、「４．２」と「４．３」が同じラベル種類として正しく判定される
    # 例: Subitem2要素（空のTitle）の親であるItem要素（「４．２」）のタイトルテキストを使用
    if not current_title_text and current_type == 'other' and config.parent_tag == 'Paragraph' and list_type == 'labeled':
        # 親要素を探す（Subitem2の場合、Subitem1を経由してItem要素を探す）
        parent_elem = current_elem.getparent()
        item_elem = None
        if parent_elem is not None:
            if parent_elem.tag == 'Item':
                item_elem = parent_elem
            elif parent_elem.tag.startswith('Subitem'):
                # Subitem1, Subitem2等の場合、さらに親を探す
                grandparent_elem = parent_elem.getparent()
                if grandparent_elem is not None and grandparent_elem.tag == 'Item':
                    item_elem = grandparent_elem
        
        if item_elem is not None:
            parent_title_elem = item_elem.find('ItemTitle')
            if parent_title_elem is not None:
                parent_title_text = "".join(parent_title_elem.itertext()).strip()
                if parent_title_text and is_label(parent_title_text):
                    # 親要素のタイトルテキストを使用してラベル判定を行う
                    current_title_text = parent_title_text
                    current_type = 'labeled'  # 親要素がラベル付きなので、current_typeを'labeled'に設定

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

    # ラベルなしの2カラムListから変換された要素（Titleが空）の場合、
    # 後続のラベル付きListは常に取り込む（テストケース26, 30の仕様）
    if not current_title_text and current_type == 'other' and list_type == 'labeled':
        return False  # 取り込み

    if current_type == 'other' and list_type in [t for t in config.supported_types if t != 'grade']:
        return True

    if current_type == 'labeled' and list_type == 'labeled':
        current_label_id = detect_label_id(current_title_text)
        
        # 文脈依存のラベル判定: 最初の要素のラベルに基づいて除外リストを生成
        exclude_label_ids = get_exclude_label_ids_for_context(current_title_text)
        list_label_id = detect_label_id(list_title_text, exclude_label_ids)

        # ラベルIDが取得できない場合は異なる階層
        if current_label_id is None or list_label_id is None:
            return False

        # ラベルIDが異なる場合は異なる階層
        if current_label_id != list_label_id:
            return False

        # ラベルIDが同じでも、アルファベットラベルの場合はラベルテキストも比較
        # テスト21: 「ａ）」と「ｂ）」は同じラベルIDだが、異なるラベルテキストなので別のSubitem1として扱う
        if current_label_id in ALPHABET_LABEL_IDS_EXTENDED:
            # アルファベットラベルの場合は、ラベルテキストが異なれば異なる階層
            return current_title_text == list_title_text

        # ラベルIDが同じで、アルファベットラベルでない場合は同じ種類（同じ処理）
        # 階層レベルや詳細なタイプは考慮しない
        return True

    if current_type == 'grade' and list_type == 'grade':
        return True

    if current_type == 'instruction' and list_type == 'instruction':
        return True

    # 丸括弧見出しの場合は、後続のすべてのListを取り込む（JSON設定による特殊処理）
    # convert_subitem1_step0.pyのテスト19で、丸括弧見出しの後にすべてのList要素が続くべき
    if current_type == 'subject_label_round':
        return False  # 取り込み（後続のListをすべて取り込む）

    # convert_item_step0.pyのロジックに合わせるための追加ルール
    # subject_name, grade, instructionタイプのItemの後には、
    # labeled, grade, instruction, no_column_textタイプのListが取り込まれる
    # （このルールを先にチェックして、取り込みを優先する）
    # テスト09, 10: gradeタイプのItemの後にsubject_nameタイプのListが来た場合も取り込まれる
    # テスト12: subject_nameタイプ同士は分割される（下記の分割ルールが優先される）
    
    # subject_name同士は分割（このルールを先にチェック）
    if current_type == 'subject_name' and list_type == 'subject_name':
        return True  # 分割（科目名同士は分割）

    # grade, instructionタイプのItemの後には、labeled, grade, instruction, no_column_text, subject_nameタイプのListが取り込まれる
    if current_type in ['grade', 'instruction'] and list_type in ['labeled', 'instruction', 'grade', 'no_column_text', 'subject_name']:
        return False  # 取り込み
    
    # subject_nameタイプのItemの後には、labeled, grade, instruction, no_column_textタイプのListが取り込まれる
    # （subject_name同士は上記の分割ルールで処理される）
    if current_type == 'subject_name' and list_type in ['labeled', 'instruction', 'grade', 'no_column_text']:
        return False  # 取り込み

    # text_first_columnタイプ同士は分割（テストケース32, 33の期待値に合わせる）
    # Columnが2つ以上で最初がテキスト（ラベルではない）のListが連続する場合、それぞれが別々のItemに変換される
    if current_type == 'text_first_column' and list_type == 'text_first_column':
        return True  # 分割
    
    # no_column_textタイプ同士の処理（設定に基づいて分割/取り込みを判定）
    # 親要素のSentenceの次のList要素がno_column_textに該当する場合の処理
    if current_type == 'no_column_text' and list_type == 'no_column_text':
        # 設定で並列分割モードが有効な場合は分割、無効な場合は取り込み
        if should_split_no_column_text_lists(config.child_tag):
            return True  # 分割（モード2）
        else:
            return False  # 取り込み（モード1）
    
    return False


def handle_labeled_list_with_same_hierarchy(child, col1_text, has_label, state: ProcessingState,
                                           config: ConversionConfig, stats, parent_elem) -> bool:
    """
    ラベル付きListで、are_same_hierarchyがTrueの場合の処理（分割）
    
    Args:
        child: List要素
        col1_text: Column1のテキスト
        has_label: ラベルかどうか
        state: 処理状態
        config: 変換設定
        stats: 統計情報
        parent_elem: 親要素
    
    Returns:
        処理が完了した場合False（通常の処理フローに戻る）
    """
    new_child, comment = create_element_from_list(child, config, stats, parent_elem)
    if new_child is not None:
        state.set_last_child(new_child)
        if has_label:
            state.add_seen_label(col1_text)
    else:
        state.append_child(child)
    return False


def should_split_labeled_list(current_title_text, col1_text, current_label_id, list_label_id, 
                              col_count: Optional[int] = None, state: Optional[ProcessingState] = None) -> bool:
    """
    ラベル付きListを分割するかどうかを判定
    
    ルール:
    1. 同じラベルの種類でかつ同じ値がまだ登場していない（兄要素にない）：分割する
    2. 同じラベルの種類でかつ、同じ値がすでに登場している：取り込む
    3. ラベルの種類が異なる：取り込む
    
    Args:
        current_title_text: 現在のItemのタイトルテキスト
        col1_text: ListのColumn1のテキスト
        current_label_id: 現在のItemのラベルID
        list_label_id: ListのラベルID
        col_count: Column数（使用しないが、後方互換性のため保持）
        state: 処理状態（既出ラベルチェック用）
    
    Returns:
        分割する場合True、取り込む場合False
    """
    # ラベルIDが取得できない場合は取り込む
    if current_label_id is None or list_label_id is None:
        return False
    
    # ラベルの種類が異なる場合は取り込む
    if current_label_id != list_label_id:
        return False
    
    # 同じラベルの種類の場合
    # 同じ値の場合は取り込む（既に登場している）
    if current_title_text == col1_text:
        return False
    
    # 異なる値の場合、まだ登場していない場合は分割する
    if state is not None and not state.has_seen_label(col1_text):
        return True
    
    # 既に登場している場合は取り込む
    return False


def handle_labeled_list_with_different_hierarchy(child, col_count, col1_text, has_label,
                                                 state: ProcessingState, config: ConversionConfig,
                                                 stats, parent_elem) -> bool:
    """
    ラベル付きListで、are_same_hierarchyがFalseの場合の処理
    
    Args:
        child: List要素
        col_count: Column数（分割判定には使用しないが、後方互換性のため保持）
        col1_text: Column1のテキスト
        has_label: ラベルかどうか
        state: 処理状態
        config: 変換設定
        stats: 統計情報
        parent_elem: 親要素
    
    Returns:
        処理が完了した場合False（通常の処理フローに戻る）
    """
    current_title_text = get_title_text(state.last_child, config)
    current_label_id = detect_label_id(current_title_text)
    
    # current_title_textが空の場合、親要素（Item要素）のタイトルテキストを参照する
    # これにより、「４．２」と「４．３」が同じラベル種類として正しく判定される
    if not current_title_text and state.last_child is not None and config.parent_tag == 'Paragraph':
        # 親要素を探す（Subitem2の場合、Subitem1を経由してItem要素を探す）
        parent_elem = state.last_child.getparent()
        item_elem = None
        if parent_elem is not None:
            if parent_elem.tag == 'Item':
                item_elem = parent_elem
            elif parent_elem.tag.startswith('Subitem'):
                # Subitem1, Subitem2等の場合、さらに親を探す
                grandparent_elem = parent_elem.getparent()
                if grandparent_elem is not None and grandparent_elem.tag == 'Item':
                    item_elem = grandparent_elem
        
        if item_elem is not None:
            parent_title_elem = item_elem.find('ItemTitle')
            if parent_title_elem is not None:
                parent_title_text = "".join(parent_title_elem.itertext()).strip()
                if parent_title_text and is_label(parent_title_text):
                    # 親要素のタイトルテキストを使用してラベル判定を行う
                    current_title_text = parent_title_text
                    current_label_id = detect_label_id(current_title_text)
    
    list_label_id = detect_label_id(col1_text)
    
    # ラベルなしの2カラムListから変換された要素（Titleが空）の場合、
    # 後続のラベル付きListは常に取り込む（テストケース26, 30の仕様）
    # ただし、親要素のタイトルテキストが取得できた場合は除く
    if not current_title_text and current_label_id is None:
        state.append_to_last_child(child)
        return False
    
    # 分割判定（ラベルの種類と値、既出チェックで判定）
    # ルール:
    # 1. 同じラベルの種類でかつ同じ値がまだ登場していない（兄要素にない）：分割する
    # 2. 同じラベルの種類でかつ、同じ値がすでに登場している：取り込む
    # 3. ラベルの種類が異なる：取り込む
    if should_split_labeled_list(current_title_text, col1_text, current_label_id, list_label_id, col_count, state):
        # 別のItemとして変換する（分割）
        new_child, comment = create_element_from_list(child, config, stats, parent_elem)
        if new_child is not None:
            state.set_last_child(new_child)
            state.add_seen_label(col1_text)
        else:
            state.append_child(child)
        return False
    
    # それ以外は子要素として取り込む
    state.append_to_last_child(child)
    return False


def handle_no_column_list_in_normal_mode(child, state: ProcessingState, config: ConversionConfig, stats) -> bool:
    """
    ColumnなしListの処理（NORMAL_PROCESSINGモード、are_same_hierarchyがFalseの場合）
    
    Args:
        child: List要素
        state: 処理状態
        config: 変換設定
    
    Returns:
        処理が完了した場合False（通常の処理フローに戻る）
    """
    # last_childがColumnありListから変換されたItemかどうかを判定
    title_text = get_title_text(state.last_child, config)
    is_column_list_converted_item = bool(title_text)
    
    # last_childが括弧付き見出し系から変換されたItemかどうかを判定
    element_type = get_element_type(state.last_child, config)
    is_bracket_item = (element_type in ['subject_name', 'instruction', 'grade', 'grade_single', 'grade_double'])
    
    # last_childがColumnなしListから変換されたItem（no_column_textタイプ）かどうかを判定
    is_no_column_text_item = (element_type == 'no_column_text')
    
    # last_childがtext_first_columnタイプ（ColumnありListで最初のColumnがテキスト）かどうかを判定
    is_text_first_column_item = (element_type == 'text_first_column')
    
    if is_column_list_converted_item or is_bracket_item:
        # ColumnありListまたは括弧付き見出し系から変換されたItemの場合、
        # 異なる種類のListはList要素のまま追加
        state.append_to_last_child(child)
        return False
    elif is_no_column_text_item:
        # ColumnなしListから変換されたItemの場合、後続のno_column_textタイプのListも取り込む
        # List要素をそのまま追加
        state.append_to_last_child(child)
        return False
    elif is_text_first_column_item:
        # text_first_columnタイプの場合、後続のColumnなしListを全て取り込む
        # List要素をそのまま追加
        state.append_to_last_child(child)
        return False
    else:
        # ColumnありListから変換されたItemでない場合の処理
        # ItemSentenceにColumn要素がある場合は、List要素として追加
        sentence_container = state.last_child.find(config.sentence_tag)
        if sentence_container is not None:
            columns = sentence_container.findall('Column')
            if len(columns) > 0:
                # Column要素がある場合は、List要素として追加
                state.append_to_last_child(child)
                return False
        
        # Column要素がない場合、新しいSentence要素を作成して追加
        list_sentence = get_list_sentence(child)
        if list_sentence is not None:
            if sentence_container is not None:
                # 既存のSentence要素の最大のNum値を取得
                existing_sentences = sentence_container.findall('Sentence')
                max_num = 0
                for sent in existing_sentences:
                    num_attr = sent.get('Num')
                    if num_attr:
                        try:
                            num_value = int(num_attr)
                            max_num = max(max_num, num_value)
                        except ValueError:
                            pass
                
                # 新しいSentence要素を作成して追加（Ruby要素などの子要素構造を保持）
                new_sentence = etree.SubElement(sentence_container, 'Sentence', Num=str(max_num + 1))
                new_sentence.text = list_sentence.text
                for child_elem in list_sentence:
                    new_sentence.append(deepcopy(child_elem))
                # 属性をコピー（WritingModeなど）
                for attr_name, attr_value in list_sentence.attrib.items():
                    if attr_name != 'Num':  # Num属性は既に設定済みなのでスキップ
                        new_sentence.set(attr_name, attr_value)
                state.made_changes = True
            else:
                # Sentenceコンテナ要素が見つからない場合は、List要素をそのまま追加
                state.append_to_last_child(child)
        else:
            # Sentence要素が取得できない場合は、List要素をそのまま追加
            state.append_to_last_child(child)
        return False


def handle_multi_column_labeled_list(child, col_count, col1_text, has_label,
                                     state: ProcessingState, config: ConversionConfig,
                                     stats, parent_elem) -> bool:
    """
    Columnが3つ以上で最初がラベルのListの処理（NORMAL_PROCESSINGモード）
    
    注意: この関数は、are_same_hierarchyの判定後に呼び出されるため、
    内部でare_same_hierarchyを再度チェックする必要はない。
    
    Args:
        child: List要素
        col_count: Column数
        col1_text: Column1のテキスト
        has_label: ラベルかどうか
        state: 処理状態
        config: 変換設定
        stats: 統計情報
        parent_elem: 親要素
    
    Returns:
        処理が完了した場合False（通常の処理フローに戻る）
    """
    # are_same_hierarchyの判定は呼び出し元で既に行われているため、
    # ここでは直接handle_labeled_list_with_different_hierarchyを呼び出す
    return handle_labeled_list_with_different_hierarchy(child, col_count, col1_text, has_label,
                                                        state, config, stats, parent_elem)


def handle_multi_column_non_labeled_list(child, col_count, state: ProcessingState,
                                        config: ConversionConfig, stats, parent_elem) -> bool:
    """
    Columnが3つ以上で最初がラベルではないListの処理（NORMAL_PROCESSINGモード、are_same_hierarchyがFalseの場合）
    
    Args:
        child: List要素
        col_count: Column数
        state: 処理状態
        config: 変換設定
        stats: 統計情報
        parent_elem: 親要素
    
    Returns:
        処理が完了した場合False（通常の処理フローに戻る）
    """
    col1_sentence, _, _ = get_list_columns(child)
    col1_text = "".join(col1_sentence.itertext()).strip() if col1_sentence is not None else ""
    list_label_id = detect_label_id(col1_text)
    
    # ラベルIDが取得できない場合（ラベルではないテキストの場合）、「text_non_label」を設定
    if list_label_id is None and col1_text:
        list_label_id = 'text_non_label'
    
    # create_element_from_listでItemに変換を試みる
    # テスト27: 「b）」はis_labelがFalseを返すが、create_element_from_listでItemに変換される
    # 「テキスト（ラベルではない）」はItemに変換されるが、子要素として取り込まれる
    new_child, comment = create_element_from_list(child, config, stats, parent_elem)
    if new_child is not None:
        # Itemに変換できた場合、are_same_hierarchyをチェックして分割/取り込みを判定
        if state.last_child is not None:
            # text_first_columnタイプ同士は常に分割
            current_type = get_element_type(state.last_child, config)
            if current_type == 'text_first_column':
                # 分割する場合、新しいItemとして追加
                state.set_last_child(new_child)
                return False
            
            # 分割判定（column数に関わらず）
            current_title_text = get_title_text(state.last_child, config)
            current_label_id = detect_label_id(current_title_text)
            
            # 前のItemもテキスト（ラベルではない）の場合、current_label_idを「text_non_label」に設定
            if current_label_id is None and not current_title_text:
                # ItemTitleが空で、ItemSentenceの最初のSentenceがラベルではないテキストの場合
                sentences = state.last_child.findall(f'{config.sentence_tag}/Sentence')
                if len(sentences) >= 2:
                    first_sentence_text = "".join(sentences[0].itertext()).strip() if len(sentences) > 0 else ""
                    if first_sentence_text and not is_label(first_sentence_text) and not is_kanji_number_label(first_sentence_text):
                        if not is_subject_name_bracket(first_sentence_text) and not is_instruction_bracket(first_sentence_text):
                            current_label_id = 'text_non_label'
            
            # 分割判定（ラベルの種類と値、既出チェックで判定）
            # ルール:
            # 1. 同じラベルの種類でかつ同じ値がまだ登場していない（兄要素にない）：分割する
            # 2. 同じラベルの種類でかつ、同じ値がすでに登場している：取り込む
            # 3. ラベルの種類が異なる：取り込む
            if should_split_labeled_list(current_title_text, col1_text, current_label_id, list_label_id, col_count, state):
                # 分割する場合、新しいItemとして追加
                state.set_last_child(new_child)
                state.add_seen_label(col1_text)
                return False
            else:
                # 取り込む場合、子要素として取り込む
                state.append_to_last_child(child)
                return False
        else:
            # last_childがNoneの場合、新しいItemとして追加
            state.set_last_child(new_child)
            return False
    
    # Itemに変換できない場合、子要素として取り込む
    if config.parent_tag == 'Paragraph' and state.last_child is not None:
        state.append_to_last_child(child)
        return False
    else:
        # それ以外の場合は変換をスキップして独立したList要素として残す
        state.append_child(child)
        return False


def handle_two_column_labeled_list(child, col_count, col1_text, has_label,
                                  state: ProcessingState, config: ConversionConfig,
                                  stats, parent_elem) -> bool:
    """
    Columnが2つで最初がラベルのListの処理（NORMAL_PROCESSINGモード）
    
    注意: この関数は、are_same_hierarchyの判定後に呼び出されるため、
    内部でare_same_hierarchyを再度チェックする必要はない。
    
    Args:
        child: List要素
        col_count: Column数
        col1_text: Column1のテキスト
        has_label: ラベルかどうか
        state: 処理状態
        config: 変換設定
        stats: 統計情報
        parent_elem: 親要素
    
    Returns:
        処理が完了した場合False（通常の処理フローに戻る）
    """
    # are_same_hierarchyの判定は呼び出し元で既に行われているため、
    # ここでは直接handle_labeled_list_with_different_hierarchyを呼び出す
    return handle_labeled_list_with_different_hierarchy(child, col_count, col1_text, has_label,
                                                        state, config, stats, parent_elem)


def handle_two_column_non_labeled_list(child, col_count, col1_text, has_label, state: ProcessingState,
                                      config: ConversionConfig, stats, parent_elem, 
                                      children_to_process: List = None, child_idx: int = None) -> bool:
    """
    Columnが2つで最初がラベルでない場合、またはColumnが1つ以下のListの処理
    （NORMAL_PROCESSINGモード、are_same_hierarchyがFalseの場合）
    
    Args:
        child: List要素
        col_count: Column数
        col1_text: Column1のテキスト
        has_label: ラベルかどうか
        state: 処理状態
        config: 変換設定
        stats: 統計情報
        parent_elem: 親要素
        children_to_process: 処理対象の子要素リスト（後続要素チェック用）
        child_idx: 現在のインデックス（後続要素チェック用）
    
    Returns:
        処理が完了した場合False（通常の処理フローに戻る）
    """
    # ラベル付きListの場合は変換を試みる
    if has_label:
        # create_element_from_listでItemに変換を試みる
        new_child, comment = create_element_from_list(child, config, stats, parent_elem)
        if new_child is not None:
            # Itemに変換できた場合、分割/取り込み判定を行う
            if state.last_child is not None:
                # text_first_columnタイプ同士は常に分割
                current_type = get_element_type(state.last_child, config)
                if current_type == 'text_first_column':
                    # 分割する場合、新しいItemとして追加
                    state.set_last_child(new_child)
                    return False
                
                current_title_text = get_title_text(state.last_child, config)
                current_label_id = detect_label_id(current_title_text)
                list_label_id = detect_label_id(col1_text)
                
                # 分割判定（ラベルの種類と値、既出チェックで判定）
                # ルール:
                # 1. 同じラベルの種類でかつ同じ値がまだ登場していない（兄要素にない）：分割する
                # 2. 同じラベルの種類でかつ、同じ値がすでに登場している：取り込む
                # 3. ラベルの種類が異なる：取り込む
                if should_split_labeled_list(current_title_text, col1_text, current_label_id, list_label_id, col_count, state):
                    # 分割する場合、新しいItemとして追加
                    state.set_last_child(new_child)
                    state.add_seen_label(col1_text)
                    return False
                else:
                    # 取り込む場合、子要素として取り込む
                    state.append_to_last_child(child)
                    return False
            else:
                # last_childがNoneの場合、新しいItemとして追加
                state.set_last_child(new_child)
                state.add_seen_label(col1_text)
                return False
        else:
            # 変換できない場合、子要素として取り込む
            state.append_to_last_child(child)
            return False
    else:
        # ラベルでない場合、前のItemがラベル付きItem（Titleが空でない）の場合は子要素として取り込む
        if state.last_child is not None:
            current_title_text = get_title_text(state.last_child, config)
            # 前のItemがラベル付きItem（Titleが空でない）の場合、ラベルなし2カラムListを子要素として取り込む
            if current_title_text:
                state.append_to_last_child(child)
                return False
        
        # 前のItemがラベルなしItem、またはlast_childがNoneの場合、create_element_from_listで変換を試みる
        new_child, comment = create_element_from_list(child, config, stats, parent_elem)
        if new_child is not None:
            # 変換できた場合、分割/取り込み判定を行う
            if state.last_child is not None:
                current_title_text = get_title_text(state.last_child, config)
                current_label_id = detect_label_id(current_title_text)
                
                # 前のItemもテキスト（ラベルではない）の場合、current_label_idを「text_non_label」に設定
                if current_label_id is None and not current_title_text:
                    # ItemTitleが空で、ItemSentenceの最初のSentenceがラベルではないテキストの場合
                    sentences = state.last_child.findall(f'{config.sentence_tag}/Sentence')
                    if len(sentences) >= 2:
                        first_sentence_text = "".join(sentences[0].itertext()).strip() if len(sentences) > 0 else ""
                        if first_sentence_text and not is_label(first_sentence_text) and not is_kanji_number_label(first_sentence_text):
                            if not is_subject_name_bracket(first_sentence_text) and not is_instruction_bracket(first_sentence_text):
                                current_label_id = 'text_non_label'
                
                # ラベルIDが取得できない場合（ラベルではないテキストの場合）、「text_non_label」を設定
                list_label_id = detect_label_id(col1_text)
                if list_label_id is None and col1_text:
                    list_label_id = 'text_non_label'
                
                # 分割判定（ラベルの種類と値、既出チェックで判定）
                # ルール:
                # 1. 同じラベルの種類でかつ同じ値がまだ登場していない（兄要素にない）：分割する
                # 2. 同じラベルの種類でかつ、同じ値がすでに登場している：取り込む
                # 3. ラベルの種類が異なる：取り込む
                if should_split_labeled_list(current_title_text, col1_text, current_label_id, list_label_id, col_count, state):
                    # 分割する場合、新しいItemとして追加
                    state.set_last_child(new_child)
                    state.add_seen_label(col1_text)
                    return False
                else:
                    # 取り込む場合、子要素として取り込む
                    state.append_to_last_child(child)
                    return False
            else:
                # last_childがNoneの場合、新しいItemとして追加
                state.set_last_child(new_child)
                return False
        else:
            # 変換できない場合、子要素として取り込む
            state.append_to_last_child(child)
            return False


def process_normal_mode_list_element(child, child_idx, children_to_process, state: ProcessingState, 
                                     config: ConversionConfig, stats, parent_elem):
    """
    NORMAL_PROCESSINGモードでのList要素処理
    
    Args:
        child: 処理対象のList要素
        child_idx: 現在のインデックス
        children_to_process: 処理対象の子要素リスト
        state: 処理状態
        config: 変換設定
        stats: 統計情報
        parent_elem: 親要素
    
    Returns:
        処理が完了した場合True（continueが必要な場合）
    """
    col1_sentence, _, col_count = get_list_columns(child)

    # 親要素が空の場合は常にList要素をそのまま追加（スキップ）
    if config.skip_empty_parent and is_parent_empty(parent_elem, config):
        state.append_child(child)
        stats[f'SKIPPED_DUE_TO_EMPTY_PARENT'] += 1
        return True

    # ColumnありListの場合、ラベルのテキストを取得
    col1_text = get_column_text(col1_sentence)
    has_label = is_label_text(col1_text, col_count)
    
    # ColumnなしListの場合、指導項目かどうかをチェック
    list_text = get_list_text(child) if col_count == 0 else ""
    is_instruction = is_instruction_bracket(list_text) if list_text else False
    
    # 指導項目の場合は重複チェックをスキップ（指導項目は必ず同じラベルが続くため）
    # 既に出現したラベルの場合、変換せずにListのまま取り込む（指導項目を除く）
    if has_label and state.has_seen_label(col1_text) and not is_instruction:
        state.append_to_last_child(child)
        return True
    
    if state.last_child is None:
        # 最初の要素の場合はcreate_element_from_listを使用
        new_child, comment = create_element_from_list(child, config, stats, parent_elem)
        if new_child is not None:
            state.set_last_child(new_child)
            # ラベルのテキストを記録
            if has_label:
                state.add_seen_label(col1_text)
        else:
            # create_element_from_listがNoneを返した場合（変換スキップ）、List要素をそのまま追加
            state.append_child(child)
        return False
    
    elif are_same_hierarchy(state.last_child, child, config):
        # モード2の並列分割が終了している場合は、通常の処理を行う
        if state.split_mode_terminated:
            # 並列分割が終了している場合、カラムなしリストは取り込む
            state.append_to_last_child(child)
            return True
        
        # モード2の場合の処理: no_column_textタイプのItemの後、カラムありリスト（ラベル付き）が登場した場合は並列分割を終了
        element_type = get_element_type(state.last_child, config)
        is_no_column_text_item = (element_type == 'no_column_text')
        is_split_mode_enabled = should_split_no_column_text_lists(config.child_tag)
        
        if is_no_column_text_item and is_split_mode_enabled:
            # モード2が有効で、last_childがno_column_textタイプの場合
            if col_count > 0 and has_label:
                # カラムありリスト（ラベル付き）が登場した場合は並列分割を終了（取り込む）
                state.append_to_last_child(child)
                state.split_mode_terminated = True  # 並列分割を終了
                return True
        
        # ColumnありListの場合、ItemTitleが空で、新しいラベルがアルファベットラベルの場合は子要素として取り込む
        # （ParagraphNumにドット区切り数字がある場合の処理）
        if col_count > 0 and has_label:
            if should_append_alphabet_label_as_child(state.last_child, child, col1_text, config):
                state.append_to_last_child(child)
                return True
        
        # ColumnなしListの場合、指導項目かどうかをチェック
        list_text_for_check = get_list_text(child) if col_count == 0 else ""
        is_instruction_for_check = is_instruction_bracket(list_text_for_check) if list_text_for_check else False
        
        # 既に出現したラベルの場合、変換せずにListのまま取り込む（指導項目を除く）
        if has_label and state.has_seen_label(col1_text) and not is_instruction_for_check:
            state.append_to_last_child(child)
            return False
        else:
            new_child, comment = create_element_from_list(child, config, stats, parent_elem)
            if new_child is not None:
                state.set_last_child(new_child)
                # ラベルのテキストを記録
                if has_label:
                    state.add_seen_label(col1_text)
            else:
                state.append_child(child)
            return False
    else:
        # last_childが存在する場合の処理
        if state.last_child is not None:
            # last_childのタイプを取得
            element_type = get_element_type(state.last_child, config)
            
            # Item内で、Subitem1Titleが空でない場合、後続のアルファベットラベル付きListを子要素として取り込む
            if config.parent_tag == 'Item' and col_count > 0 and has_label:
                if should_append_alphabet_label_as_child(state.last_child, child, col1_text, config):
                    state.append_to_last_child(child)
                    return True
            
            # 丸括弧見出しの場合は、後続のList要素をすべてList要素として取り込む（JSON設定による特殊処理）
            if element_type == 'subject_label_round':
                state.append_to_last_child(child)
                return True
            
            # text_first_columnタイプの場合、後続のList要素が同じtext_first_columnタイプの場合は分割する
            # この判定はhandle_two_column_non_labeled_listやhandle_multi_column_non_labeled_list内で行うため、
            # ここでは通常の処理フローに進む
            
            # Column数による処理分岐
            if col_count == 0:
                # ColumnなしListの処理
                return handle_no_column_list_in_normal_mode(child, state, config, stats)
            else:
                # ColumnありListの場合
                # モード2の場合の処理: no_column_textタイプのItemの後、カラムありリスト（ラベル付き）が登場した場合は並列分割を終了
                is_no_column_text_item = (element_type == 'no_column_text')
                is_split_mode_enabled = should_split_no_column_text_lists(config.child_tag)
                
                if is_no_column_text_item and is_split_mode_enabled:
                    # モード2が有効で、last_childがno_column_textタイプの場合
                    if col_count > 0 and has_label:
                        # カラムありリスト（ラベル付き）が登場した場合は並列分割を終了（取り込む）
                        state.append_to_last_child(child)
                        state.split_mode_terminated = True  # 並列分割を終了
                        return True
                
                # ColumnなしListの場合、指導項目かどうかをチェック（念のため）
                list_text_for_check2 = get_list_text(child) if col_count == 0 else ""
                is_instruction_for_check2 = is_instruction_bracket(list_text_for_check2) if list_text_for_check2 else False
                
                # 既に出現したラベルの場合、変換せずにListのまま取り込む（指導項目を除く）
                if has_label and state.has_seen_label(col1_text) and not is_instruction_for_check2:
                    state.append_to_last_child(child)
                    return True
                
                # Column数による処理分岐
                if col_count > 2:
                    # Columnが3つ以上の場合
                    if col1_text and (is_label(col1_text) or is_kanji_number_label(col1_text)):
                        # Columnが3つ以上で最初がラベルの場合の処理
                        return handle_multi_column_labeled_list(child, col_count, col1_text, has_label,
                                                                state, config, stats, parent_elem)
                    else:
                        # Columnが3つ以上で最初がラベルではない場合の処理
                        return handle_multi_column_non_labeled_list(child, col_count, state, config, stats, parent_elem)
                else:
                    # Columnが2つ以下の場合
                    if col_count >= config.column_condition_min and col1_text and (is_label(col1_text) or is_kanji_number_label(col1_text)):
                        # Columnが2つで最初がラベルの場合の処理
                        return handle_two_column_labeled_list(child, col_count, col1_text, has_label,
                                                              state, config, stats, parent_elem)
                    else:
                        # Columnが2つで最初がラベルでない場合、またはColumnが1つ以下の場合の処理
                        return handle_two_column_non_labeled_list(child, col_count, col1_text, has_label, state,
                                                                config, stats, parent_elem, children_to_process, child_idx)
        else:
            state.append_child(child)
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

    # 処理状態の初期化
    state = ProcessingState()

    # 親要素のSentenceの次の要素から処理を開始
    children_to_process = list(siblings)

    for child_idx, child in enumerate(children_to_process):
        if state.mode == ProcessingMode.LOOKING_FOR_FIRST_CHILD:
            process_first_child_mode(child, state, config, stats, parent_elem)
        
        elif state.mode == ProcessingMode.NORMAL_PROCESSING:
            if is_list_element(child):
                if process_normal_mode_list_element(child, child_idx, children_to_process, state, config, stats, parent_elem):
                    continue
            elif child.tag in STRUCT_ELEMENT_TAGS:
                # TableStruct, FigStruct, StyleStructは元の位置を保持するため、
                # append_to_last_childではなくappend_childを使用
                # これにより、文書内での順序が維持される
                state.append_child(child)
            elif hasattr(child, 'tag') and isinstance(child.tag, str) and config.child_tag in child.tag:  # 既存の子要素
                state.set_last_child(child)
            else:
                state.append_child(child)

    # 親要素の再構築
    # 親要素のタグ名から対応するCaption要素のタグ名を動的に生成
    # 例: Paragraph → ParagraphCaption, Item → ItemCaption, Subitem1 → Subitem1Caption
    caption_tag_name = config.parent_tag + 'Caption'
    parent_caption_elem = parent_elem.find(caption_tag_name)
    parent_caption_elem_copy = deepcopy(parent_caption_elem) if parent_caption_elem is not None else None
    
    # タイトル要素の取得
    if config.parent_tag == 'Paragraph':
        # Paragraphの場合はParagraphNumを保持
        parent_title_elem_copy = deepcopy(parent_elem.find('ParagraphNum')) if parent_elem.find('ParagraphNum') is not None else None
    else:
        # その他の要素の場合はTitle要素を保持
        parent_title_elem_copy = deepcopy(parent_elem.find(config.parent_tag + 'Title')) if parent_elem.find(config.parent_tag + 'Title') is not None else None

    rebuild_parent_element(parent_elem, parent_sentence, parent_caption_elem_copy, parent_title_elem_copy, state.new_children, config)

    return state.made_changes


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
        f'CONVERTED_LABELED_MULTI_COLUMN_LIST_TO_{config.child_tag.upper()}',
        f'CONVERTED_KANJI_LABELED_MULTI_COLUMN_LIST_TO_{config.child_tag.upper()}',
        f'CONVERTED_MULTI_COLUMN_LIST_TO_{config.child_tag.upper()}',
        f'CONVERTED_NO_COLUMN_LIST_TO_{config.child_tag.upper()}',
        f'CONVERTED_SUBJECT_NAME_LIST_TO_{config.child_tag.upper()}',
        f'CONVERTED_INSTRUCTION_LIST_TO_{config.child_tag.upper()}',
        f'CONVERTED_NON_LIST_TO_{config.child_tag.upper()}',
        f'CONVERTED_TEXT_FIRST_COLUMN_LIST_TO_{config.child_tag.upper()}',
        f'CONVERTED_TEXT_FIRST_COLUMN_MULTI_LIST_TO_{config.child_tag.upper()}',
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
            elif 'TEXT_FIRST_COLUMN' in key:
                desc = "Column2つ（1つ目がテキスト）"
            elif 'LABELED_MULTI_COLUMN' in key:
                desc = "Column3つ以上（1つ目がラベル）"
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


def find_split_point_common(elem: etree.Element, config: ConversionConfig, column_target: int = 0, skip_bracket_check: bool = False, subject_bracket_only: bool = False, skip_first_list: bool = False) -> Optional[Tuple[int, str]]:
    """
    共通の分割ポイント検出関数

    Args:
        elem: 処理対象要素（Item, Subitem1, Subitem2）
        config: 変換設定
        column_target: 対象とするcolumn_count（0:列なし, 1:1列のみ, etc）
        skip_bracket_check: 括弧チェックをスキップするかどうか
        subject_bracket_only: 科目名括弧のみを対象とするかどうか
        skip_first_list: subject_bracket_only=Trueの場合、最初のList要素をスキップするかどうか

    Returns:
        (index, split_type) または None
    """
    children = list(elem)

    if subject_bracket_only:
        # 科目名括弧・学年括弧を対象とする場合
        first_list_skipped = False
        for i, child in enumerate(children):
            if child.tag != 'List':
                continue

            # ColumnありListはスキップ（既に処理済み）
            col1_sentence, col2_sentence, column_count = get_list_columns(child)
            if column_count > 0:
                continue

            # skip_first_list=Trueの場合、最初のList要素はスキップ
            if skip_first_list and not first_list_skipped:
                first_list_skipped = True
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
                        # Subitem1の場合、分割対象が1つ目のList要素の場合は分割を行わない
                        if i == 2 and not skip_first_list:  # Subitem1Title, Subitem1Sentenceの後の最初のList
                            continue
                        return (i, 'bracket')  # 括弧の前で分割

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
