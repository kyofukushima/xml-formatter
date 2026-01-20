# Item以降のstep0スクリプト統合仕様書

## 目次

- [Item以降のstep0スクリプト統合仕様書](#item以降のstep0スクリプト統合仕様書)
  - [目次](#目次)
  - [概要](#概要)
    - [処理の目的](#処理の目的)
  - [共通の処理フロー](#共通の処理フロー)
    - [処理1の分岐条件（共通）](#処理1の分岐条件共通)
    - [処理2の分岐条件（共通）](#処理2の分岐条件共通)
  - [各階層の処理詳細](#各階層の処理詳細)
    - [Item要素変換（convert\_item\_step0.py）](#item要素変換convert_item_step0py)
      - [概要](#概要-1)
      - [設定](#設定)
      - [処理の特徴](#処理の特徴)
      - [入力例](#入力例)
      - [出力例](#出力例)
    - [Subitem1要素変換（convert\_subitem1\_step0.py）](#subitem1要素変換convert_subitem1_step0py)
      - [概要](#概要-2)
      - [設定](#設定-1)
      - [処理の特徴](#処理の特徴-1)
      - [入力例](#入力例-1)
      - [出力例](#出力例-1)
    - [Subitem2要素変換（convert\_subitem2\_step0.py）](#subitem2要素変換convert_subitem2_step0py)
      - [概要](#概要-3)
      - [設定](#設定-2)
      - [処理の特徴](#処理の特徴-2)
      - [入力例](#入力例-2)
      - [出力例](#出力例-2)
    - [Subitem3要素変換（convert\_subitem3\_step0.py）](#subitem3要素変換convert_subitem3_step0py)
      - [概要](#概要-4)
      - [設定](#設定-3)
      - [処理の特徴](#処理の特徴-3)
      - [入力例](#入力例-3)
      - [出力例](#出力例-3)
    - [Subitem4要素変換（convert\_subitem4\_step0.py）](#subitem4要素変換convert_subitem4_step0py)
      - [概要](#概要-5)
      - [設定](#設定-4)
      - [処理の特徴](#処理の特徴-4)
      - [入力例](#入力例-4)
      - [出力例](#出力例-4)
    - [Subitem5要素変換（convert\_subitem5\_step0.py）](#subitem5要素変換convert_subitem5_step0py)
      - [概要](#概要-6)
      - [設定](#設定-5)
      - [処理の特徴](#処理の特徴-5)
      - [入力例](#入力例-5)
      - [出力例](#出力例-5)
  - [各階層の設定比較](#各階層の設定比較)
    - [主な違い](#主な違い)
  - [補足事項](#補足事項)
    - [用語定義](#用語定義)
      - [空の要素](#空の要素)
      - [括弧付き科目名](#括弧付き科目名)
      - [括弧付き指導項目](#括弧付き指導項目)
    - [階層判定の基準](#階層判定の基準)
    - [処理の繰り返し](#処理の繰り返し)
    - [実装上の注意点](#実装上の注意点)
    - [共通モジュールの使用](#共通モジュールの使用)

---

## 概要

本仕様書は、Item要素以降の階層（Item、Subitem1〜Subitem5）を変換するstep0スクリプト群の処理ロジックを統合して説明する。

すべてのstep0スクリプトは、共通モジュール `xml_converter.py` を使用し、`ConversionConfig` で各階層の設定を指定して処理を実行する。

### 処理の目的

各階層で、親要素内の `List` 要素を子要素（Item/Subitem1〜Subitem5）に変換する。変換は以下の2段階で実行される：

- **処理1**: 親要素のSentence直後の要素（最初の1つのみ）を子要素に変換
- **処理2**: 処理1で生成された子要素の弟要素を順次処理し、子要素への取り込みまたは分割を実行

処理2で子要素が分割された場合、新しく生成された子要素に対して処理1から再実行される。

---

## 共通の処理フロー

```
親要素（Paragraph/Item/Subitem1〜Subitem4）
├─ Title要素
├─ Sentence要素
└─ 弟要素（複数）
    ↓
【処理1】最初の弟要素を子要素化
    ↓
【処理2】残りの弟要素を順次処理
    ├─ 子要素取り込み → 既存子要素の子要素として追加
    └─ 子要素分割 → 新子要素を作成
        ↓
        【処理1】から再実行
```

### 処理1の分岐条件（共通）

| 分岐 | 条件 | 処理内容 |
|------|------|----------|
| 分岐1 | 弟要素がColumnを含むList要素 | 1つ目のColumnをTitle、2つ目のColumnをSentenceに設定 |
| 分岐2-1 | （親要素が空の場合）弟要素がColumnを含まないList要素 | 処理をスキップ（Itemのみ適用されない） |
| 分岐2-2 | 弟要素がColumnを含まないList要素（括弧付き科目名） | 空の子要素を作成し、Sentenceの値を子要素Sentenceに設定 |
| 分岐2-3 | 弟要素がColumnを含まないList要素（括弧付き指導項目） | 空の子要素を作成し、Sentenceの値を子要素Sentenceに設定 |
| 分岐2-4 | 弟要素がColumnを含まないList要素（上記以外） | 空の子要素を作成し、Sentenceの値を子要素Sentenceに設定 |
| 分岐3 | 弟要素がList要素以外（TableStruct、FigStruct等） | そのまま配置（取り込み） |

### 処理2の分岐条件（共通）

| 分岐 | 条件 | 階層判定 | 処理内容 |
|------|------|----------|----------|
| 分岐1-1 | ColumnありList要素 | 同階層 | 子要素分割 |
| 分岐1-2 | ColumnありList要素 | 異なる階層 | 子要素取り込み |
| 分岐2-1 | ColumnなしList要素（通常テキスト） | - | 子要素取り込み |
| 分岐2-2 | ColumnなしList要素（括弧付き科目名） | 同階層 | 子要素分割 |
| 分岐2-3 | ColumnなしList要素（括弧付き指導項目） | 同階層 | 子要素分割 |
| 分岐3 | List要素以外（TableStruct、FigStruct等） | - | 子要素取り込み |

---

## 各階層の処理詳細

### Item要素変換（convert_item_step0.py）

#### 概要

`Paragraph` 要素内の `List` 要素を `Item` 要素に変換する。

#### 設定

```python
ConversionConfig(
    parent_tag='Paragraph',
    child_tag='Item',
    title_tag='ItemTitle',
    sentence_tag='ItemSentence',
    column_condition_min=2,  # Itemは col_count == 2
    supported_types=['labeled', 'subject_name', 'instruction', 'grade'],
    script_name='convert_item_step0',
    skip_empty_parent=False  # Item作成では親要素チェックをスキップ（空ParagraphでもItem作成）
)
```

#### 処理の特徴

1. **処理モードの概念**
   - `LOOKING_FOR_FIRST_ITEM`: 初期状態
   - `AGGREGATING_INTO_CONTAINER`: ColumnなしListが最初の場合、空のコンテナItemを作成し、後続のList要素をすべて取り込む
   - `NORMAL_PROCESSING`: ColumnありListが最初の場合、通常の取り込み・分割処理

2. **処理3（特殊分割）**
   - Paragraph要素内の最初のItem要素で、ItemTitleとItemSentenceが空の場合、条件に合致した場合に分割を実行
   - ColumnありList、括弧付き科目名、括弧付き指導項目が出現した場合に分割

#### 入力例

```xml
<Paragraph Num="1">
  <ParagraphNum/>
  <ParagraphSentence>
    <Sentence Num="1">paragraphsentenceの値</Sentence>
  </ParagraphSentence>
  <List>
    <ListSentence>
      <Column Num="1">
        <Sentence Num="1">１</Sentence>
      </Column>
      <Column Num="2">
        <Sentence Num="1">項目名1</Sentence>
      </Column>
    </ListSentence>
  </List>
</Paragraph>
```

#### 出力例

```xml
<Paragraph Num="1">
  <ParagraphNum/>
  <ParagraphSentence>
    <Sentence Num="1">paragraphsentenceの値</Sentence>
  </ParagraphSentence>
  <Item Num="1">
    <ItemTitle>１</ItemTitle>
    <ItemSentence Num="1">
      <Sentence Num="1">項目名1</Sentence>
    </ItemSentence>
  </Item>
</Paragraph>
```

---

### Subitem1要素変換（convert_subitem1_step0.py）

#### 概要

`Item` 要素内の `List` 要素を `Subitem1` 要素に変換する。

#### 設定

```python
ConversionConfig(
    parent_tag='Item',
    child_tag='Subitem1',
    title_tag='Subitem1Title',
    sentence_tag='Subitem1Sentence',
    column_condition_min=1,  # Subitem1は col_count >= 1
    supported_types=['labeled', 'subject_name', 'instruction', 'grade_single', 'grade_double'],
    script_name='convert_subitem1_step0',
    skip_empty_parent=True  # Subitem1変換では親要素チェックを行う
)
```

#### 処理の特徴

- Item要素が空（ItemTitleとItemSentenceが両方空）の場合、ColumnなしListをSubitem1化せずそのまま配置

#### 入力例

```xml
<Item Num="1">
  <ItemTitle>１</ItemTitle>
  <ItemSentence>
    <Sentence Num="1">項目名1</Sentence>
  </ItemSentence>
  <List>
    <ListSentence>
      <Column Num="1">
        <Sentence Num="1">（ア）</Sentence>
      </Column>
      <Column Num="2">
        <Sentence Num="1">下位項目名1</Sentence>
      </Column>
    </ListSentence>
  </List>
</Item>
```

#### 出力例

```xml
<Item Num="1">
  <ItemTitle>１</ItemTitle>
  <ItemSentence>
    <Sentence Num="1">項目名1</Sentence>
  </ItemSentence>
  <Subitem1 Num="1">
    <Subitem1Title>（ア）</Subitem1Title>
    <Subitem1Sentence>
      <Sentence Num="1">下位項目名1</Sentence>
    </Subitem1Sentence>
  </Subitem1>
</Item>
```

---

### Subitem2要素変換（convert_subitem2_step0.py）

#### 概要

`Subitem1` 要素内の `List` 要素を `Subitem2` 要素に変換する。

#### 設定

```python
ConversionConfig(
    parent_tag='Subitem1',
    child_tag='Subitem2',
    title_tag='Subitem2Title',
    sentence_tag='Subitem2Sentence',
    column_condition_min=0,  # Subitem2は col_count >= 0
    supported_types=['labeled', 'subject_name', 'instruction', 'grade_single', 'grade_double'],
    script_name='convert_subitem2_step0',
    skip_empty_parent=True  # Subitem2変換では親要素チェックを行う
)
```

#### 処理の特徴

- Subitem1要素が空（Subitem1TitleとSubitem1Sentenceが両方空）の場合、ColumnなしListをSubitem2化せずそのまま配置

#### 入力例

```xml
<Subitem1 Num="1">
  <Subitem1Title>（１）</Subitem1Title>
  <Subitem1Sentence>
    <Sentence Num="1">下位項目名1</Sentence>
  </Subitem1Sentence>
  <List>
    <ListSentence>
      <Column Num="1">
        <Sentence Num="1">ア</Sentence>
      </Column>
      <Column Num="2">
        <Sentence Num="1">さらに下位の項目名1</Sentence>
      </Column>
    </ListSentence>
  </List>
</Subitem1>
```

#### 出力例

```xml
<Subitem1 Num="1">
  <Subitem1Title>（１）</Subitem1Title>
  <Subitem1Sentence>
    <Sentence Num="1">下位項目名1</Sentence>
  </Subitem1Sentence>
  <Subitem2 Num="1">
    <Subitem2Title>ア</Subitem2Title>
    <Subitem2Sentence>
      <Sentence Num="1">さらに下位の項目名1</Sentence>
    </Subitem2Sentence>
  </Subitem2>
</Subitem1>
```

---

### Subitem3要素変換（convert_subitem3_step0.py）

#### 概要

`Subitem2` 要素内の `List` 要素を `Subitem3` 要素に変換する。

#### 設定

```python
ConversionConfig(
    parent_tag='Subitem2',
    child_tag='Subitem3',
    title_tag='Subitem3Title',
    sentence_tag='Subitem3Sentence',
    column_condition_min=2,  # Subitem3は col_count == 2
    supported_types=['labeled', 'subject_name', 'instruction', 'grade_single', 'grade_double', 'circled_number'],
    script_name='convert_subitem3_step0',
    skip_empty_parent=True  # Subitem3変換では親要素チェックをスキップ
)
```

#### 処理の特徴

- 丸数字（①、②など）をラベルとして認識する（`circled_number` タイプをサポート）

#### 入力例

```xml
<Subitem2 Num="1">
  <Subitem2Title>（ア）</Subitem2Title>
  <Subitem2Sentence>
    <Sentence Num="1">下位項目名1</Sentence>
  </Subitem2Sentence>
  <List>
    <ListSentence>
      <Column Num="1">
        <Sentence Num="1">①</Sentence>
      </Column>
      <Column Num="2">
        <Sentence Num="1">さらに下位の項目名1</Sentence>
      </Column>
    </ListSentence>
  </List>
</Subitem2>
```

#### 出力例

```xml
<Subitem2 Num="1">
  <Subitem2Title>（ア）</Subitem2Title>
  <Subitem2Sentence>
    <Sentence Num="1">下位項目名1</Sentence>
  </Subitem2Sentence>
  <Subitem3 Num="1">
    <Subitem3Title>①</Subitem3Title>
    <Subitem3Sentence>
      <Sentence Num="1">さらに下位の項目名1</Sentence>
    </Subitem3Sentence>
  </Subitem3>
</Subitem2>
```

---

### Subitem4要素変換（convert_subitem4_step0.py）

#### 概要

`Subitem3` 要素内の `List` 要素を `Subitem4` 要素に変換する。

#### 設定

```python
ConversionConfig(
    parent_tag='Subitem3',
    child_tag='Subitem4',
    title_tag='Subitem4Title',
    sentence_tag='Subitem4Sentence',
    column_condition_min=2,  # Subitem4は col_count == 2
    supported_types=['labeled', 'subject_name', 'instruction', 'grade_single', 'grade_double'],
    script_name='convert_subitem4_step0',
    skip_empty_parent=True  # Subitem4変換では親要素チェックを行う
)
```

#### 処理の特徴

- Subitem3要素が空（Subitem3TitleとSubitem3Sentenceが両方空）の場合、ColumnなしListをSubitem4化せずそのまま配置

#### 入力例

```xml
<Subitem3 Num="1">
  <Subitem3Title>①</Subitem3Title>
  <Subitem3Sentence>
    <Sentence Num="1">さらに下位の項目名1</Sentence>
  </Subitem3Sentence>
  <List>
    <ListSentence>
      <Column Num="1">
        <Sentence Num="1">１</Sentence>
      </Column>
      <Column Num="2">
        <Sentence Num="1">もっと下位の項目名1</Sentence>
      </Column>
    </ListSentence>
  </List>
</Subitem3>
```

#### 出力例

```xml
<Subitem3 Num="1">
  <Subitem3Title>①</Subitem3Title>
  <Subitem3Sentence>
    <Sentence Num="1">さらに下位の項目名1</Sentence>
  </Subitem3Sentence>
  <Subitem4 Num="1">
    <Subitem4Title>１</Subitem4Title>
    <Subitem4Sentence>
      <Sentence Num="1">もっと下位の項目名1</Sentence>
    </Subitem4Sentence>
  </Subitem4>
</Subitem3>
```

---

### Subitem5要素変換（convert_subitem5_step0.py）

#### 概要

`Subitem4` 要素内の `List` 要素を `Subitem5` 要素に変換する。

#### 設定

```python
ConversionConfig(
    parent_tag='Subitem4',
    child_tag='Subitem5',
    title_tag='Subitem5Title',
    sentence_tag='Subitem5Sentence',
    column_condition_min=2,  # Subitem5は col_count == 2
    supported_types=['labeled', 'subject_name', 'instruction', 'grade_single', 'grade_double'],
    script_name='convert_subitem5_step0',
    skip_empty_parent=True  # Subitem5変換では親要素チェックを行う
)
```

#### 処理の特徴

- Subitem4要素が空（Subitem4TitleとSubitem4Sentenceが両方空）の場合、ColumnなしListをSubitem5化せずそのまま配置
- 最下位階層のため、これ以上下位の階層は生成されない

#### 入力例

```xml
<Subitem4 Num="1">
  <Subitem4Title>１</Subitem4Title>
  <Subitem4Sentence>
    <Sentence Num="1">もっと下位の項目名1</Sentence>
  </Subitem4Sentence>
  <List>
    <ListSentence>
      <Column Num="1">
        <Sentence Num="1">（ａ）</Sentence>
      </Column>
      <Column Num="2">
        <Sentence Num="1">最下位の項目名1</Sentence>
      </Column>
    </ListSentence>
  </List>
</Subitem4>
```

#### 出力例

```xml
<Subitem4 Num="1">
  <Subitem4Title>１</Subitem4Title>
  <Subitem4Sentence>
    <Sentence Num="1">もっと下位の項目名1</Sentence>
  </Subitem4Sentence>
  <Subitem5 Num="1">
    <Subitem5Title>（ａ）</Subitem5Title>
    <Subitem5Sentence>
      <Sentence Num="1">最下位の項目名1</Sentence>
    </Subitem5Sentence>
  </Subitem5>
</Subitem4>
```

---

## 各階層の設定比較

| 階層 | 親要素 | 子要素 | Title要素 | Sentence要素 | Column条件 | 空親要素スキップ | サポートタイプ |
|------|--------|--------|-----------|--------------|------------|------------------|----------------|
| Item | Paragraph | Item | ItemTitle | ItemSentence | col_count == 2 | False | labeled, subject_name, instruction, grade |
| Subitem1 | Item | Subitem1 | Subitem1Title | Subitem1Sentence | col_count >= 1 | True | labeled, subject_name, instruction, grade_single, grade_double |
| Subitem2 | Subitem1 | Subitem2 | Subitem2Title | Subitem2Sentence | col_count >= 0 | True | labeled, subject_name, instruction, grade_single, grade_double |
| Subitem3 | Subitem2 | Subitem3 | Subitem3Title | Subitem3Sentence | col_count == 2 | True | labeled, subject_name, instruction, grade_single, grade_double, **circled_number** |
| Subitem4 | Subitem3 | Subitem4 | Subitem4Title | Subitem4Sentence | col_count == 2 | True | labeled, subject_name, instruction, grade_single, grade_double |
| Subitem5 | Subitem4 | Subitem5 | Subitem5Title | Subitem5Sentence | col_count == 2 | True | labeled, subject_name, instruction, grade_single, grade_double |

### 主な違い

1. **Column条件**
   - Item: `col_count == 2`（厳密に2カラム）
   - Subitem1: `col_count >= 1`（1カラム以上）
   - Subitem2: `col_count >= 0`（カラムなしも可）
   - Subitem3〜5: `col_count == 2`（厳密に2カラム）

2. **空親要素の扱い**
   - Item: `skip_empty_parent=False`（空ParagraphでもItem作成）
   - Subitem1〜5: `skip_empty_parent=True`（空親要素の場合は処理をスキップ）

3. **サポートタイプ**
   - Item: `grade`（学年パターン全般）
   - Subitem1〜5: `grade_single`, `grade_double`（単一学年、二学年並列）
   - Subitem3のみ: `circled_number`（丸数字）を追加サポート

---

## 補足事項

### 用語定義

#### 空の要素

以下の構造を持つ要素を指す：
```xml
<Item Num="1">
  <ItemTitle/>
  <ItemSentence Num="1">
    <Sentence Num="1"></Sentence>
  </ItemSentence>
</Item>
```

#### 括弧付き科目名

- `〔...〕`または`【...】`で囲まれたテキスト
- 例: `〔科目名A〕`、`【数学】`
- `指導項目`という文字列を含まない

#### 括弧付き指導項目

- `〔指導項目〕`または`【指導項目】`という完全一致のテキスト

### 階層判定の基準

項目ラベルの種類（形式）で階層を判定する：

- **Itemレベル**: `１`、`２`、`１．`、`2.`
- **Subitem1レベル**: `（１）`、`(1)`、`ア`、`イ`、`（ア）`、`（イ）`
- **Subitem2レベル**: `(ア)`、`(イ)`、`ａ`、`ｂ`、`A`、`a`
- **Subitem3レベル**: `①`、`②`（丸数字）
- **Subitem4レベル**: `１`、`２`（Subitem3レベルの「１」「２」とは異なる形式の場合）
- **Subitem5レベル**: `（ａ）`、`（ｂ）`、`(a)`、`(b)`

同じ種類のラベルは同階層と判定される。

### 処理の繰り返し

処理2で子要素が分割された場合：
1. 新しい子要素が作成される
2. 分割点以降の弟要素が残る
3. 新しい子要素に対して**処理1から再実行**される
4. 全ての弟要素が処理されるまで繰り返す

### 実装上の注意点

- 処理1は常に最初の弟要素のみを処理する
- 処理2は全ての弟要素を順次処理する
- 階層判定は項目ラベルの形式で行う（内容ではない）
- TableStruct、FigStruct等の非List要素は常に取り込み対象
- Num属性は適切に連番を付与する
- すべてのstep0スクリプトは `xml_converter.py` の共通モジュールを使用

### 共通モジュールの使用

すべてのstep0スクリプトは以下のように共通モジュールを使用する：

```python
from xml_converter import ConversionConfig, process_xml_file

config = ConversionConfig(
    parent_tag='...',
    child_tag='...',
    title_tag='...',
    sentence_tag='...',
    column_condition_min=...,
    supported_types=[...],
    script_name='...',
    skip_empty_parent=...
)

return process_xml_file(input_path, output_path, config)
```

---

**更新履歴**
- 2025年12月: Item、Subitem1、Subitem2、Subitem3の仕様書を統合
- 2025年12月: Subitem4、Subitem5の仕様を追加
- 2025年12月: 統合仕様書として初版作成
