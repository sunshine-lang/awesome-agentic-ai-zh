from pathlib import Path
import os


def load_dotenv(path=None, override=False):
    env_path = Path(path) if path else Path(__file__).with_name(".env")
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if override:
            os.environ[key] = value
        else:
            os.environ.setdefault(key, value)


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env.template")
load_dotenv(BASE_DIR / ".env", override=True)

BASE_URL = os.environ["OMLX_BASE_URL"]
API_KEY = os.environ["OMLX_API_KEY"]
MODEL = os.environ["OMLX_MODEL"]
