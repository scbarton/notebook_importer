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

/usr/local/bin/platypus \
  --name "Notebook Importer" \
  --interface-type "None" \
  --interpreter "/bin/bash" \
  --droppable \
  --suffixes "ipynb" \
  --app-icon "$DIR/icon.icns" \
  --bundled-file "$DIR/import_ipynb.py" \
  --bundled-file "$DIR/uv" \
  --app-version "$VERSION" \
  --bundle-identifier "org.scott.notebook-importer" \
  --quit-after-execution \
  --overwrite \
  "$DIR/import_ipynb.sh" \
  "$OUT"

rm "$DIR/uv"

# Patch Info.plist: extension-only, no UTI declarations
plutil -remove UTExportedTypeDeclarations "$OUT/Contents/Info.plist" 2>/dev/null || true
plutil -remove UTImportedTypeDeclarations "$OUT/Contents/Info.plist" 2>/dev/null || true
plutil -replace CFBundleDocumentTypes -json \
  '[{"CFBundleTypeExtensions":["ipynb"],"CFBundleTypeRole":"Viewer"}]' \
  "$OUT/Contents/Info.plist"

echo "Built: $OUT (v$VERSION)"
