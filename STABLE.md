# Known-good fishing baseline

Confirmed working by the user on 18 November 2026, with Bright Baubles enabled.

- **Immutable source commit:** [`e95dfccc10e4be2d1defbc8ff813b26023c83694`](https://github.com/Tmthetom/wow-fishing-forever/tree/e95dfccc10e4be2d1defbc8ff813b26023c83694).
- [Download the exact source ZIP](https://github.com/Tmthetom/wow-fishing-forever/archive/e95dfccc10e4be2d1defbc8ff813b26023c83694.zip).
- Working settings: `config/forever-working.toml` at that commit. Cast `[`, interact `]`, lure `'`; lure interval 10 minutes, application wait 6 seconds.
- Catch a few fish manually at the start of every session, even with Bright Baubles enabled. Several catches may be needed before starting the bot.
- No automatic focus recovery or scheduled movement is part of this baseline.

## Return to this version

Stop and close River Desk. Download the source ZIP into a separate folder, follow that version's AGENTS.md to install its locked dependencies, then copy its `config/forever-working.toml` to `.local/state/config/config.toml` before launching. Keep the current installation and settings as a backup. Only run one bot instance at a time.

Follow the original README's manual starter catches and calibrate before every session. The earlier claim that a lure removes the need for manual catches was incorrect.

This is a pinned recovery note, not a packaged Windows binary release. Keep this commit reference unchanged when adding new features.
