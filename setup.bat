@echo off
chcp 65001 >nul
echo ==========================================
echo   Blog API 环境设置
echo ==========================================
echo.

:: 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

:: 创建虚拟环境（如果不存在）
if not exist ".venv" (
    echo [1/3] 创建虚拟环境...
    python -m venv .venv
) else (
    echo [1/3] 虚拟环境已存在
)

:: 激活虚拟环境
echo [2/3] 激活虚拟环境...
call .venv\Scripts\activate.bat

:: 安装依赖
echo [3/3] 安装依赖包...
pip install -r requirements.txt

echo.
echo ==========================================
echo   环境设置完成！
echo ==========================================
echo.
echo 运行 start.bat 启动服务器
echo.
pause
