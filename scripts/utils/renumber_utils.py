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

from lxml import etree as ET
import re
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Set, Union


# ============================================================================
# タイトル由来の Num 導出（コーパス準拠の枝番形式）
#
# e-LAWS / 対応済コーパスでは、Num 属性は表示番号と対応させる
# （例: <ItemTitle>六の二</ItemTitle> → Num="6_2"、<ArticleTitle>第十三条の二</ArticleTitle> → Num="13_2"）。
# 括弧付き・丸数字などの数字系ラベル（「（１）の２」「①」等）は中の数値を用いる（→ "1_2"）。
# 数字以外のラベル（「イ」「ａ」等）は親の中での初出順に 1, 2, … を割り当て、
# 枝番付き（「イの二」）は初出時の値を引き継ぐ（→ "1_2"）。
# それ以外（タイトルなし・解釈不能・重複）は従来どおり親単位で連番。
# ============================================================================

# スキーマ上 Num が xs:positiveInteger のため枝番形式（"6_2"）を使えない要素
SEQUENTIAL_ONLY_TAGS: Set[str] = {'Paragraph'}

_ZEN2HAN = str.maketrans('０１２３４５６７８９', '0123456789')
_KANJI_DIGITS = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
                 '六': 6, '七': 7, '八': 8, '九': 9}
_KANJI_UNITS = {'十': 10, '百': 100, '千': 1000}

_ARABIC_PART = r'[0-9０-９]+'
_KANJI_PART = r'[一二三四五六七八九十百千]+'
_NUM_PART = rf'(?:{_ARABIC_PART}|{_KANJI_PART})'
_SEP = r'[のノ]'

# 丸数字（①〜㊿）
_CIRCLED_DIGITS = '①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳' \
                  '㉑㉒㉓㉔㉕㉖㉗㉘㉙㉚㉛㉜㉝㉞㉟㊱㊲㊳㊴㊵㊶㊷㊸㊹㊺㊻㊼㊽㊾㊿'
_CIRCLED_TO_INT = {ch: i + 1 for i, ch in enumerate(_CIRCLED_DIGITS)}

# ラベルの装飾: 「（１）」「（（１））」「１）」「１．」
_PAREN_OPEN = r'[（(]{1,2}'
_PAREN_CLOSE = r'[）)]{1,2}'
_TRAILING_MARK = r'[）)．.]'
# 数字系ラベルの先頭要素: 「１」「（１）」「（（１））」「１）」「１．」「①」
_HEAD_NUM_PART = rf'(?:{_PAREN_OPEN}{_NUM_PART}{_PAREN_CLOSE}|{_NUM_PART}{_TRAILING_MARK}?|[{_CIRCLED_DIGITS}])'

# 「１２」「六の二」「（１）の２」「①」など数字系のみのタイトル（完全一致）
_PLAIN_TITLE_RE = re.compile(rf'^{_HEAD_NUM_PART}(?:{_SEP}{_NUM_PART})*$')

# 数字以外のラベル（イロハ・カタカナ・アルファベット）＋任意の枝番: 「イ」「（ア）」「ａ」「イの二」
_ALPHA_KANA = r'(?:[ア-ヴ]+|[a-zA-Zａ-ｚＡ-Ｚ]+)'
_NON_NUMERIC_TITLE_RE = re.compile(
    rf'^((?:{_PAREN_OPEN})?{_ALPHA_KANA}(?:{_PAREN_CLOSE})?{_TRAILING_MARK}?)((?:{_SEP}{_NUM_PART})*)$'
)
# 条見出し形式: 「第１」「第１の２」「第十三条の二」など（完全一致）
_ARTICLE_TITLE_RE = re.compile(rf'^第{_NUM_PART}条?(?:{_SEP}{_NUM_PART})*$')


def _kanji_to_int(text: str) -> Optional[int]:
    """漢数字（一〜九千九百九十九）を整数に変換する。解釈できない場合は None

    「一二」のような位取り表記は番号として扱わず None を返す
    （〇を含む表記は呼び出し前の正規表現で除外される）。
    """
    result = 0
    current = 0
    last_unit = float('inf')  # 単位（十・百・千）は降順でのみ出現可（「十百」等を拒否）
    for ch in text:
        if ch in _KANJI_DIGITS:
            if current != 0:
                return None
            current = _KANJI_DIGITS[ch]
        elif ch in _KANJI_UNITS:
            unit = _KANJI_UNITS[ch]
            if unit >= last_unit:
                return None
            last_unit = unit
            result += (current if current != 0 else 1) * unit
            current = 0
        else:
            return None
    total = result + current
    return total if total > 0 else None


def _number_part_to_int(part: str) -> Optional[int]:
    """番号1要素分（アラビア数字または漢数字）を整数に変換する"""
    part = part.translate(_ZEN2HAN)
    if part.isdigit():
        num = int(part)
        return num if num > 0 else None
    return _kanji_to_int(part)


def _head_part_to_int(part: str) -> Optional[int]:
    """先頭要素（括弧・末尾記号・丸数字を含みうる）を整数に変換する

    「（１）」「（（１））」「１）」「１．」は装飾を除いた数値、「①」は 1 を返す。
    """
    if part in _CIRCLED_TO_INT:
        return _CIRCLED_TO_INT[part]
    core = re.sub(rf'^{_PAREN_OPEN}|{_PAREN_CLOSE}$|{_TRAILING_MARK}$', '', part)
    return _number_part_to_int(core)


def title_to_num(text: Optional[str]) -> Optional[str]:
    """タイトル文字列からコーパス準拠の Num 値を導出する

    例:
        「１２」「十二」          → "12"
        「６の２」「六の二」      → "6_2"
        「（１）」「（１）の２」  → "1" / "1_2"（括弧の中の数値を用いる）
        「①」「１）」「１．」    → "1"
        「第１の２」「第十三条の二」 → "13_2" 等の条見出し形式にも対応

    イロハ・アルファベット等の数字以外のラベルは、親の中での登場順に依存するため
    ここでは None を返す（derive_child_nums 側で初出順に採番する）。
    タイトル全体が番号として解釈できない場合も None を返す
    （呼び出し側で連番にフォールバックする）。
    """
    if not text:
        return None
    t = text.strip(' \t\r\n　')
    if not t:
        return None
    if _ARTICLE_TITLE_RE.match(t):
        t = t[1:].replace('条', '', 1)  # 先頭の「第」と「条」を除去
    elif not _PLAIN_TITLE_RE.match(t):
        return None
    head, *rest = re.split(_SEP, t)
    nums = [_head_part_to_int(head)] + [_number_part_to_int(p) for p in rest]
    if any(n is None for n in nums):
        return None
    return '_'.join(str(n) for n in nums)


def _derive_nums_by_appearance(titles: List[Optional[str]]) -> Optional[List[str]]:
    """数字以外のラベル（イロハ・アルファベット等）を初出順に採番する

    「の」の前の基底ラベルごとに、親の中で初めて現れた順に 1, 2, … を割り当て、
    枝番付き（「イの二」）は基底ラベルの値を引き継いで "1_2" のようにする。
    1つでも解釈できないタイトルがあれば None を返す（all-or-nothing）。

    例: ['イ', 'ロ', 'イの二', 'ハ'] → ['1', '2', '1_2', '3']
    """
    order: Dict[str, int] = {}
    nums: List[str] = []
    for text in titles:
        if not text:
            return None
        t = text.strip(' \t\r\n　')
        m = _NON_NUMERIC_TITLE_RE.match(t)
        if not m:
            return None
        base, branch = m.group(1), m.group(2)
        branch_nums = [_number_part_to_int(p) for p in re.split(_SEP, branch) if p]
        if any(n is None for n in branch_nums):
            return None
        if base not in order:
            order[base] = len(order) + 1
        nums.append('_'.join(str(n) for n in [order[base]] + branch_nums))
    return nums


def derive_child_nums(children: List[ET._Element], title_tag: str) -> Optional[List[str]]:
    """子要素群のタイトルから Num 値のリストを導出する

    1. 全要素が数字系ラベル（title_to_num で導出可能）ならその値
    2. そうでなければ、全要素が数字以外のラベル（イロハ・アルファベット等）なら初出順
       （_derive_nums_by_appearance）
    のいずれかで、値が一意である場合のみリストを返す。
    それ以外は None を返す（親単位の all-or-nothing 判定）。
    """
    titles: List[Optional[str]] = []
    for child in children:
        title_elem = child.find(title_tag)
        titles.append(title_elem.text if title_elem is not None else None)

    nums: Optional[List[str]] = [title_to_num(t) for t in titles]
    if any(n is None for n in nums):
        nums = _derive_nums_by_appearance(titles)
    if nums is None or len(set(nums)) != len(nums):
        return None
    return nums


def renumber_children(
    parent_elem: ET._Element,
    child_tag: str,
    title_tag: Optional[str] = None,
    start_num: int = 1
) -> Tuple[str, int]:
    """親要素直下の child_tag 要素の Num 属性を振り直す

    タイトル要素（title_tag、省略時は child_tag + 'Title'）から番号を導出できる場合は
    コーパス準拠の枝番形式（例: 「六の二」「（６）の２」→ "6_2"）を用いる。
    数字以外のラベル（イロハ等）は初出順に採番し、枝番は初出時の値を引き継ぐ
    （例: 「イ」「ロ」「イの二」→ "1" "2" "1_2"）。derive_child_nums 参照。
    1つでも導出できない・重複する場合は、その親要素内は従来どおり連番を振る。
    SEQUENTIAL_ONLY_TAGS（Paragraph 等、スキーマ上 Num が正整数の要素）は常に連番。

    Returns:
        Tuple[str, int]: (採番方式 'title' または 'sequential', 対象要素数)
    """
    children = [c for c in parent_elem if c.tag == child_tag]
    if not children:
        return ('sequential', 0)
    if title_tag is None:
        title_tag = child_tag + 'Title'
    nums: Optional[List[str]] = None
    if child_tag not in SEQUENTIAL_ONLY_TAGS:
        nums = derive_child_nums(children, title_tag)
    if nums is None:
        mode = 'sequential'
        nums = [str(i) for i in range(start_num, start_num + len(children))]
    else:
        mode = 'title'
    for child, num in zip(children, nums):
        child.set('Num', num)
    return (mode, len(children))


def renumber_nums_by_title(
    tree: ET.ElementTree,
    child_tags: List[str],
    start_num: int = 1
) -> Dict[str, Dict[str, int]]:
    """文書全体を対象に、指定タグの要素を「直接の親」ごとにグループ化して Num を振り直す

    親要素のタグ名を列挙する必要はなく、各要素の直接の親ごとに
    renumber_children() を適用する（親が変わるたびに連番はリセット）。

    Args:
        tree: 処理対象の ElementTree
        child_tags: 振り直す要素タグのリスト（例: ['Article'] や ['Item', 'Subitem1']）
        start_num: 連番フォールバック時の開始番号

    Returns:
        Dict[str, Dict[str, int]]: タグごとの採番方式別要素数
        例: {'Article': {'title': 12, 'sequential': 0}}
    """
    root = tree.getroot()
    stats: Dict[str, Dict[str, int]] = {}
    for tag in child_tags:
        tag_stats = {'title': 0, 'sequential': 0}
        parents: List[ET._Element] = []
        seen: Set[int] = set()
        for elem in root.iter(tag):
            parent = elem.getparent()
            if parent is not None and id(parent) not in seen:
                seen.add(id(parent))
                parents.append(parent)
        for parent in parents:
            mode, count = renumber_children(parent, tag, start_num=start_num)
            tag_stats[mode] += count
        stats[tag] = tag_stats
    return stats


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
        input_path_str = str(input_path) if isinstance(input_path, Path) else input_path
        tree = ET.parse(input_path_str)
        stats = renumber_nums_in_tree(tree, mappings, start_num)
        
        # 保存（インデント整形は別途 save_xml_with_indent を使用）
        output_path_str = str(output_path) if isinstance(output_path, Path) else output_path
        tree.write(output_path_str, encoding='utf-8', xml_declaration=True)
        
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
        tree = ET.parse(str(args.input))
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


