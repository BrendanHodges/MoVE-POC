from app.db import get_db_connection
import pandas as pd

conn = get_db_connection()

def counties_missing_questions(conn):
    """
    Prints and returns counties along with the specific questions they are missing.
    """

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
        WHERE r.question_id IS NULL 
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


counties_missing_questions(conn)

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
find_high_values(conn)


def get(conn):
    query = """SELECT sql FROM sqlite_master
        WHERE type='table' AND name='responses';"""
    
    rows = conn.execute(query).fetchall()
    for row in rows:
        print(row['sql'])

get(conn)


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
