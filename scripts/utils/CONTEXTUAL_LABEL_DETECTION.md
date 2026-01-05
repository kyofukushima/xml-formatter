# 文脈依存のラベル判定機能

## 概要

括弧付きローマ数字と括弧付きアルファベットが重複する問題を解決するため、文脈依存のラベル判定機能を実装しました。

最初の要素（比較元）のラベルが`（i）`（ローマ数字の1）であるかどうかで、弟要素のラベル判定時にローマ数字を除外するかどうかを決定します。

## 使用方法

### 基本的な使い方

```python
from utils.label_utils import detect_label_id, get_exclude_label_ids_for_context

# 最初の要素のラベルを取得（例：Listの1つ目のカラムの値）
first_label = "（i）"  # または "（a）" など

# 除外リストを生成
exclude_label_ids = get_exclude_label_ids_for_context(first_label)

# 弟要素のラベルを判定（ローマ数字が除外される場合がある）
sibling_label = "（c）"
detected_label_id = detect_label_id(sibling_label, exclude_label_ids)
```

### 判定ロジック

1. **最初の要素がローマ数字パターン（`^[（(][ivxlcdmｉｖｘｌｃｄｍ]+[）)]$`）に合致する場合**
   - ローマ数字を除外しない
   - 例：`（i）`、`（ｉ）`、`（ii）`、`（ｉｉ）`、`（iii）`、`（ｉｉｉ）`、`（iv）`、`（ｖ）`など
   - `（c）` → `paren_roman`（ローマ数字として判定）

2. **最初の要素がローマ数字パターンに合致しない場合（例：`（a）`、`（A）`、`（１）`など）**
   - ローマ数字を除外する
   - `（c）` → `paren_lowercase_alphabet`（アルファベットとして判定）

3. **最初の要素がない場合（`None`）**
   - ローマ数字を除外する（安全のため）
   - `（c）` → `paren_lowercase_alphabet`（アルファベットとして判定）

## 実装例

### List要素の処理例

```python
from utils.label_utils import (
    detect_label_id,
    get_exclude_label_ids_for_context,
    is_roman_numeral_one
)

def process_list_elements(list_element):
    """List要素を処理し、文脈に応じてラベルを判定"""
    columns = list_element.findall('.//Column')
    
    if len(columns) < 2:
        return
    
    # 最初のカラムからラベルを取得
    first_column = columns[0]
    first_sentence = first_column.find('.//Sentence')
    first_label = first_sentence.text.strip() if first_sentence is not None else None
    
    # 除外リストを生成
    exclude_label_ids = get_exclude_label_ids_for_context(first_label)
    
    # 2番目以降のカラムを処理
    for column in columns[1:]:
        sentence = column.find('.//Sentence')
        if sentence is not None and sentence.text:
            label_text = sentence.text.strip()
            # 文脈を考慮してラベルを判定
            label_id = detect_label_id(label_text, exclude_label_ids)
            # ... 処理を続ける
```

### ParagraphSentenceの次のList要素の処理例

```python
def process_list_after_paragraph_sentence(paragraph):
    """ParagraphSentenceの次のList要素を処理"""
    para_sentence = paragraph.find('ParagraphSentence')
    if para_sentence is None:
        return
    
    # ParagraphSentenceの次のList要素を取得
    children = list(paragraph)
    ps_index = children.index(para_sentence)
    
    if ps_index + 1 >= len(children):
        return
    
    next_element = children[ps_index + 1]
    if next_element.tag != 'List':
        return
    
    # List要素の最初のカラムからラベルを取得
    columns = next_element.findall('.//Column')
    if len(columns) < 1:
        return
    
    first_column = columns[0]
    first_sentence = first_column.find('.//Sentence')
    first_label = first_sentence.text.strip() if first_sentence is not None else None
    
    # 除外リストを生成
    exclude_label_ids = get_exclude_label_ids_for_context(first_label)
    
    # 2番目以降のカラムを処理
    for column in columns[1:]:
        sentence = column.find('.//Sentence')
        if sentence is not None and sentence.text:
            label_text = sentence.text.strip()
            # 文脈を考慮してラベルを判定
            label_id = detect_label_id(label_text, exclude_label_ids)
            # ... 処理を続ける
```

## APIリファレンス

### `get_exclude_label_ids_for_context(first_label: Optional[str]) -> List[str]`

最初の要素のラベルに基づいて、判定から除外するラベルIDのリストを生成します。

**パラメータ:**
- `first_label`: 最初の要素のラベルテキスト（`None`の場合は`（i）`以外として扱い、ローマ数字を除外）

**戻り値:**
- `List[str]`: 除外するラベルIDのリスト（通常は`['paren_roman']`または`[]`）

**例:**
```python
# 最初の要素がローマ数字パターンの場合
exclude_list = get_exclude_label_ids_for_context("（i）")
# → []

exclude_list = get_exclude_label_ids_for_context("（ｉ）")
# → []

exclude_list = get_exclude_label_ids_for_context("（ii）")
# → []

exclude_list = get_exclude_label_ids_for_context("（ｉｉ）")
# → []

# 最初の要素がローマ数字でない場合
exclude_list = get_exclude_label_ids_for_context("（a）")
# → ['paren_roman']

exclude_list = get_exclude_label_ids_for_context("（ａ）")
# → ['paren_roman']

# 最初の要素がない場合
exclude_list = get_exclude_label_ids_for_context(None)
# → ['paren_roman']
```

### `detect_label_id(text: str, exclude_label_ids: Optional[List[str]] = None) -> Optional[str]`

テキストからラベルIDを判定します（拡張版）。

**パラメータ:**
- `text`: 判定するテキスト
- `exclude_label_ids`: 判定から除外するラベルIDのリスト（文脈依存の判定用）

**戻り値:**
- `Optional[str]`: ラベルID、見つからない場合は`None`

**例:**
```python
# 通常の判定
label_id = detect_label_id("（c）")
# → "paren_roman" または "paren_lowercase_alphabet"（優先順位による）

# ローマ数字を除外して判定
label_id = detect_label_id("（c）", exclude_label_ids=['paren_roman'])
# → "paren_lowercase_alphabet"
```

### `is_roman_numeral(label: str) -> bool`

ラベルがローマ数字パターン（`^[（(][ivxlcdmｉｖｘｌｃｄｍ]+[）)]$`）に合致するかどうかを判定します。

**パラメータ:**
- `label`: 判定するラベル

**戻り値:**
- `bool`: ローマ数字パターンに合致する場合`True`

**例:**
```python
is_roman_numeral("（i）")    # → True
is_roman_numeral("（ｉ）")    # → True
is_roman_numeral("（ii）")    # → True
is_roman_numeral("（ｉｉ）")  # → True
is_roman_numeral("（iii）")   # → True
is_roman_numeral("（ａ）")    # → False
is_roman_numeral("（a）")     # → False
```

## テスト

テストスクリプト: `scripts/test_contextual_label_detection.py`

実行方法:
```bash
python3 scripts/test_contextual_label_detection.py
```

## 注意事項

- この機能は、List要素やParagraphSentenceの次のList要素など、複数の要素が連続する場合に使用します
- 最初の要素がない場合（`None`）は、安全のためローマ数字を除外します
- 単一の要素を判定する場合は、通常の`detect_label_id(text)`を使用してください

