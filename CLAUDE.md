# roost-palette

Marisa's shared terminal-color library. One screen of pure code in `src/roost_palette/__init__.py`: a frozen `Palette` of six intent-named role wrappers (`error`, `success`, `warn`, `info`, `heading`, `dim`), `PLAIN`/`COLOR` constants, pure `should_colorize`, and `detect()` — the one impure helper, called once at a consumer's composition root to observe TTY/`NO_COLOR`/`FORCE_COLOR` and hand back the right palette. Consumers add it with `uva roost-palette` and call `palette.error(text)`; the `roost-palette swatch` subcommand renders each role for eyeballing.

A packaged uv project on the roost Python spec (`~/Documents/roost/roost-python/docs/python-packaging-spec.md`).

@MEMORY.md
