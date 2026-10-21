#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
目次（TOC）に合わせて告示XMLを章節構造へ組み直すスクリプト

入力: MainProvision 直下に Article（第１〜）→ Paragraph → List… とフラットに
      並んだ告示XML（LawBody/TOC に TOCChapter/TOCSection/TOCSubsection/TOCDivision あり）
出力: 告示データ整備方針（パターン11／11-2D／7-3D）に沿った構造
      MainProvision
        Chapter（TOCChapter に対応）
          [Article（空Title）→ Paragraph … 節より前の本文]
          Section（TOCSection に対応）
            Subsection → Division → Article（空Title）→ Paragraph
      Paragraph 内の List は次の規則で Item／Subitem1〜10 に変換する。
        ・先頭の本文（Column なし）         → ParagraphSentence
        ・Column 1 がラベル（（１）１ ア 等）→ Title 付き要素。同種ラベルは兄弟、異種は子
        ・短い項目名（製法・性状・純度試験 等）→ Title 空の要素（項目名）。下層をその子にする
        ・本文（Column なし）               → 項目名の下は Title 空の要素、
                                            ラベル付き要素の続きは LineBreak 付き Column
        ・Column 1 がラベルでない複数 Column → Title 空の要素に Column のまま格納
        ・TableStruct／FigStruct            → 直前の要素の末尾に置く。
                                            その後に続く本文は schema 上下層を置けないため List のまま残す
        ・本文が長く連続する段落（試薬・試液の一覧等）は、短い行を項目名として
          入れ子にせず、全てを Paragraph 直下の Item として平坦に並べる
      文頭全角スペースの補填は行わない（postprocess_fullwidth_space.py を後段で適用する）。

使用方法:
    python restructure_by_toc.py input.xml output.xml [--report report.txt]
"""
import argparse
import re
import sys
from copy import deepcopy
from pathlib import Path
from typing import List, Optional, Tuple

from lxml import etree

# --------------------------------------------------------------------------
# 定数
# --------------------------------------------------------------------------
TOC_LEVELS = [
    # (TOC要素名, 本則要素名, Title要素名)
    ('TOCChapter', 'Chapter', 'ChapterTitle'),
    ('TOCSection', 'Section', 'SectionTitle'),
    ('TOCSubsection', 'Subsection', 'SubsectionTitle'),
    ('TOCDivision', 'Division', 'DivisionTitle'),
]
TOC_TAG_TO_BODY = {t: (b, title) for t, b, title in TOC_LEVELS}
STRUCT_TAGS = {'TableStruct', 'FigStruct', 'StyleStruct'}

# 階層要素: depth 1 = Item, 2 = Subitem1, ... 11 = Subitem10
def level_tags(depth: int) -> Tuple[str, str, str]:
    if depth == 1:
        return 'Item', 'ItemTitle', 'ItemSentence'
    n = depth - 1
    return f'Subitem{n}', f'Subitem{n}Title', f'Subitem{n}Sentence'

MAX_DEPTH = 11

# 項目名（見出し）の語彙。rank 1 = 各条の大項目（Paragraph 直下に並ぶ）、
# rank 2 = ラベル付き要素の内側に現れる小見出し
RANK1_HEADINGS = {
    '製法', '性状', '確認試験', 'ｐＨ', '純度試験', '定量法', '貯法',
    '純度試験（放射化学的異物）', '純度試験（異核種）',
    '溶出ガス試験', '溶出液試験', '粒度試験', '比放射能', '放射能濃度',
}
# 見出しとみなさない短文（行の折り返し等で生じた断片）
NOT_HEADINGS = {'検出器', '使用ガス：'}
HEADING_MAX_LEN = 24
# 本文（Column なし List）がこの数以上連続する段落は、項目名を入れ子にしない平坦な列記とみなす
# （試薬・試液の一覧は 100 行以上連続する一方、各条・試験法は長くても 15 行程度）
FLAT_MODE_MIN_BODY_RUN = 40
# 見出しに含まれない文字（句読点・記号・区切りの全角スペース）
HEADING_EXCLUDE_RE = re.compile(r'[。、：＝→～　　]')
DIGIT_ONLY_RE = re.compile(r'^[０-９0-9．.～~〜,，\-－]+$')

LABEL_PATTERNS = [
    ('fw_paren_num', re.compile(r'^（[０-９0-9]+）$')),
    ('hw_paren_num', re.compile(r'^\([０-９0-9]+\)$')),
    ('paren_roman', re.compile(r'^[（(][ｉｖｘivxⅰ-ⅻ]+[）)]$')),
    ('paren_katakana', re.compile(r'^[（(][ア-ン][）)]$')),
    ('paren_alpha', re.compile(r'^[（(][ａ-ｚＡ-Ｚa-zA-Z][）)]$')),
    ('circled', re.compile(r'^[①-⑳㉑-㉟]$')),
    ('dot_num', re.compile(r'^[０-９0-9]+[．.][０-９0-9]+(?:[．.][０-９0-9]+)*$')),
    ('num', re.compile(r'^[０-９0-9]+$')),
    ('kanji', re.compile(r'^[一二三四五六七八九十百]+(?:の[一二三四五六七八九十]+)*$')),
    ('katakana', re.compile(r'^[ア-ン]$')),
    ('alpha', re.compile(r'^[ａ-ｚＡ-Ｚa-zA-Z]$')),
]


def text_of(elem) -> str:
    return ''.join(elem.itertext()) if elem is not None else ''


def norm(s: str) -> str:
    """見出し比較用の正規化: 空白除去と紛らわしい記号の統一"""
    s = re.sub(r'\s|　', '', s)
    return s.translate(str.maketrans({'′': "'", '’': "'", '‘': "'", '"': '"', '”': '"', '“': '"'}))


def label_type(text: str) -> Optional[str]:
    t = text.strip()
    if not t:
        return None
    for name, pat in LABEL_PATTERNS:
        if pat.match(t):
            return name
    return None


def is_heading_text(text: str) -> bool:
    t = text.strip()
    if not t or t in NOT_HEADINGS:
        return False
    if t in RANK1_HEADINGS:
        return True
    if len(t) > HEADING_MAX_LEN:
        return False
    if HEADING_EXCLUDE_RE.search(t) or DIGIT_ONLY_RE.match(t):
        return False
    return True


def heading_rank(text: str) -> int:
    return 1 if text.strip() in RANK1_HEADINGS else 2


# --------------------------------------------------------------------------
# ブロック（Paragraph 直下の List／TableStruct 等）の分類
# --------------------------------------------------------------------------
class Block:
    def __init__(self, elem):
        self.elem = elem
        self.kind = None          # 'labeled' | 'term' | 'heading' | 'body' | 'struct' | 'other'
        self.label_type = None
        self.columns = []         # Column 要素（List の場合）
        self.sentences = []       # Column なし List の Sentence 要素
        self.text = ''
        self.heading_rank = None
        self._classify()

    def _classify(self):
        e = self.elem
        if e.tag in STRUCT_TAGS:
            self.kind = 'struct'
            return
        if e.tag != 'List':
            self.kind = 'other'
            return
        ls = e.find('ListSentence')
        self.columns = ls.findall('Column') if ls is not None else []
        if self.columns:
            col1_text = text_of(self.columns[0]).strip()
            self.text = '　'.join(text_of(c).strip() for c in self.columns)
            self.label_type = label_type(col1_text)
            self.kind = 'labeled' if self.label_type else 'term'
            return
        self.sentences = ls.findall('Sentence') if ls is not None else []
        self.text = text_of(ls).strip()
        if is_heading_text(self.text) and e.find('.//QuoteStruct') is None:
            self.kind = 'heading'
            self.heading_rank = heading_rank(self.text)
        else:
            self.kind = 'body'


# --------------------------------------------------------------------------
# 要素生成ヘルパー
# --------------------------------------------------------------------------
def append_inline(target, sentence, sep: str = ''):
    """Sentence の内容（テキストとインライン要素）を target の末尾へ追記する"""
    lead = sep + (sentence.text or '')
    if len(target):
        target[-1].tail = (target[-1].tail or '') + lead
    else:
        target.text = (target.text or '') + lead
    for child in sentence:
        target.append(deepcopy(child))


def make_title(tag: str, sentences: List, sep: str = '　'):
    """複数の Sentence から Title 要素を作る（文の間は全角スペース区切り）"""
    title = etree.Element(tag)
    for i, s in enumerate(sentences):
        append_inline(title, s, sep if i else '')
    return title


def column_sentences(column) -> List:
    return column.findall('Sentence')


def copy_sentences_into(container, sentences):
    """Sentence を Num を振り直してコンテナ直下へコピー"""
    start = len(container.findall('Sentence'))
    for i, s in enumerate(sentences, start=start + 1):
        ns = deepcopy(s)
        ns.set('Num', str(i))
        container.append(ns)


def renumber(container):
    for i, c in enumerate(container.findall('Column'), 1):
        c.set('Num', str(i))
        for j, s in enumerate(c.findall('Sentence'), 1):
            s.set('Num', str(j))
    for i, s in enumerate(container.findall('Sentence'), 1):
        s.set('Num', str(i))


class Node:
    """変換中の階層要素（Paragraph／Item／Subitem）"""

    def __init__(self, elem, kind, depth, label_type=None, rank=None, sentence_container=None):
        self.elem = elem
        self.kind = kind                # 'paragraph' | 'labeled' | 'heading' | 'body' | 'term'
        self.depth = depth              # 0 = Paragraph
        self.label_type = label_type
        self.rank = rank
        self.sentence = sentence_container
        self.has_struct = False
        self.child_count = 0


def new_element(depth: int, title_sentences: Optional[List], block: Optional[Block], kind: str,
                stats: dict) -> Node:
    """Item／Subitem 要素を生成する"""
    tag, title_tag, sent_tag = level_tags(depth)
    elem = etree.Element(tag)
    if title_sentences:
        elem.append(make_title(title_tag, title_sentences))
    else:
        etree.SubElement(elem, title_tag)
    container = etree.SubElement(elem, sent_tag)
    if block is not None:
        if block.kind == 'labeled':
            rest = block.columns[1:]
            if len(rest) == 1:
                copy_sentences_into(container, column_sentences(rest[0]))
            else:
                for col in rest:
                    container.append(deepcopy(col))
        elif block.kind == 'term':
            for col in block.columns:
                container.append(deepcopy(col))
        else:  # heading / body
            copy_sentences_into(container, block.sentences)
    if not len(container):
        etree.SubElement(container, 'Sentence', Num='1')
    renumber(container)
    stats[f'created_{kind}'] = stats.get(f'created_{kind}', 0) + 1
    return Node(elem, kind, depth, label_type=block.label_type if block else None,
                rank=block.heading_rank if block else None, sentence_container=container)


def append_as_column(node: Node, block: Block, stats: dict):
    """本文を node の *Sentence に LineBreak 付き Column として追記する"""
    container = node.sentence
    direct = container.findall('Sentence')
    if direct and not container.findall('Column'):
        col1 = etree.Element('Column', Num='1')
        for s in direct:
            container.remove(s)
            col1.append(s)
        container.append(col1)
    col = etree.SubElement(container, 'Column', LineBreak='true')
    copy_sentences_into(col, block.sentences)
    renumber(container)
    stats['appended_column'] = stats.get('appended_column', 0) + 1


def append_as_list(node: Node, block: Block, stats: dict):
    """表・図の後の本文を List のまま残す"""
    node.elem.append(deepcopy(block.elem))
    stats['kept_list_after_struct'] = stats.get('kept_list_after_struct', 0) + 1


# --------------------------------------------------------------------------
# Paragraph 内の変換
# --------------------------------------------------------------------------
def build_paragraph(blocks: List[Block], stats: dict):
    para = etree.Element('Paragraph', Num='1')
    etree.SubElement(para, 'ParagraphNum')
    ps = etree.SubElement(para, 'ParagraphSentence')

    # 先頭の本文は ParagraphSentence へ
    idx = 0
    if blocks and blocks[0].kind == 'body':
        copy_sentences_into(ps, blocks[0].sentences)
        idx = 1
        stats['paragraph_sentence_from_body'] = stats.get('paragraph_sentence_from_body', 0) + 1
    if not len(ps):
        etree.SubElement(ps, 'Sentence')

    # 本文が長く連続する段落（試薬・試液の一覧等）は、短い行を項目名として
    # 入れ子にせず、全てを Paragraph 直下の Item として平坦に並べる
    run = longest = 0
    for b in blocks:
        run = run + 1 if b.kind == 'body' else 0
        longest = max(longest, run)
    flat_mode = longest >= FLAT_MODE_MIN_BODY_RUN
    if flat_mode:
        for b in blocks:
            if b.kind == 'heading':
                b.kind = 'body'
                b.heading_rank = None
        stats['flat_mode_paragraphs'] = stats.get('flat_mode_paragraphs', 0) + 1

    root = Node(para, 'paragraph', 0)
    stack: List[Node] = [root]

    def top() -> Node:
        return stack[-1]

    def push_child(parent: Node, node: Node):
        parent.elem.append(node.elem)
        parent.child_count += 1
        node.elem.set('Num', str(parent.child_count))
        stack.append(node)

    def pop_to(node: Node):
        while stack[-1] is not node:
            stack.pop()

    def attach(parent: Node, block: Block, kind: str, title_sentences):
        """parent の子として要素を作る。parent に表・図があれば List のまま残す"""
        if parent.has_struct and parent.kind != 'paragraph':
            pop_to(parent)
            append_as_list(parent, block, stats)
            return
        if parent.depth + 1 > MAX_DEPTH:
            pop_to(parent)
            append_as_list(parent, block, stats)
            stats['depth_overflow'] = stats.get('depth_overflow', 0) + 1
            return
        pop_to(parent)
        push_child(parent, new_element(parent.depth + 1, title_sentences, block, kind, stats))

    for block in blocks[idx:]:
        if flat_mode and block.kind in ('labeled', 'term', 'body'):
            title = column_sentences(block.columns[0]) if block.kind == 'labeled' else None
            attach(root, block, block.kind, title)
            continue

        if block.kind == 'struct':
            t = top()
            t.elem.append(deepcopy(block.elem))
            t.has_struct = True
            stats['struct'] = stats.get('struct', 0) + 1
            continue

        if block.kind == 'other':
            top().elem.append(deepcopy(block.elem))
            stats['other'] = stats.get('other', 0) + 1
            continue

        if block.kind == 'labeled':
            # 同種ラベルの祖先があれば、その兄弟。なければ本文要素を飛ばした上で最上位の子
            sibling = next((n for n in reversed(stack) if n.kind == 'labeled' and n.label_type == block.label_type), None)
            if sibling is not None:
                parent = stack[stack.index(sibling) - 1]
            else:
                parent = next(n for n in reversed(stack) if n.kind not in ('body', 'term'))
            attach(parent, block, 'labeled', column_sentences(block.columns[0]))
            continue

        if block.kind == 'heading':
            parent = root
            for n in reversed(stack):
                if n.kind in ('body', 'term'):
                    continue
                if n.kind == 'heading':
                    if block.heading_rank > n.rank:
                        parent = n
                    elif block.heading_rank == n.rank:
                        parent = stack[stack.index(n) - 1]
                    else:
                        continue
                    break
                if n.kind == 'labeled':
                    if block.heading_rank >= 2:
                        parent = n
                        break
                    continue
                if n.kind == 'paragraph':
                    parent = n
                    break
            attach(parent, block, 'heading', None)
            continue

        if block.kind == 'term':
            t = top()
            if t.kind in ('term', 'body'):
                parent = stack[-2]
            else:
                parent = t
            attach(parent, block, 'term', None)
            continue

        # body
        t = top()
        if t.kind == 'labeled':
            # ラベル付き要素の続きの段落は、同じ要素内の LineBreak 付き Column
            if t.has_struct:
                append_as_list(t, block, stats)
            else:
                append_as_column(t, block, stats)
        elif t.kind in ('body', 'term'):
            # 本文の次の本文は兄弟要素（Title 空）
            attach(stack[-2], block, 'body', None)
        else:  # heading / paragraph
            attach(t, block, 'body', None)

    return para


def make_article(blocks: List[Block], num: int, stats: dict):
    art = etree.Element('Article', Num=str(num))
    etree.SubElement(art, 'ArticleTitle')
    art.append(build_paragraph(blocks, stats))
    return art


# --------------------------------------------------------------------------
# TOC との突き合わせ
# --------------------------------------------------------------------------
class TocNode:
    def __init__(self, toc_elem):
        self.toc_elem = toc_elem
        self.body_tag, self.title_tag = TOC_TAG_TO_BODY[toc_elem.tag]
        self.num = toc_elem.get('Num')
        self.title_text = norm(text_of(toc_elem.find(self.title_tag)))
        self.children = [TocNode(c) for c in toc_elem if c.tag in TOC_TAG_TO_BODY]
        self.match_index = None      # 見出しブロックの位置（flat 列のインデックス）
        self.title_sentences = None  # 本則側の見出しテキスト（Sentence 要素）


def flatten_main_provision(mp) -> List[dict]:
    """Article/Paragraph 直下の要素を1列に並べる。Article 境界は見出し候補として扱う"""
    items = []
    for art in mp.findall('Article'):
        title = text_of(art.find('ArticleTitle')).strip()
        for para in art.findall('Paragraph'):
            ps = para.find('ParagraphSentence')
            ps_sentences = ps.findall('Sentence') if ps is not None else []
            ps_text = text_of(ps).strip()
            children = [c for c in para if c.tag not in ('ParagraphNum', 'ParagraphSentence', 'ParagraphCaption')]
            # Article の見出し候補: ArticleTitle + ParagraphSentence（空なら直後の Column なし List）
            art_title_sentence = etree.Element('Sentence')
            art_title_sentence.text = title
            if ps_text:
                items.append({'elem': None, 'heading': norm(title + ps_text),
                              'title_sentences': [art_title_sentence] + ps_sentences})
            elif children and children[0].tag == 'List' and not children[0].findall('.//Column'):
                first = children.pop(0)
                items.append({'elem': None, 'heading': norm(title + text_of(first)),
                              'title_sentences': [art_title_sentence] + first.findall('.//Sentence')})
            elif title:
                items.append({'elem': None, 'heading': norm(title), 'title_sentences': [art_title_sentence]})
            for c in children:
                b = Block(c)
                h = None
                if b.kind in ('labeled', 'term'):
                    h = norm(b.text)
                    tsent = [s for col in b.columns for s in col.findall('Sentence')]
                elif b.kind in ('heading', 'body'):
                    h = norm(b.text)
                    tsent = b.sentences
                else:
                    tsent = None
                items.append({'elem': c, 'block': b, 'heading': h, 'title_sentences': tsent})
    return items


LEADING_LABEL_RE = re.compile(r'^(第?[０-９0-9一二三四五六七八九十．.]+|［[０-９0-9]+］)')


def fuzzy_find(target: str, items: List[dict], start: int, min_ratio: float = 0.85) -> Optional[int]:
    """先頭の番号（ラベル）が一致し、類似度が min_ratio 以上の見出しブロックを探す"""
    import difflib
    m = LEADING_LABEL_RE.match(target)
    lead = m.group(1) if m else None
    best, best_ratio = None, 0.0
    for i in range(start, len(items)):
        h = items[i]['heading']
        if not h:
            continue
        if lead and not h.startswith(lead):
            continue
        ratio = difflib.SequenceMatcher(None, target, h).ratio()
        if ratio >= min_ratio and ratio > best_ratio:
            best, best_ratio = i, ratio
            if ratio == 1.0:
                break
    return best


def match_toc(nodes: List[TocNode], items: List[dict], start: int, report: List[str]) -> int:
    """TOC ノードを文書順に本則の見出しへ対応付ける。戻り値は次の探索開始位置"""
    pos = start
    for node in nodes:
        found = None
        for i in range(pos, len(items)):
            if items[i]['heading'] and items[i]['heading'] == node.title_text:
                found = i
                break
        if found is None:
            # 原本側で目次と本則の表記が僅かに違う場合（記号の有無等）は、
            # 先頭の番号が同じで類似度の高い見出しを採用する
            found = fuzzy_find(node.title_text, items, pos)
            if found is not None:
                report.append(f"  警告: 表記ゆれで対応付け: 目次 '{text_of(node.toc_elem.find(node.title_tag)).strip()[:40]}' "
                              f"/ 本則 '{items[found]['heading'][:40]}'")
        if found is None:
            raise SystemExit(f"エラー: 目次の見出しが本則に見つかりません: {node.body_tag} "
                             f"'{text_of(node.toc_elem.find(node.title_tag)).strip()}'（探索開始位置 {pos}）")
        node.match_index = found
        node.title_sentences = items[found]['title_sentences']
        report.append(f"  {node.body_tag:<10} {text_of(node.toc_elem.find(node.title_tag)).strip()[:40]}  -> block {found}")
        pos = found + 1
        pos = match_toc(node.children, items, pos, report)
    return pos


def build_container(node: TocNode, items: List[dict], end: int, stats: dict):
    """TOC ノードに対応する Chapter/Section/... を作る。end は内容の終端（排他）"""
    elem = etree.Element(node.body_tag, Num=node.num or '1')
    elem.append(make_title(node.title_tag, node.title_sentences))

    first_child_start = node.children[0].match_index if node.children else end
    leading = [items[i]['block'] for i in range(node.match_index + 1, first_child_start) if items[i]['elem'] is not None]
    # Article 境界（elem None）が内容の途中に混ざることはない前提
    if leading or not node.children:
        elem.append(make_article(leading, 1, stats))
    for ci, child in enumerate(node.children):
        child_end = node.children[ci + 1].match_index if ci + 1 < len(node.children) else end
        elem.append(build_container(child, items, child_end, stats))
    return elem


# --------------------------------------------------------------------------
# 整形
# --------------------------------------------------------------------------
NO_INDENT_INSIDE_SUFFIX = ('Title', 'Label', 'Num')
NO_INDENT_INSIDE = {'Sentence', 'ArithFormula', 'QuoteStruct', 'Ruby', 'Fig', 'Line', 'EnactStatement',
                    'LawTitle', 'LawNum', 'Sup', 'Sub', 'Rt', 'Rb'}


def _is_mixed(elem) -> bool:
    """テキストとインライン要素が混在する要素（整形で空白を入れてはいけない）か"""
    if not isinstance(elem.tag, str):
        return True
    return elem.tag in NO_INDENT_INSIDE or elem.tag.endswith(NO_INDENT_INSIDE_SUFFIX)


def indent(elem, level: int = 0, space: str = '  '):
    """Sentence 等の混在内容には触れずに要素を整形する"""
    if _is_mixed(elem) or not len(elem):
        return
    pad = '\n' + space * (level + 1)
    elem.text = pad
    for child in elem:
        indent(child, level + 1, space)
        child.tail = pad
    elem[-1].tail = '\n' + space * level


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------
def restructure(tree, report: List[str], stats: dict):
    root = tree.getroot()
    law_body = root.find('LawBody')
    toc = law_body.find('TOC')
    mp = law_body.find('MainProvision')
    if toc is None or mp is None:
        raise SystemExit('エラー: TOC または MainProvision がありません')

    toc_nodes = [TocNode(c) for c in toc if c.tag in TOC_TAG_TO_BODY]
    items = flatten_main_provision(mp)
    report.append(f"本則のブロック数: {sum(1 for i in items if i['elem'] is not None)}")
    report.append('目次との対応:')
    match_toc(toc_nodes, items, 0, report)

    new_mp = etree.Element('MainProvision')
    for i, node in enumerate(toc_nodes):
        end = toc_nodes[i + 1].match_index if i + 1 < len(toc_nodes) else len(items)
        new_mp.append(build_container(node, items, end, stats))
    # 先頭の目次見出しより前に本文があれば警告
    pre = [it for it in items[:toc_nodes[0].match_index] if it['elem'] is not None]
    if pre:
        report.append(f"警告: 最初の章見出しより前に {len(pre)} ブロックあり（出力に含まれません）")

    mp.getparent().replace(mp, new_mp)
    return tree


def main():
    ap = argparse.ArgumentParser(description='目次に合わせて告示XMLを章節構造へ組み直す')
    ap.add_argument('input_file')
    ap.add_argument('output_file')
    ap.add_argument('--report', help='対応表・統計の出力先（省略時は標準出力）')
    args = ap.parse_args()

    parser = etree.XMLParser(remove_blank_text=False)
    tree = etree.parse(args.input_file, parser)
    report: List[str] = []
    stats: dict = {}
    restructure(tree, report, stats)

    root = tree.getroot()
    indent(root)
    out = Path(args.output_file)
    out.parent.mkdir(parents=True, exist_ok=True)
    tree.write(str(out), encoding='UTF-8', xml_declaration=True)

    report.append('統計:')
    for k, v in sorted(stats.items()):
        report.append(f"  {k}: {v}")
    text = '\n'.join(report) + '\n'
    if args.report:
        Path(args.report).write_text(text, encoding='utf-8')
    else:
        print(text)
    return 0


if __name__ == '__main__':
    sys.exit(main())
