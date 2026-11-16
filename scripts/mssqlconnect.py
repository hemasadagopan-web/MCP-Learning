
import pyodbc

conn = pyodbc.connect(
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=localhost\\SQLEXPRESS;"
    "DATABASE=customers;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

cursor = conn.cursor()

cursor.execute("SELECT top (100) cst_id FROM bronze.crm_cust_info")

for row in cursor.fetchall():
    print(row)

cursor.close()
conn.close()
