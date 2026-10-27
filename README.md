# UXPLIMA organization defaults

The organization's shared standards, CI and community files. Every UXPLIMA repository follows the standards here and calls the shared workflow.

- [Repository standard](docs/operations/repository-standard.md): how a repository is laid out, documented, tested and changed.
- [UXM plugin conventions](docs/internals/uxm-conventions.md): how a plugin behaves for operators and players.
- [Workspace](docs/operations/workspace.md): the local workspace, server setups and the CI runner.

## Tools

```sh
python tools/check_text.py <repo>          # documentation files, dashes, dates, decision ids, links
python tools/check_title.py "<title>" <scopes...>   # pull request title
python tools/sync.py --write|--check <repo>  # files every repository keeps identical
```

## CI

Repositories call `.github/workflows/uxm-ci.yml` from their own `ci.yml`, pinned by commit. See the repository standard's Continuous integration section.
