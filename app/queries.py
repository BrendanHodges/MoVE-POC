from app.db import get_db_connection
import pandas as pd

def fetch_move_equation_scores():

    def get_move_equation_scores() -> pd.DataFrame:
        conn = get_db_connection()
        cur = conn.cursor()

        query = """
        SELECT
            C.County_id,
            C.name AS county_name,
            Q.question_id,
            Q.question,
            Q.category,
            R.value AS response_value
        FROM Responses R
        JOIN Counties  C ON C.County_id   = R.County_id
        JOIN Questions Q ON Q.question_id = R.question_id
        ORDER BY C.County_id, Q.question_id
        """
        cur.execute(query)
        rows = cur.fetchall()
        conn.close()

        return pd.DataFrame([dict(r) for r in rows])


    def build_category_scores(df: pd.DataFrame) -> pd.DataFrame:
        df_cat = (
            df.groupby(["County_id", "county_name", "category"], as_index=False)["response_value"]
            .sum()
            .rename(columns={"response_value": "category_score"})
        )

        df_wide = (
            df_cat.pivot_table(
                index=["County_id", "county_name"],
                columns="category",
                values="category_score",
                aggfunc="first"
            )
            .reset_index()
        )

        df_wide.columns.name = None
        return df_wide


    def score(df_final: pd.DataFrame) -> pd.DataFrame:
        df = df_final.copy()

        # If you truly want to remove Abuses, do it safely:
        df = df.drop(columns=["Abuses"], errors="ignore")

        # Category columns = everything except IDs/names
        id_cols = ["County_id", "county_name"]
        cat_columns = [c for c in df.columns if c not in id_cols]

        # Make sure category columns are numeric and fill missing scores with 0
        df[cat_columns] = df[cat_columns].apply(pd.to_numeric, errors="coerce").fillna(0)

        # Debug: show standard deviations (raw)
        print("Standard deviations (raw category scores):")
        print(df[cat_columns].std())

        # Z-score standardize with zero-variance protection
        df_z = df.copy()
        for col in cat_columns:
            mean = df[col].mean()
            std = df[col].std()

            if std == 0 or pd.isna(std):
                df_z[col] = 0  # neutral contribution if no variance
            else:
                df_z[col] = (df[col] - mean) / std

        # Additive composite (sum of z-scores)
        df_z["move_additive_z"] = df_z[cat_columns].sum(axis=1)

        # Min-Max normalize additive score (0–100)
        min_v = df_z["move_additive_z"].min()
        max_v = df_z["move_additive_z"].max()

        if max_v == min_v:
            df_z["move_score_0_100"] = 50.0  # everything identical -> give neutral 50
        else:
            df_z["move_score_0_100"] = ((df_z["move_additive_z"] - min_v) / (max_v - min_v)) * 100

        # Debug: check z-score means/stds
        print("\nPost-standardization check (category z-scores):")
        print(df_z[cat_columns].agg(["mean", "std"]))

        print("\nPreview:")
        print(df_z[id_cols + ["move_additive_z", "move_score_0_100"]].head())

        return df_z

    #Grab all MoVE data for individual counties, every question
    df_raw = get_move_equation_scores()

    #Sum the questions for every MoVE variable
    df_cat_wide = build_category_scores(df_raw)

    # Score and export (MoVE equation)
    df_scored = score(df_cat_wide)

    df_scored = df_scored[['County_id', 'county_name', 'move_score_0_100']]

    #Turns dataframe into dictionary format suitable for javascript
    countyScores = {
    str(row['County_id']): {
        "name": row['county_name'],
        "score": round(row['move_score_0_100'], 2)
    }
    for _, row in df_scored.iterrows()
    }

    return countyScores

