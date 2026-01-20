# XML差分プレビュー機能向けライブラリ比較検討

## 概要

XMLファイルの処理前後の差分（修正箇所）をWebアプリで視覚的にプレビューする機能を実装する際に適したライブラリの比較検討ドキュメントです。

## 要件

### 必須機能
- XMLファイル間の差分検出
- 視覚的な差分表示（追加・削除・変更のハイライト）
- Webアプリ（Streamlit/Django）での統合が容易
- 日本語対応（UTF-8）

### オプション機能
- XML構造に特化した差分検出
- サイドバイサイド表示
- 行番号表示
- 折りたたみ可能な表示
- 差分の統計情報

## ライブラリ比較

### 1. difflib (Python標準ライブラリ)

#### 概要
Pythonに標準装備されているテキスト差分ライブラリ。既存のコードベースでも使用されている。

#### メリット

**実装の容易さ**
- ✅ **標準ライブラリ**: 追加インストール不要
- ✅ **既存コードとの統合**: 既に`compare_xml_files.py`で使用中
- ✅ **HTML出力**: `difflib.HtmlDiff()`でHTML形式の差分を生成可能
- ✅ **シンプルなAPI**: 学習コストが低い

**機能**
- ✅ **統一形式diff**: `unified_diff()`で標準的なdiff形式
- ✅ **コンテキスト表示**: 変更前後の行を表示
- ✅ **行番号表示**: 変更箇所の行番号を表示
- ✅ **HTML形式**: `HtmlDiff()`でWeb表示用HTMLを生成

#### デメリット

**XML特化機能の不足**
- ❌ **XML構造の理解**: XMLの階層構造を理解しない
- ❌ **要素単位の比較**: テキスト行単位の比較のみ
- ❌ **属性の比較**: XML属性の変更を検出しにくい
- ❌ **構造変更**: 要素の移動や再構成を検出しにくい

**表示の制限**
- ❌ **デフォルトスタイル**: HTMLのデフォルトスタイルがシンプル
- ❌ **カスタマイズ**: CSSカスタマイズが必要

#### 実装例

```python
import difflib
from pathlib import Path

def generate_html_diff(file1_path, file2_path):
    """HTML形式の差分を生成"""
    with open(file1_path, 'r', encoding='utf-8') as f1:
        lines1 = f1.readlines()
    with open(file2_path, 'r', encoding='utf-8') as f2:
        lines2 = f2.readlines()
    
    # HTML形式の差分を生成
    differ = difflib.HtmlDiff(wrapcolumn=80)
    html_diff = differ.make_file(
        lines1, lines2,
        fromdesc='処理前',
        todesc='処理後',
        context=True,
        numlines=3
    )
    return html_diff

# Streamlitでの使用例
import streamlit as st

if st.button("差分を表示"):
    html_diff = generate_html_diff("original.xml", "processed.xml")
    st.components.v1.html(html_diff, height=600, scrolling=True)
```

---

### 2. xmldiff

#### 概要
XML構造に特化した差分検出ライブラリ。XMLの階層構造を理解し、要素単位で差分を検出する。

#### メリット

**XML特化機能**
- ✅ **構造理解**: XMLの階層構造を理解
- ✅ **要素単位の比較**: 要素の追加・削除・変更を検出
- ✅ **属性の比較**: XML属性の変更を検出
- ✅ **移動の検出**: 要素の移動を検出可能
- ✅ **名前空間対応**: XML名前空間に対応

**出力形式**
- ✅ **XML形式**: 差分をXML形式で出力
- ✅ **アクション形式**: 変更アクションのリストを取得可能
- ✅ **詳細な情報**: 変更の種類と位置を詳細に取得

#### デメリット

**表示機能の不足**
- ❌ **HTML出力なし**: デフォルトでHTML形式の出力がない
- ❌ **視覚化**: 独自にHTML/CSSで視覚化する必要がある
- ❌ **統合の複雑さ**: Webアプリへの統合に追加実装が必要

**学習コスト**
- ❌ **API理解**: 出力形式の理解に時間がかかる
- ❌ **カスタマイズ**: 表示用のコードを書く必要がある

#### 実装例

```python
from xmldiff import main, formatting

def generate_xml_diff(file1_path, file2_path):
    """XML差分を検出"""
    # XML差分を検出
    diff = main.diff_files(file1_path, file2_path)
    
    # フォーマット済みの差分を取得
    formatter = formatting.XMLFormatter()
    formatted_diff = formatter.format(diff)
    
    return diff, formatted_diff

# カスタムHTML表示の実装が必要
def format_diff_as_html(diff):
    """xmldiffの結果をHTML形式に変換"""
    html = []
    html.append('<div class="xml-diff">')
    for action in diff:
        if action.name == 'insert':
            html.append(f'<div class="insert">+ {action.node}</div>')
        elif action.name == 'delete':
            html.append(f'<div class="delete">- {action.node}</div>')
        elif action.name == 'update':
            html.append(f'<div class="update">~ {action.node}</div>')
    html.append('</div>')
    return '\n'.join(html)
```

---

### 3. diff2html (JavaScript + Pythonラッパー)

#### 概要
美しいHTML差分表示を生成するJavaScriptライブラリ。Pythonからも利用可能。

#### メリット

**視覚的な表示**
- ✅ **美しいUI**: プロフェッショナルな差分表示
- ✅ **サイドバイサイド表示**: 左右に並べて表示可能
- ✅ **行単位のハイライト**: 追加・削除・変更を色分け
- ✅ **折りたたみ機能**: 変更のない部分を折りたたみ可能
- ✅ **行番号表示**: 行番号を表示

**機能**
- ✅ **統一形式diff対応**: unified diff形式を入力として受け取る
- ✅ **カスタマイズ可能**: CSSでスタイルをカスタマイズ可能
- ✅ **インタラクティブ**: クリックで折りたたみ/展開

#### デメリット

**統合の複雑さ**
- ❌ **JavaScript依存**: ブラウザ側でJavaScriptが必要
- ❌ **セットアップ**: JavaScriptライブラリの読み込みが必要
- ❌ **Python統合**: Pythonから直接使うにはラッパーが必要

**XML特化機能の不足**
- ❌ **XML構造の理解**: XMLの階層構造を理解しない
- ❌ **テキストベース**: テキスト行単位の比較のみ

#### 実装例

```python
import difflib
import json

def generate_unified_diff(file1_path, file2_path):
    """統一形式のdiffを生成"""
    with open(file1_path, 'r', encoding='utf-8') as f1:
        lines1 = f1.readlines()
    with open(file2_path, 'r', encoding='utf-8') as f2:
        lines2 = f2.readlines()
    
    diff = difflib.unified_diff(
        lines1, lines2,
        fromfile='処理前',
        tofile='処理後',
        lineterm=''
    )
    return '\n'.join(diff)

# Streamlitでの使用例（diff2htmlをJavaScriptで読み込む）
import streamlit.components.v1 as components

def show_diff2html(file1_path, file2_path):
    """diff2htmlで差分を表示"""
    unified_diff = generate_unified_diff(file1_path, file2_path)
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link rel="stylesheet" type="text/css" href="https://cdn.jsdelivr.net/npm/diff2html/bundles/css/diff2html.min.css" />
        <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/diff2html/bundles/js/diff2html-ui.min.js"></script>
    </head>
    <body>
        <div id="diff-view"></div>
        <script>
            const diffString = {json.dumps(unified_diff)};
            const configuration = {{
                drawFileList: true,
                matching: 'lines',
                highlight: true,
                outputFormat: 'side-by-side',
            }};
            const targetElement = document.getElementById('diff-view');
            const diff2htmlUi = new Diff2HtmlUI(targetElement, diffString, configuration);
            diff2htmlUi.draw();
            diff2htmlUi.highlightCode();
        </script>
    </body>
    </html>
    """
    components.html(html, height=800, scrolling=True)
```

---

### 4. difflib + カスタムHTML/CSS

#### 概要
`difflib`をベースに、カスタムHTML/CSSで視覚的な表示を実装する方法。

#### メリット

**柔軟性**
- ✅ **完全なカスタマイズ**: 表示を完全にカスタマイズ可能
- ✅ **標準ライブラリ**: 追加インストール不要
- ✅ **既存コードとの統合**: 既存の`difflib`コードを活用可能
- ✅ **軽量**: 外部ライブラリ不要

**実装**
- ✅ **段階的実装**: シンプルな実装から始めて段階的に改善可能
- ✅ **要件に合わせた調整**: プロジェクトの要件に合わせて調整可能

#### デメリット

**開発コスト**
- ❌ **実装時間**: HTML/CSSの実装に時間がかかる
- ❌ **メンテナンス**: カスタムコードのメンテナンスが必要
- ❌ **機能実装**: 折りたたみなどの機能を自分で実装する必要がある

#### 実装例

```python
import difflib
from pathlib import Path

def generate_custom_html_diff(file1_path, file2_path):
    """カスタムHTML形式の差分を生成"""
    with open(file1_path, 'r', encoding='utf-8') as f1:
        lines1 = f1.readlines()
    with open(file2_path, 'r', encoding='utf-8') as f2:
        lines2 = f2.readlines()
    
    differ = difflib.Differ()
    diff = list(differ.compare(lines1, lines2))
    
    html = ['<div class="diff-container">']
    html.append('<style>')
    html.append('''
        .diff-container { font-family: monospace; }
        .diff-added { background-color: #d4edda; color: #155724; }
        .diff-removed { background-color: #f8d7da; color: #721c24; }
        .diff-unchanged { color: #666; }
        .diff-line { padding: 2px 5px; display: block; }
    ''')
    html.append('</style>')
    
    for line in diff:
        if line.startswith('+ '):
            html.append(f'<div class="diff-line diff-added">{line}</div>')
        elif line.startswith('- '):
            html.append(f'<div class="diff-line diff-removed">{line}</div>')
        elif line.startswith('? '):
            continue  # コンテキスト行はスキップ
        else:
            html.append(f'<div class="diff-line diff-unchanged">{line}</div>')
    
    html.append('</div>')
    return '\n'.join(html)
```

---

## 比較表

| 項目 | difflib | xmldiff | diff2html | difflib + カスタム |
|------|---------|---------|-----------|-------------------|
| **インストール** | 標準ライブラリ | pip install必要 | JavaScript必要 | 標準ライブラリ |
| **XML構造理解** | ❌ | ✅ | ❌ | ❌ |
| **視覚的表示** | ⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **実装の容易さ** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **カスタマイズ性** | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **既存コード統合** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **日本語対応** | ✅ | ✅ | ✅ | ✅ |
| **サイドバイサイド** | ❌ | ❌ | ✅ | 実装可能 |
| **折りたたみ機能** | ❌ | ❌ | ✅ | 実装可能 |
| **開発速度** | 速い | 中程度 | 中程度 | 中程度 |

---

## 推奨事項

### 推奨アプローチ: **difflib + カスタムHTML/CSS** または **diff2html**

#### Phase 1: 迅速な実装（difflib.HtmlDiff）

**推奨する場合:**
- 迅速なプロトタイプが必要
- シンプルな差分表示で十分
- 既存コードとの統合を優先

**実装:**
```python
import difflib
import streamlit.components.v1 as components

def show_diff(file1_path, file2_path):
    with open(file1_path, 'r', encoding='utf-8') as f1:
        lines1 = f1.readlines()
    with open(file2_path, 'r', encoding='utf-8') as f2:
        lines2 = f2.readlines()
    
    differ = difflib.HtmlDiff(wrapcolumn=80)
    html_diff = differ.make_file(
        lines1, lines2,
        fromdesc='処理前',
        todesc='処理後',
        context=True,
        numlines=3
    )
    
    components.html(html_diff, height=600, scrolling=True)
```

#### Phase 2: より美しい表示（diff2html）

**推奨する場合:**
- よりプロフェッショナルな表示が必要
- サイドバイサイド表示が必要
- 折りたたみ機能が必要

**実装:**
上記の「diff2html」の実装例を参照

#### Phase 3: XML構造に特化（xmldiff + カスタム表示）

**推奨する場合:**
- XML構造の変更を詳細に検出したい
- 要素単位の比較が必要
- 属性の変更を検出したい

**実装:**
`xmldiff`で差分を検出し、カスタムHTML/CSSで視覚化

---

## 実装推奨: Streamlit向け統合例

### オプション1: difflib.HtmlDiff（シンプル・迅速）

```python
import streamlit as st
import difflib
import streamlit.components.v1 as components
from pathlib import Path
import tempfile

st.title("XML差分プレビュー")

uploaded_file1 = st.file_uploader("処理前XML", type=["xml"])
uploaded_file2 = st.file_uploader("処理後XML", type=["xml"])

if uploaded_file1 and uploaded_file2:
    with tempfile.TemporaryDirectory() as tmpdir:
        file1_path = Path(tmpdir) / uploaded_file1.name
        file2_path = Path(tmpdir) / uploaded_file2.name
        
        file1_path.write_bytes(uploaded_file1.read())
        uploaded_file1.seek(0)
        file2_path.write_bytes(uploaded_file2.read())
        
        if st.button("差分を表示"):
            with open(file1_path, 'r', encoding='utf-8') as f1:
                lines1 = f1.readlines()
            with open(file2_path, 'r', encoding='utf-8') as f2:
                lines2 = f2.readlines()
            
            differ = difflib.HtmlDiff(wrapcolumn=80)
            html_diff = differ.make_file(
                lines1, lines2,
                fromdesc='処理前',
                todesc='処理後',
                context=True,
                numlines=3
            )
            
            components.html(html_diff, height=800, scrolling=True)
```

### オプション2: diff2html（美しい表示）

```python
import streamlit as st
import difflib
import streamlit.components.v1 as components
from pathlib import Path
import tempfile
import json

st.title("XML差分プレビュー")

uploaded_file1 = st.file_uploader("処理前XML", type=["xml"])
uploaded_file2 = st.file_uploader("処理後XML", type=["xml"])

if uploaded_file1 and uploaded_file2:
    with tempfile.TemporaryDirectory() as tmpdir:
        file1_path = Path(tmpdir) / uploaded_file1.name
        file2_path = Path(tmpdir) / uploaded_file2.name
        
        file1_path.write_bytes(uploaded_file1.read())
        uploaded_file1.seek(0)
        file2_path.write_bytes(uploaded_file2.read())
        
        if st.button("差分を表示"):
            with open(file1_path, 'r', encoding='utf-8') as f1:
                lines1 = f1.readlines()
            with open(file2_path, 'r', encoding='utf-8') as f2:
                lines2 = f2.readlines()
            
            # 統一形式のdiffを生成
            diff_lines = list(difflib.unified_diff(
                lines1, lines2,
                fromfile='処理前',
                tofile='処理後',
                lineterm=''
            ))
            diff_string = '\n'.join(diff_lines)
            
            # diff2htmlで表示
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <link rel="stylesheet" type="text/css" 
                      href="https://cdn.jsdelivr.net/npm/diff2html/bundles/css/diff2html.min.css" />
                <script type="text/javascript" 
                        src="https://cdn.jsdelivr.net/npm/diff2html/bundles/js/diff2html-ui.min.js"></script>
                <style>
                    body {{ margin: 0; padding: 10px; }}
                </style>
            </head>
            <body>
                <div id="diff-view"></div>
                <script>
                    const diffString = {json.dumps(diff_string)};
                    const configuration = {{
                        drawFileList: true,
                        matching: 'lines',
                        highlight: true,
                        outputFormat: 'side-by-side',
                        synchronisedScroll: true,
                    }};
                    const targetElement = document.getElementById('diff-view');
                    const diff2htmlUi = new Diff2HtmlUI(targetElement, diffString, configuration);
                    diff2htmlUi.draw();
                    diff2htmlUi.highlightCode();
                </script>
            </body>
            </html>
            """
            components.html(html, height=800, scrolling=True)
```

### オプション3: 既存コードとの統合（compare_xml_files.pyを活用）

```python
import streamlit as st
from scripts.compare_xml_files import XMLComparator
import streamlit.components.v1 as components
from pathlib import Path
import tempfile
import difflib

st.title("XML差分プレビュー")

uploaded_file1 = st.file_uploader("処理前XML", type=["xml"])
uploaded_file2 = st.file_uploader("処理後XML", type=["xml"])

if uploaded_file1 and uploaded_file2:
    with tempfile.TemporaryDirectory() as tmpdir:
        file1_path = Path(tmpdir) / uploaded_file1.name
        file2_path = Path(tmpdir) / uploaded_file2.name
        
        file1_path.write_bytes(uploaded_file1.read())
        uploaded_file1.seek(0)
        file2_path.write_bytes(uploaded_file2.read())
        
        if st.button("差分を表示"):
            # 既存の比較ロジックを使用
            comparator = XMLComparator(str(file1_path), str(file2_path))
            report = comparator.compare()
            
            # テキスト差分も表示
            with open(file1_path, 'r', encoding='utf-8') as f1:
                lines1 = f1.readlines()
            with open(file2_path, 'r', encoding='utf-8') as f2:
                lines2 = f2.readlines()
            
            # HTML形式の差分を生成
            differ = difflib.HtmlDiff(wrapcolumn=80)
            html_diff = differ.make_file(
                lines1, lines2,
                fromdesc='処理前',
                todesc='処理後',
                context=True,
                numlines=3
            )
            
            # タブで切り替え表示
            tab1, tab2 = st.tabs(["視覚的差分", "詳細レポート"])
            
            with tab1:
                components.html(html_diff, height=800, scrolling=True)
            
            with tab2:
                st.code(report, language="text")
```

---

## 結論

### 推奨: **difflib.HtmlDiff** または **diff2html**

**理由:**

1. **difflib.HtmlDiff**（Phase 1推奨）
   - ✅ 既存コードとの統合が容易
   - ✅ 標準ライブラリで追加インストール不要
   - ✅ 迅速な実装が可能
   - ✅ 基本的な差分表示には十分

2. **diff2html**（Phase 2推奨）
   - ✅ より美しい視覚的表示
   - ✅ サイドバイサイド表示
   - ✅ 折りたたみ機能
   - ✅ プロフェッショナルな見た目

3. **xmldiff**（XML構造の詳細比較が必要な場合）
   - ✅ XML構造に特化した差分検出
   - ✅ 要素単位の比較
   - ⚠️ 表示機能の実装が必要

### 実装戦略

1. **まずはdifflib.HtmlDiffで実装**（1-2時間）
2. **ユーザーフィードバックを収集**
3. **必要に応じてdiff2htmlに移行**（より美しい表示が必要な場合）
4. **XML構造の詳細比較が必要な場合はxmldiffを追加**

---

## 参考リンク

- [difflib公式ドキュメント](https://docs.python.org/ja/3/library/difflib.html)
- [xmldiff公式ドキュメント](https://xmldiff.readthedocs.io/)
- [diff2html公式サイト](https://diff2html.xyz/)
- [Streamlit Components](https://docs.streamlit.io/library/components)

