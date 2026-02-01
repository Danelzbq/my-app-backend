@echo off
chcp 65001 >nul
echo ==========================================
echo   推送到 GitHub
echo ==========================================
echo.

:: 提示输入仓库地址
set /p REPO_URL="请输入 GitHub 仓库地址: "

if "%REPO_URL%"=="" (
    echo [错误] 仓库地址不能为空
    pause
    exit /b 1
)

echo.
echo [1] 添加远程仓库...
git remote remove origin 2>nul
git remote add origin %REPO_URL%

echo [2] 切换到 main 分支...
git branch -M main

echo [3] 推送到 GitHub...
git push -u origin main

echo.
echo ==========================================
echo   推送完成！
echo ==========================================
echo.
pause
