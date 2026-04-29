$ErrorActionPreference = "Stop"

if (-not (Test-Path ".venv")) {
  python -m venv .venv
}

.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env -ErrorAction SilentlyContinue

New-Item -ItemType Directory -Force -Path data | Out-Null
$env:APP_NAME = "Loop Adventure"
$env:DATABASE_URL = "sqlite:///data/os_transport.db"

python main.py
