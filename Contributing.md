# Contributing to Beautiful Captions

First off, thank you for considering contributing to Beautiful Captions! This document is the source of truth for how the project is laid out, how to set up your environment, and what every PR needs to satisfy before review.

It is written to be followed by **both human contributors and AI coding agents**. If you are an agent: read this file end-to-end before editing, and treat the [Pre-PR Checklist](#pre-pr-checklist) as a hard gate, not a suggestion.

---

## Table of Contents

1. [Code Organization](#code-organization)
2. [Development Environment](#development-environment)
3. [Dependency Management](#dependency-management)
4. [Code Style and Linting](#code-style-and-linting)
5. [Type Annotations and Type Checking](#type-annotations-and-type-checking)
6. [Tests](#tests)
7. [Adding a New Transcription Service](#adding-a-new-transcription-service)
8. [Adding a New Style or Animation](#adding-a-new-style-or-animation)
9. [Pre-PR Checklist](#pre-pr-checklist)
10. [Pull Request Process](#pull-request-process)
11. [Commit and PR Style](#commit-and-pr-style)
12. [Community](#community)

---

## Code Organization

The project uses a **`src/` layout**. The importable package lives at `src/beautiful_captions/`, and tests live at the repo root in `tests/` (NOT inside `src/`).

```
beautiful-captions/
├── src/
│   └── beautiful_captions/
│       ├── __init__.py             # Public API re-exports
│       ├── core/
│       │   ├── caption.py          # High-level captioning entry points
│       │   ├── config.py           # CaptionConfig, StyleConfig, AnimationConfig, DiarizationConfig
│       │   ├── types.py            # Shared types / enums (e.g. ServiceType)
│       │   └── video.py            # Video class
│       ├── styling/
│       │   ├── style.py            # StyleManager, FontManager
│       │   └── animation.py        # AnimationFactory, animation implementations
│       ├── transcription/
│       │   ├── base.py             # TranscriptionService ABC, Word, Utterance
│       │   ├── assemblyai.py
│       │   ├── deepgram.py
│       │   └── openai.py
│       ├── utils/
│       │   ├── ffmpeg.py
│       │   └── subtitles.py        # style_srt_content, pysrt usage
│       └── fonts/                  # Bundled .ttf font assets
├── tests/                          # All tests (unit + integration)
├── pyproject.toml                  # Single source of truth for deps + tooling
├── README.md
└── Contributing.md
```

Rules:

- **Do not** create `src/tests/`. Tests get shipped with the package if you do.
- **Do not** import from `src.beautiful_captions...` anywhere — that path only exists during development. Inside the package use **relative imports** (`from .types import ServiceType`, `from ..utils.subtitles import ...`). In tests and example scripts use **absolute imports** (`from beautiful_captions import Video`).
- If you add a new top-level subpackage, also re-export anything intended to be public from `src/beautiful_captions/__init__.py` and add it to `__all__`.

---

## Development Environment

The project uses plain `pip` plus a virtual environment. The end state must be an editable install of the package and a working `pytest` run.

```bash
git clone https://github.com/AayushGupta16/Beautiful-Captions.git
cd Beautiful-Captions

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -e .
pip install -r requirements.txt    # runtime deps with pinned versions
pip install pytest pytest-xdist    # test deps; add others as the project gains them

pytest
```

External system requirement: **`ffmpeg` must be on your PATH** for any code path that renders video. Integration tests will be skipped if it is missing (see [Tests](#tests)).

After install, run a smoke import to verify the package actually works:

```bash
python -c "import beautiful_captions; print(beautiful_captions.__version__)"
```

This single line catches the most common dependency mistake (see [Dependency Management](#dependency-management)).

---

## Dependency Management

`pyproject.toml` is the single source of truth for dependencies. Read this section carefully before adding, removing, or moving a package — it is the #1 source of broken PRs in this repo.

### Where things go

| Kind of dep | Where it goes | Example |
|---|---|---|
| Imported at runtime by `src/beautiful_captions/**` | `[project.dependencies]` | `pysrt`, `aiohttp`, `ffmpeg-python`, `assemblyai`, `deepgram-sdk`, `openai` |
| Used only in `tests/`, `benchmark.py`, dev tooling | `[project.optional-dependencies].dev` (once a `dev` extra is added — currently installed ad hoc via `pip install`) | `pytest`, `pytest-xdist`, `ruff`, the type checker |
| Only used by CI / publishing | CI workflow file, **not** project metadata | `build`, `twine` |

### Rules

1. **If you `import foo` from any file under `src/beautiful_captions/`, then `foo` MUST appear in `[project.dependencies]`.** No exceptions. A type-checker allowlist (e.g. `[tool.ty.analysis] allowed-unresolved-imports`, `[tool.mypy] ignore_missing_imports`, etc.) is not a substitute for declaring the dependency — it only suppresses the type-check warning, the import will still fail at runtime for end users. *(This is the `pysrt` regression from PR #7.)*
2. **Do not duplicate entries** in `[project.dependencies]`. Run a quick dedupe scan after editing.
3. **Pin a lower bound** (`>=X.Y`) for everything in `[project.dependencies]`. Do not pin exact versions in `pyproject.toml` — that is the lockfile's job.
4. **Lockfile**: this repo currently does not commit a lockfile. If one is ever introduced (e.g. `uv.lock`, `pip-compile`'d `requirements.txt`), it must be committed alongside any `pyproject.toml` change that affects deps.
5. **Verify before pushing**: in a clean venv, run

   ```bash
   pip install -e . && python -c "import beautiful_captions"
   ```

   If that fails, your dependency list is wrong.

### Removing a runtime dep

Removing a package from `[project.dependencies]` is only safe if you have also removed every `import` of it from `src/beautiful_captions/`. Search before you remove:

```bash
rg "^import pysrt|^from pysrt" src/
```

---

## Code Style and Linting

- **Formatter / Linter**: [ruff](https://docs.astral.sh/ruff/) is the project's chosen tool for both lint and format. If `[tool.ruff]` is configured in `pyproject.toml`, run it before pushing:

  ```bash
  ruff check .
  ruff format .
  ```

- **Do not introduce a second formatter or linter** (black, isort, flake8, etc.). Ruff covers all of those.
- **Do not add unused tooling config.** If you add `[tool.<something>]`, that tool must actually be used in CI or in the documented contributor workflow. Dead config blocks (e.g. an unused `[tool.basedpyright]` block sitting next to an active type checker) are not allowed.
- **`ruff.target-version`** must match the lowest Python version supported by `[project] requires-python`. They drift in opposite directions easily — keep them in sync.
- Use meaningful variable names. Prefer clarity over cleverness.
- Add docstrings to public functions, classes, and modules.
- Comment **why**, not **what**. Don't narrate the code.

---

## Type Annotations and Type Checking

The project uses type hints. Follow these rules so the type checker stays useful and signatures stay tight.

### Annotation rules

1. **Never widen an existing return type without a real reason.** If a function returns `str` on every code path, its annotation must stay `-> str`. Changing it to `-> str | None` (or `-> Optional[str]`) forces every caller to handle a case that cannot occur. *(This was the `AnimationFactory.create` regression from PR #7.)*
2. Annotate all new public functions and methods. Internal helpers are encouraged but not required.
3. Prefer modern union syntax (`str | None`) on Python ≥3.10 code paths; use `Optional[str]` / `Union[...]` only if you must keep working on `<3.10`.

### `# type: ignore` discipline

- **Never** use a bare `# type: ignore`. It silences every error on the line and hides regressions.
- Always pin to the specific error code:

  ```python
  result = legacy_api(x)  # type: ignore[arg-type]
  ```

- Add a one-line comment explaining why the ignore is needed if it isn't obvious.

### Type-checker config

- **Pick exactly one type checker.** Do not add a second tool's config block "just in case". If the project uses `ty`, there is no `[tool.basedpyright]` / `[tool.mypy]` / `[tool.pyright]` block, and vice versa.
- **`python-version`** for the type checker must match `[project] requires-python`. If `requires-python = ">=3.8"`, the type checker must run against 3.8, otherwise you ship code that breaks on the lowest supported runtime. *(This was the `python-version = "3.12"` mismatch in PR #7.)*

---

## Tests

All tests live in a top-level `tests/` directory (NOT in `src/tests/`).

### File and function naming

These are pytest's default discovery rules. Violating them means your tests silently do not run.

- File names: **`test_*.py`** (lowercase, **underscores**, no hyphens). Examples:
  - `test_caption_config.py`
  - `test_style_config.py`
  - `test_subtitle_styling.py`
  - **NOT** `test-style-config.py`, **NOT** `test_style_config_creaton.py` (proofread for typos).
- Function names: `def test_<thing>():`
- Class names (if used): `class TestThing:` with methods named `test_*`.

### Imports inside `tests/`

Tests import the package by its installed name and use **absolute imports** for shared test helpers:

```python
# Correct
from beautiful_captions import CaptionConfig, Video
from tests.base_config import default_config_kwargs

# Incorrect — do not mix styles across the test tree
from .base_config import default_config_kwargs
```

Pick one style (absolute) and use it everywhere under `tests/`. *(PR #7 mixed both, which broke discovery from some entry points.)*

### Unit vs integration tests

Anything that needs `ffmpeg`, a real network call, an API key, or `input.mp4` is an **integration test**. Mark it and gate it on its prerequisites:

```python
import shutil
import pytest

pytestmark = pytest.mark.integration

@pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg not installed")
def test_renders_video(tmp_path):
    ...
```

Register the marker in `pyproject.toml` so pytest doesn't warn:

```toml
[tool.pytest.ini_options]
markers = [
    "integration: tests that require external tools (ffmpeg, network, API keys, fixture videos)",
]
```

### Running tests

```bash
# All non-integration tests (default for contributors and CI on PRs)
pytest -m "not integration"

# Everything, including integration tests (requires ffmpeg + input.mp4)
pytest

# A single file or test
pytest tests/test_style_config.py
pytest tests/test_style_config.py::test_default_font_size

# With coverage
pytest --cov=beautiful_captions tests/

# In parallel — use `-n auto`, not a hardcoded number.
# Requires the `pytest-xdist` plugin.
pytest -n auto
```

### When you add a feature

Every PR that adds or changes behavior must include tests covering at least:

1. The happy path.
2. One edge case (empty input, missing optional field, boundary value, etc.).
3. The failure mode, if the function raises.

---

## Adding a New Transcription Service

1. Create a new file in `src/beautiful_captions/transcription/`, e.g. `myservice.py`.
2. Subclass `TranscriptionService` from `.base` and implement both abstract methods. The real signatures (current as of `main`) are:

    ```python
    from typing import Dict, List, Optional
    from .base import TranscriptionService, Utterance

    class MyService(TranscriptionService):
        def __init__(self, api_key: str):
            super().__init__(api_key)

        async def transcribe(
            self,
            audio_path: str,
            max_speakers: int = 3,
            censor_subtitles: bool = False,
            custom_censored_words: Optional[Dict[str, str]] = None,
        ) -> List[Utterance]:
            ...

        def to_srt(
            self,
            utterances: List[Utterance],
            speaker_colors: List[str],
            max_words_per_line: int = 1,
            include_speaker_labels: bool = True,
        ) -> str:
            ...
    ```

3. If the service is selectable via config, add an entry to the relevant enum in `src/beautiful_captions/core/types.py` and wire it into the factory/dispatcher.
4. Add tests in `tests/transcription/test_myservice.py`. Mock the network — do not hit the real API in unit tests. A real-API test, if you write one, must be marked `@pytest.mark.integration` and skipped when the API key env var is unset.
5. Add the SDK to `[project.dependencies]` in `pyproject.toml` (see [Dependency Management](#dependency-management)).

---

## Adding a New Style or Animation

- **New style preset**: add it in `src/beautiful_captions/styling/style.py` (or wherever presets are registered for the current code), expose it from `__init__.py` if it's part of the public API, and add a test in `tests/test_style_config.py` that constructs it and checks the resulting fields.
- **New animation**: add it in `src/beautiful_captions/styling/animation.py` and register it with `AnimationFactory`. Keep `AnimationFactory.create`'s return type as `str` — every code path must return a string (use `""` for "no animation"), so do not change the annotation to `str | None`.
- Document any new public config field in the README.

---

## Pre-PR Checklist

Run all of these locally and make sure they pass before you open a PR. Each one corresponds to a real failure mode that has hit this repo.

- [ ] **Fresh install works.** In a clean venv: `pip install -e . && python -c "import beautiful_captions"` succeeds. *(Catches missing runtime deps.)*
- [ ] **Every `import` under `src/beautiful_captions/` has a matching entry in `[project.dependencies]`.** Type-checker allowlists do not count.
- [ ] **No duplicate entries** in `[project.dependencies]`.
- [ ] **`pyproject.toml` is internally consistent.** `requires-python`, `ruff.target-version`, and the type checker's `python-version` all agree on the lowest supported version.
- [ ] **No dead tooling config.** Every `[tool.*]` block in `pyproject.toml` is for a tool you actually run.
- [ ] **All test files match `test_*.py`** with underscores, no hyphens, no typos.
- [ ] **Test imports are consistent** (absolute, using the installed package name).
- [ ] **Integration tests are marked** `@pytest.mark.integration` and skip cleanly when their prerequisites (ffmpeg, fixture videos, API keys) are missing.
- [ ] **`pytest -m "not integration"` is green.**
- [ ] **`ruff check .` and `ruff format --check .` are clean** (if ruff is configured).
- [ ] **The type checker is clean** (if one is configured), and any `# type: ignore` is targeted, e.g. `# type: ignore[arg-type]`.
- [ ] **Public API changes are reflected in `src/beautiful_captions/__init__.py` `__all__`** and in the README if they are user-facing.
- [ ] **No return-type widening** without a code path that actually returns the new type.
- [ ] **CHANGELOG / README updated** if the change is user-visible.

---

## Pull Request Process

1. Fork the repo and create a feature branch off `main`.
2. Make focused commits — one logical change per commit where reasonable.
3. Run the [Pre-PR Checklist](#pre-pr-checklist) end-to-end.
4. Open the PR with a description that includes:
   - **What** changed and **why** (link the issue if there is one).
   - **How** to verify it (commands, fixtures, env vars needed).
   - Any **breaking changes** called out explicitly.
   - For tooling/infra PRs (e.g. switching package manager, adding a linter), an explicit note that you ran the [Pre-PR Checklist](#pre-pr-checklist).
5. Address review comments by pushing additional commits; do not force-push during review unless asked.

PRs that touch dependencies, tooling, or the test layout will be reviewed against this document line-by-line. If your PR diverges from a rule here, either fix it or argue for changing the rule in the PR description.

---

## Commit and PR Style

### Commit messages

- Imperative mood, present tense: *"Add deepgram retry"*, not *"Added deepgram retry"* / *"Adds deepgram retry"*.
- First line ≤72 chars, capitalized, no trailing period.
- Blank line, then a body explaining *why* if the change isn't obvious.
- Reference issues/PRs in the body: `Fixes #42`.

### PR titles

Use a `<type>: <summary>` prefix where helpful:

- `feat: add Whisper transcription service`
- `fix: restore pysrt to runtime dependencies`
- `chore: migrate packaging to uv`
- `test: cover diarization edge cases`
- `docs: clarify integration-test markers`

---

## Community

- Open issues and discussions on [GitHub](https://github.com/AayushGupta16/Beautiful-Captions).
- Be respectful and constructive in reviews. Critique the code, not the contributor.
