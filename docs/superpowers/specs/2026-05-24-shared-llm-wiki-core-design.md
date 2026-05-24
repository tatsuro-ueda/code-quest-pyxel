# Shared LLM Wiki Core With Repo Adapters

## Goal

Create a shared `llm-wiki` core that can be used by both `code-quest-pyxel`
and `business-docs`, while keeping each repository free to define its own
local wiki direction.

The intended end state for this task is:

- shared `llm-wiki` skills live under `dotfiles/shared`
- shared helper scripts for `query`, `health-check`, `update-schema`, and
  single-source `tasknote ingest` also live under `dotfiles/shared`
- each repo keeps only a thin local adapter that defines path mappings and
  required tasknote section names
- `code-quest-pyxel` continues to work after switching to the shared core
- `business-docs` can run the same shared core on its existing `llm-wiki/`
- repo-specific batch ingest logic stays local and is not pulled into the
  shared core on the first rollout

## Motivation

The current `llm-wiki` flow already has a clean separation between higher-level
thinking and repo-specific layout in some places, but the actual skills and
helpers still embed many `code-quest-pyxel` assumptions.

Examples:

- `query`, `health-check`, and `update-schema` are conceptually reusable
- helper scripts still hardcode paths such as `llm-wiki/wiki/indexes/master-index.md`
- tasknote ingest assumes the current repo's tasknote structure
- the batch helper is tightly coupled to `steering/done/` and should not be
  treated as shared infrastructure yet

The user wants to run the same LLM Wiki style in another repository,
`business-docs`, on another VM. Because `dotfiles` is shared across VMs,
`dotfiles/shared` is the correct place for the reusable core.

## Scope

### In scope

- define the reusable `llm-wiki` core boundary
- move shared skills to a shared location under `dotfiles/shared`
- move reusable helper logic to a shared location under `dotfiles/shared`
- define a repo-local adapter contract with:
  - path mappings
  - required tasknote section names
- keep repo-local schema docs, but make them feed the shared core through the
  adapter layer
- migrate `code-quest-pyxel` to use the shared core
- add one `business-docs` adapter and verify that the shared core works there
- support these shared workflows on both repos:
  - `llm-wiki-query`
  - `llm-wiki-health-check`
  - `llm-wiki-update-schema`
  - single raw tasknote ingest

### Out of scope

- sharing batch ingest helpers on the first rollout
- normalizing all repo-specific note cultures into one format
- removing local schema docs from each repo
- introducing a fully generic engine driven only by one giant config file
- redesigning the content model of `business-docs` or `code-quest-pyxel`
- changing the meaning of existing `llm-wiki` pages beyond what migration needs

## Design Principles

### Principle 1: Share the core, not the local culture

The shared core owns reusable workflow logic:

- how query reads the wiki
- how health-check collects and classifies signals
- how update-schema promotes recurring rules
- how a single tasknote source is preprocessed into structured material

The local adapter owns only repo-specific surface details:

- where raw sources live
- where summaries live
- where `master-index`, `ingest-log`, and `health-check-log` live
- which tasknote sections are required

### Principle 2: Keep repo-specific batch flows local

`code-quest-pyxel` has batch helper behavior tied to `steering/done/`. That is
not a general LLM Wiki concern. The first shared rollout must not drag this
repo-specific workflow into the common core.

### Principle 3: Let repos differ in direction without forking the core

The shared core should not assume that every repo thinks about the world in the
same way. The adapter exists so that `code-quest-pyxel` and `business-docs`
can map different local conventions to the same reusable workflow engine.

## Target Architecture

### Shared Core In `dotfiles/shared`

The shared core has four parts:

1. shared skills
2. shared helper scripts
3. a shared adapter contract
4. bootstrap docs for adopting the shared core in another repo

The shared skills define the workflow and reasoning order. The helper scripts
handle deterministic preprocessing only. The adapter contract tells the shared
core where to look and which structural assumptions are safe to make. The
bootstrap docs explain how another repo should opt in.

### Repo-Local Adapter

Each repo keeps a small local adapter file or adapter block that exposes the
minimum machine-readable values needed by the shared core.

Required adapter fields for the first rollout:

- `raw_root`
- `knowledge_raw_root`
- `tasknote_raw_root`
- `summary_root`
- `knowledge_summary_root`
- `tasknote_summary_root`
- `master_index_path`
- `source_inbox_path`
- `ingest_log_path`
- `health_check_log_path`
- `area_root`
- `query_root`
- `candidate_root`
- `tasknote_required_sections`

For the first rollout, `tasknote_required_sections` is the only content-shape
setting allowed in the adapter. The adapter must not become a dumping ground
for free-form behavioral overrides.

### Schema vs Adapter

The local schema doc remains the human-facing operations guide for the repo.
The adapter is the small machine-readable layer that shared scripts and skills
read first.

This separation is important:

- schema explains the repo's LLM Wiki policy and workflow
- adapter provides concrete path and section values

Without this split, either the schema becomes too rigid for humans, or the core
has to parse too much prose to act reliably.

## Workflow Ownership

### Shared

These workflows move to the shared core:

- `llm-wiki-query`
- `llm-wiki-health-check`
- `llm-wiki-update-schema`
- tasknote material extraction for single-source ingest

### Local

These workflows remain local on the first rollout:

- `steering oldest 10 batch mode`
- any helper that assumes one specific project-note directory name
- any helper that ranks related pages using one repo's ingest history format
- any logic that assumes one repo's note lifecycle such as `steering/done`

## Candidate File Sets

### Shared core candidates under `dotfiles/shared`

Expected new or moved assets:

- shared skill docs for:
  - `llm-wiki`
  - `llm-wiki-query`
  - `llm-wiki-health-check`
  - `llm-wiki-update-schema`
  - `llm-wiki-capture-and-ingest-source`
- shared Python helpers for:
  - health-check material preparation
  - tasknote material preparation
  - adapter loading
- shared adoption docs explaining how another repo enables the core

### `code-quest-pyxel` local adapter candidates

Expected repo-local assets:

- local adapter config that maps current `llm-wiki/` paths
- current repo schema updated to explain the adapter relationship
- existing repo-local batch helpers left in place for now

### `business-docs` local adapter candidates

Expected repo-local assets:

- local adapter config that maps the existing `business-docs` `llm-wiki/`
- local schema alignment if its current wording does not expose the required
  path and section assumptions clearly enough

## Rollout Plan

### Phase 1: Extract the shared boundary from `code-quest-pyxel`

Identify which parts of the current `llm-wiki` implementation are:

- pure shared workflow logic
- deterministic preprocessing logic
- repo-specific path assumptions
- repo-specific tasknote culture

Move only the first two categories into the shared core boundary.

### Phase 2: Make `code-quest-pyxel` consume the shared core

Add a local adapter for `code-quest-pyxel` and switch the repo to use the
shared skills and helpers. Verify that the following still work:

- query on the current wiki
- health-check on the current wiki
- update-schema on the current wiki
- single raw tasknote ingest

### Phase 3: Add a `business-docs` adapter

Create a local adapter for `business-docs` and run the same shared workflows on
its existing `llm-wiki/`.

The first cross-repo success criterion is not perfect feature parity. It is
that the same shared core can operate correctly on both repos without adding
repo-name-specific branches to the core logic.

## Success Criteria

Success means all of the following are true:

- shared skills and shared helpers live in `dotfiles/shared`
- `code-quest-pyxel` uses the shared core through a local adapter
- `business-docs` uses the shared core through a local adapter
- both repos can run:
  - `query`
  - `health-check`
  - `update-schema`
  - single tasknote ingest
- the shared core does not contain `if repo == ...` style behavior forks
- batch ingest remains local and does not block the first rollout

## Failure Signals

The first rollout should be treated as mis-scoped if any of the following
happen:

- the adapter needs to express complex behavioral overrides rather than path
  and section values
- the shared core starts accumulating repo-specific conditionals
- `business-docs` cannot use the shared core without adopting
  `code-quest-pyxel`'s note culture
- the batch helper becomes a dependency for otherwise simple shared workflows

If these signals appear, the fallback is to shrink the shared scope to:

- `query`
- `health-check`
- `update-schema`

and leave all tasknote ingest local until a second round.

## Verification

Verification for this design should cover two repositories.

For `code-quest-pyxel`:

- verify the shared core can resolve the local adapter
- verify query still reads `master-index`, summaries, and areas in the expected
  order
- verify health-check still produces deterministic graph signals
- verify update-schema still reads recurring patterns from the health-check log
- verify single tasknote ingest still extracts the configured required sections

For `business-docs`:

- verify the adapter resolves the existing `llm-wiki/` paths
- verify query can answer one representative question
- verify health-check can produce one log scaffold and issue classification pass
- verify update-schema can perform one no-op or one real promotion using the
  local health-check log
- verify single tasknote ingest can parse one local tasknote using the adapter's
  required section list

## Risks

### Risk 1: Shared core drifts back toward `code-quest-pyxel`

Mitigation:

- keep the adapter contract intentionally small
- reject repo-specific logic in shared helpers
- test the same workflows in `business-docs` before expanding scope

### Risk 2: Tasknote ingest is not actually generic enough

Mitigation:

- support only path and required-section differences on the first rollout
- keep batch logic local
- fall back to local-only ingest if tasknote shape differences prove too large

### Risk 3: Human-facing schema and machine-facing adapter diverge

Mitigation:

- document the adapter-to-schema relationship explicitly in each repo
- make verification check both the adapter values and the repo-local schema

### Risk 4: Cross-VM sharing hides debugging context

Mitigation:

- keep shared code in `dotfiles/shared`, but keep repo-specific verification in
  each repo
- require one successful run in both repos before calling the rollout complete
