"""
列記List保護の設定ページ

告示データ整備方針（パターン20D・改行表現の保持）に基づく
List保護の各オプションを、XML例（変換前→変換後）を確認しながら
設定できます。設定はメインページのサイドバーと共有されます。

表示される「変換後」の例は、実際の変換スクリプト
（convert_item_step0.py / convert_subitem1_step0.py）をサンプルXMLに
適用した結果のため、例示と実際の動作が乖離しません。
"""
import subprocess
import sys
import tempfile
from pathlib import Path

import streamlit as st
from lxml import etree

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

SCRIPT_DIR = project_root / "scripts"

st.set_page_config(
    page_title="列記List保護設定 - XML変換パイプライン",
    page_icon="📑",
    layout="wide"
)

st.title("📑 列記Listの保護の設定")

# セッション状態の初期化（メインページと共有。このページを先に開いた場合に備える）
if 'preserve_enumeration' not in st.session_state:
    st.session_state.preserve_enumeration = False
if 'preserve_linebreak_list' not in st.session_state:
    st.session_state.preserve_linebreak_list = False

LAW_WRAPPER = '''<Law>
  <LawBody>
    <MainProvision>
      <Article Num="1">
        <ArticleTitle>第一</ArticleTitle>
{paragraph}
      </Article>
    </MainProvision>
  </LawBody>
</Law>'''


def _dedent_fragment(xml_bytes_or_str):
    """XML断片の共通インデントを取り除いて表示用文字列にする"""
    text = xml_bytes_or_str if isinstance(xml_bytes_or_str, str) \
        else xml_bytes_or_str.decode('utf-8')
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        return text.strip()
    indents = [len(line) - len(line.lstrip()) for line in lines]
    common = min(indents)
    return '\n'.join(line[common:] for line in lines)


@st.cache_data(show_spinner=False)
def apply_conversion(paragraph_xml, preserve_enumeration, preserve_linebreak):
    """サンプルXMLに実際の変換スクリプト（Item→Subitem1）を適用し、
    変換後のParagraph部分を返す"""
    full_xml = LAW_WRAPPER.format(paragraph=paragraph_xml)
    flags = []
    if preserve_enumeration:
        flags.append('--preserve-enumeration')
    if preserve_linebreak:
        flags.append('--preserve-linebreak-list')

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        current = tmp / "input.xml"
        current.write_text(full_xml, encoding='utf-8')
        for i, script in enumerate(
                ["convert_item_step0.py", "convert_subitem1_step0.py"]):
            out = tmp / f"step{i}.xml"
            result = subprocess.run(
                [sys.executable, str(SCRIPT_DIR / script),
                 str(current), str(out)] + flags,
                capture_output=True, text=True, timeout=60
            )
            if result.returncode != 0 or not out.exists():
                return f"（変換エラー: {script}）\n{result.stderr}"
            current = out
        root = etree.parse(str(current)).getroot()

    paragraph = root.find('.//Paragraph')
    if paragraph is None:
        return "（Paragraph要素が見つかりません）"
    return _dedent_fragment(
        etree.tostring(paragraph, encoding='unicode').rstrip())


def show_before_after(paragraph_xml, preserve_enumeration, preserve_linebreak):
    """変換前・変換後のXMLを左右に並べて表示する"""
    col_before, col_after = st.columns(2)
    with col_before:
        st.markdown("**変換前**")
        st.code(_dedent_fragment(paragraph_xml), language='xml')
    with col_after:
        st.markdown("**変換後（現在の設定）**")
        st.code(
            apply_conversion(paragraph_xml, preserve_enumeration,
                             preserve_linebreak),
            language='xml'
        )


st.markdown(
    "List要素の変換時に、列記（表形式の並記）や改行表現を持つListを"
    "変換対象から除外して保護するオプションです。各オプションのXML例を"
    "確認しながら設定してください。設定はメインページのサイドバーと連動します。"
    "（例はItem変換→Subitem1変換を適用した結果です）"
)

st.markdown("---")

# ------------------------------------------------------------------
# 1. 列記List保護（パターン20D）
# ------------------------------------------------------------------
st.header("1. 列記のList（Column構成）を保護する")

preserve_enumeration = st.checkbox(
    "列記のList（Column構成）を変換せず保持する",
    value=st.session_state.preserve_enumeration,
    help="Columnが2つ以上のListのうち、1つ目がラベル（番号等）で2つ目がテキストの"
         "「番号+見出し」構成のみを変換対象とし、1つ目と2つ目の種別が同一"
         "（テキスト同士・ラベル同士）のListは列記とみなして変換せずそのまま残します。"
         "Columnが1つのListは従来どおり変換されます。"
         "従来データの変換結果が変わるため、告示データ整備方針に沿ったデータの場合のみONにしてください。"
)
st.session_state.preserve_enumeration = preserve_enumeration

st.markdown(
    "1つ目のColumnがラベル（番号等）で2つ目がテキストの「番号+見出し」構成は"
    "設定に関わらず変換されます。1つ目と2つ目の種別が同一（テキスト同士・"
    "ラベル同士）のListは列記とみなし、ONの場合は変換せずListのまま残します。"
)

EXAMPLE_NUMBERED = '''        <Paragraph Num="1">
          <ParagraphNum/>
          <ParagraphSentence>
            <Sentence Num="1">次に掲げるとおりとする。</Sentence>
          </ParagraphSentence>
          <List>
            <ListSentence>
              <Column Num="1"><Sentence Num="1">一</Sentence></Column>
              <Column Num="2"><Sentence Num="1">番号と見出しの構成のList（常に変換対象）</Sentence></Column>
            </ListSentence>
          </List>
        </Paragraph>'''

st.subheader("番号+見出し構成（設定に関わらず変換）")
show_before_after(EXAMPLE_NUMBERED, preserve_enumeration,
                  st.session_state.preserve_linebreak_list)

EXAMPLE_ENUMERATION = '''        <Paragraph Num="1">
          <ParagraphNum/>
          <ParagraphSentence>
            <Sentence Num="1">次に掲げるとおりとする。</Sentence>
          </ParagraphSentence>
          <List>
            <ListSentence>
              <Column Num="1"><Sentence Num="1">一</Sentence></Column>
              <Column Num="2"><Sentence Num="1">番号と見出しの構成のList</Sentence></Column>
            </ListSentence>
          </List>
          <List>
            <ListSentence>
              <Column Num="1"><Sentence Num="1">検査年月日</Sentence></Column>
              <Column Num="2"><Sentence Num="1">検査結果</Sentence></Column>
            </ListSentence>
          </List>
        </Paragraph>'''

st.subheader("テキスト同士の列記List（ON時は保護）")
st.markdown(
    "2つ目のListはColumn1・Column2ともテキストの列記です。"
    "OFFの場合はSubitem1（空Title + Column2つ）に変換されますが、"
    "ONの場合はListのまま保持されます。"
)
show_before_after(EXAMPLE_ENUMERATION, preserve_enumeration,
                  st.session_state.preserve_linebreak_list)

st.markdown("---")

# ------------------------------------------------------------------
# 2. LineBreak付きColumn保護
# ------------------------------------------------------------------
st.header("2. LineBreak付きColumnを含むListを保護する")

preserve_linebreak_list = st.checkbox(
    "LineBreak付きColumnを含むListを変換せず保持する",
    value=st.session_state.preserve_linebreak_list,
    help="LineBreak=\"true\"のColumn（改行して表示する指示）を含むListを変換対象から除外します。"
         "変換するとColumnラッパーが捨てられLineBreak属性（改行表現）が失われるため、"
         "告示データ整備方針に沿ってLineBreakを使用しているデータではONを推奨します。"
)
st.session_state.preserve_linebreak_list = preserve_linebreak_list

st.markdown(
    "`LineBreak=\"true\"` のColumnは「改行して表示する」指示を持ちますが、"
    "変換の分岐によってはColumnラッパーが捨てられ属性が失われます。"
    "下の例では、OFFの場合Column2の中のSentenceだけが抽出されて"
    "`LineBreak=\"true\"`（改行表現）が失われます。"
    "ONの場合、LineBreak付きColumnを含むListは変換せずListのまま保持します。"
)

EXAMPLE_LINEBREAK = '''        <Paragraph Num="1">
          <ParagraphNum/>
          <ParagraphSentence>
            <Sentence Num="1">次に掲げるとおりとする。</Sentence>
          </ParagraphSentence>
          <List>
            <ListSentence>
              <Column Num="1"><Sentence Num="1">一</Sentence></Column>
              <Column Num="2" LineBreak="true"><Sentence Num="1">改行して表示される号の本文</Sentence></Column>
            </ListSentence>
          </List>
        </Paragraph>'''

show_before_after(EXAMPLE_LINEBREAK, preserve_enumeration,
                  preserve_linebreak_list)

st.markdown("---")

# 現在の設定サマリー
st.header("現在の設定")
st.markdown(
    f"- 列記List（Column構成）を保護: "
    f"**{'ON' if preserve_enumeration else 'OFF'}**\n"
    f"- LineBreak付きColumnを含むListを保護: "
    f"**{'ON' if preserve_linebreak_list else 'OFF'}**"
)
# page_linkはマルチページ実行時のみ有効（テストランナー等では利用不可）
try:
    st.page_link("app_pages/home.py", label="ホームへ戻って変換を実行", icon="🏠")
except Exception:
    st.caption("メインページに戻って変換を実行してください。")
