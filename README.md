# WoW Fishing Forever — úpravy pro Windows

Tento fork přidává vlastní spouštění ze zdrojového kódu na Windows. Původní projekt a jeho úplná dokumentace jsou v [rsamf/wow-fishing-forever](https://github.com/rsamf/wow-fishing-forever). Platí [licence MIT](LICENSE).

## Co jsme změnili

- `RiverDesk.cmd` spouští aplikaci ze zdrojového kódu v místním Pythonu. `RiverDesk.exe` je název běžícího procesu a `River Desk` titulek okna.
- Windows spouštěč ukládá nastavení a logy do `.local/state/`. Python, stažené závislosti a nastavení konkrétního počítače zůstávají mimo Git.
- Návod pro Codex je v [AGENTS.md](AGENTS.md).

## Instalace na druhém PC

Naklonuj tento fork do místní složky, otevři ji v Codexu a zadej: „Přečti AGENTS.md a zprovozni mi WoW Fishing Forever na tomto PC.“ Soubor obsahuje i příkazy pro ruční instalaci a diagnostiku.

### Klávesy nastav jen jednou

| Funkce ve WoW | Klávesa | Pole v aplikaci |
| --- | --- | --- |
| Fishing na akční liště | `ú` | **Cast key** `[` |
| Interact With Target | `)` | **Interact key** `]` |

Pokud ti nastavení v aplikaci už funguje, ponech ho. Při nové instalaci zadej v **Setup** `[` a `]` a klikni na **Save keys**. Aplikace těmito znaky označuje stejné fyzické klávesy, které na českém rozložení píšou `ú` a `)`. Přiřazení ve WoW nastav jen jednou a mezi relacemi je neměň. **Lure key** nech prázdné, pokud nepoužíváš makro na nástrahu.

## Před každou relací

1. Ve WoW si poznamenej původní hodnoty nastavení, která měníš. Hodnoty ikon ověříš přes `/dump GetCVar("SoftTargetIconInteract")` a `/dump GetCVar("SoftTargetIconGameObject")`.
2. V **Options** zapni **Enable Interact Key** a **Auto Loot**. V herním chatu zadej každý příkaz na samostatném řádku:

   ```text
   /console SoftTargetIconInteract 1
   /console SoftTargetIconGameObject 1
   ```

3. V **Options → Sound** stáhni **Music** a **Ambience** na nulu. **Sound Effects** a hlavní zvuk ponech zapnuté, aby aplikace slyšela šplouchnutí.
4. Postav se k vodě a ručně nahoď klávesou `ú`. Ověř, že vidíš zlatou ikonu nad splávkem a že při záběru funguje `)`. Když se ikona neobjeví, zkus nahodit blíž a zkontroluj hodnoty příkazů uvedených výše.
5. Otevři `RiverDesk.cmd`, na kartě **Fish** klikni na **Start** a přepni se zpět do WoW. Nech hru v popředí a vodu v záběru. Kalibrace obvykle proběhne při prvním nahození. Při potížích použij na kartě **Setup** tlačítko **Calibrate the gear icon** a po ručním nahození ulož výsledek přes **Save calibration**.

## Po každé relaci

1. Na kartě **Fish** klikni na **Stop** a zavři aplikaci.
2. Ve WoW vrať **Music**, **Ambience**, **Enable Interact Key** a **Auto Loot** na původní hodnoty, pokud jsi je před relací změnil.
3. Vrať i hodnoty obou příkazů pro ikony. Pokud byly před relací obě `0`, zadej:

   ```text
   /console SoftTargetIconInteract 0
   /console SoftTargetIconGameObject 0
   ```

Klávesy `ú` a `)` zůstávají přiřazené pro příští relaci.

Pro diagnostiku spusť v PowerShellu z kořene projektu `.\RiverDesk.cmd doctor`. Upozornění na chybějící okno a zvuk hry jsou běžná, když WoW není spuštěné.
