"""
納品前検証ページ

変換前・変換後のXMLファイルをアップロードし、ホーム（パイプライン処理）の
変換後に自動実行される検証と同じ検証を単独で実行します。

検証内容（scripts/compare_xml_text_content.py）:
- テキスト内容の欠落検証（変換前の全テキスト要素が変換後にも存在するか）
- 表（Table）の数と内容順序の検証
"""
import sys
import tempfile
from pathlib import Path

import streamlit as st

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.validation import (  # noqa: E402
    validate_text_content,
    format_validation_report,
)

st.set_page_config(
    page_title="納品前検証 - XML変換パイプライン",
    page_icon="✅",
    layout="wide"
)

st.title("✅ 納品前検証")

st.markdown(
    "変換前と変換後のXMLファイルを比較し、**テキスト内容の欠落**と"
    "**表（Table）の数・順序の変更**がないかを検証します。"
    "ホーム（パイプライン処理）で変換後に自動実行される検証と同じ内容を、"
    "任意のファイルの組み合わせに対して単独で実行できます。"
)

st.markdown("---")

st.header("📁 検証対象ファイルのアップロード")

col_before, col_after = st.columns(2)
with col_before:
    original_file = st.file_uploader(
        "変換前のXMLファイル",
        type=['xml'],
        key="delivery_check_original",
        help="変換パイプラインに入力した元のXMLファイル"
    )
with col_after:
    converted_file = st.file_uploader(
        "変換後のXMLファイル",
        type=['xml'],
        key="delivery_check_converted",
        help="変換パイプラインの出力（納品予定）のXMLファイル。"
             "全角スペース補填を適用している場合は、補填による差分が"
             "欠落として検出されないよう補填前のファイルを推奨します。"
    )

st.subheader("⚙️ 検証オプション")
ignore_spaces = st.checkbox(
    "全角・半角スペースの有無を無視して比較する",
    value=False,
    help="ONにすると、テキスト中の全角スペース（U+3000）と半角スペースを"
         "すべて除去してから比較します。全角スペース補填を適用した後の"
         "ファイルを検証する場合など、スペースの違いを欠落として検出したく"
         "ないときにONにしてください。OFFの場合、文頭・文末のスペースは"
         "無視されますが、文中のスペースの違いは不一致として検出されます。"
)

both_ready = original_file is not None and converted_file is not None
if not both_ready:
    st.info("変換前・変換後の両方のXMLファイルをアップロードしてください。")

if st.button("🔍 検証を実行", type="primary", disabled=not both_ready):
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        original_path = tmp / f"original_{original_file.name}"
        converted_path = tmp / f"converted_{converted_file.name}"
        original_path.write_bytes(original_file.getvalue())
        converted_path.write_bytes(converted_file.getvalue())

        with st.spinner("検証を実行中..."):
            is_valid, error_msg, output, report_data = validate_text_content(
                original_path,
                converted_path,
                project_root / "scripts" / "compare_xml_text_content.py",
                extra_args=['--ignore-spaces'] if ignore_spaces else None
            )

    st.session_state.delivery_check_result = {
        "original_name": original_file.name,
        "converted_name": converted_file.name,
        "ignore_spaces": ignore_spaces,
        "is_valid": is_valid,
        "error": error_msg,
        "output": output,
        "report_data": report_data,
    }

result = st.session_state.get("delivery_check_result")
if result is not None:
    st.markdown("---")
    st.header("📊 検証結果")
    space_mode = "無視する" if result.get("ignore_spaces") else "無視しない（文中のスペースは比較対象）"
    st.markdown(
        f"- 変換前: **{result['original_name']}**\n"
        f"- 変換後: **{result['converted_name']}**\n"
        f"- スペースの有無: **{space_mode}**"
    )

    if result["is_valid"]:
        st.success("✅ 検証に成功しました。テキスト内容は一致しています。")
        if result.get("report_data"):
            with st.expander("検証結果の詳細", expanded=False):
                st.text(format_validation_report(result["report_data"]))
    else:
        st.error(
            f"❌ {result.get('error') or 'テキスト内容の不一致が検出されました'}"
        )
        if result.get("report_data"):
            with st.expander("検証結果の詳細", expanded=True):
                st.text(format_validation_report(result["report_data"]))
                if result["report_data"].get("errors"):
                    st.error(
                        f"**エラー数**: {len(result['report_data']['errors'])}"
                    )

    # 検証レポートのダウンロード
    report_text = None
    if result.get("report_data") and result["report_data"].get("content"):
        report_text = format_validation_report(result["report_data"])
    elif result.get("output"):
        report_text = result["output"]
    if report_text:
        stem = Path(result["converted_name"]).stem
        st.download_button(
            label="📥 検証レポートをダウンロード",
            data=report_text.encode('utf-8-sig'),
            file_name=f"{stem}_検証レポート.txt",
            mime="text/plain"
        )
