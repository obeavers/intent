> Prepared experimental contract. The daemon composition must explicitly opt in;
> ordinary deployments leave memory disabled and advertise no memory capability.
> Catalog presence, internal host dispatch and an opaque identifier establish no
> readiness, instruction authority or permission.

An explicitly opted-in daemon advertises exact integer
`server.capabilities.experimentalMemoryRead: 1` for `memory.list` and
`memory.context`. Clients show these reads as experimental and discard protected
results when the original acknowledged connection, principal or workspace access
lease retires. This read capability advertises no mutation or prompt delivery.

## Experimental ledger memory

All requests require `workspaceId`. `rootId?` selects an existing server-owned
repository binding in that workspace; paths/remote URLs/native hashes cannot
create one. Absent `rootId` means workspace-only memory. Project-wide and
cross-workspace memory sharing are unsupported. `paths` defaults to `["."]`,
contains at most 32 safe repository-relative prefixes, and only narrows scope.

| Method | Additional request fields | Result |
| --- | --- | --- |
| `memory.list` | `rootId?`, `paths?`, `after?: UUID`, `limit?: 1..20` (default 20) | `{ memories: MemorySummary[], nextCursor: UUID \| null }` |
| `memory.propose` | `rootId?`, `proposal: MemoryProposalInput` | Immutable proposed `MemoryRevision` |
| `memory.accept` | `rootId?`, `expected: MemoryRevisionRef` | New accepted `MemoryRevision` |
| `memory.context` | `taskRevision`, `rootId?`, `paths?`, `query?: string` (maximum 512 bytes), `limit?: 1..20` | `MemoryRetrieval` |
| `memory.select` | `rootId?`, `paths?`, `retrievalId`, `selected: MemoryRevisionRef[1..8]` | `TaskContextReceipt` |

Requests reject unknown fields. `memory.context.taskRevision.workspaceId` must
match `workspaceId`. Workspace membership is checked before source bodies are
read. Shared acceptance requires the actual authenticated human workspace owner
or daemon administrator, with mutable credential/role facts revalidated in the
write transaction. An agent cannot accept a proposal or acquire a human-private
scope from a session owner, attached context ID or workspace owner field.

`MemoryProposalInput` contains `kind` (`decision`, `lesson`, `constraint`,
`preference`, `context`), `text` (maximum 16 KiB), `visibility` (`owner-private`
or `workspace-shared`), `paths`, `sources`, `invalidation` (required, maximum
2 KiB), and optional `supersedes: MemoryRevisionRef`. Its complete encoded
payload is limited to 32 KiB. The service supplies repository/workspace identity.
Private memories belong to the actual wire principal. Agent/daemon proposals
are shared proposals with their actual proposer provenance, never inferred
human authorship. Status is `proposed`, `accepted` or `superseded`.

`MemoryRevisionRef` is `{ memoryId: UUID, revision: integer, digest: SHA256 }`.
`MemoryRevision` adds `proposal`, `status`, `ownerPrincipalId: string | null`,
`proposedBy` and `createdAt`. `MemorySummary` contains a `candidate`
(`reference`, `kind`, bounded `preview`), `status`, and `scope`.
Supporting sources are resolved server-side at exact retained revisions:
`task { revision }`, `memory { revision }`, `confirmation { operationId,
receiptDigest }`, or `receiving-observation { observationId, journalDigest }`.
A receiving observation explicitly has no causal producer or passing-check
proof. Referenced IDs never authorize source reads.

Supersession is a new proposal naming the exact accepted predecessor. Acceptance
atomically retains a superseded predecessor revision and the accepted successor;
both retain immutable history and produce native-projector outbox inputs. A
changed predecessor refuses acceptance. Native vault projection is not yet
qualified; retrieval remains owner-filtered in the Intent ledger.

`MemoryRetrieval` contains `retrievalId`, exact `taskRevision`, up to 20
`candidates`, `truncated`, and a canonical `LedgerReadBasis`: `taskLedger` scope,
actual `sourceEventWatermark` from the same SQLite snapshot, unknown
`projectorWatermark: null`, query/ontology versions, owner visibility digest,
`ignorePolicy: "notAppliedToLedgerFacts"`, and explicit coverage/truncation.
Ranking is bounded literal text/scope matching without embeddings or network.
It records retrieval only. A different principal/agent or changed root/filter
cannot replay the retrieval ID as selection authority.

Selection rechecks each current accepted revision under a write transaction.
Changing memory between retrieval and pull refuses selection. The exact UTF-8
historical-data envelope, including its fixed provenance label, is retained in
the daemon's private evidence store (maximum 64 KiB). `TaskContextReceipt`
contains `receiptId`, `retrievalId`, exact `taskRevision`, exact `memories`,
`bytesDigest`, `bytesLength`, and `createdAt`. This is selection, not delivery.

For explicit prompt delivery, existing message metadata may contain
`workContext: { taskContextReceiptId: UUID }`. This is an opaque reference. The
manager resolves it using its exact original admitted work origin, checks task
revision and repository/root epoch, and retains an immutable binding-to-receipt
association. Private human memory delivery is refused until an explicit human
admission grant is implemented. Raw metadata text never becomes memory context.
The manager injects the exact retained bytes as historical data. Only a provider
accepted turn result records delivery; an error leaves delivery unknown. An
agent's claimed use is separately recorded against the original delivered
receipt/attempt, and is never inferred from retrieval, selection or ranking.

Historical revisions, context bytes and event evidence survive workspace
deletion. An internal human-approved remediation link retains the original
accepted decision, a separate exact corrective-task revision and the missing
check. It does not rewrite the original decision or automatically change task
or instruction status.
