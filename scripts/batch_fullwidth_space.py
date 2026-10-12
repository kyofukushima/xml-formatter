#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文頭全角スペース補填の一括実行スクリプト（フォルダ / ZIP / 複数XML対応）

Webアプリ「文頭スペース補填」ページと同じロジック
（postprocess_fullwidth_space.py の add モード）を、フォルダ・ZIP・
複数XMLファイルに対してまとめて適用する。フォルダ階層は保ったまま出力する。

使用例:
  # フォルダ内のXML（サブフォルダ含む）を補填し、<フォルダ名>_space/ に出力
  python scripts/batch_fullwidth_space.py input_dir/

  # 出力先を指定（フォルダ）
  python scripts/batch_fullwidth_space.py input_dir/ -o output_dir/

  # ZIPを入力にしてZIPで出力
  python scripts/batch_fullwidth_space.py input.zip -o output.zip

  # 複数XMLを指定
  python scripts/batch_fullwidth_space.py a.xml b.xml -o output_dir/

  # 元のファイル名のまま出力（_space を付けない）、結果一覧をCSVに保存
  python scripts/batch_fullwidth_space.py input_dir/ --keep-names --csv result.csv

オプション（Webアプリと同一）:
  --include-list    List内のSentenceも対象にする
  --exclude-paren   「（」で始まるSentenceは対象外にする
  --include-vardef  変数定義行（「Ｅ：…」等の短い記号列）も対象にする
  --keep-names      出力ファイル名を元のままにする（既定は <元の名前>_space.xml）

終了コード: 0=すべて成功、1=引数エラー、2=一部または全部のファイルでエラー
"""
import argparse
import csv
import sys
import zipfile
from io import BytesIO
from pathlib import Path

from lxml import etree

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
# scripts/utils と utils/ の名前衝突を避けるため、プロジェクトルートを最優先にする
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(PROJECT_ROOT))

import postprocess_fullwidth_space as pp  # noqa: E402
from utils.upload_helpers import (  # noqa: E402
    decode_zip_name, is_target_zip_entry, split_upload_path,
)

RESULT_KEYS = ["パス", "結果", "対象Sentence数", "補填実施",
               "「（」始まりで除外", "変数定義行で除外", "備考"]


def apply_fullwidth_space(data, include_list=False, exclude_paren=False,
                          include_vardef=False):
    """1ファイル分のXMLバイト列に補填を適用し、(結果バイト列, 統計) を返す

    Webアプリ（ホーム / 文頭スペース補填ページ）の補填処理と同一のロジック。
    XML解析に失敗した場合は etree.XMLSyntaxError を送出する。
    """
    tree = etree.parse(BytesIO(data))
    root = tree.getroot()
    targets, excluded_vardefs = pp.collect_target_sentences(
        root, include_list=include_list, include_vardef=include_vardef
    )
    changed = 0
    excluded_parens = 0
    for sentence in targets:
        if exclude_paren and pp.is_insertable(sentence) \
                and pp.starts_with_paren(sentence):
            excluded_parens += 1
            continue
        if pp.add_fullwidth_space(sentence):
            changed += 1

    # 入力の整形を維持したまま書き出す（再インデントしない）
    result_bytes = etree.tostring(
        tree, encoding='UTF-8', xml_declaration=True, pretty_print=False
    )
    stats = {
        "targets": len(targets),
        "changed": changed,
        "excluded_parens": excluded_parens,
        "excluded_vardefs": len(excluded_vardefs),
    }
    return result_bytes, stats


def output_name(file_name, keep_names=False):
    """補填後のファイル名を決める"""
    if keep_names:
        return file_name
    return f"{Path(file_name).stem}_space.xml"


def iter_inputs(paths):
    """入力（フォルダ / ZIP / XML）から (相対パス, バイト列) を順に返す

    - フォルダ: 配下のXML（サブフォルダ含む）。相対パスはフォルダからの相対
    - ZIP: 内部のXML（__MACOSX・隠しファイルは除外）。相対パスはZIP内パス
    - XMLファイル: ファイル名のみ
    """
    for path in paths:
        path = Path(path)
        if path.is_dir():
            for xml_path in sorted(path.rglob("*.xml")):
                rel = xml_path.relative_to(path).as_posix()
                if not is_target_zip_entry(rel):
                    continue
                yield rel, xml_path.read_bytes()
        elif path.suffix.lower() == ".zip":
            with zipfile.ZipFile(path) as zf:
                for info in zf.infolist():
                    name = decode_zip_name(info)
                    if is_target_zip_entry(name):
                        yield name, zf.read(info)
        else:
            yield path.name, path.read_bytes()


def run_batch(inputs, include_list=False, exclude_paren=False,
              include_vardef=False, keep_names=False):
    """(相対パス, バイト列) の列に補填を適用し、(結果行, 出力一覧) を返す

    出力一覧は (出力相対パス, バイト列) のリスト。エラーのファイルは含まない。
    """
    rows = []
    outputs = []
    for rel, data in inputs:
        folders, file_name = split_upload_path(rel)
        row = dict.fromkeys(RESULT_KEYS, "")
        row["パス"] = rel
        try:
            result_bytes, stats = apply_fullwidth_space(
                data, include_list=include_list, exclude_paren=exclude_paren,
                include_vardef=include_vardef
            )
        except etree.XMLSyntaxError as e:
            row["結果"] = "解析エラー"
            row["備考"] = f"XML解析エラー: {e}"
            rows.append(row)
            continue
        row["結果"] = "補填あり" if stats["changed"] else "補填なし"
        row["対象Sentence数"] = stats["targets"]
        row["補填実施"] = stats["changed"]
        row["「（」始まりで除外"] = stats["excluded_parens"]
        row["変数定義行で除外"] = stats["excluded_vardefs"]
        rows.append(row)
        out_rel = "/".join(folders + [output_name(file_name, keep_names)])
        outputs.append((out_rel, result_bytes))
    return rows, outputs


def write_outputs(outputs, output_path):
    """出力一覧をフォルダまたはZIP（拡張子 .zip）に書き出す"""
    output_path = Path(output_path)
    if output_path.suffix.lower() == ".zip":
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for rel, data in outputs:
                zf.writestr(rel, data)
        return
    for rel, data in outputs:
        dest = output_path / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)


def default_output_path(inputs):
    """出力先未指定時の既定値（<入力名>_space）"""
    first = Path(inputs[0])
    if len(inputs) == 1 and first.suffix.lower() == ".zip":
        return first.with_name(f"{first.stem}_space.zip")
    if len(inputs) == 1 and first.is_dir():
        return first.with_name(f"{first.name}_space")
    return first.parent / "fullwidth_space_output"


def print_summary(rows, outputs, output_path):
    ok_rows = [r for r in rows if r["結果"] in ("補填あり", "補填なし")]
    error_rows = [r for r in rows if r not in ok_rows]
    print("=" * 80)
    print("【文頭全角スペース補填（一括）】")
    print("=" * 80)
    for r in rows:
        if r["結果"] in ("補填あり", "補填なし"):
            print(f" - {r['パス']}: {r['結果']} "
                  f"(対象{r['対象Sentence数']} / 補填{r['補填実施']} / "
                  f"（除外{r['「（」始まりで除外']} / 変数定義除外{r['変数定義行で除外']})")
        else:
            print(f" - {r['パス']}: {r['結果']} {r['備考']}")
    print()
    print("処理統計:")
    print(f" - 処理ファイル数: {len(ok_rows)}件（エラー: {len(error_rows)}件）")
    print(f" - 対象Sentence数: {sum(r['対象Sentence数'] for r in ok_rows)}箇所")
    print(f" - 補填実施: {sum(r['補填実施'] for r in ok_rows)}箇所")
    print(f" - 「（」始まりで除外: {sum(r['「（」始まりで除外'] for r in ok_rows)}箇所")
    print(f" - 変数定義行で除外: {sum(r['変数定義行で除外'] for r in ok_rows)}箇所")
    print(f"\n出力先: {output_path}（{len(outputs)}件）")
    print("=" * 80)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description='文頭全角スペース補填の一括実行（フォルダ / ZIP / 複数XML）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split("使用例:", 1)[1]
    )
    parser.add_argument('inputs', nargs='+',
                        help='入力フォルダ / ZIPファイル / XMLファイル（複数可）')
    parser.add_argument('-o', '--output',
                        help='出力先フォルダ、または .zip を指定するとZIPで出力'
                             '（既定: <入力名>_space）')
    parser.add_argument('--include-list', action='store_true',
                        help='List内のSentenceも対象にする')
    parser.add_argument('--exclude-paren', action='store_true',
                        help='「（」で始まるSentenceは対象外にする')
    parser.add_argument('--include-vardef', action='store_true',
                        help='変数定義行（「Ｅ：…」等の短い記号列）も対象にする')
    parser.add_argument('--keep-names', action='store_true',
                        help='出力ファイル名を元のままにする（既定は _space を付与）')
    parser.add_argument('--csv', help='ファイルごとの結果一覧をCSVに保存する')
    args = parser.parse_args(argv)

    missing = [p for p in args.inputs if not Path(p).exists()]
    if missing:
        print(f"エラー: 入力が見つかりません: {', '.join(missing)}", file=sys.stderr)
        return 1

    output_path = Path(args.output) if args.output \
        else default_output_path(args.inputs)

    rows, outputs = run_batch(
        iter_inputs(args.inputs),
        include_list=args.include_list, exclude_paren=args.exclude_paren,
        include_vardef=args.include_vardef, keep_names=args.keep_names
    )
    if not rows:
        print("エラー: 処理対象のXMLファイルがありません", file=sys.stderr)
        return 1

    write_outputs(outputs, output_path)
    if args.csv:
        with open(args.csv, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=RESULT_KEYS)
            writer.writeheader()
            writer.writerows(rows)

    print_summary(rows, outputs, output_path)
    return 2 if any(r["結果"] == "解析エラー" for r in rows) else 0


if __name__ == '__main__':
    sys.exit(main())
