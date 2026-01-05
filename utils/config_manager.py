"""
設定管理ユーティリティ

ラベル設定ファイルの読み込み、保存、バリデーションなどの機能を提供します。
"""
import json
from pathlib import Path
from typing import Dict, Optional, Tuple, List
import streamlit as st
import jsonschema


def load_label_config(config_path: Optional[Path] = None) -> Optional[Dict]:
    """
    ラベル設定ファイルを読み込む
    
    Args:
        config_path: 設定ファイルのパス（Noneの場合はデフォルト）
    
    Returns:
        設定データの辞書、失敗時はNone
    """
    if config_path is None:
        config_path = Path(__file__).parent.parent / "scripts" / "config" / "label_config.json"
    
    try:
        if not config_path.exists():
            st.warning(f"設定ファイルが見つかりません: {config_path}")
            return None
        
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"設定ファイルが見つかりません: {config_path}")
        return None
    except json.JSONDecodeError as e:
        st.error(f"JSONファイルの形式が正しくありません: {e}")
        return None
    except Exception as e:
        st.error(f"設定ファイルの読み込みエラー: {e}")
        return None


def save_label_config(config: Dict, config_path: Optional[Path] = None) -> Tuple[bool, Optional[str]]:
    """
    ラベル設定ファイルを保存
    
    Args:
        config: 設定データの辞書
        config_path: 設定ファイルのパス（Noneの場合はデフォルト）
    
    Returns:
        (success: bool, error_message: Optional[str])
    """
    if config_path is None:
        config_path = Path(__file__).parent.parent / "scripts" / "config" / "label_config.json"
    
    try:
        # バックアップを作成
        if config_path.exists():
            backup_path = config_path.with_suffix('.json.bak')
            import shutil
            shutil.copy(config_path, backup_path)
            st.info(f"バックアップを作成しました: {backup_path.name}")
        
        # 設定ファイルを保存
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        return True, None
    except Exception as e:
        return False, str(e)


def update_boolean_settings(
    config: Dict,
    column_enabled: bool,
    split_mode_enabled: bool
) -> Dict:
    """
    ブーリアン型パラメーターを更新
    
    Args:
        config: 設定データの辞書
        column_enabled: Column処理を有効化
        split_mode_enabled: 分割モードを有効化
    
    Returns:
        更新された設定データの辞書
    """
    # conversion_behaviorsの更新
    if 'conversion_behaviors' not in config:
        config['conversion_behaviors'] = {}
    
    if 'column_list_text_first_column' not in config['conversion_behaviors']:
        config['conversion_behaviors']['column_list_text_first_column'] = {}
    config['conversion_behaviors']['column_list_text_first_column']['enabled'] = column_enabled
    
    if 'no_column_text_split_mode' not in config['conversion_behaviors']:
        config['conversion_behaviors']['no_column_text_split_mode'] = {}
    config['conversion_behaviors']['no_column_text_split_mode']['enabled'] = split_mode_enabled
    
    return config


def get_boolean_settings(config: Dict) -> Dict[str, bool]:
    """
    ブーリアン型パラメーターを取得
    
    Args:
        config: 設定データの辞書
    
    Returns:
        ブーリアン型パラメーターの辞書
    """
    result = {
        'column_enabled': False,
        'split_mode_enabled': False
    }
    
    if 'conversion_behaviors' in config:
        if 'column_list_text_first_column' in config['conversion_behaviors']:
            result['column_enabled'] = config['conversion_behaviors']['column_list_text_first_column'].get('enabled', False)
        
        if 'no_column_text_split_mode' in config['conversion_behaviors']:
            result['split_mode_enabled'] = config['conversion_behaviors']['no_column_text_split_mode'].get('enabled', False)
    
    return result


def validate_label_config(config: Dict) -> Tuple[bool, List[str]]:
    """
    ラベル設定のバリデーション
    
    Args:
        config: 設定データの辞書
    
    Returns:
        (is_valid: bool, error_messages: List[str])
    """
    errors = []
    
    # 基本的な構造チェック
    if not isinstance(config, dict):
        errors.append("設定データは辞書形式である必要があります")
        return False, errors
    
    # versionフィールドのチェック
    if 'version' not in config:
        errors.append("'version'フィールドが見つかりません")
    
    # label_definitionsフィールドのチェック
    if 'label_definitions' not in config:
        errors.append("'label_definitions'フィールドが見つかりません")
    elif not isinstance(config['label_definitions'], dict):
        errors.append("'label_definitions'は辞書形式である必要があります")
    
    # hierarchy_rulesフィールドのチェック
    if 'hierarchy_rules' in config and not isinstance(config['hierarchy_rules'], dict):
        errors.append("'hierarchy_rules'は辞書形式である必要があります")
    
    # conversion_behaviorsフィールドのチェック
    if 'conversion_behaviors' in config and not isinstance(config['conversion_behaviors'], dict):
        errors.append("'conversion_behaviors'は辞書形式である必要があります")
    
    return len(errors) == 0, errors


def export_config(config: Dict, export_path: Path) -> Tuple[bool, Optional[str]]:
    """
    設定をエクスポート
    
    Args:
        config: 設定データの辞書
        export_path: エクスポート先のパス
    
    Returns:
        (success: bool, error_message: Optional[str])
    """
    try:
        export_path.parent.mkdir(parents=True, exist_ok=True)
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True, None
    except Exception as e:
        return False, str(e)


def import_config(import_path: Path) -> Tuple[Optional[Dict], Optional[str]]:
    """
    設定をインポート
    
    Args:
        import_path: インポート元のパス
    
    Returns:
        (config: Optional[Dict], error_message: Optional[str])
    """
    try:
        if not import_path.exists():
            return None, f"ファイルが見つかりません: {import_path}"
        
        with open(import_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # バリデーション
        is_valid, errors = validate_label_config(config)
        if not is_valid:
            return None, f"設定ファイルの形式が正しくありません: {', '.join(errors)}"
        
        return config, None
    except json.JSONDecodeError as e:
        return None, f"JSONファイルの形式が正しくありません: {e}"
    except Exception as e:
        return None, str(e)


