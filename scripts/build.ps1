$ErrorActionPreference = "Stop"

python -m PyInstaller `
  --noconfirm `
  --windowed `
  --distpath "release" `
  --name "Loop Adventure" `
  --add-data "logoloop.png;." `
  main.py
