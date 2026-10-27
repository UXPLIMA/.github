# UXPLIMA organization defaults

This repository holds what every UXPLIMA repository shares: the standards in `docs/`, the reusable CI workflow, the text and title checks, the canonical copies of synced files, and the organization profile. It is public, so its own CI runs on GitHub-hosted runners for free.

## Commands

```sh
python -m unittest discover -s tools -p "test_*.py"   # all tool tests, under 2 seconds
python tools/check_text.py .                           # this repository against the standard
python tools/sync.py --check <repo>                    # a repository's synced files
```

## Ways to hurt yourself

- **Breaking every repository at once.** Repositories pin `uxm-ci.yml` by commit, so a change here reaches them only when their pin moves. Never ask them to call it at `@main`.
- **Billed features.** The organization is on GitHub Free. The shared workflow must never send a private repository's job to a GitHub-hosted runner: private repositories pass `runner: '["self-hosted","uxplima"]'`.
- **Editing a synced file downstream.** `docs/internals/uxm-conventions.md`, `shared/.editorconfig` and `shared/.gitattributes` are canonical here. A repository changes them only by changing them here first and running `tools/sync.py --write`.

## Invariants

- Every action in a workflow is pinned by commit SHA with its version in a comment.
- Workflows set `permissions: {}` at the top and grant each job what it needs, and set `defaults.run.shell: bash` so the same steps run on the Windows runner.
- The tools use the Python standard library only, so CI needs no install step.

## Testing

Tools are tested with `unittest` on temporary directories through their public functions (`check`, `main`, `drifted`). No test reads a source file as text.

## Pull requests

Titles are conventional commits. Scopes: `standard`, `conventions`, `workspace`, `tools`, `ci`, `profile`.
