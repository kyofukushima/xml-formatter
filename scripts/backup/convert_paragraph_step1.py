#!/usr/bin/env python3
"""
Paragraph特化スクリプト - Step 1

処理内容: ParagraphNum要素の補完
--------------------------------------
Paragraph要素にParagraphNum要素が存在しない場合、
Paragraph要素の先頭に空の<ParagraphNum />を追加する。

前提条件:
- Article要素より浅い階層には問題がない
- （注意: Article特化スクリプトの前後どちらで実行しても問題ありません）

参照:
- logic2_1_ParagraphNum.md
"""

import sys
import argparse
from pathlib import Path
from lxml import etree

# utilsディレクトリをインポートパスに追加（親ディレクトリのutils/を参照）
sys.path.insert(0, str(Path(__file__).parent.parent))

# 共通XMLユーティリティは未使用のためインポートしない
# from utils import save_xml_with_indent, renumber_nums_in_tree


def format_xml_lxml(tree, output_path):
    """
    lxmlのElementTreeをインデント整形して保存
    ParagraphNum要素の後に改行を挿入する
    
    Args:
        tree: lxml ElementTree
        output_path: 出力ファイルパス
    """
    import re
    
    # まずpretty_printで整形
    xml_string = etree.tostring(
        tree,
        encoding='utf-8',
        xml_declaration=True,
        pretty_print=True
    ).decode('utf-8')
    
    # XML宣言のエンコーディングを大文字に統一
    xml_string = re.sub(
        r"encoding='utf-8'",
        r"encoding='UTF-8'",
        xml_string
    )
    
    # ParagraphNum要素の後に改行を挿入（同じ行に続く要素がある場合）
    # <ParagraphNum/><ParagraphSentence> を <ParagraphNum/>\n        <ParagraphSentence> に変換
    xml_string = re.sub(
        r'(<ParagraphNum/>)(<[^/])',
        r'\1\n        \2',
        xml_string
    )
    
    # ファイルに書き込み
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(xml_string)


def complement_paragraph_nums(tree, verification_mode=False, script_name="unknown_script"):
    """
    Paragraph要素にParagraphNum要素がない場合、空のParagraphNum要素を追加
    
    Args:
        tree: XML ElementTree
        verification_mode (bool): Trueの場合、変更箇所にコメントを挿入
        script_name (str): コメントに記載するスクリプト名
        
    Returns:
        dict: 統計情報（total_paragraphs, paragraphs_with_num, 
              paragraphs_without_num, added_paragraph_nums）
    """
    root = tree.getroot()
    stats = {
        'total_paragraphs': 0,
        'paragraphs_with_num': 0,
        'paragraphs_without_num': 0,
        'added_paragraph_nums': 0
    }
    
    # すべてのParagraph要素を検索
    paragraphs = root.xpath('.//Paragraph')
    stats['total_paragraphs'] = len(paragraphs)
    
    for paragraph in paragraphs:
        # ParagraphNum要素の存在確認
        paragraph_num = paragraph.find('ParagraphNum')
        
        if paragraph_num is not None:
            # すでにParagraphNumが存在する
            stats['paragraphs_with_num'] += 1
        else:
            # ParagraphNumが存在しない → 先頭に空のParagraphNumを追加
            stats['paragraphs_without_num'] += 1

            if verification_mode:
                # 検証モード時、変更前の状態をコメントとして挿入
                before_str = etree.tostring(paragraph, pretty_print=True, encoding='unicode')
                comment_text = f"\n*** {script_name}: MODIFIED: ParagraphNum ADDED ***\n{before_str}\n"
                comment = etree.Comment(comment_text)
                paragraph.addprevious(comment)
            
            # 空のParagraphNum要素を作成
            new_paragraph_num = etree.Element('ParagraphNum')
            
            # Paragraph要素の先頭に挿入
            paragraph.insert(0, new_paragraph_num)
            
            stats['added_paragraph_nums'] += 1
    
    return stats


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description='Paragraph特化スクリプト - Step 1（ParagraphNum補完）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # 基本的な使い方
  python3 convert_paragraph_step1.py input.xml
  
  # 出力ファイルを指定
  python3 convert_paragraph_step1.py input.xml output.xml

  # 検証モードで実行（変更箇所にコメントを挿入）
  python3 convert_paragraph_step1.py input.xml --verification

処理内容:
  - Paragraph要素にParagraphNum要素がない場合、空のParagraphNum要素を先頭に追加

前提条件:
  - Article要素より浅い階層には問題がないことを想定
  - （注意: Article特化スクリプトの前後どちらで実行しても問題ありません）
        """
    )
    
    parser.add_argument(
        'input_file',
        help='入力XMLファイル'
    )
    
    parser.add_argument(
        'output_file',
        nargs='?',
        help='出力XMLファイル（デフォルト: <input>_paragraph_step1.xml）'
    )

    parser.add_argument(
        '--verification',
        action='store_true',
        help='変更箇所にコメントを挿入する検証モードを有効にする'
    )
    
    args = parser.parse_args()
    
    # 入力ファイルの存在確認
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"エラー: 入力ファイルが見つかりません: {args.input_file}")
        return 1
    
    # 出力ファイル名の決定
    if args.output_file:
        output_path = Path(args.output_file)
    else:
        output_path = input_path.parent / f"{input_path.stem}_paragraph_step1.xml"
    
    print("=" * 80)
    print("【Paragraph要素特化型変換 - Step 1: ParagraphNum補完】")
    print("=" * 80)
    print()
    
    # スクリプト名を取得
    script_name = Path(__file__).name

    # XMLファイルを読み込み
    try:
        tree = etree.parse(str(input_path))
    except Exception as e:
        print(f"エラー: XMLファイルの読み込みに失敗しました: {e}")
        return 1
    
    # 処理前の統計
    root = tree.getroot()
    paragraphs_before = len(root.xpath('.//Paragraph'))
    paragraph_nums_before = len(root.xpath('.//Paragraph/ParagraphNum'))
    
    print("処理前:")
    print(f"  - Paragraph要素: {paragraphs_before}個")
    print(f"  - ParagraphNum要素: {paragraph_nums_before}個")
    print()
    
    # ParagraphNum補完処理を実行
    stats = complement_paragraph_nums(tree, args.verification, script_name)
    
    # 処理後の統計
    paragraph_nums_after = len(root.xpath('.//Paragraph/ParagraphNum'))
    
    print("処理後:")
    print(f"  - Paragraph要素: {paragraphs_before}個")
    print(f"  - ParagraphNum要素: {paragraph_nums_after}個 (+{paragraph_nums_after - paragraph_nums_before})")
    print()
    
    print("変換統計:")
    print(f"  - 処理したParagraph: {stats['total_paragraphs']}個")
    print(f"  - ParagraphNum既存: {stats['paragraphs_with_num']}個")
    print(f"  - ParagraphNum不在: {stats['paragraphs_without_num']}個")
    print(f"  - ParagraphNum追加: {stats['added_paragraph_nums']}個")
    print()
    
    # XMLファイルに保存（整形済み）
    format_xml_lxml(tree, str(output_path))
    
    print(f"出力ファイル: {output_path}")
    print("  ✅ インデント整形済み")
    print("  ✅ ParagraphNum補完済み")
    print("=" * 80)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

