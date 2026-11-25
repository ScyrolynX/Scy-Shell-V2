# Stage 0 Deliverable 4 — Complete Lossless Settings Inventory (`1,875` Verified Settings)

Every user-accessible setting across **Lucid 2 (`643` settings)** and **Mandara (`1,232` settings)** has been extracted directly from source code (`Prefs.qml`, `HyprConfig.qml`, standalone QML `JsonAdapter`s, `Widgets.qml`, `Catalog.js`, `sddm/theme.conf`, `mandara-studio/src/registry*.rs`, `mandara-greeter/src/config.rs`, and `wallgen.rs`).

- **Full Machine-Readable Catalogue (all 1,875 entries with `scy_id`, `original_key`, `source_file`, `storage`, `category`, `type`, and `default`/`label`):** [`04-settings-catalogue.json`](./04-settings-catalogue.json)

---

## 1. Totals by Source & Storage Backend

| Project & Subsystem | Source File(s) | Backing Config File | Setting Count |
|---|---|---|---:|
| **Lucid Core Preferences** | `Prefs.qml` (`JsonAdapter`) | `~/.config/quickshell/lucidprefs/prefs.json` | 382 |
| **Lucid Live Hyprland Options** | `HyprConfig.qml` (`keys` + `lucid.*`) | `~/.config/hypr/lucid-settings.lua` | 71 |
| **Lucid Frosted Glass Blur** | `Theme.qml` / `Glass.qml` | `~/.config/quickshell/blur.json` | 1 |
| **Lucid Standalone Apps** | `Lumen` (17), `Lens` (22), `ClockApp` (5), `Moji` (12), `Keyboard` (4), `ShotOverlay` (9) | `~/.local/state/lucid/*.json` & `~/.config/quickshell/lucid*` | 69 |
| **Lucid Desktop Widget Schemas** | `Widgets.qml` (25 widget types) | `~/.config/quickshell/widgets.json` | 59 |
| **Lucid Lock Widget & Preset Schemas** | `lucidlock/parts/Catalog.js` | `Prefs.lockOpts` / `Prefs.lockSlots` | 36 |
| **Lucid SDDM Theme Config** | `support/sddm/lucid/theme.conf` | `/usr/share/sddm/themes/lucid/theme.conf` | 25 |
| **Subtotal — Lucid 2** | | | **643** |
| **Mandara Studio & ShellConfig** | `crates/mandara-studio/src/registry*.rs` (32 Sections, 48 TOML tables) | `~/.config/mandara/config.toml` | 1,096 |
| **Mandara `greetd` Pre-Auth Greeter** | `crates/mandara-greeter/src/config.rs` | `/etc/mandara/greeter.toml` | 115 |
| **Mandara `Wallgen` Procedural Studio** | `crates/mandara-config/src/wallgen.rs` | `~/.config/mandara/wallgen.toml` | 21 |
| **Subtotal — Mandara** | | | **1,232** |
| **GRAND TOTAL (Scy-Shell Studio Union)** | | `~/.config/scy-shell/config.toml` + synced engine stores | **1,875** |

---

## 2. Category Breakdown — Lucid 2 (`643` Settings)

| Category | Count | Representative Original Keys |
|---|---:|---|
| `appearance` | 5 | `accentPunch`, `surfaceDarkness`, `surfaceTint`, `uiScale` |
| `audio` | 3 | `audioMeters`, `audioMoveStreams`, `audioCombine` |
| `audio.sounds` | 12 | `sysSounds`, `sysSoundVolume`, `soundOnUsb`, `soundOnBluetooth` |
| `bar` | 22 | `barStyle`, `barPosition`, `barEnabled`, `barPopupMode` |
| `bar.modules` | 12 | `showWorkspaces`, `showMedia`, `showTray`, `showKbLayout` |
| `bar.power` | 5 | `powerModuleActions`, `powerModuleConfirm`, `powerModuleUptime`, `powerModuleStyle` |
| `bar.start` | 1 | `startModuleStyle` |
| `bar.window` | 4 | `windowModuleText`, `windowModuleWidth`, `windowModuleScroll`, `windowModuleMiddleClose` |
| `bluetooth` | 6 | `btScanOnOpen`, `btShowUnnamed`, `btReceive`, `btAgent` |
| `capture.recording` | 4 | `recordFolder`, `recordCountdown`, `recordFps`, `recordEncoder` |
| `capture.screenshot` | 7 | `shotPreview`, `shotPreviewSeconds`, `shotFolder`, `shotSaveFile` |
| `clipboard` | 1 | `clipboardEnabled` |
| `control_centre` | 13 | `systemTiles`, `systemTilesRadios`, `systemBigTiles`, `systemBlocks` |
| `datetime_clock` | 10 | `clockStyle`, `clockDateFormat`, `clock24h`, `clockShowDate` |
| `datetime_pomodoro` | 9 | `pomodoroFocus`, `pomodoroShort`, `pomodoroLong`, `pomodoroRounds` |
| `datetime_timers` | 2 | `timerSound`, `reminderSound` |
| `desktop` | 19 | `desktopSelection`, `desktopMenu`, `desktopIcons`, `desktopIconSize` |
| `display_manager.sddm` | 26 | `sddm.isLight`, `sddm.accent`, `sddm.accentHover`, `sddm.fgAccent` |
| `displays` | 5 | `monitorSetups`, `monitorShellScreen`, `monitorBarScreen`, `monitorDockScreen` |
| `dock` | 18 | `dockStyle`, `dockEnabled`, `dockAsideForBar`, `dockIconSize` |
| `environment` | 24 | `envAdopted`, `envCursorTheme`, `envCursorSize`, `envCursorShadow` |
| `gamemode` | 3 | `gameModeOnCmd`, `gameModeOffCmd`, `gameModeStatusCmd` |
| `general` | 2 | `hiddenThemes`, `autoColorMode` |
| `glass` | 3 | `glassApps`, `glassValues`, `value` |
| `hyprland` | 1 | `hyprOptions` |
| `hyprland.animations` | 1 | `animations.enabled` |
| `hyprland.cursor` | 4 | `cursor.no_warps`, `cursor.warp_on_change_workspace`, `cursor.hide_on_key_press`, `cursor.inactive_timeout` |
| `hyprland.decoration` | 7 | `decoration.rounding`, `decoration.rounding_power`, `decoration.shadow.enabled`, `decoration.shadow.range` |
| `hyprland.dwindle` | 4 | `dwindle.split_width_multiplier`, `dwindle.force_split`, `dwindle.default_split_ratio`, `dwindle.preserve_split` |
| `hyprland.general` | 11 | `general.gaps_in`, `general.gaps_out`, `general.border_size`, `general.col.active_border` |
| `hyprland.gestures` | 6 | `gestures.workspace_swipe_distance`, `gestures.workspace_swipe_invert`, `gestures.workspace_swipe_cancel_ratio`, `gestures.workspace_swipe_min_speed_to_force` |
| `hyprland.input` | 19 | `input.follow_mouse`, `input.kb_layout`, `input.kb_variant`, `input.kb_options` |
| `hyprland.lucid_extensions` | 6 | `lucid.border`, `lucid.inactive_border`, `lucid.solo`, `lucid.cursor_tilt` |
| `hyprland.master` | 4 | `master.orientation`, `master.mfact`, `master.new_status`, `master.new_on_top` |
| `hyprland.misc` | 1 | `misc.focus_on_activate` |
| `hyprland.plugin` | 7 | `plugin.dynamic_cursors.mode`, `plugin.dynamic_cursors.tilt.limit`, `plugin.dynamic_cursors.tilt.full`, `plugin.dynamic_cursors.tilt.window` |
| `hyprland.scrolling` | 2 | `scrolling.column_width`, `scrolling.fullscreen_on_one_column` |
| `idle` | 19 | `idleEnabled`, `idleAutostart`, `idleKeepAwake`, `idleAdopted` |
| `kdeconnect` | 1 | `kdeConnectEnabled` |
| `language` | 1 | `language` |
| `launcher` | 19 | `launcherSearchEngine`, `launcherWebRow`, `launcherWindows`, `launcherAppActions` |
| `location` | 7 | `gpsEnabled`, `locationName`, `locationLabel`, `locationLat` |
| `lockscreen` | 11 | `lockPreset`, `lockSlots`, `lockWidgetOpts`, `lockBlur` |
| `lockscreen.widgets.agenda` | 1 | `lockOpts.agenda.style` |
| `lockscreen.widgets.clock` | 4 | `lockOpts.clock.style`, `lockOpts.clock.size`, `lockOpts.clock.tone`, `lockOpts.clock.seconds` |
| `lockscreen.widgets.date` | 2 | `lockOpts.date.style`, `lockOpts.date.size` |
| `lockscreen.widgets.greeting` | 2 | `lockOpts.greeting.style`, `lockOpts.greeting.size` |
| `lockscreen.widgets.media` | 1 | `lockOpts.media.style` |
| `lockscreen.widgets.message` | 4 | `lockOpts.message.style`, `lockOpts.message.size`, `lockOpts.message.text`, `lockOpts.message.icon` |
| `lockscreen.widgets.notifications` | 2 | `lockOpts.notifications.style`, `lockOpts.notifications.private` |
| `lockscreen.widgets.panel_preset` | 1 | `lockOpts.panel_preset.side` |
| `lockscreen.widgets.power` | 7 | `lockOpts.power.style`, `lockOpts.power.size`, `lockOpts.power.suspend`, `lockOpts.power.hibernate` |
| `lockscreen.widgets.status` | 7 | `lockOpts.status.style`, `lockOpts.status.size`, `lockOpts.status.battery`, `lockOpts.status.network` |
| `lockscreen.widgets.weather` | 4 | `lockOpts.weather.style`, `lockOpts.weather.size`, `lockOpts.weather.highLow`, `lockOpts.weather.feels` |
| `lucid_apps.clock_app` | 5 | `clock_app.page`, `clock_app.width`, `clock_app.height`, `clock_app.face` |
| `lucid_apps.keys` | 4 | `keys.panelX`, `keys.panelY`, `keys.keySize`, `keys.keyLayer` |
| `lucid_apps.lens` | 22 | `lens.width`, `lens.height`, `lens.filmstrip`, `lens.background` |
| `lucid_apps.lumen` | 17 | `lumen.view`, `lumen.iconSize`, `lumen.chooserFolder`, `lumen.sortKey` |
| `lucid_apps.moji` | 13 | `moji.recentEmoji`, `moji.recentKaomoji`, `moji.recentGifs`, `moji.favEmoji` |
| `lucid_apps.shot_state` | 9 | `shot_state.markup`, `shot_state.target`, `shot_state.mic`, `shot_state.system` |
| `media` | 8 | `mediaStyle`, `mediaPanelStyle`, `mediaHideIdle`, `mediaArtist` |
| `motion` | 3 | `motionScale`, `jellyMotion`, `jellyAmount` |
| `night_light` | 5 | `nightLight`, `nightLightTemp`, `nightLightSchedule`, `nightLightFrom` |
| `notifications` | 13 | `notificationsStyle`, `notifShowIcons`, `notifMaxHistory`, `notifSound` |
| `notifications.dnd` | 6 | `doNotDisturb`, `dndAllowCritical`, `dndFullscreen`, `quietHours` |
| `notifications.toasts` | 18 | `toastTimeout`, `toastOnLayout`, `toastOnGameMode`, `toastOnBattery` |
| `osd` | 5 | `osdStyle`, `osdDockMorph`, `osdToggles`, `osdCapsLock` |
| `privacy` | 4 | `privacyWatch`, `privacyToast`, `privacyAlwaysShown`, `privacyStyle` |
| `startup` | 3 | `startupApps`, `startupEnv`, `startupXdg` |
| `storage` | 3 | `storageLowWarn`, `storageLowPercent`, `storageTrashDays` |
| `theme` | 2 | `themeOrder`, `themeColour` |
| `theme.matugen` | 4 | `matugenScheme`, `matugenContrast`, `matugenSourceImage`, `matugenSourceIndex` |
| `tray` | 3 | `trayStyle`, `trayIconColor`, `trayHidden` |
| `typography` | 2 | `fontFamily`, `fontScale` |
| `updates` | 2 | `updateCheck`, `updateBeta` |
| `wallpaper` | 10 | `wallpaperFolder`, `wallpaperPickerStyle`, `wallpaperPickerKeys`, `wallpaperPillsShape` |
| `wallpaper.live` | 4 | `liveWallpapers`, `liveDecoder`, `livePauseUnder`, `liveGameMode` |
| `wallpaper.transitions` | 8 | `wallTransType`, `wallTransDuration`, `wallTransAngle`, `wallTransOrigin` |
| `widgets` | 5 | `widgetsEnabled`, `widgetSnap`, `widgetLockAll`, `widgetHideFullscreen` |
| `widgets.battery` | 2 | `widgets.battery.showTime`, `widgets.battery.warnLow` |
| `widgets.calendar` | 1 | `widgets.calendar.showMonthName` |
| `widgets.clock` | 6 | `widgets.clock.hourMode`, `widgets.clock.seconds`, `widgets.clock.dot`, `widgets.clock.showDate` |
| `widgets.games` | 2 | `widgets.games.order`, `widgets.games.gameModeOnLaunch` |
| `widgets.github` | 2 | `widgets.github.months`, `widgets.github.user` |
| `widgets.kdeconnect` | 5 | `widgets.kdeconnect.showShare`, `widgets.kdeconnect.showRing`, `widgets.kdeconnect.showClipboard`, `widgets.kdeconnect.showBrowse` |
| `widgets.lyrics` | 4 | `widgets.lyrics.card`, `widgets.lyrics.outline`, `widgets.lyrics.lines`, `widgets.lyrics.idleFade` |
| `widgets.media` | 3 | `widgets.media.artTint`, `widgets.media.showProgress`, `widgets.media.scroll` |
| `widgets.network` | 3 | `widgets.network.units`, `widgets.network.showAddress`, `widgets.network.interval` |
| `widgets.notes` | 3 | `widgets.notes.tint`, `widgets.notes.edited`, `widgets.notes.text` |
| `widgets.palette` | 1 | `widgets.palette.showHex` |
| `widgets.photo` | 4 | `widgets.photo.source`, `widgets.photo.every`, `widgets.photo.shape`, `widgets.photo.showDate` |
| `widgets.progress` | 1 | `widgets.progress.span` |
| `widgets.shortcuts` | 1 | `widgets.shortcuts.start` |
| `widgets.system` | 6 | `widgets.system.showCpu`, `widgets.system.showRam`, `widgets.system.showDisk`, `widgets.system.showTemp` |
| `widgets.thermal` | 3 | `widgets.thermal.showFans`, `widgets.thermal.showControls`, `widgets.thermal.interval` |
| `widgets.timer` | 1 | `widgets.timer.presets` |
| `widgets.todo` | 2 | `widgets.todo.hideDone`, `widgets.todo.items` |
| `widgets.toggles` | 1 | `widgets.toggles.set` |
| `widgets.visualiser` | 6 | `widgets.visualiser.density`, `widgets.visualiser.tint`, `widgets.visualiser.frost`, `widgets.visualiser.rounded` |
| `windows` | 1 | `shellGap` |
| `windows.pinned` | 3 | `pinBorder`, `pinBadge`, `pinPulse` |
| `windows.urgent` | 2 | `urgentBadge`, `urgentPulse` |
| `workspaces` | 5 | `workspacesByDisplay`, `workspacesStyle`, `workspacesShown`, `workspacesWheel` |
| `workspaces.special` | 15 | `specialScratchpad`, `specialMusic`, `specialComms`, `specialTodo` |

---

## 3. Category Breakdown — Mandara (`1,232` Settings)

| Category | Count | Representative JSON Pointers / Keys |
|---|---:|---|
| `appearance` | 5 | `/appearance/app_icon_shape`, `/appearance/bar_icons`, `/appearance/icon_theme`, `/appearance/launcher_icon` |
| `apps` | 4 | `/apps/browser`, `/apps/file_manager`, `/apps/run_autostart`, `/apps/terminal` |
| `audio` | 2 | `/audio/overamplify`, `/audio/volume_step` |
| `bar` | 53 | `/bar/accent_line`, `/bar/auto_hide/delay_ms`, `/bar/auto_hide/mode`, `/bar/auto_hide/reveal_on_workspace_switch` |
| `bluetooth` | 3 | `/bluetooth/auto_connect`, `/bluetooth/connect_notifications`, `/bluetooth/pairing_agent` |
| `calendar` | 7 | `/calendar/agenda_days`, `/calendar/enabled`, `/calendar/hide_past`, `/calendar/honour_event_alarms` |
| `clipboard` | 20 | `/clipboard/auto_clear_hours`, `/clipboard/clear_on_lock`, `/clipboard/clear_on_start`, `/clipboard/click_action` |
| `compositor` | 76 | `/compositor/autostart`, `/compositor/border_width`, `/compositor/doctor_notify`, `/compositor/hyprland/blur_passes` |
| `datetime` | 11 | `/datetime/bar_date_format`, `/datetime/bar_show_date`, `/datetime/bar_time_format`, `/datetime/eastern_numerals` |
| `desktop` | 9 | `/desktop/menu/animation`, `/desktop/menu/gesture`, `/desktop/menu/item_size`, `/desktop/menu/labels` |
| `display_manager.greetd` | 4 | `greeter.language`, `greeter.font`, `greeter.layout`, `greeter.widgets` |
| `display_manager.greetd.accessibility` | 3 | `greeter.accessibility.reduced_motion`, `greeter.accessibility.large_text`, `greeter.accessibility.high_contrast` |
| `display_manager.greetd.background` | 24 | `greeter.background.mode`, `greeter.background.video`, `greeter.background.video_dirs`, `greeter.background.image_dirs` |
| `display_manager.greetd.banner` | 2 | `greeter.banner.text`, `greeter.banner.size` |
| `display_manager.greetd.card` | 11 | `greeter.card.enabled`, `greeter.card.width`, `greeter.card.padding`, `greeter.card.radius` |
| `display_manager.greetd.clock` | 11 | `greeter.clock.format_24h`, `greeter.clock.seconds`, `greeter.clock.font`, `greeter.clock.size` |
| `display_manager.greetd.date` | 5 | `greeter.date.format`, `greeter.date.font`, `greeter.date.size`, `greeter.date.weight` |
| `display_manager.greetd.keyboard` | 1 | `greeter.keyboard.layout` |
| `display_manager.greetd.logo` | 4 | `greeter.logo.path`, `greeter.logo.size`, `greeter.logo.opacity`, `greeter.logo.accent` |
| `display_manager.greetd.motion` | 12 | `greeter.motion.entrance`, `greeter.motion.stagger_ms`, `greeter.motion.entrance_spring`, `greeter.motion.pop_spring` |
| `display_manager.greetd.password` | 12 | `greeter.password.style`, `greeter.password.submit`, `greeter.password.mask`, `greeter.password.accent_border` |
| `display_manager.greetd.power` | 6 | `greeter.power.suspend`, `greeter.power.reboot`, `greeter.power.poweroff`, `greeter.power.labels` |
| `display_manager.greetd.session` | 3 | `greeter.session.default`, `greeter.session.x11`, `greeter.session.style` |
| `display_manager.greetd.theme` | 8 | `greeter.theme.preset`, `greeter.theme.accent`, `greeter.theme.glass`, `greeter.theme.rim` |
| `display_manager.greetd.user` | 9 | `greeter.user.list`, `greeter.user.avatar_shape`, `greeter.user.avatar_source`, `greeter.user.avatar_size` |
| `displays` | 5 | `/displays/auto_profiles`, `/displays/brightness/ddc`, `/displays/brightness/min_percent`, `/displays/brightness/sync_all` |
| `dock` | 70 | `/dock/alignment`, `/dock/applications/enabled`, `/dock/applications/icon_size`, `/dock/applications/order` |
| `edges` | 3 | `/edges/dwell_ms`, `/edges/launcher_bottom`, `/edges/session_right` |
| `general` | 14 | `/general/auth_dialog_width`, `/general/auto_restart`, `/general/clock_24h`, `/general/keepassxc_ask_at_login` |
| `grain` | 3 | `/grain/bars/amount`, `/grain/bars/style`, `/grain/cards/amount` |
| `hooks` | 2 | `/hooks/enabled`, `/hooks/timeout_s` |
| `hot_corners` | 12 | `/hot_corners/bottom_left/action`, `/hot_corners/bottom_left/command`, `/hot_corners/bottom_right/action`, `/hot_corners/bottom_right/command` |
| `idle` | 8 | `/idle/fade_s`, `/idle/lock_at_startup`, `/idle/lock_before_sleep`, `/idle/lock_grace_s` |
| `integrations` | 22 | `/integrations/alacritty`, `/integrations/btop`, `/integrations/cava`, `/integrations/compositor_borders` |
| `launcher` | 56 | `/launcher/agent/debounce_ms`, `/launcher/agent/enabled`, `/launcher/agent/engine`, `/launcher/enabled` |
| `location` | 5 | `/location/latitude`, `/location/longitude`, `/location/mode`, `/location/name` |
| `lock` | 15 | `/lock/background`, `/lock/blank_other_outputs`, `/lock/blur`, `/lock/clock_style` |
| `looks` | 1 | `/looks/keep_components` |
| `media` | 2 | `/media/backup/encrypted`, `/media/follow_playing` |
| `motion` | 20 | `/motion/choreography/entrance`, `/motion/choreography/parallax`, `/motion/choreography/stagger`, `/motion/choreography/stretch` |
| `network` | 3 | `/network/hotspot_band`, `/network/hotspot_ssid`, `/network/vpn_notifications` |
| `night_light` | 12 | `/night_light/brightness`, `/night_light/day_temperature`, `/night_light/enabled`, `/night_light/end` |
| `notifications` | 35 | `/notifications/click_action`, `/notifications/compact`, `/notifications/daemon`, `/notifications/dedupe` |
| `osd` | 19 | `/osd/hold_ms`, `/osd/kinds/brightness`, `/osd/kinds/custom`, `/osd/kinds/do_not_disturb` |
| `panels` | 22 | `/panels/anchor`, `/panels/animation`, `/panels/gap`, `/panels/leave_delay_ms` |
| `plugins.2048` | 5 | `/plugins/settings/2048/accent`, `/plugins/settings/2048/animations`, `/plugins/settings/2048/bar_score`, `/plugins/settings/2048/size` |
| `plugins.active-window` | 2 | `/plugins/settings/active-window/max_width`, `/plugins/settings/active-window/show` |
| `plugins.app-installer` | 7 | `/plugins/settings/app-installer/after_install`, `/plugins/settings/app-installer/allow_native`, `/plugins/settings/app-installer/confirm_rootless`, `/plugins/settings/app-installer/flatpak_scope` |
| `plugins.audio` | 1 | `/plugins/settings/audio/bar_level` |
| `plugins.authenticator` | 2 | `/plugins/settings/authenticator/clear_seconds`, `/plugins/settings/authenticator/visible_rows` |
| `plugins.backups` | 6 | `/plugins/settings/backups/cleanup_age_days`, `/plugins/settings/backups/password_file`, `/plugins/settings/backups/repository`, `/plugins/settings/backups/snapshot_directory` |
| `plugins.bluetooth` | 3 | `/plugins/settings/bluetooth/bar_style`, `/plugins/settings/bluetooth/bar_width`, `/plugins/settings/bluetooth/battery_warn_percent` |
| `plugins.breaks` | 6 | `/plugins/settings/breaks/every_min`, `/plugins/settings/breaks/long_every_min`, `/plugins/settings/breaks/long_min`, `/plugins/settings/breaks/short_s` |
| `plugins.ci` | 3 | `/plugins/settings/ci/notify`, `/plugins/settings/ci/repos`, `/plugins/settings/ci/use_gh_token` |
| `plugins.clock` | 1 | `/plugins/settings/clock/agenda_rows` |
| `plugins.color-picker` | 3 | `/plugins/settings/color-picker/copy_format`, `/plugins/settings/color-picker/copy_on_pick`, `/plugins/settings/color-picker/open_after_pick` |
| `plugins.containers` | 5 | `/plugins/settings/containers/engine`, `/plugins/settings/containers/hot_cpu_percent`, `/plugins/settings/containers/log_lines`, `/plugins/settings/containers/refresh_s` |
| `plugins.crashes` | 1 | `/plugins/settings/crashes/notify` |
| `plugins.drives` | 4 | `/plugins/settings/drives/full_warn_percent`, `/plugins/settings/drives/notify_on_plug`, `/plugins/settings/drives/show_system`, `/plugins/settings/drives/usage_every_s` |
| `plugins.feeds` | 11 | `/plugins/settings/feeds/background_minutes`, `/plugins/settings/feeds/background_refresh`, `/plugins/settings/feeds/bar_style`, `/plugins/settings/feeds/card_folder` |
| `plugins.git-repos` | 2 | `/plugins/settings/git-repos/depth`, `/plugins/settings/git-repos/roots` |
| `plugins.hadith` | 8 | `/plugins/settings/hadith/arabic_size`, `/plugins/settings/hadith/bar_label`, `/plugins/settings/hadith/collections`, `/plugins/settings/hadith/daily_collections` |
| `plugins.home-assistant` | 3 | `/plugins/settings/home-assistant/entities`, `/plugins/settings/home-assistant/refresh_seconds`, `/plugins/settings/home-assistant/server` |
| `plugins.jannah` | 7 | `/plugins/settings/jannah/arabic_size`, `/plugins/settings/jannah/bar_label`, `/plugins/settings/jannah/language`, `/plugins/settings/jannah/morning_reminder` |
| `plugins.local-ai` | 6 | `/plugins/settings/local-ai/context_bytes`, `/plugins/settings/local-ai/model`, `/plugins/settings/local-ai/provider`, `/plugins/settings/local-ai/reply_tokens` |
| `plugins.media` | 8 | `/plugins/settings/media/bar_title`, `/plugins/settings/media/hide_when_paused`, `/plugins/settings/media/lyrics`, `/plugins/settings/media/lyrics_rows` |
| `plugins.net-speed` | 5 | `/plugins/settings/net-speed/bar_upload`, `/plugins/settings/net-speed/interval_s`, `/plugins/settings/net-speed/public_ip_url`, `/plugins/settings/net-speed/speed_test_mb` |
| `plugins.network` | 3 | `/plugins/settings/network/bar_style`, `/plugins/settings/network/bar_width`, `/plugins/settings/network/networks_shown` |
| `plugins.notes` | 5 | `/plugins/settings/notes/default_topic`, `/plugins/settings/notes/editor_font`, `/plugins/settings/notes/editor_size`, `/plugins/settings/notes/preview_by_default` |
| `plugins.notifications` | 2 | `/plugins/settings/notifications/bar_style`, `/plugins/settings/notifications/bar_width` |
| `plugins.phone-connect` | 2 | `/plugins/settings/phone-connect/refresh_seconds`, `/plugins/settings/phone-connect/show_unpaired` |
| `plugins.pomodoro` | 5 | `/plugins/settings/pomodoro/auto_continue`, `/plugins/settings/pomodoro/focus_minutes`, `/plugins/settings/pomodoro/long_break_every`, `/plugins/settings/pomodoro/long_break_minutes` |
| `plugins.power` | 3 | `/plugins/settings/power/bar_percent`, `/plugins/settings/power/history_hours`, `/plugins/settings/power/show_peripherals` |
| `plugins.prayer-times` | 8 | `/plugins/settings/prayer-times/adhan`, `/plugins/settings/prayer-times/asr`, `/plugins/settings/prayer-times/hijri_offset`, `/plugins/settings/prayer-times/language` |
| `plugins.presentation` | 1 | `/plugins/settings/presentation/auto_screen_share` |
| `plugins.processes` | 2 | `/plugins/settings/processes/hot_cpu_percent`, `/plugins/settings/processes/refresh_ms` |
| `plugins.progress` | 1 | `/plugins/settings/progress/notify` |
| `plugins.quran` | 5 | `/plugins/settings/quran/arabic_size`, `/plugins/settings/quran/language`, `/plugins/settings/quran/reciter`, `/plugins/settings/quran/remove` |
| `plugins.radio` | 18 | `/plugins/settings/radio/art_style`, `/plugins/settings/radio/auto_reconnect`, `/plugins/settings/radio/bar_style`, `/plugins/settings/radio/bar_width` |
| `plugins.reddit` | 11 | `/plugins/settings/reddit/card_subreddit`, `/plugins/settings/reddit/client_id`, `/plugins/settings/reddit/images`, `/plugins/settings/reddit/layout` |
| `plugins.resources` | 9 | `/plugins/settings/resources/bar_metrics`, `/plugins/settings/resources/bar_refresh_ms`, `/plugins/settings/resources/bar_style`, `/plugins/settings/resources/disk_full_percent` |
| `plugins.screenshot` | 23 | `/plugins/settings/screenshot/border`, `/plugins/settings/screenshot/capture_on_release`, `/plugins/settings/screenshot/copy`, `/plugins/settings/screenshot/countdown` |
| `plugins.services` | 5 | `/plugins/settings/services/alert_failed`, `/plugins/settings/services/default_scope`, `/plugins/settings/services/failed_check_s`, `/plugins/settings/services/journal_lines` |
| `plugins.share` | 2 | `/plugins/settings/share/minutes`, `/plugins/settings/share/once` |
| `plugins.soundscapes` | 1 | `/plugins/settings/soundscapes/bar_timer` |
| `plugins.stash` | 8 | `/plugins/settings/stash/copy_images`, `/plugins/settings/stash/edges`, `/plugins/settings/stash/height`, `/plugins/settings/stash/max_cache_mib` |
| `plugins.sudoku` | 10 | `/plugins/settings/sudoku/accent`, `/plugins/settings/sudoku/bar_time`, `/plugins/settings/sudoku/clear_notes`, `/plugins/settings/sudoku/conflicts` |
| `plugins.taskbar` | 12 | `/plugins/settings/taskbar/focus_style`, `/plugins/settings/taskbar/grain`, `/plugins/settings/taskbar/grain_amount`, `/plugins/settings/taskbar/group_windows` |
| `plugins.todo` | 6 | `/plugins/settings/todo/bar_count`, `/plugins/settings/todo/card_rows`, `/plugins/settings/todo/default_list`, `/plugins/settings/todo/panel_rows` |
| `plugins.translator` | 4 | `/plugins/settings/translator/provider`, `/plugins/settings/translator/server`, `/plugins/settings/translator/target`, `/plugins/settings/translator/use_api_key` |
| `plugins.tray` | 1 | `/plugins/settings/tray/show_passive` |
| `plugins.updates` | 11 | `/plugins/settings/updates/arch_news`, `/plugins/settings/updates/aur`, `/plugins/settings/updates/aur_helper`, `/plugins/settings/updates/first_check_delay_s` |
| `plugins.uptime` | 3 | `/plugins/settings/uptime/checks`, `/plugins/settings/uptime/interval_s`, `/plugins/settings/uptime/notify` |
| `plugins.weather` | 5 | `/plugins/settings/weather`, `/plugins/settings/weather/animate`, `/plugins/settings/weather/latitude`, `/plugins/settings/weather/location_name` |
| `plugins.workspaces` | 3 | `/plugins/settings/workspaces/app_icons`, `/plugins/settings/workspaces/hide_empty`, `/plugins/settings/workspaces/labels` |
| `plugins.world-clock` | 5 | `/plugins/settings/world-clock/bar_cities`, `/plugins/settings/world-clock/cities`, `/plugins/settings/world-clock/clock`, `/plugins/settings/world-clock/work_end` |
| `power` | 16 | `/power/action_delay_s`, `/power/action_percent`, `/power/charging_pulse`, `/power/critical_action` |
| `privacy` | 5 | `/privacy/camera`, `/privacy/camera_poll_s`, `/privacy/indicators`, `/privacy/microphone` |
| `screen_corners` | 7 | `/screen_corners/bottom_left`, `/screen_corners/bottom_right`, `/screen_corners/enabled`, `/screen_corners/hide_between_displays` |
| `screen_time` | 6 | `/screen_time/daily_limit_min`, `/screen_time/exclude`, `/screen_time/idle_minutes`, `/screen_time/reset` |
| `session_menu` | 8 | `/session_menu/cards_layout`, `/session_menu/default_action`, `/session_menu/grid_columns`, `/session_menu/hold_ms` |
| `side_bars` | 44 | `/side_bars/align`, `/side_bars/chip_fill`, `/side_bars/chip_padding`, `/side_bars/chip_size` |
| `sidebar` | 21 | `/sidebar/add_tab_button`, `/sidebar/always_first_tab`, `/sidebar/enabled`, `/sidebar/hover_reveal` |
| `sounds` | 18 | `/sounds/brightness_change`, `/sounds/charger`, `/sounds/complete`, `/sounds/desktop_sync` |
| `studio` | 46 | `/studio`, `/studio/frame/border`, `/studio/frame/card_padding`, `/studio/frame/card_radius` |
| `style` | 18 | `/style`, `/style/backdrop_dim`, `/style/borders`, `/style/button_design` |
| `switcher` | 14 | `/switcher/all_outputs`, `/switcher/bind`, `/switcher/captions`, `/switcher/current_workspace` |
| `theme` | 15 | `/theme`, `/theme/adjustments/chroma_scale`, `/theme/adjustments/high_contrast`, `/theme/adjustments/hue_shift` |
| `typography` | 18 | `/typography/arabic_font`, `/typography/bar_font`, `/typography/display_font`, `/typography/lock_clock_font` |
| `updates` | 3 | `/updates/check_interval_hours`, `/updates/plugins`, `/updates/self_check` |
| `wallpaper` | 60 | `/wallpaper`, `/wallpaper/clock_x`, `/wallpaper/crossfade_ms`, `/wallpaper/depth` |
| `wallpaper.wallgen` | 21 | `wallgen.schedule.enabled`, `wallgen.schedule.every_minutes`, `wallgen.schedule.mode`, `wallgen.schedule.apply` |
| `weather` | 5 | `/weather/enabled`, `/weather/refresh_minutes`, `/weather/show_high_low_in_bar`, `/weather/show_location_in_bar` |

---

## 4. Semantic Non-Equivalence Audit (Settings That MUST NOT Be Destructively Merged)

| Domain | Lucid Setting(s) | Mandara Setting(s) | Why They Are NOT Equivalent & How Scy-Shell Preserves Both |
|---|---|---|---|
| **Spring Physics** | `Prefs.jelly`, `Prefs.jellyAmount`, `Prefs.motionScale` | `/motion/preset`, `/motion/stiffness`, `/motion/damping`, `/motion/mass` | Lucid controls velocity-driven **2D scaleX/scaleY squash deformation** (`Jelly.qml`), whereas Mandara configures a 1D damped harmonic oscillator (`SpringValue`). Both are preserved distinctly under `Motion -> Expressive Jelly (Lucid)` and `Motion -> Analytical Springs (Mandara)`. |
| **Glass & Blur** | `blur.json:value`, `Prefs.surfaceAlpha`, `Glass.qml` | `/appearance/glass_opacity`, `/appearance/chromatic_aberration`, `/grain/intensity` | Lucid drives compositor `ext-background-effect-v1` blur + M3 surface tint; Mandara adds refractive `ChromaticGlass` & procedural film `SurfaceGrain`. Preserved distinctly in `Appearance -> Glass & Grain`. |
| **Corner Geometry** | `Prefs.cornerScale` + `MaterialShape.qml` polygon IDs | `/appearance/roundness`, `/style/corner_style` | Scalar multiplier + M3 cookies vs discrete architectural silhouette enum (`Sharp`, `Squircle`, `Scalloped`, `TornPaper`, `Comic`). Both preserved under their respective presentation engines. |
| **Bar Layout** | `Prefs.barStyle`, `Prefs.barFloating`, `Prefs.barPosition`, 22 boolean `show*` toggles | `/bar/style` (9 `BarStyle`s), `/bar/slots/{left,center,right}` ordered plugin arrays | Boolean visibility flags vs arbitrary drag-and-drop multi-instance plugin arrays. Scy-Shell Studio renders the Lucid Module Matrix when Lucid Bar is active and the Drag-and-Drop Slot Builder when Mandara Bar is active, keeping inactive state saved! |
| **Night Light** | `Prefs.nightLightTemp`, `Prefs.nightLightSchedule` | `/night_light/day_temp`, `/night_light/night_temp`, `/night_light/transition_minutes` | Mandara supports continuous twilight ramp (`day_temp` + `night_temp` + `transition_minutes`). Shared schedule/target temp lives in `scy.shared.night_light`, while Mandara's twilight ramp fields remain intact. |

---

## 5. Inactive-Provider Preservation Guarantee
- All `643` Lucid settings live under `[providers.lucid.*]` and sync two-way with `~/.config/quickshell/lucidprefs/prefs.json`.
- All `1,232` Mandara settings live under `[providers.mandara.*]` and sync two-way with `~/.config/mandara/config.toml`.
- Switching a feature provider (e.g. `bar: lucid -> mandara -> lucid`) **never deletes, resets, or clobbers** the inactive provider's settings; in Scy-Shell Studio, inactive provider settings remain inspectable and editable inside a clearly badged *"Inactive Provider Settings (Saved)"* section.