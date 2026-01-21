#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Subitem1要素をList要素に逆変換するスクリプト

Item要素内のSubitem1要素をList要素に変換する。
- Subitem1Titleがある場合: 2カラムのList要素（Column1: Subitem1Title, Column2: Subitem1Sentence）
- Subitem1Titleがない場合: ColumnなしのList要素
"""

import sys
from pathlib import Path

# 共通モジュールをインポート
sys.path.insert(0, str(Path(__file__).resolve().parent))
from reverse_xml_converter import ReverseConversionConfig, main_with_config


def main():
    """メイン関数"""
    # Subitem1逆変換の設定
    config = ReverseConversionConfig(
        parent_tag='Item',
        child_tag='Subitem1',
        title_tag='Subitem1Title',
        sentence_tag='Subitem1Sentence',
        script_name='reverse_convert_subitem1'
    )

    return main_with_config(
        config,
        description='Subitem1要素をList要素に逆変換するスクリプト',
        default_output_suffix='_reverse_subitem1.xml'
    )


if __name__ == '__main__':
    sys.exit(main())
