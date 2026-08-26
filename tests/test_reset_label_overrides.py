#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
アプリ起動時の手動指定リセット（reset_label_overrides）のユニットテスト
"""

import importlib.util
import json
from pathlib import Path

# scripts/utils との名前衝突を避けるため、config_managerをファイルパスから直接読み込む
project_root = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location(
    "app_config_manager", project_root / "utils" / "config_manager.py")
_config_manager = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_config_manager)

reset_label_overrides = _config_manager.reset_label_overrides
get_label_overrides = _config_manager.get_label_overrides


def make_config(tmp_path: Path, overrides) -> Path:
    config = {
        "version": "1.0",
        "label_definitions": {
            "paren_fullwidth_lowercase_alphabet": {
                "id": "paren_fullwidth_lowercase_alphabet",
                "name": "括弧全角小文字アルファベット",
                "patterns": ["^[（(][ａ-ｚ]+[）)]$"],
            }
        },
        "pattern_priority": ["paren_fullwidth_lowercase_alphabet"],
        "label_overrides": overrides,
    }
    path = tmp_path / "label_config.json"
    path.write_text(json.dumps(config, ensure_ascii=False), encoding='utf-8')
    return path


def test_reset_clears_overrides(tmp_path):
    path = make_config(tmp_path, {"（ｃ）": "paren_fullwidth_lowercase_alphabet"})
    assert reset_label_overrides(path) is True
    with open(path, encoding='utf-8') as f:
        config = json.load(f)
    assert config['label_overrides'] == {}
    # 他のセクションは保持される
    assert 'paren_fullwidth_lowercase_alphabet' in config['label_definitions']


def test_reset_noop_when_already_empty(tmp_path):
    path = make_config(tmp_path, {})
    before = path.read_text(encoding='utf-8')
    assert reset_label_overrides(path) is False
    # 変更なし（ファイルは書き換えられない）
    assert path.read_text(encoding='utf-8') == before


def test_reset_missing_file_returns_false(tmp_path):
    assert reset_label_overrides(tmp_path / "nonexistent.json") is False


def test_get_label_overrides_helper():
    assert get_label_overrides({}) == {}
    assert get_label_overrides({'label_overrides': None}) == {}
    assert get_label_overrides({'label_overrides': {'（ｃ）': 'x'}}) == {'（ｃ）': 'x'}
