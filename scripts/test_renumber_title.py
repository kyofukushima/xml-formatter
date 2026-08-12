#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
タイトル由来の Num 採番（renumber_utils）のユニットテスト

- title_to_num: タイトル文字列 → コーパス準拠の Num 値（"6_2" 等）の導出
- renumber_children: 親単位 all-or-nothing のタイトル由来採番と連番フォールバック
- renumber_nums_by_title: 直接の親ごとのグループ化採番
"""

import sys
from pathlib import Path

from lxml import etree
import pytest

script_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(script_dir))

from utils.renumber_utils import (
    title_to_num,
    renumber_children,
    renumber_nums_by_title,
)


# ============================================================================
# title_to_num
# ============================================================================

@pytest.mark.parametrize("text,expected", [
    # アラビア数字（全角・半角）
    ("１", "1"),
    ("12", "12"),
    ("１２", "12"),
    ("６の２", "6_2"),
    ("6の2", "6_2"),
    # 漢数字
    ("一", "1"),
    ("十二", "12"),
    ("十六", "16"),
    ("五十九", "59"),
    ("百", "100"),
    ("二百十", "210"),
    ("六の二", "6_2"),
    ("五十九の二", "59_2"),
    ("三の四の二", "3_4_2"),
    # 条見出し形式
    ("第１", "1"),
    ("第１の２", "1_2"),
    ("第一条", "1"),
    ("第十三条の二", "13_2"),
    ("第百条", "100"),
    # 前後の空白（全角スペース含む）は無視
    ("　六の二　", "6_2"),
    (" １２ ", "12"),
])
def test_title_to_num_valid(text, expected):
    assert title_to_num(text) == expected


@pytest.mark.parametrize("text", [
    None,
    "",
    "　",
    "（１）",       # 括弧付きは対象外（コーパスでも連番）
    "（２）",
    "イ",           # イロハは対象外
    "ア",
    "一二",         # 位取り表記は番号として扱わない
    "一〇三",       # 〇を含む表記は対象外
    "第１　総則",   # 番号以外の文字列を含む
    "沖縄科学技術大学院大学学園会計基準の「第５２",  # 「の」を含む非番号タイトル
    "様式",
    "別表第一",
])
def test_title_to_num_invalid(text):
    assert title_to_num(text) is None


# ============================================================================
# renumber_children
# ============================================================================

def _make_paragraph(item_titles):
    """指定タイトルの Item を持つ Paragraph 要素を生成する（タイトル None は ItemTitle なし）"""
    paragraph = etree.Element('Paragraph', Num="1")
    for title in item_titles:
        item = etree.SubElement(paragraph, 'Item', Num="999")
        if title is not None:
            title_elem = etree.SubElement(item, 'ItemTitle')
            title_elem.text = title
        etree.SubElement(item, 'ItemSentence')
    return paragraph


def _item_nums(paragraph):
    return [item.get('Num') for item in paragraph.findall('Item')]


def test_renumber_children_title_derived():
    """全 Item のタイトルが導出可能 → 枝番形式で採番"""
    paragraph = _make_paragraph(['１', '２', '６の２', '７'])
    mode, count = renumber_children(paragraph, 'Item')
    assert mode == 'title'
    assert count == 4
    assert _item_nums(paragraph) == ['1', '2', '6_2', '7']


def test_renumber_children_kanji_branch():
    """漢数字の枝番タイトルも導出できる"""
    paragraph = _make_paragraph(['一', '二', '六の二', '六の三'])
    mode, _ = renumber_children(paragraph, 'Item')
    assert mode == 'title'
    assert _item_nums(paragraph) == ['1', '2', '6_2', '6_3']


def test_renumber_children_fallback_on_underivable():
    """1つでも導出できないタイトルがあれば親単位で連番にフォールバック"""
    paragraph = _make_paragraph(['一', '（２）', '三'])
    mode, _ = renumber_children(paragraph, 'Item')
    assert mode == 'sequential'
    assert _item_nums(paragraph) == ['1', '2', '3']


def test_renumber_children_fallback_on_missing_title():
    """ItemTitle が無い要素が混在する場合も連番にフォールバック"""
    paragraph = _make_paragraph(['一', None, '三'])
    mode, _ = renumber_children(paragraph, 'Item')
    assert mode == 'sequential'
    assert _item_nums(paragraph) == ['1', '2', '3']


def test_renumber_children_fallback_on_duplicate():
    """導出値が重複する場合は連番にフォールバック"""
    paragraph = _make_paragraph(['一', '一', '二'])
    mode, _ = renumber_children(paragraph, 'Item')
    assert mode == 'sequential'
    assert _item_nums(paragraph) == ['1', '2', '3']


def test_renumber_children_paragraph_always_sequential():
    """Paragraph は Num が xs:positiveInteger のため常に連番"""
    main = etree.Element('MainProvision')
    for _ in range(3):
        etree.SubElement(main, 'Paragraph', Num="999")
    mode, count = renumber_children(main, 'Paragraph')
    assert mode == 'sequential'
    assert count == 3
    assert [p.get('Num') for p in main.findall('Paragraph')] == ['1', '2', '3']


def test_renumber_children_no_children():
    paragraph = etree.Element('Paragraph', Num="1")
    mode, count = renumber_children(paragraph, 'Item')
    assert count == 0


def test_renumber_children_direct_children_only():
    """孫要素（Subitem1 内の Item 等）は採番対象にしない"""
    paragraph = _make_paragraph(['一', '二'])
    subitem = etree.SubElement(paragraph.findall('Item')[0], 'Subitem1', Num="1")
    nested_item = etree.SubElement(subitem, 'Item', Num="999")
    renumber_children(paragraph, 'Item')
    assert nested_item.get('Num') == '999'  # 変更されない


# ============================================================================
# renumber_nums_by_title
# ============================================================================

def test_renumber_nums_by_title_article_grouping():
    """Article を直接の親（Chapter）ごとにグループ化して採番する"""
    xml = """
    <Law>
      <LawBody>
        <MainProvision>
          <Chapter Num="1">
            <ChapterTitle>第一章</ChapterTitle>
            <Article Num="99"><ArticleTitle>第一条</ArticleTitle></Article>
            <Article Num="99"><ArticleTitle>第二条</ArticleTitle></Article>
            <Article Num="99"><ArticleTitle>第二条の二</ArticleTitle></Article>
          </Chapter>
          <Chapter Num="2">
            <ChapterTitle>第二章</ChapterTitle>
            <Article Num="99"><ArticleTitle>第三条</ArticleTitle></Article>
          </Chapter>
        </MainProvision>
      </LawBody>
    </Law>
    """
    tree = etree.ElementTree(etree.fromstring(xml))
    stats = renumber_nums_by_title(tree, ['Article'])
    nums = [a.get('Num') for a in tree.getroot().iter('Article')]
    assert nums == ['1', '2', '2_2', '3']
    assert stats['Article'] == {'title': 4, 'sequential': 0}


def test_renumber_nums_by_title_mixed_parents():
    """導出可否は親単位で独立に判定される"""
    xml = """
    <MainProvision>
      <Paragraph Num="1">
        <Item Num="9"><ItemTitle>一</ItemTitle><ItemSentence/></Item>
        <Item Num="9"><ItemTitle>六の二</ItemTitle><ItemSentence/></Item>
      </Paragraph>
      <Paragraph Num="2">
        <Item Num="9"><ItemTitle>（１）</ItemTitle><ItemSentence/></Item>
        <Item Num="9"><ItemTitle>（２）</ItemTitle><ItemSentence/></Item>
      </Paragraph>
    </MainProvision>
    """
    tree = etree.ElementTree(etree.fromstring(xml))
    stats = renumber_nums_by_title(tree, ['Item'])
    paragraphs = tree.getroot().findall('Paragraph')
    assert [i.get('Num') for i in paragraphs[0].findall('Item')] == ['1', '6_2']
    assert [i.get('Num') for i in paragraphs[1].findall('Item')] == ['1', '2']
    assert stats['Item'] == {'title': 2, 'sequential': 2}


if __name__ == '__main__':
    sys.exit(pytest.main([__file__, '-v']))
