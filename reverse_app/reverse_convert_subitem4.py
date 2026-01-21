#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Subitem4要素をList要素に逆変換するスクリプト

Subitem3要素内のSubitem4要素をList要素に変換する。
- Subitem4Titleがある場合: 2カラムのList要素（Column1: Subitem4Title, Column2: Subitem4Sentence）
- Subitem4Titleがない場合: ColumnなしのList要素
"""

import sys
from pathlib import Path

# 共通モジュールをインポート
sys.path.insert(0, str(Path(__file__).resolve().parent))
from reverse_xml_converter import ReverseConversionConfig, main_with_config


def main():
    """メイン関数"""
    # Subitem4逆変換の設定
    config = ReverseConversionConfig(
        parent_tag='Subitem3',
        child_tag='Subitem4',
        title_tag='Subitem4Title',
        sentence_tag='Subitem4Sentence',
        script_name='reverse_convert_subitem4'
    )

    return main_with_config(
        config,
        description='Subitem4要素をList要素に逆変換するスクリプト',
        default_output_suffix='_reverse_subitem4.xml'
    )


if __name__ == '__main__':
    sys.exit(main())
