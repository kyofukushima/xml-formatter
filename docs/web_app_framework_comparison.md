# Webアプリ化フレームワーク比較検討

## 概要

XML変換パイプライン処理システムをWebアプリ化する際の、DjangoとStreamlitの比較検討ドキュメントです。

## 要件

### 必須機能
- XMLファイルのアップロード
- 処理後XMLのダウンロード
- 利用するスクリプトの選択（18個の変換スクリプトから選択）

### オプション機能
- 処理後XMLのプレビュー
- 処理進捗の表示
- エラーハンドリングとログ表示

## フレームワーク比較

### 1. Streamlit

#### 概要
Pythonスクリプトを簡単にWebアプリ化できるフレームワーク。データサイエンスや機械学習のプロトタイプ開発に最適。

#### メリット

**開発速度**
- ✅ **極めて高速な開発**: 数時間でプロトタイプが完成可能
- ✅ **最小限のコード**: HTML/CSS/JavaScriptの知識不要
- ✅ **インタラクティブなUI**: ファイルアップロード、ダウンロード、プレビューが簡単に実装可能
- ✅ **リアルタイム更新**: `st.rerun()`で簡単に状態更新

**機能実装の容易さ**
- ✅ **ファイルアップロード**: `st.file_uploader()`で1行で実装
- ✅ **ファイルダウンロード**: `st.download_button()`で簡単
- ✅ **XMLプレビュー**: `st.code()`や`st.text()`で簡単に表示可能
- ✅ **進捗表示**: `st.progress()`と`st.status()`で視覚的な進捗表示が可能
- ✅ **エラー表示**: `st.error()`で分かりやすいエラー表示

**既存コードとの統合**
- ✅ **既存スクリプトの再利用**: 現在のPythonスクリプトをそのまま呼び出し可能
- ✅ **シェルスクリプトの統合**: `subprocess`で`run_pipeline.sh`を呼び出し可能
- ✅ **最小限の変更**: 既存のロジックをほぼそのまま使用可能

**デプロイ**
- ✅ **Streamlit Cloud**: 無料で簡単にデプロイ可能
- ✅ **Docker対応**: コンテナ化が容易
- ✅ **軽量**: リソース消費が少ない

#### デメリット

**機能制限**
- ❌ **認証機能**: 標準では認証機能が弱い（サードパーティライブラリが必要）
- ❌ **複雑なルーティング**: ページ遷移が制限的
- ❌ **カスタマイズ性**: UIの自由度がDjangoより低い
- ❌ **セッション管理**: 複雑なセッション管理には不向き

**スケーラビリティ**
- ❌ **同時実行**: 大量の同時リクエストには不向き
- ❌ **バックグラウンド処理**: 長時間処理の非同期実行が複雑

**本番環境**
- ❌ **エンタープライズ機能**: ログ、モニタリング、セキュリティ機能が限定的

#### 実装イメージ

```python
import streamlit as st
import subprocess
from pathlib import Path
import tempfile

st.title("XML変換パイプライン")

# スクリプト選択
selected_scripts = st.multiselect(
    "処理するスクリプトを選択",
    options=["convert_article_focused.py", "convert_paragraph_step1.py", ...],
    default=["convert_article_focused.py"]
)

# ファイルアップロード
uploaded_file = st.file_uploader("XMLファイルをアップロード", type=["xml"])

if uploaded_file and st.button("処理開始"):
    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = Path(tmpdir) / uploaded_file.name
        output_path = Path(tmpdir) / f"{uploaded_file.stem}-final.xml"
        
        # ファイル保存
        input_path.write_bytes(uploaded_file.read())
        
        # 進捗表示
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # スクリプト実行
        for i, script in enumerate(selected_scripts):
            status_text.text(f"実行中: {script}")
            subprocess.run(["python3", script, str(input_path), str(output_path)])
            progress_bar.progress((i + 1) / len(selected_scripts))
        
        # プレビュー
        if output_path.exists():
            st.subheader("処理結果プレビュー")
            st.code(output_path.read_text(), language="xml")
            
            # ダウンロード
            st.download_button(
                "ダウンロード",
                data=output_path.read_bytes(),
                file_name=output_path.name,
                mime="application/xml"
            )
```

---

### 2. Django

#### 概要
フル機能のWebフレームワーク。エンタープライズレベルのアプリケーション開発に最適。

#### メリット

**機能性**
- ✅ **認証・認可**: 強力な認証システムが標準装備
- ✅ **管理画面**: 自動生成される管理画面（Django Admin）
- ✅ **ORM**: データベース操作が容易（履歴管理などに有用）
- ✅ **セキュリティ**: CSRF保護、XSS対策などが標準装備

**スケーラビリティ**
- ✅ **非同期処理**: Celery等を使ったバックグラウンド処理が容易
- ✅ **キャッシング**: Redis等を使ったキャッシュ機能
- ✅ **同時実行**: 大量のリクエストに対応可能
- ✅ **マイクロサービス**: API化が容易（Django REST Framework）

**拡張性**
- ✅ **プラグイン**: 豊富なサードパーティパッケージ
- ✅ **カスタマイズ性**: UI/UXを完全にカスタマイズ可能
- ✅ **ルーティング**: 複雑なURL構造に対応
- ✅ **テンプレート**: 柔軟なテンプレートシステム

**本番環境**
- ✅ **ログ**: 詳細なログ機能
- ✅ **モニタリング**: パフォーマンス監視が容易
- ✅ **デプロイ**: WSGIサーバー（Gunicorn等）での本番運用が標準的

#### デメリット

**開発コスト**
- ❌ **学習曲線**: 学習コストが高い
- ❌ **開発時間**: 初期セットアップに時間がかかる
- ❌ **ボイラープレート**: 設定ファイルが多く、コード量が多い
- ❌ **複雑性**: シンプルなアプリには過剰な機能

**実装の複雑さ**
- ❌ **ファイルアップロード**: `FileField`や`FileSystemStorage`の設定が必要
- ❌ **非同期処理**: Celery等のセットアップが必要
- ❌ **進捗表示**: WebSocketやServer-Sent Eventsの実装が必要
- ❌ **プレビュー**: テンプレートとビューの実装が必要

**リソース**
- ❌ **メモリ消費**: Streamlitより多くのリソースを消費
- ❌ **依存関係**: 多くのパッケージが必要

#### 実装イメージ

```python
# views.py
from django.shortcuts import render
from django.http import FileResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import subprocess
import tempfile
import json

def upload_xml(request):
    if request.method == 'POST':
        uploaded_file = request.FILES['xml_file']
        selected_scripts = json.loads(request.POST['scripts'])
        
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = os.path.join(tmpdir, uploaded_file.name)
            output_path = os.path.join(tmpdir, f"{uploaded_file.name}-final.xml")
            
            # ファイル保存
            with open(input_path, 'wb') as f:
                for chunk in uploaded_file.chunks():
                    f.write(chunk)
            
            # スクリプト実行
            for script in selected_scripts:
                subprocess.run(["python3", script, input_path, output_path])
            
            # レスポンス
            return FileResponse(
                open(output_path, 'rb'),
                as_attachment=True,
                filename=output_path.name
            )
    
    return render(request, 'upload.html')
```

```html
<!-- templates/upload.html -->
<form method="post" enctype="multipart/form-data">
    {% csrf_token %}
    <input type="file" name="xml_file" accept=".xml">
    <select name="scripts" multiple>
        <option value="convert_article_focused.py">Article処理</option>
        <!-- ... -->
    </select>
    <button type="submit">処理開始</button>
</form>
```

---

## 比較表

| 項目 | Streamlit | Django |
|------|-----------|--------|
| **開発速度** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **学習コスト** | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **コード量** | 少ない（50-100行） | 多い（500-1000行以上） |
| **ファイルアップロード** | 簡単（1行） | 中程度（設定必要） |
| **ダウンロード** | 簡単（1行） | 中程度 |
| **プレビュー** | 簡単 | 中程度 |
| **進捗表示** | 簡単 | 複雑（WebSocket等） |
| **認証機能** | 弱い | 強い |
| **スケーラビリティ** | 低い | 高い |
| **カスタマイズ性** | 低い | 高い |
| **本番運用** | 中程度 | 高い |
| **既存コード統合** | 容易 | 中程度 |
| **デプロイ** | 簡単（Streamlit Cloud） | 中程度（設定必要） |

---

## 推奨事項

### Streamlitを推奨する場合

✅ **以下の条件に当てはまる場合**
- 迅速なプロトタイプ開発が必要
- 内部ツールとして使用（認証不要）
- 同時ユーザー数が少ない（10人以下）
- 既存のPythonスクリプトを最小限の変更で統合したい
- 開発リソースが限られている
- シンプルなUIで十分

**このプロジェクトの場合**: 
- XML変換パイプラインは内部ツールとして使用される可能性が高い
- 既存の18個のスクリプトをそのまま利用したい
- 迅速な開発が求められる
- **→ Streamlitが最適**

### Djangoを推奨する場合

✅ **以下の条件に当てはまる場合**
- エンタープライズレベルのアプリケーションが必要
- 認証・認可機能が必須
- 大量の同時ユーザーに対応が必要
- 処理履歴の管理が必要
- 複雑なUI/UXが必要
- 長期的な拡張性が重要

---

## 実装推奨アプローチ

### Phase 1: Streamlitでプロトタイプ（推奨）

1. **短期間でプロトタイプを作成**（1-2週間）
   - ファイルアップロード/ダウンロード機能
   - スクリプト選択機能
   - 基本的なプレビュー機能

2. **ユーザーフィードバックを収集**
   - 実際の使用感を確認
   - 必要な機能を洗い出し

3. **必要に応じてDjangoに移行**
   - 認証が必要になった場合
   - スケーラビリティが必要になった場合
   - より複雑な機能が必要になった場合

### Phase 2: 機能拡張（必要に応じて）

**Streamlitで追加可能な機能**
- 処理履歴の表示（SQLiteで簡単に実装可能）
- バッチ処理（複数ファイルの一括処理）
- 設定の保存（`st.session_state`で実装可能）
- エラーログの表示

**Djangoが必要になる機能**
- ユーザー認証・権限管理
- 処理履歴の詳細管理
- 非同期処理（Celery）
- API化（他システムとの連携）

---

## 実装例（Streamlit）

### 最小実装例

```python
import streamlit as st
import subprocess
from pathlib import Path
import tempfile
import os

st.set_page_config(page_title="XML変換パイプライン", layout="wide")

st.title("XML変換パイプライン処理システム")

# サイドバーでスクリプト選択
st.sidebar.header("処理オプション")

# 利用可能なスクリプトリスト
available_scripts = [
    "convert_article_focused.py",
    "convert_paragraph_step1.py",
    "convert_paragraph_step2.py",
    "convert_paragraph_step3.py",
    "convert_paragraph_step4.py",
    "convert_item_step0.py",
    "convert_item_step1.py",
    "convert_subject_item.py",
    "convert_subitem1_step0.py",
    "convert_subitem1_step1.py",
    "convert_subitem2_step0.py",
    "convert_subitem2_step1.py",
    "convert_subitem3_step0.py",
    "convert_subitem3_step1.py",
    "convert_subitem4_step0.py",
    "convert_subitem4_step1.py",
    "convert_subitem5_step0.py",
    "convert_subitem5_step1.py",
]

selected_scripts = st.sidebar.multiselect(
    "実行するスクリプトを選択",
    options=available_scripts,
    default=available_scripts  # デフォルトで全選択
)

# メインエリア
uploaded_file = st.file_uploader(
    "XMLファイルをアップロードしてください",
    type=["xml"],
    help="処理対象のXMLファイルを選択してください"
)

if uploaded_file is not None:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("入力ファイル")
        st.code(uploaded_file.read().decode('utf-8'), language="xml")
        uploaded_file.seek(0)  # ポインタをリセット
    
    if st.button("処理開始", type="primary"):
        script_dir = Path(__file__).parent.parent / "scripts"
        
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / uploaded_file.name
            output_path = Path(tmpdir) / f"{Path(uploaded_file.name).stem}-final.xml"
            
            # 入力ファイルを保存
            input_path.write_bytes(uploaded_file.read())
            
            # 進捗表示
            progress_bar = st.progress(0)
            status_container = st.container()
            
            # 各スクリプトを実行
            current_input = input_path
            for i, script_name in enumerate(selected_scripts):
                script_path = script_dir / script_name
                
                if not script_path.exists():
                    st.error(f"スクリプトが見つかりません: {script_name}")
                    continue
                
                with status_container:
                    st.info(f"実行中: {script_name} ({i+1}/{len(selected_scripts)})")
                
                # 中間出力ファイル
                step_output = Path(tmpdir) / f"step_{i}_{script_name.replace('.py', '.xml')}"
                
                # スクリプト実行
                try:
                    result = subprocess.run(
                        ["python3", str(script_path), str(current_input), str(step_output)],
                        capture_output=True,
                        text=True,
                        timeout=300  # 5分タイムアウト
                    )
                    
                    if result.returncode != 0:
                        st.error(f"エラー: {script_name}")
                        st.code(result.stderr)
                        break
                    
                    current_input = step_output
                    progress_bar.progress((i + 1) / len(selected_scripts))
                    
                except subprocess.TimeoutExpired:
                    st.error(f"タイムアウト: {script_name}")
                    break
                except Exception as e:
                    st.error(f"実行エラー: {e}")
                    break
            
            # 最終結果をコピー
            if current_input.exists() and current_input != input_path:
                import shutil
                shutil.copy(current_input, output_path)
            
            # 結果表示
            if output_path.exists():
                st.success("処理が完了しました！")
                
                with col2:
                    st.subheader("処理結果")
                    
                    # プレビュー
                    if st.checkbox("プレビューを表示"):
                        st.code(output_path.read_text(), language="xml")
                    
                    # ダウンロードボタン
                    st.download_button(
                        label="処理済みXMLをダウンロード",
                        data=output_path.read_bytes(),
                        file_name=f"{Path(uploaded_file.name).stem}-final.xml",
                        mime="application/xml"
                    )
            else:
                st.error("処理に失敗しました")
```

---

## 結論

### このプロジェクトには **Streamlit** を推奨

**理由:**
1. ✅ 開発速度が圧倒的に速い（1-2週間で完成可能）
2. ✅ 既存のPythonスクリプトをそのまま利用可能
3. ✅ 要件（アップロード、ダウンロード、プレビュー、スクリプト選択）を簡単に実装可能
4. ✅ 内部ツールとして使用する場合、認証機能は後から追加可能
5. ✅ 必要に応じて後からDjangoに移行可能

**Djangoを検討すべき場合:**
- 複数ユーザーが同時に使用する必要がある
- 処理履歴を詳細に管理する必要がある
- 認証・権限管理が必須
- 将来的にAPI化が必要

---

## 次のステップ

1. **Streamlitプロトタイプの作成**
   - 上記の実装例をベースに開発
   - 既存スクリプトとの統合テスト

2. **機能追加**
   - エラーハンドリングの強化
   - 処理ログの表示
   - 設定の保存機能

3. **デプロイ**
   - Streamlit Cloudでのデプロイ
   - またはDockerコンテナでのデプロイ

4. **ユーザーフィードバック収集**
   - 実際の使用感を確認
   - 必要な機能を洗い出し

5. **必要に応じてDjango移行**
   - 要件が複雑化した場合
   - エンタープライズ機能が必要になった場合


















