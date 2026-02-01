#!/usr/bin/env python3
"""Download models defined in a facehugger.yaml manifest file.

The manifest file format (YAML)::

    models:
      - repo: owner/model-repo
        ref: main                # optional, defaults to "main"
        include: "*.gguf"        # optional glob pattern (or list of patterns)
        exclude: "*.ckpt"        # optional glob pattern (or list of patterns)

Each entry mirrors the options of the ``hf download`` CLI.
Except ``ref`` instead of ``revision``.
The tool prints the equivalent ``hf download`` command for each model, performs
the download (unless ``--dry-run`` is given), and performs the equivalent of
`hf cache verify`.
The tool also runs ``hf cache ls`` at the start and end and highlights the delta.
"""

from pydantic import ValidationError

import argparse
import logging
import os
import subprocess
import sys
import difflib
from pathlib import Path
from importlib.metadata import version, PackageNotFoundError

import yaml
from huggingface_hub import snapshot_download
from huggingface_hub import HfApi
from huggingface_hub.utils import (
    RepositoryNotFoundError,
    RevisionNotFoundError,
    # HfHubHTTPError,
)

from facehugger.models import FacehuggerManifest

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def load_manifest(file_path: Path) -> FacehuggerManifest:
    """Load the manifest file.

    Returns a dictionary with at least a ``models`` key (list).  If the file does
    not exist or cannot be parsed, the function exits with an error message.
    """
    if not file_path.is_file():
        sys.exit(f"Manifest file not found: {file_path}")
    with file_path.open("r", encoding="utf-8") as f:
        try:
            data = yaml.safe_load(f) or {}
        except yaml.YAMLError as exc:
            sys.exit(f"Failed to parse manifest file {file_path}: {exc}")

    try:
        manifest = FacehuggerManifest.model_validate(data)
    except ValidationError as exc:
        sys.exit(f"Facehugger manifest {file_path} failed validation: {exc}")

    return manifest


def get_hf_env() -> dict[str, str]:
    """Get environment with venv's bin directory prepended to PATH.

    This ensures facehugger will use hf from its own venv if available,
    otherwise fall back to system hf.
    """
    venv_bin: Path = Path(sys.executable).parent
    env: dict[str, str] = os.environ.copy()
    current_path = env.get("PATH", "")
    if current_path:
        env["PATH"] = f"{venv_bin}:{env['PATH']}"
    else:
        env["PATH"] = str(venv_bin)
    return env


def build_hf_command(
    repo: str,
    ref: str | None = None,
    include: str | list[str] | None = None,
    exclude: str | list[str] | None = None,
) -> str:
    """Construct the equivalent ``hf download`` CLI command.

    ``include`` and ``exclude`` can be a single glob string or a list of strings.
    """
    parts = ["hf", "download", repo]
    if ref:
        parts[-1] = f"{repo}@{ref}"
    if include:
        if isinstance(include, list):
            for pat in include:
                parts.extend(["--include", pat])
        else:
            parts.extend(["--include", include])
    if exclude:
        if isinstance(exclude, list):
            for pat in exclude:
                parts.extend(["--exclude", pat])
        else:
            parts.extend(["--exclude", exclude])
    return " ".join(parts)


def download_model(
    repo: str,
    ref: str | None = None,
    include: str | list[str] | None = None,
    exclude: str | list[str] | None = None,
) -> None:
    """Download a model using ``huggingface_hub.snapshot_download``.

    ``include`` maps to ``allow_patterns`` and ``exclude`` to ``ignore_patterns``.
    The function relies on the default cache directory used by the hub.
    """
    logging.info(f"Downloading repo {repo}{f'@{ref}' if ref else ''}")
    snapshot_download(
        repo_id=repo,
        revision=ref,
        allow_patterns=include,
        ignore_patterns=exclude,
    )
    # Get a new line because huggingface_hub has probably hasn't terminated the line
    print()


def get_cache_listing() -> list[str]:
    """Return a list of lines from ``hf cache ls`` output."""
    try:
        result = subprocess.run(
            ["hf", "cache", "ls"],
            check=True,
            text=True,
            capture_output=True,
            env=get_hf_env(),
        )
        return result.stdout.splitlines()
    except subprocess.CalledProcessError as exc:
        logging.error("hf cache ls failed with exit code %s", exc.returncode)
        return []


def verify_cache(
    repo: str, repo_type: str | None = None, ref: str | None = None
) -> None:
    """Run ``hf cache verify``; include ``--revision`` if provided."""

    cmd = ["hf", "cache", "verify", repo]
    if ref:
        cmd.extend(["--revision", ref])
    cmd = " ".join(cmd)
    logging.info(
        f"Verifying repo {repo}{f'@{ref}' if ref else ''}, equivalent to: `{cmd}`"
    )

    # Create an API instance
    api = HfApi()

    try:
        # Verify repo checksums
        result = api.verify_repo_checksums(
            repo_id=repo,
            repo_type=repo_type,
            revision=ref,
        )
    except RepositoryNotFoundError as exc:
        logging.error(f"Repository {repo} not found: {exc}")
        return
    except RevisionNotFoundError as exc:
        logging.error(f"Repository {repo} revision {ref} not found: {exc}")
        return
    if bool(result.mismatches):
        logging.error(
            f"❌ Repo {repo} checksum verification failed for the following file(s)"
        )
        for m in result.mismatches:
            logging.error(
                f"  - {m['path']}: expected {m['expected']} ({m['algorithm']}), got {m['actual']}"
            )
        return
    else:
        logging.info(
            f"✅ Verified {result.checked_count} file(s) for '{repo}' ({repo_type}) in {result.verified_path}"
        )
        # logging.info("  All checksums match.")


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download models defined in a facehugger.yaml manifest file."
    )
    parser.add_argument(
        "manifest",
        nargs="?",
        default="facehugger.yaml",
        help="Path to the manifest file (default: facehugger.yaml)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the hf download commands without performing the download",
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Print the package version and exit",
    )
    args = parser.parse_args()
    if args.version:
        try:
            pkg_version = version("facehugger")
        except PackageNotFoundError:
            pkg_version = "0.0.0"
        print(pkg_version)
        return
    # version already handled above

    logging.basicConfig(level=logging.INFO, format="%(message)s")

    manifest_path = Path(args.manifest)
    data = load_manifest(manifest_path)
    models = data.models
    # placeholder for initial_cache default
    initial_cache = []  # default, will be set if models exist

    if not models:
        logging.info("No models defined in %s", manifest_path)
    else:
        # Capture initial cache state
        initial_cache = get_cache_listing()
        logging.info("\nInitial cache state:")
        for line in initial_cache:
            logging.info(line)

        for entry in models:
            repo = entry.repo
            if not repo:
                logging.warning("Skipping entry without 'repo' key: %s", entry)
                continue
            ref = entry.ref
            include = entry.include
            exclude = entry.exclude

            # Build and print the equivalent CLI command
            cmd_str = build_hf_command(
                repo=repo, ref=ref, include=include, exclude=exclude
            )
            logging.info(f"Equivalent command: `{cmd_str}`")

            if not args.dry_run:
                download_model(repo=repo, ref=ref, include=include, exclude=exclude)
                # Verify cache after each download, passing ref if present
                verify_cache(repo, ref=ref)

    # After all downloads (or dry‑run) show final cache state and diff
    final_cache = get_cache_listing()
    logging.info("\nFinal cache state:")
    for line in final_cache:
        logging.info(line)
    # Show diff
    diff = "".join(
        difflib.unified_diff(
            initial_cache, final_cache, fromfile="initial", tofile="final", lineterm=""
        )
    )
    if diff:
        logging.info("\nCache changes (colourised):")
        for line in diff.splitlines():
            if line.startswith("+") and not line.startswith("+++"):
                logging.info(f"\x1b[32m{line}\x1b[0m")  # green
            elif line.startswith("-") and not line.startswith("---"):
                logging.info(f"\x1b[31m{line}\x1b[0m")  # red
            else:
                logging.info(line)


if __name__ == "__main__":
    main()
