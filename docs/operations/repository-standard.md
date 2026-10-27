# Repository standard

How every repository of the UXPLIMA organization is laid out, documented, tested and changed. It applies to plugins, uxmLib, the build tooling and the server setups. How a plugin behaves for players and operators is in [uxm-conventions.md](../internals/uxm-conventions.md).

The model is the Rawframe Project standard, itself modeled on [pingdotgg/t3code](https://github.com/pingdotgg/t3code). Sources are listed at the end.

Contents: [Principles](#principles) · [Files](#files) · [AGENTS.md](#agentsmd) · [Documentation](#documentation) · [Tests](#tests) · [Build](#build) · [Continuous integration](#continuous-integration) · [Changes](#changes) · [Releases](#releases) · [Work](#work) · [Enforcement](#enforcement) · [Migrating a repository](#migrating-a-repository)

## Principles

1. **A repository reads like a product, not a diary.** It says what the product is and how it works today. History lives in git, pull requests and the changelog.
2. **Less context is better context.** Every line of guidance must prevent a real mistake.
3. **Rules that must always hold are enforced by a tool.** Prose is advice; a build check, a CI job or a hook is a guarantee.
4. **Code is the source of truth.** Documentation explains what the code cannot: intent, constraints and traps.
5. **Tests guard behavior, not structure.** A test that breaks on a refactor with no behavior change is a defect.

## Files

A repository contains these documentation files and no others outside `docs/`, `.agents/` and `.github/`.

| Path | Purpose |
|---|---|
| `README.md` | What the product is, a quick start, links. For buyers and server owners. |
| `AGENTS.md` | The guide for coding agents. See [AGENTS.md](#agentsmd). |
| `CLAUDE.md` | One line: `@AGENTS.md`. |
| `CHANGELOG.md` | User-facing changes per release, written by release-please and curated. |
| `LICENSE` | MIT for public libraries. Private plugins carry none. |
| `docs/README.md` | Index of the documentation. |
| `docs/user/` | For operators: install, configure, commands, permissions, placeholders, troubleshooting. |
| `docs/internals/` | How it works and why. Always `overview.md`; `uxm-conventions.md` is synced in. |
| `docs/operations/` | How to develop, test and release it. |
| `.agents/skills/` | Agent skills. `.claude/skills` points to it. |

Never committed: plans, research notes, work logs, decision records, numbered docs, dated notes, task lists, screenshots for one pull request. Working material stays outside the repository; progress lives in the issue.

## AGENTS.md

Hand-written, at most 200 lines. For every line ask whether an agent would make a mistake without it; if not, delete it.

It contains, in this order:

1. **What the product is** in two or three sentences, and what it never compromises on.
2. **Commands** an agent cannot guess: the build, the fast check, one test, running a local server.
3. **Ways to hurt yourself:** actions that damage state, a running server or the machine, and what to do instead. Every repository includes: never kill a process found by matching a name; kill only a PID you started.
4. **Invariants** not visible from one file: dependency direction, generated files, shared files that must not be edited here.
5. **Testing rules** specific to the repository, on top of [Tests](#tests).
6. **Pull requests:** the commit scopes the repository uses.

It never contains directory tours, file lists, feature lists, API descriptions, history, dates or anything the code already says. A procedure needed only sometimes becomes a skill.

## Documentation

- `docs/user/` follows the operator's task: install, configure, use, troubleshoot. One page per major feature. `docs/user/reference.md` lists every command, permission and placeholder.
- `docs/internals/` holds one living page per topic. Each explains how a part works, why it is built that way, and the traps that are hard to see in the source. It links to source instead of copying it.
- Most code changes need no documentation change. When a documented behavior changes, rewrite or delete the affected text in the same pull request. Never append a dated note or a second account.
- Present tense, third person, the product's voice. No first person, no "we decided", no dates, no names, no internal numbers.
- A decision is recorded by writing its reasoning into the relevant internals page and by the pull request that made it. A rejected alternative gets one short paragraph only when someone would otherwise try it again.
- Pages stay under 400 lines; reference pages over 100 lines start with a table of contents.

## Tests

### What gets a test

Tests protect what a player, an operator or a caller relies on: domain rules, use case outcomes, storage on every backend, configuration and migration behavior, wire and file formats, and bugs that already escaped once.

- **Domain and use cases:** plain JUnit 5 and AssertJ, with hand-written fakes for ports. No server, no mocks of our own classes.
- **Storage adapters:** `@EveryBackend` from `uxmlib-storage-testing`, tagged `real-database`.
- **Integration:** a few end-to-end scenarios per plugin with MockBukkit (enable the plugin, run the main command flow, reload, upgrade an old config), tagged `integration`.
- **Bug fixes** to logic, data or state come with the fewest tests that fail on the unfixed code for the right reason, in the module's existing test file.
- **Visual and wording changes** (colors, lore, layout, messages, sounds) get no test. The proof is a before and after capture in the pull request.
- **New features:** tests cover the behavior someone relies on. A case is added only when the code branches differently for it.

### What never gets a test

- A test that reads source code, comments, documentation or build files as text.
- A test that asserts the implementation: call order, `verify()` mirrors of the code, private state, class or method names.
- A test that exists to prove another test exists.
- A test for a getter, a record, a constant or framework behavior.

Rules that can be checked statically belong to a tool, not a test: the single ArchUnit test for dependency direction and forbidden APIs, Error Prone, NullAway, Spotless and the text check.

### How a test is written

- It goes through the public interface and survives refactoring.
- Every assertion can fail, and the strongest exact check is preferred.
- It is deterministic and hermetic: no wall clock (inject a `Clock`), no sleeps, no polling, no external network, no retries. A flaky test is fixed, not retried.
- A unit test runs in milliseconds, an integration test in about a second.
- A skipped or aborted test fails the build. MockBukkit's unimplemented methods abort tests, so a scenario that needs one is rewritten or removed.
- The failure message says what broke.

### Budgets

- `./gradlew check -Pchanged`, the fast check an agent runs before pushing: under 2 minutes.
- The pull request check in CI: under 10 minutes, `real-database` included.
- Over budget, tests are pruned or merged before anything is added.

## Build

- Gradle with the Kotlin DSL and the wrapper committed. Gradle and Maven caches stay in the user's home, never inside the repository or workspace.
- Build logic comes from the `uxm-gradle` convention plugins published to `repo.uxplima.com`: `uxm.java` (toolchain, compiler flags, Error Prone, NullAway, Spotless, test setup, skip and abort checks), `uxm.paper-plugin` (Paper API, Shadow, relocation, jar verification, run-paper) and `uxm.library` (publishing). A repository has no `buildSrc`.
- Versions come from the shared `uxm` version catalog published by `uxm-gradle`. A repository adds its own catalog entries only for dependencies no other repository uses.
- `./gradlew build` runs everything CI runs: formatting, compile with checks, tests, jar verification.
- `./gradlew runServer` starts a local Paper server with the plugin, under `run/` in the repository, ignored by git.

## Continuous integration

A repository's `ci.yml` calls the reusable workflows in `UXPLIMA/.github`.

- **Jobs:** `changes` (a pull request that touches only documentation skips the build), `build` (`./gradlew build` on Temurin 25 with `gradle/actions/setup-gradle`), `text` (the text check), `title` (pull request title), and `required`.
- **One required check.** `required` runs `if: always()`, needs every other job, and fails if any failed or was cancelled. The ruleset requires only `required` and `title`.
- **Runners.** Private repositories run only on the organization's self-hosted Linux runners (`[self-hosted, uxplima]`), never on GitHub-hosted runners, whose minutes are billed for private repositories. Public repositories run on GitHub-hosted runners, which are free for them.
- **Free features only.** No Git LFS, GitHub Packages, Codespaces, larger runners, or code and secret scanning on private repositories. Public repositories may use the free CodeQL and secret scanning. Self-hosted jobs run only for branches of the same repository, never for a fork. Every workflow sets `defaults.run.shell: bash`.
- **Caches.** The Gradle cache is written only from `main`; pull requests read it.
- **Concurrency.** A new push to a pull request cancels its running CI. Runs on `main` are never cancelled.
- **Hygiene.** `permissions: {}` at the top and per-job grants, actions pinned by commit SHA with the version in a comment, `persist-credentials: false`, event data passed to scripts only through `env`. Dependabot keeps actions and Gradle dependencies current, weekly and grouped.
- **Failures.** A failed build uploads test reports for a week. A red `main` is fixed before any other work.

## Changes

- Nothing in this standard may cost money: the organization stays on GitHub Free. Public repositories protect `main` with a ruleset (pull requests only, `required` and `title` must pass, linear history, no force push). Private repositories cannot have rulesets on the Free plan, so the same rules hold by practice there: changes arrive through pull requests and merge only when `required` is green.
- Branch names are short and hyphenated without prefixes (`key-limits`).
- Pull request titles are conventional commits: `type(scope): summary`, lower case, under 72 characters. Types: `feat`, `fix`, `perf`, `refactor`, `docs`, `test`, `build`, `ci`, `chore`. Scopes are listed in the repository's `AGENTS.md`.
- The body has three parts: Problem, Change, Verification (what was run and what it showed), and ends with `Closes #<issue>`.
- Pull requests are squash-merged; the title becomes the commit on `main`. Auto-merge is on.
- One issue, one pull request. Unrelated fixes go in separate pull requests.
- Before merging, the change is reviewed in a fresh context with `/code-review`: correctness first, then this standard.
- Commits and pull requests carry no `Co-Authored-By`, "Generated with", model or session lines. The owner is the author.

## Releases

- Semantic Versioning, tags `vX.Y.Z`, managed by release-please from the conventional commits.
- Versions stay below 1.0.0 while the API or the configuration format still changes. A breaking change carries `!` and a `BREAKING CHANGE:` footer; before 1.0.0 it bumps the minor.
- For a plugin, breaking means an operator must edit a file or loses data. Configuration and storage migrations exist so that this is rare.
- Before merging a release pull request, its changelog entry is rewritten for operators: Added, Changed, Fixed, Removed. Internal refactors and tests are left out.
- A plugin release attaches the shaded jar and a `SHA256SUMS` file to the GitHub release. uxmLib and `uxm-gradle` publish to `repo.uxplima.com`.
- Every repository restarts at `0.0.1` when it migrates to this standard.

## Work

- Work is tracked in GitHub issues on the organization's single Project board: Backlog, Ready, In progress, In review, Done. Milestones group issues toward a release or a server launch.
- The issue body is the progress record: a short problem statement and a checklist. Findings that matter later go into issue comments, not files.
- Labels: `bug`, `feature`, `docs`, `test`, `performance`, `security`, `chore`, `blocked`, `duplicate`, `wontfix`.

## Enforcement

- **Text check** (`UXPLIMA/.github`): only the allowed documentation files; `CLAUDE.md` is exactly `@AGENTS.md`; `AGENTS.md` at most 200 lines, pages at most 400; no em or en dash; no dates, issue numbers or decision ids in docs and comments; links resolve.
- **Title check:** conventional commit format and a known scope.
- **Build:** Spotless, Error Prone, NullAway, `-Werror`, the ArchUnit test, skipped and aborted tests fail, jar verification.
- **Synced files:** `docs/internals/uxm-conventions.md`, `.editorconfig`, `.gitattributes` and the shared `.gitignore` are written by `tools/sync.py` in `UXPLIMA/.github` and checked nightly; a drift is fixed like a red `main`.

## Migrating a repository

One pull request, or for a large repository a short series (files and docs, then tests and build, then comments):

1. Write `AGENTS.md`, `README.md` and `docs/` from the code. Old documents are read only to recover intent; nothing is copied.
2. Delete everything this standard does not allow: `docs/notes/`, `docs/adr/`, numbered docs, `buildSrc`, local style scripts.
3. Switch the build to the `uxm-gradle` plugins and the shared catalog.
4. Delete every existing test. The old suites are not pruned: none of them is carried over. New tests are written to the rules above, starting with storage on every backend and the core domain rules, in later pull requests.
5. Rewrite comments to say why, without history.
6. Add the shared CI, release-please with the manifest at `0.0.1`, the ruleset and labels (`tools/repo-setup.sh`). The pull request body ends with `Release-As: 0.0.1`.

Order: `uxm-gradle`, then uxmLib, then `uxm-plugin-template` as the pilot plugin, then the plugins in groups of three or four.

## Sources

- Anthropic, [Best practices for Claude Code](https://code.claude.com/docs/en/best-practices) and [How Claude remembers your project](https://code.claude.com/docs/en/memory): CLAUDE.md under 200 lines, prune what the agent already does right, enforce with hooks and checks, procedures as skills.
- Rawframe Project, [repository standard](https://github.com/Rawframe-Project/.github/blob/main/docs/repository-standard.md), and [t3code AGENTS.md](https://github.com/pingdotgg/t3code/blob/main/AGENTS.md).
- Gloaguen et al., [Evaluating AGENTS.md](https://arxiv.org/abs/2602.11988): generated, long context files lower success.
- Google Testing Blog, "Change-Detector Tests Considered Harmful", and *Software Engineering at Google*, chapters 12 and 13: test behavior through public APIs, prefer fakes to mocks.
- Kent Beck, [Test Desiderata](https://testdesiderata.com/).
- [Conventional Commits](https://www.conventionalcommits.org/), [release-please](https://github.com/googleapis/release-please), [Diataxis](https://diataxis.fr/).
