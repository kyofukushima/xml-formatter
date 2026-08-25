# 15_branch_number_split: 枝番付き第○ラベルでのArticle分割

## 目的

ArticleTitleが「第一」のArticle内に、Column1が「第一の一の二」（3分割）や
「第一の二」（2分割）のListが続く場合、それぞれが**後続する並列のArticle要素の
ArticleTitle**として分割されることを検証する。

実例: 告示 XML（H18厚労省告示107号 掲示事項等）の「第一の一の二」「第一の二」
「第十三の二の二」等の枝番付き節見出し。

## 検証内容

1. 「第一の一の二」「第一の二」のListがArticle境界として認識され、
   元のArticle（第一）と同格の並列Articleに分割される
2. 分割前のList（「一」等の通常ラベル）は元のArticleに残る
3. 分割後のArticleのNum属性がタイトル由来のコーパス準拠枝番形式で採番される
   （「第一の一の二」→ Num="1_1_2"、「第一の二」→ Num="1_2"）

## 関連設定

- `scripts/convert_article_focused.py` の `article_boundary_pattern`
  （枝番付き第○ラベル対応の拡張）
- `scripts/utils/renumber_utils.py` の `title_to_num`（枝番形式 Num の導出）
