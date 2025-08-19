from db import get_conn, fetchall_dict
from datetime import datetime
import json
import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static/uploads'

def list_products_simple():
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT p.ProductID, p.Name, p.SKU, p.Price, c.Name as CategoryName
            FROM Products p
            JOIN Categories c ON p.CategoryID=c.CategoryID
            ORDER BY p.CreatedAt DESC
        """)
        products = fetchall_dict(cur)

        # Attach images
        for p in products:
            cur.execute("SELECT ImagePath FROM ProductImages WHERE ProductID=? ORDER BY ImageID", (p['ProductID'],))
            imgs = fetchall_dict(cur)
            p['images'] = [i['ImagePath'] for i in imgs]

        return products


def create_product(payload, uploaded_files=None):
    """
    payload: {'name','sku','price','category_id','attributes':{slug:val,...}}
    uploaded_files: list of FileStorage objects (from Flask request.files.getlist)
    """
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO Products (CategoryID, Name, SKU, Price, IsActive, CreatedAt)
            OUTPUT INSERTED.ProductID
            VALUES (?, ?, ?, ?, 1, ?)
        """, (payload['category_id'], payload['name'], payload['sku'], payload['price'], datetime.utcnow()))
        prod_id = int(cur.fetchone()[0])

        # Insert attributes (same as before)
        cur.execute("SELECT AttributeDefID, Slug, DataType FROM AttributeDefinitions WHERE CategoryID = ?", (payload['category_id'],))
        defs = fetchall_dict(cur)
        for d in defs:
            val = payload['attributes'].get(d['Slug'])
            dt = (d['DataType'] or '').lower()
            if val in (None, ''):
                cur.execute("INSERT INTO ProductAttributeValues (ProductID, AttributeDefID) VALUES (?, ?)", (prod_id, d['AttributeDefID']))
            else:
                if dt in ('int', 'integer'):
                    cur.execute("INSERT INTO ProductAttributeValues (ProductID, AttributeDefID, ValueInt) VALUES (?, ?, ?)", (prod_id, d['AttributeDefID'], int(val)))
                elif dt in ('float', 'double'):
                    cur.execute("INSERT INTO ProductAttributeValues (ProductID, AttributeDefID, ValueFloat) VALUES (?, ?, ?)", (prod_id, d['AttributeDefID'], float(val)))
                elif dt in ('bool', 'boolean'):
                    v = 1 if str(val).lower() in ('1','true','yes','on') else 0
                    cur.execute("INSERT INTO ProductAttributeValues (ProductID, AttributeDefID, ValueBool) VALUES (?, ?, ?)", (prod_id, d['AttributeDefID'], v))
                else:
                    cur.execute("INSERT INTO ProductAttributeValues (ProductID, AttributeDefID, ValueString) VALUES (?, ?, ?)", (prod_id, d['AttributeDefID'], val))

        # Insert uploaded images
        if uploaded_files:
            for file in uploaded_files:
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
                    filename = f"{timestamp}_{filename}"
                    path = os.path.join(UPLOAD_FOLDER, filename)
                    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                    file.save(path)
                    db_path = f"uploads/{filename}"
                    cur.execute("INSERT INTO ProductImages (ProductID, ImagePath) VALUES (?, ?)", (prod_id, db_path))

        conn.commit()
        return prod_id


def get_product(product_id):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT p.ProductID, p.Name, p.SKU, p.Price, c.Name as CategoryName, p.CategoryID
            FROM Products p JOIN Categories c ON p.CategoryID=c.CategoryID
            WHERE p.ProductID = ?
        """, (product_id,))
        row = cur.fetchone()
        if not row:
            return None
        product = {'ProductID': row.ProductID, 'Name': row.Name, 'SKU': row.SKU, 'Price': row.Price, 'CategoryName': row.CategoryName}

        # Fetch attributes
        cur.execute("""
            SELECT adv.AttributeDefID, adv.Name as AttrName, adv.Slug, adv.DataType,
                   pav.ValueString, pav.ValueInt, pav.ValueFloat, pav.ValueBool, pav.ValueJSON
            FROM ProductAttributeValues pav
            JOIN AttributeDefinitions adv ON pav.AttributeDefID = adv.AttributeDefID
            WHERE pav.ProductID = ?
        """, (product_id,))
        rows = fetchall_dict(cur)
        details = []
        for r in rows:
            val = None
            dt = (r.get('DataType') or '').lower()
            if dt in ('int','integer'):
                val = r.get('ValueInt')
            elif dt in ('float','double'):
                val = r.get('ValueFloat')
            elif dt in ('bool','boolean'):
                val = r.get('ValueBool')
            elif r.get('ValueString') is not None:
                val = r.get('ValueString')
            elif r.get('ValueJSON') is not None:
                try:
                    val = json.loads(r.get('ValueJSON'))
                except:
                    val = r.get('ValueJSON')
            details.append({'name': r.get('AttrName'), 'type': r.get('DataType'), 'value': val})
        product['attributes'] = details

        # Fetch images
        cur.execute("SELECT ImagePath FROM ProductImages WHERE ProductID=? ORDER BY ImageID", (product_id,))
        imgs = fetchall_dict(cur)
        product['images'] = [i['ImagePath'] for i in imgs]

        return product
