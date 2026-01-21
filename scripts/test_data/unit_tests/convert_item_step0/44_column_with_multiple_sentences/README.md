# Column内に複数のSentenceがある場合のテスト

## テストの目的

正変換スクリプトにおいて、Column内に複数のSentenceがある場合に、変換後もすべてのSentenceが保持されることを確認する。

## 問題の説明

`get_list_columns`関数や`get_all_list_columns`関数が`find('.//Sentence')`を使用して最初のSentence要素のみを取得しているため、Column内に複数のSentenceがある場合、2つ目以降が欠落してしまう。

### 問題が発生するケース

1. **Columnが2つで最初がラベルの場合** (`create_element_with_title_and_sentence`を使用)
   - `get_list_columns`が最初のSentenceのみを返す
   - `create_element_with_title_and_sentence`が最初のSentenceのみをコピー
   - **結果**: 2つ目以降のSentenceが欠落する ❌

2. **Columnが3つ以上で最初がラベルの場合** (`create_element_with_title_and_multiple_sentences`を使用)
   - `get_all_list_column_elements`がColumn要素全体を返す
   - `deepcopy(column)`でColumn全体をコピー
   - **結果**: すべてのSentenceが保持される ✅

## テストケース1: Columnが3つ以上の場合（問題なし）

### 入力XML

- Column Num="1": ラベル「一」
- Column Num="2": 1つのSentence
- Column Num="3": 2つのSentence（mainとproviso）

### 期待される動作

- Column Num="1"がItemTitleに変換される
- Column Num="2"とColumn Num="3"がItemSentence内のColumn要素として保持される
- Column Num="3"内の2つのSentenceが両方とも保持される

### 検証項目

1. Column Num="3"内の2つのSentenceが両方とも出力XMLに存在する
2. SentenceのFunction属性が保持される
3. SentenceのNum属性が正しく設定される

## テストケース2: Columnが2つで最初がラベルの場合（問題あり）

### 入力XML (`input_2columns.xml`)

- Column Num="1": ラベル「（１）」
- Column Num="2": 2つのSentence（mainとproviso）

### 期待される動作

- Column Num="1"がItemTitleに変換される
- Column Num="2"内の2つのSentenceがItemSentence内に保持される

### 実際の動作（問題）

- Column Num="1"がItemTitleに変換される ✅
- Column Num="2"内の最初のSentenceのみが保持される ❌
- Column Num="2"内の2つ目のSentenceが欠落する ❌

### 検証項目

1. Column Num="2"内の2つのSentenceが両方とも出力XMLに存在する（現在は失敗）
2. SentenceのFunction属性が保持される
3. SentenceのNum属性が正しく設定される
