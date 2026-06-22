#!/usr/bin/env bash
# Download datasheets for the essential op amp list
# Run from wherever you want the datasheets/ folder created
# Usage: bash get_datasheets.sh

set -euo pipefail

OUTDIR="./datasheets"
mkdir -p "$OUTDIR"

UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

dl() {
    local NAME="$1"
    local URL="$2"
    local OUT="$OUTDIR/${NAME}.pdf"

    if [[ -f "$OUT" && $(stat -c%s "$OUT") -gt 10000 ]]; then
        echo "  [skip] $NAME (already exists)"
        return
    fi

    printf "  %-20s " "$NAME"
    HTTP=$(curl -s -L -A "$UA" \
        -H "Accept: application/pdf,*/*" \
        -H "Referer: https://www.google.com/" \
        --connect-timeout 15 --max-time 60 \
        -o "$OUT" -w "%{http_code}" \
        "$URL")

    SIZE=$(stat -c%s "$OUT" 2>/dev/null || echo 0)

    if [[ "$HTTP" == "200" && "$SIZE" -gt 10000 ]]; then
        echo "OK  (${SIZE} bytes)"
    else
        echo "FAIL  (HTTP $HTTP, ${SIZE} bytes)"
        rm -f "$OUT"
    fi
}

echo ""
echo "=== TI Parts ==="
dl "OPA1612"   "https://www.ti.com/lit/ds/symlink/opa1612.pdf"
dl "OPA2387"   "https://www.ti.com/lit/ds/symlink/opa2387.pdf"
dl "OPA388"    "https://www.ti.com/lit/ds/symlink/opa388.pdf"
dl "OPA211"    "https://www.ti.com/lit/ds/symlink/opa211.pdf"
dl "OPA657"    "https://www.ti.com/lit/ds/symlink/opa657.pdf"
dl "OPA847"    "https://www.ti.com/lit/ds/symlink/opa847.pdf"
dl "OPA627"    "https://www.ti.com/lit/ds/symlink/opa627.pdf"
dl "OPA549"    "https://www.ti.com/lit/ds/symlink/opa549.pdf"
dl "OPA340"    "https://www.ti.com/lit/ds/symlink/opa340.pdf"
dl "TLV9062"   "https://www.ti.com/lit/ds/symlink/tlv9062.pdf"
dl "THS4551"   "https://www.ti.com/lit/ds/symlink/ths4551.pdf"
dl "THS3491"   "https://www.ti.com/lit/ds/symlink/ths3491.pdf"
dl "INA333"    "https://www.ti.com/lit/ds/symlink/ina333.pdf"
dl "INA828"    "https://www.ti.com/lit/ds/symlink/ina828.pdf"
dl "NE5532"    "https://www.ti.com/lit/ds/symlink/ne5532.pdf"
dl "TL072"     "https://www.ti.com/lit/ds/symlink/tl072.pdf"
dl "TL081"     "https://www.ti.com/lit/ds/symlink/tl081.pdf"
dl "TL082"     "https://www.ti.com/lit/ds/symlink/tl082.pdf"
dl "TL084"     "https://www.ti.com/lit/ds/symlink/tl084.pdf"
dl "LM358"     "https://www.ti.com/lit/ds/symlink/lm358.pdf"
dl "LM324"     "https://www.ti.com/lit/ds/symlink/lm324.pdf"
dl "LM741"     "https://www.ti.com/lit/ds/symlink/lm741.pdf"
dl "OP07"      "https://www.ti.com/lit/ds/symlink/op07.pdf"

echo ""
echo "=== ADI / Linear Technology Parts (via Chrome — analog.com is Akamai-protected) ==="
# analog.com rejects curl (Akamai bot manager resets the stream / returns 403).
# fetch_adi.py drives real Chrome through the DevTools Protocol to get the PDFs.
python3 "$(dirname "$0")/fetch_adi.py" "$OUTDIR" \
    || echo "  (ADI/LT fetch reported errors — see above)"

echo ""
echo "=== Summary ==="
TOTAL=$(ls "$OUTDIR"/*.pdf 2>/dev/null | wc -l)
echo "  $TOTAL PDFs in $OUTDIR/"
echo ""
ls -lh "$OUTDIR"/*.pdf 2>/dev/null | awk '{print "  " $5 "\t" $9}'
echo ""
echo "Done."
