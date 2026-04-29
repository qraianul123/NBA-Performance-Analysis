import pandas as pd
import os

seasons = ["2023-24", "2024-25", "2025-26"]

team_frames = []
adv_frames = []

for season in seasons:
    
    ts = pd.read_csv(f"team_stats_{season}.csv")
    ts["Season"] = season
    team_frames.append(ts)

    
    adv = pd.read_csv(f"advanced_stat_{season}.csv", header=1)
    adv["Season"] = season
    adv_frames.append(adv)

team_df = pd.concat(team_frames, ignore_index=True)
adv_df = pd.concat(adv_frames, ignore_index=True)

team_df = team_df[team_df["Team"].notna()]
team_df = team_df[~team_df["Team"].str.contains("League Average", na=False)]

team_df["Team"] = team_df["Team"].str.replace("*", "", regex=False).str.strip()

team_df = team_df.drop(columns=["Rk"], errors="ignore")

numeric_cols = ["G","MP","FG","FGA","FG%","3P","3PA","3P%","2P","2PA","2P%",
                "FT","FTA","FT%","ORB","DRB","TRB","AST","STL","BLK","TOV","PF","PTS"]
for col in numeric_cols:
    if col in team_df.columns:
        team_df[col] = pd.to_numeric(team_df[col], errors="coerce")

adv_df = adv_df[adv_df["Team"].notna()]
adv_df = adv_df[~adv_df["Team"].str.contains("League Average", na=False)]
adv_df = adv_df[adv_df["Team"] != "Team"]  # remove repeated headers

adv_df["Team"] = adv_df["Team"].str.replace("*", "", regex=False).str.strip()

adv_keep = ["Team", "Season", "Age", "W", "L", "MOV", "SOS", "SRS",
            "ORtg", "DRtg", "NRtg", "Pace", "TS%", "Attend./G"]
adv_df = adv_df[[c for c in adv_keep if c in adv_df.columns]]

adv_numeric = ["Age","W","L","MOV","SOS","SRS","ORtg","DRtg","NRtg","Pace","TS%","Attend./G"]
for col in adv_numeric:
    if col in adv_df.columns:
        adv_df[col] = pd.to_numeric(adv_df[col], errors="coerce")

master = pd.merge(team_df, adv_df, on=["Team", "Season"], how="inner")

master["Win%"] = master["W"] / (master["W"] + master["L"])

master["AST/TOV"] = (master["AST"] / master["TOV"]).round(2)

master["PTS/FGA"] = (master["PTS"] / master["FGA"]).round(2)

master.to_csv("nba_master.csv", index=False)

yoy = master.groupby("Season").agg(
    Avg_PTS=("PTS", "mean"),
    Avg_3P_Pct=("3P%", "mean"),
    Avg_Pace=("Pace", "mean"),
    Avg_ORtg=("ORtg", "mean"),
    Avg_DRtg=("DRtg", "mean"),
    Avg_Win_Pct=("Win%", "mean"),
    Avg_Attendance=("Attend./G", "mean")
).round(3).reset_index()
yoy.to_csv("nba_season_summary.csv", index=False)

print("Done. Files created:")
print(f"  nba_master.csv        — {len(master)} rows, {len(master.columns)} columns")
print(f"  nba_season_summary.csv — {len(yoy)} rows (one per season)")
print("\nColumn list for nba_master.csv:")
print(list(master.columns))
