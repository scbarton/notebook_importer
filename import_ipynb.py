# /// script
# requires-python = ">=3.9"
# dependencies = ["nbconvert>=7.0", "nbformat>=5.0"]
# ///
"""
Jupyter Notebook to Obsidian importer.

When run via Platypus, dropped .ipynb files are passed as arguments.
On first run (no prefs), native config dialogs appear via osascript.
Prefs are stored at ~/.config/obsidian-ipynb-import/prefs.json

On first drop, uv installs nbconvert into its cache (~30s). Subsequent runs are instant.
"""

import re
import sys
import json
import shutil
import subprocess
import urllib.parse
from pathlib import Path
from typing import Optional

import nbformat
from nbconvert import MarkdownExporter

PREFS_PATH = Path.home() / ".config" / "obsidian-ipynb-import" / "prefs.json"


# ── osascript helpers ─────────────────────────────────────────────────────────

def _osascript(script: str) -> Optional[str]:
    r = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def alert(title: str, message: str) -> None:
    _osascript(f'display alert "{title}" message "{message}"')


def notify(message: str) -> None:
    _osascript(f'display notification "{message}" with title "Notebook Importer"')


# ── Preferences ───────────────────────────────────────────────────────────────

def load_prefs() -> dict:
    if PREFS_PATH.exists():
        return json.loads(PREFS_PATH.read_text())
    return {}


def save_prefs(prefs: dict) -> None:
    PREFS_PATH.parent.mkdir(parents=True, exist_ok=True)
    PREFS_PATH.write_text(json.dumps(prefs, indent=2))


def configure() -> Optional[dict]:
    """Show native config dialogs via osascript. Returns prefs dict or None if cancelled."""
    vault_path = _osascript('POSIX path of (choose folder with prompt "Select your Obsidian vault folder:")')
    if not vault_path:
        return None
    vault_path = vault_path.rstrip("/")

    assets_folder = _osascript(
        'text returned of (display dialog "Assets folder (relative to vault root):" '
        'default answer "Attachments" with title "Notebook Importer")'
    )
    if assets_folder is None:
        return None

    notes_folder = _osascript(
        'text returned of (display dialog "Notes destination folder (relative to vault root, '
        'leave blank for vault root):" default answer "" with title "Notebook Importer")'
    )
    if notes_folder is None:
        return None

    return {
        "vault": vault_path,
        "assets_folder": assets_folder or "Attachments",
        "notes_folder": notes_folder,
    }


# ── Import logic ──────────────────────────────────────────────────────────────

def sanitize_name(name: str) -> str:
    return re.sub(r'[\\/:*?"<>|#^[\]]', "-", name).strip()


def import_notebook(ipynb_path: Path, prefs: dict) -> Path:
    vault = Path(prefs["vault"])
    note_name = sanitize_name(ipynb_path.stem)

    notes_root = vault / prefs["notes_folder"] if prefs.get("notes_folder") else vault
    notes_root.mkdir(parents=True, exist_ok=True)
    note_dest = notes_root / f"{note_name}.md"

    asset_subdir = vault / prefs["assets_folder"] / note_name

    # Convert notebook to markdown
    nb = nbformat.read(str(ipynb_path), as_version=4)
    exporter = MarkdownExporter()
    body, resources = exporter.from_notebook_node(nb)

    # Save extracted output images (plots, etc.)
    outputs = resources.get("outputs", {})
    if outputs:
        asset_subdir.mkdir(parents=True, exist_ok=True)
        for filename, data in outputs.items():
            (asset_subdir / filename).write_bytes(data)

        # Rewrite image links to Obsidian wikilink format
        def rewrite(match):
            filename = Path(match.group(2)).name
            return f"![[{note_name}/{filename}]]"
        body = re.sub(r"!\[([^\]]*)\]\(([^)\s]+)\)", rewrite, body)

    note_dest.write_text(body, encoding="utf-8")

    vault_name = vault.name
    file_rel = str(note_dest.relative_to(vault).with_suffix(""))
    uri = f"obsidian://open?vault={urllib.parse.quote(vault_name)}&file={urllib.parse.quote(file_rel)}"
    subprocess.run(["open", uri])

    return note_dest


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    argv_paths = sys.argv[1:]
    stdin_paths = sys.stdin.read().splitlines() if not sys.stdin.isatty() else []
    all_paths = argv_paths or stdin_paths
    notebooks = [Path(p) for p in all_paths if p.endswith(".ipynb")]

    # Double-clicked with no files
    if not notebooks:
        prefs = load_prefs()
        if prefs.get("vault"):
            btn = _osascript(
                'button returned of (display dialog "Notebook Importer is configured." '
                '& return & return & "Vault: ' + prefs.get("vault", "") + '" '
                'buttons {"Reconfigure…", "OK"} default button "OK" with icon note)'
            )
            if btn == "Reconfigure…":
                new_prefs = configure()
                if new_prefs:
                    save_prefs(new_prefs)
                    notify("Settings saved.")
        else:
            new_prefs = configure()
            if new_prefs:
                save_prefs(new_prefs)
                notify("Settings saved.")
        return

    prefs = load_prefs()
    if not prefs.get("vault"):
        new_prefs = configure()
        if not new_prefs:
            return
        save_prefs(new_prefs)
        prefs = new_prefs

    errors = []
    imported = 0
    for nb_path in notebooks:
        try:
            import_notebook(nb_path, prefs)
            imported += 1
        except Exception as e:
            errors.append(f"{nb_path.name}: {e}")

    if errors:
        alert("Notebook Import", "\n".join(f"• {e}" for e in errors))
    elif imported > 0:
        notify(f"{imported} notebook(s) imported successfully.")


if __name__ == "__main__":
    main()
