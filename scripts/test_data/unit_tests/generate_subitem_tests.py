#!/usr/bin/env python3
"""
item要素のテストケースをベースとして、subitem1~10のテストケースを自動作成するスクリプト

使用方法:
    python generate_subitem_tests.py [--output-dir OUTPUT_DIR] [--test-case TEST_CASE_NAME]

例:
    # 全てのテストケースを生成
    python generate_subitem_tests.py

    # 特定のテストケースのみ生成
    python generate_subitem_tests.py --test-case 26_column_list_non_label_first_column

    # 出力ディレクトリを指定
    python generate_subitem_tests.py --output-dir test_generated
"""

import os
import sys
import argparse
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Tuple
import shutil

# label_utilsをインポート（相対パスで）
script_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(script_dir))
try:
    from utils.label_utils import detect_label_id
except ImportError as e:
    # フォールバック: 簡易的な判定関数を定義
    print(f"警告: label_utilsのインポートに失敗しました: {e}", file=sys.stderr)
    def detect_label_id(text: str, exclude_label_ids=None):
        """簡易的なラベル判定（label_utilsがインポートできない場合のフォールバック）"""
        if not text or not text.strip():
            return None
        text = text.strip()
        # 基本的なラベルパターンをチェック
        if (text.startswith('（') and text.endswith('）')) or \
           text.isdigit() or \
           (len(text) == 1 and text.isalpha()) or \
           text.endswith('）') or \
           text in ['①', '②', '③', '④', '⑤', '⑥', '⑦', '⑧', '⑨', '⑩']:
            return 'label'  # ダミーのラベルID
        return None


# XML名前空間の定義
NAMESPACES = {
    '': 'http://www.w3.org/XML/1998/namespace'
}

# 要素名のマッピング
ELEMENT_MAPPING = {
    'item': {
        'parent': 'Paragraph',
        'element': 'Item',
        'title': 'ItemTitle',
        'sentence': 'ItemSentence',
    },
    'subitem1': {
        'parent': 'Item',
        'element': 'Subitem1',
        'title': 'Subitem1Title',
        'sentence': 'Subitem1Sentence',
    },
    'subitem2': {
        'parent': 'Subitem1',
        'element': 'Subitem2',
        'title': 'Subitem2Title',
        'sentence': 'Subitem2Sentence',
    },
    'subitem3': {
        'parent': 'Subitem2',
        'element': 'Subitem3',
        'title': 'Subitem3Title',
        'sentence': 'Subitem3Sentence',
    },
    'subitem4': {
        'parent': 'Subitem3',
        'element': 'Subitem4',
        'title': 'Subitem4Title',
        'sentence': 'Subitem4Sentence',
    },
    'subitem5': {
        'parent': 'Subitem4',
        'element': 'Subitem5',
        'title': 'Subitem5Title',
        'sentence': 'Subitem5Sentence',
    },
    'subitem6': {
        'parent': 'Subitem5',
        'element': 'Subitem6',
        'title': 'Subitem6Title',
        'sentence': 'Subitem6Sentence',
    },
    'subitem7': {
        'parent': 'Subitem6',
        'element': 'Subitem7',
        'title': 'Subitem7Title',
        'sentence': 'Subitem7Sentence',
    },
    'subitem8': {
        'parent': 'Subitem7',
        'element': 'Subitem8',
        'title': 'Subitem8Title',
        'sentence': 'Subitem8Sentence',
    },
    'subitem9': {
        'parent': 'Subitem8',
        'element': 'Subitem9',
        'title': 'Subitem9Title',
        'sentence': 'Subitem9Sentence',
    },
    'subitem10': {
        'parent': 'Subitem9',
        'element': 'Subitem10',
        'title': 'Subitem10Title',
        'sentence': 'Subitem10Sentence',
    },
}


def get_base_path() -> Path:
    """スクリプトのベースパスを取得"""
    return Path(__file__).parent


def get_item_test_cases() -> List[str]:
    """convert_item_step0のテストケース一覧を取得"""
    item_dir = get_base_path() / 'convert_item_step0'
    if not item_dir.exists():
        return []
    
    test_cases = []
    for item in item_dir.iterdir():
        if item.is_dir() and not item.name.startswith('_') and item.name != 'test_generated':
            test_cases.append(item.name)
    
    return sorted(test_cases)


def read_xml(file_path: Path) -> ET.Element:
    """XMLファイルを読み込む"""
    tree = ET.parse(file_path)
    return tree.getroot()


def write_xml(root: ET.Element, file_path: Path):
    """XMLファイルに書き込む"""
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    tree.write(file_path, encoding='utf-8', xml_declaration=True)


def create_parent_element(parent_name: str, num: int = 1, title: str = "", sentence_text: str = "") -> ET.Element:
    """親要素を作成"""
    parent_elem = ET.Element(parent_name)
    parent_elem.set('Num', str(num))
    
    # Title要素を追加
    title_elem = ET.SubElement(parent_elem, f'{parent_name.replace("item", "Item").replace("subitem", "Subitem")}Title')
    if title:
        title_elem.text = title
    
    # Sentence要素を追加
    sentence_elem = ET.SubElement(parent_elem, f'{parent_name.replace("item", "Item").replace("subitem", "Subitem")}Sentence')
    if sentence_text:
        sentence = ET.SubElement(sentence_elem, 'Sentence')
        sentence.set('Num', '1')
        sentence.text = sentence_text
    
    return parent_elem


def get_subitem_label(subitem_level: int) -> str:
    """subitemレベルに応じたラベルを取得"""
    labels = {
        1: '（ア）',
        2: 'a',
        3: '（a）',
        4: '（イ）',
        5: 'b',
        6: '（b）',
        7: '（ウ）',
        8: 'c',
        9: '（c）',
        10: '（エ）',
    }
    return labels.get(subitem_level, '（ア）')


def convert_item_input_to_subitem_input(item_input_root: ET.Element, subitem_level: int) -> ET.Element:
    """itemのinput.xmlをsubitemのinput.xmlに変換
    
    処理フロー:
    1. 全要素をコピー（値はそのまま）
    2. Paragraph要素を、検証対象の親要素（subitem1の場合はItem要素）に変換
    3. Item要素を検証対象の要素（subitem1の場合はSubitem1要素）に変換
    """
    # Law要素をコピー
    law_elem = ET.Element('Law')
    
    # LawBodyをコピー
    law_body_elem = item_input_root.find('.//LawBody')
    if law_body_elem is None:
        law_body = ET.SubElement(law_elem, 'LawBody')
    else:
        law_body = ET.SubElement(law_elem, 'LawBody')
    
    # MainProvisionまたはParagraph要素を取得
    main_provision = item_input_root.find('.//MainProvision')
    paragraph = item_input_root.find('.//Paragraph')
    
    if main_provision is not None:
        new_main_provision = ET.SubElement(law_body, 'MainProvision')
        if paragraph is not None:
            new_paragraph = ET.SubElement(new_main_provision, 'Paragraph')
        else:
            new_paragraph = ET.SubElement(new_main_provision, 'Paragraph')
    else:
        if paragraph is not None:
            new_paragraph = ET.SubElement(law_body, 'Paragraph')
        else:
            new_paragraph = ET.SubElement(law_body, 'Paragraph')
    
    # 1. 全要素をコピー（値はそのまま）
    if paragraph is not None:
        new_paragraph.set('Num', paragraph.get('Num', '1'))
        
        # ParagraphNumをコピー
        paragraph_num = paragraph.find('ParagraphNum')
        if paragraph_num is not None:
            new_paragraph_num = ET.SubElement(new_paragraph, 'ParagraphNum')
            new_paragraph_num.text = paragraph_num.text
        
        # ParagraphSentenceをコピー
        paragraph_sentence = paragraph.find('ParagraphSentence')
        if paragraph_sentence is not None:
            new_paragraph_sentence = ET.SubElement(new_paragraph, 'ParagraphSentence')
            for sentence in paragraph_sentence.findall('Sentence'):
                new_sentence = ET.SubElement(new_paragraph_sentence, 'Sentence')
                new_sentence.set('Num', sentence.get('Num', '1'))
                if sentence.text:
                    new_sentence.text = sentence.text
                # 子要素もコピー
                for child in sentence:
                    new_child = ET.SubElement(new_sentence, child.tag)
                    copy_element(child, new_child)
    
    # 2. Paragraph要素を、検証対象の親要素（subitem1の場合はItem要素）に変換
    # 親要素の階層を構築
    current_parent = new_paragraph
    
    # Item要素を作成（subitem1の場合）
    if subitem_level >= 1:
        item_elem = ET.SubElement(current_parent, 'Item')
        item_elem.set('Num', '1')
        item_title = ET.SubElement(item_elem, 'ItemTitle')
        item_title.text = '（１）'
        item_sentence = ET.SubElement(item_elem, 'ItemSentence')
        sentence = ET.SubElement(item_sentence, 'Sentence')
        sentence.set('Num', '1')
        sentence.text = 'Itemの内容'
        current_parent = item_elem
    
    # Subitem1要素を作成（subitem2の場合）
    if subitem_level >= 2:
        subitem1_elem = ET.SubElement(current_parent, 'Subitem1')
        subitem1_elem.set('Num', '1')
        subitem1_title = ET.SubElement(subitem1_elem, 'Subitem1Title')
        subitem1_title.text = 'ア'
        subitem1_sentence = ET.SubElement(subitem1_elem, 'Subitem1Sentence')
        sentence = ET.SubElement(subitem1_sentence, 'Sentence')
        sentence.set('Num', '1')
        sentence.text = 'Subitem1の内容'
        current_parent = subitem1_elem
    
    # Subitem2~9要素を作成
    for level in range(3, subitem_level + 1):
        subitem_name = f'Subitem{level - 1}'
        subitem_elem = ET.SubElement(current_parent, subitem_name)
        subitem_elem.set('Num', '1')
        subitem_title = ET.SubElement(subitem_elem, f'{subitem_name}Title')
        subitem_title.text = get_subitem_label(level - 1)
        subitem_sentence = ET.SubElement(subitem_elem, f'{subitem_name}Sentence')
        sentence = ET.SubElement(subitem_sentence, 'Sentence')
        sentence.set('Num', '1')
        sentence.text = f'{subitem_name}の内容'
        current_parent = subitem_elem
    
    # Paragraph要素内の子要素を取得
    lists = paragraph.findall('List') if paragraph is not None else []
    non_list_elements = []
    if paragraph is not None:
        non_list_elements = paragraph.findall('TableStruct') + paragraph.findall('FigStruct') + paragraph.findall('StyleStruct')
    
    # Paragraph要素内のList要素を親要素（Item要素など）にコピー（値はそのまま）
    for list_elem in lists:
        new_list = ET.SubElement(current_parent, 'List')
        copy_element(list_elem, new_list)
    
    # Paragraph要素内の非List要素を親要素にコピー
    for non_list_elem in non_list_elements:
        new_non_list = ET.SubElement(current_parent, non_list_elem.tag)
        copy_element(non_list_elem, new_non_list)
    
    return law_elem


def copy_element(source: ET.Element, target: ET.Element):
    """要素を深いコピー"""
    target.text = source.text
    target.tail = source.tail
    
    # 属性をコピー
    for key, value in source.attrib.items():
        target.set(key, value)
    
    # 子要素をコピー
    for child in source:
        new_child = ET.SubElement(target, child.tag)
        copy_element(child, new_child)


def convert_item_expected_to_subitem_expected(item_expected_root: ET.Element, subitem_level: int) -> ET.Element:
    """itemのexpected.xmlをsubitemのexpected.xmlに変換
    
    処理フロー:
    1. 全要素をコピー（値はそのまま）
    2. Paragraph要素を、検証対象の親要素（subitem1の場合はItem要素）に変換
    3. Item要素を検証対象の要素（subitem1の場合はSubitem1要素）に変換
    """
    # Law要素をコピー
    law_elem = ET.Element('Law')
    
    # LawBodyをコピー
    law_body_elem = item_expected_root.find('.//LawBody')
    if law_body_elem is None:
        law_body = ET.SubElement(law_elem, 'LawBody')
    else:
        law_body = ET.SubElement(law_elem, 'LawBody')
    
    # MainProvisionまたはParagraph要素を取得
    main_provision = item_expected_root.find('.//MainProvision')
    paragraph = item_expected_root.find('.//Paragraph')
    
    if main_provision is not None:
        new_main_provision = ET.SubElement(law_body, 'MainProvision')
        if paragraph is not None:
            new_paragraph = ET.SubElement(new_main_provision, 'Paragraph')
        else:
            new_paragraph = ET.SubElement(new_main_provision, 'Paragraph')
    else:
        if paragraph is not None:
            new_paragraph = ET.SubElement(law_body, 'Paragraph')
        else:
            new_paragraph = ET.SubElement(law_body, 'Paragraph')
    
    # 1. 全要素をコピー（値はそのまま）
    if paragraph is not None:
        new_paragraph.set('Num', paragraph.get('Num', '1'))
        
        # ParagraphNumをコピー
        paragraph_num = paragraph.find('ParagraphNum')
        if paragraph_num is not None:
            new_paragraph_num = ET.SubElement(new_paragraph, 'ParagraphNum')
            new_paragraph_num.text = paragraph_num.text
        
        # ParagraphSentenceをコピー
        paragraph_sentence = paragraph.find('ParagraphSentence')
        if paragraph_sentence is not None:
            new_paragraph_sentence = ET.SubElement(new_paragraph, 'ParagraphSentence')
            for sentence in paragraph_sentence.findall('Sentence'):
                new_sentence = ET.SubElement(new_paragraph_sentence, 'Sentence')
                new_sentence.set('Num', sentence.get('Num', '1'))
                if sentence.text:
                    new_sentence.text = sentence.text
    
    # 2. Paragraph要素を、検証対象の親要素（subitem1の場合はItem要素）に変換
    # 親要素の階層を構築
    current_parent = new_paragraph
    
    # Item要素を作成（subitem1の場合）
    if subitem_level >= 1:
        item_elem = ET.SubElement(current_parent, 'Item')
        item_elem.set('Num', '1')
        item_title = ET.SubElement(item_elem, 'ItemTitle')
        item_title.text = '（１）'
        item_sentence = ET.SubElement(item_elem, 'ItemSentence')
        sentence = ET.SubElement(item_sentence, 'Sentence')
        sentence.set('Num', '1')
        sentence.text = 'Itemの内容'
        current_parent = item_elem
    
    # Subitem1要素を作成（subitem2の場合）
    if subitem_level >= 2:
        subitem1_elem = ET.SubElement(current_parent, 'Subitem1')
        subitem1_elem.set('Num', '1')
        subitem1_title = ET.SubElement(subitem1_elem, 'Subitem1Title')
        subitem1_title.text = 'ア'
        subitem1_sentence = ET.SubElement(subitem1_elem, 'Subitem1Sentence')
        sentence = ET.SubElement(subitem1_sentence, 'Sentence')
        sentence.set('Num', '1')
        sentence.text = 'Subitem1の内容'
        current_parent = subitem1_elem
    
    # Subitem2~9要素を作成
    for level in range(3, subitem_level + 1):
        subitem_name = f'Subitem{level - 1}'
        subitem_elem = ET.SubElement(current_parent, subitem_name)
        subitem_elem.set('Num', '1')
        subitem_title = ET.SubElement(subitem_elem, f'{subitem_name}Title')
        subitem_title.text = get_subitem_label(level - 1)
        subitem_sentence = ET.SubElement(subitem_elem, f'{subitem_name}Sentence')
        sentence = ET.SubElement(subitem_sentence, 'Sentence')
        sentence.set('Num', '1')
        sentence.text = f'{subitem_name}の内容'
        current_parent = subitem_elem
    
    # Paragraph要素内の子要素を取得
    items = paragraph.findall('Item') if paragraph is not None else []
    lists = paragraph.findall('List') if paragraph is not None else []
    non_list_elements = []
    if paragraph is not None:
        non_list_elements = paragraph.findall('TableStruct') + paragraph.findall('FigStruct') + paragraph.findall('StyleStruct')
    
    # Paragraph要素内のList要素を親要素（Item要素など）にコピー
    for list_elem in lists:
        new_list = ET.SubElement(current_parent, 'List')
        copy_element(list_elem, new_list)
    
    # Paragraph要素内の非List要素を親要素にコピー
    for non_list_elem in non_list_elements:
        new_non_list = ET.SubElement(current_parent, non_list_elem.tag)
        copy_element(non_list_elem, new_non_list)
    
    # 3. Item要素を検証対象の要素（subitem1の場合はSubitem1要素）に変換
    subitem_name = f'Subitem{subitem_level}'
    subitem_title_name = f'{subitem_name}Title'
    subitem_sentence_name = f'{subitem_name}Sentence'
    
    for item_idx, item in enumerate(items):
        # Item要素をSubitem要素に変換
        subitem_elem = ET.SubElement(current_parent, subitem_name)
        subitem_elem.set('Num', item.get('Num', str(item_idx + 1)))
        
        # ItemTitleをSubitemTitleに変換（値はそのままコピー）
        item_title = item.find('ItemTitle')
        if item_title is not None:
            subitem_title = ET.SubElement(subitem_elem, subitem_title_name)
            # 値はそのままコピー
            subitem_title.text = item_title.text if item_title.text else ''
            # 子要素もコピー
            for child in item_title:
                new_child = ET.SubElement(subitem_title, child.tag)
                copy_element(child, new_child)
        
        # ItemSentenceをSubitemSentenceに変換（値はそのままコピー）
        item_sentence = item.find('ItemSentence')
        if item_sentence is not None:
            subitem_sentence = ET.SubElement(subitem_elem, subitem_sentence_name)
            for sentence in item_sentence.findall('Sentence'):
                new_sentence = ET.SubElement(subitem_sentence, 'Sentence')
                new_sentence.set('Num', sentence.get('Num', '1'))
                if sentence.text:
                    new_sentence.text = sentence.text
                # 子要素もコピー
                for child in sentence:
                    new_child = ET.SubElement(new_sentence, child.tag)
                    copy_element(child, new_child)
        
        # Item内のその他の要素をコピー（List要素、Subitem1, Subitem2、TableStructなど）
        # 値はそのままコピーして、構造のみを変更
        for child in item:
            if child.tag not in ['ItemTitle', 'ItemSentence']:
                new_child = ET.SubElement(subitem_elem, child.tag)
                copy_element(child, new_child)
    
    return law_elem


def generate_subitem_test_case(test_case_name: str, subitem_level: int, output_base_dir: Path):
    """特定のテストケースをsubitemレベルに変換して生成"""
    item_dir = get_base_path() / 'convert_item_step0' / test_case_name
    if not item_dir.exists():
        print(f"警告: テストケース '{test_case_name}' が見つかりません")
        return False
    
    # 出力ディレクトリを作成
    output_dir = output_base_dir / f'convert_subitem{subitem_level}_step0' / test_case_name
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # input.xmlを変換
    input_file = item_dir / 'input.xml'
    if input_file.exists():
        item_input_root = read_xml(input_file)
        subitem_input_root = convert_item_input_to_subitem_input(item_input_root, subitem_level)
        
        output_input_file = output_dir / 'input.xml'
        write_xml(subitem_input_root, output_input_file)
        print(f"  生成: {output_input_file}")
    else:
        print(f"  警告: input.xmlが見つかりません: {input_file}")
    
    # expected.xmlを変換
    expected_file = item_dir / 'expected.xml'
    if expected_file.exists():
        item_expected_root = read_xml(expected_file)
        subitem_expected_root = convert_item_expected_to_subitem_expected(item_expected_root, subitem_level)
        
        output_expected_file = output_dir / 'expected.xml'
        write_xml(subitem_expected_root, output_expected_file)
        print(f"  生成: {output_expected_file}")
    else:
        print(f"  警告: expected.xmlが見つかりません: {expected_file}")
    
    # README.mdをコピー（存在する場合）
    readme_file = item_dir / 'README.md'
    if readme_file.exists():
        shutil.copy(readme_file, output_dir / 'README.md')
        print(f"  コピー: {readme_file} -> {output_dir / 'README.md'}")
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description='item要素のテストケースをベースとして、subitem1~10のテストケースを自動作成'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='test_generated',
        help='出力ディレクトリ名（デフォルト: test_generated）'
    )
    parser.add_argument(
        '--test-case',
        type=str,
        help='特定のテストケース名のみ生成（指定しない場合は全て生成）'
    )
    parser.add_argument(
        '--subitem-levels',
        type=str,
        default='1-10',
        help='生成するsubitemレベル（例: 1-10, 1,2,3）'
    )
    
    args = parser.parse_args()
    
    # 出力ディレクトリを設定
    output_base_dir = get_base_path() / args.output_dir
    
    # subitemレベルを解析
    if '-' in args.subitem_levels:
        start, end = map(int, args.subitem_levels.split('-'))
        subitem_levels = list(range(start, end + 1))
    else:
        subitem_levels = [int(x) for x in args.subitem_levels.split(',')]
    
    # テストケースを取得
    if args.test_case:
        test_cases = [args.test_case]
    else:
        test_cases = get_item_test_cases()
    
    if not test_cases:
        print("エラー: テストケースが見つかりません")
        return 1
    
    print(f"テストケース生成を開始します...")
    print(f"  ベースディレクトリ: {get_base_path() / 'convert_item_step0'}")
    print(f"  出力ディレクトリ: {output_base_dir}")
    print(f"  生成対象レベル: subitem{subitem_levels}")
    print(f"  テストケース数: {len(test_cases)}")
    print()
    
    success_count = 0
    for test_case in test_cases:
        print(f"処理中: {test_case}")
        for level in subitem_levels:
            print(f"  subitem{level}を生成中...")
            if generate_subitem_test_case(test_case, level, output_base_dir):
                success_count += 1
        print()
    
    print(f"完了: {success_count}個のテストケースを生成しました")
    return 0


if __name__ == '__main__':
    sys.exit(main())










