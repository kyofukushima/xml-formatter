#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
括弧関連ユーティリティ関数

括弧付きテキストの判定を行う共通関数群
"""

import re
import json
from pathlib import Path
from typing import Optional


def is_subject_name_bracket(text: str) -> bool:
    """
    テキストが括弧付き科目名かチェック（label_config.jsonのsubject_labelパターンを使用）

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
        >>> is_subject_name_bracket('（相談窓口の担当者が適切に対応することができるようにしていると認められる例）')
        True
        >>> is_subject_name_bracket('〔指導項目〕')
        False
        >>> is_subject_name_bracket('〔指導項目〕の（１）...')
        False
    """
    if not text:
        return False
    text = text.strip()

    # label_config.jsonからsubject_labelパターンを読み込む
    config_path = Path(__file__).parent.parent / "config" / "label_config.json"
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        subject_label = config.get('label_definitions', {}).get('subject_label', {})
        patterns = subject_label.get('patterns', [])

        for pattern in patterns:
            if re.match(pattern, text):
                # 「指導項目」が含まれないことを確認
                return '指導項目' not in text

        return False

    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        # 設定ファイルが見つからない場合のフォールバック（従来のロジック）
        return bool(re.match(r'^[〔【［].+[〕】］]$', text) and '指導項目' not in text)


def is_instruction_bracket(text: str) -> bool:
    """
    テキストが括弧付き指導項目かチェック（label_config.jsonのinstructionパターンを使用）

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

    # label_config.jsonからinstructionパターンを読み込む
    config_path = Path(__file__).parent.parent / "config" / "label_config.json"
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        instruction_label = config.get('label_definitions', {}).get('instruction', {})
        patterns = instruction_label.get('patterns', [])

        for pattern in patterns:
            if re.match(pattern, text):
                return True

        return False

    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        # 設定ファイルが見つからない場合のフォールバック（従来のロジック）
        return text in ['〔指導項目〕', '【指導項目】']


def is_grade_single_bracket(text: str) -> bool:
    """
    テキストが括弧付き学年（1つ記載）かチェック（label_config.jsonのgrade_singleパターンを使用）

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

    # label_config.jsonからgrade_singleパターンを読み込む
    config_path = Path(__file__).parent.parent / "config" / "label_config.json"
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        grade_single_label = config.get('label_definitions', {}).get('grade_single', {})
        patterns = grade_single_label.get('patterns', [])

        for pattern in patterns:
            if re.match(pattern, text):
                return True

        return False

    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        # 設定ファイルが見つからない場合のフォールバック（従来のロジック）
        return bool(re.match(r'^〔第[1-6１-６]学年〕$', text))


def is_grade_double_bracket(text: str) -> bool:
    """
    テキストが括弧付き学年（2つ記載）かチェック（label_config.jsonのgrade_doubleパターンを使用）

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

    # label_config.jsonからgrade_doubleパターンを読み込む
    config_path = Path(__file__).parent.parent / "config" / "label_config.json"
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        grade_double_label = config.get('label_definitions', {}).get('grade_double', {})
        patterns = grade_double_label.get('patterns', [])

        for pattern in patterns:
            if re.match(pattern, text):
                return True

        return False

    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        # 設定ファイルが見つからない場合のフォールバック（従来のロジック）
        return bool(re.match(r'^〔第[1-6１-６]学年及び第[1-6１-６]学年〕$', text))


def get_bracket_type(text: str) -> Optional[str]:
    """
    括弧の種類を返す（label_config.jsonから読み込む）
    
    Args:
        text (str): 判定対象のテキスト
    
    Returns:
        'subject_label_square': 〔〕で囲まれている
        'subject_label_double_square': 【】で囲まれている
        'subject_label_corner': ［］で囲まれている
        'subject_label_round': （）で囲まれている
        None: 該当する括弧タイプがない
    """
    if not text:
        return None
    text = text.strip()
    
    # 「指導項目」が含まれている場合は除外
    if '指導項目' in text:
        return None
    
    # label_config.jsonから各括弧タイプのパターンを読み込む
    config_path = Path(__file__).parent.parent / "config" / "label_config.json"
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        label_definitions = config.get('label_definitions', {})
        
        # 優先順位に従ってチェック（pattern_priorityの順序）
        pattern_priority = config.get('pattern_priority', [])
        
        for label_id in pattern_priority:
            if label_id not in ['subject_label_square', 'subject_label_double_square', 
                               'subject_label_corner', 'subject_label_round']:
                continue
                
            label_def = label_definitions.get(label_id, {})
            patterns = label_def.get('patterns', [])
            
            for pattern in patterns:
                if re.match(pattern, text):
                    return label_id
        
        return None
        
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        # 設定ファイルが見つからない場合のフォールバック
        if re.match(r'^〔.+〕$', text):
            return 'subject_label_square'
        elif re.match(r'^【.+】$', text):
            return 'subject_label_double_square'
        elif re.match(r'^［.+］$', text):
            return 'subject_label_corner'
        elif re.match(r'^[（(].+[）)]$', text):
            return 'subject_label_round'
        return None
