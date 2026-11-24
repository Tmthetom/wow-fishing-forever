# WoW Fishing Forever — Windows fork

<img src="src/wowfish/assets/river-desk.png" alt="River Desk icon showing a cork fishing bobber with two feathers" width="96">

A Windows fork of [rsamf/wow-fishing-forever](https://github.com/rsamf/wow-fishing-forever), a World of Warcraft fishing bot that detects the bobber icon and listens for a splash. Licensed under [MIT](LICENSE).

## What this fork changes

- **Local Windows launcher:** `RiverDesk.cmd` runs the source code using a local Python installation. Each launch generates a name such as `River-a31f72c084bd` for the window and its `.exe` process. Keep using the existing River Desk shortcut.
- **River Desk icon:** The app uses an original fishing bobber illustration. The [Windows ICO](src/wowfish/assets/river-desk.ico) can also be used for a Windows shortcut.
- **Local setup:** settings and logs stay in `.local/state/`; Python and dependencies also stay inside the project folder. Machine-specific files are excluded from Git. This installation is not yet a ready-to-share portable package.
- **Practical setup instructions:** Czech keyboard bindings, calibration, and window placement based on use on this PC.

## Install and launch

Clone this fork and follow [AGENTS.md](AGENTS.md), or ask Codex: “Read AGENTS.md and set up this project on this PC.” Open `RiverDesk.cmd` to launch the app. Run `.\RiverDesk.cmd doctor` from PowerShell for diagnostics; missing game warnings are expected when WoW is closed.

The launcher keeps a small helper process (`pythonw.exe`, or `RiverDesk.exe` with the existing taskbar shortcut) open until the GUI exits, then removes the temporary named executable. Settings and logs stay in the same location. If startup fails, check `.local/state/log/launcher-error.log`. Direct CLI launches keep the standard window title.

The app opens on **Fishing** with Start, Stop, session totals, and local start and stop times for the current or most recent run. Stop times come from the bot's own stop events. A game logout that leaves the client open has no dedicated detection.

**Catches / hour** estimates the session's average after the first minute. **Since last catch** shows the time since the session's latest catch, and holds the value when the session stops. Both metrics start fresh on Start.

**Catches by day** shows the last 14 calendar days, including today. Hover over a bar for its date and count. Daily totals are saved for GUI sessions in `.local/state/log/catches.sqlite3` and survive restarts. The chart starts collecting data when this feature is installed.

**Setup** has a scrollable layout with calibration first. **Activity → Logs** shows the local date and time for each entry and includes a copy button. **Activity → Bite diagnostics** shows the last matched frame and the similarity to four reference sounds. Blue, orange, and green are splash samples 1–3. Amber is the extra bite sample. The horizontal dashed line is the detection threshold. The vertical marker labeled **bite** is when the detector registered a bite.

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

Lure use is timer-based: the bot does not check the active buff or whether application succeeded. When it sends the macro, it schedules renewal 10 minutes after the expected end of the 6-second application. **Stop → Start preserves that schedule while the app stays open**, even if you stop during the application wait. If you resume before the wait ends, the bot waits out the remaining time before casting. An expired lure is renewed on the next run.

Closing the app resets the timer. Changing the lure key or duration, or starting against a different game process/window, also resets it. After switching characters or fishing poles, or if the macro failed, close and reopen the app to force a fresh application; those changes are not detected automatically.

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
5. On the **Fishing** tab, click **Start**. Keep River Desk positioned to the side, then minimize it and return to WoW. Keep the game in the foreground and the water unobstructed. If detection fails, stop the bot, repeat calibration and the manual catches, then try again.

## After every session

Click **Stop**, then close River Desk. Restore any sound, interaction, and loot settings you changed. Restore the icon values too; if both were originally `0`, enter:

```text
/console SoftTargetIconInteract 0
/console SoftTargetIconGameObject 0
```

Keep the fishing key bindings for next time.

## Known-good version

The current stable version is [v1.2.0](https://github.com/Tmthetom/wow-fishing-forever/releases/tag/v1.2.0). See [STABLE.md](STABLE.md) for source downloads and restore instructions.

## Optional session helpers

In **Setup → Session helpers (optional)**, enter **Check foreground (min)** and **Jump every (min)**, then click **Save timers**. The selected intervals for this PC are 1 and 5 minutes. Leave either field empty (or enter `0`) to disable that function. Saved values appear when you reopen the app; changes apply on the next **Start**.

- **Foreground recovery (Windows):** while fishing is running, check at the saved interval (1 minute on this PC) and request that the same WoW window return to the foreground if it lost focus. After recovery, start a fresh cast. Stop the bot before deliberately using another app; it will otherwise try to return to WoW.
- **Small movement:** jump in place at the saved interval (5 minutes on this PC), only between casts, and wait to land before casting. The timer is deferred while a fish is on the line. `jump_key` defaults to `space`; no mouse movement is sent.
- Both are disabled in the generic defaults and in the preserved working configuration snapshot. The settings are stored as `behavior.focus_check_minutes` and `behavior.jump_every_minutes`.

Windows may refuse foreground activation, and an always-on-top popup can still cover the game. The bot stays paused when focus cannot be confirmed; this feature does not close TeamViewer or its dialogs. See [Microsoft's foreground activation rules](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setforegroundwindow).

## Experimental Windows window capture

In **Setup → Session helpers (optional)**, enable **Capture the WoW window directly** to try reading the game's client area when another window covers it. The setting is saved immediately and applies to the next calibration or **Start**. Keep WoW unminimized. Fishing still pauses when WoW loses focus. If direct capture reports an error or the preview is blank or frozen, turn it off and retry. The default is screen capture (`run.window_capture = false`).

To test capture independently of fishing, click **Calibrate the gear icon**, cast manually, and cover part of WoW with another window. Check the calibration preview for game pixels in the covered area. The fishing status **Paused** reports keyboard focus.

## Detection and current status

The bot finds the bobber icon before listening for a bite. It compares audio against bundled splash recordings; manual catches do not train it. **Setup → Record 60 s and check the bite** can suggest a bite threshold; click **Save** to apply it. Keep other windows clear of the game and inspect `.local/state/log/wowfish.log` when detection fails.

| Area | Status |
| --- | --- |
| Original fishing setup | User-verified baseline pinned in [STABLE.md](STABLE.md). |
| Foreground recovery, scheduled jumps, Setup timers, randomized launch names | Included in the current stable version and verified by the user. |
| Bobber icon acquisition | Saved calibration is tried first. Fallback starts after repeated icon timeouts, a change in window size, or when saved calibration is unavailable. It checks the cast deadline and Stop between template matches. The new fallback waits 1.5 seconds after casting and rejects an icon that also appeared in the same place before the cast. |
| Lure reuse across Stop/Start | Included in the current stable version. Automated tests cover restart and expiry while the app stays open. |
| Portable sharing ZIP | Planned, to be prepared when requested; no distributable build is available yet. |

Acquisition previously checked its timeout only after an unrestricted calibration sweep, using an old timestamp. The new checks prevent that full sweep from blocking a cast; one capture or OpenCV match already in progress can still finish after the deadline. If the saved size is wrong, recalibrate in Setup. Manual starter catches remain in the workflow until live tests establish whether they are still needed; the bot does not learn splash sounds from them.

The fishing loop and manual calibration briefly wait between iterations to limit CPU use. The user approved v1.1.0 after testing it in WoW Forever.

To check whether automatic calibration ran, look for **Measured the gear icon** in **Activity → Logs**. A cast that finds the icon using the saved size skips the measurement.
