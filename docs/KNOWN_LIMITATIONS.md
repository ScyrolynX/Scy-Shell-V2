# Known Limitations & Platform Notes

Scy-Shell `v2.0.0` prioritizes honesty and predictable behavior over fake toggles. Below are the known platform boundaries:

1. **Wayland & Hyprland `0.57+` Requirement**:
   - Scy-Shell uses `wlr-layer-shell-unstable-v1`, `ext-session-lock-v1`, and Hyprland `0.57+` IPC/v2 `match:` rules. X11 sessions and older Hyprland (`< 0.53`) rule parsers are not targeted.
2. **System Display Manager Root Permissions (`Section 12 Login Experience`)**:
   - Regular user sessions cannot write directly to `/etc/sddm.conf.d/` or `/etc/greetd/` without privilege escalation. Scy-Shell safely stages validated configs under `~/.local/state/scy-shell/{staged-sddm-theme.conf,staged-greeter.toml}` and `~/.config/scy-shell/login-greeter.json`, providing the exact one-line `sudo install` helper when you choose to apply system-wide greeter changes.
3. **Mandara Full Rust Binary Compilation Memory**:
   - Compiling the full `mandara` Rust workspace from source (`gpui` + `wasmtime` + `tract-core` ONNX) requires `>= 4 GiB` of available RAM + swap (`rustc` + fat LTO). On CachyOS desktops (`8–64 GiB` RAM) this builds cleanly; on constrained `< 2 GiB` containers, pass `--skip-engine-build` to `./install.sh` or install a prebuilt binary.
4. **Hardware-Dependent Controls**:
   - External monitor brightness requires a monitor supporting DDC/CI and `ddcutil` (`i2c-dev` permissions).
   - Battery efficiency telemetry and charge thresholds only activate when `/sys/class/power_supply/BAT*` is present.
   - Screen OCR requires `tesseract` and language data (`tesseract-data-eng`); screen recording requires `wf-recorder`.
5. **NVIDIA Proprietary Driver Notes**:
   - On NVIDIA GPUs under Hyprland `0.57+`, ensure `nvidia_drm.modeset=1` is enabled. If heavy multi-pass Dual-Kawase blur (`blur_strength >= 5`) increases frame times at 4K, switch Scy Intelligent Performance (`Section 10`) to `Balanced` or `Performance`.
