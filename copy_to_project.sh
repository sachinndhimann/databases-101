#!/usr/bin/env bash
# Copies database-101/ into $PROJECT_ROOT (defaults to current directory).
# Usage: PROJECT_ROOT=/path/to/target ./copy_to_project.sh
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-$(pwd)}"
SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Copying database-101/ into: $PROJECT_ROOT/database-101"
mkdir -p "$PROJECT_ROOT/database-101"
cp -R "$SRC_DIR"/* "$PROJECT_ROOT/database-101/"

echo "Done. Next steps:"
echo "  cd $PROJECT_ROOT/database-101"
echo "  cp .env.example .env"
echo "  make up && make venv && source .venv/bin/activate && make install"
