# XML整形機能の実装

## 実施日
2025年10月28日

## 概要
すべての特化型スクリプト（Article、Paragraph、Item等）で共通的に使用できるXMLインデント整形機能を実装しました。

---

## 1. 実装内容

### 新規作成ファイル

**`xml_utils.py`** - 共通XMLユーティリティモジュール

**提供機能:**
1. `indent_xml()` - 独自実装のインデント整形関数（Python全バージョン対応）
2. `save_xml_with_indent()` - Treeをインデント整形して保存
3. `pretty_print_xml()` - 既存XMLファイルを整形
4. 自動的に最適な方法を選択（Python 3.9以降なら標準の`ET.indent()`を使用）

---

## 2. 使用方法

### 方法1: スクリプト内で使用（推奨）

```python
from xml_utils import save_xml_with_indent

# XMLツリーを処理
tree = ET.parse('input.xml')
root = tree.getroot()

# ... 処理 ...

# インデント整形して保存
save_xml_with_indent(tree, 'output.xml')
```

### 方法2: コマンドラインから直接使用

```bash
# 既存のXMLファイルを整形
python xml_utils.py input.xml output.xml

# 出力ファイル名を省略すると "_formatted" サフィックスが付く
python xml_utils.py input.xml
# → input_formatted.xml が生成される
```

### 方法3: 手動でインデント整形のみ実行

```python
from xml_utils import indent_xml

tree = ET.parse('input.xml')
root = tree.getroot()

indent_xml(root)  # インデント整形

tree.write('output.xml', encoding='utf-8', xml_declaration=True)
```

---

## 3. 特徴

### ✅ Pythonバージョンの自動判定

- **Python 3.9以降**: 標準の`ET.indent()`を使用（高速）
- **Python 3.8以前**: 独自実装の`indent_xml()`を使用（互換性）

### ✅ カスタマイズ可能なインデント

```python
# 2スペース（デフォルト）
save_xml_with_indent(tree, 'output.xml')

# 4スペース
save_xml_with_indent(tree, 'output.xml', indent_str="    ")

# タブ
save_xml_with_indent(tree, 'output.xml', indent_str="\t")
```

### ✅ 既存のtext/tail属性を尊重

空白のみのtext/tailは上書きされますが、実際のコンテンツを含む場合は保持されます。

---

## 4. Article特化スクリプトへの適用

### 修正内容

**`convert_article_focused.py`:**

```python
# インポート追加
from xml_utils import save_xml_with_indent

# 保存部分を修正
# 変更前:
tree.write(output_path, encoding='utf-8', xml_declaration=True)

# 変更後:
save_xml_with_indent(tree, output_path)
```

### 実行結果

```bash
$ python convert_article_focused.py test_input5.xml test_input5_article_formatted.xml

出力ファイル: test_input5_article_formatted.xml
  ✅ インデント整形済み
```

---

## 5. 出力例

### 整形前（1行）
```xml
<Article Num="999999999"><ArticleTitle /><Paragraph Num="1"><ParagraphNum /><List>...
```

### 整形後（適切なインデント）
```xml
<Article Num="999999999">
  <ArticleTitle />
  <Paragraph Num="1">
    <ParagraphNum />
    <List>
      <ListSentence>
        <Sentence Num="1">高等部における教育については...</Sentence>
      </ListSentence>
    </List>
  </Paragraph>
</Article>
```

---

## 6. 他のスクリプトへの適用方法

### Paragraph特化スクリプト

```python
from xml_utils import save_xml_with_indent

class ParagraphFocusedConverter:
    def process_xml(self, input_path, output_path):
        tree = ET.parse(input_path)
        # ... 処理 ...
        save_xml_with_indent(tree, output_path)  # ← この1行を追加
```

### Item特化スクリプト

```python
from xml_utils import save_xml_with_indent

class ItemFocusedConverter:
    def process_xml(self, input_path, output_path):
        tree = ET.parse(input_path)
        # ... 処理 ...
        save_xml_with_indent(tree, output_path)  # ← この1行を追加
```

### Subitem特化スクリプト

同様に、すべての特化型スクリプトで使用可能です。

---

## 7. テスト結果

### テスト環境
- Python: 3.x
- 入力ファイル: `test_input5.xml` (6679行)
- 出力ファイル: `test_input5_article_formatted.xml` (6663行)

### 検証項目

| 項目 | 結果 |
|------|------|
| XML宣言の保持 | ✅ `<?xml version='1.0' encoding='utf-8'?>` |
| 要素のインデント | ✅ 2スペースで正しく整形 |
| 属性の保持 | ✅ すべて保持 |
| テキストコンテンツの保持 | ✅ すべて保持 |
| Article分割部分の整形 | ✅ 正しく整形 |
| List要素の整形 | ✅ 正しく整形 |

### パフォーマンス
- 6679行のXMLファイルを1秒以内で整形
- メモリ使用量: 適切

---

## 8. 既存XMLファイルの一括整形

複数のXMLファイルを一括で整形したい場合：

```bash
# シェルスクリプト例
for file in *.xml; do
    python xml_utils.py "$file" "${file%.xml}_formatted.xml"
done
```

または、Pythonスクリプト：

```python
from pathlib import Path
from xml_utils import pretty_print_xml

xml_files = Path('.').glob('*.xml')
for xml_file in xml_files:
    output_file = xml_file.parent / f"{xml_file.stem}_formatted.xml"
    pretty_print_xml(xml_file, output_file)
    print(f"整形完了: {xml_file} → {output_file}")
```

---

## 9. まとめ

### ✅ 達成したこと

1. **共通モジュール化**: すべてのスクリプトで再利用可能
2. **互換性**: Python 3.8以前でも動作
3. **最適化**: Python 3.9以降では標準機能を活用
4. **柔軟性**: インデント文字列をカスタマイズ可能
5. **実績**: Article特化スクリプトで正常動作確認

### 📝 今後の適用

次の特化型スクリプトでも同じ方法で適用：
- Paragraph特化処理
- Item特化処理
- Subitem特化処理
- その他の変換スクリプト

### 🎯 推奨事項

1. すべての変換スクリプトで`xml_utils.save_xml_with_indent()`を使用
2. デバッグ時は整形後のXMLを確認（可読性向上）
3. 本番環境では整形済みXMLを生成（保守性向上）

---

**作成日**: 2025年10月28日  
**モジュール**: `xml_utils.py`  
**適用スクリプト**: `convert_article_focused.py`  
**テスト済みファイル**: `test_input5_article_formatted.xml`

