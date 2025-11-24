#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Subitem1要素変換ロジック実装スクリプト（共通化版）

xml_converter.pyを使用してItem要素内のList要素をSubitem1要素に変換する。
"""

import sys
import argparse
from pathlib import Path

# 共通モジュールをインポート
from xml_converter import ConversionConfig, process_xml_file


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description='Subitem1要素変換ロジック実装スクリプト（共通化版）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
使用例:
  python3 convert_subitem1_step0.py input.xml
  python3 convert_subitem1_step0.py input.xml output.xml
        '''
    )

    parser.add_argument('input_file', help='入力XMLファイル')
    parser.add_argument('output_file', nargs='?', help='出力XMLファイル（デフォルト: _subitem1_step0.xml）')

    args = parser.parse_args()

    input_path = Path(args.input_file)

    if not input_path.exists():
        print(f"エラー: 入力ファイルが見つかりません: {args.input_file}", file=sys.stderr)
        return 1

    output_path = Path(args.output_file) if args.output_file else input_path.parent / f"{input_path.stem}_subitem1_step0.xml"

    # Subitem1変換の設定
    config = ConversionConfig(
        parent_tag='Item',
        child_tag='Subitem1',
        title_tag='Subitem1Title',
        sentence_tag='Subitem1Sentence',
        column_condition_min=1,  # Subitem1は col_count >= 1
        supported_types=['labeled', 'subject_name', 'instruction', 'grade_single', 'grade_double'],
        script_name='convert_subitem1_step0',
        skip_empty_parent=True  # Subitem1変換では親要素チェックを行う
    )

    return process_xml_file(input_path, output_path, config)


if __name__ == '__main__':
    sys.exit(main())
