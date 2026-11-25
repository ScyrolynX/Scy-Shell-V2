# Scy-Shell User & Operations Guide (CachyOS + Hyprland)

## 1. Installation & Profiles

Scy-Shell provides three installation profiles via `./install.sh`:

| Profile | Included Capabilities |
|---|---|
| `minimal` | Core `scy-daemon`, C11 `scy-shell-ipc`, Lucid M3 Bar/Dock/Launcher/QuickSettings/Lock, Dormant Mandara plugin/AI backend, Scy-Shell Studio |
| `balanced` *(default)* | Everything in `minimal` + 28-app SHA-256 theme sync, 13-style Wallgen studio, 89 built-in/WASM plugins |
| `full` | Everything in `balanced` + OCR (`tesseract`), recording (`wf-recorder`), external display DDC (`ddcutil`), KDE Connect, Lumen `FileChooser` portal, staged SDDM/greetd themes |

All installs support `--dry-run`, `--with-hypr`, `--restore-backup <dir>`, and `--uninstall`.

---

## 2. Unified Keybindings (Lucid-First Policy + Conflict-Free Mandara Chords)

All **61** original Lucid 2 shortcuts keep their exact chords (`SUPER + Space` Launcher, `SUPER + N` Control Centre, `SUPER + L` Lock, `SUPER + SHIFT + S` Scratchpad, `SUPER + SHIFT + T` LucidShot OCR, `SUPER + /` Cheat Sheet, etc.). Shared surfaces dispatch through `scy-shell-ipc` in **1.4 ms** so switching providers requires zero keybind edits.

Six conflict-free chords expose Mandara's unique capabilities:

| Chord | Action | Command |
|---|---|---|
| `SUPER + SHIFT + A` | Toggle Local AI Command Agent (`FunctionGemma` / `Qwen3`) | `scy-shell-ipc agent toggle` |
| `SUPER + SHIFT + B` | Toggle Mandara Sidebar / Edge Drawer | `scy-shell-ipc sidebar toggle` |
| `SUPER + ALT + T` | Open 20-Look Visual Identity Switcher | `scy-shell-ipc look picker` |
| `SUPER + SHIFT + P` | Open 89 Built-in & WASM Plugins Studio | `scy-shell-ipc plugins` |
| `SUPER + SHIFT + G` | Open 3D Steam / Lutris / Heroic Game Shelf | `scy-shell-ipc games` |
| `SUPER + SHIFT + W` | Open 13-Style Procedural Wallgen Studio | `scy-shell-ipc wallgen` |

---

## 3. CLI Reference (`scy-shell` & `scy-shell-ipc`)

```bash
# Inspect current provider & presentation routing
scy-shell status

# Switch individual shell surfaces without losing inactive settings
scy-shell provider bar mandara
scy-shell provider bar lucid
scy-shell provider desktop_widgets hybrid

# Separate visual presentation from functional backend
scy-shell presentation toasts lucid
scy-shell presentation primary_identity sea-glass
scy-shell presentation primary_identity scy-m3-expressive

# Search, read, or modify any of the 1,875 unified settings
scy-shell config search jellyAmount
scy-shell config set scy.providers.lucid.prefs.jellyAmount 0.8
scy-shell config set scy.providers.mandara.config.bar.height 40

# Generate procedural artwork & apply to active wallpaper engine
scy-shell wallgen aurora --seed "#7AA2F7"

# Run deterministic / local-LLM natural language command
scy-shell ai switch bar to lucid and lock screen to mandara

# Emit validated Hyprland configs or roll back a 15-second trial
scy-shell hypr emit
scy-shell hypr trial-revert

# Run CachyOS / Wayland / conflict diagnostics
scy-shell doctor
```
