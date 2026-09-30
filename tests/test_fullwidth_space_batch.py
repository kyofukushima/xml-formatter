"""
文頭全角スペース補填ページの複数ファイル・ZIP一括処理のテスト

utils/upload_helpers.py のZIP展開と、fullwidth_space_tool.py の
run_batch（複数XML / ZIP / エラー混在）を検証する。
"""
import importlib
import sys
import zipfile
from io import BytesIO
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent

XML = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<Law><Item Num="1"><ItemTitle/><ItemSentence>'
    '<Sentence>本文です。</Sentence></ItemSentence></Item>'
    '<Item Num="2"><ItemTitle/><ItemSentence>'
    '<Sentence>（注）括弧です。</Sentence></ItemSentence></Item></Law>'
).encode('utf-8')


class FakeUpload:
    def __init__(self, name, data):
        self.name = name
        self._data = data

    def getvalue(self):
        return self._data


def make_zip(entries):
    buf = BytesIO()
    with zipfile.ZipFile(buf, 'w') as zf:
        for name, data in entries.items():
            zf.writestr(name, data)
    return buf.getvalue()


@pytest.fixture(scope="module")
def tool():
    pytest.importorskip("streamlit")
    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
    sys.path.insert(0, str(PROJECT_ROOT))
    return importlib.import_module("app_pages.fullwidth_space_tool")


def test_iter_uploaded_xml_skips_non_xml_and_macosx():
    from utils.upload_helpers import iter_uploaded_xml
    data = make_zip({
        "告示/R04/a.xml": XML,
        "告示/memo.txt": b"x",
        "__MACOSX/告示/._a.xml": b"x",
        "告示/.hidden.xml": b"x",
    })
    items = list(iter_uploaded_xml([FakeUpload("告示.zip", data)], True))
    assert [(src, path) for src, path, _, err in items] == [("告示.zip", "告示/R04/a.xml")]
    assert all(err is None for *_, err in items)


def test_iter_uploaded_xml_reports_zip_errors():
    from utils.upload_helpers import iter_uploaded_xml
    files = [
        FakeUpload("broken.zip", b"not a zip"),
        FakeUpload("empty.zip", make_zip({"x/readme.txt": b"a"})),
    ]
    items = list(iter_uploaded_xml(files, True))
    assert [err for *_, err in items] == [
        "ZIPファイルとして読み込めません", "ZIP内にXMLファイルがありません"]


def test_run_batch_multiple_xml_files(tool):
    files = [
        FakeUpload("a.xml", XML),
        FakeUpload("b.xml", XML),
        FakeUpload("bad.xml", b"<x>"),
    ]
    rows, outputs = tool.run_batch(files, False, False, True, False, False)
    assert [r["結果"] for r in rows] == ["補填あり", "補填あり", "解析エラー"]
    assert rows[0]["対象Sentence数"] == 2
    assert rows[0]["補填実施"] == 1
    assert rows[0]["「（」始まりで除外"] == 1
    assert [path for _, path, _ in outputs] == ["a_space.xml", "b_space.xml"]
    assert "<Sentence>　本文です。</Sentence>" in outputs[0][2].decode('utf-8')
    assert "<Sentence>（注）括弧です。</Sentence>" in outputs[0][2].decode('utf-8')


def test_run_batch_zip_keeps_folder_hierarchy(tool):
    data = make_zip({"告示/R04/a.xml": XML, "告示/b.xml": XML})
    rows, outputs = tool.run_batch(
        [FakeUpload("告示.zip", data)], True, False, False, False, True)
    assert [(r["_folders"], r["ファイル名"], r["結果"]) for r in rows] == [
        (["告示", "R04"], "a.xml", "補填あり"),
        (["告示"], "b.xml", "補填あり"),
    ]
    # 出力ファイル名を元のままにする（keep_names=True）と階層もそのまま
    assert [path for _, path, _ in outputs] == ["告示/R04/a.xml", "告示/b.xml"]
    # 括弧始まり除外なしなので2箇所とも補填される
    assert rows[0]["補填実施"] == 2


def test_run_batch_zip_default_adds_space_suffix(tool):
    data = make_zip({"告示/a.xml": XML})
    _, outputs = tool.run_batch(
        [FakeUpload("告示.zip", data)], True, False, False, False, False)
    assert [path for _, path, _ in outputs] == ["告示/a_space.xml"]


def test_decode_zip_name_prefers_utf8_without_flag():
    """macOSのzipコマンドはUTF-8フラグなしでUTF-8名を書くため、UTF-8を優先する"""
    from utils.upload_helpers import decode_zip_name
    info = zipfile.ZipInfo("dummy")
    info.flag_bits = 0
    info.filename = "in/告示/a.xml".encode('utf-8').decode('cp437')
    assert decode_zip_name(info) == "in/告示/a.xml"
    info.filename = "in/告示/a.xml".encode('cp932').decode('cp437')
    assert decode_zip_name(info) == "in/告示/a.xml"


def test_cli_batch_folder_to_folder(tmp_path):
    """CLI: フォルダ入力 → 既定の <入力名>_space フォルダに階層を保って出力"""
    import subprocess
    src = tmp_path / "in" / "告示" / "R04"
    src.mkdir(parents=True)
    (src / "a.xml").write_bytes(XML)
    (tmp_path / "in" / "告示" / "bad.xml").write_bytes(b"<x>")
    csv_path = tmp_path / "result.csv"
    proc = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "scripts" / "batch_fullwidth_space.py"),
         str(tmp_path / "in"), "--exclude-paren", "--csv", str(csv_path)],
        capture_output=True, text=True, cwd=PROJECT_ROOT
    )
    assert proc.returncode == 2, proc.stderr  # 解析エラーが1件あるため
    out = tmp_path / "in_space" / "告示" / "R04" / "a_space.xml"
    assert out.exists()
    assert "<Sentence>　本文です。</Sentence>" in out.read_text('utf-8')
    assert "（注）括弧です。" in out.read_text('utf-8')
    assert not (tmp_path / "in_space" / "告示" / "bad_space.xml").exists()
    assert "補填実施: 1箇所" in proc.stdout
    assert "告示/R04/a.xml,補填あり,2,1,1,0" in csv_path.read_text('utf-8-sig')


def test_cli_batch_zip_to_zip_keep_names(tmp_path):
    """CLI: ZIP入力 → ZIP出力（--keep-names で元の名前・階層のまま）"""
    import subprocess
    src_zip = tmp_path / "告示.zip"
    src_zip.write_bytes(make_zip({"告示/R04/a.xml": XML, "告示/b.xml": XML}))
    out_zip = tmp_path / "out.zip"
    proc = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "scripts" / "batch_fullwidth_space.py"),
         str(src_zip), "-o", str(out_zip), "--keep-names"],
        capture_output=True, text=True, cwd=PROJECT_ROOT
    )
    assert proc.returncode == 0, proc.stderr
    with zipfile.ZipFile(out_zip) as zf:
        assert sorted(zf.namelist()) == ["告示/R04/a.xml", "告示/b.xml"]
        assert "　本文です。" in zf.read("告示/b.xml").decode('utf-8')
