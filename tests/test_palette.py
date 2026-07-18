"""roost-palette library tests: pure wrappers, the `should_colorize` truth table, and
the `detect()` shell helper via monkeypatched env + fake streams."""

from __future__ import annotations

import sys

import pytest

from roost_palette import COLOR, PLAIN, Palette, detect, should_colorize

_RESET = "\033[0m"
_ROLE_CODES = {
    "error": "\033[1;31m",
    "success": "\033[1;32m",
    "warn": "\033[33m",
    "info": "\033[36m",
    "heading": "\033[1m",
    "dim": "\033[2m",
}


class _Stream:
    """A minimal stand-in for a text stream: only what `detect` touches."""

    def __init__(self, tty: bool) -> None:
        self._tty = tty

    def isatty(self) -> bool:
        return self._tty


@pytest.fixture
def clean_env(monkeypatch):
    monkeypatch.delenv("NO_COLOR", raising=False)
    monkeypatch.delenv("FORCE_COLOR", raising=False)


@pytest.mark.parametrize(("role", "code"), sorted(_ROLE_CODES.items()))
def test_enabled_role_wraps_with_code_and_reset(role, code):
    assert getattr(COLOR, role)("text") == f"{code}text{_RESET}"


@pytest.mark.parametrize("role", sorted(_ROLE_CODES))
def test_disabled_role_returns_text_unchanged(role):
    assert getattr(PLAIN, role)("text") == "text"


def test_constants():
    assert PLAIN == Palette(enabled=False)
    assert COLOR == Palette(enabled=True)


@pytest.mark.parametrize(
    ("isatty", "no_color", "force_color", "expected"),
    [
        (False, False, False, False),
        (True, False, False, True),
        (False, False, True, True),
        (True, False, True, True),
        (False, True, False, False),
        (True, True, False, False),
        (False, True, True, False),  # NO_COLOR beats FORCE_COLOR
        (True, True, True, False),  # NO_COLOR beats FORCE_COLOR
    ],
)
def test_should_colorize_truth_table(isatty, no_color, force_color, expected):
    assert (
        should_colorize(isatty=isatty, no_color=no_color, force_color=force_color)
        is expected
    )


def test_detect_tty_is_color(clean_env):
    assert detect(_Stream(tty=True)) is COLOR


def test_detect_non_tty_is_plain(clean_env):
    assert detect(_Stream(tty=False)) is PLAIN


def test_detect_no_color_beats_tty(clean_env, monkeypatch):
    monkeypatch.setenv("NO_COLOR", "1")
    assert detect(_Stream(tty=True)) is PLAIN


def test_detect_force_color_beats_non_tty(clean_env, monkeypatch):
    monkeypatch.setenv("FORCE_COLOR", "1")
    assert detect(_Stream(tty=False)) is COLOR


def test_detect_stream_without_isatty_is_plain(clean_env):
    assert detect(object()) is PLAIN  # type: ignore[arg-type]


def test_detect_defaults_to_stdout(clean_env, monkeypatch):
    monkeypatch.setattr(sys, "stdout", _Stream(tty=True))
    assert detect() is COLOR
