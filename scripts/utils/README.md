# Utils - 共通ユーティリティモジュール

各特化型スクリプト（Article、Paragraph、Item等）で共通的に使用する機能を提供します。

---

## モジュール一覧

### xml_utils.py

XML処理のための共通ユーティリティ関数を提供します。

**主な機能:**
- `save_xml_with_indent()` - XMLツリーをインデント整形して保存
- `indent_xml()` - XML要素を再帰的にインデント整形
- `pretty_print_xml()` - 既存XMLファイルを整形
- `get_python_version_info()` - Pythonバージョン情報を取得

### renumber_utils.py

Num属性の連番振り直し機能を提供します。

**主な機能:**
- `renumber_nums_in_tree()` - ElementTreeのNum属性を連番で振り直し
- `renumber_nums_in_file()` - XMLファイルのNum属性を連番で振り直し
- `renumber_common_elements()` - 一般的な要素のNum属性を一括振り直し
- `get_default_mappings()` - デフォルトの親子関係マッピングを取得

---

## 使用方法

### スクリプト内で使用

```python
from utils import save_xml_with_indent

# XMLツリーを処理
tree = ET.parse('input.xml')
root = tree.getroot()

# ... 処理 ...

# インデント整形して保存
save_xml_with_indent(tree, 'output.xml')
```

### renumber_utils.pyを使用

```python
from utils import renumber_nums_in_tree

# Article要素のNum属性を1から連番で振り直し
tree = ET.parse('input.xml')
stats = renumber_nums_in_tree(tree, [('Article', None)])
print(f"Article: {stats['Article']}個")

# Paragraph内のItemを連番で振り直し（Paragraphごとにリセット）
stats = renumber_nums_in_tree(tree, [('Paragraph', 'Item')])
```

### コマンドラインから使用

```bash
# XMLファイルを整形
python -m utils.xml_utils input.xml output.xml

# 出力ファイル名を省略
python -m utils.xml_utils input.xml
# → input_formatted.xml が生成される

# Article要素のNum属性を振り直し
python -m utils.renumber_utils input.xml output.xml --elements Article

# Paragraph内のItemを振り直し
python -m utils.renumber_utils input.xml output.xml --parent Paragraph --child Item

# デフォルトマッピングで一括振り直し
python -m utils.renumber_utils input.xml output.xml --default
```

---

## 利用例

### Article特化スクリプト

```python
from utils import save_xml_with_indent, renumber_nums_in_tree

class ArticleFocusedConverter:
    def process_xml(self, input_path, output_path, renumber=True):
        tree = ET.parse(input_path)
        # ... Article分割処理 ...
        
        # Num属性の振り直し
        if renumber:
            stats = renumber_nums_in_tree(tree, [('Article', None)])
            print(f"Article: {stats['Article']}個を1から連番で振り直し")
        
        # 整形して保存
        save_xml_with_indent(tree, output_path)
```

### Paragraph特化スクリプト

```python
from utils import save_xml_with_indent, renumber_nums_in_tree

class ParagraphFocusedConverter:
    def process_xml(self, input_path, output_path, renumber=True):
        tree = ET.parse(input_path)
        # ... Paragraph変換処理 ...
        
        # Num属性の振り直し
        if renumber:
            stats = renumber_nums_in_tree(tree, [
                ('Article', 'Paragraph')  # Article内のParagraphを連番
            ])
            print(f"Paragraph: {stats['Paragraph']}個を振り直し")
        
        save_xml_with_indent(tree, output_path)
```

### Item特化スクリプト

```python
from utils import save_xml_with_indent, renumber_nums_in_tree

class ItemFocusedConverter:
    def process_xml(self, input_path, output_path, renumber=True):
        tree = ET.parse(input_path)
        # ... Item変換処理 ...
        
        # Num属性の振り直し
        if renumber:
            stats = renumber_nums_in_tree(tree, [
                ('Paragraph', 'Item')  # Paragraph内のItemを連番
            ])
            print(f"Item: {stats['Item']}個を振り直し")
        
        save_xml_with_indent(tree, output_path)
```

---

## 機能詳細

### save_xml_with_indent()

XMLツリーをインデント整形して保存します。

**特徴:**
- Python 3.9以降なら標準の`ET.indent()`を自動使用（高速）
- Python 3.8以前でも動作（独自実装）
- インデント文字列をカスタマイズ可能

**パラメータ:**
- `tree`: ElementTree - 保存するXMLツリー
- `output_path`: str/Path - 出力ファイルパス
- `indent_str`: str - インデント文字列（デフォルト: 2スペース）

**使用例:**
```python
# デフォルト（2スペース）
save_xml_with_indent(tree, 'output.xml')

# 4スペース
save_xml_with_indent(tree, 'output.xml', indent_str="    ")

# タブ
save_xml_with_indent(tree, 'output.xml', indent_str="\t")
```

---

## 今後の拡張

このフォルダには、今後以下のような共通機能を追加する予定：

- ✅ `xml_utils.py` - XML整形ユーティリティ（実装済み）
- ✅ `renumber_utils.py` - Num属性振り直しユーティリティ（実装済み）
- `validation_utils.py` - スキーマ検証ユーティリティ
- `text_utils.py` - テキスト処理ユーティリティ
- `file_utils.py` - ファイル操作ユーティリティ
- `logging_utils.py` - ロギングユーティリティ

---

**作成日:** 2025年10月28日  
**場所:** `scripts/education_script/utils/`

