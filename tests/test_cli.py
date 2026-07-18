"""roost-palette CLI tests (spec §13): call `main(argv)` directly, assert exit codes and
capsys output. Under src-layout this exercises the installed package."""

from __future__ import annotations

import pytest

from roost_palette import cli

_ROLES = ("error", "success", "warn", "info", "heading", "dim")


@pytest.fixture
def clean_env(monkeypatch):
    monkeypatch.delenv("NO_COLOR", raising=False)
    monkeypatch.delenv("FORCE_COLOR", raising=False)


def test_help_exits_zero():
    with pytest.raises(SystemExit) as exc:
        cli.main(["-h"])
    assert exc.value.code == 0


def test_no_command_prints_usage(capsys):
    assert cli.main([]) == 2
    assert "usage" in capsys.readouterr().err.lower()


def test_unknown_command_exits_nonzero():
    with pytest.raises(SystemExit) as exc:
        cli.main(["nonesuch"])
    assert exc.value.code != 0


def test_swatch_prints_all_roles(clean_env, capsys):
    assert cli.main(["swatch"]) == 0
    out = capsys.readouterr().out
    for role in _ROLES:
        assert role in out


def test_swatch_no_color_output_is_plain(clean_env, monkeypatch, capsys):
    monkeypatch.setenv("NO_COLOR", "1")
    assert cli.main(["swatch"]) == 0
    assert "\033" not in capsys.readouterr().out


def test_swatch_force_color_output_has_sgr_codes(clean_env, monkeypatch, capsys):
    monkeypatch.setenv("FORCE_COLOR", "1")
    assert cli.main(["swatch"]) == 0
    assert "\033[" in capsys.readouterr().out
