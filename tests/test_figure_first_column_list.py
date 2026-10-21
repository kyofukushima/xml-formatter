#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
1つ目のColumnが数式画像（QuoteStruct/Fig）のみでテキストを持たない2列Listの変換テスト

液化ガスばら積船の貨物タンク等の技術基準（昭和61年運輸省告示第298号）第十二条で、
「[数式画像] | （メガパスカル）」の List が空の Subitem に置き換わり、図と単位の
テキストが欠落した事象の回帰テスト。
"""

import subprocess
import sys
from pathlib import Path

import pytest
from lxml import etree

project_root = Path(__file__).resolve().parent.parent
SCRIPTS = project_root / "scripts"

XML = """<?xml version="1.0" encoding="UTF-8"?>
<Law><LawBody><MainProvision><Article Num="12"><Paragraph Num="1">
<ParagraphNum/>
<ParagraphSentence><Sentence>貨物タンクの設計荷重は、次のとおりとする。</Sentence></ParagraphSentence>
<Item Num="1">
  <ItemTitle>一</ItemTitle>
  <ItemSentence><Sentence>内圧荷重</Sentence></ItemSentence>
  <List><ListSentence>
    <Column Num="1"><Sentence><ArithFormula>Ｐ＋ｐ</ArithFormula></Sentence></Column>
    <Column Num="2"><Sentence>（メガパスカル）</Sentence></Column>
  </ListSentence></List>
  <List><ListSentence><Sentence>Ｐは、設計ガス圧</Sentence></ListSentence></List>
  <List><ListSentence>
    <Column Num="1"><Sentence><QuoteStruct><Fig src="./pict/formula.jpg"/></QuoteStruct></Sentence></Column>
    <Column Num="2"><Sentence>（メガパスカル）</Sentence></Column>
  </ListSentence></List>
  <List><ListSentence><Sentence>ａは、加速度の無次元数</Sentence></ListSentence></List>
</Item>
</Paragraph></Article></MainProvision></LawBody></Law>
"""


def run_script(script_name, input_xml, tmp_path, extra_args=None):
    in_file = tmp_path / "input.xml"
    out_file = tmp_path / "output.xml"
    in_file.write_text(input_xml, encoding="utf-8")
    cmd = [sys.executable, str(SCRIPTS / script_name), str(in_file), str(out_file)] + (extra_args or [])
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    assert result.returncode == 0, result.stderr
    return etree.parse(str(out_file))


def _texts(tree):
    return [t.strip() for t in tree.getroot().itertext() if t.strip()]


@pytest.mark.parametrize("extra_args", [
    [],
    ["--merge-no-column-lists"],
    ["--preserve-linebreak-list", "--merge-no-column-lists", "--preserve-lists-after-struct"],
])
def test_figure_first_column_list_is_not_dropped(tmp_path, extra_args):
    tree = run_script("convert_subitem1_step0.py", XML, tmp_path, extra_args)
    figs = [f.get("src") for f in tree.getroot().iter("Fig")]
    assert figs == ["./pict/formula.jpg"]
    texts = _texts(tree)
    assert texts.count("（メガパスカル）") == 2
    # 順序: 数式 → 単位 → Ｐ → 画像 → 単位 → ａ
    order = [t for t in texts if t in ("Ｐ＋ｐ", "（メガパスカル）", "Ｐは、設計ガス圧", "ａは、加速度の無次元数")]
    assert order == ["Ｐ＋ｐ", "（メガパスカル）", "Ｐは、設計ガス圧", "（メガパスカル）", "ａは、加速度の無次元数"]
    # 空の Sentence が作られていない
    item = tree.getroot().find(".//Item")
    empties = [s for s in item.iter("Sentence") if not "".join(s.itertext()).strip() and len(s) == 0]
    assert empties == []


def test_figure_first_column_becomes_text_first_columns(tmp_path):
    # subitem1 段階では前の要素の子 List として保持され、subitem2 段階で Column 付き要素になる
    tree1 = run_script("convert_subitem1_step0.py", XML, tmp_path)
    assert tree1.getroot().find(".//List//Fig") is not None
    tree2 = run_script("convert_subitem2_step0.py", etree.tostring(tree1, encoding="unicode"), tmp_path)
    holder = next(e for e in tree2.getroot().iter("Subitem2") if e.find(".//Fig") is not None)
    assert "".join(holder.find("Subitem2Title").itertext()) == ""
    cols = holder.find("Subitem2Sentence").findall("Column")
    assert len(cols) == 2
    assert cols[0].find(".//Fig") is not None
    assert "".join(cols[1].itertext()).strip() == "（メガパスカル）"
    # 空の Sentence が作られていない
    empties = [x for x in tree2.getroot().iter("Sentence") if not "".join(x.itertext()).strip() and len(x) == 0]
    assert empties == []
