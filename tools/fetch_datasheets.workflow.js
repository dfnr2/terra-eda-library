// Datasheet acquisition workflow (Claude runner).
//
// One haiku agent per unique datasheet in the chunk: find the official PDF
// (manufacturer > tier-1 distributor > other; avoid no-name mirrors), download
// with a UNIQUE temp file (mktemp — never a shared path), verify it is a real,
// plausible PDF, and store it content-addressed (sha256 = filename). Implausible
// or mirror-sourced files are QUARANTINED for human review, never silently dropped.
//
// Agents only write PDFs (race-safe via content addressing); they RETURN structured
// records. The caller ingests those into assets/datasheets/acquisition.jsonl.
//
// Invoke: Workflow({ scriptPath: "tools/fetch_datasheets.workflow.js",
//                     args: { chunkFile: "build/chunk.json", count: <N> } })
// The chunk file (an array of {filename,manufacturer,mpns,part_count}) is produced
// by tools/datasheets/remaining.py. Agents read their item from it by index.

export const meta = {
  name: 'fetch-datasheets',
  description: 'Fetch + verify + content-address a chunk of component datasheets (mktemp-safe, quarantine-not-reject)',
  phases: [{ title: 'Fetch', detail: 'one haiku per unique datasheet: find, download, verify, store or quarantine' }],
}

const CHUNK = (args && args.chunkFile) || 'build/chunk.json'
const COUNT = (args && args.count) || 0
if (!COUNT) { log('no count in args — nothing to do'); return [] }

const SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['filename', 'status', 'source_tier'],
  properties: {
    filename: { type: 'string' },
    status: { type: 'string', enum: ['ok', 'quarantine', 'notfound', 'error'] },
    source: { type: 'string' },
    source_tier: { type: 'string', enum: ['manufacturer', 'tier1', 'other', 'mirror', 'none'] },
    final_url: { type: 'string' },
    sha256: { type: 'string' },
    size_bytes: { type: 'integer' },
    pages: { type: 'integer' },
    mpn_in_doc: { type: 'boolean' },
    quarantine_reason: { type: 'string' },
    notes: { type: 'string' },
  },
}

function prompt(i) {
  return `You fetch ONE electronic-component datasheet PDF. Work in /users/dave/vsrc/terra-eda-library.

STEP 0 — read your work item (index ${i} of the chunk):
  python3 -c "import json; print(json.dumps(json.load(open('${CHUNK}'))[${i}]))"
Keys: filename (CERN datasheet filename hint), manufacturer, mpns (example part numbers sharing this sheet). Use these as your target.

GOAL: find the official datasheet PDF for this part (a documented family/series sheet is acceptable if the exact-MPN sheet does not exist), download it, verify it, store it content-addressed.

SOURCE PREFERENCE — try in order, stop at the first GOOD result:
  1. Manufacturer's own website (most reliable)
  2. Tier-1 distributors: Mouser, Digi-Key, Farnell/Newark, Octopart, RS, Arrow, TME
  3. Other reputable distributors
  AVOID no-name datasheet mirrors (alldatasheet clones, ic-components.ru, *.ru mirrors, unknown aggregators). If ONLY such a mirror has it, you may download it but you MUST set source_tier="mirror" and status="quarantine".
Use WebSearch (e.g. "<manufacturer> <first mpn> datasheet pdf") and WebFetch to locate the real PDF link.

DOWNLOAD with a UNIQUE temp file (NEVER a shared path — critical for parallel safety):
  TMP=$(mktemp /tmp/ds.XXXXXX.pdf)
  curl -L --fail -A "Mozilla/5.0" -o "$TMP" "<URL>"
If curl hits a network/sandbox error, retry with the Bash tool parameter dangerouslyDisableSandbox=true.

VALIDATE a real PDF (not an HTML error page):
  file "$TMP"        # must contain "PDF document"
  head -c 5 "$TMP"   # must be %PDF-
If not a real PDF, try the next source.

PLAUSIBILITY — decide status:
  SIZE=$(stat -c%s "$TMP")
  PAGES=$(pdfinfo "$TMP" 2>/dev/null | awk '/^Pages:/{print $2}')           # may be empty
  pdftotext "$TMP" - 2>/dev/null | grep -iF "<an mpn or its family/series>" # is the part named in the doc?
  - status="ok" ONLY if: real PDF AND size >= 25000 AND the MPN (or clear family/series) appears in the text AND source_tier is manufacturer/tier1/other.
  - status="quarantine" if ANY of: size < 25000; OR pages known and < 2; OR MPN/family NOT in the text; OR source_tier="mirror". Quarantine = KEEP FOR HUMAN REVIEW, do not discard.
  - status="notfound" if no real PDF can be located anywhere.

STORE content-addressed (sha256 IS the filename; identical content dedups automatically):
  H=$(sha256sum "$TMP" | cut -d' ' -f1)
  # status ok:
  mv "$TMP" "/users/dave/vsrc/terra-eda-library/assets/datasheets/files/$H.pdf"
  # status quarantine:
  mv "$TMP" "/users/dave/vsrc/terra-eda-library/assets/datasheets/quarantine/$H.pdf"
Both dirs are gitignored. Do NOT git add or commit. Touch no files other than the one PDF you store.

Return the structured result: filename (from your item), status, source (site name), source_tier, final_url, sha256 (or ""), size_bytes (or 0), pages (or 0), mpn_in_doc (true/false), quarantine_reason (or ""), notes (brief).`
}

phase('Fetch')
const idx = Array.from({ length: COUNT }, (_, i) => i)
const results = await pipeline(
  idx,
  (i) => agent(prompt(i), { label: `ds:${i}`, phase: 'Fetch', model: 'haiku', schema: SCHEMA })
    .then(r => r || { filename: `idx:${i}`, status: 'error', source_tier: 'none', notes: 'agent returned null' }),
)

const by = (s) => results.filter(r => r && r.status === s).length
log(`done: ok=${by('ok')} quarantine=${by('quarantine')} notfound=${by('notfound')} error=${by('error')}`)
return results
