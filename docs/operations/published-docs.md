# Published documentation

Every UXM product has a manual on [docs.uxplima.com](https://docs.uxplima.com), written in
[UXPLIMA/docs](https://github.com/UXPLIMA/docs). The model is uxmClaims (`content/minecraft/plugins/uxmclaims/`): a
reader who bought the plugin finds every command, permission, setting, message, menu and placeholder there, with what
it does and what it defaults to, without opening a file or asking. A plugin's manual is held to that standard.

## Where it lives

- A plugin's manual is `content/minecraft/plugins/<name>/`, where `<name>` is the plugin name in lower case
  (`uxmparkour`). A setup's is under `content/minecraft/setups/`.
- `docs/user/` in the plugin repository stays the short guide that ships with the code. The manual is the full
  account, written for the buyer.
- A plugin's own section of the manual is replaced only by a manual that says at least as much. Before a page is
  deleted, what it says is read and either carried into the new page or checked to be wrong.

## Layout

The plugin folder holds one `index.md` and a folder per section, each with its own `index.md` that lists its pages in a
table. A section the plugin has nothing for is left out; one the plugin needs and this list does not name is added in
the same shape (uxmClaims has `protection/`, uxmEssentials has `modules/`).

| Section | Pages |
|---|---|
| `getting-started/` | `welcome.md` (what it is and who it is for), `installation.md` (a requirements table, optional plugins with what each adds, the install steps, the file tree the first start writes), `concepts.md` (the ideas the rest builds on), and a first walk-through such as `first-claim.md` |
| `commands/` | `overview.md` (the roots, aliases, how a command picks its target, renaming in `commands.conf`), then one page per group of commands, each command with its arguments, what it does, and the permission it needs |
| `menus/` | `overview.md`, then one page per window: what each slot does, what each click does, and a screenshot taken in game |
| feature sections | One folder per concept the plugin is built around, such as `protection/`, `arenas/`, `rewards/` |
| `config/` | `index.md` with a table of every file, then one page per file: every key with its default and what it does, grouped as the file groups them; `messages.md` for the language files and how a line is written; `languages.md` for the shipped languages and how one is chosen |
| `permissions/` | `reference.md` with every node, its default and what it grants, and pages for limits or abilities when nodes carry numbers or sets |
| `placeholders/` | `reference.md` with every placeholder, what it renders, and whether it answers for an offline player |
| `integrations/` | `overview.md` with every plugin it hooks into and what each turns on, then a page per integration that has settings of its own |
| `database/` | `overview.md`, then a page per supported backend, with the settings and how to move between them |
| `developer/` | For a plugin with an API: how to depend on it, the API, the events, the models |

## Pages

- Front matter on every page: `title`, `order`, a one-line `description` and an `icon` (a [Lucide](https://lucide.dev)
  name). The plugin `index.md` carries the plugin's order among the plugins; section `index.md` files are numbered
  `10`, `20`, `30` in reading order, and the pages of a section continue the section's number (`101`, `102`).
- Tables before sentences: commands, permissions, keys, placeholders, slots and files are tables. A sentence explains
  a rule a table cannot hold.
- Every table cell is checked against the code and the shipped files of the release the manual describes, never
  written from memory or from an older page. A default is the shipped value.
- One `Callout` per page at most, for a mistake that costs the reader something: a node nobody has by default, a
  setting that locks everybody out.
- Links between pages name the file, such as `../getting-started/installation.md`, so they survive every
  version and locale.
- The writing rules of the [repository standard](repository-standard.md#documentation) apply: present tense, second
  person for the reader, no marketing words, no dash, English.

## Keeping it current

- A pull request that changes what the manual says (a command, a node, a key, a default, a message, a window) comes
  with a pull request to UXPLIMA/docs that changes the manual to match, and each names the other.
- A release is not done until its manual describes it. The installation page names the version it describes.
- Before a docs pull request merges, the content compiles with the platform's own compiler (`compileFilesystemSource`
  and `validateCompiledPages` from `packages/content` in uxw-docs) and `scripts/check-style.sh` is clean. Publishing
  the new snapshot is a step in the administration.
