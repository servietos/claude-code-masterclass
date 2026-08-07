#!/usr/bin/env bash
# Copy a built deck out as a versioned, client-named deliverable.
# The build artifact keeps its own name; the shippable pair lands in
# <deck folder>/dist/<NAME>_v<VERSION>_<LANG>.{pptx,pdf}.
#
# Usage: bash package.sh <deck.pptx> <NAME> <VERSION> [LANG]
set -e
PPTX="$1"
NAME="$2"
VERSION="$3"
# Language is the one field most decks never vary, so it defaults.
LANG="${4:-EN}"

HERE="$(cd "$(dirname "$0")" && pwd)"
DIST="$(dirname "$PPTX")/dist"
BASE="${NAME}_v${VERSION}_${LANG}"
mkdir -p "$DIST"

bash "$HERE/make_pdf.sh" "$PPTX" >/dev/null

cp "$PPTX" "$DIST/$BASE.pptx"
cp "${PPTX%.pptx}.pdf" "$DIST/$BASE.pdf"
echo "Deliverable → $DIST/$BASE.pptx"
echo "Deliverable → $DIST/$BASE.pdf"
