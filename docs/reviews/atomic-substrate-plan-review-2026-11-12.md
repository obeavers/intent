# Review: the two Atomic plans, and proposed changes to the substrate plan (2026-11-12)

## What was reviewed

- **Substrate plan** (the base for the changes below): the plan that adopts Atomic as Intent's
  change and work-evidence substrate. It links Atomic's Rust crates at v0.22.0, makes Intent the
  only recorder, and builds a task → change → confirm loop on Atomic's intents, triage, query,
  provenance and memory.
- **CLI plan**: `docs/plans/atomic-vcs-replacement-2026-11-12.md`, with its critique in
  `docs/reviews/atomic-vcs-replacement-plan-critique-2026-11-12.md`. It drives a bundled
  `atomic` 0.19.1 binary, lets Atomic's agent hooks record turns, and replaces Git per
  workspace with a route to retiring Git.
- **Evidence:** Atomic source at `61d8040` (confirmed as tag `v0.22.0`), intentd `c755f03`
  (v0.11.197), cloudlands-fe `db83827`, protocol 18.0. Sources were read and the two lockfiles
  compared. Nothing was built or run, so every build claim below still needs the spike in C1.

## Verdict

Keep the substrate plan as the base. It is the only one of the two that uses what is new in
Atomic (intents, triage, the knowledge graph, provenance, memory), and its identity, idempotency
and recovery rules are sound. The CLI plan treats Atomic as a Git replacement and forbids agents
from touching the knowledge features.

The substrate plan needs six structural changes before it can be implemented, and it lacks the
execution scaffolding the CLI plan has:

1. Linking Atomic's crates into intentd will very likely not build as specified (C1).
2. Its activation gate depends on Intent infrastructure that does not exist (C3).
3. It does not say where the user and the primary agent work, or how child agents get a warm
   build (C4).
4. The explanation of accepted work is lost at the first forge merge (C6).
5. No user-visible value arrives until the whole stack is qualified (C7, C8).
6. It silently reverses or leaves open three decisions recorded in the CLI plan (section 4).

## 1. How the plans compare

| Dimension | CLI plan | Substrate plan | Take |
|---|---|---|---|
| What Atomic is for | A VCS under each workspace | Change graph plus the record of intent, evidence and decisions | Substrate |
| Integration | Bundled CLI, JSON parsing | Crates linked into intentd | Neither: an owned host process (C1) |
| Who records | Atomic hooks in provider processes, Intent fills gaps | Intent only, two-phase with exact bytes | Substrate, with provenance fed from ACP events (C9) |
| Working directories | One shared sandbox per workspace | A private directory per writer, frozen baselines | Substrate, plus a single-writer fast path (C4) |
| Publication | `atomic git push` through the proposed Git bridge | Intent-owned projection repository, verified tree, fixed parent | Substrate |
| Legacy `git.*` on Atomic roots | Git-shaped projection | Typed refusal | Substrate, with a compatibility test (C19) |
| Product surfaces | Turn timeline, rewind, insert, provenance gutter, conflict UI, session fork | Confirmation card described in prose only | Import the CLI plan's (C12, C13, C19) |
| Rollout and operations | Labs flag, eligibility, telemetry, packaging, maturity and retirement gates | Almost none | Import (C17) |
| Grounding | Real paths and line numbers | Many owners left as "locate" | Import, and fill the rest (C16) |
| Executability | Decisions, assumptions, work items, verification matrix | Twelve prose steps | Import the structure (C22) |

## 2. Facts to correct in the substrate plan

### 2.1 Atomic at the pin

| Plan says | Source shows | Consequence |
|---|---|---|
| Use `LocalService` where its semantics match | It dispatches 23 of 105 declared RPCs (`libatomic/src/local.rs:91-358`). Triage, sandbox, diff, the turn journal, unrecord, conflicts, preview, vault entity create/update/validate, project identity and Git interop are not dispatched. | `LocalService` is not a usable route for this plan (C2) |
| "Semantic merge" as a qualification corpus | Token-level three-way merge with a generic lexer, no AST (`atomic-core/src/merge/three_way.rs:79-88`). The property test is a seeded generator of line edits. | Rename it, and build our own corpus (C12) |
| `RecordRequest.request_id` must not be trusted | The field is `RequestMeta.request_id`. Replay detection is declared but handlers hard-code `replayed: false`. | Correct the name; the conclusion holds |
| `Repository::insert_change` in `changes.rs` | It is in `repository/insert.rs:2413` | Citation fix |
| Insert preview "can" return empty conflicts | It always returns `conflicts: []` and no snapshot (`libatomic/src/daemon/services.rs:627-677`) | Private composition is the only conflict check |
| `dependency-only` classification | The fields are `captured_changes`, `declared_changes`, `recording_changes`, `dependency_changes` (`intent_graph.rs:33-44`) | Use the field names |
| Prospective turn binding is available | It exists (`atomic-agent/src/turn/session.rs:776-856`) but its only caller is the CLI `intent update` | Needs a facade (C2) |
| Ingress needs a durability patch | Confirmed: plain `std::fs::write` (`repository/changes.rs:331`). The only durable path is for projected-span changes and is Unix-only. | Carry a patch; needs a fork policy (C2) |
| Pin v0.22.0 | v0.22.1 already exists (a fix for history recorded before 0.20) | Add a pin-bump procedure |
| Triage independence | A string inequality on `attributedTo` plus `status == "done"`, no signature check (`triage/report.rs:329-346`). The triage reference hashes pins only. | The plan's extra checks are required, and Intent can do better (C11) |
| Not stated | `rust-version` 1.90, toolchain pinned to 1.98.0, release profile `panic = "abort"`, not on crates.io, 544 packages in the lockfile, Git import Unix-only | See C1 |
| Not stated | redb permits one open handle; two sandbox roots get two serialization gates over one database file (`libatomic/src/daemon/state.rs:71-75`) | One owning process; agents cannot run the `atomic` CLI against the store (C9, C10) |
| OCI stage/seal as out of scope | Implemented with tests (`atomic-repository/src/oci.rs`) | Candidate transport for cloud machines (C14) |

### 2.2 Intent at the current pins

| Plan assumes | Repository shows | Consequence |
|---|---|---|
| Atomic runs at the existing node boundary, behind a qualified writer barrier | The head/node split, node link and checkpoint format are "prepared… not implemented" (`docs/ARCHITECTURE.md:122-147`). No writer-barrier type exists. | C3 |
| Isolated local placement is a seam to reuse | Local agents share one worktree. Per-agent sandboxes were dropped (migration `0187`), local placement rejects a `checkout` (`intent-core/src/placement.rs:235-249`), and delegate `isolation` maps to plain local placement (`agent_ops.rs:13870-13878`). | C3 |
| An immutable task revision can be captured | A task is a note with `TaskMetadata`. `rev` is a counter, `note_version` keeps the newest 50 snapshots with no digest, and `acceptance_criteria` is `Vec<String>` (`intent-core/src/model.rs:1900-1945`). | C8 |
| An authorized confirmation action exists | None. `review_required` is set by `agent.reportToParent` (`agent_ops.rs:13031`) and `complete` by the generic `task.updateNoteStatus`. | C8 |
| Existing memory, outbox and blob-storage owners | No memory service, no transactional outbox, no blob store, no cost store (token usage only) | All four are new work (C8, C14) |
| A separate data profile is needed to keep old binaries out | `intent-store` already refuses a database whose migration ledger is newer than the build (`intent-store/src/lib.rs:461-485`) | C18 |

## 3. Proposed changes

Each change names the part of the substrate plan it rewrites.

### A. Architecture

**C1. Host Atomic in an owned sidecar process instead of linking it into intentd.**
Rewrites: Summary, "Native owner and cancellation", the file table, step 1.

- **Why linking is unlikely to work.**
  - `atomic-agent` (which holds turn binding and the provenance classifier) depends on
    `rusqlite` 0.32, so `libsqlite3-sys` 0.30.1. intentd resolves `libsqlite3-sys` 0.37.0
    through sqlx. Both bind the native `sqlite3` library, and Cargo allows one such package per
    graph. Expect a resolution failure. `libatomic` depends on `atomic-agent`, so it is
    affected too. `atomic-repository` on its own is not, but linking only that crate gives up
    turn binding, the classifier and every `libatomic` handler.
  - Atomic enables `vendored-openssl`, `https` and `ssh` on `git2` 0.21. Feature unification
    would switch those on for intentd's own `git2`.
  - Atomic is built and tested with `panic = "abort"`, and its own embedding investigation
    names that as a blocker. intentd unwinds.
  - Atomic pins toolchain 1.98.0; intentd pins 1.96.0.
  - Git import and the durable write path are Unix-only; intentd ships four Windows targets.
  - There is an unconditional debug `eprintln!` with a forced backtrace on an error path
    (`repository/projection.rs:26-29`).
- **Change.** Split `intent-atomic` in two:
  - a client crate inside the intentd workspace that depends only on `intent-core` types;
  - an `intent-atomic-host` binary in its own Cargo workspace, lockfile and toolchain, linking
    Atomic at the pinned Git revision.

  One host process per node owns every canonical store. The contract between them is the
  plan's `WorkspaceEngine` plus the evidence facade; large payloads pass by spool path. intentd
  supervises the host, and a host crash enters the reconciliation path the plan already
  specifies. Bundle it through `electron-builder.yml` `extraResources` beside `intentd/`, with
  the existing macOS signing hook. Do not ship it on Windows; the capability is then absent.
- **What is kept.** No CLI output parsing, exact change bytes, one owner per store.
- **Cost.** A contract to version, payload streaming, and one more signed binary.
- **First gate.** A half-day build spike. If in-process linking is still preferred, the spike
  must show a clean dependency resolution on all seven release targets.

**C2. Drop `LocalService` as a route and list the upstream facades.**
Rewrites: "Atomic facts", "Native owner", "Durable projection".

- The host calls `atomic-repository`, `atomic-canonical` and `atomic-agent` directly. The rule
  of one route per operation stays.
- Upstream changes needed, each with a file reference from section 2.1: durable ingress,
  create-or-resolve an intent with a caller-supplied UID (`repository/vault_intent.rs:141`
  allocates a new ULID per call), a turn-binding API, an insert preview that analyses
  conflicts, and working replay detection.
- Add a fork policy: open the upstream PR first, pin to our fork revision until it merges, and
  re-run the qualification fixtures on every pin bump.

**C3. Make Atomic the local isolation mechanism instead of waiting for the node boundary.**
Rewrites: "Ownership and data flow", "Immutable baseline", steps 6 and 7.

- Implement isolated checkout for local placement as an Atomic private working directory.
- Define a local capture barrier in the Atomic path: stop turn admission at
  `agent_manager.rs` `try_begin_turn`, drain the provider turn, stop scripts and terminals whose
  working directory is inside, then capture. Write it so the node design can adopt it later.
- Make format-2 checkpoints local-first, with no hub upload in the pilot.

**C4. Define the primary working directory, and clone children warm.**
Rewrites: "Immutable baseline and private agent work", "Composition".

- **Problem.** The plan gives every writer a directory materialized from a manifest and
  requires a clean, idle target for adoption. It never says where the user and the primary
  agent work, or where setup scripts, dev servers and terminals run. A directory built from a
  manifest has no `node_modules` or `target`, so every child re-runs setup, and the user no
  longer sees edits as they happen.
- **Change.**
  - The workspace root is the working copy of the workspace view. The user and the primary
    agent work there. With one writer, turn settlement records straight into the workspace
    view under the barrier, with no compose or adopt step.
  - A child gets a copy-on-write clone of the parent directory, ignored build output included.
    Its tracked content is then verified against the frozen baseline manifest.
  - Adoption from child to workspace stays as specified.
  - The benchmark compares warm and cold child start.

**C5. Decide: one canonical store per repository per node, shared by its workspaces.**
Rewrites: "Native owner", "Identity".

- Memories, intents and the knowledge graph only help later work if they span workspaces.
- With one host process, the CLI plan's cross-process writer concern no longer applies.
- Atomic has no frozen view. A frozen baseline is a root view that Intent never mutates; the
  nearest native aids are tags and `(view, sequence, state)` pins
  (`atomic-core/src/pristine/traits/tag.rs:24-34`).

**C6. Keep the explanation of accepted work across the forge round-trip.**
Rewrites: "Git projection and incoming Git changes", "Make the query engine an agent
capability".

- **Problem.** Every new workspace starts from an imported cutover baseline. After a squash or
  rebase merge, the next baseline is opaque Git content, so `work.explainChange` stops at the
  baseline. The intent and evidence behind merged code become unreachable from that code after
  the first merge.
- **Change.**
  - Store `projection ↔ pull request ↔ merge commit` in `vcs_projection`; the PR monitor
    already observes merges.
  - Implement `work.explainChange(path, line)` as: Git blame in the retained source → merge
    commit → projection → candidate → confirmation receipt → task revision.
  - Evaluate Atomic's binding packs (`repository/binding_fetch.rs`, `binding_store.rs`) as the
    native carrier.
  - This index is independent of the engine, so it also serves Git workspaces.

### B. Getting more out of Atomic

**C7. Ship the knowledge layer first, read-only, on existing Git workspaces.**
Rewrites: Summary, "Durable projection and first-pilot acceptance", implementation order.

- Build a derived store outside the worktree by importing the workspace's Git history. It is
  rebuildable and has no authority over source, so none of the recovery gates apply to it.
- Expose code search, the entity index (tree-sitter grammars for TypeScript, Python, Rust, Go,
  Java, C, C++ and Swift; Svelte is absent), change impact, `work.findRelated` and
  `work.context`.
- Implement it as a second `ContextEngine` beside the auggie one in `intent-context`.
- It works on every workspace, including this monorepo, and supplies the Git-workflow baseline
  metrics the plan's comparison needs.
- Keep embeddings off by default: Atomic sends them over HTTP to Voyage, OpenAI or Anthropic.
  Test that the default configuration makes no network calls.

**C8. Make the evidence loop engine-neutral and land it on Git first.**
Rewrites: "Ownership and the task-to-intent bridge", "Persistence".

- `TaskRevisionRef`, `CandidateEvidence` and `ConfirmationReceipt` bind to a `NativeStateRef`,
  which can be a Git commit and tree.
- Add `task.confirm`. Today nothing stops `task.updateNoteStatus` from marking a bound task
  complete, so a receipt could be bypassed; route completion of bound tasks through the
  confirmation compare-and-swap.
- Add a content digest and a pin flag to `note_version` (or a `task_revision` table) so a
  governing revision survives the 50-snapshot pruning.
- Map each `acceptance_criteria` string to one `:::acceptance-criterion` with origin
  "explicit task content".
- Add the content-addressed blob store and the transactional outbox as named new work.

**C9. Get tool-level provenance from ACP events, using Atomic's own classifier.**
Rewrites: "Reuse native primitives" table row on the turn journal, "Native owner".

- The CLI plan chose hooks to get the exploration / commitment / verification graph. Hooks
  cannot coexist with a store held by one process.
- Atomic's classifier is library code (`atomic-agent/src/provenance/classify.rs:15-19`), and
  the journal handlers have bodies. Feed Intent's ACP tool-call events through them from the
  host. This covers every ACP provider with no per-provider hook injection and no gap-filler.
- Add a parity gate: for Claude Code and Codex, the ACP-fed graph is at least as rich as a
  hook-recorded session.
- Neutralise the user's own Atomic install in provider processes. This machine has `atomic`
  0.19.1 and global agent hooks; a hook firing in an Intent working directory would try to open
  a 0.22 store. Use a daemon-scoped Atomic configuration and identity directory, working
  directories that expose no discoverable repository pointer where the API allows it, and keys
  held in the OS keychain through the existing keychain helper.

**C10. Let agents take part, through sandbox grants.**
Rewrites: "Make the query engine an agent capability", "Context, learning".

- Atomic's sandbox grants scope one view of one repository to a capability subset with an
  expiry, and the host supplies the authority (`libatomic/src/daemon/sandbox_grants.rs`). Issue
  one per assignment.
- Add `ws.work.*` bindings in `intent-acp/src/mcp_server/bindings/`: the read queries, plus
  proposal writes (`proposeCriterion`, `proposeMemory`, `submitReview`) that go to the Intent
  owner for admission.
- These bindings are the agents' only route, because the store is exclusively held. Add the
  Atomic variant of the agent instructions (C20).

**C11. Run independent review as a delegated agent on a different model.**
Rewrites: "Reuse native triage", lifecycle table, step 8.

- Atomic's workflow expects a reviewer under a different identity, ideally a different model.
  Intent already orchestrates several providers, so it can supply real independence.
- Spawn the reviewer through `agent_delegate_op` with a read-only grant on the candidate
  materialization. Its output is a signed review intent, and Intent verifies the signer against
  the reviewer principal.
- The triage report's `layers` are empty at the pin. Derive reading order from the entity index
  until upstream fills them.

**C12. Use conflicts as data for a conflict panel and a resolver agent.**
Rewrites: "Better delegation and integration", qualification corpus.

- `ConflictSetObject` is content-addressed and tested (`repository/conflict_object.rs`). Intent
  has no conflict-resolution UI today. Add `vcs.conflicts.list` and `vcs.conflicts.resolve`,
  with per-side task and agent attribution.
- Build a corpus of real concurrent edits in Rust, TypeScript, Svelte and Swift. Upstream's
  tests do not cover real code.

**C13. Name per-turn records, rewind and fork as product increments.**
Rewrites: lifecycle table, later increments.

- Record every settled turn, including cancelled and failed ones. `auto_commit.rs:83` skips
  those today.
- Rewind is a new view without the later changes. Fork-at-turn creates a sibling workspace
  (`proposeSibling` with carried changes). Native undo only works at the sole current head
  (`repository/operation.rs:785-800`), so do not build rewind on it.

**C14. Tie the later increments to concrete primitives.**
Rewrites: "Context, learning, usage and portable evidence", step 11.

- **Evidence on the forge.** Generate a pull-request block from the confirmation receipt
  (criteria coverage, agents and models, checks run, reviewer) and attach the DSSE export
  (`atomic-canonical/src/provenance_export.rs`).
- **Publication check.** Run Atomic's provenance gate (`repository/provenance_gate.rs`) before
  projection.
- **Delegation.** Mirror Intent's delegation tree with delegation certificates
  (`atomic-canonical/src/delegation.rs`), and map delegation groups to goals.
- **Cloud machines.** Evaluate OCI stage/seal for shipping baselines to E2B and Northflank,
  the only placement where isolated checkouts are live today.
- **Projection checks.** Express "required derived facts exist" as SHACL shapes
  (`atomic-shacl`).
- **Memory.** Atomic's memory kinds (decision, lesson, constraint, preference, context) become
  Intent's first memory system. Define the owner (`memory_ops.rs`, `memory.*` methods) and
  inject selected memories in `rules.rs` prompt assembly.

### C. Carry over from the CLI plan

**C15. A seam phase with enforcement.** Golden byte-identical wire tests for `git.*`,
`accept-changes.*` and `file-tracking.*`; a seam lint with a shrinking baseline (540
`intent_git::` lines in 78 files and 393 `git2::` lines in 56 files sit outside `intent-git`);
`git2` moved into `intent-git`; a typed skip outcome replacing the substring matching at
`auto_commit.rs:374-377`; the attribution helpers behind the engine, since
`file_tracking.rs:112`, `tracked_changes_sweep.rs:112` and `agent_locks.rs:208` all open a Git
repository.

**C16. Replace every "locate" row** with the owners in the appendix.

**C17. Rollout and operations.** Labs flag (`shared/app-settings-schema.ts:234-300` plus a
daemon setting); dynamic capability through `with_runtime_capabilities`
(`intent-transport/src/client.rs:149-170`); the telemetry field list; a closed set of
eligibility reasons behind `vcs.eligibility`; ignore parity and secret safety (carry over
`info/exclude` and the global excludes, and test that `.env` and `node_modules/` are never
recorded or projected); binary and LFS policy; the assistant-app-guide rule; and the AGENTS.md
workflow (docs lead the pin, intentd before the frontend, no manual signed builds for
migrations).

**C18. Simplify the compatibility guard.** Replace the separate native-only data profile and
launcher check with a test that an older binary refuses before inspecting roots. Keep the
separate profile only if that test fails.

**C19. Wire and frontend detail.** Method and event tables for `vcs.*`, `work.*`,
`task.confirm` and `memory.*`; the CLI plan's frontend file list; new surfaces for the
confirmation card and criteria (none exist; the nearest is `TaskProgressControl.svelte`), the
conflict panel and the activity timeline. Keep the refusal of legacy `git.*` on Atomic roots,
and add a test that an old frontend on a new daemon cannot create an Atomic workspace and
shows "needs a newer client".

**C20. Agents without Git.** The Atomic variant of the agent instructions, the `INTENT_VCS`
and `INTENT_BASE_*` environment variables, `agent.git_command_failed` telemetry, and an
eligibility warning for build scripts that call `git`.

**C21. State a position on each recorded user decision** (section 4).

### D. Make it executable at scale

**C22.** Add a decisions table, an assumption register (claim, status, validation, fallback), a
work-item index (goal, done when, key files, dependencies, size, lane) and a verification
matrix. Convert the caveats written as prose into numbered requirements and a non-goals list.

**C23.** Give every phase an exit gate with thresholds, for example turn settlement overhead
under 1 s at p50 and 5 s at p95.

**C24.** Define five lanes that can run in parallel: seam; evidence loop on Git; read-only
knowledge layer; host and repository mechanics; frontend.

**C25.** Replace the `chatgpt.com/library` source links with repository paths at the pins
above. Implementers cannot open them.

## 4. Decisions to confirm

| Decision | Substrate plan | Recommendation |
|---|---|---|
| Integration topology | Link crates into intentd | Owned host process (C1) |
| Who records (CLI plan D6: hooks primary) | Reverses it without saying so | Confirm the reversal: Intent is the only recorder, provenance comes from ACP events (C9) |
| Record every turn (CLI plan D7) | Ambiguous ("workspace policy applies before recording") | Adopt D7 on Atomic roots (C13) |
| Retire the Git backend (CLI plan D11) | Left open | Keep it as the end state with the CLI plan's retirement gate, off the pilot's critical path; a Git engine stays for secondary roots and submodules |
| No Git in agent working directories (CLI plan D13) | Consistent | Adopt with C20 |
| Store scope | Unstated | One per repository per node (C5) |
| Order of delivery | Everything qualified before the first pilot | Knowledge layer and the evidence loop on Git first (C7, C8) |

## 5. Revised implementation order

1. **Spikes and pins.** Host build spike (C1), upstream facade list and fork policy (C2),
   capability ledger, owner manifest (appendix).
2. **Seam, no behaviour change.** Neutral types, `GitWorkspaceEngine`, golden wire tests, seam
   lint (C15). In parallel: blob store, outbox, task revision pinning.
3. **Evidence loop on Git.** `task.confirm`, candidate evidence, confirmation receipts, the
   projection ↔ merge index (C6, C8). Start recording baseline metrics.
4. **Read-only knowledge layer.** Host process, derived stores, `work.*` reads, the Atomic
   `ContextEngine`, memory owner (C7, C14).
5. **Repository mechanics in disposable stores.** Exact bytes, durable ingress, frozen
   baselines, closure export and restore, ACP-fed provenance with the parity gate (C9).
6. **Local isolation.** Capture barrier, workspace working copy, warm child clones, format-2
   checkpoints (C3, C4).
7. **Authoritative Atomic workspaces behind the Labs flag.** Eligibility, ignore parity, agent
   instructions, per-turn records (C13, C17, C20).
8. **Full loop.** Composition, native triage, the reviewer agent, signing, adoption, the
   conflict panel (C11, C12).
9. **Projection and forge publication,** with the pull-request evidence block (C14).
10. **Pilot and recovery drills,** then the increments in C13 and C14, then conversion and the
    retirement gate.

Steps 2 to 5 can run as parallel lanes. Step 7 needs 5 and 6.

## Appendix: owners for the substrate plan's "locate" rows

Paths are under `packages/intentd/crates/` unless shown otherwise.

| Plan row | Owner |
|---|---|
| Task and note services | `intent-core/src/model.rs:1900-1945`; `intent-services/src/{note_ops,note_write,note_merge}.rs`; `intent-store/src/{note_repo,note_version_repo,task_agent_link_repo}.rs`; migrations `0021`, `0037`, `0151` |
| Agent create, delegate, wake | `intent-services/src/agent_ops.rs`: `agent_create_op` 5980 (admission 6059-6100), `agent_delegate_op` 13731, `agent_wake_or_create_op` 17306, `agent_report_to_parent_op` 12842 |
| Turn dispatch gate | `intent-services/src/agent_manager.rs`: `acquire_turn_start` 2200, `run_turn` 6734, `try_begin_turn` 10651; `agent_session.rs` `run_prompt_turn` 3931 |
| Completion settlement | `intent-services/src/lib.rs:9115` `deliver_completion_to_watches`, loop at 7517; `agent_subscriptions.rs` (`CompletionWatch` 155, `DelegationGroup` 217); tables `completion_watch`, `completion_wake_delivery` |
| Auto-record | `intent-services/src/auto_commit.rs` (`spawn_auto_commit_loop` 207, started from `intentd/src/main.rs:3007`) |
| Context and prompt assembly | `intent-context/src/lib.rs` (`ContextEngine`); `intent-services/src/rules.rs:589-742`; `intent-store/src/workspace_context_repo.rs` (opaque payload) |
| Usage | `intent-services/src/{agent_session.rs:6213,token_usage.rs,usage_stats.rs,usage_semantics.rs}`; `intent-store/src/usage_stats_repo.rs` |
| Store migrations | Newest is `0190_agent_session_permission_policy.sql`; next is `0191` or later |
| Checkpoint pointers | `0136_node_foundations.sql` (`node_checkpoint`, `node_assignment.current_checkpoint_id`); codec at `intent-git/src/checkpoint/mod.rs` |
| Placement | `intent-core/src/placement.rs` (`PlacementCheckout` at 38) |
| Transport and capabilities | `intent-transport/src/router.rs`; `client.rs:118-170`; `protocol.rs:774` |
| Agent bindings | `intent-acp/src/mcp_server/bindings/mod.rs:392-470`; `git.rs:46`; `workspace.rs:80` |
| Accept changes and review | `intent-services/src/accept_changes.rs:18-28` (includes an `export` action the frontend does not list), `:266` `history_refresh_identity`; `intent-core/src/native_review.rs` |
| Attribution | `intent-git/src/attribution.rs:218` (`PathState`); `intent-store/src/tracked_changes_repo.rs` |
| Frontend | `packages/cloudlands-fe/src/lib/client/app-client.ts:1629` (`GitClient`); `lib/components/workspace/sidebar/`; `features/accept-changes/`; `shared/app-settings-schema.ts:234-300` |
| Packaging | `packages/cloudlands-fe/electron-builder.yml:35-61` (`extraResources`) |
