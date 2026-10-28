# Building from source

These steps reproduce the Windows `onedir` application layout from the source in this repository. The program itself uses only Python's standard library; PyInstaller is needed only to package it as an executable.

## Build environment

- Windows 10/11, 64-bit
- Python 3.14, 64-bit, with Tcl/Tk selected in the Python installer
- PyInstaller 6.22.3 (pinned in `requirements-build.txt`)
- Network access during setup only, to install the pinned packaging tool and its dependencies from PyPI

## Build commands

Open PowerShell in the repository root and run:

```powershell
py -3.14 -m venv .venv-build
.\.venv-build\Scripts\python.exe -m pip install --upgrade pip
.\.venv-build\Scripts\python.exe -m pip install -r requirements-build.txt
.\.venv-build\Scripts\python.exe -m PyInstaller --clean --noconfirm --windowed --onedir --name Breathedge2SaveEditor --distpath .\dist --workpath .\build\work .\Breathedge2SaveEditor.py
```

The build output is:

```text
dist\Breathedge2SaveEditor\Breathedge2SaveEditor.exe
dist\Breathedge2SaveEditor\_internal\...
```

Run the executable from that output directory. Do not move the executable away from `_internal`; PyInstaller's one-directory build needs the adjacent runtime files. If PowerShell blocks script activation, these commands do not require activation because they call the virtual-environment Python executable directly.

## Repackaging a Nexus archive

Copy `README.md` and `Breathedge2SaveEditor.py` into the generated `dist\Breathedge2SaveEditor` folder. Add the Nexus page description as `Nexus_Description.txt` if desired. Zip the contents of that folder (including `_internal`) so the archive extracts to one `Breathedge2SaveEditor` directory. The source code is not required in the end-user release archive when a public source repository is linked from the Nexus page.

The original Nexus release was built as a PyInstaller `onedir` Windows package. Builds made with another Python or PyInstaller patch version may differ byte-for-byte while containing the same source and functionality.

## Dependency inventory

- Application runtime: Python standard library only (`tkinter`, `struct`, `hashlib`, `pathlib`, and other standard modules).
- Build-time: `pyinstaller==6.22.3` and its declared PyPI dependencies.
- No UE4SS, game binaries, game assets, network service, or runtime installer is required by the Save Editor.
