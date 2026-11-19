# Proposed minimum viable Atomic tracer

Status: delivery specification adopted by the [governing plan](atomic-substrate-adoption-2026-11-12.md#12-delivery).
The tracer command and completed workflow do not exist yet. This document specifies T1
and T2; T3–T5 and POST retain the rest of the plan.

Build one repeatable scenario connecting the existing product to the real Atomic host.
The first pass uses a disposable **Git-authoritative workspace with an Atomic derived
index**. This follows the plan's Git-first task/evidence and read-only knowledge increments.
The second pass exercises native Atomic writing against the same fixture and assertions.
Do not reopen unrelated infrastructure work until the first pass is executable.

## The first executable scenario

Use one provider already authenticated through the existing Intent adapter, one human
task, one source file, one test and one resulting commit. Use an isolated daemon data
directory and disposable repository, not an installed application's database or real project.

Fixture: src/fees.js exports feeCents(amountCents, basisPoints), initially using Math.floor.
A fixed Node built-in test expects feeCents(1234, 500) to return 62. The human task is:
"Round the fee to the nearest cent; change only src/fees.js and preserve the test."
The source correction should make that test pass. No package installation is needed.

The scenario must:

1. Create and confirm the task through the existing planning path, retaining its original
   TaskRevision, criteria and permitted file reference.
2. Start one actual configured model/provider through the ordinary Git execution path.
   The provider edits the file. The application records the resulting Git contribution.
3. Require the recorded contribution's changed-path set to be exactly src/fees.js, with
   no altered test or unrelated changes. Execute the real fixed test against a materialization
   of that recorded commit. Retain
   its command, actual exit result, log hash and source commit/tree. Verify the test itself
   was not changed. A model saying "tests pass" is not a test result.
4. Explicitly prepare Atomic's real recorded-code index for that commit and query the
   known feeCents symbol/text through the actual host/client transport. Require a positive
   hit in the correct file identifying the corrected recorded content and its source basis;
   an empty result, wrong index or sentinel absence alone must not pass.
5. Compose an inspectable report showing the original task/run, Git contribution,
   separately retained test observation and actual Atomic query/read basis.
6. Add an uncommitted sentinel to the working file and show that the recorded-code query
   excludes it. Never fall back to live working files.
7. Stop and restart Services and the Atomic host while retaining their fixture data.
   Explicitly prepare the same commit again, re-query and verify the same durable derived
   data generation, commit/tree and original task lineage. There must be no new agent
   execution or duplicate contribution. A new process/connection generation is expected.
   This is durable reopen/idempotent preparation, not interrupted native-record reconciliation.

The report must distinguish observed test evidence from any separately qualified check
receipt. It must not assert exclusive authorship, independent review, source acceptance
or automatic task completion. Task-plan confirmation is not source-adoption approval.

## Existing pieces and the actual glue work

The relevant current, partly uncommitted source paths are relative to packages/intentd:

```text
crates/intent-services/src/auto_commit/recording.rs
crates/intent-services/src/knowledge_ops.rs
crates/intent-services/src/task_work_evidence.rs
crates/intent-atomic/src/knowledge.rs
crates/intent-atomic-proto/src/knowledge.rs
```

- Actual task-bound Git contribution retention already exists.
- Services::prepare_recorded_code and query_recorded_code already import/query an
  authorized immutable Git revision through the real Atomic client. They currently have
  no production caller outside their definitions/tests.
- The original confirmed-run evidence read and frontend already exist.
- AtomicCodeClient's authorized prepared-index lookup is in memory. Restart requires
  preparation again; the host can reuse its durable mapping. Skipping this step would
  produce an absent-index failure rather than successful recovery.

Implement only these three pieces for pass one:

| Piece | Required output |
|---|---|
| One tracer controller and developer command | Boots the disposable scenario, uses the existing APIs, runs one real provider and produces an honest pass/fail report. Proposed target name: make atomic-tracer; it does not exist yet. |
| One explicit task/run-to-query association | Retains original receipts and verifies contribution commit == imported commit == queried source commit, with matching repository/root/epoch. Reject drift or unavailable evidence. Reuse existing evidence storage. |
| One thin display | Initially an inspectable report; then expose that same report from the existing task/evidence UI. Show task, changed file, test observation, commit and Atomic query basis. No new general dashboard or changes panel. |

Preparation resolves the current commit on the server. Keep the fixture at its recorded
commit and compare the returned basis to the expected contribution. If HEAD advances,
refuse or report stale coverage; do not silently attach a later index to the old task.

The association is currently missing: the derived query basis intentionally says
ImportedGitSnapshot and has task_revision: None. The existing task-evidence DTO has no
derived-query result field. Preserve these facts. The new composed association belongs to
Intent; it must not masquerade as native Atomic task-intent linkage. Native task projection
currently requires an Atomic root and cannot simply be called on the Git workspace.

## Run it where it can actually execute

The fastest first target is the user's **native macOS ARM64 machine**, outside this session's
IPC restrictions, with the explicitly configured pinned native-host binary. The runtime's
platform gate supports macOS ARM64. This first pass needs no Linux provider namespace.

Linux ARM64 is currently supported only by qualification tooling, not by the Services
runtime platform gate. An executable override does not bypass that gate. Do not remove it
to get a green tracer. Use a supported target or separately implement and qualify support.

Use actual local IPC and a real host. Scripted ACP can help debug transport, but a scripted
model must not satisfy the first tracer's real-provider acceptance condition. Missing
authentication, binary, platform or IPC support is a setup failure, not a mocked success.

## Native-writing pass: the next tracer, not a hidden claim about pass one

Reuse the same scenario in a fresh Atomic Draft root; do not convert the T1 Git root or
change its fixed engine. The controller must bootstrap
its real baseline, original task/native projection, manager admission and explicit one-file
selection, then invoke the existing private scoped execution owner. That path already joins:

```text
actual scoped execution and callback drain
original-source checkpoint
immutable source capture
native record settlement
retained evidence and restart recovery
```

The important existing implementation is:

```text
crates/intent-services/src/agent_manager/atomic_turn.rs
crates/intent-services/src/agent_manager/atomic_capture.rs
crates/intent-services/src/atomic_work_lifecycle.rs
```

Positive Linux execution, controller/bootstrap/selection glue and a provider-compatible
resource/network/tool arrangement are still missing or unqualified. A deterministic
confined ACP patch worker can first verify the real transport/record/recovery mechanics.
Adding a controller-side model call that supplies patch data is a possible subsequent
bridge; that bridge is new work and would not qualify unrestricted provider CLI sandboxing.

Native-pass acceptance: a real native task UID and change hash refer to the original
task; only the allowed file is recorded; checkpoint/record facts survive restart; controlled
interrupted operations reuse their original operation ID, retained prepared bytes/hash
and known effects without duplicating a record; failed custody or stale scope stays refused. It
does not authorize canonical adoption, publication or ordinary Atomic workspace creation.

## Explicitly outside this tracer

Multi-agent fan-out, conflict UI, upstream skill compatibility, native source adoption and
rewind, independent reviewer qualification, forge publication, general memory learning,
four-platform releases, performance claims and rollout are separate increments.

Do not weaken existing source-authority gates. The first success criterion is a reproducible
real task-to-Atomic-query loop; the next is a reproducible native record/recovery loop.
Set estimates from the first executable attempt and its actual failing seam, rather than
from component-test counts. Preserve the architectural invariants and original production/pilot
qualification criteria; the governing plan's T1–T5 sequence supersedes the previous ordering.

See the [implementation handoff](atomic-substrate-handoff-2026-11-15.md) and
[current status](atomic-substrate-status.md) for existing code and validated boundaries.
