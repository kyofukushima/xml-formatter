# 逆変換スクリプト 単体テスト

このディレクトリには、`scripts/reverse/README.md`に記載されている仕様に基づいたテストケースが含まれています。

## テストケース一覧

### 01_case1_title_with_content
**仕様**: ケース1 - タイトル要素がある場合（2カラムList）

- **条件**: タイトル要素が存在し、かつ空でない場合
- **期待結果**: 2カラムのList要素に変換（Column1: タイトル、Column2: 本文）

### 02_case2_title_empty
**仕様**: ケース2 - タイトル要素がない場合（ColumnなしList）

- **条件**: タイトル要素が空または存在しない場合
- **期待結果**: ColumnのないList要素に変換

### 03_case3_title_with_multiple_columns
**仕様**: ケース3 - ItemTitleがあり、ItemSentenceに複数のColumn要素がある場合

- **条件**: ItemTitleが存在し、かつ空でない、かつItemSentence内に複数のColumn要素が存在する
- **期待結果**: 複数カラムのList要素に変換（ItemTitleを最初のColumnとして追加）

### 04_case4_empty_title_with_multiple_columns
**仕様**: ケース4 - ItemTitleが空で、ItemSentenceに複数のColumn要素がある場合

- **条件**: ItemTitleが空または存在しない、かつItemSentence内に複数のColumn要素が存在する
- **期待結果**: 複数カラムのList要素に変換（ItemSentence内のすべてのColumn要素をそのまま使用）

### 05_hierarchical_structure
**仕様**: 階層構造の処理順序

- **条件**: 深い階層構造（Item → Subitem1 → Subitem2 → Subitem3）
- **期待結果**: 内側から外側へ順番に処理され、XMLファイル上で登場する値の順番が保持される

### 06_integrated_list_elements
**仕様**: 統合されたList要素の扱い

- **条件**: Item要素の子要素としてList要素が含まれている
- **期待結果**: Item要素とその子要素のList要素を順番に処理することで、元の順序を保持

### 07_special_structures
**仕様**: 特殊な構造（TableStructなど）の扱い

- **条件**: TableStructなどの特殊な構造が階層構造内に含まれている
- **期待結果**: 特殊な構造はそのまま残され、前後でList要素が正しい順序で登場する

### 08_case5_title_with_multiple_sentences
**仕様**: ケース5 - ItemTitleがあり、ItemSentenceに複数のSentence要素がある場合

- **条件**: ItemTitleが存在し、かつ空でない、かつItemSentence内に複数のSentence要素が存在する
- **期待結果**: 
  - 最初のSentence要素はタイトルと一緒に2カラムのList要素に変換
  - 2つ目以降のSentence要素はそれぞれ別々のList要素（Columnなし）に変換

### 09_case6_empty_title_with_multiple_sentences
**仕様**: ケース6 - ItemTitleが空で、ItemSentenceに複数のSentence要素がある場合

- **条件**: ItemTitleが空または存在しない、かつItemSentence内に複数のSentence要素が存在する
- **期待結果**: それぞれのSentence要素を別々のList要素（Columnなし）に変換

## テストの実行方法

```bash
cd scripts/reverse/test_data/unit_tests
python3 run_tests.py
```

## テストケースの構造

各テストケースは以下の構造を持ちます：

```
<test_case_name>/
  ├── input.xml      # 逆変換前のXMLファイル（階層構造）
  ├── expected.xml   # 期待される出力XMLファイル（List要素の並び）
  └── output.xml     # 実際の出力XMLファイル（テスト実行後に生成）
```

## 検証方法

テストスクリプトは以下の検証を行います：

1. 逆変換パイプラインを実行
2. 出力XMLファイルを期待値と比較
3. XMLを正規化して構造的な一致を確認

## 順序検証

各テストケースの順序検証は、`verify_reverse_order.py`スクリプトを使用して行うことができます：

```bash
python3 ../../verify_reverse_order.py <test_case>/input.xml <test_case>/output.xml
```
