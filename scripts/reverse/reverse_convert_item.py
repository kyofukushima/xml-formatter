#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Item要素をList要素に逆変換するスクリプト

Paragraph要素内のItem要素をList要素に変換する。
- ItemTitleがある場合: 2カラムのList要素（Column1: ItemTitle, Column2: ItemSentence）
- ItemTitleがない場合: ColumnなしのList要素
"""

import sys
import argparse
from pathlib import Path

# 共通モジュールをインポート
sys.path.insert(0, str(Path(__file__).resolve().parent))
from reverse_xml_converter import ReverseConversionConfig, process_xml_file


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description='Item要素をList要素に逆変換するスクリプト',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
使用例:
  python3 reverse_convert_item.py input.xml
  python3 reverse_convert_item.py input.xml output.xml
        '''
    )

    parser.add_argument('input_file', help='入力XMLファイル')
    parser.add_argument('output_file', nargs='?', help='出力XMLファイル（デフォルト: _reverse_item.xml）')

    args = parser.parse_args()

    input_path = Path(args.input_file)

    if not input_path.exists():
        print(f"エラー: 入力ファイルが見つかりません: {args.input_file}", file=sys.stderr)
        return 1

    output_path = Path(args.output_file) if args.output_file else input_path.parent / f"{input_path.stem}_reverse_item.xml"

    # Item逆変換の設定
    config = ReverseConversionConfig(
        parent_tag='Paragraph',
        child_tag='Item',
        title_tag='ItemTitle',
        sentence_tag='ItemSentence',
        script_name='reverse_convert_item'
    )

    return process_xml_file(input_path, output_path, config)


if __name__ == '__main__':
    sys.exit(main())
