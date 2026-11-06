# Ticket to Ride: London - Individual Extensions

I developed this individual final sprint during FIT3077 at Monash University in 2026, building on the [Ticket to Ride application I created with my team](https://github.com/prmdhaliwal/ticket-to-ride-group). My focus was making the architecture easier to extend, adding new game mechanics and testing the rules behind them.

## What I Added

- **Clearer responsibilities:** I consolidated game setup and extracted route-claim coordination and payment rules into dedicated classes.
- **Ferry routes:** I introduced standard and ferry route-claim strategies, including the required-card and substitute-card rules.
- **Visible ticket market:** I added a three-ticket market, ticket selection and replenishment, and the corresponding interface.
- **Configurable maps:** I moved map loading into a `MapCatalog`, with JSON-driven locations, routes, tickets, scores and player limits. I included London and a small Sydney test map.
- **UI and rule checks:** I refined setup and board layouts and added tests for route claims, map loading, card drawing and ticket selection.

I committed this work under `pdha0007`. Earlier commits and the prototypes retain my teammates' contributions to the shared foundation.

## Architecture

I kept the models, controllers and Tkinter views separate. `GameSetup` creates the initial state; `TurnManager` coordinates turns; `RouteClaimManager` delegates route payment rules to standard or ferry strategies. `MapCatalog` loads map configuration without putting file-loading responsibilities in `MapDefinition`.

```text
app/
  controllers/   Game setup and action coordination
  models/        Game state, route strategies, maps and scoring
  views/         Tkinter setup and game windows
  assets/maps/   London and Sydney JSON configurations
  tests/         Automated rule and map-loading checks
```

## Run Locally

I use Python with Tkinter and `sv-ttk`. From PowerShell on Windows:

```powershell
git clone https://github.com/prmdhaliwal/ticket-to-ride-individual.git
cd ticket-to-ride-individual
python -m venv .venv
./.venv/Scripts/python.exe -m pip install -r requirements.txt
./.venv/Scripts/python.exe app/main.py
```

Choose a map and enter the player names in the setup window. The source does not require an account, database or external service.

## Tests

```powershell
./.venv/Scripts/python.exe -B -m unittest discover -s app/tests -v
```

All 38 tests pass at this revision. They cover route-claim validation, ferry payment rules, the ticket market, map loading, player limits and card-drawing behaviour. These are backend checks, not a complete GUI playthrough.

## Windows Packaging

I kept the PyInstaller specification in [`Sprint 3/TicketToRideLondon.spec`](Sprint%203/TicketToRideLondon.spec). To build from the repository root:

```powershell
./.venv/Scripts/python.exe -m pip install pyinstaller
./.venv/Scripts/python.exe -m PyInstaller "Sprint 3/TicketToRideLondon.spec" --noconfirm --distpath app/dist --workpath app/build
```

The configured output is `app/dist/TicketToRideLondon.exe`. A packaged executable is not included in this repository.
