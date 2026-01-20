# 28_duplicate_label_keep_as_list

## テスト内容

同じラベルが連続して出現した場合、最初の出現は変換し、2回目以降の同じラベルは変換せずにListのまま、前回変換された要素の子要素として取り込むことをテストします。

## 期待される動作

- **最初の出現（a, b, c, d）**: それぞれItem要素に変換される
- **2回目の出現（a, b, c）**: 既に出現したラベルなので、変換せずにListのまま、最後に変換されたItem（d）の子要素として取り込まれる
- **新しいラベル（e, f）**: 新しいラベルなので、Item要素に変換され、dの弟要素として配置される

## 入力構造

```
Paragraph
  - List (a) → 変換
  - List (b) → 変換
  - List (c) → 変換
  - List (d) → 変換
  - List (a) → Listのままdの子要素
  - List (b) → Listのままdの子要素
  - List (c) → Listのままdの子要素
  - List (e) → 変換（dの弟要素）
  - List (f) → 変換（eの弟要素）
```

## 出力構造

```
Paragraph
  - Item (a)
  - Item (b)
  - Item (c)
  - Item (d)
    - List (a) ← 2回目の出現、Listのまま
    - List (b) ← 2回目の出現、Listのまま
    - List (c) ← 2回目の出現、Listのまま
  - Item (e) ← 新しいラベル
  - Item (f) ← 新しいラベル
```
