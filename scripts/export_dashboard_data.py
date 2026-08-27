\
from __future__ import annotations

import argparse
from pathlib import Path
import sqlite3
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = (
    ROOT.parent
    / "champions-league-2025-26-analytics"
    / "data"
    / "processed"
    / "champions_league.db"
)
DEFAULT_OUTPUT = ROOT / "data" / "derived"
REQUIRED_TABLES = {"teams", "matches", "league_phase_stats", "player_rankings"}

def query(conn: sqlite3.Connection, sql: str) -> pd.DataFrame:
    return pd.read_sql_query(sql, conn)

def ensure_database(conn: sqlite3.Connection) -> None:
    found = set(
        pd.read_sql_query(
            "SELECT name FROM sqlite_master WHERE type='table';", conn
        )["name"]
    )
    missing = REQUIRED_TABLES - found
    if missing:
        raise RuntimeError(
            "Database is missing required tables: "
            + ", ".join(sorted(missing))
            + ". Run the analytics base pipeline and player upgrade first."
        )

def export(db_path: Path, output_dir: Path) -> dict[str, int]:
    if not db_path.exists():
        raise FileNotFoundError(
            f"Analytics database not found: {db_path}\n"
            "Expected the completed analytics project in the sibling folder, "
            "or pass a custom path with --db."
        )

    output_dir.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path) as conn:
        ensure_database(conn)

        matches = query(conn, """
            SELECT
                m.match_id, m.date, m.kickoff_time, m.stage, m.matchday,
                h.team_name AS home_team, a.team_name AS away_team,
                m.home_goals, m.away_goals,
                m.regulation_home_goals, m.regulation_away_goals,
                m.half_time_home_goals, m.half_time_away_goals,
                m.extra_time, m.penalty_shootout,
                m.penalty_home, m.penalty_away,
                m.match_outcome, m.winner,
                s.venue, s.referee,
                s.home_possession, s.away_possession,
                s.home_shots_total, s.away_shots_total,
                s.home_shots_on_target_count, s.away_shots_on_target_count,
                s.home_saves_count, s.away_saves_count,
                s.home_shots_on_target_pct, s.away_shots_on_target_pct,
                s.home_saves_pct, s.away_saves_pct
            FROM matches m
            JOIN teams h ON h.team_id = m.home_team_id
            JOIN teams a ON a.team_id = m.away_team_id
            LEFT JOIN league_phase_stats s ON s.match_id = m.match_id
            ORDER BY m.date, m.match_id;
        """)

        league_table = query(conn, """
            WITH team_matches AS (
                SELECT
                    t.team_name,
                    m.home_goals AS goals_for,
                    m.away_goals AS goals_against,
                    CASE WHEN m.home_goals > m.away_goals THEN 3
                         WHEN m.home_goals = m.away_goals THEN 1 ELSE 0 END AS points,
                    CASE WHEN m.home_goals > m.away_goals THEN 1 ELSE 0 END AS win,
                    CASE WHEN m.home_goals = m.away_goals THEN 1 ELSE 0 END AS draw,
                    CASE WHEN m.home_goals < m.away_goals THEN 1 ELSE 0 END AS loss
                FROM matches m
                JOIN teams t ON t.team_id = m.home_team_id
                WHERE m.stage = 'League Phase'

                UNION ALL

                SELECT
                    t.team_name,
                    m.away_goals,
                    m.home_goals,
                    CASE WHEN m.away_goals > m.home_goals THEN 3
                         WHEN m.away_goals = m.home_goals THEN 1 ELSE 0 END,
                    CASE WHEN m.away_goals > m.home_goals THEN 1 ELSE 0 END,
                    CASE WHEN m.away_goals = m.home_goals THEN 1 ELSE 0 END,
                    CASE WHEN m.away_goals < m.home_goals THEN 1 ELSE 0 END
                FROM matches m
                JOIN teams t ON t.team_id = m.away_team_id
                WHERE m.stage = 'League Phase'
            )
            SELECT
                team_name,
                COUNT(*) AS played,
                SUM(win) AS wins,
                SUM(draw) AS draws,
                SUM(loss) AS losses,
                SUM(goals_for) AS goals_for,
                SUM(goals_against) AS goals_against,
                SUM(goals_for) - SUM(goals_against) AS goal_difference,
                SUM(points) AS points,
                ROUND(1.0 * SUM(points) / COUNT(*), 2) AS points_per_match
            FROM team_matches
            GROUP BY team_name
            ORDER BY points DESC, goal_difference DESC, goals_for DESC, team_name;
        """)
        league_table.insert(0, "position", range(1, len(league_table) + 1))

        team_summary = query(conn, """
            WITH team_games AS (
                SELECT
                    t.team_name,
                    m.home_goals AS goals_for,
                    m.away_goals AS goals_against,
                    CASE WHEN m.home_goals > m.away_goals THEN 1 ELSE 0 END AS win,
                    CASE WHEN m.home_goals = m.away_goals THEN 1 ELSE 0 END AS draw,
                    CASE WHEN m.home_goals < m.away_goals THEN 1 ELSE 0 END AS loss
                FROM matches m
                JOIN teams t ON t.team_id = m.home_team_id

                UNION ALL

                SELECT
                    t.team_name,
                    m.away_goals,
                    m.home_goals,
                    CASE WHEN m.away_goals > m.home_goals THEN 1 ELSE 0 END,
                    CASE WHEN m.away_goals = m.home_goals THEN 1 ELSE 0 END,
                    CASE WHEN m.away_goals < m.home_goals THEN 1 ELSE 0 END
                FROM matches m
                JOIN teams t ON t.team_id = m.away_team_id
            ),
            detailed AS (
                SELECT
                    t.team_name,
                    s.home_possession AS possession,
                    s.home_shots_total AS shots,
                    s.home_shots_on_target_count AS shots_on_target
                FROM league_phase_stats s
                JOIN matches m ON m.match_id = s.match_id
                JOIN teams t ON t.team_id = m.home_team_id

                UNION ALL

                SELECT
                    t.team_name,
                    s.away_possession,
                    s.away_shots_total,
                    s.away_shots_on_target_count
                FROM league_phase_stats s
                JOIN matches m ON m.match_id = s.match_id
                JOIN teams t ON t.team_id = m.away_team_id
            ),
            detailed_rollup AS (
                SELECT
                    team_name,
                    ROUND(AVG(possession), 2) AS avg_league_possession,
                    ROUND(AVG(shots), 2) AS avg_league_shots,
                    ROUND(AVG(shots_on_target), 2) AS avg_league_shots_on_target
                FROM detailed
                GROUP BY team_name
            )
            SELECT
                g.team_name,
                COUNT(*) AS matches_played,
                SUM(g.win) AS wins,
                SUM(g.draw) AS draws,
                SUM(g.loss) AS losses,
                SUM(g.goals_for) AS goals_for,
                SUM(g.goals_against) AS goals_against,
                SUM(g.goals_for) - SUM(g.goals_against) AS goal_difference,
                ROUND(1.0 * SUM(g.goals_for) / COUNT(*), 2) AS goals_per_match,
                d.avg_league_possession,
                d.avg_league_shots,
                d.avg_league_shots_on_target
            FROM team_games g
            LEFT JOIN detailed_rollup d ON d.team_name = g.team_name
            GROUP BY g.team_name
            ORDER BY goals_for DESC, goal_difference DESC, g.team_name;
        """)

        home_away = query(conn, """
            WITH team_games AS (
                SELECT
                    t.team_name, 'Home' AS venue_role,
                    m.home_goals AS goals_for, m.away_goals AS goals_against,
                    CASE WHEN m.home_goals > m.away_goals THEN 3
                         WHEN m.home_goals = m.away_goals THEN 1 ELSE 0 END AS points
                FROM matches m
                JOIN teams t ON t.team_id = m.home_team_id
                WHERE m.stage = 'League Phase'

                UNION ALL

                SELECT
                    t.team_name, 'Away',
                    m.away_goals, m.home_goals,
                    CASE WHEN m.away_goals > m.home_goals THEN 3
                         WHEN m.away_goals = m.home_goals THEN 1 ELSE 0 END
                FROM matches m
                JOIN teams t ON t.team_id = m.away_team_id
                WHERE m.stage = 'League Phase'
            )
            SELECT
                team_name, venue_role, COUNT(*) AS played,
                SUM(points) AS points,
                SUM(goals_for) AS goals_for,
                SUM(goals_against) AS goals_against,
                ROUND(1.0 * SUM(points) / COUNT(*), 2) AS points_per_match
            FROM team_games
            GROUP BY team_name, venue_role
            ORDER BY team_name, venue_role;
        """)

        rolling_form = query(conn, """
            WITH team_games AS (
                SELECT
                    m.match_id, m.date, t.team_name,
                    m.home_goals AS goals_for, m.away_goals AS goals_against,
                    CASE WHEN m.home_goals > m.away_goals THEN 3
                         WHEN m.home_goals = m.away_goals THEN 1 ELSE 0 END AS points
                FROM matches m
                JOIN teams t ON t.team_id = m.home_team_id
                WHERE m.stage = 'League Phase'

                UNION ALL

                SELECT
                    m.match_id, m.date, t.team_name,
                    m.away_goals, m.home_goals,
                    CASE WHEN m.away_goals > m.home_goals THEN 3
                         WHEN m.away_goals = m.home_goals THEN 1 ELSE 0 END
                FROM matches m
                JOIN teams t ON t.team_id = m.away_team_id
                WHERE m.stage = 'League Phase'
            )
            SELECT
                team_name, match_id, date, goals_for, goals_against, points,
                SUM(points) OVER (
                    PARTITION BY team_name
                    ORDER BY date, match_id
                    ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
                ) AS rolling_5_points,
                ROW_NUMBER() OVER (
                    PARTITION BY team_name
                    ORDER BY date, match_id
                ) AS match_number
            FROM team_games
            ORDER BY team_name, date, match_id;
        """)

        stage_summary = query(conn, """
            SELECT
                stage,
                COUNT(*) AS matches,
                SUM(home_goals + away_goals) AS goals,
                ROUND(1.0 * SUM(home_goals + away_goals) / COUNT(*), 2) AS goals_per_match
            FROM matches
            GROUP BY stage
            ORDER BY
                CASE stage
                    WHEN 'League Phase' THEN 1
                    WHEN 'Knockout Play-offs' THEN 2
                    WHEN 'Round of 16' THEN 3
                    WHEN 'Quarter-finals' THEN 4
                    WHEN 'Semi-finals' THEN 5
                    WHEN 'Final' THEN 6
                    ELSE 99
                END,
                stage;
        """)

        player_rankings = query(conn, """
            SELECT *
            FROM player_rankings
            ORDER BY
                CASE position_group
                    WHEN 'Forward' THEN 1
                    WHEN 'Midfielder' THEN 2
                    WHEN 'Defender' THEN 3
                    WHEN 'Goalkeeper' THEN 4
                    ELSE 5
                END,
                rank, player;
        """)

    total_goals = int((matches["home_goals"] + matches["away_goals"]).sum())
    all_teams = pd.concat([matches["home_team"], matches["away_team"]]).drop_duplicates()

    summary = pd.DataFrame([{
        "teams": int(len(all_teams)),
        "matches": int(len(matches)),
        "league_phase_matches": int((matches["stage"] == "League Phase").sum()),
        "goals": total_goals,
        "goals_per_match": round(total_goals / len(matches), 2),
        "first_match_date": matches["date"].min(),
        "last_match_date": matches["date"].max(),
    }])

    outputs = {
        "tournament_summary.csv": summary,
        "matches.csv": matches,
        "league_table.csv": league_table,
        "team_summary.csv": team_summary,
        "home_away_summary.csv": home_away,
        "rolling_form.csv": rolling_form,
        "stage_summary.csv": stage_summary,
        "player_rankings.csv": player_rankings,
    }

    for filename, frame in outputs.items():
        frame.to_csv(output_dir / filename, index=False)

    return {name: len(frame) for name, frame in outputs.items()}

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export dashboard-ready CSVs from the completed analytics SQLite database."
    )
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    counts = export(args.db.resolve(), args.output.resolve())
    print(f"Dashboard data exported from -> {args.db.resolve()}")
    print(f"Dashboard data written to   -> {args.output.resolve()}")
    for filename, rows in counts.items():
        print(f"  {filename}: {rows} row(s)")

if __name__ == "__main__":
    main()


