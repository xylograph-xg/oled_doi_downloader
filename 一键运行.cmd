@echo off
chcp 65001 >nul
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [首次运行] 正在创建虚拟环境...
    py -m venv .venv
    if errorlevel 1 (
        echo 未找到 Python。请先安装 Python 3，并确保 py 命令可用。
        pause
        exit /b 1
    )

    echo [首次运行] 正在安装依赖...
    ".venv\Scripts\python.exe" -m pip install --upgrade pip
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
)

echo.
set /p DOI=请输入 DOI（例如 10.1038/s41586-020-2649-2）：
echo.
".venv\Scripts\python.exe" download_by_doi.py "%DOI%"

echo.
pause
