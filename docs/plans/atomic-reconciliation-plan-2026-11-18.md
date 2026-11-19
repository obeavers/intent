# Atomic reconciliation and integration plan

Audit date: 18 November 2026 (New York). Read alongside the
[T1–T5 governing plan](atomic-substrate-adoption-2026-11-12.md),
[tracer specification](atomic-bullet-tracer-2026-11-15.md) and
[implementation handoff](atomic-substrate-handoff-2026-11-15.md).

## Decision

Preserve all existing work, then port reviewed slices onto current main. The present
feature branches are development checkpoints, not merge-ready implementations. A merge
of their commits alone would omit most implementation; copying their working trees
over main would restore obsolete database, runtime and frontend code.

Reconcile the foundations required by T1 first, then implement its three existing
tickets: controller, explicit task/query association and report. Keep every later
capability accounted for, without making the first real tracer depend on completing
native writing, every frontend surface or all platform releases.

This audit changes documentation only. No source was committed, pushed or merged; no
branch was rebased or reset. Atomic remains disabled for ordinary source-authority use.
The accompanying [file inventory](atomic-reconciliation-inventory-2026-11-18.json)
records source identities and worker dispositions. **An inventory is not a backup:**
checkpointing the actual changed bytes is the first execution step below.

## Verified source state

Counts expand untracked directories into files. They describe the source state before
the two new reconciliation documents; the component-pointer entries are included in
the root count. Nothing is staged in any of these working trees.

| Repository | Branch / HEAD | Behind live main | Branch-only commits | Dirty entries |
|---|---|---:|---:|---:|
| intent | docs/atomic-substrate / d4849072 | 361 | 1 | 24: 16 tracked, 8 untracked |
| intentd | feat/atomic-substrate / df549124 | 185 | 1 | 451: 127 tracked, 324 untracked |
| cloudlands-fe | feat/atomic-substrate / 050e969d | 224 | 0 | 134: 52 tracked, 82 untracked |

There are **609 dirty repository entries** in the aggregate checkout, including two
submodule pointers: 607 ordinary file entries. The root's sole commit contains the
older plans/reviews/status; the adopted T1–T5 update is still dirty. The daemon's sole
commit classifies direct Git calls. The frontend has no unique implementation commit.
The historical validation receipts therefore cannot be recovered by checking out HEAD.

Live GitHub refs were verified separately from local cached origin/main:

| Repository | Cached origin/main | Live main |
|---|---|---|
| intent | 8ae32c472054f8d8113babe46a9ba1c0f0db4ce2 | 394a60e3a320c4fc85f60de3c440b4b9b3b5d0e7 |
| intentd | 2980938757eb5c3b4f0282ee39080604252fa2de | 10e1c3dbc671bcb19ebd4d08201e366c1c696fd8 |
| cloudlands-fe | 8a368f6319a08ad3962a6490a594d0411878f220 | 8a368f6319a08ad3962a6490a594d0411878f220 |

Live root main pins daemon 2980938 and frontend 8a368f6. The backend's newest commit
has not reached that root pin. Refresh these exact refs before starting integration;
do not treat cached branch names or this dated table as permanently current.

### Work outside the aggregate checkout

Six registered worker worktrees contain **242 additional dirty entries** and two
commits absent from the aggregate's history. Counts are file versions in separate
trees, not 242 distinct new features. No stashes were found.

| Worker under the sibling intent-wt directory | HEAD | Dirty | Disposition |
|---|---|---:|---|
| intentd-v1 / wave1/v1 | d421971 | 193 | Recover candidate: 191 JSON compatibility goldens, coverage document and real UDS harness absent from aggregate and cached main. |
| intentd-w01 / wave1/w01 | 6092196 | 3 | Older host skeleton; preserve original spike/build evidence, compare with expanded aggregate host. |
| intentd-w02 / wave1/w02 | df54912 | 0 | Covered: same committed HEAD as aggregate. |
| intentd-w03 / wave1/w03 | d421971 | 16 | Older alternative VCS decomposition; compare semantic/test cases before retiring it. |
| intentd-w08 / wave1/w08 | bdf3db8 | 2 | Alternative blob/outbox implementation and competing migration; preserve useful tests, do not overlay it. |
| fe-w38 / wave1/w38 | 050e969 | 28 | Alternative paint/latency instrumentation; compare missing cases with aggregate instrumentation in T5. |

Unique worker commits are 60921969d1a0cbad49a6f2f56559dc811302730d and
bdf3db83b62eb9ed38f3c59117d2002a79b872a2. Their ancestry is not evidence their
functionality is missing: the aggregate has newer alternative implementations.

The V1 harness is a valuable recovery candidate: 1,522 lines exercise 41 dispatched
methods through composed Services and a Unix-domain socket. Three forge/native-review
methods have error-path coverage only. Preserve the existing fixture hashes, establish
their original-baseline provenance, and compare against main before porting the harness.
Discovery does not make V1 green. Do not regenerate expected outputs from the changed
implementation and call that a compatibility test.

## Actual integration risks

A read-only three-way text probe compared each overlapping working file with its
merge-base and cached-main blobs using git merge-file. It did not modify any checkout.
This is narrower than a merge: it excludes the newer remote commits and cannot detect
API, schema, routing or lifecycle incompatibilities.

| Repository | Paths changed locally and on cached main | Text-conflict paths |
|---|---:|---:|
| Root | 8, including two gitlinks | 1 ordinary file |
| Daemon | 55 | 6 |
| Frontend | 20 | 9 |

There are no same-path collisions between aggregate untracked files and new files on
cached main. That does not imply the additions compile against main.

| Risk | Concrete finding | Required resolution |
|---|---|---|
| Migration identity | Local SQLite migrations 0191–0209; main already uses 0191–0196 for workspace-home. Six version collisions despite different filenames. | Allocate new versions after then-current main; preserve main's migration bytes. If all 19 local migrations landed together at this snapshot, the mapping would be 0191–0209 → 0197–0215. T1 may need fewer, so this is not a reservation. |
| Storage abstraction | Main now has Backend::{Sqlite,Postgres}, SqliteStore and dispatch wrappers. New evidence modules use the old Store/raw-pool layout. | Port storage methods intentionally, retaining tenant boundaries and write ownership. Specify backend support or an approved explicit refusal for each added operation; do not introduce a silent fallback. |
| Production build | Latest daemon main restricts raw read_pool/write_pool APIs to tests/test-support and guards the release feature graph. | Keep production storage behind the new Store API. Do not enable test-support in production to make compilation pass. |
| Runtime ownership | Main added a per-agent resource registry, turn-start/retirement/archive ordering fixes and workspace-home lifecycle. | Reconcile admissions and evidence capture into that lifecycle; preserve main's cleanup/order fixes. |
| Transport dispatch | Main split the router by namespace and added push/workspace-home routing. | Add methods to current handlers and routing policies, rather than replacing the old router wholesale. |
| Frontend integration | Main added machine-frame routing, push and workspace-home support, and removed desktop Browser access. | Keep current lifecycle/IPC/store integration and port feature hunks into it. Do not resurrect removed paths. |
| Build metadata | Main has newer Cargo dependencies, release metadata and frontend 2.353.2; the feature tree is older. | Retain current versions and toolchain/check layout; regenerate lockfiles from intentional dependency changes. |
| Fixture provenance | Both local event-recovery fixture locks identify unmerged root commit d484907. | Export both mirrors from the same merged root-main commit containing the canonical bytes. Squash merging does not preserve that feature-commit ancestry. |

Backend text-conflict paths are the e2e test map, attachment_upload.rs, Store lib.rs,
agent_repo.rs, note_repo.rs and the transport router. Root's is the method catalog.
Frontend's are the eight locale JSON files and shared/types.ts. Other shared hubs can
merge textually while remaining semantically incompatible; in particular, the Store
and runtime changes above are more significant than the conflict count.

Locale edits have no overlapping changed keys: local adds/changes 130 keys per locale,
main 205. Merge by key using main's locale tooling; retain main's files and new keys.

## Execution order and review batches

These are proposed **hunk-level extraction boundaries**, not a claim that today's files
are already independently buildable. Some large evidence/client modules import later
features. Resolve their dependency closure, compile and review each slice before moving
it forward. Prefer several coherent batches over either a giant patch or one PR per file.

| Batch | Deliverable | Dependency / exit gate |
|---|---|---|
| C0 — checkpoint and baseline | Checkpoint aggregate and all worker bytes, unique commits, original goldens and receipts; create isolated current-main integration branches. | Complete recoverable source capture and verified inventories. No stash/reset/clean or submodule checkout in the original trees. |
| R1 — governing docs | Final T1–T5 plan, reviews, handoff/status/receipts, coverage map/checker and this reconciliation record. | Clean root-main docs checks; omit dirty gitlinks. Can prepare independently. |
| R2 — additive protocol | Contracts needed by extracted batches, retaining main's namespaces, methods/events/errors and fixture registry. | Consumer checks against current pins; additions land before consumers. Can share a root PR with R1 if review stays clear. |
| B1 — Git and identity foundation | Core VCS/knowledge DTOs and rooted intent-git adapters required by the normal Git contribution/query path. Recover applicable V1 tests. | Ordinary Git behavior and authority preserved; current-main compile/lints and meaningful compatibility checks pass. |
| B2 — original task and evidence | Minimum root binding, confirmed task revision/admission, contribution identity and retained original-run evidence. Port the necessary schema and Store methods. | Depends on shared identities. Fresh DB, old-schema/current-main upgrades, original-task fencing, retention/transfer and backend-policy checks. |
| B3 — inert recorded-code host | Standalone pinned host, protocol/client and actual prepare/query lane for immutable Git snapshots. | DTO contract agreed with B1; can develop alongside B2. Host opt-in, normal startup inert, actual transport/query tests on an admitted platform. |
| B4 — Git runtime integration | Join normal Git agent admission/contribution recording with B2 evidence and the current agent resource/lifecycle implementation. | B1/B2 plus relevant contract additions; no duplicate run/contribution, source drift refused, ordinary Git regression checks. |
| T1 — connected tracer | Existing controller/association/report tickets using B3/B4; retain observed test results and query basis, then exercise restart. | Real provider, real fixed test, real host query and durable reopen; exact acceptance below. |
| R3 — tracer entry point | Root developer command and final usage docs. | Backend implementation merged and included in automatic root pin. Do not land a command that calls unavailable code. |

B1–B4 need not become exactly four PRs. Combine only where compilation or review makes
that clearer. In particular, do not import the full evidence ledger and all native
modules just to avoid extracting a small root-binding dependency for T1.

### Preserve first, integrate in isolation

1. Record full HEAD/base/main identities, index state, source hashes and unique worker
   commits. Capture tracked diffs including intent-to-add additions, untracked bytes,
   modes/symlinks and deletions for every tree. Include original goldens and historical
   receipts. Check actual source payloads back against the inventory; a root commit
   never captures dirty submodule content. Keep a second recoverable source copy before
   changing any source branch.
2. Make explicitly labeled checkpoint commits/refs in each component and worker, or
   an equivalent verified source archive plus commit bundles. Checkpoints are recovery
   artifacts, not product merge candidates. Preserve competing worker versions until
   their tests/findings have an explicit disposition.
3. Fetch and pin then-current main in all three repos. Create separate integration
   branches/worktrees; leave these existing dirty trees available for comparison. Use
   a permitted workspace location and normal Git operations; do not change filesystem
   protection rules to do this.
4. Run a clean-main baseline on the intended test profile, then apply scoped source
   deltas to it. For each batch record source checkpoint, extracted hunks, omitted
   dependencies, resolved conflicts and exact gate results. Keep main's architecture,
   release versions and unrelated fixes.
5. Resolve migration allocation and the backend contract before integrating schema
   consumers. For old experimental databases that applied local 0191–0209, preserve or
   export them and use fresh disposable fixtures; do not edit applied migration checksums
   or point an integration build at a user's installed database.
6. Open reviewable component PRs as their batches pass. Prepare frontend PRs in parallel
   where useful, but merge any frontend consuming new methods only after its daemon
   contract is merged. Request the repository's service review. Actual PR merges/queue
   admission still require explicit human authorization under repository policy.
7. Let auto/submodule-bump advance root pins. Verify pin inclusion before R3 or any
   dependent root command. Do not include today's dirty gitlinks in an ordinary docs PR.

### Root-specific corrections

- Recompute the method catalog from the integrated implementation. Cached main has
  505 dispatchable / 451 router methods; the stale feature table starts at 502 / 448
  and adds nine. If all nine are retained, the current-main result is 514 / 460, not
  511 / 457. T1's narrower extraction may expose fewer; derive the final count.
- Re-export both event-recovery mirrors and locks from one shared merged root SHA.
  The canonical fixture bytes are unchanged across this root branch and cached main.
  sameSourceAcrossComponents requires matching provenance, not just equal JSON bytes.
  Registering the not-yet-adopted frontend copy can land first; adoption follows the
  shared commit and component order.
- In the first docs PR, describe the historical daemon seam-manifest path as branch
  evidence rather than a live tracked-component link: current pins do not contain it.
  Check docs with current pinned components, not just the dirty feature checkout.

## What T1 needs, and what it proves

Existing Services prepare_recorded_code/query_recorded_code operations have no
production caller. They resolve the server-selected committed Git source. The tracer
must hold the fixture at the recorded contribution, prepare that source and verify the
returned identity; it cannot silently attach a later HEAD to the original task.

The query read basis truthfully remains ImportedGitSnapshot with task_revision None.
Implement an **Intent-owned retained association** between original task/run,
contribution, test observation and query/import basis. Match repository, root, epoch,
commit and tree; do not pretend this is native Atomic task-intent linkage. Existing
evidence DTOs do not yet carry that query association.

The first outcome gate is the existing fixed scenario:

1. Confirm a real task and run one actual configured provider through the normal Git
   path. It changes only src/fees.js so feeCents(1234,500) rounds to 62.
2. Retain the actual Git contribution and require exactly that changed path. Execute
   the unchanged fixed test against the recorded commit and retain its actual result,
   log identity and source identity. A model's statement that a test passed is insufficient.
3. Query the actual Atomic derived index and require a positive hit identifying the
   corrected recorded content. Retain the explicit association and inspectable report.
4. Add an uncommitted sentinel and verify the recorded query excludes it. Restart
   Services and host with retained data, explicitly prepare the same commit again,
   and verify the same durable generation/source/lineage without another agent run or
   duplicate contribution. The client prepared-index map is process-local; reprepare
   is required.

Use supported native macOS ARM64 with an explicit pinned host on an execution profile
that allows real IPC/provider access. Linux ARM64 qualification helpers exist, but
the Services runtime platform gate still rejects Linux aarch64. An executable override
does not fix that. Qualifying native-writing confinement on Linux belongs to T2;
it is not a prerequisite for this Git-authoritative T1 on a supported platform.

T1 does not prove native writing, independent review, source adoption, publication,
multi-agent composition, performance or ordinary Atomic workspace readiness.

## Disposition of all remaining work

The existing 361-definition coverage map remains authoritative. No original requirement
is removed or marked complete by this audit. File areas in the inventory identify where
source must be reconciled; they do not establish review approval or product readiness.

| Preserved scope | Integration destination | Specific boundary |
|---|---|---|
| Native process custody, isolated ACP, working allocation, selection, checkpoints, record/recovery | T2 stack after B1/B2/B3 and current lifecycle reconciliation | Positive Linux execution, bootstrap/selection controller and provider-compatible resources remain unqualified. Keep activation off. |
| Review, confirmation receipts/cards, adoption and rewind | T3 | No qualified ordinary independent reviewer/adoption path. Confirmation UI has no production confirmationCard/decide service ports yet. |
| Parallel children, composition, conflict/read models, tools and memory extensions | T4 and assigned T5 gates | Preserve original-source and captured-connection fences; no generic metadata may waive custody checks. |
| Confirmed planning and original-run evidence frontend | Separate FE planning/evidence PRs after daemon contracts | Shared DTO/client prerequisites; keep exact revision and late-allocation behavior, bounded original first-admission history. UI need not block T1. |
| Neutral frontend DTOs/transport/read models | FE foundation PR | Leaf memory client and confirmation-card DTO imports may be needed even while those controls remain dormant. |
| Experimental memory panel | Separate opt-in FE/backend increment | Explicit experimentalMemoryRead capability only; no default activation or learning/mutation claim. |
| Host artifact packaging, skills, platform/release matrix, latency/pilot | T5 and later gates | Actual artifact contract and platform tests first. Raw pinned skill workflow is incompatible/inactive; qualification-tool unit passes are not runtime qualification. |
| Worker host/blob/VCS alternatives | Preserved checkpoint plus semantic/test comparison | Record useful cases as ported, superseded with reason, or still pending. Never blindly overlay competing implementations or migrations. |
| Worker latency alternatives and aggregate instrumentation | W38/T5 | Reconcile measurement/paint cases into one instrumentation approach; no performance qualification from source presence. |
| Incremental publication and eventual Git conversion/retirement | POST W36/W37 | Original pilot, migration and retirement gates remain binding. |

For frontend integration, use separate review groups for neutral contracts, planning,
evidence, confirmation, experimental memory, latency diagnostics and host packaging.
Give shared AppClient/live client, Redux registry, IPC and locale hubs one integration
owner. Keep current machine-frame routing, push, workspace-home, provider model IPC
and main/renderer/preload type-check structure. Do not copy older package metadata or
removed Browser access wiring from the feature tree.

## Parallel ownership and gates

Four productive lanes can run after C0: contracts/docs plus the recovered compatibility
harness; Git/runtime adapters; storage/schema and original task evidence; host/query
transport. Their small shared contracts should be agreed first. One integrator owns
each shared hub and lockfile. Frontend preparation and worker comparison can run in
separate trees, but broad new capability construction stays off the active T1 queue.

| Owner | Shared conflict surface | Required evidence |
|---|---|---|
| Storage | Store dispatch/backend modules, migration numbering, transfer/retention | Fresh DB; schema-190 and current-main upgrades; backend/tenant/write-lock lints; original-task, replay and export exclusions; release feature graph. |
| Runtime/Git | Services lib/agent manager/retirement and resource registry | Ordinary Git regressions; admission/cancellation/ABA; actual contribution capture; compatibility fixture results and explicit unsupported cases. |
| Contracts | Core types, namespace router/catalog/hello/events; root docs | Current consumer/catalog/DTO checks, node/remote routing and missing-capability refusal. |
| Host/build | Protocol/client/host, manifests/locks and payload definitions | Pinned source, isolated workspace, warnings denied; actual recorded Git import/query/reopen on a supported profile. |
| Frontend | Client/IPC/reducer/saga/locale hubs | Current main's type checks, capability and retirement tests, planning/evidence tests and actual Electron smoke before release. |

Use the repository's prescribed changed-tests selection and required checks for each
integrated slice. Manifest/lock changes can select the full suite. Historical focused
passes are regression assets, not waivers. Do not widen coverage claims from mocked
tool tests, policy tests, compile-only probes or an older Docker source snapshot.

The integration environment needs allowed IPC and provider access for T1, and an
authorized Linux x64 profile for the repository's pinned full callback fixture suite.
This audit did not retry restricted sockets/Docker or run expensive old-tree builds.
There is no defensible runtime estimate until the first current-main extraction
compiles and the real T1 attempt identifies its failing seam. Track progress by merged
and gated batches, then the reproducible tracer outcome, rather than aggregate test
counts or a guessed percentage.

## Immediate queue

1. C0: preserve aggregate plus six worker trees, especially the missing V1 suite.
2. Establish current-main baseline and assign storage/runtime/contract/host owners.
3. Prepare R1/R2 and B1/B2/B3 in parallel with agreed minimum T1 contracts.
4. Join B4, then finish the existing three T1 tickets and obtain the real report/restart
   result. Complete component review/authorized merges and automatic pins per batch.
5. Resume T2–T5 using the existing delivery map; close each worker disposition as its
   useful code/tests are integrated or superseded with evidence.

This reconciliation work precedes the existing T1 tickets. It does not activate more
product tickets or change the governing plan's safety, qualification or retirement gates.

## Audit verification

- Recomputed all aggregate statuses, merge bases, branch-only commits and cached-main
  overlap; checked live-main divergence through GitHub and inspected its newest backend
  commit. Inspected registered worker worktrees, unique commits and stash metadata.
- Verified all 861 inventoried ordinary file versions against their current SHA-256
  hashes, including worker versions. Gitlinks are recorded separately. These hashes
  identify the captured bytes; they do not retain the payloads themselves.
- The existing delivery checker passes with all 361 definitions retained, and its 26
  tests pass. The reconciliation does not alter the protected requirement definitions.
- Documentation links pass, with six existing unverifiable references skipped; root
  git diff --check passes. These checks use the present feature checkout, not a fresh
  main integration tree, so the current-pin docs caveat above still applies.
- No implementation build, runtime test, source merge or product qualification was
  performed in this analysis. Historical validation remains labeled separately.
