
from fastapi import FastAPI
import pyodbc

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Welcome to my FastAPI application"}

def conn():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 18 for SQL Server};"
        "SERVER=localhost\\SQLEXPRESS;"
        "DATABASE=customers;"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )

@app.get("/tasks")
def get_tasks():
    c = conn()
    cur = c.cursor()

    cur.execute("SELECT * FROM dbo.details")

    columns = [column[0] for column in cur.description]
    rows = [dict(zip(columns, row)) for row in cur.fetchall()]

    cur.close()
    c.close()

    return rows


@app.post("/tasks/{name}")
def insert_task(name: str, gender: str, country: str):
    c = conn()
    cur = c.cursor()

    cur.execute(
        "INSERT INTO dbo.details (name, gender, country) VALUES (?, ?, ?)",
        (name, gender, country)
    )

    c.commit()
    cur.close()
    c.close()

    return {"status": "inserted"}


@app.delete("/tasks/{name}")
def delete_task(name: str):
    c = conn()
    cur = c.cursor()

    cur.execute("DELETE FROM dbo.details WHERE name = ?", (name,))

    c.commit()
    deleted = cur.rowcount

    cur.close()
    c.close()

    return {"status": "deleted", "rows_affected": deleted}
