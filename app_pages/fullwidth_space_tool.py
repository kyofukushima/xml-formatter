"""
文頭全角スペース補填の単独実行ページ

変換パイプラインを通さず、アップロードしたXMLに対して
文頭全角スペース補填（scripts/postprocess_fullwidth_space.py）のみを
単独で実行します。

対象: Title要素が空（または不在）のItem/Subitem1～10の先頭Sentence冒頭、
および LineBreak="true" のColumn内の先頭Sentence冒頭。
除外条件（数式・変数定義行・補填済み等）はメインページの補填機能と同一です。
"""
import sys
from io import BytesIO
from pathlib import Path

import streamlit as st
from lxml import etree

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "scripts"))

import postprocess_fullwidth_space as pp  # noqa: E402

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

st.markdown("---")

# ------------------------------------------------------------------
# ファイルアップロードと実行
# ------------------------------------------------------------------
st.header("📁 XMLファイルのアップロード")

uploaded_file = st.file_uploader(
    "補填対象のXMLファイルを選択してください",
    type=['xml'],
    key="standalone_space_uploader"
)

if uploaded_file is not None:
    if st.button("🈳 全角スペース補填を実行", type="primary"):
        try:
            tree = etree.parse(BytesIO(uploaded_file.getvalue()))
        except etree.XMLSyntaxError as e:
            st.error(f"❌ XMLの解析に失敗しました: {e}")
            st.stop()

        root = tree.getroot()
        # メインページの補填処理（addモード）と同一のロジックを適用する
        targets, excluded_vardefs = pp.collect_target_sentences(
            root, include_list=include_list
        )
        changed = 0
        excluded_parens = 0
        for sentence in targets:
            if exclude_paren and pp.is_insertable(sentence) \
                    and pp.starts_with_paren(sentence):
                excluded_parens += 1
                continue
            if pp.add_fullwidth_space(sentence):
                changed += 1

        # 入力の整形を維持したまま書き出す（再インデントしない）
        result_bytes = etree.tostring(
            tree, encoding='UTF-8', xml_declaration=True,
            pretty_print=False
        )

        st.session_state.standalone_space_result = {
            "file_name": uploaded_file.name,
            "data": result_bytes,
            "targets": len(targets),
            "changed": changed,
            "excluded_parens": excluded_parens,
            "excluded_vardefs": len(excluded_vardefs),
        }

# ------------------------------------------------------------------
# 結果表示とダウンロード
# ------------------------------------------------------------------
result = st.session_state.get("standalone_space_result")
if result is not None:
    st.markdown("---")
    st.header("📊 実行結果")
    st.success(f"✅ 補填が完了しました（対象ファイル: {result['file_name']}）")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("対象Sentence数", f"{result['targets']}箇所")
    col2.metric("補填実施", f"{result['changed']}箇所")
    col3.metric("「（」始まりで除外", f"{result['excluded_parens']}箇所")
    col4.metric("変数定義行で除外", f"{result['excluded_vardefs']}箇所")

    if result['changed'] == 0:
        st.info(
            "補填された箇所はありません（対象がない、または"
            "すべて補填済み・除外条件に該当）。"
        )

    stem = Path(result['file_name']).stem
    st.download_button(
        label="📥 補填後のXMLファイルをダウンロード",
        data=result['data'],
        file_name=f"{stem}_space.xml",
        mime="application/xml"
    )

    show_preview = st.checkbox("📄 補填後のXMLをプレビュー", value=False)
    if show_preview:
        preview_text = result['data'].decode('utf-8')
        lines = preview_text.splitlines()
        max_lines = 500
        with st.expander("📄 補填後のXMLのプレビュー", expanded=True):
            st.code('\n'.join(lines[:max_lines]), language='xml')
            if len(lines) > max_lines:
                st.caption(
                    f"（先頭{max_lines}行のみ表示。全{len(lines)}行）")
