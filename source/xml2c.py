import subprocess
import os
from pathlib import Path

def xml2c(xml_filename: str):
    root = Path(__file__).parent.parent
    appimage = root / "srcml" / "srcml-x86_64.AppImage"
    arquivo_xml = root / xml_filename

    if not arquivo_xml.exists():
        raise FileNotFoundError(f"Arquivo XML não encontrado: {arquivo_xml}")

    if xml_filename.endswith(".xml"):
        arquivo_c = root / xml_filename.replace(".xml", "")
    else:
        raise ValueError("O nome do arquivo XML deve terminar com .xml")

    env = os.environ.copy()
    env["APPIMAGE_EXTRACT_AND_RUN"] = "1"

    # Sem a flag --from=srcML
    subprocess.run(
        [str(appimage), str(arquivo_xml), "-o", str(arquivo_c)],
        env=env,
        check=True
    )

    print(f"✅ {arquivo_c.name} gerado com sucesso em: {arquivo_c}")

# Exemplo de uso
xml2c("variables.xml")
