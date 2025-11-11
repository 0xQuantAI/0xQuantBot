@echo off
REM Twitter News Bot - Quick Run Script for Windows

echo ╔═══════════════════════════════════════╗
echo ║   Twitter News Bot - Quick Launcher  ║
echo ╚═══════════════════════════════════════╝
echo.

REM Check if .env exists
if not exist .env (
    echo ⚠ No .env file found
    echo Creating .env from .env.example...
    copy .env.example .env
    echo Please edit .env with your credentials before running the bot
    pause
    exit /b 1
)

echo Select run mode:
echo 1. Run once (text only)
echo 2. Run once with image
echo 3. Run once with video placeholder
echo 4. Run on schedule (text only)
echo 5. Run on schedule with images
echo.
set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" (
    echo 🤖 Running bot once (text only)...
    call npm run once
) else if "%choice%"=="2" (
    echo 🎨 Running bot once with image...
    call npm run once:image
) else if "%choice%"=="3" (
    echo 🎬 Running bot once with video placeholder...
    call npm run once:video
) else if "%choice%"=="4" (
    echo ⏰ Starting scheduled bot (text only)...
    echo Press Ctrl+C to stop
    call npm run scheduled
) else if "%choice%"=="5" (
    echo ⏰🎨 Starting scheduled bot with images...
    echo Press Ctrl+C to stop
    call npm run scheduled:image
) else (
    echo Invalid choice
    pause
    exit /b 1
)

pause

