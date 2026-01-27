# facehugger

Manages Huggingface repo/files like a package manager.

This project provides a tool to download Huggingface models based on a YAML manifest file.


## Facehugger Manifest Files

The manifest file (`facehugger.yaml`) defines model repositories and optional include/exclude/ref settings.

Example manifest file:

```yaml
models:
  # Example just repo
  - repo: my-org/my-model
  # Example repo + include pattern
  - repo: my-org/my-model
    include: path/to/files/*
  # Example repo + include + exclude + ref
  - repo: my-org/my-model
    include: path/to/files/*
    exclude: path/to/ignore/*
    ref: v1.2.3
```

Each entry mirrors the options of the `hf download` CLI (`ref` -> `revision`).
The tool performs equivalents of `hf download` (unless `--dry-run` is given) and `hf cache verify` commands for each model.
It also performs the `hf cache ls` at the start and end to show the delta.

So far only `models` types are implemented.
Other repo types may be added in the future.


## Installation

```bash
uv tool install facehugger
```

## Usage
facehugger [manifest_file]
```

Options:
- `--dry-run`: Print the hf download commands without performing the download
- `--version`: Print the package version and exit
