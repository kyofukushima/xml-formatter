# テストケース30: ドット区切り数字とアルファベットラベルの階層関係

## テスト内容

`ParagraphNum`に`４．１`のようなドット区切り数字がある場合、最初の`List`（ラベルなし、2つのColumn）が`Item`に変換され、その後の`ａ）`, `ｂ）`, `ｃ）`, `ｄ）`のようなアルファベットラベルの`List`要素が、変換せずに`List`のまま、その`Item`の直接の子要素として取り込まれることをテストします。

## 入力構造

```
Paragraph(ParagraphNum: ４．１)
├─ List(Column2つ、ラベルなし) → Itemに変換（ItemTitleは空）
├─ List(ａ）) → Itemの子要素として取り込む（Listのまま）
├─ List(ｂ）) → Itemの子要素として取り込む（Listのまま）
├─ List(ｃ）) → Itemの子要素として取り込む（Listのまま）
└─ List(ｄ）) → Itemの子要素として取り込む（Listのまま）
```

## 期待される出力

1. 最初の`List`（ラベルなし、2つのColumn）は`Item`に変換され、`ItemTitle`は空、`ItemSentence`に2つの`Sentence`要素が設定される
2. `ａ）`, `ｂ）`, `ｃ）`, `ｄ）`の`List`要素は、変換せずに`List`のまま、その`Item`の直接の子要素として配置される

## 修正方針

`convert_item_step0.py`の`process_elements_recursive`関数で、`NORMAL_PROCESSING`モードにおいて：

1. `ParagraphNum`にドット区切り数字がある場合、最初の`List`（ラベルなし、2つのColumn）は`Item`に変換され、`ItemTitle`は空になる
2. その後のアルファベットラベル（`ａ）`, `ｂ）`, `ｃ）`, `ｄ）`など）を持つ`List`要素を処理する際：
   - `are_same_hierarchy`が`True`を返す場合でも、`last_child`の`ItemTitle`が空で、新しいラベルがアルファベットラベルの場合は、子要素として取り込む
   - `are_same_hierarchy`が`False`を返す場合、`last_child`の`ItemTitle`が空で、新しいラベルがアルファベットラベルの場合も、子要素として取り込む












