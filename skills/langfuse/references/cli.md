---
name: langfuse-cli
description: Langfuse CLI usage reference — install, resource/action discovery, credentials, and common usage tips for the Langfuse CLI. Use for further tips on using the Langfuse CLI.
---

# Langfuse CLI Reference

Documentation: https://langfuse.com/docs/api-and-data-platform/features/cli

## Install

```bash
# Run directly without installing
npx @langfuse/cli api <resource> <action>
bunx @langfuse/cli api <resource> <action>

# Or install globally
npm install --global @langfuse/cli
langfuse api <resource> <action>
```

For the Hermes project, run `langfuse-hermes` instead of `langfuse`. It loads a separate Viewer key from a local file and passes the arguments through to the CLI. On each machine:

1. Install `@langfuse/cli` globally and run `make link` in `my-skills` to link the wrapper into `~/.local/bin`.
2. Store the Hermes Viewer key pair in 1Password.
3. Create `~/.config/langfuse/hermes.env` with mode `0600` and these lines, replacing the placeholders locally:

   ```sh
   LANGFUSE_PUBLIC_KEY=your-viewer-public-key
   LANGFUSE_SECRET_KEY=your-viewer-secret-key
   LANGFUSE_BASE_URL=https://us.cloud.langfuse.com
   ```

4. Run `langfuse-hermes api __schema` to verify CLI startup, then make a bounded read query to verify authentication.

Do not put the key in Fish's `config.fish` or a universal variable. The wrapper reads this file for each invocation, so Fish does not need to export anything. Do not print the file or put its values in a command line or issue/PR text. The CLI has no separate login step. The key pair scopes access to the Hermes Langfuse project; the Viewer permission allows reads and blocks writes.

## Discovery

```bash
# List all resources and auth info
langfuse-hermes api __schema

# List actions for a resource
langfuse-hermes api <resource> --help

# Show args/options for a specific action
langfuse-hermes api <resource> <action> --help
```

Do not use `--curl` with credentials: the preview prints the Authorization header. The Hermes wrapper rejects this flag.

## Credentials

Outside the Hermes wrapper, the CLI reads these environment variables. In Fish, set them for the current session with `set -gx`:

```fish
set -gx LANGFUSE_PUBLIC_KEY 'your-project-public-key'
set -gx LANGFUSE_SECRET_KEY 'your-project-secret-key'
set -gx LANGFUSE_BASE_URL 'https://us.cloud.langfuse.com'
```

## Tips

- Use `--json` for machine-readable JSON output
- All list commands support filtering — check `<resource> <action> --help` for available options
- Prefer `observations` over `legacy-observations-v1s` — `observations` is the modern high-performance endpoint (cursor pagination, selective field groups); `legacy-observations-v1s` is the deprecated v1
- Prefer `metrics` over `legacy-metrics-v1s` for the same reason
- Prefer `scores` over `legacy-score-v1s` for list/get operations
- Always query via `observations`, not `traces`, even when the user phrases the request in terms of traces — the `traces` endpoints are outdated (add `--trace-id` to scope to a known trace). See the [Observations API docs](https://langfuse.com/docs/api-and-data-platform/features/observations-api) for the v1 → v2 mapping.
- Pagination: legacy v1 endpoints use `--limit` and `--page`; modern endpoints (`observations`, `metrics`, `scores`) use cursor-based pagination — pass `--limit`, then thread `meta.cursor` from the response into the next request's `--cursor`
