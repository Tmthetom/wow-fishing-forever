# Known-good fishing baseline

## Current stable release

The user approved [v1.2.0](https://github.com/Tmthetom/wow-fishing-forever/releases/tag/v1.2.0). The Fishing dashboard shows the latest 14 days of catch history, session start and stop times, catches per hour, and time since the last catch. Bite diagnostics names the four reference sounds in its legend.

- [Download the v1.2.0 source ZIP](https://github.com/Tmthetom/wow-fishing-forever/archive/refs/tags/v1.2.0.zip)

## Previous stable release v1.1.0

The user tested and approved [v1.1.0](https://github.com/Tmthetom/wow-fishing-forever/releases/tag/v1.1.0) in WoW Forever. It includes the River Desk redesign, timestamped activity logs, and the feathered bobber icon. On Windows, direct window capture is optional. Automatic calibration waits for the cast to land, and quick Stop → Start no longer resends a lure macro during the application wait.

- [Download the v1.1.0 source ZIP](https://github.com/Tmthetom/wow-fishing-forever/archive/refs/tags/v1.1.0.zip)

## Previous stable release v1.0.0

The user tested this version in WoW Forever and approved it as the new recovery point. It includes faster bobber icon acquisition and preserves the Bright Baubles timer across Stop → Start while River Desk stays open. Keep the manual starter catches and calibrate before each session.

- [GitHub release v1.0.0](https://github.com/Tmthetom/wow-fishing-forever/releases/tag/v1.0.0)
- [Exact source commit](https://github.com/Tmthetom/wow-fishing-forever/tree/a9984dfec939e8d5a753e1c0cf99554ecebd9c71)
- [Download the source ZIP](https://github.com/Tmthetom/wow-fishing-forever/archive/a9984dfec939e8d5a753e1c0cf99554ecebd9c71.zip)

## Earlier verified recovery point

The user has confirmed that foreground recovery, scheduled jumps, the Setup timers, and randomized window/process names work in the game. The source state before the lure-timer change is pinned at [`a688b38c61256f883511e23f66e3662378cea3e5`](https://github.com/Tmthetom/wow-fishing-forever/tree/a688b38c61256f883511e23f66e3662378cea3e5). [Download that source ZIP](https://github.com/Tmthetom/wow-fishing-forever/archive/a688b38c61256f883511e23f66e3662378cea3e5.zip). This is a source recovery point, not the planned portable package. It still reapplies the lure on every Start.

## Original fishing-only baseline

Confirmed working by the user on 18 November 2026, with Bright Baubles enabled.

- **Immutable source commit:** [`e95dfccc10e4be2d1defbc8ff813b26023c83694`](https://github.com/Tmthetom/wow-fishing-forever/tree/e95dfccc10e4be2d1defbc8ff813b26023c83694).
- [Download the exact source ZIP](https://github.com/Tmthetom/wow-fishing-forever/archive/e95dfccc10e4be2d1defbc8ff813b26023c83694.zip).
- Working settings: `config/forever-working.toml` at that commit. Cast `[`, interact `]`, lure `'`; lure interval 10 minutes, application wait 6 seconds.
- Catch a few fish manually at the start of every session, even with Bright Baubles enabled. Several catches may be needed before starting the bot.
- No automatic focus recovery or scheduled movement is part of this baseline.

## Restore a recovery point

Stop and close River Desk. Extract the selected source ZIP into a separate folder and follow that version's AGENTS.md to install its locked dependencies. Before launching, copy its `config/forever-working.toml` to `.local/state/config/config.toml`. Keep the current installation and settings as a backup. Run one bot instance at a time.

Follow that version's README for calibration and manual starter catches. The downloads above contain source code and require the setup steps in AGENTS.md.
