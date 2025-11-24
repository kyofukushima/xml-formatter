# logic3系ロジック拡張提案：深い階層への対応

## 概要

現行のlogic3_0はParagraph直下のList→Item変換のみに対応しています。
本文書では、Item内やSubitem内のList変換を含む、深い階層処理への拡張案を提案します。

## 階層構造の理解

### XMLスキーマの階層定義

```
Paragraph
├─ Item (1階層目)
   ├─ Subitem1 (2階層目)
      ├─ Subitem2 (3階層目)
         ├─ Subitem3 (4階層目)
            ├─ ... (最大Subitem10まで)
```

### 項目ラベルの階層パターン（例）

```
レベル1: １, ２, ３...
レベル2: （１）,（２）,（３）...
レベル3: （（１））,（（２））,（（３））...
レベル4: ア, イ, ウ...
```

## logic3_1: Item内List→Subitem1変換

### 対象パターン

```xml
<!-- 変換前 -->
<Item Num="1">
  <ItemTitle>１</ItemTitle>
  <ItemSentence>
    <Sentence>項目名</Sentence>
  </ItemSentence>
  <List>
    <ListSentence>
      <Column Num="1"><Sentence>（１）</Sentence></Column>
      <Column Num="2"><Sentence>サブ項目A</Sentence></Column>
    </ListSentence>
  </List>
  <List>
    <ListSentence>
      <Column Num="1"><Sentence>（２）</Sentence></Column>
      <Column Num="2"><Sentence>サブ項目B</Sentence></Column>
    </ListSentence>
  </List>
</Item>
```

```xml
<!-- 変換後 -->
<Item Num="1">
  <ItemTitle>１</ItemTitle>
  <ItemSentence>
    <Sentence>項目名</Sentence>
  </ItemSentence>
  <Subitem1 Num="1">
    <Subitem1Title>（１）</Subitem1Title>
    <Subitem1Sentence>
      <Sentence>サブ項目A</Sentence>
    </Subitem1Sentence>
  </Subitem1>
  <Subitem1 Num="2">
    <Subitem1Title>（２）</Subitem1Title>
    <Subitem1Sentence>
      <Sentence>サブ項目B</Sentence>
    </Subitem1Sentence>
  </Subitem1>
</Item>
```

### 処理ロジック

#### 処理1: ItemSentenceの次のColumn付きList

**条件**:
1. Item要素内にあるList要素
2. ItemSentenceの直後に配置されている
3. Listが2つのColumnを持つ
4. Column1の階層レベルがItemTitleより深い

**処理**:
1. List要素をSubitem1要素に変換
2. Column1の内容をSubitem1Titleに配置
3. Column2の内容をSubitem1Sentenceに配置
4. 連続する同階層のListも同様に変換

#### 処理2: 空ItemSentenceの場合の特別処理

**条件**:
- ItemSentenceが`<Sentence></Sentence>`または`<Sentence/>`

**処理**:
- Subitem1に変換後、ItemSentence自体は残す（スキーマ要件のため）

#### 処理3: Columnなし Listの扱い

**条件**:
- ItemSentenceの次にColumnなしListが存在

**処理**:
- Subitem1に変換
- Subitem1Titleは空
- ListSentenceの内容をSubitem1Sentenceに配置

### 実装における注意点

1. **階層判定の精度**:
   - ItemTitleが「１」でColumn1が「（１）」→ 深い（変換する）
   - ItemTitleが「（１）」でColumn1が「（２）」→ 同じ（変換しない）

2. **連続性の判定**:
   - 同じ階層パターンのListが連続する限り変換を続ける
   - 異なる階層が現れたら処理を停止

3. **Num属性の連番管理**:
   - Subitem1のNum属性は1から開始して連番を振る

## logic3_2: 再帰的なSubitem変換（汎用化）

### 基本方針

logic3_1のロジックを汎用化し、任意の階層（Subitem1→Subitem2→...→Subitem10）に適用可能にする。

### 汎用処理アルゴリズム

```python
def convert_list_to_subitem(parent_element, parent_title_value, current_level):
    """
    親要素内のListを次の階層のSubitemに変換する汎用関数
    
    Args:
        parent_element: 親要素（Item, Subitem1, Subitem2, ...）
        parent_title_value: 親要素のタイトル値（階層判定用）
        current_level: 現在の階層レベル（1=Item, 2=Subitem1, ...）
    """
    if current_level >= 11:  # Subitem10が上限
        return
    
    # 次の階層の要素名を決定
    next_level_name = f"Subitem{current_level}" if current_level > 1 else "Subitem1"
    sentence_element_name = parent_element.tag.replace("Title", "Sentence")
    
    # 親要素のSentence要素を取得
    sentence_elem = parent_element.find(sentence_element_name)
    if sentence_elem is None:
        return
    
    # Sentence要素の次のList要素を探索
    lists_to_convert = []
    found_sentence = False
    expected_hierarchy = None
    
    for child in parent_element:
        if child == sentence_elem:
            found_sentence = True
            continue
        
        if not found_sentence:
            continue
        
        if child.tag == "List":
            columns = child.findall(".//Column")
            if len(columns) >= 2:
                col1_text = columns[0].find("Sentence").text or ""
                
                # 階層判定
                if is_deeper_hierarchy(parent_title_value, col1_text):
                    current_hierarchy = get_hierarchy_pattern(col1_text)
                    
                    if expected_hierarchy is None:
                        expected_hierarchy = current_hierarchy
                        lists_to_convert.append(child)
                    elif current_hierarchy == expected_hierarchy:
                        lists_to_convert.append(child)
                    else:
                        # 異なる階層パターン → 変換停止
                        break
                else:
                    # 同じまたは浅い階層 → 変換停止
                    break
            else:
                # ColumnなしList → 特別処理
                lists_to_convert.append(child)
        else:
            # List以外の要素 → 変換停止
            break
    
    # Listを次階層のSubitemに変換
    for i, list_elem in enumerate(lists_to_convert, 1):
        subitem = create_subitem_element(
            next_level_name,
            num=i,
            list_elem=list_elem
        )
        
        # list_elemの位置にsubitemを挿入
        insert_index = list(parent_element).index(list_elem)
        parent_element.remove(list_elem)
        parent_element.insert(insert_index, subitem)
        
        # 再帰的に次の階層も処理
        subitem_title = subitem.find(f"{next_level_name}Title").text or ""
        convert_list_to_subitem(subitem, subitem_title, current_level + 1)


def is_deeper_hierarchy(parent_label, child_label):
    """
    child_labelがparent_labelより深い階層かを判定
    
    Examples:
        ("１", "（１）") → True
        ("（１）", "（（１））") → True
        ("（１）", "（２）") → False
        ("１", "２") → False
    """
    parent_pattern = get_hierarchy_pattern(parent_label)
    child_pattern = get_hierarchy_pattern(child_label)
    
    hierarchy_order = [
        "arabic",           # １, ２, ３
        "paren_arabic",     # （１）,（２）,（３）
        "double_paren",     # （（１））,（（２））
        "katakana",         # ア, イ, ウ
        "paren_katakana",   # （ア）,（イ）,（ウ）
        # ... 他の階層パターン
    ]
    
    try:
        parent_idx = hierarchy_order.index(parent_pattern)
        child_idx = hierarchy_order.index(child_pattern)
        return child_idx > parent_idx
    except ValueError:
        # パターンが見つからない場合の処理
        return False


def get_hierarchy_pattern(label):
    """
    ラベルから階層パターンを判定
    
    Returns:
        str: 階層パターン名
    """
    if not label:
        return "none"
    
    # 正規表現で各パターンを判定
    patterns = {
        "arabic": r"^[０-９]+$",                    # １, ２
        "paren_arabic": r"^（[０-９]+）$",         # （１）
        "double_paren": r"^（（[０-９]+））$",     # （（１））
        "katakana": r"^[ア-ン]+$",                  # ア, イ
        "paren_katakana": r"^（[ア-ン]+）$",       # （ア）
        # ... 他のパターン
    }
    
    import re
    for pattern_name, regex in patterns.items():
        if re.match(regex, label):
            return pattern_name
    
    return "unknown"


def create_subitem_element(element_name, num, list_elem):
    """
    List要素からSubitem要素を作成
    """
    from xml.etree.ElementTree import Element, SubElement
    
    subitem = Element(element_name)
    subitem.set("Num", str(num))
    
    # Title要素の作成
    title_elem = SubElement(subitem, f"{element_name}Title")
    
    # Sentence要素の作成
    sentence_container = SubElement(subitem, f"{element_name}Sentence")
    
    # Listの内容を移植
    columns = list_elem.findall(".//Column")
    if len(columns) >= 2:
        # Column付きList
        title_elem.text = columns[0].find("Sentence").text or ""
        col2_sentence = columns[1].find("Sentence")
        sentence = SubElement(sentence_container, "Sentence")
        sentence.text = col2_sentence.text
        sentence.set("Num", "1")
    else:
        # ColumnなしList
        title_elem.text = ""
        list_sentence = list_elem.find(".//Sentence")
        sentence = SubElement(sentence_container, "Sentence")
        sentence.text = list_sentence.text if list_sentence is not None else ""
        sentence.set("Num", "1")
    
    return subitem
```

### 使用例

```python
# Paragraph要素に対して処理開始
for paragraph in root.findall(".//Paragraph"):
    para_num_elem = paragraph.find("ParagraphNum")
    para_num = para_num_elem.text if para_num_elem is not None else ""
    
    # Paragraph→Item変換（logic3_0）
    convert_list_to_item_for_paragraph(paragraph, para_num)
    
    # Item→Subitem1変換（logic3_1）
    for item in paragraph.findall("Item"):
        item_title = item.find("ItemTitle").text or ""
        convert_list_to_subitem(item, item_title, current_level=1)
```

## logic3_3: 空要素判定と処理

### 対象ケース

#### ケース1: 見出しのみの項目

```xml
<!-- 元のList -->
<List>
  <ListSentence>
    <Column Num="1"><Sentence>２</Sentence></Column>
    <Column Num="2"><Sentence>項目名</Sentence></Column>
  </ListSentence>
</List>
<List>
  <ListSentence>
    <Sentence>項目の詳細説明...</Sentence>
  </ListSentence>
</List>
```

この場合、Column2が短い（見出しとして機能）ため、ItemSentenceを空にして、次のListを子要素として扱うべきです。

```xml
<!-- 期待される変換 -->
<Item Num="2">
  <ItemTitle>２</ItemTitle>
  <ItemSentence>
    <Sentence>項目名</Sentence>  <!-- または空 -->
  </ItemSentence>
  <List>
    <ListSentence>
      <Sentence>項目の詳細説明...</Sentence>
    </ListSentence>
  </List>
</Item>
```

### 判定ロジック

```python
def should_create_empty_sentence(column2_text, next_element):
    """
    ItemSentenceを空にすべきかを判定
    
    Args:
        column2_text: Column2のテキスト内容
        next_element: 次の要素（ListやTableStructの可能性）
    
    Returns:
        bool: Trueなら空のSentenceを作成
    """
    # 条件1: Column2が短い（20文字以下など）
    if len(column2_text or "") <= 20:
        # 条件2: 次の要素がListまたはTableStruct
        if next_element is not None and next_element.tag in ["List", "TableStruct", "FigStruct"]:
            return True
    
    # 条件3: Column2が特定のキーワードのみ（「次のとおり」など）
    keywords = ["次のとおり", "次のとおりとする", "以下のとおり"]
    if any(kw in (column2_text or "") for kw in keywords):
        return True
    
    return False
```

## logic3_4: 「次のとおり」判定との連携

### 問題の所在

ポリシーには「次のとおり判定」というルールがあります：

> 「次のとおりとする」等の後の内容は同一Item要素内に配置

この判定とlogic3系の変換処理が競合する可能性があります。

### 統合アプローチ

#### 処理順序の定義

1. **Step 1**: 「次のとおり」判定を実施
   - 該当する箇所をマーキング

2. **Step 2**: logic3系の変換処理を実施
   - ただし、「次のとおり」でマークされた箇所はスキップ

3. **Step 3**: 最終調整
   - 残ったListの処理

### 実装例

```python
def mark_tsugino_tori_sections(paragraph):
    """
    「次のとおり」を含む箇所をマーキング
    """
    marked_lists = []
    
    for i, child in enumerate(paragraph):
        if child.tag in ["ParagraphSentence", "ItemSentence"]:
            text = "".join(child.itertext())
            if "次のとおり" in text or "以下のとおり" in text:
                # 次の要素をマーク
                if i + 1 < len(paragraph):
                    next_elem = paragraph[i + 1]
                    if next_elem.tag == "List":
                        marked_lists.append(next_elem)
    
    return marked_lists


def convert_with_tsugino_tori_check(paragraph):
    """
    「次のとおり」判定を考慮した変換
    """
    # Step 1: マーキング
    marked_lists = mark_tsugino_tori_sections(paragraph)
    
    # Step 2: 変換処理（マークされた要素はスキップ）
    for child in paragraph:
        if child.tag == "List" and child not in marked_lists:
            # 通常の変換処理
            convert_list_to_item_or_subitem(child)
```

## 実装の優先順位

### Phase 1（即座に実装すべき）

1. ✅ logic3_0の動作確認（完了）
2. 🔴 logic3_1の実装（Item内List→Subitem1）
3. 🔴 階層判定関数の実装（`is_deeper_hierarchy`, `get_hierarchy_pattern`）

### Phase 2（次に実装）

4. 🟡 logic3_2の汎用化（再帰的処理）
5. 🟡 テストケースの作成と検証

### Phase 3（その後）

6. 🟢 logic3_3の実装（空要素判定）
7. 🟢 logic3_4の実装（「次のとおり」判定連携）

## テストケース

### test_input6の提案: Item内List変換

```xml
<!-- 入力 -->
<Paragraph Num="1">
  <ParagraphNum>１</ParagraphNum>
  <ParagraphSentence>
    <Sentence>大項目</Sentence>
  </ParagraphSentence>
  <List>
    <ListSentence>
      <Column Num="1"><Sentence>（１）</Sentence></Column>
      <Column Num="2"><Sentence>中項目A</Sentence></Column>
    </ListSentence>
  </List>
  <List>
    <ListSentence>
      <Sentence>中項目Aの詳細説明</Sentence>
    </ListSentence>
  </List>
  <List>
    <ListSentence>
      <Column Num="1"><Sentence>ア</Sentence></Column>
      <Column Num="2"><Sentence>小項目A-1</Sentence></Column>
    </ListSentence>
  </List>
  <List>
    <ListSentence>
      <Column Num="1"><Sentence>イ</Sentence></Column>
      <Column Num="2"><Sentence>小項目A-2</Sentence></Column>
    </ListSentence>
  </List>
</Paragraph>
```

```xml
<!-- 期待される出力（logic3_0 + logic3_1 + logic3_2適用後） -->
<Paragraph Num="1">
  <ParagraphNum>１</ParagraphNum>
  <ParagraphSentence>
    <Sentence>大項目</Sentence>
  </ParagraphSentence>
  <Item Num="1">
    <ItemTitle>（１）</ItemTitle>
    <ItemSentence>
      <Sentence>中項目A</Sentence>
    </ItemSentence>
    <List>
      <ListSentence>
        <Sentence>中項目Aの詳細説明</Sentence>
      </ListSentence>
    </List>
    <Subitem1 Num="1">
      <Subitem1Title>ア</Subitem1Title>
      <Subitem1Sentence>
        <Sentence>小項目A-1</Sentence>
      </Subitem1Sentence>
    </Subitem1>
    <Subitem1 Num="2">
      <Subitem1Title>イ</Subitem1Title>
      <Subitem1Sentence>
        <Sentence>小項目A-2</Sentence>
      </Subitem1Sentence>
    </Subitem1>
  </Item>
</Paragraph>
```

## まとめ

logic3_0は基礎として機能していますが、深い階層処理には以下の拡張が必須です：

1. **logic3_1**: Item内のList→Subitem1変換
2. **logic3_2**: 汎用的な再帰処理（Subitem10まで）
3. **logic3_3**: 空要素判定
4. **logic3_4**: 「次のとおり」判定との連携

これらを段階的に実装することで、ポリシーパターン5を含む複雑な階層構造に対応できます。
