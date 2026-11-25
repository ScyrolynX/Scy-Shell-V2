//! Scy-Shell Unified Core exclusive-resource & dormant-surface gates.
//!
//! When `managed_by_scy_shell` is `false` (default when running Mandara
//! standalone), every `*_enabled()` helper returns `true`, preserving 100%
//! original Mandara behavior. Under Scy-Shell supervision, `scy-daemon`
//! populates `[scy_gates]` in `config.toml` so exclusive D-Bus/Wayland
//! claims and GPU swapchains never collide with active Lucid 2 providers.

use serde::{Deserialize, Serialize};

fn default_true() -> bool { true }
fn default_lucid() -> String { "lucid".into() }

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(default)]
pub struct ScyGatesConfig {
    pub managed_by_scy_shell: bool,
    #[serde(default = "default_true")]
    pub owns_notifications: bool,
    #[serde(default = "default_true")]
    pub owns_polkit: bool,
    #[serde(default = "default_true")]
    pub owns_lock: bool,
    #[serde(default = "default_true")]
    pub owns_night_light: bool,
    #[serde(default = "default_true")]
    pub owns_bt_agent: bool,
    #[serde(default = "default_true")]
    pub owns_idle: bool,
    #[serde(default = "default_true")]
    pub owns_clipboard: bool,
    #[serde(default = "default_true")]
    pub owns_wallpaper: bool,
    #[serde(default = "default_lucid")]
    pub bar_mode: String,
    #[serde(default = "default_lucid")]
    pub dock_mode: String,
    #[serde(default = "default_lucid")]
    pub launcher_mode: String,
    #[serde(default = "default_lucid")]
    pub desktop_widgets_mode: String,
    #[serde(default = "default_lucid")]
    pub toast_renderer: String,
    #[serde(default = "default_lucid")]
    pub osd_renderer: String,
}

impl Default for ScyGatesConfig {
    fn default() -> Self {
        Self {
            managed_by_scy_shell: false,
            owns_notifications: true,
            owns_polkit: true,
            owns_lock: true,
            owns_night_light: true,
            owns_bt_agent: true,
            owns_idle: true,
            owns_clipboard: true,
            owns_wallpaper: true,
            bar_mode: "mandara".into(),
            dock_mode: "mandara".into(),
            launcher_mode: "mandara".into(),
            desktop_widgets_mode: "mandara".into(),
            toast_renderer: "mandara".into(),
            osd_renderer: "mandara".into(),
        }
    }
}

impl ScyGatesConfig {
    pub fn notifications_enabled(&self) -> bool {
        !self.managed_by_scy_shell || self.owns_notifications
    }
    pub fn polkit_enabled(&self) -> bool {
        !self.managed_by_scy_shell || self.owns_polkit
    }
    pub fn night_light_enabled(&self) -> bool {
        !self.managed_by_scy_shell || self.owns_night_light
    }
    pub fn clipboard_enabled(&self) -> bool {
        !self.managed_by_scy_shell || self.owns_clipboard
    }
    pub fn wallpaper_enabled(&self) -> bool {
        !self.managed_by_scy_shell || self.owns_wallpaper
    }
    pub fn toasts_enabled(&self) -> bool {
        !self.managed_by_scy_shell || self.toast_renderer == "mandara"
    }
    pub fn osd_enabled(&self) -> bool {
        !self.managed_by_scy_shell || self.osd_renderer == "mandara"
    }
    /// Dormant Zero-Swapchain check: returns false when Lucid owns all persistent
    /// layer surfaces, avoiding idle wgpu swapchain allocations until needed.
    pub fn needs_shell_surface(&self) -> bool {
        if !self.managed_by_scy_shell {
            return true;
        }
        self.bar_mode != "lucid"
            || self.dock_mode == "mandara"
            || self.launcher_mode == "mandara"
            || self.desktop_widgets_mode != "lucid"
            || self.toast_renderer == "mandara"
            || self.osd_renderer == "mandara"
    }
}
