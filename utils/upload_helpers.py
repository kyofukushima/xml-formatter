"""
アップロードファイル（XML / ZIP）の共通ヘルパー

List有無判定・文頭スペース補填など、複数ファイルやZIP化したフォルダを
まとめて処理するページで共有する。
"""
import zipfile
from io import BytesIO


def split_upload_path(name):
    """パスをフォルダ階層とファイル名に分解する"""
    parts = name.replace('\\', '/').split('/')
    parts = [p for p in parts if p]
    if not parts:
        return [], name
    return parts[:-1], parts[-1]


def decode_zip_name(info):
    """ZIP内のファイル名を正しい文字コードで取得する

    ZIPの仕様上、UTF-8フラグが立っていないエントリ名はcp437として
    デコードされるため、日本語名を復元する。macOSのFinder/zipコマンドは
    UTF-8フラグを立てずにUTF-8名を書くことがあり、Windowsのエクスプローラーはcp932で
    書くため、UTF-8→cp932の順に試す（cp932のバイト列が偶然UTF-8として
    妥当になることはほぼないが、逆は起こり得る）。
    """
    if info.flag_bits & 0x800:  # UTF-8フラグ
        return info.filename
    try:
        raw = info.filename.encode('cp437')
    except UnicodeEncodeError:
        return info.filename
    for encoding in ('utf-8', 'cp932'):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return info.filename


def is_target_zip_entry(name):
    """ZIP内エントリが処理対象のXMLファイルかどうか"""
    if name.endswith('/'):
        return False
    parts = [p for p in name.replace('\\', '/').split('/') if p]
    if not parts:
        return False
    # macOSのメタデータ・隠しファイルを除外
    if any(p == '__MACOSX' for p in parts):
        return False
    if parts[-1].startswith('._') or parts[-1].startswith('.'):
        return False
    return parts[-1].lower().endswith('.xml')


def iter_uploaded_xml(files, is_zip_mode):
    """アップロードされたファイルから (source, path_name, data, error) を順に返す

    - source: アップロードしたファイル名（ZIPモード時はZIP名、それ以外は""）
    - path_name: ZIP内のパス（フォルダ階層を含む）またはファイル名
    - data: XMLのバイト列（読み込めなかった場合は None）
    - error: ZIP自体の問題（対象なし・破損）の説明。問題なければ None
    """
    for uploaded in files:
        if not is_zip_mode:
            yield "", uploaded.name, uploaded.getvalue(), None
            continue
        try:
            with zipfile.ZipFile(BytesIO(uploaded.getvalue())) as zf:
                xml_entries = [
                    info for info in zf.infolist()
                    if is_target_zip_entry(decode_zip_name(info))
                ]
                if not xml_entries:
                    yield uploaded.name, "", None, "ZIP内にXMLファイルがありません"
                    continue
                for info in xml_entries:
                    yield (uploaded.name, decode_zip_name(info),
                           zf.read(info), None)
        except zipfile.BadZipFile:
            yield uploaded.name, "", None, "ZIPファイルとして読み込めません"
