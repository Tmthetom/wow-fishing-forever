# Known-good fishing baseline

Confirmed working by the user on 18 November 2026, with Bright Baubles enabled.

- **Immutable source commit:** [`e95dfccc10e4be2d1defbc8ff813b26023c83694`](https://github.com/Tmthetom/wow-fishing-forever/tree/e95dfccc10e4be2d1defbc8ff813b26023c83694).
- [Download the exact source ZIP](https://github.com/Tmthetom/wow-fishing-forever/archive/e95dfccc10e4be2d1defbc8ff813b26023c83694.zip).
- Working settings: `config/forever-working.toml` at that commit. Cast `[`, interact `]`, lure `'`; lure interval 10 minutes, application wait 6 seconds.
- With the lure enabled, fishing works from the first cast without manual starter catches. This is the user's observation on this setup, not an automatic lure-detection feature.
- No automatic focus recovery or scheduled movement is part of this baseline.

## Return to this version

Stop and close River Desk. Download the source ZIP into a separate folder, follow that version's AGENTS.md to install its locked dependencies, then copy its `config/forever-working.toml` to `.local/state/config/config.toml` before launching. Keep the current installation and settings as a backup. Only run one bot instance at a time.

The old README asks for manual starter catches; the verified lure setup does not require them. Recalibrate if the game UI or display changes.

This is a pinned recovery note, not a packaged Windows binary release. Keep this commit reference unchanged when adding new features.
