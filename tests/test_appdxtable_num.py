"""
別表（AppdxTable）の Num 属性付与（scripts/postprocess_appdxtable_num.py）のテスト

- parse_title_ordinal: タイトルからの序数・枝番の読み取り
- assign_nums: タイトル序数方式 / 出現順連番方式、既存 Num の扱い、未付与・重複・要確認の報告
- process_file: CLI 相当の入出力（整形維持、冪等性）
- ホーム画面のオプション（チェックボックス・ラジオとセッション状態）
"""
import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest
from lxml import etree

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
SCRIPT = SCRIPTS_DIR / "postprocess_appdxtable_num.py"
HOME_PAGE = PROJECT_ROOT / "app_pages" / "home.py"

_spec = importlib.util.spec_from_file_location("postprocess_appdxtable_num", SCRIPT)
pan = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pan)


# ------------------------------------------------------------------
# parse_title_ordinal
# ------------------------------------------------------------------
@pytest.mark.parametrize("title,expected", [
    ("別表第一", (1, False)),
    ("別表第二", (2, False)),
    ("別表第十三", (13, False)),
    ("別表第２", (2, False)),
    ("別表2", (2, False)),
    ("別表１２", (12, False)),
    ("別記第二十", (20, False)),
    ("付録第３", (3, False)),
    ("付表三", (3, False)),
    ("　別表第一　", (1, False)),
    ("別表第一（第三条関係）", (1, False)),
    # 枝番付き（先頭の序数と True）
    ("別表第三の一の二", (3, True)),
    ("別表第九の二", (9, True)),
    ("別表第１の２", (1, True)),
    ("別表第十ノ二", (10, True)),
    # 「の」の後が数字でなければ枝番ではない
    ("別表第一の施設基準", (1, False)),
])
def test_parse_title_ordinal(title, expected):
    assert pan.parse_title_ordinal(title) == expected


@pytest.mark.parametrize("title", [
    None, "", "　", "別表", "様式", "別表第", "一二", "別表第一二", "別表第〇",
])
def test_parse_title_ordinal_invalid(title):
    assert pan.parse_title_ordinal(title) == (None, False)


@pytest.mark.parametrize("value,expected", [
    ("1", True), ("44", True), ("0", False), ("", False), (None, False),
    ("1_2", False), ("一", False), ("-1", False),
])
def test_is_valid_num(value, expected):
    assert pan.is_valid_num(value) is expected


# ------------------------------------------------------------------
# assign_nums
# ------------------------------------------------------------------
def _make_root(tables):
    """[(Num属性 or None, タイトル or None), ...] から LawBody を生成する"""
    root = etree.Element('LawBody')
    for num, title in tables:
        attrib = {'Num': num} if num is not None else {}
        table = etree.SubElement(root, 'AppdxTable', attrib)
        if title is not None:
            t = etree.SubElement(table, 'AppdxTableTitle')
            t.text = title
        etree.SubElement(table, 'TableStruct')
    return root


def _nums(root, tag='AppdxTable'):
    return [e.get('Num') for e in root.iter(tag)]


def test_title_mode_assigns_from_ordinal():
    root = _make_root([(None, '別表第一'), (None, '別表第二'), (None, '別表第２０')])
    result = pan.assign_nums(root, ['AppdxTable'], mode='title')
    assert _nums(root) == ['1', '2', '20']
    assert len(result['assigned']) == 3
    assert result['unassigned'] == [] and result['duplicated'] == []


def test_title_mode_skips_branch_titles_and_reports():
    root = _make_root([(None, '別表第三'), (None, '別表第三の一の二'), (None, '別表第四')])
    result = pan.assign_nums(root, ['AppdxTable'], mode='title')
    assert _nums(root) == ['3', None, '4']
    assert len(result['unassigned']) == 1
    tag, line, title, reason = result['unassigned'][0]
    assert title == '別表第三の一の二' and '枝番' in reason


def test_title_mode_skips_unreadable_title_when_multiple():
    root = _make_root([(None, '別表第一'), (None, '別表'), (None, None)])
    result = pan.assign_nums(root, ['AppdxTable'], mode='title')
    assert _nums(root) == ['1', None, None]
    assert len(result['unassigned']) == 2


def test_title_mode_single_element_without_ordinal_gets_one():
    root = _make_root([(None, '別表')])
    pan.assign_nums(root, ['AppdxTable'], mode='title')
    assert _nums(root) == ['1']


def test_title_mode_reports_duplicates_but_assigns():
    root = _make_root([(None, '別表第一'), (None, '別記第一'), (None, '別表第二')])
    result = pan.assign_nums(root, ['AppdxTable'], mode='title')
    assert _nums(root) == ['1', '1', '2']
    assert result['duplicated'] == [('AppdxTable', '1', 2)]


def test_sequential_mode_numbers_in_document_order():
    root = _make_root([(None, '別表第一'), (None, '別表第三の一の二'), (None, '別表'), (None, None)])
    result = pan.assign_nums(root, ['AppdxTable'], mode='sequential')
    assert _nums(root) == ['1', '2', '3', '4']
    assert result['unassigned'] == []


def test_existing_valid_num_is_kept_and_mismatch_reported():
    root = _make_root([('5', '別表第一'), (None, '別表第二'), ('0', '別表第三')])
    result = pan.assign_nums(root, ['AppdxTable'], mode='title')
    # 有効な Num="5" は維持（方式では 1 なので要確認）、Num="0" は無効なので付与
    assert _nums(root) == ['5', '2', '3']
    assert result['kept']['AppdxTable'] == 1
    assert len(result['mismatched']) == 1
    assert result['mismatched'][0][3:] == ('5', '1')


def test_overwrite_renumbers_valid_nums():
    root = _make_root([('5', '別表第一'), ('7', '別表第二')])
    result = pan.assign_nums(root, ['AppdxTable'], mode='title', overwrite=True)
    assert _nums(root) == ['1', '2']
    assert result['mismatched'] == [] and sum(result['kept'].values()) == 0


def test_sequential_mode_without_overwrite_uses_position():
    root = _make_root([('1', '別表第一'), (None, '別表第二'), (None, '別表第三')])
    pan.assign_nums(root, ['AppdxTable'], mode='sequential')
    assert _nums(root) == ['1', '2', '3']


def test_other_elements_untouched_unless_specified():
    root = _make_root([(None, '別表第一')])
    note = etree.SubElement(root, 'AppdxNote')
    etree.SubElement(note, 'AppdxNoteTitle').text = '別記第二'
    pan.assign_nums(root, ['AppdxTable'], mode='title')
    assert note.get('Num') is None
    pan.assign_nums(root, ['AppdxTable', 'AppdxNote'], mode='title')
    assert note.get('Num') == '2'


def test_idempotent():
    root = _make_root([(None, '別表第一'), (None, '別表第二')])
    pan.assign_nums(root, ['AppdxTable'], mode='title')
    first = etree.tostring(root)
    result = pan.assign_nums(root, ['AppdxTable'], mode='title')
    assert etree.tostring(root) == first
    assert result['assigned'] == [] and result['kept']['AppdxTable'] == 2


def test_unknown_mode_raises():
    with pytest.raises(ValueError):
        pan.assign_nums(_make_root([]), ['AppdxTable'], mode='bogus')


# ------------------------------------------------------------------
# process_file / CLI
# ------------------------------------------------------------------
SAMPLE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<Law>
  <LawBody>
    <AppdxTable>
      <AppdxTableTitle>別表第一</AppdxTableTitle>
      <TableStruct/>
    </AppdxTable>
    <AppdxTable>
      <AppdxTableTitle>別表第三の二</AppdxTableTitle>
      <TableStruct/>
    </AppdxTable>
  </LawBody>
</Law>
"""


def test_process_file_preserves_formatting_and_text(tmp_path):
    src = tmp_path / "in.xml"
    out = tmp_path / "out.xml"
    src.write_text(SAMPLE_XML, encoding='utf-8')
    assert pan.process_file(src, out, mode='title') == 0
    text = out.read_text(encoding='utf-8')
    assert '<AppdxTable Num="1">' in text
    assert text.count('<AppdxTable>') == 1  # 枝番付きは未付与のまま
    # 属性以外（整形・テキスト）は変わらない
    strip = lambda s: s.replace(' Num="1"', '').split('?>', 1)[1].strip()
    assert strip(text) == strip(SAMPLE_XML)


def test_cli_sequential_and_idempotent(tmp_path):
    src = tmp_path / "in.xml"
    out1 = tmp_path / "out1.xml"
    out2 = tmp_path / "out2.xml"
    src.write_text(SAMPLE_XML, encoding='utf-8')
    r = subprocess.run([sys.executable, str(SCRIPT), str(src), str(out1), '--mode', 'sequential'],
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr
    assert '付与実施: 2箇所' in r.stdout
    nums = [e.get('Num') for e in etree.parse(str(out1)).getroot().iter('AppdxTable')]
    assert nums == ['1', '2']
    r2 = subprocess.run([sys.executable, str(SCRIPT), str(out1), str(out2), '--mode', 'sequential'],
                        capture_output=True, text=True, timeout=60)
    assert r2.returncode == 0 and '付与実施: 0箇所' in r2.stdout
    assert out1.read_bytes() == out2.read_bytes()


def test_cli_reports_unassigned_with_line_numbers(tmp_path):
    src = tmp_path / "in.xml"
    out = tmp_path / "out.xml"
    src.write_text(SAMPLE_XML, encoding='utf-8')
    r = subprocess.run([sys.executable, str(SCRIPT), str(src), str(out)],
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr
    assert '未付与: 1箇所' in r.stdout
    assert 'in.xml:8 <AppdxTable> 別表第三の二' in r.stdout


def test_cli_rejects_unknown_element(tmp_path):
    src = tmp_path / "in.xml"
    src.write_text(SAMPLE_XML, encoding='utf-8')
    r = subprocess.run([sys.executable, str(SCRIPT), str(src), str(tmp_path / 'out.xml'),
                        '--elements', 'Paragraph'], capture_output=True, text=True, timeout=60)
    assert r.returncode == 1
    assert '対象外の要素' in r.stderr


# ------------------------------------------------------------------
# ホーム画面のオプション
# ------------------------------------------------------------------
def test_home_has_appdxtable_num_option_default_off():
    pytest.importorskip("streamlit")
    from streamlit.testing.v1 import AppTest

    at = AppTest.from_file(str(HOME_PAGE), default_timeout=120).run()
    assert not at.exception, [str(e) for e in at.exception]
    label = "変換後に別表（AppdxTable）のNum属性を付与する"
    matches = [c for c in at.checkbox if c.label == label]
    assert len(matches) == 1
    assert matches[0].value is False
    assert at.session_state["apply_appdxtable_num"] is False
    assert at.session_state["appdxtable_num_mode"] == "title"
    assert at.session_state["appdxtable_num_overwrite"] is False

    matches[0].check().run()
    assert not at.exception, [str(e) for e in at.exception]
    assert at.session_state["apply_appdxtable_num"] is True

    radios = [r for r in at.radio if r.label == "付与方式"]
    assert len(radios) == 1
    radios[0].set_value("sequential").run()
    assert not at.exception, [str(e) for e in at.exception]
    assert at.session_state["appdxtable_num_mode"] == "sequential"
