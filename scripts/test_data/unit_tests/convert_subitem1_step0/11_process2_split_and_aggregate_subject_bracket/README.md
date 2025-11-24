# 11_process2_split_and_aggregate_subject_bracket

## 概要
科目名パターンのItem要素に対して、異なる種類のList要素がすべてSubitem1要素に取り込まれることをテストするケース

## 入力
- 科目名パターンのItem要素（〔国語〕）
- ラベル付きList要素（（１））
- ColumnなしList要素
- 学年パターンList要素（〔第１学年及び第２学年〕）
- 指導項目List要素（〔指導項目〕）
- 学年パターンList要素（〔第１学年〕）

## 期待される動作
- 最初のラベル付きListがSubitem1に変換される
- 残りの異なる種類のList要素がすべて同じSubitem1に取り込まれる
- 科目名パターンのItemに対して異なる種類の要素は分割されない

## 仕様書の対応
処理2: Subitem1要素の弟要素を順次処理（取り込みまたは分割）

## 統計期待値
- ColumnありList → Subitem1: 1箇所
- ColumnなしList → Subitem1内List: 4箇所







