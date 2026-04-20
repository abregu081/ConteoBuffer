from pathlib import Path
from cx_Freeze import setup, Executable

BASE_DIR = Path(__file__).resolve().parent

build_exe_options = {
    "excludes": ["tkinter", "unittest", "test", "tests"],
    "include_files": [
        (str(BASE_DIR / "Configuraciones.cfg"), "Configuraciones.cfg"),
    ],
}

setup(
    name="Traductor_Router",
    description="Traductor Router - Motrex / ContadorBUFFERS",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(str(BASE_DIR / "Main.py"), base=None, target_name="ContadorBuffer.exe")
    ],
)