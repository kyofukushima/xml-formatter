# ラベル設定機能実装 推奨ライブラリ

## 概要

ラベル設定の表示・編集・バリデーション機能（FR-023～FR-027）およびブーリアン型パラメーター簡易設定機能（FR-029）を実装する際の推奨ライブラリをまとめます。

本資料は、推奨フレームワークである**Streamlit**を前提として、各機能に適したライブラリを推奨します。

---

## 推奨フレームワーク: Streamlit

既存のアーキテクチャ比較資料（`web_app_architecture_comparison.md`）に基づき、**Streamlit**が推奨フレームワークとして選定されています。

---

## 機能別推奨ライブラリ

### FR-023: ラベル設定の表示

#### 要件
- JSON設定ファイル（`label_config.json`）の内容を読み込んで表示
- ラベル定義、パターン優先度、階層ルール、変換動作を分かりやすく表示

#### 推奨ライブラリ

**1. 標準ライブラリ（推奨）**
- **`json`**: Python標準ライブラリ
  - JSONファイルの読み込み・パース
  - 追加のインストール不要
  - シンプルで確実

**2. 表示用ライブラリ**
- **`streamlit`**: 標準コンポーネント
  - `st.json()`: JSONデータの整形表示
  - `st.dataframe()`: 表形式での表示
  - `st.expander()`: 折りたたみ可能なセクション
  - `st.markdown()`: マークダウン形式での説明表示

**実装例**
```python
import json
import streamlit as st

# JSONファイルの読み込み
with open('scripts/config/label_config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# ラベル定義を表形式で表示
st.subheader("ラベル定義")
for label_id, label_def in config['label_definitions'].items():
    with st.expander(f"{label_def['name']} ({label_id})"):
        st.write(f"**パターン**: {label_def['patterns']}")
        st.write(f"**例**: {label_def['examples']}")
        st.write(f"**説明**: {label_def['description']}")
```

---

### FR-024: ラベル設定の編集

#### 要件
- JSON設定ファイルの内容を編集
- ラベル定義の追加・編集・削除
- パターン優先度の順序変更
- 階層ルールと変換動作の編集

#### 推奨ライブラリ

**1. JSONエディタ（推奨）**
- **`streamlit-json-editor`**: Streamlit用のJSONエディタ
  - インストール: `pip install streamlit-json-editor`
  - JSONを視覚的に編集可能
  - バリデーション機能付き
  - GitHub: https://github.com/okld/streamlit-json-editor

**2. 代替案: カスタムフォーム**
- **`streamlit`**: 標準コンポーネント
  - `st.text_input()`: テキスト入力
  - `st.text_area()`: 複数行テキスト入力
  - `st.selectbox()`: 選択ボックス
  - `st.multiselect()`: 複数選択
  - `st.button()`: ボタン

**3. JSON操作**
- **`json`**: Python標準ライブラリ
  - JSONデータの操作・保存

**実装例（streamlit-json-editor使用）**
```python
import streamlit as st
from streamlit_json_editor import json_editor

# JSONファイルの読み込み
with open('scripts/config/label_config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# JSONエディタで編集
st.subheader("ラベル設定の編集")
edited_config = json_editor(config, key="label_config_editor")

if st.button("保存"):
    # バリデーション
    if validate_config(edited_config):
        # 保存
        with open('scripts/config/label_config.json', 'w', encoding='utf-8') as f:
            json.dump(edited_config, f, ensure_ascii=False, indent=2)
        st.success("設定を保存しました")
    else:
        st.error("設定にエラーがあります")
```

**実装例（カスタムフォーム）**
```python
import streamlit as st
import json

# ラベル定義の追加フォーム
st.subheader("新しいラベル定義を追加")
with st.form("add_label_form"):
    label_id = st.text_input("ラベルID")
    label_name = st.text_input("ラベル名")
    patterns = st.text_area("パターン（正規表現、1行に1つ）").split('\n')
    examples = st.text_area("例（1行に1つ）").split('\n')
    description = st.text_input("説明")
    
    if st.form_submit_button("追加"):
        # ラベル定義を追加
        config['label_definitions'][label_id] = {
            "id": label_id,
            "name": label_name,
            "patterns": [p.strip() for p in patterns if p.strip()],
            "examples": [e.strip() for e in examples if e.strip()],
            "description": description
        }
```

---

### FR-025: ラベル設定の保存

#### 要件
- 編集した設定をJSONファイルとして保存
- 既存ファイルの上書きまたは新規ファイルとして保存

#### 推奨ライブラリ

**1. 標準ライブラリ（推奨）**
- **`json`**: Python標準ライブラリ
  - JSONデータの保存
  - `json.dump()`: ファイルへの書き込み
  - `ensure_ascii=False`: 日本語の文字化け防止
  - `indent=2`: 読みやすい形式で保存

**2. ファイル操作**
- **`pathlib`**: Python標準ライブラリ
  - ファイルパスの操作
  - ファイルの存在確認

**実装例**
```python
import json
from pathlib import Path

def save_label_config(config, file_path=None):
    """ラベル設定を保存"""
    if file_path is None:
        file_path = Path('scripts/config/label_config.json')
    
    # バックアップを作成（オプション）
    if file_path.exists():
        backup_path = file_path.with_suffix('.json.bak')
        file_path.rename(backup_path)
    
    # 設定を保存
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    return True
```

---

### FR-026: ラベル設定のインポート/エクスポート

#### 要件
- JSON設定ファイルのエクスポート（ダウンロード）
- JSON設定ファイルのインポート（アップロード）

#### 推奨ライブラリ

**1. ファイルアップロード/ダウンロード（推奨）**
- **`streamlit`**: 標準コンポーネント
  - `st.file_uploader()`: ファイルアップロード
  - `st.download_button()`: ファイルダウンロード

**2. JSON操作**
- **`json`**: Python標準ライブラリ
  - JSONデータの読み込み・保存

**実装例**
```python
import streamlit as st
import json
from pathlib import Path

# エクスポート
def export_label_config():
    """ラベル設定をエクスポート"""
    config_path = Path('scripts/config/label_config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    config_json = json.dumps(config, ensure_ascii=False, indent=2)
    
    st.download_button(
        label="設定をエクスポート",
        data=config_json,
        file_name=f"label_config_{datetime.now().strftime('%Y%m%d')}.json",
        mime="application/json"
    )

# インポート
def import_label_config():
    """ラベル設定をインポート"""
    uploaded_file = st.file_uploader(
        "設定ファイルを選択",
        type=['json'],
        help="JSON形式の設定ファイルを選択してください"
    )
    
    if uploaded_file is not None:
        try:
            config = json.load(uploaded_file)
            # バリデーション
            if validate_config(config):
                st.success("設定ファイルが正常に読み込まれました")
                return config
            else:
                st.error("設定ファイルにエラーがあります")
                return None
        except json.JSONDecodeError:
            st.error("JSONファイルの形式が正しくありません")
            return None
```

---

### FR-027: ラベル設定のバリデーション

#### 要件
- JSON形式のチェック
- 必須項目のチェック
- ラベル定義の妥当性チェック
- パターン優先度の整合性チェック

#### 推奨ライブラリ

**1. JSONスキーマバリデーション（推奨）**
- **`jsonschema`**: JSONスキーマによるバリデーション
  - インストール: `pip install jsonschema`
  - JSONスキーマを定義してバリデーション
  - エラーメッセージが詳細
  - 公式: https://python-jsonschema.readthedocs.io/

**2. 正規表現バリデーション**
- **`re`**: Python標準ライブラリ
  - 正規表現パターンの妥当性チェック

**3. カスタムバリデーション**
- **`json`**: Python標準ライブラリ
  - JSON形式のチェック

**実装例（jsonschema使用）**
```python
import json
import jsonschema
from jsonschema import validate, ValidationError

# JSONスキーマの定義
LABEL_CONFIG_SCHEMA = {
    "type": "object",
    "required": ["label_definitions", "pattern_priority"],
    "properties": {
        "label_definitions": {
            "type": "object",
            "patternProperties": {
                ".*": {
                    "type": "object",
                    "required": ["id", "name", "patterns"],
                    "properties": {
                        "id": {"type": "string"},
                        "name": {"type": "string"},
                        "patterns": {"type": "array", "items": {"type": "string"}},
                        "examples": {"type": "array", "items": {"type": "string"}},
                        "description": {"type": "string"}
                    }
                }
            }
        },
        "pattern_priority": {
            "type": "array",
            "items": {"type": "string"}
        }
    }
}

def validate_config(config):
    """ラベル設定のバリデーション"""
    errors = []
    
    # JSONスキーマバリデーション
    try:
        validate(instance=config, schema=LABEL_CONFIG_SCHEMA)
    except ValidationError as e:
        errors.append(f"スキーマエラー: {e.message}")
    
    # カスタムバリデーション
    # 1. パターン優先度に含まれるラベルIDが、ラベル定義に存在するか
    label_ids = set(config.get('label_definitions', {}).keys())
    priority_ids = set(config.get('pattern_priority', []))
    
    missing_ids = priority_ids - label_ids
    if missing_ids:
        errors.append(f"パターン優先度に存在しないラベルID: {missing_ids}")
    
    # 2. 正規表現パターンの妥当性チェック
    import re
    for label_id, label_def in config.get('label_definitions', {}).items():
        for pattern in label_def.get('patterns', []):
            try:
                re.compile(pattern)
            except re.error as e:
                errors.append(f"ラベル '{label_id}' のパターンが無効: {pattern} ({e})")
    
    return len(errors) == 0, errors
```

**実装例（カスタムバリデーション）**
```python
import json
import re
from pathlib import Path

def validate_label_config(config):
    """ラベル設定のカスタムバリデーション"""
    errors = []
    
    # 必須項目のチェック
    if 'label_definitions' not in config:
        errors.append("必須項目 'label_definitions' がありません")
    
    if 'pattern_priority' not in config:
        errors.append("必須項目 'pattern_priority' がありません")
    
    # ラベル定義のチェック
    label_definitions = config.get('label_definitions', {})
    for label_id, label_def in label_definitions.items():
        # IDの重複チェック
        if label_def.get('id') != label_id:
            errors.append(f"ラベルIDの不一致: {label_id}")
        
        # 必須項目のチェック
        if 'patterns' not in label_def:
            errors.append(f"ラベル '{label_id}' に 'patterns' がありません")
        
        # 正規表現パターンの妥当性チェック
        for pattern in label_def.get('patterns', []):
            try:
                re.compile(pattern)
            except re.error as e:
                errors.append(f"ラベル '{label_id}' のパターンが無効: {pattern}")
    
    # パターン優先度のチェック
    pattern_priority = config.get('pattern_priority', [])
    label_ids = set(label_definitions.keys())
    priority_ids = set(pattern_priority)
    
    missing_ids = priority_ids - label_ids
    if missing_ids:
        errors.append(f"パターン優先度に存在しないラベルID: {missing_ids}")
    
    return len(errors) == 0, errors
```

---

### FR-029: ブーリアン型パラメーターの簡易設定

#### 要件
- ブーリアン型パラメーターをチェックボックスまたはトグルスイッチで表示
- オン/オフの切り替え
- 変更されたパラメーターのみをJSONファイルに反映

#### 推奨ライブラリ

**1. UIコンポーネント（推奨）**
- **`streamlit`**: 標準コンポーネント
  - `st.checkbox()`: チェックボックス
  - `st.toggle()`: トグルスイッチ（Streamlit 1.28.0以降）
  - `st.columns()`: レイアウト

**2. JSON操作**
- **`json`**: Python標準ライブラリ
  - JSONデータの読み込み・保存

**実装例**
```python
import streamlit as st
import json
from pathlib import Path

def render_boolean_settings():
    """ブーリアン型パラメーターの簡易設定UI"""
    # JSONファイルの読み込み
    config_path = Path('scripts/config/label_config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    st.subheader("簡易設定")
    
    # 階層ルールセクション
    st.markdown("### 階層ルール")
    
    hierarchy_rules = config.get('hierarchy_rules', {})
    
    same_pattern = st.checkbox(
        "同じパターンは同じ階層にまとめる",
        value=hierarchy_rules.get('same_pattern_same_hierarchy', True),
        help="同じラベルパターンは同じ階層の要素にまとめます"
    )
    
    allow_cross = st.checkbox(
        "階層をまたぐ分割を許可する",
        value=hierarchy_rules.get('allow_cross_hierarchy_split', False),
        help="階層をまたいで要素を分割することを許可します"
    )
    
    # 変換動作セクション
    st.markdown("### 変換動作")
    
    conversion_behaviors = config.get('conversion_behaviors', {})
    
    column_enabled = st.checkbox(
        "Column処理の動作設定を有効にする",
        value=conversion_behaviors.get('column_list_text_first_column', {}).get('enabled', True),
        help="Columnが2つあり、かつ1つ目のColumnがラベル要素に該当しない場合、ItemSentence/Subitem*Sentenceの中にSentence要素を2つ作成して各Columnの値を挿入する"
    )
    
    split_mode_enabled = st.checkbox(
        "カラムなしリストの分割モードを有効にする",
        value=conversion_behaviors.get('no_column_text_split_mode', {}).get('enabled', True),
        help="no_column_textタイプのItemの後、カラムなしリストを並列分割するかどうか。false: List要素のまま取り込む（モード1）、true: 並列分割して別々のItem要素に変換（モード2）"
    )
    
    # 保存ボタン
    if st.button("設定を保存", type="primary"):
        # 変更を反映
        config['hierarchy_rules']['same_pattern_same_hierarchy'] = same_pattern
        config['hierarchy_rules']['allow_cross_hierarchy_split'] = allow_cross
        
        if 'column_list_text_first_column' not in config['conversion_behaviors']:
            config['conversion_behaviors']['column_list_text_first_column'] = {}
        config['conversion_behaviors']['column_list_text_first_column']['enabled'] = column_enabled
        
        if 'no_column_text_split_mode' not in config['conversion_behaviors']:
            config['conversion_behaviors']['no_column_text_split_mode'] = {}
        config['conversion_behaviors']['no_column_text_split_mode']['enabled'] = split_mode_enabled
        
        # 保存
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        st.success("設定を保存しました")
```

---

## 推奨ライブラリ一覧

### 必須ライブラリ

| ライブラリ | 用途 | インストール |
|-----------|------|------------|
| `streamlit` | Webアプリフレームワーク | `pip install streamlit` |
| `json` | JSON操作（標準ライブラリ） | 不要 |
| `pathlib` | ファイルパス操作（標準ライブラリ） | 不要 |

### 推奨ライブラリ

| ライブラリ | 用途 | インストール | 優先度 |
|-----------|------|------------|--------|
| `streamlit-json-editor` | JSONエディタ（FR-024） | `pip install streamlit-json-editor` | 高 |
| `jsonschema` | JSONスキーマバリデーション（FR-027） | `pip install jsonschema` | 高 |
| `re` | 正規表現バリデーション（標準ライブラリ） | 不要 | 中 |

### オプションライブラリ

| ライブラリ | 用途 | インストール | 優先度 |
|-----------|------|------------|--------|
| `datetime` | 日時処理（標準ライブラリ） | 不要 | 低 |

---

## インストールコマンド

```bash
# 必須ライブラリ
pip install streamlit

# 推奨ライブラリ
pip install streamlit-json-editor jsonschema
```

---

## 実装の優先順位

### Phase 1で実装する機能

1. **FR-029: ブーリアン型パラメーターの簡易設定**（最優先）
   - Streamlit標準コンポーネントのみで実装可能
   - 実装が簡単で、すぐに使える

2. **FR-023: ラベル設定の表示**
   - Streamlit標準コンポーネントのみで実装可能
   - JSONファイルの読み込みと表示

3. **FR-027: ラベル設定のバリデーション**
   - `jsonschema`を使用して実装
   - 設定の保存前に必須

4. **FR-025: ラベル設定の保存**
   - 標準ライブラリのみで実装可能
   - バリデーション後に保存

5. **FR-026: ラベル設定のインポート/エクスポート**
   - Streamlit標準コンポーネントで実装可能
   - ファイルアップロード/ダウンロード機能

6. **FR-024: ラベル設定の編集**
   - `streamlit-json-editor`を使用して実装
   - 最も複雑だが、ユーザビリティが高い

---

## 実装例の統合

すべての機能を統合した実装例は、`web_app_implementation_examples.md`を参照してください。

---

**最終更新**: 2025年1月

