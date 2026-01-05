#!/usr/bin/env python3
"""
項目ラベル判定ユーティリティ

項目ラベル（１、（１）、ア、（ア）等）のパターン判定と
階層レベル判定機能を提供します。

参照: logic2_2_Paragraph_text.md
"""

import re
import json
from enum import Enum
from typing import Tuple, Optional, Dict, List
from pathlib import Path


class LabelPattern(Enum):
    """項目ラベルのパターン（後方互換性のため維持）"""
    GRADE_DOUBLE = "grade_double"                  # 〔第１学年及び第２学年〕
    GRADE_SINGLE = "grade_single"                  # 〔第１学年〕
    SUBJECT_LABEL = "subject_label"                # 〔医療と社会〕
    ARTICLE_BOUNDARY = "article_boundary"          # 第１、第２
    DOUBLE_PAREN_ALPHABET = "double_paren_alphabet"  # （（a））、((a))
    DOUBLE_PAREN_NUMBER = "double_paren_number"    # （（１））、((1))
    DOUBLE_PAREN_KATAKANA = "double_paren_katakana"  # （（ア））、((ア))
    PAREN_ALPHABET = "paren_alphabet"              # （a）、（ａ）
    PAREN_KATAKANA = "paren_katakana"              # （ア）、（イ）
    PAREN_NUMBER = "paren_number"                  # （１）、（２）
    PAREN_ROMAN = "paren_roman"                    # （i）、（ｉ）、（ii）、（ｉｉ）
    CIRCLED_NUMBER = "circled_number"              # ①、②、③
    KATAKANA = "katakana"                          # ア、イ、ウ
    ALPHABET = "alphabet"                          # a、b、A、B
    FULLWIDTH_NUMBER = "fullwidth_number"          # １、２、３
    HALFWIDTH_NUMBER = "halfwidth_number"          # 1、2、3
    KANJI_NUMBER = "kanji_number"                  # 一、二、三
    EMPTY = "empty"                                # （空文字）
    UNKNOWN = "unknown"                            # 不明


class LabelConfig:
    """JSON設定ファイルベースのラベル設定管理クラス"""

    def __init__(self, config_path: Optional[str] = None):
        """
        LabelConfigの初期化

        Args:
            config_path: 設定ファイルのパス（Noneの場合はデフォルトパス）
        """
        if config_path is None:
            # デフォルト設定ファイルパス
            script_dir = Path(__file__).parent.parent
            config_path = script_dir / "config" / "label_config.json"

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"ラベル設定ファイルが見つかりません: {config_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"ラベル設定ファイルのJSON構文エラー: {e}")

        self._build_pattern_cache()

    def _build_pattern_cache(self):
        """正規表現パターンをコンパイルしてキャッシュ"""
        self.pattern_cache: Dict[str, Dict] = {}
        self.pattern_priority: List[str] = self.config.get('pattern_priority', [])

        for label_id, definition in self.config['label_definitions'].items():
            compiled_patterns = []
            for pattern in definition.get('patterns', []):
                try:
                    compiled_patterns.append(re.compile(pattern))
                except re.error as e:
                    raise ValueError(f"無効な正規表現パターン '{pattern}' in {label_id}: {e}")

            self.pattern_cache[label_id] = {
                'patterns': compiled_patterns,
                'definition': definition
            }

    def detect_label_id(self, text: str, exclude_label_ids: Optional[List[str]] = None) -> Optional[str]:
        """
        テキストからラベルIDを判定

        Args:
            text: 判定するテキスト
            exclude_label_ids: 判定から除外するラベルIDのリスト（文脈依存の判定用）

        Returns:
            Optional[str]: ラベルID、見つからない場合はNone
        """
        if text is None:
            return None

        text = text.strip()
        
        if exclude_label_ids is None:
            exclude_label_ids = []

        # 優先順位に従ってパターンマッチング
        for label_id in self.pattern_priority:
            # 除外リストに含まれている場合はスキップ
            if label_id in exclude_label_ids:
                continue
                
            if label_id in self.pattern_cache:
                cache_item = self.pattern_cache[label_id]
                for pattern in cache_item['patterns']:
                    if pattern.match(text):
                        return label_id

        return None


    def get_label_definition(self, label_id: str) -> Optional[Dict]:
        """
        ラベルIDの定義情報を取得

        Args:
            label_id: ラベルID

        Returns:
            Optional[Dict]: ラベル定義情報
        """
        if label_id in self.pattern_cache:
            return self.pattern_cache[label_id]['definition']
        return None

    def is_valid_label_id(self, label_id: str) -> bool:
        """
        有効なラベルIDかどうかを判定

        Args:
            label_id: ラベルID

        Returns:
            bool: 有効な場合はTrue
        """
        return label_id in self.pattern_cache


# グローバル設定インスタンス（遅延初期化）
_label_config: Optional[LabelConfig] = None

def get_label_config() -> LabelConfig:
    """グローバルLabelConfigインスタンスを取得"""
    global _label_config
    if _label_config is None:
        _label_config = LabelConfig()
    return _label_config

def detect_label_id(text: str, exclude_label_ids: Optional[List[str]] = None) -> Optional[str]:
    """
    テキストからラベルIDを判定（JSON設定ベース）

    Args:
        text: 判定するテキスト
        exclude_label_ids: 判定から除外するラベルIDのリスト（文脈依存の判定用）

    Returns:
        Optional[str]: ラベルID、見つからない場合はNone
    """
    return get_label_config().detect_label_id(text, exclude_label_ids)


def is_valid_label_id(label_id: str) -> bool:
    """
    有効なラベルIDかどうかを判定

    Args:
        label_id: ラベルID

    Returns:
        bool: 有効な場合はTrue
    """
    return get_label_config().is_valid_label_id(label_id)


def detect_label_pattern(text: str) -> LabelPattern:
    """
    項目ラベルのパターンを判定（後方互換性のため維持）

    JSON設定ベースの実装を使用し、Enumにマッピングして返します。

    Args:
        text: 判定するテキスト

    Returns:
        LabelPattern: 判定されたパターン
    """
    label_id = detect_label_id(text)
    if label_id is None:
        return LabelPattern.UNKNOWN

    # ラベルIDをLabelPattern Enumにマッピング
    try:
        return LabelPattern(label_id)
    except ValueError:
        return LabelPattern.UNKNOWN


def is_label(text: str) -> bool:
    """
    テキストが項目ラベルかどうかを判定
    
    Args:
        text: 判定するテキスト
        
    Returns:
        bool: 項目ラベルの場合True
        
    Examples:
        >>> is_label("１")
        True
        
        >>> is_label("（ア）")
        True
        
        >>> is_label("これはテキストです")
        False
    """
    label_id = detect_label_id(text)
    if label_id is None:
        return False
    # emptyラベルはFalseを返す
    if label_id == 'empty':
        return False
    # text_non_labelはラベルではないテキストを表すため、Falseを返す
    if label_id == 'text_non_label':
        return False
    return True


def get_alphabet_type(label: str) -> str:
    """
    アルファベットラベルの種類を判定（大文字/小文字、全角/半角、括弧の種類）

    Args:
        label: アルファベットラベル（括弧付きも可）

    Returns:
        str: 'uppercase'（大文字）、'lowercase'（小文字）、'fullwidth_upper'（全角大文字）、'fullwidth_lower'（全角小文字）、
             'paren_uppercase'（括弧大文字）、'paren_lowercase'（括弧小文字）、'fullwidth_paren_upper'（全角括弧大文字）、'fullwidth_paren_lower'（全角括弧小文字）、'unknown'（不明）

    Examples:
        >>> get_alphabet_type("A")
        'uppercase'

        >>> get_alphabet_type("a")
        'lowercase'

        >>> get_alphabet_type("Ａ")
        'fullwidth_upper'

        >>> get_alphabet_type("ａ")
        'fullwidth_lower'

        >>> get_alphabet_type("(A)")
        'paren_uppercase'

        >>> get_alphabet_type("（ａ）")
        'fullwidth_paren_lower'
    """
    if not label:
        return 'unknown'

    label = label.strip()

    # 二重全角括弧付きの場合
    if re.match(r'^（（.+））$', label):
        inner = label[2:-2]
        # 全角大文字アルファベット（Ａ-Ｚ）
        if re.match(r'^[Ａ-Ｚ]+$', inner):
            return 'double_fullwidth_paren_upper'
        # 全角小文字アルファベット（ａ-ｚ）
        if re.match(r'^[ａ-ｚ]+$', inner):
            return 'double_fullwidth_paren_lower'
        # 半角大文字アルファベット（A-Z）
        if re.match(r'^[A-Z]+$', inner):
            return 'double_fullwidth_paren_upper'
        # 半角小文字アルファベット（a-z）
        if re.match(r'^[a-z]+$', inner):
            return 'double_fullwidth_paren_lower'

    # 二重半角括弧付きの場合
    elif re.match(r'^\(\(.+\)\)$', label):
        inner = label[2:-2]
        # 全角大文字アルファベット（Ａ-Ｚ）
        if re.match(r'^[Ａ-Ｚ]+$', inner):
            return 'double_paren_fullwidth_upper'
        # 全角小文字アルファベット（ａ-ｚ）
        if re.match(r'^[ａ-ｚ]+$', inner):
            return 'double_paren_fullwidth_lower'
        # 半角大文字アルファベット（A-Z）
        if re.match(r'^[A-Z]+$', inner):
            return 'double_paren_uppercase'
        # 半角小文字アルファベット（a-z）
        if re.match(r'^[a-z]+$', inner):
            return 'double_paren_lowercase'

    # 全角括弧付きの場合
    elif re.match(r'^（.+）$', label):
        inner = label[1:-1]
        # 全角大文字アルファベット（Ａ-Ｚ）
        if re.match(r'^[Ａ-Ｚ]+$', inner):
            return 'fullwidth_paren_upper'
        # 全角小文字アルファベット（ａ-ｚ）
        if re.match(r'^[ａ-ｚ]+$', inner):
            return 'fullwidth_paren_lower'
        # 半角大文字アルファベット（A-Z）
        if re.match(r'^[A-Z]+$', inner):
            return 'fullwidth_paren_upper'
        # 半角小文字アルファベット（a-z）
        if re.match(r'^[a-z]+$', inner):
            return 'fullwidth_paren_lower'

    # 半角括弧付きの場合
    elif re.match(r'^\(.+\)$', label):
        inner = label[1:-1]
        # 全角大文字アルファベット（Ａ-Ｚ）
        if re.match(r'^[Ａ-Ｚ]+$', inner):
            return 'paren_fullwidth_upper'
        # 全角小文字アルファベット（ａ-ｚ）
        if re.match(r'^[ａ-ｚ]+$', inner):
            return 'paren_fullwidth_lower'
        # 半角大文字アルファベット（A-Z）
        if re.match(r'^[A-Z]+$', inner):
            return 'paren_uppercase'
        # 半角小文字アルファベット（a-z）
        if re.match(r'^[a-z]+$', inner):
            return 'paren_lowercase'

    # 括弧なしの場合
    else:
        # 全角大文字アルファベット（Ａ-Ｚ）
        if re.match(r'^[Ａ-Ｚ]+$', label):
            return 'fullwidth_upper'
        # 全角小文字アルファベット（ａ-ｚ）
        if re.match(r'^[ａ-ｚ]+$', label):
            return 'fullwidth_lower'
        # 半角大文字アルファベット（A-Z）
        if re.match(r'^[A-Z]+$', label):
            return 'uppercase'
        # 半角小文字アルファベット（a-z）
        if re.match(r'^[a-z]+$', label):
            return 'lowercase'

    return 'unknown'


def get_number_type(label: str) -> str:
    """
    数字ラベルの種類を判定（全角/半角/漢数字、括弧の種類を含む）

    Args:
        label: 数字ラベル（括弧付きも可）

    Returns:
        str: 'fullwidth'（全角）、'halfwidth'（半角）、'kanji'（漢数字）、
             'paren_fullwidth'（括弧全角）、'paren_halfwidth'（括弧半角）、'paren_kanji'（括弧漢数字）、
             'double_paren_fullwidth'（二重括弧全角）など

    Examples:
        >>> get_number_type("０")
        'fullwidth'

        >>> get_number_type("1")
        'halfwidth'

        >>> get_number_type("一")
        'kanji'

        >>> get_number_type("(1)")
        'paren_halfwidth'

        >>> get_number_type("（（1））")
        'double_fullwidth_paren_fullwidth'
    """
    if not label:
        return 'unknown'

    label = label.strip()

    # 二重全角括弧付きの場合
    if re.match(r'^（（.+））$', label):
        inner = label[2:-2]
        if re.match(r'^[０-９]+$', inner):
            return 'double_fullwidth_paren_fullwidth'
        if re.match(r'^[0-9]+$', inner):
            return 'double_fullwidth_paren_halfwidth'
        if re.match(r'^[一二三四五六七八九十百千]+$', inner):
            return 'double_fullwidth_paren_kanji'

    # 二重半角括弧付きの場合
    elif re.match(r'^\(\(.+\)\)$', label):
        inner = label[2:-2]
        if re.match(r'^[０-９]+$', inner):
            return 'double_paren_fullwidth'
        if re.match(r'^[0-9]+$', inner):
            return 'double_paren_halfwidth'
        if re.match(r'^[一二三四五六七八九十百千]+$', inner):
            return 'double_paren_kanji'

    # 全角括弧付きの場合
    elif re.match(r'^（.+）$', label):
        inner = label[1:-1]
        if re.match(r'^[０-９]+$', inner):
            return 'fullwidth_paren_fullwidth'
        if re.match(r'^[0-9]+$', inner):
            return 'fullwidth_paren_halfwidth'
        if re.match(r'^[一二三四五六七八九十百千]+$', inner):
            return 'fullwidth_paren_kanji'

    # 半角括弧付きの場合
    elif re.match(r'^\(.+\)$', label):
        inner = label[1:-1]
        if re.match(r'^[０-９]+$', inner):
            return 'paren_fullwidth'
        if re.match(r'^[0-9]+$', inner):
            return 'paren_halfwidth'
        if re.match(r'^[一二三四五六七八九十百千]+$', inner):
            return 'paren_kanji'

    # 括弧なしの場合
    else:
        # 全角数字（０-９）
        if re.match(r'^[０-９]+$', label):
            return 'fullwidth'

        # 半角数字（0-9）
        if re.match(r'^[0-9]+$', label):
            return 'halfwidth'

        # 漢数字（一二三四五六七八九十百千）
        if re.match(r'^[一二三四五六七八九十百千]+$', label):
            return 'kanji'

    return 'unknown'




def split_label_and_content(text: str) -> Tuple[Optional[str], Optional[str]]:
    """
    「ラベル＋スペース＋テキスト」形式の文字列を分離
    
    Args:
        text: 分離する文字列
        
    Returns:
        Tuple[Optional[str], Optional[str]]: (ラベル, テキスト)
        ラベルが見つからない場合は (None, text)
        
    Examples:
        >>> split_label_and_content("１　テキスト")
        ('１', 'テキスト')
        
        >>> split_label_and_content("（ア）　項目アのテキスト")
        ('（ア）', '項目アのテキスト')
        
        >>> split_label_and_content("普通のテキスト")
        (None, '普通のテキスト')
    """
    if not text:
        return (None, None)
    
    text = text.strip()
    
    # 各パターンに対して「ラベル + スペース + 残り」をチェック
    patterns = [
        # 括弧科目名は分離しない（全体が1つのラベル）
        (r'^(〔.+〕)$', False),
        # 第○パターン（通常は単独で使われる）
        (r'^(第[0-9０-９一二三四五六七八九十百千]+)[\s　]+(.+)$', True),
        # 二重括弧カタカナ
        (r'^([（(]{2}[ア-ヴ]+[）)]{2})[\s　]+(.+)$', True),
        # 括弧アルファベット
        (r'^([（(][a-zａ-ｚA-ZＡ-Ｚ]+[）)])[\s　]+(.+)$', True),
        # 括弧カタカナ
        (r'^([（(][ア-ヴ]+[）)])[\s　]+(.+)$', True),
        # 括弧数字
        (r'^([（(][０-９0-9]+[）)])[\s　]+(.+)$', True),
        # 丸数字
        (r'^([①-⑳]+)[\s　]+(.+)$', True),
        # カタカナ
        (r'^([ア-ヴ]+)[\s　]+(.+)$', True),
        # アルファベット
        (r'^([a-zａ-ｚA-ZＡ-Ｚ]+)[\s　]+(.+)$', True),
        # 全角数字
        (r'^([０-９]+)[\s　]+(.+)$', True),
        # 半角数字
        (r'^([0-9]+)[\s　]+(.+)$', True),
        # 漢数字
        (r'^([一二三四五六七八九十百千]+)[\s　]+(.+)$', True),
    ]
    
    for pattern, has_content in patterns:
        match = re.match(pattern, text)
        if match:
            if has_content and len(match.groups()) >= 2:
                return (match.group(1), match.group(2))
            elif not has_content:
                return (match.group(1), None)
    
    # マッチしない場合
    return (None, text)


def is_paragraph_label(label: str) -> bool:
    """
    ラベルがParagraphレベル（数字）かどうかを判定

    Args:
        label: 判定するラベル

    Returns:
        bool: Paragraphレベルの場合True

    Examples:
        >>> is_paragraph_label("１")
        True

        >>> is_paragraph_label("（１）")
        False
    """
    pattern = detect_label_pattern(label)
    return pattern in (LabelPattern.FULLWIDTH_NUMBER, LabelPattern.HALFWIDTH_NUMBER, LabelPattern.KANJI_NUMBER)


def is_item_label(label: str) -> bool:
    """
    ラベルがItemレベル（括弧数字）かどうかを判定
    
    Args:
        label: 判定するラベル
        
    Returns:
        bool: Itemレベルの場合True
        
    Examples:
        >>> is_item_label("（１）")
        True
        
        >>> is_item_label("１")
        False
    """
    pattern = detect_label_pattern(label)
    return pattern == LabelPattern.PAREN_NUMBER


def is_roman_numeral(label: str) -> bool:
    """
    ラベルがローマ数字パターン（^[（(][ivxlcdmｉｖｘｌｃｄｍ]+[）)]$）に合致するかどうかを判定
    
    Args:
        label: 判定するラベル
        
    Returns:
        bool: ローマ数字パターンに合致する場合True
        
    Examples:
        >>> is_roman_numeral("（i）")
        True
        
        >>> is_roman_numeral("（ｉ）")
        True
        
        >>> is_roman_numeral("（ii）")
        True
        
        >>> is_roman_numeral("（ｉｉ）")
        True
        
        >>> is_roman_numeral("（iii）")
        True
        
        >>> is_roman_numeral("（ａ）")
        False
        
        >>> is_roman_numeral("（a）")
        False
    """
    if not label:
        return False
    
    label = label.strip()
    # ローマ数字のパターン: ^[（(][ivxlcdmｉｖｘｌｃｄｍ]+[）)]$
    # paren_romanのパターンと一致
    roman_pattern = re.compile(r'^[（(][ivxlcdmｉｖｘｌｃｄｍ]+[）)]$')
    
    return bool(roman_pattern.match(label))


def get_exclude_label_ids_for_context(first_label: Optional[str]) -> List[str]:
    """
    最初の要素のラベルに基づいて、判定から除外するラベルIDのリストを生成
    
    最初の要素がローマ数字パターン（^[（(][ivxlcdmｉｖｘｌｃｄｍ]+[）)]$）に合致する場合、
    ローマ数字（paren_roman）を除外しない。
    最初の要素がローマ数字でない場合、ローマ数字（paren_roman）を除外リストに追加する。
    これにより、アルファベットとローマ数字の重複を回避できる。
    
    Args:
        first_label: 最初の要素のラベルテキスト（Noneの場合はローマ数字以外として扱い、ローマ数字を除外）
        
    Returns:
        List[str]: 除外するラベルIDのリスト
        
    Examples:
        >>> get_exclude_label_ids_for_context("（i）")
        []
        
        >>> get_exclude_label_ids_for_context("（ｉ）")
        []
        
        >>> get_exclude_label_ids_for_context("（ii）")
        []
        
        >>> get_exclude_label_ids_for_context("（ａ）")
        ['paren_roman']
        
        >>> get_exclude_label_ids_for_context("（a）")
        ['paren_roman']
        
        >>> get_exclude_label_ids_for_context(None)
        ['paren_roman']
    """
    # 最初の要素がない場合もローマ数字以外として扱い、ローマ数字を除外
    if first_label is None:
        return ['paren_roman']
    
    # 最初の要素がローマ数字パターンに合致する場合、ローマ数字を除外しない
    if is_roman_numeral(first_label):
        return []
    
    # 最初の要素がローマ数字でない場合、ローマ数字を除外
    return ['paren_roman']


# テスト用のメイン関数
if __name__ == '__main__':
    """テストケースを実行"""
    print("=" * 60)
    print("項目ラベル判定ユーティリティ - テスト")
    print("=" * 60)
    print()
    
    # テストケース
    test_cases = [
        ("１", LabelPattern.FULLWIDTH_NUMBER, 1),
        ("２", LabelPattern.FULLWIDTH_NUMBER, 1),
        ("10", LabelPattern.HALFWIDTH_NUMBER, 1),
        ("一", LabelPattern.KANJI_NUMBER, 1),
        ("二", LabelPattern.KANJI_NUMBER, 1),
        ("十", LabelPattern.KANJI_NUMBER, 1),
        ("（１）", LabelPattern.PAREN_NUMBER, 2),
        ("(2)", LabelPattern.PAREN_NUMBER, 2),
        ("ア", LabelPattern.KATAKANA, 3),
        ("イ", LabelPattern.KATAKANA, 3),
        ("（ア）", LabelPattern.PAREN_KATAKANA, 4),
        ("(イ)", LabelPattern.PAREN_KATAKANA, 4),
        ("①", LabelPattern.CIRCLED_NUMBER, 4),
        ("②", LabelPattern.CIRCLED_NUMBER, 4),
        ("③", LabelPattern.CIRCLED_NUMBER, 4),
        ("（（ア））", LabelPattern.DOUBLE_PAREN_KATAKANA, 5),
        ("((イ))", LabelPattern.DOUBLE_PAREN_KATAKANA, 5),
        ("a", LabelPattern.ALPHABET, 6),
        ("A", LabelPattern.ALPHABET, 6),
        ("ａ", LabelPattern.ALPHABET, 6),
        ("（a）", LabelPattern.PAREN_ALPHABET, 7),
        ("(ａ)", LabelPattern.PAREN_ALPHABET, 7),
        ("第１", LabelPattern.ARTICLE_BOUNDARY, 0),
        ("第２", LabelPattern.ARTICLE_BOUNDARY, 0),
        ("〔医療と社会〕", LabelPattern.SUBJECT_LABEL, -1),
        ("【医療と社会】", LabelPattern.SUBJECT_LABEL, -1),
        ("［善悪の判断，自律，自由と責任］", LabelPattern.SUBJECT_LABEL, -1),
        ("普通のテキスト", LabelPattern.UNKNOWN, -1),
        ("", LabelPattern.EMPTY, -1),
    ]
    
    all_passed = True
    for i, (label, expected_pattern, expected_level) in enumerate(test_cases, 1):
        pattern = detect_label_pattern(label)
        # Label ID システム移行により階層レベルは使用しないため、常にTrueとする
        level_ok = True
        is_lbl = is_label(label)

        pattern_ok = pattern == expected_pattern
        is_label_ok = is_lbl == (expected_pattern not in (LabelPattern.UNKNOWN, LabelPattern.EMPTY))

        status = "✓" if (pattern_ok and is_label_ok) else "✗"

        if not (pattern_ok and is_label_ok):
            all_passed = False

        print(f"{status} テスト{i}: '{label}'")
        print(f"    パターン: {pattern.value} (期待: {expected_pattern.value}) {'✓' if pattern_ok else '✗'}")
        print(f"    is_label(): {is_lbl} {'✓' if is_label_ok else '✗'}")
    
    print()
    print("=" * 60)
    print("分離テスト")
    print("=" * 60)
    print()
    
    split_test_cases = [
        ("１　テキスト", ("１", "テキスト")),
        ("1　テキスト", ("1", "テキスト")),
        ("一　テキスト", ("一", "テキスト")),
        ("（ア）　項目アのテキスト", ("（ア）", "項目アのテキスト")),
        ("a　項目a", ("a", "項目a")),
        ("普通のテキスト", (None, "普通のテキスト")),
        ("〔医療と社会〕", ("〔医療と社会〕", None)),
    ]
    
    for i, (text, expected) in enumerate(split_test_cases, 1):
        result = split_label_and_content(text)
        status = "✓" if result == expected else "✗"
        print(f"{status} 分離テスト{i}: '{text}'")
        print(f"    結果: {result}")
        print(f"    期待: {expected}")
        if result != expected:
            all_passed = False
    
    print()
    print("=" * 60)
    if all_passed:
        print("✅ 全てのテストが成功しました！")
    else:
        print("❌ 一部のテストが失敗しました")
    print("=" * 60)






