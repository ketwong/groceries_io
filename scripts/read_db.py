import sqlite3
import os

# Correct the path to your database file
database_path = os.path.join(os.path.dirname(__file__), '..', 'instance', 'results.db')

# Connect to the SQLite database
conn = sqlite3.connect(database_path)

# Create a cursor object
cursor = conn.cursor()

# Execute a query
cursor.execute("SELECT * FROM image_result")  # Ensure the table name is correct

# Fetch column names
columns = [description[0] for description in cursor.description]

# Fetch all rows from the query
rows = cursor.fetchall()

# Print column names
print("Columns:", columns)

# Print the rows
for row in rows:
    print(row)

# Close the connection
conn.close()
