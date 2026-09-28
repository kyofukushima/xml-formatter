#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
アップロード時の非対応要素（Sublist1/2/3）検出のユニットテスト
"""

import importlib.util
import sys
import types
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent

# utils/validation.py は streamlit を import するため、未インストール環境向けにダミーを用意
if "streamlit" not in sys.modules:
    try:
        import streamlit  # noqa: F401
    except ImportError:
        sys.modules["streamlit"] = types.ModuleType("streamlit")

# scripts/utils との名前衝突を避けるため、ファイルパスから直接読み込む
_spec = importlib.util.spec_from_file_location(
    "app_validation", project_root / "utils" / "validation.py")
_validation = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_validation)

find_unsupported_elements = _validation.find_unsupported_elements
validate_unsupported_elements = _validation.validate_unsupported_elements


XML_WITH_SUBLIST = """<?xml version="1.0" encoding="UTF-8"?>
<Law><LawBody><MainProvision><Article Num="1"><Paragraph Num="1">
<ParagraphSentence><Sentence>本文</Sentence></ParagraphSentence>
<List>
  <ListSentence><Sentence><ArithFormula>百×Ｚ</ArithFormula></Sentence></ListSentence>
  <Sublist1><Sublist1Sentence>
    <Column><Sentence>（ｉ）</Sentence></Column>
    <Column><Sentence>要件一</Sentence></Column>
  </Sublist1Sentence></Sublist1>
  <Sublist1><Sublist1Sentence>
    <Column><Sentence>（ｉｉ）</Sentence></Column>
    <Column><Sentence>要件二</Sentence></Column>
  </Sublist1Sentence></Sublist1>
</List>
</Paragraph></Article></MainProvision></LawBody></Law>
"""

XML_WITHOUT_SUBLIST = """<?xml version="1.0" encoding="UTF-8"?>
<Law><LawBody><MainProvision><Article Num="1"><Paragraph Num="1">
<ParagraphSentence><Sentence>本文</Sentence></ParagraphSentence>
<List><ListSentence>
  <Column><Sentence>（ｉ）</Sentence></Column>
  <Column><Sentence>要件一</Sentence></Column>
</ListSentence></List>
</Paragraph></Article></MainProvision></LawBody></Law>
"""


def test_detects_sublist_with_line_and_path(tmp_path: Path):
    xml_path = tmp_path / "with_sublist.xml"
    xml_path.write_text(XML_WITH_SUBLIST, encoding="utf-8")

    found = find_unsupported_elements(xml_path)

    assert [f["tag"] for f in found] == ["Sublist1", "Sublist1"]
    assert found[0]["line"] == 6
    assert found[1]["line"] == 10
    assert found[0]["path"].endswith("/List/Sublist1[1]")
    assert found[1]["path"].endswith("/List/Sublist1[2]")


def test_validate_returns_error_message_with_locations(tmp_path: Path):
    xml_path = tmp_path / "with_sublist.xml"
    xml_path.write_text(XML_WITH_SUBLIST, encoding="utf-8")

    is_valid, msg = validate_unsupported_elements(xml_path)

    assert is_valid is False
    assert "Sublist1" in msg
    assert "2 件" in msg
    assert "6行目" in msg
    assert "10行目" in msg


def test_passes_without_sublist(tmp_path: Path):
    xml_path = tmp_path / "ok.xml"
    xml_path.write_text(XML_WITHOUT_SUBLIST, encoding="utf-8")

    assert find_unsupported_elements(xml_path) == []
    assert validate_unsupported_elements(xml_path) == (True, None)


def test_detects_sublist2_and_sublist3(tmp_path: Path):
    xml = XML_WITH_SUBLIST.replace("Sublist1Sentence", "Sublist2Sentence").replace("Sublist1", "Sublist2")
    xml = xml.replace("<Sublist2><Sublist2Sentence>\n    <Column><Sentence>（ｉｉ）",
                      "<Sublist3><Sublist3Sentence>\n    <Column><Sentence>（ｉｉ）", 1)
    xml = xml.replace("要件二</Sentence></Column>\n  </Sublist2Sentence></Sublist2>",
                      "要件二</Sentence></Column>\n  </Sublist3Sentence></Sublist3>", 1)
    xml_path = tmp_path / "mixed.xml"
    xml_path.write_text(xml, encoding="utf-8")

    found = find_unsupported_elements(xml_path)
    assert [f["tag"] for f in found] == ["Sublist2", "Sublist3"]


def test_missing_file(tmp_path: Path):
    is_valid, msg = validate_unsupported_elements(tmp_path / "nope.xml")
    assert is_valid is False
    assert msg
