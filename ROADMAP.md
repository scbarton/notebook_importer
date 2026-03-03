# Roadmap

## v1.0
- [ ] Cross-platform dialog support (replace `osascript` with `tkinter`)

## v1.x — Cross-platform support

The core conversion logic is already cross-platform. The main work is replacing
macOS-specific components with portable equivalents.

### Linux
- [ ] Package as PyInstaller binary
- [ ] `.desktop` file for "Open With..." registration
- [ ] MIME type definition for `.ipynb`
- [ ] Install script to register MIME and desktop databases

### Windows
- [ ] Package as PyInstaller `.exe`
- [ ] Registry entries for `.ipynb` "Open With..." association
- [ ] Inno Setup installer to handle registration
