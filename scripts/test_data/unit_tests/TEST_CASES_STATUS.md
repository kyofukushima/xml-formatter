# テストケース整備状況

最終更新日: 2026年7月30日

## 概要

このドキュメントは、`convert_item_step0`および`convert_subitem1_step0`から`convert_subitem10_step0`までのテストケースの整備状況をまとめたものです。

## テストケース数一覧（2026-07-30 実測）

| テストディレクトリ | テストケース数 | 状態 |
|-------------------|--------------|------|
| `convert_item_step0` | 46 | ✅ 全テスト成功 |
| `convert_subitem1_step0` | 36 | ✅ 全テスト成功 |
| `convert_subitem2_step0` | 28 | ✅ 全テスト成功 |
| `convert_subitem3_step0` | 21 | ✅ 全テスト成功 |
| `convert_subitem4_step0` | 19 | ✅ 全テスト成功 |
| `convert_subitem5_step0` | 19 | ✅ 全テスト成功 |
| `convert_subitem6_step0` | 19 | ✅ 全テスト成功 |
| `convert_subitem7_step0` | 19 | ✅ 全テスト成功 |
| `convert_subitem8_step0` | 19 | ✅ 全テスト成功 |
| `convert_subitem9_step0` | 19 | ✅ 全テスト成功 |
| `convert_subitem10_step0` | 19 | ✅ 全テスト成功 |

## テストケース追加履歴

### テストケース27, 28, 29の追加

以下のテストケースが`convert_item_step0`から`convert_subitem10_step0`まで追加されました：

- **27_column_list_three_or_more_with_label**: 3列以上のColumnありListでラベルが含まれる場合のテスト
- **28_duplicate_label_keep_as_list**: 重複ラベルの場合、List要素のまま保持するテスト
- **29_instruction_bracket_duplicate**: 括弧付き指導項目が重複する場合のテスト

これらのテストケースは、新しい分割ルール（ラベルタイプが同じで値が既に出現した場合はappend、異なる場合はsplit）を検証するために追加されました。

## 現在の問題点

なし（2026-07-30時点で全スイート成功）。

## 修正済みの問題（2026-07-30）

### Column保持化に伴う期待値の更新（全Subitemレベル）

コミット e2793f4 以降、コンバータは「ColumnありList（1つ目が非ラベル、または3列以上）」を変換する際、
Columnの中身をSentence要素に展開せず、**Column要素ごとSentenceコンテナ内に保持**する仕様に変わりました
（逆変換でのラウンドトリップのための構造保持）。
Itemスイートの期待値はこの仕様に更新済みでしたが（例: コミット b4527b9「outputを正として反映」）、
Subitemスイートの以下の期待値は旧仕様（Sentence展開）のまま残っており失敗していました：

- `18_process1_branch1_column_list_3columns`（subitem1・2）／ `05_process1_branch1_column_list_3columns`（subitem3〜6）
- `26_column_list_non_label_first_column`（subitem1〜10）
- `27_column_list_three_or_more_with_label`（subitem1〜10）
- `30_dot_separated_number_with_alphabet_children`（subitem1・2）

**対応**: 現仕様（Column保持）を正とする方針決定を受け、テキスト保全とColumn保持形式を検証のうえ、
28件の期待値を出力で更新（2026-07-30）。

### テストデータ不備の修正（グループ2・3）

以下の失敗はテストデータ自体の不備であり、修正済みです：

1. **期待値のラッパー要素名誤り**（`19_round_bracket_long_description`・`20_empty_parent_create_item`、subitem3〜10）
   - 期待値が親レベル要素（例: Subitem2）を子レベル名（Subitem3）で記載していた
   - → 出力（テキスト保全・構造を検証済み）を正として期待値を更新
2. **入力データの階層不足**（`01〜04`・`20_skip_empty_parent`、subitem7〜10）
   - 入力の入れ子が Subitem5 で止まり、変換対象のListが正しい親（Subitem{N-1}）の下になかった
   - → 欠落していた中間レベルを挿入して入力を修正し、期待値を更新
3. **入力データの最深要素の誤命名**（`21`・`22`、subitem6〜10）
   - 最深要素が Subitem{N} と誤命名され、中間レベル（Subitem4〜）も欠落していた
   - → Subitem{N-1} に改名・中間レベルを挿入して入力を修正し、期待値を更新
4. **入力データのColumn誤入れ子**（`06_process2_split_and_aggregate`、subitem2）
   - ListSentence > Sentence > Column という不正な構造で、変換時にテキストが欠落していた
   - → ListSentence > Column の正しい構造に修正（欠落は解消、期待値どおりの出力を確認）

## テストケースの構造

### convert_item_step0
- **親タグ**: `Paragraph`
- **子タグ**: `Item`
- **テストケース数**: 31

### convert_subitem1_step0
- **親タグ**: `Item`
- **子タグ**: `Subitem1`
- **テストケース数**: 35
- **備考**: `convert_item_step0`より4つ多い（追加のテストケースあり）

### convert_subitem2_step0 ～ convert_subitem10_step0
- **親タグ**: `Subitem{N-1}`（例: `Subitem2_step0`の親タグは`Subitem1`）
- **子タグ**: `Subitem{N}`（例: `Subitem2_step0`の子タグは`Subitem2`）
- **テストケース数**: 18～26（レベルによって異なる）

## テスト実行方法

各テストディレクトリで以下のコマンドを実行：

```bash
cd scripts/test_data/unit_tests/convert_{item|subitem{N}}_step0
python run_tests.py
```

## 今後の対応

1. **テストケースの追加**
   - 必要に応じて、不足しているテストケースを追加

## 関連ファイル

- `scripts/xml_converter.py`: 共通の変換ロジック
- `scripts/convert_item_step0.py`: Item要素変換スクリプト
- `scripts/convert_subitem{N}_step0.py`: Subitem{N}要素変換スクリプト
- `scripts/test_data/unit_tests/convert_{item|subitem{N}}_step0/run_tests.py`: テスト実行スクリプト


