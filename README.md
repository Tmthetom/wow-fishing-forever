# WoW Fishing Forever — Windows fork

A Windows fork of [rsamf/wow-fishing-forever](https://github.com/rsamf/wow-fishing-forever), a World of Warcraft fishing bot that detects the bobber icon and listens for a splash. Licensed under [MIT](LICENSE).

## What this fork changes

- **Local Windows launcher:** `RiverDesk.cmd` runs the source code using a local Python installation. Each launch generates a name such as `River-a31f72c084bd` for the window and its `.exe` process. Keep using the existing River Desk shortcut.
- **Local setup:** settings and logs stay in `.local/state/`; Python and dependencies also stay inside the project folder. Machine-specific files are excluded from Git. This installation is not yet a ready-to-share portable package.
- **Practical setup instructions:** Czech keyboard bindings, calibration, and window placement based on use on this PC.

## Install and launch

Clone this fork and follow [AGENTS.md](AGENTS.md), or ask Codex: “Read AGENTS.md and set up this project on this PC.” Open `RiverDesk.cmd` to launch the app. Run `.\RiverDesk.cmd doctor` from PowerShell for diagnostics; missing game warnings are expected when WoW is closed.

The launcher keeps a small helper process (`pythonw.exe`, or `RiverDesk.exe` with the existing taskbar shortcut) open until the GUI exits, then removes the temporary named executable. Settings and logs stay in the same location. If startup fails, check `.local/state/log/launcher-error.log`. Direct CLI launches keep the standard window title.

## Sharing with another PC (planned option)

When a distributable build is needed, prepare a **portable Windows x64 ZIP** containing the app, Python, its dependencies, a launcher, and a clean default configuration. The intended workflow is **extract and launch**, with no separate Python installation or dependency download on the recipient's PC. Keep settings and logs inside the extracted folder and preserve the randomized launch names.

**This package has not been built or tested yet.** The GitHub source ZIP is not that package. Do not simply ZIP the current installation: its virtual environment and shortcuts can contain paths specific to this PC. Build from a selected commit, include the license notices, exclude personal logs and local state, and verify startup from a different path on a clean Windows PC before sharing. Record the source commit with the package.

Recipients will still need to configure WoW, check their key bindings, calibrate for their display, and follow the manual starter-catch workflow. Until a portable package is available, use the source installation instructions above.

## Set the keys once

| Action | WoW binding (Czech layout) | App setting |
| --- | --- | --- |
| Fishing | `ú` | **Cast key:** `[` |
| Interact With Target | `)` | **Interact key:** `]` |
| Bright Baubles macro | Physical key matching the app's `'` binding | **Lure key:** `'` |

Enter `[`, `]`, and `'` (a single apostrophe) in **Setup**, then click **Save keys**. The app uses US-style names for physical keys; the characters shown by WoW can differ on a Czech layout. Bind the macro to the corresponding physical key and test it manually. Keep working bindings unchanged between sessions.

## Bright Baubles macro

Create this macro in WoW and place it on an action bar:

```text
#showtooltip Bright Baubles
/use Bright Baubles
/use 16
```

Keep Bright Baubles in your bags and equip the fishing pole in your main hand (slot `16`). Bind the macro to the key configured as **Lure key** `'` in the app. The bot presses it before the first cast and reapplies it at the configured interval. The saved setup uses `lure_minutes = 10.0` and `lure_cast_s = 6.0`; check the item's duration in your client if you change lures. Clear **Lure key** to disable automatic lure use.

Lure use is timer-based: the bot does not check the active buff or whether application succeeded. The 10-minute timer starts after the 6-second application wait; renewal happens between casts. Stopping and starting fishing resets the timer and applies the lure again, even if the previous lure is still active.

## Saved working configuration

[config/forever-working.toml](config/forever-working.toml) is a copy of the working configuration saved on this PC, including the three key bindings, lure timing, and detection settings. To reuse it, close River Desk, back up your existing `.local/state/config/config.toml`, and copy this file to that location.

The saved icon size is `32` px, the icon threshold is `0.66`, and the bite threshold is `0.5`. These values are a starting point for other PCs; repeat calibration for the current display and game setup. The app reads the local configuration, not this reference file.

## Before every session

1. Note any game settings you change so you can restore them later. Enable **Enable Interact Key** and **Auto Loot**. Set **Music** and **Ambience** to zero; keep **Sound Effects** and master sound on.
2. Enable both interaction icons. Enter each command separately in the game chat:

   ```text
   /console SoftTargetIconInteract 1
   /console SoftTargetIconGameObject 1
   ```

   Before changing them, you can check their current values with `/dump GetCVar("SoftTargetIconInteract")` and `/dump GetCVar("SoftTargetIconGameObject")`.
3. **Calibrate every session.** Stand by the water. Move River Desk to the side, clear of the bobber and its gold icon; minimizing alone is not always enough. In **Setup**, click **Calibrate the gear icon**, return to WoW, and cast manually with `ú`. Once the app detects the icon, click **Save calibration**.
4. **Catch a few fish manually at the start of every session, even with Bright Baubles enabled.** Use `)` to interact; several catches may be needed before starting the bot. If the gold icon is missing, cast closer and check the commands above.
5. On the **Fish** tab, click **Start**. Keep River Desk positioned to the side, then minimize it and return to WoW. Keep the game in the foreground and the water unobstructed. If detection fails, stop the bot, repeat calibration and the manual catches, then try again.

## After every session

Click **Stop**, then close River Desk. Restore any sound, interaction, and loot settings you changed. Restore the icon values too; if both were originally `0`, enter:

```text
/console SoftTargetIconInteract 0
/console SoftTargetIconGameObject 0
```

Keep the fishing key bindings for next time.

## Known-good version

See [STABLE.md](STABLE.md) for the user-verified baseline, its exact source download, and recovery instructions before trying later changes.

## Optional session helpers (new; not part of the verified baseline)

In **Setup → Session helpers (optional)**, enter **Check foreground every (min)** and **Jump every (min)**, then click **Save timers**. The selected intervals for this PC are 1 and 5 minutes. Leave either field empty (or enter `0`) to disable that function. Saved values appear when you reopen the app; changes apply on the next **Start**.

- **Foreground recovery (Windows):** while fishing is running, check at the saved interval (1 minute on this PC) and request that the same WoW window return to the foreground if it lost focus. After recovery, start a fresh cast. Stop the bot before deliberately using another app; it will otherwise try to return to WoW.
- **Small movement:** jump in place at the saved interval (5 minutes on this PC), only between casts, and wait to land before casting. The timer is deferred while a fish is on the line. `jump_key` defaults to `space`; no mouse movement is sent.
- Both are disabled in the generic defaults and in the preserved working configuration snapshot. The settings are stored as `behavior.focus_check_minutes` and `behavior.jump_every_minutes`.

Windows may refuse foreground activation, and an always-on-top popup can still cover the game. The bot stays paused when focus cannot be confirmed; this feature does not close TeamViewer or its dialogs. See [Microsoft's foreground activation rules](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setforegroundwindow).

## Detection and current status

The bot finds the bobber icon before listening for a bite. It compares audio against bundled splash recordings; manual catches do not train it. **Setup → Record 60 s and check the bite** can suggest a bite threshold; click **Save** to apply it. Keep other windows clear of the game and inspect `.local/state/log/wowfish.log` when detection fails.

| Area | Status |
| --- | --- |
| Original fishing setup | User-verified baseline pinned in [STABLE.md](STABLE.md). |
| Foreground recovery, scheduled jumps, Setup timers, randomized launch names | Implemented and covered by automated tests; live verification of the new features is still pending. |
| Slow icon acquisition | Logs show some attempts taking about a minute despite a 4-second limit. Synchronous fallback calibration is a suspected cause; a fix is not implemented. |
| Lure reuse across Stop/Start | Not implemented; every new run still applies the lure again. |
| Portable sharing ZIP | Planned, to be prepared when requested; no distributable build is available yet. |
