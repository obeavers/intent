# Atomic substrate: implementation status ledger

**19 November execution status:** the [current reconciliation journal](atomic-reconciliation-execution-2026-11-19.md)
records preserved source, local integration commits and current gates. The opt-in CLI
builds; its real attempted run failed before provider admission because local host
IPC binding was denied. T1 is not qualified. Nothing has been pushed, merged into
main or activated. R1 path provenance is corrected; the 361-definition guard, its 26
tests, doc links and all 20 root consumer checks pass. Earlier branch tables and
validation receipts below are historical.

**18 November integration audit:** the
[reconciliation plan](atomic-reconciliation-plan-2026-11-18.md) records current main
divergence, unreconciled worker trees, migration conflicts and the path to T1. No merge
or implementation gate is completed by that analysis.

## Historical reconciliation execution — 18 November 2026

C0 is **green for source preservation only**: checkpoint
.reconciliation/checkpoints/20261119T035821Z verified nine source trees, 864 file
versions and three independently restored repository bundles, retaining 128 refs and
original shallow boundaries. The exact verification command and recovery notes are
in the [current handoff](atomic-substrate-handoff-2026-11-15.md#reconciliation-execution-checkpoint--18-november-2026).

Current-main integration is local in separate clones on integrate/atomic-t1, starting
at root ae48c764 / daemon 643f862. The original branch names, W/A/V states and test
receipts below describe the preserved feature-source checkpoint. They do not establish
that the extracted current-main implementation compiles or passes its runtime gates.

R2 additive protocol checks pass against pristine root pins eade125 / f4a8646. R1
delivery coverage passes all 361 retained definitions and its 26 tests; its full docs
gate is blocked by ten references to scripts absent from the current daemon pin.
Those scripts must land and be pinned, or R2 must land separately ahead of R1. The
checker and protected plan requirements remain unchanged. B1–B4 and T1 are in progress;
ordinary Atomic source authority remains disabled.

## Historical implementation ledger

The historical script and artifact names below belong to the preserved feature-source
checkpoint, not the current pinned component checkout. Their original source is retained
in .reconciliation/checkpoints/20261119T035821Z. Commands, results and counts remain
historical receipts; current integration gates are recorded in the execution journal.

Tracks `docs/plans/atomic-substrate-adoption-2026-11-12.md`. A gate is marked **green** only
with the exact command that ran and its result. States: `not started`, `in progress`,
`code landed` (local branch, not gated), `green`, `blocked` (reason), `deferred` (reason).

Branches: monorepo branch docs/atomic-substrate, intentd `feat/atomic-substrate`,
cloudlands-fe `feat/atomic-substrate`. Nothing pushed; no PRs; no merges.

Atomic sources: `~/CodeRepositories/atomic-src/atomic` at `bf9893a`, skills at `e9332eb`.

**Resume here:** [concise implementation handoff](atomic-substrate-handoff-2026-11-15.md).
It summarizes delivered code, validated boundaries, blockers, source locations and next commands.

**Execution sequence:** the governing plan's [T1–T5 delivery section](atomic-substrate-adoption-2026-11-12.md#12-delivery)
now controls work. Its [coverage map](atomic-substrate-delivery-map.json) retains all 361
original definitions. Only the three T1 integration tickets are initially active. This
plan-only refactor does not change any implementation or qualification status below.

## Implementation boundary (2026-11-15, continuing)

The initial foundation was only a partial delivery. Implementation is continuing across the
seam, ledger, host and frontend instrumentation lanes; all changes remain local and uncommitted.
The manual Linux Docker attempt has now finished: the actual GNU x86_64 host release
build and 92 default-profile runtime/process tests passed, with four ignored. Its
containment control was unavailable because bubblewrap could not create a namespace;
the overall qualification remains blocked. See the completed evidence below.
The validation table below records the first foundation run; later changes require fresh
central validation and are not covered merely by those earlier passes. Atomic source authority is not
activated. The confirmed-plan frontend, backend and retained first-turn evidence reads are
implemented and separately gated; their task-planning/read capabilities do not enable Atomic
source authority. The full plan remains incomplete. Private composition has local native and Git tests; qualified normal source authority,
adoption/rewind, qualified independent reviewer execution, publication, the corresponding
product surfaces and rollout still have open work.
Qualification must complete before dependent runtime work is admitted. The bundled assistant guide's “Add context, run a task, and find
results” section now explains reviewed task plans, pinned first-run launch, retained first-turn
evidence, human completion and reopening before requirement edits. Experimental read models and
native features are not promoted there.

### Resumed implementation and current gates (2026-11-15)

Native host contract version 3 now dispatches actual store initialization, task projection,
session creation/metadata close, turn declaration/freeze, exact bound record preparation/admission,
control capture, triage, working-copy registration and recorded-view closure operations. An exact
record retry can finish its uniquely retained interrupted operation while ordinary commands remain
blocked for explicit reconciliation. A metadata session close is not provider process exit.

The daemon now owns original native task/turn/session/execution/settlement objects and retains exact
record commands, encodings and known native facts for historical recovery. Startup discovers retained
record owners in bounded pages; it never substitutes a current task or starts a provider. Fresh local
runtime observations retain the original allocation and actual child exit, separately from callback
drain. The internal manager now joins those owners to actual source capture, pre-record checkpoint
and bound settlement. Positive Linux namespace/pidfd execution and the complete provider/CLI route
remain unqualified; the ordinary Atomic workspace path stays disabled.

Checkpoint aggregation now retains raw dirty/ignored files, selected bytes/deletions independent of
later working edits, evidence and exact native closure objects. Recorded-view closures preserve
conflicts and explicit empty directories, and restore after deleting all original Git/native stores.
Replay validates the existing private restore without following replaced metadata paths or repairing
changed files. Unsupported native external knowledge, attributes and presentation differences refuse
explicitly. Store-owned reservations allocate ordered capture revisions; actual archive, canonical
receipt and component blobs are retained before the same-transaction root/epoch/working-copy pointer
CAS. Replay preserves the original disposition and observes current pointer freshness separately.
Services capture borrows the original drained source and frozen turn before record settlement, then
startup scans retained owners in bounded pages and resumes verified bytes without native recapture.
Missing retained components refuse rather than being rebuilt. Off-view selected contributions and
unavailable original selected payloads are explicitly unsupported in this source owner. The
frozen-baseline profile remains a baseline-plus-overlay profile; recorded-view capture exports the
original named native view. Workspace replacement and normal Atomic readiness are not implied.

| Claim | Exact command | Result | Evidence |
|---|---|---|---|
| Native recorded closure and aggregate restoration | `cargo test --offline --locked --manifest-path packages/intentd/atomic-host/Cargo.toml --lib -- recorded_closures aggregate_recorded_checkpoint_tests aggregate_checkpoint_tests --test-threads=1` (Rust 1.98, isolated Cargo home, run from `/tmp`) | 13 passed | `/tmp/intent-atomic-validation/aggregate-recorded-native-audited-20261115.{json,log}` |
| Typed checkpoint/closure clients and immutable replay | `COMPACT=1 CARGO_NET_OFFLINE=true python3 ../../scripts/resumable_nextest.py --compact-cargo cargo test --offline --locked -p intent-atomic --lib -- checkpoint::tests recorded_closures::tests --test-threads=1` (from intentd) | 15 passed | `/tmp/intent-atomic-validation/aggregate-recorded-client-audited-20261115.{json,log}` |
| Native-host full library run before policy-only test addition | `env -u VOYAGE_API_KEY -u OPENAI_API_KEY -u ANTHROPIC_API_KEY CARGO_HOME=/var/folders/g1/8492sgnd1bvgv0mdjfblysv00000gn/T/intent-atomic-host-cargo-5p9tt_qa CARGO_NET_OFFLINE=true CARGO_TERM_PROGRESS_WHEN=never rustup run 1.98.0 cargo test --offline --locked --manifest-path /Users/oliverbeavers/CodeRepositories/intent/packages/intentd/atomic-host/Cargo.toml --lib -- --test-threads=1` (from `/tmp`) | 135 passed, 0 failed, 4 ignored; 165.76s tests | `/tmp/intent-atomic-validation/native-host-library-coherent-20261115.{json,log}` |

Confirmed planning now has criterion/required-kind/file-reference inputs and distinct review,
confirmation and first-run actions. Human-only `task.configureWorkDefinition` performs one strict
note CAS; `agent.create.expectedTaskRevision` persists the original source through first admission.
The client requires the exact acknowledged planning capability and connection/principal at actual
transport send, preserves known allocation facts after connection changes and never silently falls
back to an unpinned or remote launch.
Frontend planning validation passed 573 unique tests plus renderer/main TypeScript, scoped Svelte,
ESLint, localization and ownership checks; the final cohort/recovery logs are
`/tmp/intent-task-planning-complete-final-tests.log` and
`/tmp/intent-task-planning-recovery-final-tests.log`. The historical evidence surface now has its real bounded
`task.workEvidence` RPC, dedicated read capability, SQL owner, frontend and guide text; its focused
frontend cohort passed 413 tests (`/tmp/intent-task-run-evidence-final-tests.log`). Reads resolve the original confirmed first-admission binding,
independently page contributions and committed SQL effect references, and label source previews,
unknown coverage and unavailable check/review/settlement linkage. They do not infer task completion,
source adoption or complete authorship. Dedicated multi-child fan-out and V44 remain open.
The daemon and transport test targets, including new WebSocket contract tests, compile. Actual
WebSocket execution still cannot bind in this session. These results are not an end-to-end source
acceptance test or a qualification of the full migration.

The current daemon-owner cohort passed 153 Services tests and 8 ACP tests, with two explicitly
ignored Services entries. All eight Services checkpoint cases now pass after correcting their
original repository locator and canonical fixture root; production guards were preserved. This
cohort also covers descriptor-safe callback worker cancellation, original connection/MCP scope,
retained native fact recovery, cold quarantine, credential-leaf races, resource preflight, confirmed
planning, auto-commit engine routing and serialized capture fences. Public ordinary provider creation
now refuses persisted Atomic roots before probes, processes or custody side effects, and refuses a
foreign session workspace. Reused/remote/session-open paths and the final synchronous spawn branches
have the same negative guard. The existing turn-start future-size budget passes unchanged.
Exact command and receipt: `/tmp/intent-atomic-validation/daemon-owner-final-verified-20261115.{json,log}`.

The subsequent isolated Store integration cohort passed all 56 cases, including all 11 checkpoint
tests, confirmed-plan pins, historical evidence reads and transfer exclusion registration. Its
receipt is `/tmp/intent-atomic-validation/store-checkpoint-integration-20261115.{json,log}`.
The complete daemon client/protocol libraries also passed: 62 client and 9 protocol cases, recorded
in `/tmp/intent-atomic-validation/atomic-client-proto-full-20261115.{json,log}`. Strict native-host
all-target Clippy passed with `-D warnings`, recorded in
`/tmp/intent-atomic-validation/native-host-clippy-scrubbed-20261115.{json,log}`.

The read-only memory slice passed 63 frontend tests plus renderer/main TypeScript, scoped Svelte,
ESLint, localization, Redux and ownership gates. Its exact server capability is advertised only by
the existing explicit memory opt-in on a non-node Services composition. Normal deployments omit it.
The Context panel labels it experimental, performs explicit bounded page reads, and purges previews
when the original view/session retires. It exposes no selection, delivery, claimed-use or acceptance
mutation. Exact receipts: `/tmp/intent-atomic-validation/fe-memory-read-final-20261115.{json,log}`
and `/tmp/intent-atomic-validation/fe-memory-static-final-20261115.json`.

The complete monorepo consumer runner now passes. Plan references were corrected without placeholder
files or check exemptions, and the event-stream fixture was exported for both components using the
shared tool and its actual committed canonical source. Receipt:
`/tmp/intent-atomic-validation/monorepo-consumers-verified-20261115.{json,log}`.

Actual private Draft reconstruction now preserves original project/objects/views/materialization,
while a host-owned journal alone permits fresh local numeric IDs during assembly. Native admission
still uses the original expected state. The native record/seal/working-copy cohort passed 29 tests
with one ignored subprocess entry. Independent changed-path coverage prevents ignored selected
files from silently becoming a no-change or partial receipt; symlink ignore controls refuse before
native ignore loading. The current full native-host run completed 139 tests: 135 passed, none
failed and four ignored, superseding the earlier fixture failure. It includes actual Draft sealing,
ignore coverage, the 16 warm-copy safety cases and process-crash child fixtures. The warm-copy
case may explicitly return unsupported before cloning; this pass does not prove copy-on-write
support, warm-build budgets or Linux process-scope custody. Five subsequently added policy-only
cases passed separately; native all-target Clippy and formatting cover that final source tree.

The internal manager path now joins actual scoped-process exit, isolated descriptor-safe ACP
callback drain, original task/selection, pre-record checkpoint and bound native settlement inside
registered finite owners. Scope subjects are associated with their original work before release;
exit bytes are archived only after actual pidfd/Child observation. Startup quarantines prior private
allocations without restoring custody, and resumes retained record/checkpoint bytes without current
task lookup or source recapture. Checkpoint failure remains separate from a later known record fact.
This is an internal qualification path: no normal selector, provider resource/network configuration,
MCP tool routing, auto-selection/attribution policy or user Atomic capability is qualified.

Future Linux qualification accepts explicit `--platform linux/arm64`, avoiding amd64 emulation on an
ARM64 Docker engine; amd64 remains the default and the release matrix is unchanged. Platform,
compiler, ELF machine, source, recipe and resume identities are fenced. A tiny compile-only probe
includes the exact production Linux process-scope files and runs before the expensive native build
after namespace preflight. Its denied Services shim is not a Services/runtime/MSRV proof.
A separate explicit ARM64 compile-only entry now stages just the five probe/source inputs and
checks them without requiring namespace preflight. It performs no native-host build, provider,
test or scope execution; its distinct receipts cannot resume or qualify the full runner. This lets
a normal Terminal obtain Linux type errors independently of a denied namespace control. All 58
CI-wired packaging/mocked qualification cases pass; actual Linux compilation and namespace scope
execution remain unrun here. The original November 14 output remains untouched and cannot qualify
new contract/version-3 source.

Repository formatting now passes with the project's formatter. Full `make check` is blocked at
`cargo shear`: offline Cargo metadata needs uncached `anstyle-wincon 3.0.11` even on this Mac host.
Strict workspace all-target Clippy passes with `-D warnings`. All 25 source-lint suites pass,
297 tests total, including the new process site classified against its actual `prepare_scope`
provider gate. Test waits use the repository timeout helper; no lint budget was raised. Final
workspace and standalone-host formatting and native all-target Clippy pass. The unconditional
legacy-start guard and unchanged future-size budget also pass their three focused cases after
extraction, and actual pinned-package/hello checks pass separately.

[Implementation-checkpoint validation receipts and changed-code inventory](atomic-substrate-validation-2026-11-15.json)
retain 16 successful commands, their results and raw-log hashes, required blocked commands, frontend
handoffs and the exact-source CLI compatibility report. The inventory is a current cumulative
worktree snapshot from before the delivery-plan refactor, not a current fingerprint,
authorship attribution or retroactive sealed-build proof. No merge,
activation, signed install, user database migration or release has been performed.

### Current source-adoption slice (2026-11-14)

The Git source-confirmation/adoption owner is under implementation; this is not a completed
plan or an activated feature. New code is being centrally validated. Earlier green selections
do not qualify these edits. No protocol route or capability is enabled.

Here “Git adoption” means applying a confirmed candidate to an existing **Git** working
copy. It does not mean adoption of Atomic itself. This slice exercises the shared evidence,
confirmation and recovery contract on the current backend. Live **Atomic** workspace
activation (W26), native source-turn ownership and the corresponding end-to-end workflow
are still unavailable; these Git tests cannot qualify them.

Actual ACP, Git facade, direct file RPC, attachment and local pull writers now retain counted
admission through their effects, including blocking work that survives caller cancellation.
The capture owner closes execution first, drains it, then closes and drains source primitives
before taking the existing worktree mutex and revalidating the root. It currently closes all
workspaces conservatively because different workspace/root IDs may alias the same checkout.
Admission reopens after revocation and kicks parked sends, including canceled acquisitions.

Provider runtime teardown is **not qualified**. A busy-empty observation, stop request or absent
new-daemon handle is insufficient. Immutable custody refusals are retained before provider
startup, and migration seeds legacy session workspaces. Until actual process/callback exit
receipts exist, these refusals survive restart and prevent live source-adoption barriers.
Remote executor write barriers also remain unavailable. Current Git reviews retain unknown
potential authors/read-only gaps, so source acceptance remains blocked; explicit human review
scope does not fabricate qualification. Preparation, rejection and request-changes are being
implemented separately from physical effect admission and completion CAS.

Registered runtime/transfer feature owners remain unqualified and cause barrier refusal,
including registration through another Services clone. Only the built-in stateless wake adapter
is allowed because every turn it starts uses the counted manager. The reduced internal composition is
the only current positive barrier fixture. Fresh source adoption also refuses any active work
binding anywhere on the daemon. Current production wiring supplies neither a qualified
review producer nor a CandidateRunner custody owner. There is no ordinary source-acceptance
or Atomic workspace path to advertise.

Native macOS cannot run the repository's Linux x64 callback fixture; the prescribed test
runner refuses before execution. This sandbox also denies loopback binds, and crates.io DNS
is unavailable for uncached cross-platform metadata dependencies. These failures are recorded
as blocked gates, not passes. Focused filesystem-only checks supplement the refused gates.

## Decisions taken on open questions

| Q | Taken | Basis |
|---|---|---|
| Q1 | Only the primary agent writes in the workspace working copy | Plan recommendation |
| Q5 | Merge index is an Intent table only | Plan recommendation |
| Q6 | A human may complete a bound task without confirmation, recorded as such | Plan recommendation |
| Q2 | Daemon-owned local signing files per D16; Linux qualification open | D16 and its owner-only-file fallback; no new custody policy chosen |
| Q3 | Embeddings remain off; lexical/local recorded-code path only | Default no-network profile; enabling an external provider remains a separate choice |
| Q4, Q7 | Fork/upstream owner and eligible dogfood repositories remain open | Required before their respective qualification/rollout gates close |

## Work items

| ID | Goal | State | Evidence |
|---|---|---|---|
| W01 | Build spike, pin, fork policy | blocked | Pinned `bf9893adb57dccbaa8f7e14277e02d060d74bf53`; reproducible offline qualification and local uncommitted evidence at packages/intentd/atomic-host/qualification/evidence/2026-11-13/ (absent from the pinned checkout). SQLite link conflict reproduced for all four target resolvers; standalone macOS arm64 probe built. Real host cross-target builds, contained runtime checks and fork ownership remain open. |
| W02 | Owner manifest | green | Current inventory814 rows,0 unclassified;5 generator tests pass and two regenerations match. Diagnostic inventory only; see the historical daemon scripts/vcs-seam-manifest.md in the preserved source checkpoint for limitations. |
| W03 | Neutral types and errors | green | `cargo check -p intent-core --tests --offline --locked` passed; `cargo test -p intent-core --test vcs_contract --offline --locked`: 7 passed. Tagged identities, explicit unsupported/error outcomes and Git/Atomic serialization fixtures. |
| W04 | `git2` consolidated into `intent-git` | green | Production `git2::` uses removed from `accept_changes.rs` and `git_ops.rs`. Git owns coherent ref capture and submodule path context; services retain JSON/hash/error policy. The native service selection passed 84 tests (all existing selected cases); a new empty-path fixture was corrected without changing production behavior and all 3 attribution tests then passed. Git history 32/32 and submodule 16/16 passed; full workspace Clippy and source lints passed. Full prescribed Linux gate remains blocked. |
| W05 | `GitWorkspaceEngine` | in progress | Git implements retained target capture, complete composition custody, journaled changed-path application and inspection-only recovery. Latest central Git selection40 passed, including descriptor-safe symlink/FIFO refusal, owner-only operation directories and known-CAS progress. This provides no Atomic activation evidence. |
| W06 | Call-site migration: reads, writes, attribution, auto-commit outcomes, accept-changes, provisioning | in progress | Live RPC/cache/refresher/accept-changes/lifecycle migrated through rooted engine/provisioner. Admission, nested-repository and observed-state mechanics belong to intent-git;77 direct hits remain in67 frozen source/symbol keys, down from180 keys. Complete V1 wire parity and current whole-tree gates remain open. |
| W07 | Seam lint in CI | green | The seam lint's6 cases passed at its last recorded gate. Current frozen source/symbol keys are180→67 with77 direct hits; no broad exemptions. Existing CI source-lint glob discovers it. This counts qualified paths/imports, not later calls through an existing alias, and does not replace fresh whole-tree source lint after later edits. |
| W08 | Blob store and outbox | in progress | Unix dirfd/nofollow/fsync immutable blobs, same-transaction outbox, replay and uncertainty implemented. Latest central Store selection58 passed, plus4 completion/import regressions. Native vault/projector delivery and nonUnix durability remain unqualified. |
| W09 | task_revision, work_binding, dispatch gate | in progress | Manager admission retains exact turn UUID, original TaskRevision and Active status atomically, with ABA/cancellation fences and immutable delegation origins. Confirmed planning persists the original human source with allocation and rechecks it at first admission without latest-task fallback. Internal Atomic admission validates the retained native projection; actual source/grant/settlement owners are joined. Earlier117-case cohort passed; later checkpoint/runtime edits need the expanded rerun and positive Linux custody qualification. |
| W10 | Check runs bound to a candidate state | in progress | Configured host checker runs against a privately verified materialization with bounded outputs/artifacts, cancellation/drain and retained uncertain recovery. Seven actual runner tests passed within41-test service selection. The opaque composition-proof path retains exact full inventory; its actual service tests pass in the95-test selection. No default command RPC or OS process filesystem/network sandbox. |
| W11 | task.confirm, receipts, completion gate | in progress | Strict source offers, original human decisions, opaque effect admission, native fact retention and separate completion CAS are implemented internally. Latest Store selection43 and Services73 selections passed. Full workspace Clippy and all25 source-lint targets pass. Runtime custody and qualified review remain unavailable; no RPC/UI/capability enabled. |
| W12 | Projection and merge index; work.explainChange by blame | in progress | Exact contribution/merge/explicit line mappings and bounded ledger reads exist. Native settlement retains actual receipt/encoding facts; shared-copy recording governance and historical association do not prove complete authorship. `task.workEvidence` exposes only original first-turn contribution identities and linked committed SQL effects. Earlier auto-commit/explanation tests pass; automatic merge/squash/rebase lineage, native blame and complete authorship remain unqualified. |
| W13 | Baseline metrics | in progress | Actual per-dispatch provider/model acknowledgement, physical connection, retries/failovers and immutable usage capture implemented. Capture must start before the first managed invocation; it cannot backfill legacy coverage. Store4 usage cases passed in the latest62-test selection; all five actual runtime cases pass in the95-test service selection. Missing accounting/identity remains unknown. Two-week baseline and cost/performance comparison are absent. |
| W14 | Protocol docs and fixtures | in progress | Actual `task.configureWorkDefinition`/`task.workEvidence`, dedicated hello capabilities and durable `agent.create.expectedTaskRevision` are documented and registered, separately from experimental read models/memory. Catalog/field-parity checks and earlier router/event fixtures pass at their recorded snapshots. New real WSS contract targets compile, but socket execution remains denied; this does not qualify the complete protocol or source workflow. |
| W15 | Contract crate, client, supervision | in progress | Native protocol v3 dispatches actual store/project/turn/session/record/capture/control/triage/recorded-closure operations, with exact handshake/reconcile, bounded frames/spools and lazy supervision. Earlier31 client/protocol tests passed; later checkpoint/closure15 and sealed-source3 selections passed. The actual compiled process contract still cannot bind its private Unix socket (EPERM); new contract source is not qualified by the old Linux binary. |
| W16 | Host skeleton: store open and validation, operation journal, reconcile | in progress | Exact-pin Rust1.98 host has shared handles, durable operation ownership and conservative reconciliation. Current full139-case library run completed135 passed/0 failed/4 ignored in165.76s, including genuine Draft sealing, ignored-change coverage, warm-copy safety and process-crash children. Unsupported-COW early return is not clone qualification. Earlier native Clippy passed at its source snapshot; socket/containment/cross-target and Linux process-scope gates remain open. |
| W17 | Derived store import, code queries, ContextEngine | in progress | Actual native add/record/search/SyntaxIndex over named immutable Git trees, scope budgets and complete QueryReadBasis implemented. Authorized Services prepare/query path and optional inline/stream basis forwarding integrated;4 service query/forwarding cases passed. No default activation/capability or network-containment qualification. |
| W18 | Memory owner, retrieval, prompt injection | in progress | Immutable ledger memory, actual owner filtering, revision-gated rank/pull/selection and exact retained prompt bytes integrated with original turn. Delivery acknowledged only after successful prompt result; use remains separate.5 prepared methods require explicit server opt-in defaultfalse. Unit selection passed; native vault projection/cross-workspace grants and real WSS qualification remain. |
| W19 | work.* reads with read basis and scoping | in progress | Task/code reads retain durable watermarks and explicit scope. Public `task.workEvidence` resolves retained original confirmation→first admission→binding, excludes later/current-task fallback, bounds previews/results and independently pages contributions/effects without polling. Store/Services cases passed in the earlier117 cohort and FE reader413 passed; check/review/settlement linkage, native blame and complete candidate contribution coverage remain unavailable. |
| W20 | Exact record and durable ingress | in progress | Actual native raw-v3-byte preparation, fsynced ingress, expected-state writer admission, retained no-change/posteffect receipts and crash replay implemented. Real3phase subprocess crash tests and terminal-integrity recovery passed. New records restricted to Draft; no live source route. Upstream ingress/filter patches remain project-contained and unapplied. |
| W21 | Baselines, views, materialization, fidelity | in progress | Independent full-reimport baseline fallback and exact fidelity tests pass for binaries,CRLF,exec,symlinks,empty files,ignored tracked files and filters.20k corpus ran twice in debug:636.32s and779.26s under mixed compile load; materialization improved but total variance prevents a speedup claim. No release/p95 budget qualified. Incremental baseline storage/canonical live drafts remain open. |
| W22 | Closure export and restore; format-2 checkpoints | in progress | Actual frozen-baseline and recorded-view archives retain native closure objects plus exact raw overlay, independent selected bytes/deletions and evidence. Opaque Store reservation, durable component/history retention and monotonic root/epoch/working-copy pointer CAS exist; registered pre-record Services capture and bounded retained-byte startup recovery are wired. Native13/client15 aggregate selections and earlier10 Store checkpoint cases passed. Store now has11 cases; Services8 are authored but latest fixture correction awaits rerun. No workspace replacement/readiness; off-view selected contributions or unavailable original selected payloads refuse. |
| W23 | ACP provenance feed | in progress | Durable journal/SQL ingest and seal/cancel recovery exist. Fresh scoped prompts use a private queue, descriptor-safe filesystem service and actual worker tickets; original connection/MCP gates and cancellation tails passed in the earlier integrated cohort and latest ACP8 selection. Internal native execution joins actual callback drain with process/source owners. Reused sessions remain SessionAmbiguous, and Claude Code/Codex provenance parity plus positive Linux process execution remain unqualified. |
| W24 | Intent bridge: create-or-resolve, pins, turn binding, control workspace | in progress | Stable UID, exact source/canonical/substance/proof pins, partial projection repair, current control export and HostFacadeFreezeV1 are implemented/tested locally. Original TaskRevision survives incidental note bookkeeping; completion separately CASes completionNoteRev. The internal manager joins original native task/session/freeze to execution and settlement, but binding is never freeze proof. Full provider/CLI, Linux source custody and activation remain unqualified; no upstream patch is claimed. |
| W25 | Capture barrier, workspace working copy, child clones, grants | in progress | Actual internal `execute_scoped` now joins original native/SQL grants, isolated allocation, actual child/process-scope exit, callback worker drain, source fences, pre-record checkpoint and exact bound record settlement inside registered finite owners. Startup quarantines prior allocations and resumes retained records/checkpoints without source recapture. Latest Services114/120 had only six new checkpoint fixture failures, now source-fixed but not rerun. Positive Linux namespace/pidfd execution, normal provider/CLI routing, resource/network policy, clone budgets and a normal selector remain open. |
| W26 | Atomic workspace lifecycle, eligibility, ignore parity, Labs flag, capability, agent instructions and bindings, turn settlement. Lands together so no Atomic workspace runs without a recorder | in progress | Internal native turn recording/settlement and retained recovery are joined, but the activation bundle remains absent. Eligibility/ignore parity, source-engine selection, normal provider/CLI routing, instructions and gated creation are not qualified. AtomicWorkspaceEngine advertises no normal capabilities; the ordinary workspace path still selects Git. |
| W27 | Composition, conflicts, adoption, rewind and fork | in progress | Native private composition and immutable capture exist as local library operations; canonical Atomic targets remain unchanged. Atomic resolution, application, rewind and fork are missing. Shared Git application/recovery tests do not qualify these native operations. |
| W28 | Triage, signing, reviewer agent | in progress | Native triage/signing exist as local library evidence APIs. Required typed transport/client integration and a qualified reviewer producer are missing. Current inventories deliberately retain unknown potential authors, and every retained review receives a read-only execution gap. A signature cannot confer independence or readiness. |
| W29 | Projection repository, publication, evidence block | in progress | Prepared Git transport now supports explicit branch-absent or exact advertised-old condition plus actual local fast-forward ancestry with non-force refspec.4native-push tests passed. No GitHub/GitLab push qualification, native projection repository, publication/evidence/PR receipts or capability enabled. |
| W30 | Types, clients, slices, capability helpers | in progress | Neutral DTOs and actual desktop/browser clients now carry reviewed planning and bounded first-turn evidence reads through dedicated acknowledged capabilities and current-connection/principal guards. Planning573 and evidence413 FE tests passed with scoped type/static gates. These capabilities are independent of inactive Atomic engine/mutation ports; no Git fallback or source-readiness inference is introduced. Full transport/runtime gates remain open. |
| W31 | Task confirmation, evidence and review surfaces | in progress | Existing source-joined confirmation/card owners remain separate from the actual task-plan editor and Recorded work surface. The latter shows original first-turn contribution/effect identities, source previews and explicit unavailable check/review/settlement links with manual independent pages. FE planning573/evidence413 passed; source acceptance/reviewer decision ports and independent review qualification remain unavailable. Human completion stays a separate action. |
| W32 | Atomic changes panel, selection, conflicts, activity, create flow | not started | |
| W33 | Knowledge entry points and memory | in progress | Actual explicit non-node server opt-in advertises `experimentalMemoryRead:1`; normal composition omits it. Strict read-only clients, captured transport, Redux ownership and the labeled experimental Context panel passed 63 frontend tests and both TypeScript/static gates. Services scope/opt-in tests and the actual hello helper pass. Related-work and why-line entry points remain open; no memory mutation or source authority is enabled. |
| W34 | Packaging and CI for the host | in progress | Exact-pin isolated host build,4target CI/release composite, staged complete hashes and signing/fetch rules implemented. Python build11+containment6 and FE payload/fetch/sign59 tests passed; workflow lint passed. Cross-build/signing/contained-runtime execution not run; local release suites lack PyYAML. |
| W35 | Pilot, recovery drills, benchmark | not started | |
| W38 | Latency instrumentation and harness | in progress | Opt-in correlated renderer/main/daemon timing, bounded4096 capture, strict23metric comparator and actual CDP-Paint harness implemented. Latest496 tests/16files passed, plus later recovery corpus suites. Static8/9 passed; tsx IPC bind EPERM blocks complete FE gate. Named machine20k repo/live V39 timings remain unmeasured. |
| W39 | Push read model and fenced mutations | in progress | Transactional paired sequence/token projection, bounded snapshot/replay and captured-session main/browser ingress implemented. Git owning mutation tails invalidate stale generations despite waiter cancellation; explicit startup recovery fences precrash tokens without a status walk. Current Store and actual service facade cases pass. FE focused transport/recovery suites pass; official architecture, real WSS and p95 qualification remain blocked/unmeasured. |
| W40 | Skills delivery and sandbox ingress: bundled pinned skills, catalog precedence and hiding, Intent's workflow body, the pinned CLI under grants | in progress | Exact source manifest, read-only package verifier, persisted-engine hiding/precedence and inactive workflow body implemented. Eight catalog/content tests and explicit verification of the actual pinned seven-file package pass. The executable source audit identifies incompatible unchanged skill commands; 58 qualification-tool cases and five actual native policy/registry cases pass. Counted CLI ingress, command adaptation and distributable packaging remain open. Content/source checks confer no execution authority. |
| W41 | Planning flow: criteria, file references and confirmation/fan-out | in progress | Actual editor inputs exact criteria, required evidence kinds and repository-relative file references; explicit human confirmation uses one note CAS, then a separate Run persists the original task revision through first admission. Current-connection/principal dispatch guards refuse stale confirmation and preserve known allocations. `task.workEvidence`/Recorded work links only the original first confirmed turn's retained contribution/SQL effect observations, with unknown source relationship and unavailable checks/reviews/settlement. FE planning573/evidence413 and prior backend owner cases passed; latest expanded rerun is pending. Dedicated multi-child fan-out, complete observed file-reference settlement and V44 remain open; declarations grant no access or acceptance. |
| W42 | Speculative review: background composition, triage, entity summary and diff prewarm after each settlement; parse and snapshot caches | not started | |
| W36 | Increments, each with its own plan: incoming Git updates, remote placement and sandbox images, mixed roots, delegation certificates, external signing, portable evidence packets, partial-hunk selection, dirty-parent delegation | not started | |
| W37 | Conversion of existing workspaces; retirement gate | not started | |

## Assumptions

| ID | Assumption | State | Evidence |
|---|---|---|---|
| A1 | Linking `libatomic` into intentd fails dependency resolution or changes intentd's build | green | Historical intentd script scripts/atomic-qualify.py: four offline `cargo tree -d --target ...` probes reproduced the actual conflicting native sqlite3 links; per-target logs retained in qualification evidence. |
| A2 | The host builds at the pin for macOS arm64 and x64 and Linux gnu and musl | in progress | Actual standalone GNU Linux x86_64 host release build passed under Docker amd64 emulation on November 14; ELF identity and retained binary hash verified. Earlier macOS arm64 release result was a libatomic/repository probe, not the production host. Other production release targets remain unverified. |
| A3 | The host makes no network calls in its default configuration | blocked | macOS OS control refused with `sandbox_apply: Operation not permitted`, exit 71. The completed Linux Docker attempt also refused at bubblewrap namespace creation, before contained handler execution. Passing ordinary runtime tests under Docker network isolation does not replace the required independent denial control. |
| A4 | Recording with save and apply disabled yields stable bytes, and import plus insert reproduces the same hash | in progress | Native raw preparation/import/crash tests pass, including repeated exact bytes and same-operation concurrent preparation after lease fix. Full source activation still unavailable. |
| A5 | The durable-ingress patch is small and acceptable upstream | not started | |
| A6 | A root view Intent never mutates stays unchanged under every host operation, and a draft over it sees exact membership | green | Qualified per-baseline independent full-reimport fallback:5 frozen/fidelity/parent+sibling baseline tests passed. No mutable shared baseline is used. |
| A7 | Closure export restores on a fresh store with an identical materialization | in progress | Actual frozen-baseline/recorded-view aggregate fixtures restore native objects, exact raw overlay, independent selected bytes/deletions and evidence after original Git/native stores are deleted: native13/client15 selections passed. Unsupported native knowledge/presentation and off-view selected contributions in the Services owner refuse explicitly. Services durability/startup and complete platform/source qualification still need current gates. |
| A8 | An intent can be created with a caller-supplied identifier and repaired after partial creation | green | Actual native stable-UID projection and partial entry/manifest/materialization recovery tests passed; conflicting operation/source replay refuses. This qualifies the local host facade, not live source activation. |
| A9 | The host can address a working copy by explicit root and store path, and the agent's sandbox pointer can be supplied from outside the working copy | in progress | Pinned CLI discovers only an in-tree .atomic-sandbox pointer. Hardened excluded pointer fallback and actual warm clone/barrier under implementation; external environment pointer unproved. |
| A10 | A new baseline can be created as the previous baseline plus an imported delta, exactly and cheaply | deferred | Per-baseline full-reimport fallback selected and5baseline tests passed. Incremental native baseline chaining not claimed; actual20k corpus run currently measuring fallback cost. |
| A11 | Turn binding is callable as a library and freezes at record start | in progress | Pinned public bind API available; native freeze method private. Local HostFacadeFreezeV1 tests pass for exact fsynced marker, actual public same-UID bind refusal, lock contention, failure/NoChanges and process-exit recovery. Live recorder/turn-start integration remains open; binding alone never acknowledges a frozen turn. |
| A12 | The journal handlers are callable from the host, and the ACP-fed graph matches a hook-recorded one for Claude Code and Codex | blocked | Actual pinned tool classifier is callable/tested, but reused ACP sessions do not identify original prompts. Journals deliberately retain SessionAmbiguous, no causal binding, provenance_available=false. Fresh one-prompt transport6tests pass; full provider parity still required. |
| A13 | Preparation with sync, enrichment and indexing off does not advance authored state | green | Actual native preparation tests compare unchanged authored state with save/apply/sync/enrichment/index disabled; same-op concurrent requests reuse exact retained bytes. This qualifies local preparation only. |
| A14 | Triage runs through the repository API with the control workspace on the same store, and review metadata does not change a candidate's materialization | not started | |
| A15 | Local Ed25519 keys satisfy the canonical gate, and `attributedTo` can be bound to the configured signer | in progress |3 actual canonical signing/verification/tamper/key-storage tests pass. Native verification does not by itself bind attributedTo; host explicitly compares the DID to the configured public key. Local evidence signatures do not establish reviewer identity, independence or readiness. Linux/platform qualification remains open. |
| A16 | Sandbox grants enforce view scope and the capability subset with the host as authority | in progress |9 SQL ownership/revoke/drain tests,4 actual pinned SandboxImpl cases and8 adapted shared-handle native registry cases pass. The latter cover frozen/captured source, exact view, expiry/replay/restart, replacement safety and counted close/drain. Services producer and actual IPC/provider/CLI ingress remain unqualified. |
| A17 | A copy-on-write clone including ignored build output gives a warm build in the clone | not started | |
| A18 | Atomic honours nested `.gitignore` files, and materialized excludes take effect | not started | |
| A19 | Binary files record faithfully | in progress | Actual raw baseline/record corpus preserves binary,empty,CRLF,exec andsymlink data. Live turn selection/settlement is not activated. |
| A20 | Git import of a base branch is incremental, idempotent and fast enough on the largest repositories | not started | |
| A21 | Revision-gated memory pull works with owner filtering in a shared store | in progress | Ledger-only revision-gated fallback passes owner/selection/delivery unit cases. Real WSS test compiles but loopback bind denied; native vault projector unqualified. |
| A22 | The token-level merge behaves on real concurrent edits in Rust, TypeScript, Svelte and Swift | not started | |
| A23 | Conflict sets are readable after a private composition, and a resolution records as a new change | not started | |
| A24 | A tree built from a materialization is byte-identical to the Git tree it came from | not started | |
| A25 | Existing Git transport can enforce expected-old-value and fast-forward only together | in progress |4 actual local graph/remote-advertisement guard tests pass, including branch-absent and exact-old conditions. GitHub/GitLab network push qualification remains open and publication stays disabled. |
| A26 | Provider CLIs and setup scripts work in a directory with no Git repository | not started | |
| A27 | An older intentd refuses a newer database before inspecting roots | not started | |
| A28 | Native usage summaries can be joined to Intent's measurements without double counting | in progress |4 real usage Store tests pass original managed-start capture, immutable invocation identity, unknown cumulative baselines/gaps/reset and measurement dedup. Production per-dispatch capture implemented; exact Git contribution settlement still being connected. Native summary join is not inferred. |
| A29 | Keys can be held in the OS keychain through the existing helper on macOS, with a workable Linux store | not started | |
| A30 | Sandbox images are a workable baseline transport for cloud machines | not started | |
| A31 | The host can hold one long-lived store handle and serve concurrent read transactions beside one writer, for status, log, change, content and query reads | green | 4actual native snapshot/handler concurrency tests passed: ReadState+QueryCode complete during ObjectDurable/MembershipKnown held record; errored owner closes reads until reconcile; single ReadTxn cannot mix generations; lifted state hash matches upstream. No p95 timing claim. |
| A32 | `libatomic` handlers needed by the host (triage, turn journal, sandbox ingress) can run on the shared handle, or the host can yield its handle around them without stalling reads past budget | in progress | Native recording/read shared-handle fixtures pass. Triage/control/sandbox handlers still need actual shared-handle qualification. |
| A33 | The pinned `atomic` CLI inside a working copy reaches the host through the sandbox ingress with a grant token and no local store, and the capability subset withholds recording | blocked | Exact-source audit of21 pinned inputs identifies removed intent-builder command forms and required routes outside native sandbox scope. The existing Host counted registry is not shared by raw upstream gRPC handlers. Actual command execution remains untested; no CLI endpoint is enabled. The plan's adapted ws.vcs/ws.work fallback is not implemented or activated. |
| A34 | Status and record can be driven by a caller-supplied changed-path set, so both cost O(changed) | not started | |
| A35 | Record preparation for different working copies runs in parallel, with admission as a short fenced write | not started | |
| A36 | A triage report on a large repository finishes within a 10 s background budget | not started | |
| A37 | A directory-level clone on APFS and parallel reflinks on Btrfs and XFS meet the child-ready budget on a tree with 200,000 ignored files | not started | |
| A38 | The Electron main-process hop adds under 5 ms at p95 for a small request | not started | |
| A39 | Intent's skill catalog can give pinned skills precedence and hide skills by engine | in progress | Eight content/catalog tests plus actual pinned-package verification pass. Ordinary prompt assembly supplies an exact matching persisted root; unknown/Git/unverified Atomic states hide the reserved skills. Positive source-engine delivery and CLI readiness remain unqualified. |
| A40 | Line-level blame for unmerged native changes can be lifted from the CLI into the host | not started | |

## Verification cases

| ID | Case | State | Evidence |
|---|---|---|---|
| V1 | Every `git.*`, `accept-changes.*` and `file-tracking.*` response on Git workspaces is byte-identical before and after the seam | not started | |
| V2 | Git engine parity through the contract: status, diff, commit modes 1 to 4, discard, rebase, reset | green | Fourteen `intent-git` adapter parity tests passed via the native Cargo fallback; required Make runner refused the Linux-only callback fixture before running tests. |
| V3 | Seam lint fails on a new direct use | green | Historical intentd script scripts/check-vcs-seam.sh: 6 passed. New qualified dependencies/increased counts fail, removals pass, and the updater can only lower existing budgets. |
| V4 | Host contract: version mismatch refuses; killing the host mid-operation leads to reconciliation with no duplicate record | not started | |
| V5 | Exact bytes: repeat preparation is identical; import and insert reproduce the hash; crash injection at object durability and membership change | green | Actual pinned-native record preparation/import/admission and three-phase subprocess recovery tests pass in the latest71-test native library run. No user source route enabled. |
| V6 | A frozen baseline is unaffected by later parent and sibling activity | green | Full-reimport baseline parent/sibling/previous identity fixtures pass in the latest native run. No mutable shared baseline used. |
| V7 | Closure export and restore on a fresh store; late and repeated checkpoints; an older capture never replaces the pointer | in progress | Native13/client15 aggregate selections passed; earlier10 Store checkpoint cases cover immutable replay, reversed/concurrent completion, stale scope and monotonic pointer CAS. Store now has11 tests and the registered Services/startup owner has8 source cases; six fixture failures are corrected in source but their rerun is pending. Full qualified source/platform and workspace replacement gates remain open. |
| V8 | File fidelity: modes, symlinks, binaries, CRLF and filters, renames, case collisions, ignored tracked files | in progress | Native baseline/record/private-composition corpus passes exact fidelity and rejects filters/case/reserved-path hazards. Complete publication corpus and cross-platform qualification remain open. |
| V9 | Selection: selected versus unselected edits; another actor's selection untouched; `discardWorking`; missing attribution refuses | not started | |
| V10 | Turn settlement: every finish reason gives exactly one of four results; a duplicate idle event is a no-op; a new file is recorded | not started | |
| V11 | Child clone: verified against the baseline; a dirty parent is refused; a no-op child has no authored delta | in progress |12 local capture/native-handler fixtures pass, including dirty-parent refusal, original-owner drain and preserved ignored bytes. Actual live child/no-op settlement and child-ready budget remain open. |
| V12 | Composition: independent changes in both orders; same line, disjoint tokens; same token; three competing changes; dependence on parent work in progress | in progress |9 native and8 Git private-composition fixtures pass their respective merge/conflict/dependency/target-race cases. Complete language/concurrency corpus and live settlement are not qualified. |
| V13 | Conflict list and resolve; the resolution is a new contribution | not started | |
| V14 | Adoption: an advanced or dirty target is rejected under the barrier and left intact; old assignments are fenced | not started | |
| V15 | Rewind and fork reproduce the state at the chosen turn | not started | |
| V16 | A task edited mid-turn creates a new revision; a delayed acknowledgement cannot release a replaced turn | not started | |
| V17 | Intent creation repeated after a crash resolves to one identity; a conflicting replay is rejected | green | Actual stable native UID, partial creation recovery and conflicting original operation/source replay fixtures pass. |
| V18 | Shared files do not imply shared intent; an unbound historical change stays unbound | not started | |
| V19 | Provenance parity (A12); duplicate and delayed projection events; a stale index returns a partial read basis | not started | |
| V20 | A check run on the wrong candidate is rejected; failed checks are retained | not started | |
| V21 | Triage: empty placeholder arrays are not read as clean; a stale control-workspace projection returns stale; review metadata leaves the candidate's materialization unchanged | not started | |
| V22 | Reviewer agent: a different model is enforced; the signature verifies; a changed candidate invalidates the review | not started | |
| V23 | Confirmation: stale offer on changed requirements, candidate or target; adoption succeeds then the task transition fails and is recovered without reapplying; an agent cannot complete a bound task | not started | |
| V24 | A research task with no source change completes with evidence | not started | |
| V25 | Query scope: unauthorized neighbours and memories are not returned; truncation is flagged; budgets hold | not started | |
| V26 | Memory: a change between ranking and pull is rejected; retrieval, selection, delivery and use are distinct | not started | |
| V27 | Usage: overlapping measurements counted once; missing values reported as unknown | not started | |
| V28 | Projection: tree equals manifest; parent rules; import → record nothing → project gives a byte-identical tree on the fidelity corpus | not started | |
| V29 | Publication: expected-old and fast-forward enforced; push succeeds and pull-request creation fails; lost response; external branch movement | not started | |
| V30 | `.env`, `node_modules/` and files under a nested ignore are never recorded or projected | not started | |
| V31 | After merge, squash and rebase strategies, `work.explainChange` resolves a line to its task revision | not started | |
| V32 | Agents without Git: `git` fails; the pinned `atomic` read commands work; an external `atomic` cannot open the store; a user's global hooks record nothing | not started | |
| V33 | Capability matrix: old frontend with new daemon; new frontend with old daemon; Windows daemon; flag off | not started | |
| V34 | An older intentd refuses a newer database before inspecting roots or running startup cleanup | not started | |
| V35 | Load at 1, 4, 16 and 32 agents on representative repositories, same workload for Git and Atomic; no lost edit, no duplicate record, no unauthorized dependency | not started | |
| V36 | Knowledge layer on a Git workspace: import is idempotent; search, entities and impact answer with a read basis; no network calls | not started | |
| V37 | Retire and delete: ownership proofs; native custody confirmed before removal; evidence survives workspace deletion | not started | |
| V38 | Evidence loop on Git: a confirmation binds a commit and tree; a new commit makes the offer stale | not started | |
| V39 | Latency budgets: a scripted scenario on the mock-agent stack, on a named reference machine and a repository of at least 20,000 files, asserts every row of the table in section 5.11; a regression fails the gate | not started | |
| V40 | Push path: an agent write reaches the changes panel as a delta with no status walk and no refetch; a reconnect resumes by sequence number or resnapshots | not started | |
| V41 | An optimistic mutation made against a stale state token is refused and rolls back cleanly, for selection, record and confirm | not started | |
| V42 | Evidence capture adds no more than its budget to a tool call; settlement waits for the journal flush; a crash mid-turn leaves the turn uncertain, never silently short of observations | not started | |
| V43 | Skills: every command a bundled skill names exists in the pinned CLI; pinned skills are offered in an Atomic workspace and take precedence over a user copy; they are hidden with a reason in a Git workspace; the in-sandbox CLI's read commands work and `add`, `record` and `view` are refused; a definition edit becomes a proposal while a state edit lands as an agent claim | in progress | Catalog/content ownership is tested, but unchanged upstream commands fail the source-compatibility audit. Five native policy/registry tests demonstrate why general allowlists, missing tokens or copied extensions cannot qualify an ingress. No in-sandbox CLI execution or proposal/claim routing is qualified; see A33. |
| V44 | Triage linkage: a bound turn's changes are never `ORPHAN_CHANGE`; a met criterion without a passing record of each required kind is blocked | not started | |
| V45 | With a record in progress, status, diff and query reads complete within budget | not started | |

## Validation evidence (2026-11-13)

Commands below ran from the monorepo root unless the command begins with `cargo`,
`rustup`, `scripts/` or `python3`: those ran from `packages/intentd`. The workflow lint command also ran there.

| Claim | Command | Result | Artifact |
|---|---|---|---|
| Foundation workspace type checks and pedantic Rust lints | `CARGO_NET_OFFLINE=true make clippy` | Pass at foundation snapshot, full workspace/all native targets, 5m 33s | Superseded by later source edits; not the latest whole-tree gate. Dependency-only existing pprof warnings. |
| Neutral identity, serialization and error contracts | `cargo test -p intent-core --test vcs_contract --offline --locked` | Pass, 7 tests | `crates/intent-core/tests/vcs_contract.rs` and state goldens |
| Git adapter parity | `rustup run 1.96.0 cargo test -p intent-git --lib engine::tests --offline --locked` | Pass, 14 tests | `crates/intent-git/src/engine/tests.rs` |
| Git ref snapshot extraction | `target/debug/deps/intent_git-ab1b304ef83ef63e history::tests` | Pass, 32 tests; exact binary produced by the successful current-tree Cargo test build | `crates/intent-git/src/history.rs` |
| Git submodule path context | `target/debug/deps/intent_git-ab1b304ef83ef63e submodule::tests` | Pass, 16 tests | `crates/intent-git/src/submodule.rs` |
| Existing/shared diff extraction | `target/debug/deps/intent_git-ab1b304ef83ef63e diff::tests` | Pass, 30 tests | `crates/intent-git/src/diff.rs` |
| Service extraction and attribution regressions | `rustup run 1.96.0 cargo test --offline --locked -p intent-services --lib -- file_tracking::tests accept_changes::tests git_ops::tests tracked_changes_sweep::tests agent_locks::tests --test-threads=1` | 84 passed; one newly added test used `./` as an empty-path fixture even though existing normalization retains `.`. Corrected the fixture to an empty string; production behavior unchanged. Targeted rerun: `rustup run 1.96.0 cargo test --offline --locked -p intent-services --lib file_tracking::tests -- --test-threads=1` passed all 3 tests | `crates/intent-services/src/file_tracking.rs` and affected service modules |
| All repository source lints | `CARGO_NET_OFFLINE=true make lint-sources` | Pass, every workspace `*_lint` target, including test registration and the new seam guard | Existing CI discovery glob and current sources |
| No new direct Git mechanics outside the engine | Historical intentd command: scripts/check-vcs-seam.sh | Pass, 6 tests including repository scan | `crates/intent-core/tests/vcs_seam_lint.rs` and per-crate baselines |
| Qualification refuses misleading dependency failures | `python3 -I -B -S scripts/test-atomic-qualify.py` | Pass, 5 tests | Qualification driver and retained report |
| Diagnostic inventory classifies checkout mutations | `python3 -I -B -S scripts/test-gen-vcs-seam-manifest.py` | Pass, 5 tests; two generations identical | Historical intentd artifact scripts/vcs-seam-manifest.tsv |
| New script suites are wired in CI | `python3 -I -B scripts/check-test-scripts-wired.py` | Pass, 75 suites; registration self-tests: 13 passed | `.github/workflows/ci.yml` |
| Workflow syntax and shell lint | `bash scripts/lint-workflows.sh .github/workflows/ci.yml` | Pass with actionlint 1.7.12 and ShellCheck | `.github/workflows/ci.yml` |
| Full prescribed check gate | `CARGO_NET_OFFLINE=true make check` | Blocked at cargo-shear: missing cached `anstyle-wincon` dependency. Normal `cargo shear --deny-warnings` also failed because static.crates.io DNS is unavailable. Format and field parity passed; lints run separately above | Gate output; existing staged-field warnings retained |
| Required changed-tests selection | `CARGO_NET_OFFLINE=true make test-changed` | Refused: correctly selected full suite for build-wide script changes, then callback fixture preflight refused native macOS. No pass claimed | `CONTRIBUTING.md#linux-x64-callback-gates` |
| Service test selection through the supported runner | `CARGO_NET_OFFLINE=true make test-select E='package(intent-services) and (test(/^file_tracking::tests::/) or test(/^accept_changes::tests::/) or test(/^git_ops::tests::/) or test(/^tracked_changes_sweep::tests::/) or test(/^agent_locks::tests::/))'` | Refused before execution by the same Linux-only callback fixture preflight | Filesystem-only native fallback recorded above |

Full frontend/daemon integration, latency budgets and V1 wire parity remain unverified.
No sandbox was started; the sandbox inventory was empty on the final status check. No PR or release was created. The pre-existing off-pin intentd branch and monorepo drift were preserved; no gitlink was staged or reset.

Local checks for the bounded implementation are complete as recorded below. Source activation,
aggregate checkpoints, adoption/rewind, qualified reviewer execution, publication, source
surfaces, pinned skills and rollout remain incomplete. Full gates need a Linux x64 host
with working IPC, effective network containment and uncached dependencies; cross-target
builds and fork ownership remain open. No PR, release or rollout is claimed.

## Continued validation evidence

These later selections supersede the foundation-only numbers for their exact cases; they do
not qualify an entire work item, a later edit or an end-to-end milestone.

| Claim | Exact command (from intentd unless noted) | Result | Limits |
|---|---|---|---|
| Durable evidence/confirmation/read-model/memory/explanation owners | `cargo test --offline --locked -p intent-store --lib -- evidence_ledger::tests candidate_evidence::tests evidence_blob::tests work_confirmation::tests work_assignment::tests work_read_model::tests work_observation::tests memory_repo::tests work_explanation::tests transfer_reimport_tests::imported_ --test-threads=1` |58 passed |The last filter did not select actual transfer tests; work_observation belongs to Services. |
| Real legacy credential completion and imported completion guard | `cargo test --offline -p intent-store --lib -- work_confirmation::tests::immediate_legacy transfer_repo::reimport_tests::imported_ --test-threads=1` |4 passed |Supplemental native fixture-free selection; root lock refreshed after legitimate dev dependency. |
| Admission, pinned prompt, delegation, queries, confirmation, read model, journal, memory, runtime, actual check runner | `cargo test --offline --locked -p intent-services --lib -- work_admission_tests future_size_tests work_delegation::tests search_basis_tests knowledge_ops::tests work_confirmation::tests work_read_model::tests work_observations::tests memory_ops::tests memory_prompt::tests atomic_runtime::tests work_candidate::tests --test-threads=1` |41 passed |5m37s compile;41s test. Later grant/usage edits need fresh checks. |
| Client bounded read concurrency, control serialization, cancellation and generation fences | `cargo test --offline --locked -p intent-atomic-proto -p intent-atomic` |26 passed |23client+3protocol; actual host overlap still separately qualifies. |
| Portable frozen-baseline closure | `CARGO_HOME=<isolated-cache> rustup run 1.98.0 cargo test --manifest-path <absolute-atomic-host-manifest> --offline --locked --lib closures::tests -- --test-threads=1` from `/tmp` |3 passed |Retains exact native objects, deletes original Git/all stores and restores fresh; does not prove full checkpoint aggregate. |
| Catalog golden and read-model router | `INTENTD_UPDATE_GOLDENS=1 cargo test --offline --locked -p intent-transport --lib -- catalog::tests::method_catalog_matches_golden router::work_read_model_tests --test-threads=1` |4 passed |Router tests do not replace actual TLS WSS tests. |
| Protocol method/event docs parity | `node scripts/check-protocol-catalog.mjs`; `node scripts/check-event-catalog.mjs` from monorepo |Pass;14existing docs-lead warnings |Uses dirty/off-pin component checkout, not recorded pin. |

| Additional original-grant and prospective task-source owners | `cargo test --offline --locked -p intent-store --lib -- task_work_definition::tests evidence_ledger::tests::explicit_work work_execution_grant::tests --test-threads=1` |12 passed |9real SQL grant/revoke/drain/ABA cases +3task-source cases. Initial fixture/trigger enum casing corrected to actual serialized WorkspaceStatus. |
| Usage semantics and actual required-kind acceptance | `cargo test --offline --locked -p intent-store --lib -- work_usage::tests work_confirmation::tests::declared_required task_work_definition::tests --test-threads=1` |6 passed |3usage +1each-required-kind actual runner-vs-claim/failed case +2source-shape cases. |
| Fresh physical ACP and original detached context | `cargo test --offline --locked -p intent-acp --lib -- transport::single_prompt::tests detached --test-threads=1` |9 passed |6one-prompt +1required-context restoration +2existing detached cases; no provider/network fixture invoked. |
| Native actual handler/snapshot overlap | Native all-target command using isolated cache/Rust1.98 |36 passed,1same-op preparation test failed,2ignored |4new concurrency cases passed. Failure fixed with actual per-op blocking lease, not test weakening; targeted repeated-preparation test then passed. Full fresh rerun pending. |
| Opaque composition ownership and neutral contracts | `cargo test --offline --locked -p intent-core --test vcs_proof_owner_lint --test vcs_contract` |10 passed |New source lint restricts production proof construction to inspecting Git/Atomic adapters; no service exemption. |
| Real WSS memory/read-model source coverage | `cargo test --offline --locked -p intent-transport --lib -- ws::read_model_tests ws::memory_tests --test-threads=1` |Compiled;2blocked at listener bind EPERM |No WSS behavior pass claimed. Read-model case covers snapshot/transient actual write/durable reconnect/member-vs-outsider once run on a bind-capable host. |
| Latest captured FE push path | Focused Vitest286tests/9files; official verify:changed |Focused pass; official architecture blocked by tsx IPC pipe EPERM |`.dev/verify-changed/attempts/2026-11-13T17-44-08-287Z-80508-93b41d`; separate static8/9 pass. Exact generator succeeds via Node --import tsx. No live p95 timing or full2704file unit pass. |

| Actual private composition, native grants and APFS warm copies | Exact-pin isolated Rust1.98 `cargo test --offline --locked --all-targets` native host |56 active passed (55lib+1main),2ignored |6composition +12capture/grant cases included. Later target-race/hash-NONE/client protocol additions need fresh qualification. |
|20k native file fidelity (debug profile, this sandbox under mixed build load) | Isolated native `cargo test --offline --locked --lib baselines::tests::qualification_twenty_thousand_file_baseline_import_and_materialization -- --ignored --test-threads=1 --nocapture` |Pass; first636.32s: import454.72s/materialize178.44s; after removing redundant scans/grouping directory fsync779.26s: import655.35s/materialize119.51s |No release/p95 budget claim. Second run: assemble0.44s/serialize0.99s/object durable66.49s/native graph inserted647.02s/native files verified649.73s. Native insertion dominates debug time; materialization stayed exact and faster, total variance prevents an overall speedup claim. |
| Actual original runtime retry/model acknowledgement and admission budget | `cargo test --offline --locked -p intent-services --lib -- work_usage_runtime::tests work_admission_tests future_size_tests --test-threads=1` |11 passed |5runtime identity/retry/meta cases +5original admission/prompt/cancel cases +future-size budget. |
| Real service confirmation/completion and prepared planning owner | `cargo test --offline --locked -p intent-services --lib -- work_planning::tests work_execution_grant::tests work_confirmation::tests work_usage_runtime::tests --test-threads=1` |11 passed at that source snapshot |7confirmation/completion +1missing original execution grant +1human planning CAS +2initial runtime parser cases. Later card wrapper/newusage cases qualified separately. |
| Exact remote condition and non-force ancestry prerequisite | `cargo test --offline --locked -p intent-git --lib -- native_push::tests --test-threads=1` |4 passed |Actual local Git graph/callback guard tests; no network push or cross-forge A25 qualification. |

## Later local checks and unresolved integration

All commands in this section ran from `packages/intentd`, except native commands
which ran from `/tmp` with the isolated native Cargo home and absolute manifest.
These results qualify the selected cases at execution time, not subsequent edits.

| Claim | Command | Result | Limits |
|---|---|---|---|
| Original definition, lifecycle completion CAS, SQL grants, read-model recovery, review and usage storage | `cargo test --offline --locked -p intent-store --lib -- evidence_ledger::tests work_confirmation::tests task_native_binding::tests work_read_model::tests work_usage::tests work_review::tests work_execution_grant::tests --test-threads=1` |62 passed |Before the final lifecycle-after-offer regression and explicit shared-working-copy provenance changes. |
| Actual one-prompt cwd/session fencing and detached required scope | `cargo test --offline --locked -p intent-acp --lib -- transport::single_prompt::tests one_prompt_prepared_cwd_is_frozen detached --test-threads=1` |12 passed |Includes original cwd and actual session/new response checks; no provider/network fixture. |
| Current client/protocol contracts | `cargo test --offline --locked -p intent-atomic-proto -p intent-atomic` |31 passed:26 client+5 protocol |Actual process IPC remains blocked; not a positive end-to-end execution-grant qualification. |
| Full local native library | `rustup run 1.98.0 cargo test --manifest-path /Users/oliverbeavers/CodeRepositories/intent/packages/intentd/atomic-host/Cargo.toml --offline --locked --lib -- --test-threads=1` |87 passed/3 ignored;128.90s test |Includes9 composition,8 adapted grants,4 triage and3 signing cases. Before subsequent provider-free vault route changes. The ignored cases are the separately run20k qualification and two subprocess entry points invoked by active parents. |
| Original native grant, exact current control and native report/signing batch | Same isolated native command with `-- execution_grants::tests intents::control_export::tests triage::tests signing::tests --test-threads=1` |18 passed |Before provider-free vault route changes. Exact original source remains distinct from native verdict and signing identity. |
| Actual Services owners | `cargo test --offline --locked -p intent-services --lib -- work_candidate::tests vcs_ops::tests work_review::tests work_usage_runtime::tests work_confirmation::tests work_admission_tests future_size_tests work_execution_grant::tests codex_session_title::tests --test-threads=1` |36 passed/5 failed; rerun required |New composition fixtures omitted their required existing spool directory; service wiring fixture omitted caller context. Fixtures corrected without relaxing production guards. Later original-record governance and grant-producer edits remain ungated. |

The source audit found that a shared Git recorder receipt establishes the original
recording request's governance, not all possible authors of its bytes. Actual
production auto-commit retention and explicit unknown authorship are now connected;
manually retained fixture receipts cannot bypass this distinction. Native authoring,
adoption/rewind, aggregate checkpoints, qualified reviewer execution, publication,
source UI, pinned skills and rollout remain unfinished. No PR, merge or shipped
release is claimed.

## Stabilized local selections

| Scope | Exact command (intentd cwd unless noted) | Result | Remaining limit |
|---|---|---|---|
| Storage owners | `cargo test --offline --locked -p intent-store --lib -- evidence_ledger::tests candidate_evidence::tests evidence_blob::tests work_confirmation::tests task_native_binding::tests work_read_model::tests work_usage::tests work_review::tests work_execution_grant::tests work_explanation::tests memory_repo::tests work_assignment::tests task_work_definition::tests --test-threads=1` |93 passed |Selected native fixture-free cases, not full prescribed Linux gate. |
| Actual Services and original Git settlement | `cargo test --offline --locked -p intent-services --lib -- auto_commit::tests work_delegation::tests vcs_ops::tests work_review::tests work_usage_runtime::tests work_confirmation::tests work_admission_tests future_size_tests work_candidate::tests work_execution_grant codex_session_title::tests work_read_model::tests --test-threads=1` |95 passed |Includes legacy auto-commit regressions and five new actual settlement cases; no enabled native provider workflow. |
| Git mechanics, private composition, lock and transport preconditions | `cargo test --offline --locked -p intent-git --lib -- engine::tests engine::recording::tests engine::composition::tests provisioning::tests native_push::tests --test-threads=1` |45 passed |Unix local graph/checkout corpus; no GitHub/GitLab push or cross-platform qualification. |
| Client and private wire contracts | `cargo test --offline --locked -p intent-atomic-proto -p intent-atomic` |32 passed |26 client+6 protocol, including unchanged boxed-payload wire shapes. No real process IPC pass. |
| Current native library | Credential-scrubbed exact-pin native `cargo test --offline --locked --lib -- --test-threads=1` as in host README |89 passed/4 ignored |Inherited external-provider configuration is refused. Earlier unsanitized run63 passed/26 refused; this is an environment-policy result, not an egress qualification. |
| Latest vault/guard/native signing changes | Same native command with `-- triage:: signing::tests intents::control_export::tests embedding_policy::tests every_ambient_provider_refuses --test-threads=1` |13 passed |Exact four-default bounded profile; unknown control entries and canonical Memory spines refuse. |
| Latest native composition/closure after wire-preserving enum changes | Same native command with `-- composition::tests closures::tests --test-threads=1` |12 passed |Private composition and portable baseline component only. |
| Native all-target pedantic lint | Credential-scrubbed exact-pin native `cargo clippy --offline --locked --all-targets -- -D warnings` |Pass |Only installed native target; cross-target build and contained process gates remain open. |
| Latest runner lease, journal queue/drain and typed memory opt-in | `cargo test --offline --locked -p intent-services --lib -- work_candidate::tests work_observations::tests memory_ops::tests memory_prompt::tests --test-threads=1` |20 passed |Includes actual runner exclusion until owner drop; no process IPC/provider source activation. |
| Actual router/catalog ownership and bounded snapshot routing | `cargo test --offline --locked -p intent-transport --lib -- catalog::tests router::work_read_model_tests --test-threads=1` |36 passed |Corrected table ordering only; router method inventory, allowlist membership and payload budgets preserved. Actual WSS listener remains blocked. |
| Repository source lints | `CARGO_NET_OFFLINE=true make lint-sources` from monorepo |Pass, all discovered workspace source-lint targets |Includes the original-origin, spawn, journal, typed proof, deadline, source-registration and VCS seam guards; no new baseline exemptions. |
| Required whole-tree check | `CARGO_NET_OFFLINE=true make check` from monorepo |Blocked at uncached `anstyle-wincon v3.0.11` |Format, target references and field parity passed;12 existing field/pin warnings. No full check pass claimed. |

Whole-workspace/all-target native Clippy passes on the stabilized source with
`CARGO_NET_OFFLINE=true make clippy` (2m54s); only pre-existing dependency warnings
from vendored pprof remain. Source lints and focused lifetime/router checks pass
as recorded above. Real Unix socket/TCP listeners, containment,
the Linux x64 callback fixture, signed/cross-target builds, performance and rollout
remain blocked or unmeasured. No sandbox/listener was started; final status preserved
the pre-existing off-pin intentd HEAD and monorepo protocol-doc drift. No gitlink was
staged or reset.

## Source workflow checkpoint validation (2026-11-14)

This is the shared confirmation/apply/recovery substrate on **Git**, not qualification of
live Atomic workspaces. All changes are local/uncommitted; no PR or release exists.
Commands run from `packages/intentd`. Saved attempt receipts/logs are under
`/tmp/intent-atomic-validation/`; the observations below do not depend on a still-live terminal.

| Claim | Exact command | Observed result | Scope / remaining check |
|---|---|---|---|
| Initial adoption contract and constructor ownership | `cargo test --offline --locked -p intent-core --test vcs_contract --test vcs_proof_owner_lint --test vcs_seam_lint` |17 passed |Before the additional known-CAS progress carrier; final source lint rerun required. |
| Actual Git effects, preimage retention, stale capture, replay and shared path locks | `cargo test --offline --locked -p intent-git --lib -- engine::adoption::tests engine::composition::tests worktree::tests --test-threads=1` |35 passed |Initial capture/progress snapshot. Later known-CAS and parent-symlink hardening require a fresh run; this is not Atomic activation. |
| ACP writes retain actual admission after waiter cancellation; response waits for change publication | `cargo test --offline --locked -p intent-acp --lib -- fs::tests write_response_waits_for_file_changed_publish write_then_read_round_trip_fires_file_changed --test-threads=1` |6 passed; Services/Store library integration compiled |`source-owner-integration-compile-20261114`; actual filesystem effects, no socket/provider fixture. |
| Immutable runtime custody, legacy-session migration, Store confirmation, read-model generation and transfer decisions | `cargo test --offline --locked -p intent-store --lib -- work_confirmation:: source_runtime_custody::tests work_read_model::tests every_live_table_has_an_explicit_transfer_decision --test-threads=1` |41 passed,1 failed |Transfer inventory correctly found15 older new tables without a declared fate. Added explicit source-retained exclusions; fresh run including the additional cross-workspace binding case remains required. Structural historical Store witnesses do not qualify a review/execution producer. |
| Broader source workflow and writer-owner regressions | `cargo test --offline --locked -p intent-services --lib -- work_confirmation::tests work_candidate::tests work_source_writes::tests work_admission_tests work_provisioning::tests vcs_ops::tests attachment_upload::source_write_tests checkout_transfer::source_write_tests repo_config::tests repo_config::source_write_tests future_size_tests --test-threads=1` |Not green yet |Initial compile caught a nonexistent test timeout helper; next run caught four test-future borrow lifetimes. Both corrected without weakening production guards. Fresh `services-source-adoption-fixed-20261114` attempt is compiling; no runtime pass claimed. A disconnected earlier command has an unobserved final exit and is not counted as a pass. |
| Formatting and patch whitespace | `cargo fmt --all --check`; `git diff --check` in monorepo and intentd |Pass at current checkpoint |Later safety-fix edits still need final format/lint verification. No staged gitlinks. |

Read-only review found that the initial target observer could follow a symlinked parent
before dirty-target refusal. The new source-capture boundary is being corrected and a real
negative regression is required before closing this slice. No public source route is enabled.
Native process/containment and Linux callback qualification remain blocked on this host;
full Atomic execution, independent reviewer execution, UI, publication, checkpoints and
rollout remain incomplete.

### Atomic-specific handoff boundary

IPC permission is not the only missing piece. `AtomicWorkspaceEngine` is still a
construction-only implementation with empty capabilities and unsupported authoritative
operations; main selects Git. The host command enum dispatches baseline/closure, private
composition, derived reads and read grants, but does not dispatch the native task
projection/freeze, working-copy register/capture, exact recording or triage library APIs.
Those local library tests do not establish a daemon-to-host-to-provider workflow.

The next bounded Atomic-specific implementation slice is typed host dispatch/client ownership
for those existing primitives, with immutable command identity and replay tests, followed by
manager-owned admission/recording/settlement. Aggregate format-2 checkpoints, qualified complete
authorship and read-only review producers, Atomic application/rewind/fork and their product
surfaces remain missing. Independent review cannot be enabled merely by granting Unix IPC.
Activation must still wait for the plan's required runtime/containment qualification.

Fresh local environment audit reconfirmed AF_UNIX and TCP loopback binds fail with EPERM.
Docker29.1.2 exists, but access to its selected local daemon socket is denied; cached Linux
images and architecture could not be inspected. Other checked local Linux runtimes were
unavailable. No VM/service, installation, alternate endpoint or privilege bypass was used.

Parallel non-Cargo checks passed57 protocol/event-script tests and5 manifest tests, including
the missing `vcs.subscribe`/`work.subscribe` routing classification fix. Catalog parity passed
with14 existing docs-lead warnings; the iOS event check was skipped because its submodule is
uninitialized. Read-only readiness review found no normal UI/help promotion, source mutation
route or Atomic-to-Git fallback. This is a source review, not runtime qualification.

Known separate boundary: legacy transfer checkpoint pathname reads still need the same safe
reader or an explicit qualification refusal. The new source-capture fix does not qualify that
older transfer path. Its follow-up is not silently included in the new source gate's passes.

### Settled local validation (2026-11-14)

These observations supersede the intermediate failures above for the final bounded slice.
`COMPACT=1` uses the repository's existing `scripts/resumable_nextest.py --compact-cargo`
profile helper; it does not bypass or qualify the Linux callback fixture. Filesystem-only
unit selections are supplemental native checks. The full prescribed suite still refused.

| Claim | Exact command / attempt | Final observation | Limit |
|---|---|---|---|
| Git application, composition and worktree ownership | `COMPACT=1 python3 ../../scripts/resumable_nextest.py --compact-cargo cargo test --offline --locked -p intent-git --lib -- engine::adoption::tests engine::composition::tests worktree::tests --test-threads=1` |40 passed, `git-source-final-20261114` |Includes11 actual adoption cases: permission modes, known-CAS progress, parent-symlink/FIFO races and no-reapply recovery. Does not qualify Atomic application. |
| Service confirmation and counted writer ownership | Same compact helper, `cargo test --offline --locked -p intent-services --lib -- work_confirmation:: work_candidate::tests work_source_writes::tests work_admission_tests work_provisioning::tests vcs_ops::tests attachment_upload::source_write_tests checkout_transfer::source_write_tests repo_config::tests repo_config::source_write_tests future_size_tests work_read_model::tests --test-threads=1` |73 passed, `services-source-confirmed-20261114` |All prior failures corrected: exact internal wake adapter, authenticated attachment fixtures, explicit private operation directories and required rejection reasons. No source-readiness check weakened. |
| Store proof, uncertainty, completion and transfer inventory | Current binary from the successful compact three-package `cargo test --offline --locked --no-run -p intent-services -p intent-store -p intent-git --lib` build; `target/debug/deps/intent_store-4d325ab64e1d073d work_confirmation:: source_runtime_custody::tests work_read_model::tests every_live_table_has_an_explicit_transfer_decision --test-threads=1` |43 passed, `store-source-final-20261114` |Historical structural witnesses exercise Store mechanics; no qualified authorship/reviewer producer is implied. |
| Full workspace native target type/lint gate | `CARGO_NET_OFFLINE=true make clippy` from monorepo |Pass, `workspace-clippy-settled-20261114` |5m08s; existing dependency-only pprof warnings. |
| All discovered repository source-lint targets | `CARGO_NET_OFFLINE=true make lint-sources` from monorepo |Pass, all25 targets, `source-lints-20261114` |Includes proof constructor ownership, VCS seam, source discovery, egress, test registration and timeout rules. No baseline expansion. |
| Neutral serialization/error contracts | Same compact helper, `cargo test --offline --locked -p intent-core --test vcs_contract` |7 passed, `vcs-contract-final-20261114` |No process/runtime qualification. |
| Required whole check | `CARGO_NET_OFFLINE=true make check` from monorepo |Blocked, `required-check-20261114` |Format and field parity pass;12 existing parity warnings. Cargo shear cannot download uncached `anstyle-wincon v3.0.11` offline. Not a check-gate pass. |
| Required changed-tests gate | `CARGO_NET_OFFLINE=true make test-changed` from monorepo |Refused before test execution, `required-changed-tests-20261114` |Correctly selected full suite; native macOS cannot run the verified Linux x64 callback fixture. No fake fixture or unsupported gate bypass. |

The staged Docker qualification recipe is available locally and uncommitted at
packages/intentd/scripts/atomic-linux-qualification/README.md (absent from the pinned checkout). It records the exact staged
source, immutable image identity, architecture/emulation, commands, exits and log hashes.
Only image/dependency preparation permits network; native checks run offline with no
privilege/socket/home mounts. Every successful phase requires both a successful process exit
and a passed report. Static checks, staging smoke and aggregate-result regressions passed;
Docker itself has not been executed from this denied session. The user confirmed their normal
Terminal's Docker daemon is `linux/aarch64`; Linux amd64 execution will be emulated and is not
performance evidence. The recipe is native-host-only; root callback qualification remains
separate. Live Atomic activation remains off and the missing implementation list above still
applies even if this recipe passes.

The user started the manual Docker attempt at `2026-11-14T15:57:11Z`, with retained
evidence in `/Users/oliverbeavers/atomic-linux-evidence-20261114T155711Z`.
At `16:36:51Z`, the saved logs showed that image construction and dependency fetch
had passed and the Linux x86_64 GNU release build had finished successfully in
`34m 07s` at `16:33:17Z`. Default-profile test compilation was actively progressing;
runtime, IPC and containment results were still pending. This is a partial build
observation, not a completed qualification. The original recipe's outer report stays
`unavailable` while a phase is running, so the live command log and artifact timestamps
are needed to distinguish progress from a completed refusal. Preserve this attempt's
source, recipe, evidence and Cargo cache while it is running.

The next runner revision now streams compiler/test output, prints a 15-second
phase/subcommand heartbeat and records running/terminal UTC timestamps. New-format
sessions retain separate attempt receipts and support resume with frozen
source/recipe/image checks, exclusive ownership, prior-container absence checks,
matching archived driver/context and verified command logs/cache artifacts.
Rerunning a prerequisite invalidates every later phase receipt. The original
November 14 attempt has no version-2 session receipt and is deliberately refused
by `--resume` before writes or Docker calls; its current build continues unchanged.

Python syntax, shell syntax and eight independent mock-Docker execution cases
passed: phase output, nonzero Docker exit despite a passed inner report, legacy
refusal without mutation, concurrent-run exclusion, preserved source/recipe/prior
attempts, unverified-driver reexecution, dependent reexecution after an artifact
changes, and changed-source refusal. Focused independent review found no remaining
concrete blocker. These fixtures start no containers and provide no Linux runtime
qualification. At `16:48:05Z`, the original attempt was still compiling default-profile
tests, with fresh OpenSSL object files; runtime/IPC/containment results remained pending.

### Completed manual Linux Docker evidence (2026-11-14)

The original attempt finished at `2026-11-14T16:57:49Z` (11:57 a.m. New York), after
approximately 61 minutes. This final observation supersedes the running observations
above. The user's command was the documented `run.sh --output` invocation, with output
`/Users/oliverbeavers/atomic-linux-evidence-20261114T155711Z`.

| Claim | Retained command/log | Result | Limit |
|---|---|---|---|
| Actual host release build | `evidence/build/release-host.log`, exact argv in its phase report | Passed; 34m07s; GNU x86_64 ELF verified | Emulated amd64, not native performance evidence. |
| Default-profile test compilation | `evidence/build/compile-all-default-tests.log` | Passed; 18m11s | Compilation alone executes no tests. |
| Native library and binary tests | `evidence/runtime/native-library-and-binary.log` | 90 library + 1 binary passed, 4 ignored, 0 failed | Default-profile standalone host tests; root callback suite excluded. |
| Actual daemon-client process/IPC | `evidence/runtime/actual-ipc-process.log` | 1 passed, 0 failed | Exercises capture/composition without source mutation; not live Atomic activation. |
| Independent OS containment control | `evidence/contained-host/network-denial-control.log` | Unavailable; helper/container exit 2 | Bubblewrap reported no permission to create a namespace. Contained handlers never ran. |
| Overall native-host qualification | `evidence/report.json` | `unavailable` | Fetch/build/runtime passed with zero container exits; containment did not pass. |

Independent read-only verification matched all 18 referenced command/control log hashes,
all 259 staged source files and the aggregate inventory hash, all five recipe hashes,
the four saved phase reports and the retained release ELF/hash. Release binary:
49,768,480 bytes, SHA256
`3ebcbc33f386b70c51d7c4880743b9d51f66591b1f04ba2807d5cb363fdd6d5c`.
The source snapshot remains the originally recorded `8c28413b...e734e4e`; all evidence
and Cargo cache are preserved. No privileged or uncontained retry was attempted.
These are reported test counts, not positive qualification of every platform capability:
some copy-on-write/grant fixtures accept an explicit unsupported-filesystem refusal.

The next full qualification needs a Linux execution environment that can actually
perform the required unprivileged namespace operation. The existing build/cache and
passing runtime evidence need no repeat merely to acknowledge this environment refusal.
The AI session still cannot access the local Docker socket. A fresh `make status` attempt
also refused before execution because no per-worktree development port block was free;
no services or port allocations were changed.

The future runner now checks the same bounded OS denial control immediately after
image verification and before dependency fetch or compilation, including on resume.
It uses the same restricted container policy and frozen containment helpers. This
preflight does not qualify native execution or replace any of the four required
phases. A nonzero Docker exit, unavailable report or failed control returns unavailable
before Cargo. Ten mock-Docker execution cases now pass, including early namespace
refusal and a nonzero preflight Docker exit despite a passed inner report; Python and
embedded-control syntax checks and independent policy review passed. No new real Docker
run was attempted, and the completed original output was not changed.
