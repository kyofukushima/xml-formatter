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

## 各ページへのアクセス

- **ホームページ**: `http://localhost:8501` （デフォルト）
- **設定ページ**: `http://localhost:8501/⚙️_設定`

サイドバーのナビゲーションから各ページにアクセスできます。


