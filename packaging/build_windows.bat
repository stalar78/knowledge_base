@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "SCRIPT_DIR=%~dp0"
pushd "%SCRIPT_DIR%.."
set "PROJECT_ROOT=%CD%"

echo [INFO] Project root: %PROJECT_ROOT%

python -m PyInstaller --version >nul 2>&1
if errorlevel 1 (
  echo [ERROR] PyInstaller is not installed.
  echo [HINT]  Run: python -m pip install pyinstaller
  popd
  exit /b 1
)

echo [INFO] Building GPTCourseKnowledgeRunner...
python -m PyInstaller --noconfirm "%PROJECT_ROOT%\packaging\GPTCourseKnowledgeRunner.spec"
if errorlevel 1 (
  echo [ERROR] Runner build failed.
  popd
  exit /b 1
)

echo [INFO] Building GPTCourseKnowledgeExtractor...
python -m PyInstaller --noconfirm "%PROJECT_ROOT%\packaging\GPTCourseKnowledgeExtractor.spec"
if errorlevel 1 (
  echo [ERROR] GUI build failed.
  popd
  exit /b 1
)

set "FINAL_DIST=%PROJECT_ROOT%\dist\GPTCourseKnowledgeExtractor"
if exist "%FINAL_DIST%" rmdir /s /q "%FINAL_DIST%"
mkdir "%FINAL_DIST%"

echo [INFO] Collecting portable files...
copy /y "%PROJECT_ROOT%\dist\GPTCourseKnowledgeExtractor\GPTCourseKnowledgeExtractor.exe" "%FINAL_DIST%\" >nul
if errorlevel 1 (
  echo [ERROR] Could not find GPTCourseKnowledgeExtractor.exe
  popd
  exit /b 1
)

copy /y "%PROJECT_ROOT%\dist\GPTCourseKnowledgeRunner\GPTCourseKnowledgeRunner.exe" "%FINAL_DIST%\" >nul
if errorlevel 1 (
  echo [ERROR] Could not find GPTCourseKnowledgeRunner.exe
  popd
  exit /b 1
)

if exist "%PROJECT_ROOT%\config" (
  xcopy /e /i /y "%PROJECT_ROOT%\config" "%FINAL_DIST%\config" >nul
)

mkdir "%FINAL_DIST%\tools\ffmpeg" >nul 2>&1
if exist "%PROJECT_ROOT%\tools\ffmpeg\ffmpeg.exe" (
  copy /y "%PROJECT_ROOT%\tools\ffmpeg\ffmpeg.exe" "%FINAL_DIST%\tools\ffmpeg\" >nul
  echo [INFO] ffmpeg.exe copied to portable tools folder.
) else (
  echo [WARN] tools\ffmpeg\ffmpeg.exe not found. Portable build will rely on system PATH FFmpeg.
)

mkdir "%FINAL_DIST%\courses" >nul 2>&1

echo [INFO] Portable build ready:
echo        %FINAL_DIST%
popd
exit /b 0
