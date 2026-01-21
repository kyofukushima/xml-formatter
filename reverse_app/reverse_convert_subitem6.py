#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Subitem6要素をList要素に逆変換するスクリプト

Subitem5要素内のSubitem6要素をList要素に変換する。
- Subitem6Titleがある場合: 2カラムのList要素（Column1: Subitem6Title, Column2: Subitem6Sentence）
- Subitem6Titleがない場合: ColumnなしのList要素
"""

import sys
from pathlib import Path

# 共通モジュールをインポート
sys.path.insert(0, str(Path(__file__).resolve().parent))
from reverse_xml_converter import ReverseConversionConfig, main_with_config


def main():
    """メイン関数"""
    # Subitem6逆変換の設定
    config = ReverseConversionConfig(
        parent_tag='Subitem5',
        child_tag='Subitem6',
        title_tag='Subitem6Title',
        sentence_tag='Subitem6Sentence',
        script_name='reverse_convert_subitem6'
    )

    return main_with_config(
        config,
        description='Subitem6要素をList要素に逆変換するスクリプト',
        default_output_suffix='_reverse_subitem6.xml'
    )


if __name__ == '__main__':
    sys.exit(main())
