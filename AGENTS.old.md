# facehugger

* This is a Python based huggingface repo/file "package" manager.
* Akin to the `uv` tool for python dependencies, but with `facehugger.yaml` instead of `pyproject.toml` and `facehugger.lock` instead of `uv.lock`.

## Package Management (python dependencies)
* This module is designed to be used with the `uv` package manager.
* DO NOT USE `pip`.
* For example use `uv list` to list packages rather than `pip list`.
* To add or remove dependencies use `uv add foo` and `uv remove foo` rather than editing `pyproject.toml` directly.


## Installation

To install this package using `uv`, run:

```bash
uv pip install .
```

This will install the package in development mode, allowing you to run the `facehugger` command directly from the local directory.


## Usage

Once installed, you can use the `facehugger` command to download models defined in a `facehugger.yaml` manifest file:

```bash
facehugger
```

This will download the models specified in the `facehugger.yaml` file in the current directory.

If you want to use a different manifest file, you can specify it as an argument:

```bash
facehugger path/to/your/manifest.yaml
```

For a dry run (to see what commands would be executed without actually downloading), use:

```bash
facehugger --dry-run
```

To see the version of the package, use:

```bash
facehugger --version
```

To see the help message, use:

```bash
facehugger --help
```


## Manifest File Format

The manifest file (default: `facehugger.yaml`) defines the models to be downloaded.
The format is YAML and supports the following fields:

- `repo`: The Hugging Face repository name (or `repo_id`) (required)
- `ref`: The revision (optional, defaults to `main`)
- `include`: A glob pattern or list of patterns to include (optional)
- `exclude`: A glob pattern or list of patterns to exclude (optional)

Example:

```yaml
models:
  - repo: owner/model-repo
    ref: main
    include: "*.gguf"
    exclude: "*.ckpt"
```

This mirrors the options of the `hf download` CLI (except `ref` instead of `revision`).


## Lock File Format

The purpose of the lock file is to enable exact reproduction of model revisions when the `--frozen` argument is given.

The lock file format is the compatible with the the JSON output of the `hf cache ls --revisions --format json` command.
Thus a lock file can be produced by `hf cache ls --revisions --format json > facehugger.lock`.

Only the `repo_id`, `revision`, and `refs` fields are used.
The `snapshot_path`, `size_on_disk`, `last_accessed`, and `last_modified` keys are ignored.
Any other extra keys are also ignored.

Example `facehugger.lock` file:

```json
[
  {
    "repo_id": "Qwen/Qwen-Image",
    "repo_type": "model",
    "revision": "75e0b4be04f60ec59a75f475837eced720f823b6",
    #"snapshot_path": "/var/home/bdawg/.cache/huggingface/hub/models--Qwen--Qwen-Image/snapshots/75e0b4be04f60ec59a75f475837eced720f823b6",
    #"size_on_disk": 57704594653,
    #"last_accessed": 1768666473.4315884,
    #"last_modified": 1768553738.260807,
    "refs": [
      "main"
    ]
  }
]
```


## Source Code Formatting
* `ruff format` is used for formatting.
* If you add or change code, try to conform to ruff style.
* You can run `ruff format --exit-non-zero-on-format` to check the formatting.


## Source Code Linting
* `ruff check` is used for linting.
* If you add or change code, try to pass all linting checks.
* You can run `ruff check` to perform linting.


## Source Code Type Checking
* Astral `ty` is used for type checking.
* If you add or chagne code, you shouldn't introduce type check errors.
* You can run `uv run ty check --error-on-warning` to perform type checking.


## Testing
* `pytest` (a dev dependency) is used for the testing framework.
* When adding tests, don't use `subprocess` to call `facehugger`, just use imports and test that way.
* If you make code changes, run the `pytest` to ensure the tests all pass.
  You could run `pytest` before you make changes to ensure they are in a good state to begin with.
* You should run `pytest --cov tests/` to check how much code coverage your tests have.
  You should aim for 100% coverage.


## Containerisation
* There's a `Dockerfile` with multiple stages.
* Some stages would be skipped by default, but can be explicitly targetted, such as `check` and `image-test`.
* These `check` and `image-test` stages are to containerise source code formatting, linting, and type checking checks, and test the produced image is functional.
* You can run these with `docker build -t berne/facehugger --target $TARGET .`, where `$TARGET` is `check` or `image-test` etc.


## Agent Instructions
* Do NOT do git write actions like `git commit`, `git reset`, `git add`, `git rm` etc., unless given explicit instructions to do so.
* Git read actions like `git log`, `git ls-files`, etc. are OK.
* Before you go running `cd <some-directory>`, you are probably already in it. There's no point `cd`'ing into the current directory you are already in.
  For example is you are in `/some/directory` (as seen by `pwd`), do NOT run `cd /some/directory && python -m pytest tests/ -v` - as you are already in that directory.
* DO NOT RUN `cd /var/home/bdawg/co/berney/facehugger && ...`. Run `pwd` and you will see the current working directory is `/var/home/bdawg/co/berney/facehugger`.
  Running `cd /var/home/bdawg/co/berney/facehugger` will do nothing useful as you are already in that directory.
  Running `cd /var/home/bdawg/co/berney/facehugger && ...` is the same as just running `...`, so just run `...` without the `cd blah && ...`.
* DO NOT RUN `python -m pytest ...` - just run `pytest ...`.
* DO NOT RUN `pytest tests/` just run `pytest` - it will already run the tests in the `test/` directory.
