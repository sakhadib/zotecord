import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect("zotero.sqlite")

# Get the schema using a query on sqlite_master
cursor = conn.cursor()
cursor.execute("SELECT sql FROM sqlite_master WHERE sql IS NOT NULL;")
schema_statements = cursor.fetchall()

# Write the schema to schema.txt
with open("schema.txt", "w", encoding="utf-8") as f:
    for stmt in schema_statements:
        f.write(stmt[0] + ";\n\n")

# Clean up
conn.close()

print("Schema has been saved to schema.txt")
