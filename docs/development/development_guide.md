# Streamlit開発ガイド

## 概要

本ドキュメントは、StreamlitベースのWebアプリケーション開発における実装ガイドラインとベストプラクティスを説明します。

---

## プロジェクト構造

### 推奨ディレクトリ構造

```
kouzou1_xml_app/
├── app.py                    # メインアプリケーション
├── pages/                    # マルチページアプリ（オプション）
│   ├── 01_🏠_ホーム.py
│   ├── 02_⚙️_設定.py
│   └── 03_📋_履歴.py
├── utils/                    # ユーティリティ関数
│   ├── __init__.py
│   ├── pipeline.py          # パイプライン実行
│   ├── validation.py        # 検証処理
│   ├── config_manager.py    # 設定管理
│   └── file_handler.py      # ファイル操作
├── components/              # 再利用可能なコンポーネント（オプション）
│   ├── __init__.py
│   ├── file_uploader.py
│   └── progress_display.py
├── scripts/                 # 既存の変換スクリプト
│   ├── config/
│   │   └── label_config.json
│   └── ...
├── input/                   # 入力ファイル
├── output/                  # 出力ファイル
├── .streamlit/             # Streamlit設定
│   └── config.toml
├── requirements.txt         # 依存関係
└── docs/                   # ドキュメント
```

---

## 実装の優先順位（Phase 1）

### Phase 1.1: 基本機能（必須）

1. **FR-001: XMLファイルのアップロード**
2. **FR-002: 変換スクリプトの選択**
3. **FR-003: パイプライン処理の実行**
4. **FR-004: 処理済みXMLファイルのダウンロード**
5. **FR-005: 処理進捗の表示**
6. **FR-006: エラーメッセージの表示**

### Phase 1.2: 検証機能

7. **FR-007: 構文検証の実行**
8. **FR-008: テキスト内容検証の実行**
9. **FR-009: 検証レポートの表示**

### Phase 1.3: ラベル設定機能

10. **FR-029: ブーリアン型パラメーターの簡易設定**（最優先）
11. **FR-023: ラベル設定の表示**
12. **FR-027: ラベル設定のバリデーション**
13. **FR-025: ラベル設定の保存**
14. **FR-026: ラベル設定のインポート/エクスポート**
15. **FR-024: ラベル設定の編集**

### Phase 1.4: オプション機能

16. **FR-010: XMLファイルのプレビュー**
17. **FR-011: 中間ファイルのダウンロード**

---

## 実装パターン

### 1. ファイル構造のパターン

#### シングルページアプリ

```python
# app.py
import streamlit as st
from utils.pipeline import run_pipeline
from utils.validation import validate_xml

def main():
    st.title("XML変換パイプライン")
    
    # ファイルアップロード
    uploaded_file = st.file_uploader("XMLファイル", type=["xml"])
    
    if uploaded_file:
        # 処理実行
        if st.button("処理開始"):
            result = run_pipeline(uploaded_file)
            st.download_button("ダウンロード", data=result)

if __name__ == "__main__":
    main()
```

#### マルチページアプリ

```python
# pages/01_🏠_ホーム.py
import streamlit as st

st.title("ホーム")
st.write("XMLファイルをアップロードして処理を開始します")

# pages/02_⚙️_設定.py
import streamlit as st

st.title("設定")
st.write("ラベル設定を編集します")
```

### 2. セッション状態の管理

```python
import streamlit as st

# セッション状態の初期化
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None

if 'processing' not in st.session_state:
    st.session_state.processing = False

# セッション状態の使用
uploaded_file = st.file_uploader("XMLファイル", type=["xml"])
if uploaded_file:
    st.session_state.uploaded_file = uploaded_file

# セッション状態のクリア
if st.button("リセット"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
```

### 3. エラーハンドリング

```python
import streamlit as st
from pathlib import Path

def load_config():
    """設定ファイルの読み込み（エラーハンドリング付き）"""
    config_path = Path("scripts/config/label_config.json")
    
    try:
        if not config_path.exists():
            st.error(f"設定ファイルが見つかりません: {config_path}")
            return None
        
        import json
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    except json.JSONDecodeError as e:
        st.error(f"JSONファイルの形式が正しくありません: {e}")
        return None
    
    except Exception as e:
        st.error(f"予期しないエラーが発生しました: {e}")
        return None
```

### 4. 進捗表示

```python
import streamlit as st
import time

def show_progress(total_steps, current_step, status_text=""):
    """進捗バーの表示"""
    progress_bar = st.progress(0)
    status_container = st.empty()
    
    progress = current_step / total_steps
    progress_bar.progress(progress)
    
    if status_text:
        status_container.info(f"処理中 ({current_step}/{total_steps}): {status_text}")
    
    return progress_bar, status_container

# 使用例
progress_bar, status = show_progress(15, 5, "convert_item_step0.py を実行中")
```

### 5. ファイル操作

```python
import streamlit as st
import tempfile
from pathlib import Path

def save_uploaded_file(uploaded_file):
    """アップロードされたファイルを一時保存"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xml') as tmp_file:
        tmp_file.write(uploaded_file.read())
        return Path(tmp_file.name)

def cleanup_temp_files(file_paths):
    """一時ファイルの削除"""
    for path in file_paths:
        if isinstance(path, Path) and path.exists():
            path.unlink()
```

---

## ユーティリティ関数の実装

### utils/pipeline.py

```python
"""パイプライン実行ユーティリティ"""
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Tuple

def run_pipeline(
    input_path: Path,
    output_path: Path,
    scripts: List[str],
    script_dir: Path,
    timeout: int = 300
) -> Tuple[bool, Optional[str]]:
    """
    パイプラインを実行
    
    Args:
        input_path: 入力XMLファイルのパス
        output_path: 出力XMLファイルのパス
        scripts: 実行するスクリプトのリスト
        script_dir: スクリプトディレクトリのパス
        timeout: タイムアウト時間（秒）
    
    Returns:
        (success: bool, error_message: Optional[str])
    """
    current_input = input_path
    
    for script_name in scripts:
        script_path = script_dir / script_name
        
        if not script_path.exists():
            return False, f"スクリプトが見つかりません: {script_name}"
        
        step_output = script_dir.parent / "temp" / f"step_{script_name.replace('.py', '.xml')}"
        step_output.parent.mkdir(exist_ok=True)
        
        try:
            result = subprocess.run(
                [sys.executable, str(script_path), str(current_input), str(step_output)],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode != 0:
                return False, f"{script_name}の実行に失敗しました: {result.stderr}"
            
            if not step_output.exists():
                return False, f"出力ファイルが作成されませんでした: {script_name}"
            
            current_input = step_output
        
        except subprocess.TimeoutExpired:
            return False, f"タイムアウト: {script_name}"
        except Exception as e:
            return False, f"実行エラー: {e}"
    
    # 最終結果をコピー
    import shutil
    shutil.copy(current_input, output_path)
    
    return True, None
```

### utils/config_manager.py

```python
"""設定管理ユーティリティ"""
import json
from pathlib import Path
from typing import Dict, Optional, Tuple

def load_label_config(config_path: Optional[Path] = None) -> Optional[Dict]:
    """ラベル設定ファイルを読み込む"""
    if config_path is None:
        config_path = Path("scripts/config/label_config.json")
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return None

def save_label_config(config: Dict, config_path: Optional[Path] = None) -> Tuple[bool, Optional[str]]:
    """ラベル設定ファイルを保存"""
    if config_path is None:
        config_path = Path("scripts/config/label_config.json")
    
    try:
        # バックアップを作成
        if config_path.exists():
            backup_path = config_path.with_suffix('.json.bak')
            import shutil
            shutil.copy(config_path, backup_path)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        return True, None
    except Exception as e:
        return False, str(e)

def update_boolean_settings(
    config: Dict,
    same_pattern_same_hierarchy: bool,
    allow_cross_hierarchy_split: bool,
    column_enabled: bool,
    split_mode_enabled: bool
) -> Dict:
    """ブーリアン型パラメーターを更新"""
    config['hierarchy_rules']['same_pattern_same_hierarchy'] = same_pattern_same_hierarchy
    config['hierarchy_rules']['allow_cross_hierarchy_split'] = allow_cross_hierarchy_split
    
    if 'conversion_behaviors' not in config:
        config['conversion_behaviors'] = {}
    
    if 'column_list_text_first_column' not in config['conversion_behaviors']:
        config['conversion_behaviors']['column_list_text_first_column'] = {}
    config['conversion_behaviors']['column_list_text_first_column']['enabled'] = column_enabled
    
    if 'no_column_text_split_mode' not in config['conversion_behaviors']:
        config['conversion_behaviors']['no_column_text_split_mode'] = {}
    config['conversion_behaviors']['no_column_text_split_mode']['enabled'] = split_mode_enabled
    
    return config
```

---

## ベストプラクティス

### 1. コードの整理

- **関数の分割**: 1つの関数は1つの責任を持つ
- **定数の定義**: マジックナンバーや文字列は定数として定義
- **型ヒント**: 関数の引数と戻り値に型ヒントを付ける

### 2. エラーハンドリング

- **適切なエラーメッセージ**: ユーザーに分かりやすいエラーメッセージを表示
- **例外処理**: 予期しないエラーにも対応
- **ログの記録**: エラーの詳細をログに記録

### 3. パフォーマンス

- **キャッシュの活用**: `@st.cache_data`を使用して重い処理をキャッシュ
- **非同期処理**: 長時間処理は非同期で実行（将来の拡張）

### 4. ユーザビリティ

- **明確なメッセージ**: ユーザーに分かりやすいメッセージを表示
- **進捗表示**: 処理中の状態を明確に表示
- **確認ダイアログ**: 重要な操作には確認を求める

---

## テスト

### 単体テストの例

```python
# tests/test_pipeline.py
import pytest
from pathlib import Path
from utils.pipeline import run_pipeline

def test_run_pipeline_success():
    """パイプライン実行の成功テスト"""
    input_path = Path("tests/test_data/input.xml")
    output_path = Path("tests/test_data/output.xml")
    scripts = ["convert_item_step0.py"]
    script_dir = Path("scripts")
    
    success, error = run_pipeline(input_path, output_path, scripts, script_dir)
    
    assert success is True
    assert error is None
    assert output_path.exists()
```

### 実行方法

```bash
# すべてのテストを実行
pytest tests/

# 特定のテストファイルを実行
pytest tests/test_pipeline.py

# カバレッジを取得
pytest --cov=utils tests/
```

---

## デプロイ

### Streamlit Cloud

1. GitHubリポジトリにプッシュ
2. [Streamlit Cloud](https://streamlit.io/cloud)にサインアップ
3. リポジトリを接続
4. デプロイ設定を確認
5. デプロイ

### Docker

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

```bash
# ビルド
docker build -t xml-pipeline-app .

# 実行
docker run -p 8501:8501 xml-pipeline-app
```

---

## 参考資料

- [機能要件定義書](../functional_requirements_specification.md)
- [実装例](../web_app_implementation_examples.md)
- [ライブラリ推奨](../label_config_libraries_recommendation.md)
- [Streamlit公式ドキュメント](https://docs.streamlit.io/)

---

**最終更新**: 2025年1月

