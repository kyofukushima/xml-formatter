# XML変換パイプライン処理システム Webアプリ開発ガイド

## 概要

本プロジェクトは、XML変換パイプライン処理システムをWebアプリケーション（Streamlitベース）として提供するための開発リポジトリです。

---

## クイックスタート

### 1. 開発環境のセットアップ

```bash
# 仮想環境の作成
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# または
venv\Scripts\activate  # Windows

# 依存関係のインストール
pip install -r requirements.txt

# Streamlitアプリの起動
streamlit run app.py
```

詳細は [`docs/development/development_setup_guide.md`](development_setup_guide.md) を参照してください。

---

## プロジェクト構造

```
kouzou1_xml_app/
├── app.py                    # Streamlitアプリのメインファイル
├── pages/                    # マルチページアプリ（オプション）
├── utils/                    # ユーティリティ関数
├── components/               # 再利用可能なコンポーネント（オプション）
├── scripts/                  # 既存の変換スクリプト
├── input/                    # 入力ファイル用
├── output/                   # 出力ファイル用
├── docs/                     # ドキュメント
│   ├── development/          # 開発用ドキュメント
│   │   ├── development_setup_guide.md
│   │   ├── development_guide.md
│   │   ├── implementation_plan.md
│   │   └── README.md
│   ├── functional_requirements_specification.md
│   └── ...
├── requirements.txt          # 依存関係
└── README.md                # プロジェクト説明
```

---

## ドキュメント一覧

### 開発者向けドキュメント

- **[開発環境セットアップガイド](development_setup_guide.md)**
  - 開発環境のセットアップ手順
  - 必要なライブラリのインストール
  - トラブルシューティング

- **[開発ガイド](development_guide.md)**
  - 実装パターンとベストプラクティス
  - ユーティリティ関数の実装例
  - テスト方法

- **[実装計画書](implementation_plan.md)**
  - 実装フェーズの詳細
  - タスク一覧とスケジュール
  - リスク管理

### 機能要件・設計ドキュメント

- **[機能要件定義書](../functional_requirements_specification.md)**
  - 全機能の詳細仕様
  - ユーザーストーリー
  - 非機能要件

- **[アーキテクチャ比較資料](../web_app_architecture_comparison.md)**
  - フレームワーク比較
  - 推奨アプローチ

- **[実装例集](../web_app_implementation_examples.md)**
  - Streamlit実装例
  - コードサンプル

- **[ラベル設定ライブラリ推奨](../label_config_libraries_recommendation.md)**
  - ラベル設定機能の実装に必要なライブラリ
  - 実装例

---

## 開発の流れ

### 1. 開発環境のセットアップ

```bash
# 開発環境セットアップガイドを参照
# docs/development/development_setup_guide.md
```

### 2. 機能の実装

```bash
# 実装計画書を参照
# docs/development/implementation_plan.md

# 開発ガイドを参照
# docs/development/development_guide.md
```

### 3. テスト

```bash
# テストの実行
pytest tests/

# カバレッジの確認
pytest --cov=utils tests/
```

### 4. 動作確認

```bash
# Streamlitアプリの起動
streamlit run app.py
```

---

## 実装の優先順位

### Phase 1: 基本機能（2-3週間）

1. **基本機能**（FR-001〜FR-006）
   - XMLファイルのアップロード
   - 変換スクリプトの選択
   - パイプライン処理の実行
   - 処理済みXMLファイルのダウンロード
   - 処理進捗の表示
   - エラーメッセージの表示

2. **検証機能**（FR-007〜FR-009）
   - 構文検証の実行
   - テキスト内容検証の実行
   - 検証レポートの表示

3. **ラベル設定機能**（FR-023〜FR-027, FR-029）
   - ブーリアン型パラメーターの簡易設定
   - ラベル設定の表示・編集・保存
   - ラベル設定のインポート/エクスポート
   - ラベル設定のバリデーション

4. **オプション機能**（FR-010, FR-011）
   - XMLファイルのプレビュー
   - 中間ファイルのダウンロード

詳細は [`docs/development/implementation_plan.md`](implementation_plan.md) を参照してください。

---

## 必要なライブラリ

### 必須

- `streamlit>=1.28.0`: Webアプリフレームワーク
- `lxml>=4.9.0`: XML処理（既存）

### 推奨

- `streamlit-json-editor>=0.1.0`: JSONエディタ
- `jsonschema>=4.17.0`: JSONスキーマバリデーション

### 開発用（オプション）

- `black>=23.0.0`: コードフォーマッター
- `flake8>=6.0.0`: リンター
- `pytest>=7.0.0`: テストフレームワーク

インストール:

```bash
pip install -r requirements.txt
```

---

## コーディング規約

### Python

- **PEP 8**: Pythonコーディング規約に準拠
- **型ヒント**: 関数の引数と戻り値に型ヒントを付ける
- **docstring**: 関数にはdocstringを記述

### Streamlit

- **セッション状態**: `st.session_state`を使用して状態を管理
- **エラーハンドリング**: 適切なエラーメッセージを表示
- **進捗表示**: 長時間処理には進捗バーを表示

---

## テスト

### 単体テスト

```bash
# すべてのテストを実行
pytest tests/

# 特定のテストファイルを実行
pytest tests/test_pipeline.py

# カバレッジを取得
pytest --cov=utils tests/
```

### 統合テスト

```bash
# Streamlitアプリの動作確認
streamlit run app.py
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

```bash
# ビルド
docker build -t xml-pipeline-app .

# 実行
docker run -p 8501:8501 xml-pipeline-app
```

---

## トラブルシューティング

よくある問題と解決方法は [`development_setup_guide.md`](development_setup_guide.md) の「トラブルシューティング」セクションを参照してください。

---

## 参考資料

- [Streamlit公式ドキュメント](https://docs.streamlit.io/)
- [機能要件定義書](../functional_requirements_specification.md)
- [開発環境セットアップガイド](development_setup_guide.md)
- [開発ガイド](development_guide.md)
- [実装計画書](implementation_plan.md)

---

## ライセンス

（プロジェクトのライセンス情報を記載）

---

**最終更新**: 2025年1月

