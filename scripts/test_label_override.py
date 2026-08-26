#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ラベル種別の手動オーバーライド（label_overrides）のユニットテスト

- LabelConfig.detect_label_id: オーバーライドが最優先で適用されること
- 無効なオーバーライド（存在しないラベルID）は無視されること
- LABEL_CONFIG_PATH 環境変数による設定ファイル切り替え
- 変換パイプライン（サブプロセス）でのオーバーライド反映（E2E）

背景: ローマ数字の構成文字（c, d 等）を含む括弧アルファベット（ｃ）（ｄ）が、
本物のローマ数字系列（ｉ）（ｉｉ）と共存する文書で paren_roman に誤判定される
問題への対処として、値単位でラベル種別を指定できるようにした。
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from lxml import etree

script_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(script_dir))

import utils.label_utils as label_utils
from utils.label_utils import LabelConfig

DEFAULT_CONFIG_PATH = script_dir / "config" / "label_config.json"


def make_config_file(tmp_path: Path, overrides: dict) -> Path:
    """実際の設定をベースに label_overrides を差し込んだ一時設定ファイルを作成"""
    with open(DEFAULT_CONFIG_PATH, encoding='utf-8') as f:
        config = json.load(f)
    config['label_overrides'] = overrides
    path = tmp_path / "label_config_override.json"
    path.write_text(json.dumps(config, ensure_ascii=False), encoding='utf-8')
    return path


# ============================================================================
# LabelConfig.detect_label_id
# ============================================================================

def test_override_takes_precedence(tmp_path):
    cfg = LabelConfig(str(make_config_file(
        tmp_path, {"（ｃ）": "paren_fullwidth_lowercase_alphabet"})))
    # オーバーライド対象は指定種別になる
    assert cfg.detect_label_id("（ｃ）") == "paren_fullwidth_lowercase_alphabet"
    # 対象外の値は従来どおりパターン判定（（ｄ）はローマ数字が優先）
    assert cfg.detect_label_id("（ｄ）") == "paren_roman"
    assert cfg.detect_label_id("（ａ）") == "paren_fullwidth_lowercase_alphabet"
    assert cfg.detect_label_id("（ｉ）") == "paren_roman"


def test_override_without_config_uses_pattern(tmp_path):
    cfg = LabelConfig(str(make_config_file(tmp_path, {})))
    # オーバーライドなしでは（ｃ）はローマ数字と判定される（従来動作）
    assert cfg.detect_label_id("（ｃ）") == "paren_roman"


def test_override_wins_over_exclude_list(tmp_path):
    cfg = LabelConfig(str(make_config_file(tmp_path, {"（ｘ）": "paren_roman"})))
    # 明示的な指定は文脈依存の除外リストよりも優先される
    assert cfg.detect_label_id("（ｘ）", exclude_label_ids=["paren_roman"]) == "paren_roman"


def test_invalid_override_target_is_ignored(tmp_path):
    cfg = LabelConfig(str(make_config_file(
        tmp_path, {"（ｃ）": "nonexistent_label_id"})))
    # 存在しないラベルIDへの指定は無視され、通常のパターン判定になる
    assert cfg.detect_label_id("（ｃ）") == "paren_roman"


def test_override_value_is_stripped(tmp_path):
    cfg = LabelConfig(str(make_config_file(
        tmp_path, {" （ｃ） ": "paren_fullwidth_lowercase_alphabet"})))
    # 設定側・入力側の前後空白は無視して一致する
    assert cfg.detect_label_id("（ｃ）") == "paren_fullwidth_lowercase_alphabet"


# ============================================================================
# LABEL_CONFIG_PATH 環境変数
# ============================================================================

def test_env_var_config_path(tmp_path, monkeypatch):
    path = make_config_file(tmp_path, {"（ｃ）": "paren_fullwidth_lowercase_alphabet"})
    monkeypatch.setenv('LABEL_CONFIG_PATH', str(path))
    cfg = label_utils.reload_label_config()
    try:
        assert cfg.detect_label_id("（ｃ）") == "paren_fullwidth_lowercase_alphabet"
    finally:
        # グローバルキャッシュを既定設定に戻す（他テストへの影響防止）
        monkeypatch.delenv('LABEL_CONFIG_PATH')
        label_utils.reload_label_config()


# ============================================================================
# E2E: 変換パイプラインでのオーバーライド反映
# ============================================================================

INPUT_XML = """<?xml version="1.0" encoding="UTF-8"?>
<Law>
  <LawBody>
    <Paragraph Num="1">
      <ParagraphNum>1</ParagraphNum>
      <ParagraphSentence>
        <Sentence Num="1">ローマ数字とアルファベットの共存</Sentence>
      </ParagraphSentence>
      {lists}
    </Paragraph>
  </LawBody>
</Law>
"""

LIST_TMPL = """<List>
  <ListSentence>
    <Column Num="1"><Sentence Num="1">{label}</Sentence></Column>
    <Column Num="2"><Sentence Num="1">{body}</Sentence></Column>
  </ListSentence>
</List>"""

LABELS = [
    ("イ", "カタカナイ"),
    ("（ｉ）", "ローマ数字1"),
    ("（ｉｉ）", "ローマ数字2"),
    ("（ａ）", "アルファベットa"),
    ("（ｂ）", "アルファベットb"),
    ("（ｃ）", "アルファベットc"),
]


def run_pipeline(input_path: Path, out_dir: Path, env_extra: dict) -> Path:
    """convert_item_step0 〜 convert_subitem3_step0 を順に実行"""
    env = {**os.environ, **env_extra}
    cur = input_path
    for step in ['convert_item_step0', 'convert_subitem1_step0',
                 'convert_subitem2_step0', 'convert_subitem3_step0']:
        out = out_dir / f"{step}.xml"
        result = subprocess.run(
            [sys.executable, str(script_dir / f"{step}.py"), str(cur), str(out)],
            capture_output=True, text=True, timeout=60, env=env)
        assert result.returncode == 0, f"{step} 失敗: {result.stderr}"
        cur = out
    return cur


def build_input(tmp_path: Path) -> Path:
    lists = "\n".join(LIST_TMPL.format(label=l, body=b) for l, b in LABELS)
    path = tmp_path / "input.xml"
    path.write_text(INPUT_XML.format(lists=lists), encoding='utf-8')
    return path


def titles_by_tag(tree, tag):
    return [e.text for e in tree.iter(tag)]


def test_pipeline_without_override_reproduces_misdetection(tmp_path):
    """オーバーライドなし: （ｃ）はローマ数字と誤判定され（ｉ）と同階層になる"""
    cfg_path = make_config_file(tmp_path, {})
    input_path = build_input(tmp_path)
    out = run_pipeline(input_path, tmp_path, {'LABEL_CONFIG_PATH': str(cfg_path)})
    tree = etree.parse(str(out))
    assert titles_by_tag(tree, 'Subitem1Title') == ['（ｉ）', '（ｉｉ）', '（ｃ）']
    assert titles_by_tag(tree, 'Subitem2Title') == ['（ａ）', '（ｂ）']


def test_pipeline_with_override_fixes_hierarchy(tmp_path):
    """オーバーライドあり: （ｃ）は（ａ）（ｂ）と同階層（兄弟）になる"""
    cfg_path = make_config_file(
        tmp_path, {"（ｃ）": "paren_fullwidth_lowercase_alphabet"})
    input_path = build_input(tmp_path)
    out = run_pipeline(input_path, tmp_path, {'LABEL_CONFIG_PATH': str(cfg_path)})
    tree = etree.parse(str(out))
    assert titles_by_tag(tree, 'Subitem1Title') == ['（ｉ）', '（ｉｉ）']
    assert titles_by_tag(tree, 'Subitem2Title') == ['（ａ）', '（ｂ）', '（ｃ）']
    # （ａ）（ｂ）（ｃ）が同一親の直下に並ぶこと
    parents = {e.getparent().getparent().find('Subitem1Title').text
               for e in tree.iter('Subitem2Title')}
    assert parents == {'（ｉｉ）'}
