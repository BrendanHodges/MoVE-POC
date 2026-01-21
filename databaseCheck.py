from app.db import get_db_connection
import pandas as pd

conn = get_db_connection()

def counties_missing_responses(conn, expected_questions=34):
    """
    Returns counties that do not have exactly `expected_questions`
    unique question responses.
    """

    query = """
        SELECT
            c.name,
            c.state_id,
            c.county_id,
            COUNT(DISTINCT r.question_id) AS question_count
        FROM responses r
        JOIN counties c
            ON r.county_id = c.county_id
        GROUP BY c.county_id, c.name, c.state_id
        HAVING COUNT(DISTINCT r.question_id) <> ?
        ORDER BY question_count;
    """

    return conn.execute(query, (expected_questions,)).fetchall()

bad_counties = counties_missing_responses(conn)
if bad_counties:
    print("Counties with missing or extra responses:")
    print(len(bad_counties), "counties found.")
    for county in bad_counties:
        print(f"{county['name']}, {county['county_id']}, {county['state_id']}: {county['question_count']} responses")
    
conn.close()