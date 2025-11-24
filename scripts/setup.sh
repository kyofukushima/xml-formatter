#!/bin/bash

###############################################################################
# XML パイプライン環境セットアップスクリプト
# 
# 用途: 初回セットアップ時に環境を準備します
#       - 必要なフォルダを作成
#       - lxml ライブラリをインストール
#       - 実行権限を設定
###############################################################################

set -e

# 色付き出力用
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════╗"
echo "║ XML パイプライン環境セットアップスクリプト ║"
echo "╚════════════════════════════════════════════╝"
echo -e "${NC}"

###############################################################################
# ステップ1: Python 環境確認
###############################################################################

echo ""
echo -e "${YELLOW}[ステップ 1/4] Python 環境を確認中...${NC}"

if ! command -v python3 &> /dev/null; then
  echo -e "${RED}[エラー] Python3 がインストールされていません${NC}"
  echo "以下のコマンドでインストールしてください:"
  echo "  Ubuntu/Debian: sudo apt-get install python3"
  echo "  macOS: brew install python3"
  echo "  Windows: https://www.python.org からダウンロード"
  exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✓ Python $PYTHON_VERSION が見つかりました${NC}"

###############################################################################
# ステップ2: lxml ライブラリをインストール
###############################################################################

echo ""
echo -e "${YELLOW}[ステップ 2/4] lxml ライブラリをインストール中...${NC}"

if python3 -c "import lxml" 2>/dev/null; then
  LXML_VERSION=$(python3 -c "import lxml; print(lxml.__version__)")
  echo -e "${GREEN}✓ lxml $LXML_VERSION は既にインストール済みです${NC}"
else
  echo "lxml をインストール中..."
  if pip3 install lxml 2>/dev/null; then
    LXML_VERSION=$(python3 -c "import lxml; print(lxml.__version__)")
    echo -e "${GREEN}✓ lxml $LXML_VERSION をインストールしました${NC}"
  else
    echo -e "${RED}[エラー] lxml のインストールに失敗しました${NC}"
    echo "手動でインストールしてください: pip3 install lxml"
    exit 1
  fi
fi

###############################################################################
# ステップ3: ディレクトリ構造を作成
###############################################################################

echo ""
echo -e "${YELLOW}[ステップ 3/4] ディレクトリ構造を作成中...${NC}"

# 作成するディレクトリ
DIRS=("input" "output" ".temp")

for dir in "${DIRS[@]}"; do
  if [ ! -d "$dir" ]; then
    mkdir -p "$dir"
    echo -e "${GREEN}✓ ディレクトリを作成しました: $dir${NC}"
  else
    echo -e "${GREEN}✓ ディレクトリは既に存在します: $dir${NC}"
  fi
done

###############################################################################
# ステップ4: スクリプトの実行権限を設定
###############################################################################

echo ""
echo -e "${YELLOW}[ステップ 4/4] 実行権限を設定中...${NC}"

if [ -f "run_pipeline_fixed.sh" ]; then
  chmod +x run_pipeline_fixed.sh
  echo -e "${GREEN}✓ run_pipeline_fixed.sh に実行権限を付与しました${NC}"
else
  echo -e "${YELLOW}⚠ run_pipeline_fixed.sh が見つかりません${NC}"
fi

if [ -f "setup.sh" ]; then
  chmod +x setup.sh
  echo -e "${GREEN}✓ setup.sh に実行権限を付与しました${NC}"
fi

###############################################################################
# 完了メッセージ
###############################################################################

echo ""
echo -e "${GREEN}"
echo "╔════════════════════════════════════════════╗"
echo "║       セットアップが完了しました！        ║"
echo "╚════════════════════════════════════════════╝"
echo -e "${NC}"

echo ""
echo -e "${BLUE}次のステップ:${NC}"
echo ""
echo "1. XMLファイルを input/ フォルダに配置します"
echo "   例: cp your_file.xml input/"
echo ""
echo "2. パイプラインを実行します"
echo "   例: ./run_pipeline_fixed.sh ./input ./output all"
echo ""
echo "3. 結果を確認します"
echo "   例: ls -lh output/"
echo ""

echo -e "${BLUE}詳細は以下のドキュメントを参照してください:${NC}"
echo "  - README.md         (完全なドキュメント)"
echo "  - QUICKSTART.md     (クイックスタート)"
echo "  - CHANGES.md        (修正内容の説明)"
echo ""

echo -e "${GREEN}セットアップ完了！${NC}"
