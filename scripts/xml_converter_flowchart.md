# xml_converter.py 処理フローチャート

## ラベル付きList要素の処理フロー（NORMAL_PROCESSINGモード）

### 全体フロー

```mermaid
flowchart TD
    Start([process_normal_mode_list_element開始<br/>List要素を処理する]) --> CheckLastChild{last_childがNone?<br/>前のItem要素が存在しない?}
    
    CheckLastChild -->|Yes<br/>最初の要素| CreateFirst["create_element_from_listを呼び出してItemに変換<br/>List要素をItem要素に変換し、state.last_childに設定"]
    CreateFirst --> End1([処理終了])
    
    CheckLastChild -->|No<br/>前の要素が存在| CheckSameHierarchy{"are_same_hierarchy == True?<br/>同じ階層のラベルか?<br/>同じラベルIDで同じラベルテキスト"}
    
    CheckSameHierarchy -->|Yes<br/>同じ階層| HandleSameHierarchy["handle_labeled_list_with_same_hierarchy<br/>create_element_from_listを呼び出してItemに変換（分割）<br/>新しいItemとして追加"]
    HandleSameHierarchy --> End2([処理終了])
    
    CheckSameHierarchy -->|No<br/>異なる階層| CheckColumnCount{"Column数による分岐<br/>col_countの値で処理を分岐"}
    
    CheckColumnCount -->|Column == 0<br/>ColumnなしList| HandleNoColumn["handle_no_column_list_in_normal_mode<br/>ColumnなしListの処理<br/>指導項目のチェックなど"]
    HandleNoColumn --> End3([処理終了])
    
    CheckColumnCount -->|"Column > 2 かつ 最初がラベル<br/>3列以上でラベル付き"| HandleMultiLabeled["handle_multi_column_labeled_list<br/>handle_labeled_list_with_different_hierarchy<br/>分割/取り込み判定を行う"]
    HandleMultiLabeled --> End4([処理終了])
    
    CheckColumnCount -->|"Column > 2 かつ 最初がラベルでない<br/>3列以上でラベルなし"| HandleMultiNonLabeled["handle_multi_column_non_labeled_list<br/>ラベルなし3列以上のList処理<br/>create_element_from_listで変換を試みる"]
    HandleMultiNonLabeled --> End5([処理終了])
    
    CheckColumnCount -->|"Column == 2 かつ 最初がラベル<br/>2列でラベル付き"| HandleTwoLabeled["handle_two_column_labeled_list<br/>handle_labeled_list_with_different_hierarchy<br/>分割/取り込み判定を行う"]
    HandleTwoLabeled --> End6([処理終了])
    
    CheckColumnCount -->|"Column == 2 かつ 最初がラベルでない<br/>またはColumn == 1<br/>2列でラベルなし、または1列"| HandleTwoNonLabeled["handle_two_column_non_labeled_list<br/>ラベルなし2列以下のList処理<br/>ラベル付きの場合は変換を試みる"]
    HandleTwoNonLabeled --> End7([処理終了])
```

**処理の説明:**

- **CheckLastChild**: `state.last_child`が`None`かどうかをチェック。最初の要素の場合は`None`。
- **CreateFirst**: 最初の要素の場合は、`create_element_from_list`でItemに変換し、`state.last_child`に設定。
- **CheckSameHierarchy**: `are_same_hierarchy`関数で、現在のItemと新しいListが同じ階層（同じラベルIDで同じラベルテキスト）かチェック。
- **HandleSameHierarchy**: 同じ階層の場合は、新しいItemとして分割（`create_element_from_list`で変換）。
- **CheckColumnCount**: Column数（`col_count`）と最初のColumnがラベルかどうかで処理を分岐。
- **HandleMultiLabeled**: Columnが3つ以上で最初がラベルの場合、`handle_labeled_list_with_different_hierarchy`で分割/取り込み判定。
- **HandleMultiNonLabeled**: Columnが3つ以上で最初がラベルでない場合、`create_element_from_list`で変換を試みる。
- **HandleTwoLabeled**: Columnが2つで最初がラベルの場合、`handle_labeled_list_with_different_hierarchy`で分割/取り込み判定。
- **HandleTwoNonLabeled**: Columnが2つで最初がラベルでない場合、またはColumnが1つの場合の処理。ラベル付きの場合は変換を試みる。

### handle_labeled_list_with_different_hierarchy の詳細フロー

```mermaid
flowchart TD
    Start([handle_labeled_list_with_different_hierarchy開始<br/>異なる階層のList要素を処理]) --> SplitCheck{"should_split_labeled_list<br/>分割判定<br/>ラベルの種類と値、既出チェックで判定"}
    
    SplitCheck -->|True<br/>分割する| Split["create_element_from_listを呼び出してItemに変換（分割）<br/>state.set_last_child<br/>state.add_seen_label<br/>新しいItemとして追加<br/>return False"]
    Split --> End1([処理終了])
    
    SplitCheck -->|False<br/>分割しない| AppendDefault["子要素として取り込む<br/>state.append_to_last_child<br/>前のItem要素の子要素として追加<br/>return False"]
    AppendDefault --> End2([処理終了])
```

**処理の説明:**

- **SplitCheck**: `should_split_labeled_list`関数で分割するかどうかを判定。以下のルールに基づいて判定：
  1. 同じラベルの種類でかつ同じ値がまだ登場していない（兄要素にない）：分割する
  2. 同じラベルの種類でかつ、同じ値がすでに登場している：取り込む
  3. ラベルの種類が異なる：取り込む
- **Split**: 分割する場合、`create_element_from_list`でItemに変換し、`state.set_last_child`で新しいItemとして設定。`state.add_seen_label`でラベルを記録。
- **AppendDefault**: 分割しない場合、`state.append_to_last_child`で子要素として取り込む。

### should_split_labeled_list の詳細フロー

```mermaid
flowchart TD
    Start([should_split_labeled_list開始<br/>分割するかどうかを判定<br/>引数: current_title_text, col1_text, current_label_id, list_label_id, col_count, state]) --> CheckLabelId{"ラベルIDが取得できる?<br/>current_label_id != None<br/>かつ list_label_id != None"}
    
    CheckLabelId -->|No<br/>ラベルIDが取得できない| ReturnFalse1["return False<br/>取り込む、分割しない<br/>ラベルIDが取得できない場合は取り込む"]
    ReturnFalse1 --> End1([処理終了])
    
    CheckLabelId -->|Yes<br/>ラベルIDが取得できる| CheckLabelType{"ラベルの種類が同じ?<br/>current_label_id == list_label_id<br/>同じラベルIDか?"}
    
    CheckLabelType -->|No<br/>ラベルの種類が異なる| ReturnFalse2["return False<br/>取り込む、分割しない<br/>ラベルの種類が異なる場合は取り込む"]
    ReturnFalse2 --> End2([処理終了])
    
    CheckLabelType -->|Yes<br/>同じラベルの種類| CheckSameValue{"ラベルテキストが同じ?<br/>current_title_text == col1_text<br/>同じ値か?"}
    
    CheckSameValue -->|Yes<br/>同じ値| ReturnFalse3["return False<br/>取り込む、分割しない<br/>同じ値が既に登場しているので取り込む"]
    ReturnFalse3 --> End3([処理終了])
    
    CheckSameValue -->|No<br/>異なる値| CheckSeenLabel{"まだ登場していない?<br/>state != None かつ<br/>not state.has_seen_label(col1_text)<br/>兄要素に同じ値がない?"}
    
    CheckSeenLabel -->|Yes<br/>まだ登場していない| ReturnTrue["return True<br/>分割する<br/>同じラベルの種類で異なる値がまだ登場していないので分割"]
    ReturnTrue --> End4([処理終了])
    
    CheckSeenLabel -->|No<br/>既に登場している| ReturnFalse4["return False<br/>取り込む、分割しない<br/>既に登場しているので取り込む"]
    ReturnFalse4 --> End5([処理終了])
```

**処理の説明:**

- **CheckLabelId**: ラベルIDが取得できるかどうかをチェック。`current_label_id`または`list_label_id`が`None`の場合は取り込む。
- **ReturnFalse1**: ラベルIDが取得できない場合、取り込む（分割しない）。
- **CheckLabelType**: ラベルの種類（ラベルID）が同じかどうかをチェック。`current_label_id == list_label_id`で判定。
- **ReturnFalse2**: ラベルの種類が異なる場合、取り込む（分割しない）。ルール3に基づく。
- **CheckSameValue**: 同じラベルの種類の場合、ラベルテキスト（値）が同じかどうかをチェック。`current_title_text == col1_text`で判定。
- **ReturnFalse3**: 同じ値の場合、取り込む（分割しない）。ルール2に基づく。
- **CheckSeenLabel**: 異なる値の場合、まだ登場していないかどうかをチェック。`state.has_seen_label(col1_text)`で判定。
- **ReturnTrue**: まだ登場していない場合、分割する。ルール1に基づく。
- **ReturnFalse4**: 既に登場している場合、取り込む（分割しない）。ルール2に基づく。

### handle_multi_column_non_labeled_list の詳細フロー

```mermaid
flowchart TD
    Start([handle_multi_column_non_labeled_list開始<br/>Columnが3つ以上で最初がラベルでないListを処理]) --> CreateElement["create_element_from_listでItemに変換を試みる<br/>Columnが3つ以上で最初がラベルでない場合でも<br/>Itemに変換できる場合がある（例: 「ｂ）」）"]
    
    CreateElement --> CheckCreated{"Itemに変換できた?<br/>new_child != None<br/>変換が成功したか?"}
    
    CheckCreated -->|No<br/>変換できない| CheckParent{"parent_tag == 'Paragraph'<br/>かつ last_child != None?<br/>Paragraph内で前のItemが存在する?"}
    
    CheckParent -->|Yes<br/>Paragraph内で前のItemが存在| AppendChild1["子要素として取り込む<br/>state.append_to_last_child<br/>前のItemの子要素として追加<br/>return False"]
    AppendChild1 --> End1([処理終了])
    
    CheckParent -->|No<br/>条件を満たさない| AppendChild2["独立したList要素として残す<br/>state.append_child<br/>変換できない場合はListのまま残す<br/>return False"]
    AppendChild2 --> End2([処理終了])
    
    CheckCreated -->|Yes<br/>変換できた| CheckLastChild{"last_child != None?<br/>前のItem要素が存在する?"}
    
    CheckLastChild -->|No<br/>最初の要素| SetLastChild1["新しいItemとして追加<br/>state.set_last_child<br/>state.add_seen_label<br/>最初の要素なので新しいItemとして設定<br/>return False"]
    SetLastChild1 --> End3([処理終了])
    
    CheckLastChild -->|Yes<br/>前の要素が存在| SplitCheck{"should_split_labeled_list<br/>分割判定<br/>ラベルの種類と値、既出チェックで判定"}
    
    SplitCheck -->|True<br/>分割する| SetLastChild2["分割する場合、新しいItemとして追加<br/>state.set_last_child<br/>state.add_seen_label<br/>新しいItemとして設定<br/>return False"]
    SetLastChild2 --> End4([処理終了])
    
    SplitCheck -->|False<br/>分割しない| AppendChild3["取り込む場合、子要素として取り込む<br/>state.append_to_last_child<br/>前のItemの子要素として追加<br/>return False"]
    AppendChild3 --> End5([処理終了])
```

**処理の説明:**

- **CreateElement**: `create_element_from_list`関数でItemに変換を試みる。Columnが3つ以上で最初がラベルでない場合でも、Itemに変換できる場合がある（例: 「ｂ）」は`is_label`が`False`を返すが、`create_element_from_list`でItemに変換される）。
- **CheckCreated**: `create_element_from_list`の戻り値（`new_child`）が`None`でないかどうかをチェック。変換が成功したかどうかを判定。
- **CheckParent**: Itemに変換できない場合、`parent_tag`が`'Paragraph'`で、`state.last_child`が`None`でないかどうかをチェック。Paragraph内で前のItemが存在するかどうかを判定。
- **AppendChild1**: Paragraph内で前のItemが存在する場合、子要素として取り込む。
- **AppendChild2**: 条件を満たさない場合、独立したList要素として残す。
- **CheckLastChild**: Itemに変換できた場合、`state.last_child`が`None`でないかどうかをチェック。前のItem要素が存在するかどうかを判定。
- **SetLastChild1**: 前のItem要素が存在しない場合（最初の要素）、新しいItemとして追加。
- **SplitCheck**: 前のItem要素が存在する場合、`should_split_labeled_list`で分割するかどうかを判定。ラベルの種類と値、既出チェックで判定。
- **SetLastChild2**: 分割する場合、新しいItemとして追加。
- **AppendChild3**: 分割しない場合、子要素として取り込む。

### handle_two_column_non_labeled_list の詳細フロー

```mermaid
flowchart TD
    Start([handle_two_column_non_labeled_list開始<br/>Columnが2つで最初がラベルでない、またはColumnが1つ以下]) --> CheckHasLabel{"has_label<br/>ラベルか?"}
    
    CheckHasLabel -->|Yes<br/>ラベル付き| CreateElement["create_element_from_listでItemに変換を試みる<br/>List要素をItem要素に変換"]
    
    CreateElement --> CheckCreated{"Itemに変換できた?<br/>new_child != None"}
    
    CheckCreated -->|Yes<br/>変換成功| CheckLastChild{"last_child != None?<br/>前のItem要素が存在する?"}
    
    CheckLastChild -->|No<br/>最初の要素| SetLastChild1["新しいItemとして追加<br/>state.set_last_child<br/>state.add_seen_label<br/>ラベルを記録"]
    SetLastChild1 --> End1([処理終了])
    
    CheckLastChild -->|Yes<br/>前の要素が存在| SplitCheck{"should_split_labeled_list<br/>分割判定<br/>ラベルの種類と値、既出チェックで判定"}
    
    SplitCheck -->|True<br/>分割する| SetLastChild2["分割する場合、新しいItemとして追加<br/>state.set_last_child<br/>state.add_seen_label<br/>ラベルを記録"]
    SetLastChild2 --> End2([処理終了])
    
    SplitCheck -->|False<br/>分割しない| AppendChild1["取り込む場合、子要素として取り込む<br/>state.append_to_last_child<br/>前のItem要素の子要素として追加"]
    AppendChild1 --> End3([処理終了])
    
    CheckCreated -->|No<br/>変換失敗| AppendChild2["子要素として取り込む<br/>state.append_to_last_child<br/>変換できない場合は子要素として取り込む"]
    AppendChild2 --> End4([処理終了])
    
    CheckHasLabel -->|No<br/>ラベルなし| AppendChild3["子要素として取り込む<br/>state.append_to_last_child<br/>前のItem要素の子要素として追加"]
    AppendChild3 --> End5([処理終了])
```

**処理の詳細:**

1. **ラベル付きListのチェック**
   - `has_label`が`True`（`is_label_text(col1_text, col_count)`が`True`）の場合：
     - `create_element_from_list`でItemに変換を試みる
     - 変換できた場合（`new_child != None`）：
       - 前のItem要素が存在する場合、`should_split_labeled_list`で分割/取り込み判定を行う
       - 分割する場合、`state.set_last_child(new_child)`で新しいItemとして追加
       - 分割しない場合、`state.append_to_last_child(child)`で子要素として取り込む
       - 前のItem要素が存在しない場合、`state.set_last_child(new_child)`で新しいItemとして追加
     - 変換できなかった場合：
       - `state.append_to_last_child(child)`で子要素として取り込む

2. **ラベルなしListの場合**
   - `state.append_to_last_child(child)`で子要素として取り込む
   - 前のItem要素の子要素として追加される

**重要なポイント:**

- **呼び出し条件**: この関数は、`is_label(col1_text)`が`False`かつ`is_kanji_number_label(col1_text)`が`False`の場合に呼び出されます
- **`has_label`の値**: `has_label`は`is_label_text(col1_text, col_count)`の結果で、`is_label_text`は`is_label(text) or is_kanji_number_label(text)`を返します
- **分割判定**: ラベル付きListでItemに変換できた場合、`should_split_labeled_list`で分割/取り込み判定を行う。ラベルの種類と値、既出チェックで判定。

**使用例:**
- Columnが2つで最初がテキスト（例: 「テキスト1」「テキスト2」）の場合、子要素として取り込まれます
- Columnが1つの場合、子要素として取り込まれます
- Columnが2つで最初がラベルだが`is_label`が`False`を返す場合でも、`has_label`が`True`の場合は変換を試みます

## 処理の優先順位

### handle_labeled_list_with_different_hierarchy の処理順序

1. **分割判定**（`should_split_labeled_list`）
   - ラベルの種類と値、既出チェックで判定
   - 同じラベルの種類でかつ同じ値がまだ登場していない（兄要素にない）：分割する
   - 同じラベルの種類でかつ、同じ値がすでに登場している：取り込む
   - ラベルの種類が異なる：取り込む

2. **それ以外**
   - デフォルトで取り込む

### handle_multi_column_non_labeled_list の処理順序

1. **create_element_from_listでItemに変換を試みる**
   - Columnが3つ以上で最初がラベルでない場合でも、Itemに変換できる場合がある

2. **Itemに変換できた場合、分割/取り込み判定**
   - `should_split_labeled_list`で分割/取り込み判定を行う
   - ラベルの種類と値、既出チェックで判定

3. **Itemに変換できない場合**
   - 子要素として取り込む

### handle_two_column_non_labeled_list の処理順序

1. **ラベル付きListの場合は変換を試みる**
   - `create_element_from_list`でItemに変換を試みる

2. **Itemに変換できた場合、分割/取り込み判定**
   - `should_split_labeled_list`で分割/取り込み判定を行う
   - ラベルの種類と値、既出チェックで判定

3. **ラベルなしListの場合**
   - 子要素として取り込む

## 重要なポイント

- **ラベルの種類による処理の統一**
  - アルファベットラベル、数字ラベル、その他のラベルに関わらず、同じルールで処理される
  - ラベルの種類が異なる場合は常に取り込む
  - 同じラベルの種類で同じ値が既に登場している場合は取り込む
  - 同じラベルの種類で異なる値がまだ登場していない場合は分割する

- **Column数は処理の分岐にのみ使用される**
  - Column数によって、どのハンドラー関数を呼び出すかを決定する
  - ただし、最終的な分割/取り込み判定は`should_split_labeled_list`で統一されている

- **既出ラベルのチェック**
  - `state.has_seen_label(col1_text)`で、同じ値のラベルが既に登場しているかどうかをチェック
  - 既に登場している場合は取り込む（分割しない）

- **ラベルIDが取得できない場合**
  - `detect_label_id`が`None`を返す場合、取り込む（分割しない）
