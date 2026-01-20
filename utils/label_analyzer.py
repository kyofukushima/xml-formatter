"""
ラベル種類判定ユーティリティ

XMLファイルからList要素のColumn要素の1つ目を抽出し、
ラベル種類を判定する機能を提供します。
"""
import sys
import importlib.util
from pathlib import Path
from typing import List, Set, Tuple, Dict, Optional, TYPE_CHECKING
from lxml import etree
import pandas as pd

# scripts/utils/label_utils.pyを直接インポート
project_root = Path(__file__).resolve().parent.parent
label_utils_path = project_root / "scripts" / "utils" / "label_utils.py"

# モジュールを動的に読み込む
spec = importlib.util.spec_from_file_location("label_utils", label_utils_path)
label_utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(label_utils)

LabelConfig = label_utils.LabelConfig
detect_label_id = label_utils.detect_label_id

# 型チェック用の型エイリアス（実行時にはLabelConfigと同じ）
LabelConfigType = LabelConfig


def extract_list_column1_values(xml_path: Path) -> Tuple[Set[str], bool]:
    """
    XMLファイルからすべてのList要素のColumn要素の1つ目の値を抽出し、
    重複を排除してセットに格納
    
    Args:
        xml_path: XMLファイルのパス
        
    Returns:
        Tuple[Set[str], bool]: (Column要素の1つ目の値のセット（重複排除済み）, ColumnありのList要素が存在するかどうか)
    """
    try:
        tree = etree.parse(str(xml_path))
        root = tree.getroot()
    except Exception as e:
        raise ValueError(f"XMLファイルの読み込みに失敗しました: {e}")
    
    column1_values = set()
    has_column_list = False
    
    # すべてのList要素を検索
    for list_elem in root.iter('List'):
        # List要素からColumn要素を取得
        columns = list_elem.findall('.//Column')
        
        if len(columns) >= 1:
            has_column_list = True
            # 1つ目のColumn要素からSentence要素を取得
            col1 = columns[0]
            sentence = col1.find('.//Sentence')
            
            if sentence is not None:
                # テキストを取得
                text = "".join(sentence.itertext()).strip()
                if text:
                    column1_values.add(text)
    
    return column1_values, has_column_list


def analyze_label_types(column1_values: Set[str], label_config: Optional[LabelConfigType] = None) -> pd.DataFrame:
    """
    セットから値を取り出し、どのラベル要素か判定し、
    すべての値に対して判定を実施
    
    Args:
        column1_values: Column要素の1つ目の値のセット
        label_config: ラベル設定（Noneの場合はデフォルト設定を使用）
        
    Returns:
        pd.DataFrame: 判定結果の表（ラベル要素、値の2列構成）
    """
    if label_config is None:
        label_config = LabelConfig()
    
    results = []
    
    # すべての値に対して判定を実施
    for value in sorted(column1_values):
        label_id = detect_label_id(value)
        
        if label_id:
            # ラベル定義から名前を取得
            label_def = label_config.get_label_definition(label_id)
            label_name = label_def.get('name', label_id) if label_def else label_id
        else:
            label_id = "unknown"
            label_name = "不明"
        
        results.append({
            'ラベル要素': label_name,
            '値': value
        })
    
    # DataFrameに変換
    df = pd.DataFrame(results)
    
    # ラベル要素でソート（値も併せてソート）
    df = df.sort_values(['ラベル要素', '値'], ascending=[True, True])
    
    return df


def analyze_xml_labels(xml_path: Path, label_config: Optional[LabelConfigType] = None) -> Tuple[Optional[pd.DataFrame], bool]:
    """
    XMLファイルからList要素のColumn要素の1つ目を抽出し、
    ラベル種類を判定して表にまとめる
    
    処理の流れ:
    1. List要素のColumn要素の1つ目を抽出
    2. セットに格納（重複排除のため）
    3. すべてのList要素に対し上記実施
    4. 作成したセットから値を取り出し、どのラベル要素か判定
    5. すべての値に対して判定を実施
    6. 判定結果を表にまとめる（ラベル要素、値の2列構成）
    
    Args:
        xml_path: XMLファイルのパス
        label_config: ラベル設定（Noneの場合はデフォルト設定を使用）
        
    Returns:
        Tuple[Optional[pd.DataFrame], bool]: (判定結果の表（ラベル要素、値の2列構成）, ColumnありのList要素が存在するかどうか)
        ColumnありのList要素がない場合は (None, False) を返す
    """
    # Column要素の1つ目の値を抽出（重複排除済み）
    column1_values, has_column_list = extract_list_column1_values(xml_path)
    
    # ColumnありのList要素がない場合
    if not has_column_list:
        return None, False
    
    # ラベル種類を判定して表にまとめる
    result_df = analyze_label_types(column1_values, label_config)
    
    return result_df, True
