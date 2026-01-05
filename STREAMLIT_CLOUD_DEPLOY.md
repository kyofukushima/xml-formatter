# Streamlit Cloud デプロイガイド

## 必要なファイル

Streamlit Cloudにデプロイする際、以下のファイルが必要です：

### 必須ファイル

1. **`app.py`** ✅
   - メインアプリケーションファイル
   - プロジェクトルートに配置

2. **`requirements.txt`** ✅
   - Python依存パッケージのリスト
   - プロジェクトルートに配置
   - 現在の内容：
     ```
     streamlit>=1.28.0
     jsonschema>=4.17.0
     lxml>=4.9.0
     ```

3. **`.streamlit/config.toml`** ✅（オプション）
   - Streamlit設定ファイル
   - テーマやサーバー設定を定義

### 推奨ファイル

4. **`.gitignore`** ✅
   - Gitで無視するファイルを定義
   - `venv/`、`__pycache__/`、`output/`などを除外

5. **`README.md`** ✅
   - プロジェクトの説明とセットアップ手順

## デプロイ手順

### 1. GitHubリポジトリの準備

```bash
# Gitリポジトリの初期化（まだの場合）
git init

# 必要なファイルをステージング
git add app.py
git add requirements.txt
git add .streamlit/
git add utils/
git add components/
git add pages/
git add scripts/
git add .gitignore
git add README.md

# コミット
git commit -m "Initial commit for Streamlit Cloud"

# GitHubリポジトリを作成し、リモートを追加
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

### 2. Streamlit Cloudでのデプロイ

1. [Streamlit Cloud](https://share.streamlit.io/)にアクセス
2. GitHubアカウントでログイン
3. 「New app」をクリック
4. 以下の情報を入力：
   - **Repository**: 作成したGitHubリポジトリを選択
   - **Branch**: `main`（または使用しているブランチ名）
   - **Main file path**: `app.py`
5. 「Deploy!」をクリック

### 3. デプロイ後の確認

- デプロイが完了すると、アプリのURLが生成されます
- アプリが正常に動作するか確認してください
- エラーが発生した場合は、Streamlit Cloudのログを確認してください

## 注意事項

### ファイルサイズ制限

- Streamlit Cloudにはファイルサイズ制限があります
- 大きなファイル（テストデータ、サンプルXMLなど）は`.gitignore`に追加することを推奨

### 環境変数

- 環境変数が必要な場合は、Streamlit Cloudの設定画面で設定できます
- 現在のアプリでは環境変数は使用していません

### Pythonバージョン

- Streamlit CloudはデフォルトでPython 3.9を使用します
- 特定のバージョンが必要な場合は、`runtime.txt`を作成：
  ```
  python-3.9.18
  ```

### 依存パッケージの更新

- `requirements.txt`を更新した場合、Streamlit Cloudは自動的に再デプロイします
- 手動で再デプロイする場合は、Streamlit Cloudのダッシュボードから実行できます

## トラブルシューティング

### デプロイエラー

1. **依存パッケージのエラー**
   - `requirements.txt`の内容を確認
   - パッケージ名とバージョンが正しいか確認

2. **インポートエラー**
   - ローカルで動作確認：`streamlit run app.py`
   - 相対パスやモジュールのインポートを確認

3. **ファイルが見つからないエラー**
   - `scripts/`、`utils/`、`components/`などのディレクトリがGitHubに含まれているか確認
   - `.gitignore`で除外されていないか確認

### パフォーマンス

- 大きなXMLファイルの処理には時間がかかる場合があります
- タイムアウトエラーが発生する場合は、処理を最適化するか、ファイルサイズを制限してください

## 参考リンク

- [Streamlit Cloud Documentation](https://docs.streamlit.io/streamlit-community-cloud)
- [Streamlit Cloud Deployment Guide](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app)

