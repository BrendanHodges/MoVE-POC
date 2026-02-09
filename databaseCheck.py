from app.db import get_db_connection
import pandas as pd

conn = get_db_connection()

def counties_missing_questions(conn):
    query = """
        WITH expected_questions AS (
            SELECT question_id FROM questions
        ),
        county_base AS (
            SELECT DISTINCT county_id FROM responses
        )
        SELECT
            c.name,
            c.state_id,
            c.county_id,
            GROUP_CONCAT(q.question_id, ', ') AS missing_questions
        FROM county_base cb
        CROSS JOIN expected_questions q
        LEFT JOIN responses r
            ON r.county_id = cb.county_id
           AND r.question_id = q.question_id
        JOIN counties c
            ON c.county_id = cb.county_id
        WHERE r.question_id IS NULL AND q.question_id NOT IN (10)
        GROUP BY c.county_id, c.name, c.state_id
        ORDER BY c.state_id, c.name;
    """

    rows = conn.execute(query).fetchall()

    if not rows:
        print("All counties have complete question coverage.")
        return rows

    print("Counties missing one or more questions:")
    print(f"{len(rows)} counties found.\n")

    for row in rows:
        print(
            f"{row['name']} ({row['state_id']}, {row['county_id']}): "
            f"missing questions → {row['missing_questions']}"
        )

    return rows

def find_duplicate_county_questions(conn):
    query = """
        SELECT
            r.county_id,
            c.name AS county_name,
            c.state_id,
            r.question_id,
            COUNT(*) AS response_count
        FROM responses r
        JOIN counties c
            ON c.county_id = r.county_id
        GROUP BY r.county_id, c.name, c.state_id, r.question_id
        HAVING COUNT(*) > 1
        ORDER BY c.state_id, c.name, r.question_id;
    """

    rows = conn.execute(query).fetchall()

    if not rows:
        print("No duplicate county–question pairs found.")
        return rows

    print("Duplicate county–question pairs detected:")
    print(f"{len(rows)} violations found.\n")

    for row in rows:
        print(
            f"{row['county_name']} ({row['state_id']}, {row['county_id']}), "
            f"Question {row['question_id']} → {row['response_count']} responses"
        )

    return rows

def find_high_values(conn):
    query = """
        SELECT c.county_id, c.name, c.state_id, q.question_id, q.question, r.value
        FROM responses r, counties c, questions q
        WHERE r.county_id = c.county_id
          AND r.question_id = q.question_id
          AND q.question_id NOT IN (32, 33, 10)
          AND r.value >= 2
          ORDER BY c.state_id, c.name;"""
    
    rows = conn.execute(query).fetchall()
    print("\nHigh values for questions 10, 32, 33 (value > 2):")
    for row in rows:
        print(
            f"{row['name']} ({row['state_id']}, {row['county_id']}): "
            f"Q{row['question_id']} '{row['question']}' → {row['value']}"
        )
    return rows

def dump_sqlite_schema(conn):
    cur = conn.cursor()

    print("\n=== TABLE DEFINITIONS (sqlite_master) ===")
    cur.execute("""
        SELECT name, sql
        FROM sqlite_master
        WHERE type = 'table'
          AND name NOT LIKE 'sqlite_%'
        ORDER BY name;
    """)
    for row in cur.fetchall():
        print(f"\n--- {row['name']} ---")
        print(row['sql'])

    cur.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
          AND name NOT LIKE 'sqlite_%'
        ORDER BY name;
    """)

    tables = [r["name"] for r in cur.fetchall()]

    for table in tables:
        print(f"\n=== TABLE: {table} ===")

        print("\nColumns:")
        cur.execute(f"PRAGMA table_info({table});")
        for c in cur.fetchall():
            print(
                f"  {c['name']} {c['type']}"
                f"{' NOT NULL' if c['notnull'] else ''}"
                f"{' PRIMARY KEY' if c['pk'] else ''}"
                f"{f' DEFAULT {c['dflt_value']}' if c['dflt_value'] is not None else ''}"
            )

        print("\nForeign Keys:")
        cur.execute(f"PRAGMA foreign_key_list({table});")
        fks = cur.fetchall()
        if not fks:
            print("  (none)")
        else:
            for fk in fks:
                print(
                    f"  {fk['from']} → {fk['table']}.{fk['to']} "
                    f"(on_update={fk['on_update']}, on_delete={fk['on_delete']})"
                )

        print("\nIndexes:")
        cur.execute(f"PRAGMA index_list({table});")
        indexes = cur.fetchall()
        if not indexes:
            print("  (none)")
        else:
            for idx in indexes:
                print(f"  {idx['name']} (unique={bool(idx['unique'])})")
                cur.execute(f"PRAGMA index_info({idx['name']});")
                cols = [r["name"] for r in cur.fetchall()]
                print(f"    columns: {cols}")

    conn.close()


def state_sums(state_abbrev):
    def get_move_equation_scores(state) -> pd.DataFrame:
        conn = get_db_connection()
        cur = conn.cursor()

        query = """
            SELECT
                C.county_id,
                C.name AS county_name,
                C.state_id AS state_id,
                Q.question_id,
                Q.question,
                Q.category,
                R.value AS response_value
            FROM Responses R
            JOIN Counties C ON C.county_id = R.county_id
            JOIN Questions Q ON Q.question_id = R.question_id
            WHERE C.state_abbrev = ? AND q.question_id NOT IN (10)
            ORDER BY C.county_id, Q.question_id
            """
        cur.execute(query, (state,))
        rows = cur.fetchall()
        conn.close()
        return pd.DataFrame([dict(r) for r in rows])
    def build_category_scores(df: pd.DataFrame) -> pd.DataFrame:
        df_cat = (
            df.groupby(["county_id", "county_name", "state_id", "category"], as_index=False)["response_value"]
            .sum()
            .rename(columns={"response_value": "category_score"})
        )

        print(df_cat)

        df_wide = (
            df_cat.pivot_table(
                index=["county_id", "county_name", "state_id"],
                columns="category",
                values="category_score",
                aggfunc="first"
            )
            .reset_index()
        )

        df_wide.columns.name = None
        df_wide.drop(columns = ['county_id', 'state_id'], inplace=True)
        return df_wide
    df = get_move_equation_scores(state_abbrev)
    df_wide = build_category_scores(df)
    print(df_wide)
    df_wide.to_csv(f'{state_abbrev.lower()}_move_equation_scores.csv', index=False)


print("\nLETS RUN THROUGH A DATABASE CHECK AND SCORE\n")
input("Press Enter to continue...")

missing_question = input("\n1. Check counties missing questions (Y or N): ")
if missing_question.lower() == 'y':
    print("\n==============================================")
    print("Checking for counties missing questions...")
    counties_missing_questions(conn)

high_values = input("\n2. Check for high values in certain questions (Y or N): ")
if high_values.lower() == 'y':
    print("\n==============================================")
    print("Finding high values for questions 10, 32, 33...")
    find_high_values(conn)

duplicate_check = input("\n3. Check for duplicate county-question pairs (Y or N): ")
if duplicate_check.lower() == 'y':
    print("\n==============================================")
    print("Checking for duplicate county-question pairs...")
    find_duplicate_county_questions(conn)

while True:
    state_cat_sums = input("\n4. Get state category sums (Y or N): ").strip().lower()

    if state_cat_sums == 'y':
        print("\n==============================================")
        state_abbrev = input("Enter state abbreviation (e.g., 'MD'): ").strip().upper()
        print("Getting state category sums...")
        state_sums(state_abbrev)

    elif state_cat_sums == 'n':
        print("Exiting state category sums.")
        break

    else:
        print("Please enter Y or N.")





