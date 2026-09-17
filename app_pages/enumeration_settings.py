"""
List保護・統合の設定ページ

告示データ整備方針（パターン20D・改行表現の保持）に基づく
List保護の各オプションと、連続するColumnなしListをLineBreak付きColumnとして
統合するオプションを、XML例（変換前→変換後）を確認しながら設定できます。
設定はメインページのサイドバーと共有されます。

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
    page_title="List保護・統合設定 - XML変換パイプライン",
    page_icon="📑",
    layout="wide"
)

st.title("📑 Listの保護・統合の設定")

# セッション状態の初期化（メインページと共有。このページを先に開いた場合に備える）
if 'preserve_enumeration' not in st.session_state:
    st.session_state.preserve_enumeration = False
if 'preserve_linebreak_list' not in st.session_state:
    st.session_state.preserve_linebreak_list = False
if 'merge_no_column_lists' not in st.session_state:
    st.session_state.merge_no_column_lists = True
if 'preserve_lists_after_struct' not in st.session_state:
    st.session_state.preserve_lists_after_struct = False

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
def apply_conversion(paragraph_xml, preserve_enumeration, preserve_linebreak,
                     merge_no_column=False, preserve_after_struct=False):
    """サンプルXMLに実際の変換スクリプト（Item→Subitem1）を適用し、
    変換後のParagraph部分を返す"""
    full_xml = LAW_WRAPPER.format(paragraph=paragraph_xml)
    flags = []
    if preserve_enumeration:
        flags.append('--preserve-enumeration')
    if preserve_linebreak:
        flags.append('--preserve-linebreak-list')
    if merge_no_column:
        flags.append('--merge-no-column-lists')
    if preserve_after_struct:
        flags.append('--preserve-lists-after-struct')

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


def show_before_after(paragraph_xml, preserve_enumeration, preserve_linebreak,
                      merge_no_column=False, preserve_after_struct=None):
    """変換前・変換後のXMLを左右に並べて表示する

    preserve_after_struct を省略した場合は現在のセッション設定を使う"""
    if preserve_after_struct is None:
        preserve_after_struct = st.session_state.preserve_lists_after_struct
    col_before, col_after = st.columns(2)
    with col_before:
        st.markdown("**変換前**")
        st.code(_dedent_fragment(paragraph_xml), language='xml')
    with col_after:
        st.markdown("**変換後（現在の設定）**")
        st.code(
            apply_conversion(paragraph_xml, preserve_enumeration,
                             preserve_linebreak, merge_no_column,
                             preserve_after_struct),
            language='xml'
        )


st.markdown(
    "List要素の変換時に、列記（表形式の並記）や改行表現を持つList、表・図の後に続くListを"
    "変換対象から除外して保護するオプションと、連続するColumnなしList（段落）を"
    "LineBreak付きColumnとして1要素に統合するオプションです。各オプションのXML例を"
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
                  st.session_state.preserve_linebreak_list,
                  st.session_state.merge_no_column_lists)

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
                  st.session_state.preserve_linebreak_list,
                  st.session_state.merge_no_column_lists)

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
                  preserve_linebreak_list,
                  st.session_state.merge_no_column_lists)

st.markdown("---")

# ------------------------------------------------------------------
# 3. ColumnなしList統合（告示データ整備方針①: 同一項番内の段落分け）
# ------------------------------------------------------------------
st.header("3. 連続するColumnなしListをLineBreak付きColumnとして統合する")

merge_no_column_lists = st.checkbox(
    "連続するColumnなしListをLineBreak付きColumnとして1要素に統合する",
    value=st.session_state.merge_no_column_lists,
    help="連続するColumnなしList（段落）を個別のItem/Subitemに分割せず、1つの空Title要素の"
         "*Sentence内にColumn（LineBreak=\"true\"）として並べます。"
         "Titleあり要素（ラベル付きList由来）の本文直後に続くColumnなしListは、"
         "本文（見出し）をColumn1に、各段落をColumn2以降に畳み込み、空TitleのSubitemは作りません。"
         "ラベル付きListや表等が現れた時点で統合を終了します。"
         "告示データ整備方針に沿ったデータを前提にデフォルトONです。従来どおり段落ごとに"
         "個別のItem/Subitemへ分割したい場合はOFFにしてください。"
)
st.session_state.merge_no_column_lists = merge_no_column_lists

st.markdown(
    "告示データ整備方針①では、同一項番内の段落分けを `LineBreak=\"true\"` のColumnで表現します。"
    "OFFの場合、連続するColumnなしList（段落）は個別の空Title要素に分割されます。"
    "ONの場合は1つの空Title要素にまとめ、各段落を `LineBreak=\"true\"` のColumnとして並べます。"
    "`LineBreak=\"true\"` は「そのColumnの後ろで改行する」指示のため、見出しや最後のColumnにも付与します。"
)

EXAMPLE_MERGE_PARAGRAPH = '''        <Paragraph Num="1">
          <ParagraphNum>１</ParagraphNum>
          <ParagraphSentence>
            <Sentence Num="1">基本的な考え方</Sentence>
          </ParagraphSentence>
          <List>
            <ListSentence>
              <Sentence Num="1">一段目の段落です。</Sentence>
            </ListSentence>
          </List>
          <List>
            <ListSentence>
              <Sentence Num="1">また、二段目の段落です。</Sentence>
            </ListSentence>
          </List>
          <List>
            <ListSentence>
              <Sentence Num="1">なお、三段目の段落です。</Sentence>
            </ListSentence>
          </List>
        </Paragraph>'''

st.subheader("Paragraph直下の連続する段落（ON時は1つの空Title Itemに統合）")
show_before_after(EXAMPLE_MERGE_PARAGRAPH, preserve_enumeration,
                  preserve_linebreak_list, merge_no_column_lists)

EXAMPLE_MERGE_TITLED = '''        <Paragraph Num="1">
          <ParagraphNum>２</ParagraphNum>
          <ParagraphSentence>
            <Sentence Num="1">取り組むべき事項</Sentence>
          </ParagraphSentence>
          <List>
            <ListSentence>
              <Column Num="1"><Sentence Num="1">（１）</Sentence></Column>
              <Column Num="2"><Sentence Num="1">原材料等の使用の合理化</Sentence></Column>
            </ListSentence>
          </List>
          <List>
            <ListSentence>
              <Sentence Num="1">可能な限り使用する原材料等の量を少なくすること。</Sentence>
            </ListSentence>
          </List>
          <List>
            <ListSentence>
              <Sentence Num="1">また、過剰な包装を抑制すること。</Sentence>
            </ListSentence>
          </List>
          <List>
            <ListSentence>
              <Column Num="1"><Sentence Num="1">（２）</Sentence></Column>
              <Column Num="2"><Sentence Num="1">耐久性の向上</Sentence></Column>
            </ListSentence>
          </List>
          <List>
            <ListSentence>
              <Sentence Num="1">製品全体の耐久性を高めること。</Sentence>
            </ListSentence>
          </List>
        </Paragraph>'''

st.subheader("Titleあり要素の本文直後に続く段落（ON時は見出しをColumn1にして畳み込み）")
st.markdown(
    "OFFの場合、「（１）」の本文の後に続く段落は空TitleのSubitem1に変換されます。"
    "ONの場合は、見出し「原材料等の使用の合理化」をColumn1、各段落をColumn2以降として"
    "ItemSentence内に畳み込み、空TitleのSubitem1は作りません"
    "（ラベル付きListが現れた時点で統合を終了します）。"
)
show_before_after(EXAMPLE_MERGE_TITLED, preserve_enumeration,
                  preserve_linebreak_list, merge_no_column_lists)

st.markdown("---")

# ------------------------------------------------------------------
# 4. 表・図の後のList保護（schema: Item/Subitem内では表・図の後ろに下位Subitemを置けない）
# ------------------------------------------------------------------
st.header("4. 表・図の後のListを保護する")

preserve_lists_after_struct = st.checkbox(
    "表・図の後のListを変換せず保持する",
    value=st.session_state.preserve_lists_after_struct,
    help="Item/Subitemの本文（*Sentence）の直後に表・図（TableStruct/FigStruct/StyleStruct）が"
         "置かれている場合、その後に続くListを変換せずListのまま残します。"
         "スキーマ上、Item/Subitem内では表・図の後ろに下位のSubitemを置けないため、"
         "変換するとスキーマ違反になるのを防ぎます。Paragraph直下は表・図の後にItemを置けるため対象外です。"
)
st.session_state.preserve_lists_after_struct = preserve_lists_after_struct

st.markdown(
    "告示スキーマでは、`Item`/`Subitem` の内容は「本文 → 下位のSubitem → 表・図・List」の順序で"
    "固定されています。本文の直後に `TableStruct`/`FigStruct` があり、その後にListが続く場合、"
    "OFFのままではListが表・図の**後ろ**にSubitemとして作られ、スキーマ違反になります。"
    "ONの場合、表・図の後のListは変換せずListのまま残します（表・図の後ろにListを置くことは"
    "スキーマで許容されています）。表・図の**前**にListがある場合は従来どおり変換され、"
    "表・図はそのSubitemの中に取り込まれるため対象外です。"
    "`Paragraph` は本文の直後に表・図、その後にItemを置くことが許容されているため、"
    "この設定に関わらず従来どおり変換されます。"
)

EXAMPLE_STRUCT_THEN_LISTS = '''        <Paragraph Num="1">
          <ParagraphNum/>
          <ParagraphSentence>
            <Sentence Num="1">次に掲げるとおりとする。</Sentence>
          </ParagraphSentence>
          <Item Num="1">
            <ItemTitle>一</ItemTitle>
            <ItemSentence>
              <Sentence Num="1">号の本文。次の表による。</Sentence>
            </ItemSentence>
            <TableStruct>
              <Table>
                <TableRow>
                  <TableColumn><Sentence Num="1">表の内容</Sentence></TableColumn>
                </TableRow>
              </Table>
            </TableStruct>
            <List>
              <ListSentence>
                <Column Num="1"><Sentence Num="1">（１）</Sentence></Column>
                <Column Num="2"><Sentence Num="1">表の後のラベル付きList</Sentence></Column>
              </ListSentence>
            </List>
            <List>
              <ListSentence>
                <Sentence Num="1">表の後のColumnなしList</Sentence>
              </ListSentence>
            </List>
          </Item>
        </Paragraph>'''

st.subheader("Item本文の直後に表があり、その後にListが続く（ON時は保護）")
show_before_after(EXAMPLE_STRUCT_THEN_LISTS, preserve_enumeration,
                  preserve_linebreak_list, merge_no_column_lists,
                  preserve_lists_after_struct)

EXAMPLE_LIST_THEN_STRUCT = '''        <Paragraph Num="1">
          <ParagraphNum/>
          <ParagraphSentence>
            <Sentence Num="1">次に掲げるとおりとする。</Sentence>
          </ParagraphSentence>
          <Item Num="1">
            <ItemTitle>一</ItemTitle>
            <ItemSentence>
              <Sentence Num="1">号の本文。</Sentence>
            </ItemSentence>
            <List>
              <ListSentence>
                <Column Num="1"><Sentence Num="1">（１）</Sentence></Column>
                <Column Num="2"><Sentence Num="1">表の前のラベル付きList。次の表による。</Sentence></Column>
              </ListSentence>
            </List>
            <TableStruct>
              <Table>
                <TableRow>
                  <TableColumn><Sentence Num="1">表の内容</Sentence></TableColumn>
                </TableRow>
              </Table>
            </TableStruct>
            <List>
              <ListSentence>
                <Column Num="1"><Sentence Num="1">（２）</Sentence></Column>
                <Column Num="2"><Sentence Num="1">表の後のラベル付きList</Sentence></Column>
              </ListSentence>
            </List>
          </Item>
        </Paragraph>'''

st.subheader("表の前にListがある場合（設定に関わらず従来どおり変換）")
st.markdown(
    "表の前のListがSubitem1に変換され、表はそのSubitem1の中に取り込まれます。"
    "Item直下に表が残らないため、表の後のListも従来どおりSubitem1に変換されます。"
)
show_before_after(EXAMPLE_LIST_THEN_STRUCT, preserve_enumeration,
                  preserve_linebreak_list, merge_no_column_lists,
                  preserve_lists_after_struct)

st.markdown("---")

# 現在の設定サマリー
st.header("現在の設定")
st.markdown(
    f"- 列記List（Column構成）を保護: "
    f"**{'ON' if preserve_enumeration else 'OFF'}**\n"
    f"- LineBreak付きColumnを含むListを保護: "
    f"**{'ON' if preserve_linebreak_list else 'OFF'}**\n"
    f"- 連続するColumnなしListをLineBreak付きColumnとして統合: "
    f"**{'ON' if merge_no_column_lists else 'OFF'}**\n"
    f"- 表・図の後のListを保護: "
    f"**{'ON' if preserve_lists_after_struct else 'OFF'}**"
)
# page_linkはマルチページ実行時のみ有効（テストランナー等では利用不可）
try:
    st.page_link("app_pages/home.py", label="ホームへ戻って変換を実行", icon="🏠")
except Exception:
    st.caption("メインページに戻って変換を実行してください。")
