from app.db import get_db_connection
import pandas as pd


def fetch_all_counties_census_data() -> dict:
    conn = get_db_connection()

    query = """
    SELECT
        c.county_id,
        c.name AS county_name,
        v.name AS variable,
        f.data AS value
    FROM census_facts f
    JOIN census_variables v
      ON f.variable_id = v.variable_id
    JOIN counties c
      ON f.county_id = c.county_id
    WHERE v.name IN (
        'Overall Population',
        'Overall median earnings',
        'Estimate of the population (25 years and over) with a Bachelor’s degree (regardless of place of birth)'
      )
    ORDER BY c.county_id, v.name;
    """

    df = pd.read_sql(query, conn)
    conn.close()

    df["variable"] = df["variable"].replace({
        "Estimate of the population (25 years and over) with a Bachelor’s degree (regardless of place of birth)":
        "Overall Bachelor's degree population"
    })

    # nested dict:
    # {county_id: {"county_name": "...", "data": {variable: value}}}
    out = {}
    for (county_id, county_name), sub in df.groupby(["county_id", "county_name"]):
        out[int(county_id)] = {
            "county_name": county_name,
            "data": sub.set_index("variable")["value"].to_dict()
        }

    return out

print(fetch_all_counties_census_data())