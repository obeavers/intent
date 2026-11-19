# Atomic as Intent's Version-Control Substrate: Plan

Status: draft plan (no implementation). Pins observed: intentd `c755f03` (v0.11.197),
cloudlands-fe `db83827`, protocol 18.0, Atomic CLI 0.19.1. All `intentd` paths below are
relative to `packages/intentd/crates/` unless shown otherwise; frontend paths are relative to
`packages/cloudlands-fe/src/`.

## 1. Goal

Replace Git as the version-control system underneath Intent workspaces with
[Atomic](https://github.com/atomicdotdev/atomic). Atomic is a patch-theory VCS with views, CoW
sandboxes, an agent session ledger, managed agent lifecycles for outer orchestrators, signed
provenance and review triage. Its agent-native capabilities should become first-class IDE
features: per-agent views instead of branches, turn-level changes instead of auto-commits,
cherry-pick-free insertion of changes between views, provenance and attestation in review,
triage-driven review, session fork and rewind, and first-class conflicts. GitHub and GitLab
forge workflows (PRs, CI, merge queues) must keep working through Atomic's Git bridge, both
during and after the transition.

## 2. Summary

Intent gains a version-control **seam**. Each workspace gets a `vcs_kind`, set at creation and
never changed afterwards (except by an explicit eject). Atomic arrives as a second backend
behind the seam, and existing workspaces keep today's Git behaviour unchanged.

How an Atomic workspace maps onto Atomic:

- **Workspace** → a draft view (`ws-<workspaceId>`) plus a copy-on-write sandbox at the existing
  `worktreePath`. The sandbox comes from one shared Atomic repository per source repo. That
  repository also holds a `.git` directory, so Git and Atomic sit side by side.
- **Agent turns** → Atomic changes, recorded by **Atomic's own agent hooks** running under
  Intent-managed leases (`atomic agent lifecycle begin --owner intent --view ws-<id>`). These
  hooks also capture Atomic's tool-level causal provenance graph. At every turn end, Intent
  gap-fills any edits the hooks did not capture (for example, providers without hook support),
  so **every turn is always recorded**. Turn records replace auto-commit.
- **Agents see no Git.** The `.git` that `sandbox create` copies into the sandbox is stripped.
  Agents use Atomic, read-only, and the `ws.vcs.*` tools.
- **Forge flows** → Intent publishes the view to the workspace's existing `branch` with
  `atomic git push -b`. From there the existing `SourceControl` code handles PRs, CI and merge
  queues, untouched.

**Integration:** Intent runs a pinned, bundled `atomic` CLI and parses its JSON output. It does
not link Atomic's Rust crates.

**Protocol:** a new capability-gated `vcs.*` namespace for operations that make sense for both
backends, and an `atomic.*` namespace for Atomic-only features: provenance, triage, insert
between views, rewind/fork and conflicts. Legacy `git.*` reads on an Atomic workspace are
answered from a Git-shaped projection, so today's UI keeps working while the new screens are
built.

**Rollout:** behind a Labs flag, opt-in per workspace, with repo eligibility checks. Every
Atomic workspace can be converted back to Git ("eject") until the Git backend is retired.
Wider rollout waits on explicit Atomic maturity criteria. Remote nodes, submodule-heavy repos
(including Intent's own monorepo) and Windows stay Git-only until the Reach phase.

**End state: full retirement of the Git backend.** After Atomic becomes the default, existing
Git workspaces are converted. Then `GitVcs`/`GitProvisioner` and the `git.*` wire namespace
are removed in a breaking protocol release, gated on explicit criteria (§10.5). `intent-git`
shrinks to the Git-*interop* utilities that Atomic still needs at the forge boundary: the repo
cache that feeds `atomic git import`, forge credentials, `ls-remote` and clone.

**The resulting IDE experience** (Phase 2–3):

- A turn timeline in the changes panel. Every agent turn is a recorded change with
  agent/model chips, plus "Rewind to here".
- Unrecorded → Recorded → Published lanes replace unstaged/staged/committed.
- Insert one agent's changes into another view with a dependency-aware preview, with no
  cherry-pick.
- A provenance gutter showing which agent, model, session and turn produced a hunk, with
  exportable signed W3C PROV.
- A triage review tab: candidate set vs. trunk, risk-sorted, with a semantic walkthrough.
- Intent's first conflict UI: per-side agent attribution, resolved by recording a change.
- Fork an agent session at a turn into a sibling workspace, and carry changes into proposed
  sibling workspaces.

**Why not a big-bang swap.** Atomic is v0.19.1 and its JSON output covers only some commands.
Its Git bridge is still a proposed RFC and is Unix-only. Concurrent writers to one Atomic repo
have not been load-tested upstream. About 400 call sites depend on Git's staging area, refs and
SHAs. A per-workspace backend lets both live side by side, roll back per workspace, and gather
real-world data before Atomic becomes the default.

---

## 3. Current state

### 3.1 Workspace ↔ git mapping (1:1 branch + checkout)

- **`Workspace`** model: `intent-core/src/model.rs:358`.
  - Git fields: `branch`, `base_ref`, `base_commit_sha`, `repository_path`/`owner`/`name`,
    `worktree_path`, `skip_worktree`.
  - PR fields: `pr_number`, `pr_url`, `pr_status`, `active_pull_request`, `pull_requests`.
  - Other fields: `setup_script`, `plain_folder`, and `checkout_mode` (`worktree` | `cow` |
    `direct`, immutable once provisioned).
- **The store schema hard-codes git.**
  - `intent-store/migrations/0001_init.sql:6-30` defines `branch TEXT NOT NULL` (plain folders
    store `""`), `base_ref`, `base_commit_sha`, `worktree_path`, `skip_worktree`, `pr_number`
    and `pr_url`.
  - Later columns: `setup_script` (0019), `branch_auto_generated` (0024, gates branch
    deletion), `checkout_mode` (0055), `auto_commit_enabled` (0067), `context_links` (0110).
  - `workspace_git_root` (0093) holds secondary roots, including submodules (`source` is
    `agent` | `auto`), with their own PR columns. Rows are unique on `(workspace_id, path)`.
  - `repository_selection_state` (0146/0163) is a continuity mirror maintained by triggers.
  - The legacy `sandbox` table (0038) has an `sb/<agentId>` branch and `base_commit_sha`.
    Per-agent sandboxes were retired in protocol 16.
  - No standalone repository table exists. Identity is `repository_path`/`owner`/`name` on the
    workspace row, plus the repo cache.
  - The newest migration at the pinned intentd is `0190_agent_session_permission_policy.sql`.
- **Create** (`workspace.create`, `docs/protocol/methods/workspace.md:29`, details at
  `:485-594`; daemon steps in `intent-services/src/lib.rs` ~21758–23480):
  1. **Branch name:** a slug is generated, `workspace.branchPrefix` applied, and the result
     uniquified (`branch_auto_generated=1` at `lib.rs:23134`).
  2. **Checkout:** a linked worktree at `<root>/<workspaceId>/<repo-slug>` via
     `intent_git::worktree::provision_worktree` (`intent-git/src/worktree.rs:93`, called at
     `lib.rs:22957`), under the per-repo `WorktreeLocks`.
  3. **Base ref:** resolved in order remote-tracking → local → rev-parse → `HEAD`, with a
     pre-fetch. A failed fetch stops the create with `base-refresh-failed` unless
     `skipBaseRefresh` is set.
  4. **GitHub URL with no local path:** hydrates from `<root>/.repo-cache/<owner>/<repo>`
     (`repo_cache.rs:342` `ensure_cached_repo`). A CoW probe (`cow_checkout.rs:108`) picks
     `cow`; otherwise a local clone gives `direct` (`repo_cache.rs:956`).
  5. **Setup script:** `runtime().run_setup_script` (`lib.rs:23469`, `feature_ports.rs:1030`).
- **Auto-commit:** `intent-services/src/auto_commit.rs:1-20` subscribes to `agent:idle`, then
  `handle_agent_idle_auto_commit`, then finish-reason, session, plain-folder and
  folder-presence checks, then an LLM message (60 s timeout, 10 min cool-down), then
  `git_agent_commit` (`lib.rs:29192`).
  - Commits carry `Agent-Id:` and `Linked-Note-Id:` trailers.
  - It is gated by the `git.autoCommit` setting plus a per-workspace override, a non-empty
    diff, and no pending merge.
  - Silent skips are detected by matching error-text markers.
- **Proposals** are workspace-create cards, not PRs. An agent calls `ws.workspace.proposeSibling`
  (`intent-acp/src/mcp_server/bindings/workspace.rs:220` `propose_sibling`), and applying it (`:599`) runs a normal
  `workspace.create`. Unpushed local work is never carried into the sibling.
- **Archive** only flips status and interrupts turns.
- **Retire** (`intent-services/src/retire.rs:93`) deletes the checkout and keeps the branch and
  DB rows. It uses `detach_worktree` (`:403`), and revive re-provisions (`:415`, `:616`).
  Related helpers: `retire_supported`, `require_owned_worktree`, `remove_retired_checkout`,
  `revive_retired_checkout` and `is_standalone_checkout`.
- **Delete:** `cleanup_workspace_worktree_locked` (`lib.rs:12942`) prunes the worktree and
  renames it to trash (`worktree.rs:264`). It deletes the branch only if the branch is
  auto-generated, checked out, and not `main`/`master`. CoW and direct checkouts get only the
  rename (`lib.rs:13023`).
- **GitLab path:** `sourceControl.checkout.*` (`docs/protocol/methods/repository-checkout.md`
  §5.53) plus `workspace.create.repositoryCheckout`.

### 3.2 Where version control lives in intentd

| Concern | Today's owner | Notes for this plan |
|---|---|---|
| Workspace identity | `Workspace` (§3.1) | `branch` must be non-empty in the DB; `checkout_mode` is fixed once provisioned. Both stay meaningful for Atomic: `branch` becomes the publish branch. |
| Local Git | `intent-git` (~25k lines). Flat `pub mod`s in `src/lib.rs`, no façade, no VCS trait. | Re-exports Git-shaped types from `intent_core` (`GitStatus`, `GitBranches`, `GitBranchStatus`, `GitFileStatus`, `GitMergeConflicts`, `GitPullResult`, `GitAgentCommitResult`; `lib.rs:10-13`). Sync API; callers use `spawn_blocking` under `WorktreeLocks`. |
| Workspace create/delete | `intent-services/src/lib.rs` | See §3.1. |
| Turn-end commit | `intent-services/src/auto_commit.rs` | See §3.1. |
| Retire/revive | `intent-services/src/retire.rs` | `require_owned_worktree` needs a registered Git worktree or a standalone `.git` dir. |
| Accept changes | `intent-services/src/accept_changes.rs` (uses git2 directly) | Actions `commit\|push\|create-pr\|merge\|undo-push\|undo-commit\|reset-to-trunk\|rebase-onto-trunk`. Also hosts the qualified GitLab native-review path, which binds Git refs and SHAs. |
| Attribution | `tracked_changes` table, `intent-git/src/attribution.rs`; writers `intent-acp/src/handler.rs`, `intent-services/src/file_tracking_ops.rs`, `intent-store/src/tracked_changes_repo.rs` | Feeds commit-set rule 3 and agent locks. |
| Forge | `SourceControl` trait (`intent-sourcecontrol/src/lib.rs:74`; GitHub, GitLab) | Already VCS-independent: works on `RepoRef` plus branch names. **No change needed.** The crate doc says local git lives in intent-git, never in intent-sourcecontrol. |
| Checkpoints/hub | `intent-git/src/checkpoint/mod.rs`, `docs/protocol/node-checkpoints.md` | The hub contract is "prepared", not implemented, and entirely Git-ref based. |
| Example additive migration | `0093_workspace_git_root.sql` | Pattern to copy: new table, cascading FK, CHECK on a closed set, unique identity index. |

**`intent-git` internals.**

- **Modules:**
  - checkout: `worktree`, `cow`, `cow_checkout`, `native_checkout`, `native_push`, `submodule`
  - working-tree reads: `status`, `diff`, `show`, `local_changes`
  - writes: `stage`, `commit`, `reset`
  - refs and remotes: `branches`, `refs`, `remote`, `ls_remote`, `push`, `pull`, `fetch`
  - history rewriting and state: `rebase`, `squash`, `stash`, `conflicts`, `checkpoint`
  - attribution and history: `attribution`, `history`
  - identity and auth: `identity`, `auth`, `redact` (`redact_credentials` at `redact.rs:15`)
  - remote and node support: `repo_cache`, `node_git`, `hub`, `standalone_work`
- **git2 vs the git CLI:** it uses **both**. git2 is dominant. The `git` CLI is used for
  network, credentials, submodules and node paths: `auth.rs:156`, `fetch.rs:394`,
  `ls_remote.rs:175`, `repo_cache.rs:1636`, `node_git.rs:278`, `cow_checkout.rs:608`,
  `stage.rs:475`, `submodule.rs:41`.
- **Traits:** the only ones are `NativeCheckoutCredentials` (`native_checkout.rs:76`) and
  `NativeCacheAuthority` (`repo_cache/qualified.rs:16`).
- **Slow-call warning:** `SLOW_GIT_WARN_THRESHOLD` is 5 s (`lib.rs:59`, `pub(crate)`).
- **Dependents** (grep line counts): intent-services 414 lines in 40 files, intentd 53/20,
  intent-svc-transfer 30/4, intent-svc-remote 14, intent-svc-runtime 13, intent-acp 9,
  intent-transport 7.
- **Most-used modules:** status 65, history 51, repo_cache 49, auth 44, diff 35, remote 32,
  node_git 30, refs 26, local_changes 24, worktree 20, branches 18, commit 17, stage 14.
- **Direct git2 use outside intent-git** blocks a clean seam:
  - `intent-services/src/accept_changes.rs` and `git_ops.rs`
  - `intent-svc-transfer/src/transfer_{git,materialize,export,remotes}.rs`
  - `intent-acp`, `intent-svc-runtime`, `intent-svc-remote`

**Checkpoints and attribution.**

- **Checkpoint codec:** `intent-git/src/checkpoint/mod.rs` is ref-free and
  transfer-compatible.
  - Data: `Snapshot { object_format, head, index, wip?, branch? }`.
  - Functions: `capture` at `:317`, `verify_source` at `:353`, `restore` at `:461`.
  - Markers: `WIP_SENTINEL` and the `Intent-Index-Tree:` trailer.
  - Callers must quiesce writers. The current `snapshot_wip` mutates live HEAD/index and then
    unwinds it.
- **Node hub refs** (prepared contract): `refs/intent/ws/<ws>/agents/<agent>/{head,wip}`,
  `refs/intent/checkpoints/<cp>/<repo>/{head,wip,index}` and `refs/intent/publish/<branch>`.
  The `git-remote-intent` helper runs over the node link with scoped grants, quarantine, and
  expected-old-OID updates.
- **`tracked_changes`** (`intent-store/migrations/0006_code_review.sql:9`): `path`, `stage`,
  `status`, `agent_id`, `session_id`, `turn`, `commit_hash`, `old_blob_sha`/`new_blob_sha`,
  and additions/deletions.
  - Stage values in use: `unstaged|staged|committed|pushed|pull_request|merged|trunk`.
  - Git checks: `is_ignored_untracked` (`attribution.rs:206`), `classify_paths` (`:241`),
    `lockable_paths` (`:312`).

### 3.3 Wire contract

The documented protocol version is 18.0. Additive methods are capability-gated with no
version bump (`docs/protocol/versioning.md`). Capabilities are advertised in the capability
JSON at `intent-transport/src/client.rs:118`, alongside `boundedReads` and `nativeReview`.

- **`git.*`** (§5.6, `methods/git.md`):
  - Documented: status, stage, unstage, discard, agentCommit, checkMergeConflicts,
    getBranches, getRemoteUrl, branchStatus, pull, changes, diffs, commits, commitDetails,
    showFile, showFileChunk, numstat, branchDiff, clone.
  - Also called by the FE: `git.commit`, `git.stageHunk`/`unstageHunk`, `git.push`,
    `git.fetch`, `git.renameBranch`, `git.prStatus`.
  - Bounded reads are routed in `intent-transport/src/protocol.rs:1011-1022`.
- **`pr.refresh`** (`methods/pr.md:13`).
- **`accept-changes.*`** (§5.18, `methods/change-tracking.md:14-18, 95-96`):
  - Methods: getStatus, prepare, execute, mergePR, addRemote, reconcile, release.
  - `execute` restores attribution from `file-tracking`.
- **`file-tracking.*`** (§5.19): getChanges, loadCommits, getAgentLocks, stage, unstage.
- **`metrics.getAgentStats`.**
- **Events:** `git:branch|clone:done|clone:progress|commit|merge|pull|push`,
  `pr:linked|unlinked|updated`, `changes:git-status`, `changes:agent-locks`, `workspace:*`.
- **MCP agent bindings:** `ws.git.commit`, `ws.git.listRoots`, `ws.git.registerRoot`,
  `ws.git.unregisterRoot` (`docs/protocol/methods/mcp-bindings.md:214-217`).
  `check-mcp-bindings` is advisory upstream.
- **Git-specific payload fields throughout:** `sha`, `commitHash`, `branch`, `baseRef`,
  `ahead`/`behind`, `upstream`, `remote`, `localHeadSha`, `gitRootId`, `historyIdentity`.

### 3.4 Frontend

The frontend has no generated protocol types. Wire shapes are hand-written TS or zod.

- **Central seam:**
  - `lib/client/app-client.ts`: `GitClient` at ~L1629; `GitBranchesResult` and
    `GitBranchStatusResult` at ~L370–383.
  - `lib/client/live/live-git-client.ts`: git.status L142, getRemoteUrl L382, diffs L424 (paged
    via `git-diff-pages.ts`), commitDetails L443, getBranches L540, branchStatus L576,
    pr.refresh L608, stage/unstage/discard L643–660, agentCommit L674, pull L698.
  - `mock-app-client.ts`.
- **Code that bypasses the seam:**
  - legacy `features/git/git.client.ts` (git.commits L197, `getHistory`)
  - `store/renderer/slices/git/sagas/git-write-saga.ts` (status L71, stage/unstage L131–164,
    stageHunk L165/L316, commit L326)
  - `store/renderer/seeders/git-bridge-seeder.ts` (push L87, fetch L98, renameBranch)
  - `lib/client/live/bounded-object-read.ts` (showFile L147)
  - `pr-workflow-saga.ts` (commit L115, pull L206)
- **Surfaces:**
  - **Changes and diff:** `lib/components/chat/ChatChangesPanel.svelte` (checkpoint via
    `agentSession.checkpoint` at L1609) and `UnifiedMultiStageDiff.svelte`.
  - **Branch:** `lib/components/workspace/sidebar/BranchDisplay.svelte`,
    `initializer/BranchSelector.svelte` (getBranches L645/L928, branchStatus L999) and
    `CompactWorkspaceInitializer.svelte` (L2336).
  - **Create submission:** `workspace-initialization-submission.ts` L236–238 (hard-coded
    `'main'` for new repos).
  - **Review:** `features/accept-changes/` (`NativeSidebarReview.svelte`,
    `accept-changes.client.ts`, `types.ts`).
  - **PR state:** the `pr-workflow/`, `pr-status/` and `pr-monitor/` slices.
  - **Settings:** `lib/components/settings/GitWorkspaceSettings.svelte`.
  - **Conflicts:** there is **no conflict-resolution UI** today.
- **Types that assume Git:**
  - `shared/types.ts` L1401 `GitStatus`
  - `features/git-tracking/types.ts` (`GitCommit.sha/parents`, `GitBranch.ahead/behind/upstream`)
  - staging-area types: `ChangeStage` (file-tracking), `ChangeCategory =
    'unstaged'|'staged'|'committed'` (chat), `PrepareAcceptFile.staged`,
    `WorkspaceGitStatus.stagedCount`
  - git vocabulary in the inlang `messages/` catalog

### 3.5 What can be reused, and what blocks

**Reusable as-is:**
- `SourceControl` plus the whole PR, PR-monitor and merge-queue stack, all keyed on
  `workspace.branch`.
- `WorktreeLocks`, the folder-presence check, `PlainFolderGuard`, and the ownership proofs
  (which get extended).
- The repo cache: an Atomic repo is imported from it.
- `GitStatusCache`, once generalised.
- The bounded-read packing (the `git.diffs` budget logic).
- The `tracked_changes` pipeline, which keeps feeding live unrecorded attribution. Its Git checks
  are **not** reusable as-is: `file_tracking.rs:112` (`is_ignored_untracked`),
  `tracked_changes_sweep.rs:112` (`classify_paths`) and `agent_locks.rs:208` (`lockable_paths`)
  all open a Git repo. With `.git` stripped (D13) they would re-open the intent-hq/intent#7266
  class of stuck rows, so they move behind the seam (§6.1).

**Blocking:**
1. There is no trait, and git2 is used directly across five crates.
2. Git-shaped domain types are threaded into wire projections.
3. The UI and pipelines assume a staging area, and Atomic has no index.
4. Identity tokens are SHA-based (`historyIdentity`, native-review `localHeadSha`).
5. The node and checkpoint contracts are Git-ref based.

### 3.6 Prior art

No prior plan, design or issue in this monorepo mentions Atomic or Pijul. The closest internal
precedents are the node hub/checkpoint contract and the retired CoW work: the per-agent CoW
sandbox (removed in protocol 16) and the CoW isolation setting (removed in protocol 17).

---

## 4. Atomic capability baseline (verified)

Sources: the README, upstream docs/CONCURRENT-AGENT-SANDBOXES.md,
upstream docs/RFC-ATOMIC-GIT-CAUSAL-BRIDGE.md, docs.atomic.dev/agents/overview, and `--help` of the
locally installed CLI 0.19.1. Licence Apache-2.0. Builds from source need Rust ≥ 1.98.

- **Model.**
  - Changes are content-addressed graph operations (patch theory; Atomic credits Pijul).
    Independent changes merge commutatively. Conflicts are token-granular.
  - **Views** replace branches: draft vs shared/root scope.
  - Commands: `view create [--from] [--draft] [--parent] [--switch]`,
    `view split <name> [hashes] [--from] [--last N] [--cascade] [--dry-run]`, `view switch`,
    `view promote`, `view delete [--force]`, `view list`. `split` *moves* changes; a fork via
    `view create --from` *copies* them.
  - Other history commands: `revise [ref] [-- files] [-m] [--reword]`, `unrecord [CHANGE]`,
    `tag`, `stash push|pop|apply|list|show|drop|clear`, `identity` (signing, DIDs).
- **Working copy.**
  - `status [PATH] --json` emits a versioned JSON document for IDEs.
  - `diff [FILES] [--change H] [--view V] [--word-diff] [--untracked] --json`.
  - `restore [FILES] [--dry-run] [--force]` restores to the last recorded state.
  - `conflicts --short` prints `<path>:<line>:<kind>` lines.
- **Recording.** `record [FILES] -m … [--ai-assisted --ai-provider P --ai-model M] [--identity]
  [--skip-binary] [--max-size N] [--allow-conflict-markers] [--dry-run]`. Binary files make
  `record` fail unless `--skip-binary` is passed.
- **History.**
  - `log [--view] [--path] [-n] [--reverse] --format json`
  - `change <hash> --format json [--show-deps] [--show-hunks] [--full-hash]`
- **Moving changes.**
  - `insert change <hashes…> --to-view V [--deps] [--allow-conflicts]`
  - `insert view <src> --to-view V [--deps] [--dry-run]`
  - `insert preview`
  - The `-n/--dry-run` and `--confirm` flags apply when promoting between shared views.
- **Agent-native features.**
  - **Hooks:** `atomic agent enable` installs hooks for Claude Code, Codex, Antigravity,
    OpenCode, Cursor, Grok and others. Every file-modifying turn becomes a change carrying
    model, session, turn and timing. Each session gets an isolated draft view. Tool calls are
    classified as exploration, commitment or verification nodes in a causal provenance graph.
  - **Managed runs:** `agent lifecycle begin --owner <orchestrator> --session <id>
    [--executor codex|claude-code] [--work-item] [--view V] [--workdir <sandbox>]
    [--ttl-seconds 86400] --json`, plus `renew|stop|resume|abandon|end|status`. This exists
    explicitly for **outer orchestrators**. `--view` makes the run's sessions adopt that view
    for recording, and `--executor` scopes which agent's hooks participate.
  - **Other agent commands:** `agent attest|explain|identity|status --json`;
    `session show|fork <parent> --at-turn N --child <id>|rebuild`.
  - **Provenance:** `provenance trace <change> [--json [--sign]]` and `provenance show`
    (signed W3C PROV JSON-LD).
  - **Triage:** `triage candidates [VIEW] [--into T] --json` and `triage review` (verdict,
    findings, and a semantic walkthrough).
  - **Knowledge:** `intent`, `memory`, `vault`, `query` (knowledge graph).
- **Sandboxes.**
  - `sandbox create <name> [--dest P] [--view V | --from V]` makes a reflink CoW working tree
    (APFS clonefile, Btrfs/XFS FICLONE, ReFS, plain-copy fallback) that points at one
    canonical graph via `.atomic-sandbox`. `--from` forks a draft view **named after the
    sandbox**.
  - Provisioning skips only `.atomic/` and nested sandboxes, so a colocated `.git` is
    **copied** into the sandbox (§11.1 A8).
  - Records **serialize** through redb cross-process locks. Concurrent writers are not
    load-tested.
  - `sandbox stage|seal` (OCI) are **design-only**.
- **Git interop.**
  - `git import [--branch|--all|--incremental|--with-crdt|--dry-run|--no-vault]`.
  - `git push [-m] [--remote origin] [-b <remote branch>] [--no-push]
    [--allow-conflict-markers]`. It synthesizes a commit from the Atomic change messages **on
    the current Git branch**; `-b` only changes the remote destination, which is meant for PR
    branches.
  - `git hooks install|uninstall|status`.
- **Git Causal Bridge** (RFC rev 3, 2026-09-02). It is **proposed**: phases N and 0 are
  complete, some items are partial, and it is **Unix-only**.
  - Atomic owns history; Git is a projection. `.git` and `.atomic` are colocated.
  - Shared views map to `refs/heads/*`; drafts map to `refs/atomic/views/*`.
  - Signed bindings live in `refs/atomic/bindings/*`. Commit headers are `atomic-binding`,
    `atomic-set`, `atomic-state`, `atomic-author` and `atomic-agent`, plus `Co-authored-by`.
  - Ref updates use leases, with three-way ref reconciliation.
  - Known losses: empty dirs, ambiguous renames (become delete+add), opaque large binaries,
    conflict markers instead of an unmerged index, and **submodules recorded as gitlinks and
    not recursed**.
  - Merges imported from Git become resolution changes. A squash with no binding becomes one
    change marked as a squash.
- **Interfaces.** Only the CLI is documented; the Rust crates (`atomic-core`,
  `atomic-repository`, `atomic-agent`, `atomic-remote`, `libatomic`, …) have no stable library
  API. Remote and hosting commands (`remote|server|workspace|project|org|team`) exist, but
  their model is undocumented.

---

## 5. Key decisions

| # | Decision | Rationale |
|---|---|---|
| D1 | **Per-workspace backend, not a global switch, and no "shadow mode".** | Recording Atomic changes alongside Git commits in the same worktree means two writers reconciled by the bridge's three-way ref merge, which is still RFC-stage. Per-workspace gives isolation and per-workspace rollback. |
| D2 | **For Atomic workspaces, Atomic is the system of record and Git is a projection made at publish time.** | Turn records, views, insert and rewind are only valuable when Atomic owns history. Git is only needed at the forge boundary. |
| D3 | **Use the pinned, bundled CLI with JSON output; do not link the crates.** | No stable library API exists. Linking would force Rust ≥ 1.98 on the whole intentd workspace and couple Intent to Atomic's internal redb locking. A separate process contains crashes and allows version gating. Cost: output parsing and incomplete JSON coverage, mitigated by contract fixtures per pinned version (§6.3). |
| D4 | **A sync trait (`WorkspaceVcs`) in a new crate `intent-vcs`, called from `spawn_blocking` under locks, exactly as intent-git is used today.** | Keeps the migration mechanical and avoids an async rewrite of ~400 call sites. |
| D5 | **Only workspace-scoped operations whose behaviour depends on the backend go behind the trait.** Repo cache, auth, identity, redaction, ls-remote, clone, fetch-to-cache, native checkout/push, node_git, hub and transfer stay direct intent-git calls. | Atomic repos are imported from Git caches, so those utilities stay Git by nature. Abstracting them adds layers with no benefit. |
| D6 | **Atomic's agent hooks are the primary recorder, running under Intent-managed leases. Intent is the gap-filler.** (User decision, replaces the baseline's "Intent records turns itself; never install hooks".) Intent installs executor hooks scoped to the provider processes it spawns (§6.6), and starts each agent run with `agent lifecycle begin --owner intent --executor <x> --view ws-<id> --workdir <sandbox>`, so hook sessions record straight into the workspace view. At every `agent:idle`, Intent indexes the hook-recorded changes, then records any remaining attributed edits itself. | Hooks populate Atomic's full provenance: tool calls classified as exploration, commitment or verification, causal edges, session attestations with cost and tokens, and `agent explain`. This is the novel review surface. The gap-filler keeps the "every turn is recorded" guarantee (D7) for providers without hooks, failed hooks and interrupted turns. The race between hook and gap-filler is closed by sequencing (§6.6). |
| D7 | **Turn records are always on in Atomic workspaces, for every turn, including interrupted ones.** The `git.autoCommit` setting does not apply, and LLM commit-message generation moves to publish time. (Confirmed by the user, which resolves Q3.) | Records are local draft changes that the user publishes deliberately, so the original reason for the setting goes away. A rewind boundary exists at every turn. It also removes the 60 s generation wait at every idle. |
| D8 | **`branch` holds the publish branch; `checkout_mode` reuses `cow`/`direct`; no new enum values.** | Keeps PR discovery, the PR monitor and older frontend code working, and leaves existing switch statements intact. |
| D9 | **Legacy `git.*` reads are served from a projection for Atomic workspaces; `git.*` writes are refused or mapped explicitly** (§6.7). | The existing UI and the MCP `ws.git.commit` work on day one, and new screens use `vcs.*`/`atomic.*`. |
| D10 | **Unsupported for Atomic workspaces in Phase 2, refused at create time or call time:** remote placement, isolated delegation, GitLab qualified native review, submodules, LFS, Windows. | Each depends on unfinished Atomic or Intent contracts (§11). Failing closed is better than silently losing data. |
| D11 | **The end state is full retirement of the Git backend** (user decision; the baseline kept Git permanently). Phases 7–8 (§10.1) first convert existing Git workspaces, then delete `GitVcs`/`GitProvisioner` and remove `git.*` in a breaking protocol version. Both steps are gated by the retirement gate (§10.5). The `WorkspaceVcs` trait stays, with Atomic plus a test fake. | Retirement must not strand any user, so every reason the baseline gave for keeping Git (ineligible repos, Windows, remote nodes, GitLab native review, rollback) becomes an explicit gate item that has to close first. Eject is replaced by "export to a Git branch", which is just publish. |
| D12 | **View names are `ws-<workspaceId>`; per-agent sub-views are `ws-<workspaceId>--agent-<agentId>`.** | `sandbox create --from` names the draft view after the sandbox, so one command creates both. Hyphenated names are also path-safe for `--dest` defaults. (The baseline proposed `ws/<id>`.) |
| D14 | **Each Atomic workspace gets a hidden, daemon-only publish checkout:** `.atomic-repos/<key>/publish/<id>`, an Atomic sandbox on `ws-<id>` whose `.git` is a `git worktree` link to the canonical `.git` on the publish branch. It is created at first publish (or seeded at the remote tip on conversion), used for publish, eject and conversion, and removed on delete. It is exempt from D13 and is never agent-visible. | `atomic git push` commits on the *current Git branch*. Run in the canonical repo, it would pollute trunk and the import mirror for every workspace. Run in a throwaway copy, successive publishes would not fast-forward. A persistent worktree keeps commits in the shared object store and lets publishes fast-forward (A7). |
| D13 | **Strip `.git` from every Atomic sandbox; agents see Atomic only** (user decision; resolves Q7). Agents may run read-only `atomic status\|diff\|log\|change` and the `ws.vcs.*` MCP tools. They must not run mutating `atomic` commands or `git`. | A copied `.git` would be an orphaned second history. Agent `git commit`s there would be invisible to Intent and lost at publish. Failing loudly ("not a git repository") beats silent divergence. |

---

## 6. Design

### 6.1 The VCS seam: new crate `intent-vcs`

It depends on `intent-core` and `intent-git`, and owns the trait, the neutral request types and
`GitVcs`.

**Neutral domain types** live in `intent-core/src/vcs.rs`. They are wire-serialised, and wire
types live in intent-core. `intent-vcs` re-exports them.

```rust
pub enum VcsKind { Git, Atomic }            // serde "git" | "atomic"
pub struct ChangeId(pub String);            // git: full commit hash; atomic: change hash
pub enum RevSpec { Head, Index, Change(ChangeId), Parent(ChangeId), Named(String) }

pub struct VcsCapabilities {                // per-backend feature flags
    pub staging: bool, pub hunk_staging: bool, pub turn_records: bool,
    pub unrecord: bool, pub insert: bool, pub provenance: bool, pub triage: bool,
    pub first_class_conflicts: bool, pub native_review: bool, pub remote_placement: bool,
}

pub struct VcsFileEntry { path, status: GitFileStatus, staged: bool /* always false for atomic */,
                          conflicted: bool, mode?, old_sha?, new_sha? }
pub struct VcsStatus {
    kind: VcsKind, publish_branch: String, view: Option<String>,
    files: Vec<VcsFileEntry>, has_uncommitted_changes: bool, has_untracked_files: bool,
    ahead_of_trunk: u32, behind_trunk: u32, has_upstream: bool, unpushed_count: Option<u32>,
    recorded_unpublished: u32,              // atomic: changes in view not yet published; git: = unpushed
    conflicts: u32,
}
pub struct VcsChange { id: ChangeId, message, author, author_email?, date,
                       agent: Option<ChangeAgent>, linked_note_id?, published_git_sha: Option<String>,
                       dependencies: Vec<ChangeId> /* empty for git */ }
pub struct ChangeAgent { agent_id?, provider?, model?, session_id?, turn: Option<u32> }
```

`impl From<&VcsStatus> for GitStatus` is the **only** place the legacy wire projection is
built. It lives in intent-core next to `GitStatus`.

The three attribution methods replace the direct `intent_git::attribution::*` calls in
`file_tracking.rs:112`, `tracked_changes_sweep.rs:112` and `agent_locks.rs:208`. The tracked
changes sweep branches on `vcs_kind`. The Atomic implementations are driven by
`atomic status --json` and the ignore parity in §6.11.

**Traits** (`intent-vcs/src/lib.rs`), shown as shapes:

```rust
pub struct VcsCtx<'a> { workspace_id: &'a WorkspaceId, checkout: &'a Path, repo: &'a Path,
                        view: Option<&'a str>, base_ref: Option<&'a str>, base_sha: Option<&'a str> }

pub trait WorkspaceVcs: Send + Sync {
    fn kind(&self) -> VcsKind;
    fn capabilities(&self) -> VcsCapabilities;
    // reads
    fn status(&self, cx: &VcsCtx) -> Result<VcsStatus>;
    fn diff_working(&self, cx: &VcsCtx, scope: DiffScope, paths: Option<&[&str]>) -> Result<Vec<FileDiffWithHunks>>;
    fn diff_change(&self, cx: &VcsCtx, id: &ChangeId) -> Result<Vec<FileDiffWithHunks>>;
    fn show_file(&self, cx: &VcsCtx, path: &str, at: &RevSpec) -> Result<ShowFileResult>;
    fn history(&self, cx: &VcsCtx, q: HistoryQuery) -> Result<HistoryPage>;   // bounded, boundary-aware
    fn change_details(&self, cx: &VcsCtx, id: &ChangeId) -> Result<ChangeDetails>;
    fn history_identity(&self, cx: &VcsCtx) -> Result<Option<String>>;
    // attribution support (today in intent-git/src/attribution.rs; must not assume .git, D13)
    fn is_ignored(&self, cx: &VcsCtx, rel_path: &str) -> bool;
    fn classify_paths(&self, cx: &VcsCtx, rel_paths: &[String]) -> Result<Vec<PathState>>;
    fn lockable_paths(&self, cx: &VcsCtx, status: &VcsStatus, candidates: &[String]) -> Vec<String>;
    // writes
    fn record(&self, cx: &VcsCtx, req: RecordRequest) -> Result<RecordOutcome>;  // git: commit
    fn discard(&self, cx: &VcsCtx, paths: &[&str]) -> Result<()>;
    fn stage(&self, cx: &VcsCtx, paths: &[&str]) -> Result<()>   { Err(unsupported("stage")) }
    fn unstage(&self, cx: &VcsCtx, paths: &[&str]) -> Result<()> { Err(unsupported("unstage")) }
    fn undo(&self, cx: &VcsCtx, ids: &[ChangeId], mode: UndoMode) -> Result<UndoOutcome>;
    fn integrate_trunk(&self, cx: &VcsCtx) -> Result<IntegrateOutcome>;        // git: rebase; atomic: insert
    fn publish(&self, cx: &VcsCtx, req: PublishRequest) -> Result<PublishOutcome>;
}

pub trait VcsProvisioner: Send + Sync {
    fn provision(&self, req: &ProvisionRequest) -> Result<ProvisionedCheckout>;   // create/revive
    fn detach(&self, cx: &VcsCtx, keep_history: bool) -> Result<Option<PathBuf>>; // returns trash path
    fn owns_checkout(&self, cx: &VcsCtx) -> bool;                                  // retire ownership proof
}
```

- **Record requests:** `RecordRequest { message, paths: RecordPaths::{Explicit(Vec),
  StagedIndex, Attributed(Vec)}, ai: Option<AiMeta { provider, model, session_id, turn }>,
  trailers: Vec<(String,String)> }`. `RecordPaths` encodes the existing `git.agentCommit`
  commit-set modes 1–3. Mode 4 (refusal) stays in services.
- **Record outcomes:** `RecordOutcome { id: ChangeId, files: Vec<String>, file_count }`
  replaces `GitAgentCommitResult` inside services. The wire result is unchanged.
- **Errors** reuse `intent_core::Error` with these new variants:
  - `VcsUnsupported { operation, kind }` → `-32602`, `data.code = "vcs-unsupported"`.
  - `AtomicUnavailable { reason }` → `-32603`, `data.code = "atomic-unavailable"`.
  - `AtomicIneligible { reasons }` → `-32602`, `data.code = "atomic-ineligible"`.
  - `AtomicCli { subcommand, exit_code: Option<i32>, stderr_redacted }` → `-32603`.
- **Stop matching error text.** Add `RecordOutcome::Skipped(SkipReason::{NoChanges, Disabled,
  MergeInProgress})` so `auto_commit.rs` no longer matches message strings. The Git adapter
  maps `CLEAN_TREE_ERROR` and `PARTIAL_MERGE_COMMIT_ERROR` into it.

**`GitVcs`** (`intent-vcs/src/git.rs`) is a zero-state struct that delegates to the existing
intent-git functions (`status`, `diff::*`, `show`, `history::history_since`, `commit`, `stage`,
`reset`, `rebase`, `push`) with identical behaviour. Its capabilities: staging and hunk staging
true, Atomic features false, `native_review` and `remote_placement` true.

**Resolution.**
- `Services::vcs_for(&Workspace) -> Arc<dyn WorkspaceVcs>` and
  `Services::provisioner_for(VcsKind)` live in `intent-services/src/vcs_dispatch.rs` (new) and
  match on `ws.vcs_kind`.
- `GitVcs` is a process singleton. `AtomicVcs` is created once per `Services` and holds the
  `AtomicCli` handle.
- An Atomic workspace on a daemon whose Atomic backend is unavailable (no binary, flag off,
  wrong version) gets a **`FrozenAtomicVcs`**.
  - Reads come from the stored `atomic_turn_record` index, plus the on-disk sandbox read as a
    plain folder.
  - Every write fails with `AtomicUnavailable`.
  - So no workspace ever becomes unreadable.

**Keeping new code behind the seam.** Add the planned intentd script scripts/check-vcs-seam.sh. It greps
`intent-services`, `intent-acp`, `intent-transport` and `intentd` for
`intent_git::(status|diff|show|history|commit|stage|reset|rebase|squash|stash|conflicts|local_changes|attribution|checkpoint)`
and for `git2::` imports. It checks them against a frozen baseline,
the proposed scripts/vcs-seam-baseline.txt, and CI fails on any new entry. The baseline shrinks as each
migration step lands, following the FE `eslint-rules/baselines` pattern. Wire it into the
intentd CI workflow (these scripts live in the intentd repo, under
`packages/intentd/scripts/`).

### 6.2 Migrating call sites (Phase 0, no behaviour change)

Order the work by blast radius. Each step compiles on its own and runs the existing suites.

1. **Move direct git2 use into intent-git.** Pull the git2 code in `accept_changes.rs` and
   `git_ops.rs` into new intent-git functions (e.g. `intent_git::commit::undo_commits`,
   `intent_git::reset::reset_to_ref`, `intent_git::refs::is_pushed`) so `GitVcs` can own them.
   Direct git2 use in `intent-svc-transfer` and `-remote` stays, because that is transfer and
   node code and is Git-only under D10. List it in the seam baseline as "allowed: git-only
   subsystem". The git2 use in `intent-acp` and `intent-svc-runtime` is **test-only**: for
   example `intent-acp/src/mcp_server/bindings/app/workspaces.rs:2203` sits inside `#[cfg(test)] mod tests`
   (`:1286`), and `intent-svc-runtime/{script_ops,terminal_ops}.rs` are test fixtures. So the
   seam lint excludes `#[cfg(test)]` and `tests.rs` rather than allow-listing those crates.
   Enumerate the remaining uses first with `rg 'git2::'` (U5).
2. **Introduce the types and `GitVcs`.** Add `intent-core/src/vcs.rs`, the `intent-vcs` crate,
   and `Workspace.vcs_kind: VcsKind`. Use serde default `Git` and `skip_serializing_if =
   is_git`, so wire bytes stay unchanged.
3. **Migrate the read paths in `git_ops.rs`.** `git.status`, `git.changes`, `git.diffs`,
   `git.commits`, `git.commitDetails`, `git.showFile(Chunk)`, `git.numstat` and
   `git.branchDiff` go through `vcs_for(ws)`.
   - The `git_status_cache` value type changes from `GitStatus` to `VcsStatus`, and the wire
     projection comes from the `From` impl.
   - Registered secondary roots (`gitRootId`) always use `GitVcs`; roots stay Git (§11.2).
4. **Migrate the write paths.** `git_agent_commit` is the most-used write; it keeps commit-set
   modes 1–4 by building `RecordPaths`. Then stage/unstage/discard, then the accept-changes
   steps.
5. **Migrate `file_tracking_ops.rs`.** `loadCommits` → `history`; `historyIdentity` →
   `history_identity`.
6. **Migrate `auto_commit.rs`** to `RecordOutcome::Skipped`, which removes the marker matching.
7. **Migrate provisioning and cleanup.** Create, delete and retire/revive in `lib.rs` and
   `retire.rs` go through `VcsProvisioner`. `GitProvisioner` wraps `provision_worktree`,
   `provision_direct_checkout_with_progress`, the CoW paths, `detach_worktree` and
   `cleanup_workspace_*_locked`.

Expected result: the baseline drops from ~414 lines in intent-services to under 120 (the D5
Git-only utilities plus the repo cache). The exact number is measured when step 1 lands.

### 6.3 Atomic backend: new crate `intent-atomic`

It depends on `intent-core`, `intent-vcs` and `serde_json`, plus `tokio` for the process helpers
only.

**`AtomicCli`** (`src/cli.rs`) is the only place that spawns a process.

- **Fields:** `bin: PathBuf`, `version: semver::Version`, `env: Vec<(OsString, OsString)>`,
  `timeouts: AtomicTimeouts`.
- **Binary resolution order:**
  1. the setting `vcs.atomic.binaryPath`;
  2. the bundled `libexec/atomic` (intentd packaging) or Electron `resources/bin/atomic`,
     passed via the existing daemon launch env;
  3. `PATH`.
- **Boot probe:** run `atomic --version`. Require `>= ATOMIC_MIN_VERSION` (initially `0.19.1`)
  and `< ATOMIC_MAX_TESTED_MAJOR_MINOR`. On failure, store
  `AtomicAvailability::Unavailable(reason)` on `Services` and report it in capabilities.
- **`run_json<T: DeserializeOwned>(cwd, args, class: CmdClass) -> Result<T>`** and
  **`run_text(..)`**:
  - spawn with `std::process::Command`, stdin null, stdout/stderr piped with a 16 MiB cap;
  - apply the per-class timeout and kill the process group on timeout;
  - pass stderr through `intent_git::redact::redact_credentials` before it reaches errors or
    logs;
  - warn-log any call slower than `SLOW_ATOMIC_WARN_THRESHOLD = 5s`, mirroring
    `SLOW_GIT_WARN_THRESHOLD` (`intent-git/src/lib.rs:59`).
- **Timeouts per class:** Read 30 s, Record 60 s, Mutate 120 s, Import 15 min, Push 150 s.
- **Environment.**
  - Never inherit `ATOMIC_*` from the user's shell, and set the Atomic config dir to
    `<daemon data dir>/atomic`.
  - Inject Git credentials for bridge pushes the same way `git.clone` does: set
    `GIT_CONFIG_PARAMETERS` with the github.com-scoped helper. Reuse the existing builder, never
    duplicate it, by exposing it from `intent-git/src/auth.rs` as `pub fn
    github_credential_env(..)`.
  - Atomic's config dir is daemon-scoped, so `agent identity set` (machine-wide in the user's
    config) is applied to Intent's config only and never touches the user's own selection.
  - Hook installation is scoped to Intent-spawned provider processes (§6.6, A15). It never uses
    `agent enable -g` and never writes into the user's repository (`--agents-md` is never
    used).
- **Process limit:** one global semaphore of 8 concurrent `atomic` processes per daemon. Read
  calls may queue. This prevents fork storms on large workspaces.

**Output parsing** (`src/parse/`) has one module per subcommand: `status.rs`, `diff.rs`,
`log.rs`, `change.rs`, `sandbox.rs`, `lifecycle.rs`, `view.rs`, `provenance.rs`, `triage.rs`,
`insert.rs`, `conflicts.rs`.

- Each module defines tolerant raw structs (unknown fields allowed) and converts them to
  neutral types.
- JSON is available for `status --json`, `diff --json`, `log --format json`, `change --format
  json`, `triage candidates --json`, `agent lifecycle begin --json`, `agent status --json` and
  `provenance trace --json`.
- Line formats are parsed only for `conflicts --short` (`<path>:<line>:<kind>`) and any command
  found without JSON during validation.
- Fixtures live in `intent-atomic/tests/fixtures/v<version>/<subcommand>/*.{json,txt}`. They
  are captured against the pinned binary by the proposed scripts/capture-atomic-fixtures.sh.

**`AtomicRepoLocks`** (`src/locks.rs`) has the same shape as `WorktreeLocks` (async
`with_lock(path, fut)`), keyed by the canonical Atomic repo path.

- **Every mutating subcommand Intent runs** goes under it: `add`, `record`, `unrecord`,
  `revise`, `restore`, `insert`, `view create|split|switch|delete`, `sandbox create`,
  `git import`, `git push`, and `agent lifecycle begin|end|abandon`.
- Reads run unlocked. If a read fails with a redb lock error, retry once after 200 ms (A9).
- This serialises **Intent's** writers in-process. It cannot order the hook recorders, which
  run inside provider processes and write to the same redb (D6). The gap-filler is therefore
  sequenced on Atomic-side run state (§6.6.3, A26), and V10 load-tests hook writers from
  several workspaces at once. Whether to share one canonical repo per source repo is Q9.

**`AtomicVcs: WorkspaceVcs`** (`src/backend.rs`). Mappings are checked against 0.19.1 help;
items marked Ax need contract validation.

| Trait method | Atomic command | Notes |
|---|---|---|
| `status` | `atomic status --json` in the sandbox | `staged=false` always. `ahead_of_trunk` = changes in the view but not in the trunk view; `behind_trunk` = trunk changes not in the view, computed from the `log --view … --format json` set difference (A4). `recorded_unpublished` comes from `atomic_turn_record` rows where `published_git_sha IS NULL`. |
| `diff_working` | `atomic diff --json --untracked [FILES]` | `DiffScope::Staged` returns `[]`. |
| `diff_change` | `atomic change <hash> --format json --show-hunks --full-hash` | Hunks mapped to `FileDiffWithHunks`. |
| `show_file` | `RevSpec::Head`/`Index` → recorded state of the view (A5); `Change(h)`/`Parent(h)` → state read at that change | |
| `history` | `atomic log --view ws-<id> --format json [-n] [--path]` | The boundary is the view's fork state (`atomic_base_state`); `include_older` lists the trunk view up to that state. |
| `change_details` | `atomic change <hash> --format json --show-deps` | Dependencies fill `VcsChange.dependencies`. |
| `record` | first `atomic add -- <untracked paths among FILES>` (`record` skips untracked files unless `-a`/`--all`), then `atomic record --ai-assisted --ai-provider P --ai-model M --ai-session-id <providerSessionId> --ai-tool intent -m MSG --skip-binary -- <FILES>` | `StagedIndex` → `VcsUnsupported` (no index). The native AI flags let Atomic's own provenance queries see gap-fill records (`--ai-input-tokens`, `--ai-output-tokens` and `--ai-cost-usd` too, when the session reports them). Trailers (`Agent-Id:`, `Linked-Note-Id:`, `Intent-Turn:`, `Intent-Session:`) go into the message body so they survive into the Git projection. Path scoping is A11; binary policy is in §9. |
| `discard` | `atomic restore -- <FILES>` | Under the repo lock. |
| `undo` | for each change, newest first: `atomic unrecord <hash>` (`--dry-run` for preview); for `revert-files` mode, also `atomic restore -- <paths of those changes>` | `unrecord` takes **one** change per call. A dependents error → `UndoOutcome::HasDependents(Vec<ChangeId>)` (A12b). Whether unrecord leaves the edits in the working copy is A13. |
| `integrate_trunk` | `atomic git import --incremental --branch <baseRef>` in the canonical repo, then `atomic insert view <baseRef> --to-view ws-<id> --deps --dry-run`, and if clean the same without `--dry-run` | Conflicts → `IntegrateOutcome::Conflicts(Vec<ConflictInfo>)`, applied only with `allow_conflicts` (`--allow-conflicts`). |
| `publish` | in the workspace's publish checkout (D14), synced to `ws-<id>`: `atomic git push -b <branch> --remote origin -m <msg>` | `git push` commits on the *current* Git branch, which in the publish checkout is the publish branch. `-b` only changes the remote destination. Returns the Git SHA from `git rev-parse` of the pushed ref. Never passes `--allow-conflict-markers`. A7 must prove: (i) successive publishes fast-forward; (ii) the first parent is `base_commit_sha`, or the remote tip on a converted branch; (iii) after `vcs.syncTrunk` the trunk tip is an ancestor of the next publish; (iv) the canonical trunk ref never moves. |
| `history_identity` | `sha256(view state hash ‖ remote publish-branch tip)` | Omitted on any error, as in §5.18. |

**`AtomicProvisioner: VcsProvisioner`**: see §6.5. **`AtomicLeaseManager`** (`src/lease.rs`):
see §6.6.

### 6.4 Store: additive migration `NNNN_workspace_vcs.sql`

`NNNN` is the next free number, ≥ `0191` (the newest at the pinned intentd is `0190`); check
again at implementation time. The change is additive only.

```sql
ALTER TABLE workspace ADD COLUMN vcs_kind TEXT NOT NULL DEFAULT 'git'
  CHECK (vcs_kind IN ('git','atomic'));
ALTER TABLE workspace ADD COLUMN atomic_repo_key   TEXT;   -- FK-like to atomic_repo.repo_key
ALTER TABLE workspace ADD COLUMN atomic_view       TEXT;   -- 'ws-<workspaceId>'
ALTER TABLE workspace ADD COLUMN atomic_base_state TEXT;   -- Atomic state hash at fork

CREATE TABLE atomic_repo (
  repo_key            TEXT PRIMARY KEY,   -- opaque hash of (provider, host, owner, repo) or of canonical local path
  canonical_path      TEXT NOT NULL UNIQUE,
  source_repository_path TEXT,            -- local repo or repo cache it was imported from
  repo_owner TEXT, repo_name TEXT,
  trunk_ref           TEXT NOT NULL,      -- base branch mirrored as shared view
  last_import_git_sha TEXT,
  import_state        TEXT NOT NULL CHECK (import_state IN ('importing','ready','failed')),
  atomic_version      TEXT NOT NULL,
  created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);

CREATE TABLE atomic_turn_record (         -- derived index; Atomic is the source of truth
  change_hash  TEXT NOT NULL,
  workspace_id TEXT NOT NULL REFERENCES workspace(id) ON DELETE CASCADE,
  view         TEXT NOT NULL,
  agent_id     TEXT, session_id TEXT, turn INTEGER, message_id TEXT,
  provider TEXT, model TEXT,
  source       TEXT NOT NULL CHECK (source IN ('hook','intent')),  -- who recorded it (D6)
  atomic_session TEXT,                      -- external session id in the Atomic ledger
  message      TEXT NOT NULL,
  files        TEXT NOT NULL DEFAULT '[]', -- JSON [{path,additions,deletions}]
  additions INTEGER NOT NULL DEFAULT 0, deletions INTEGER NOT NULL DEFAULT 0,
  recorded_at  TEXT NOT NULL,
  unrecorded_at TEXT,                       -- set on rewind; row kept for audit
  published_git_sha TEXT,
  PRIMARY KEY (workspace_id, change_hash)
);
CREATE INDEX idx_atomic_turn_record_agent ON atomic_turn_record(workspace_id, agent_id, recorded_at);

CREATE TABLE atomic_agent_lease (                     -- one row per managed run
  run_id TEXT PRIMARY KEY,                              -- from `lifecycle begin --json`; keys renew/stop/resume/abandon/end
  workspace_id TEXT NOT NULL REFERENCES workspace(id) ON DELETE CASCADE,
  agent_id TEXT,                                        -- NULL for LEASE_PER_WORKSPACE runs
  lifecycle_session TEXT NOT NULL,                      -- owner session passed to --session
  provider_session_id TEXT,                             -- provider's external session id (session show/fork key, A25)
  view TEXT NOT NULL, executor TEXT NOT NULL, hooks_installed INTEGER NOT NULL DEFAULT 0,
  atomic_version TEXT NOT NULL,                         -- binary the hooks ran (pinned; §6.6.1)
  state TEXT NOT NULL CHECK (state IN ('active','stopped','ended','abandoned')),
  ttl_seconds INTEGER NOT NULL, renewed_at TEXT NOT NULL, created_at TEXT NOT NULL
);

CREATE INDEX idx_atomic_agent_lease_ws ON atomic_agent_lease(workspace_id, agent_id, state);

ALTER TABLE tracked_changes ADD COLUMN change_hash TEXT;   -- set when stage advances via an Atomic record
```

- **Store repos:** `intent-store` gets `atomic_repo_repo.rs`, `atomic_turn_record_repo.rs` and
  `atomic_agent_lease_repo.rs`.
  - They provide CRUD plus `mark_published(workspace_id, hashes, git_sha)` and
    `mark_unrecorded`.
  - `Workspace` row mapping covers the new columns.
  - `set_workspace_vcs_git(id, branch, worktree, checkout_mode)` supports eject.
- **Model:** `Workspace` gains `vcs_kind` plus `atomic: Option<WorkspaceAtomic { repo_key,
  view, base_state }>`. On the wire this is `atomic?: { view, repoKey }`, omitted for Git.
- **New code reading old data:** the default `'git'` means no existing row changes behaviour.
- **Old code reading new data (rollback), corrected against the code:** `intent-store` refuses
  to open a database whose migration ledger records a version newer than the build
  (`intent-store/src/lib.rs:461-485`: "database schema is newer than this intentd build …
  downgrades are …").
  - So once the migration has run, an older daemon cannot open the DB at all. This is true of
    every migration and is not specific to Atomic.
  - The baseline's "old daemon treats an Atomic workspace as Git" scenario cannot happen.
  - Rollback is therefore per-workspace eject plus the flag off (§10.3). A daemon downgrade
    needs a DB backup restore, and release notes must say so.
- **Testing constraint:** per AGENTS.md, a change that adds intent-store migrations must
  **not** be tested through the manual signed-build route, because it irreversibly migrates
  the tester's local DB.

### 6.5 Data mapping and workspace lifecycle

| Intent concept | Git backend (unchanged) | Atomic backend |
|---|---|---|
| Source of history | repo / repo cache | Shared Atomic repo at `<workspacesRoot>/.atomic-repos/<repoKey>/`, holding both `.atomic` and `.git`, imported from the repo cache or the local repo |
| Workspace | branch + linked worktree / cow / direct clone | View `ws-<workspaceId>` + sandbox at the same `worktreePath` (`<root>/<id>/<slug>`) |
| `branch` | working branch | **Publish branch** (same slug generation and `workspace.branchPrefix`), created in Git only at first publish |
| `repository_path` | source repo or checkout | Always the **Git source**: the local repo or the repo-cache path. Never the sandbox, and never `canonical_path`. Path-based `git.*` reads (`getBranches`, `getRemoteUrl`), `proposeSibling`'s `sibling_github_origin` (`intent-acp/src/mcp_server/bindings/workspace.rs:142`, `intent_git::remote::origin_url(repo_path)`) and roll-ups stay correct. |
| `base_ref` | trunk name | Trunk name, mirrored as the shared view `<baseRef>` |
| `base_commit_sha` | fork commit | Git SHA of `<baseRef>` at the last import before the fork; keeps §5.19 boundary semantics meaningful for the projection |
| `atomic_base_state` | — | View state hash at the fork; the history boundary |
| `checkout_mode` | worktree / cow / direct | `cow` if `sandbox create` reflinked, `direct` if it fell back to a plain copy (A2) |
| Commit / auto-commit | `git_agent_commit` at idle, if enabled | Hook-recorded turn changes plus an Intent gap-fill record at every idle with changes (§6.6) |
| `tracked_changes` stages | unstaged → staged → committed → pushed → PR → merged | unstaged → **committed** (recorded, `change_hash` set) → **pushed** (published) → PR → merged; `staged` is never used |
| Checkpoint (`agentSession.checkpoint`) | Git checkpoint codec | "Record now" with message `checkpoint: <label>`; restore = `undo` of the changes recorded after it |
| `proposeSibling` apply | new `workspace.create`; local work never carried over | Same by default. Optional `carryChanges: "copy"` → fork the sibling view from the source view (`view create --from ws-<src>`); `carryChanges: "move"` → `view split ws-<new> <hashes> --from ws-<src>` (Phase 3) |
| Retire | detach worktree, keep branch | End leases, detach sandbox, **keep the view** |
| Revive | fresh checkout of the default branch on a new branch | New sandbox on the **same view**: recorded work comes back, unrecorded work is lost |
| Delete | prune worktree, delete branch if auto-generated | End leases, remove sandbox, `view delete --force ws-<id>` and its agent sub-views (subject to A12), delete the publish branch under the existing rule |

**Record before destroying.** No operation that discards or replaces the sandbox silently
loses work (D7). This covers retire, delete, revive's replacement sandbox, the post-merge view
rebuild, eject and conversion.
1. Require that the agents are stopped.
2. Run a final gap-fill record with `Intent-Recorder: lifecycle`.
3. Stop the workspace scripts and terminals whose cwd is under the sandbox.
4. Proceed.

Revive then restores everything recorded. The only loss left is ignored build artifacts, so
the setup script is re-run.

**Create flow** (`workspace.create` with additive param `vcs?: { kind: "atomic" }`):

1. Check `atomicAvailable && settings.labs.atomicVcs`. Otherwise fail with `-32602`,
   `data.code: "atomic-unavailable"`.
2. Run the existing source resolution (local path, or GitHub cache hydration plus base
   refresh). Reject `plainFolder`, `skipIsolation`, `isRemote`, `repositoryCheckout` (the
   GitLab native path) and a remote `defaultAgentPlacement` with `vcs-unsupported`.
3. Run the eligibility check, `AtomicEligibility::check(repo_path)` (§6.11). On failure return
   `-32602` with `data: { code: "atomic-ineligible", reasons: [...] }`.
4. Under `AtomicRepoLocks(canonical)`, ensure the `atomic_repo` exists.
   - **If absent:** `git clone --local` from the cache into the canonical path, then `atomic
     git import --branch <baseRef>`. `import_state` goes `importing` → `ready`.
   - **If present:** `git fetch` from the cache, then `atomic git import --incremental
     --branch <baseRef>`.
   - **On failure:** a failed import sets the state to `failed`, the create fails with
     `AtomicCli`, and the next attempt retries.
   - **Progress:** import can be long, so emit the existing `workspace.create` progress frames
     under a new phase, `"atomic-import"` (an additive progress phase string).
5. Under the same lock: `atomic sandbox create ws-<id> --dest <worktreePath> --from <baseRef>`
   creates the draft view `ws-<id>` and the sandbox in one step (D12). Then **remove the copied
   `.git`** from the sandbox root (D13, A8). Removing it is cheap because the copy is
   reflinked. Finally, read the view state hash.
6. Persist the row (`vcs_kind=atomic`, `branch_auto_generated=true`). Run the setup script
   unchanged.
7. On failure after step 5, roll back: delete the sandbox dir and run `view delete --force
   ws-<id>`. Both are best effort and logged, mirroring revive's rollback.

**Ownership proof for retire and delete.** `AtomicProvisioner::owns_checkout` requires all of:
- the existing root-anchored `<root>/<id>` check, `resolve_within_root`, unchanged;
- a regular `.atomic-sandbox` file whose recorded repo path canonicalises to
  `atomic_repo.canonical_path`;
- no `.git` at the sandbox root (D13). A `.git` that reappears (for example an agent ran
  `git init`) fails the proof, and retire/delete refuse with the existing ownership error
  instead of deleting an unknown repository.

**`retire.rs` changes.**
- `require_owned_worktree` branches on `ws.vcs_kind` before the Git-worktree and standalone
  checks.
- `retire_supported` is unchanged; it already checks plain folder, remote, `skip_worktree`
  and missing paths.
- `is_standalone_checkout` must return `false` for Atomic, otherwise
  `refuse_standalone_work` and `provision_standalone_revive` would run Git logic. Rename it to
  `is_standalone_git_checkout` and add a `vcs_kind == Git` guard.

### 6.6 Turn recording, Atomic hooks and agent leases (replaces auto-commit for Atomic)

**Recording model (D6, D7).**
- **Primary recorder:** Atomic's own executor hooks. They run inside the provider process
  under an Intent-managed lease that makes the hook session record into `ws-<id>`.
- **Gap-filler:** Intent itself, at every `agent:idle`. It records whatever the hooks did not
  capture: providers without hooks, failed or unhealthy hooks, interrupted turns that the
  hooks did not seal, and edits made outside the provider (terminal, tools).
- **Guarantee:** every turn that changed files produces at least one recorded change in
  `ws-<id>`. Hook-recorded changes also carry Atomic's causal provenance: tool calls classified
  as exploration, commitment or verification, plus session attestations.

#### 6.6.1 Hook installation, scoped to Intent

- **Which providers.** Executors with Atomic integrations: Claude Code, Codex, Antigravity,
  OpenCode, Cursor and Grok. The executor mapping is below.
- **Where.** `atomic agent enable` has no destination or scope flag: the default is
  project-local, `-g` writes `~/.claude/settings.json`, and `--hooks <FILE>` is a manifest
  *source*. So Intent **generates the hook configuration itself** and injects it additively,
  per provider spawn, for Atomic sandboxes only. This is an extra settings layer or a CLI
  override for each provider.
  - The user's provider configuration, auth, plugins and MCP config stay untouched. Swapping
    the whole provider config dir would hide them and is ruled out.
  - The per-provider mechanism is A15.
  - **Hooks only:** never the integration's skills package (`--from-skills`) or `AGENTS.md`,
    which tell agents to run `atomic intent|memory|vault|record` (§6.6.4).
- **Hook process environment.** Hooks run `atomic` inside the provider process, so every
  Atomic-sandbox provider spawn sets:
  - the pinned `atomic` first on `PATH`;
  - the same Atomic config-dir variables as `AtomicCli` (`<daemon data dir>/atomic`).

  Otherwise hooks would resolve the user's binary (another version) or none, and would read a
  different session registry, where Intent's lease is invisible and the hooks behave as
  unleased. V16 asserts that the hook's `atomic --version` equals the pinned version, and the
  lease row records `atomic_version`.
- **What it never does.** It never uses `agent enable -g` (that writes `~/.claude/settings.json`
  in the user's own environment), never uses the default project-local install (that writes
  into the user's repository and would be recorded and published), and never uses
  `--agents-md`.
- **Fallback.** A provider whose hooks can only be installed globally or project-locally gets
  **no hooks**. Intent's gap-filler records its turns, which is correct but carries less
  provenance.
- **User-installed global hooks** (the user ran `atomic agent enable -g` themselves). They fire
  too, but they use the user's binary and config, which breaks version pinning and lease
  visibility. Intent does **not** defer to them.
  - Detect them with `atomic agent status --json`.
  - Where the provider allows it, override them in the injected layer for Intent-spawned
    processes.
  - Otherwise treat them as untrusted: changes not recorded by the pinned binary under the
    lease are found at idle (stray-view detection, §6.6.3) and re-homed.
  - No turn may be recorded twice (V16).
- **Hook health.** Check it with `atomic agent status --json` at boot and when each lease
  begins. Persist the result in `atomic_agent_lease.hooks_installed`. Emit the
  `atomic.hooks_health` telemetry field. Unhealthy hooks are disabled for that process with
  `lifecycle stop --cause hook-failure`, and the gap-filler covers.

#### 6.6.2 Leases: `AtomicLeaseManager` (`intent-atomic/src/lease.rs`)

- **Begin.** Begin a lease only when the provider maps to an executor (see the mapping below).
  `--executor` is **always** passed. When it is omitted, `begin --help` says "any agent inside
  the workdir participates", which would pull in stray or user-global hooks. On agent
  activation in an Atomic workspace:

  ```
  atomic agent lifecycle begin --owner intent --session <agentId> \
    --executor <map(provider)> --view ws-<id> --workdir <sandbox> \
    [--work-item <linkedNoteId>] --json
  ```

  - The TTL is left at the CLI default of 86400 s. `begin --help` calls the lease "crash
    protection, not a session limit"; the baseline's 3600 s would expire during laptop sleep.
  - Persist one `atomic_agent_lease` row per run, keyed by the returned `run_id`.
  - The hook point is the agent activation path in `intent-services/src/agent_manager.rs` (U3).
  - `--work-item` carries the Intent note or task the agent works on, so Atomic's provenance
    links changes to it.
- **Provider session ID.** Capture the provider's external session ID (the ACP or provider
  session handle) on the lease row (`provider_session_id`). `session show` and `session fork`
  key on it, not on Intent's agent ID (A25). If the provider doesn't expose it, read it from
  `lifecycle end --json` or `session show --json` (no ID), filtered by workdir.
- **Renew** with `lifecycle renew --run-id R` at **every turn start** and from a 20 min daemon
  timer.
- **Turn-start gate.** Before an Atomic-workspace agent accepts a prompt, its run must be
  `active` (`lifecycle status --json`). Otherwise, begin a new run on the same view and workdir
  with a new `run_id` **before** the prompt is forwarded. Unleased hooks "fork their usual
  per-session view", so a provider that outlives its run would record outside `ws-<id>`.
- **Stop** on agent stop: `lifecycle stop --run-id R --cause
  user-requested|process-exited|hook-failure|system-shutdown`. Use `system-shutdown` at daemon
  shutdown and `hook-failure` when the health check fails.
- **Resume** on re-activation of a stopped run. `lifecycle resume` fences prior writers. If the
  run has expired or is terminal, `begin` a new run.
- **End** on agent delete, workspace retire or workspace delete: `lifecycle end --run-id R
  --json`. Index the summary's sessions, changes and views.
- **Boot reconciler** (`AtomicLeaseManager::reconcile`). It runs at daemon start, and must
  finish before Atomic workspaces accept turns.
  - It runs `lifecycle status --json`.
  - For each `owner=intent` run with no live provider process, it calls `stop --cause
    process-exited` and marks the row `stopped`, so reactivation resumes cleanly.
  - A run whose provider survived the restart is renewed and re-adopted (Q13).
  - Rows with no upstream run are marked `ended`.
  - This prevents a second active run on the same view and workdir after a crash (the
    unverified A10 case). V22 covers it.
- **Executor mapping** (table in `lease.rs`): `claude*` → `claude-code`, `codex*` → `codex`,
  `antigravity`/`agy` → `antigravity`, `opencode` → `opencode`, `cursor` → `cursor`, `grok` →
  `grok`. Any other provider gets **no lease and no hooks**, and Intent's gap-filler records
  with `--ai-provider`.
- **Failures never gate execution.** If `lifecycle begin` fails, the agent runs **without
  hooks**: the provider is spawned (or re-spawned at the turn-start gate) without the hook
  layer, and Intent's gap-filler records every turn.
- **Many agents on one shared sandbox.** Several runs on one view and workdir are unverified
  (A10). The fallback, behind const `LEASE_PER_WORKSPACE`, is one run per workspace with
  `--session ws-<id>` and `agent_id = NULL`. Per-agent attribution then comes from provider
  session IDs plus the gap-filler's flags and trailers.

#### 6.6.3 The turn boundary at `agent:idle`

The work lives in a new module, `intent-services/src/turn_record.rs`.
`spawn_auto_commit_loop` stays the only `agent:idle` subscriber, so there is no parallel path.
`handle_agent_idle_auto_commit` loads the workspace once. When `vcs_kind == Atomic` it calls
`self.record_turn(&event, &session, &ws)`, which runs these steps:

1. **Finish-reason gate.** Act on **every** finish reason, including `cancelled` and `error`.
   Non-normal turns get the message suffix ` (interrupted)`. Rewind needs a boundary at every
   turn; without one, an unrecorded partial edit would be swept into the next turn's record.
   - Still skip when `session.skip_auto_commit` is set, since that flag means "do not write
     history for me".
   - Plain folders and missing checkouts skip exactly as they do today.
2. **Seal interrupted turns.** On `cancelled` or `error` with a live run, run `atomic agent
   lifecycle abandon --run-id R --json` to seal the pending hook turn.
   - A18 must establish two things: whether the sealed turn becomes a recorded change, and the
     run's state afterwards.
   - If the run is terminal after `abandon`, the turn-start gate (§6.6.2) begins a new run
     before the user's next prompt in the same provider session. If it is not terminal,
     nothing more is needed.
   - If `abandon` does not record the edits, step 5 does.
   - V16 covers cancel-then-continue.
3. **Wait for the run to settle.** Hooks are cross-process writers that `AtomicRepoLocks`
   cannot order. So the gap-filler proceeds only when Atomic-side state shows no pending or
   unsealed turn for this run, from `lifecycle status --json` or the session ledger (A26). It
   also proceeds once `abandon` or `stop` has returned, or after a bounded wait: 3 polls at
   1 s, extendable per provider (A19).
4. **Index hook records.**
   - Read this run's ledger with `atomic session show <providerSessionId> --json`, or `atomic
     log --view ws-<id> --format json` filtered by session.
   - Insert any change not yet indexed into `atomic_turn_record` with `source='hook'`. The
     primary key on `(workspace_id, change_hash)` makes this idempotent.
   - **Hook records are not attribution-filtered.** They can contain any file that was dirty in
     the workdir: another agent's in-flight edits, terminal edits, setup output. So advance
     **every** `tracked_changes` row whose path appears in an indexed change, whichever agent
     owns it, to `committed` with `change_hash`.
   - When a change's files go beyond the leased agent's rows, emit
     `vcs.record.attribution_mismatch`.
   - **Stray-view detection.** If a change from this provider session landed in a view other
     than `ws-<id>` (lease expired, unleased hooks, user-global hooks), re-home it with `atomic
     insert change <h> --to-view ws-<id> --deps`, index it, and emit `vcs.record.stray_view`.
5. **Gap-fill.**
   - **Paths:** the agent's `tracked_changes` rows still at `unstaged`, intersected with the
     files from `atomic status --json`. This is the same rule as commit-set mode 3. If the set
     is empty, skip quietly.
   - **Message:** deterministic, no LLM call: `"<task title | agent name>: turn <n>"`, a body
     with the first 200 characters of the user prompt, and the trailers `Agent-Id`,
     `Linked-Note-Id`, `Intent-Turn`, `Intent-Session` and `Intent-Recorder: gap-fill`.
   - **Record:** `AtomicVcs::record` (which runs `atomic add` first for untracked paths) with
     `AiMeta { provider: session.provider, model: session.model, session_id: agent_id, turn }`,
     `--ai-session-id` and `--skip-binary` (§9). It runs under `AtomicRepoLocks`, inside
     `spawn_blocking`.
   - **Indexing:** the record goes into `atomic_turn_record` with `source='intent'`.
6. **On success,** in one store transaction, write the `atomic_turn_record` rows and the
   `tracked_changes` advances. After the transaction, publish `vcs:record` and
   `changes:git-status` (the projection) and evict the status cache.
7. **On failure.**
   - Lock timeout or CLI error: warn-log with `subcommand`, `exit_code` and `elapsed_ms`. The
     paths stay `unstaged` and the next idle picks them up. There is no retry loop.
   - CLI killed by timeout: run `atomic log --view ws-<id> -n 1 --format json`. If the newest
     change carries this turn's `Intent-Turn` trailer, treat the record as done and index it.
     Otherwise leave the paths unrecorded.

**Race between hooks and the gap-filler.** Step 3 sequences the gap-filler after the hook run
has settled, which is Atomic-side state, not an in-process lock. A hook record that still lands
after the gap-filler ran produces a change whose paths are already `committed`. It is indexed
on the next idle and flagged in telemetry as `vcs.record.late_hook`. V16 asserts that this case
does not occur with healthy hooks.

**Duplicate or out-of-order `agent:idle` events.** Indexing is keyed by change hash, and the
gap-fill only finds paths still `unstaged`. A duplicate event therefore finds nothing and is
skipped.

**User-initiated record** (`vcs.record`, or `git.agentCommit` with `userRequested`) takes
explicit paths, or the "all unrecorded" set (`RecordPaths::Explicit(all status files)`). Mode
2 (`StagedIndex`) doesn't exist in Atomic, so it maps to "everything unrecorded that is not
locked by an active agent" (`file-tracking.getAgentLocks`). These records have
`source='intent'` and carry no AI metadata unless an agent made the request.

**Agent locks** (`file-tracking.getAgentLocks`). For Atomic workspaces, `autoCommitEnabled` is
reported as `true`, because turn recording is always on. The lock rule is otherwise unchanged,
which stops a manual record from racing the agent's turn record.

**`ws.git.commit` (MCP) and `git.agentCommit` in Atomic workspaces** map to `record`. The
auto-commit-disabled gate (`assert_agent_commit_allowed`) is skipped for Atomic (D7). Document
this in git.md and `mcp-bindings.md`.

#### 6.6.4 Agent-facing instructions and environment (D13)

Add an Atomic variant to the versioned agent-instruction resources
(`intent-services/resources/agent-instructions/<next version>/`). It is selected when
`vcs_kind == Atomic` and tells agents:

- This workspace has **no Git repository**. History is managed by Atomic, and every turn is
  recorded automatically.
- Do not run `git` commands. They fail with "not a git repository".
- Do not run mutating `atomic` commands: `add`, `record`, `unrecord`, `revise`, `insert`,
  `view`, `sandbox`, `git push`, `restore`, `stash`, `tag`, and, pending Q10, `intent`,
  `memory` and `vault`.
- To inspect history and changes, use `atomic status|diff|log|change` (read-only) or the
  `ws.vcs.status` / `ws.vcs.changes` MCP tools (§6.7).

**Enforcement.**
- Instructions alone are not enough. ACP tool-call inspection counts mutating `atomic` runs by
  agents in `agent.atomic_mutation_attempted`, alongside `agent.git_command_failed`.
- At idle, any change in `ws-<id>` whose recorder is neither the leased hook (pinned binary,
  this run) nor Intent is flagged in the UI and in telemetry.

Setup scripts and agent processes get the environment variables `INTENT_VCS=atomic`,
`INTENT_BASE_REF` and `INTENT_BASE_COMMIT_SHA`. Build tools that stamp versions from
`git rev-parse` can read these instead (§9, §11.2).

### 6.7 Protocol: capabilities, `vcs.*`, `atomic.*`, events

**Capabilities** are advertised next to `boundedReads` and `nativeReview` in the capability JSON
at `intent-transport/src/client.rs:118`.
- `vcs: 1` is always advertised by daemons that have the seam.
- `atomic: 1` is advertised only when `AtomicAvailability::Available && labs.atomicVcs &&
  !windows`. Otherwise it is omitted, and `atomicUnavailableReason?:
  "flag-off"|"binary-missing"|"version"|"platform"` is included for diagnostics.
- **The capability is dynamic.** Today `server_json(has_display, os, arch, version, …)` in
  `intent-transport/src/client.rs` has no access to `Services` or settings. So pass an
  `AtomicAvailability` snapshot into it. Toggling `labs.atomicVcs`, or the binary appearing or
  disappearing, emits a `capabilities:changed` event carrying the new `atomic` fields.
  `client-hello.md` documents this. Clients without the event re-read capabilities on
  reconnect.

**Workspace wire:** add `vcsKind?: "atomic"` (omitted for Git) and `atomic?: { view, repoKey }`.
`workspace.create` gets the additive param `vcs?: { kind }`.

**Proposed doc file docs/protocol/methods/vcs.md.** The §5.x number is assigned when the doc is
written. Every method requires `workspaceId` except eligibility.

| Method | Params | Result | Kinds |
|---|---|---|---|
| `vcs.status` | workspaceId, forceRefresh? | `VcsStatus` (camelCase) | both |
| `vcs.changes.list` | workspaceId, view?, agentId?, limit? (≤200), nextToken?, includeOlder? | `{ changes: VcsChange[], boundary, nextToken, historyIdentity? }` | both (Git: commits mapped) |
| `vcs.changes.show` | workspaceId, changeId, paths?, maxBytes?, nextToken? | bounded per-file hunks; same packing and `truncatedReason` as `git.diffs` | both |
| `vcs.record` | workspaceId, message, paths?, userRequested: true | `{ changeId, files, fileCount }` | both (Git: = agentCommit) |
| `vcs.publish` | workspaceId, message?, branch? (rename allowed before first publish), remote? (default `origin`) | `{ branch, gitSha, pushed: true, publishedChanges: string[] }` | atomic (Git: `vcs-unsupported`; use the existing push) |
| `vcs.syncTrunk` | workspaceId, apply?: boolean, allowConflicts? | `{ imported: number, preview: InsertPreview, applied: boolean, conflicts? }` | atomic |
| `vcs.eject` | workspaceId | `{ workspaceId, branch, worktreePath }` | atomic (§10.3) |
| `vcs.atomic.eligibility` | repoPath? \| githubUrl? | `{ eligible, reasons: EligibilityReason[] }` | n/a |
| `atomic.views.list` | workspaceId | `{ views: [{ name, scope: "draft"\|"shared", agentId?, changeCount }] }` | atomic |
| `atomic.insert.preview` / `atomic.insert` | workspaceId, fromView, toView, changeIds[], withDeps?, allowConflicts? | `InsertPreview { changes[], addedDeps[], conflicts[] }` / `{ applied: string[], conflicts[] }` | atomic |
| `atomic.unrecord` | workspaceId, changeIds[], mode: "keep-files"\|"revert-files" | `{ unrecorded: string[] }`; dependents → `-32602`, `data: { code: "has-dependents", dependents }` | atomic |
| `atomic.conflicts.list` / `atomic.conflicts.resolve` | workspaceId / workspaceId, path, resolution: "ours"\|"theirs"\|{ content } | `{ conflicts: [{ path, sides: [{ changeId, agent?, excerpt }] }] }` / `{ ok, changeId }` (the resolution is written to the file and recorded as a change) | atomic |
| `atomic.provenance.trace` | workspaceId, changeId | `{ entries: [{ changeId, agent?, provider?, model?, sessionId?, turn?, recordedAt, signed: boolean }] }` (from `provenance trace <hash> --json`) | atomic |
| `atomic.provenance.forPath` | workspaceId, path, line? | as above, for the changes touching `path` (`log --path <p> --format json`); `line` is honoured only if A14 holds | atomic |
| `atomic.provenance.export` | workspaceId, changeId, signed? | `{ jsonld: string }` (`provenance trace --json [--sign]`; bounded at 480 KB, otherwise `truncated`) | atomic |
| `atomic.triage.candidates` | workspaceId, target? (default baseRef) | `{ candidates: [{ changeId, risk, summary, files }] }` (`triage candidates ws-<id> --into <target> --json`) | atomic |
| `atomic.triage.review` | workspaceId, changeIds[] | `{ walkthrough: [{ title, body, changeIds, files }] }` (`triage review`) | atomic |
| `atomic.session.explain` | workspaceId, agentId, turn? | `{ summaries: [{ turn, changeId, reasoning }] }` (Phase 3; `agent explain <atomicSession> --turn N --save`; uses Atomic's Claude CLI model, so it is cost-bearing and runs only on explicit user action) | atomic |
| `atomic.session.fork` | workspaceId, agentId, atTurn, mode: "sibling-workspace" | `{ workspaceId, agentId }` (Phase 3). Start a new provider session for a new agent first, then run `session fork <providerSessionId> --at-turn N --child <newProviderSessionId>`. Both IDs are the providers' external session IDs, not Intent agent IDs (A25). Then create a new view holding the changes ≤ N (A17). | atomic |

**Errors and routing.**
- Any `atomic.*` method called on a Git workspace returns `-32602 vcs-unsupported`. Malformed
  params return `-32602`, and CLI failures return `-32603` with a redacted message.
- `intent-transport/src/protocol.rs` dispatches the new methods, adds the large reads
  (`vcs.changes.show`, `atomic.provenance.export`) to the bounded-read routing list, and keeps
  the existing workspace-membership checks.
- Writes require a host member or admin, as for `git.agentCommit`. Guest collaborators are
  refused.

**Legacy `git.*`, `accept-changes.*` and `file-tracking.*` on Atomic workspaces:**

| Method | Behaviour |
|---|---|
| `git.status`, `git.changes` | Projection from `VcsStatus` (`staged: false`; `hasUpstream` is true once published) |
| `git.diffs` | `staged: true` → `[]`; otherwise `diff_working`; with `commitHash` → `diff_change` |
| `git.commits`, `git.commitDetails`, `file-tracking.loadCommits` | Atomic changes mapped (`hash` = change hash; `sha` = first 7 characters) |
| `git.showFile(Chunk)` | `show_file`; ref `":0"` → Head |
| `git.numstat`, `git.branchDiff` | Computed against `atomic_base_state` |
| `git.stage` / `unstage` / `stageHunk` / `unstageHunk` | `-32602 vcs-unsupported` |
| `git.discard` | → `discard` |
| `git.agentCommit`, `git.commit` | → `record` (§6.6) |
| `git.push` | → `vcs.publish` |
| `git.fetch` | → `vcs.syncTrunk` with `apply: false` |
| `git.renameBranch` | Allowed until the first publish, then `vcs-unsupported` |
| `git.pull`, `git.getBranches`, `git.branchStatus`, `git.getRemoteUrl` | Path-based on the source repo; unchanged |
| `git.checkMergeConflicts` | `integrate_trunk` dry run |
| `accept-changes.*` | See §6.8 |

**Events** (§6.5 of the events doc; all carry `workspaceId`):
- `vcs:record { changeId, agentId?, turn?, files, fileCount }`
- `vcs:unrecord { changeIds }`
- `vcs:insert { fromView, toView, applied, conflicts }`
- `vcs:conflict { count, paths }`
- `vcs:publish { branch, gitSha, publishedChanges }`
- `vcs:trunk-synced { imported }`
- `atomic:lease { agentId, state }`

For compatibility the daemon **also** emits `changes:git-status` (projection) after every Atomic
mutation, `git:push` after a publish, and `git:commit { hash: changeId }` after a record, so
existing frontend consumers refresh. `historyIdentity` keeps the same contract.

**MCP agent bindings** (additive, documented in `docs/protocol/methods/mcp-bindings.md`):
- **Phase 2**, required because agents have no `.git` (D13): `ws.vcs.status`, `ws.vcs.changes`
  and `ws.vcs.diff`.
- **Phase 3:** `ws.atomic.views`, `ws.atomic.insertPreview` and `ws.atomic.provenance`.

Agents can then inspect their own turn history and sibling views. Write bindings (`insert`,
`unrecord`) are deferred to Phase 3 and need an explicit product decision. `check-mcp-bindings`
is advisory, and the auto-bump regenerates its index.

**Deprecating and removing `git.*` (Phases 7–8, D11).**
- **Atomic workspaces:** by Phase 4, every Atomic-workspace frontend surface calls
  `vcs.*`/`atomic.*` directly. **Git workspaces stay on `git.*` until Phase 7 converts them.**
  `vcs.*` deliberately has no Git staging, fetch, rename or pull equivalents, so making the FE
  "`vcs.*` for both backends" would be wire churn for a backend about to be deleted. (This
  corrects the earlier draft.)
- **Telemetry:** a per-method `git.*` call counter, tagged with the client version, tracks
  remaining use.
- **Phase 8, breaking protocol release:** most of `git.*` is removed. The Git-interop reads on
  **source repos** that Atomic workspaces still need move to `vcs.source.*` aliases, which land
  additively before removal:
  - `git.clone` → `vcs.source.clone`
  - `git.getRemoteUrl` → `vcs.source.remoteUrl`
  - `git.getBranches` → `vcs.source.branches` (BranchSelector's base-ref picker)
  - `git.branchStatus` → `vcs.source.branchStatus`

  `git.pull` on Atomic is `vcs.syncTrunk`. Also removed:
  `accept-changes` staging params, `file-tracking.stage`/`unstage`, and the `git:*` events
  return `-32601 Method not found` or stop being emitted.
- **Precedent:** this follows the 18.0 retirement pattern in `versioning.md`: a major version
  bump, a capability removal, and a documented surface count. Clients gated on the `vcs`
  capability since Phase 0 keep working.

### 6.8 Forge and PR path; rewriting accept-changes

`SourceControl` is unchanged. `pr.refresh`, the PR monitor (`intent-services/src/pr_monitor.rs`),
the merge queue and the workspace-list PR roll-up all key on `workspace.branch`, which holds the
publish branch, so they work as soon as something is published.

**`accept_changes.rs` rewrite.** Split the action pipeline into `AcceptPipeline` steps that call
`vcs_for(ws)`.

| Action | Git | Atomic |
|---|---|---|
| `commit` | unchanged | `record` (explicit `files`, or all unrecorded; `stageUnstaged` is ignored) |
| `push` | unchanged | `publish`. The LLM generates the message here: move `generate_auto_commit_message` into `publish_message.rs` and reuse its timeout, cool-down and fallback. On success set `atomic_turn_record.published_git_sha` and move `tracked_changes` to `pushed`. |
| `create-pr` | unchanged | Unchanged: `SourceControl::create_pr` with head = the publish branch. Needs a prior publish; otherwise the step fails with "publish first", or chains through `pushAfterCommit`. |
| `merge` | unchanged | Unchanged forge merge, then `vcs.syncTrunk` (import) |
| `undo-commit` | unchanged | `undo` of the given `upToCommitHash` range; a dependents error fails the step |
| `undo-push` | unchanged | Step `failed` with `vcs-unsupported`: rewriting a published branch needs force-push semantics the bridge doesn't define |
| `reset-to-trunk` | unchanged | `undo` of all unpublished view changes with `revert-files` |
| `rebase-onto-trunk` | unchanged | `integrate_trunk`: sync, then insert trunk changes into the view |

- `getStatus` adds `vcsKind` and `unrecordedCount` (additive fields on `WorkspaceGitStatus`),
  and `stagedCount` is `0`.
- **Qualified native review** (the branch where `review` is present) is refused for Atomic with
  the existing sanitised `-32003` / `forbidden` "Repository review unavailable", because it
  binds Git source refs and SHAs.
- **Provenance in the PR body** (Phase 3, optional). On `create-pr` for an Atomic workspace,
  append a short attestation summary (agents, models, turn count, and whether signed
  provenance is available) from `atomic agent attest` / `atomic_turn_record`. It goes in a
  collapsible block, never the breaking-change footer token.

**The post-merge duplication problem (critical).** A GitHub squash or rebase merge creates new
Git commits without bridge binding headers. Importing them into the trunk view creates changes
that duplicate the workspace's changes semantically. A later `insert` of trunk into the view
would then conflict or apply the edits twice. Mitigation:
- After a merge, `vcs.syncTrunk` **marks the workspace "merged"** (from the PR status). Its next
  integrate becomes a view rebuild:
  1. create a new view `ws-<id>-<n>` from the trunk view;
  2. insert only the changes recorded **after** the last publish;
  3. swap `atomic_view`;
  4. recreate the sandbox at the same path, under the archive fence;
  5. keep the old view for audit.
- The accept-changes merge step for Atomic defaults `mergeStrategy` to `merge` (keeping the
  original commits and bindings) **only if A22 shows** that 0.19.x `git push` emits binding
  headers and `git import` recognises them. Binding headers belong to the *proposed* Causal
  Bridge. If A22 fails, the view rebuild becomes unconditional after **every** merge strategy,
  and the repository's merge strategy is left alone.
- **Simpler rebuild candidate (A23).** Instead of recreating the sandbox at the same path, run
  `atomic view switch --stash ws-<id>-<n>` inside the sandbox (`view switch` has `-s/--stash`
  in 0.19.1). This keeps the path, ignored build artifacts and running terminals. Use it if A23
  confirms the switch is sandbox-scoped. Otherwise use the record-first recreate (§6.5).
- Test V9 covers all three strategies.

### 6.9 Remote nodes and the hub

**Phases 2–4.** In Atomic workspaces, these are refused with `-32602`, `data.code:
"vcs-placement-unsupported"`:
- `workspace.create` with a remote `defaultAgentPlacement`;
- model create or delegate with `placement: remote`;
- isolated delegation.

The check lives in the placement resolver (the intent-services agent/node placement path),
keyed on `ws.vcs_kind`. `intent-svc-transfer`, `-remote` and `-runtime` never see Atomic
workspaces.

**Phase 5 design direction.** This needs its own plan, written once the hub contract is
implemented for Git.
- Per-agent isolated **views**: `sandbox create ws-<id>--agent-<agentId> --from ws-<id>`
  replaces the "inherited baseline / executionBase" machinery.
- Merge-back is `atomic insert` from the child view into the parent view. Child-owned changes
  are explicit, so no synthetic-baseline normalisation rules are needed.
- Node transport uses Atomic remotes (`atomic remote` / push / pull of changes) over the node
  link instead of `git-remote-intent`.
- Checkpoints become recorded changes on a hidden view `ckpt-<agentId>-<rev>`.
- Publication normalisation becomes trivial, because only shared-view changes go through the
  bridge.
- Gate: the Atomic remote protocol is documented, and local isolated views have shipped in
  Phase 3.

### 6.10 Frontend

**Types and client.**
- `shared/types.ts`: add `Workspace.vcsKind?: 'git' | 'atomic'`, `Workspace.atomic?: { view:
  string; repoKey: string }` and `CreateWorkspaceRequest.vcs?: { kind: 'atomic' }`.
- New `shared/types/vcs.ts`: `VcsStatus`, `VcsChange`, `ChangeAgent`, `InsertPreview`,
  `ConflictInfo`, `ProvenanceEntry`, `TriageCandidate`, `TriageStep`, `EligibilityReason` (a
  closed union matching the daemon) and `VcsCapabilities`.
- `lib/client/app-client.ts`: a new `VcsClient` interface and `AppClient.vcs: VcsClient`.

  ```ts
  interface VcsClient {
    status(ws, opts?): Promise<VcsStatus | null>;
    changes(ws, opts?): Promise<{ changes: VcsChange[]; nextToken: string | null; historyIdentity?: string }>;
    showChange(ws, changeId, opts?): Promise<DiffChunk[]>;
    record(ws, p: { message: string; paths?: string[] }): Promise<MutationResult>;
    publish(ws, p?): Promise<MutationResult & { gitSha?: string; branch?: string }>;
    syncTrunk(ws, p?): Promise<{ preview: InsertPreview; applied: boolean } | null>;
    eject(ws): Promise<MutationResult>;
    eligibility(p: { repoPath?: string; githubUrl?: string }): Promise<{ eligible: boolean; reasons: EligibilityReason[] } | null>;
    // atomic.*
    unrecord, insertPreview, insert, conflicts, resolveConflict, provenance, provenanceForPath,
    exportProvenance, triageCandidates, triageReview, forkSession
  }
  ```

- New `lib/client/live/live-vcs-client.ts`, in the same style as `LiveGitClient`:
  - validate and normalise untrusted payloads;
  - fold reads to `null` / `[]`;
  - use `runMutation` for writes;
  - reuse `requestAllDiffPages` for `showChange`.
- A mock in `mock-app-client.ts`.
- **Capability plumbing:** expose `vcs` and `atomic` from the server-hello capability store,
  wherever `boundedReads` and `nativeReview` are read today; locate this at implementation
  time with a grep for `boundedReads`. Add `lib/vcs/vcs-mode.ts` with `isAtomicWorkspace(ws)`
  and `atomicAvailable(state)`.
- **Store:** a new slice `store/renderer/slices/vcs/` (`vcs-slice.ts`, `vcs-types.ts`,
  `sagas/vcs-events-saga.ts`).
  - It holds per-workspace `changes`, `conflicts`, `views` and `lastPublished`.
  - It consumes `vcs:*` events.
  - It uses `historyIdentity` with the same reject-stale rules as the commits list.

**Code that bypasses the seam must branch on `vcsKind`:**
- `git-write-saga.ts`: stage/unstage dispatches become no-ops with a toast for Atomic. This
  shouldn't happen, because the UI hides those controls.
- `git-bridge-seeder.ts`: push → `vcs.publish`; fetch → `vcs.syncTrunk({ apply: false })`;
  renameBranch is allowed before the first publish.
- `features/git/git.client.ts` `getHistory`: route Atomic workspaces through
  `appClient.vcs.changes`.
- `pr-workflow-saga.ts` (`git.commit` L115, `git.pull` L206): commit → record; pull stays
  path-based on the source repo.

**Screens:**

| Screen | Change |
|---|---|
| `ChatChangesPanel.svelte`, `UnifiedMultiStageDiff.svelte` | Atomic sections: **Unrecorded** (category `unstaged`), **Recorded** (`committed`, grouped by turn with agent/model chips and a "Rewind to here" action → `atomic.unrecord`), and **Published**. The staged section is hidden. The checkpoint button maps to `vcs.record({ message: 'checkpoint: …' })`. `ChangeCategory` is unchanged. |
| `features/accept-changes/` (`NativeSidebarReview.svelte`, `accept-changes.client.ts`, `types.ts`) | Atomic flow: Record → Publish → Create PR → Merge. Stage toggles hidden; `PrepareAcceptFile.staged` ignored. Adds `vcsKind?` and `unrecordedCount?` to `WorkspaceGitStatus`. Native-review entry hidden. |
| `BranchDisplay.svelte` | Shows the view name and the publish branch ("unpublished" before the first publish) |
| `BranchSelector.svelte`, `CompactWorkspaceInitializer.svelte`, `workspace-initialization-submission.ts` | A "Version control: Git / Atomic (Labs)" segmented control, shown when `atomicAvailable`. Calls `vcs.atomic.eligibility` when the repo changes and lists the reasons when disabled. Sends `vcs: { kind: 'atomic' }`. Remembers the last choice per repo in local preferences. |
| `GitWorkspaceSettings.svelte` | Atomic: hide auto-commit, with the explanation "every agent turn is recorded; publish to push". Add an Eject action (§10.3). |
| New `features/atomic-provenance/` (`ProvenanceGutter.svelte`, `ProvenancePopover.svelte`) | Provenance in diff and file viewers via `atomic.provenance.forPath`/`trace`, loaded lazily per hover and cached by `(changeId, path)`. A popover action exports signed PROV. |
| New `features/atomic-triage/` (`TriagePanel.svelte`) | A review tab beside accept-changes: candidates sorted by risk, and walkthrough steps that link to diffs |
| New `features/atomic-insert/` (`InsertChangesDialog.svelte`) | Pick changes from an agent or sibling view → preview (added deps, conflicts) → apply |
| New `features/atomic-conflicts/` (`ConflictPanel.svelte`) | Intent's first conflict UI: per-path sides with agent attribution; resolve with ours / theirs / edit → `atomic.conflicts.resolve` |
| Settings (Labs section) | Toggle bound to the daemon setting `labs.atomicVcs` (via `settings.update`) |
| `messages/*` | New i18n keys for every new string (paraglide) |

The legacy `GitClient` methods keep working against Atomic workspaces through the daemon
projection, so screens not listed above need no change in Phase 2.

### 6.11 Onboarding, eligibility, submodules, binaries, Windows

**`AtomicEligibility::check(repo) -> Vec<EligibilityReason>`**
(`intent-atomic/src/eligibility.rs`) is a fast, read-only, bounded check: ≤ 2 s, cached per repo
and HEAD. Its reasons are a closed set:
- `platform-unsupported` (Windows)
- `submodules` (`.gitmodules` with at least one entry)
- `lfs` (`.gitattributes` containing `filter=lfs`)
- `large-binaries` (any tracked blob > 50 MiB, via a capped `git ls-tree -r -l HEAD`)
- `shallow`
- `object-format` (SHA-256)
- `empty-dirs-significant` (warning only, never blocks)

**Import.** `atomic git import` runs per repo on first use, under the repo lock, with progress
events. Intent's own monorepo is ineligible (submodules) until Phase 5.

**Ignore parity and secret safety (A24).** Atomic has its own ignore mechanism (`add -f` forces
ignored files). Stripping `.git` (D13) also removes `.git/info/exclude`. And hooks record
workdir-wide, so anything Atomic doesn't ignore (`.env`, credentials, `node_modules/`, build
output) would be recorded and then published to GitHub.
- At repo import and at every incremental import, materialise the source repo's
  `.git/info/exclude` and the user's `core.excludesFile` into the canonical repo's Atomic
  ignore configuration. This is repo-level and never committed to the tree.
- A24 validates that nested `.gitignore` files are honoured.
- Eligibility fails with `ignore-parity-unverified` until A24 passes for the pinned version.
- V21 asserts that neither hooks nor the gap-filler record `.env` or `node_modules/` content.

**Submodules (Phase 5).** The primary root moves to Atomic, and submodules stay Git workspace
roots (`workspace_git_root`, `source: auto`). Gitlink bumps are recorded as ordinary Atomic
changes to the gitlink path. This needs the bridge to project gitlinks faithfully. The known
behaviour, "recorded as gitlinks, not recursed", is enough for pin bumps. Validate with V12.

**Windows.** `atomic` is never advertised, because the bridge is Unix-only. Atomic workspace rows
in a synced DB opened on Windows use `FrozenAtomicVcs`.

### 6.12 Packaging

- Pin the version in the proposed packages/intentd/packaging/atomic-version.txt. The packaging dirs
  `deb/`, `homebrew/`, `libexec/` and `e2b/` exist.
- Download and verify (sha256) the binary in those packaging scripts, and into cloudlands-fe
  `resources/bin/` for desktop builds. On macOS the existing notarisation path signs it, and
  `apple-ticket-retry` already handles stapling flakiness.
- Add the Apache-2.0 notice to the bundled third-party licences.

---

## 7. File-by-file impact

### 7.1 intentd (`packages/intentd/`)

| File | Change | Why | Depends on |
|---|---|---|---|
| `crates/intent-core/src/vcs.rs` (new) | `VcsKind`, `ChangeId`, `RevSpec`, `VcsCapabilities`, `VcsStatus`, `VcsFileEntry`, `VcsChange`, `ChangeAgent`, `InsertPreview`, `ConflictInfo`, `From<&VcsStatus> for GitStatus` | neutral types (D4) | — |
| `crates/intent-core/src/model.rs` | `Workspace.vcs_kind` (serde default, skip-if-git), `Workspace.atomic: Option<WorkspaceAtomic>`; `WorkspaceCreate.vcs: Option<VcsRequest>` | data mapping | vcs.rs |
| `crates/intent-core/src/error.rs` | variants `VcsUnsupported`, `AtomicUnavailable`, `AtomicIneligible { reasons }`, `AtomicCli`; JSON-RPC mapping with `data.code` | error contract | — |
| `crates/intent-core/src/events.rs` | constants `VCS_RECORD`, `VCS_UNRECORD`, `VCS_INSERT`, `VCS_CONFLICT`, `VCS_PUBLISH`, `VCS_TRUNK_SYNCED`, `ATOMIC_LEASE` | events | — |
| `crates/intent-core/src/settings_file.rs` (or wherever settings are defined) | `labs.atomicVcs: bool` (default false), `vcs.atomic.binaryPath: Option<String>` | rollout | — |
| `crates/intent-vcs/` (new crate) | `WorkspaceVcs`, `VcsProvisioner`, `VcsCtx`, request/outcome types, `GitVcs`, `GitProvisioner` | seam | intent-core |
| `crates/intent-git/src/{commit,reset,refs}.rs` | absorb the git2 code now in `accept_changes.rs` / `git_ops.rs` as pub functions | owned by GitVcs | — |
| `crates/intent-git/src/auth.rs` | expose `github_credential_env(..)` | bridge push credentials | — |
| `crates/intent-git/src/lib.rs` | doc comment: the Git backend behind intent-vcs; no API removal | — | — |
| `crates/intent-atomic/` (new crate) | `cli.rs`, `locks.rs`, `backend.rs` (`AtomicVcs`), `provision.rs` (`AtomicProvisioner`), `lease.rs`, `eligibility.rs`, `parse/*`, `frozen.rs` (`FrozenAtomicVcs`), tests and fixtures | Atomic backend | intent-vcs |
| `crates/intent-store/migrations/NNNN_workspace_vcs.sql` (new, NNNN ≥ 0191) | §6.4 | persistence | — |
| `crates/intent-store/src/{workspace_repo,atomic_repo_repo,atomic_turn_record_repo,atomic_agent_lease_repo,tracked_changes_repo}.rs` | column mapping, new repos, `change_hash`, `set_workspace_vcs_git` | persistence | migration |
| `crates/intent-services/src/vcs_dispatch.rs` (new) | `vcs_for`, `provisioner_for`, `AtomicAvailability` on `Services` | dispatch | both crates |
| `crates/intent-services/src/git_ops.rs` | reads and writes through `vcs_for`; legacy projection and refusal table (§6.7); status cache holds `VcsStatus` | seam + compat | dispatch |
| `crates/intent-services/src/accept_changes.rs` | `AcceptPipeline` per §6.8; native-review refusal for Atomic | forge path | dispatch, publish_message |
| `crates/intent-services/src/publish_message.rs` (new) | LLM message generation moved out of `auto_commit.rs`, shared by Git auto-commit and Atomic publish | D7, no duplication | — |
| `crates/intent-services/src/auto_commit.rs` | `RecordOutcome::Skipped`; branch to `record_turn` for Atomic; generation calls `publish_message` | turn records | turn_record |
| `crates/intent-services/src/turn_record.rs` (new) | §6.6 | turn records | atomic crate, store |
| `crates/intent-services/src/file_tracking_ops.rs` | `loadCommits` / `historyIdentity` via the trait; agent locks report `autoCommitEnabled=true` for Atomic | attribution | dispatch |
| `crates/intent-services/src/retire.rs` | ownership proof per kind; `is_standalone_git_checkout`; retire ends leases and detaches the sandbox; revive re-sandboxes on the same view with an Atomic-specific notice | lifecycle | provisioner |
| `crates/intent-services/src/lib.rs` | workspace create (vcs param, eligibility, AtomicProvisioner, `atomic-import` progress phase); delete cleanup per kind; placement refusal for Atomic | lifecycle | provisioner |
| `crates/intent-services/src/agent_manager.rs` | lease begin/stop/resume/end hooks on activation transitions; Atomic agent-instruction selection | leases | lease.rs |
| `crates/intent-services/resources/agent-instructions/<next>/` | Atomic sandbox instruction variant (§6.6.4, D13) | agent correctness | — |
| provider spawn path (`crates/intent-providers/` and/or `crates/intent-acp/`; locate the per-provider config-dir env at implementation) | scoped Atomic hook config per Atomic sandbox spawn; omit hooks when the lease failed or hooks are unhealthy | D6 | lease.rs, A15 |
| `crates/intent-services/src/vcs_convert.rs` (new, Phase 7) | `vcs.convert` / `convert-all` (§10.6) | retirement path | WI-17 |
| `crates/intent-services/src/pr_monitor.rs` | none (branch-keyed). Add a test only: an Atomic workspace's publish branch is discovered | — | — |
| `crates/intent-services/src/vcs_ops.rs` (new) | handlers for `vcs.*` / `atomic.*` | protocol | dispatch |
| `crates/intent-acp/src/handler.rs` and `src/mcp_server/bindings/workspace.rs` | `ws.git.commit` (already routed through `git_agent_commit`) works via the trait; `ws.vcs.*`/`ws.atomic.*` read bindings; `proposeSibling` apply accepts `carryChanges` (Phase 3) | MCP parity | Phase 3 |
| `crates/intent-transport/src/protocol.rs`, `src/client.rs` | dispatch entries, bounded-read routing, capability advertisement (`vcs`, `atomic`, `atomicUnavailableReason`) | protocol | vcs_ops |
| `crates/intentd/src/main.rs` (composition root) | create `AtomicCli` (probe), start the lease renew task, `intentd atomic eject-all` subcommand | lifecycle | atomic crate |
| `packaging/{deb,homebrew,libexec,e2b}`, `packaging/atomic-version.txt` | bundle the pinned binary | D3 | — |
| Planned intentd script scripts/check-vcs-seam.sh, proposed scripts/vcs-seam-baseline.txt, proposed scripts/capture-atomic-fixtures.sh, `.github/workflows/*` | seam lint, fixture capture, contract-test job (macOS and Linux) | guard rails | — |

### 7.2 Monorepo docs

| File | Change |
|---|---|
| `docs/plans/atomic-vcs-replacement-2026-11-12.md` | this plan |
| Proposed docs/protocol/methods/vcs.md | §6.7 methods, errors, examples |
| `docs/protocol/methods/git.md` | "Atomic workspaces" section: projection and refusal table |
| `docs/protocol/methods/change-tracking.md` | additive `WorkspaceGitStatus.vcsKind` / `unrecordedCount`; Atomic accept-changes action table; native review unavailable for Atomic |
| `docs/protocol/methods/workspace.md` | `vcs` param, `vcsKind`/`atomic` fields, `atomic-import` progress phase, Atomic retire/revive semantics, `carryChanges` (Phase 3) |
| `docs/protocol/methods/mcp-bindings.md` | `ws.vcs.*` / `ws.atomic.*` bindings; `ws.git.commit` semantics for Atomic |
| `docs/protocol/06-events.md`, `event-types.json` | new events plus the compatibility re-emits |
| `docs/protocol/methods/client-hello.md` | `vcs` / `atomic` capabilities, `atomicUnavailableReason` |
| `docs/protocol/05-method-catalog.md`, `versioning.md` | catalog rows; "Also within 18.x (additive, capability-gated, no version bump)" entry |
| `docs/protocol/node-checkpoints.md` | note: Atomic workspaces excluded until Phase 5 |
| Proposed docs/protocol/fixtures/vcs/ | request/response seeds plus a static validator, following the existing fixtures pattern |

### 7.3 Frontend (`packages/cloudlands-fe/src/`)

| File | Change |
|---|---|
| `shared/types.ts`, `shared/types/vcs.ts` (new) | §6.10 types |
| `lib/client/app-client.ts` | `VcsClient`, `AppClient.vcs` |
| `lib/client/live/live-vcs-client.ts` (new), `mock-app-client.ts` | implementation and mock |
| `lib/vcs/vcs-mode.ts` (new) | helpers |
| `store/renderer/slices/vcs/**` (new) | slice and event saga |
| `store/renderer/slices/git/sagas/git-write-saga.ts`, `store/renderer/seeders/git-bridge-seeder.ts`, `features/git/git.client.ts`, `pr-workflow-saga.ts` | branch on `vcsKind` |
| `features/accept-changes/{types.ts,accept-changes.client.ts,NativeSidebarReview.svelte}` | Atomic flow |
| `lib/components/chat/{ChatChangesPanel.svelte,UnifiedMultiStageDiff.svelte}` | turn timeline, rewind, sections |
| `lib/components/workspace/sidebar/BranchDisplay.svelte` | view / publish branch |
| `lib/components/workspace/initializer/{BranchSelector.svelte,CompactWorkspaceInitializer.svelte}`, `workspace-initialization-submission.ts` | VCS choice and eligibility |
| `lib/components/settings/GitWorkspaceSettings.svelte` (+ Labs settings) | hide auto-commit, Eject, Labs toggle |
| `features/atomic-{provenance,triage,insert,conflicts}/**` (new) | Phase 3 screens |
| `messages/*` | strings |
| tests: `tests/unit/live-vcs-client.test.ts`, Playwright component tests for the new panels | verification |

### 7.4 Assistant app guide

`packages/intentd/crates/intent-services/resources/assistant-app-guide.md` is **not** updated
while Atomic workspaces are Labs-only. AGENTS.md forbids promoting Labs or unfinished features
in the guide. Each PR records "no user-help impact (Labs-only)". The guide gets an "Atomic
workspaces" section in the Phase 4 promotion PR.

---

## 8. Concurrency and lifecycle

- **Execution model.** The trait is sync and runs on `spawn_blocking`. Atomic mutations hold
  `AtomicRepoLocks(canonical)`, and workspace-scoped Git operations keep `WorktreeLocks`. Lock
  order is always archive fence → AtomicRepoLocks, the same order retire already uses with
  worktree locks.
- **Retire and revive vs. turn records.** Retire stops agents before detaching, but a turn record
  that already holds the repo lock must finish first. So `remove_retired_checkout` acquires
  `AtomicRepoLocks` before detaching (the same pattern as `worktree_locks.with_lock`).
- **Lease renew task.** One daemon task, shut down on `settings_tasks.closed()` like the
  auto-commit loop. A missed renew lets the lease expire upstream; the next activation calls
  `resume` and falls back to `begin`.
- **Cancellation.** A CLI timeout kills the process group. For mutating classes, state is checked
  afterwards (§6.6 step 6). `publish` is never retried automatically: on timeout, query the
  remote branch tip. If it equals the locally synthesised SHA, mark it published; otherwise
  report it as uncertain. This mirrors the hub publication rule.
- **Event ordering.** `vcs:*` events are emitted after the store transaction commits. Consumers
  order Atomic changes by `historyIdentity`, not by event arrival.
- **Process limits.** One global semaphore of 8 concurrent `atomic` processes per daemon (§6.3).

## 9. Errors and edge cases

| Case | Behaviour |
|---|---|
| Binary missing or wrong version after Atomic workspaces exist | `FrozenAtomicVcs`: reads come from the index and the plain sandbox; writes fail with `atomic-unavailable`. The UI shows a banner with an Eject option. Eject needs the binary, so the banner tells the user to reinstall it. |
| Import fails or is interrupted | `import_state=failed`; the create fails; the next attempt re-runs the import (incremental if possible) |
| Sandbox missing on disk | The existing folder-presence check suppresses turn records; `vcs.status` returns the existing missing-checkout errors |
| Empty view (no records) | `history` is empty and the boundary is the base state. Publish is refused with "nothing to publish" (`-32602`). |
| Unrecord with dependents | `has-dependents` with the list; the UI offers "unrecord N dependents too" |
| Conflicts after insert or sync | The view holds the conflicts and `VcsStatus.conflicts > 0`. Publish is refused until they are resolved (`data.code: "conflicts-present"`); `git push` refuses conflict markers by default. |
| Agent edits during a user `vcs.record` of the same paths | Agent locks prevent it in the UI, and the daemon also drops locked paths from a mode-2 record |
| Binary files written by an agent | `record` fails on binary files unless `--skip-binary` is passed (CLI help; corrects the baseline's "record unaffected"). Turn records pass `--skip-binary`. Skipped binaries stay in **Unrecorded** with a "binary – not recorded" badge, and `vcs.record` reports them in `skipped[]`. Full binary support waits on A16. Diffs mark `isBinary`. |
| Non-UTF-8 text | Diffs mark `isBinary`; recording is unaffected |
| An agent runs `git` in the sandbox | The command fails with "not a git repository" (D13). The agent instructions (§6.6.4) steer it to `atomic` reads and `ws.vcs.*`. If an agent runs `git init`, the ownership proof fails and retire/delete refuse (§6.5). Turn indexing logs a `sandbox.git_reappeared` warning and the UI shows a banner. |
| Build tools or setup scripts need Git metadata (`git rev-parse HEAD`, `git describe`, `git submodule`) | They fail in the sandbox. `INTENT_VCS`, `INTENT_BASE_REF` and `INTENT_BASE_COMMIT_SHA` are provided (§6.6.4). Eligibility adds the warning `git-metadata-in-build` when the setup script or common build files reference `git ` commands. This is a known limitation, documented in Labs. |
| User-installed global Atomic hooks fire inside a sandbox | Detected with `atomic agent status --json`. Intent skips its own installation for that executor so no turn is recorded twice. Under the lease (`--view ws-<id> --executor`) the user's hooks adopt the workspace view (A15, V16). |
| `lifecycle begin` fails, or hooks are unhealthy | The provider is spawned without hook config; Intent's gap-filler records every turn (§6.6.2). |
| A hook record lands after the gap-filler ran | It is indexed on the next idle and flagged as `vcs.record.late_hook` (§6.6.3). |
| Workspace eject while agents are running | Refused (`InvalidInput`): stop the agents first |
| Daemon crash mid-turn | The boot reconciler stops orphaned `owner=intent` runs before turns are accepted (§6.6.2). The next turn records into `ws-<id>` (V22). |
| Lease expired while the provider kept running (laptop sleep) | Renewal at every turn start plus the turn-start gate. Changes already recorded in a stray view are re-homed at idle (§6.6.3 step 4). |
| An agent writes an ignored path (`node_modules/`, `.env`) | No `tracked_changes` row is created (`WorkspaceVcs::is_ignored`), and nothing is recorded or published (§6.11, V21) |
| After Phase 8, a non-plain row still has `vcs_kind='git'` (restored backup, synced DB) | `vcs_for` → `LegacyGitFrozen`: folder reads plus a "convert this workspace" banner, writes refused. Plain folders → a no-VCS adapter (V19). |
| `branch` rename after publish | `vcs-unsupported` |
| Old frontend + new daemon on an Atomic workspace | Works through the projection; staging buttons return a clear error |
| New frontend + old daemon | No `atomic` capability → no Atomic UI |

---

## 10. Rollout

### 10.1 Phases (each exit criterion is a gate)

| Phase | Scope | Exit criteria |
|---|---|---|
| **0: Seam** | §6.2 steps 1–7; neutral types; seam lint | Full intentd and FE suites green; wire byte-identical (golden tests on `git.*` responses); seam baseline ≤ target |
| **1: Atomic foundation (hidden)** | intent-atomic crate, CLI pinning and packaging, migration, eligibility, contract fixtures, `atomic` capability (flag default off) | Contract suite green on macOS and Linux against the pinned binary; A1–A26 resolved or fallbacks implemented. Scoped, additive hook injection (user config and auth untouched) proven for at least Claude Code and Codex (A15). Hook process environment pinned (§6.6.1). Untracked-file recording (A11), ignore parity (A24) and publish-checkout fast-forward properties (A7) proven. Q9 decided. |
| **2: Atomic workspace MVP (Labs)** | Create/delete/retire/revive with `.git` stripped, scoped hook installation, leases, hook indexing plus the Intent gap-filler, projection, `vcs.*` core, `ws.vcs.*` MCP reads, accept-changes, publish/PR/merge/sync, eject, FE initializer toggle, changes panel, accept flow, Atomic agent instructions | V1–V11, V16, V17 and V20 green; dogfood on 3 eligible internal repos for 2 weeks; no data-loss incidents; eject used successfully at least 3 times |
| **3: Atomic IDE features** | Provenance with the tool-level causal graph from hooks (incl. PR-body attestation), "Explain this turn" (`atomic.session.explain`), triage, insert, conflicts UI, rewind, session fork, `proposeSibling carryChanges`, local per-agent isolated views (delegation `isolation: isolated` → `sandbox --from`), `ws.atomic.*` MCP bindings, and all Atomic-workspace FE surfaces on `vcs.*`/`atomic.*` directly (Git workspaces stay on `git.*` until Phase 7) | V12–V15 green; turn-record latency < 1 s p50 / < 5 s p95 |
| **4: Beyond Labs** | Default stays Git; Atomic offered as opt-in to all users; assistant app guide updated | Maturity gate §10.4 met |
| **5: Reach** | Remote nodes/hub (separate plan), submodules (unlocks Intent's own monorepo), LFS policy, Windows once the bridge ships | Per-item plans |
| **6: Default for eligible repos** | The initializer defaults to Atomic for eligible repos | 30 days of Phase 4 telemetry within SLOs; eject rate < 2 % of Atomic workspaces |
| **7: Convert existing Git workspaces** | `vcs.convert { workspaceId }` (and `intentd atomic convert-all`) turns a Git workspace into an Atomic one (§10.6). The Git option is hidden in the initializer for eligible repos. | Conversion success ≥ 99.5 % across the telemetry population; zero data-loss reports; every non-converted workspace has a recorded ineligibility reason |
| **8: Retire the Git backend** | Remove `GitVcs`/`GitProvisioner`, the legacy projection, `git.*` (breaking protocol release), `git.autoCommit`, the staging UI, and eject (replaced by "export to Git branch" = publish). Shrink `intent-git` to interop utilities. | Retirement gate §10.5 met |

### 10.2 Telemetry

These are structured `tracing` fields, forwarded through the existing telemetry pipeline if one
exists (U4). None of them carry paths, messages or URLs.
- `atomic.cli`: `subcommand`, `class`, `exit_code`, `elapsed_ms`, `timed_out`, `atomic_version`
- `atomic.lock_wait_ms`
- `vcs.record`: `outcome` (recorded/skipped/failed), `file_count`, `skipped_binary_count`
- `vcs.publish`: `outcome`, `elapsed_ms`
- `vcs.conflicts_created`
- `vcs.eject`
- `atomic.import`: `elapsed_ms`, `changes`
- `workspace.create.vcs_kind` and `eligibility_reasons`
- `atomic.hooks_health` (per executor: installed / user-global / none / unhealthy),
  `vcs.record.source` (hook / intent) and `vcs.record.late_hook`
- `agent.git_command_failed` (count only)
- `wire.git_method_calls` (method name and client version; used by the §10.5 wire gate)
- `vcs.convert`: `outcome`, `elapsed_ms`, `ineligibility_reason`

### 10.3 Rollback

**Per workspace: Eject** (`vcs.eject { workspaceId }`, admin or member):
1. Stop leases and require that no agents are running.
2. Run the record-before-destroying steps (§6.5). Then, **in the publish checkout** (D14), run
   `atomic git push -b <branch> --no-push -m "eject: <workspace title>"` to commit the view onto
   the publish branch in the shared `.git` (A7). Running it in the canonical repo would commit
   onto trunk.
3. Provision a Git worktree (`GitProvisioner`) for that branch in a temporary directory.
4. Stop scripts and terminals rooted in the sandbox. Move ignored files (`.env`, caches) into the
   new checkout. Then, under the archive fence, swap directories so that `worktree_path` stays
   the same. Scripts, browser tabs and anything keyed on the path keep working.
5. Update the row with `set_workspace_vcs_git`: `vcs_kind=git`, `checkout_mode=worktree`. Keep
   the `atomic_*` columns for audit.
6. Detach the old sandbox, now at the trash path, and remove the publish checkout.

If eject fails partway, the row stays Atomic and the failed step is reported.

**Per daemon.** Turning `labs.atomicVcs` off stops advertising `atomic` and stops new creates.
The flag gates creation, not use: existing Atomic workspaces keep full functionality while the
binary is available, and can be ejected. A bulk `intentd atomic eject-all` CLI subcommand exists
for downgrade preparation.

**Downgrading the daemon.** Any daemon older than the migration refuses to open the DB (§6.4),
so a downgrade needs a pre-migration DB backup, whether or not Atomic was used. Release notes
document this, and `eject-all` is the step to run before deliberately restoring a backup.

**After Phase 8 (Git retired).**
- Eject no longer exists. The escape hatch is **export**: `vcs.publish` to any branch produces
  a normal Git branch on the forge, which any Git client can check out outside Intent.
- Restoring the Git backend means running the last pre-retirement intentd major, which still
  contains `GitVcs`. So the retirement release ships as a new major, and the previous major
  stays downloadable for the deprecation window.

### 10.4 Maturity gate (Phase 4)

1. An Atomic release with JSON output for every command the backend relies on: already true for
   `status`, `diff`, `log`, `change`, `triage candidates` and `agent lifecycle`; still needed
   for `record`, `sandbox create`, `unrecord`, `insert`, `view` and `conflicts`.
2. The Causal Bridge RFC is accepted, with lease-based ref updates implemented.
3. Load test V10 passes at 8 concurrent agents for 1 h with zero repo corruption, three releases
   in a row.
4. The round-trip fidelity corpus V8 is 100 % byte-identical on eligible repos.
5. No open Sev-1/2 Atomic-workspace incidents for 30 days.

### 10.5 Retirement gate (Phase 8)

Every reason the baseline gave for keeping Git must be closed. Phase 8 starts only when all of
the following hold:

1. **Platforms:** Atomic workspaces are supported on every platform Intent ships, including
   Windows. That needs either the Causal Bridge on Windows or a Windows publish path that
   doesn't depend on the bridge.
2. **Repository shapes:**
   - Submodules are supported (Phase 5, V12), so Intent's own monorepo runs on Atomic.
   - LFS and large binaries have a shipped policy (A16).
   - Shallow and SHA-256 repos either import or have a documented conversion path.
   - **Secondary Git roots** (`workspace_git_root`, `ws.git.*Root` bindings) and submodule
     roots have a decided Atomic-era home (Q12). The recommendation is a minimal `GitRootVcs`
     for secondary roots only: Phase 8 deletes the *workspace* Git backend, not root support,
     because submodule repos are themselves Git repos on the forge. The alternatives are
     roots as Atomic sub-repos, or dropping agent-registered roots.
3. **Execution:** remote nodes, the hub and isolated delegation run on Atomic (the Phase 5
   plan).
4. **Forges:** GitLab qualified native review works for Atomic workspaces (Q5), and GitHub
   PR, merge-queue and CI flows have been green on Atomic for at least 90 days.
5. **Adoption:** at least 95 % of active non-plain-folder workspaces are Atomic. Every
   remaining Git workspace is either converted or has an ineligibility reason that has itself
   been eliminated.
6. **Wire:** zero `git.*` calls from current-version clients for 30 days, measured **after**
   Phase 7 conversion (telemetry, §6.7). The `vcs.source.*` aliases have shipped.
   The supported-client window no longer contains any client that needs `git.*`.
7. **Upstream stability:** an Atomic 1.0 release, or a written compatibility commitment from
   upstream, and an accepted Causal Bridge RFC.
8. **Conversion:** Phase 7 conversion success is ≥ 99.5 % with zero data-loss reports.

Plain-folder workspaces are unaffected: they never had a VCS. `vcs_kind` stays `'git'` by
default in the schema for historical rows, but after conversion no non-plain-folder row
keeps `'git'`, and services treat `plain_folder` first. A later additive migration can switch
the column default to `'atomic'`.

### 10.6 Converting a Git workspace (Phase 7)

`vcs.convert { workspaceId }` is the reverse of eject. Members or admins call it, and only when
no agents are running.

1. Run eligibility; refuse if the repo is ineligible.
2. Ensure `atomic_repo` exists and import trunk (`git import --incremental --branch
   <baseRef>`).
3. Import the workspace branch's commits that are not yet on trunk as changes into a new view
   `ws-<id>` forked from `<baseRef>`. Use `git import --branch <branch> --incremental` into a
   temporary view, then `insert view` (A20).
4. Record any dirty working-tree edits as one change, `convert: uncommitted work`.
5. **Pushed branches and open PRs.** If `<branch>` exists on the remote, seed the publish
   checkout (D14) at the remote tip. A20 must prove that the first publish after conversion
   fast-forwards from that tip. Until it does, refuse conversion of pushed branches with
   `vcs-convert-pushed-branch`, unless Q11 allows one explicit force-push.
6. Create the sandbox in a temporary directory and strip its `.git` (D13). Stop scripts and
   terminals, move ignored files across, and swap directories under the archive fence so that
   `worktree_path` stays the same.
7. Update the row to `vcs_kind=atomic`, keeping `branch` as the publish branch and keeping
   PR linkage.
8. Detach the old Git worktree, keeping the branch.

If conversion fails partway, the row stays Git and the failed step is reported. Rehearse it on
every Phase 7 telemetry cohort before running `convert-all` (V18).

---

## 11. Risks and open questions

### 11.1 Atomic CLI assumptions (Phase 1 blockers)

Validate each with the pinned binary in the proposed scripts/capture-atomic-fixtures.sh. The Status column
records what was already confirmed against 0.19.1 `--help` while writing this plan.

| ID | Assumption | Status | Validation | Fallback |
|---|---|---|---|---|
| A1 | `git import --branch` works on a `git clone --local` copy, and `--incremental` is idempotent | open | import twice; diff the state hash | full re-import into a fresh repo |
| A2 | `sandbox create` reports whether it reflinked | open | inspect output; otherwise compare clone flags with `stat` | treat as `direct` |
| A3 | `log` and `change` emit machine-parsable records | **resolved**: both take `--format json` | fixture capture | — |
| A4 | the view difference against trunk can be computed | open | `log --view <v> --format json` on both views | `triage candidates ws-<id> --into <baseRef> --json` |
| A5 | the recorded content of a path at a change can be read without a checkout | open | `change --show-hunks` / docs | temporary sandbox read (slow path) |
| A6 | a path-scoped revert of unrecorded edits exists | **resolved**: `atomic restore [FILES]` | fixture | — |
| A7 | the per-workspace publish checkout (D14: an Atomic sandbox on `ws-<id>` plus a `git worktree` link on the publish branch) publishes correctly: (i) successive publishes fast-forward; (ii) the first parent is `base_commit_sha` (or the remote tip after conversion); (iii) after `vcs.syncTrunk` the trunk tip is an ancestor; (iv) the canonical trunk ref never moves | open: `git push` commits on the *current Git branch* and `-b` only redirects the remote | two views, three publishes, one sync | refuse publish after sync until merged; publish fresh branches only |
| A8 | the sandbox has no `.git` | **likely false**: provisioning skips only `.atomic/` and nested sandboxes, so a colocated `.git` is reflink-copied. **Handled by D13**: Intent strips it | inspect after `sandbox create` | — (stripping is the design) |
| A9 | concurrent read commands are safe during a write | open | stress test | lock reads too |
| A10 | several lifecycle sessions can share one view/workdir | open | test | `LEASE_PER_WORKSPACE` |
| A11 | `record -- <FILES>` limits recording to those paths, and new files are recorded after `atomic add` (`record` skips untracked files without `-a`) | open | test with modified and new files | per-turn temporary sandbox (expensive) |
| A12 | `view delete` refuses, or keeps, changes referenced elsewhere | open | test | never delete views in Phase 2; GC in Phase 3 |
| A12b | `unrecord <hash>` of a change with dependents fails cleanly and names them | open | test with `--dry-run` | compute dependents via `change --show-deps` before calling |
| A13 | `unrecord` leaves the change's edits in the working copy (keep-files) | open | test | for keep-files, rewrite the content from A5 after unrecord |
| A14 | line/token-level attribution can be queried (README mentions token-level blame) | open | search the CLI/docs (`query`, `change --show-hunks`) | path-level `log --path` only |
| A15 | for each executor, Atomic hook config can be injected **additively** per provider spawn (an extra settings layer or CLI override), with the user's provider config, auth, plugins and MCP unchanged. `agent enable` has no destination flag (project-local default, `-g`, `--hooks` = manifest source). User-global hooks can be detected and overridden. | open | per provider: spawn with the injected layer, run a turn, check `agent status --json`, `session show --json`, and that the user config is untouched | that provider gets no hooks; the gap-filler records its turns |
| A18 | `lifecycle abandon --run-id` seals the pending turn as a recorded change, and the run's state afterwards is known (terminal or active) | open | cancel a turn mid-edit under a run, then send another prompt | gap-filler records the interrupted edits; turn-start gate begins a new run |
| A19 | a hook-recorded turn is visible in `session show --json` / `log --view` by the time ACP reports idle, or within 3 s | open | measure across providers | longer bounded wait per provider; `late_hook` telemetry |
| A20 | a Git branch's unique commits can be imported into a chosen view (`git import --branch <b> --incremental`, then `insert view`) for conversion | open | convert a workspace with 5 commits and dirty edits | export patches with `git format-patch` and record them change by change |
| A21 | `lifecycle renew` takes `--run-id` and extends the TTL | **resolved**: `renew --run-id <RUN_ID> [--ttl-seconds, default 86400]` | — | — |
| A22 | 0.19.x `git push` emits Causal-Bridge binding headers and `git import` recognises them (the post-merge "merge keeps bindings" lever) | open | publish, merge on GitHub with each strategy, re-import (V9) | unconditional view rebuild after every merge; leave merge strategy alone |
| A23 | `view switch --stash <view>` inside a sandbox switches only that sandbox | open | two sandboxes, switch one | record-first sandbox recreate (§6.5) |
| A24 | Atomic honours nested `.gitignore`s, and materialised `info/exclude` and global excludes take effect | open | `.env`, `node_modules/` and nested ignore fixtures (V21) | eligibility fails with `ignore-parity-unverified` |
| A25 | the provider's external session ID is obtainable per agent (ACP handle, or `lifecycle end --json` / `session show --json` filtered by workdir) | open | per provider | `LEASE_PER_WORKSPACE`; fork unsupported for that provider |
| A26 | a run's pending or unsealed turn is observable (`lifecycle status --json` or the ledger), so the gap-filler can sequence after hooks | open | inspect during an in-flight turn | bounded wait plus `late_hook` telemetry only |
| A16 | binary files can be recorded faithfully | open (`--skip-binary` implies failure by default) | test | keep `--skip-binary`; eligibility warns on binary-heavy repos |
| A17 | `session fork --at-turn N --child` + a new view with changes ≤ N reproduces the turn state | open | test | sibling workspace from the base, then `insert change` of the changes ≤ N |

### 11.2 Risks

- **Post-merge duplicate changes** (§6.8). This is the highest product risk. It is mitigated by
  the view rebuild and by defaulting to merge commits, and V9 checks it.
- **Store corruption under concurrent processes** (redb). Mitigated by in-process serialisation,
  eject, and the Phase 4 load gate.
- **Git expectations inside sandboxes.** Agents are trained to run `git status`, `git diff` and
  `git commit`. With `.git` stripped (D13) those commands fail loudly. That is a behaviour
  change for agents, mitigated by the Atomic instruction variant and the `ws.vcs.*` tools.
  Track it with the telemetry field `agent.git_command_failed` (from ACP tool-call
  inspection).
- **Build tooling that depends on Git metadata** fails in sandboxes (`git rev-parse`,
  `git describe`, submodule scripts). Mitigation: the `INTENT_*` environment variables, the
  eligibility warning, and Labs documentation. This may become a gate item if it proves
  common.
- **Hook installation and provider updates.** Hooks live in provider configuration that
  providers can change between releases, and scoped installation per provider is unproven
  (A15). Mitigation: per-provider fallback to the gap-filler, the hook health check, and V16
  in the contract suite for every pinned provider and Atomic version.
- **Retirement is a one-way door** (D11). Once `GitVcs` is deleted, rollback means running the
  previous intentd major. Mitigation: the §10.5 gate, Phase 7 conversion telemetry, and
  export via publish.
- **Losing the staging area** surprises Git-literate users. Mitigated by per-turn records,
  partial record and the Labs framing.
- **Auto-commit semantics change**: records are always on and agent commits are not gated
  (decided, D7).
- **Hook recorders are cross-process writers** on a shared redb, across every workspace of a
  source repo. In-process locks cannot order them. Mitigation: sequencing on run state (A26),
  V10 with hook writers from several workspaces, and Q9 (shared vs per-workspace canonical
  repo).
- **Secret leakage through publish** if Atomic's ignore rules diverge from Git's. Mitigation:
  the §6.11 ignore parity, the eligibility gate, and V21.
- **Secondary git roots** stay Git inside Atomic workspaces. The registered-root `gitRootId`
  paths keep `GitVcs`; this is documented.
- **Disk.** The shared repo is a full clone plus `.atomic`. Mitigation: per-repo sharing, and
  Phase 3 GC once no workspace references it.
- **Upstream churn.** Atomic is pre-1.0 and the bridge is an RFC. Mitigation: pinned binary,
  version-range probe, fixtures per version, and `FrozenAtomicVcs`.
- **Licensing.** Apache-2.0 is compatible; the notice is required.

### 11.3 Open questions (owner: product/arch; decide before the phase noted)

- **Q1 (Phase 2):** should Atomic records sign with a per-daemon identity from day one, or only
  with Phase 3 provenance? Recommendation: Phase 3.
- **Q2 (Phase 3):** do Atomic-hosted remotes have a place, or does Intent stay GitHub/GitLab only?
  Recommendation: forge-only until Phase 5.
- **Q3 (resolved):** always record every turn; `git.autoCommit` does not apply (D7).
- **Q4 (Phase 2):** Atomic revive semantics: the same view (recommended) or Git parity (a fresh
  view)?
- **Q5 (Phase 5):** should GitLab qualified native review support Atomic by binding to the
  published Git SHA?
- **Q6 (resolved):** Atomic hooks record under Intent-managed leases, which gives the
  tool-level causal graph; Intent gap-fills (D6).
- **Q7 (resolved):** strip `.git`; agents see Atomic only (D13).
- **Q8 (Phase 7):** is conversion opt-in per workspace, or automatic for idle eligible
  workspaces once Phase 6 holds? Recommendation: opt-in with a nudge in Phase 7, and automatic
  for idle workspaces only in the final 60 days before Phase 8.
- **Q9 (before WI-7):** one shared canonical Atomic repo per source repo, or one per workspace?
  A shared repo saves disk and import time but puts every workspace's hook writers on one
  redb lock. Per-workspace repos isolate writers and contamination, at the cost of disk.
  Recommendation: shared by default, with a per-workspace fallback flag. V10 (with hook
  writers) decides before Phase 2.
- **Q10 (Phase 2):** may agents write Atomic knowledge (`intent`, `memory`, `vault`) in
  sandboxes? Recommendation: no in Phase 2 (hooks only, no skills), and revisit with
  Phase 3 provenance.
- **Q11 (Phase 7):** converting pushed branches with open PRs: allow one explicit,
  user-confirmed force-push at conversion, or refuse until A20 proves a fast-forward?
  Recommendation: refuse first, decided by A20.
- **Q12 (before Phase 8):** what happens to secondary Git roots and submodule roots at
  retirement? Recommendation: a minimal `GitRootVcs` (§10.5 item 2).
- **Q13 (Phase 2):** do provider processes survive daemon restarts? This decides whether the
  boot reconciler stops or re-adopts runs (§6.6.2).

### 11.4 Implementation unknowns

- **U1 (resolved):** the newest migration is `0190`, and `intent-store` refuses newer schemas
  (`intent-store/src/lib.rs:461-485`).
- **U2 (resolved):** the capability JSON is at `intent-transport/src/client.rs:118`. FE consumers
  are found by grepping `boundedReads`.
- **U3 (partial):** the agent activation path is in `intent-services/src/agent_manager.rs` (the
  `activate` test helper is at `:23000`). Pin the production transition at implementation
  time.
- **U4:** does a telemetry sink exist beyond `tracing`? Check the intentd composition root.
- **U5:** the full list of direct git2 uses in `accept_changes.rs` / `git_ops.rs`. Run
  `rg 'git2::'` when Phase 0 starts.

---

## 12. Implementation order and execution index

### 12.1 Ordered steps

Steps marked **(atomic)** must land together.

1. Add the `intent-core/src/vcs.rs` types, error variants and event constants. It compiles and
   has no users yet.
2. Move the git2 code in `accept_changes.rs` / `git_ops.rs` into intent-git pub functions.
   Behaviour tests stay unchanged.
3. Create the `intent-vcs` crate with the traits, `GitVcs` and `GitProvisioner`, plus parity tests
   that run the existing intent-git test cases through the trait.
4. **(atomic)** Add `Workspace.vcs_kind` (model and store mapping), the `NNNN_workspace_vcs.sql`
   migration, and `vcs_dispatch.rs` (Git only). Wire golden tests prove the bytes are unchanged.
5. Migrate `git_ops.rs` reads, then writes, then `file_tracking_ops.rs`, then `auto_commit.rs`
   (`RecordOutcome::Skipped` and the `publish_message.rs` extraction), then `accept_changes.rs`
   (`AcceptPipeline`), then `retire.rs` / `lib.rs` provisioning. One PR each, updating the seam
   baseline each time.
6. Land the planned intentd script scripts/check-vcs-seam.sh in CI with the final Phase 0 baseline. **Phase 0 is done.**
7. Create the `intent-atomic` crate: `AtomicCli`, parsers, fixtures, locks, eligibility, plus the
   contract-test CI job and the packaging pin and bundling. Resolve A1–A26 (A15 per provider).
8. Add the store repos for `atomic_repo`, `atomic_turn_record` and `atomic_agent_lease`, and the
   `Workspace.atomic` mapping.
9. Add the settings `labs.atomicVcs` and `vcs.atomic.binaryPath`, the availability probe in the
   composition root, and the capability advertisement (`vcs`, `atomic`). **Phase 1 is done.**
10. Add `AtomicProvisioner`, the create flow (vcs param, eligibility, import progress, strip
    `.git` and verify with V17, ignore parity), the record-before-destroying steps, the
    delete/retire/revive branches and the placement refusals.
11. Add the `AtomicVcs` reads, the legacy `git.*` projection table, and the `vcs.status` /
    `vcs.changes.*` handlers and routing. Also move attribution behind the seam
    (`is_ignored`/`classify_paths`/`lockable_paths` and the sweep branch, §6.1), which is a
    prerequisite of step 12.
12. **(atomic)** Land `turn_record.rs` (hook indexing plus the gap-filler), the dispatch branch
    in `auto_commit.rs`, `AtomicLeaseManager` with its activation hooks, scoped hook
    installation in the provider spawn path, the agent-lock rule, the Atomic agent
    instructions, `INTENT_*` env, and the `ws.vcs.*` MCP reads. They must land together so
    that Atomic workspaces never run without a recorder, and agents are never left without
    Git and without a replacement.
13. Add the publish checkout (D14) first. Then `vcs.record` / `vcs.publish` / `vcs.syncTrunk`,
    the Atomic accept-changes pipeline, the post-merge view rebuild (A22/A23), and
    `vcs.eject` / `eject-all` with path-preserving swaps.
14. Write the protocol docs (`vcs.md`, git.md, change-tracking.md, workspace.md, mcp-bindings.md,
    events, client-hello, catalog, versioning) and fixtures. As additions, these docs land in
    the monorepo **before** the component PRs merge (AGENTS.md "Docs lead the pin").
15. Frontend, in order: types → `VcsClient` / live / mock → capability helpers → vcs slice and
    saga → code that bypasses the seam → initializer toggle → changes panel → accept-changes →
    BranchDisplay → settings (Labs, Eject) → i18n. Each step is mergeable behind
    `atomicAvailable`, and the FE PR merges only after the intentd PR is merged (protocol rule).
    **Phase 2 is done** after the dogfood exit criteria are met.
16. Phase 3, daemon then frontend for each feature: provenance (and PR-body attestation) →
    triage → insert → conflicts → unrecord/rewind UI → session fork / `carryChanges` → local
    isolated per-agent views → MCP read bindings.
17. Phase 4 promotion when §10.4 holds, including the assistant app guide section. Phases 5 and 6
    get separate plans.
18. Phase 7: `vcs.convert` / `convert-all` (§10.6), the `git.*` call-count telemetry, and hiding
    the Git option in the initializer for eligible repos.
19. Phase 8, when §10.5 holds:
    - **Docs first** (a removal lands **component first**, per AGENTS.md, then the docs entry is
      dropped after the bump): `vcs.source.*` aliases, then the breaking protocol version.
    - **Removals:** delete `GitVcs`, `GitProvisioner` and the projection; remove `git.*`, the
      staging paths in accept-changes and file-tracking, `git.autoCommit`, and the eject and
      FE staging UI.
    - **Shrink `intent-git`** to `repo_cache`, `auth`, `identity`, `redact`, `ls_remote`,
      clone/fetch-to-cache and `submodule` reads (bridge support).
    - **Store:** an additive migration switches the `vcs_kind` default to `'atomic'`.

### 12.2 Execution index

| WI | Goal | Done when | Key files | Dependencies | Size |
|---|---|---|---|---|---|
| WI-1 | Neutral VCS types and errors | `vcs.rs`, error variants and event constants compile; unit tests for the `From<&VcsStatus> for GitStatus` projection | `intent-core/src/{vcs,error,events}.rs` | — | S |
| WI-2 | git2 consolidated into intent-git | No `git2::` in `accept_changes.rs`/`git_ops.rs`; existing tests green | `intent-git/src/{commit,reset,refs}.rs`, `intent-services/src/{accept_changes,git_ops}.rs` | — | M |
| WI-3 | `intent-vcs` crate with `GitVcs`/`GitProvisioner` | V2 parity green | `crates/intent-vcs/**` | WI-1, WI-2 | M |
| WI-4 | `vcs_kind` column + dispatch (Git only) | Migration applies; V1 golden wire tests byte-identical | migration `NNNN_workspace_vcs.sql`, `model.rs`, `workspace_repo.rs`, `vcs_dispatch.rs` | WI-3 | M |
| WI-5 | Call-site migration (reads → writes → tracking → auto-commit → accept → provisioning) | Seam baseline < 120 lines in intent-services; full suites green | `git_ops.rs`, `file_tracking_ops.rs`, `auto_commit.rs`, `publish_message.rs`, `accept_changes.rs`, `retire.rs`, `lib.rs` | WI-4 | XL (6 PRs) |
| WI-6 | Seam lint in CI | `check-vcs-seam.sh` fails on a new direct use | Planned intentd script scripts/check-vcs-seam.sh, baseline, intentd CI | WI-5 | S |
| WI-7 | `intent-atomic` foundation + contract suite | V3/V4 green on macOS and Linux; A1–A26 resolved or fallbacks built | `crates/intent-atomic/**`, proposed scripts/capture-atomic-fixtures.sh, packaging | WI-3 | L |
| WI-8 | Atomic store repos | CRUD tests; `set_workspace_vcs_git` | `intent-store/src/atomic_*_repo.rs` | WI-4 | S |
| WI-9 | Availability, settings, capabilities | Capability matrix (V15, daemon side) passes | `settings_file.rs`, `intentd/src/main.rs`, `intent-transport/src/client.rs` | WI-7 | S |
| WI-10 | Atomic provisioning and lifecycle | Create/retire/revive/delete V11 green; placement refusals | `intent-atomic/src/provision.rs`, `lib.rs`, `retire.rs` | WI-8, WI-9 | L |
| WI-11 | Atomic reads + legacy projection + attribution behind the seam | V6 and V21 green | `intent-atomic/src/backend.rs`, `git_ops.rs`, `vcs_ops.rs`, `protocol.rs` | WI-10 | M |
| WI-12 | Hook-primary recording + gap-filler + leases (turn-start gate, boot reconciler) + scoped hook injection and environment + agent instructions + `ws.vcs.*` reads (land together) | V5, V16, V17, V20, V22 green | `turn_record.rs`, `auto_commit.rs`, `lease.rs`, `agent_manager.rs`, provider spawn path (`intent-providers` / `intent-acp`), agent-instructions, `intent-acp` bindings | WI-11 | XL |
| WI-13 | Publish checkout, record/publish/sync, accept pipeline, view rebuild, eject | V7, V9, V11 (eject), V23 green | `vcs_ops.rs`, `accept_changes.rs`, `intentd` CLI | WI-12 | L |
| WI-14 | Protocol docs + fixtures | `make consumer-checks` green; docs merged first | `docs/protocol/**` | WI-11–13 shapes frozen | M |
| WI-15 | Frontend Phase 2 | V14 + FE side of V15 green; dogfood exit criteria met | §7.3 | WI-14, intentd merged | XL |
| WI-16 | Phase 3 IDE features | V12–V15 green; latency SLO | `features/atomic-*`, `vcs_ops.rs`, `intent-acp` | WI-15 | XL |
| WI-17 | Phase 4 promotion | §10.4 met; assistant app guide updated | `assistant-app-guide.md`, settings defaults | WI-16 | S |
| WI-18 | Conversion of Git workspaces (Phase 7) | V18 green; conversion success ≥ 99.5 % | `intent-services/src/vcs_convert.rs` (new), `intentd` CLI, FE settings action | WI-17, Phase 5–6 | L |
| WI-19 | Git backend retirement (Phase 8) | V19 green; §10.5 gate met; breaking protocol release shipped | `intent-vcs/src/git.rs` (deleted), `git_ops.rs`, `accept_changes.rs`, `file_tracking_ops.rs`, `docs/protocol/**`, FE git slices | WI-18 | XL |

---

## 13. Verification

| ID | Test | Layer |
|---|---|---|
| V1 | Golden wire tests: every `git.*`, `accept-changes.*` and `file-tracking.*` response for Git workspaces is byte-identical before and after Phase 0 | intent-services integration |
| V2 | `GitVcs` parity: the existing intent-git cases (status, diff, commit modes 1–4, rebase, reset) run through the trait | intent-vcs |
| V3 | CLI parsers against the recorded fixtures for every subcommand; unknown fields tolerated; malformed output → `AtomicCli` error | intent-atomic unit |
| V4 | Contract suite against the real pinned binary (`INTENT_ATOMIC_BIN`, macOS and Linux CI): A1–A26 | intent-atomic integration |
| V5 | Create → edits by two agents (including a **newly created file**) → idle → turn records with correct per-agent paths, trailers, `tracked_changes` advanced and events emitted. Run both with hooks enabled and with the gap-filler only. A duplicate `agent:idle` is a no-op. | services integration (fake provider / `MOCK_AGENT=1` stack) |
| V6 | Legacy projection: `git.status` / `diffs` / `commits` / `commitDetails` / `showFile` on an Atomic workspace match `vcs.*` data; stage returns `vcs-unsupported` | services |
| V7 | Accept-changes Atomic pipeline: record → publish → create-pr → merge using `StubForge` (pr_monitor test support); the PR monitor discovers the publish branch | services |
| V8 | Round-trip fidelity: import → record nothing → publish produces a tree byte-identical to the base; corpus of 10 public repos (nightly) | nightly |
| V9 | Post-merge for the merge / squash / rebase strategies: sync + view rebuild leaves the view with only post-publish changes, no duplicates or conflicts | services + real binary |
| V10 | Load: 8 agents recording concurrently for 1 h in one shared repo; zero lock deadlocks, zero corruption (`atomic doctor check`, the read-only subcommand), p95 record < 5 s. Includes hook writers from several workspaces sharing one canonical repo (Q9). | nightly perf |
| V11 | Retire/revive/delete/eject: the ownership proof rejects foreign sandboxes and symlink escapes (mirroring the existing retire tests). Record-before-destroying captures unrecorded edits. Revive restores recorded changes. Eject yields a working Git workspace with an identical tree at the **same** `worktree_path`, with `.env` preserved. | services |
| V12 | Submodule gitlink bump fidelity through the bridge (Phase 5 gate) | real binary |
| V13 | Unrecord with dependents, insert preview/apply, and conflict list/resolve round-trips | services + real binary |
| V14 | Frontend: `live-vcs-client` normalisation (vitest); `ChatChangesPanel` Atomic sections and rewind; initializer eligibility gating; the accept flow hides staging (Playwright component tests) | FE |
| V15 | Capability matrix: old frontend ↔ new daemon (projection works), new frontend ↔ old daemon (no Atomic UI), Windows daemon (no `atomic`), flag off (no creates, existing workspaces usable) | e2e |
| V16 | Hook recording under leases, run for each hooked provider (also: cancel-then-continue in the same provider session stays in `ws-<id>`; the user's provider config and auth are unchanged; the hook's `atomic --version` equals the pinned version): an Intent-managed turn produces exactly one hook-recorded change in `ws-<id>` with tool-level provenance, and no stray per-session views. With user-installed global hooks also present there is still exactly one change. An interrupted turn is sealed (A18) or gap-filled. No `late_hook` events with healthy hooks (A15, A18, A19). | real binary + provider fixtures |
| V17 | Sandbox Git hygiene: after create the sandbox has no `.git`. `git status` in the sandbox fails with "not a git repository". A `.git` that reappears fails the ownership proof (D13). | services + real binary |
| V18 | Conversion: Git workspaces with commits, dirty edits, a linked **open PR on a pushed branch** (first publish fast-forwards, or conversion is refused), `.env` preserved at the same `worktree_path`, and auto-generated vs. explicit branches, convert to Atomic. The tree is identical, history appears as changes, PR linkage is preserved, and a failure leaves a working Git workspace (A20). | services + real binary |
| V19 | Retirement: the daemon builds and passes all suites without `GitVcs`. `git.*` returns `-32601` and the `vcs.source.*` aliases answer. Legacy non-plain `git` rows open as `LegacyGitFrozen`, and plain folders are unaffected. Old clients see the capability change and degrade cleanly. The `intent-git` public surface contains only interop modules (seam lint with an empty baseline). | full gates + e2e |
| V21 | Ignore parity: an agent writes `.env`, `node_modules/x`, and a file under a nested `.gitignore`. No `tracked_changes` row persists and nothing is recorded or published (A24). | services + real binary |
| V22 | Crash recovery: kill -9 the daemon mid-turn and restart. The reconciler stops orphaned runs, and the next turn records into `ws-<id>` with no duplicate active run. | services + real binary |
| V23 | Publish checkout: three publishes, a trunk sync and a merge. Every push fast-forwards, the canonical trunk ref never moves, and the PR diff contains only workspace changes (A7). | services + real binary |
| V20 | Gap-filler: with a provider that has no hooks, and with `lifecycle begin` forced to fail, every turn that changes files is recorded by Intent with correct AI metadata and trailers. | services (fake provider / `MOCK_AGENT=1`) |

**Commands and gates.**
- Rust: `make check`, `make test`, or `make test-changed` / `make test-select E='<filterset>'`
  for iteration. Prove flakes with `make test-stress`.
- Frontend: `make fe-verify-changed`.
- Monorepo docs: `make consumer-checks` (method and event catalogs, protocol→FE field parity,
  docs-check, check-makefile-targets).
- Manual app checks:
  - `make dev-sandbox-stack MOCK_AGENT=1` with `labs.atomicVcs` on.
  - Create an Atomic workspace and run two agent turns. Expect two Recorded entries.
  - Rewind the second turn, then publish to a scratch GitHub repo and open a PR. Expect the PR
    monitor to link it.
  - Eject, and confirm the workspace becomes a working Git workspace.
- Migration changes are never tested through manual signed builds (§6.4).

---

## 14. Repository workflow constraints (from AGENTS.md)

- **Cross-component order.** The intentd and cloudlands-fe PRs are developed in parallel. Because
  this is a protocol change, the FE PR is not merged, enqueued, or auto-merged until the intentd
  PR is confirmed merged.
- **Docs lead additions.** The `docs/protocol/` additions land in the monorepo first; the consumer
  checks warn until the components catch up.
- **Merging.** Merges need explicit human permission (merge queue via `gh pr merge --squash
  --auto` after permission). Request the `intent-hq-service` review on every PR.
- **Commits.** Use conventional commits, and never quote the breaking-change footer token. All
  Atomic changes are additive and capability-gated, so no protocol version bump is needed.
- **Assistant app guide.** No update while Labs-only (§7.4). Each PR records that.
- **Release tracking.** Track shipped work to a cloudlands-fe alpha with `scripts/shipped-in.sh`,
  then run the ergonomics retrospective before the final status.

---

## 15. Baseline corrections log

These are changes from the `context_builder` plan baseline, each with its evidence:

| Baseline item | Correction | Evidence |
|---|---|---|
| View name `ws/<id>`; two-step `view create` + `sandbox create --view` | `ws-<id>` via a single `sandbox create ws-<id> --from <baseRef>` (D12) | `sandbox create --help`: `--from` creates a draft view named after the sandbox |
| A3 needs a TSV/base64 `--format` template | `--format json` exists for `log` and `change` | `atomic log --help`, `atomic change --help` |
| `discard` → `atomic reset` (A6 open) | `atomic restore -- <FILES>`; A6 resolved | `atomic restore --help` (no `reset` subcommand) |
| `undo` → `atomic unrecord <hash…> [--reset]` | One change per call, looped newest-first; no `--reset`; added A12b/A13 | `atomic unrecord --help` |
| `atomic insert --from --to` | `insert view <src> --to-view` / `insert change <hashes> --to-view [--deps] [--allow-conflicts]` | `atomic insert view|change --help` |
| `triage candidates --target` | `triage candidates [VIEW] --into <target> --json` | `atomic triage candidates --help` |
| `atomic.provenance.trace { path, line? }` | Change-keyed `trace`; new `forPath` via `log --path`; line-level is A14 | `atomic provenance trace --help` (TARGET = change) |
| A8 "sandbox has no `.git`" | Likely false; the user chose to strip `.git` (D13); added V17 | Sandbox doc: provisioning skips only `.atomic/` and nested sandboxes |
| Binary files: "record unaffected" | `record` fails on binaries unless `--skip-binary`; added policy, A16 and telemetry | `atomic record --help` |
| Old daemon reading the new DB "treats Atomic as Git" | Old daemons refuse newer schemas; rollback = eject + flag; downgrade needs a backup | `intent-store/src/lib.rs:461-485` |
| Migration number "≥ 0164" | ≥ 0191 | `intent-store/migrations/` newest is `0190` |
| U1, U2 open | Resolved (see §11.4) | as cited |
| `publish` "scoped to the view (A7)" | A7 clarified: `git push` commits on the current Git branch and `-b` only redirects the remote | `atomic git push --help` |
| No MCP or agent-instruction impact listed | Added `ws.vcs.*`/`ws.atomic.*` read bindings and an Atomic agent-instruction variant | `mcp-bindings.md:214-217`; `resources/agent-instructions/` |
| No assistant-guide handling | Added §7.4 per AGENTS.md | AGENTS.md "Assistant app guide" |
| No user-installed hook handling | Added A15, V16 and the §9 row | `agent lifecycle begin --help` (`--executor` / `--view` semantics) |

---

### 15.1 User decisions at the mid-flow check-in

| Question | Decision | Plan changes |
|---|---|---|
| Git inside agent sandboxes (A8/Q7) | Strip `.git`; agents see Atomic only | D13; §6.5 create step 5 and ownership proof; §6.6.4 instructions and `INTENT_*` env; `ws.vcs.*` MCP reads moved to Phase 2; §9 rows; V17 |
| How complete "replace" is | Full retirement of the Git backend | D11 rewritten; Phases 7–8; §10.5 retirement gate; §10.6 conversion; `git.*` deprecation path (§6.7); WI-18/19; V18/V19; Q8 |
| Turn recording vs. auto-commit (D7/Q3) | Always record every turn | D7 confirmed; Q3 resolved |
| Provenance depth (D6/Q6) | Atomic hooks record under Intent-managed leases | D6 reversed (hooks primary, Intent gap-fills); §6.6 rewritten (scoped install, `run_id` leases, abandon-sealing, hook indexing, race rules); store `source`, `atomic_session`, `run_id`, `hooks_installed`; A15/A18/A19/A21; V16/V20; `atomic.session.explain` |

### 15.2 Corrections from the design critique

The full critique is in `docs/reviews/atomic-vcs-replacement-plan-critique-2026-11-12.md`. Each
correction below was checked against the 0.19.1 CLI help or the code before it was applied.

| Finding | Applied change |
|---|---|
| The attribution helpers need `.git` (`file_tracking.rs:112`, `tracked_changes_sweep.rs:112`, `agent_locks.rs:208`) | Moved behind `WorkspaceVcs` (§6.1); the §3.5 note; WI-11 prerequisite; V21 |
| `record` skips untracked files without `-a` | `atomic add` before record (§6.3); A11 extended; V5 covers new files |
| Native AI flags (`--ai-session-id`, `--ai-tool`, tokens, cost) | Used on gap-fill records (§6.3) |
| `git push` commits on the current Git branch, so publish had no safe working copy | D14 per-workspace publish checkout; A7 (i)–(iv); V23; eject and conversion use it |
| Cancel-then-continue escaped the workspace view | Turn-start gate plus A18 run-state (§6.6.2–6.6.3); V16 |
| The TTL of 3600 contradicted the CLI ("crash protection", default 86400) | Default TTL, renew at every turn start (§6.6.2) |
| Missing explicit `--executor` pulls in any agent's hooks | Always pass `--executor`; no lease for unmapped providers (§6.6.2) |
| `agent enable` has no destination flag | A15 restated as additive per-spawn injection that preserves the user's config and auth; hooks only, no skills (§6.6.1) |
| The hook process env was unspecified (binary, config dir) | Pinned `PATH` plus Atomic config dir on provider spawns; version asserted (§6.6.1, V16) |
| Hooks are cross-process writers; in-process locks can't close the race | Sequencing on run state (A26); V10 with hook writers; Q9 |
| Hook records aren't attribution-filtered | Advance every row whose path appears; `attribution_mismatch`; stray-view re-homing (§6.6.3) |
| `session show`/`fork` key on the provider session ID | `provider_session_id` on leases; fork re-specified; A25 |
| Lease PK `agent_id` couldn't model runs | `run_id` PK, nullable `agent_id`, index (§6.4) |
| No crash recovery for leases | Boot reconciler (§6.6.2); V22; Q13 |
| Ignore parity and secret leakage | §6.11 materialised excludes; A24; eligibility gate; V21 |
| Lifecycle operations destroyed unrecorded work; path changes on eject/convert | Record-before-destroying (§6.5); path-preserving directory swaps (§10.3, §10.6) |
| "Merge keeps bindings" relied on the RFC | A22 gates it; otherwise an unconditional rebuild; A23 `view switch --stash` alternative (§6.8) |
| Pushed branches and open PRs on conversion | Seeded publish checkout; refuse until A20; Q11 (§10.6) |
| `GitVcs` deletion vs. secondary roots/submodules | §10.5 item 2 and Q12 (`GitRootVcs` recommended) |
| Phase 8 removed `git.*` reads that Atomic still uses | `vcs.source.{clone,remoteUrl,branches,branchStatus}` aliases (§6.7) |
| "FE on `vcs.*` for both backends" was unmeetable | Git workspaces stay on `git.*` until conversion; the wire gate is measured after Phase 7 |
| `repository_path` was undefined for Atomic | Always the Git source (§6.5 row) |
| The `atomic` capability is dynamic | Availability snapshot into `server_json`, plus a `capabilities:changed` event (§6.7) |
| `vcs_for` was undefined for leftover Git rows after Phase 8 | `LegacyGitFrozen` / no-VCS adapter (§9); V19 |
| git2 use in `intent-acp`/`intent-svc-runtime` is test-only | Seam lint excludes `#[cfg(test)]` (§6.2) |
| V10 integrity check | `atomic doctor check` (read-only) |
| The mutating-`atomic` forbidden list was incomplete; nothing enforced it | `add`, `stash`, `tag` (+ `intent`/`memory`/`vault` per Q10); `agent.atomic_mutation_attempted` telemetry (§6.6.4) |

## References

- Atomic: https://github.com/atomicdotdev/atomic · https://docs.atomic.dev/ ·
  https://docs.atomic.dev/agents/overview
- https://github.com/atomicdotdev/atomic/blob/dev/docs/CONCURRENT-AGENT-SANDBOXES.md
- https://github.com/atomicdotdev/atomic/blob/dev/docs/RFC-ATOMIC-GIT-CAUSAL-BRIDGE.md
- https://github.com/atomicdotdev/atomic/blob/dev/docs/intent-graph.md
- https://github.com/atomicdotdev/atomic/blob/dev/docs/provenance-dsse-export.md
- Intent: `AGENTS.md`, `docs/ARCHITECTURE.md`, `docs/protocol/versioning.md`,
  `docs/protocol/node-checkpoints.md`, `docs/protocol/methods/{git,pr,change-tracking,workspace,
  repository-checkout,mcp-bindings}.md`, `docs/fe/code-review-ui.md`
