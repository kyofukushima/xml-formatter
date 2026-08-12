"""
ラベル設定管理ページ

ラベル設定の表示、編集、保存機能を提供します。
"""
import streamlit as st
from pathlib import Path
import sys
import json
import tempfile

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# ユーティリティ関数のインポート
from utils.config_manager import (
    load_label_config,
    save_label_config,
    update_boolean_settings,
    get_boolean_settings,
    validate_label_config,
    export_config,
    import_config
)

st.set_page_config(
    page_title="設定 - XML変換パイプライン",
    page_icon="⚙️",
    layout="wide"
)

st.title("⚙️ ラベル設定管理")

# セッション状態の初期化
if 'config_data' not in st.session_state:
    st.session_state.config_data = None
if 'config_modified' not in st.session_state:
    st.session_state.config_modified = False

# 設定ファイルのパス
config_path = project_root / "scripts" / "config" / "label_config.json"

# 設定の読み込み
if st.session_state.config_data is None:
    st.session_state.config_data = load_label_config(config_path)

# タブの作成
tab1, tab2, tab3, tab4 = st.tabs([
    "📋 設定の表示",
    "✅ ブーリアン型パラメーター",
    "✏️ JSONエディタ",
    "📤 インポート/エクスポート"
])

with tab1:
    st.header("ラベル設定の表示")
    
    if st.session_state.config_data:
        st.success("✅ 設定ファイルが読み込まれました")
        
        # 設定の基本情報
        st.subheader("基本情報")
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**バージョン**: {st.session_state.config_data.get('version', 'N/A')}")
        with col2:
            label_count = len(st.session_state.config_data.get('label_definitions', {}))
            st.info(f"**ラベル定義数**: {label_count}")
        
        # 変換動作の表示
        st.subheader("変換動作")
        if 'conversion_behaviors' in st.session_state.config_data:
            conversion_behaviors = st.session_state.config_data['conversion_behaviors']
            st.json(conversion_behaviors)
        else:
            st.warning("変換動作が設定されていません")
        
        # ラベル定義の一覧表示
        st.subheader("ラベル定義一覧")
        if 'label_definitions' in st.session_state.config_data:
            label_definitions = st.session_state.config_data['label_definitions']
            
            # 検索機能
            search_term = st.text_input("ラベル定義を検索", placeholder="ラベル名やIDで検索")
            
            filtered_labels = {}
            if search_term:
                search_lower = search_term.lower()
                for label_id, label_data in label_definitions.items():
                    if (search_lower in label_id.lower() or
                        search_lower in label_data.get('name', '').lower() or
                        search_lower in label_data.get('description', '').lower()):
                        filtered_labels[label_id] = label_data
            else:
                filtered_labels = label_definitions
            
            # ラベル定義の表示
            for label_id, label_data in filtered_labels.items():
                with st.expander(f"**{label_data.get('name', label_id)}** ({label_id})"):
                    st.markdown(f"**ID**: {label_id}")
                    st.markdown(f"**名前**: {label_data.get('name', 'N/A')}")
                    st.markdown(f"**説明**: {label_data.get('description', 'N/A')}")
                    
                    if 'patterns' in label_data:
                        st.markdown("**パターン**:")
                        for pattern in label_data['patterns']:
                            st.code(pattern, language='regex')
                    
                    if 'examples' in label_data:
                        st.markdown("**例**:")
                        for example in label_data['examples']:
                            st.text(f"  - {example}")
        else:
            st.warning("ラベル定義が設定されていません")
    else:
        st.error("❌ 設定ファイルを読み込めませんでした。")

with tab2:
    st.header("ブーリアン型パラメーターの簡易設定")
    st.markdown("よく使用する設定項目を簡単に変更できます。")
    
    if st.session_state.config_data:
        # 現在の設定値を取得
        boolean_settings = get_boolean_settings(st.session_state.config_data)
        
        # XML例の定義
        xml_examples = {
            'column_enabled': {
                'on': {
                    'input': '''<?xml version="1.0" encoding="UTF-8"?>
<Law>
  <LawBody>
    <Paragraph Num="1">
      <ParagraphNum>1</ParagraphNum>
      <ParagraphSentence>
        <Sentence Num="1">Paragraphの内容</Sentence>
      </ParagraphSentence>
      <List>
        <ListSentence>
          <Column Num="1">
            <Sentence Num="1">（１）</Sentence>
          </Column>
          <Column Num="2">
            <Sentence Num="1">ColumnありListの内容</Sentence>
          </Column>
        </ListSentence>
      </List>
    </Paragraph>
  </LawBody>
</Law>''',
                    'output': '''<?xml version="1.0" encoding="UTF-8"?>
<Law>
  <LawBody>
    <Paragraph Num="1">
      <ParagraphNum>1</ParagraphNum>
      <ParagraphSentence>
        <Sentence Num="1">Paragraphの内容</Sentence>
      </ParagraphSentence>
      <Item Num="1">
        <ItemTitle>（１）</ItemTitle>
        <ItemSentence>
          <Sentence Num="1">ColumnありListの内容</Sentence>
        </ItemSentence>
      </Item>
    </Paragraph>
  </LawBody>
</Law>''',
                    'description': 'ColumnありListの最初のColumnがItemTitleに変換されます'
                },
                'off': {
                    'input': '''<?xml version="1.0" encoding="UTF-8"?>
<Law>
  <LawBody>
    <Paragraph Num="1">
      <ParagraphNum>1</ParagraphNum>
      <ParagraphSentence>
        <Sentence Num="1">Paragraphの内容</Sentence>
      </ParagraphSentence>
      <List>
        <ListSentence>
          <Column Num="1">
            <Sentence Num="1">（１）</Sentence>
          </Column>
          <Column Num="2">
            <Sentence Num="1">ColumnありListの内容</Sentence>
          </Column>
        </ListSentence>
      </List>
    </Paragraph>
  </LawBody>
</Law>''',
                    'output': '''<?xml version="1.0" encoding="UTF-8"?>
<Law>
  <LawBody>
    <Paragraph Num="1">
      <ParagraphNum>1</ParagraphNum>
      <ParagraphSentence>
        <Sentence Num="1">Paragraphの内容</Sentence>
      </ParagraphSentence>
      <List>
        <ListSentence>
          <Column Num="1">
            <Sentence Num="1">（１）</Sentence>
          </Column>
          <Column Num="2">
            <Sentence Num="1">ColumnありListの内容</Sentence>
          </Column>
        </ListSentence>
      </List>
    </Paragraph>
  </LawBody>
</Law>''',
                    'description': 'Column処理が無効なため、List要素のまま残ります'
                }
            },
            'split_mode_enabled': {
                'on': {
                    'input': '''<?xml version="1.0" encoding="UTF-8"?>
<Law>
  <LawBody>
    <Paragraph Num="1">
      <ParagraphNum>1</ParagraphNum>
      <ParagraphSentence>
        <Sentence Num="1">Paragraphの内容</Sentence>
      </ParagraphSentence>
      <List>
        <ListSentence>
          <Sentence Num="1">最初のカラムなしリスト</Sentence>
        </ListSentence>
      </List>
      <List>
        <ListSentence>
          <Sentence Num="1">2つ目のカラムなしリスト</Sentence>
        </ListSentence>
      </List>
      <List>
        <ListSentence>
          <Sentence Num="1">3つ目のカラムなしリスト</Sentence>
        </ListSentence>
      </List>
    </Paragraph>
  </LawBody>
</Law>''',
                    'output': '''<?xml version="1.0" encoding="UTF-8"?>
<Law>
  <LawBody>
    <Paragraph Num="1">
      <ParagraphNum>1</ParagraphNum>
      <ParagraphSentence>
        <Sentence Num="1">Paragraphの内容</Sentence>
      </ParagraphSentence>
      <Item Num="1">
        <ItemTitle/>
        <ItemSentence>
          <Sentence Num="1">最初のカラムなしリスト</Sentence>
        </ItemSentence>
      </Item>
      <Item Num="2">
        <ItemTitle/>
        <ItemSentence>
          <Sentence Num="1">2つ目のカラムなしリスト</Sentence>
        </ItemSentence>
      </Item>
      <Item Num="3">
        <ItemTitle/>
        <ItemSentence>
          <Sentence Num="1">3つ目のカラムなしリスト</Sentence>
        </ItemSentence>
      </Item>
    </Paragraph>
  </LawBody>
</Law>''',
                    'description': '分割モードが有効なため、各Listが別々のItem要素に変換されます（並列分割）'
                },
                'off': {
                    'input': '''<?xml version="1.0" encoding="UTF-8"?>
<Law>
  <LawBody>
    <Paragraph Num="1">
      <ParagraphNum>1</ParagraphNum>
      <ParagraphSentence>
        <Sentence Num="1">Paragraphの内容</Sentence>
      </ParagraphSentence>
      <List>
        <ListSentence>
          <Sentence Num="1">最初のカラムなしリスト</Sentence>
        </ListSentence>
      </List>
      <List>
        <ListSentence>
          <Sentence Num="1">2つ目のカラムなしリスト</Sentence>
        </ListSentence>
      </List>
      <List>
        <ListSentence>
          <Sentence Num="1">3つ目のカラムなしリスト</Sentence>
        </ListSentence>
      </List>
    </Paragraph>
  </LawBody>
</Law>''',
                    'output': '''<?xml version="1.0" encoding="UTF-8"?>
<Law>
  <LawBody>
    <Paragraph Num="1">
      <ParagraphNum>1</ParagraphNum>
      <ParagraphSentence>
        <Sentence Num="1">Paragraphの内容</Sentence>
      </ParagraphSentence>
      <Item Num="1">
        <ItemTitle/>
        <ItemSentence>
          <Sentence Num="1">最初のカラムなしリスト</Sentence>
        </ItemSentence>
        <List>
          <ListSentence>
            <Sentence Num="1">2つ目のカラムなしリスト</Sentence>
          </ListSentence>
        </List>
        <List>
          <ListSentence>
            <Sentence Num="1">3つ目のカラムなしリスト</Sentence>
          </ListSentence>
        </List>
      </Item>
    </Paragraph>
  </LawBody>
</Law>''',
                    'description': '分割モードが無効なため、最初のItemに後続のListが取り込まれます（集約）'
                }
            },
            'image_split_enabled': {
                'on': {
                    'input': '''<?xml version="1.0" encoding="UTF-8"?>
<Law>
  <LawBody>
    <Paragraph Num="1">
      <ParagraphNum>1</ParagraphNum>
      <ParagraphSentence>
        <Sentence Num="1">Paragraphの内容</Sentence>
      </ParagraphSentence>
      <List>
        <ListSentence>
          <Sentence Num="1"><QuoteStruct><Fig src="./pict/sample.jpg"/></QuoteStruct></Sentence>
        </ListSentence>
      </List>
      <List>
        <ListSentence>
          <Sentence Num="1">1つ目のテキストリスト</Sentence>
        </ListSentence>
      </List>
      <List>
        <ListSentence>
          <Sentence Num="1">2つ目のテキストリスト</Sentence>
        </ListSentence>
      </List>
    </Paragraph>
  </LawBody>
</Law>''',
                    'output': '''<?xml version="1.0" encoding="UTF-8"?>
<Law>
  <LawBody>
    <Paragraph Num="1">
      <ParagraphNum>1</ParagraphNum>
      <ParagraphSentence>
        <Sentence Num="1">Paragraphの内容</Sentence>
      </ParagraphSentence>
      <Item Num="1">
        <ItemTitle/>
        <ItemSentence>
          <Sentence Num="1">
            <QuoteStruct>
              <Fig src="./pict/sample.jpg"/>
            </QuoteStruct>
          </Sentence>
        </ItemSentence>
      </Item>
      <Item Num="2">
        <ItemTitle/>
        <ItemSentence>
          <Sentence Num="1">1つ目のテキストリスト</Sentence>
        </ItemSentence>
      </Item>
      <Item Num="3">
        <ItemTitle/>
        <ItemSentence>
          <Sentence Num="1">2つ目のテキストリスト</Sentence>
        </ItemSentence>
      </Item>
    </Paragraph>
  </LawBody>
</Law>''',
                    'description': '画像List後の並列分割が有効なため、画像Listと後続のテキストListがそれぞれ別々のItem要素に変換されます（並列分割）'
                },
                'off': {
                    'input': '''<?xml version="1.0" encoding="UTF-8"?>
<Law>
  <LawBody>
    <Paragraph Num="1">
      <ParagraphNum>1</ParagraphNum>
      <ParagraphSentence>
        <Sentence Num="1">Paragraphの内容</Sentence>
      </ParagraphSentence>
      <List>
        <ListSentence>
          <Sentence Num="1"><QuoteStruct><Fig src="./pict/sample.jpg"/></QuoteStruct></Sentence>
        </ListSentence>
      </List>
      <List>
        <ListSentence>
          <Sentence Num="1">1つ目のテキストリスト</Sentence>
        </ListSentence>
      </List>
      <List>
        <ListSentence>
          <Sentence Num="1">2つ目のテキストリスト</Sentence>
        </ListSentence>
      </List>
    </Paragraph>
  </LawBody>
</Law>''',
                    'output': '''<?xml version="1.0" encoding="UTF-8"?>
<Law>
  <LawBody>
    <Paragraph Num="1">
      <ParagraphNum>1</ParagraphNum>
      <ParagraphSentence>
        <Sentence Num="1">Paragraphの内容</Sentence>
      </ParagraphSentence>
      <Item Num="1">
        <ItemTitle/>
        <ItemSentence>
          <Sentence Num="1">
            <QuoteStruct>
              <Fig src="./pict/sample.jpg"/>
            </QuoteStruct>
          </Sentence>
          <Sentence Num="2">1つ目のテキストリスト</Sentence>
          <Sentence Num="3">2つ目のテキストリスト</Sentence>
        </ItemSentence>
      </Item>
    </Paragraph>
  </LawBody>
</Law>''',
                    'description': '画像List後の並列分割が無効なため、後続のテキストListが同じItemSentence内に連続するSentence要素として統合されます'
                }
            }
        }

        # 設定UI
        st.subheader("変換動作")
        
        column_enabled = st.checkbox(
            "Column処理を有効化",
            value=boolean_settings['column_enabled'],
            help="Columnリストのテキストを最初の列に配置する処理を有効化します",
            key="checkbox_column_enabled"
        )
        
        # XML例の表示（トグル）
        show_example_column = st.toggle(
            "XML例を表示",
            value=st.session_state.get('show_example_column', False),
            key="toggle_column_example"
        )
        st.session_state['show_example_column'] = show_example_column
        
        if show_example_column:
            example_key = 'on' if column_enabled else 'off'
            example = xml_examples['column_enabled'][example_key]
            st.info(f"**説明**: {example['description']}")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**入力XML**")
                st.code(example['input'], language='xml')
            with col2:
                st.markdown("**出力XML**")
                st.code(example['output'], language='xml')
        
        split_mode = st.checkbox(
            "分割モードを有効化",
            value=boolean_settings['split_mode_enabled'],
            help="列がないテキストの分割モードを有効化します",
            key="checkbox_split_mode"
        )

        # XML例の表示（トグル）
        show_example_split_mode = st.toggle(
            "XML例を表示",
            value=st.session_state.get('show_example_split_mode', False),
            key="toggle_split_mode_example"
        )
        st.session_state['show_example_split_mode'] = show_example_split_mode

        if show_example_split_mode:
            example_key = 'on' if split_mode else 'off'
            example = xml_examples['split_mode_enabled'][example_key]
            st.info(f"**説明**: {example['description']}")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**入力XML**")
                st.code(example['input'], language='xml')
            with col2:
                st.markdown("**出力XML**")
                st.code(example['output'], language='xml')

        image_split = st.checkbox(
            "画像List後の並列分割を有効化",
            value=boolean_settings['image_split_enabled'],
            help="画像List（QuoteStructのみでテキストのないList）の後にテキストのColumnなしListが"
                 "続く場合、Sentence要素として統合せず、それぞれ並列の要素（Item/Subitem等）に分割します。"
                 "数式画像とその変数説明のListが連続する告示データなどで使用します。"
                 "後続List同士の並列分割には「分割モード」も有効である必要があります。",
            key="checkbox_image_split"
        )

        # XML例の表示（トグル）
        show_example_image_split = st.toggle(
            "XML例を表示",
            value=st.session_state.get('show_example_image_split', False),
            key="toggle_image_split_example"
        )
        st.session_state['show_example_image_split'] = show_example_image_split

        if show_example_image_split:
            example_key = 'on' if image_split else 'off'
            example = xml_examples['image_split_enabled'][example_key]
            st.info(f"**説明**: {example['description']}")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**入力XML**")
                st.code(example['input'], language='xml')
            with col2:
                st.markdown("**出力XML**")
                st.code(example['output'], language='xml')

        # 保存ボタン
        if st.button("設定を保存", type="primary", key="save_boolean_settings"):
            # 設定を更新
            updated_config = update_boolean_settings(
                st.session_state.config_data.copy(),
                column_enabled,
                split_mode,
                image_split
            )
            
            # 保存
            success, error_msg = save_label_config(updated_config, config_path)
            
            if success:
                st.success("✅ 設定を保存しました")
                st.session_state.config_data = updated_config
                st.session_state.config_modified = False
                st.rerun()
            else:
                st.error(f"❌ 保存に失敗しました: {error_msg}")
    else:
        st.error("❌ 設定ファイルを読み込めませんでした。")

with tab3:
    st.header("JSONエディタ")
    st.markdown("設定ファイルを直接編集できます。")
    
    if st.session_state.config_data:
        # JSONエディタ
        edited_config = st.text_area(
            "設定JSON",
            value=json.dumps(st.session_state.config_data, ensure_ascii=False, indent=2),
            height=600,
            help="設定ファイルのJSONを直接編集できます"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("設定を検証", type="secondary", key="validate_json_editor"):
                try:
                    parsed_config = json.loads(edited_config)
                    is_valid, errors = validate_label_config(parsed_config)
                    
                    if is_valid:
                        st.success("✅ 設定は有効です")
                    else:
                        st.error("❌ 設定にエラーがあります:")
                        for error in errors:
                            st.error(f"  - {error}")
                except json.JSONDecodeError as e:
                    st.error(f"❌ JSONの形式が正しくありません: {e}")
        
        with col2:
            if st.button("設定を保存", type="primary", key="save_json_editor"):
                try:
                    parsed_config = json.loads(edited_config)
                    
                    # バリデーション
                    is_valid, errors = validate_label_config(parsed_config)
                    if not is_valid:
                        st.error("❌ 設定にエラーがあります:")
                        for error in errors:
                            st.error(f"  - {error}")
                    else:
                        # 保存
                        success, error_msg = save_label_config(parsed_config, config_path)
                        
                        if success:
                            st.success("✅ 設定を保存しました")
                            st.session_state.config_data = parsed_config
                            st.session_state.config_modified = False
                            st.rerun()
                        else:
                            st.error(f"❌ 保存に失敗しました: {error_msg}")
                except json.JSONDecodeError as e:
                    st.error(f"❌ JSONの形式が正しくありません: {e}")
    else:
        st.error("❌ 設定ファイルを読み込めませんでした。")

with tab4:
    st.header("インポート/エクスポート")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📤 エクスポート")
        st.markdown("現在の設定をJSONファイルとしてエクスポートします。")
        
        if st.session_state.config_data:
            # エクスポートボタン
            config_json = json.dumps(st.session_state.config_data, ensure_ascii=False, indent=2)
            st.download_button(
                label="設定をエクスポート",
                data=config_json,
                file_name="label_config.json",
                mime="application/json"
            )
        else:
            st.warning("⚠️ 設定ファイルを読み込めませんでした。")
    
    with col2:
        st.subheader("📥 インポート")
        st.markdown("JSONファイルから設定をインポートします。")
        
        uploaded_config_file = st.file_uploader(
            "設定ファイルを選択",
            type=['json'],
            help="ラベル設定のJSONファイルをアップロードします"
        )
        
        if uploaded_config_file:
            try:
                config_content = uploaded_config_file.read().decode('utf-8')
                imported_config = json.loads(config_content)
                
                # バリデーション
                is_valid, errors = validate_label_config(imported_config)
                
                if is_valid:
                    st.success("✅ 設定ファイルは有効です")
                    
                    # プレビュー
                    with st.expander("設定のプレビュー", expanded=False):
                        st.json(imported_config)
                    
                    # インポートボタン
                    if st.button("設定をインポート", type="primary", key="import_config"):
                        success, error_msg = save_label_config(imported_config, config_path)
                        
                        if success:
                            st.success("✅ 設定をインポートしました")
                            st.session_state.config_data = imported_config
                            st.session_state.config_modified = False
                            st.rerun()
                        else:
                            st.error(f"❌ インポートに失敗しました: {error_msg}")
                else:
                    st.error("❌ 設定ファイルにエラーがあります:")
                    for error in errors:
                        st.error(f"  - {error}")
            except json.JSONDecodeError as e:
                st.error(f"❌ JSONファイルの形式が正しくありません: {e}")
            except Exception as e:
                st.error(f"❌ エラーが発生しました: {e}")


