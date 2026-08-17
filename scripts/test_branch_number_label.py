#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
枝番付き数字ラベル（「一の二」「１の１」「1の2」等）の判定ユニットテスト

- detect_label_id: 枝番付きラベルが枝番なしと同一の label_id に判定されること
- 誤検知防止: 通常のテキストや不完全な形が数字ラベルに判定されないこと
- split_label_and_content: 「ラベル＋スペース＋本文」の分離が枝番付きでも機能すること
"""

import sys
from pathlib import Path

import pytest

script_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(script_dir))

from utils.label_utils import detect_label_id, is_label, split_label_and_content


# ============================================================================
# detect_label_id: 枝番付きラベルの種別判定
# ============================================================================

@pytest.mark.parametrize("text,expected", [
    # 漢数字（枝番なし・従来動作の確認）
    ("一", "kanji_number"),
    ("二", "kanji_number"),
    ("十", "kanji_number"),
    # 漢数字（枝番付き）
    ("一の二", "kanji_number"),
    ("十の二", "kanji_number"),
    ("十三の二", "kanji_number"),
    ("十三の四", "kanji_number"),
    # 多段の枝番（第○条の二の三 相当）
    ("二の三の四", "kanji_number"),
    # カタカナ「ノ」区切り（renumber_utils と同仕様）
    ("十ノ二", "kanji_number"),
    # 全角数字
    ("１", "fullwidth_number"),
    ("２", "fullwidth_number"),
    ("１の１", "fullwidth_number"),
    ("１３の２", "fullwidth_number"),
    # 半角数字
    ("1", "halfwidth_number"),
    ("1の2", "halfwidth_number"),
    ("13の2", "halfwidth_number"),
])
def test_branch_number_label_id(text, expected):
    assert detect_label_id(text) == expected


@pytest.mark.parametrize("text", [
    "一の二",
    "十三の四",
    "１の１",
    "1の2",
])
def test_branch_number_is_label(text):
    assert is_label(text)


# ============================================================================
# 誤検知防止: 数字ラベルに判定されてはいけないもの
# ============================================================================

@pytest.mark.parametrize("text", [
    "子の養育",   # 通常のテキスト
    "千の",       # 「の」の後に数字がない
    "の二",       # 「の」で始まる
    "一の２",     # 種別の混在（漢数字＋全角数字）は対象外
    "１の1",      # 種別の混在（全角＋半角）は対象外
])
def test_non_branch_number_not_number_label(text):
    label_id = detect_label_id(text)
    assert label_id not in ("kanji_number", "fullwidth_number", "halfwidth_number"), \
        f"{text!r} が {label_id} に誤判定された"


# ============================================================================
# split_label_and_content: ラベルと本文の分離
# ============================================================================

@pytest.mark.parametrize("text,expected", [
    ("一の二　テキスト", ("一の二", "テキスト")),
    ("十三の四　テキスト", ("十三の四", "テキスト")),
    ("１の１　テキスト", ("１の１", "テキスト")),
    ("1の2 テキスト", ("1の2", "テキスト")),
    # 従来動作の確認（枝番なし）
    ("一　テキスト", ("一", "テキスト")),
    ("１　テキスト", ("１", "テキスト")),
    # 「の」の後が数字でない場合はラベル部を最小に保つ（従来同様マッチしない）
    ("二の　テキスト", (None, "二の　テキスト")),
])
def test_split_label_and_content_with_branch(text, expected):
    assert split_label_and_content(text) == expected
