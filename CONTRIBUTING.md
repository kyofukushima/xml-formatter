# コントリビューションガイド

このプロジェクトへの貢献をありがとうございます。このドキュメントでは、開発・運用・保守のためのGitHub活用方法について説明します。

## ブランチ戦略

このプロジェクトでは、**Git Flow**に基づいたブランチ戦略を採用しています。

### ブランチの種類

- **`main`**: 本番環境用の安定版ブランチ
- **`feature/*`**: 新機能開発用ブランチ（例: `feature/reverse-conversion`）
- **`bugfix/*`**: バグ修正用ブランチ（例: `bugfix/fix-validation-error`）
- **`hotfix/*`**: 緊急修正用ブランチ（例: `hotfix/critical-security-fix`）

### ブランチ命名規則

- 機能追加: `feature/機能名`（例: `feature/reverse-conversion`）
- バグ修正: `bugfix/修正内容`（例: `bugfix/fix-xml-parsing`）
- 緊急修正: `hotfix/修正内容`（例: `hotfix/fix-security-issue`）

## 開発フロー

### 1. 機能開発の流れ

```bash
# 1. mainブランチから最新の変更を取得
git checkout main
git pull origin main

# 2. 機能ブランチを作成
git checkout -b feature/機能名

# 3. 変更を加える
# ... コードを編集 ...

# 4. 変更をステージング
git add .

# 5. コミット（適切なメッセージを付ける）
git commit -m "feat: 機能の説明"

# 6. リモートにプッシュ
git push -u origin feature/機能名

# 7. GitHubでプルリクエストを作成
# https://github.com/kyofukushima/xml-formatter/pulls
```

### 2. コミットメッセージの規約

[Conventional Commits](https://www.conventionalcommits.org/)に準拠します。

```
<type>: <subject>

<body>

<footer>
```

#### Type（必須）

- `feat`: 新機能の追加
- `fix`: バグ修正
- `docs`: ドキュメントの変更
- `style`: コードスタイルの変更（動作に影響しない）
- `refactor`: リファクタリング
- `test`: テストの追加・変更
- `chore`: ビルドプロセスやツールの変更

#### 例

```
feat: 逆変換機能をWebアプリに追加

- 逆変換ページを追加
- 逆変換パイプライン処理ユーティリティを追加
- メインページのナビゲーションに逆変換リンクを追加
```

### 3. プルリクエスト（PR）の作成

1. **GitHubでプルリクエストを作成**
   - ブランチをプッシュ後、GitHubの通知リンクから作成
   - または、GitHubの「Pull requests」タブから作成

2. **PRのタイトルと説明**
   - タイトル: 変更内容を簡潔に記述
   - 説明: 変更の目的、変更内容、テスト方法を記述

3. **レビュー待ち**
   - 他のメンバーにレビューを依頼
   - フィードバックに基づいて修正

4. **マージ**
   - レビューが承認されたら、mainブランチにマージ
   - マージ後、機能ブランチは削除可能

### 4. マージ後の作業

```bash
# mainブランチに切り替え
git checkout main

# 最新の変更を取得
git pull origin main

# 不要になったブランチを削除
git branch -d feature/機能名
```

## ベストプラクティス

### ✅ 推奨事項

1. **小さなコミットを心がける**
   - 1つのコミットは1つの変更に集中
   - 関連する変更はまとめる

2. **mainブランチに直接コミットしない**
   - 必ず機能ブランチを作成してから作業
   - プルリクエストを通じてマージ

3. **定期的にmainブランチと同期**
   ```bash
   git checkout feature/機能名
   git merge main  # または git rebase main
   ```

4. **テストを実行してからコミット**
   - コードの動作確認
   - リンターエラーの確認

5. **意味のあるコミットメッセージ**
   - 何を変更したか、なぜ変更したかを明確に

### ❌ 避けるべきこと

1. **mainブランチへの直接push**
   - コードレビューなしでのマージを避ける

2. **大きなコミット**
   - 複数の変更を1つのコミットにまとめない

3. **意味のないコミットメッセージ**
   - 「修正」「更新」などの曖昧なメッセージを避ける

4. **コミット前の動作確認不足**
   - テストや検証をスキップしない

## トラブルシューティング

### コンフリクトが発生した場合

```bash
# mainブランチの最新を取得
git checkout main
git pull origin main

# 機能ブランチに戻る
git checkout feature/機能名

# mainブランチをマージ
git merge main

# コンフリクトを解決
# ... ファイルを編集 ...

# 解決後、コミット
git add .
git commit -m "merge: mainブランチと統合"
```

### 間違ったブランチにコミットしてしまった場合

```bash
# 最新のコミットを取り消す（変更は保持）
git reset --soft HEAD~1

# 正しいブランチに切り替え
git checkout feature/正しいブランチ名

# 変更をコミット
git commit -m "feat: 変更内容"
```

## リリース管理

### バージョン管理

- セマンティックバージョニング（SemVer）に準拠
- 形式: `MAJOR.MINOR.PATCH`（例: `1.3.0`）

### タグ付け

重要なリリースにはタグを付けます：

```bash
# タグを作成
git tag -a v1.3.0 -m "リリース v1.3.0: 逆変換機能追加"

# タグをプッシュ
git push origin v1.3.0
```

## 質問・サポート

問題が発生した場合や質問がある場合は、GitHubのIssuesで報告してください。

---

**重要**: このガイドラインに従うことで、プロジェクトの品質と保守性が向上します。ご協力ありがとうございます！
