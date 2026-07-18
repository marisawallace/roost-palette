"""ANSI color palette for the roost fleet: wrap text in SGR codes, or don't.

Coloring is presentation, and whether to apply it is an environment fact — is the
stream a TTY? is `NO_COLOR` set? — that belongs to the imperative shell. This module
keeps the two cleanly apart: `should_colorize` is the pure decision given the facts
the shell observed, and a `Palette` is just a bundle of pure text-wrapping functions
that either emit SGR codes (enabled) or return the text untouched (disabled). The
consuming program observes the TTY/env once at its composition root — `detect()` is
the one impure helper that does exactly that — builds the right palette, and passes
it down; call sites never branch on color — they just call `palette.error(text)`.

Roles are named by intent (`error`, `success`, `warn`, …), not by hue, so the call
sites read as meaning and the actual colors can change in one place, fleet-wide —
this is the shared module every roost tool consumes (as `uva roost-palette`).
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from typing import IO

_RESET = "\033[0m"
_CODES = {
    "error": "\033[1;31m",  # bold red
    "success": "\033[1;32m",  # bold green
    "warn": "\033[33m",  # yellow
    "info": "\033[36m",  # cyan
    "heading": "\033[1m",  # bold
    "dim": "\033[2m",  # dim
}


@dataclass(frozen=True, slots=True)
class Palette:
    """A bundle of role→wrapper functions. `enabled=False` makes every role a no-op,
    so the same call site works colored or plain with no branching."""

    enabled: bool

    def _wrap(self, role: str, text: str) -> str:
        return f"{_CODES[role]}{text}{_RESET}" if self.enabled else text

    def error(self, text: str) -> str:
        return self._wrap("error", text)

    def success(self, text: str) -> str:
        return self._wrap("success", text)

    def warn(self, text: str) -> str:
        return self._wrap("warn", text)

    def info(self, text: str) -> str:
        return self._wrap("info", text)

    def heading(self, text: str) -> str:
        return self._wrap("heading", text)

    def dim(self, text: str) -> str:
        return self._wrap("dim", text)


PLAIN = Palette(enabled=False)  # the safe default: every wrapper is identity
COLOR = Palette(enabled=True)


def should_colorize(*, isatty: bool, no_color: bool, force_color: bool) -> bool:
    """Decide coloring from the facts the shell observed. `NO_COLOR` (the cross-tool
    opt-out convention) wins outright; `FORCE_COLOR` overrides a non-TTY (CI logs the
    user wants colored); otherwise we color only a real terminal."""
    if no_color:
        return False
    if force_color:
        return True
    return isatty


def detect(stream: IO[str] | None = None) -> Palette:
    """The imperative-shell helper: observe `NO_COLOR`/`FORCE_COLOR` in the environment
    (presence, any value) and whether `stream` (default `sys.stdout`) is a TTY, then
    return `COLOR` or `PLAIN` via `should_colorize`. Call it once at the entrypoint and
    pass the palette down; everything else in this module is pure."""
    if stream is None:
        stream = sys.stdout
    try:
        isatty = bool(stream.isatty())
    except Exception:
        isatty = False
    return (
        COLOR
        if should_colorize(
            isatty=isatty,
            no_color="NO_COLOR" in os.environ,
            force_color="FORCE_COLOR" in os.environ,
        )
        else PLAIN
    )
