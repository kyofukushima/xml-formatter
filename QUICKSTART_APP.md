# Streamlitアプリケーション クイックスタートガイド

## 動作確認手順

### 1. 仮想環境の作成（初回のみ）

```bash
# プロジェクトディレクトリに移動
cd /Users/fukushima/Documents/xml_anken/kouzou1_xml_app

# 仮想環境を作成
python3 -m venv venv
```

### 2. 仮想環境の有効化

```bash
# macOS/Linuxの場合
source venv/bin/activate

# 仮想環境が有効化されると、プロンプトの前に (venv) が表示されます
```

### 3. 必要なライブラリのインストール

```bash
# requirements.txtからすべてのライブラリをインストール
pip install -r requirements.txt
```

### 4. Streamlitアプリケーションの起動

```bash
# アプリケーションを起動
streamlit run app.py
```

ブラウザが自動的に開き、`http://localhost:8501`でアプリケーションが表示されます。

---

## よくある問題と解決方法

### 仮想環境が有効化されない場合

```bash
# 仮想環境のパスを確認
ls -la venv/bin/activate

# 手動で有効化
source venv/bin/activate
```

### ライブラリのインストールエラー

```bash
# pipを最新版にアップグレード
pip install --upgrade pip

# 再度インストール
pip install -r requirements.txt
```

### ポート8501が既に使用されている場合

```bash
# 別のポートで起動
streamlit run app.py --server.port 8502
```

### 仮想環境を無効化する場合

```bash
# 仮想環境を無効化
deactivate
```

---

## 開発モードでの起動

```bash
# 自動リロードを有効にする（デフォルト）
streamlit run app.py --server.runOnSave true
```

ファイルを保存すると自動的にアプリケーションがリロードされます。

---

## ページ構成

起動後 `http://localhost:8501` でホームが開きます。他のページは左メニュー（サイドバー上部のナビゲーション）から切り替えます。ページの実体は `app_pages/` 配下にあります。

| グループ | ページ | 用途 |
|---|---|---|
| | 🏠 ホーム | XMLをアップロードして変換パイプラインを実行。サイドバーで実行スクリプトと各オプション（列記List保護、LineBreak付きList保護、表・図の後のList保護、ColumnなしList統合、文頭全角スペース補填）を選択。変換後に構文検証とテキスト内容検証が自動実行される。ラベル判定表とラベル種別の手動指定もここ |
| | 🔄 逆変換 | Item〜Subitem10の階層をList要素に戻す。処理対象の親要素の選択と、逆変換前の文頭全角スペース除去が可能 |
| | 📊 List有無判定 | 複数XMLまたはZIP化したフォルダをアップロードし、List要素の有無と個数を一覧表示。CSVダウンロード可 |
| | 🈳 文頭スペース補填 | 変換パイプラインを通さず、文頭全角スペース補填だけを実行 |
| | ✅ 納品前検証 | 変換前後のXMLをアップロードし、ホームと同じ検証（テキスト欠落・文書順・表・図・構造要素数）を単独実行。スペース無視オプション付き |
| 設定 | ⚙️ ラベル設定管理 | ラベル定義・優先度・分割モードの編集（`scripts/config/label_config.json`） |
| 設定 | 🔤 全角スペース補填設定 | 補填オプションをXML例で確認しながら設定。ホームのサイドバーと連動 |
| 設定 | 📑 List保護・統合設定 | 列記保護・LineBreak保護・ColumnなしList統合・表・図の後のList保護をXML例で確認しながら設定。ホームのサイドバーと連動 |

### 基本的な流れ

1. ホームでXMLファイルをアップロードし、ラベル判定表を確認する（必要なら手動指定を適用）。
2. サイドバーでオプションを確認する。ColumnなしListの統合と文頭全角スペース補填はデフォルトON、列記List保護・LineBreak付きList保護・表・図の後のList保護はデフォルトOFF。従来どおり段落ごとに個別の要素へ分割したい場合は統合をOFFにする。
3. 「処理開始」で変換を実行し、検証結果を確認する。
4. 変換後XML（`_final` 付きファイル名）をダウンロードする。必要に応じて「納品前検証」で再検証する。

各機能の詳細は [README.md](./README.md) を参照してください。


