#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
空Title要素の除去（postprocess_remove_empty_titles）のユニットテスト
"""

import importlib.util
import subprocess
import sys
from pathlib import Path

from lxml import etree

project_root = Path(__file__).resolve().parent.parent
SCRIPT_PATH = project_root / "scripts" / "postprocess_remove_empty_titles.py"

_spec = importlib.util.spec_from_file_location(
    "postprocess_remove_empty_titles", SCRIPT_PATH)
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)

is_empty_title = _module.is_empty_title
remove_empty_titles = _module.remove_empty_titles


def _root(xml: str) -> etree._Element:
    return etree.fromstring(xml.encode('utf-8'))


class TestIsEmptyTitle:
    def test_self_closing_is_empty(self):
        assert is_empty_title(_root('<ItemTitle/>'))

    def test_empty_text_is_empty(self):
        assert is_empty_title(_root('<ItemTitle></ItemTitle>'))

    def test_whitespace_only_is_empty(self):
        assert is_empty_title(_root('<ItemTitle>\n    </ItemTitle>'))

    def test_text_is_not_empty(self):
        assert not is_empty_title(_root('<ItemTitle>一</ItemTitle>'))

    def test_child_element_is_not_empty(self):
        # Ruby等の子要素を持つTitleは内容ありとして保持する
        xml = '<ItemTitle><Ruby>一<Rt>いち</Rt></Ruby></ItemTitle>'
        assert not is_empty_title(_root(xml))

    def test_attribute_is_not_empty(self):
        # 属性付きのTitleは情報を持つため保持する
        assert not is_empty_title(_root('<ItemTitle WritingMode="vertical"/>'))


class TestRemoveEmptyTitles:
    def test_removes_empty_item_title(self):
        root = _root('''<Paragraph>
  <Item Num="1">
    <ItemTitle/>
    <ItemSentence><Sentence Num="1">本文</Sentence></ItemSentence>
  </Item>
</Paragraph>''')
        removed = remove_empty_titles(root)
        assert removed == {'ItemTitle': 1}
        assert root.find('.//ItemTitle') is None
        assert root.find('.//ItemSentence/Sentence').text == '本文'

    def test_keeps_non_empty_item_title(self):
        root = _root('''<Paragraph>
  <Item Num="1">
    <ItemTitle>一</ItemTitle>
    <ItemSentence><Sentence Num="1">本文</Sentence></ItemSentence>
  </Item>
</Paragraph>''')
        removed = remove_empty_titles(root)
        assert removed == {}
        assert root.find('.//ItemTitle').text == '一'

    def test_removes_all_subitem_levels(self):
        # Subitem1～10まで空Titleがすべて除去される
        inner = '<Subitem10Title/><Subitem10Sentence><Sentence Num="1">末端</Sentence></Subitem10Sentence>'
        for i in range(9, 0, -1):
            inner = (f'<Subitem{i}Title/>'
                     f'<Subitem{i}Sentence><Sentence Num="1">s{i}</Sentence></Subitem{i}Sentence>'
                     f'<Subitem{i + 1} Num="1">{inner}</Subitem{i + 1}>')
        xml = (f'<Item Num="1"><ItemTitle/>'
               f'<ItemSentence><Sentence Num="1">本文</Sentence></ItemSentence>'
               f'<Subitem1 Num="1">{inner}</Subitem1></Item>')
        root = _root(xml)
        removed = remove_empty_titles(root)
        assert removed['ItemTitle'] == 1
        for i in range(1, 11):
            assert removed[f'Subitem{i}Title'] == 1
            assert root.find(f'.//Subitem{i}Title') is None
        # Sentenceは残っている
        assert len(root.findall('.//Sentence')) == 11

    def test_mixed_empty_and_non_empty(self):
        root = _root('''<Paragraph>
  <Item Num="1">
    <ItemTitle>一</ItemTitle>
    <ItemSentence><Sentence Num="1">本文1</Sentence></ItemSentence>
    <Subitem1 Num="1">
      <Subitem1Title/>
      <Subitem1Sentence><Sentence Num="1">本文2</Sentence></Subitem1Sentence>
    </Subitem1>
  </Item>
  <Item Num="2">
    <ItemTitle/>
    <ItemSentence><Sentence Num="1">本文3</Sentence></ItemSentence>
  </Item>
</Paragraph>''')
        removed = remove_empty_titles(root)
        assert removed == {'ItemTitle': 1, 'Subitem1Title': 1}
        # 内容ありのTitleは残る
        titles = root.findall('.//ItemTitle')
        assert len(titles) == 1
        assert titles[0].text == '一'

    def test_does_not_touch_other_title_tags(self):
        # ArticleTitle/ParagraphCaption等は対象外
        root = _root('''<Article Num="1">
  <ArticleTitle></ArticleTitle>
  <Paragraph Num="1">
    <ParagraphNum/>
    <ParagraphSentence><Sentence Num="1">本文</Sentence></ParagraphSentence>
  </Paragraph>
</Article>''')
        removed = remove_empty_titles(root)
        assert removed == {}
        assert root.find('.//ArticleTitle') is not None
        assert root.find('.//ParagraphNum') is not None

    def test_indentation_is_preserved(self):
        # 除去後にインデントが崩れない（Titleのtailが親のtextに引き継がれる）
        root = _root('<Item Num="1">\n    <ItemTitle/>\n    '
                     '<ItemSentence><Sentence Num="1">本文</Sentence></ItemSentence>\n  </Item>')
        remove_empty_titles(root)
        assert root.text == '\n    '
        xml_out = etree.tostring(root, encoding='unicode')
        assert '<Item Num="1">\n    <ItemSentence>' in xml_out


class TestCliExecution:
    def test_cli_removes_empty_titles(self, tmp_path):
        input_path = tmp_path / "input.xml"
        output_path = tmp_path / "output.xml"
        input_path.write_text('''<?xml version="1.0" encoding="UTF-8"?>
<Law>
  <Paragraph Num="1">
    <Item Num="1">
      <ItemTitle/>
      <ItemSentence><Sentence Num="1">本文</Sentence></ItemSentence>
      <Subitem1 Num="1">
        <Subitem1Title>（１）</Subitem1Title>
        <Subitem1Sentence><Sentence Num="1">細目</Sentence></Subitem1Sentence>
      </Subitem1>
    </Item>
  </Paragraph>
</Law>''', encoding='utf-8')

        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), str(input_path), str(output_path)],
            capture_output=True, text=True, timeout=60
        )
        assert result.returncode == 0, result.stderr
        assert output_path.exists()

        root = etree.parse(str(output_path)).getroot()
        assert root.find('.//ItemTitle') is None
        assert root.find('.//Subitem1Title').text == '（１）'
        assert root.find('.//ItemSentence/Sentence').text == '本文'

    def test_cli_missing_input_returns_error(self, tmp_path):
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH),
             str(tmp_path / "nonexistent.xml"), str(tmp_path / "out.xml")],
            capture_output=True, text=True, timeout=60
        )
        assert result.returncode == 1
