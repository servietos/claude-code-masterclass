#!/usr/bin/env bash
# Render a built deck to an Acrobat-safe PDF.
#
# LibreOffice embeds variable fonts (Manrope/Inter) as Type-3, which makes
# Adobe Acrobat crash on open. We export via LibreOffice, then re-distill
# through Ghostscript to normalise the file into a clean, Acrobat-safe PDF.
#
# Requires: soffice (LibreOffice), gs (Ghostscript).
# Usage: bash make_pdf.sh <deck.pptx>
set -e
PPTX="$1"
# Swap the extension so the PDF lands beside the deck under the same stem.
OUT="${PPTX%.pptx}.pdf"
STEM="$(basename "${PPTX%.pptx}")"
TMP="$(mktemp -d)"

# A headless soffice left running from an earlier build holds a profile lock and
# the convert then produces nothing while still exiting 0.
pkill -9 -f soffice 2>/dev/null || true
sleep 1
soffice --headless --convert-to pdf --outdir "$TMP" "$PPTX" >/dev/null 2>&1
gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.6 -dPDFSETTINGS=/prepress \
   -dNOPAUSE -dBATCH -dQUIET -dDetectDuplicateImages=true \
   -sOutputFile="$OUT" "$TMP/$STEM.pdf"
rm -rf "$TMP"
echo "Acrobat-safe PDF → $OUT"
