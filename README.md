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

Enter the app values in **Setup** and click **Save keys**. They refer to the same physical keys on the Czech layout. Leave **Lure key** empty unless you use a lure macro. Keep working bindings unchanged between sessions.

## Before every session

1. Note any game settings you change so you can restore them later. Enable **Enable Interact Key** and **Auto Loot**. Set **Music** and **Ambience** to zero; keep **Sound Effects** and master sound on.
2. Enable both interaction icons. Enter each command separately in the game chat:

   ```text
   /console SoftTargetIconInteract 1
   /console SoftTargetIconGameObject 1
   ```

   Before changing them, you can check their current values with `/dump GetCVar("SoftTargetIconInteract")` and `/dump GetCVar("SoftTargetIconGameObject")`.
3. **Calibrate every session.** Stand by the water. Move River Desk to the side, clear of the bobber and its gold icon; minimizing alone is not always enough. In **Setup**, click **Calibrate the gear icon**, return to WoW, and cast manually with `ú`. Once the app detects the icon, click **Save calibration**.
4. **Catch the first fish manually** with `)`. You may need to catch several fish manually before detection works reliably. If the gold icon is missing, cast closer and check the commands above.
5. On the **Fish** tab, click **Start**. Keep River Desk positioned to the side, then minimize it and return to WoW. Keep the game in the foreground and the water unobstructed. If detection fails, stop the bot, repeat calibration and the manual catches, then try again.

## After every session

Click **Stop**, then close River Desk. Restore any sound, interaction, and loot settings you changed. Restore the icon values too; if both were originally `0`, enter:

```text
/console SoftTargetIconInteract 0
/console SoftTargetIconGameObject 0
```

Keep the fishing key bindings for next time.
