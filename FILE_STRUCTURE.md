# ファイル構成ガイド

## プロジェクト全体のディレクトリ構造

```
xml_pipeline_project/
│
├── 【メインスクリプト】
├── run_pipeline_fixed.sh           ★ 修正版パイプラインスクリプト（推奨）
├── run_pipeline.sh                 × 元のスクリプト（非推奨）
│
├── 【Python 変換スクリプト】
├── convert_article_focused.py      # Article 要素処理
├── convert_paragraph_step1.py      # Paragraph 分割 Step 1
├── convert_paragraph_step2.py      # Paragraph 分割 Step 2
├── convert_paragraph_step3.py      # Paragraph 処理 Step 3
├── convert_paragraph_step4.py      # Paragraph 処理 Step 4
├── convert_item_step0.py           # Item 変換 Step 0
├── convert_item_step1.py           # Item 修正 Step 1
├── convert_subject_item.py         # Subject Item 変換
├── convert_subitem1_step0.py       # Subitem1 変換 Step 0
├── convert_subitem1_step1.py       # Subitem1 修正 Step 1
├── convert_subitem2_step0.py       # Subitem2 変換 Step 0
├── convert_subitem2_step1.py       # Subitem2 修正 Step 1
│
├── 【セットアップスクリプト】
├── setup.sh                        # 初回環境セットアップ
│
├── 【ドキュメント】
├── README.md                       ★ 完全なドキュメント（最初に読むべき）
├── QUICKSTART.md                   ★ クイックスタート（5分で開始）
├── CHANGES.md                      # 修正内容の詳細説明
├── FILE_STRUCTURE.md               # このファイル
│
├── 【作業ディレクトリ】
├── input/                          ★ 入力XMLファイルを配置
│   ├── sample1.xml
│   ├── sample2.xml
│   └── sample3.xml
│
├── output/                         ★ 処理結果が出力されます
│   ├── sample1-final.xml
│   ├── sample2-final.xml
│   └── sample3-final.xml
│
└── .temp/                          # 一時ファイル（作成時に自動削除）
```

---

## 各ファイルの役割

### 【重要なスクリプト】

| ファイル | 説明 | 用途 |
|---------|------|------|
| `run_pipeline_fixed.sh` | 修正版パイプラインスクリプト | **これを使用してください** |
| `run_pipeline.sh` | 元のスクリプト | 参考用（非推奨） |
| `setup.sh` | 初回セットアップスクリプト | 初回実行時に1回実行 |

### 【Python 変換スクリプト】

| ステップ | ファイル | 処理内容 | 入力 | 出力 |
|---------|---------|---------|------|------|
| 1 | `convert_article_focused.py` | Article 要素の処理 | 生のXML | Article 処理済みXML |
| 2 | `convert_paragraph_step1.py` | Paragraph 分割1 | Article XML | Paragraph1 XML |
| 3 | `convert_paragraph_step2.py` | Paragraph 分割2 | Paragraph1 XML | Paragraph2 XML |
| 4 | `convert_paragraph_step3.py` | Paragraph 処理3 | Paragraph2 XML | Paragraph3 XML |
| 5 | `convert_paragraph_step4.py` | Paragraph 処理4 | Paragraph3 XML | Paragraph4 XML |
| 6 | `convert_item_step0.py` | Item 変換0 | Paragraph4 XML | Item0 XML |
| 7 | `convert_item_step1.py` | Item 修正1 | Item0 XML | Item1 XML |
| 8 | `convert_subject_item.py` | Subject Item 変換 | Item1 XML | SubjectItem XML |
| 9 | `convert_subitem1_step0.py` | Subitem1 変換0 | SubjectItem XML | Subitem10 XML |
| 10 | `convert_subitem1_step1.py` | Subitem1 修正1 | Subitem10 XML | Subitem11 XML |
| 11 | `convert_subitem2_step0.py` | Subitem2 変換0 | Subitem11 XML | Subitem20 XML |
| 12 | `convert_subitem2_step1.py` | Subitem2 修正1 | Subitem20 XML | Subitem21 XML |
| 13 | `convert_subitem3_step0.py` | Subitem3 変換0 | Subitem21 XML | Subitem30 XML |
| 14 | `convert_subitem3_step1.py` | Subitem3 修正1 | Subitem30 XML | Subitem31 XML |
| 15 | `convert_subitem4_step0.py` | Subitem4 変換0 | Subitem31 XML | Subitem40 XML |
| 16 | `convert_subitem4_step1.py` | Subitem4 修正1 | Subitem40 XML | Subitem41 XML |
| 17 | `convert_subitem5_step0.py` | Subitem5 変換0 | Subitem41 XML | Subitem50 XML |
| 18 | `convert_subitem5_step1.py` | Subitem5 修正1 | Subitem50 XML | **最終XML** |

### 【ドキュメント】

| ファイル | 対象者 | 内容 | 読むべき順 |
|---------|--------|------|-----------|
| `README.md` | すべてのユーザー | 完全ドキュメント、セットアップ方法、トラブルシューティング | **1番目** |
| `QUICKSTART.md` | 初心者 | 5分で始める手順、よくある質問、簡単な例 | **2番目** |
| `CHANGES.md` | 開発者、詳しい方 | 修正内容の技術的説明 | 3番目（オプション） |
| `FILE_STRUCTURE.md` | すべてのユーザー | このファイル。全体構成の説明 | 参考用 |

---

## クイック操作ガイド

### 初回セットアップ（1回だけ）

```bash
# 1. セットアップスクリプトを実行
chmod +x setup.sh
./setup.sh

# 2. セットアップが完了
# → input/、output/ フォルダが自動作成
# → lxml がインストール済み
```

### 通常の使用

```bash
# 1. XMLファイルを input/ フォルダに配置
cp your_file1.xml input/
cp your_file2.xml input/

# 2. パイプラインを実行
./run_pipeline_fixed.sh ./input ./output all

# 3. 結果を確認
ls -lh output/
cat output/your_file1-final.xml
```

### ステップバイステップ実行（確認しながら）

```bash
./run_pipeline_fixed.sh ./input ./output step
# → 各ステップで一時停止します
```

---

## ファイルサイズの目安

通常のXML処理の場合：

| ファイル | サイズの目安 |
|---------|-----------|
| 入力XML（小） | 100 KB - 1 MB |
| 入力XML（中） | 1 MB - 10 MB |
| 入力XML（大） | 10 MB - 100 MB |
| 出力XML | 入力とほぼ同じ |
| 中間ファイル（合計） | 処理中のみメモリ使用 |

---

## よくある質問

### Q: どのドキュメントを最初に読むべき？

**A:** 以下の順序を推奨します：
1. `README.md` - 全体概要
2. `QUICKSTART.md` - すぐに始めたい場合
3. `CHANGES.md` - 詳細を知りたい場合（オプション）

### Q: `run_pipeline_fixed.sh` と `run_pipeline.sh` の違いは？

**A:** 
- `run_pipeline_fixed.sh` **（新版・推奨）**
  - 入力フォルダ、出力フォルダを分離
  - 複数ファイルを一度に処理
  - 中間ファイルを自動削除
  - 初心者向き

- `run_pipeline.sh` **（旧版・参考用）**
  - 単一ファイルのみ処理
  - 中間ファイルが蓄積
  - 出力場所がわかりにくい

詳細は `CHANGES.md` を参照。

### Q: セットアップスクリプト（setup.sh）は必須？

**A:** 必須ではありませんが、推奨です。以下を自動処理します：
- lxml のインストール
- 必要なフォルダの作成
- 実行権限の設定

手動で設定することもできますが、`setup.sh` を使う方が簡単です。

### Q: Python スクリプトを直接実行できる？

**A:** はい、できます。ただし推奨しません。

```bash
# 可能だが、ステップ順序間違いのリスク
python3 convert_paragraph_step1.py input.xml output.xml

# 推奨: パイプラインスクリプトを使用
./run_pipeline_fixed.sh ./input ./output all
```

### Q: 出力ファイルの名前を変更できる？

**A:** はい。デフォルトは `{入力名}-final.xml` です。

修正版パイプラインスクリプト内の以下の行を編集：

```bash
output_filename="${filename_no_ext}-final.xml"
# ↓
output_filename="${filename_no_ext}-converted.xml"  # 例
```

---

## ディレクトリ作成の自動化

`setup.sh` スクリプトが以下を自動実行します：

```bash
# Python 環境確認
python3 --version

# lxml インストール
pip3 install lxml

# フォルダ作成
mkdir -p input output .temp

# 実行権限設定
chmod +x run_pipeline_fixed.sh setup.sh
```

---

## トラブルシューティング

### スクリプトが見つからないエラー

```bash
# 現在のディレクトリを確認
pwd

# ファイル一覧を確認
ls -la

# すべてのスクリプトが存在するか確認
ls -la *.py *.sh
```

### 権限エラー

```bash
# 実行権限を付与
chmod +x run_pipeline_fixed.sh setup.sh

# 確認
ls -la run_pipeline_fixed.sh
# → -rwxr-xr-x が表示されれば OK
```

### XMLファイルが見つからない

```bash
# input/ フォルダを確認
ls -la input/

# XMLファイルをコピー
cp your_file.xml input/

# 再度確認
ls -la input/*.xml
```

---

## セキュリティに関する注意

1. **入力ファイル**
   - 信頼できるソースからのみXMLを使用
   - XMLインジェクション対策は各Pythonスクリプトで実装

2. **出力ファイル**
   - `output/` フォルダの権限を適切に設定
   - 必要に応じて `chmod 700 output/` で制限

3. **一時ファイル**
   - 自動削除される（`.temp/`）
   - ディスク容量の心配なし

---

## パフォーマンス最適化

### 大量ファイルの処理

```bash
# 50ファイル以上を処理する場合、メモリ監視を推奨
top -p $$  # 別ターミナルで監視

# または、バッチ処理
for i in {1..10}; do
  ./run_pipeline_fixed.sh ./input ./output all
  sleep 5  # 次の処理まで待機
done
```

---

## サポート情報

問題が発生した場合：

1. **ドキュメントを確認**
   - README.md のトラブルシューティング
   - QUICKSTART.md のQ&A

2. **ログを確認**
   ```bash
   # エラーメッセージを確認
   ./run_pipeline_fixed.sh ./input ./output all 2>&1 | tee process.log
   ```

3. **手動テスト**
   ```bash
   # 個別スクリプトをテスト
   python3 convert_article_focused.py input/test.xml output/test.xml
   ```

---

**最終更新**: 2025年11月11日

---

## 関連ファイル

- `README.md` - 完全なドキュメント
- `QUICKSTART.md` - クイックスタート
- `CHANGES.md` - 修正内容の詳細
