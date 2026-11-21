# Latest upstream reconciliation — 20 November 2026

The continuation baseline now includes the following captured upstream snapshots
alongside the prepared Atomic implementation. These are a fixed integration
cutoff; upstream may continue advancing while qualification runs. The aggregate
commit's gitlinks identify the exact reconciled component revisions.

| Repository | Captured upstream main | Incoming commits incorporated |
| --- | --- | --- |
| intent | 5f6899efce6f18d02e2b03326da243c3e3a9f9a5 | 93 |
| intentd | 38e858ae594938510bb7da08a621df2a630b9efe | 45 |
| cloudlands-fe | 9041a12f56be47a4b3749a56dca786468d26c744 | 59 |

The backend now uses the upstream 0.11.261 baseline, and the frontend uses
2.361.4. The prepared task evidence, Atomic host staging, capability gates,
frontend controls and all 130 Atomic keys in each locale are retained. Incoming
passkey staging and upstream locale values are also retained. Original dirty
source trees remain preserved; this refresh does not import the deferred older
experimental backend graph or close later stages of the governing plan.

Upstream's Postgres migration 0008_tenant_writer.sql remains unchanged. The
unpublished tracer migration is now 0009_tracer_evidence.sql, byte-identical to
its prior contents; SQLite remains 0197. Evidence reads use the upstream
repeatable-read snapshot API, and mutations retain its typed tenant writer lock.
The compatibility harness received lint cleanup without changing any of its
191 expected JSON files or assertions. The combined protocol catalog now counts
517 dispatchable names, comprising 462 router and 55 fast-path methods, plus six
reverse RPC names; the nine prepared Atomic additions remain gated.

The root merge at 43677965 passed all 20 consumer checks against backend
0911ec439b0eac3a550902b4631422784731dde3 and frontend
55a341ba833abb9c3211447606aa6d760dae6625. Later backend follow-ups change only
the isolated host lock metadata and compatibility test-harness linting. The final
pin check and publication receipt are retained with this refresh's evidence.

Selected validation during this refresh:

- All 361 protected definitions and 26 mutation tests pass. Plans, delivery-map
  requirements and canonical event-stream contract are unchanged.
- Root helper selection and runner tests pass: 81 passed and 14 skipped, using a
  canonical temporary-directory path to avoid macOS /var aliases. Callback tests
  add six passes and 24 Linux-only skips. Consumer isolation and fork pin helper
  checks pass under Bash 5 and stock Bash 3.2; the changed workflow passes actionlint.
- The backend Store ledger passes 11 tests at 0911ec4. Postgres source checks pass
  29 and five tests, and PgStore units pass nine at 911fc65. Their production and
  Store source is unchanged by the later lockfile/harness-only follow-ups.
- Final backend 27e1957 passes locked, offline, all-target workspace Clippy with
  both atomic-tracer and intent-store/postgres features and warnings denied.
- Frontend 55a341b passes 1,159 tests across all 40 changed unit-test files, plus
  formatting, ESLint, package-script checks, knip, Svelte checking with zero errors,
  renderer TypeScript and canonical fixture checks.

The broader gates are not green. The initial root script selection was stopped
with exit 130 after failures; a receipt-selection test bug was reproduced on
pristine upstream, as were macOS canonical-path comparison failures. The unchanged
Linux OS source in install-ci-bash3.sh also trips ShellCheck SC1091 on this Mac.
The canonical Rust changed-test selector chooses the full suite, whose actual
attempt exits 2 because the descriptor-pinned callback fixture requires Linux
x64. No fixture bypass was used.

Frontend static and changed verification timed out at 360 and 600 seconds during
main TypeScript without compiler diagnostics. Architecture checks also hit the
existing tsx IPC denial, and workflow lint retains the two unchanged SC2329
findings. Main/preload TypeScript, test-type baselines, the full unit/component
suite and Electron/WSS acceptance remain unqualified for this cohort. Live
Postgres, real provider/native-host T1 execution, broader platform qualification
and normal Atomic activation remain open.

Refresh receipts, exact command exits and pristine-upstream comparisons are under
.reconciliation/evidence/upstream-refresh-20261120 in the original workspace.
Earlier sections below retain their own source identities and validation limits;
their 0008 tracer migration and older main references are historical.

---

> Current integration direction — own forks' main branches (19 November 2026)
>
> The implementation baseline is obeavers/intent, obeavers/intentd and
> obeavers/cloudlands-fe. Upstream contribution is outside this consolidation.
> The user clarified that these forks' main branches should contain the work so
> the restructured plan can continue. Earlier unpublished/main-merge restrictions
> below are dated history; the runtime, qualification and release gates remain.

The protocol merge is caff6599ea9090a976df0dc041642f7f07e3b504 in
obeavers/intent main. Component main now includes backend
85e5348ef1c053c864546f3c01beacfac37847eb and frontend
bed06ac2a33ff47546044d3828ca5d2e6da2115c. This aggregate consolidation pins those
exact commits and routes its public submodules to those same forks. Active
integration clones use the own fork as origin and retain intent-hq as upstream;
the original dirty checkout and its worker source remain preserved.

The newer backend main's Postgres migration 0007_delete_purge.sql is preserved.
The unpublished tracer migration is now 0008_tracer_evidence.sql; SQLite remains
0197. A new Store test checks that original task/admission evidence survives the
new workspace-deletion path. Fork consumer checks and notifications now use the
own aggregate repository. Immutable upstream fixture provenance and existing
release-owner guards remain unchanged; no workflow activation or deployment is
part of consolidation.

Current selected checks include Store ledger 11, Postgres-feature units 13,
Store Postgres-enabled strict Clippy, production opt-in CLI typechecking, metadata
14 + 32, backend native-routing 68, frontend focused tests 152 and workflow-policy
10. The pin readiness helper resolves the fork owner and passes its existing
Bash suites. The consumer isolation fixture now supplies trusted Python as well
as Node, preserving the two Atomic guards and all existing Node assertions.
Recorded older binary hashes and broader validation cohorts below retain their
original source identity; they are not relabeled as new qualification.

The backend event-stream recovery fixture now adopts the already merged canonical
source ae48c764 with its truthful upstream repository provenance. Only the fixture's
top-level shipped-static-examples annotation and its lock metadata changed; all 31
scenarios, 9 request-validation cases and 191 V1 JSON expectations are unchanged.
Both consumers now lock the same canonical source. The canonical 8 Node tests and
strict verification of both copies pass.

Final aggregate verification passes all 20 consumer checks against these own-fork
component commits, including the repaired shared fixture parity. The delivery-map
guard retains all 361 definitions, and its 26 mutation tests pass. The trusted
interpreter fixture and fork pin helper pass on Bash 5 and stock Bash 3.2; the
changed root workflow passes actionlint. These are local integration receipts,
not a claim that full CI, live Postgres or actual provider execution passed.

Full release-script/workflow gates retain recorded inherited or environment
failures. Full real-provider T1 acceptance still requires an execution profile
that permits local IPC; live Postgres and the other transport/platform gates are
open. Consolidating the code into development main does not qualify T1, activate
ordinary Atomic source authority or close T2–T5/POST. All 361 protected definitions
remain assigned in the delivery map. Final remote-main verification and current
check receipts are recorded in the own-fork consolidation receipt.

---

# Atomic reconciliation execution journal — 19 November 2026

This is the current execution record for the [reconciliation plan](atomic-reconciliation-plan-2026-11-18.md),
the [T1–T5 governing plan](atomic-substrate-adoption-2026-11-12.md) and the
[first tracer specification](atomic-bullet-tracer-2026-11-15.md). It supersedes earlier
handoff summaries for current integration status, while retaining their historical
receipts and all 361 protected definitions in the [delivery map](atomic-substrate-delivery-map.json).

**Current boundary:** source reconciliation and the real developer tracer implementation
are locally committed in the backend; its worktree is clean. The CLI builds and
its help command succeeds. Audited newer main has been merged into the local root
integration branch; fresh root consumer gates pass. Component refresh receipts are
recorded separately below. The actual attempted run failed before provider admission
because this profile denies the native host's Unix socket bind. There is no
qualified T1 pass, merge into GitHub main, publication,
installed-database migration or ordinary Atomic source-authority activation.

## Source preservation and working locations

The original aggregate checkout remains at /Users/oliverbeavers/CodeRepositories/intent.
The original dirty feature branches and six worker trees remain preserved. Active
integration uses three independent clones below that checkout's .reconciliation/integration:
intent, intentd and cloudlands-fe. They are not replacement checkouts of the original
submodules. Do not reset, clean, stash or repoint the original trees to resume this work.

Paths beginning .reconciliation in this journal refer to the original aggregate
checkout, which owns the shared evidence and build artifacts. These local receipts
are separate from the source committed in the integration clones.

| Checkpoint | Verified preservation | Meaning |
|---|---|---|
| .reconciliation/checkpoints/20261119T035821Z | Nine source trees; 864 file versions; 128 refs; three independently restored bundles with full fsck and original shallow boundaries | Preserves the original aggregate and worker source, indexes, binary diffs, modes, symlinks and deletions. Supersedes the earlier 035616Z attempt. |
| .reconciliation/checkpoints/20261119T135127Z-integration | Three integration trees; 585 file versions; 839 refs; three independently restored bundles with full fsck and original shallow boundaries | Newly preserves the integrated source, including all 31 then-pending backend entries and 16 dirty root entries. Verified 2026-11-19T13:53:39.951740Z. |
| .reconciliation/checkpoints/20261119T142137Z-pre-main-refresh | Three integration trees; 588 file versions; 842 refs; three independently restored bundles with full fsck and original shallow boundaries | Preserves root 6644cc5c, backend bf136549, frontend 39c25a96a and pending journal bytes before fresh-main reconciliation. Independently verified 2026-11-19T14:23:07.937278Z; original Git/source state unchanged. |

The integration checkpoint contains root 43c81c67214f0ff647e67d09ed63f402668e07a4
(28 file versions), daemon a4c518739ccbf8ce732bd713628230f864341f0b
(419 file versions) and frontend 39c25a96abcc5093384e47954d400ecb90c9d8b5
(138 file versions). Its manifest SHA256 is
54d95b95adfc5028c8db559001399d968f204dc34b112466ab02ed11445dd5da.
Receipt: .reconciliation/evidence/reconnect-integration-checkpoint.json;
inventory: .reconciliation/evidence/reconnect-integration-source-inventory.json.
The later pre-refresh checkpoint has manifest SHA256
fb6e3538f6726682487171383e8c676b3050b4b0329bb3778603f73b186cac6e;
receipt .reconciliation/evidence/reconnect-pre-main-refresh-integration-checkpoint.json.
Subsequent edits require a later commit or checkpoint; this dated snapshot does not
claim to contain future changes. C0 is green for source preservation only.

The reusable checkpoint tool is scripts/checkpoint-atomic-reconciliation.py. Its
RESTORE.md and manifest describe recovery into a new directory without touching the
original checkout. Verification of a checkpoint uses:

```sh
python3 scripts/checkpoint-atomic-reconciliation.py --verify-existing \
  /Users/oliverbeavers/CodeRepositories/intent/.reconciliation/checkpoints/20261119T135127Z-integration
```

## Pre-refresh local integration checkpoint

All three integration clones use integrate/atomic-t1. These source identities and
test cohorts precede the newer-main refresh. At that checkpoint, root gitlinks
were main's daemon eade125 / frontend f4a8646 pins. No experimental component
commit was manually pinned.

| Repository | Integration baseline | Local committed slices | Remaining local source |
|---|---|---|---|
| intent | ae48c76413d68e8c63a3e517e2be23b50453dd1c | 43c81c67 additive Atomic protocol contracts, also retained on integrate/atomic-contracts; 6644cc5c governing plan, complete requirement map, reconciliation tooling and documentation | R1 is locally committed at 6644cc5c7fd7abc5ba3f22f774666bd291d3af09, with a clean tree before this journal follow-up. All 20 root consumer checks pass; component gitlinks remain unchanged. |
| intentd | 643f8621c9587f58536a53ebdaab1b4046236473 | 13dbb7a rooted Git contracts/compatibility fixtures; f9e81c3 inert native host/query client; a4c5187 paired Store ledger; 2d0e4cb B4/T1 Services/admission/recording/transport/CLI; bf13654 strict source-lint conventions | Clean at bf136549d4a83785ab3e7f34a649f2be8013078d. B4 commit 2d0e4cbe5c5b156a4933c5b75874aed20e49af97 contains 32 files / 5291 insertions / 47 deletions. Final affected tests, transport refusals, selected all-target strict Clippy, all 68 core/Services/daemon source-lint tests and delivery CLI build/help pass for this dated baseline. Real T1 acceptance is blocked. |
| cloudlands-fe | f4a8646408491d6ecb13384c0da0ad83474f3d38 | 39c25a96a reconciles gated Atomic workflows with version 2.355.0 main | Clean after this local commit; full application/platform acceptance remains open. |

## Fresh audited main reconciliation

A later remote audit found that all three main branches had advanced. These are
the explicit observed heads for the refresh, not moving branch-name assumptions:

| Repository | Audited main SHA | Local reconciliation / fresh acceptance |
|---|---|---|
| intent | c23e0f33dfbc75b74bb27c04ba2562fc7df8cc56 | New integrate/atomic-contracts-current branch from this main, R2 cherry-pick 482f578564b8c22e62848782260622d4487d3fa5. Merged into integrate/atomic-t1 as 1f4c6c8d516100045c4f4bed3e0c3e83af3d7398, preserving old R2/R1 history. Fresh consumer checks: 20/20 pass; guard retains 361 definitions; 26 mutation and 32 doc-link regression tests pass. |
| intentd | fae6ba19f6912834197f3a465dd284e315eb150d | Local merge 7c64774174009c22ffc5d4c0f45198d6eaacc983 preserves new Postgres registry/writers/rollback and tracer access. Test-only SQL-check classification fix 90fc2914bc83d737750b4ad67c09abebb49ac69e preserves production SQL and negative fixtures. Clean follow-up e4a019ba8d3f543fb27df2d42ecea7fd0a6d6a87 boxes the clone-progress EventBus field to satisfy the Postgres-enabled enum size. Six selected T1 cohorts pass at their recorded source; final Postgres-enabled four-package strict Clippy, clone 35/future-size 1 units and CLI build/help pass at e4a019ba. |
| cloudlands-fe | e850e80f52ea38737a6c698f501a607f57ca272e | Local merge d9a7a3b incorporates audited main. Clean follow-up bfa864f4f320e9c40035c06aeb7c96e6080a5610 fixes 14 integration-owned test files. Production TypeScript, both test-type baselines, 216 focused runtime tests and final lint/format checks pass; full static still fails at preload generation's denied tsx IPC listen. |

Before the refresh, root journal bytes were committed as c05754ac. The old
integrate/atomic-contracts branch and original root/source history remain intact.
The new contracts branch has its own worktree at
.reconciliation/integration/intent-contracts-current; it contains the additive R2
contracts without the R1 planning slice.

Root's new main contributed updated KEYBINDINGS documentation and upstream
component-pin bumps. The merge inherited exactly fae6ba19/e850e80f gitlinks from
audited main. Only after each pristine root-clone component checkout was confirmed
clean was it moved to its exact inherited pin. No experimental gitlink was chosen;
the original aggregate's Git/index and component checkouts were not touched.
Root was clean after that synchronization. Fresh logs:
.reconciliation/logs/reconnect-root-consumer-checks-current-main.log and
reconnect-root-plan-current-main.log.

The later pre-refresh validation table retains backend/frontend cohorts as dated
evidence. It does not promote them into fresh-main acceptance. The completed fresh
component receipts below identify their actual refreshed commits.

Fresh backend metadata gates already pass: 14 version-group tests, 32 release
fast-path tests, and offline/locked Cargo metadata for the daemon and independent
Rust 1.98 host. Workspace, Atomic client and protocol crate versions align at 252;
the host lock adjustment changes three local versions only. This metadata evidence
is narrower than the completed selected T1, Store/Postgres unit, all-target strict
Clippy and final CLI build checks below. The frontend's refreshed type/focused
runtime passes remain separate from its dated full-fallback failure and its
current IPC-blocked generation checks.

| Fresh component gate | Actual result / source | Boundary |
|---|---|---|
| Selected T1 backend | Six Cargo cohorts / 31 tests passed with exit 0 at 7c647741: recording 5, admission 2, planning 6, tracer 13, future size 1, transport refusals 4. Receipt .reconciliation/evidence/reconnect-refreshed-focused-tests.json records commands, source identities and timestamps. | Not the full Services or transport suites; later EventBus source changes require their appropriate checks. |
| Store/Postgres units | T1 Store 10 and Postgres-enabled units 13 pass. Clean-source Postgres receipt .reconciliation/evidence/current-main-sealed-postgres-units.json identifies 90fc2914. | No Postgres runtime/service was available; these units do not substitute for live paired-backend execution. |
| Refreshed native host | Actual binary build exited 0 in 207s. Provider-free child-environment library run exited 0: 140 passed, 4 ignored, in 127s. Receipt .reconciliation/evidence/fresh-main-host-validation.json proves its relevant host source/closure unchanged between 7c647741 and 90fc2914. | Raw ambient-environment run separately failed: 99 passed / 41 guard refusals / 4 ignored. That failed cohort and its environment distinction remain retained. Neither library result is real T1 acceptance or containment qualification. |
| Final backend strict | Clean e4a019ba passes cargo clippy -p intent-store -p intent-services -p intent-transport -p intentd --all-targets --features atomic-tracer,intent-store/postgres --offline -- -D warnings: exit 0 in 176.9s. Receipt .reconciliation/evidence/current-main-pg-final-strict-clippy.json. The clone-progress EventBus box resolves the enum-size warning without changing upstream Postgres behavior. | Postgres parity targets are typechecked; no real database execution or full-workspace runtime-gate claim. |
| Final Postgres-enabled clone/future units | Clean e4a019ba: deterministic clone 35/35 passed (319.81s compile/run command, 0.03s tests); future_size 1/1 passed in 1.15s. Complete exit-0 receipts current-main-pg-final-{clone-units,future-size}.json and aggregate .reconciliation/evidence/current-main-pg-final-validation.json. | Completes the affected boxed-EventBus/stack-size checks with Postgres enabled. These units do not require or claim a running Postgres database. |
| Refreshed normal CLI | On clean e4a019ba, the opt-in normal CLI build exited 0 in 155.18s and --help exited 0 in 1.54s; source HEAD/status stayed unchanged. Receipts .reconciliation/evidence/current-main-normal-cli-{build,help}.json; aggregate current-main-normal-cli-validation.json. | Build/help proof only. No actual full scenario was run with this newly built binary. |
| Refreshed frontend types/static | Clean bfa864f4 passes production renderer/main/preload TypeScript, main unit-type baseline (zero new errors), renderer unit-type baseline (zero new errors; 2547 historical errors across 532 files; baseline bytes unchanged), final Prettier/ESLint and diff checks. The 14 test-only fixes resolve all 38 new errors and the captured audit-saga expectation. Focused runtime tests: 216 across 14 files (UI 14 / three files, transport/registry 96 / five, stores 106 / six). Receipt .reconciliation/evidence/fresh-main-fe-test-fixes-commit.json. | Full static still fails solely at generated-preload's tsx IPC listen (EPERM); the separate design-cheatsheet check is also blocked by that IPC restriction. No bypass or fabricated pass. Focused tests are not full-suite/CT/Electron/WSS acceptance. |

The refreshed host binary SHA256 is
09148f8fca9f4966f523c29b2b07513a6b2d867531e4341374cb6f63868660e1
and remained unchanged throughout its recorded tests. It has not replaced the host
identity in the earlier actual failed-run receipts; those attempts retain their
own source/artifact identities.

The newest normal developer CLI is now at
packages/intentd/target/debug/atomic-tracer under the original aggregate checkout
(a generated build artifact, not an edit to the original component source). Its
SHA256 is 5bada4c925955261f395bd0585282b3648a40de0d02607edad2b338f47ed254b,
259443776 bytes, from clean refreshed backend e4a019ba. The older private-target
artifacts below retain their dated build identities and actual-attempt receipts.

No GitHub push, PR or merge has occurred. An attempted push was rejected by automatic
approval review because source export to GitHub lacked explicit authorization. A
reconnection is not publication approval. Continue local implementation and review;
do not retry publication through another route. Root/component main integration and
the normal component-pin workflow remain later operations.

## What was reconciled and what still needs adaptation

| Slice | Current implementation | Boundary |
|---|---|---|
| B1: core/Git and compatibility source | Typed VCS/work/knowledge contracts, rooted Git operations and fixture bootstrap; recovered the V1 worker's 191 original JSON goldens, coverage document and real 1,522-line UDS harness. | JSON expected outputs were retained. The harness was subsequently formatted; not all 193 current files are byte-identical. Original-baseline provenance and real compatibility execution remain open. |
| B2: minimum Store | SQLite migration 0197 and paired Postgres 0007; work_t1_evidence and work_t1_agent_fence; immutable original TaskRevision, atomic confirmed-agent insertion, first admission, cancellation/replay, Git contribution and blob references; main's root-incarnation counter rejects ABA. | This is the minimum T1 ledger, not the old 19-migration relational graph. Later native/review/memory modules must adapt to it or supply reviewed migrations. Old SQL references to task_revision/work_binding tables cannot be copied unchanged. Evidence/fences are excluded from transfer. Real Postgres execution remains unrun. |
| B3: host/query | Independent Rust 1.98 host pinned to Atomic bf9893adb57dccbaa8f7e14277e02d060d74bf53, protocol 3; inert supervision/client and actual recorded Git import/query closure. | Normal startup remains inactive. Admitted runtime targets are macOS ARM64/x64 and Linux x64 GNU/musl. Linux aarch64 is not runtime-qualified by helper tooling or earlier x64 Docker receipts. |
| B4: real source admission and recording | Locally committed in 2d0e4cb/bf13654 and retained through the fresh-main merge/follow-ups above. Retains the exact task source before provider admission; original private idle-event carrier; physical Git effect observed before awaiting; finite settlement ownership preserves receipts through cancellation; retained replay refuses duplicate commits. | Selected recording/admission/tracer, transport-refusal, Postgres-enabled clone/future tests and four-package all-target strict Clippy pass at their recorded source identities. Actual tracer acceptance and broader full-suite/platform gates remain open. Older artifacts and incomplete historical test runs are diagnostic evidence only. |
| T1 controller, association and report | Guarded new output directories; held directory/database identity; normal app composition and MCP bridge; one actual configured provider, fixed fees fixture, real Node test against the recorded commit, positive native query, dirty sentinel exclusion, restart/reprepare and no duplicate admission/contribution. | Actual provider/host acceptance has not passed. Services must become idle before reopen. The feature is explicitly opt-in and absent from ordinary CLI builds. |
| Task-planning transport | No taskPlanning wire capability is advertised. Any present expectedTaskRevision, including null, is refused before allocation; stale agentId rejection keeps priority. | Six planning and four transport-refusal tests pass. This does not advertise an unfinished capability or establish broader platform acceptance. |

The T1 fixture requires feeCents(1234,500) to equal 62, changes only src/fees.js and
retains the fixed test/package. Its association is owned by Intent. Atomic truthfully
returns ImportedGitSnapshot with no native TaskRevision. Test observations do not
become independent-check receipts, native task linkage, exclusive authorship,
adoption, automatic completion or publication evidence.

All original W/A/V requirements remain assigned across T1–T5/POST. C0 preservation
and a T1 subset do not close whole W items. Native writing, adoption/rewind,
independent review, memory/knowledge, publication, product surfaces and rollout still
require their assigned implementation and qualification.

## Pre-refresh builds, actual attempts and diagnosis

The actual opt-in CLI build passed in 2m41s, and the build after the report-footer
fix passed in approximately 23 seconds:

```sh
cargo build -p intentd --features atomic-tracer --bin atomic-tracer
```

The first build used the isolated Cargo home and target directory recorded in
.reconciliation/evidence/reconnect-cli-build.json and its .log. Its binary SHA256 was
6215642a107d438b44fc3f84c30ed88a5f67d69245750b2589aea42bc7314847
(259448064 bytes). All 419 daemon source file versions matched the pre-build
integration checkpoint; its --help exited 0.

The intermediate built artifact after the footer fix had path
.reconciliation/build/tracer-cli-target/debug/atomic-tracer, SHA256
3d112e8f0c02634b55115f73047811e5f49301f8df2bc7a59f632c940f33cdaa
(259448032 bytes). Its source manifest SHA256 is
33ec1f66d05e33a7e8b75cb87286f97f1547e5a67fe922375bc50cd0a6f79ea3.
All 2849 recorded source file versions were unchanged during build and verification.
Build and --help both exited 0; receipts/logs are
.reconciliation/evidence/reconnect-cli-final-{build,help}.{json,log}.

The final delivery build from clean committed backend bf136549 also passed, in
approximately 22 seconds, and its --help exited 0. The binary at the same build
path now has SHA256
adc1bfdb8fe9738ae2fb58dd4d74042b609522a93c880e8174fc77b0580bf1ee
(259448032 bytes). All 2850 source file versions remained unchanged, with source
manifest SHA256 a25144ec8face77f936c54cc60179938759d30d577d015f73faa445c5f2de408.
Receipts/logs: .reconciliation/evidence/reconnect-cli-delivery-{build,help}.{json,log}.
This artifact was built after the nonsemantic lint corrections; no real scenario
was run with it. The retained real attempts below used their own earlier recorded
source/binary cohorts and remain failed.

The latest actual configured-provider/native-host attempt used the intermediate
footer-fixed binary with SHA256 3d112e8f… and this command:

```sh
/Users/oliverbeavers/CodeRepositories/intent/.reconciliation/build/tracer-cli-target/debug/atomic-tracer \
  --directory /private/tmp/iat-20261119T140440Z \
  --host /Users/oliverbeavers/CodeRepositories/intent/.reconciliation/build/atomic-host/debug/intent-atomic-host \
  --provider codex
```

It exited 1 after approximately 0.25 seconds, before host readiness or provider
admission. Its retained report has outcome failed, no completed phases and
qualifiedRealT1Pass false. The association and retained association are absent;
the corrected setup-failure footer truthfully reports that absence. Evidence is in
.reconciliation/evidence/reconnect-cli-final-run-20261119T140440Z (receipt.json,
report.json, report.md and run.log). The original failed 13:57:22Z attempt remains
retained separately in reconnect-cli-run-20261119T135722Z, with its historical
summary reconnect-cli-run-latest.json. The unchanged host binary SHA256 is
0dd9a9c72c4bdc32006fc1115108112b6379a7b1109db093637b1cd694eaad90.

A separate normal foreground startup, retaining the same supervised owner-lock
descriptor contract, confirmed the exact cause: “bind private host IPC socket:
Operation not permitted (os error 1).” The process exited 1 and was reaped;
no containment bypass was used. Receipt/log:
.reconciliation/evidence/reconnect-native-host-startup.{json,log}.
The first failed report contained an unconditional association-footer claim. The
formatter was corrected, rebuilt and exercised by the second actual attempt:
setupFooterVerified is true and claimsAssociationBlob is false. This source fix
does not turn either attempted run into a pass.

## Pre-refresh validation ledger

These are separate cohorts and dated receipts, not a sum of unique tests or a
single sealed end-to-end acceptance run. Earlier evidence retains its source/hash
caveats; later edits require checks appropriate to those edits.

| Gate | Actual result / evidence | Limit |
|---|---|---|
| B1 core/Git | 65 passed: VCS 7, knowledge 2, engine 50, fixture 2, proof-owner lint 4. Receipt .reconciliation/evidence/b1-validation.json. | Separate cohorts; recovered compatibility harness itself remains unqualified. |
| B3 native host | Library 140 passed / 4 ignored, including five real recorded-code cases; all-target Clippy with warnings denied passed; packaging helper 8 passed. | No ordinary native source-authority or Linux aarch64 runtime qualification. |
| Client/protocol | 62 + 9 passed. | Library contract evidence. |
| B2 Store | T1 10, blobs 9, work-definition 2, transfer 1; Postgres SQL/writer-lock 18 and schema/tenant 4; strict all-target Clippy including postgres passed. Receipt .reconciliation/evidence/store-validation.json. | INTENT_STORE_TEST_PG_URL absent: no real Postgres runtime pass. Paired tenant test is present/typechecked. |
| Version-group metadata | 11 passed. | Focused integration cohort. |
| Root plan | All 361 definitions retained; mutation suite 26 passed. | Traceability only; no completion inference. |
| Root consumer checks | Initial all-20 pass against pristine eade125/f4a8646 pins; fresh-main rerun also exits 0 with all 20 passing against fae6ba19/e850e80f. Logs .reconciliation/logs/reconnect-root-consumer-checks.log and reconnect-root-consumer-checks-current-main.log. | Fresh root checks use upstream main's exact pins, not experimental component branches; no runtime qualification. |
| Frontend | Renderer/main/preload TypeScript, Svelte zero errors, knip, main-test type baseline, localization and package-script checks passed; focused lifecycle and captured IPC-audit cohorts passed separately. | Full fallback run failed and was terminated, exit 130. Six failures were observed: two integration defects were fixed/retested; four environment process/warning probes remain. No full-suite, CT, Electron or WSS acceptance claim. |
| Current tracer Services | cargo test -p intent-services --lib atomic_tracer --offline --message-format=short -- --test-threads=1: 13 passed before the footer fix, 13 after it and 13 in the final-source affected rerun. Final log .reconciliation/logs/reconnect-tracer-source-final.log; complete exit-0 receipt .reconciliation/evidence/reconnect-final-source-tests.json. | Repeated cohorts are not additive acceptance. Final run includes the corrected footer, scaled helper and bf13654 test-module organization. |
| Historical recording execution | Prior log compiled in 5m19s, began 64 tests and retained only a partial pass list; no final result. | Not a cohort pass. Old process/session identifiers are stale after reconnection. |
| Older-artifact diagnosis | Five original_recording and two work_admission tests passed individually on the older already-built artifact. Logs .reconciliation/logs/reconnect-older-artifact-{original-recording,work-admission}-diagnostic.log. | Diagnostic only; not final-source acceptance or completion of the interrupted 64-test run. |
| Fresh B4/planning/future size | Bounded Cargo runs exited 0 with original_recording 5, work_admission 2, work_planning 6 and future_size 1 passed. Final-source affected reruns again pass recording 5 and admission 2. Commands/log hashes: .reconciliation/evidence/reconnect-focused-tests.json and reconnect-final-source-tests.json. | Telemetry-disabled runs have complete exit receipts. They are separate/repeated cohorts, not broad suite acceptance. |
| Broader auto_commit rerun | Its output reached 64 passed in 28.47 seconds, but the runner's completion polling was rejected after unexpected PostHog telemetry appeared. | No complete runner exit receipt; retain this partial log as diagnostic evidence rather than promote it to qualification. The narrower recording rerun above has a complete exit-0 receipt. |
| Fresh transport refusals | cargo test -p intent-transport --lib task_planning_rejection --offline --message-format=short -- --test-threads=1 exited 0: four passed. Log .reconciliation/logs/reconnect-planning-rejection.log and focused-test receipt. | Focused negative-route evidence. |
| Core source lints | Four source-lint targets passed: fixed_deadline_lint 17, full_literal_lint 19, test_helper_track_caller_lint 16, test_target_registration_lint 6. Receipt .reconciliation/evidence/reconnect-final-core-source-lints.json. | Exact command and complete exit-0 receipt retained. |
| Services source lints | Provider-spawn and note-write path suites passed: seven tests. Receipt .reconciliation/evidence/reconnect-final-services-source-lints.json and its .log. | Complete exit-0 receipt retained; no provider was admitted by these static checks. |
| Final strict Clippy | cargo clippy -p intent-services -p intent-transport -p intentd --all-targets --features atomic-tracer --offline --message-format=short -- -D warnings exited 0 in 3m03s. Log .reconciliation/logs/reconnect-services-cli-clippy-final.log. | Checks selected package targets and their dependency closure, not an independently run full workspace gate. Four existing vendored pprof warnings remain dependency warnings; selected application targets pass with warnings denied. |
| Final delivery CLI | Final committed-source build and help both exited 0, with 2850 file hashes unchanged. Receipts .reconciliation/evidence/reconnect-cli-delivery-{build,help}.json. | No real-run claim for this binary; earlier actual attempts failed before provider admission. |
| Daemon caller-binding source lint | Daemon caller-binding suite passed: three tests, completing all 68 selected core/Services/daemon source-lint tests for the pre-refresh source. | Completes that dated local source-lint cohort, not acceptance against subsequently advanced main. |
| Real T1 | Actual binary and host attempt failed before provider admission as recorded above. | Must rerun on an admitted execution profile with permitted local IPC and ordinary provider prerequisites. |

## R1 documentation provenance correction

The earlier root documentation gate failed on ten source-reference occurrences
that do not exist at pristine current component pins. Inspection confirmed six
planned implementation locations and four historical feature-source evidence
references. They had been formatted as current-checkout source paths. The retained
failure receipt is /tmp/atomic-root-doc-links.log. Its original file/line positions
are below; new status notices shift subsequent line numbers.

| Document | Receipt line(s) | Missing reference |
|---|---|---|
| atomic-substrate-adoption-2026-11-12.md | 343, 1423 | scripts/check-vcs-seam.sh |
| atomic-substrate-status.md | 308 | scripts/atomic-qualify.py |
| atomic-substrate-status.md | 355, 414 | scripts/check-vcs-seam.sh |
| atomic-substrate-status.md | 416 | scripts/vcs-seam-manifest.tsv |
| atomic-vcs-replacement-2026-11-12.md | 526, 1389, 1770, 1827 | scripts/check-vcs-seam.sh |

The correction scopes planned scripts as planned intentd locations, and historical
scripts/artifacts as original feature-source evidence retained by the nine-tree
checkpoint. Their literal script names, requirements, command text, results and
counts are retained as prose; they no longer imply the files exist at current pins.
This changes documentation provenance, not implementation or historical pass status.

Two planned references occur inside the protected architecture span. After reviewing
those two presentation/provenance edits, only that span's digest in the delivery map
was updated, from
5a40c956d1b42cdaa1cd9a8588c2543113c0355aad7fdfd50123b2bd9432afb4 to
5a8e3542d4eba879d643ac1b23596bdccf2300079424fa1bd3e7b58e1c4e5f9f.
All 361 canonical definition hashes, the retained ID-set hash and every other
protected-block digest remain unchanged. The checker/enforcement, component pins
and source requirements are unchanged; no placeholder files were added.

Fresh checks pass in both original and integration roots: the 361-definition
guard, all 26 mutation tests and the doc-link checker. The integration checker
retains its normal seven unverifiable-reference skips; the original checker has
six. These skips were not added by the correction. The full pristine-pin
make consumer-checks rerun then exited 0 with all 20 rows passing, including
docs-check and the 32 checker regression tests. All 20 checks, the 361-definition
guard and its 26 tests passed again after merging audited newer root main and
using its exact component pins. The checker/enforcement source was not changed.

## Next acceptance sequence

1. Preserve the final source commits and completed scoped receipts with this root
   journal follow-up and a final source backup; retain earlier evidence as dated.
2. Run the real tracer on an admitted profile with working local IPC and normal
   provider authentication; retain real query, fixed-test, restart and replay evidence.
   A build, help output or failed setup cannot substitute for this run.
3. Complete the remaining generation/platform/product gates in their proper
   execution profiles, including the IPC-blocked frontend checks and live Postgres
   qualification where required. Preserve the full-suite/CT/Electron/WSS limits.
4. Review component
   integration and normal pin updates without overlaying the original feature trees.
   Publication and merges into GitHub main remain separate authorized operations.
5. Progress through T2–T5/POST with explicit schema adaptation and each original gate.
   Ordinary Atomic activation remains gated by the governing plan.
