#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Subitem8要素をList要素に逆変換するスクリプト

Subitem7要素内のSubitem8要素をList要素に変換する。
- Subitem8Titleがある場合: 2カラムのList要素（Column1: Subitem8Title, Column2: Subitem8Sentence）
- Subitem8Titleがない場合: ColumnなしのList要素
"""

import sys
from pathlib import Path

# 共通モジュールをインポート
sys.path.insert(0, str(Path(__file__).resolve().parent))
from reverse_xml_converter import ReverseConversionConfig, main_with_config


def main():
    """メイン関数"""
    # Subitem8逆変換の設定
    config = ReverseConversionConfig(
        parent_tag='Subitem7',
        child_tag='Subitem8',
        title_tag='Subitem8Title',
        sentence_tag='Subitem8Sentence',
        script_name='reverse_convert_subitem8'
    )

    return main_with_config(
        config,
        description='Subitem8要素をList要素に逆変換するスクリプト',
        default_output_suffix='_reverse_subitem8.xml'
    )


if __name__ == '__main__':
    sys.exit(main())
