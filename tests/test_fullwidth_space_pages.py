"""
文頭全角スペース補填の Web ページに関するテスト

「変数定義行（「Ｅ：…」等の短い記号列）も対象にする」オプションが
各ページに存在し、切り替えるとセッション状態と補填結果が変わることを
Streamlit の AppTest で検証する。
"""
from pathlib import Path

import pytest

pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest  # noqa: E402

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SETTINGS_PAGE = PROJECT_ROOT / "app_pages" / "fullwidth_space_settings.py"
TOOL_PAGE = PROJECT_ROOT / "app_pages" / "fullwidth_space_tool.py"
HOME_PAGE = PROJECT_ROOT / "app_pages" / "home.py"

VARDEF_LABEL_SETTINGS = "変数定義行・数式行にも補填する"
VARDEF_LABEL_SIDEBAR = "変数定義行（「Ｅ：…」等の短い記号列）も対象にする"


def _checkbox(at, label):
    matches = [c for c in at.checkbox if c.label == label]
    assert len(matches) == 1, f"チェックボックスが見つかりません: {label}"
    return matches[0]


def _run(page):
    at = AppTest.from_file(str(page), default_timeout=120).run()
    assert not at.exception, [str(e) for e in at.exception]
    return at


def test_settings_page_has_vardef_option_default_off():
    at = _run(SETTINGS_PAGE)
    cb = _checkbox(at, VARDEF_LABEL_SETTINGS)
    assert cb.value is False
    assert at.session_state["fullwidth_space_include_vardef"] is False


def test_settings_page_vardef_example_changes_with_option():
    at = _run(SETTINGS_PAGE)
    # 補填を有効化した上で、変数定義行オプションをOFF→ONに切り替える
    _checkbox(at, "変換後に文頭全角スペースを補填する").check().run()
    assert not at.exception

    def vardef_example_after():
        # 変数定義行のXML例（補填後）を含む code ブロックを探す
        blocks = [c.value for c in at.code if "Ｅ：ガス消費量" in c.value]
        assert blocks, "変数定義行のXML例が表示されていません"
        return blocks

    before, after = vardef_example_after()[:2]
    assert "　Ｅ：ガス消費量" not in before
    assert "　Ｅ：ガス消費量" not in after, "OFF時は変数定義行に補填されないはず"

    _checkbox(at, VARDEF_LABEL_SETTINGS).check().run()
    assert not at.exception
    assert at.session_state["fullwidth_space_include_vardef"] is True
    before, after = vardef_example_after()[:2]
    assert "　Ｅ：ガス消費量" not in before
    assert "　Ｅ：ガス消費量" in after, "ON時は変数定義行に補填されるはず"
    assert "　Ｖｇ：庫内容積" in after.replace("<Sub>", "").replace("</Sub>", "")
    assert "　ＥＭ＝αＭ×Ａ" in after


def test_tool_page_has_vardef_option_default_off():
    at = _run(TOOL_PAGE)
    cb = _checkbox(at, VARDEF_LABEL_SIDEBAR)
    assert cb.value is False


def test_home_sidebar_has_vardef_option_and_syncs_session_state():
    at = _run(HOME_PAGE)
    cb = _checkbox(at, VARDEF_LABEL_SIDEBAR)
    assert cb.value is False
    assert at.session_state["fullwidth_space_include_vardef"] is False

    cb.check().run()
    assert not at.exception
    assert at.session_state["fullwidth_space_include_vardef"] is True


def test_settings_and_home_share_vardef_state():
    """設定ページでONにした値がセッション状態に保存される（ホームと共有）"""
    at = _run(SETTINGS_PAGE)
    _checkbox(at, "変換後に文頭全角スペースを補填する").check().run()
    _checkbox(at, VARDEF_LABEL_SETTINGS).check().run()
    assert at.session_state["fullwidth_space_include_vardef"] is True
    assert "変数定義行も対象: **ON**" in "".join(m.value for m in at.markdown)
