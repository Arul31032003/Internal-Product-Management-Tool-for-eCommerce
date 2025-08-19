from db import get_conn, fetchall_dict

def list_attributes_for_category(cat_id):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT AttributeDefID, Name, Slug, DataType, IsRequired FROM AttributeDefinitions WHERE CategoryID = ?",
                    (cat_id,))
        return fetchall_dict(cur)

def create_attribute(category_id, name, slug, data_type, is_required):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""INSERT INTO AttributeDefinitions
                       (CategoryID, Name, Slug, DataType, IsRequired)
                       VALUES (?, ?, ?, ?, ?)""",
                    (category_id, name, slug, data_type, is_required))
        conn.commit()
