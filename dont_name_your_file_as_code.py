from eralchemy2 import render_er

# Path to the SQLite database
db_path = "sqlite:///db.sqlite3"

# Generate an ER diagram 
render_er(db_path, "db_schema.png")

print("Database schema saved as db_schema.png")

