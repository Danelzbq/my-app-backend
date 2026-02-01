@echo off
chcp 65001 >nul
echo ==========================================
echo   启动 Blog API 服务器
echo ==========================================
echo.

:: 检查虚拟环境
if not exist ".venv\Scripts\activate.bat" (
    echo [错误] 虚拟环境不存在，请先运行 setup.bat
    pause
    exit /b 1
)

:: 激活虚拟环境
call .venv\Scripts\activate.bat

:: 启动服务器
echo [INFO] 正在启动服务器...
echo [INFO] API文档: http://localhost:8000/docs
echo [INFO] 按 CTRL+C 停止服务器
echo.
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
