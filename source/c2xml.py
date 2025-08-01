import subprocess
import os
from pathlib import Path

def c2xml(name):
    root = Path(__file__).parent.parent
    appimage = root / "srcml" / "srcml-x86_64.AppImage"
    arquivo_c = root / f"{name}"
    arquivo_xml = root / f"{name}.xml"

    env = os.environ.copy()
    env["APPIMAGE_EXTRACT_AND_RUN"] = "1"

    subprocess.run(
        [str(appimage), str(arquivo_c), "--position", "-o", str(arquivo_xml)],
        env=env,
        check=True
    )
    print("\033[1;33mWARNING: If there are syntax errors in C, srcML will generate corrupted XML, resulting in a corrupted .clearly file! Ensure the syntax of your C code is correct by running it with your preferred compiler.")
    print(f"\033[1;32m✅ arquivo.xml gerado com sucesso em: {arquivo_xml}")

c2xml("arquivo.c")
