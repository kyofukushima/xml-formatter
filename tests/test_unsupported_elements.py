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


XML_WITH_NESTED_LIST = """<?xml version="1.0" encoding="UTF-8"?>
<Law><LawBody><MainProvision><Article Num="1"><Paragraph Num="1">
<ParagraphSentence><Sentence>本文</Sentence></ParagraphSentence>
<List>
  <ListSentence>
    <Column><Sentence>（２）</Sentence></Column>
    <Column><Sentence>異核種</Sentence></Column>
  </ListSentence>
  <List><ListSentence><Sentence>定量法</Sentence></ListSentence></List>
  <List><ListSentence><Sentence>準用する。</Sentence></ListSentence></List>
</List>
<List><ListSentence><Sentence>次の段落</Sentence></ListSentence></List>
</Paragraph></Article></MainProvision></LawBody></Law>
"""


def test_detects_nested_list(tmp_path: Path):
    xml_path = tmp_path / "nested_list.xml"
    xml_path.write_text(XML_WITH_NESTED_LIST, encoding="utf-8")

    found = find_unsupported_elements(xml_path)

    # 外側の List 1件のみ（入れ子側の List や正常な List は報告しない）
    assert len(found) == 1
    assert found[0]["tag"] == _validation.NESTED_LIST_TAG
    assert found[0]["line"] == 4
    assert found[0]["path"].endswith("/Paragraph/List[1]")
    assert "直下に List 2件" in found[0]["detail"]
    assert "9行目〜10行目" in found[0]["detail"]


def test_validate_reports_nested_list_message(tmp_path: Path):
    xml_path = tmp_path / "nested_list.xml"
    xml_path.write_text(XML_WITH_NESTED_LIST, encoding="utf-8")

    is_valid, msg = validate_unsupported_elements(xml_path)

    assert is_valid is False
    assert "1 件" in msg
    assert _validation.NESTED_LIST_TAG in msg
    assert "4行目" in msg
    assert "欠落" in msg


def test_detects_sublist_and_nested_list_together(tmp_path: Path):
    xml = XML_WITH_NESTED_LIST.replace(
        "<List><ListSentence><Sentence>次の段落</Sentence></ListSentence></List>",
        "<List><ListSentence><Sentence>次の段落</Sentence></ListSentence>"
        "<Sublist1><Sublist1Sentence><Sentence>枝</Sentence></Sublist1Sentence></Sublist1></List>")
    xml_path = tmp_path / "both.xml"
    xml_path.write_text(xml, encoding="utf-8")

    found = find_unsupported_elements(xml_path)
    assert [f["tag"] for f in found] == [_validation.NESTED_LIST_TAG, "Sublist1"]

    is_valid, msg = validate_unsupported_elements(xml_path)
    assert is_valid is False
    assert "2 件" in msg
    assert "Sublist1/Sublist2/Sublist3: 1 件" in msg
    assert f"{_validation.NESTED_LIST_TAG}: 1 件" in msg


XML_WITH_MISSING_LIST_OPEN_TAG = """<?xml version="1.0" encoding="UTF-8"?>
<Law><LawBody><MainProvision><Article Num="1"><Paragraph Num="1">
<ParagraphSentence><Sentence>本文</Sentence></ParagraphSentence>
<List>
  <ListSentence>
    <Column><Sentence>（２）</Sentence></Column>
    <Column><Sentence>異核種</Sentence></Column>
  </ListSentence>
  <List><ListSentence><Sentence>定量法</Sentence></ListSentence></List>
  <TableStruct><Table><TableRow><TableColumn><Sentence>表</Sentence></TableColumn></TableRow></Table></TableStruct>
  <ListSentence><Sentence>ｐＨ</Sentence></ListSentence>
</List>
<List><ListSentence><Sentence>６．０～８．０</Sentence></ListSentence></List>
</Paragraph></Article></MainProvision></LawBody></Law>
"""


def test_detects_missing_list_open_tag_pattern(tmp_path: Path):
    """<List> 開始タグ欠落で List 直下に List・TableStruct・2つ目の ListSentence が並ぶケース"""
    xml_path = tmp_path / "missing_open.xml"
    xml_path.write_text(XML_WITH_MISSING_LIST_OPEN_TAG, encoding="utf-8")

    found = find_unsupported_elements(xml_path)
    assert len(found) == 1
    assert found[0]["tag"] == _validation.NESTED_LIST_TAG
    assert found[0]["line"] == 4
    assert "List 1件" in found[0]["detail"]
    assert "TableStruct 1件" in found[0]["detail"]
    assert "ListSentence（2つ目以降） 1件" in found[0]["detail"]
    assert "9行目〜11行目" in found[0]["detail"]

    is_valid, msg = validate_unsupported_elements(xml_path)
    assert is_valid is False
    assert "TableStruct 1件" in msg
