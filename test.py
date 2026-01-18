from app.db import get_db_connection
import pandas as pd


def fetch_county_census_data(county_id: int) -> dict:
    conn = get_db_connection()

    query = """
    SELECT
        v.name AS variable,
        f.data AS value
    FROM census_facts f
    JOIN census_variables v
      ON f.variable_id = v.variable_id
    WHERE f.county_id = ?
      AND v.name IN (
        'Overall Population',
        'Overall median earnings',
        'Estimate of the population (25 years and over) with a Bachelor’s degree (regardless of place of birth)'
      );
    """

    df = pd.read_sql(query, conn, params=(county_id,))
    conn.close()

    # Rename the VARIABLE VALUE, not the column
    df["variable"] = df["variable"].replace({
        "Estimate of the population (25 years and over) with a Bachelor’s degree (regardless of place of birth)":
        "Overall Bachelor's degree population"
    })

    # Convert to dict
    data_dict = df.set_index("variable")["value"].to_dict()

    return data_dict

print(fetch_county_census_data('01009'))  # Example usage