#!/usr/bin/env python3
"""
XML処理のための共通ユーティリティモジュール

各特化型スクリプト（Article、Paragraph、Item等）で共通的に使用する
XML処理関数を提供します。
"""

from lxml import etree as ET
import sys
from pathlib import Path
from typing import Union


def get_text_from_element(element: Union[ET.Element, None]) -> str:
    """要素からテキストを安全に取得する。要素が存在しない場合やテキストがない場合は空文字列を返す。"""
    if element is not None and element.text is not None:
        return element.text.strip()
    return ""

def create_element_with_text(tag: str, text: str, attrib: dict = None) -> ET.Element:
    """指定されたタグとテキストで新しいElementを作成する。"""
    if attrib is None:
        attrib = {}
    element = ET.Element(tag, attrib)
    element.text = text
    return element


def indent_xml(elem: ET.Element, level: int = 0, indent_str: str = "  ") -> None:
    """XML要素を再帰的にインデント整形
    
    Python 3.9以降のET.indent()と同等の機能を提供。
    Python 3.9未満でも動作するように独自実装。
    
    Args:
        elem: 整形対象のElement
        level: 現在のインデントレベル
        indent_str: インデント文字列（デフォルト: 2スペース）
    
    Usage:
        tree = ET.parse('input.xml')
        root = tree.getroot()
        indent_xml(root)
        tree.write('output.xml', encoding='utf-8', xml_declaration=True)
    """
    # 現在のレベルのインデント
    current_indent = "\n" + (indent_str * level)
    
    # 子要素が存在する場合
    if len(elem):
        # 最初の子要素の前にインデントを追加
        if not elem.text or not elem.text.strip():
            elem.text = current_indent + indent_str
        
        # 各子要素を再帰的に処理
        for i, child in enumerate(elem):
            indent_xml(child, level + 1, indent_str)
            
            # 子要素の後にインデントを追加
            if i < len(elem) - 1:
                # 最後以外の子要素
                if not child.tail or not child.tail.strip():
                    child.tail = current_indent + indent_str
            else:
                # 最後の子要素
                if not child.tail or not child.tail.strip():
                    child.tail = current_indent
        
        # 閉じタグの前のインデント調整
        if not elem.tail or not elem.tail.strip():
            elem.tail = current_indent
    else:
        # 子要素がない場合
        if level > 0 and (not elem.tail or not elem.tail.strip()):
            elem.tail = current_indent


# インライン内容を持つ要素（本文テキストと子要素が同居する「混在内容」の容器）。
# これらの内側にインデント用の改行・空白を挿入すると、Ruby（ふりがな）の内側などに
# 空白文字が本文として入り、表示上の改行やずれの原因になる。
INLINE_CONTAINER_TAGS = frozenset({
    'Sentence', 'Ruby', 'Rt', 'Sub', 'Sup', 'Line', 'ParagraphNum',
})


def _is_inline_container(elem) -> bool:
    """インデントを内側に入れてはいけない要素かどうか

    Sentence・各種 Title/Caption・Ruby 等の既知のインライン容器に加え、
    本文テキストと子要素が同居している（混在内容の）要素も対象とする。
    """
    tag = elem.tag
    if not isinstance(tag, str):
        return False
    if tag in INLINE_CONTAINER_TAGS or tag.endswith('Title') or tag.endswith('Caption'):
        return True
    if len(elem) == 0:
        return False
    if elem.text and elem.text.strip():
        return True
    return any(child.tail and child.tail.strip() for child in elem)


def _has_no_newline(value) -> bool:
    return value is None or '\n' not in value


def indent_xml_preserving_inline(root: ET.Element, space: str = "  ", level: int = 0) -> None:
    """構造要素だけをインデント整形し、インライン容器の内側には空白を追加しない

    lxml の etree.indent() は子要素を持つ要素をすべてブロック要素とみなすため、
    Sentence 内の Ruby（ふりがな）等の内側（例: </Rt> と </Ruby> の間）にも
    改行とインデントを挿入してしまう。この関数は etree.indent() を実行した後、
    インライン容器の内側で「元は空白がなかった（または改行を含まなかった）」
    text/tail を元の値に戻すことで、本文への空白追加を防ぐ。

    元から改行を含む空白（前段の整形結果など）は、従来どおり再インデントされる。

    Args:
        root: 整形対象のルート要素（lxml）
        space: インデント文字列
        level: 開始レベル
    """
    snapshot = []
    for elem in root.iter():
        if not _is_inline_container(elem):
            continue
        if _has_no_newline(elem.text):
            snapshot.append((elem, 'text', elem.text))
        for desc in elem.iterdescendants():
            if _has_no_newline(desc.text):
                snapshot.append((desc, 'text', desc.text))
            if _has_no_newline(desc.tail):
                snapshot.append((desc, 'tail', desc.tail))

    ET.indent(root, space=space, level=level)

    for elem, attr, value in snapshot:
        setattr(elem, attr, value)


def format_xml_lxml(tree: ET.ElementTree, output_path: Union[str, Path], space: str = "  ") -> None:
    """lxml の ElementTree をインデント整形して保存する（各変換スクリプト共通）

    文字列化と再パースで既存の空白ノードを正規化した上で、
    indent_xml_preserving_inline() により Ruby 等の内側に空白を入れずに整形する。
    """
    clean_root = ET.fromstring(ET.tostring(tree.getroot()))
    indent_xml_preserving_inline(clean_root, space=space, level=0)
    ET.ElementTree(clean_root).write(
        str(output_path),
        encoding='utf-8',
        xml_declaration=True,
        pretty_print=False
    )


def indent_xml_native(elem: ET.Element, space: str = "  ") -> None:
    """lxmlのpretty_print機能を使用したインデント整形
    
    lxmlでは、tree.write()のpretty_printオプションを使用するため、
    この関数は非推奨です。save_xml_with_indent()を使用してください。
    
    Args:
        elem: 整形対象のElement
        space: インデント文字列（デフォルト: 2スペース）
    
    Note:
        lxmlでは、tree.write(pretty_print=True)を使用することを推奨します。
    """
    # lxmlでは、tree.write()のpretty_printオプションを使用
    # この関数は後方互換性のため残していますが、indent_xml()を使用してください
    indent_xml(elem, indent_str=space)


def save_xml_with_indent(tree: ET.ElementTree, output_path: Union[str, Path], 
                         indent_str: str = "  ") -> None:
    """XML Treeをインデント整形して保存
    
    lxmlを使用してインデント整形を行います。
    動的に要素を追加・削除した場合でも、正しくインデントを再設定します。
    
    Args:
        tree: 保存するElementTree（lxml.etree.ElementTree）
        output_path: 出力ファイルパス
        indent_str: インデント文字列（デフォルト: 2スペース）
    
    Usage:
        tree = ET.parse('input.xml')
        root = tree.getroot()
        # ... 処理 ...
        save_xml_with_indent(tree, 'output.xml')
    """
    root = tree.getroot()

    # 動的に要素を追加・削除した場合、pretty_printだけでは不十分なため
    # インデントを再設定する。Sentence 内の Ruby 等（インライン容器）の内側には
    # 空白を追加しない（indent_xml_preserving_inline 参照）
    indent_xml_preserving_inline(root, space=indent_str)

    # Pathオブジェクトの場合は文字列に変換
    output_path_str = str(output_path) if isinstance(output_path, Path) else output_path

    # XML宣言付きで保存（インデントは上で設定済みのため pretty_print は使わない）
    tree.write(
        output_path_str,
        encoding='utf-8',
        xml_declaration=True,
        pretty_print=False
    )


def pretty_print_xml(input_path: Union[str, Path], output_path: Union[str, Path], 
                     indent_str: str = "  ") -> None:
    """XMLファイルを読み込んでインデント整形して保存
    
    既存のXMLファイルを整形したい場合に使用。
    
    Args:
        input_path: 入力XMLファイルパス
        output_path: 出力XMLファイルパス
        indent_str: インデント文字列（デフォルト: 2スペース）
                   lxmlではpretty_print=Trueを使用するため、この引数は後方互換性のため残しています
    
    Usage:
        pretty_print_xml('input.xml', 'output_formatted.xml')
    """
    # Pathオブジェクトの場合は文字列に変換（lxmlの要求）
    input_path_str = str(input_path) if isinstance(input_path, Path) else input_path
    tree = ET.parse(input_path_str)
    save_xml_with_indent(tree, output_path, indent_str)


def get_python_version_info() -> str:
    """Pythonバージョン情報を取得
    
    Returns:
        str: バージョン情報文字列
    """
    version = sys.version_info
    return f"Python {version.major}.{version.minor}.{version.micro}"


if __name__ == '__main__':
    """コマンドラインから直接XMLファイルを整形"""
    import sys
    
    if len(sys.argv) < 2:
        print("使用方法: python xml_utils.py <input.xml> [output.xml]")
        print("\n例:")
        print("  python xml_utils.py test.xml")
        print("  python xml_utils.py test.xml test_formatted.xml")
        print(f"\n現在の環境: {get_python_version_info()}")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) >= 3 else input_file.parent / f"{input_file.stem}_formatted.xml"
    
    if not input_file.exists():
        print(f"エラー: 入力ファイルが見つかりません: {input_file}")
        sys.exit(1)
    
    print(f"XMLファイルを整形中...")
    print(f"  入力: {input_file}")
    print(f"  出力: {output_file}")
    print(f"  環境: {get_python_version_info()}")
    
    pretty_print_xml(input_file, output_file)
    
    print("完了！")

