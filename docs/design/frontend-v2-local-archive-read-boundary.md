# Frontend V2 — bounded local archive read boundary

Status: **OWNER-AUTHORIZED CANDIDATE IMPLEMENTATION; NOT YET INDEPENDENTLY ACCEPTED**. Observation #38 records the bounded local capture/read acceptance; the project owner additionally authorized Observation-owned SQLite access through a local HTTP read-only adapter in this workstream. Tracks #38, #66 and #67. Source-backed local capability: `ArchiveReader` in `src/observation/archive.py`.

## Authority
Observation owns archival reads; World owns causal commits; Lab owns scientific evidence admission; Frontend is passive. Owner authorization to develop does not waive independent BAW-004 review or competent acceptance.

## Existing operations
`ArchiveReader.query_page(filters, after_receipt_sequence, limit)` returns receipt-ordered records, `next_after_receipt_sequence`, `has_more`, status, unsupported filters and identity status. `capture_catalog`, `capture_coverage`, `integrity_check` are separate. `run_id` and `world_tick` are unsupported filters. Receipt order is not World causal time. A closed-verified capture only verifies its bounded local delivery interval.

## Proposed adapter (requires exact contract approval)
- Local loopback, GET-only capture catalog, coverage and bounded receipt pages. No SQL endpoint, writes or remote listener.
- Strict allowed filters, bounded page sizes and bytes, integer receipt-sequence pagination cursor; reject malformed input, symlinks, corrupt digests, unsupported schemas and unsupported filters without exposing internal paths.
- Return capture identity, receipt/source sequence, digest, owner provenance, source-declared time and coverage state. Do not fabricate World-run joins or complete cross-owner snapshots.
- Distinguish unavailable, no matching receipts, unsupported query, incomplete capture and corrupt archive. Keep current M1 read independent.
- Capture is opt-in; `make run` does not currently enable it.

## Required decisions and acceptance
Observation/Architecture/Security owners must approve exact URL paths, JSON schema, resource limits and operator capture procedure. Candidate adapter implementation is in this PR; competent review must verify its exact wire contract before merge. Require independent review and fresh World→archive→adapter→browser E2E with pagination, gap, corruption, unsupported-filter and unchanged archive-hash cases. No scientific evidence admission or global V2 acceptance is implied.
