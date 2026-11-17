import pyodbc

def conn():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 18 for SQL Server};"
        "SERVER=localhost\\SQLEXPRESS;"
        "DATABASE=customers;"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )


# READ
def read_details():
    c = conn()
    cur = c.cursor()

    cur.execute("SELECT * FROM dbo.details")

    columns = [column[0] for column in cur.description]
    rows = [dict(zip(columns, row)) for row in cur.fetchall()]

    cur.close()
    c.close()

    return rows


# INSERT
def insert_details(name, gender, country):
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


# UPDATE
def update_details(old_name, name, gender, country):
    c = conn()
    cur = c.cursor()

    cur.execute(
        """UPDATE dbo.details
           SET name = ?, gender = ?, country = ?
           WHERE name = ?""",
        (name, gender, country, old_name)
    )

    c.commit()
    affected = cur.rowcount

    cur.close()
    c.close()

    return {"status": "updated", "rows_affected": affected}


# DELETE
def delete_details(name):
    c = conn()
    cur = c.cursor()

    cur.execute(
        "DELETE FROM dbo.details WHERE name = ?",
        (name,)
    )

    c.commit()
    affected = cur.rowcount

    cur.close()
    c.close()

    return {"status": "deleted", "rows_affected": affected}
