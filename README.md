# WoW Fishing Forever — Windows fork

A Windows fork of [rsamf/wow-fishing-forever](https://github.com/rsamf/wow-fishing-forever), a World of Warcraft fishing bot that detects the bobber icon and listens for a splash. Licensed under [MIT](LICENSE).

## What this fork changes

- **Local Windows launcher:** `RiverDesk.cmd` runs the source code using a local Python installation. The window is named **River Desk** and the process is `RiverDesk.exe`.
- **Portable setup:** settings and logs stay in `.local/state/`; Python and dependencies also stay inside the project folder. Machine-specific files are excluded from Git.
- **Practical setup instructions:** Czech keyboard bindings, calibration, and window placement based on use on this PC.

## Install and launch

Clone this fork and follow [AGENTS.md](AGENTS.md), or ask Codex: “Read AGENTS.md and set up this project on this PC.” Open `RiverDesk.cmd` to launch the app. Run `.\RiverDesk.cmd doctor` from PowerShell for diagnostics; missing game warnings are expected when WoW is closed.

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
4. **With Bright Baubles enabled, the verified setup works from the first cast without manual starter catches.** If fishing without a lure or troubleshooting detection, try a few manual catches with `)`. If the gold icon is missing, cast closer and check the commands above.
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

Close River Desk before editing `.local/state/config/config.toml`. Add these entries to its existing `[behavior]` section, then reopen the app:

```toml
focus_check_minutes = 1.0
jump_every_minutes = 5.0
```

- **Foreground recovery (Windows):** while fishing is running, check once per minute and request that the same WoW window return to the foreground if it lost focus. After recovery, start a fresh cast. Stop the bot before deliberately using another app; it will otherwise try to return to WoW.
- **Small movement:** jump in place every five minutes, only between casts, and wait to land before casting. The timer is deferred while a fish is on the line. `jump_key` defaults to `space`; no mouse movement is sent.
- Set either interval to `0` to disable it. Both are disabled in the generic defaults and in the preserved working configuration snapshot. Changes take effect on the next run after loading the settings.

Windows may refuse foreground activation, and an always-on-top popup can still cover the game. The bot stays paused when focus cannot be confirmed; this feature does not close TeamViewer or its dialogs. See [Microsoft's foreground activation rules](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setforegroundwindow).
