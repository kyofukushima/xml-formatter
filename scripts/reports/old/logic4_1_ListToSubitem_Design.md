# List要素をSubitem要素に変換するロジック設計書

## 概要

このドキュメントは、`convert_list_to_subitem.py`の設計と実装について説明します。`logic3_1_Item.md`に基づき、Item要素に続くList要素を適切なSubitem1〜Subitem10の階層構造に変換します。

## 参照ドキュメント

- `scripts/education_script/reports/logic3_1_Item.md` - 変換ロジックの仕様
- `scripts/education_script/utils/label_utils.py` - ラベル判定ユーティリティ
- `scripts/education_script/utils/xml_utils.py` - XML処理ユーティリティ

## 変換パターン

### パターン1: Columnを含まないList要素の処理

**対象**: Item要素の直後に連続するColumnなしList要素

**処理内容**:
1. 連続するColumnなしList要素を収集
2. 空のSubitem1要素を作成
3. 収集したList要素をSubitem1内に移動
4. ItemSentenceの直後に挿入

**入力例**:
```xml
<Item Num="2">
    <ItemTitle>（２）</ItemTitle>
    <ItemSentence>
        <Sentence>項目２</Sentence>
    </ItemSentence>
</Item>
<List>
    <ListSentence>
        <Sentence>テキスト１</Sentence>
    </ListSentence>
</List>
<List>
    <ListSentence>
        <Sentence>テキスト２</Sentence>
    </ListSentence>
</List>
```

**出力例**:
```xml
<Item Num="2">
    <ItemTitle>（２）</ItemTitle>
    <ItemSentence>
        <Sentence>項目２</Sentence>
    </ItemSentence>
    <Subitem1 Num="1">
        <Subitem1Title></Subitem1Title>
        <Subitem1Sentence>
            <Sentence></Sentence>
        </Subitem1Sentence>
        <List>
            <ListSentence>
                <Sentence>テキスト１</Sentence>
            </ListSentence>
        </List>
        <List>
            <ListSentence>
                <Sentence>テキスト２</Sentence>
            </ListSentence>
        </List>
    </Subitem1>
</Item>
```

### パターン1-2: 括弧科目名（〔XXX〕）の処理

**対象**: 〔医療と社会〕、〔指導項目〕などの科目名

**処理内容**:

#### ケース1: Item内にSubitemが既に存在する場合
1. 最後のSubitemレベルを取得
2. 1つ深い階層のSubitemを作成
3. 空のSubitemを親として、深い階層Subitemを子として追加

**入力例**:
```xml
<Item Num="2">
    <ItemTitle>（1）</ItemTitle>
    <ItemSentence>
        <Sentence>項目1</Sentence>
    </ItemSentence>
    <Subitem1 Num="1">
        <Subitem1Title></Subitem1Title>
        <Subitem1Sentence>
            <Sentence></Sentence>
        </Subitem1Sentence>
        <List>
            <ListSentence>
                <Sentence>テキスト１</Sentence>
            </ListSentence>
        </List>
    </Subitem1>
</Item>
<List>
    <ListSentence>
        <Sentence>〔項目2〕</Sentence>
    </ListSentence>
</List>
```

**出力例**:
```xml
<Item Num="2">
    <ItemTitle>（1）</ItemTitle>
    <ItemSentence>
        <Sentence>項目1</Sentence>
    </ItemSentence>
    <Subitem1 Num="1">
        <Subitem1Title></Subitem1Title>
        <Subitem1Sentence>
            <Sentence></Sentence>
        </Subitem1Sentence>
        <List>
            <ListSentence>
                <Sentence>テキスト１</Sentence>
            </ListSentence>
        </List>
    </Subitem1>
    <Subitem1 Num="2">
        <Subitem1Title></Subitem1Title>
        <Subitem1Sentence>
            <Sentence></Sentence>
        </Subitem1Sentence>
        <Subitem2 Num="1">
            <Subitem2Title></Subitem2Title>
            <Subitem2Sentence>
                <Sentence>〔項目2〕</Sentence>
            </Subitem2Sentence>
        </Subitem2>
    </Subitem1>
</Item>
```

#### ケース2: Item内にSubitemが存在しない場合
1. Subitem1を作成
2. Sentenceに科目名を設定

**入力例**:
```xml
<Item Num="2">
    <ItemTitle>１</ItemTitle>
    <ItemSentence>
        <Sentence>項目1</Sentence>
    </ItemSentence>
</Item>
<List>
    <ListSentence>
        <Sentence>〔項目2〕</Sentence>
    </ListSentence>
</List>
```

**出力例**:
```xml
<Item Num="2">
    <ItemTitle>１</ItemTitle>
    <ItemSentence>
        <Sentence>項目1</Sentence>
    </ItemSentence>
    <Subitem1 Num="1">
        <Subitem1Title></Subitem1Title>
        <Subitem1Sentence>
            <Sentence>〔項目2〕</Sentence>
        </Subitem1Sentence>
    </Subitem1>
</Item>
```

### パターン2-1: より深い階層のColumn付きList処理

**対象**: ItemTitleより深い階層レベルのラベルを持つColumn付きList

**処理内容**:
1. Column形式のList要素を分析
2. ラベルの階層レベルを判定
3. ItemTitleより深い場合、適切なSubitemレベルを決定
4. 同レベルの連続するList要素を収集
5. Subitem要素に変換して挿入

**階層レベル決定ロジック**:

#### ItemTitleが空の場合
| ラベル階層 | ラベル例 | Subitemレベル |
|----------|---------|-------------|
| 2 (括弧数字) | （１）、（２） | 1 |
| 3 (カタカナ) | ア、イ、ウ | 1 |
| 4 (括弧カタカナ) | （ア）、（イ） | 2 |
| 5以上 | （（ア））、(a) | label_level - 2 |

#### ItemTitleがある場合
親ラベルと新ラベルの階層差分からSubitemレベルを決定:

- ItemTitle（括弧数字=2）→ カタカナ(3): **Subitem1**
- ItemTitle（括弧数字=2）→ 括弧カタカナ(4): **Subitem2**
- 一般ケース: min(level_diff, 10)

**入力例**:
```xml
<Item Num="1">
    <ItemTitle>（１）</ItemTitle>
    <ItemSentence>
        <Sentence>項目名1</Sentence>
    </ItemSentence>
</Item>
<List>
    <ListSentence>
        <Column Num="1">
            <Sentence>ア</Sentence>
        </Column>
        <Column Num="2">
            <Sentence>項目名2</Sentence>
        </Column>
    </ListSentence>
</List>
<List>
    <ListSentence>
        <Column Num="1">
            <Sentence>イ</Sentence>
        </Column>
        <Column Num="2">
            <Sentence>項目名3</Sentence>
        </Column>
    </ListSentence>
</List>
<List>
    <ListSentence>
        <Column Num="1">
            <Sentence>（ア）</Sentence>
        </Column>
        <Column Num="2">
            <Sentence>項目名4</Sentence>
        </Column>
    </ListSentence>
</List>
```

**出力例**:
```xml
<Item Num="1">
    <ItemTitle>（１）</ItemTitle>
    <ItemSentence>
        <Sentence>項目名1</Sentence>
    </ItemSentence>
    <Subitem1 Num="1">
        <Subitem1Title>ア</Subitem1Title>
        <Subitem1Sentence>
            <Sentence>項目名2</Sentence>
        </Subitem1Sentence>
    </Subitem1>
    <Subitem1 Num="2">
        <Subitem1Title>イ</Subitem1Title>
        <Subitem1Sentence>
            <Sentence>項目名3</Sentence>
        </Subitem1Sentence>
        <Subitem2 Num="1">
            <Subitem2Title>（ア）</Subitem2Title>
            <Subitem2Sentence>
                <Sentence>項目名4</Sentence>
            </Subitem2Sentence>
        </Subitem2>
    </Subitem1>
</Item>
```

### パターン2-2: 同じ階層レベルのColumn付きList処理

**対象**: ItemTitleと同じ階層レベルのラベルを持つColumn付きList

**処理**: Item要素の分割が必要（上位の処理で実行）

この処理は`convert_list_to_subitem.py`では実装せず、別のスクリプトで処理します。理由は、Item要素を分割するには親要素（Paragraph等）へのアクセスが必要で、Itemレベルの処理では適切に実装できないためです。

## クラス設計

### ListToSubitemConverter

List要素をSubitem要素に変換するメインクラス。

#### 主要メソッド

##### `process_pattern1_non_column_lists(item, following_lists) -> bool`

処理１: Columnを含まないList要素を処理

**パラメータ**:
- `item`: 処理対象のItem要素
- `following_lists`: Item直後のList要素リスト

**戻り値**:
- `bool`: 処理が実行された場合True

**処理フロー**:
1. 先頭から連続するColumnなしListを収集
2. 空のSubitem1を作成
3. List要素をSubitem1に移動
4. ItemSentenceの直後に挿入

##### `process_pattern1_2_subject_label(item, following_lists) -> bool`

処理１−２: 括弧科目名（〔XXX〕）を処理

**パラメータ**:
- `item`: 処理対象のItem要素
- `following_lists`: Item直後のList要素リスト

**戻り値**:
- `bool`: 処理が実行された場合True

**処理フロー**:
1. 最初のList要素が〔XXX〕形式かチェック
2. Item内の最深Subitemレベルを取得
3. 既存Subitemがある場合: 1つ深い階層を作成
4. Subitemがない場合: Subitem1を作成

##### `determine_subitem_level(label, parent_label) -> Optional[int]`

ラベルから適切なSubitemレベルを決定

**パラメータ**:
- `label`: 新しいラベル
- `parent_label`: 親要素のラベル

**戻り値**:
- `Optional[int]`: Subitemレベル（1-10）、決定できない場合None

**判定ロジック**:

1. **親ラベルがない場合**:
   - 括弧数字(2) → Subitem1
   - カタカナ(3) → Subitem1
   - 括弧カタカナ(4) → Subitem2
   - それ以上 → label_level - 2

2. **親ラベルがある場合**:
   - 同じ階層レベル → None（分割が必要）
   - ItemTitle（括弧数字=2）+ カタカナ(3) → Subitem1
   - ItemTitle（括弧数字=2）+ 括弧カタカナ(4) → Subitem2
   - 一般ケース → min(level_diff, 10)

##### `process_pattern2_1_deeper_hierarchy(item, following_lists) -> bool`

処理２−１: より深い階層のColumn付きListを処理

**パラメータ**:
- `item`: 処理対象のItem要素
- `following_lists`: Item直後のList要素リスト

**戻り値**:
- `bool`: 処理が実行された場合True

**処理フロー**:
1. Column付きList要素を順次処理
2. ラベルの階層レベルを判定
3. ItemTitleと同じレベルの場合は処理終了
4. より深い場合、Subitemレベルを決定
5. 同レベルの連続Listを収集
6. Subitem要素に変換
7. 適切な親要素に挿入

##### `process_item(item) -> None`

Item要素とその後続List要素を処理

**パラメータ**:
- `item`: 処理対象のItem要素

**処理フロー**:
1. Item要素の親要素を取得
2. Item直後のList要素を収集
3. 処理１: Columnなし List
4. 処理１−２: 括弧科目名
5. 処理２−１: より深い階層
6. 変換済みList要素を削除

##### `convert_tree(root) -> None`

XMLツリー全体を処理

**パラメータ**:
- `root`: XMLルート要素

**処理フロー**:
1. 全Item要素を収集
2. 逆順で各Itemを処理（削除の影響回避）
3. 統計情報を更新

## ユーティリティ関数

### label_utils.py

#### `detect_label_pattern(text) -> LabelPattern`

テキストが項目ラベルかどうかを判定し、パターンを返す。

**優先順位**:
1. 括弧科目名（〔XXX〕）
2. 第○パターン
3. 二重括弧カタカナ
4. 括弧アルファベット
5. 括弧カタカナ
6. 括弧数字
7. カタカナ
8. アルファベット
9. 数字
10. 空

#### `get_hierarchy_level(label) -> int`

項目ラベルの階層レベル（0-7）を返す。

**階層レベル**:
- 0: 第○パターン
- 1: 数字
- 2: 括弧数字
- 3: カタカナ
- 4: 括弧カタカナ
- 5: 二重括弧カタカナ
- 6: アルファベット
- 7: 括弧アルファベット

### xml_utils.py

#### `indent_xml(elem, level=0)`

XML要素を整形（pretty print）する。

## 使用方法

### 基本的な使用

```bash
python convert_list_to_subitem.py input.xml output.xml
```

### デバッグモード

```bash
python convert_list_to_subitem.py input.xml output.xml --debug
```

デバッグモードでは、処理の詳細ログが出力されます。

### 出力ファイル名の自動生成

出力ファイル名を省略すると、入力ファイル名に`_subitem`を付加したファイル名が使用されます。

```bash
python convert_list_to_subitem.py input.xml
# 出力: input_subitem.xml
```

## 統計情報

変換終了時に以下の統計情報が出力されます:

- `items_processed`: 処理したItem要素数
- `lists_converted`: 変換したList要素数
- `subitems_created`: 作成したSubitem要素数
- `lists_moved`: Subitem内に移動したList要素数
- `subject_labels_processed`: 処理した括弧科目名数

## 制限事項

1. **Item分割非対応**: パターン2-2（同じ階層レベルのList）によるItem分割は未実装
2. **Subitem10の制限**: Subitem10を超える階層は作成不可
3. **親要素の制約**: Item要素が適切な親要素（Paragraph等）に含まれている必要がある

## 今後の拡張

### Item分割機能の実装

パターン2-2を実装するための別スクリプト`split_item_by_same_level.py`が必要です:

```python
def split_items_by_same_level_labels(paragraph: ET.Element) -> List[ET.Element]:
    """
    Paragraphを分析し、同じ階層レベルのColumn付きListで
    Item要素を分割
    """
    pass
```

### より高度なラベル判定

現在のラベル判定は固定パターンに基づいていますが、以下のような拡張が考えられます:

- 複合ラベル（1.1.1、1.1.2等）への対応
- カスタムラベルパターンの追加
- コンテキストに応じた動的な階層判定

## テストケース

### テスト1: Columnなし List処理

**入力**: Item + 3個のColumnなしList
**期待結果**: 全ListがSubitem1内に収容

### テスト2: 括弧科目名処理（Subitemなし）

**入力**: Item（Subitemなし） + 〔科目名〕
**期待結果**: Subitem1が作成され、Sentenceに科目名

### テスト3: 括弧科目名処理（Subitemあり）

**入力**: Item（Subitem1あり） + 〔科目名〕
**期待結果**: 新しいSubitem1 + Subitem2が作成

### テスト4: より深い階層（単一レベル）

**入力**: Item（括弧数字） + カタカナ List×2
**期待結果**: 2個のSubitem1が作成

### テスト5: より深い階層（多層）

**入力**: Item（括弧数字） + カタカナ List×2 + 括弧カタカナ List
**期待結果**: Subitem1×2、最後のSubitem1内にSubitem2

## 参考資料

- [logic3_1_Item.md](./logic3_1_Item.md) - 変換ロジックの詳細仕様
- [label_utils.py](../utils/label_utils.py) - ラベル判定実装
- [convert_list_to_item_v2.py](../archive/convert_list_to_item_v2.py) - 既存の変換スクリプト

## 更新履歴

- 2025-01-XX: 初版作成
- 処理パターン1、1-2、2-1を実装
- label_utilsとの統合
- 統計情報機能の追加
