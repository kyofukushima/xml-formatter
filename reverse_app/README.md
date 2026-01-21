# 逆変換スクリプト仕様書

このフォルダには、Paragraph~subitem要素をList要素に逆変換するスクリプト群が含まれています。

## 目次

1. [スクリプト一覧](#スクリプト一覧)
2. [逆変換の定義](#逆変換の定義)
3. [変換仕様](#変換仕様)
4. [処理順序と順序保持](#処理順序と順序保持)
5. [特殊なケースの処理](#特殊なケースの処理)
6. [使用方法](#使用方法)
7. [注意事項](#注意事項)

---

## スクリプト一覧

- `reverse_xml_converter.py` - 逆変換機能の共通モジュール
- `reverse_convert_item.py` - Paragraph内のItem要素をList要素に変換
- `reverse_convert_subitem1.py` - Item内のSubitem1要素をList要素に変換
- `reverse_convert_subitem2.py` - Subitem1内のSubitem2要素をList要素に変換
- `reverse_convert_subitem3.py` - Subitem2内のSubitem3要素をList要素に変換
- `reverse_convert_subitem4.py` - Subitem3内のSubitem4要素をList要素に変換
- `reverse_convert_subitem5.py` - Subitem4内のSubitem5要素をList要素に変換
- `reverse_convert_subitem6.py` - Subitem5内のSubitem6要素をList要素に変換
- `reverse_convert_subitem7.py` - Subitem6内のSubitem7要素をList要素に変換
- `reverse_convert_subitem8.py` - Subitem7内のSubitem8要素をList要素に変換
- `reverse_convert_subitem9.py` - Subitem8内のSubitem9要素をList要素に変換
- `reverse_convert_subitem10.py` - Subitem9内のSubitem10要素をList要素に変換
- `run_reverse_pipeline.sh` - 逆変換パイプライン実行スクリプト

---

## 逆変換の定義

逆変換とは、階層構造（Item → Subitem1 → Subitem2 → ...）を、フラットなList要素の並びに変換する処理です。

**対応範囲**: ItemからSubitem1~10の範囲。変換できないもの（TableStructなど）はスルーされます。

**例:**
```xml
<!-- 変換前（階層構造） -->
<Subitem1 Num="1">
  <Subitem1Title>1</Subitem1Title>
  <Subitem1Sentence>
    <Sentence Num="1">subitem1要素</Sentence>
  </Subitem1Sentence>
  <Subitem2 Num="1">
    <Subitem2Title>a</Subitem2Title>
    <Subitem2Sentence>
      <Sentence Num="1">subitem2要素</Sentence>
    </Subitem2Sentence>
  </Subitem2>
</Subitem1>
```

```xml
<!-- 変換後（フラットなList要素の並び） -->
<List>
  <ListSentence>
    <Column Num="1">
      <Sentence Num="1">1</Sentence>
    </Column>
    <Column Num="2">
      <Sentence Num="1">subitem1要素</Sentence>
    </Column>
  </ListSentence>
</List>
<List>
  <ListSentence>
    <Column Num="1">
      <Sentence Num="1">a</Sentence>
    </Column>
    <Column Num="2">
      <Sentence Num="1">subitem2要素</Sentence>
    </Column>
  </ListSentence>
</List>
```

---

## 変換仕様

### 基本ケース

#### ケース1: タイトル要素がある場合（ItemTitle/Subitem1Title/.../Subitem10Title）

**条件**: タイトル要素が存在し、かつ空でない場合

**変換結果**: 2カラムのList要素に変換
- Column1: タイトル内容
- Column2: 本文内容（ItemSentence/Subitem1Sentence/.../Subitem10Sentence）

**例:**
```xml
<!-- 変換前 -->
<Item Num="1">
  <ItemTitle>（１）</ItemTitle>
  <ItemSentence>
    <Sentence Num="1">項目A</Sentence>
  </ItemSentence>
</Item>
```

```xml
<!-- 変換後 -->
<List>
  <ListSentence>
    <Column Num="1">
      <Sentence Num="1">（１）</Sentence>
    </Column>
    <Column Num="2">
      <Sentence Num="1">項目A</Sentence>
    </Column>
  </ListSentence>
</List>
```

#### ケース2: タイトル要素がない場合（空または存在しない）

**条件**: タイトル要素が空または存在しない場合

**変換結果**: ColumnのないList要素に変換
- ListSentence内のSentenceに本文内容

**例:**
```xml
<!-- 変換前 -->
<Subitem3 Num="1">
  <Subitem3Title/>
  <Subitem3Sentence>
    <Sentence Num="1">テキスト</Sentence>
  </Subitem3Sentence>
</Subitem3>
```

```xml
<!-- 変換後 -->
<List>
  <ListSentence>
    <Sentence Num="1">テキスト</Sentence>
  </ListSentence>
</List>
```

### 複数Column要素がある場合

#### ケース3: ItemTitleがあり、ItemSentenceに複数のColumn要素がある場合

**条件**: 
- `ItemTitle`が存在し、かつ空でない
- `ItemSentence`内に複数の`Column`要素が存在する

**変換結果**: 複数カラムのList要素に変換
- `ItemTitle`を最初のColumn（Column Num="1"）として追加
- `ItemSentence`内のすべての`Column`要素を順番に追加（Column Num="2", "3", ...）

**例:**
```xml
<!-- 変換前 -->
<Item Num="1">
  <ItemTitle>（１）</ItemTitle>
  <ItemSentence>
    <Column Num="1">
      <Sentence Num="1">項目A</Sentence>
    </Column>
    <Column Num="2">
      <Sentence Num="1">項目B</Sentence>
    </Column>
    <Column Num="3">
      <Sentence Num="1">項目C</Sentence>
    </Column>
  </ItemSentence>
</Item>
```

```xml
<!-- 変換後 -->
<List>
  <ListSentence>
    <Column Num="1">
      <Sentence Num="1">（１）</Sentence>
    </Column>
    <Column Num="2">
      <Sentence Num="1">項目A</Sentence>
    </Column>
    <Column Num="3">
      <Sentence Num="1">項目B</Sentence>
    </Column>
    <Column Num="4">
      <Sentence Num="1">項目C</Sentence>
    </Column>
  </ListSentence>
</List>
```

#### ケース4: ItemTitleが空で、ItemSentenceに複数のColumn要素がある場合

**条件**:
- `ItemTitle`が空または存在しない
- `ItemSentence`内に複数の`Column`要素が存在する

**変換結果**: 複数カラムのList要素に変換
- `ItemSentence`内のすべての`Column`要素をそのまま使用（Column Num="1", "2", ...）

**例:**
```xml
<!-- 変換前 -->
<Item Num="1">
  <ItemTitle></ItemTitle>
  <ItemSentence>
    <Column Num="1">
      <Sentence Num="1">項目名</Sentence>
    </Column>
    <Column Num="2">
      <Sentence Num="1">内容A</Sentence>
    </Column>
    <Column Num="3">
      <Sentence Num="1">内容B</Sentence>
    </Column>
  </ItemSentence>
</Item>
```

```xml
<!-- 変換後 -->
<List>
  <ListSentence>
    <Column Num="1">
      <Sentence Num="1">項目名</Sentence>
    </Column>
    <Column Num="2">
      <Sentence Num="1">内容A</Sentence>
    </Column>
    <Column Num="3">
      <Sentence Num="1">内容B</Sentence>
    </Column>
  </ListSentence>
</List>
```

### その他の要素

- **List要素以外の要素** → 変更されずにスルー
- **既存のList要素** → 変更されません

---

## 処理順序と順序保持

### 実行順序

逆変換は以下の順序で実行する必要があります（**内側から外側へ**）：

1. `reverse_convert_subitem10.py` - Subitem10 → List
2. `reverse_convert_subitem9.py` - Subitem9 → List
3. `reverse_convert_subitem8.py` - Subitem8 → List
4. `reverse_convert_subitem7.py` - Subitem7 → List
5. `reverse_convert_subitem6.py` - Subitem6 → List
6. `reverse_convert_subitem5.py` - Subitem5 → List
7. `reverse_convert_subitem4.py` - Subitem4 → List
8. `reverse_convert_subitem3.py` - Subitem3 → List
9. `reverse_convert_subitem2.py` - Subitem2 → List
10. `reverse_convert_subitem1.py` - Subitem1 → List
11. `reverse_convert_item.py` - Item → List

パイプラインスクリプト（`run_reverse_pipeline.sh`）はこの順序で自動実行します。

### 順序保持の原則

**重要な原則**: 階層構造の順序が失われても問題ありません。重要なのは、**XMLファイル上で登場する値の順番が変わっていないこと**です。

- 各階層を独立して処理しても、XMLファイルを順番に読み込んで処理することで、登場する値の順序は保持されます
- 階層構造の情報（どの要素がどの階層に属していたか）は失われますが、これは許容範囲内です
- 逆変換後のXMLファイルで、元のXMLファイルと同じ順序で値が登場していれば、機能的に等価です

**例:**
```xml
<!-- 変換前（階層構造） -->
<Item Num="1">
  <ItemTitle>（１）</ItemTitle>
  <ItemSentence>
    <Sentence Num="1">項目A</Sentence>
  </ItemSentence>
  <Subitem1 Num="1">
    <Subitem1Title>ア</Subitem1Title>
    <Subitem1Sentence>
      <Sentence Num="1">項目B</Sentence>
    </Subitem1Sentence>
  </Subitem1>
</Item>
```

```xml
<!-- 変換後（順序が保持される） -->
<List>
  <ListSentence>
    <Column Num="1">
      <Sentence Num="1">（１）</Sentence>
    </Column>
    <Column Num="2">
      <Sentence Num="1">項目A</Sentence>
    </Column>
  </ListSentence>
</List>
<List>
  <ListSentence>
    <Column Num="1">
      <Sentence Num="1">ア</Sentence>
    </Column>
    <Column Num="2">
      <Sentence Num="1">項目B</Sentence>
    </Column>
  </ListSentence>
</List>
```

---

## 特殊なケースの処理

### 統合されたList要素の扱い

**状況**: 元の変換処理では、ColumnありListから変換されたItem要素の後に続くColumnなしListは、そのItem要素の子要素として取り込まれます。

**逆変換時の扱い**:
- 統合情報（元々独立したList要素だったのか、Item要素の一部だったのか）が失われても問題ありません
- 重要なのは、**上から登場する順序が正しいこと**です
- Item要素とその子要素のList要素を順番に処理することで、元の順序を保持します
- 元の構造と完全一致しない場合がありますが、順序が正しければ機能的に等価です

**例:**
```xml
<!-- 変換前（元のList要素） -->
<Paragraph>
  <List>
    <ListSentence>
      <Column Num="1">
        <Sentence Num="1">（１）</Sentence>
      </Column>
      <Column Num="2">
        <Sentence Num="1">項目A</Sentence>
      </Column>
    </ListSentence>
  </List>
  <List>
    <ListSentence>
      <Sentence Num="1">追加の説明文</Sentence>
    </ListSentence>
  </List>
</Paragraph>
```

```xml
<!-- 変換後（Item要素） -->
<Paragraph>
  <Item Num="1">
    <ItemTitle>（１）</ItemTitle>
    <ItemSentence>
      <Sentence Num="1">項目A</Sentence>
    </ItemSentence>
    <List>
      <ListSentence>
        <Sentence Num="1">追加の説明文</Sentence>
      </ListSentence>
    </List>
  </Item>
</Paragraph>
```

```xml
<!-- 逆変換後（順序が保持される） -->
<Paragraph>
  <List>
    <ListSentence>
      <Column Num="1">
        <Sentence Num="1">（１）</Sentence>
      </Column>
      <Column Num="2">
        <Sentence Num="1">項目A</Sentence>
      </Column>
    </ListSentence>
  </List>
  <List>
    <ListSentence>
      <Sentence Num="1">追加の説明文</Sentence>
    </ListSentence>
  </List>
</Paragraph>
```

### 特殊な構造の扱い（TableStructなど）

**状況**: `TableStruct`などの特殊な構造は、変換対象外の要素です。

**逆変換時の扱い**:
- `TableStruct`などの特殊な構造は、**そのまま残します**
- これらは変換対象外の要素であり、逆変換処理ではスルーされます
- 重要なのは、**XMLファイル上で登場する値の順番が変わっていないこと**です
- 特殊な構造の前後で、List要素が正しい順序で登場していれば、機能的に等価です
- XMLファイルを順番に読み込んで処理することで、登場する値の順序は保持されます

**例:**
```xml
<!-- 変換前（階層構造） -->
<Subitem1 Num="1">
  <Subitem1Title>ア</Subitem1Title>
  <Subitem1Sentence>
    <Sentence Num="1">項目B</Sentence>
  </Subitem1Sentence>
  <TableStruct>
    <!-- テーブル構造 -->
  </TableStruct>
  <Subitem2 Num="1">
    <Subitem2Title>（ア）</Subitem2Title>
    <Subitem2Sentence>
      <Sentence Num="1">項目C</Sentence>
    </Subitem2Sentence>
  </Subitem2>
</Subitem1>
```

```xml
<!-- 逆変換後（TableStructはそのまま残る） -->
<List>
  <ListSentence>
    <Column Num="1">
      <Sentence Num="1">ア</Sentence>
    </Column>
    <Column Num="2">
      <Sentence Num="1">項目B</Sentence>
    </Column>
  </ListSentence>
</List>
<TableStruct>
  <!-- テーブル構造 -->
</TableStruct>
<List>
  <ListSentence>
    <Column Num="1">
      <Sentence Num="1">（ア）</Sentence>
    </Column>
    <Column Num="2">
      <Sentence Num="1">項目C</Sentence>
    </Column>
  </ListSentence>
</List>
```

---

## 使用方法

### 個別スクリプト実行

```bash
# Item逆変換
python3 reverse_convert_item.py input.xml output.xml

# Subitem1逆変換
python3 reverse_convert_subitem1.py input.xml output.xml

# Subitem2逆変換
python3 reverse_convert_subitem2.py input.xml output.xml

# Subitem10逆変換
python3 reverse_convert_subitem10.py input.xml output.xml
```

### パイプライン実行（全階層逆変換）

```bash
# 連続実行
./run_reverse_pipeline.sh input_folder output_folder

# ステップ実行（各ステップで確認）
./run_reverse_pipeline.sh input_folder output_folder step
```

---

## 注意事項

### 基本的な注意事項

- 逆変換スクリプトは正変換スクリプト（`../`）とは別のフォルダに配置されています
- 既存のList要素は変更されません
- XML構造の完全性を保ちつつ逆変換を行います

### 逆変換の限界

逆変換は完全な復元を保証するものではありません。以下の情報は失われる可能性があります：

1. **階層構造の情報**: どの要素がどの階層に属していたかという情報は失われます
2. **統合情報**: 元々独立したList要素だったのか、Item要素の一部だったのかという情報は失われます
3. **特殊な構造の位置情報**: `TableStruct`などの特殊な構造が元のList要素の並び順にどのように影響していたかという情報は失われます

**ただし、これらの情報が失われても問題ありません。重要なのは、XMLファイル上で登場する値の順番が変わっていないことです。**

### 検証

逆変換後のXMLファイルは、以下の観点で検証することを推奨します：

- XMLファイル上の値の順序が元のファイルと同じであること
- すべてのList要素が正しく変換されていること
- 特殊な構造が適切に保持されていること

#### 順序検証スクリプト

逆変換後にXMLファイル上で登場する値の順番が変わっていないことを検証するスクリプトが用意されています。

**使用方法:**

```bash
# 基本的な使用方法
python3 scripts/reverse/verify_reverse_order.py <元のXMLファイル> <逆変換後のXMLファイル>

# レポートファイルを指定する場合
python3 scripts/reverse/verify_reverse_order.py input.xml output.xml --report order_report.txt
```

**実行例:**

```bash
# 逆変換を実行
cd scripts/reverse
./run_reverse_pipeline.sh ../input ../output

# 順序を検証
python3 verify_reverse_order.py ../input/original.xml ../output/original-final.xml
```

**出力:**

スクリプトは以下の情報を表示・保存します：

- テキストの統計情報（元のファイルと逆変換後のファイルのテキスト数）
- 順序が保持されているかどうかの検証結果
- 順序の不一致が検出された場合、その詳細情報（最初の10件）

**検証結果の例:**

```
================================================================================
逆変換順序検証レポート
================================================================================

統計情報:
--------------------------------------------------------------------------------
元のファイルのテキスト数: 150
逆変換後のテキスト数: 150

検証結果:
--------------------------------------------------------------------------------
✅ 成功: XMLファイル上で登場する値の順番は保持されています。
```

順序の不一致が検出された場合：

```
検証結果:
--------------------------------------------------------------------------------
❌ 失敗: XMLファイル上で登場する値の順番に変更が検出されました。

詳細:
--------------------------------------------------------------------------------
⚠️  テキストの数が異なります:
   元のファイル: 150個
   逆変換後: 148個

❌ 順序の不一致が 2 箇所で検出されました:
--------------------------------------------------------------------------------

位置 45:
  元のファイル: [ItemTitle] （１）
  逆変換後:     [ListSentence] 項目A
```

**既存の検証スクリプト:**

プロジェクトには以下の検証スクリプトも用意されています：

- `scripts/compare_xml_files.py` - XMLファイルの構造と内容を詳細に比較
- `scripts/compare_xml_text_content.py` - テキスト内容の欠落を検証（順序は検証しない）

---

## テストケース

仕様に基づいた単体テストケースが用意されています。

### テストケースの場所

`scripts/reverse/test_data/unit_tests/` ディレクトリに、以下のテストケースが含まれています：

1. **01_case1_title_with_content** - タイトル要素がある場合（2カラムList）
2. **02_case2_title_empty** - タイトル要素がない場合（ColumnなしList）
3. **03_case3_title_with_multiple_columns** - ItemTitleがあり、ItemSentenceに複数のColumn要素がある場合
4. **04_case4_empty_title_with_multiple_columns** - ItemTitleが空で、ItemSentenceに複数のColumn要素がある場合
5. **05_hierarchical_structure** - 階層構造の処理順序
6. **06_integrated_list_elements** - 統合されたList要素の扱い
7. **07_special_structures** - 特殊な構造（TableStructなど）の扱い

### テストの実行方法

```bash
cd scripts/reverse/test_data/unit_tests
python3 run_tests.py
```

各テストケースは、`input.xml`（逆変換前）と`expected.xml`（期待される出力）を含んでいます。テスト実行後、`output.xml`が生成され、期待値と比較されます。

詳細は `scripts/reverse/test_data/unit_tests/README.md` を参照してください。

---

## 参考資料

- [逆変換が困難なケースの分析](../../docs/reverse_conversion_difficulties.md) - 逆変換時の困難なケースと解決策の詳細
- [処理ロジック.md](../../docs/処理ロジック.md) - 正変換の処理ロジック
- [education_markup_policy.md](../../docs/education_markup_policy.md) - 教育XMLのマークアップポリシー
