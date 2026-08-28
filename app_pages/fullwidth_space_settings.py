"""
文頭全角スペース補填の設定ページ

告示データ整備方針・告示マークアップ修正案資料に基づく
文頭全角スペース補填の各オプションを、XML例（補填前→補填後）を
確認しながら設定できます。設定はメインページのサイドバーと共有されます。

表示される「補填後」の例は、実際の補填処理
（scripts/postprocess_fullwidth_space.py）をサンプルXMLに
適用した結果のため、例示と実際の動作が乖離しません。
"""
import sys
from pathlib import Path

import streamlit as st
from lxml import etree

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "scripts"))

import postprocess_fullwidth_space as pp  # noqa: E402

st.set_page_config(
    page_title="全角スペース補填設定 - XML変換パイプライン",
    page_icon="🔤",
    layout="wide"
)

st.title("🔤 文頭全角スペース補填の設定")

# セッション状態の初期化（メインページと共有。このページを先に開いた場合に備える）
if 'apply_fullwidth_space' not in st.session_state:
    st.session_state.apply_fullwidth_space = False
if 'fullwidth_space_include_list' not in st.session_state:
    st.session_state.fullwidth_space_include_list = False
if 'fullwidth_space_exclude_paren' not in st.session_state:
    st.session_state.fullwidth_space_exclude_paren = False


def apply_to_example(xml_str, include_list=False, exclude_paren=False,
                     enabled=True):
    """サンプルXMLに実際の補填処理を適用して返す"""
    if not enabled:
        return xml_str
    root = etree.fromstring(xml_str.encode('utf-8'))
    targets, _ = pp.collect_target_sentences(root, include_list=include_list)
    for sentence in targets:
        if exclude_paren and pp.is_insertable(sentence) \
                and pp.starts_with_paren(sentence):
            continue
        pp.add_fullwidth_space(sentence)
    return etree.tostring(root, encoding='unicode')


def show_before_after(xml_str, include_list=False, exclude_paren=False,
                      enabled=True):
    """補填前・補填後のXMLを左右に並べて表示する"""
    col_before, col_after = st.columns(2)
    with col_before:
        st.markdown("**補填前**")
        st.code(xml_str, language='xml')
    with col_after:
        label = "**補填後（現在の設定）**" if enabled else \
            "**補填後（現在の設定では補填されません）**"
        st.markdown(label)
        st.code(
            apply_to_example(xml_str, include_list=include_list,
                             exclude_paren=exclude_paren, enabled=enabled),
            language='xml'
        )


st.markdown(
    "告示データ整備方針に基づき、段落冒頭の1字下げを全角スペース（U+3000）の"
    "補填で再現します。各オプションのXML例を確認しながら設定してください。"
    "設定はメインページのサイドバーと連動します。"
)

st.markdown("---")

# ------------------------------------------------------------------
# 1. 補填の適用
# ------------------------------------------------------------------
st.header("1. 補填を適用する")

apply_fullwidth_space = st.checkbox(
    "変換後に文頭全角スペースを補填する",
    value=st.session_state.apply_fullwidth_space,
    help="Title要素が空のItem/Subitem1～10のSentence冒頭、および"
         "LineBreak=\"true\"のColumn内Sentence冒頭に全角スペースを挿入します。"
)
st.session_state.apply_fullwidth_space = apply_fullwidth_space

st.markdown(
    "Title要素（番号）が空の `Item`/`Subitem1`～`Subitem10` の先頭Sentenceが"
    "対象です。番号があるものは表示側で番号の後ろに1字分の空きが付くため"
    "対象外です。"
)

EXAMPLE_BASIC = '''<Item Num="1">
  <ItemTitle>一</ItemTitle>
  <ItemSentence>
    <Sentence Num="1">番号ありの号の本文（対象外）</Sentence>
  </ItemSentence>
</Item>
<Item Num="2">
  <ItemTitle/>
  <ItemSentence>
    <Sentence Num="1">タイトルが空の号の本文（補填対象）</Sentence>
  </ItemSentence>
</Item>'''

show_before_after(
    f"<MainProvision>\n{EXAMPLE_BASIC}\n</MainProvision>",
    enabled=apply_fullwidth_space
)

st.markdown(
    "同一要素内で `LineBreak=\"true\"` の `Column` により改行された"
    "二段目以降の段落も対象です。"
)

EXAMPLE_COLUMN = '''<Item Num="1">
  <ItemTitle>一</ItemTitle>
  <ItemSentence>
    <Column>
      <Sentence Num="1">一段目の本文（対象外）</Sentence>
    </Column>
    <Column LineBreak="true">
      <Sentence Num="1">改行された二段目の段落（補填対象）</Sentence>
    </Column>
  </ItemSentence>
</Item>'''

show_before_after(
    f"<MainProvision>\n{EXAMPLE_COLUMN}\n</MainProvision>",
    enabled=apply_fullwidth_space
)

with st.expander("常に補填されないもの（設定に関わらず除外）"):
    st.markdown(
        "- **数式画像のみのSentence**（`QuoteStruct`/`Fig`）と、"
        "冒頭が `ArithFormula`（算式）で始まるSentence\n"
        "- **変数定義行・数式行**（「Ｅ：…」「ｎ：…」等の記号定義、"
        "「ＥＭ＝αＭ×Ａ…」等のテキスト数式）\n"
        "- 既に全角スペースで始まるSentence（二重補填の防止）\n"
        "- テキストのない空のSentence"
    )
    st.code('''<Subitem4 Num="1">
  <Subitem4Title/>
  <Subitem4Sentence>
    <Sentence Num="1"><QuoteStruct><Fig src="./pict/formula.jpg"/></QuoteStruct></Sentence>
  </Subitem4Sentence>
</Subitem4>
<Subitem4 Num="2">
  <Subitem4Title/>
  <Subitem4Sentence>
    <Sentence Num="1"><ArithFormula>売上高－費用総額＋給与総額</ArithFormula></Sentence>
  </Subitem4Sentence>
</Subitem4>
<Subitem5 Num="1">
  <Subitem5Title/>
  <Subitem5Sentence>
    <Sentence Num="1">Ｅ<Sub>ＡＣ</Sub>：空気調和設備の設計一次エネルギー消費量</Sentence>
  </Subitem5Sentence>
</Subitem5>''', language='xml')

st.markdown("---")

# ------------------------------------------------------------------
# 2. List内のSentence
# ------------------------------------------------------------------
st.header("2. List内のSentenceも対象にする")

fullwidth_space_include_list = st.checkbox(
    "List/ListSentence内のSentence冒頭にも補填する",
    value=st.session_state.fullwidth_space_include_list,
    disabled=not apply_fullwidth_space,
    help="整備方針資料上「要確認」のためデフォルトは対象外です。"
)
st.session_state.fullwidth_space_include_list = fullwidth_space_include_list

st.markdown(
    "整備方針資料では List 内の扱いは「要確認」とされているため、"
    "デフォルトは対象外です。ONにすると `ListSentence` 直下の先頭Sentenceにも"
    "補填します。"
)

EXAMPLE_LIST = '''<Item Num="1">
  <ItemTitle>一</ItemTitle>
  <ItemSentence>
    <Sentence Num="1">号の本文</Sentence>
  </ItemSentence>
  <List>
    <ListSentence>
      <Sentence Num="1">List内の文章（オプションON時のみ補填対象）</Sentence>
    </ListSentence>
  </List>
</Item>'''

show_before_after(
    f"<MainProvision>\n{EXAMPLE_LIST}\n</MainProvision>",
    include_list=fullwidth_space_include_list,
    enabled=apply_fullwidth_space
)

st.markdown("---")

# ------------------------------------------------------------------
# 3. 「（」始まりの除外
# ------------------------------------------------------------------
st.header("3. 「（」で始まるSentenceを対象外にする")

fullwidth_space_exclude_paren = st.checkbox(
    "「（」で始まるSentenceには補填しない",
    value=st.session_state.fullwidth_space_exclude_paren,
    disabled=not apply_fullwidth_space,
    help="「（注）…」等の括弧書きを字下げ対象とするかは告示ごとの"
         "官報体裁に依存するため選択式です。"
)
st.session_state.fullwidth_space_exclude_paren = fullwidth_space_exclude_paren

st.markdown(
    "「（注）…」のような括弧書きで始まる文章を字下げするかどうかは"
    "告示ごとに官報の体裁が異なります。官報原本の該当箇所を確認して"
    "選択してください。"
)

EXAMPLE_PAREN = '''<Subitem1 Num="1">
  <Subitem1Title/>
  <Subitem1Sentence>
    <Sentence Num="1">この告示における計算方法は、次のとおりとする。</Sentence>
  </Subitem1Sentence>
  <Subitem2 Num="1">
    <Subitem2Title/>
    <Subitem2Sentence>
      <Sentence Num="1">（注）費用総額は、売上原価の額とする。</Sentence>
    </Subitem2Sentence>
  </Subitem2>
</Subitem1>'''

show_before_after(
    f"<MainProvision>\n{EXAMPLE_PAREN}\n</MainProvision>",
    exclude_paren=fullwidth_space_exclude_paren,
    enabled=apply_fullwidth_space
)

st.markdown("---")

# 現在の設定サマリー
st.header("現在の設定")
st.markdown(
    f"- 補填を適用する: **{'ON' if apply_fullwidth_space else 'OFF'}**\n"
    f"- List内も対象: "
    f"**{'ON' if fullwidth_space_include_list else 'OFF'}**\n"
    f"- 「（」始まりを対象外: "
    f"**{'ON' if fullwidth_space_exclude_paren else 'OFF'}**"
)
# page_linkはマルチページ実行時のみ有効（テストランナー等では利用不可）
try:
    st.page_link("app_pages/home.py", label="ホームへ戻って変換を実行", icon="🏠")
except Exception:
    st.caption("メインページに戻って変換を実行してください。")
