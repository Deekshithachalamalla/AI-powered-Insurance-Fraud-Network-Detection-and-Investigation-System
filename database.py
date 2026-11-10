
import sqlite3

# Create database
connection = sqlite3.connect("company.db")

# Create cursor
cursor = connection.cursor()

# Create employee table
cursor.execute("""
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY,
    name TEXT,
    age INTEGER,
    salary REAL,
    department TEXT
)
""")

# Insert employee records
employees = [
    (1, "Rahul", 25, 30000, "IT"),
    (2, "Priya", 24, 35000, "HR"),
    (3, "Arjun", 27, 45000, "IT"),
    (4, "Sneha", 23, 32000, "Finance"),
    (5, "Kiran", 26, 40000, "IT")
]

cursor.executemany("""
INSERT OR REPLACE INTO employees
(id, name, age, salary, department)
VALUES (?, ?, ?, ?, ?)
""", employees)

# Save changes
connection.commit()

print("Database created successfully!")

# Display records
cursor.execute("SELECT * FROM employees")

for row in cursor.fetchall():
    print(row)

connection.close()
