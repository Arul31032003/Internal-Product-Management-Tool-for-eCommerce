from db import get_conn, fetchall_dict

def list_categories():
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT CategoryID, Name, Description FROM Categories ORDER BY Name")
        return fetchall_dict(cur)

def create_category(name, description=''):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO Categories (Name, Description) VALUES (?, ?)", (name, description))
        conn.commit()

def get_category(cat_id):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT CategoryID, Name, Description FROM Categories WHERE CategoryID = ?", (cat_id,))
        row = cur.fetchone()
        if not row:
            return None
        return {'CategoryID': row.CategoryID, 'Name': row.Name, 'Description': row.Description}

def update_category(cat_id, name, description=''):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE Categories SET Name = ?, Description = ? WHERE CategoryID = ?",
            (name, description, cat_id)
        )
        conn.commit()

def delete_category(cat_id):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM Categories WHERE CategoryID = ?", (cat_id,))
        conn.commit()
