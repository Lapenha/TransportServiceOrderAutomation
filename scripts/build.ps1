$ErrorActionPreference = "Stop"

python -m PyInstaller `
  --noconfirm `
  --windowed `
  --distpath "release" `
  --name "Loop Adventure" `
  --icon "loop_adventure.ico" `
  --add-data "logoloop.png;." `
  --add-data "loop_adventure.ico;." `
  main.py
