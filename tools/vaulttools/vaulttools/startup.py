"""Refresh configured Git scopes while preserving contribution work."""

from __future__ import annotations

import json
import os
import re
import tempfile
import time
from contextlib import suppress
from dataclasses import dataclass, replace
from pathlib import Path

from .board import Config, Repo, Scope, VaultError

_GIT_ENV = {"GIT_LFS_SKIP_SMUDGE": "1"}
_MUTATION_HOOKS = ("reference-transaction", "pre-merge-commit", "post-merge")
_OPERATIONS = (
    "MERGE_HEAD",
    "CHERRY_PICK_HEAD",
    "REVERT_HEAD",
    "BISECT_LOG",
    "rebase-merge",
    "rebase-apply",
)
_POINTER_RE = re.compile(
    rb"version https://git-lfs.github.com/spec/v1\n"
    rb"oid sha256:([0-9a-f]{64})\n"
    rb"size ([0-9]+)\n?\Z"
)


class _DeadlineReached(VaultError):
    """The whole-run work or reporting window is exhausted."""


@dataclass(frozen=True)
class ScopeReport:
    """Observed result for one configured checkout."""

    name: str
    path: Path
    configured: str = "-"
    initial_head: str = "-"
    final_head: str = "-"
    target: str = "-"
    relation: str = "unknown"
    refresh: str = "preserved"
    lfs_remote: str = "not-used"
    lfs_cache: str = "not-used"
    assets: str = "not-applicable"
    submodules: str = "not-inspected"
    detail: str = ""
    attention: bool = True
    git_dir: Path | None = None
    common_dir: Path | None = None
    action: str = "inspect"


@dataclass(frozen=True)
class Report:
    """The bounded result of a startup traversal."""

    rows: tuple[ScopeReport, ...]
    complete: bool = True

    @property
    def attention(self) -> bool:
        return not self.complete or any(row.attention for row in self.rows)

    @property
    def exit_code(self) -> int:
        return 0 if self.complete else 124


@dataclass(frozen=True)
class _Budget:
    started: float
    child_limit: float
    hard_deadline: float
    work_deadline: float

    @classmethod
    def start(cls, child_limit: float, deadline: int) -> _Budget:
        if child_limit <= 0:
            raise VaultError("startup timeout must be greater than zero")
        if deadline < 2:
            raise VaultError("startup deadline must be at least 2 seconds")
        reserve = min(10, max(1, deadline // 10))
        if deadline <= reserve:
            raise VaultError("startup deadline must exceed its report reserve")
        started = time.monotonic()
        return cls(started, child_limit, started + deadline, started + deadline - reserve)

    def _remaining(self, boundary: float, label: str) -> float:
        remaining = boundary - time.monotonic()
        if remaining <= 0:
            raise _DeadlineReached(label)
        return min(self.child_limit, remaining)

    def work_timeout(self) -> float:
        return self._remaining(self.work_deadline, "whole-run work deadline")

    def report_timeout(self) -> float:
        return self._remaining(self.hard_deadline, "whole-run report deadline")

    def work_expired(self) -> bool:
        return time.monotonic() >= self.work_deadline

    def hard_expired(self) -> bool:
        return time.monotonic() >= self.hard_deadline


@dataclass(frozen=True)
class _Worktree:
    scope: Scope
    path: Path
    top: Path
    git_dir: Path
    common_dir: Path

    @property
    def identity(self) -> tuple[Path, Path]:
        return self.top, self.git_dir


@dataclass(frozen=True)
class _Snapshot:
    head: str
    branch: str | None
    status: str
    operations: tuple[str, ...]
    locks: tuple[str, ...]

    @property
    def clean(self) -> bool:
        return not self.status and not self.operations and not self.locks


@dataclass(frozen=True)
class _LfsResult:
    remote: str
    cache: str
    assets: str
    detail: str = ""
    attention: bool = False


@dataclass(frozen=True)
class _RefreshResult:
    row: ScopeReport
    deadline: bool = False
    complete: bool = True


def _configured(scope: Scope) -> str:
    return f"branch:{scope.branch}" if scope.branch is not None else f"pin:{scope.pin}"


def _action(row: ScopeReport) -> str:
    if not row.attention:
        return "none"
    if row.refresh in {"deadline", "unvisited"}:
        return "rerun the bounded startup report"
    if row.refresh in {"missing", "unavailable", "stale"}:
        return "inspect the configured path or origin; independent work may continue"
    if row.lfs_cache in {"partial", "unavailable", "unknown"} or row.assets in {
        "partial",
        "unknown",
    }:
        return "inspect Git LFS before using affected assets"
    return "inspect and refresh this checkout separately"


def _call(
    repo: Repo,
    *args: str,
    budget: _Budget,
    check: bool = True,
    report_phase: bool = False,
    input_text: str | None = None,
):
    timeout = budget.report_timeout if report_phase else budget.work_timeout
    try:
        return repo.git(
            *args,
            check=check,
            timeout=timeout,
            env=_GIT_ENV,
            input_text=input_text,
        )
    except VaultError as error:
        expired = budget.hard_expired() if report_phase else budget.work_expired()
        if expired:
            raise _DeadlineReached(str(error)) from error
        raise


def _local(
    repo: Repo,
    *args: str,
    budget: _Budget,
    check: bool = True,
    report_phase: bool = False,
) -> str:
    return _call(
        repo,
        *args,
        budget=budget,
        check=check,
        report_phase=report_phase,
    ).stdout.strip()


def _raw(
    repo: Repo,
    *args: str,
    budget: _Budget,
    report_phase: bool = False,
    input_text: str | None = None,
) -> str:
    return _call(
        repo,
        *args,
        budget=budget,
        report_phase=report_phase,
        input_text=input_text,
    ).stdout


def _git_path(repo: Repo, name: str, budget: _Budget, *, report_phase: bool = False) -> Path:
    raw = _local(repo, "rev-parse", "--git-path", name, budget=budget, report_phase=report_phase)
    path = Path(raw)
    return (repo.root / path).resolve() if not path.is_absolute() else path.resolve()


def _snapshot(repo: Repo, budget: _Budget, *, report_phase: bool = False) -> _Snapshot:
    head = _local(repo, "rev-parse", "HEAD", budget=budget, report_phase=report_phase)
    branch_result = _call(
        repo,
        "symbolic-ref",
        "--quiet",
        "--short",
        "HEAD",
        budget=budget,
        check=False,
        report_phase=report_phase,
    )
    branch = branch_result.stdout.strip() if branch_result.returncode == 0 else None
    status = _local(
        repo,
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
        budget=budget,
        report_phase=report_phase,
    )
    operations = tuple(
        name for name in _OPERATIONS if _git_path(repo, name, budget, report_phase=report_phase).exists()
    )
    lock_paths = {
        "index.lock": _git_path(repo, "index", budget, report_phase=report_phase).with_name("index.lock"),
        "HEAD.lock": _git_path(repo, "HEAD", budget, report_phase=report_phase).with_name("HEAD.lock"),
        "packed-refs.lock": _git_path(repo, "packed-refs", budget, report_phase=report_phase).with_name(
            "packed-refs.lock"
        ),
    }
    locks = tuple(name for name, path in lock_paths.items() if path.exists())
    return _Snapshot(head, branch, status, operations, locks)


def _active_hooks(repo: Repo, budget: _Budget) -> tuple[str, ...]:
    active: list[str] = []
    for name in _MUTATION_HOOKS:
        path = _git_path(repo, f"hooks/{name}", budget)
        if not path.is_file() or not os.access(path, os.X_OK):
            continue
        # Git LFS installs this generated hook, but the kernel skips it during
        # Git advancement and performs its own bounded LFS phase.
        if (
            name == "post-merge"
            and path.stat().st_size <= 8192
            and b"git lfs post-merge" in path.read_bytes()
        ):
            continue
        active.append(name)
    return tuple(active)


def _worktree(scope: Scope, vault: Path, budget: _Budget) -> _Worktree | None:
    path = (vault / scope.path).resolve()
    if not path.exists():
        return None
    repo = Repo(path)
    result = _call(
        repo,
        "rev-parse",
        "--is-inside-work-tree",
        budget=budget,
        check=False,
    )
    if result.returncode or result.stdout.strip() != "true":
        return None
    top = Path(_local(repo, "rev-parse", "--show-toplevel", budget=budget)).resolve()
    rooted = Repo(top)
    git_dir = Path(_local(rooted, "rev-parse", "--absolute-git-dir", budget=budget)).resolve()
    common_raw = _local(rooted, "rev-parse", "--git-common-dir", budget=budget)
    common = Path(common_raw)
    common_dir = (top / common).resolve() if not common.is_absolute() else common.resolve()
    return _Worktree(scope, path, top, git_dir, common_dir)


def _unvisited(scope: Scope, vault: Path, detail: str = "whole-run deadline") -> ScopeReport:
    return ScopeReport(
        scope.name,
        (vault / scope.path).resolve(),
        _configured(scope),
        relation="unvisited",
        refresh="unvisited",
        assets="unknown",
        detail=detail,
        action="rerun the bounded startup report",
    )


def _inventory(vault: Path, config: Config, budget: _Budget) -> tuple[list[_Worktree], list[ScopeReport]]:
    if not config.scopes:
        raise VaultError("[scopes] is empty; configure at least one path and branch or pin")
    worktrees: list[_Worktree] = []
    missing: list[ScopeReport] = []
    identities: dict[tuple[Path, Path], str] = {}
    for scope in config.scopes:
        try:
            worktree = _worktree(scope, vault, budget)
        except _DeadlineReached:
            raise
        except VaultError as error:
            missing.append(
                ScopeReport(
                    scope.name,
                    (vault / scope.path).resolve(),
                    _configured(scope),
                    refresh="unavailable",
                    detail=str(error),
                )
            )
            continue
        if worktree is None:
            missing.append(
                ScopeReport(
                    scope.name,
                    (vault / scope.path).resolve(),
                    _configured(scope),
                    refresh="missing",
                    detail="configured path is missing or is not a Git worktree",
                )
            )
            continue
        previous = identities.get(worktree.identity)
        if previous is not None:
            raise VaultError(
                f"scopes {previous!r} and {scope.name!r} name the same worktree {worktree.top}"
            )
        identities[worktree.identity] = scope.name
        worktrees.append(worktree)

    vault_identity: tuple[Path, Path] | None = None
    try:
        vault_worktree = _worktree(Scope("self", ".", branch="HEAD"), vault, budget)
        if vault_worktree is not None:
            vault_identity = vault_worktree.identity
    except _DeadlineReached:
        raise
    except VaultError:
        pass
    worktrees.sort(key=lambda item: item.identity == vault_identity)
    return worktrees, missing


def _fetch_target(repo: Repo, scope: Scope, budget: _Budget, empty_hooks: Path) -> tuple[str | None, str]:
    common = (
        "-c",
        "fetch.recurseSubmodules=false",
        "-c",
        "submodule.recurse=false",
        "-c",
        f"core.hooksPath={empty_hooks}",
        "fetch",
        "--quiet",
        "--no-tags",
        "--no-recurse-submodules",
        "--no-auto-maintenance",
        "--no-write-commit-graph",
        "--refmap=",
        "origin",
    )
    if scope.branch is not None:
        destination = f"refs/remotes/origin/{scope.branch}"
        refspec = f"+refs/heads/{scope.branch}:{destination}"
        result = _call(repo, *common, refspec, budget=budget, check=False)
        if result.returncode:
            return None, (result.stderr or result.stdout).strip()
        target = _local(repo, "rev-parse", f"{destination}^{{commit}}", budget=budget)
    else:
        assert scope.pin is not None
        result = _call(repo, *common, scope.pin, budget=budget, check=False)
        if result.returncode:
            return None, (result.stderr or result.stdout).strip()
        target = _local(repo, "rev-parse", "FETCH_HEAD^{commit}", budget=budget)
        if target.lower() != scope.pin:
            return None, f"origin returned {target}, not configured pin {scope.pin}"
    if _local(repo, "cat-file", "-t", target, budget=budget) != "commit":
        return None, f"fetched target {target} is not a commit"
    return target, ""


def _relation(repo: Repo, head: str, target: str, budget: _Budget) -> tuple[int, int]:
    raw = _local(
        repo,
        "rev-list",
        "--left-right",
        "--count",
        f"{head}...{target}",
        budget=budget,
    )
    try:
        ahead, behind = (int(value) for value in raw.split())
    except (TypeError, ValueError) as error:
        raise VaultError(f"could not classify {head} against {target}: {raw!r}") from error
    return ahead, behind


def _incoming_blockers(repo: Repo, head: str, target: str, budget: _Budget) -> tuple[str, ...]:
    changed = _raw(
        repo,
        "diff",
        "--name-only",
        "--diff-filter=ACMRT",
        "-z",
        head,
        target,
        budget=budget,
    ).split("\0")
    tracked = set(_raw(repo, "ls-files", "-z", budget=budget).split("\0"))
    blockers: set[str] = set()
    for name in (item for item in changed if item):
        path = repo.root / name
        if os.path.lexists(path) and name not in tracked:
            blockers.add(name)
        parent = path.parent
        while parent != repo.root and repo.root in parent.parents:
            if os.path.lexists(parent) and not parent.is_dir():
                blockers.add(str(parent.relative_to(repo.root)))
                break
            parent = parent.parent
    return tuple(sorted(blockers))


def _changed_populated_submodules(repo: Repo, head: str, target: str, budget: _Budget) -> tuple[str, ...]:
    changed = _raw(repo, "diff", "--name-only", "-z", head, target, budget=budget).split("\0")
    blocked: list[str] = []
    for name in (item for item in changed if item):
        before = _call(repo, "ls-tree", head, "--", name, budget=budget, check=False).stdout
        after = _call(repo, "ls-tree", target, "--", name, budget=budget, check=False).stdout
        if (before.startswith("160000 ") or after.startswith("160000 ")) and (repo.root / name).is_dir():
            blocked.append(name)
    return tuple(blocked)


def _show_optional(repo: Repo, revision: str, path: str, budget: _Budget) -> str | None:
    result = _call(repo, "show", f"{revision}:{path}", budget=budget, check=False)
    return result.stdout if result.returncode == 0 else None


def _lfs_inventory(repo: Repo, revision: str, budget: _Budget) -> list[dict[str, object]]:
    raw = _local(repo, "lfs", "ls-files", "--json", revision, budget=budget)
    payload = json.loads(raw)
    files = payload.get("files") if isinstance(payload, dict) else None
    if not isinstance(files, list) or any(not isinstance(item, dict) for item in files):
        raise VaultError("git lfs ls-files returned malformed JSON")
    return files


def _lfs_paths(repo: Repo, target: str, budget: _Budget) -> tuple[str, ...]:
    names = _raw(repo, "ls-tree", "-r", "-z", "--name-only", target, budget=budget)
    if not names:
        return ()
    raw = _raw(
        repo,
        "check-attr",
        f"--source={target}",
        "--stdin",
        "-z",
        "filter",
        budget=budget,
        input_text=names + ("" if names.endswith("\0") else "\0"),
    )
    fields = raw.split("\0")
    if not fields or fields[-1] != "" or (len(fields) - 1) % 3:
        raise VaultError("git check-attr returned malformed NUL records")
    return tuple(fields[index] for index in range(0, len(fields) - 1, 3) if fields[index + 2] == "lfs")


def _pointers(repo: Repo, target: str, paths: tuple[str, ...], budget: _Budget) -> dict[str, str]:
    pointers: dict[str, str] = {}
    for path in paths:
        result = _call(repo, "show", f"{target}:{path}", budget=budget, check=False)
        if result.returncode:
            raise VaultError(f"cannot read LFS pointer {path!r} at captured target")
        match = _POINTER_RE.fullmatch(result.stdout.encode("utf-8"))
        if match is None:
            raise VaultError(f"{path!r} is marked as LFS but is not a canonical pointer")
        pointers[path] = match.group(1).decode("ascii")
    return pointers


def _hydration_gate(
    repo: Repo,
    scope: Scope,
    target: str,
    initially_preserved: bool,
    budget: _Budget,
) -> tuple[bool, str]:
    if initially_preserved:
        return False, ""
    hooks = _active_hooks(repo, budget)
    if hooks:
        return False, "active mutation hooks appeared before LFS hydration: " + ", ".join(hooks)
    snapshot = _snapshot(repo, budget)
    if not snapshot.clean or snapshot.head != target:
        return False, "checkout changed before LFS hydration"
    if scope.pin is not None:
        return True, ""
    if snapshot.branch != scope.branch:
        return False, "configured branch changed before LFS hydration"
    return True, ""


def _lfs(
    repo: Repo,
    scope: Scope,
    target: str,
    initially_preserved: bool,
    budget: _Budget,
    empty_hooks: Path,
) -> _LfsResult:
    try:
        paths = _lfs_paths(repo, target, budget)
        if not paths:
            return _LfsResult("not-used", "not-used", "not-applicable")
        pointers = _pointers(repo, target, paths, budget)
    except _DeadlineReached:
        raise
    except (VaultError, ValueError) as error:
        return _LfsResult("unknown", "unknown", "unknown", str(error), True)

    version = _call(repo, "lfs", "version", budget=budget, check=False)
    if version.returncode:
        return _LfsResult("unavailable", "unavailable", "unknown", "git-lfs is unavailable", True)
    head = _local(repo, "rev-parse", "HEAD", budget=budget)
    if head != target and _show_optional(repo, head, ".lfsconfig", budget) != _show_optional(
        repo, target, ".lfsconfig", budget
    ):
        return _LfsResult(
            "unknown",
            "unknown",
            "preserved",
            "captured target changes .lfsconfig; endpoint was not contacted",
            True,
        )

    lfs_args = (
        "-c",
        "lfs.fetchrecentalways=false",
        "-c",
        "lfs.fetchrecentremoterefs=false",
        "-c",
        "lfs.fetchrecentrefsdays=0",
        "-c",
        "lfs.fetchrecentcommitsdays=0",
        "-c",
        f"core.hooksPath={empty_hooks}",
        "lfs",
        "fetch",
        "-I",
        "",
        "-X",
        "",
        "origin",
        target,
    )
    fetched = _call(repo, *lfs_args, budget=budget, check=False)
    remote = "fetched" if fetched.returncode == 0 else "failed"
    fetch_detail = "" if fetched.returncode == 0 else (fetched.stderr or fetched.stdout).strip()

    try:
        inventory = _lfs_inventory(repo, target, budget)
    except (VaultError, json.JSONDecodeError) as error:
        return _LfsResult(
            remote,
            "unknown",
            "unknown",
            f"{fetch_detail}; {error}".strip("; "),
            True,
        )
    inventory_oids = {
        str(item.get("name")): str(item.get("oid")).removeprefix("sha256:") for item in inventory
    }
    if inventory_oids != pointers:
        return _LfsResult(
            remote,
            "unknown",
            "unknown",
            "Git attributes, pointers, and LFS inventory disagree",
            True,
        )
    cache_complete = all(bool(item.get("downloaded")) for item in inventory)
    cache = "complete" if cache_complete else "partial"
    assets = "preserved"
    detail = fetch_detail
    can_hydrate, gate_detail = _hydration_gate(repo, scope, target, initially_preserved, budget)
    if gate_detail:
        detail = "; ".join(part for part in (detail, gate_detail) if part)
    if can_hydrate:
        assets = "pointer-only"
        if cache_complete:
            hydrated = _call(
                repo,
                "-c",
                f"core.hooksPath={empty_hooks}",
                "lfs",
                "checkout",
                budget=budget,
                check=False,
            )
            final_gate, final_detail = _hydration_gate(repo, scope, target, False, budget)
            current = _lfs_inventory(repo, "HEAD", budget)
            readable = {
                str(item.get("name")): str(item.get("oid")).removeprefix("sha256:")
                for item in current
                if bool(item.get("downloaded"))
            }
            if hydrated.returncode == 0 and final_gate and readable == pointers:
                assets = "readable"
            else:
                assets = "partial"
                command_detail = (hydrated.stderr or hydrated.stdout).strip()
                detail = "; ".join(part for part in (detail, command_detail, final_detail) if part)
    attention = (
        remote != "fetched"
        or cache != "complete"
        or (can_hydrate and assets != "readable")
        or bool(gate_detail)
    )
    return _LfsResult(remote, cache, assets, detail, attention)


def _deadline_result(
    worktree: _Worktree,
    initial: _Snapshot | None,
    target: str,
    budget: _Budget,
    detail: str,
) -> _RefreshResult:
    final_head = "unknown"
    evidence = detail
    complete = True
    try:
        final = _snapshot(Repo(worktree.top), budget, report_phase=True)
        final_head = final.head
        observed = []
        if final.status:
            observed.append("working tree/index changed")
        if final.operations:
            observed.append("operation=" + ",".join(final.operations))
        if final.locks:
            observed.append("locks=" + ",".join(final.locks))
        if observed:
            evidence = "; ".join((evidence, *observed))
    except (VaultError, _DeadlineReached) as error:
        complete = False
        evidence = "; ".join(part for part in (evidence, str(error)) if part)
    return _RefreshResult(
        ScopeReport(
            worktree.scope.name,
            worktree.top,
            _configured(worktree.scope),
            initial.head if initial else "-",
            final_head,
            target,
            "interrupted",
            "deadline",
            "unknown",
            "unknown",
            "unknown",
            "not-inspected",
            evidence,
        ),
        deadline=True,
        complete=complete,
    )


def _refresh(worktree: _Worktree, budget: _Budget, empty_hooks: Path) -> _RefreshResult:
    scope = worktree.scope
    repo = Repo(worktree.top)
    initial: _Snapshot | None = None
    target = "-"
    try:
        initial = _snapshot(repo, budget)
        hooks = _active_hooks(repo, budget)
        if hooks:
            return _RefreshResult(
                ScopeReport(
                    scope.name,
                    worktree.top,
                    _configured(scope),
                    initial.head,
                    initial.head,
                    relation="hook-blocked",
                    refresh="preserved",
                    assets="preserved",
                    detail="active mutation hooks require inspection: " + ", ".join(hooks),
                )
            )

        captured, fetch_error = _fetch_target(repo, scope, budget, empty_hooks)
        if captured is None:
            final = _snapshot(repo, budget)
            return _RefreshResult(
                ScopeReport(
                    scope.name,
                    worktree.top,
                    _configured(scope),
                    initial.head,
                    final.head,
                    relation="stale",
                    refresh="stale",
                    assets="unknown",
                    detail=fetch_error,
                )
            )
        target = captured

        observed = _snapshot(repo, budget)
        ahead, behind = _relation(repo, observed.head, target, budget)
        initial_blockers = _incoming_blockers(repo, observed.head, target, budget) if behind else ()
        submodules = _changed_populated_submodules(repo, observed.head, target, budget) if behind else ()

        preserved = False
        detail = ""
        if observed.head != initial.head:
            relation, detail, preserved = "race", "HEAD changed during refresh", True
        elif observed.operations:
            relation, detail, preserved = (
                "operation-active",
                ", ".join(observed.operations),
                True,
            )
        elif observed.locks:
            relation, detail, preserved = "lock-active", ", ".join(observed.locks), True
        elif observed.status:
            relation, detail, preserved = "dirty", observed.status, True
        elif initial_blockers:
            relation, detail, preserved = (
                "local-path-blocked",
                "incoming tracked paths would overwrite local paths: " + ", ".join(initial_blockers),
                True,
            )
        elif submodules:
            relation, detail, preserved = (
                "submodule-blocked",
                "changed populated submodules require explicit refresh: " + ", ".join(submodules),
                True,
            )
        elif scope.pin is not None:
            relation = "pin-match" if observed.head == target else "pin-mismatch"
            preserved = relation == "pin-mismatch"
        elif observed.branch != scope.branch:
            relation = "other-branch"
            detail = f"checked out {observed.branch or 'detached'}, configured {scope.branch}"
            preserved = True
        elif ahead and behind:
            relation, preserved = "diverged", True
        elif ahead:
            relation, preserved = "ahead", True
        elif behind:
            relation = "behind"
        else:
            relation = "current"

        refresh = "preserved" if preserved else "current"
        interrupted = False
        if relation == "behind" and not preserved:
            recheck = _snapshot(repo, budget)
            blockers = _incoming_blockers(repo, recheck.head, target, budget)
            live_submodules = _changed_populated_submodules(repo, recheck.head, target, budget)
            if recheck != observed:
                relation, refresh, preserved = "race", "preserved", True
                detail = "checkout state changed before fast-forward"
            elif blockers:
                relation, refresh, preserved = "local-path-blocked", "preserved", True
                detail = "incoming tracked paths would overwrite local paths: " + ", ".join(blockers)
            elif live_submodules:
                relation, refresh, preserved = "submodule-blocked", "preserved", True
                detail = "changed populated submodules require explicit refresh: " + ", ".join(
                    live_submodules
                )
            else:
                try:
                    merged = _call(
                        repo,
                        "-c",
                        "submodule.recurse=false",
                        "-c",
                        f"core.hooksPath={empty_hooks}",
                        "merge",
                        "--ff-only",
                        target,
                        budget=budget,
                        check=False,
                    )
                except VaultError as error:
                    actual = _snapshot(repo, budget)
                    refresh, relation, preserved, interrupted = (
                        "interrupted",
                        "uncertain",
                        True,
                        True,
                    )
                    detail = f"{error}; observed HEAD {actual.head}"
                else:
                    actual = _snapshot(repo, budget)
                    if merged.returncode == 0 and actual.head == target and actual.clean:
                        refresh = "advanced"
                    else:
                        refresh, preserved, interrupted = "interrupted", True, True
                        relation = "uncertain"
                        detail = (
                            merged.stderr or merged.stdout
                        ).strip() or "fast-forward result is not clean"

        final = _snapshot(repo, budget)
        if interrupted:
            lfs = _LfsResult(
                "not-attempted",
                "unknown",
                "preserved",
                "LFS skipped after interrupted Git mutation",
                True,
            )
        else:
            lfs = _lfs(repo, scope, target, preserved, budget, empty_hooks)
        detail = "; ".join(part for part in (detail, lfs.detail) if part)
        attention = preserved or interrupted or lfs.attention
        return _RefreshResult(
            ScopeReport(
                scope.name,
                worktree.top,
                _configured(scope),
                initial.head,
                final.head,
                target,
                relation,
                refresh,
                lfs.remote,
                lfs.cache,
                lfs.assets,
                "blocked:" + ",".join(submodules) if submodules else "unchanged-or-empty",
                detail,
                attention,
            )
        )
    except _DeadlineReached as error:
        return _deadline_result(worktree, initial, target, budget, str(error))
    except VaultError as error:
        final_head = "unknown"
        with suppress(VaultError, _DeadlineReached):
            final_head = _snapshot(repo, budget).head
        return _RefreshResult(
            ScopeReport(
                scope.name,
                worktree.top,
                _configured(scope),
                initial.head if initial else "-",
                final_head,
                target,
                relation="uncertain",
                refresh="unavailable",
                assets="unknown",
                detail=str(error),
            )
        )


def run(
    vault: Path,
    config: Config,
    timeout: float = 20,
    deadline: int = 120,
) -> Report:
    """Refresh scopes within one deadline; repository findings do not abort later scopes."""
    budget = _Budget.start(timeout, deadline)
    try:
        worktrees, missing = _inventory(vault, config, budget)
    except _DeadlineReached:
        return Report(tuple(_unvisited(scope, vault) for scope in config.scopes))

    rows = list(missing)
    complete = True
    deadline_reached = False
    with tempfile.TemporaryDirectory(prefix="vault-startup-hooks-") as hook_dir:
        empty_hooks = Path(hook_dir)
        for index, worktree in enumerate(worktrees):
            if deadline_reached or budget.work_expired():
                rows.append(_unvisited(worktree.scope, vault))
                deadline_reached = True
                continue
            result = _refresh(worktree, budget, empty_hooks)
            rows.append(
                replace(
                    result.row,
                    git_dir=worktree.git_dir,
                    common_dir=worktree.common_dir,
                    action=_action(result.row),
                )
            )
            complete = complete and result.complete
            if result.deadline:
                deadline_reached = True
                for remaining in worktrees[index + 1 :]:
                    rows.append(_unvisited(remaining.scope, vault))
                break
    if budget.hard_expired():
        complete = False
    return Report(tuple(rows), complete)


def render(report: Report) -> str:
    """Render traversal completion separately from repository readiness."""
    if not report.complete:
        heading = "REPORT INCOMPLETE — DEADLINE"
    else:
        heading = "REPORT COMPLETED — ATTENTION" if report.attention else "REPORT COMPLETED"
    lines = [heading]
    for row in report.rows:
        lines.append(
            f"{row.name}: configured={row.configured} refresh={row.refresh} "
            f"relation={row.relation} initial={row.initial_head} head={row.final_head} "
            f"target={row.target} lfs-remote={row.lfs_remote} "
            f"lfs-cache={row.lfs_cache} assets={row.assets} "
            f"submodules={row.submodules} path={row.path} "
            f"git-dir={row.git_dir or '-'} common-dir={row.common_dir or '-'}"
        )
        if row.detail:
            lines.append(f"    detail  {row.detail}")
        lines.append(f"    action  {row.action}")
    lines.append(heading)
    return "\n".join(lines)
