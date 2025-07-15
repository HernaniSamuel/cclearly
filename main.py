import subprocess
import os
from pathlib import Path

appimage = Path(__file__).parent / "srcml" / "srcml-x86_64.AppImage"
env = os.environ.copy()
env["APPIMAGE_EXTRACT_AND_RUN"] = "1"

result = subprocess.run([str(appimage), "--version"], env=env, check=True, capture_output=True, text=True)
print(result.stdout)
