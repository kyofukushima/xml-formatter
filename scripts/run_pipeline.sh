#!/bin/bash

###############################################################################
# XML パイプライン処理スクリプト - 検証機能付き
#
# 用途: 入力フォルダ内のXMLファイルを複数のステップで順次処理し、
#       出力フォルダに整形されたXMLを保存します
#       また、処理前後のテキスト内容の整合性を検証します
#
# 使用方法:
#   ./run_pipeline.sh input_folder output_folder [mode]
#
# 引数:
#   input_folder  : 処理対象のXMLファイルを格納するフォルダ
#   output_folder : 処理結果を保存するフォルダ
#   mode          : 実行モード (all=連続実行 [デフォルト], step=確認しながら実行)
#
# 機能:
#   - 複数の変換スクリプトによるXML加工
#   - テキスト内容の検証（構造変更を無視した値の整合性チェック）
#   - 中間ファイルと検証レポートの保存
#
# 例:
#   ./run_pipeline.sh ./input ./output all
#   ./run_pipeline.sh ./input ./output step
#
###############################################################################

set -e

# スクリプトディレクトリを取得
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

# 色付き出力用（オプション）
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'  # No Color

# 変換スクリプトのリスト（実行順序が重要）
CONVERTERS=(
  "preprocess_non_first_sentence_to_list.py"  # 前処理: 2個目以降のSentence要素をList要素に変換
  "convert_article_focused.py"
  "convert_paragraph_step3.py"
  "convert_paragraph_step4.py"
  "convert_item_step0.py"
  "convert_subitem1_step0.py"
  "convert_subitem2_step0.py"
  "convert_subitem3_step0.py"
  "convert_subitem4_step0.py"
  "convert_subitem5_step0.py"
  "convert_subitem6_step0.py"
  "convert_subitem7_step0.py"
  "convert_subitem8_step0.py"
  "convert_subitem9_step0.py"
  "convert_subitem10_step0.py"
)

# 検証スクリプト
VALIDATION_SCRIPT="compare_xml_text_content.py"

# パース検証スクリプト
PARSE_VALIDATION_SCRIPT="validate_xml.py"

###############################################################################
# ヘルプと使用方法
###############################################################################

print_usage() {
  cat << EOF
${YELLOW}========================================${NC}
XML パイプライン処理スクリプト
${YELLOW}========================================${NC}

使用方法:
  $0 <input_folder> <output_folder> [mode]

引数:
  input_folder   : 処理対象のXMLファイルを格納するフォルダ
  output_folder  : 処理結果を保存するフォルダ
  mode           : 実行モード
                   - all  (デフォルト) 連続実行
                   - step 各ステップで一時停止

例:
  $0 ./input ./output
  $0 ./input ./output all
  $0 ./input ./output step

EOF
}

print_step() {
  local step_name="$1"
  echo ""
  echo -e "${GREEN}===============================================${NC}"
  echo -e "${GREEN}${step_name}${NC}"
  echo -e "${GREEN}===============================================${NC}"
}

print_error() {
  echo -e "${RED}[エラー] $1${NC}" >&2
}

print_success() {
  echo -e "${GREEN}[成功] $1${NC}"
}

print_info() {
  echo -e "${YELLOW}[情報] $1${NC}"
}

###############################################################################
# メイン処理
###############################################################################

# 引数チェック
if [ $# -lt 2 ]; then
  print_usage
  exit 1
fi

INPUT_FOLDER="$1"
OUTPUT_FOLDER="$2"
MODE="${3:-all}"

# モード値の検証
if [ "$MODE" != "all" ] && [ "$MODE" != "step" ]; then
  print_error "無効なモード: '$MODE'. 'all' または 'step' を指定してください。"
  print_usage
  exit 1
fi

# 入力フォルダの存在確認
if [ ! -d "$INPUT_FOLDER" ]; then
  print_error "入力フォルダが見つかりません: $INPUT_FOLDER"
  exit 1
fi

# 入力フォルダ内にXMLファイルがあるか確認
if [ -z "$(find "$INPUT_FOLDER" -maxdepth 1 -name '*.xml' -type f)" ]; then
  print_error "入力フォルダにXMLファイルが見つかりません: $INPUT_FOLDER"
  exit 1
fi

# 出力フォルダを作成
if [ ! -d "$OUTPUT_FOLDER" ]; then
  print_info "出力フォルダを作成します: $OUTPUT_FOLDER"
  mkdir -p "$OUTPUT_FOLDER"
  print_success "出力フォルダを作成しました"
fi

# 入力フォルダと出力フォルダのパスを絶対パスに変換
INPUT_FOLDER="$(cd "$INPUT_FOLDER" && pwd)"
OUTPUT_FOLDER="$(cd "$OUTPUT_FOLDER" && pwd)"

print_step "パイプライン処理を開始します"
echo "入力フォルダ: $INPUT_FOLDER"
echo "出力フォルダ: $OUTPUT_FOLDER"
echo "実行モード: $MODE"

# 処理対象のXMLファイル一覧を取得
xml_files=($(find "$INPUT_FOLDER" -maxdepth 1 -name '*.xml' -type f | sort))
file_count=${#xml_files[@]}

echo ""
print_info "処理対象ファイル数: $file_count"
for file in "${xml_files[@]}"; do
  echo "  - $(basename "$file")"
done

###############################################################################
# ファイルごとのパイプライン処理
###############################################################################

# 中間ファイル保存用のベースディレクトリ
INTERMEDIATE_FOLDER="$OUTPUT_FOLDER/intermediate_files"
if [ ! -d "$INTERMEDIATE_FOLDER" ]; then
  print_info "中間ファイル保存用のフォルダを作成します: $INTERMEDIATE_FOLDER"
  mkdir -p "$INTERMEDIATE_FOLDER"
fi

file_index=0
for xml_file in "${xml_files[@]}"; do
  file_index=$((file_index + 1))
  filename=$(basename "$xml_file")
  filename_no_ext="${filename%.xml}"
  
  print_step "ファイル $file_index/$file_count: $filename を処理中"
  
  # 各ファイルの中間ファイル保存用ディレクトリを作成
  intermediate_dir="$INTERMEDIATE_FOLDER/$filename_no_ext"
  mkdir -p "$intermediate_dir"
  print_info "中間ファイルは $intermediate_dir に保存されます"

  # パース検証を実行
  parse_validation_script_path="$SCRIPT_DIR/$PARSE_VALIDATION_SCRIPT"
  parse_report="$intermediate_dir/${filename_no_ext}-parse_validation.txt"

  print_info "パース検証を実行中..."
  echo "  検証対象ファイル: $xml_file"
  echo "  パース検証レポート: $parse_report"

  if [ -f "$parse_validation_script_path" ]; then
    if python3 "$parse_validation_script_path" "$xml_file" > "$parse_report" 2>&1; then
      if grep -q "SUCCESS:" "$parse_report"; then
        print_success "パース検証が完了しました（正常）"
      else
        print_error "パース検証で問題が検出されました"
        echo "パース検証レポートを確認してください: $parse_report"
        echo "このファイルの処理をスキップします。"
        echo ""
        continue
      fi
    else
      print_error "パース検証スクリプトの実行中にエラーが発生しました"
      echo "パース検証レポートを確認してください: $parse_report"
      echo "このファイルの処理をスキップします。"
      echo ""
      continue
    fi
  else
    print_error "パース検証スクリプトが見つかりません: $parse_validation_script_path"
    echo "処理を続行しますが、パース検証はスキップされます。"
  fi

  current_input="$xml_file"
  final_output=""
  
  # パイプラインのステップを実行
  for i in "${!CONVERTERS[@]}"; do
    converter_script="${CONVERTERS[$i]}"
    step_num=$((i + 1))
    total_steps=${#CONVERTERS[@]}
    
    # スクリプトのフルパスを作成
    converter_path="$SCRIPT_DIR/$converter_script"
    
    # スクリプトが存在するか確認
    if [ ! -f "$converter_path" ]; then
      print_error "スクリプトが見つかりません: $converter_path"
      exit 1
    fi
    
    # 出力ファイルパスを作成
    step_name=$(basename "$converter_script" .py)
    output_file="$intermediate_dir/${filename_no_ext}-${step_name}.xml"
    
    print_info "[$step_num/$total_steps] $converter_script を実行中..."
    
    # Pythonスクリプトを実行
    if ! python3 "$converter_path" "$current_input" "$output_file" 2>/dev/null; then
      print_error "$converter_script の実行中にエラーが発生しました。"
      echo "入力ファイル: $current_input"
      echo "出力ファイル: $output_file"
      exit 1
    fi
    
    # 出力ファイルが正常に作成されたか確認
    if [ ! -f "$output_file" ]; then
      print_error "出力ファイルが作成されませんでした: $output_file"
      exit 1
    fi
    
    print_success "$converter_script が完了しました"
    
    current_input="$output_file"
    final_output="$output_file"
    
    # step モードの場合、各ステップ後に一時停止
    if [ "$MODE" = "step" ] && [ $step_num -lt $total_steps ]; then
      read -p "次のステップに進むには Enter キーを押してください..."
      echo ""
    fi
  done
  
  # 最終出力ファイルを出力フォルダにコピー
  if [ -f "$final_output" ]; then
    output_filename="${filename_no_ext}-final.xml"
    final_destination="$OUTPUT_FOLDER/$output_filename"

    cp "$final_output" "$final_destination"
    print_success "最終結果を保存しました: $final_destination"

    # 検証ステップ：オリジナルファイルと最終出力ファイルを比較
    validation_script_path="$SCRIPT_DIR/$VALIDATION_SCRIPT"
    validation_report="$intermediate_dir/${filename_no_ext}-validation_report.txt"

    print_info "検証スクリプトを実行中..."
    echo "  オリジナルファイル: $xml_file"
    echo "  最終出力ファイル: $final_destination"
    echo "  検証レポート: $validation_report"

    if [ -f "$validation_script_path" ]; then
      if python3 "$validation_script_path" "$xml_file" "$final_destination" --report_file "$validation_report" 2>/dev/null; then
        print_success "検証が完了しました"
      else
        print_error "検証中にエラーが発生しました"
        echo "検証レポートを確認してください: $validation_report"
      fi
    else
      print_error "検証スクリプトが見つかりません: $validation_script_path"
    fi

  else
    print_error "最終出力ファイルが見つかりません"
    exit 1
  fi

  echo ""
done

###############################################################################
# 完了メッセージ
###############################################################################

print_step "処理完了"
echo "すべてのファイルの処理が完了しました。"
echo ""
echo "出力ファイル一覧:"
ls -lh "$OUTPUT_FOLDER"/*.xml 2>/dev/null || echo "  (出力ファイルなし)"
echo ""
echo "パース検証レポート一覧:"
find "$INTERMEDIATE_FOLDER" -name "*-parse_validation.txt" -type f | while read report_file; do
  echo "  - $report_file"
  # パース検証結果の簡易表示
  if grep -q "SUCCESS:" "$report_file" 2>/dev/null; then
    echo -e "    ${GREEN}[成功] XML構文が正しいです${NC}"
  elif grep -q "ERROR:" "$report_file" 2>/dev/null; then
    echo -e "    ${RED}[エラー] XML構文エラーが検出されました${NC}"
  fi
done

echo ""
echo "検証レポート一覧:"
find "$INTERMEDIATE_FOLDER" -name "*-validation_report.txt" -type f | while read report_file; do
  echo "  - $report_file"
  # 検証結果の簡易表示
  if grep -q "❌ Error:" "$report_file" 2>/dev/null; then
    echo -e "    ${RED}[要確認] テキスト欠落が検出されました${NC}"
  elif grep -q "✅ Success:" "$report_file" 2>/dev/null; then
    echo -e "    ${GREEN}[成功] テキスト内容が一致しています${NC}"
  fi
done
echo ""
print_success "パイプライン処理と検証が完了しました"
