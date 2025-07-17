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
        [str(appimage), str(arquivo_c), "-o", str(arquivo_xml)],
        env=env,
        check=True
    )

    print(f"✅ arquivo.xml gerado com sucesso em: {arquivo_xml}")

c2xml("arquivo.c")