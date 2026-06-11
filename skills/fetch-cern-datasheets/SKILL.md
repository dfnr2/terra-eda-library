---
name: fetch-cern-datasheets
description: >-
  Resumable, multi-session procedure for acquiring a datasheet PDF for every part in
  the terra library. Use whenever continuing/​running the datasheet fetch: "fetch
  datasheets", "continue the datasheet run", "grab more datasheets", "run the next
  datasheet chunk", or any work under assets/datasheets/. The fetch unit is the unique
  datasheet (many parts share one), agents find+download+verify+content-address each,
  and progress is a committed log so any session resumes where the last stopped.
---

# Fetching CERN/terra datasheets (resumable)

Acquire one PDF per **unique datasheet** (not per part — many parts share a sheet),
store it content-addressed, and record the outcome in a committed log so the run
survives across sessions and machines. Feeds the datasheet/param resolver
(`./2026-06-10-datasheet-param-resolver-design.md`): once the collection is complete it
is mirrored to GitHub Releases and the DB `datasheet` field is repointed there.

**Everything is resumable.** Progress is one committed file. A run is always:
`compute remaining → do a bounded chunk → ingest → commit → audit → repeat`.

## State (the source of truth)

- `assets/datasheets/acquisition.jsonl` — **committed**, append-only. One record per
  completed work item, keyed by `filename`: `{filename, status, source, source_tier,
  final_url, sha256, size_bytes, pages, mpn_in_doc, quarantine_reason, notes}`.
  `status ∈ {ok, quarantine, notfound, error}`. **Done = ok|quarantine|notfound**;
  `error` rows are retried. This file IS the progress — back it up by committing it.
- `assets/datasheets/files/` — **gitignored**, content-addressed (`<sha256>.pdf`) store
  of accepted datasheets. Race-safe: identical content collapses to one file.
- `assets/datasheets/quarantine/` — **gitignored**, content-addressed store of files
  held for human review (too small, MPN not found in text, or no-name mirror source).
- `build/worklist.json`, `build/chunk.json` — gitignored, regenerable scratch.

If the gitignored PDF stores are ever lost, they rebuild from the log's `source_url`s.

## The loop (run each chunk)

1. **Build/refresh the work-list** (only needed when the DB changed):
   `uv run python tools/datasheets/build_worklist.py`
   → `build/worklist.json` (unique datasheets from all `cern_*` tables).
2. **Compute the next chunk** (work-list minus the log):
   `uv run python tools/datasheets/remaining.py <chunk_size>`
   → writes `build/chunk.json`, prints `remaining=`. Keep chunk_size so that
   `2 × size` stays well under the 1000-agents/workflow cap; **300 is a safe default**.
   Start smaller (~40) the first time on a new machine to gauge Haiku token cost.
3. **Run the chunk** with one of the runners below (Claude workflow OR third-party).
4. **Ingest results → log → commit:**
   - Save the runner's returned records to `build/results.json`.
   - `uv run python tools/datasheets/ingest.py build/results.json` (dedups by filename).
   - `git add assets/datasheets/acquisition.jsonl && git commit -m "datasheets: fetch chunk (N ok, M quarantine, …)"`.
5. **Audit:** `uv run python tools/datasheets/audit.py` (on-disk hashes vs log; exits
   non-zero on corruption/orphans/missing).
6. **Repeat** until `remaining=0`. Then review quarantine and mirror to Releases.

## Runner A — Claude workflow (default)

`Workflow({ scriptPath: "tools/fetch_datasheets.workflow.js",
            args: { chunkFile: "build/chunk.json", count: <chunk length> } })`

Agents read their item from `build/chunk.json` by index, fetch, and RETURN records (they
never write the log — no concurrent-append races). Save the workflow's return value to
`build/results.json`, then ingest (step 4). Resume a killed run with the same
`scriptPath` + `resumeFromRunId`.

## Runner B — third-party / cheaper agent (provider-agnostic contract)

Any agent runner can process a chunk if it honors this exact contract per work item. This
is what keeps the run portable when Haiku usage adds up:

**Input:** one work item `{filename, manufacturer, mpns[]}` from `build/chunk.json`.
**Procedure (identical to the workflow agent):**
1. Search sources in order — **manufacturer site → tier-1 distributor (Mouser, Digi-Key,
   Farnell, Octopart, RS, Arrow, TME) → other reputable**. **Avoid no-name mirrors**
   (alldatasheet clones, `ic-components.ru`, `*.ru`, unknown aggregators); if only a
   mirror has it, download but mark `source_tier="mirror"` + `status="quarantine"`.
2. Download to a **unique** temp path (`mktemp` — never a shared filename; this is the
   one rule that, if broken, silently corrupts parallel runs).
3. Verify a real PDF (`file` says "PDF document"; starts with `%PDF-`).
4. Plausibility → status: **ok** only if real PDF AND `size ≥ 25000` AND the MPN/family
   appears in `pdftotext` AND source is not a mirror; else **quarantine** (small / not
   found / pages<2 / mirror); **notfound** if nothing real exists. Quarantine is **kept
   for review, never discarded.**
5. Store content-addressed: ok → `assets/datasheets/files/<sha256>.pdf`;
   quarantine → `assets/datasheets/quarantine/<sha256>.pdf`.
6. Emit a JSON record with the log fields above.
**Output:** the array of records → `build/results.json` → `ingest.py` (step 4).

Because storage is content-addressed and the log dedups by filename, a third-party runner
and the Claude workflow can even split the same chunk without conflict.

## Quarantine review (before mirroring)

Quarantined files are real candidates, not rejects. Periodically: list quarantine records
(`status=quarantine` in the log), eyeball each PDF, and either promote (move file to
`files/`, set `status=ok` in the log) or mark `notfound`/leave. Common causes: a correct
family sheet flagged because the exact MPN string wasn't matched; a small-but-valid sheet
for a simple part; a mirror-only source you accept.

## Gotchas (hard-won)

- **`mktemp`, always.** The pilot run lost a datasheet because every agent wrote
  `/tmp/ds_dl.pdf`; concurrent agents clobbered it and two reported the same hash. Unique
  temp paths are mandatory.
- **Don't trust agent self-reports.** Verify against disk: `audit.py` re-hashes every
  referenced file. An agent claiming success with a hash whose file is absent/mismatched
  is the signal of a temp-path or download bug.
- **Agents never write the log or commit.** They write one content-addressed PDF and
  return data; the coordinator ingests + commits. Keeps the committed log race-free.
- **Chunk size vs the 1000-agent workflow cap.** One agent per item → keep chunks ≤ ~400.
- **`error` rows retry automatically** (not "done"); a `notfound` is terminal until you
  re-queue it by editing the log.
- Native (non-CERN) tables already hold real datasheet URLs — they are out of this
  work-list and handled directly at mirror time.
