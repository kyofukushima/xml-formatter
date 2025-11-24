#!/usr/bin/env python3
"""
項目ラベル判定ユーティリティ

項目ラベル（１、（１）、ア、（ア）等）のパターン判定と
階層レベル判定機能を提供します。

参照: logic2_2_Paragraph_text.md
"""

import re
from enum import Enum
from typing import Tuple, Optional


class LabelPattern(Enum):
    """項目ラベルのパターン"""
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
    CIRCLED_NUMBER = "circled_number"              # ①、②、③
    KATAKANA = "katakana"                          # ア、イ、ウ
    ALPHABET = "alphabet"                          # a、b、A、B
    NUMBER = "number"                              # １、２、３、一、二、三
    EMPTY = "empty"                                # （空文字）
    UNKNOWN = "unknown"                            # 不明


def detect_label_pattern(text: str) -> LabelPattern:
    """
    項目ラベルのパターンを判定
    
    logic2_2_Paragraph_text.mdの「パターン判定の優先順位」に従って判定します。
    
    Args:
        text: 判定するテキスト
        
    Returns:
        LabelPattern: 判定されたパターン
        
    Examples:
        >>> detect_label_pattern("１")
        LabelPattern.NUMBER
        
        >>> detect_label_pattern("（１）")
        LabelPattern.PAREN_NUMBER
        
        >>> detect_label_pattern("ア")
        LabelPattern.KATAKANA
        
        >>> detect_label_pattern("①")
        LabelPattern.CIRCLED_NUMBER
        
        >>> detect_label_pattern("〔医療と社会〕")
        LabelPattern.SUBJECT_LABEL
    """
    if text is None:
        return LabelPattern.UNKNOWN
    
    text = text.strip()
    
    # 空文字
    if text == '':
        return LabelPattern.EMPTY
    
    # 優先順位順にチェック（logic2_2_Paragraph_text.md の順序）

    # 1. 学年パターン（2つ記載）（最優先）
    if re.match(r'^〔第[1-6１-６]学年及び第[1-6１-６]学年〕$', text):
        return LabelPattern.GRADE_DOUBLE

    # 2. 学年パターン（1つ記載）
    if re.match(r'^〔第[1-6１-６]学年〕$', text):
        return LabelPattern.GRADE_SINGLE

    # 3. 括弧科目名
    if re.match(r'^[〔【［].+[〕】］]$', text):
        return LabelPattern.SUBJECT_LABEL
    
    # 2. 第○パターン（Article分割）
    if re.match(r'^第[0-9０-９一二三四五六七八九十百千]+$', text):
        return LabelPattern.ARTICLE_BOUNDARY
    
    # 3. 二重括弧アルファベット
    if re.match(r'^[（(]{2}[a-zａ-ｚA-ZＡ-Ｚ]+[）)]{2}$', text):
        return LabelPattern.DOUBLE_PAREN_ALPHABET

    # 4. 二重括弧数字
    if re.match(r'^[（(]{2}[０-９0-9一二三四五六七八九十百千]+[）)]{2}$', text):
        return LabelPattern.DOUBLE_PAREN_NUMBER

    # 5. 二重括弧カタカナ
    if re.match(r'^[（(]{2}[ア-ヴ]+[）)]{2}$', text):
        return LabelPattern.DOUBLE_PAREN_KATAKANA

    # 6. 括弧アルファベット（全角・半角、小文字・大文字）
    if re.match(r'^[（(][a-zａ-ｚA-ZＡ-Ｚ]+[）)]$', text):
        return LabelPattern.PAREN_ALPHABET
    
    # 5. 括弧カタカナ
    if re.match(r'^[（(][ア-ヴ]+[）)]$', text):
        return LabelPattern.PAREN_KATAKANA
    
    # 6. 括弧数字（全角・半角・漢数字）
    if re.match(r'^[（(][０-９0-9一二三四五六七八九十百千]+[）)]$', text):
        return LabelPattern.PAREN_NUMBER
    
    # 7. 丸数字（①-⑳）
    if re.match(r'^[①-⑳]+$', text):
        return LabelPattern.CIRCLED_NUMBER
    
    # 8. カタカナ（括弧なし）
    if re.match(r'^[ア-ヴ]+$', text):
        return LabelPattern.KATAKANA
    
    # 9. アルファベット（括弧なし、全角・半角、小文字・大文字）
    if re.match(r'^[a-zａ-ｚA-ZＡ-Ｚ]+$', text):
        return LabelPattern.ALPHABET
    
    # 10. 数字（括弧なし、全角・半角・漢数字）
    if re.match(r'^[０-９0-9一二三四五六七八九十百千]+$', text):
        return LabelPattern.NUMBER
    
    # 11. マッチしない場合
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
    pattern = detect_label_pattern(text)
    return pattern not in (LabelPattern.UNKNOWN, LabelPattern.EMPTY)


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


def get_hierarchy_level(label: str) -> int:
    """
    項目ラベルの階層レベルを取得
    
    logic2_2_Paragraph_text.mdの「階層レベルの順序」に従います。
    
    Args:
        label: 項目ラベル
        
    Returns:
        int: 階層レベル（0-7）、不明な場合は-1
        
    階層レベル:
        0: 第○パターン（Article分割）
        1: 数字（Paragraph / Item）
        2: 括弧数字（Item / Subitem1）
        3: カタカナ（Subitem1 / Subitem2）
        4: 括弧カタカナ（Subitem2 / Subitem3）
        4: 丸数字（Subitem3レベル）
        5: 二重括弧カタカナ（Subitem3 / Subitem4）
        6: アルファベット（Subitem3以降）
        7: 括弧アルファベット（Subitem4以降）
        
    Examples:
        >>> get_hierarchy_level("１")
        1
        
        >>> get_hierarchy_level("（１）")
        2
        
        >>> get_hierarchy_level("ア")
        3
    """
    pattern = detect_label_pattern(label)
    
    hierarchy_map = {
        LabelPattern.ARTICLE_BOUNDARY: 0,
        LabelPattern.NUMBER: 1,
        LabelPattern.PAREN_NUMBER: 2,
        LabelPattern.KATAKANA: 3,
        LabelPattern.PAREN_KATAKANA: 4,
        LabelPattern.CIRCLED_NUMBER: 4,  # Subitem3レベル（括弧カタカナと同じ階層）
        LabelPattern.DOUBLE_PAREN_KATAKANA: 5,
        LabelPattern.ALPHABET: 6,
        LabelPattern.PAREN_ALPHABET: 7,
    }
    
    return hierarchy_map.get(pattern, -1)


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
        # 数字
        (r'^([０-９0-9一二三四五六七八九十百千]+)[\s　]+(.+)$', True),
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
    return pattern == LabelPattern.NUMBER


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


# テスト用のメイン関数
if __name__ == '__main__':
    """テストケースを実行"""
    print("=" * 60)
    print("項目ラベル判定ユーティリティ - テスト")
    print("=" * 60)
    print()
    
    # テストケース
    test_cases = [
        ("１", LabelPattern.NUMBER, 1),
        ("２", LabelPattern.NUMBER, 1),
        ("10", LabelPattern.NUMBER, 1),
        ("一", LabelPattern.NUMBER, 1),
        ("二", LabelPattern.NUMBER, 1),
        ("十", LabelPattern.NUMBER, 1),
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
        level = get_hierarchy_level(label)
        is_lbl = is_label(label)
        
        pattern_ok = pattern == expected_pattern
        level_ok = level == expected_level
        is_label_ok = is_lbl == (expected_pattern not in (LabelPattern.UNKNOWN, LabelPattern.EMPTY))
        
        status = "✓" if (pattern_ok and level_ok and is_label_ok) else "✗"
        
        if not (pattern_ok and level_ok and is_label_ok):
            all_passed = False
        
        print(f"{status} テスト{i}: '{label}'")
        print(f"    パターン: {pattern.value} (期待: {expected_pattern.value}) {'✓' if pattern_ok else '✗'}")
        print(f"    階層レベル: {level} (期待: {expected_level}) {'✓' if level_ok else '✗'}")
        print(f"    is_label(): {is_lbl} {'✓' if is_label_ok else '✗'}")
    
    print()
    print("=" * 60)
    print("分離テスト")
    print("=" * 60)
    print()
    
    split_test_cases = [
        ("１　テキスト", ("１", "テキスト")),
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






