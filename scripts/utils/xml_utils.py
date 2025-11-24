#!/usr/bin/env python3
"""
XML処理のための共通ユーティリティモジュール

各特化型スクリプト（Article、Paragraph、Item等）で共通的に使用する
XML処理関数を提供します。
"""

import xml.etree.ElementTree as ET
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


def indent_xml_native(elem: ET.Element, space: str = "  ") -> None:
    """Python 3.9以降のET.indent()を使用したインデント整形
    
    Python 3.9以降でのみ使用可能。
    
    Args:
        elem: 整形対象のElement
        space: インデント文字列（デフォルト: 2スペース）
    
    Raises:
        AttributeError: Python 3.9未満の場合
    """
    if hasattr(ET, 'indent'):
        ET.indent(elem, space=space)
    else:
        raise AttributeError("ET.indent() is not available. Use indent_xml() instead.")


def save_xml_with_indent(tree: ET.ElementTree, output_path: Union[str, Path], 
                         indent_str: str = "  ") -> None:
    """XML Treeをインデント整形して保存
    
    Pythonのバージョンに応じて、最適な方法でインデント整形を行います。
    
    Args:
        tree: 保存するElementTree
        output_path: 出力ファイルパス
        indent_str: インデント文字列（デフォルト: 2スペース）
    
    Usage:
        tree = ET.parse('input.xml')
        root = tree.getroot()
        # ... 処理 ...
        save_xml_with_indent(tree, 'output.xml')
    """
    root = tree.getroot()
    
    # Python 3.9以降ならET.indent()を使用、それ以外なら独自実装
    python_version = sys.version_info
    if python_version.major == 3 and python_version.minor >= 9:
        # Python 3.9以降
        ET.indent(root, space=indent_str)
    else:
        # Python 3.8以前
        indent_xml(root, indent_str=indent_str)
    
    # XML宣言付きで保存
    tree.write(output_path, encoding='utf-8', xml_declaration=True)


def pretty_print_xml(input_path: Union[str, Path], output_path: Union[str, Path], 
                     indent_str: str = "  ") -> None:
    """XMLファイルを読み込んでインデント整形して保存
    
    既存のXMLファイルを整形したい場合に使用。
    
    Args:
        input_path: 入力XMLファイルパス
        output_path: 出力XMLファイルパス
        indent_str: インデント文字列（デフォルト: 2スペース）
    
    Usage:
        pretty_print_xml('input.xml', 'output_formatted.xml')
    """
    tree = ET.parse(input_path)
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

