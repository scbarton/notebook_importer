#!/bin/bash
set -e

VERSION="0.9"

DIR="$(cd "$(dirname "$0")" && pwd)"
OUT="$DIR/Notebook Importer.app"

# Regenerate icon
/Users/scott/opt/venv/python3.12/bin/python "$DIR/make_icon.py"

# Build universal uv binary (arm64 + x86_64)
UV_VERSION="$(uv --version | awk '{print $2}')"
echo "Fetching uv $UV_VERSION x86_64..."
curl -fsSL "https://github.com/astral-sh/uv/releases/download/${UV_VERSION}/uv-x86_64-apple-darwin.tar.gz" \
  | tar -xz -C /tmp --strip-components=1 uv-x86_64-apple-darwin/uv
lipo -create /opt/homebrew/bin/uv /tmp/uv -output "$DIR/uv"
rm /tmp/uv
echo "Built universal uv binary"

rm -rf "$OUT"

/usr/local/bin/platypus \
  --name "Notebook Importer" \
  --interface-type "None" \
  --interpreter "/bin/bash" \
  --droppable \
  --suffixes "ipynb" \
  --bundled-file "$DIR/import_ipynb.py" \
  --bundled-file "$DIR/uv" \
  --app-version "$VERSION" \
  --bundle-identifier "org.scott.notebook-importer" \
  --quit-after-execution \
  "$DIR/import_ipynb.sh" \
  "$OUT"

rm "$DIR/uv"

# Replace Platypus-composited icon with raw icon
cp "$DIR/icon.icns" "$OUT/Contents/Resources/AppIcon.icns"

# Set custom Finder icon via NSWorkspace (same as dragging icon in Get Info)
/usr/bin/python3 -c "
import AppKit
img = AppKit.NSImage.alloc().initWithContentsOfFile_('$DIR/icon.icns')
AppKit.NSWorkspace.sharedWorkspace().setIcon_forFile_options_(img, '$OUT', 0)
"

# Patch Info.plist: icon, extension-only doc types, no UTI declarations
plutil -replace CFBundleIconFile -string "AppIcon" "$OUT/Contents/Info.plist"
plutil -remove UTExportedTypeDeclarations "$OUT/Contents/Info.plist" 2>/dev/null || true
plutil -remove UTImportedTypeDeclarations "$OUT/Contents/Info.plist" 2>/dev/null || true
plutil -replace CFBundleDocumentTypes -json \
  '[{"CFBundleTypeExtensions":["ipynb"],"CFBundleTypeRole":"Viewer"}]' \
  "$OUT/Contents/Info.plist"

echo "Built: $OUT (v$VERSION)"
