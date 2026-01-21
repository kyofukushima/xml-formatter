#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Subitem7要素をList要素に逆変換するスクリプト

Subitem6要素内のSubitem7要素をList要素に変換する。
- Subitem7Titleがある場合: 2カラムのList要素（Column1: Subitem7Title, Column2: Subitem7Sentence）
- Subitem7Titleがない場合: ColumnなしのList要素
"""

import sys
from pathlib import Path

# 共通モジュールをインポート
sys.path.insert(0, str(Path(__file__).resolve().parent))
from reverse_xml_converter import ReverseConversionConfig, main_with_config


def main():
    """メイン関数"""
    # Subitem7逆変換の設定
    config = ReverseConversionConfig(
        parent_tag='Subitem6',
        child_tag='Subitem7',
        title_tag='Subitem7Title',
        sentence_tag='Subitem7Sentence',
        script_name='reverse_convert_subitem7'
    )

    return main_with_config(
        config,
        description='Subitem7要素をList要素に逆変換するスクリプト',
        default_output_suffix='_reverse_subitem7.xml'
    )


if __name__ == '__main__':
    sys.exit(main())
