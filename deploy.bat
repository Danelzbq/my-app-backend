@echo off
chcp 65001 >nul
echo ==========================================
echo   上传项目到 GitHub
echo ==========================================
echo.

:: 检查 git
git --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Git，请先安装 Git
    echo 下载地址: https://git-scm.com/download/win
    pause
    exit /b 1
)

:: 初始化仓库（如果未初始化）
if not exist ".git" (
    echo [1] 初始化 Git 仓库...
    git init
) else (
    echo [1] Git 仓库已存在
)

:: 添加所有文件
echo [2] 添加文件到暂存区...
git add .

:: 提交
echo [3] 提交更改...
git commit -m "Initial commit: FastAPI blog backend"

:: 提示添加远程仓库
echo.
echo ==========================================
echo   下一步操作
echo ==========================================
echo.
echo 1. 在 GitHub 创建新仓库: https://github.com/new
echo.
echo 2. 复制仓库地址（例如: https://github.com/用户名/仓库名.git）
echo.
echo 3. 运行以下命令连接远程仓库并推送:
echo.
echo    git remote add origin [你的仓库地址]
echo    git branch -M main
echo    git push -u origin main
echo.
echo 或者直接运行 push.bat 脚本
echo.
pause
