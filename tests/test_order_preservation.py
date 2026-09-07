#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
コンテンツ順序保持・テキスト欠落防止のユニットテスト

対象:
- scripts/preprocess_non_first_sentence_to_list.py
  （Ruby等のインライン子要素・複数Sentenceの保持）
- scripts/convert_article_focused.py
  （Article分割時のParagraph子要素の並び順保持）
- scripts/compare_xml_text_content.py
  （順序入れ替わり・重複断片欠落の検出）
"""

import subprocess
import sys
from pathlib import Path

import pytest
from lxml import etree

project_root = Path(__file__).resolve().parent.parent
SCRIPTS = project_root / "scripts"


def run_script(script_name: str, input_xml: str, tmp_path: Path,
               extra_args=None) -> etree._ElementTree:
    """変換スクリプトをCLIとして実行し、出力XMLツリーを返す"""
    in_file = tmp_path / "input.xml"
    out_file = tmp_path / "output.xml"
    in_file.write_text(input_xml, encoding='utf-8')
    cmd = [sys.executable, str(SCRIPTS / script_name),
           str(in_file), str(out_file)] + (extra_args or [])
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    assert result.returncode == 0, f"スクリプト実行失敗: {result.stderr}"
    return etree.parse(str(out_file))


def full_text(tree_or_elem) -> str:
    """空白（全角含む）を除いた文書順の全テキスト"""
    root = tree_or_elem.getroot() if hasattr(tree_or_elem, 'getroot') else tree_or_elem
    return ''.join(''.join(root.itertext()).split()).replace('　', '')


# ---------------------------------------------------------------------------
# preprocess_non_first_sentence_to_list.py
# ---------------------------------------------------------------------------

class TestPreprocessPreservesContent:
    SCRIPT = "preprocess_non_first_sentence_to_list.py"

    def test_ruby_is_preserved(self, tmp_path):
        """Ruby等のインライン子要素とその後続テキストが変換後も保持される"""
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Law><LawBody><MainProvision><Article Num="1"><ArticleTitle>第１</ArticleTitle>
<Paragraph Num="1"><ParagraphNum>１</ParagraphNum>
<ParagraphSentence><Sentence Num="1">最初の文</Sentence></ParagraphSentence>
<ParagraphSentence><Sentence Num="1">九　コンクリート充<Ruby>塡<Rt>てん</Rt></Ruby>鋼管造の材料強度</Sentence></ParagraphSentence>
</Paragraph></Article></MainProvision></LawBody></Law>"""
        tree = run_script(self.SCRIPT, input_xml, tmp_path)

        # 2つ目のParagraphSentenceがListに変換されている
        lists = tree.findall('.//List')
        assert len(lists) == 1
        cols = lists[0].findall('.//Column')
        assert cols[0].find('Sentence').text == '九'

        # Column2のSentenceにRuby子要素と後続テキスト（tail）が残っている
        col2_sentence = cols[1].find('Sentence')
        assert col2_sentence.text == 'コンクリート充'
        ruby = col2_sentence.find('Ruby')
        assert ruby is not None
        assert ruby.text == '塡'
        assert ruby.find('Rt').text == 'てん'
        assert ruby.tail == '鋼管造の材料強度'

        # 全テキストが欠落していない（区切りの全角スペース以外）
        assert '最初の文九コンクリート充塡てん鋼管造の材料強度' in full_text(tree)

    def test_multiple_sentences_are_preserved(self, tmp_path):
        """XxxSentenceが複数のSentenceを持つ場合、2つ目以降も保持される"""
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Law><LawBody><MainProvision><Article Num="1"><ArticleTitle>第１</ArticleTitle>
<Paragraph Num="1"><ParagraphNum>１</ParagraphNum>
<ParagraphSentence><Sentence Num="1">最初の文</Sentence></ParagraphSentence>
<ParagraphSentence><Sentence Num="1">一　本文その一。</Sentence><Sentence Num="2">続きの文。</Sentence></ParagraphSentence>
</Paragraph></Article></MainProvision></LawBody></Law>"""
        tree = run_script(self.SCRIPT, input_xml, tmp_path)

        lists = tree.findall('.//List')
        assert len(lists) == 1
        cols = lists[0].findall('.//Column')
        assert cols[0].find('Sentence').text == '一'

        col2_sentences = cols[1].findall('Sentence')
        assert len(col2_sentences) == 2
        assert col2_sentences[0].text == '本文その一。'
        assert col2_sentences[1].text == '続きの文。'
        assert col2_sentences[0].get('Num') == '1'
        assert col2_sentences[1].get('Num') == '2'

    def test_plain_sentence_conversion_unchanged(self, tmp_path):
        """従来どおりの単純な「ラベル＋全角スペース＋本文」の変換（回帰確認）"""
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Law><LawBody><MainProvision><Article Num="1"><ArticleTitle>第１</ArticleTitle>
<Paragraph Num="1"><ParagraphNum>１</ParagraphNum>
<ParagraphSentence><Sentence Num="1">最初の文</Sentence></ParagraphSentence>
<ParagraphSentence><Sentence Num="1">（３）　評価基準（新築住宅）</Sentence></ParagraphSentence>
</Paragraph></Article></MainProvision></LawBody></Law>"""
        tree = run_script(self.SCRIPT, input_xml, tmp_path)

        lists = tree.findall('.//List')
        assert len(lists) == 1
        cols = lists[0].findall('.//Column')
        assert cols[0].find('Sentence').text == '（３）'
        assert cols[1].find('Sentence').text == '評価基準（新築住宅）'

    def test_non_label_sentence_not_converted(self, tmp_path):
        """ラベルで始まらないSentenceは変換されない"""
        input_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Law><LawBody><MainProvision><Article Num="1"><ArticleTitle>第１</ArticleTitle>
<Paragraph Num="1"><ParagraphNum>１</ParagraphNum>
<ParagraphSentence><Sentence Num="1">最初の文</Sentence></ParagraphSentence>
<ParagraphSentence><Sentence Num="1">ラベルではない　ただの文章</Sentence></ParagraphSentence>
</Paragraph></Article></MainProvision></LawBody></Law>"""
        tree = run_script(self.SCRIPT, input_xml, tmp_path)
        assert len(tree.findall('.//List')) == 0
        assert len(tree.findall('.//ParagraphSentence')) == 2


# ---------------------------------------------------------------------------
# convert_article_focused.py
# ---------------------------------------------------------------------------

class TestArticleSplitPreservesOrder:
    SCRIPT = "convert_article_focused.py"

    INPUT = """<?xml version="1.0" encoding="UTF-8"?>
<Law><LawBody><MainProvision>
<Article Num="1"><ArticleTitle>第一</ArticleTitle>
<Paragraph Num="1">
  <ParagraphNum/>
  <ParagraphSentence><Sentence Num="1">冒頭の文</Sentence></ParagraphSentence>
  <TableStruct><Table><TableRow><TableColumn><Sentence>表一の内容</Sentence></TableColumn></TableRow></Table></TableStruct>
  <ParagraphSentence><Sentence Num="1">表一の後の文</Sentence></ParagraphSentence>
  <List><ListSentence>
    <Column Num="1"><Sentence Num="1">第二</Sentence></Column>
    <Column Num="2"><Sentence Num="1">次の章の内容</Sentence></Column>
  </ListSentence></List>
  <TableStruct><Table><TableRow><TableColumn><Sentence>表二の内容</Sentence></TableColumn></TableRow></Table></TableStruct>
  <ParagraphSentence><Sentence Num="1">表二の後の文</Sentence></ParagraphSentence>
</Paragraph></Article>
</MainProvision></LawBody></Law>"""

    def test_split_keeps_document_order(self, tmp_path):
        """Article分割後もTableStructとParagraphSentence等の出現順が保たれる"""
        tree = run_script(self.SCRIPT, self.INPUT, tmp_path)

        # 分割されて2つのArticleになっている
        articles = tree.findall('.//Article')
        assert len(articles) == 2
        assert articles[1].find('ArticleTitle').text == '第二'

        # コンテンツの出現順が入力と同一
        text = full_text(tree)
        markers = ['冒頭の文', '表一の内容', '表一の後の文',
                   '第二', '次の章の内容', '表二の内容', '表二の後の文']
        positions = [text.index(m) for m in markers]
        assert positions == sorted(positions), \
            f"コンテンツの順序が変わっています: {[(m, p) for m, p in zip(markers, positions)]}"

    def test_split_halves_contain_right_content(self, tmp_path):
        """分割点の前後で要素が正しいArticleに振り分けられる"""
        tree = run_script(self.SCRIPT, self.INPUT, tmp_path)
        articles = tree.findall('.//Article')

        first_text = full_text(articles[0])
        second_text = full_text(articles[1])

        assert '冒頭の文' in first_text
        assert '表一の内容' in first_text
        assert '表一の後の文' in first_text
        assert '表二の内容' not in first_text
        assert '表二の後の文' not in first_text

        assert '次の章の内容' in second_text
        assert '表二の内容' in second_text
        assert '表二の後の文' in second_text
        assert '冒頭の文' not in second_text

        # 分割後半のParagraph内でも順序が保たれる
        # （新ParagraphSentence → TableStruct → 元のParagraphSentence）
        pos = [second_text.index(m)
               for m in ['次の章の内容', '表二の内容', '表二の後の文']]
        assert pos == sorted(pos)


# ---------------------------------------------------------------------------
# compare_xml_text_content.py
# ---------------------------------------------------------------------------

class TestCompareDetectsOrderIssues:
    SCRIPT = "compare_xml_text_content.py"

    BASE = """<?xml version="1.0" encoding="UTF-8"?>
<Law><LawBody><MainProvision><Article Num="1"><ArticleTitle>第１</ArticleTitle>
<Paragraph Num="1"><ParagraphNum>１</ParagraphNum>
<ParagraphSentence><Sentence Num="1">{s1}</Sentence></ParagraphSentence>
<ParagraphSentence><Sentence Num="1">{s2}</Sentence></ParagraphSentence>
<ParagraphSentence><Sentence Num="1">{s3}</Sentence></ParagraphSentence>
</Paragraph></Article></MainProvision></LawBody></Law>"""

    def run_compare(self, tmp_path, original_xml, final_xml):
        orig = tmp_path / "original.xml"
        final = tmp_path / "final.xml"
        report = tmp_path / "report.txt"
        orig.write_text(original_xml, encoding='utf-8')
        final.write_text(final_xml, encoding='utf-8')
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / self.SCRIPT),
             str(orig), str(final), '--report_file', str(report)],
            capture_output=True, text=True, timeout=120)
        report_text = report.read_text(encoding='utf-8') if report.exists() else ''
        return result, report_text

    def test_identical_files_pass(self, tmp_path):
        xml = self.BASE.format(s1='文章その一', s2='文章その二', s3='文章その三')
        result, report = self.run_compare(tmp_path, xml, xml)
        assert result.returncode == 0
        assert '✅ Text order is correct.' in report

    def test_reordered_content_is_detected(self, tmp_path):
        """断片は全て存在するが順序が入れ替わっている場合にエラーになる"""
        orig = self.BASE.format(s1='文章その一', s2='文章その二', s3='文章その三')
        final = self.BASE.format(s1='文章その一', s2='文章その三', s3='文章その二')
        result, report = self.run_compare(tmp_path, orig, final)
        assert result.returncode == 1
        assert '❌ Error:' in report
        assert 'text order/content issue' in report

    def test_lost_duplicate_fragment_is_detected(self, tmp_path):
        """同一テキストが2箇所→1箇所に減った場合（set比較では検出不能）にエラーになる"""
        orig = self.BASE.format(s1='重複する文', s2='重複する文', s3='別の文')
        final = self.BASE.format(s1='重複する文', s2='別の文', s3='おまけの文')
        result, report = self.run_compare(tmp_path, orig, final)
        assert result.returncode == 1
        assert '❌ Error:' in report

    def test_insertion_only_is_tolerated(self, tmp_path):
        """変換で正当に発生する挿入（ParagraphNum複製等）はエラーにしない"""
        orig = self.BASE.format(s1='文章その一', s2='文章その二', s3='文章その三')
        final = self.BASE.format(s1='文章その一', s2='文章その二',
                                 s3='文章その三').replace(
            '</Paragraph>',
            '<ParagraphSentence><Sentence Num="1">追加された文</Sentence>'
            '</ParagraphSentence></Paragraph>')
        result, report = self.run_compare(tmp_path, orig, final)
        assert result.returncode == 0
        assert '✅ Text order is correct.' in report


if __name__ == '__main__':
    sys.exit(pytest.main([__file__, '-v']))
