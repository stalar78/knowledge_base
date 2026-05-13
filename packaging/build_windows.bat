@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "SCRIPT_DIR=%~dp0"
pushd "%SCRIPT_DIR%.."
set "PROJECT_ROOT=%CD%"
set "PYI_DIST=%PROJECT_ROOT%\dist\_pyinstaller"
set "FINAL_DIST=%PROJECT_ROOT%\dist\GPTCourseKnowledgeExtractor"
set "RUNNER_RAW_DIR=%PYI_DIST%\GPTCourseKnowledgeRunner"
set "GUI_RAW_DIR=%PYI_DIST%\GPTCourseKnowledgeExtractor"
set "RUNNER_RAW_EXE=%RUNNER_RAW_DIR%\GPTCourseKnowledgeRunner.exe"
set "GUI_RAW_EXE=%GUI_RAW_DIR%\GPTCourseKnowledgeExtractor.exe"

echo [INFO] Project root: %PROJECT_ROOT%
echo [INFO] Raw PyInstaller dist: %PYI_DIST%
echo [INFO] Final portable dist: %FINAL_DIST%

python -m PyInstaller --version >nul 2>&1
if errorlevel 1 (
  echo [ERROR] PyInstaller is not installed.
  echo [HINT]  Run: python -m pip install pyinstaller
  popd
  exit /b 1
)

if exist "%PYI_DIST%" rmdir /s /q "%PYI_DIST%"
if exist "%PROJECT_ROOT%\build\pyinstaller" rmdir /s /q "%PROJECT_ROOT%\build\pyinstaller"
if exist "%FINAL_DIST%" rmdir /s /q "%FINAL_DIST%"

echo [INFO] Building GPTCourseKnowledgeRunner...
python -m PyInstaller --noconfirm --distpath "%PYI_DIST%" "%PROJECT_ROOT%\packaging\GPTCourseKnowledgeRunner.spec"
if errorlevel 1 (
  echo [ERROR] Runner build failed.
  popd
  exit /b 1
)

echo [INFO] Building GPTCourseKnowledgeExtractor...
python -m PyInstaller --noconfirm --distpath "%PYI_DIST%" "%PROJECT_ROOT%\packaging\GPTCourseKnowledgeExtractor.spec"
if errorlevel 1 (
  echo [ERROR] GUI build failed.
  popd
  exit /b 1
)

echo [INFO] Raw runner dist path: %RUNNER_RAW_DIR%
echo [INFO] Raw GUI dist path: %GUI_RAW_DIR%
echo [INFO] Final portable path: %FINAL_DIST%

mkdir "%FINAL_DIST%"

echo [INFO] Collecting portable files...

if not exist "%GUI_RAW_EXE%" (
  echo [ERROR] Could not find GPTCourseKnowledgeExtractor.exe
  echo [ERROR] Expected path: %GUI_RAW_EXE%
  popd
  exit /b 1
)

xcopy /e /i /y "%GUI_RAW_DIR%\*" "%FINAL_DIST%\" >nul
if errorlevel 1 (
  echo [ERROR] Failed to copy GUI portable files.
  echo [ERROR] Source path: %GUI_RAW_DIR%
  popd
  exit /b 1
)

if not exist "%RUNNER_RAW_EXE%" (
  echo [ERROR] Could not find GPTCourseKnowledgeRunner.exe
  echo [ERROR] Expected path: %RUNNER_RAW_EXE%
  popd
  exit /b 1
)

copy /y "%RUNNER_RAW_EXE%" "%FINAL_DIST%\GPTCourseKnowledgeRunner.exe" >nul
if errorlevel 1 (
  echo [ERROR] Failed to copy GPTCourseKnowledgeRunner.exe to portable folder.
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
