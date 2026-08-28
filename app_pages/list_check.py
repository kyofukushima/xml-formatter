"""
List要素判定ページ

アップロードしたXMLファイルにList要素が含まれているかを判定し、
含まれている場合はその個数を表示します。

- ファイル単位: XMLファイルを直接アップロード（複数選択可）
- フォルダ単位: フォルダをZIP化してアップロード（ZIP内のフォルダ階層を
  「階層1」「階層2」…の列に分けて表示。階層の深さに応じて列を追加）

結果一覧はCSVとしてダウンロードできます。
"""
import zipfile
from io import BytesIO

import pandas as pd
import streamlit as st
from lxml import etree

st.set_page_config(
    page_title="List有無判定 - XML変換パイプライン",
    page_icon="📊",
    layout="wide"
)

st.title("📊 List有無判定")

st.markdown(
    "アップロードしたXMLファイルに `List` 要素が含まれているかを判定し、"
    "含まれている場合はその個数を表示します。"
    "フォルダ単位で判定する場合は**フォルダをZIP化してアップロード**すると、"
    "フォルダ階層が結果一覧に表示されます。結果一覧はCSVとして"
    "ダウンロードできます。"
)

st.markdown("---")

st.header("📁 アップロード")

upload_mode = st.segmented_control(
    "アップロード方法",
    options=["ファイル選択（複数可）", "ZIPアップロード（フォルダごと）"],
    default="ファイル選択（複数可）",
    help="フォルダごと判定したい場合は、フォルダをZIP化してアップロード"
         "してください。ZIP内のフォルダ階層が結果一覧に表示されます。"
)

if upload_mode == "ZIPアップロード（フォルダごと）":
    st.caption(
        "フォルダを右クリック→「圧縮」等でZIP化し、そのZIPファイルを"
        "アップロードしてください（ドラッグ＆ドロップ可、複数ZIP可）。"
        "ZIP内のXMLファイル（サブフォルダを含む）が判定対象になります。"
    )
    uploaded_files = st.file_uploader(
        "判定対象のZIPファイルを選択してください",
        type=['zip'],
        accept_multiple_files=True,
        key="list_check_uploader_zip"
    )
else:
    uploaded_files = st.file_uploader(
        "判定対象のXMLファイルを選択してください（複数選択可）",
        type=['xml'],
        accept_multiple_files=True,
        key="list_check_uploader_files"
    )


def split_upload_path(name):
    """パスをフォルダ階層とファイル名に分解する"""
    parts = name.replace('\\', '/').split('/')
    parts = [p for p in parts if p]
    if not parts:
        return [], name
    return parts[:-1], parts[-1]


def decode_zip_name(info):
    """ZIP内のファイル名を正しい文字コードで取得する

    ZIPの仕様上、UTF-8フラグが立っていないエントリ名はcp437として
    デコードされるため、日本語名（Windowsで作成されたZIPはcp932）を
    復元する。
    """
    if info.flag_bits & 0x800:  # UTF-8フラグ
        return info.filename
    try:
        raw = info.filename.encode('cp437')
    except UnicodeEncodeError:
        return info.filename
    for encoding in ('cp932', 'utf-8'):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return info.filename


def is_target_zip_entry(name):
    """ZIP内エントリが判定対象のXMLファイルかどうか"""
    if name.endswith('/'):
        return False
    parts = [p for p in name.replace('\\', '/').split('/') if p]
    if not parts:
        return False
    # macOSのメタデータ・隠しファイルを除外
    if any(p == '__MACOSX' for p in parts):
        return False
    if parts[-1].startswith('._') or parts[-1].startswith('.'):
        return False
    return parts[-1].lower().endswith('.xml')


def analyze_xml_data(path_name, data, source=""):
    """1ファイル分のXMLデータを解析してList要素の判定結果を返す"""
    folders, file_name = split_upload_path(path_name)
    row = {
        "_source": source,
        "_folders": folders,
        "ファイル名": file_name,
        "判定": "",
        "List要素数": 0,
        "うちColumnなし": 0,
        "備考": "",
    }
    try:
        tree = etree.parse(BytesIO(data))
    except etree.XMLSyntaxError as e:
        row["判定"] = "解析エラー"
        row["List要素数"] = None
        row["うちColumnなし"] = None
        row["備考"] = f"XML解析エラー: {e}"
        return row

    lists = list(tree.getroot().iter('List'))
    row["List要素数"] = len(lists)
    row["判定"] = "あり" if lists else "なし"
    row["うちColumnなし"] = sum(
        1 for l in lists if l.find('.//Column') is None
    )
    return row


def collect_rows(files, is_zip_mode):
    """アップロードされたファイルから判定結果の行を収集する"""
    rows = []
    for uploaded in files:
        if not is_zip_mode:
            rows.append(analyze_xml_data(uploaded.name, uploaded.getvalue()))
            continue
        try:
            with zipfile.ZipFile(BytesIO(uploaded.getvalue())) as zf:
                xml_entries = [
                    info for info in zf.infolist()
                    if is_target_zip_entry(decode_zip_name(info))
                ]
                if not xml_entries:
                    rows.append({
                        "_source": uploaded.name, "_folders": [],
                        "ファイル名": "", "判定": "対象なし",
                        "List要素数": None, "うちColumnなし": None,
                        "備考": "ZIP内にXMLファイルがありません",
                    })
                    continue
                for info in xml_entries:
                    rows.append(analyze_xml_data(
                        decode_zip_name(info), zf.read(info),
                        source=uploaded.name
                    ))
        except zipfile.BadZipFile:
            rows.append({
                "_source": uploaded.name, "_folders": [],
                "ファイル名": "", "判定": "解析エラー",
                "List要素数": None, "うちColumnなし": None,
                "備考": "ZIPファイルとして読み込めません",
            })
    return rows


if uploaded_files:
    is_zip_mode = (upload_mode == "ZIPアップロード（フォルダごと）")
    rows = collect_rows(uploaded_files, is_zip_mode)

    # フォルダ階層の最大深さに応じて「階層N」列を作成する
    max_depth = max(len(r["_folders"]) for r in rows)
    show_source = is_zip_mode and len(uploaded_files) > 1
    records = []
    for r in rows:
        record = {}
        if show_source:
            record["ZIPファイル"] = r["_source"]
        for i in range(max_depth):
            record[f"階層{i + 1}"] = (
                r["_folders"][i] if i < len(r["_folders"]) else ""
            )
        for key in ["ファイル名", "判定", "List要素数", "うちColumnなし", "備考"]:
            record[key] = r[key]
        records.append(record)
    df = pd.DataFrame(records)

    # ZIPファイル→フォルダ階層→ファイル名の順に並べる
    sort_cols = (["ZIPファイル"] if show_source else []) \
        + [f"階層{i + 1}" for i in range(max_depth)] + ["ファイル名"]
    df = df.sort_values(sort_cols, kind='stable').reset_index(drop=True)

    st.markdown("---")
    st.header("📊 判定結果")

    xml_rows = [r for r in rows if r["判定"] in ("あり", "なし", "解析エラー")]
    total = len(xml_rows)
    with_list = sum(1 for r in xml_rows if r["判定"] == "あり")
    errors = sum(1 for r in rows if r["判定"] == "解析エラー")
    total_lists = sum(r["List要素数"] or 0 for r in rows)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("判定ファイル数", f"{total}件")
    col2.metric("List要素あり", f"{with_list}件")
    col3.metric("List要素数の合計", f"{total_lists}個")
    col4.metric("解析エラー", f"{errors}件")

    if max_depth > 0:
        st.caption(
            "「階層1」以降の列はZIP内のフォルダ階層です"
            "（フォルダ階層の深さに応じて列が追加されます）。"
        )
    st.dataframe(df, width="stretch", hide_index=True)

    if errors:
        st.warning(
            "⚠️ 解析エラーのファイルがあります。備考欄のエラー内容を"
            "確認してください。"
        )

    # CSVダウンロード（ExcelでもCP932環境でも文字化けしないようBOM付きUTF-8）
    csv_bytes = df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 判定結果をCSVでダウンロード",
        data=csv_bytes,
        file_name="list_element_check.csv",
        mime="text/csv"
    )
else:
    st.info(
        "XMLファイルまたはZIPファイルをアップロードすると判定結果が"
        "表示されます。"
    )
