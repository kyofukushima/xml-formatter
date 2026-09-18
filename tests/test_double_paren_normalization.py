"""
二重パーレン（((N))）の丸数字正規化に関するテスト

- scripts/normalize_double_paren.py の変換関数
- 拡張した丸数字ラベル（㉑〜㊿）の判定
- ホーム画面のオプション（チェックボックスとセッション状態）
"""
import importlib.util
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
HOME_PAGE = PROJECT_ROOT / "app_pages" / "home.py"

_spec = importlib.util.spec_from_file_location(
    "normalize_double_paren", SCRIPTS_DIR / "normalize_double_paren.py")
ndp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ndp)



def _detect_label(text):
    """scripts/utils/label_utils の判定結果を返す

    scripts/ を sys.path に入れると、プロジェクト直下の utils パッケージ
    （Webアプリ用）と衝突して他のテストの home.py 読み込みが壊れるため、
    サブプロセスで判定する。
    """
    import json
    import subprocess
    code = (
        "import json, sys\n"
        "from utils.label_utils import detect_label_id, is_label\n"
        "t = sys.argv[1]\n"
        "print(json.dumps({'is_label': is_label(t), 'id': detect_label_id(t)}))\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", code, text],
        cwd=str(SCRIPTS_DIR), capture_output=True, text=True, timeout=60,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout.strip().splitlines()[-1])


# ------------------------------------------------------------------
# 変換関数
# ------------------------------------------------------------------
@pytest.mark.parametrize("n, expected", [
    (1, "①"), (20, "⑳"), (21, "㉑"), (35, "㉟"), (36, "㊱"), (50, "㊿"),
])
def test_circled_number_boundaries(n, expected):
    assert ndp.circled_number(n) == expected


@pytest.mark.parametrize("n", [0, 51, 100, -1])
def test_circled_number_out_of_range(n):
    assert ndp.circled_number(n) is None


@pytest.mark.parametrize("text, expected", [
    ("（（２１））", "㉑"),
    ("((21))", "㉑"),
    ("（(２)）", "②"),
    ("( ( 3 ) )", "③"),
    ("（（　４　））", "④"),
    ("（（２１））及び（（２２））", "㉑及び㉒"),
])
def test_normalize_text_converts(text, expected):
    assert ndp.normalize_text(text) == expected


@pytest.mark.parametrize("text", [
    "（（０））", "（（５１））", "（（１２３））", "（（ア））", "（１）", "本文のみ", "", None,
])
def test_normalize_text_leaves_unchanged(text):
    assert ndp.normalize_text(text) == text


def test_normalize_text_is_idempotent():
    once = ndp.normalize_text("（（２１））と((5))")
    assert ndp.normalize_text(once) == once == "㉑と⑤"


def test_normalize_text_records_stats():
    stats = ndp.new_stats()
    ndp.normalize_text("（（２１））、（（２１））、（（５１））", stats)
    assert stats["replaced"] == 2
    assert stats["pairs"][("（（２１））", "㉑")] == 2
    assert stats["skipped"]["（（５１））"] == 1


# ------------------------------------------------------------------
# ラベル判定（㉑〜㊿ が丸数字として扱われること）
# ------------------------------------------------------------------
@pytest.mark.parametrize("label", ["①", "⑳", "㉑", "㉟", "㊱", "㊿"])
def test_extended_circled_numbers_detected_as_label(label):
    result = _detect_label(label)
    assert result["is_label"] is True
    assert result["id"] == "circled_number"


def test_double_paren_labels_still_detected():
    assert _detect_label("（（２１））")["id"] == "double_paren_fullwidth_number"
    assert _detect_label("((21))")["id"] == "double_paren_halfwidth_number"


# ------------------------------------------------------------------
# ホーム画面のオプション
# ------------------------------------------------------------------
def test_home_has_normalize_option_default_off():
    pytest.importorskip("streamlit")
    from streamlit.testing.v1 import AppTest

    at = AppTest.from_file(str(HOME_PAGE), default_timeout=120).run()
    assert not at.exception, [str(e) for e in at.exception]
    label = "二重パーレン（((N))）を丸数字に正規化する"
    matches = [c for c in at.checkbox if c.label == label]
    assert len(matches) == 1
    assert matches[0].value is False
    assert at.session_state["normalize_double_paren"] is False

    matches[0].check().run()
    assert not at.exception
    assert at.session_state["normalize_double_paren"] is True
