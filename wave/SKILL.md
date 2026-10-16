---
name: wave
description: Control Wave Terminal with the wsh CLI from inside a Wave block. Use when asked to open, show, or display a file, PDF, image, directory, or website in Wave, run a command in a new block, manage blocks, tabs, or workspaces, send output to Wave AI, notify, or inspect terminal state, or when WAVETERM / WAVETERM_BLOCKID env vars are present. Prefers wsh view, wsh web open, and wsh run over launching a new terminal app or using xdg-open / open.
---

# Wave Terminal control with `wsh`

When the agent runs inside Wave Terminal, the user is already looking at Wave.
"Open X in Wave" therefore means **open a block in the current Wave window**
using the `wsh` CLI — never launch a second Wave app, and never shell out to
`xdg-open` / `open` / `waveterm` for on-screen display.

## 1. Am I inside Wave?

Check before assuming `wsh` can control any UI:

```sh
[ -n "$WAVETERM" ] && echo "inside wave"
command -v wsh
echo "block=$WAVETERM_BLOCKID tab=$WAVETERM_TABID workspace=$WAVETERM_WORKSPACEID"
```

- `WAVETERM=1` (+ `TERM_PROGRAM=waveterm`) means stdin/stdout is a Wave block.
  `wsh` commands issued here affect the surrounding UI.
- `WAVETERM_BLOCKID`, `WAVETERM_TABID`, `WAVETERM_WORKSPACEID` identify where
  you are. `wsh` targets the current block/tab by default, so usually no IDs
  are needed.
- If `WAVETERM` is unset or `wsh` is missing, you are **not** in Wave. Say so
  and stop: `wsh view` / `wsh web open` will not display anything for the user.

`wsh` is on `PATH` inside Wave (typically `~/.local/share/waveterm/bin/wsh`).
Help is local and authoritative: `wsh --help`, `wsh <cmd> --help`.

## 2. Mental model (just enough)

| Concept | What it is | Notes for agents |
|---|---|---|
| Workspace | Top-level grouping of windows | List with `wsh workspace list` |
| Window | An OS window showing tabs | IDs come from `wsh workspace list` |
| Tab | A row of blocks | Scopes state; address as `-b tab` |
| Block | One visual panel (terminal, preview, web, editor, AI) | Every display action creates one |
| View | Block type: `term`, `preview`, `web`, `edit`, `waveai`, `sysinfo` | Filter listings with `--view=` |
| Magnified | Full-tab focus mode for one block | Flag `-m` / `--magnified` / `--magnify` |
| Badge | Icon overlay on a block/tab header | `wsh badge`; cleared with `--clear` |

Pressing Ctrl+Shift in the UI overlays block numbers. Those numbers (1–9) are
usable as `-b` targets alongside UUIDs.

## 3. Addressing a block (`-b`)

Most `wsh` commands act on the current block unless `-b` says otherwise:

```sh
wsh getmeta                  # current block ("this", the default)
wsh getmeta -b 2             # block number 2 in current tab
wsh getmeta -b tab           # current tab
wsh getmeta -b workspace     # current workspace
wsh getmeta -b 8e711d45      # UUID prefix (first 8+ chars suffice)
wsh getmeta -b d6ff4966-231a-4074-b78a-20acc7226b41  # full UUID
```

The same `-b` values work for `setmeta`, `setvar`/`getvar`, `badge`,
`focusblock`, `deleteblock`, and `termscrollback`. Variable scopes also accept
the words `block`, `tab`, `workspace`, `client` (global), e.g.
`wsh setvar -b tab SHARED_ENV=staging`.

## 4. The display commands (use these, not app launchers)

### Open a file, PDF, image, or directory — `wsh view`

This is the answer to "open this PDF / image / markdown / folder in Wave":

```sh
wsh view ./report.pdf        # PDF renders in a preview block
wsh view ./screenshot.png    # images render
wsh view README.md           # markdown renders; text/code opens editable
wsh view ./src               # directories get a file browser
wsh view -m ./report.pdf     # magnified (full-tab) variant
```

- Aliases: `wsh preview`, `wsh open` are the same command. For URLs use
  `wsh web open`, not `wsh view`.
- Prefer **absolute or `./`-relative paths** from the current `cmd:cwd`
  (check with `wsh getmeta` if unsure). Quote paths with spaces.
- `wsh view` opens **in Wave**. Do not substitute `xdg-open`, `open`,
  `evince`, browsers, or a bare `waveterm` invocation.

### Open a website — `wsh web open`

This is the answer to "open this website in Wave":

```sh
wsh web open https://example.com
wsh web open -m https://github.com          # magnified web block
wsh web open localhost:3000                # scheme optional, still opens
wsh web open "wave terminal documentation" # bare text = search engine query
wsh web open -r 2 https://example.com      # replace block 2 instead of new block
```

- `-m` and `-r` are mutually exclusive.
- This renders **inside Wave** as a web block. Do not open the system browser.

### Edit a file — `wsh edit` / `wsh editor`

```sh
wsh edit ./config.json       # opens graphical editor, returns immediately
wsh edit -m ./config.json    # magnified editor
wsh editor ./CHANGELOG.md    # BLOCKS until the editor tab is closed
export EDITOR="wsh editor"   # $EDITOR integration (git commit, crontab -e)
```

`edit` is fire-and-forget; `editor` is for tools that wait on `$EDITOR`.
The file must already exist for `wsh editor`.

### Run something in a new block — `wsh run` / `wsh term`

```sh
wsh run -- npm test                 # new block running npm test
wsh run -c "ls -la | head"          # -c for shell strings (pipes, redirects)
wsh run -m -- npm run dev           # magnified dev server
wsh run -x -- npm test              # auto-close block on success, stay open on error
wsh run -X -- ./flaky.sh            # auto-close regardless of exit status
wsh run -x --delay 5000 -- ./deploy.sh   # wait 5s before auto-close
wsh run --cwd ./project -- make test     # explicit working directory
wsh run -p -- ./server --dev        # create paused, let user press Enter
wsh term                            # empty terminal block (add -m to magnify)
```

- Prefer `-- cmd args...` for plain commands (exact argv), `-c "..."` only
  when you need shell features.
- Without `-x`/`-X`, the block stays and Enter re-runs the command.
- Commands inherit the current environment and cwd by default.

## 5. Recipes for the requests agents get wrong

| User says | Wrong | Right |
|---|---|---|
| "open this PDF in Wave" | `xdg-open report.pdf`, launching WaveTerm app | `wsh view ./report.pdf` |
| "open this site in Wave" | `xdg-open https://…`, `firefox …` | `wsh web open https://…` |
| "show this folder / README" | `ls`, `cat` into chat only | `wsh view .` / `wsh view README.md` (+ chat summary) |
| "edit this file" | `sed -i`, instructing user to open editor | `wsh edit <file>` |
| "run the dev server where I can see it" | background `&` job in current block | `wsh run -m -- npm run dev` |
| "tell me when the build finishes" | polling, silence | `npm run build && wsh notify "Build complete"` |

Each display command should still get a one-line chat confirmation, e.g.
"Opened `report.pdf` in a preview block." — the user may not be watching the
tab that received the block.

## 6. Reading state (inspect before acting)

```sh
wsh getmeta                       # metadata of current block (has cmd:cwd, view, controller)
wsh getmeta -b 2 file             # what file is preview block 2 showing?
wsh getmeta -b tab                # current tab metadata
wsh getmeta -b tab "bg:*"         # prefix query
wsh blocks list                   # all blocks (add --view=term|web|preview|edit|waveai)
wsh blocks list --view=web --json # JSON for scripting
wsh workspace list                # workspaces / windows
wsh termscrollback --lastcommand  # output of last command (needs shell integration)
wsh termscrollback -b 2 -o log.txt  # scrollback of block 2 into a file
wsh getvar API_KEY                # persistent variable (exit 1 if unset)
wsh getvar --all                  # list all (add -0 for null-terminated scripting)
```

Use `wsh getmeta` output's `cmd:cwd` to resolve relative paths. Use
`wsh blocks list --json` before scripting over blocks; block numbers shift as
blocks open/close.

## 7. Writing state, feedback, and AI handoff

```sh
# Persistent variables (survive sessions; scopes: block/tab/workspace/client)
wsh setvar API_KEY=abc123
wsh setvar -b tab SHARED_ENV=staging
wsh setvar -l BLOCK_ONLY=1         # block-local
wsh setvar -r OLD_KEY              # remove

# Move a preview/web block to new content without a new block
wsh setmeta -b 2 file=~/notes.md
wsh setmeta -b 2 url=https://example.com

# Focus / cleanup
wsh focusblock -b 2
wsh deleteblock -b 2
wsh badge circle-check --color green --beep   # draw attention; --clear to remove
wsh badge --pid 12345                         # auto-clear when PID exits (not on Windows)
wsh notify "Deploy done" -t "CI"              # desktop notification; -s silences sound
wsh setbg --opacity 0.3 ~/pics/bg.jpg         # tab background; --clear removes

# Files across local + remote (10 MB cap on cat/write/cp/mv)
wsh file ls ./local-dir/ -l
wsh file cat wsh://user@host/home/user/app.log
wsh file cat /~/config/app.json               # /~/ = local machine from a remote block
echo hi | wsh file write ./greeting.txt
wsh file cp ./a.csv wsh://user@host/~/a.csv

# Secrets (system keychain; never echo values into chat/logs)
wsh secret set github_token=ghp_xxx
wsh secret get github_token
export API_KEY="$(wsh secret get my_api_key)"

# Send context to Wave's AI sidebar (attachments, not pasted text)
git diff | wsh ai -                              # stdin; user submits in UI
wsh ai main.go -m "find bugs"                    # attach + message, no auto-submit
tail -n 50 app.log | wsh ai -s - -m "why?"       # -s auto-submits
wsh ai -n report.pdf -m "summarize"              # -n starts a fresh chat
```

Limits: `wsh ai` ≤ 15 files; text ≤ 200 KB, PDF ≤ 5 MB, image ≤ 7 MB each.
`wsh file` transfers ≤ 10 MB. Secret names match `[A-Za-z][A-Za-z0-9_]*`.

Miscellaneous (reach for these only when asked): `wsh launch <widget-id>`
opens a pre-configured widget (see `widgets.json` via `wsh editconfig
widgets.json`); `wsh wavepath {config|data|log}` prints Wave paths (`-t log`
tails the log for troubleshooting); `wsh conn {status|connect|disconnect|
ensure|reinstall}` manages SSH/WSL connections; `wsh editconfig [file]` opens
Wave config files; `wsh setbg` extras (`--tile`, `--center`, `--clear`) are
detailed in `wsh setbg --help`.

## 8. Rules

1. **Inside Wave, display means `wsh`.** Never run `waveterm`, `xdg-open`,
   `open`, `gnome-open`, or a GUI browser/editor to satisfy "open/show in
   Wave".
2. **Quote and absolutize.** Quote `#` colors (`"#ff0000"`), URLs with `&`,
   and paths with spaces. Resolve relative paths against `cmd:cwd`.
3. **One block per intent.** Prefer `-r <block>` (web) or `setmeta` retarget
   over opening duplicate blocks when the user says "now show X instead".
4. **Do not scrape the UI.** `wsh getmeta` / `blocks list --json` /
   `termscrollback` are the APIs; never parse screenshots or terminal escape
   output to discover block state.
5. **Keep secrets secret.** Get-then-use in one substitution; never print,
   log, or `wsh ai`-attach secret values.
6. **Confirm briefly.** After each display action, name what opened where
   (`preview block`, `web block`, `new run block`) so the user can find it.

## 9. When it fails

- `wsh: command not found` → not in Wave (or stripped `PATH`). Check
  `$WAVETERM`, offer `~/.local/share/waveterm/bin/wsh`.
- New block opens in an unseen tab → announce it; use `wsh focusblock -b <id>`
  only when asked to bring it forward.
- `wsh blocks list` → `Error: no workspaces found` → RPC not reachable from
  this context; fall back to `wsh getmeta` for local context and continue.
- `wsh web open` shows search instead of page → the URL lacked a scheme or
  host typo; retry with full `https://`.
- `wsh ai` rejects files → over count/size caps; trim to the smallest
  relevant subset and retry.

## References

- `wsh --help`, `wsh <command> --help` (local, authoritative for installed version)
- [wsh overview](https://docs.waveterm.dev/wsh) — concepts, variables, remote-local file access, AI sidebar, scripting
- [wsh reference](https://docs.waveterm.dev/wsh-reference) — per-command flags for `view`, `edit`/`editor`, `web`, `run`, `getmeta`/`setmeta`, `getvar`/`setvar`, `file`, `ai`, `badge`, `notify`, `launch`, `termscrollback`, `wavepath`, `blocks`, `secret`, `conn`, `setbg`
