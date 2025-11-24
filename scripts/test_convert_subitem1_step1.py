
import sys
import subprocess
from pathlib import Path
from lxml import etree
import pytest

# ============================================================================ 
# Test Setup
# ============================================================================ 

# スクリプトのルートディレクトリ
SCRIPT_DIR = Path(__file__).parent

# テスト対象のスクリプト
TARGET_SCRIPT = SCRIPT_DIR / "convert_subitem1_step1.py"

# テストデータのベースディレクトリ
TEST_DATA_BASE_DIR = SCRIPT_DIR / "test_data" / "unit_tests" / "convert_subitem1_step1"

# lxmlのパーサー（空白を無視）
XML_PARSER = etree.XMLParser(remove_blank_text=True)

def run_script(input_file: Path, output_file: Path) -> subprocess.CompletedProcess:
    """テスト対象のPythonスクリプトを実行する"""
    return subprocess.run(
        [sys.executable, str(TARGET_SCRIPT), str(input_file), str(output_file)],
        capture_output=True,
        text=True,
        encoding='utf-8'
    )

def assert_xml_equal(file1: Path, file2: Path):
    """2つのXMLファイルが構造的に等しいかアサートする"""
    # ファイルの内容を読み込む
    xml_str1 = file1.read_text(encoding='utf-8')
    xml_str2 = file2.read_text(encoding='utf-8')
    
    # 文字列からXMLツリーをパース
    tree1 = etree.fromstring(xml_str1.encode('utf-8'), parser=XML_PARSER)
    tree2 = etree.fromstring(xml_str2.encode('utf-8'), parser=XML_PARSER)

    # 正規化（c14n）して比較
    c14n_str1 = etree.tostring(tree1, method='c14n', with_comments=False)
    c14n_str2 = etree.tostring(tree2, method='c14n', with_comments=False)

    assert c14n_str1 == c14n_str2, f"XMLの内容が異なります:\n--- Expected: {file2} ---\n{c14n_str2.decode('utf-8')}\n--- Actual: {file1} ---\n{c14n_str1.decode('utf-8')}"

# ============================================================================ 
# Test Execution
# ============================================================================ 

# テストシナリオのディレクトリを動的に収集
scenario_dirs = [d for d in TEST_DATA_BASE_DIR.iterdir() if d.is_dir()]
scenario_ids = [d.name for d in scenario_dirs]

@pytest.mark.parametrize("scenario_dir", scenario_dirs, ids=scenario_ids)
def test_subitem1_conversion_scenarios(scenario_dir, tmp_path):
    """
    パラメータ化されたテスト関数。各シナリオディレクトリでテストを実行する。
    """
    input_file = scenario_dir / "input.xml"
    expected_output_file = scenario_dir / "expected.xml"
    actual_output_file = tmp_path / "actual_output.xml"

    # 入力ファイルと期待結果ファイルが存在することを確認
    assert input_file.exists(), f"テスト入力ファイルが見つかりません: {input_file}"
    assert expected_output_file.exists(), f"期待結果ファイルが見つかりません: {expected_output_file}"

    # スクリプトを実行
    result = run_script(input_file, actual_output_file)

    # スクリプトが正常に終了したか確認
    assert result.returncode == 0, f"スクリプトの実行に失敗しました:\n{result.stderr}" 
    
    # 出力ファイルが生成されたか確認
    assert actual_output_file.exists(), "出力ファイルが生成されませんでした"

    # 期待される出力と実際に出力されたXMLを比較
    assert_xml_equal(actual_output_file, expected_output_file)

