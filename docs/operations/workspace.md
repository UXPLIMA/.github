# UXPLIMA workspace

The local workspace on the owner's Windows PC that replaces `/home/uxm-setups` on the old server. One Claude session works here at a time. Product rules are in [uxm-conventions.md](../internals/uxm-conventions.md), repository rules in [repository-standard.md](repository-standard.md).

## Why

The old workspace mixed four things in one folder: product code, caches (23 GB Gradle, 9.8 GB Maven), runtime snapshots (62 lobby copies, 16 GB) and working notes. Its documents grew into diaries (dated notes, ADRs, 1000-line canons) and its tests into thousands of change detectors. The new workspace keeps each of those in its own place and lets tools enforce the rules.

## Goals

- `tools/setup.sh` recreates the whole workspace from GitHub on a clean machine.
- Every repository follows the repository standard after its migration.
- Developing, updating plugins and building server setups all happen from this one folder.
- The final state of `uxm-lobby` is preserved.

## Non-goals

- No license checks, obfuscation or license server in any build.
- No multi-session coordination (manager, reviewer sessions, message passing). One session.
- No support for Minecraft versions below 26.2.

## Layout

```
setups/                        UXPLIMA/uxplima-org: workspace root, holds no product code
  AGENTS.md                    workspace guide (sessions, layout, machine, owner preferences)
  CLAUDE.md                    @AGENTS.md
  README.md
  .gitignore                   ignores every checkout below and run/
  .claude/settings.json        deny Agent; shared permission allowlist
  tools/
    setup.sh                   clone every repository into its place; safe to rerun
    repo-setup.sh              apply ruleset, labels and merge settings to one repository
    repos.txt                  repository name and folder, one per line
  .github/                     UXPLIMA/.github: standards, reusable workflows, synced files, sync tool
  gradle/                      UXPLIMA/uxm-gradle: convention plugins and the uxm version catalog
  lib/uxm-lib/                 UXPLIMA/uxm-lib
  plugins/<repo>/              one checkout per plugin, folder named as the repository
  setups/<setup>/              one checkout per server setup
  run/<setup>/                 ignored: a running server assembled from a setup
```

Folders carry their GitHub repository names; a setup's folder drops the `-setup` suffix.

## Server setups

A setup is a repository (`UXPLIMA/<name>-setup`, private, checked out at `setups/<name>/`) that describes a server network. Its name follows the product it ships, so `uxm-lobby` lives in `uxm-lobby-setup`; a running server is assembled from it and is never committed.

```
uxm-lobby-setup/
  AGENTS.md  CLAUDE.md  README.md
  setup.toml                   servers, exact jars with sha256, backup location
  servers/<server>/            server.properties, platform configs, plugins/<Plugin>/ configs
  secrets.example.env          every secret the setup needs, with empty values
  tools/up.py  tools/backup.py
```

- `python tools/up.py` builds `run/<setup>/`: it restores the newest state backup, copies the configs over it with every `{{secret.NAME}}` filled from an untracked `.env`, and places every jar after checking its sha256. A jar comes from its release, or from the imported final copy of the old setup until it has one.
- State (worlds, plugin databases, keys, operators and whitelist) never enters git. It is backed up on the owner's PC under `~/uxm-backups/<setup>/<server>/state-<yyyymmdd-hhmm>.tar.gz`, outside the workspace. `python tools/backup.py` writes one archive per run with the servers stopped and keeps the newest five.
- Secrets (`forwarding.secret`, database passwords, webhook URLs) never enter git. `${NAME}` stays a HOCON substitution that plugins read themselves.

The final `uxm-lobby` of the old server is kept untouched under `~/uxm-backups/uxm-lobby/final/`: its configs are the repository, its state the first backup.

## CI runners

CI of private repositories runs on the organization's self-hosted Linux runners (`uxplima-runner-1` to `-3`, labels `self-hosted, uxplima`), three machines of their own, separate from the development server. They cost nothing. GitHub-hosted runners are used only by public repositories, for which they are free.

## Claude setup

- `CLAUDE.md` is `@AGENTS.md` everywhere. The workspace `AGENTS.md` holds the shared rules (talk to the owner in Turkish, write files in English, no em dash, no subagents, no co-author lines). Each repository's `AGENTS.md` holds only its own.
- `.claude/settings.json` in the workspace and every checkout denies `Agent`. `tools/setup.sh` writes it.
- Shared skills live in `UXPLIMA/.github` and are synced into repositories that need them. A skill is written only after the same need came up more than once.
- No Stop hook at first: Gradle builds are too slow to run on every turn. CI enforces; `AGENTS.md` names the fast check.

## Order of work

1. `UXPLIMA/uxplima-org`, `UXPLIMA/.github` and `UXPLIMA/uxm-lobby-setup`, with the standards, the checks and the shared workflow.
2. `UXPLIMA/uxm-gradle` with the convention plugins and catalog, extracted from the current `buildSrc` and `libs.versions.toml`.
3. uxmLib, then `uxm-plugin-template` as the pilot, then the plugins in groups. Each migration deletes the repository's whole test suite and restarts its version at `0.0.1`; new tests follow in later pull requests.

## Left to the builder

- Exact SHA pins, action versions and Gradle plugin versions.
- The text check's implementation and its precise patterns.
- The ArchUnit rule set, kept to dependency direction and the forbidden APIs.
- How `up.py` downloads released jars once plugins and the server have releases.
