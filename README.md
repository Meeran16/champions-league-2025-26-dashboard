\
# UEFA Champions League 2025/26 Dashboard

Interactive Streamlit + Plotly application built on the separate
[`champions-league-2025-26-analytics`](https://github.com/Meeran16/champions-league-2025-26-analytics)
project.

The analytics repository remains the data-engineering and SQL layer. This repository focuses on interactive exploration and application design.

## Dashboard pages

1. **Tournament Overview** — competition KPIs, stage breakdown, league table and scoring.
2. **Team Analysis** — club-level results, league-phase home/away performance, rolling form and detailed averages.
3. **Player Rankings** — Top-5 LPI rankings by position with source-signal breakdowns.
4. **Player Comparison** — same-position LPI comparison.
5. **Match Explorer** — tournament filters and match-level inspection.

The AI-assisted football analysis layer is intentionally added only after this base dashboard is validated.

## Architecture

```text
champions-league-2025-26-analytics
        │
        │ completed SQLite database
        ▼
scripts/export_dashboard_data.py
        │
        ▼
data/derived/*.csv
        │
        ▼
Streamlit + Plotly dashboard
```

## Local setup

Recommended folder layout:

```text
D:\Github\
├── champions-league-2025-26-analytics\
└── champions-league-2025-26-dashboard\
```

### 1. Prepare the analytics database

From the analytics repository:

```powershell
python src/run_pipeline.py
python src/run_player_upgrade.py
python src/validate_data.py
python src/validate_player_data.py
```

### 2. Install dashboard dependencies

```powershell
pip install -r requirements.txt
```

### 3. Export dashboard datasets

```powershell
python scripts/export_dashboard_data.py
```

The exporter automatically looks for:

```text
..\champions-league-2025-26-analytics\data\processed\champions_league.db
```

A custom database path can also be passed:

```powershell
python scripts/export_dashboard_data.py --db "D:\path\to\champions_league.db"
```

### 4. Validate the exported data

```powershell
python scripts/validate_dashboard_data.py
```

Expected core checks:

- 36 teams
- 189 matches
- 144 league-phase matches
- 36 league-table rows
- Forward, Midfielder, Defender and Goalkeeper LPI groups

### 5. Start Streamlit

```powershell
streamlit run app.py
```

Streamlit normally opens:

```text
http://localhost:8501
```

## Data scope

- Complete tournament results: **189 matches**
- Detailed possession/shooting statistics: **144 league-phase matches**
- Player layer: reproducible **Leaderboard Performance Index (LPI)**
- Extra time and penalty shootouts: modelled separately

No missing knockout-stage possession or shooting values are inferred.

## Player-ranking limitation

The LPI is a project-defined analytical index, not an official UEFA award and not a complete event-data ranking of every tournament player.

It ranks players represented in the preserved source-leaderboard candidate pool. Different positions use different source signals and weights, so Player Comparison is restricted to the same position group.

## Data redistribution

Generated files under `data/derived/` are ignored by Git by default.

Before a public deployment, review the redistribution/licensing terms of the underlying detailed match-statistics sources and decide which generated datasets can be packaged with the deployed application.

## Planned AI layer

The next stage will use:

```text
Natural-language question
        ↓
Approved analytics function
        ↓
Validated dashboard dataset
        ↓
Structured evidence
        ↓
LLM explanation
```

The language model will explain validated results rather than invent or calculate tournament statistics itself.
