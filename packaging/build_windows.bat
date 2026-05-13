@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "SCRIPT_DIR=%~dp0"
pushd "%SCRIPT_DIR%.."
set "PROJECT_ROOT=%CD%"
set "PYI_DIST=%PROJECT_ROOT%\dist\_pyinstaller"
set "FINAL_DIST=%PROJECT_ROOT%\dist\GPTCourseKnowledgeExtractor"
set "ZIP_PATH=%PROJECT_ROOT%\dist\GPTCourseKnowledgeExtractor-portable.zip"
set "RUNNER_RAW_DIR=%PYI_DIST%\GPTCourseKnowledgeRunner"
set "GUI_RAW_DIR=%PYI_DIST%\GPTCourseKnowledgeExtractor"
set "RUNNER_RAW_EXE=%RUNNER_RAW_DIR%\GPTCourseKnowledgeRunner.exe"
set "GUI_RAW_EXE=%GUI_RAW_DIR%\GPTCourseKnowledgeExtractor.exe"
set "TEMPLATES_DIR=%PROJECT_ROOT%\packaging\templates"

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
if exist "%ZIP_PATH%" del /f /q "%ZIP_PATH%"

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

if exist "%TEMPLATES_DIR%\START_HERE.bat" (
  copy /y "%TEMPLATES_DIR%\START_HERE.bat" "%FINAL_DIST%\START_HERE.bat" >nul
) else (
  echo [ERROR] Missing template: %TEMPLATES_DIR%\START_HERE.bat
  popd
  exit /b 1
)

if exist "%TEMPLATES_DIR%\README_PORTABLE.txt" (
  copy /y "%TEMPLATES_DIR%\README_PORTABLE.txt" "%FINAL_DIST%\README_PORTABLE.txt" >nul
) else (
  echo [ERROR] Missing template: %TEMPLATES_DIR%\README_PORTABLE.txt
  popd
  exit /b 1
)

if exist "%TEMPLATES_DIR%\README_FFMPEG.txt" (
  copy /y "%TEMPLATES_DIR%\README_FFMPEG.txt" "%FINAL_DIST%\tools\ffmpeg\README_FFMPEG.txt" >nul
)

if not exist "%FINAL_DIST%\GPTCourseKnowledgeExtractor.exe" (
  echo [ERROR] Required file missing: %FINAL_DIST%\GPTCourseKnowledgeExtractor.exe
  popd
  exit /b 1
)
if not exist "%FINAL_DIST%\GPTCourseKnowledgeRunner.exe" (
  echo [ERROR] Required file missing: %FINAL_DIST%\GPTCourseKnowledgeRunner.exe
  popd
  exit /b 1
)
if not exist "%FINAL_DIST%\config" (
  echo [ERROR] Required folder missing: %FINAL_DIST%\config
  popd
  exit /b 1
)
if not exist "%FINAL_DIST%\courses" (
  echo [ERROR] Required folder missing: %FINAL_DIST%\courses
  popd
  exit /b 1
)
if not exist "%FINAL_DIST%\tools\ffmpeg" (
  echo [ERROR] Required folder missing: %FINAL_DIST%\tools\ffmpeg
  popd
  exit /b 1
)
if not exist "%FINAL_DIST%\START_HERE.bat" (
  echo [ERROR] Required file missing: %FINAL_DIST%\START_HERE.bat
  popd
  exit /b 1
)
if not exist "%FINAL_DIST%\README_PORTABLE.txt" (
  echo [ERROR] Required file missing: %FINAL_DIST%\README_PORTABLE.txt
  popd
  exit /b 1
)

where powershell >nul 2>&1
if errorlevel 1 (
  echo [WARN] PowerShell not found. Skipping portable zip creation.
) else (
  powershell -NoProfile -ExecutionPolicy Bypass -Command "Compress-Archive -Path '%FINAL_DIST%\*' -DestinationPath '%ZIP_PATH%' -Force" >nul 2>&1
  if errorlevel 1 (
    echo [WARN] Failed to create portable zip: %ZIP_PATH%
  ) else (
    echo [INFO] Portable zip ready:
    echo        %ZIP_PATH%
  )
)

echo [INFO] Portable build ready:
echo        %FINAL_DIST%
popd
exit /b 0
