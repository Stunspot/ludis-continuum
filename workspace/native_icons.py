"""Optional Windows icon binding for the existing Ludis launcher."""
import os
from pathlib import Path
import subprocess


def bind_windows(root=None):
    root = Path(root or Path(__file__).resolve().parent).resolve()
    if os.name != "nt":
        return {"status": "not_applicable", "platform": os.name}
    def quote(value):
        return "'" + str(value).replace("'", "''") + "'"
    script = (
        "$ErrorActionPreference='Stop';$taskShell=New-Object -ComObject WScript.Shell;"
        "$taskShortcut=$taskShell.CreateShortcut(" + quote(root / "Open Ludis.lnk") + ");"
        "$taskShortcut.TargetPath=" + quote(root / "Open Ludis.cmd") + ";"
        "$taskShortcut.WorkingDirectory=" + quote(root) + ";"
        "$taskShortcut.IconLocation=" + quote(str(root / "ludis.ico") + ",0") + ";"
        "$taskShortcut.Description='Ludis Continuum session desk';$taskShortcut.Save()"
    )
    try:
        shell = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32/WindowsPowerShell/v1.0/powershell.exe"
        subprocess.run([str(shell), "-NoProfile", "-NonInteractive", "-Command", script],
                       check=True, capture_output=True, timeout=10,
                       creationflags=subprocess.CREATE_NO_WINDOW)
        return {"status": "bound", "platform": "windows", "entry": str(root / "Open Ludis.lnk")}
    except (OSError, subprocess.TimeoutExpired, subprocess.CalledProcessError) as error:
        return {"status": "unavailable", "platform": "windows", "detail": str(error)[:240]}
