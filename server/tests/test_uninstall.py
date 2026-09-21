"""
Tests for the uninstaller.

This code deletes things, so the tests are mostly about what it must *refuse*
to delete: a developer's checkout, anything outside the install root, and the
obvious catastrophic paths.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils import uninstall  # noqa: E402


def make_tree(root: Path, managed: bool) -> Path:
    """A minimal SPIDER_CTRL-shaped tree."""
    (root / "server" / "venv" / "bin").mkdir(parents=True)
    (root / "server" / "venv" / "bin" / "python").write_text("x" * 100)
    (root / "server" / "server.py").write_text("# fake — just needs to exist")
    (root / "server" / "config").mkdir(parents=True)
    (root / "server" / "config" / "pairing.json").write_text('{"token": "secret"}')
    (root / "server" / "certs").mkdir(parents=True)
    (root / "frontend" / "out").mkdir(parents=True)
    (root / "frontend" / "out" / "index.html").write_text("<html>")
    (root / "frontend" / "app").mkdir(parents=True)
    (root / "frontend" / "app" / "page.tsx").write_text("source!")
    (root / "README.md").write_text("source!")
    if managed:
        (root / uninstall.INSTALL_MARKER).write_text("installer")
    return root


@pytest.fixture
def dev_tree(tmp_path, monkeypatch):
    root = make_tree(tmp_path / "checkout", managed=False)
    monkeypatch.setattr(uninstall, "install_root", lambda: root)
    return root


@pytest.fixture
def installed_tree(tmp_path, monkeypatch):
    root = make_tree(tmp_path / "installed", managed=True)
    monkeypatch.setattr(uninstall, "install_root", lambda: root)
    return root


# ── mode detection ──────────────────────────────────────────────────────────
def test_unmarked_tree_is_treated_as_a_working_copy(dev_tree):
    p = uninstall.plan()
    assert p["mode"] == "artifacts" and p["managed"] is False
    assert str(dev_tree) not in [i["path"] for i in p["items"]]


def test_marked_tree_is_removable_whole(installed_tree):
    p = uninstall.plan()
    assert p["mode"] == "full" and p["managed"] is True
    assert [i["path"] for i in p["items"]] == [str(installed_tree)]


def test_plan_reports_sizes(dev_tree):
    p = uninstall.plan()
    assert p["total_bytes"] > 0
    assert all(i["bytes"] >= 0 for i in p["items"])


def test_plan_changes_nothing(dev_tree):
    uninstall.plan()
    assert (dev_tree / "server" / "venv").exists()
    assert (dev_tree / "frontend" / "app" / "page.tsx").exists()


# ── the source must survive ─────────────────────────────────────────────────
def test_artifacts_mode_keeps_the_source(dev_tree):
    res = uninstall.execute("DELETE")
    assert res["ok"], res
    # generated
    assert not (dev_tree / "server" / "venv").exists()
    assert not (dev_tree / "server" / "config").exists()
    assert not (dev_tree / "frontend" / "out").exists()
    # source — must still be here
    assert (dev_tree / "frontend" / "app" / "page.tsx").read_text() == "source!"
    assert (dev_tree / "README.md").exists()
    assert dev_tree.exists()


def test_full_mode_removes_everything(installed_tree):
    res = uninstall.execute("DELETE")
    assert res["ok"], res
    assert not installed_tree.exists()


def test_pairing_token_is_always_removed(dev_tree):
    token = dev_tree / "server" / "config" / "pairing.json"
    assert token.exists()
    uninstall.execute("DELETE")
    assert not token.exists()


# ── confirmation ────────────────────────────────────────────────────────────
@pytest.mark.parametrize("phrase", ["", "delete", "Delete", "DELET", "yes", "DELETE "])
def test_wrong_confirmation_deletes_nothing(dev_tree, phrase):
    res = uninstall.execute(phrase)
    assert res["ok"] is False
    assert (dev_tree / "server" / "venv").exists()


def test_exact_phrase_is_required_and_works(dev_tree):
    assert uninstall.execute(uninstall.CONFIRM_PHRASE)["ok"]


# ── refusing dangerous roots ────────────────────────────────────────────────
def test_refuses_the_home_directory(monkeypatch):
    monkeypatch.setattr(uninstall, "install_root", lambda: Path.home())
    p = uninstall.plan()
    assert p["blocked"] and p["items"] == []
    assert uninstall.execute("DELETE")["ok"] is False


def test_refuses_the_filesystem_root(monkeypatch):
    monkeypatch.setattr(uninstall, "install_root", lambda: Path("/"))
    assert uninstall.plan()["blocked"]
    assert uninstall.execute("DELETE")["ok"] is False


def test_refuses_a_tree_that_is_not_ours(tmp_path, monkeypatch):
    stranger = tmp_path / "someone-elses-project"
    (stranger / "src").mkdir(parents=True)
    monkeypatch.setattr(uninstall, "install_root", lambda: stranger)
    p = uninstall.plan()
    assert p["blocked"] and "does not look like" in p["blocked"]
    assert uninstall.execute("DELETE")["ok"] is False
    assert (stranger / "src").exists()


@pytest.mark.parametrize("path", ["/", "/tmp"])
def test_shallow_paths_are_refused(monkeypatch, path):
    monkeypatch.setattr(uninstall, "install_root", lambda: Path(path))
    assert uninstall.plan()["blocked"]


# ── containment ─────────────────────────────────────────────────────────────
def test_targets_outside_the_root_are_refused(dev_tree, tmp_path, monkeypatch):
    """
    Guard against a bad plan. execute() re-checks containment at delete time,
    so a target that escaped the root must be skipped rather than removed.
    """
    outsider = tmp_path / "precious"
    outsider.mkdir()
    (outsider / "data.txt").write_text("do not delete me")

    real_plan = uninstall.plan()
    real_plan["items"].append({
        "path": str(outsider), "label": "escaped", "bytes": 10, "exists": True,
    })
    monkeypatch.setattr(uninstall, "plan", lambda root=None: real_plan)

    res = uninstall.execute("DELETE")
    assert (outsider / "data.txt").read_text() == "do not delete me"
    assert any("outside the install root" in f["error"] for f in res["failed"])


def test_second_run_is_harmless(installed_tree):
    """Running it twice must refuse cleanly, not crash or wander upward."""
    assert uninstall.execute("DELETE")["ok"]
    assert not installed_tree.exists()

    again = uninstall.execute("DELETE")
    assert again["ok"] is False
    assert "Already removed" in again["error"]
    # The parent must be untouched — nothing walked up a level.
    assert installed_tree.parent.exists()


# ── multi-install discovery (find_installs) ─────────────────────────────────
def test_find_installs_includes_self(dev_tree):
    installs = uninstall.find_installs()
    selves = [i for i in installs if i["is_self"]]
    assert len(selves) == 1
    assert selves[0]["root"] == str(dev_tree.resolve())


def test_find_installs_via_extra_roots(dev_tree, tmp_path):
    other = make_tree(tmp_path / "elsewhere", managed=False)
    installs = uninstall.find_installs(extra_roots=[str(other)])
    matches = [i for i in installs if i["root"] == str(other.resolve())]
    assert len(matches) == 1
    assert matches[0]["is_self"] is False


def test_find_installs_ignores_non_install_directories(dev_tree, tmp_path):
    not_an_install = tmp_path / "random-folder"
    (not_an_install / "notes").mkdir(parents=True)
    installs = uninstall.find_installs(extra_roots=[str(not_an_install)])
    assert not any(i["root"] == str(not_an_install.resolve()) for i in installs)


def test_find_installs_dedupes_the_same_path(dev_tree):
    installs = uninstall.find_installs(extra_roots=[str(uninstall.install_root())] * 5)
    selves = [i for i in installs if i["is_self"]]
    assert len(selves) == 1


def test_self_is_sorted_first(dev_tree, tmp_path):
    """
    A foreign install with a bigger footprint must not push self down the
    list — the running server's own tree is what the Danger Zone button acts
    on by default, so it should always be first.
    """
    big = make_tree(tmp_path / "bigger", managed=False)
    (big / "server" / "venv" / "huge.bin").write_bytes(b"x" * 10_000_000)
    installs = uninstall.find_installs(extra_roots=[str(big)])
    assert installs[0]["is_self"] is True


# ── executing against a root that is not the running process ───────────────
def test_execute_on_a_foreign_root_never_shuts_down(dev_tree, tmp_path):
    other = make_tree(tmp_path / "foreign", managed=True)
    res = uninstall.execute("DELETE", other)
    assert res["ok"]
    assert res["self"] is False
    assert res["shutdown"] is False
    assert not other.exists()


def test_execute_on_self_reports_self_and_shutdown(dev_tree):
    res = uninstall.execute("DELETE", uninstall.install_root())
    assert res["self"] is True
    assert res["shutdown"] is True


def test_execute_default_root_matches_explicit_self(dev_tree):
    """No root passed must behave exactly like passing install_root()."""
    res = uninstall.execute("DELETE")
    assert res["self"] is True


def test_a_second_unrelated_install_survives_removing_the_first(dev_tree, tmp_path):
    first = make_tree(tmp_path / "first", managed=True)
    second = make_tree(tmp_path / "second", managed=True)
    uninstall.execute("DELETE", first)
    assert not first.exists()
    assert second.exists()


# ── the stricter "looks like SPIDER_CTRL" check ─────────────────────────────
def test_a_bare_server_directory_with_no_server_py_is_rejected(tmp_path, monkeypatch):
    """
    find_installs() requires server/server.py, and plan()/execute() have to
    agree — otherwise /uninstall/remove (which trusts plan()'s own sanity
    check rather than re-deriving find_installs()'s allowlist) could be
    pointed at a directory that merely has a server/ folder for some other
    reason.
    """
    root = tmp_path / "looks-close-but-isnt"
    (root / "server").mkdir(parents=True)
    (root / "server" / "not_server.py").write_text("x")
    monkeypatch.setattr(uninstall, "install_root", lambda: root)
    p = uninstall.plan()
    assert p["blocked"] and "does not look like" in p["blocked"]


# ── psutil running-detection degrades safely ────────────────────────────────
def test_running_detection_survives_psutil_being_unavailable(dev_tree, monkeypatch):
    monkeypatch.setattr(uninstall, "psutil", None)
    assert uninstall._root_is_running(dev_tree) is False
    # Must not block plan()/execute() either.
    assert uninstall.plan()["blocked"] is None


def test_running_detection_does_not_raise_on_a_hostile_process_list(dev_tree, monkeypatch):
    class ExplodingIter:
        def __iter__(self):
            raise RuntimeError("simulated psutil failure")

    class FakePsutil:
        NoSuchProcess = Exception
        AccessDenied = Exception
        CONN_LISTEN = "LISTEN"

        @staticmethod
        def process_iter(attrs):
            return ExplodingIter()

        @staticmethod
        def net_connections(kind):
            raise RuntimeError("also simulated")

    monkeypatch.setattr(uninstall, "psutil", FakePsutil)
    assert uninstall._root_is_running(dev_tree) is False
