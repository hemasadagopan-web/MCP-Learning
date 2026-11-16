
import mysql.connector

def conn():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="customers"
    )


# READ - Get all records
def read_details():
    c = conn()
    cur = c.cursor(dictionary=True)

    cur.execute("SELECT * FROM details")
    rows = cur.fetchall()

    cur.close()
    c.close()
    return rows


# INSERT - Add a new record
def insert_details(name, gender, country):
    c = conn()
    cur = c.cursor()

    cur.execute(
        "INSERT INTO details (name, gender, country) VALUES (%s, %s, %s)",
        (name, gender, country)
    )

    c.commit()
    cur.close()
    c.close()
    return {"status": "inserted"}


# UPDATE - Update a record using name
def update_details(old_name, name, gender, country):
    c = conn()
    cur = c.cursor()

    cur.execute(
        "UPDATE details SET name=%s, gender=%s, country=%s WHERE name=%s",
        (name, gender, country, old_name)
    )

    c.commit()
    cur.close()
    c.close()
    return {"status": "updated", "rows_affected": cur.rowcount}


# DELETE - Delete a record using name
def delete_details(name):
    c = conn()
    cur = c.cursor()

    cur.execute(
        "DELETE FROM details WHERE name=%s",
        (name,)
    )

    c.commit()
    deleted = cur.rowcount

    cur.close()
    c.close()
    return {"status": "deleted", "rows_affected": deleted}
