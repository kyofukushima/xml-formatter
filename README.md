# XML パイプライン処理ガイド

## 概要

`scripts/run_pipeline.sh` は、入力フォルダ内の全XMLファイルを順次変換し、出力フォルダに最終結果と検証レポートを保存するパイプラインスクリプトです。構造変換に加え、XML構文チェックとテキスト内容の整合性検証を自動で行います。

---

## セットアップ

### 必要な環境
- Python 3.7 以上
- lxml ライブラリ（各変換スクリプトで使用）

### 事前準備

```bash
pip install lxml
chmod +x scripts/run_pipeline.sh
mkdir -p input output
```

---

## 使い方

### コマンド

```bash
./scripts/run_pipeline.sh <input_folder> <output_folder> [mode]
```

- `<input_folder>`: 処理対象のXMLを置くフォルダ（配下の `*.xml` をすべて処理）
- `<output_folder>`: 最終出力とレポートの保存先
- `[mode]`: `all`（デフォルト・連続実行） / `step`（各ステップ後に一時停止）

#### 例

```bash
# 連続実行
./scripts/run_pipeline.sh ./input ./output

# ステップごとに確認しながら
./scripts/run_pipeline.sh ./input ./output step
```

---

## 処理フロー（実行順）

パイプラインは以下の順序で変換を行います。

| 順序 | スクリプト | 主な処理内容 |
|---|---|---|
| 1 | `preprocess_non_first_sentence_to_list.py` | 2個目以降のSentenceをListに変換 |
| 2 | `convert_article_focused.py` | Article 要素の分割と調整 |
| 3 | `convert_paragraph_step3.py` | Paragraph 処理（step3） |
| 4 | `convert_paragraph_step4.py` | Paragraph 処理（step4） |
| 5 | `convert_item_step0.py` | Item 変換 |
| 6 | `convert_subitem1_step0.py` | Subitem1 変換 |
| 7 | `convert_subitem2_step0.py` | Subitem2 変換 |
| 8 | `convert_subitem3_step0.py` | Subitem3 変換 |
| 9 | `convert_subitem4_step0.py` | Subitem4 変換 |
| 10 | `convert_subitem5_step0.py` | Subitem5 変換 |
| 11 | `convert_subitem6_step0.py` | Subitem6 変換 |
| 12 | `convert_subitem7_step0.py` | Subitem7 変換 |
| 13 | `convert_subitem8_step0.py` | Subitem8 変換 |
| 14 | `convert_subitem9_step0.py` | Subitem9 変換 |
| 15 | `convert_subitem10_step0.py` | Subitem10 変換（最終） |

### 検証
- **構文検証**: `validate_xml.py` が最初に実行され、結果は `intermediate_files/<元ファイル名>/...-parse_validation.txt` に保存されます。
- **テキスト内容検証**: パイプライン完了後に `compare_xml_text_content.py` を実行し、元XMLとのテキスト一致を確認します（レポート: `...-validation_report.txt`）。

---

## 出力とファイル配置

```
output/
├── <入力名>-final.xml                 # 最終出力
└── intermediate_files/
    └── <入力名>/
        ├── <入力名>-<各ステップ>.xml        # 中間XML
        ├── <入力名>-parse_validation.txt    # 構文検証レポート
        └── <入力名>-validation_report.txt   # テキスト検証レポート
```

- 最終ファイルは常に `<入力名>-final.xml` として `<output_folder>` にコピーされます。
- 中間ファイルと検証レポートは出力フォルダ配下の `intermediate_files/` にまとめて保存されます。

---

## 開発・運用・保守

このプロジェクトの開発フローやコントリビューション方法については、[CONTRIBUTING.md](./CONTRIBUTING.md)を参照してください。

### 主な開発フロー

1. **機能ブランチを作成**: `git checkout -b feature/機能名`
2. **変更をコミット**: 適切なコミットメッセージでコミット
3. **プルリクエストを作成**: GitHubでPRを作成してレビュー依頼
4. **マージ**: レビュー承認後、mainブランチにマージ

詳細は[CONTRIBUTING.md](./CONTRIBUTING.md)を参照してください。

---

## トラブルシューティング

- `入力フォルダにXMLファイルが見つかりません`: `<input_folder>` 直下に `*.xml` があるか確認してください。
- `スクリプトが見つかりません`: `scripts/` 配下に全変換スクリプトがあるか確認してください。
- テキスト検証で `要確認` が出る: `intermediate_files/<入力名>/<入力名>-validation_report.txt` を確認し、欠落や差分をレビューしてください。

---

**最終更新**: 2025年12月
