# Pokyny pro Codex

Toto je Windows varianta projektu [WoW Fishing Forever](https://github.com/rsamf/wow-fishing-forever) pod licencí MIT. Při zprovoznění na dalším PC postupuj z kořene tohoto klonu. [README.md](README.md) popisuje klávesy a postup před každou relací i po ní.

## Instalace na Windows x64

Pokud není k dispozici `uv`, stáhni oficiální archiv `uv-x86_64-pc-windows-msvc.zip` z [Astral uv Releases](https://github.com/astral-sh/uv/releases/latest) a rozbal jej do `.local/uv`, aby v ní byl `uv.exe`. V PowerShellu spusť:

```powershell
$env:UV_CACHE_DIR = Join-Path $PWD '.local\cache'
$env:UV_PYTHON_INSTALL_DIR = Join-Path $PWD '.local\python'
$env:UV_NO_REGISTRY = '1'
.\.local\uv\uv.exe sync --locked --python 3.13 --managed-python --no-dev
.\RiverDesk.cmd doctor
```

Pokud už je `uv` v PATH, lze místo `.\.local\uv\uv.exe` použít `uv`. Po instalaci otevři GUI příkazem `.\RiverDesk.cmd`. Chybějící okno hry v diagnostice je očekávané, pokud WoW neběží. Pro kontrolu instalace stačí diagnostika a otevření GUI.

## Nastavení

- Zachovej uživatelovo funkční nastavení kláves. Při nové instalaci použij hodnoty pro kartu **Setup** uvedené v README. Ve WoW zůstává Fishing na `ú` a Interact With Target na `)`.
- Místní konfigurace je v `.local/state/config/config.toml`. Pokud ji uživatel přenáší, zkopíruj ji přímo mezi počítači. Zachovej ostatní uložené hodnoty. `.local/` a `.venv/` patří mimo Git.
- Windows spouštěč je `RiverDesk.cmd`, jeho vstup v Pythonu je `scripts/river_desk.py`. Klávesy mapuje `src/wowfish/input/keys.py`.
