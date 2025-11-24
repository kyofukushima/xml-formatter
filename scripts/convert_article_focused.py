#!/usr/bin/env python3
"""
Article要素に特化した階層限定型変換スクリプト

Article処理内容.md のロジックを実装

【主な機能】
1. Article要素の分割: 「第○」パターンで新しいArticleを作成
   - ArticleTitleが「第１」「第２」などの場合、次に「第２」「第３」が出現したら分割
2. ArticleTitleが空の場合: 何も処理しない（そのまま保持）

【処理対象】
- MainProvision以下のArticle要素
- Article分割のみ（List要素はItem特化処理で処理）

【処理しないこと】
- ArticleTitleが空のArticle要素
- Article内のList要素（Item特化処理に委譲）
"""

import xml.etree.ElementTree as ET
import re
import sys
from pathlib import Path
from typing import List, Tuple, Optional
import copy

# utilsディレクトリをインポートパスに追加（親ディレクトリのutils/を参照）
sys.path.insert(0, str(Path(__file__).parent.parent))

# 共通XMLユーティリティをインポート
from utils import save_xml_with_indent, renumber_nums_in_tree


class ArticleFocusedConverter:
    """Article要素に特化した変換クラス（分割のみ）"""
    
    def __init__(self):
        """初期化"""
        # Article境界を示すパターン: 「第○」形式
        # 半角数字、全角数字、漢数字に対応
        self.article_boundary_pattern = r'^第[0-9０-９一二三四五六七八九十百千]+$'
        
        # 統計情報
        self.stats = {
            'articles_total': 0,
            'articles_split': 0,
            'articles_skipped': 0,  # ArticleTitleが空で処理スキップ
            'article_titles_added': 0,  # ArticleTitleを追加した数
        }
    
    def is_article_boundary_label(self, label: str) -> bool:
        """Article境界を示すラベルかを判定
        
        Args:
            label: ラベル文字列
        
        Returns:
            bool: Article境界ラベルならTrue
        """
        if not label:
            return False
        return re.match(self.article_boundary_pattern, label.strip()) is not None
    
    def extract_article_title(self, article: ET.Element) -> Optional[str]:
        """ArticleTitleを抽出
        
        Args:
            article: Article要素
        
        Returns:
            Optional[str]: ArticleTitleのテキスト、存在しないか空ならNone
        """
        article_title_elem = article.find('ArticleTitle')
        if article_title_elem is None:
            return None
        
        title = article_title_elem.text
        if title and title.strip():
            return title.strip()
        
        return None
    
    def find_article_split_point(self, article: ET.Element) -> Optional[Tuple[int, ET.Element, str, str]]:
        """Article内で分割すべき位置を検索
        
        Args:
            article: Article要素
        
        Returns:
            Optional[Tuple[int, ET.Element, str, str]]: 
                (Paragraph内のListのindex, Paragraph要素, 境界ラベル, 境界内容)
                見つからない場合はNone
        """
        current_title = self.extract_article_title(article)
        
        # ArticleTitleが空なら分割しない
        if not current_title:
            return None
        
        # ArticleTitleが「第○」パターンでなければ分割しない
        if not self.is_article_boundary_label(current_title):
            return None
        
        # Article内の全List要素を走査
        for paragraph in article.findall('.//Paragraph'):
            list_elements = list(paragraph.findall('List'))
            
            for i, list_elem in enumerate(list_elements):
                # Column構造を確認
                columns = list_elem.findall('.//Column')
                
                if len(columns) >= 2:
                    # 最初のColumnからラベルを取得
                    first_col = columns[0]
                    sentence = first_col.find('.//Sentence')
                    
                    if sentence is not None and sentence.text:
                        label = sentence.text.strip()
                        
                        # Article境界パターンかチェック
                        if self.is_article_boundary_label(label):
                            # 現在のArticleTitleと異なるかチェック
                            if label != current_title:
                                # 2番目のColumnから内容を取得
                                second_col = columns[1]
                                sentence2 = second_col.find('.//Sentence')
                                content = sentence2.text.strip() if sentence2 is not None and sentence2.text else ''
                                
                                return (i, paragraph, label, content)
        
        return None
    
    def split_article(self, article: ET.Element, split_paragraph: ET.Element, split_index: int, 
                     new_title: str, new_content: str) -> Tuple[ET.Element, ET.Element]:
        """Article要素を分割
        
        Args:
            article: 元のArticle要素
            split_paragraph: 分割点を含むParagraph要素
            split_index: Paragraph内のList要素のインデックス
            new_title: 新しいArticleのタイトル
            new_content: 新しいArticleの最初のParagraphSentenceの内容
        
        Returns:
            Tuple[ET.Element, ET.Element]: (前半のArticle, 後半のArticle)
        """
        # 元のArticleのNum属性を取得
        original_num = article.get('Num', '1')
        
        # 前半のArticleを作成
        first_article = ET.Element('Article', attrib={'Num': original_num})
        
        # 元のArticleのArticleTitleをコピー
        original_title_elem = article.find('ArticleTitle')
        if original_title_elem is not None:
            first_article.append(copy.deepcopy(original_title_elem))
        
        # 後半のArticleを作成
        next_num = str(int(original_num) + 1) if original_num.isdigit() else str(len(self.stats) + 1)
        second_article = ET.Element('Article', attrib={'Num': next_num})
        
        # 新しいArticleTitleを作成
        new_title_elem = ET.SubElement(second_article, 'ArticleTitle')
        new_title_elem.text = new_title
        
        # 分割点より前の要素を前半のArticleに追加
        for child in article:
            if child.tag == 'ArticleTitle' or child.tag == 'ArticleCaption':
                continue  # 既に処理済み
            
            if child == split_paragraph:
                # 分割Paragraphの場合、split_indexより前のList要素のみを含むParagraphを作成
                new_para = ET.Element('Paragraph', attrib=child.attrib)
                
                # ParagraphNum、ParagraphSentenceをコピー
                for sub_child in child:
                    if sub_child.tag in ['ParagraphNum', 'ParagraphSentence', 'ParagraphCaption']:
                        new_para.append(copy.deepcopy(sub_child))
                
                # split_indexより前のList要素をコピー
                list_children = [c for c in child if c.tag == 'List']
                for i, list_elem in enumerate(list_children):
                    if i < split_index:
                        new_para.append(copy.deepcopy(list_elem))
                
                # 他の要素（Item, TableStructなど）もコピー
                for sub_child in child:
                    if sub_child.tag not in ['ParagraphNum', 'ParagraphSentence', 'ParagraphCaption', 'List']:
                        new_para.append(copy.deepcopy(sub_child))
                
                # Only append the paragraph if it has meaningful content
                has_content = any(
                    sub.tag not in ['ParagraphNum', 'ParagraphCaption']
                    for sub in new_para
                )
                if has_content:
                    first_article.append(new_para)
                
                break  # 分割点に到達したので終了
            else:
                first_article.append(copy.deepcopy(child))
        
        # 分割点以降の要素を後半のArticleに追加
        found_split = False
        for child in article:
            if child == split_paragraph:
                found_split = True
                
                # 新しいParagraphを作成（split_index以降のList要素を含む）
                new_para = ET.Element('Paragraph', attrib={'Num': '1'})
                
                # ParagraphNumをコピー（存在する場合）
                original_para_num = split_paragraph.find('ParagraphNum')
                if original_para_num is not None:
                    new_para.append(copy.deepcopy(original_para_num))
                else:
                    # 存在しない場合は空のParagraphNumを作成（スキーマ準拠のため）
                    ET.SubElement(new_para, 'ParagraphNum')
                
                # ParagraphSentence（新しい内容）を作成
                para_sentence = ET.SubElement(new_para, 'ParagraphSentence')
                sentence = ET.SubElement(para_sentence, 'Sentence')
                sentence.text = new_content
                
                # split_index以降のList要素をコピー
                list_children = [c for c in child if c.tag == 'List']
                for i, list_elem in enumerate(list_children):
                    if i > split_index:  # split_index自体はスキップ（既にArticleTitleになっている）
                        new_para.append(copy.deepcopy(list_elem))
                
                # 他の要素もコピー
                for sub_child in child:
                    if sub_child.tag not in ['ParagraphNum', 'ParagraphSentence', 'ParagraphCaption', 'List']:
                        new_para.append(copy.deepcopy(sub_child))
                
                second_article.append(new_para)
            
            elif found_split:
                # 分割点以降の要素をすべてコピー
                second_article.append(copy.deepcopy(child))
        
        self.stats['articles_split'] += 1
        
        return (first_article, second_article)
    
    def ensure_article_title(self, article: ET.Element) -> ET.Element:
        """Article要素にArticleTitleが存在しない場合、空のArticleTitleを追加
        
        Args:
            article: Article要素
        
        Returns:
            ET.Element: ArticleTitleを持つArticle要素
        """
        # ArticleTitle要素が存在するか確認
        article_title_elem = article.find('ArticleTitle')
        
        if article_title_elem is None:
            # ArticleTitleが存在しない場合、先頭に空のArticleTitleを追加
            new_article = ET.Element('Article', attrib=article.attrib)
            
            # 空のArticleTitleを追加
            empty_title = ET.SubElement(new_article, 'ArticleTitle')
            
            # 他の子要素をコピー
            for child in article:
                new_article.append(copy.deepcopy(child))
            
            self.stats['article_titles_added'] += 1
            
            return new_article
        
        return article
    
    def process_article(self, article: ET.Element) -> List[ET.Element]:
        """Article要素を処理（分割が必要な場合は分割）
        
        Args:
            article: Article要素
        
        Returns:
            List[ET.Element]: 処理後のArticle要素のリスト（分割された場合は複数）
        """
        self.stats['articles_total'] += 1
        
        # パターン3: ArticleTitleがない場合は空のArticleTitleを追加
        article = self.ensure_article_title(article)
        
        # ArticleTitleを確認
        article_title = self.extract_article_title(article)
        
        # ArticleTitleが空の場合は何もしない（パターン1）
        if not article_title:
            self.stats['articles_skipped'] += 1
            return [article]
        
        # ArticleTitleが「第○」パターンでない場合も何もしない
        if not self.is_article_boundary_label(article_title):
            return [article]
        
        # パターン2: 分割点を検索
        split_info = self.find_article_split_point(article)
        
        if split_info is None:
            # 分割点が見つからない場合はそのまま
            return [article]
        
        # 分割を実行
        split_index, split_paragraph, new_title, new_content = split_info
        first_article, second_article = self.split_article(
            article, split_paragraph, split_index, new_title, new_content
        )
        
        # 再帰的に処理（後半のArticleにさらに分割点がある可能性）
        result = [first_article]
        result.extend(self.process_article(second_article))
        
        return result
    
    def process_xml(self, input_path: Path, output_path: Path, renumber: bool = True):
        """XMLファイルを処理
        
        Args:
            input_path: 入力XMLファイルのパス
            output_path: 出力XMLファイルのパス
            renumber: Num属性を振り直すかどうか（デフォルト: True）
        """
        tree = ET.parse(input_path)
        root = tree.getroot()

        # Pre-processing step: Wrap direct child Lists of an Article in a new Paragraph
        # This normalizes the structure to ensure the split logic can find them.
        for article in root.findall('.//Article'):
            direct_lists = [child for child in article if child.tag == 'List']
            if not direct_lists:
                continue

            # Find the insertion point (after the last existing Paragraph, or after ArticleTitle/Caption)
            insert_pos = -1
            for i, child in enumerate(list(article)):
                if child.tag in ['ArticleTitle', 'ArticleCaption', 'Paragraph']:
                    insert_pos = i
            
            # Create a new Paragraph to hold these lists
            new_para = ET.Element('Paragraph', attrib={'Num': '0'}) # Dummy Num, will be renumbered later if needed

            # Move the lists from the article to the new paragraph
            for l in direct_lists:
                article.remove(l)
                new_para.append(l)
            
            # Insert the new paragraph into the article
            article.insert(insert_pos + 1, new_para)
        
        print("="*80)
        print("【Article要素特化型変換（分割のみ）】")
        print("="*80)
        
        # 処理前の統計
        articles_before = len(root.findall('.//Article'))
        
        print(f"\n処理前:")
        print(f"  - Article要素: {articles_before}個")
        
        # 全てのArticle要素を処理
        for parent in root.iter():
            articles = [child for child in parent if child.tag == 'Article']
            
            if not articles:
                continue
            
            # 各Articleを処理（分割の可能性あり）
            for article in articles:
                index = list(parent).index(article)
                
                # Article要素を処理（分割された場合は複数のArticleが返る）
                new_articles = self.process_article(article)
                
                # 元のArticleを削除
                parent.remove(article)
                
                # 新しいArticle要素群を挿入
                for i, new_article in enumerate(new_articles):
                    parent.insert(index + i, new_article)
        
        # 処理後の統計
        articles_after = len(root.findall('.//Article'))
        
        print(f"\n処理後:")
        print(f"  - Article要素: {articles_after}個 ({articles_after - articles_before:+d})")
        
        print(f"\n変換統計:")
        print(f"  - 処理したArticle: {self.stats['articles_total']}個")
        print(f"  - ArticleTitleを追加: {self.stats['article_titles_added']}個")
        print(f"  - 分割したArticle: {self.stats['articles_split']}個")
        print(f"  - スキップしたArticle: {self.stats['articles_skipped']}個（ArticleTitleが空）")
        
        # Num属性の振り直し（親要素が変わるたびにリセット）
        if renumber:
            print(f"\nNum属性振り直し:")
            # Article要素の全親要素パターン（スキーマに基づく）
            # 各親要素内でArticleを1から連番（親が変わるたびにリセット）
            renumber_stats = renumber_nums_in_tree(tree, [
                ('MainProvision', 'Article'),  # 本文本体
                ('Part', 'Article'),           # 編
                ('Chapter', 'Article'),        # 章
                ('Section', 'Article'),        # 節
                ('Subsection', 'Article'),     # 款
                ('Division', 'Article'),       # 目
                ('SupplProvision', 'Article')  # 付則
            ], start_num=1)
            for elem_type, count in renumber_stats.items():
                print(f"  - {elem_type}: {count}個（親要素ごとに1からリセット）")
        
        # 結果を保存（インデント整形付き）
        save_xml_with_indent(tree, output_path)
        
        print(f"\n出力ファイル: {output_path}")
        print("  ✅ インデント整形済み")
        if renumber:
            print("  ✅ Num属性振り直し済み")
        print("="*80)


def main():
    """メイン処理"""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Article要素に特化した階層限定型変換スクリプト',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # 基本的な使用方法（Num属性振り直しあり）
  python convert_article_focused.py test_input5.xml
  
  # 出力ファイル名を指定
  python convert_article_focused.py test_input5.xml test_output.xml
  
  # Num属性振り直しを無効化
  python convert_article_focused.py test_input5.xml --no-renumber
        """
    )
    
    parser.add_argument('input', help='入力XMLファイル')
    parser.add_argument('output', nargs='?', help='出力XMLファイル（省略時: <input>_article_split.xml）')
    parser.add_argument('--no-renumber', action='store_true', 
                       help='Num属性の振り直しを無効化（デフォルト: 有効）')
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    output_path = Path(args.output) if args.output else input_path.parent / f"{input_path.stem}_article_split.xml"
    
    if not input_path.exists():
        print(f"エラー: 入力ファイルが見つかりません: {input_path}")
        sys.exit(1)
    
    converter = ArticleFocusedConverter()
    converter.process_xml(input_path, output_path, renumber=not args.no_renumber)


if __name__ == '__main__':
    main()
