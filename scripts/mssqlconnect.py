
import pyodbc

conn = pyodbc.connect(
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=localhost\\SQLEXPRESS;"
    "DATABASE=customers;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

cursor = conn.cursor()

cursor.execute("SELECT * FROM dbo.details")

for row in cursor.fetchall():
    print(row)

cursor.close()
conn.close()
