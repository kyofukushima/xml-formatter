#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
処理結果レポート全文（txtダウンロード用）生成のユニットテスト
"""

import importlib.util
import sys
import types
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent

if "streamlit" not in sys.modules:
    try:
        import streamlit  # noqa: F401
    except ImportError:
        sys.modules["streamlit"] = types.ModuleType("streamlit")

_spec = importlib.util.spec_from_file_location(
    "app_validation", project_root / "utils" / "validation.py")
_validation = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_validation)

build_result_report_text = _validation.build_result_report_text
format_validation_report = _validation.format_validation_report


def _success_result():
    errors = [f"❌ Error: error {i}" for i in range(15)]
    long_content = "A" * 1500
    return {
        "success": True,
        "output_path": Path("/tmp/out/sample_final.xml"),
        "execution_log": {
            "total_steps": 2, "completed_steps": 2, "failed_step": None,
            "steps": [
                {"step": 1, "script": "a.py", "success": True, "error": None},
                {"step": 2, "script": "b.py", "success": True, "error": None},
            ],
        },
        "validation_results": {
            "syntax": {"is_valid": True, "error": None, "output": "SUCCESS: well-formed"},
            "content": {
                "is_valid": False,
                "error": "テキスト内容の不一致が検出されました\nエラー数: 15",
                "output": "stdout line\n",
                "report_data": {"success": False, "errors": errors, "content": long_content},
            },
        },
        "fullwidth_space_applied": True,
        "double_paren_normalized": 3,
        "appdxtable_num_result": None,
    }


def test_full_report_is_not_truncated():
    result = _success_result()
    text = build_result_report_text(result, "sample.xml")

    # 画面表示用は省略される
    shown = format_validation_report(result["validation_results"]["content"]["report_data"])
    assert "他 5 件のエラー" in shown
    assert "以下省略" in shown

    # 全文版は省略されない
    assert "error 14" in text
    assert "A" * 1500 in text
    assert "他 5 件" not in text
    assert "以下省略" not in text
    assert "入力ファイル: sample.xml" in text
    assert "出力ファイル: sample_final.xml" in text
    assert "処理結果: 成功" in text
    assert "NG（不一致あり）" in text
    assert "全角スペース補填前" in text
    assert "正規化: 3箇所" in text
    assert "[OK] ステップ 2: b.py" in text


def test_failure_report_contains_error_and_failed_step():
    result = {
        "success": False,
        "error": "convert_item_step0.pyの実行に失敗しました\nエラー詳細: Traceback ...",
        "execution_log": {
            "total_steps": 3, "completed_steps": 1, "failed_step": "convert_item_step0.py",
            "steps": [
                {"step": 1, "script": "pre.py", "success": True, "error": None},
                {"step": 2, "script": "convert_item_step0.py", "success": False,
                 "error": "convert_item_step0.pyの実行に失敗しました\nエラー詳細: Traceback ..."},
            ],
        },
    }
    text = build_result_report_text(result, "x.xml")
    assert "処理結果: 失敗" in text
    assert "Traceback ..." in text
    assert "失敗ステップ: convert_item_step0.py" in text
    assert "[NG] ステップ 2: convert_item_step0.py" in text
    assert "完了ステップ: 1 / 3" in text


def test_empty_result():
    text = build_result_report_text(None)
    assert "処理結果がありません" in text
