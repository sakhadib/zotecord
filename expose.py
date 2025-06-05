# expose.py

import sqlite3
import sys
import os

def dump_sqlite(db_path: str, out_path: str):
    if not os.path.isfile(db_path):
        print(f"❌ Error: file not found: {db_path}")
        return

    # Open the SQLite DB in read-only mode
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    cur = conn.cursor()

    with open(out_path, "w", encoding="utf-8") as f:
        def writeln(line=""):
            f.write(line + "\n")

        writeln(f"--- SQLite Dump of {db_path} (first 5 rows per table) ---\n")

        # 1) Dump sqlite_master entries (all tables, indexes, views, triggers)
        writeln("#\n# Schema Objects (sqlite_master)\n#")
        cur.execute("SELECT type, name, tbl_name, sql FROM sqlite_master ORDER BY type, name;")
        rows = cur.fetchall()
        if not rows:
            writeln("No sqlite_master entries found.\n")
        else:
            for r in rows:
                typ, name, tbl_name, sql_stmt = r
                writeln(f"• TYPE: {typ}")
                writeln(f"  NAME: {name}")
                writeln(f"  TABLE: {tbl_name}")
                writeln("  SQL:")
                if sql_stmt:
                    for line in sql_stmt.splitlines():
                        writeln(f"    {line}")
                else:
                    writeln("    <NULL>")
                writeln()

        # 2) Identify all user tables (skip internal sqlite_ tables)
        cur.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
              AND name NOT LIKE 'sqlite_%'
            ORDER BY name;
        """)
        tables = [r[0] for r in cur.fetchall()]

        if not tables:
            writeln("#\n# No user-defined tables found.\n#")
        else:
            # 3) For each table, dump column info and up to first 5 rows
            for tbl in tables:
                writeln(f"#\n# Table: {tbl}\n#")

                # 3a) Column info
                writeln("## Columns (PRAGMA table_info):")
                cur.execute(f"PRAGMA table_info('{tbl}')")
                cols = cur.fetchall()
                if cols:
                    # cols: [(cid, name, type, notnull, default_value, pk), ...]
                    writeln("  cid | name | type | notnull | default_value | pk")
                    for col in cols:
                        cid, name, ctype, notnull, dflt, pk = col
                        dv = dflt if dflt is not None else "NULL"
                        writeln(f"   {cid}  | {name} | {ctype} | {notnull} | {dv} | {pk}")
                else:
                    writeln("  <no columns?>")
                writeln()

                # 3b) Up to first 5 data rows
                writeln("## First 5 Data Rows:")
                try:
                    # Only fetch up to 5 rows
                    cur.execute(f"SELECT * FROM '{tbl}' LIMIT 5;")
                    first_rows = cur.fetchall()
                    col_names = [d[0] for d in cur.description]

                    # Write header
                    writeln("  | ".join(col_names))
                    writeln("-" * (len("  | ".join(col_names)) + 2))
                    if first_rows:
                        for row in first_rows:
                            # Represent each cell with repr(), so blobs etc are visible
                            row_repr = [repr(cell) for cell in row]
                            writeln("  | ".join(row_repr))
                        if len(first_rows) < 5:
                            writeln(f"  <only {len(first_rows)} rows available>")
                    else:
                        writeln("  <no rows>")
                except Exception as e:
                    writeln(f"  ❌ Error reading data from {tbl}: {e}")
                writeln()

        conn.close()
        writeln(f"--- End of dump ---")

    print(f"✅ Dump complete: {out_path}")


if __name__ == "__main__":
    # if len(sys.argv) < 2:
    #     print("Usage: python expose.py path/to/database.sqlite [output.txt]")
    #     sys.exit(1)

    sqlite_path = r"C:\Users\sakha\Zotero\zotero.sqlite"
    output_file = sys.argv[2] if len(sys.argv) >= 3 else "dump.txt"
    dump_sqlite(sqlite_path, output_file)
