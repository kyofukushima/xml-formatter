#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Subitem10要素をList要素に逆変換するスクリプト

Subitem9要素内のSubitem10要素をList要素に変換する。
- Subitem10Titleがある場合: 2カラムのList要素（Column1: Subitem10Title, Column2: Subitem10Sentence）
- Subitem10Titleがない場合: ColumnなしのList要素
"""

import sys
from pathlib import Path

# 共通モジュールをインポート
sys.path.insert(0, str(Path(__file__).resolve().parent))
from reverse_xml_converter import ReverseConversionConfig, main_with_config


def main():
    """メイン関数"""
    # Subitem10逆変換の設定
    config = ReverseConversionConfig(
        parent_tag='Subitem9',
        child_tag='Subitem10',
        title_tag='Subitem10Title',
        sentence_tag='Subitem10Sentence',
        script_name='reverse_convert_subitem10'
    )

    return main_with_config(
        config,
        description='Subitem10要素をList要素に逆変換するスクリプト',
        default_output_suffix='_reverse_subitem10.xml'
    )


if __name__ == '__main__':
    sys.exit(main())
