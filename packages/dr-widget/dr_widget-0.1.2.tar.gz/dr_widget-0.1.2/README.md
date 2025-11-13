# dr_widget

dr_widget is a hybrid Python/Svelte project for building reusable AnyWidget components that can be dropped into Marimo notebooks today and exported to full Svelte apps later. The repository currently ships a Config File Manager widget, but the layout is designed to host additional widgets.

## Quick Start

```bash
# Install JS dependencies (root + workspace)
bun install

# Live-reload the Config File Manager widget in a browser
bun run dev:config-file-manager

# Produce the optimized bundle used by AnyWidget
bun run build

# Build the Python distributions (wheel + sdist)
uv build

# Launch the Marimo demo notebook
marimo run notebooks/config_file_manager_widget.py
```

Prerequisites: Bun ≥ 1.0, Node-compatible environment, Python ≥ 3.11 with `uv`, and Marimo ≥ 0.17.6.

## Repository Layout

- `src/dr_widget/` – Python package exposing AnyWidget classes.
  - `widgets/config_file_manager/` – widget workspace (Svelte source in `src/`, build output in `static/`).
    - `src/ConfigFileManager.svelte` – orchestration layer wiring bindings into the panel components.
    - `src/lib/hooks/use-file-bindings.ts` – shared logic for syncing AnyWidget traitlets.
    - `src/lib/components/` – shadcn-style UI primitives and panels, including a config viewer card with both a tree view and graph view for JSON payloads.
- `docs/` – additional reference material (architecture, development workflows).
- `notebooks/config_file_manager_widget.py` – Marimo notebook that exercises the Config File Manager widget.

## Documentation

- [Architecture Overview](docs/architecture.md) – how Python, AnyWidget, and Svelte fit together.
- [Development Workflow](docs/development.md) – commands for widget builds, packaging, and notebooks.
- [Repository Guidelines](AGENTS.md) – coding standards, contracts, and contribution checklist.

## Contributing

1. Work inside a dedicated branch.
2. Run `bun run build`, `npx svelte-check`, and `uv build` before opening a PR.
3. Update the notebook and docs when you add or change widget behaviour.
4. Follow the commit and PR practices outlined in `AGENTS.md`.

Please open an issue if you hit build problems or want to discuss new widgets.
