# Num属性振り直し機能実装完了レポート

## 実施日
2025年10月28日

## 概要
Num属性を1から連番で振り直す共通ユーティリティを実装しました。
Article、Paragraph、Item専用スクリプトなど、すべての特化型スクリプトで再利用可能です。

---

## 1. 実装内容

### 1.1. 新規作成ファイル

#### `utils/renumber_utils.py`（全353行）

**主な機能:**

1. **`renumber_nums_in_tree(tree, mappings, start_num=1)`**
   - ElementTreeのNum属性を連番で振り直し（推奨）
   - 親子関係を指定可能
   - 親をNoneにすると全体で連番

2. **`renumber_nums_in_file(input_path, output_path, mappings, ...)`**
   - XMLファイルのNum属性を連番で振り直し
   - `preserve_formatting=True`で元のインデントを完全保持

3. **`renumber_common_elements(tree, start_num=1)`**
   - 一般的な要素のNum属性を一括振り直し（便利関数）
   - デフォルトマッピングを使用

4. **`get_default_mappings()`**
   - デフォルトの親子関係マッピングを取得
   ```python
   [
       ('Article', None),  # Article全体で連番
       ('Subsection', 'Article'),  # Subsection内のArticleを連番
       ('Paragraph', 'Item'),  # Paragraph内のItemを連番
       ('Item', 'Subitem1'),
       ('Subitem1', 'Subitem2'),
       ...  # Subitem10まで
   ]
   ```

**コマンドライン対応:**
```bash
# Article要素を振り直し
python -m utils.renumber_utils input.xml output.xml --elements Article

# Paragraph内のItemを振り直し
python -m utils.renumber_utils input.xml output.xml --parent Paragraph --child Item

# デフォルトマッピングで一括振り直し
python -m utils.renumber_utils input.xml output.xml --default
```

---

### 1.2. 更新したファイル

#### `utils/__init__.py`

新しい関数をエクスポート：
```python
from .renumber_utils import (
    renumber_nums_in_tree,
    renumber_nums_in_file,
    renumber_common_elements,
    get_default_mappings
)
```

#### `convert_article_focused.py`

**変更点:**

1. **インポート追加:**
   ```python
   from utils import save_xml_with_indent, renumber_nums_in_tree
   ```

2. **`process_xml()`メソッドに`renumber`パラメータを追加:**
   ```python
   def process_xml(self, input_path, output_path, renumber=True):
       # ... 既存の処理 ...
       
       # Num属性の振り直し
       if renumber:
           renumber_stats = renumber_nums_in_tree(tree, [('Article', None)])
           # 統計表示
       
       save_xml_with_indent(tree, output_path)
   ```

3. **コマンドライン引数に`--no-renumber`オプションを追加:**
   ```python
   parser.add_argument('--no-renumber', action='store_true', 
                      help='Num属性の振り直しを無効化')
   ```

#### `utils/README.md`

- `renumber_utils.py`の説明を追加
- 使用例を追加
- Article/Paragraph/Item特化スクリプトの使用例を更新

---

## 2. 使用方法

### 2.1. スクリプト内で使用（推奨）

```python
from utils import renumber_nums_in_tree

# Article要素を1から連番
tree = ET.parse('input.xml')
stats = renumber_nums_in_tree(tree, [('Article', None)])
print(f"Article: {stats['Article']}個")

# Paragraph内のItemを連番（Paragraphごとにリセット）
stats = renumber_nums_in_tree(tree, [('Paragraph', 'Item')])
print(f"Item: {stats['Item']}個")

# 複数の要素を一度に振り直し
stats = renumber_nums_in_tree(tree, [
    ('Article', None),
    ('Paragraph', 'Item'),
    ('Item', 'Subitem1')
])
```

### 2.2. Article特化スクリプトで使用

```bash
# デフォルト（Num属性振り直しあり）
python convert_article_focused.py test_input5.xml

# Num属性振り直しを無効化
python convert_article_focused.py test_input5.xml --no-renumber
```

### 2.3. コマンドラインから直接使用

```bash
# Article要素を振り直し
python -m utils.renumber_utils test_input5.xml test_output.xml --elements Article

# Paragraph内のItemを振り直し
python -m utils.renumber_utils test_input5.xml test_output.xml --parent Paragraph --child Item

# デフォルトマッピングで一括振り直し
python -m utils.renumber_utils test_input5.xml test_output.xml --default

# Dry-run（実行せずに統計のみ表示）
python -m utils.renumber_utils test_input5.xml test_output.xml --elements Article --dry-run
```

---

## 3. 動作確認

### 3.1. テスト実行

```bash
$ python3 convert_article_focused.py test_input5.xml test_input5_article_renumbered.xml

================================================================================
【Article要素特化型変換（分割のみ）】
================================================================================

処理前:
  - Article要素: 13個

処理後:
  - Article要素: 14個 (+1)

変換統計:
  - 処理したArticle: 14個
  - ArticleTitleを追加: 0個
  - 分割したArticle: 1個
  - スキップしたArticle: 12個（ArticleTitleが空）

Num属性振り直し:
  - Article: 14個を1から連番で振り直し

出力ファイル: test_input5_article_renumbered.xml
  ✅ インデント整形済み
  ✅ Num属性振り直し済み
================================================================================
```

### 3.2. 結果確認

```bash
$ grep -o '<Article Num="[^"]*"' test_input5_article_renumbered.xml | head -20

<Article Num="1"
<Article Num="2"
<Article Num="3"
<Article Num="4"
<Article Num="5"
<Article Num="6"
<Article Num="7"
<Article Num="8"
<Article Num="9"
<Article Num="10"
<Article Num="11"
<Article Num="12"
<Article Num="13"
<Article Num="14"
```

✅ **正しく1から14まで連番で振られています！**

---

## 4. 主な特徴

### ✅ 柔軟な親子関係指定

```python
# 全体で連番
[('Article', None)]

# 親要素内で連番（親が変わるとリセット）
[('Paragraph', 'Item')]

# 複数の親子関係を一度に指定
[
    ('Article', None),
    ('Paragraph', 'Item'),
    ('Item', 'Subitem1')
]
```

### ✅ ElementTreeベース（安全・推奨）

- DOM解析による安全な処理
- 構造を完全に理解した上で変更
- エラーが起こりにくい

### ✅ テキストベースオプション（互換性）

```python
renumber_nums_in_file(
    'input.xml', 
    'output.xml',
    [('Article', None)],
    preserve_formatting=True  # 元のインデントを完全保持
)
```

### ✅ コマンドライン対応

- スクリプトなしで直接実行可能
- Dry-runモードで事前確認可能
- 柔軟なオプション指定

### ✅ 統計情報の取得

```python
stats = renumber_nums_in_tree(tree, [('Article', None), ('Item', None)])
# → {'Article': 14, 'Item': 125}
```

---

## 5. 既存スクリプトとの連携

### `special_fixer/renumber_article_nums.py`との関係

- **既存スクリプト**: テキストベースの連番付け直し（インデント保持重視）
- **新ユーティリティ**: ElementTreeベースの連番付け直し（安全性重視）

**使い分け:**
- 通常は新ユーティリティ（`utils/renumber_utils.py`）を使用
- 既存XMLのインデント・コメントを完全保持したい場合は、
  `preserve_formatting=True`オプションまたは既存スクリプトを使用

---

## 6. 他のスクリプトへの展開

### 今後の実装予定

1. **`convert_paragraph_focused.py`**
   ```python
   # Paragraph内のItemを振り直し
   renumber_stats = renumber_nums_in_tree(tree, [('Article', 'Paragraph')])
   ```

2. **`convert_item_focused.py`**
   ```python
   # Paragraph内のItemを振り直し
   renumber_stats = renumber_nums_in_tree(tree, [('Paragraph', 'Item')])
   ```

3. **`convert_subitem_focused.py`**
   ```python
   # Item内のSubitem1を振り直し
   renumber_stats = renumber_nums_in_tree(tree, [('Item', 'Subitem1')])
   ```

4. **`convert_list_unified.py`**
   ```python
   # すべての要素を一括振り直し
   renumber_stats = renumber_common_elements(tree)
   ```

---

## 7. ファイル構成

### utils/フォルダ

```
utils/
├── __init__.py  ← 公開APIを定義
├── xml_utils.py  ← XML整形ユーティリティ（170行）
├── renumber_utils.py  ← Num属性振り直しユーティリティ（353行）
└── README.md  ← ドキュメント（190行）
```

### 出力ファイル

```
scripts/education_script/
├── test_input5.xml  ← 入力（6679行）
├── test_input5_article_split.xml  ← Article分割のみ（6701行）
└── test_input5_article_renumbered.xml  ← Article分割+Num振り直し（6701行）
```

---

## 8. メリット

### ✅ 共通化による保守性向上

- 1つのモジュールで全スクリプトに対応
- バグ修正が1箇所で済む
- 機能追加も1箇所で済む

### ✅ 再利用性

- 他のプロジェクトにも`utils/`フォルダごとコピー可能
- `from utils import renumber_nums_in_tree`だけで使用可能

### ✅ テスト容易性

- 独立したモジュールなので単体テストが容易
- 各特化型スクリプトから分離されている

### ✅ 柔軟性

- 親子関係を自由に指定可能
- 開始番号をカスタマイズ可能
- ElementTreeベースとテキストベースを選択可能

---

## 9. 今後の拡張

### Phase 1: 既存スクリプトへの統合 ✅

- [x] `convert_article_focused.py` ← 完了

### Phase 2: 他のスクリプトへの展開

- [ ] `convert_paragraph_focused.py`
- [ ] `convert_item_focused.py`
- [ ] `convert_subitem_focused.py`
- [ ] `convert_list_unified.py`

### Phase 3: 機能拡張

- [ ] バリデーション機能の追加
  - 連番に抜けがないかチェック
  - 重複がないかチェック
- [ ] レポート機能の追加
  - 変更前後の差分レポート
  - 統計情報の詳細化
- [ ] パフォーマンス最適化
  - 大規模XMLファイルへの対応

---

## 10. まとめ

### ✅ 完了したこと

1. **`utils/renumber_utils.py`を作成**
   - ElementTreeベースの安全な実装
   - テキストベースオプションも提供
   - コマンドライン対応

2. **`utils/__init__.py`を更新**
   - 新しい関数をエクスポート

3. **`convert_article_focused.py`に統合**
   - `renumber`パラメータを追加
   - `--no-renumber`オプションを追加
   - Num属性振り直し統計を表示

4. **ドキュメント作成**
   - `utils/README.md`に詳細な説明を追加
   - 使用例を追加
   - コマンドライン使用方法を追加

5. **動作確認完了**
   - Article要素14個を1から連番で振り直し
   - インデント整形も同時に適用
   - 正常に動作することを確認

### 📝 推奨事項

1. **他のスクリプトにも適用**:
   - `convert_paragraph_focused.py`
   - `convert_item_focused.py`
   - `convert_subitem_focused.py`
   - `convert_list_unified.py`

2. **統合テストの実施**:
   - 全スクリプトを連続実行
   - Num属性が正しく振られているか確認

3. **ドキュメント拡充**:
   - トラブルシューティングガイド
   - FAQ
   - ベストプラクティス

---

**実施者:** AI Assistant  
**作業日:** 2025年10月28日  
**フォルダ:** `scripts/education_script/utils/`  
**状態:** ✅ 完了

**関連ファイル:**
- `utils/renumber_utils.py`
- `utils/__init__.py`
- `utils/README.md`
- `convert_article_focused.py`
- `test_input5_article_renumbered.xml`

