# 36_no_column_list_after_column_list_separate_sentences

## テスト内容

ColumnありListで最初のColumnがテキスト（ラベルではない）の場合、後続のList要素（Columnあり/なしに関わらず）を全て取り込む処理をテストします。

## 期待される動作

- ParagraphSentence直後のColumnありList（3カラム、最初のColumnが「ＪＡＳあとで消す」というテキスト）がItem要素に変換される
- ItemTitleは空になる
- 1つ目、2つ目、3つ目のColumnがItemSentenceのSentence要素として追加される
- その後のColumnなしListは、**List要素のままItem内に取り込まれる**（結合されない）
- 各ColumnなしListが独立したList要素として保持される

## 検証ポイント

- ColumnありListで最初のColumnがテキスト（ラベルではない）の場合、後続のList要素を全て取り込むこと
- Columnあり/なしに関わらず、後続のList要素が全て取り込まれること
- 各List要素が独立して保持されること

## 修正内容

`text_first_column`タイプ（ColumnありListで最初のColumnがテキスト）の場合、後続のList要素（Columnあり/なしに関わらず）を全て取り込むように修正しました。

### 修正前の動作

- ColumnありListから変換されたItemの後にColumnなしListが来た場合、Sentence要素に結合されていた

### 修正後の動作

- `text_first_column`タイプの場合、後続のList要素（Columnあり/なしに関わらず）を全てList要素のまま取り込む

