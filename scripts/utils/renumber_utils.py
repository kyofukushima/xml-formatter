#!/usr/bin/env python3
"""
Num属性の連番振り直しユーティリティ

特化型スクリプト（Article、Paragraph、Item等）から共通的に使用する
Num属性の連番付け直し機能を提供します。

【主な機能】
1. ElementTreeベース: DOM解析による安全な連番付け（推奨）
2. テキストベース: 元のインデント・コメントを完全保持

【使用例】
```python
from utils import renumber_nums_in_tree, renumber_nums_in_file

# ElementTreeを使った連番付け（推奨）
tree = ET.parse('input.xml')
stats = renumber_nums_in_tree(tree, [('Article', None)])
# → Article要素のNumを1から連番で振る

# ファイルを直接処理
stats = renumber_nums_in_file('input.xml', 'output.xml', [('Article', None)])
```
"""

import xml.etree.ElementTree as ET
import re
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Set, Union


def renumber_nums_in_tree(
    tree: ET.ElementTree, 
    mappings: List[Tuple[str, Optional[str]]],
    start_num: int = 1
) -> Dict[str, int]:
    """ElementTreeのNum属性を連番で振り直す（推奨）
    
    親子関係を指定することで、親要素が切り替わるたびに子要素のカウンタをリセットします。
    親を指定しない場合（None）は、全体で連番を振ります。
    
    Args:
        tree: 処理対象のElementTree
        mappings: [(親要素名, 子要素名), ...] のリスト
                 親をNoneにすると全体で連番
                 例: [('Article', None)]  → Article全体で連番
                     [('Paragraph', 'Item')]  → Paragraph内のItemを連番
                     [('Article', None), ('Paragraph', 'Item')]  → 複数指定
        start_num: 開始番号（デフォルト: 1）
    
    Returns:
        Dict[str, int]: 各要素タイプごとの置換数
        例: {'Article': 14, 'Item': 125}
    
    Example:
        >>> tree = ET.parse('input.xml')
        >>> # Article要素を1から連番
        >>> stats = renumber_nums_in_tree(tree, [('Article', None)])
        >>> print(stats)  # {'Article': 14}
        >>> 
        >>> # Paragraph内のItemを連番（Paragraphが変わるたびにリセット）
        >>> stats = renumber_nums_in_tree(tree, [('Paragraph', 'Item')])
        >>> print(stats)  # {'Item': 125}
    """
    root = tree.getroot()
    stats: Dict[str, int] = {}
    
    for parent_tag, child_tag in mappings:
        if child_tag is None:
            # 親を指定しない場合: 全体で連番
            counter = start_num
            for elem in root.iter(parent_tag):
                if 'Num' in elem.attrib:
                    elem.set('Num', str(counter))
                    counter += 1
                    stats[parent_tag] = stats.get(parent_tag, 0) + 1
        else:
            # 親子関係を指定した場合: 親ごとにカウンタリセット
            for parent_elem in root.iter(parent_tag):
                counter = start_num
                for child_elem in parent_elem.iter(child_tag):
                    # 親要素の直接/間接の子要素であることを確認
                    if 'Num' in child_elem.attrib:
                        child_elem.set('Num', str(counter))
                        counter += 1
                        stats[child_tag] = stats.get(child_tag, 0) + 1
    
    return stats


def renumber_nums_in_file(
    input_path: Union[str, Path],
    output_path: Union[str, Path],
    mappings: List[Tuple[str, Optional[str]]],
    start_num: int = 1,
    preserve_formatting: bool = False
) -> Dict[str, int]:
    """XMLファイルのNum属性を連番で振り直す
    
    Args:
        input_path: 入力XMLファイルパス
        output_path: 出力XMLファイルパス
        mappings: [(親要素名, 子要素名), ...] のリスト
        start_num: 開始番号（デフォルト: 1）
        preserve_formatting: Trueの場合、元のインデントを完全保持（テキストベース処理）
    
    Returns:
        Dict[str, int]: 各要素タイプごとの置換数
    
    Example:
        >>> # Article要素を1から連番で振り直し
        >>> stats = renumber_nums_in_file(
        ...     'test_input.xml', 
        ...     'test_output.xml',
        ...     [('Article', None)]
        ... )
        >>> print(f"Article要素を{stats['Article']}個振り直しました")
    """
    input_path = Path(input_path)
    output_path = Path(output_path)
    
    if preserve_formatting:
        # テキストベース処理: 元のインデントを完全保持
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        new_content, stats = _renumber_text_based(content, mappings, start_num)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return stats
    else:
        # ElementTreeベース処理: 推奨
        tree = ET.parse(input_path)
        stats = renumber_nums_in_tree(tree, mappings, start_num)
        
        # 保存（インデント整形は別途 save_xml_with_indent を使用）
        tree.write(output_path, encoding='utf-8', xml_declaration=True)
        
        return stats


def _renumber_text_based(
    content: str, 
    mappings: List[Tuple[str, Optional[str]]],
    start_num: int = 1
) -> Tuple[str, Dict[str, int]]:
    """テキストベースのNum属性振り直し（内部用）
    
    元のインデント・コメントを完全に保持します。
    
    Args:
        content: XML文字列
        mappings: [(親要素名, 子要素名), ...] のリスト
        start_num: 開始番号
    
    Returns:
        Tuple[str, Dict[str, int]]: (新しいXML文字列, 統計)
    """
    stats: Dict[str, int] = {}
    new_content = content
    
    for parent_tag, child_tag in mappings:
        if child_tag is None:
            # 親を指定しない場合: 全体で連番
            counter = start_num
            pattern = re.compile(
                rf'(<{re.escape(parent_tag)}\b[^>]*?\bNum\s*=\s*")([^"]*?)(")',
                re.DOTALL
            )
            
            def replace_func(match):
                nonlocal counter
                result = f"{match.group(1)}{counter}{match.group(3)}"
                counter += 1
                stats[parent_tag] = stats.get(parent_tag, 0) + 1
                return result
            
            new_content = pattern.sub(replace_func, new_content)
        else:
            # 親子関係を指定した場合: 親ブロックごとにカウンタリセット
            parent_block_pattern = re.compile(
                rf'(<{re.escape(parent_tag)}\b[\s\S]*?</{re.escape(parent_tag)}>)',
                re.DOTALL
            )
            
            def replace_block(match):
                block_text = match.group(1)
                counter = start_num
                
                child_pattern = re.compile(
                    rf'(<{re.escape(child_tag)}\b[^>]*?\bNum\s*=\s*")([^"]*?)(")',
                    re.DOTALL
                )
                
                def replace_child(child_match):
                    nonlocal counter
                    result = f"{child_match.group(1)}{counter}{child_match.group(3)}"
                    counter += 1
                    stats[child_tag] = stats.get(child_tag, 0) + 1
                    return result
                
                return child_pattern.sub(replace_child, block_text)
            
            new_content = parent_block_pattern.sub(replace_block, new_content)
    
    return new_content, stats


def get_default_mappings() -> List[Tuple[str, Optional[str]]]:
    """デフォルトの親子関係マッピングを取得
    
    一般的な法令XML構造に対応したデフォルト設定を返します。
    
    Returns:
        List[Tuple[str, Optional[str]]]: デフォルトマッピング
        
    Default Mappings:
        - Article: 全体で連番
        - Subsection内のArticle: Subsectionごとに連番
        - Paragraph内のItem: Paragraphごとに連番
        - Item内のSubitem1: Itemごとに連番
        - Subitem1内のSubitem2: Subitem1ごとに連番
        - ...Subitem9内のSubitem10: Subitem9ごとに連番
    """
    return [
        ('Article', None),  # Article全体で連番
        ('Subsection', 'Article'),  # Subsection内のArticleを連番
        ('Paragraph', 'Item'),  # Paragraph内のItemを連番
        ('Item', 'Subitem1'),
        ('Subitem1', 'Subitem2'),
        ('Subitem2', 'Subitem3'),
        ('Subitem3', 'Subitem4'),
        ('Subitem4', 'Subitem5'),
        ('Subitem5', 'Subitem6'),
        ('Subitem6', 'Subitem7'),
        ('Subitem7', 'Subitem8'),
        ('Subitem8', 'Subitem9'),
        ('Subitem9', 'Subitem10'),
    ]


def renumber_common_elements(
    tree: ET.ElementTree,
    start_num: int = 1
) -> Dict[str, int]:
    """一般的な要素のNum属性をまとめて振り直す（便利関数）
    
    デフォルトのマッピングを使用して、一般的な法令XML要素の
    Num属性を一括で振り直します。
    
    Args:
        tree: 処理対象のElementTree
        start_num: 開始番号（デフォルト: 1）
    
    Returns:
        Dict[str, int]: 各要素タイプごとの置換数
    
    Example:
        >>> tree = ET.parse('input.xml')
        >>> stats = renumber_common_elements(tree)
        >>> print(stats)
        {'Article': 14, 'Item': 125, 'Subitem1': 45, ...}
    """
    mappings = get_default_mappings()
    return renumber_nums_in_tree(tree, mappings, start_num)


if __name__ == '__main__':
    """コマンドラインから直接実行"""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(
        description='XMLファイルのNum属性を連番で振り直す',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # Article要素を1から連番で振り直し
  python renumber_utils.py input.xml output.xml --elements Article
  
  # Paragraph内のItemを連番で振り直し（Paragraphごとにリセット）
  python renumber_utils.py input.xml output.xml --parent Paragraph --child Item
  
  # デフォルトマッピングで一括振り直し
  python renumber_utils.py input.xml output.xml --default
  
  # 元のインデントを完全保持
  python renumber_utils.py input.xml output.xml --elements Article --preserve-formatting
        """
    )
    
    parser.add_argument('input', help='入力XMLファイル')
    parser.add_argument('output', help='出力XMLファイル')
    parser.add_argument('--elements', nargs='+', help='連番を振る要素名（全体で連番）')
    parser.add_argument('--parent', help='親要素名')
    parser.add_argument('--child', help='子要素名（親要素内で連番）')
    parser.add_argument('--default', action='store_true', help='デフォルトマッピングを使用')
    parser.add_argument('--start', type=int, default=1, help='開始番号（デフォルト: 1）')
    parser.add_argument('--preserve-formatting', action='store_true', 
                       help='元のインデントを完全保持（テキストベース処理）')
    parser.add_argument('--dry-run', action='store_true', help='実行せずに統計のみ表示')
    
    args = parser.parse_args()
    
    # マッピングを構築
    mappings: List[Tuple[str, Optional[str]]] = []
    
    if args.default:
        mappings = get_default_mappings()
    elif args.elements:
        for elem in args.elements:
            mappings.append((elem, None))
    elif args.parent and args.child:
        mappings.append((args.parent, args.child))
    else:
        parser.error('--elements, --parent/--child, または --default のいずれかを指定してください')
    
    # 処理実行
    if args.dry_run:
        tree = ET.parse(args.input)
        stats = renumber_nums_in_tree(tree, mappings, args.start)
        
        print("Dry-run: 以下のNum属性を振り直します:")
        for elem_type, count in stats.items():
            print(f"  - {elem_type}: {count}個")
    else:
        stats = renumber_nums_in_file(
            args.input, 
            args.output, 
            mappings, 
            args.start,
            args.preserve_formatting
        )
        
        print("振り直し完了:")
        for elem_type, count in stats.items():
            print(f"  - {elem_type}: {count}個")
        print(f"\n出力ファイル: {args.output}")


