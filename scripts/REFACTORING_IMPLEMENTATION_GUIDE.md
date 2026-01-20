# リファクタリング実装ガイド

このガイドでは、`run_pipeline.sh` のリファクタリングを段階的に実施する手順を説明します。

## 前提条件

- 既存の `run_pipeline.sh` が正常に動作していること
- バックアップが取られていること
- テスト環境で実施できること

## 実装手順

### ステップ1: ディレクトリ構造の作成

```bash
cd /Users/fukushima/Documents/xml_anken/kouzou1_xml/scripts
mkdir -p lib
```

### ステップ2: 共通ライブラリの作成

1. `lib/pipeline_common.sh` を作成
   - `lib/pipeline_common.sh.example` を参考に実装
   - または、`lib/pipeline_common.sh.example` をコピーして `pipeline_common.sh` にリネーム

```bash
cp lib/pipeline_common.sh.example lib/pipeline_common.sh
chmod +x lib/pipeline_common.sh
```

### ステップ3: 既存スクリプトのバックアップ

```bash
cp run_pipeline.sh run_pipeline.sh.backup
cp run_reverse_pipeline.sh run_reverse_pipeline.sh.backup
```

### ステップ4: テスト用のリファクタリング版を作成

1. `run_pipeline.sh.refactored` を作成
   - `run_pipeline.sh.refactored.example` を参考に実装
   - または、サンプルをコピーして調整

```bash
cp run_pipeline.sh.refactored.example run_pipeline.sh.refactored
chmod +x run_pipeline.sh.refactored
```

### ステップ5: 動作確認

1. テスト用の入力ファイルで実行

```bash
# テスト実行
./run_pipeline.sh.refactored ./test_input ./test_output all

# 既存版と比較
./run_pipeline.sh ./test_input ./test_output_existing all

# 出力を比較
diff -r ./test_output ./test_output_existing
```

2. 各機能を個別にテスト
   - パース検証が正常に動作するか
   - 変換スクリプトが正常に実行されるか
   - 検証レポートが正常に生成されるか
   - エラーハンドリングが適切か

### ステップ6: 既存スクリプトの置き換え

動作確認が完了したら、既存スクリプトを置き換えます。

```bash
# リファクタリング版を本番版に置き換え
mv run_pipeline.sh.refactored run_pipeline.sh

# 必要に応じて、run_reverse_pipeline.sh も同様にリファクタリング
```

### ステップ7: 逆変換スクリプトのリファクタリング

`run_reverse_pipeline.sh` も同様の手順でリファクタリングします。

1. `run_reverse_pipeline.sh.refactored` を作成
2. 共通ライブラリを使用するように修正
3. テスト実行
4. 置き換え

## 検証項目

### 機能テスト

- [ ] 引数チェックが正常に動作する
- [ ] 入力フォルダの検証が正常に動作する
- [ ] XMLファイルの検証が正常に動作する
- [ ] パース検証が正常に実行される
- [ ] 変換スクリプトが順番に実行される
- [ ] 検証レポートが正常に生成される
- [ ] エラーハンドリングが適切に動作する
- [ ] step モードが正常に動作する

### パフォーマンステスト

- [ ] 処理時間が既存版と同等または改善されている
- [ ] メモリ使用量が適切である

### 互換性テスト

- [ ] 既存のワークフローと互換性がある
- [ ] 既存の設定ファイルがそのまま使用できる

## トラブルシューティング

### 問題1: 共通ライブラリが読み込まれない

**原因**: パスの問題

**解決策**:
```bash
# スクリプトディレクトリの取得方法を確認
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
source "$SCRIPT_DIR/lib/pipeline_common.sh"
```

### 問題2: 関数が見つからない

**原因**: 共通ライブラリの読み込み順序の問題

**解決策**: `set -e` の前に `source` を実行するか、エラーハンドリングを追加

### 問題3: 配列の間接参照が動作しない

**原因**: Bash のバージョンや配列の扱いの問題

**解決策**: `run_pipeline` 関数の実装を確認し、必要に応じて修正

## ロールバック手順

問題が発生した場合、バックアップから復元します。

```bash
# バックアップから復元
cp run_pipeline.sh.backup run_pipeline.sh
chmod +x run_pipeline.sh

# 共通ライブラリを削除（必要に応じて）
rm -rf lib/
```

## 次のステップ

リファクタリングが完了したら、以下の改善を検討できます：

1. **設定の外部化**
   - 変換スクリプトリストを JSON/YAML ファイルに移動
   - 環境変数による設定の柔軟化

2. **ログ機能の強化**
   - 詳細なログファイルの生成
   - ログレベルの設定

3. **並列処理の追加**
   - 複数ファイルの並列処理
   - パフォーマンスの向上

4. **テストの自動化**
   - 単体テストの追加
   - 統合テストの追加

## 参考資料

- `ANALYSIS_PIPELINE_REFACTORING.md` - 詳細な分析レポート
- `lib/pipeline_common.sh.example` - 共通ライブラリのサンプル
- `run_pipeline.sh.refactored.example` - リファクタリング後のメインスクリプトのサンプル












