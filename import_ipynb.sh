#!/bin/bash
# Bootstrap: find bundled uv and use it to run the Python script with its dependencies.
DIR="$(cd "$(dirname "$0")" && pwd)"
exec "$DIR/uv" run "$DIR/import_ipynb.py" "$@"
