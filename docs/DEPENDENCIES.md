# Dependencies Guide (CachyOS & Arch Linux)

Scy-Shell is built for **CachyOS Linux** + **Hyprland `0.57+`** + **Quickshell** + **Zsh**. It does **not** require `fish`.

---

## 1. Core Runtime Dependencies (Required)

| Package | Role in Scy-Shell |
|---|---|
| `hyprland` (`>= 0.57.0`) | Wayland compositor (`layerrule` / `windowrule` v2 `match:` syntax, IPC socket, workspaces) |
| `quickshell` | Qt6 Wayland layer-shell QML runtime hosting Scy-Shell primary surfaces & Unified Studio |
| `qt6-declarative`, `qt6-svg`, `qt6-multimedia` | QML scenegraph, vector icons, shaders, and audio feedback |
| `python` (`>= 3.11`) | `scy-daemon`, `scy-shell` CLI, 2,026-setting persistence engine, ledger reconciliation |
| `awww` (or `swww`) & `matugen` | Smooth wallpaper transitions and Material 3 / OKLCH dynamic palette extraction |
| `wl-clipboard` & `cliphist` | Wayland clipboard management and searchable clipboard history |
| `xdg-desktop-portal-hyprland` & `xdg-desktop-portal-gtk` | Screen sharing, file pickers, and dark/light color-scheme portal broadcasting |
| `pipewire`, `wireplumber` | Audio routing, volume OSD, and Control Center mixer (`wpctl`) |
| `networkmanager`, `bluez` | Wi-Fi / Ethernet (`nmcli`) and Bluetooth (`bluetoothctl`) Control Center integration |

---

## 2. Build Dependencies (For Local Compilation)

| Package | Role |
|---|---|
| `gcc`, `make` | Compiles ultra-fast C11 Unix-socket client `bin/scy-shell-ipc` (`< 2 ms` keybind dispatch) |
| `rust`, `cargo`, `clang`, `pkgconf`, `wayland-protocols` | Compiles bundled Mandara Rust GPUI companion (`mandara`, `wallgen`, `mandara-greeter`) |

---

## 3. Optional Feature Dependencies

| Package | Feature Unlocked |
|---|---|
| `zsh` | Interactive tab-completion via `_scy-shell` (`packaging/zsh/_scy-shell`) |
| `tesseract` (`+ tesseract-data-eng`) | One-click OCR text extraction in region screen captures (Section `13`) |
| `wf-recorder` | Hardware-accelerated MP4/GIF screen recording (Section `13`) |
| `ddcutil` | External monitor hardware brightness control over DDC/CI (Section `09` / `10`) |
| `kdeconnect` | Phone notifications, battery sync, clipboard & file sharing (Section `09` / `10`) |
| `power-profiles-daemon` | System ACPI power profile switching alongside Scy Intelligent Performance |
| `sddm` or `greetd` | Optional Section `12` pre-session login greeter styling (system auth remains untouched if omitted) |
