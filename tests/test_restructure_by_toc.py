#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
scripts/restructure_by_toc.py（目次に合わせた章節構造への組み直し）のユニットテスト
"""

import importlib.util
import sys
from pathlib import Path

from lxml import etree

project_root = Path(__file__).resolve().parent.parent


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, project_root / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


restructure_mod = _load("restructure_by_toc", "scripts/restructure_by_toc.py")
schema_mod = _load("validate_kokuji_schema", "scripts/validate_kokuji_schema.py")


SAMPLE = """<?xml version="1.0" encoding="UTF-8"?>
<Law Era="Heisei" Lang="ja" LawType="Misc" Num="1" Year="25">
  <LawNum>平成二十五年告示第一号</LawNum>
  <LawBody>
    <LawTitle>試験基準</LawTitle>
    <TOC>
      <TOCLabel>目次</TOCLabel>
      <TOCChapter Num="1"><ChapterTitle>第１　通則</ChapterTitle></TOCChapter>
      <TOCChapter Num="2">
        <ChapterTitle>第２　各条</ChapterTitle>
        <TOCSection Num="1"><SectionTitle>１　甲（<Sup>１８</Sup>Ｆ）注射液</SectionTitle></TOCSection>
        <TOCSection Num="2"><SectionTitle>２　乙注射液</SectionTitle></TOCSection>
      </TOCChapter>
    </TOC>
    <MainProvision>
      <Article Num="1">
        <ArticleTitle>第１</ArticleTitle>
        <Paragraph Num="1">
          <ParagraphNum/>
          <ParagraphSentence><Sentence>通則</Sentence></ParagraphSentence>
          <List><ListSentence><Column><Sentence>１</Sentence></Column><Column><Sentence>一番目の規定。</Sentence></Column></ListSentence></List>
          <List><ListSentence><Sentence>続きの段落。</Sentence></ListSentence></List>
          <List><ListSentence><Column><Sentence>（１）</Sentence></Column><Column><Sentence>細目一</Sentence></Column></ListSentence></List>
          <List><ListSentence><Column><Sentence>（２）</Sentence></Column><Column><Sentence>細目二</Sentence></Column></ListSentence></List>
          <List><ListSentence><Column><Sentence>２</Sentence></Column><Column><Sentence>単位は次による。</Sentence></Column></ListSentence></List>
          <List><ListSentence><Column><Sentence>メートル</Sentence></Column><Column><Sentence>ｍ</Sentence></Column></ListSentence></List>
          <List><ListSentence><Column><Sentence>グラム</Sentence></Column><Column><Sentence>ｇ</Sentence></Column></ListSentence></List>
        </Paragraph>
      </Article>
      <Article Num="2">
        <ArticleTitle>第２</ArticleTitle>
        <Paragraph Num="1">
          <ParagraphNum/>
          <ParagraphSentence><Sentence/></ParagraphSentence>
          <List><ListSentence><Sentence>各条</Sentence></ListSentence></List>
          <List><ListSentence><Column><Sentence>１</Sentence></Column><Column><Sentence>甲（<Sup>１８</Sup>Ｆ）注射液</Sentence></Column></ListSentence></List>
          <List><ListSentence><Sentence>本品は、注射剤である。</Sentence></ListSentence></List>
          <List><ListSentence><Sentence>製法</Sentence></ListSentence></List>
          <List><ListSentence><Sentence>本品は、精製して製する。</Sentence></ListSentence></List>
          <List><ListSentence><Sentence>純度試験</Sentence></ListSentence></List>
          <List><ListSentence><Column><Sentence>（１）</Sentence></Column><Column><Sentence>異物　試験を行う。</Sentence></Column></ListSentence></List>
          <List><ListSentence><Sentence>なお、薄層板を用いる。</Sentence></ListSentence></List>
          <List><ListSentence><Sentence>試験条件</Sentence></ListSentence></List>
          <List><ListSentence><Sentence>検出器：紫外吸光光度計</Sentence></ListSentence></List>
          <TableStruct><Table><TableRow><TableColumn><Sentence>表</Sentence></TableColumn></TableRow></Table></TableStruct>
          <List><ListSentence><Sentence>流量：毎分１ｍＬ</Sentence></ListSentence></List>
          <List><ListSentence><Column><Sentence>（２）</Sentence></Column><Column><Sentence>異核種　認めない。</Sentence></Column></ListSentence></List>
          <List><ListSentence><Sentence>定量法</Sentence></ListSentence></List>
          <List><ListSentence><Sentence>放射能を測定する。</Sentence></ListSentence></List>
          <List><ListSentence><Column><Sentence>２</Sentence></Column><Column><Sentence>乙注射液</Sentence></Column></ListSentence></List>
          <List><ListSentence><Sentence>本品は、乙を含む。</Sentence></ListSentence></List>
        </Paragraph>
      </Article>
    </MainProvision>
  </LawBody>
</Law>
"""


def _run(xml_text: str, tmp_path: Path):
    src = tmp_path / "in.xml"
    src.write_text(xml_text, encoding="utf-8")
    tree = etree.parse(str(src))
    report, stats = [], {}
    restructure_mod.restructure(tree, report, stats)
    restructure_mod.indent(tree.getroot())
    out = tmp_path / "out.xml"
    tree.write(str(out), encoding="UTF-8", xml_declaration=True)
    return etree.parse(str(out)).getroot(), report, stats


def _text(e):
    return "".join(e.itertext()).strip()


def test_chapters_and_sections_follow_toc(tmp_path: Path):
    root, report, stats = _run(SAMPLE, tmp_path)
    mp = root.find(".//MainProvision")
    chapters = mp.findall("Chapter")
    assert [c.get("Num") for c in chapters] == ["1", "2"]
    assert _text(chapters[0].find("ChapterTitle")) == "第１　通則"
    assert _text(chapters[1].find("ChapterTitle")) == "第２　各条"
    sections = chapters[1].findall("Section")
    assert [_text(s.find("SectionTitle")) for s in sections] == ["１　甲（１８Ｆ）注射液", "２　乙注射液"]
    # 本則側の見出しのインライン要素（Sup）を Title に保持する
    assert sections[0].find("SectionTitle/Sup") is not None
    # 章直下に本文が無いので Article は作らない
    assert chapters[1].find("Article") is None
    assert sections[0].find("Article/ArticleTitle") is not None


def test_item_hierarchy_in_general_rules(tmp_path: Path):
    root, _, _ = _run(SAMPLE, tmp_path)
    para = root.find(".//Chapter[@Num='1']/Article/Paragraph")
    assert _text(para.find("ParagraphSentence")) == ""
    items = para.findall("Item")
    assert [_text(i.find("ItemTitle")) for i in items] == ["１", "２"]
    # ラベル付き要素の続きの段落は LineBreak 付き Column
    cols = items[0].find("ItemSentence").findall("Column")
    assert [_text(c) for c in cols] == ["一番目の規定。", "続きの段落。"]
    assert cols[1].get("LineBreak") == "true"
    # （１）（２）は １ の子、同種ラベルは兄弟
    subs = items[0].findall("Subitem1")
    assert [_text(s.find("Subitem1Title")) for s in subs] == ["（１）", "（２）"]
    # ラベルでない複数 Column は Title 空の子要素に Column のまま格納
    terms = items[1].findall("Subitem1")
    assert len(terms) == 2
    assert _text(terms[0].find("Subitem1Title")) == ""
    assert [_text(c) for c in terms[0].find("Subitem1Sentence").findall("Column")] == ["メートル", "ｍ"]


def test_heading_nesting_and_struct_handling(tmp_path: Path):
    root, _, _ = _run(SAMPLE, tmp_path)
    para = root.find(".//Section[@Num='1']/Article/Paragraph")
    # 冒頭の本文は ParagraphSentence
    assert _text(para.find("ParagraphSentence")) == "本品は、注射剤である。"
    items = para.findall("Item")
    assert [_text(i.find("ItemSentence")) for i in items] == ["製法", "純度試験", "定量法"]
    assert all(_text(i.find("ItemTitle")) == "" for i in items)
    # 項目名の下の本文は Title 空の Subitem1
    assert _text(items[0].find("Subitem1/Subitem1Sentence")) == "本品は、精製して製する。"
    purity = items[1].findall("Subitem1")
    assert [_text(s.find("Subitem1Title")) for s in purity] == ["（１）", "（２）"]
    # （１）の続き「なお…」は Column、小見出し「試験条件」は（１）の子
    cols = purity[0].find("Subitem1Sentence").findall("Column")
    assert [_text(c) for c in cols] == ["異物　試験を行う。", "なお、薄層板を用いる。"]
    cond = purity[0].find("Subitem2")
    assert _text(cond.find("Subitem2Sentence")) == "試験条件"
    body = cond.find("Subitem3")
    assert _text(body.find("Subitem3Sentence")) == "検出器：紫外吸光光度計"
    # 表は直前の要素（Title 空の本文）の末尾。その後の本文は兄弟の Title 空要素
    assert body.find("TableStruct") is not None
    bodies = cond.findall("Subitem3")
    assert [_text(b.find("Subitem3Sentence")) for b in bodies] == ["検出器：紫外吸光光度計", "流量：毎分１ｍＬ"]


def test_text_after_struct_in_labeled_element_is_kept_as_list(tmp_path: Path):
    xml = SAMPLE.replace(
        '<List><ListSentence><Sentence>試験条件</Sentence></ListSentence></List>\n'
        '          <List><ListSentence><Sentence>検出器：紫外吸光光度計</Sentence></ListSentence></List>\n', '')
    root, _, stats = _run(xml, tmp_path)
    para = root.find(".//Section[@Num='1']/Article/Paragraph")
    one = para.findall("Item")[1].findall("Subitem1")[0]
    assert _text(one.find("Subitem1Title")) == "（１）"
    # （１）に表が付き、その後の本文は schema 上 Subitem2 を置けないため List のまま
    assert one.find("TableStruct") is not None
    assert [_text(l) for l in one.findall("List")] == ["流量：毎分１ｍＬ"]
    assert stats.get("kept_list_after_struct") == 1


def test_output_is_schema_valid_and_text_preserved(tmp_path: Path):
    root, _, _ = _run(SAMPLE, tmp_path)
    schema = schema_mod.load_schema(str(project_root / "schema" / "kokuji20250320_asukoe.xsd"))
    assert schema.validate(etree.ElementTree(root)), [e.message for e in schema.error_log][:5]
    src_text = "".join(etree.fromstring(SAMPLE.encode("utf-8")).find(".//MainProvision").itertext())
    out_text = "".join(root.find(".//MainProvision").itertext())
    norm = lambda s: s.replace(" ", "").replace("\n", "").replace("　", "")
    assert norm(out_text) == norm(src_text)


def test_flat_mode_for_long_unlabeled_lists(tmp_path: Path):
    entries = "".join(
        f"<List><ListSentence><Sentence>試薬{i}　説明{i}</Sentence></ListSentence></List>"
        for i in range(45)
    ) + ("<List><ListSentence><Sentence>純度試験</Sentence></ListSentence></List>"
         "<List><ListSentence><Sentence>類縁物質　試験を行う。</Sentence></ListSentence></List>")
    xml = SAMPLE.replace(
        '<List><ListSentence><Sentence>本品は、乙を含む。</Sentence></ListSentence></List>',
        '<List><ListSentence><Sentence>本品は、乙を含む。</Sentence></ListSentence></List>' + entries)
    root, _, stats = _run(xml, tmp_path)
    para = root.find(".//Section[@Num='2']/Article/Paragraph")
    assert stats.get("flat_mode_paragraphs") == 1
    # 「純度試験」も入れ子にせず Title 空の Item として平坦に並ぶ
    assert all(i.find("Subitem1") is None for i in para.findall("Item"))
    assert len(para.findall("Item")) == 45 + 2


def test_missing_toc_heading_is_an_error(tmp_path: Path):
    xml = SAMPLE.replace("<SectionTitle>２　乙注射液</SectionTitle>", "<SectionTitle>２　丙注射液</SectionTitle>")
    import pytest
    with pytest.raises(SystemExit):
        _run(xml, tmp_path)
