# Working in this repository

Personal dotfiles for macOS, managed with [dotbot](https://github.com/anishathalye/dotbot).
Forked from [sobolevn/dotfiles](https://github.com/sobolevn/dotfiles).

## Layout

| Path | What it holds |
|------|----------------|
| `install` | Entry point. Syncs submodules, then runs each `steps/*.yml` through dotbot. |
| `steps/` | dotbot configs: `terminal.yml` (symlinks), `dependencies.yml` (Brewfile), `vscode.yml`. |
| `config/` | The dotfiles themselves. `steps/terminal.yml` symlinks them into `$HOME`. |
| `Brewfile` | Every package, cask, App Store app and editor extension on the machine. |
| `scripts/brew-dump` | Regenerates the Brewfile from the machine and opens a PR. |
| `dotbot/`, `dotbot-brewfile/` | Submodules. Do not edit; bump them instead. |

`CLAUDE.md` is a symlink to this file.

## Upgrades

The two upgrade paths are separate, and neither runs on its own.

**Pull in changes from the parent repo.** The `upstream` remote is already
configured:

```bash
git fetch upstream
git merge upstream/master        # merge, not rebase: this is a long-lived fork
git submodule update --init --recursive
```

Expect conflicts in `Brewfile` and `config/`, which are the personalised files.

**Apply the Brewfile to the machine.** `./install` installs only taps and
formulae, because `steps/dependencies.yml` sets `include: ['tap', 'brew']` and
`no-upgrade: true`. Casks, Mac App Store apps and editor extensions need an
explicit call:

```bash
brew bundle install --file=Brewfile           # everything, including casks
brew bundle check   --file=Brewfile --verbose # what is still missing
brew bundle cleanup --file=Brewfile           # list strays; --force uninstalls
```

Removing a line from the Brewfile never uninstalls anything. Only
`brew bundle cleanup --force` does that. Package versions come from whatever
Homebrew currently serves; the Brewfile pins nothing.

## Brewfile

Do not edit the Brewfile by hand. Run `scripts/brew-dump`, which writes the file
from the machine's actual state and opens a pull request when the result
differs. Pass `--no-pr` to update the file and stop there.

The script exists because `brew bundle dump` alone gets three things wrong on
this machine:

1. **It omits formulae whose tap is gone.** `skhd` is installed, but
   `koekeishiya/formulae` is no longer tapped, so the dump drops it. The script
   re-adds it from its `EXTRA` block.
2. **It reads the wrong editor.** The dump shells out to a `code` binary. There
   is none here, so it returns Cursor's extension list. The script reads
   `~/.vscode/extensions` instead. Cursor-only extensions are therefore absent
   by design: the `vscode` directive installs into VS Code, where they do not
   exist.
3. **It cannot see apps installed outside Homebrew.** Chrome, Cursor, Obsidian
   and the rest live in `/Applications` without a cask. They are listed in the
   script's `EXTRA` block so that a rebuild reinstalls them.

When an app moves in or out of that third category, edit `EXTRA` in
`scripts/brew-dump`, not the Brewfile.

## Conventions

- Commit messages: subject in the imperative, body explaining why. Prefix
  Brewfile changes with `Brewfile:`.
- Shell config lives in `config/`, never in `$HOME` directly. Anything you add
  there needs a matching link in `steps/terminal.yml`.

`gh pr create` defaults its base to the parent repository, because this is a
fork. Always pass `--repo kirmalyshev/dotfiles --base master`.
