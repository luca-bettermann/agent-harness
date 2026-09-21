"""A throwaway root: canonical clones with real remotes, and a vault clone with a board."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from vaulttools.board import Config, load_config

BOARD = """---

kanban-plugin: board

---

## backlog


## open


## in progress


## promotion


"""

VAULT_TOML = """board = "kanban.md"
tasks = ["tasks"]
repos = "repos"

[caps]
root = 15000
"tasks/" = 10000
"doctrine/" = 15000
"""


def git(cwd: Path, *args: str) -> str:
    result = subprocess.run(
        ("git", "-C", str(cwd), *args), check=True, capture_output=True, text=True
    )
    return result.stdout


def _init(path: Path, remote: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(("git", "init", "-q", "-b", "main", str(path)), check=True)
    subprocess.run(("git", "init", "-q", "--bare", str(remote)), check=True)
    settings = (("user.email", "bench@example.com"), ("user.name", "Bench"), ("commit.gpgsign", "false"))
    for key, value in settings:
        git(path, "config", key, value)
    git(path, "remote", "add", "origin", str(remote))


class Bench:
    """One disposable root holding `repos/` clones and a vault clone."""

    def __init__(self, tmp_path: Path) -> None:
        self.root = tmp_path / "root"
        self.vault = self.root / "vault"
        self.remotes = tmp_path / "remotes"
        _init(self.vault, self.remotes / "vault.git")
        self.write("vault.toml", VAULT_TOML)
        self.write("kanban.md", BOARD)
        self.write("doctrine/AGENTS.md", "the always-read file\n")
        self.commit("bench: initial vault")
        git(self.vault, "push", "-q", "-u", "origin", "main")

    @property
    def config(self) -> Config:
        return load_config(self.vault)

    def write(self, relative: str, text: str) -> Path:
        path = self.vault / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def commit(self, message: str) -> None:
        git(self.vault, "add", "-A")
        git(self.vault, "commit", "-q", "-m", message)

    def publish(self, message: str = "bench: state") -> None:
        self.commit(message)
        git(self.vault, "push", "-q", "origin", "main")

    def card(self, title: str, column: str, tags: str = "#example") -> None:
        board = (self.vault / "kanban.md").read_text(encoding="utf-8")
        marker = f"## {column}\n"
        head, _, tail = board.partition(marker)
        self.write("kanban.md", f"{head}{marker}\n- [ ] [[{title}]] {tags}\n{tail.lstrip(chr(10))}")

    def other_writer(self) -> Path:
        """A second clone of the vault remote, for a commit that lands while an action runs."""
        path = self.root.parent / "other"
        subprocess.run(("git", "clone", "-q", str(self.remotes / "vault.git"), str(path)), check=True)
        for key, value in (("user.email", "o@e.com"), ("user.name", "O"), ("commit.gpgsign", "false")):
            git(path, "config", key, value)
        git(path, "checkout", "-q", "-B", "main", "origin/main")
        return path

    def repo(self, name: str, stream: str, merged: bool = True, keep: bool = False) -> str:
        """A canonical clone whose `stream/<stream>` branch is merged (or merely deleted)."""
        clone = self.root / "repos" / name
        _init(clone, self.remotes / f"{name}.git")
        (clone / "README.md").write_text("base\n", encoding="utf-8")
        git(clone, "add", "-A")
        git(clone, "commit", "-q", "-m", "base")
        git(clone, "push", "-q", "-u", "origin", "main")
        git(clone, "checkout", "-q", "-b", f"stream/{stream}")
        (clone / "feature.md").write_text("work\n", encoding="utf-8")
        git(clone, "add", "-A")
        git(clone, "commit", "-q", "-m", "stream work")
        tip = git(clone, "rev-parse", "HEAD").strip()
        git(clone, "push", "-q", "-u", "origin", f"stream/{stream}")
        git(clone, "checkout", "-q", "main")
        if merged:
            git(clone, "merge", "-q", "--no-ff", "-m", "merge stream", f"stream/{stream}")
            git(clone, "push", "-q", "origin", "main")
        if not keep:
            git(clone, "push", "-q", "origin", "--delete", f"stream/{stream}")
            git(clone, "fetch", "-q", "--prune", "origin")
        return tip

    def stream(self, name: str, title: str, tip: str, repo: str, execute: bool = True) -> None:
        """A stream note in `promotion` with two front-matter members, both on its task list."""
        box = "x" if execute else " "
        self.write(
            f"tasks/{title}.md",
            f"---\ntype: stream\nstream: {name}\nrepos: [{repo}]\nblocked:\n---\n"
            f"Owner: example\n\nStream description: the {name} stream.\n\n"
            f"Merge evidence:\n- {repo}: {tip} -> origin/main\n\n"
            f"Tasks:\n- [ ] [[{title} one]]\n- [ ] [[{title} two]]\n\n"
            f"MR link:\n\nPromotion:\n- [ ] one concept candidate\n- [{box}] Execute\n",
        )
        for suffix in ("one", "two"):
            self.write(
                f"tasks/{title} {suffix}.md",
                f"---\ntype: task\nstream: {name}\nrepos: [{repo}]\nblocked:\n---\nwork package {suffix}\n",
            )
        self.card(title, "promotion")
        self.publish(f"bench: stream {name}")


@pytest.fixture
def bench(tmp_path: Path) -> Bench:
    return Bench(tmp_path)
