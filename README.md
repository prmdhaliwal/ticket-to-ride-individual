# FIT3077 Ticket to Ride Prototype

This repository contains the Sprint 3 Python/Tkinter prototype for Ticket to Ride: London.

## Target Platform

The executable is built for Windows.

## Run the Executable

Open PowerShell in the repository root, then run:

```powershell
python -m pip install sv-ttk
python "Sprint 3\main.py"
```

The setup window opens first. Enter the player names, then start the game.

## Build the Sprint 3 Executable

The Sprint 3 executable is built from the tracked PyInstaller spec file at `Sprint 3/TicketToRideLondon.spec`. This spec packages the game source, Tkinter UI code, theme files, and map assets.

Open PowerShell in the repository root, then run:

```powershell
python -m pip install pyinstaller sv-ttk
cd "Sprint 3"
python -m PyInstaller TicketToRideLondon.spec --noconfirm
```

After the build finishes, the executable is created at:

```powershell
Sprint 3\dist\TicketToRideLondon.exe
```

## Run the Sprint 3 Executable

From the repository root:

```powershell
cd "Sprint 3\dist"
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
