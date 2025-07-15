import subprocess
import os
from pathlib import Path

root = Path(__file__).parent
appimage = root / "srcml" / "srcml-x86_64.AppImage"
arquivo_c = root / "arquivo.c"
arquivo_xml = root / "arquivo.xml"

env = os.environ.copy()
env["APPIMAGE_EXTRACT_AND_RUN"] = "1"

subprocess.run(
    [str(appimage), str(arquivo_c), "-o", str(arquivo_xml)],
    env=env,
    check=True
)

print(f"✅ arquivo.xml gerado com sucesso em: {arquivo_xml}")
