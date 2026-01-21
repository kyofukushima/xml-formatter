# 45_single_column_multiple_sentences

## テストの目的

正変換スクリプトにおいて、Columnが1つでその中に複数のSentenceがある場合に、変換後もすべてのSentenceが保持されることを確認する。

## 問題の説明

以前の実装では、`create_element_from_list`関数において、Columnが1つしかない場合の処理が不足していたため、Column内に複数のSentenceがある場合、2つ目以降のSentenceが欠落してしまう問題があった。

### 問題が発生するケース

**Columnが1つで最初がテキスト（ラベルではない）の場合**
- `create_element_from_list`関数にColumn数が1つの場合の処理が存在しない
- 結果として、空のItem要素が作成されるか、最初のSentenceのみが保持される
- **結果**: 2つ目以降のSentenceが欠落する ❌

## テストケース: Columnが1つで複数のSentenceがある場合

### 入力XML

- ColumnなしList: 1つ（最初のItemに変換）
- Column Num="1": 2つのSentence（テキスト、ラベルではない）
- ColumnなしList: 1つ（2つ目のItemに取り込まれる）

### 期待される動作

1. 最初のColumnなしListがItem Num="1"に変換される
2. Columnが1つで複数のSentenceがあるListがItem Num="2"に変換される
   - ItemTitleは空
   - ItemSentence内にColumn Num="1"要素が作成される
   - Column内の2つのSentenceが両方とも保持される
3. 3つ目のColumnなしListがItem Num="2"に取り込まれる（List要素として）

### 検証項目

1. Column Num="1"内の2つのSentenceが両方とも出力XMLに存在する ✅
2. SentenceのNum属性が正しく設定される（Num="1"とNum="2"） ✅
3. Column要素がItemSentence内に正しく配置される ✅
4. 後続のColumnなしListが正しく取り込まれる ✅

## 修正内容

1. `create_element_with_single_column`関数を新規作成
   - Columnが1つでその中に複数のSentenceがある場合に対応

2. `create_element_from_list`関数にColumn数が1つの場合の処理を追加
   - Columnが1つで最初のColumnがラベルではない場合の条件分岐を追加

3. `create_element_with_title_and_sentence`関数でColumnが1つの場合の処理を修正
   - Columnが1つの場合、そのColumn内のすべてのSentence要素を処理するように修正

## 関連する問題

- テストケース44 (`44_column_with_multiple_sentences`) では、Columnが2つ以上の場合をテストしている
- 本テストケースは、Columnが1つの場合をテストする補完的なテストケース