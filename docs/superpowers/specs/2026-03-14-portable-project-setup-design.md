# Design: Portable Project Setup — GCS USV

**Date:** 2026-03-14
**Status:** Approved
**Goal:** Transform GCS_USV into a professional, self-contained project anyone can clone and run with simple scripts on Ubuntu Linux.

---

## 1. Scope

- Remove Firebase entirely (optional feature, credentials in repo = security issue)
- Replace `~/venv-ardupilot` global venv with project-local `.venv/`
- Reorganize file structure: source into `src/gcs_usv/`, all tests into `tests/`
- Delete artifacts, debug files, and dev leftovers
- Add polished install/run/verify scripts with colored output
- Add `pyproject.toml` with pinned dependencies
- Rewrite README for USV/competition context
- Full ArduPilot SITL setup automated in `install.sh`

---

## 2. File Structure

### Deleted (artifacts, Firebase, leftovers)
```
eeprom.bin, mav.parm, mav.tlog, mav.tlog.raw
debug_mission.py
deneme/, experiment/, vanttec_usv/, gazebo/
Database/, FirebaseUserTest.py
TelemetryWidget.py.backup
serial.tools.list_ports
Ground-Control-Station-for-UAV.pyproject
Ground-Control-Station-for-UAV.pyproject.user
commands.txt, komutlar.txt
ENHANCED_TELEMETRY_SUMMARY.md, ENHANCEMENT_SUMMARY.md  ← dev leftovers
Readme.md                      ← replaced by README.md (rewritten)
map.html                       ← runtime-generated, added to .gitignore
venv/                          ← recreated by install.sh as .venv/
Root-level test_*.py files     ← moved to tests/
requirements.txt               ← replaced by pyproject.toml
```

### New Layout
```
GCS_USV/
├── src/
│   └── gcs_usv/
│       ├── __init__.py
│       ├── main.py
│       ├── MainWindow.py
│       ├── HomePage.py
│       ├── IndicatorsPage.py
│       ├── TargetsPage.py
│       ├── MapWidget.py
│       ├── TelemetryWidget.py
│       ├── USVTelemetryWidget.py
│       ├── CameraWidget.py
│       ├── IconUtils.py
│       ├── AntennaTracker.py
│       ├── MediaPlayer.py
│       ├── indicators_rc.py
│       ├── vehicle/
│       │   ├── __init__.py
│       │   ├── ArdupilotConnection.py
│       │   └── Exploration.py
│       └── uifolder/
│           ├── __init__.py
│           ├── *.ui
│           ├── ui_*.py
│           └── assets/
├── tests/
│   ├── conftest.py
│   └── test_*.py              ← all tests consolidated here
├── scripts/
│   ├── install.sh
│   ├── run.sh
│   ├── sitl.sh
│   ├── update.sh
│   └── verify.sh
├── config/
│   └── boat.parm              ← FRAME_CLASS=2 + boat tuning params
├── docs/
│   ├── superpowers/specs/
│   └── screenshots/
├── .gitignore
├── pyproject.toml
├── pytest.ini
└── README.md
```

---

## 3. Dependency Management

Replace bare `requirements.txt` with `pyproject.toml`:

```toml
[project]
name = "gcs-usv"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "PySide6==6.9.1",
    "pymavlink>=2.4.41",
    "folium>=0.18.0",
    "Pillow>=10.0.0",
    "pyserial>=3.5",
]

[project.optional-dependencies]
dev = ["pytest", "pytest-qt", "mypy", "flake8"]

[project.scripts]
gcs-usv = "gcs_usv.main:main"

[tool.setuptools.packages.find]
where = ["src"]

[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"
```

Local `.venv/` lives at `GCS_USV/.venv/` — never `~/venv-ardupilot` again.

`install.sh` step 3 must run `pip install -e .[dev]` (editable install). This adds `src/` to `sys.path` via the `.pth` mechanism, which is what makes all intra-package flat imports work at runtime when running `python src/gcs_usv/main.py`.

---

## 4. Scripts

### `install.sh` — main event (colored, guided, idempotent)

```
[GCS USV] Installation
═══════════════════════════════════
[1/6] Checking system (Ubuntu/Debian, Python 3.12)...
[2/6] Installing system dependencies (apt)...
[3/6] Creating local .venv and installing Python deps...
[4/6] Cloning ArduPilot + installing SITL prerequisites...
[5/6] Building ArduPilot Rover SITL binary...
[6/6] Applying boat parameters (FRAME_CLASS=2)...

 GCS USV ready! Run ./run.sh to start.
```

**Step 2 apt packages (minimum required on a fresh Ubuntu install):**
```bash
sudo apt-get install -y \
  git python3.12 python3.12-venv python3-pip \
  libxcb-cursor0 libxcb-icccm4 libxcb-image0 \
  libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 \
  libxcb-xinerama0 libgl1 libegl1 libdbus-1-3
```

**ArduPilot setup steps (inside step 4/5):**
```bash
# Clone with ALL submodules (required — SITL won't build without them)
git clone --recurse-submodules https://github.com/ArduPilot/ardupilot ~/ardupilot

cd ~/ardupilot

# Official prereq installer: installs MAVProxy + all build dependencies
Tools/environment_install/install-prereqs-ubuntu.sh -y

# Reload PATH (required for waf and sim_vehicle.py to be found)
source ~/.profile

# Build SITL binary for Rover
./waf configure --board sitl
./waf rover

# Add Tools/autotest to PATH permanently (exposes sim_vehicle.py)
echo 'export PATH=$PATH:$HOME/ardupilot/Tools/autotest' >> ~/.bashrc
source ~/.bashrc
```

**Flags:**
- `--skip-sitl` — skip ArduPilot clone + build
- `--skip-apt` — skip apt installs (CI / already provisioned)
- `--verbose` — show full output instead of progress indicators

**Idempotency:** re-running skips steps already done (checks for `~/ardupilot`, `.venv/`, built binary).

### `sitl.sh` — launch SITL pre-configured as boat

```bash
sim_vehicle.py -v Rover --console --map \
  --add-param-file=config/boat.parm \
  --mavproxy-args="--cmd='param set FRAME_CLASS 2; param save'"
```

### `run.sh` — launch the GCS
Activates `.venv/`, runs `python src/gcs_usv/main.py`.

### `update.sh` — pull latest + sync deps
`git pull` → `pip install -e .` → done.

### `verify.sh` — smoke test everything
1. Imports all GCS modules (catches broken deps)
2. Launches SITL headlessly via `sim_vehicle.py -v Rover --no-mavproxy` (no GUI, direct TCP), connects via pymavlink
3. Reads `FRAME_CLASS` param — asserts value == 2
4. Exits SITL, runs `pytest tests/` headless
5. Prints pass/fail summary

If `DISPLAY` is unset (CI environment), step 2 is skipped with a warning. The `--no-mavproxy` flag avoids opening MAVProxy's GUI and allows a direct pymavlink TCP connection on port 5760.

---

## 5. Boat Parameters (`config/boat.parm`)

```
FRAME_CLASS 2
```

Applied two ways for persistence:
- `--add-param-file=config/boat.parm` on every SITL launch
- `param set FRAME_CLASS 2; param save` via MAVProxy on startup

Manual override (inside MAVProxy console):
```
param set FRAME_CLASS 2
param save
```

---

## 6. `.gitignore` Additions

```
.venv/
__pycache__/
*.pyc
*.tlog
*.tlog.raw
*.bin
mav.*
map.html
logs/
*.log
Database/
Database/*.json
```

---

## 7. README Structure

```
# GCS USV — Ground Control Station for Unmanned Surface Vehicle

[screenshot]

Built for TEKNOFEST 2026 İnsansız Deniz Aracı competition.
Controls an ArduPilot Rover (FRAME_CLASS=2 boat) via MAVLink.

## Requirements
## Quick Start
## What install.sh Does       ← full step-by-step breakdown
## Manual SITL Param Setup    ← param set FRAME_CLASS 2 documented
## Update
## Project Structure
## Competition Notes (TEKNOFEST 2026)
## Development
```

---

## 8. Import Path Fix-ups Required After Move

With a `src/` layout, `pip install -e .` adds `src/` to `sys.path` — NOT `src/gcs_usv/`. This means **all flat imports between modules must be updated** to use the package prefix.

### Required import changes (all files moving to `src/gcs_usv/`)

**Cross-module imports** — change `from X import Y` → `from gcs_usv.X import Y`:
- `main.py`: `from MainWindow import MainWindow` → `from gcs_usv.MainWindow import MainWindow`
- `MainWindow.py`: `from HomePage import …` → `from gcs_usv.HomePage import …`, same for `TargetsPage`, `IndicatorsPage`, `AntennaTracker`, etc.
- `HomePage.py`: `from MapWidget import …` → `from gcs_usv.MapWidget import …`, same for `CameraWidget`, `TelemetryWidget`
- All similar flat imports in every file under `src/gcs_usv/`

**Vehicle subpackage** — `Vehicle/` becomes `src/gcs_usv/vehicle/` (lowercase):
- `from Vehicle.ArdupilotConnection import ArdupilotConnectionThread` → `from gcs_usv.vehicle.ArdupilotConnection import ArdupilotConnectionThread`
- `from Vehicle.Exploration import ExplorationThread` → `from gcs_usv.vehicle.Exploration import ExplorationThread`
- Affected: `MainWindow.py` and all test files in `tests/` that import from `Vehicle.*`
- `src/gcs_usv/vehicle/__init__.py` must be **created** (does not exist currently)

**UI resource import**:
- `uifolder/ui_IndicatorsPage.py`: `import indicators_rc` → `from gcs_usv import indicators_rc`

**Firebase removal**:
- `CameraWidget.py`: `from Database.VideoStream import VideoStreamThread` — remove this import and the VideoStream usage entirely (Database/ is deleted)

### `main.py` entry point wrapper
The `pyproject.toml` console script `gcs-usv = "gcs_usv.main:main"` requires a callable. Add:
```python
def main():
    # existing if __name__ == '__main__' body here

if __name__ == '__main__':
    main()
```

## 9. What Does NOT Change

- Internal module logic (no business logic touched)
- `uifolder/` internal structure (except the `indicators_rc` import fix above)
- `pytest.ini`
- `CLAUDE.md` (updated to reflect new `.venv/` path)

---

## 10. Git History — Firebase Credentials

The Firebase credential JSON files (`Database/*.json`) are already tracked in git history. Simply deleting them does not remove them from history — they remain accessible via `git log`.

**Action required:** Scrub them from history using `git filter-repo`:
```bash
pip install git-filter-repo
git filter-repo --path Database/ --invert-paths --force
git filter-repo --path FirebaseUserTest.py --invert-paths --force
```
After scrubbing, force-push to remote to overwrite history.

If the credentials are already expired/revoked (Firebase service accounts can be deactivated in the Firebase console), note this in the README security section and proceed without scrubbing. Either way, `.gitignore` must block re-adding them.

---

## 11. Success Criteria

- [ ] Fresh Ubuntu machine: `git clone` + `./install.sh` produces a working GCS + SITL
- [ ] `./verify.sh` passes: FRAME_CLASS == 2, all imports resolve, tests green
- [ ] No secrets in repo (Firebase credentials gone from history, `.gitignore` blocks future accidents)
- [ ] `./run.sh` launches GCS without activating any global venv
- [ ] CLAUDE.md updated: references `.venv/` not `~/venv-ardupilot`
- [ ] `gcs-usv` CLI entry point works via `pyproject.toml` console script
