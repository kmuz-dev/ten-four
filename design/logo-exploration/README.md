# Handy Logo Exploration

This directory contains four isolated, production-ready identity systems.
Nothing here replaces the application's active icons or marks.

## Directions

- `keystone`: tactile top-down keycap with an integrated light well
- `press-plane`: offset planes expressing the press action
- `tally-cut`: monolithic key-like slab shaped by negative space
- `typeform`: speech contours condensing into typographic strokes

## Regenerate

```bash
python3 design/logo-exploration/generate_assets.py
```

The generator writes SVG sources, PNG masters, tray states, direction boards, manifests, and isolated Tauri platform bundles.
It requires Python with Pillow and the repository's installed Tauri CLI.

## Selection gate

Review `comparison-board.png`, the four direction boards, and `SCORING.md`.
Record an explicit user selection in `direction-approved.md` before integrating any direction into active application assets.
