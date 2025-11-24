#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
括弧関連ユーティリティ関数

括弧付きテキストの判定を行う共通関数群
"""

import re


def is_subject_name_bracket(text: str) -> bool:
    """
    テキストが括弧付き科目名かチェック（〔...〕、【...】、または［...］）

    Args:
        text (str): 判定対象のテキスト

    Returns:
        bool: 科目名括弧の場合True、そうでない場合False

    Examples:
        >>> is_subject_name_bracket('〔医療と社会〕')
        True
        >>> is_subject_name_bracket('【医療と社会】')
        True
        >>> is_subject_name_bracket('［善悪の判断，自律，自由と責任］')
        True
        >>> is_subject_name_bracket('〔指導項目〕')
        False
        >>> is_subject_name_bracket('〔指導項目〕の（１）...')
        False
    """
    if not text:
        return False
    text = text.strip()
    return bool(re.match(r'^[〔【［].+[〕】］]$', text) and '指導項目' not in text)


def is_instruction_bracket(text: str) -> bool:
    """
    テキストが括弧付き指導項目かチェック（〔指導項目〕または【指導項目】）

    Args:
        text (str): 判定対象のテキスト

    Returns:
        bool: 指導項目括弧の場合True、そうでない場合False

    Examples:
        >>> is_instruction_bracket('〔指導項目〕')
        True
        >>> is_instruction_bracket('【指導項目】')
        True
        >>> is_instruction_bracket('〔医療と社会〕')
        False
    """
    if not text:
        return False
    text = text.strip()
    return text in ['〔指導項目〕', '【指導項目】']


def is_grade_single_bracket(text: str) -> bool:
    """
    テキストが括弧付き学年（1つ記載）かチェック（〔第１学年〕等）

    Args:
        text (str): 判定対象のテキスト

    Returns:
        bool: 学年（1つ）括弧の場合True、そうでない場合False

    Examples:
        >>> is_grade_single_bracket('〔第１学年〕')
        True
        >>> is_grade_single_bracket('〔第２学年〕')
        True
        >>> is_grade_single_bracket('〔第１学年及び第２学年〕')
        False
        >>> is_grade_single_bracket('〔医療と社会〕')
        False
    """
    if not text:
        return False
    text = text.strip()
    return bool(re.match(r'^〔第[1-6１-６]学年〕$', text))


def is_grade_double_bracket(text: str) -> bool:
    """
    テキストが括弧付き学年（2つ記載）かチェック（〔第１学年及び第２学年〕等）

    Args:
        text (str): 判定対象のテキスト

    Returns:
        bool: 学年（2つ）括弧の場合True、そうでない場合False

    Examples:
        >>> is_grade_double_bracket('〔第１学年及び第２学年〕')
        True
        >>> is_grade_double_bracket('〔第３学年及び第４学年〕')
        True
        >>> is_grade_double_bracket('〔第１学年〕')
        False
        >>> is_grade_double_bracket('〔医療と社会〕')
        False
    """
    if not text:
        return False
    text = text.strip()
    return bool(re.match(r'^〔第[1-6１-６]学年及び第[1-6１-６]学年〕$', text))
