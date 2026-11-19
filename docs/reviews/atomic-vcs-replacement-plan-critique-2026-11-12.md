# Critique: Atomic VCS replacement plan (2026-11-12)

## Scope

- **Reviewed:** `docs/plans/atomic-vcs-replacement-2026-11-12.md`, read in full (1,761 lines).
- **Baseline:** the generated plan response in
  `prompt-exports/oracle-plan-2026-11-12-210954-plan-replace-git-wit-d9e5.md`, lines 125–907. The
  composed prompt and selection dump at the top of the export were treated as context only.
- **Not reopened:** the four §15.1 user decisions: D13 (strip `.git`), D11 (retire Git), D7
  (record every turn), D6 (hooks primary under leases, with Intent gap-filling). Findings below
  are about carrying those decisions out, not about whether to make them.
- **Evidence:** spot checks against the installed `atomic` 0.19.1 (`--help` for `agent
  lifecycle begin|renew|stop|resume|abandon|status`, `agent enable`, `agent status`, `git push`,
  `sandbox create`, `record`, `add`, `status`, `session show|fork`, `view switch`, `doctor`), plus
  these intentd files: `intent-git/src/attribution.rs`, `intent-services/src/{file_tracking,
  tracked_changes_sweep,agent_locks}.rs`, `intent-acp/src/mcp_server/bindings/{workspace,
  app/workspaces}.rs`, and `intent-transport/src/client.rs`.

Severity: **high** means it blocks correctness or causes data loss or leakage; **med** means a
real gap that will need rework if left alone; **low** means precision or hygiene.

---

## 1. Export content missing or weakened in the plan

**1.1 (med) Hook records drop the baseline's attribution filter (commit-set mode 3).**
- **What changed:** the export recorded only the agent's own attributed paths
  (`tracked_changes` ∩ status, export §4.6 step 2). Its D6 rejected hooks specifically because
  they "race Intent's own turn boundary and attribution filter."
- **Why it matters:** the plan keeps mode 3 for the gap-filler only. A hook-recorded change can
  contain any file dirty in the workdir: another agent's in-flight edits in the shared sandbox,
  terminal edits, or setup-script output. §6.6.3 step 3 then advances only "the agent's
  `unstaged` paths ∩ the change's files". Rows for other agents' paths are left stuck at
  `unstaged`, and those paths no longer appear in `atomic status`, so no gap-fill ever picks
  them up.
- **Fix:** state that hook records are not attribution-filtered. Advance every `tracked_changes`
  row whose path appears in an indexed change, whichever agent owns it, and set its
  `change_hash`. Emit `vcs.record.attribution_mismatch` when the change's files go beyond the
  leased agent's rows. Extend V5 to run with hooks enabled.

**1.2 (med) The rule for providers without a mapped executor got lost.**
- **What changed:** the export said "everything else → no lease". The plan says "any other
  provider gets no hooks", but §6.6.2 still begins a lease on every activation and does not say
  what `--executor` is then.
- **Why it matters:** `lifecycle begin --help` says that when `--executor` is omitted, "any agent
  inside the workdir participates". An unmapped provider would therefore pull in a user's global
  hooks, or a stray terminal agent's hooks, under Intent's lease.
- **Fix:** restore the export's rule: no lease without a mapped executor. Or always pass an
  explicit `--executor`. Never call `begin` without one.

(Nothing else implementation-bearing from the export is missing. The other differences are
logged corrections in §15.)

---

## 2. Contradictions, leftover pre-decision text, under-specified seams

**2.1 (high) Secondary Git roots and submodules keep `GitVcs`, which contradicts D11.**
- **The conflict:**
  - §6.2 step 3 and §11.2 say registered roots (`gitRootId`) "always use `GitVcs`".
  - §6.11 Phase 5 keeps submodules as Git `workspace_git_root` rows.
  - `ws.git.listRoots|registerRoot|unregisterRoot` stay as MCP bindings.
  - Phase 8 deletes `GitVcs`, and §10.5 item 2 counts submodules as supported through exactly
    those Git roots.
- **Fix:** decide what happens to roots (see Q6), then pick one of:
  - (a) keep a minimal `GitRootVcs` for secondary roots only, so Phase 8 deletes the
    *workspace* Git backend but not root support;
  - (b) make roots Atomic sub-repos;
  - (c) drop agent-registered roots for Atomic workspaces.

  Update D11, §10.5 item 2, §12.1 step 19 and V19 to match.

**2.2 (med) Phase 8 removes `git.*` reads that Atomic workspaces still use.**
- **The conflict:** §6.7 keeps `git.getBranches`, `git.branchStatus`, `git.pull` and
  `git.getRemoteUrl` as "path-based on the source repo; unchanged" for Atomic workspaces, and
  `BranchSelector` uses `getBranches` to pick the base ref at create time. Phase 8 keeps only
  `git.clone` and `git.getRemoteUrl` (as `vcs.source.*`).
- **Fix:** add `vcs.source.branches` (plus `branchStatus` if the FE still needs it) to the
  Phase 8 alias list. Define `git.pull` for Atomic as `vcs.syncTrunk` or remove it explicitly.

**2.3 (med) "Every FE surface on `vcs.*` for both backends" can't be met as specified, and its
phase is inconsistent.**
- **The inconsistency:** §6.7 puts the requirement in Phase 4; §10.1 puts it in Phase 3 scope.
- **The gap:** `vcs.*` has no Git equivalents for stage, unstage, stage/unstage hunk, fetch,
  rename branch or pull, and `vcs.publish`/`vcs.syncTrunk` are documented as `vcs-unsupported`
  on Git.
- **Fix:** drop the "both backends" requirement. Git workspaces stay on `git.*` until Phase 7
  converts them, and the §10.5 item 6 wire gate is measured after conversion. Alternatively, add
  Git-only `vcs.stage*`/`vcs.push` methods, but that is wire churn for a backend about to be
  deleted.

**2.4 (high) The publish working copy is unresolved, and eject contradicts A7.** See 4.3 for the
mechanism.
- Eject step 2 synthesises the branch "in the shared repo's `.git`".
- A7's fallback publishes from a "dedicated per-publish sandbox".
- `atomic git push --help` says the commit "is still created on the current branch", which in
  the shared repo is trunk.

**2.5 (med) `repository_path` is undefined for Atomic workspaces.**
- **The gap:** §6.5 maps every Git field except `repository_path`, but several things are keyed
  on it:
  - the "path-based on the source repo" `git.*` reads;
  - `proposeSibling` (`intent-acp/.../workspace.rs:143` `sibling_github_origin` calls
    `intent_git::remote::origin_url(repo_path)`);
  - workspace identity and roll-ups.
- **Why it matters:** for GitHub-hydrated `direct` workspaces it can today point at the checkout
  itself, which in an Atomic workspace is a sandbox with no `.git`.
- **Fix:** add a §6.5 row saying that `repository_path` holds the Git source (local repo or repo
  cache path), never the sandbox or `canonical_path`. Add a V6 case for `proposeSibling` and
  `getRemoteUrl` on an Atomic workspace.

**2.6 (med) The `atomic` capability is dynamic, but capability JSON is built statically at
hello time.**
- **The gap:** `intent-transport/src/client.rs` `server_json(has_display, os, arch, version, …)`
  has no access to `Services` or settings. `atomic` depends on `AtomicAvailability` and on
  `labs.atomicVcs`, which can change at runtime.
- **Fix:** pass an availability snapshot into `server_json`. Then either emit a
  `capabilities:changed` event or document that toggling the Labs flag needs a reconnect, and
  say so in `client-hello.md`.

**2.7 (low–med) The lease schema doesn't fit the lease model.**
- **The gap:** `atomic_agent_lease.agent_id PRIMARY KEY` allows one row per agent ever.
  - It cannot represent the `LEASE_PER_WORKSPACE` fallback.
  - It overwrites old `run_id`s, so late hook records or `lifecycle end` summaries from an
    earlier run can't be mapped back.
- **Fix:** make `run_id` the primary key and add an index on `(workspace_id, agent_id, state)`,
  plus a nullable `agent_id` for per-workspace runs.

**2.8 (low) Leftover pre-decision text.**
- §11.2 says "Product sign-off is needed (Q3)", but Q3 is resolved. Delete it.
- §12.1 step 10 says "`.git` neutralisation". Write "strip `.git` and verify (V17)".
- §6.3 says `AtomicRepoLocks` "deliberately serialises all writers in-process". That stopped
  being true under D6 (see 4.1). Reword it to "serialises Intent's writers".
- §6.2 step 1 says the direct git2 use in `intent-acp`/`intent-svc-runtime` "is transfer and
  node code". A spot check shows it is test-only (e.g.
  `intent-acp/.../app/workspaces.rs:2203` sits inside `#[cfg(test)] mod tests` at `:1286`;
  `intent-svc-runtime/{script_ops,terminal_ops}.rs` are test fixtures). The seam lint should
  exclude `#[cfg(test)]`/`tests.rs` rather than allow-listing those crates.

---

## 3. Details the code or CLI disproves (precise corrections)

**3.1 (high) The `tracked_changes` pipeline is not "reusable as-is". It depends on Git and
breaks once `.git` is stripped (D13).**
- **What breaks:**
  - `file_tracking.rs:105` `is_ignored_write` calls `intent_git::attribution::is_ignored_untracked`.
    Without a repo it answers `false`, so every agent write to an ignored path (`node_modules/`,
    `dist/`, `.env`) gets an `unstaged` row. That re-opens the intent-hq/intent#7266 class of
    bug: the row never leaves the working stage and locks the path forever.
  - `tracked_changes_sweep.rs:112` `classify_paths` fails when it can't open the repo, and the
    sweep's rule is "any scan failure deletes nothing", so those rows are never pruned.
  - `agent_locks.rs:208` `lockable_paths` returns every path when the repo can't be opened.
- **Fix:**
  - Put `is_ignored(path)`, `classify_paths(paths)` and `lockable_paths(status, paths)` behind
    `WorkspaceVcs`, with an Atomic implementation driven by `atomic status --json` and the
    ignore parity from 4.5.
  - Branch the sweep on `vcs_kind`.
  - Make this a prerequisite of WI-12 (list it under WI-11) and add a V-test: an agent writes an
    ignored file in an Atomic sandbox and no row persists.
  - Update §3.5 "Reusable as-is".

**3.2 (high) `atomic record` does not record untracked files by default.**
- **Evidence:** `record --help` shows `-a, --all  Record all changes including untracked files`,
  and `atomic add` exists, with `-f` to "force add ignored files".
- **Why it matters:** the §6.3 and §6.6.3 record commands
  (`record --ai-assisted … -- <FILES>`) will silently drop files that agents create.
- **Fix:**
  - For gap-fill and user records, first run `atomic add -- <new paths from status>`, under the
    repo lock. Or validate that explicit `[FILES]` adds untracked paths (extend A11).
  - Add `add` to the `AtomicRepoLocks` list and to the agent "do not run" list (§6.6.4).
  - Add a V5 case for a newly created file.

**3.3 (med) `session show` and `session fork` take the *external agent session ID*, not
Intent's IDs.**
- **Evidence:** the help text says `[SESSION_ID] External agent session ID` and
  `<PARENT_SESSION_ID> External session ID`. `lifecycle begin --session` is a different thing,
  the *owner* session.
- **What's wrong in the plan:**
  - It never says where `atomic_turn_record.atomic_session` comes from.
  - `atomic.session.fork` calls `session fork <agentId>`, which is wrong, and it fails outright
    under `LEASE_PER_WORKSPACE`.
  - `--child` must be a provider session ID that doesn't exist until the provider starts the
    forked session.
- **Fix:**
  - Capture the provider's session ID (the ACP or provider session handle) on the lease row, or
    read it from `lifecycle end --json` / `session show` (no ID) filtered by workdir.
  - Re-specify fork as: create a provider session, then
    `session fork <providerSessionId> --at-turn N --child <newProviderSessionId>`.
  - Add an A-item for the mapping.

**3.4 (high) Abandoning on every cancelled turn strands the long-lived provider process.**
- **Evidence:** `abandon` "Explicitly abandon and seal a pending turn", while `resume` applies
  to "a stopped managed run".
- **What the plan does:** it abandons on `cancelled`/`error` and resumes at the "next
  activation".
- **Why it matters:** ACP providers are long-lived across turns, with the hook configuration
  fixed at spawn. Users routinely cancel and then type again in the same session. If `abandon`
  ends the run, the next turn's hooks run unleased, and per `begin --help` they "fork their
  usual per-session view", so records land outside `ws-<id>`.
- **Fix:**
  - A18 must also establish the run's state after `abandon`.
  - If the run is terminal, `begin` a new run (same view and workdir, new `run_id`) *before the
    next prompt is accepted*: gate turn start on lease state, not on activation.
  - Otherwise, use `stop --cause user-requested` and then `resume`.
  - Cover cancel-then-continue in V16.

**3.5 (med) The 1 h TTL contradicts the CLI's intent and invites expiry mid-run.**
- **Evidence:** `begin --help` says the TTL "is crash protection, not a session limit
  [default: 86400]". The plan uses `--ttl-seconds 3600` with a 20 min renew.
- **Why it matters:** laptop sleep or a stalled daemon for more than 1 h expires the lease while
  the provider keeps running with hooks, which leads to stray views as in 3.4. The plan has no
  detection or recovery for this.
- **Fix:**
  - Use the default TTL, or set it explicitly to ≥ 24 h.
  - Renew at every turn start as well as on the timer.
  - At idle, detect hook changes whose session is this provider's but whose view is not
    `ws-<id>`, then `insert change … --to-view ws-<id>` and index them (`late_hook` →
    `stray_view` telemetry).

**3.6 (low) A21 is resolved, and a stop cause is missing.**
- `lifecycle renew --run-id <RUN_ID> [--ttl-seconds]` exists, so A21 is resolved. Mark it so in
  §11.1.
- `stop --cause` also accepts `hook-failure`. Use it when the hook health check fails (§6.6.1);
  the plan lists only three causes.

**3.7 (med) A15's "`agent enable --hooks <manifest>` targeted at that scope" isn't something
the CLI offers.**
- **Evidence:** `agent enable` has project-local (the default), `-g` (it writes
  `~/.claude/settings.json`), `--hooks <FILE>` (an integration manifest *source*, not a
  destination) and `--from`. There is no destination or scope flag.
- **What that means:** the only Intent-scoped path is for Intent to generate hook configuration
  itself and inject it per provider spawn.
- **Why it matters:** swapping in a "per-daemon provider config dir" would also hide the user's
  provider auth, settings, plugins and MCP config.
- **Fix:** restate A15 as an additive, per-invocation hook injection that preserves the user's
  provider config and auth (an extra settings file layered on top, or a CLI override, per
  provider). Make "user config and auth unchanged" an explicit V16 assertion.

**3.8 (low) V10's integrity check should name the read-only subcommand.** `atomic doctor` has
repairing subcommands (`repair-dependency-index`, `materialize-crdt`). V10 should require
`atomic doctor check`, which its help describes as read-only.

**3.9 (low) Use the native AI flags in `record`.**
- **What's there:** `record` has `--ai-session-id`, `--ai-tool`, `--ai-request-id`,
  `--ai-input-tokens`/`--ai-output-tokens` and `--ai-cost-usd`.
- **The gap:** §6.3 maps only provider and model, so `AiMeta.session_id` and `turn` live only
  in message trailers.
- **Fix:** pass `--ai-session-id` (and `--ai-tool intent`) on gap-fill records so that Atomic's
  own provenance queries see them. Keep the trailers for the Git projection.

---

## 4. Problems absent from both

**4.1 (high) Hooks are cross-process writers, so `AtomicRepoLocks` cannot close the race.**
- **The problem:** under D6, hook recorders run inside provider processes and write to the
  *shared* canonical redb. That covers every agent in every workspace of the same source repo,
  which is exactly the "concurrent cross-process writers, not load-tested" case that §6.3 says
  in-process locks avoid. The §6.6.3 race rule ("the gap-filler … takes `AtomicRepoLocks`")
  orders the gap-filler only against other Intent writers, not against a hook that is still
  recording.
- **Fix:**
  - (a) Sequence the gap-filler on Atomic-side state. Proceed only when
    `lifecycle status --json` (or the session ledger) shows no pending or unsealed turn for the
    run, or after `abandon`/`stop` returns. Add an A-item that this state is observable.
  - (b) Make V10 run with hook writers from several workspaces at once, plus Intent records.
  - (c) Decide Q1 (shared vs per-workspace canonical repo).
  - (d) Specify what a hook does on a redb lock timeout: whether it fails the provider's turn
    or skips. Hook failures must never block the agent.

**4.2 (high) The hook process environment isn't specified: binary, config dir, lease
visibility.**
- **The problem:** hooks run `atomic` from inside the provider process.
  - Intent pins a bundled binary that isn't on the provider's `PATH`.
  - `AtomicCli` points Atomic's config dir at `<daemon data dir>/atomic`, while session ledgers
    observably live under the config dir (`~/.atomic/sessions` exists on this host).
  - If provider spawns don't carry the same binary path and config dir, hooks either resolve
    the user's `atomic` (another version) or none, and they read a different registry where
    Intent's lease isn't visible. They then behave as unleased, as in 3.4.
  - "User-installed global hooks" (§6.6.1) always use the user's binary and config, so deferring
    to them breaks version pinning.
- **Fix:**
  - Specify the provider spawn environment: put the pinned `atomic` first on `PATH` and set the
    same `ATOMIC_*` config-dir variables as `AtomicCli`.
  - Add a V16 assertion that the hook's `atomic --version` equals the pinned version.
  - For user-global hooks, don't defer to them. Override them, or treat them as untrusted
    (detect, then gap-fill), and record which binary recorded each change.

**4.3 (high) Publishing needs a persistent, per-workspace Git working copy. Neither document
designs one.**
- **The mechanism:** `git push` commits on the *current Git branch*.
  - **Run in the canonical repo** (where trunk is checked out), it commits onto local trunk.
    That pollutes the mirror that the next `git import --incremental --branch <baseRef>` reads,
    and contaminates every other workspace's trunk view.
  - **Run in A7's throwaway sandbox** (whose `.git` is a reflink copy at trunk), the commit
    lands in a discarded object store. The second publish then has the base trunk commit as its
    parent instead of the previous publish, so the push is non-fast-forward and is rejected
    (force-push is ruled out in §6.8).
  - **After `vcs.syncTrunk`**, nothing says whether trunk becomes an ancestor of the next
    publish commit. If it doesn't, the GitHub PR diff shows trunk changes as PR changes.
- **Fix:**
  - Give each workspace a hidden publish checkout under `.atomic-repos/<key>/publish/<id>`: an
    Atomic sandbox `--view ws-<id>` whose `.git` is replaced by a `git worktree` link to the
    canonical `.git` on branch `<branch>`. It is created at the first publish and removed on
    delete.
  - Commits then persist in the shared object store, and successive publishes fast-forward.
  - Extend A7 to prove: (i) successive publishes fast-forward; (ii) the first parent is
    `base_commit_sha`; (iii) after a sync, the trunk tip is an ancestor; (iv) the canonical
    trunk ref never moves.
  - Use the same checkout for eject (step 2) and conversion.
  - Exclude it from D13 and from the ownership proof explicitly: it is daemon-only and never
    agent-visible.

**4.4 (high) Conversion and eject break any branch that already has a remote or an open PR.**
- **The problem:** §10.6 keeps `branch` as the publish branch and keeps the PR linked. The first
  Atomic publish synthesises a commit that isn't a descendant of the remote branch tip, so the
  push is non-fast-forward. The same happens after eject → re-convert.
- **Fix:**
  - Seed the 4.3 publish checkout at the existing remote tip, and require (in A20) that the first
    publish after conversion fast-forwards from it.
  - Otherwise, refuse conversion for pushed branches until a policy exists (Q4).
  - Add an "open PR" case to V18.

**4.5 (high) Ignore parity and secret leakage.**
- **The problem:** neither document checks *which* ignore rules Atomic applies. `add -f` shows
  that Atomic has its own ignore mechanism.
  - Stripping `.git` (D13) also removes `.git/info/exclude`, and Atomic may not read the user's
    `core.excludesFile`.
  - Hooks record workdir-wide, so anything Atomic doesn't ignore (`.env`, credentials, build
    output) gets recorded, and is then published to GitHub by `git push`.
- **Fix:**
  - Add an A-item: Atomic honours nested `.gitignore`s; `info/exclude` and global excludes are
    carried over.
  - At repo import, materialise the source repo's `info/exclude` and the global excludes into
    the canonical repo's Atomic ignore configuration (repo-level, not committed to the tree).
  - Add a V-test: an agent writes `.env` and a `node_modules/` file, and neither the hook nor
    the gap-filler records them.

**4.6 (med–high) Lease lifecycle across a daemon crash or restart.**
- **The problem:** §8 covers only a clean shutdown (`stop --cause system-shutdown`).
  - After a crash, `atomic_agent_lease` rows and upstream runs stay `active` until the TTL runs
    out.
  - On reactivation, `resume` (stopped runs only) may refuse.
  - Falling back to `begin` then creates a second active run on the same view and workdir,
    which is the unverified A10 case.
- **Fix:**
  - Add a boot reconciler. It runs `lifecycle status --json` and, for each `owner=intent` run
    with no live provider process, calls `stop --cause process-exited` and marks the row
    `stopped`. Reactivation then resumes cleanly.
  - Make reconciliation a precondition of accepting turns in Atomic workspaces.
  - Add a V-test: kill -9 the daemon mid-turn, restart, and the next turn records into
    `ws-<id>`.

**4.7 (med) Lifecycle operations that destroy the sandbox don't record first.**
- **The problem:**
  - Retire, delete, the post-merge "recreate the sandbox at the same path", eject and conversion
    all discard unrecorded edits. Under D7 nothing should be lost silently, yet the plan accepts
    "unrecorded work is lost" on revive.
  - Recreating the sandbox also throws away ignored build artifacts (`node_modules`), so the
    setup script has to re-run.
- **Fix:**
  - Before any of these, require agents stopped, run a final gap-fill record (`Intent-Recorder:
    lifecycle`), then proceed.
  - For the view rebuild, evaluate the simpler alternative of an in-place `atomic view switch
    --stash ws-<id>-<n>` inside the sandbox. It exists in 0.19.1; validate that it is
    sandbox-scoped. It keeps the path, the ignored files and running terminals intact.

**4.8 (med) Path changes on eject and conversion (`<slug>-git` / `<slug>-atomic`).**
- **The problem:** "Copy nothing else" loses ignored and untracked-ignored files (`.env`,
  caches) and orphans running terminals and scripts whose cwd is the old path. Rebinding
  `worktree_path` also affects scripts, browser tabs and anything keyed on the path.
- **Fix:**
  - Stop workspace scripts and terminals first.
  - Move ignored files into the new checkout, then swap directories under the archive fence so
    that `worktree_path` stays the same.
  - Add V11 and V18 assertions that `.env` survives.

**4.9 (med) The hook bundle may undercut the "no mutating `atomic`" rule, and nothing enforces
the rule.**
- **The problem:**
  - `agent enable` syncs an integration package and a skills package (`--from-skills`). Those
    skills tell agents to run `atomic intent|memory|vault|record`.
  - §6.6.4 relies on instructions alone.
  - The forbidden list omits `add`, `stash`, `tag`, `intent`, `memory` and `vault`.
- **Fix:**
  - Inject hooks only, never skills.
  - Decide Q3 (vault and memory writes).
  - Detect mutating `atomic` runs by agents through ACP tool-call inspection
    (`agent.atomic_mutation_attempted`, like `agent.git_command_failed`).
  - At idle, flag any change in `ws-<id>` whose recorder is neither hook nor Intent.

**4.10 (med) The post-merge mitigation assumes the RFC's bindings.**
- **The problem:** §6.8 relies on "`merge` keeps the original commits and bindings", but binding
  headers (`atomic-binding`, …) are part of the *proposed* Causal Bridge. Nothing shows that
  0.19.1's `git push` emits them, or that `git import` recognises them.
- **Fix:** add an A-item. If bindings are absent, make the view rebuild unconditional after
  *every* merge strategy and drop the "default `mergeStrategy` to `merge`" lever, which changes
  repository merge behaviour for no benefit. V9 already uses the real binary, so it decides
  this.

**4.11 (low–med) `vcs_for` after Phase 8 when a row still says `git`.**
- **The problem:** plain folders keep `vcs_kind='git'`, and a restored backup or a DB synced from
  an older daemon can bring back unconverted Git rows. With `GitVcs` deleted, dispatch for these
  rows is undefined.
- **Fix:** define `vcs_for` as plain folder → no-VCS adapter. A non-plain row with `vcs_kind=git`
  → read-only `LegacyGitFrozen` (folder reads plus a "convert" banner), or a forced conversion at
  boot. Add the case to V19.

---

## 5. Questions that change the design or implementation order

1. **Shared or per-workspace canonical Atomic repo?** With hooks as cross-process writers (4.1),
   one redb per source repo puts every workspace's hooks on one lock. Per-workspace repos trade
   disk for isolation and remove cross-workspace contamination risk (4.3). This changes §6.4
   `atomic_repo`, the locking, and the V10 design. Answer it before WI-7.
2. **May Intent alter provider configuration to inject hooks?** It needs a per-provider
   mechanism that keeps the user's auth and settings (3.7). If no provider allows that, D6
   degrades to "gap-filler only" for that provider. This decides what Phase 1 can exit on.
3. **Are Atomic knowledge writes (`intent`, `memory`, `vault`) allowed for agents in
   sandboxes?** This decides whether skills are installed and what the forbidden list contains
   (4.9).
4. **Converting pushed branches or open PRs:** allow a single explicit force-push at conversion,
   or refuse until a fast-forward is proven (4.4)? This gates Phase 7.
5. **Do provider processes survive or resume across daemon restarts?** That decides whether the
   boot reconciler (4.6) stops runs or re-adopts them.
6. **What happens to secondary Git roots and submodules at retirement** (2.1)? This decides
   whether `GitVcs` can actually be deleted and what V19 asserts.
7. **Order:** 3.1 (attribution behind the seam), 3.2 (untracked files), 4.2 (hook environment)
   and 4.5 (ignore parity) are prerequisites of WI-12, and 4.3 (publish checkout) is a
   prerequisite of WI-13. Should they be added to WI-11 / Phase 1 exit criteria? Recommended:
   yes.
