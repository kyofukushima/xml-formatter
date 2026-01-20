# Webアプリ化 実装例集

## 目次

1. [Streamlit実装例（推奨）](#streamlit実装例推奨)
2. [Flask実装例](#flask実装例)
3. [FastAPI実装例](#fastapi実装例)
4. [共通ユーティリティ関数](#共通ユーティリティ関数)

---

## Streamlit実装例（推奨）

### 最小実装例

```python
# app.py
import streamlit as st
import subprocess
from pathlib import Path
import tempfile
import os
import sys

# ページ設定
st.set_page_config(
    page_title="XML変換パイプライン",
    page_icon="📄",
    layout="wide"
)

# タイトル
st.title("📄 XML変換パイプライン処理システム")

# サイドバー: 設定
st.sidebar.header("⚙️ 処理オプション")

# 利用可能なスクリプトリスト
AVAILABLE_SCRIPTS = [
    "preprocess_non_first_sentence_to_list.py",
    "convert_article_focused.py",
    "convert_paragraph_step3.py",
    "convert_paragraph_step4.py",
    "convert_item_step0.py",
    "convert_subitem1_step0.py",
    "convert_subitem2_step0.py",
    "convert_subitem3_step0.py",
    "convert_subitem4_step0.py",
    "convert_subitem5_step0.py",
    "convert_subitem6_step0.py",
    "convert_subitem7_step0.py",
    "convert_subitem8_step0.py",
    "convert_subitem9_step0.py",
    "convert_subitem10_step0.py",
]

# スクリプト選択
selected_scripts = st.sidebar.multiselect(
    "実行するスクリプトを選択",
    options=AVAILABLE_SCRIPTS,
    default=AVAILABLE_SCRIPTS,  # デフォルトで全選択
    help="処理に使用するスクリプトを選択してください"
)

# メインエリア
st.header("📤 ファイルアップロード")

uploaded_file = st.file_uploader(
    "XMLファイルをアップロードしてください",
    type=["xml"],
    help="処理対象のXMLファイルを選択してください"
)

if uploaded_file is not None:
    # ファイル情報表示
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"📄 ファイル名: {uploaded_file.name}")
        st.info(f"📊 ファイルサイズ: {uploaded_file.size:,} bytes")
    
    # プレビューオプション
    show_preview = st.checkbox("入力ファイルをプレビュー", value=False)
    if show_preview:
        uploaded_file.seek(0)
        st.code(uploaded_file.read().decode('utf-8'), language="xml")
        uploaded_file.seek(0)
    
    # 処理開始ボタン
    if st.button("🚀 処理開始", type="primary", use_container_width=True):
        if not selected_scripts:
            st.error("⚠️ 実行するスクリプトを1つ以上選択してください")
        else:
            process_file(uploaded_file, selected_scripts)

def process_file(uploaded_file, selected_scripts):
    """ファイル処理のメイン関数"""
    script_dir = Path(__file__).parent.parent / "scripts"
    
    # セッション状態の初期化
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    
    st.session_state.processing = True
    
    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = Path(tmpdir) / uploaded_file.name
        output_path = Path(tmpdir) / f"{Path(uploaded_file.name).stem}-final.xml"
        
        # 入力ファイルを保存
        input_path.write_bytes(uploaded_file.read())
        
        # 進捗表示用のコンテナ
        progress_container = st.container()
        status_container = st.container()
        
        with progress_container:
            progress_bar = st.progress(0)
            status_text = st.empty()
        
        # 各スクリプトを実行
        current_input = input_path
        errors = []
        
        for i, script_name in enumerate(selected_scripts):
            script_path = script_dir / script_name
            
            if not script_path.exists():
                error_msg = f"スクリプトが見つかりません: {script_name}"
                st.error(error_msg)
                errors.append(error_msg)
                break
            
            # ステータス更新
            with status_container:
                st.info(f"🔄 実行中 ({i+1}/{len(selected_scripts)}): {script_name}")
            
            # 中間出力ファイル
            step_output = Path(tmpdir) / f"step_{i}_{script_name.replace('.py', '.xml')}"
            
            # スクリプト実行
            try:
                result = subprocess.run(
                    [sys.executable, str(script_path), str(current_input), str(step_output)],
                    capture_output=True,
                    text=True,
                    timeout=300  # 5分タイムアウト
                )
                
                if result.returncode != 0:
                    error_msg = f"エラー: {script_name}\n{result.stderr}"
                    st.error(error_msg)
                    errors.append(error_msg)
                    break
                
                if not step_output.exists():
                    error_msg = f"出力ファイルが作成されませんでした: {script_name}"
                    st.error(error_msg)
                    errors.append(error_msg)
                    break
                
                current_input = step_output
                progress_bar.progress((i + 1) / len(selected_scripts))
                
            except subprocess.TimeoutExpired:
                error_msg = f"タイムアウト: {script_name}"
                st.error(error_msg)
                errors.append(error_msg)
                break
            except Exception as e:
                error_msg = f"実行エラー: {e}"
                st.error(error_msg)
                errors.append(error_msg)
                break
        
        # 最終結果をコピー
        if current_input.exists() and current_input != input_path:
            import shutil
            shutil.copy(current_input, output_path)
        
        # 結果表示
        if output_path.exists() and not errors:
            st.success("✅ 処理が完了しました！")
            
            # 結果プレビュー
            st.subheader("📋 処理結果")
            
            col1, col2 = st.columns(2)
            with col1:
                show_output_preview = st.checkbox("出力ファイルをプレビュー", value=False)
                if show_output_preview:
                    st.code(output_path.read_text(), language="xml")
            
            with col2:
                # ダウンロードボタン
                st.download_button(
                    label="📥 処理済みXMLをダウンロード",
                    data=output_path.read_bytes(),
                    file_name=f"{Path(uploaded_file.name).stem}-final.xml",
                    mime="application/xml",
                    use_container_width=True
                )
        else:
            st.error("❌ 処理に失敗しました")
            if errors:
                st.error("エラー詳細:")
                for error in errors:
                    st.code(error)
        
        st.session_state.processing = False
```

### 機能拡張版（検証機能付き）

```python
# app_advanced.py
import streamlit as st
import subprocess
from pathlib import Path
import tempfile
import os
import sys
import json

# ... (上記の基本実装) ...

def run_validation(input_path, output_path, script_dir):
    """検証スクリプトを実行"""
    validation_script = script_dir / "validate_xml.py"
    compare_script = script_dir / "compare_xml_text_content.py"
    
    results = {}
    
    # 構文検証
    if validation_script.exists():
        try:
            result = subprocess.run(
                [sys.executable, str(validation_script), str(input_path)],
                capture_output=True,
                text=True,
                timeout=60
            )
            results['parse_validation'] = {
                'success': result.returncode == 0,
                'output': result.stdout
            }
        except Exception as e:
            results['parse_validation'] = {
                'success': False,
                'error': str(e)
            }
    
    # テキスト内容検証
    if compare_script.exists() and output_path.exists():
        try:
            result = subprocess.run(
                [sys.executable, str(compare_script), str(input_path), str(output_path)],
                capture_output=True,
                text=True,
                timeout=60
            )
            results['content_validation'] = {
                'success': result.returncode == 0,
                'output': result.stdout
            }
        except Exception as e:
            results['content_validation'] = {
                'success': False,
                'error': str(e)
            }
    
    return results

# 処理関数に検証を追加
def process_file_with_validation(uploaded_file, selected_scripts):
    """検証機能付きファイル処理"""
    # ... (基本処理) ...
    
    # 検証実行
    if output_path.exists():
        st.subheader("🔍 検証結果")
        
        validation_results = run_validation(input_path, output_path, script_dir)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**構文検証**")
            if 'parse_validation' in validation_results:
                if validation_results['parse_validation']['success']:
                    st.success("✅ XML構文は正しいです")
                else:
                    st.error("❌ XML構文エラーが検出されました")
                    st.code(validation_results['parse_validation'].get('output', ''))
        
        with col2:
            st.write("**テキスト内容検証**")
            if 'content_validation' in validation_results:
                if validation_results['content_validation']['success']:
                    st.success("✅ テキスト内容が一致しています")
                else:
                    st.warning("⚠️ テキスト内容に差異があります")
                    st.code(validation_results['content_validation'].get('output', ''))
```

### バッチ処理対応版

```python
# app_batch.py
import streamlit as st
from pathlib import Path
import tempfile
import zipfile

def process_batch_files(uploaded_files, selected_scripts):
    """複数ファイルの一括処理"""
    script_dir = Path(__file__).parent.parent / "scripts"
    
    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, uploaded_file in enumerate(uploaded_files):
        status_text.text(f"処理中 ({i+1}/{len(uploaded_files)}): {uploaded_file.name}")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / uploaded_file.name
            output_path = Path(tmpdir) / f"{Path(uploaded_file.name).stem}-final.xml"
            
            input_path.write_bytes(uploaded_file.read())
            
            # パイプライン実行
            success = run_pipeline(input_path, output_path, selected_scripts, script_dir)
            
            if success and output_path.exists():
                results.append({
                    'name': uploaded_file.name,
                    'output': output_path.read_bytes(),
                    'success': True
                })
            else:
                results.append({
                    'name': uploaded_file.name,
                    'success': False
                })
        
        progress_bar.progress((i + 1) / len(uploaded_files))
    
    # 結果表示
    st.success(f"✅ {len([r for r in results if r['success']])}/{len(results)} ファイルの処理が完了しました")
    
    # ZIPファイルとしてダウンロード
    if results:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_zip:
            with zipfile.ZipFile(tmp_zip.name, 'w') as zipf:
                for result in results:
                    if result['success']:
                        zipf.writestr(result['name'], result['output'])
            
            st.download_button(
                label="📦 すべての結果をZIPでダウンロード",
                data=Path(tmp_zip.name).read_bytes(),
                file_name="processed_xml_files.zip",
                mime="application/zip"
            )
```

---

## Flask実装例

### 基本実装

```python
# app.py
from flask import Flask, request, render_template, send_file, jsonify
import subprocess
import tempfile
from pathlib import Path
import os
import sys

app = Flask(__name__)

AVAILABLE_SCRIPTS = [
    "preprocess_non_first_sentence_to_list.py",
    "convert_article_focused.py",
    # ... (他のスクリプト)
]

@app.route('/')
def index():
    return render_template('index.html', scripts=AVAILABLE_SCRIPTS)

@app.route('/process', methods=['POST'])
def process_xml():
    if 'xml_file' not in request.files:
        return jsonify({'error': 'ファイルがアップロードされていません'}), 400
    
    file = request.files['xml_file']
    selected_scripts = request.form.getlist('scripts')
    
    if not selected_scripts:
        return jsonify({'error': 'スクリプトが選択されていません'}), 400
    
    script_dir = Path(__file__).parent.parent / "scripts"
    
    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = Path(tmpdir) / file.filename
        output_path = Path(tmpdir) / f"{Path(file.filename).stem}-final.xml"
        
        # ファイル保存
        file.save(str(input_path))
        
        # パイプライン実行
        current_input = input_path
        for script_name in selected_scripts:
            script_path = script_dir / script_name
            step_output = Path(tmpdir) / f"step_{script_name.replace('.py', '.xml')}"
            
            result = subprocess.run(
                [sys.executable, str(script_path), str(current_input), str(step_output)],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return jsonify({'error': f'{script_name}の実行に失敗しました', 'details': result.stderr}), 500
            
            current_input = step_output
        
        # 最終結果をコピー
        import shutil
        shutil.copy(current_input, output_path)
        
        # ダウンロード
        return send_file(
            str(output_path),
            as_attachment=True,
            download_name=f"{Path(file.filename).stem}-final.xml"
        )

if __name__ == '__main__':
    app.run(debug=True)
```

### HTMLテンプレート

```html
<!-- templates/index.html -->
<!DOCTYPE html>
<html>
<head>
    <title>XML変換パイプライン</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; }
        .form-group { margin: 20px 0; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        select[multiple] { width: 100%; height: 200px; }
        button { background: #007bff; color: white; padding: 10px 20px; border: none; cursor: pointer; }
        button:hover { background: #0056b3; }
    </style>
</head>
<body>
    <h1>XML変換パイプライン処理システム</h1>
    
    <form method="POST" action="/process" enctype="multipart/form-data">
        <div class="form-group">
            <label>XMLファイルを選択:</label>
            <input type="file" name="xml_file" accept=".xml" required>
        </div>
        
        <div class="form-group">
            <label>実行するスクリプトを選択（Ctrl+クリックで複数選択）:</label>
            <select name="scripts" multiple required>
                {% for script in scripts %}
                <option value="{{ script }}" selected>{{ script }}</option>
                {% endfor %}
            </select>
        </div>
        
        <button type="submit">処理開始</button>
    </form>
</body>
</html>
```

---

## FastAPI実装例

### バックエンドAPI

```python
# main.py
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
from typing import List
import subprocess
import tempfile
from pathlib import Path
import sys

app = FastAPI()

AVAILABLE_SCRIPTS = [
    "preprocess_non_first_sentence_to_list.py",
    "convert_article_focused.py",
    # ... (他のスクリプト)
]

@app.get("/")
async def root():
    return {"message": "XML変換パイプラインAPI", "scripts": AVAILABLE_SCRIPTS}

@app.post("/api/process")
async def process_xml(
    file: UploadFile = File(...),
    scripts: List[str] = Form(...)
):
    script_dir = Path(__file__).parent.parent / "scripts"
    
    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = Path(tmpdir) / file.filename
        output_path = Path(tmpdir) / f"{Path(file.filename).stem}-final.xml"
        
        # ファイル保存
        with open(input_path, 'wb') as f:
            content = await file.read()
            f.write(content)
        
        # パイプライン実行
        current_input = input_path
        for script_name in scripts:
            script_path = script_dir / script_name
            step_output = Path(tmpdir) / f"step_{script_name.replace('.py', '.xml')}"
            
            result = subprocess.run(
                [sys.executable, str(script_path), str(current_input), str(step_output)],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return {"error": f"{script_name}の実行に失敗しました", "details": result.stderr}
            
            current_input = step_output
        
        # 最終結果をコピー
        import shutil
        shutil.copy(current_input, output_path)
        
        return FileResponse(
            str(output_path),
            media_type="application/xml",
            filename=f"{Path(file.filename).stem}-final.xml"
        )
```

### フロントエンド（React例）

```jsx
// App.jsx
import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [file, setFile] = useState(null);
  const [selectedScripts, setSelectedScripts] = useState([]);
  const [processing, setProcessing] = useState(false);
  const [downloadUrl, setDownloadUrl] = useState(null);

  const availableScripts = [
    "preprocess_non_first_sentence_to_list.py",
    "convert_article_focused.py",
    // ... (他のスクリプト)
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setProcessing(true);

    const formData = new FormData();
    formData.append('file', file);
    selectedScripts.forEach(script => {
      formData.append('scripts', script);
    });

    try {
      const response = await axios.post('/api/process', formData, {
        responseType: 'blob',
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      setDownloadUrl(url);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div>
      <h1>XML変換パイプライン</h1>
      <form onSubmit={handleSubmit}>
        <div>
          <label>XMLファイル:</label>
          <input type="file" accept=".xml" onChange={(e) => setFile(e.target.files[0])} />
        </div>
        <div>
          <label>実行スクリプト:</label>
          <select multiple value={selectedScripts} onChange={(e) => setSelectedScripts([...e.target.selectedOptions].map(o => o.value))}>
            {availableScripts.map(script => (
              <option key={script} value={script}>{script}</option>
            ))}
          </select>
        </div>
        <button type="submit" disabled={processing || !file || selectedScripts.length === 0}>
          {processing ? '処理中...' : '処理開始'}
        </button>
      </form>
      {downloadUrl && (
        <a href={downloadUrl} download>ダウンロード</a>
      )}
    </div>
  );
}

export default App;
```

---

## 共通ユーティリティ関数

### パイプライン実行関数

```python
# utils/pipeline.py
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

def run_pipeline(
    input_path: Path,
    output_path: Path,
    scripts: List[str],
    script_dir: Path,
    timeout: int = 300
) -> tuple[bool, Optional[str]]:
    """
    パイプラインを実行
    
    Returns:
        (success: bool, error_message: Optional[str])
    """
    current_input = input_path
    
    for script_name in scripts:
        script_path = script_dir / script_name
        
        if not script_path.exists():
            return False, f"スクリプトが見つかりません: {script_name}"
        
        # 中間出力ファイル
        step_output = script_dir.parent / "temp" / f"step_{script_name.replace('.py', '.xml')}"
        step_output.parent.mkdir(exist_ok=True)
        
        # スクリプト実行
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

### 検証関数

```python
# utils/validation.py
import subprocess
import sys
from pathlib import Path
from typing import Dict

def validate_xml(input_path: Path, output_path: Path, script_dir: Path) -> Dict:
    """XMLファイルの検証を実行"""
    validation_script = script_dir / "validate_xml.py"
    compare_script = script_dir / "compare_xml_text_content.py"
    
    results = {}
    
    # 構文検証
    if validation_script.exists():
        try:
            result = subprocess.run(
                [sys.executable, str(validation_script), str(input_path)],
                capture_output=True,
                text=True,
                timeout=60
            )
            results['parse_validation'] = {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr if result.returncode != 0 else None
            }
        except Exception as e:
            results['parse_validation'] = {
                'success': False,
                'error': str(e)
            }
    
    # テキスト内容検証
    if compare_script.exists() and output_path.exists():
        try:
            result = subprocess.run(
                [sys.executable, str(compare_script), str(input_path), str(output_path)],
                capture_output=True,
                text=True,
                timeout=60
            )
            results['content_validation'] = {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr if result.returncode != 0 else None
            }
        except Exception as e:
            results['content_validation'] = {
                'success': False,
                'error': str(e)
            }
    
    return results
```

---

## デプロイ設定例

### Streamlit Cloud用設定

```toml
# .streamlit/config.toml
[server]
port = 8501
enableCORS = false
enableXsrfProtection = true

[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"
```

### Docker設定（Streamlit）

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# 依存関係のインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードのコピー
COPY . .

# Streamlitの実行
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

```txt
# requirements.txt
streamlit>=1.28.0
lxml>=4.9.0
```

### Docker Compose設定

```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./scripts:/app/scripts
      - ./input:/app/input
      - ./output:/app/output
    environment:
      - PYTHONUNBUFFERED=1
```

---

**最終更新**: 2025年1月

