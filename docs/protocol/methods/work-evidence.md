> Prepared, experimental contract. These methods do not enable Atomic source
> authority or imply that confirmation, publication or native mutations are ready.

## Committed changes and evidence read models

| Method | Params | Result |
| --- | --- | --- |
| `vcs.subscribe` | `workspaceId` (required), `after?: { sequence, stateToken }` | `{ frames: ReadModelFrame[] }`, changes channel |
| `work.subscribe` | `workspaceId` (required), `after?: { sequence, stateToken }` | `{ frames: ReadModelFrame[] }`, evidence channel |

Both reads require current workspace membership. They read the daemon's committed SQLite
projection and never scan a working tree or invoke the Atomic host. The projection is
rebuildable; it is not execution authority or a competing source-head record. No capability
is advertised until the corresponding client and qualification gates are ready.

Clients require the negotiated generic event-stream recovery contract, and install the
existing per-workspace event subscription with `lossRecovery: 1` before issuing either method,
then buffer `vcs:delta` and `work:delta` events while the capture is pending. Events are
transient hints, with `ReadModelFrame` as their `data`; their event-log sequence is unrelated
to the read-model cursor. Read-model replay comes from the retained projection journal.
On reconnect use the last accepted `{ sequence, stateToken }`; a missing, expired or invalid
resume point returns a fresh snapshot. A gap requires resynchronization, never a partial fold.
An `events.lost` control for this lease also requires durable-cursor recovery, even if no
later delta arrives to expose a sequence gap. Initial captures are inline RPC results;
these methods do not mint a second lease or send `subscription.push` snapshots.

```ts
type ReadModelFrame = {
  type: "snapshot";
  workspaceId: string;
  channel: "vcs" | "work";
  sequence: number;
  stateToken: string;
  items: ReadModelItem[];
} | {
  type: "delta";
  workspaceId: string;
  channel: "vcs" | "work";
  previousSequence: number;
  sequence: number;
  stateToken: string;
  upserts: ReadModelItem[];
  removedIds: string[];
};
```

Each committed projection change advances a shared workspace sequence and opaque token,
and retains a frame for both channels, including an empty delta on the unaffected channel.
An actual second write to an already dirty path also advances the token. Replay of an
identical receipt does not. A client can authorize a fenced optimistic action only after
both channel views converge on the same sequence and token; the owning server transaction
must independently check that token before effects. Source operations also need their
native root/state/working-copy barriers. A read-model token alone does not grant permission.

Rows have the closed tagged form `{ kind, value }`. Changes rows use `change` or `dirtySet`;
work rows use `binding`, `candidate`, `check`, `offer`, `receipt` or `taskTransition`. Root summaries retain
workspace, root, repository, engine and binding epoch, and omit host filesystem locators.
Check summaries contain outcome and digest/count references, rather than command output.
An offer summary omits private authority facts and cannot be submitted as an offer itself.
It retains the original `taskRevision` and a separate server-derived `completionNoteRev`.
The latter identifies the current note row eligible for the completion compare-and-swap;
clients must not substitute the original task revision's `rev`. Status, assignment and
other bookkeeping writes may advance the note revision while preserving the original
requested work. The daemon compares the original title, body, content type, criteria,
work definition, estimated effort and dependency/conflict relations; changed requirements
or unavailable original source pins refuse confirmation. It never fills missing historical
content type from the current note. Any note write after offer capture requires a refreshed
offer, including a lifecycle-only write. A confirmed transition retains the original
`taskRevision` and has `noteRevAfter = completionNoteRev + 1`.
Unknown line counts are `null`, not invented zeroes. Consumers validate the complete frame
before advancing its cursor, and fence callbacks from an earlier local subscription.
Task-transition rows distinguish confirmed completion from human completion without
confirmation. They retain the operation, exact task revision, receipt digest and completion
time; they omit private caller authority and credential facts.

Responses are bounded before loading rows: at most 2,048 rows and 400 KiB of serialized
projection data, reserving 8 KiB for envelopes and accounting for UTF-8 bytes.
If retained deltas exceed the read budget, the
server may resnapshot. If the snapshot itself exceeds the budget, the read refuses explicitly;
it never returns a truncated snapshot with a complete sequence. Paged snapshots for larger
inventories remain unqualified. Clients must not enable this experimental path merely
because a method is registered.
