# Num属性振り直し処理の比較

## 調査日
2025年1月

## 調査目的
`convert_article_focused.py`の399-414行目で定義されているNum属性振り直し処理が、他の階層のスクリプトにも存在するかを確認

---

## 調査結果

### ✅ `convert_article_focused.py`（Article階層）

**使用している関数**: `renumber_nums_in_tree()`（`utils/renumber_utils.py`から）

**実装内容**:
```python
renumber_stats = renumber_nums_in_tree(tree, [
    ('MainProvision', 'Article'),  # 本文本体
    ('Part', 'Article'),           # 編
    ('Chapter', 'Article'),        # 章
    ('Section', 'Article'),        # 節
    ('Subsection', 'Article'),     # 款
    ('Division', 'Article'),       # 目
    ('SupplProvision', 'Article')  # 付則
], start_num=1)
```

**特徴**:
- 複数の親要素パターンに対応
- 親要素が変わるたびにNum属性を1からリセット
- 統計情報を表示

---

### ❌ 他の階層のスクリプト

他の階層のスクリプトでは、`convert_article_focused.py`と同じような`renumber_nums_in_tree()`を使用したNum属性振り直しは**存在しません**。

代わりに、以下のような異なるアプローチが使用されています：

#### 1. `xml_converter.py`の`renumber_elements()`関数を使用

**使用しているスクリプト**:
- `convert_item_step1.py`
- `convert_subitem1_step1.py`
- `convert_subitem2_step1.py`
- `convert_subitem3_step1.py`
- `convert_subitem4_step1.py`
- `convert_subitem5_step1.py`

**実装内容**:
```python
def renumber_elements(tree, config: ConversionConfig):
    """子要素のNum属性を再採番"""
    root = tree.getroot()
    for parent in root.xpath(f'.//{config.parent_tag}'):
        children = parent.findall(config.child_tag)
        for i, child in enumerate(children):
            child.set('Num', str(i + 1))
```

**特徴**:
- 単一の親子関係のみを処理
- 例: `('Paragraph', 'Item')` → Paragraph内のItemを再採番
- 親要素ごとに1からリセット

**使用例**:
```python
# convert_item_step1.py
config = ConversionConfig(
    parent_tag='Paragraph',
    child_tag='Item',
    ...
)
renumber_elements(tree, config)
```

#### 2. 独自の`renumber_elements()`関数を実装

**使用しているスクリプト**:
- `convert_paragraph_step3.py`

**実装内容**:
```python
def renumber_elements(tree):
    """ParagraphとItemのNumを再採番する"""
    root = tree.getroot()
    
    parents = {p for p in root.xpath('.//Paragraph/..')}
    for parent in parents:
        paragraphs = parent.findall('Paragraph')
        for i, para in enumerate(paragraphs):
            para.set('Num', str(i + 1))

    for paragraph in root.xpath('.//Paragraph'):
        items = paragraph.findall('Item')
        for i, item in enumerate(items):
            item.set('Num', str(i + 1))
```

**特徴**:
- ParagraphとItemの両方を再採番
- 親要素ごとにリセット

#### 3. インラインで再採番ロジックを実装

**使用しているスクリプト**:
- `convert_subject_item.py`

**実装内容**:
```python
# Item要素のNum属性を再採番
remaining_items = paragraph.findall('Item')
for i, item in enumerate(remaining_items):
    item.set('Num', str(i + 1))

# Subitem1のNum属性を再採番
for item in remaining_items:
    subitems = item.findall('Subitem1')
    for i, subitem in enumerate(subitems):
        subitem.set('Num', str(i + 1))
```

**特徴**:
- 処理関数内で直接実装
- ItemとSubitem1の両方を再採番

---

## 比較表

| スクリプト | 使用関数 | 親要素パターン | 特徴 |
|-----------|---------|--------------|------|
| `convert_article_focused.py` | `renumber_nums_in_tree()` | 7種類（MainProvision, Part, Chapter等） | 複数の親要素パターンに対応、統計表示 |
| `convert_item_step1.py` | `renumber_elements()` | 1種類（Paragraph） | 単一の親子関係のみ |
| `convert_subitem1_step1.py` | `renumber_elements()` | 1種類（Item） | 単一の親子関係のみ |
| `convert_paragraph_step3.py` | 独自実装 | ParagraphとItem | ParagraphとItemの両方を再採番 |
| `convert_subject_item.py` | インライン実装 | Paragraph内 | ItemとSubitem1の両方を再採番 |

---

## 結論

**`convert_article_focused.py`で定義されているような、複数の親要素パターンに対応したNum属性振り直し処理は、他の階層のスクリプトには存在しません。**

### 理由

1. **Article階層の特殊性**
   - Article要素は、MainProvision、Part、Chapter、Section、Subsection、Division、SupplProvisionなど、複数の異なる親要素の下に存在する可能性がある
   - 各親要素ごとにNum属性を1からリセットする必要がある

2. **他の階層の単純性**
   - Paragraph要素は通常、Article要素の直接の子要素
   - Item要素は通常、Paragraph要素の直接の子要素
   - Subitem要素は通常、Item要素の直接の子要素
   - 単一の親子関係のみを処理すれば十分

### 推奨事項

他の階層のスクリプトでも、必要に応じて`renumber_nums_in_tree()`を使用することで、一貫性を保つことができます。ただし、現在の実装でも十分に機能しているため、必須ではありません。


















