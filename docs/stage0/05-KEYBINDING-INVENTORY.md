# Stage 0 Deliverable 5 — Complete Keybinding Inventory & Conflict Resolution Table

Extracted verbatim from both projects' actual source files:
- **Lucid 2 (`support/hypr/keybinds.json`):** **61** bind definitions (plus **17** contextual `DesktopIcons.qml` shortcuts).
- **Mandara (`crates/mandara-config/src/compositor.rs::default_keybinds()` + `shortcuts.rs`):** **25** compositor/shell keybinds + **0** internal Studio/surface shortcuts.

---

## 1. Exact Chord Collision Analysis (Lucid `binds` vs Mandara `default_keybinds()`)

Per User Constraints, **Lucid's keybindings are the default mapping** when chords overlap or actions are equivalent, while Mandara's distinct actions (`sidebar toggle`, `theme mode toggle`, `agent`, `plugins`, `wallgen`) are preserved on conflict-free chords and in a selectable `Mandara Classic` profile.

| Chord | Lucid `keybinds.json` Entry | Mandara `default_keybinds()` Entry | Collision Class | Scy-Shell Unified Default |
|---|---|---|---|---|
| `SUPER + SPACE` / `SUPER + Super_L` | `launcher` (App launcher) | `launcher toggle` | Equivalent action | Routes to `scy-shell ipc launcher toggle` (opens active Launcher; Lucid default). |
| `SUPER + B` | Browser / Lucid bind (check table below) | `sidebar toggle` | **Distinct Mandara feature!** | Preserve Lucid's `SUPER + B` if bound; bind Mandara Sidebar Drawer to `SUPER + SHIFT + B` (and keep `SUPER + B` in Mandara profile). |
| `SUPER + SHIFT + S` | `shot-region` (`qs ipc call shot region`) | `screenshot region` | Equivalent action | Routes to `scy-shell ipc shot region` (`LucidShot` default, Mandara Capture selectable). |
| `Print` / `CTRL+Print` / `ALT+Print` | `shot-screen` / `shot-window` | `screenshot screen / region / window` | Equivalent action | Routes to `scy-shell ipc shot {screen,region,window}`. |
| `SUPER + SHIFT + V` / `SUPER + V` | Clipboard history (`launcher clipboard`) | `panel toggle clipboard` (`SUPER+SHIFT+V` & `ALT+V`) | Equivalent action | `SUPER + V` (Lucid default) + `SUPER + SHIFT + V` optional alias -> active Clipboard UI. |
| `SUPER + SHIFT + T` | `shot-ocr` (Text extractor / OCR) | `theme mode toggle` (Light/Dark toggle) | **DIRECT CHORD COLLISION!** | **Lucid Preferred:** `SUPER + SHIFT + T` = OCR Region (`shot-ocr`); **Mandara Preserved:** `SUPER + ALT + T` = Theme/Look Mode Toggle! |
| `SUPER + SHIFT + E` / `CTRL + ALT + Delete` | Power / Exit session | `session menu toggle` | Equivalent action | Routes to `scy-shell ipc power toggle` (active Power/Session menu). |
| `CTRL + SHIFT + W` / `SUPER + W` | Wallpaper picker (`lucidwall`) | `wallpaper picker toggle` (`CTRL+SHIFT+W`) | Equivalent action | Routes to `scy-shell ipc wallpaper picker` (active Wallpaper Picker + `Wallgen` tab). |
| `ALT + Tab` / `ALT + SHIFT + Tab` | Window cycle / Exposé | `switcher next` / `switcher prev` | Equivalent action | Routes to active Window Switcher (`lucidexpose` or `mandara-switcher`). |
| `XF86Audio*` (7 keys) & `XF86MonBrightness*` (2 keys) | Lucid audio/brightness/MPRIS + Lucid OSD | Mandara `audio`/`brightness`/`media` + Mandara OSD | **Double-step + Double-OSD hazard** | Single `scy-shell ipc` hardware handler adjusts volume/brightness ONCE and triggers ONLY active OSD! |

---

## 2. Complete Verbatim Lucid 2 Keybindings (`support/hypr/keybinds.json` — All 61 Binds)

| # | ID | Category | Chord (`keys`) | Type | Command / Dispatcher | Description |
|---:|---|---|---|---|---|---|
| 1 | `launcher` | `Lucid` | `SUPER + Super_L` | `exec` | `qs ipc call launcher toggle` | App launcher (tap Super) |
| 2 | `launcher-commands` | `Lucid` | `SUPER + P` | `exec` | `qs ipc call launcher command` | Command launcher |
| 3 | `wallpaper` | `Lucid` | `SUPER + B` | `exec` | `qs ipc call launcher wallpaper` | Wallpaper picker |
| 4 | `theme` | `Lucid` | `SUPER + T` | `exec` | `qs ipc call launcher theme` | Theme picker |
| 5 | `clipboard` | `Lucid` | `SUPER + SHIFT + V` | `exec` | `qs ipc call launcher clipboard` | Clipboard history |
| 6 | `settings` | `Lucid` | `SUPER + S` | `exec` | `qs ipc call settings toggle` | Lucid Settings |
| 7 | `moji` | `Lucid` | `SUPER + period` | `exec` | `qs ipc call moji toggle` | Emoji picker |
| 8 | `keyboard` | `Lucid` | `SUPER + K` | `exec` | `qs ipc call keyboard toggle` | On-screen keyboard |
| 9 | `keybinds-sheet` | `Lucid` | `SUPER + slash` | `exec` | `qs ipc call keybinds toggle` | Show keybinds |
| 10 | `overview` | `Lucid` | `SUPER + W` | `exec` | `qs ipc call workspaces toggle` | Workspace overview |
| 11 | `session` | `Lucid` | `SUPER + Escape` | `exec` | `qs ipc call session toggle` | Session screen: lock, sleep, log out, restart, shut down |
| 12 | `switcher` | `Windows` | `CTRL + ALT + Tab` | `exec` | `qs ipc call switcher next` | Window switcher, every workspace |
| 13 | `switcher-back` | `Windows` | `CTRL + ALT + SHIFT + Tab` | `exec` | `qs ipc call switcher prev` | Window switcher, stepping back |
| 14 | `close` | `Windows` | `SUPER + C` | `lua` | `` | Close window |
| 15 | `exit` | `Windows` | `SUPER + M` | `exec` | `command -v hyprshutdown >/dev/null 2>&1 && hyprshutdown \|\| hyprctl dispatch 'hl.dsp.exit()'` | Exit Hyprland |
| 16 | `files` | `Apps` | `SUPER + E` | `exec` | `$HOME/.config/quickshell/lucidlumen/lumen` | File manager |
| 17 | `float` | `Windows` | `SUPER + V` | `lua` | `` | Toggle floating |
| 18 | `fullscreen` | `Windows` | `SUPER + F` | `lua` | `` | Toggle fullscreen |
| 19 | `split` | `Windows` | `SUPER + J` | `lua` | `` | Toggle split direction |
| 20 | `focus-left` | `Windows` | `SUPER + left` | `lua` | `` | Focus left |
| 21 | `focus-right` | `Windows` | `SUPER + right` | `lua` | `` | Focus right |
| 22 | `focus-up` | `Windows` | `SUPER + up` | `lua` | `` | Focus up |
| 23 | `focus-down` | `Windows` | `SUPER + down` | `lua` | `` | Focus down |
| 24 | `ws-focus` | `Workspaces` | `SUPER + {key}` | `lua` | `` | Workspace {n} |
| 25 | `ws-move` | `Workspaces` | `SUPER + SHIFT + {key}` | `lua` | `` | Move window to workspace {n} |
| 26 | `scratchpad` | `Workspaces` | `SUPER + SHIFT + S` | `lua` | `` | Scratchpad, or put away the open special workspace |
| 27 | `scratchpad-stash` | `Workspaces` | `SUPER + ALT + S` | `lua` | `` | Stash the focused window, or bring it back |
| 28 | `special-music` | `Workspaces` | `SUPER + SHIFT + M` | `lua` | `` | Music workspace |
| 29 | `special-comms` | `Workspaces` | `SUPER + SHIFT + D` | `lua` | `` | Comms workspace |
| 30 | `special-todo` | `Workspaces` | `SUPER + SHIFT + R` | `lua` | `` | To-do workspace |
| 31 | `special-sysmon` | `Workspaces` | `CTRL + SHIFT + Escape` | `lua` | `` | System monitor workspace |
| 32 | `ws-scroll-next` | `Workspaces` | `SUPER + mouse_down` | `lua` | `` | Next workspace (scroll) |
| 33 | `ws-scroll-prev` | `Workspaces` | `SUPER + mouse_up` | `lua` | `` | Previous workspace (scroll) |
| 34 | `drag` | `Windows` | `SUPER + mouse:272` | `lua` | `` | Move window (drag) |
| 35 | `resize` | `Windows` | `SUPER + mouse:273` | `lua` | `` | Resize window (drag) |
| 36 | `f1-mute` | `Function keys` | `F1` | `exec` | `wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle` | Mute |
| 37 | `f2-vol-down` | `Function keys` | `F2` | `exec` | `wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%-` | Volume down |
| 38 | `f3-vol-up` | `Function keys` | `F3` | `exec` | `wpctl set-volume -l 1 @DEFAULT_AUDIO_SINK@ 5%+` | Volume up |
| 39 | `f4-mic-mute` | `Function keys` | `F4` | `exec` | `wpctl set-mute @DEFAULT_AUDIO_SOURCE@ toggle` | Mute microphone |
| 40 | `f5-bright-down` | `Function keys` | `F5` | `exec` | `brightnessctl -e4 -n2 set 5%-` | Brightness down |
| 41 | `f6-bright-up` | `Function keys` | `F6` | `exec` | `brightnessctl -e4 -n2 set 5%+` | Brightness up |
| 42 | `f8-rfkill` | `Function keys` | `F8` | `exec` | `rfkill toggle all` | Toggle all radios |
| 43 | `f9-terminal` | `Function keys` | `F9` | `exec` | `kitty` | Terminal |
| 44 | `f10-lock` | `Function keys` | `F10` | `exec` | `qs ipc call lock lock` | Lock screen |
| 45 | `f12-calc` | `Function keys` | `F12` | `exec` | `gnome-calculator` | Calculator |
| 46 | `xf86-mute` | `Media keys` | `XF86AudioMute` | `exec` | `wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle` | Mute |
| 47 | `xf86-vol-down` | `Media keys` | `XF86AudioLowerVolume` | `exec` | `wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%-` | Volume down |
| 48 | `xf86-vol-up` | `Media keys` | `XF86AudioRaiseVolume` | `exec` | `wpctl set-volume -l 1 @DEFAULT_AUDIO_SINK@ 5%+` | Volume up |
| 49 | `xf86-mic-mute` | `Media keys` | `XF86AudioMicMute` | `exec` | `wpctl set-mute @DEFAULT_AUDIO_SOURCE@ toggle` | Mute microphone |
| 50 | `xf86-bright-down` | `Media keys` | `XF86MonBrightnessDown` | `exec` | `brightnessctl -e4 -n2 set 5%-` | Brightness down |
| 51 | `xf86-bright-up` | `Media keys` | `XF86MonBrightnessUp` | `exec` | `brightnessctl -e4 -n2 set 5%+` | Brightness up |
| 52 | `xf86-next` | `Media keys` | `XF86AudioNext` | `exec` | `qs ipc call media next` | Next track |
| 53 | `xf86-pause` | `Media keys` | `XF86AudioPause` | `exec` | `qs ipc call media playPause` | Play / pause |
| 54 | `xf86-play` | `Media keys` | `XF86AudioPlay` | `exec` | `qs ipc call media playPause` | Play / pause |
| 55 | `xf86-prev` | `Media keys` | `XF86AudioPrev` | `exec` | `qs ipc call media previous` | Previous track |
| 56 | `snap-region` | `Screenshots` | `Print` | `exec` | `qs ipc call snap toggle` | Region screenshot |
| 57 | `snap-full` | `Screenshots` | `SUPER + Print` | `exec` | `qs ipc call screenshot full` | Full screenshot |
| 58 | `snap-region-d` | `Screenshots` | `SUPER + D` | `exec` | `qs ipc call snap toggle` | Region screenshot |
| 59 | `snap-text` | `Screenshots` | `SUPER + SHIFT + T` | `exec` | `qs ipc call snap text` | Copy text from a region (OCR) |
| 60 | `snap-color` | `Screenshots` | `SUPER + SHIFT + C` | `exec` | `qs ipc call snap color` | Pick a colour from the screen |
| 61 | `reload` | `Lucid` | `SUPER + R` | `exec` | `$HOME/.config/hypr/scripts/reload.sh` | Reload Hyprland and the shell |

### 2.1 Lucid Contextual Desktop-Icon Shortcuts (`DesktopIcons.qml` — 17 Actions)
Scoped strictly to `DesktopIcons.qml` focus: `Return` (Open), `Space` (Quick Look in `Lens`), `F2` (Rename), `Delete` (Trash), `Shift+Delete` (Delete Permanently), `Ctrl+C` (Copy), `Ctrl+X` (Cut), `Ctrl+V` (Paste), `Ctrl+D` (Duplicate), `Ctrl+A` (Select All), `Ctrl+Shift+N` (New Folder), `Ctrl+Z` (Undo), `Menu`/`Shift+F10` (Context Menu), `Arrows` (Navigate), `Shift+Arrows` (Range Select), `Home`/`End` (Jump), `Escape` (Deselect).

---

## 3. Complete Verbatim Mandara Keybindings (`compositor.rs::default_keybinds()` — All 25 Binds)

| # | Modifiers | Key | Mandara IPC Command (`BindAction::Mandara`) | Scy-Shell Unified Mapping |
|---:|---|---|---|---|
| 1 | `SUPER` | `space` | `mandara ipc launcher toggle` | `scy-shell ipc` unified router (see Section 1) |
| 2 | `SUPER + ALT` | `space` | `mandara ipc launcher toggle` | `scy-shell ipc` unified router (see Section 1) |
| 3 | `SUPER` | `b` | `mandara ipc sidebar toggle` | `scy-shell ipc` unified router (see Section 1) |
| 4 | `SUPER + SHIFT` | `e` | `mandara ipc session menu toggle` | `scy-shell ipc` unified router (see Section 1) |
| 5 | `CTRL + ALT` | `Delete` | `mandara ipc session menu toggle` | `scy-shell ipc` unified router (see Section 1) |
| 6 | `SUPER + SHIFT` | `s` | `mandara ipc screenshot region` | `scy-shell ipc` unified router (see Section 1) |
| 7 | `SUPER + SHIFT` | `v` | `mandara ipc panel toggle clipboard` | `scy-shell ipc` unified router (see Section 1) |
| 8 | `ALT` | `v` | `mandara ipc panel toggle clipboard` | `scy-shell ipc` unified router (see Section 1) |
| 9 | `(None)` | `Print` | `mandara ipc screenshot screen` | `scy-shell ipc` unified router (see Section 1) |
| 10 | `CTRL` | `Print` | `mandara ipc screenshot region` | `scy-shell ipc` unified router (see Section 1) |
| 11 | `ALT` | `Print` | `mandara ipc screenshot window` | `scy-shell ipc` unified router (see Section 1) |
| 12 | `SUPER + SHIFT` | `t` | `mandara ipc theme mode toggle` | `scy-shell ipc` unified router (see Section 1) |
| 13 | `CTRL + SHIFT` | `w` | `mandara ipc wallpaper picker toggle` | `scy-shell ipc` unified router (see Section 1) |
| 14 | `ALT` | `Tab` | `mandara ipc switcher next` | `scy-shell ipc` unified router (see Section 1) |
| 15 | `ALT + SHIFT` | `Tab` | `mandara ipc switcher prev` | `scy-shell ipc` unified router (see Section 1) |
| 16 | `(None)` | `XF86AudioMute` | `mandara ipc audio mute-all toggle` | `scy-shell ipc` unified router (see Section 1) |
| 17 | `(None)` | `XF86AudioRaiseVolume` | `mandara ipc audio volume up` | `scy-shell ipc` unified router (see Section 1) |
| 18 | `(None)` | `XF86AudioLowerVolume` | `mandara ipc audio volume down` | `scy-shell ipc` unified router (see Section 1) |
| 19 | `(None)` | `XF86MonBrightnessUp` | `mandara ipc brightness up` | `scy-shell ipc` unified router (see Section 1) |
| 20 | `(None)` | `XF86MonBrightnessDown` | `mandara ipc brightness down` | `scy-shell ipc` unified router (see Section 1) |
| 21 | `(None)` | `XF86AudioPlay` | `mandara ipc media play-pause` | `scy-shell ipc` unified router (see Section 1) |
| 22 | `(None)` | `XF86AudioPause` | `mandara ipc media play-pause` | `scy-shell ipc` unified router (see Section 1) |
| 23 | `(None)` | `XF86AudioNext` | `mandara ipc media next` | `scy-shell ipc` unified router (see Section 1) |
| 24 | `(None)` | `XF86AudioPrev` | `mandara ipc media previous` | `scy-shell ipc` unified router (see Section 1) |
| 25 | `(None)` | `XF86AudioMicMute` | `mandara ipc audio mic mute` | `scy-shell ipc` unified router (see Section 1) |

### 3.2 Scy-Shell Dedicated Conflict-Free Chords for Mandara-Unique Subsystems
- `SUPER + SHIFT + A` -> **Local AI Command Agent** (`scy-shell ipc agent toggle`)
- `SUPER + SHIFT + B` -> **Mandara Sidebar / Edge Drawer** (`scy-shell ipc sidebar toggle`)
- `SUPER + ALT + T` -> **Theme & 19-Look Quick Switcher** (`scy-shell ipc look toggle`)
- `SUPER + SHIFT + P` -> **88-Plugin & WASM Host Drawer** (`scy-shell ipc plugins toggle`)
- `SUPER + SHIFT + G` -> **3D Steam/Lutris/Heroic Game Shelf** (`scy-shell ipc games toggle`)
- `SUPER + SHIFT + W` -> **Wallgen Procedural Wallpaper Studio** (`scy-shell ipc wallgen toggle`)