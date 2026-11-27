#!/bin/zsh
cd "$(dirname "$0")"

if [ ! -x ".venv/bin/python" ]; then
  echo "[首次运行] 正在创建虚拟环境..."
  python3 -m venv .venv || exit 1
  echo "[首次运行] 正在安装依赖..."
  .venv/bin/python -m pip install --upgrade pip
  .venv/bin/python -m pip install -r requirements.txt
fi

echo -n "请输入 DOI（例如 10.1038/s41586-020-2649-2）："
read DOI
.venv/bin/python download_by_doi.py "$DOI"
echo
read "?按回车退出..."
