# FIT3077 Ticket to Ride Prototype

This repository contains the Sprint 3 Python/Tkinter prototype for Ticket to Ride: London.

## Repository Organisation

- `app/` contains the runnable game source code, tests, and map assets.
- `Sprint 1/` contains Sprint 1 submission artifacts.
- `Sprint 2/` contains Sprint 2 submission artifacts only.
- `Sprint 3/` contains Sprint 3 submission artifacts and the PyInstaller build spec.
- `prototypes/` contains earlier individual prototype files.

## Target Platform

The executable is built for Windows.

## Run the Executable

Open PowerShell in the repository root, then run:

```powershell
python -m pip install sv-ttk
python app\main.py
```

The setup window opens first. Enter the player names, then start the game.

## Build the Sprint 3 Executable

The Sprint 3 executable is built from the tracked PyInstaller spec file at `Sprint 3/TicketToRideLondon.spec`. This spec packages the game source, Tkinter UI code, theme files, and map assets.

Open PowerShell in the repository root, then run:

```powershell
python -m pip install pyinstaller sv-ttk
python -m PyInstaller "Sprint 3\TicketToRideLondon.spec" --noconfirm --distpath app\dist --workpath app\build
```

After the build finishes, the executable is created at:

```powershell
app\dist\TicketToRideLondon.exe
```

## Run the Sprint 3 Executable

From the repository root:

```powershell
cd app\dist
.\TicketToRideLondon.exe
```

## If the Build Command Fails

Make sure Python and PyInstaller are available on the build machine:

```powershell
python --version
python -m PyInstaller --version
```

If PyInstaller is missing, install it with:

```powershell
python -m pip install pyinstaller
```

Then run the Sprint 3 build command again.
