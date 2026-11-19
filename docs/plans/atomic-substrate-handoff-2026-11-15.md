# Atomic implementation handoff — 15 November 2026

**19 November execution status:** the [current reconciliation journal](atomic-reconciliation-execution-2026-11-19.md)
records preserved source, local integration commits and current gates. The opt-in CLI
builds; its real attempted run failed before provider admission because local host
IPC binding was denied. T1 is not qualified. Nothing has been pushed, merged into
main or activated. R1 path provenance is corrected; the 361-definition guard, its 26
tests, doc links and all 20 root consumer checks pass. Earlier branch tables and
validation receipts below are historical.

**Current integration assessment:** see the
[18 November reconciliation plan](atomic-reconciliation-plan-2026-11-18.md) for verified
main divergence, additional worker work, schema conflicts and the merge sequence.
The validation receipts below remain historical; they do not qualify current main.

## Reconciliation execution checkpoint — 18 November 2026

C0 source preservation is complete. The checkpoint at
.reconciliation/checkpoints/20261119T035821Z contains all nine source trees,
864 ordinary file versions, exact index/deletion/mode metadata and 128 refs across
three repository bundles. Each bundle was restored independently and passed full
fsck with its original shallow boundaries. The checkpoint's RESTORE.md documents
recovery into a new directory. These artifacts preserve source; they do not qualify
runtime behavior or supersede the historical receipts below.

The reusable checkpoint tool is scripts/checkpoint-atomic-reconciliation.py. Its
verification command is:

```sh
python3 scripts/checkpoint-atomic-reconciliation.py --verify-existing \
  /Users/oliverbeavers/CodeRepositories/intent/.reconciliation/checkpoints/20261119T035821Z
```

Integration now proceeds in separate local clones under .reconciliation/integration.
The root branch integrate/atomic-t1 starts at ae48c76413d68e8c63a3e517e2be23b50453dd1c;
the daemon branch starts at 643f8621c9587f58536a53ebdaab1b4046236473. Original aggregate
and worker trees remain preserved and available for comparison. Root gitlinks stay
at main's daemon eade125 / frontend f4a8646 pins.

R2 additive contracts pass the current-pin protocol, event, field-parity and fixture
checks. R1 preserves the final governing plan and its coverage checker, but its full
docs gate waits for referenced daemon seam/qualification scripts to reach the pins.
No protected requirement or doc-link check was weakened to bypass that dependency.
B1–B4 source extraction and T1 implementation are in progress; their old feature-tree
test results are not evidence of current-main compatibility.

The full plan is **not implemented or qualified**. Substantial backend, native-host,
frontend and recovery code exists and passes the local gates below. Ordinary Atomic
workspaces remain disabled; the default editing backend is Git. Do not treat the
remaining work as a flag flip.

Read this handoff first, then the [work-item status ledger](atomic-substrate-status.md)
and [saved validation receipts](atomic-substrate-validation-2026-11-15.json).
The governing plan is [Atomic substrate adoption](atomic-substrate-adoption-2026-11-12.md).
The ledger has the detailed W01–W42/assumption/verification status; no reliable overall
completion percentage has been established.

The controlling execution sequence is now the governing plan's
[T1–T5 delivery section](atomic-substrate-adoption-2026-11-12.md#12-delivery), with a
[complete requirement map](atomic-substrate-delivery-map.json). Start with the
[T1 tracer specification](atomic-bullet-tracer-2026-11-15.md): first a real Git task feeding
Atomic's derived query engine, then native writing against the same fixture. The original
requirements and implementation status are retained; resequencing adds no readiness claim.

## Preserve the current workspace

Working directory: `/Users/oliverbeavers/CodeRepositories/intent`.
The following branches and HEADs were checked again when preparing this handoff:

| Repository | Branch | HEAD |
|---|---|---|
| Monorepo | docs/atomic-substrate | d48490723f8dda6bbb4185d8b19aa505ec1f04b8 |
| packages/intentd | feat/atomic-substrate | df5491245575a4d39f52eeeff07fe28df81edc62 |
| packages/cloudlands-fe | feat/atomic-substrate | 050e969d9a0b2f6e6fba405b4b9596916cc53110 |

**The implementation is largely uncommitted. HEAD alone does not contain it.**
No changes were pushed, no PRs opened or merged, and no installed daemon, user database,
release or Atomic activation was changed. The workspace already contained substantial
changes before the latest implementation pass. Preserve those edits and submodule
pointers: do not reset, clean, or run a submodule checkout to restore the pins.

The saved validation JSON inventories 568 changed code files with hashes, including
preexisting work; this is a cumulative snapshot, not authorship attribution. It also
embeds frontend handoffs, exact successful commands, log hashes and blocked-gate receipts.
It is not retroactive proof that every earlier test used a sealed identical source tree.
Raw logs under /tmp may disappear; the repository documents and JSON are the primary handoff.

## What exists now

| Area | Implemented | Remaining boundary |
|---|---|---|
| Git seam | Neutral identities/errors, rooted Git adapter, migrated reads/writers, capture admissions, read-model invalidation and auto-commit adapter routing. Direct-call baseline reduced to 67 source/symbol keys, 77 hits. | Migration and Git retirement are incomplete; the ratchet is not proof every later call through an alias is covered. |
| Native host | Standalone pinned host, protocol version 3, typed client/supervisor, actual store/task/session operations, freeze, exact record preparation/admission, triage/control reads and retained recovery. | A closed metadata session is not process exit. No ordinary Atomic source-authority route is enabled. |
| Runtime/capture | Internal manager joins original task/session/turn/grant owners, private working allocation, process exit, counted isolated ACP callbacks, selection, checkpoint and record settlement. Legacy provider starts refuse Atomic roots before side effects. | Positive Linux execution is unrun. Normal provider resources, network/tool policy and source activation are not qualified. |
| Checkpoints | Native closures and aggregate archives preserve conflicts, empty directories, dirty/ignored bytes, independent selected contents/deletions and evidence. Durable blob/history retention precedes monotonic pointer CAS; startup recovery uses retained bytes. | No normal workspace replacement. Off-view selections or unavailable original selected payloads explicitly refuse. Unsupported native attributes/external knowledge are not silently omitted. |
| Source acceptance | Internal engine-neutral evidence, review/confirmation structures and Git candidate/capture/application/recovery pieces. | No qualified ordinary source-acceptance workflow or independent reviewer producer. Human task-plan confirmation does not authorize source adoption. |
| Task planning/evidence | Review → confirm → first-run launch; original human TaskRevision pin; actual bounded task.workEvidence RPC and UI for original first-admission history. | Dedicated multi-child fan-out and V44 remain open. Check/review/settlement linkage and complete attribution are not inferred. |
| Memory | Explicit opt-in, non-node experimentalMemoryRead capability; strict captured read-only transport, Redux ownership and experimental Context panel. | Default deployments omit the capability. No memory mutation, delivery/acceptance UI, related-work or why-line live entry points. |
| Skills | Exact pinned package verifier, engine-aware catalog hiding/precedence, inactive Intent workflow body and executable source-compatibility inspection. | Unchanged full upstream skill workflow is incompatible at this pin. No counted CLI ingress, adapted binding fallback or distributable package is complete. |
| Qualification tooling | ARM64-aware full runner, immutable evidence/resume fences, early namespace control, exact-production Linux compile probe and a separate compile-only entry. | Tooling tests are mocked; actual current-source Linux compilation and confinement are unrun. Release target matrix is unchanged. |

Native Atomic pin: **bf9893adb57dccbaa8f7e14277e02d060d74bf53**.
Skill pin: **e9332ebff36f188ed7b7fc31769f661599363184**.

## Validation actually completed

These are separate cohorts, not an additive total or a complete end-to-end suite.

| Check | Result |
|---|---|
| Native host full library run | 135 passed, 4 ignored |
| Subsequently added native CLI policy/registry tests | 5 passed |
| Native client and protocol libraries | 62 + 9 passed |
| Store integration cohort | 56 passed, including all 11 checkpoint cases |
| Services/ACP owner cohort | 153 + 8 passed; 2 Services entries ignored |
| Shared legacy-start guard and future-size budget after extraction | 3 passed |
| Actual pinned skill package and memory hello capability | 1 + 1 passed |
| Frontend planning / evidence / experimental memory cohorts | 573 unique / 413 / 63 passed |
| Source lints | All 25 suites, 297 tests passed |
| Qualification-tool CI entry | 58 mocked tests passed |
| Strict workspace and native-host Clippy | All targets passed with warnings denied |
| Formatting / monorepo consumer checks / final diff checks | Passed |

Frontend TypeScript, focused Svelte, lint, localization and ownership checks also pass.
The validation JSON retains exact commands and scope distinctions. Some warm-copy tests
can explicitly return UnsupportedCOW: their pass is not positive COW or performance proof.

Required checks still blocked:

- Full make check stops at offline cargo-shear metadata needing uncached
  anstyle-wincon 3.0.11. The separate final formatter, Clippy and source lints pass.
- Build-wide changes require the full prescribed test suite. Its pinned callback fixture
  requires an authorized **Linux x64** host; native macOS cannot run it. Focused tests
  supplement rather than replace that gate.
- Real WebSocket/IPC execution cannot bind here; Electron behavior is not qualified.
- Docker socket access is denied in this session. Linux process-scope compilation,
  namespace/pidfd/provider execution and root Linux/MSRV qualification remain open.
- Final make status could not allocate a development port block; its service/health
  inventory is unavailable. No sandbox/service was started by this work.

The user's old Docker run is preserved at:

```text
/Users/oliverbeavers/atomic-linux-evidence-20261114T155711Z
```

It built the old GNU x86_64 host and passed 92 default runtime/process tests, but the
bubblewrap namespace control was unavailable. It used an older source/protocol snapshot
and cannot qualify current code. Do not overwrite it or reinterpret it as a pass.

## Where the next implementer should look

These are current working-tree paths relative to the monorepo, including uncommitted files:

```text
packages/intentd/atomic-host/src/
packages/intentd/crates/intent-atomic-proto/src/
packages/intentd/crates/intent-atomic/src/
packages/intentd/crates/intent-services/src/agent_manager/atomic_turn.rs
packages/intentd/crates/intent-services/src/agent_manager/atomic_capture.rs
packages/intentd/crates/intent-services/src/agent_manager/atomic_process_scope.rs
packages/intentd/crates/intent-services/src/agent_manager/atomic_process_scope_linux.rs
packages/intentd/crates/intent-services/src/agent_manager/provider_source_guard.rs
packages/intentd/crates/intent-services/src/atomic_work_lifecycle.rs
packages/intentd/crates/intent-services/src/atomic_checkpoint.rs
packages/intentd/crates/intent-store/src/atomic_checkpoint.rs
packages/intentd/crates/intent-services/src/skill_catalog/atomic.rs
packages/cloudlands-fe/src/features/task-planning/
packages/cloudlands-fe/src/features/knowledge/ExperimentalMemorySection.svelte
packages/intentd/scripts/atomic-linux-qualification/
```

Store migrations 0206–0209 add selection, confirmed-plan ownership, evidence-read indexes
and checkpoint pointers. Do not test these through a signed install against a user's database.
The assistant guide has companion planning/evidence, skill-hiding and explicitly experimental
memory text. Preserve its readiness distinctions when extending product surfaces.

## Current implementation queue: T1

Only three tickets are initially active: tracer-controller, tracer-association and
tracer-report. Follow the governing delivery section for their exact acceptance criteria.
No unrelated component expansion before the real Git-to-Atomic query/restart scenario
passes. Existing safety requirements apply to every exercised effect.

## Native qualification and later-stage reference

The following notes remain relevant to T2 and later. They are not prerequisites for the
Git-authoritative T1 tracer on an admitted platform; they do not supersede the controlling
T1–T5 sequence or its separate acceptance criteria.

1. Obtain the current Linux typecheck first. From a normal Terminal with Docker access:

   ```sh
   cd /Users/oliverbeavers/CodeRepositories/intent/packages/intentd
   python3 -I -B -S scripts/atomic-linux-qualification/compile-scope.py \
     --platform linux/arm64 \
     --output "$HOME/atomic-linux-scope-compile-$(date -u +%Y%m%dT%H%M%SZ)"
   ```

   Read its saved diagnostics and fix actual failures. This checks the exact two production
   scope files through a denying Services shim with Rust 1.98. It executes no provider or
   native host and proves neither complete Services integration, confinement nor root
   Rust 1.96 compatibility. Its distinct receipts cannot resume the full qualification runner.

2. Qualify actual Linux namespaces, pidfds, resources, callbacks, teardown/cancellation and
   the complete Services route. Run the prescribed Linux x64 callback/nextest gates too.
   The full ARM64 host runner is separate; its namespace control must pass, with no
   privilege or uncontained fallback. Follow its README and use a fresh output for current code.
3. Finish the Atomic activation bundle: eligibility/ignore parity, source-engine selection,
   original selection/attribution, provider resource/network/tool policy, instructions,
   creation/lifecycle and recording of every settled turn. Do not enable capability flags early.
4. Resolve CLI compatibility. Raw upstream SandboxImpl would bypass Intent's counted
   shared-owner model and cannot be exposed by copying a grant token. The plan already names
   adapted ws.vcs/ws.work bindings as a fallback, but that route is not implemented or activated.
5. Complete qualified independent review, native adoption/rewind, projection/publication,
   remaining UI and planning fan-out; then pilot, recovery drills and two-week measurements.

Keep original physical owners and immutable task/source identities through cancellation and
recovery. A DTO, empty busy set, parent exit alone, metadata close or historical journal does
not recreate execution custody. Never weaken these refusals to make a qualification pass.

Read AGENTS before further work. Use project edition-2021 formatting; the standalone host
uses its isolated Rust-1.98 workspace. Exact successful invocation environments are saved in
the validation JSON. Do not merge or arm auto-merge without explicit human permission.

No implementation workers or validation commands were intentionally left running at the
last completed checkpoint. Continue from these files rather than relying on chat history.
