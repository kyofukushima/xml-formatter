# Streamlit開発環境セットアップガイド

## 概要

本ドキュメントは、XML変換パイプライン処理システムのWebアプリケーション（Streamlitベース）の開発環境をセットアップする手順を説明します。

---

## 前提条件

### 必要な環境

- **Python**: 3.7以上（推奨: 3.9以上）
- **pip**: Pythonパッケージマネージャー
- **Git**: バージョン管理システム（オプション）

### 推奨環境

- **OS**: macOS, Linux, Windows
- **エディタ**: VS Code, PyCharm, その他お好みのエディタ
- **仮想環境**: venv, conda（推奨）

---

## セットアップ手順

### 1. プロジェクトのクローン/ダウンロード

```bash
# Gitを使用する場合
git clone <repository-url>
cd kouzou1_xml_app

# または、既存のプロジェクトディレクトリに移動
cd /Users/fukushima/Documents/xml_anken/kouzou1_xml_app
```

### 2. 仮想環境の作成（推奨）

```bash
# venvを使用する場合
python3 -m venv venv

# 仮想環境の有効化（macOS/Linux）
source venv/bin/activate

# 仮想環境の有効化（Windows）
venv\Scripts\activate
```

### 3. 必要なライブラリのインストール

```bash
# 必須ライブラリ
pip install streamlit

# 推奨ライブラリ
pip install streamlit-json-editor jsonschema

# 既存のプロジェクトで使用しているライブラリ
pip install lxml

# 開発用ライブラリ（オプション）
pip install black flake8 pytest
```

### 4. requirements.txtの作成

プロジェクトルートに`requirements.txt`を作成します：

```txt
# Webアプリフレームワーク
streamlit>=1.28.0

# JSONエディタ
streamlit-json-editor>=0.1.0

# JSONスキーマバリデーション
jsonschema>=4.17.0

# XML処理（既存）
lxml>=4.9.0

# 開発用（オプション）
black>=23.0.0
flake8>=6.0.0
pytest>=7.0.0
```

インストールコマンド：

```bash
pip install -r requirements.txt
```

### 5. プロジェクト構造の確認

```
kouzou1_xml_app/
├── app.py                    # Streamlitアプリのメインファイル（新規作成）
├── pages/                    # マルチページアプリ用（オプション）
│   ├── 01_🏠_ホーム.py
│   ├── 02_⚙️_設定.py
│   └── 03_📋_履歴.py
├── utils/                    # ユーティリティ関数
│   ├── __init__.py
│   ├── pipeline.py          # パイプライン実行関数
│   ├── validation.py        # 検証関数
│   └── config_manager.py    # 設定管理関数
├── scripts/                 # 既存の変換スクリプト
│   ├── config/
│   │   └── label_config.json
│   └── ...
├── input/                   # 入力ファイル用（既存）
├── output/                  # 出力ファイル用（既存）
├── docs/                    # ドキュメント（既存）
├── requirements.txt         # 依存関係（新規作成）
└── README.md               # プロジェクト説明（既存）
```

---

## 開発の開始

### 1. 基本的なStreamlitアプリの作成

`app.py`を作成します：

```python
import streamlit as st

st.set_page_config(
    page_title="XML変換パイプライン",
    page_icon="📄",
    layout="wide"
)

st.title("📄 XML変換パイプライン処理システム")

st.write("開発中...")
```

### 2. アプリの起動

```bash
streamlit run app.py
```

ブラウザが自動的に開き、`http://localhost:8501`でアプリが表示されます。

### 3. 開発モードでの起動

```bash
# 自動リロードを有効にする（デフォルト）
streamlit run app.py --server.runOnSave true

# または、設定ファイルで設定
# .streamlit/config.toml に以下を追加:
# [server]
# runOnSave = true
```

---

## 設定ファイル

### Streamlit設定ファイル

`.streamlit/config.toml`を作成します：

```toml
[server]
port = 8501
enableCORS = false
enableXsrfProtection = true
runOnSave = true

[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"

[browser]
gatherUsageStats = false
```

### プロジェクト設定ファイル

`config/app_config.py`を作成します（オプション）：

```python
# アプリケーション設定
SCRIPTS_DIR = "scripts"
CONFIG_DIR = "scripts/config"
LABEL_CONFIG_FILE = "scripts/config/label_config.json"
INPUT_DIR = "input"
OUTPUT_DIR = "output"
```

---

## トラブルシューティング

### よくある問題

#### 1. `streamlit: command not found`

**原因**: Streamlitがインストールされていない、または仮想環境が有効化されていない

**解決方法**:
```bash
# 仮想環境を有効化
source venv/bin/activate  # macOS/Linux
# または
venv\Scripts\activate  # Windows

# Streamlitをインストール
pip install streamlit
```

#### 2. ポート8501が既に使用されている

**原因**: 他のプロセスがポート8501を使用している

**解決方法**:
```bash
# 別のポートで起動
streamlit run app.py --server.port 8502

# または、使用中のプロセスを終了
# macOS/Linux
lsof -ti:8501 | xargs kill -9

# Windows
netstat -ano | findstr :8501
taskkill /PID <PID> /F
```

#### 3. モジュールが見つからない

**原因**: パスが正しく設定されていない

**解決方法**:
```python
# app.pyの先頭に以下を追加
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
```

#### 4. JSONファイルの読み込みエラー

**原因**: ファイルパスが正しくない、またはファイルが存在しない

**解決方法**:
```python
from pathlib import Path

# 絶対パスを使用
config_path = Path(__file__).parent.parent / "scripts" / "config" / "label_config.json"

# ファイルの存在確認
if not config_path.exists():
    st.error(f"設定ファイルが見つかりません: {config_path}")
```

---

## 開発ワークフロー

### 1. 機能開発の流れ

1. **ブランチの作成**（Git使用時）
   ```bash
   git checkout -b feature/機能名
   ```

2. **機能の実装**
   - `app.py`または`pages/`に機能を追加
   - `utils/`にユーティリティ関数を追加

3. **動作確認**
   ```bash
   streamlit run app.py
   ```

4. **テストの作成**（オプション）
   ```bash
   pytest tests/
   ```

5. **コミット**
   ```bash
   git add .
   git commit -m "機能: 説明"
   ```

### 2. デバッグ方法

**Streamlitのデバッグ機能**:
- `st.write()`: 変数の値を表示
- `st.json()`: JSONデータを表示
- `st.error()`, `st.warning()`, `st.info()`: エラーメッセージの表示

**Pythonデバッガーの使用**:
```python
import pdb; pdb.set_trace()  # ブレークポイント
```

**ログの確認**:
```bash
# Streamlitのログを確認
streamlit run app.py --logger.level=debug
```

---

## 次のステップ

1. **基本機能の実装**: [`development_guide.md`](development_guide.md)を参照
2. **機能要件の確認**: [`../functional_requirements_specification.md`](../functional_requirements_specification.md)を参照
3. **実装例の確認**: [`../web_app_implementation_examples.md`](../web_app_implementation_examples.md)を参照
4. **ライブラリの確認**: [`../label_config_libraries_recommendation.md`](../label_config_libraries_recommendation.md)を参照

---

## 参考資料

- [Streamlit公式ドキュメント](https://docs.streamlit.io/)
- [Streamlit API Reference](https://docs.streamlit.io/library/api-reference)
- [プロジェクトの機能要件定義書](../functional_requirements_specification.md)
- [アーキテクチャ比較資料](../web_app_architecture_comparison.md)

---

**最終更新**: 2025年1月

