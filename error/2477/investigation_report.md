# TableStruct順序変更問題の詳細調査報告

## 問題の概要

処理前後のXMLファイルを比較すると、TableStructの順序が変更されているにも関わらず、検証スクリプトが「Table order is correct」と報告している。

## 調査対象ファイル

- **処理前**: `error/2477/H13null[2490]1347_R07null[2490]248_R070730_1test_split2.xml`
- **処理後**: `error/2477/H13null[2490]1347_R07null[2490]248_R070730_1test_split2_final.xml`

## 問題箇所の特定

### 処理前の構造（Paragraph要素内）

```
Paragraph Num="1"
  [49] List: ロ - 評価事項
  [50] List: ①
  [51] List: ②
  [52] TableStruct: ['（い）', '（ろ）']  ← 表1
  [53] List: ③
  [54] TableStruct: ['（い）', '（ろ）']  ← 表2
  [55] List: （３）
  [57] List: イ
```

### 処理後の構造（Subitem2要素内）

```
Subitem2 Num="2" (（２）)
  [0] Subitem2Title: （２）
  [1] Subitem2Sentence: ...
  [2] Subitem3: イ
  [3] Subitem3: ロ  ← 「ロ」のSubitem3要素
    - Subitem3Title: ロ
    - Subitem3Sentence: 評価事項
    - Subitem4要素なし
    - TableStruct要素なし  ← 問題：TableStructが存在しない
```

## 問題1：検証スクリプトが検知できなかった理由

### 検証スクリプトの動作

1. **`get_table_sequence`関数の動作**:
   - TableStructを文書順序で取得
   - 各TableStructの最初の10個のテキストを結合した文字列で識別
   - 処理前後で同じ順序で出現するかチェック

2. **検証スクリプトの限界**:
   - 同じ内容のTableStructが複数ある場合、順序が変わっても検知できない
   - 処理前後で、同じ内容のTableStructが同じ順序で出現しているため、「Table order is correct」と表示

### 実際の動作

- 処理前：101個のTableStruct
- 処理後：101個のTableStruct
- 検証結果：「Table order is correct」

しかし、実際には：
- 処理前：Paragraph要素内に「ロ」のList要素の後にTableStructが2つ存在
- 処理後：Subitem2要素内に「ロ」のSubitem3要素は存在するが、TableStructが存在しない

## 問題2：この問題が発生した理由

### Subitem3変換の処理フロー

1. **`process_elements_recursive`関数の動作**:
   - `parent_sentence.itersiblings()`を使用して、親要素（Subitem2）のSentenceの次の要素から処理を開始
   - List要素をSubitem3要素に変換
   - TableStructは`STRUCT_ELEMENT_TAGS`として処理され、`state.append_child(child)`で親要素（Subitem2）の直接の子要素として追加される

2. **実際の処理結果**:
   - Subitem3変換の段階で、List要素（「ロ」「①」「②」「③」）がSubitem3要素に変換された
   - しかし、TableStructはSubitem2要素の直接の子要素として追加されていない
   - 処理後のSubitem2要素内には、Subitem3要素（イ、ロ）しか存在しない

### 原因の仮説

1. **Subitem3変換の段階で、TableStructが処理されていない可能性**:
   - `process_elements_recursive`関数は、`parent_sentence.itersiblings()`を使用して、親要素のSentenceの次の要素から処理を開始
   - しかし、Subitem3変換の段階では、Subitem2要素内のList要素をSubitem3要素に変換するため、TableStructは処理されない可能性がある

2. **TableStructが別の場所に移動した可能性**:
   - 処理後のファイル全体を見ると、TableStructはすべてParagraph要素の子要素として存在している
   - これは、Subitem3変換の段階で、TableStructが処理されていないことを示している

## 確認が必要な点

1. **Subitem3変換の段階で、TableStructがどのように処理されるか**:
   - `process_elements_recursive`関数が、Subitem2要素内のTableStructをどのように処理するか
   - TableStructがSubitem2要素の直接の子要素として追加されるか

2. **Subitem4変換の段階で、TableStructがどのように処理されるか**:
   - Subitem4変換の段階で、TableStructがSubitem4の子要素として処理されるか
   - TableStructの順序が保持されるか

3. **検証スクリプトの改善**:
   - TableStructの識別方法を改善（位置情報を含める、またはより詳細な比較を行う）
   - 同じ内容のTableStructが複数ある場合でも、順序の違いを検知できるようにする

## 推奨される対応

1. **検証スクリプトの改善**:
   - TableStructの識別方法を改善（位置情報を含める、またはより詳細な比較を行う）
   - 同じ内容のTableStructが複数ある場合でも、順序の違いを検知できるようにする

2. **処理ロジックの確認**:
   - Subitem3変換の段階で、TableStructがSubitem2要素の直接の子要素として正しく処理されるか確認
   - Subitem4変換の段階で、TableStructの順序が保持されるか確認

3. **単体テストの追加**:
   - Subitem3変換の段階で、TableStructの順序が保持されることを確認する単体テストを追加
   - Subitem4変換の段階で、TableStructの順序が保持されることを確認する単体テストを追加
