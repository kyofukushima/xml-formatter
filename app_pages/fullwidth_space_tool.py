"""
文頭全角スペース補填の単独実行ページ

変換パイプラインを通さず、アップロードしたXMLに対して
文頭全角スペース補填（scripts/postprocess_fullwidth_space.py）のみを
単独で実行します。

- ファイル単位: XMLファイルを直接アップロード（複数選択可）
- フォルダ単位: フォルダをZIP化してアップロード（ZIP内のフォルダ階層を
  保ったまま補填後のXMLをZIPで返却。結果一覧には階層を列として表示）

対象: Title要素が空（または不在）のItem/Subitem1～10の先頭Sentence冒頭、
および LineBreak="true" のColumn内の先頭Sentence冒頭。
除外条件（数式・変数定義行・補填済み等）とオプションはメインページの補填機能と同一です。
"""
import sys
import zipfile
from io import BytesIO
from pathlib import Path

import pandas as pd
import streamlit as st
from lxml import etree

# プロジェクトルートをパスに追加
# （scripts/utils と utils/ の名前衝突を避けるため、プロジェクトルートを最優先にする）
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "scripts"))
sys.path.insert(0, str(project_root))

from batch_fullwidth_space import apply_fullwidth_space, output_name  # noqa: E402
from utils.upload_helpers import iter_uploaded_xml, split_upload_path  # noqa: E402

st.set_page_config(
    page_title="全角スペース補填実行 - XML変換パイプライン",
    page_icon="🈳",
    layout="wide"
)

st.title("🈳 文頭全角スペース補填の単独実行")

st.markdown(
    "変換パイプラインを通さず、アップロードしたXMLファイルに"
    "**文頭全角スペース補填のみ**を実行します。"
    "Title要素が空（または省略されている）`Item`/`Subitem1`～`Subitem10` の"
    "先頭Sentence冒頭、および `LineBreak=\"true\"` のColumn内Sentence冒頭に"
    "全角スペース（U+3000）を挿入します。"
    "既に全角スペースで始まるSentenceには挿入しないため、再実行しても安全です。"
    "複数ファイルをまとめて処理する場合は、XMLを複数選択するか、"
    "**フォルダをZIP化してアップロード**してください（フォルダ階層を保った"
    "ままZIPで返却します）。"
)
try:
    st.page_link(
        "app_pages/fullwidth_space_settings.py",
        label="補填条件のXML例を確認する",
        icon="🔤"
    )
except Exception:
    pass

st.markdown("---")

# ------------------------------------------------------------------
# オプション
# ------------------------------------------------------------------
st.header("⚙️ オプション")

include_list = st.checkbox(
    "List内のSentenceも対象にする",
    value=False,
    help="List/ListSentence内のSentence冒頭にも全角スペースを挿入します"
         "（整備方針資料上「要確認」のためデフォルトは対象外）"
)
exclude_paren = st.checkbox(
    "「（」で始まるSentenceは対象外にする",
    value=False,
    help="「（注）…」等の括弧書きで始まるSentenceに全角スペースを挿入しません。"
         "括弧書きを字下げするかどうかは告示ごとの官報体裁に合わせて選択してください。"
)
include_vardef = st.checkbox(
    "変数定義行（「Ｅ：…」等の短い記号列）も対象にする",
    value=False,
    help="「Ｅ：ガス消費量…」「ＥＭ＝αＭ×Ａ…」のように短い記号列＋「：」「＝」で始まる"
         "変数定義行・数式行にも全角スペースを挿入します。"
         "官報体裁では字下げしないことが多いためデフォルトは対象外です。"
)
keep_names = st.checkbox(
    "出力ファイル名を元のままにする（「_space」を付けない）",
    value=False,
    help="OFFの場合、補填後のファイル名は「元のファイル名_space.xml」になります。"
         "ONにすると元のファイル名のまま出力するため、元フォルダへそのまま"
         "上書き配置できます。"
)

st.markdown("---")

# ------------------------------------------------------------------
# ファイルアップロードと実行
# ------------------------------------------------------------------
st.header("📁 XMLファイルのアップロード")

upload_mode = st.segmented_control(
    "アップロード方法",
    options=["ファイル選択（複数可）", "ZIPアップロード（フォルダごと）"],
    default="ファイル選択（複数可）",
    help="フォルダごと補填したい場合は、フォルダをZIP化してアップロード"
         "してください。ZIP内のフォルダ階層を保ったまま補填後のXMLを"
         "ZIPで返却します。"
)
is_zip_mode = (upload_mode == "ZIPアップロード（フォルダごと）")

if is_zip_mode:
    st.caption(
        "フォルダを右クリック→「圧縮」等でZIP化し、そのZIPファイルを"
        "アップロードしてください（ドラッグ＆ドロップ可、複数ZIP可）。"
        "ZIP内のXMLファイル（サブフォルダを含む）が補填対象になります。"
        "XML以外のファイルは出力に含まれません。"
    )
    uploaded_files = st.file_uploader(
        "補填対象のZIPファイルを選択してください",
        type=['zip'],
        accept_multiple_files=True,
        key="standalone_space_uploader_zip"
    )
else:
    uploaded_files = st.file_uploader(
        "補填対象のXMLファイルを選択してください（複数選択可）",
        type=['xml'],
        accept_multiple_files=True,
        key="standalone_space_uploader"
    )


def run_batch(files, is_zip_mode, include_list, exclude_paren,
              include_vardef, keep_names):
    """アップロードされたファイル群に補填を適用し、結果行と出力の一覧を返す"""
    rows = []
    outputs = []  # (source, 出力パス, バイト列)
    for source, path_name, data, error in iter_uploaded_xml(files, is_zip_mode):
        folders, file_name = split_upload_path(path_name) if path_name \
            else ([], "")
        row = {
            "_source": source,
            "_folders": folders,
            "ファイル名": file_name,
            "結果": "",
            "対象Sentence数": None,
            "補填実施": None,
            "「（」始まりで除外": None,
            "変数定義行で除外": None,
            "備考": "",
        }
        if error is not None:
            row["結果"] = "エラー"
            row["備考"] = error
            rows.append(row)
            continue
        try:
            result_bytes, stats = apply_fullwidth_space(
                data, include_list, exclude_paren, include_vardef
            )
        except etree.XMLSyntaxError as e:
            row["結果"] = "解析エラー"
            row["備考"] = f"XML解析エラー: {e}"
            rows.append(row)
            continue
        row["結果"] = "補填あり" if stats["changed"] else "補填なし"
        row["対象Sentence数"] = stats["targets"]
        row["補填実施"] = stats["changed"]
        row["「（」始まりで除外"] = stats["excluded_parens"]
        row["変数定義行で除外"] = stats["excluded_vardefs"]
        rows.append(row)
        out_path = "/".join(folders + [output_name(file_name, keep_names)])
        outputs.append((source, out_path, result_bytes))
    return rows, outputs


if uploaded_files:
    if st.button("🈳 全角スペース補填を実行", type="primary"):
        with st.spinner("文頭全角スペースを補填中..."):
            rows, outputs = run_batch(
                uploaded_files, is_zip_mode, include_list, exclude_paren,
                include_vardef, keep_names
            )
        st.session_state.standalone_space_result = {
            "is_zip_mode": is_zip_mode,
            "sources": [f.name for f in uploaded_files],
            "rows": rows,
            "outputs": outputs,
        }

# ------------------------------------------------------------------
# 結果表示とダウンロード
# ------------------------------------------------------------------
result = st.session_state.get("standalone_space_result")
if result is not None:
    rows = result["rows"]
    outputs = result["outputs"]
    st.markdown("---")
    st.header("📊 実行結果")

    ok_rows = [r for r in rows if r["結果"] in ("補填あり", "補填なし")]
    error_rows = [r for r in rows if r["結果"] not in ("補填あり", "補填なし")]
    total_targets = sum(r["対象Sentence数"] or 0 for r in ok_rows)
    total_changed = sum(r["補填実施"] or 0 for r in ok_rows)
    total_parens = sum(r["「（」始まりで除外"] or 0 for r in ok_rows)
    total_vardefs = sum(r["変数定義行で除外"] or 0 for r in ok_rows)

    if len(rows) == 1 and ok_rows:
        st.success(
            f"✅ 補填が完了しました（対象ファイル: {ok_rows[0]['ファイル名']}）")
    elif ok_rows:
        st.success(
            f"✅ 補填が完了しました（処理ファイル数: {len(ok_rows)}件"
            + (f"、エラー: {len(error_rows)}件" if error_rows else "")
            + "）"
        )
    else:
        st.error("❌ 補填できたファイルがありません。備考欄を確認してください。")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("対象Sentence数", f"{total_targets}箇所")
    col2.metric("補填実施", f"{total_changed}箇所")
    col3.metric("「（」始まりで除外", f"{total_parens}箇所")
    col4.metric("変数定義行で除外", f"{total_vardefs}箇所")

    if ok_rows and total_changed == 0:
        st.info(
            "補填された箇所はありません（対象がない、または"
            "すべて補填済み・除外条件に該当）。"
        )

    # 複数ファイルのときはファイルごとの結果一覧を表示する
    if len(rows) > 1 or result["is_zip_mode"]:
        max_depth = max(len(r["_folders"]) for r in rows)
        show_source = result["is_zip_mode"] and len(result["sources"]) > 1
        records = []
        for r in rows:
            record = {}
            if show_source:
                record["ZIPファイル"] = r["_source"]
            for i in range(max_depth):
                record[f"階層{i + 1}"] = (
                    r["_folders"][i] if i < len(r["_folders"]) else ""
                )
            for key in ["ファイル名", "結果", "対象Sentence数", "補填実施",
                        "「（」始まりで除外", "変数定義行で除外", "備考"]:
                record[key] = r[key]
            records.append(record)
        df = pd.DataFrame(records)
        sort_cols = (["ZIPファイル"] if show_source else []) \
            + [f"階層{i + 1}" for i in range(max_depth)] + ["ファイル名"]
        df = df.sort_values(sort_cols, kind='stable').reset_index(drop=True)

        st.subheader("📋 ファイルごとの結果")
        if max_depth > 0:
            st.caption(
                "「階層1」以降の列はZIP内のフォルダ階層です"
                "（フォルダ階層の深さに応じて列が追加されます）。"
            )
        st.dataframe(df, width="stretch", hide_index=True)
        if error_rows:
            st.warning(
                "⚠️ エラーのファイルがあります。備考欄の内容を確認してください。"
                "エラーのファイルは出力に含まれません。"
            )
        csv_bytes = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 ファイルごとの結果をCSVでダウンロード",
            data=csv_bytes,
            file_name="fullwidth_space_result.csv",
            mime="text/csv"
        )
    elif error_rows:
        st.error(f"❌ {error_rows[0]['備考']}")

    # ダウンロード: 1ファイルならXMLをそのまま、複数ならZIPにまとめる
    if len(outputs) == 1 and not result["is_zip_mode"]:
        _, out_path, data = outputs[0]
        st.download_button(
            label="📥 補填後のXMLファイルをダウンロード",
            data=data,
            file_name=out_path,
            mime="application/xml"
        )
    elif outputs:
        zip_buffer = BytesIO()
        multi_source = len(result["sources"]) > 1
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            for source, out_path, data in outputs:
                # 複数ZIPをまとめて処理した場合はZIP名ごとのフォルダに分ける
                if result["is_zip_mode"] and multi_source:
                    out_path = f"{Path(source).stem}/{out_path}"
                zf.writestr(out_path, data)
        if result["is_zip_mode"] and not multi_source:
            zip_name = f"{Path(result['sources'][0]).stem}_space.zip"
        else:
            zip_name = "fullwidth_space_output.zip"
        st.download_button(
            label=f"📥 補填後のXMLファイルをZIPでダウンロード（{len(outputs)}件）",
            data=zip_buffer.getvalue(),
            file_name=zip_name,
            mime="application/zip"
        )

    if outputs:
        show_preview = st.checkbox("📄 補填後のXMLをプレビュー", value=False)
        if show_preview:
            if len(outputs) == 1:
                selected = outputs[0]
            else:
                labels = [
                    (f"{src} / {path}" if src else path)
                    for src, path, _ in outputs
                ]
                idx = st.selectbox(
                    "プレビューするファイル",
                    options=range(len(outputs)),
                    format_func=lambda i: labels[i]
                )
                selected = outputs[idx]
            preview_text = selected[2].decode('utf-8')
            lines = preview_text.splitlines()
            max_lines = 500
            with st.expander(f"📄 補填後のXMLのプレビュー（{selected[1]}）",
                             expanded=True):
                st.code('\n'.join(lines[:max_lines]), language='xml')
                if len(lines) > max_lines:
                    st.caption(
                        f"（先頭{max_lines}行のみ表示。全{len(lines)}行）")
