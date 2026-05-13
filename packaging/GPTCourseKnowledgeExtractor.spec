# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

_SPEC_PATH = Path(globals().get("__file__", SPEC)).resolve()
PROJECT_ROOT = _SPEC_PATH.parent.parent

def safe_collect_submodules(name: str) -> list[str]:
    try:
        return collect_submodules(name)
    except Exception:
        return []


def safe_collect_data_files(name: str) -> list[tuple[str, str]]:
    try:
        return collect_data_files(name)
    except Exception:
        return []


hiddenimports = []
hiddenimports += safe_collect_submodules("src")
hiddenimports += safe_collect_submodules("faster_whisper")
hiddenimports += safe_collect_submodules("ctranslate2")
hiddenimports += safe_collect_submodules("huggingface_hub")
hiddenimports += safe_collect_submodules("tokenizers")
hiddenimports += safe_collect_submodules("onnxruntime")
hiddenimports += safe_collect_submodules("numpy")

datas = [(str(PROJECT_ROOT / "config"), "config")]
datas += safe_collect_data_files("faster_whisper")
datas += safe_collect_data_files("huggingface_hub")
datas += safe_collect_data_files("tokenizers")

a = Analysis(
    [str(PROJECT_ROOT / "src" / "gui_app.py")],
    pathex=[str(PROJECT_ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="GPTCourseKnowledgeExtractor",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="GPTCourseKnowledgeExtractor",
)
