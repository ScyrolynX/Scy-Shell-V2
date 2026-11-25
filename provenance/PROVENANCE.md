# Scy-Shell Stage 0 — Upstream Source Provenance & Integrity Ledger

- **Audit Date:** 2026-11-24
- **Project:** Scy-Shell (Unified Lucid 2 + Mandara Wayland Desktop Shell)
- **Primary Target Platform:** CachyOS Linux (Arch-based) + Hyprland (0.55+ / 0.57+ Lua & Socket2)

---

## 1. Repository Layout & Isolation Verification

| Directory | Role | Git Branch / Ref | Commit SHA | Status |
|---|---|---|---|---|
| `upstream/lucid/` | Pristine read-only upstream clone of **Lucid 2** | `main` (`tag: v1.21.1`) | `15f13429bc59b4a97223bcfe5592735cb1eb92be` | **CLEAN / UNTOUCHED** |
| `upstream/mandara/` | Pristine read-only upstream clone of **Mandara** | `main` (1 AUR commit after `v0.38.2`) | `8a50e16af3a59cd8745df36e5656d825e5284641` | **CLEAN / UNTOUCHED** |
| `engines/lucid/` | Editable Lucid working tree for Scy-Shell adapter hooks | `scy-working` | `15f13429bc59b4a97223bcfe5592735cb1eb92be` | **CLEAN (Stage 0 Gate)** |
| `engines/mandara/` | Editable Mandara working tree for Scy-Shell adapter hooks | `scy-working` | `8a50e16af3a59cd8745df36e5656d825e5284641` | **CLEAN (Stage 0 Gate)** |
| `upstream/snapshots/` | Pinned immutable `git archive` source tarballs | `v1.21.1` / `8a50e16a` | Verified | **ARCHIVED** |
| `` | Unified Scy-Shell Core, Studio, Adapters, Docs & Provenance | — | — | **STAGE 0 COMPLETE** |

---

## 2. Upstream Repository Metadata

### 2.1 Lucid 2 (`Sn3akyy1/lucid`)
- **Upstream URL:** `https://github.com/Sn3akyy1/lucid`
- **Pinned Commit:** `15f13429bc59b4a97223bcfe5592735cb1eb92be`
- **Git Tree SHA:** Verified in `PROVENANCE.json`
- **Release Tag:** `v1.21.1` (`HEAD == tag v1.21.1`)
- **Submodules / Git LFS:** None (`.gitmodules` absent; binary wallpapers and fonts committed directly in Git)
- **Tracked File Count:** `920` tracked files (`1,291,144,574` bytes including `wallpapers/` collection; `8.74 MB` compressed code/font archive excluding `wallpapers/`)
- **SHA-256 Manifest:** `provenance/lucid-v1.21.1-sha256sums.txt`
- **Snapshot Tarball:** `upstream/snapshots/lucid-v1.21.1-core-no-wallpapers.tar.gz` (full 1.2 GB wallpapers remain intact in `sources/lucid-upstream/wallpapers/`)
- **Primary License:** **MIT License** (`Copyright (c) 2026 Sn3akyy1`, `LICENSE`)
- **Bundled Asset Licenses:**
  - `support/fonts/google-sans/` — Google Sans variable font (**SIL Open Font License 1.1**)
  - `support/fonts/jetbrains-mono/` — JetBrains Mono (**SIL Open Font License 1.1**)
  - `support/fonts/material-symbols/` — Material Symbols Rounded variable icon font (**Apache-2.0**)

### 2.2 Mandara (`theHamdiz/mandara`)
- **Upstream URL:** `https://github.com/theHamdiz/mandara`
- **Pinned Commit:** `8a50e16af3a59cd8745df36e5656d825e5284641` (`chore(aur): regenerate PKGBUILD checksums for v0.38.2`)
- **Release Tag:** `v0.38.2` (`f66e1303aba62cd1108d2c8aa1f9c6e2bc9dfb6d` — all 16 Rust crates are 100% byte-identical between `f66e1303` and `8a50e16a`)
- **Submodules / Git LFS:** None (`vendor/` crates committed directly in-tree)
- **Tracked File Count:** `2,788` tracked files (`156,043,284` bytes; `1,289` `.rs` files across `crates/` totaling `531,775` LOC)
- **SHA-256 Manifest:** `provenance/mandara-v0.38.2-sha256sums.txt`
- **Snapshot Tarball:** `upstream/snapshots/mandara-v0.38.2-8a50e16a.tar.gz` (`110,058,345` bytes)
- **Primary License:** **GNU General Public License v3.0 or later (`GPL-3.0-or-later`)** (`Copyright (C) 2026 Ahmad Hamdi (theHamdiz) and contributors`, `LICENSE` + `COPYRIGHT.md`)
- **Vendored / Bundled Asset Licenses (`COPYRIGHT.md`):**
  - `vendor/gpui` & `vendor/gpui_macros` — Forked from Zed Industries GPUI (**GPL-3.0-or-later** / Apache-2.0 upstream origins; patched in-tree for Wayland `wlr-layer-shell` & `ext-session-lock-v1`)
  - `vendor/wgpu-26.0.1`, `vendor/wgpu-core-26.0.1`, `vendor/wgpu-hal-26.0.6` — Patched wgpu stack (**MIT OR Apache-2.0**)
  - `vendor/uni-ocr-0.2.0` — Local OCR abstraction (**MIT OR Apache-2.0**)
  - `assets/fonts/` — Space Grotesk, Inter, Noto Sans Arabic, Cairo, JetBrains Mono (**SIL Open Font License 1.1**)
  - `assets/icons/` — Phosphor Icons (**MIT**)
  - `assets/sounds/` — Synthesized / CC0 sound pack
  - Optional runtime downloadable AI weights (`mandara-agent`): `google/functiongemma-270m-it` (Gemma Terms of Use — user-initiated opt-in download only, never bundled in binary packages) and `Qwen3-0.6B` (**Apache-2.0**).

---

## 3. Combined Scy-Shell Licensing Determination

1. **MIT (Lucid 2) + GPL-3.0-or-later (Mandara):** Under FSF and OSI compatibility rules, the MIT License is strictly upward-compatible with `GPL-3.0-or-later`.
2. **Combined Distribution License:** The unified **Scy-Shell** distribution, installer, and combined binaries are governed by **`GPL-3.0-or-later`**.
3. **Preserved Notices:**
   - All Lucid QML, Lua, Python, and shell files in `sources/lucid-working/` and packaged under Scy-Shell retain Sn3akyy1's original MIT copyright and permission notice verbatim.
   - All Mandara Rust crates and assets retain Ahmad Hamdi's `GPL-3.0-or-later` copyright header and `COPYRIGHT.md` ledger.
   - All bundled SIL OFL 1.1 and Apache-2.0 fonts/icons retain their standalone license files under `scy-shell/licenses/`.
   - Optional local LLM weights (`FunctionGemma-270M` / `Qwen3-0.6B`) are **never bundled** into redistributable archives; they remain strictly opt-in user downloads with explicit license disclosure in Scy-Shell Studio.
