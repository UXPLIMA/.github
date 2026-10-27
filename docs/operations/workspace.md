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

Folders carry their GitHub repository names.

## Server setups

A setup is a repository (`UXPLIMA/setup-<name>`, private) that describes a server network; a running server is built from it and is never committed.

```
setup-uxm-lobby/
  AGENTS.md  CLAUDE.md  README.md
  setup.yml                    Paper and Velocity builds, plugin list with exact versions, servers and ports
  proxy/                       velocity.toml and proxy plugin configs
  servers/<server>/            server.properties, paper configs, plugins/<Plugin>/ configs
  secrets.example.env          every secret the setup needs, with empty values
```

- `tools/up.sh <setup>` (in the setup repository) builds `run/<setup>/`: downloads Paper and Velocity, fetches each plugin jar from its GitHub release and checks `SHA256SUMS`, copies configs, restores the worlds from the latest local backup, fills secrets from an untracked `.env`.
- Worlds never enter git or a GitHub release. They live in `run/<setup>/` and are backed up on the owner's PC under `C:\Users\pc\uxm-backups\<setup>\<server>\`, outside the workspace. `tools/backup.sh <setup>` writes one archive per run and keeps the last five.
- Secrets (`forwarding.secret`, database passwords, webhook URLs) never enter git. Config files reference them through placeholders that `up.sh` fills.
- `tools/deploy.sh <setup> <host>` pushes a built setup to a server over SSH and keeps one previous copy for rollback, not one per run.

The final `uxm-lobby` from `/home/uxm-setups/uxm-setups/setups/uxm-lobby` (3.6 GB) is imported once: configs into the repository, worlds into the first local backup, jars dropped in favor of released versions.

## CI runner

The GitHub Actions self-hosted runner runs on this PC as a Windows service, registered to the UXPLIMA organization with the labels `self-hosted, uxplima`. It needs Temurin 25, Git for Windows (bash) and Docker Desktop (the `real-database` tests start MySQL, MariaDB and PostgreSQL containers). Private repositories queue their CI while the PC is off.

## Claude setup

- `CLAUDE.md` is `@AGENTS.md` everywhere. The workspace `AGENTS.md` holds the shared rules (talk to the owner in Turkish, write files in English, no em dash, no subagents, no co-author lines). Each repository's `AGENTS.md` holds only its own.
- `.claude/settings.json` in the workspace and every checkout denies `Agent`. `tools/setup.sh` writes it.
- Shared skills live in `UXPLIMA/.github` and are synced into repositories that need them. A skill is written only after the same need came up more than once.
- No Stop hook at first: Gradle builds are too slow to run on every turn. CI enforces; `AGENTS.md` names the fast check.

## Order of work

1. Create `UXPLIMA/uxplima-org` and `UXPLIMA/.github`, land the three documents, the text check and the reusable workflows.
2. Create `UXPLIMA/uxm-gradle` with the convention plugins and catalog, extracted from the current `buildSrc` and `libs.versions.toml`.
3. Import `uxm-lobby` into `UXPLIMA/setup-uxm-lobby`.
4. Register the self-hosted runner on this PC and move CI off the old server.
5. Migrate uxmLib, then `uxm-plugin-template` as the pilot, then the plugins in groups. Each migration deletes the repository's whole test suite and restarts its version at `0.0.1`; new tests follow in later pull requests.

## Left to the builder

- Exact SHA pins, action versions and Gradle plugin versions.
- The text check's implementation and its precise patterns.
- The ArchUnit rule set, kept to dependency direction and the forbidden APIs.
- How `up.sh` downloads Paper and Velocity builds (their download APIs).
