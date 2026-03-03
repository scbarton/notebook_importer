# Notebook Importer

A macOS drag-and-drop app that converts Jupyter notebooks (`.ipynb`) into Obsidian notes.

## Features

- Drag one or more `.ipynb` files onto the app to import them
- Converts notebook cells and output to Markdown
- Extracts output images (plots, figures) as attachments
- Copies the original `.ipynb` file as an attachment
- Adds frontmatter with links back to the source file and attachment
- Opens the created note in Obsidian automatically
- Supports dropping multiple notebooks at once

## Installation

Download `Notebook Importer.zip` from the [Releases](../../releases) page, unzip, and drag the app to your Applications folder.

On first launch macOS may show a security prompt — click Open to proceed.

## Usage

**First drop:** the app will ask you to configure three settings:

| Setting | Description | Default |
|---------|-------------|---------|
| Vault folder | Your Obsidian vault root | — |
| Assets folder | Where attachments are stored, relative to vault root | `Attachments` |
| Notes folder | Where notes are created, relative to vault root | vault root |

Settings are saved to `~/.config/obsidian-ipynb-import/prefs.json`.

**Subsequent drops:** drag any `.ipynb` file (or a selection of files) onto the app. Each notebook is converted and opened in Obsidian immediately.

**Reconfigure:** double-click the app to view current settings or reconfigure.

## What gets created

For a notebook named `my_analysis.ipynb`, the import produces:

```
vault/
  Notes/
    my_analysis.md          ← converted note
  Attachments/
    my_analysis/
      my_analysis.ipynb     ← original notebook
      output_1.png          ← extracted output images (if any)
```

The note includes YAML frontmatter:

```yaml
---
source: "file:///path/to/original/my_analysis.ipynb"
notebook: "[[my_analysis/my_analysis.ipynb]]"
---
```

`source` links to the original file location. `notebook` is an Obsidian wikilink to the attached copy.

## First-run note

On the very first import, `uv` installs `nbconvert` into its cache — this takes about 30 seconds. All subsequent imports are instant.

## Building from source

Requirements:
- Xcode Command Line Tools (`xcode-select --install`)
- [Platypus](https://sveinbjorn.org/platypus) (`brew install --cask platypus`), with the command line tool installed via **Platypus → Install Command Line Tool**
- [uv](https://github.com/astral-sh/uv) (`brew install uv`)
- Python 3 with Pillow (for icon generation — `pip install Pillow`)

```bash
./build.sh
```

This produces `Notebook Importer.app` in the project directory. The app is unsigned; macOS will prompt on first launch — right-click → Open to bypass Gatekeeper.

## License

MIT
