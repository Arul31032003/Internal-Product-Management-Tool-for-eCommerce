import os
from flask import (
    Flask, render_template, request, redirect, url_for, jsonify, flash
)
from werkzeug.utils import secure_filename
from config import FLASK_SECRET

# service imports (your existing service modules)
from services.category_service import (
    list_categories, create_category, get_category,
    update_category, delete_category
)
from services.attribute_service import (
    list_attributes_for_category, create_attribute
)
from services.product_service import (
    create_product, get_product, list_products_simple
)

# Upload folder
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.secret_key = FLASK_SECRET
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# -------------------------
# Home / Dashboard
# -------------------------
@app.route('/')
def index():
    cats = list_categories()
    prods = list_products_simple()
    # be defensive if services return None
    cats = cats or []
    prods = prods or []
    cats.sort(key=lambda c: c.get('CategoryID', 0))
    return render_template('index.html', categories=cats, products=prods, dashboard_page=True)


# -------------------------
# Categories: list + create
# -------------------------
@app.route('/categories', methods=['GET', 'POST'])
def categories():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        desc = request.form.get('description', '').strip()
        if not name:
            flash('Name is required', 'error')
            return redirect(url_for('categories'))
        create_category(name, desc)
        flash('Category added', 'success')
        return redirect(url_for('categories'))

    cats = list_categories() or []
    cats.sort(key=lambda c: c.get('CategoryID', 0))
    return render_template('categories.html', categories=cats, dashboard_page=False)


# -------------------------
# Edit Category (AJAX/form)
# -------------------------
@app.route('/categories/edit/<int:cat_id>', methods=['POST'])
def edit_category(cat_id):
    # Support both application/x-www-form-urlencoded (request.form)
    # and JSON payloads (request.get_json())
    data = {}
    if request.is_json:
        data = request.get_json() or {}
    else:
        data['name'] = request.form.get('name', '')
        data['description'] = request.form.get('description', '')

    name = (data.get('name') or '').strip()
    description = (data.get('description') or '').strip()

    if not name:
        return jsonify({'status': 'error', 'message': 'Name required'}), 400

    # Update in service
    update_category(cat_id, name, description)
    return jsonify({'status': 'success'})


# -------------------------
# Delete Category (AJAX)
# -------------------------
@app.route('/categories/delete/<int:cat_id>', methods=['POST'])
def delete_category_route(cat_id):
    # You may want to check for related objects before deleting in service layer
    delete_category(cat_id)
    return jsonify({'status': 'success'})


# -------------------------
# Manage Attributes for Category
# -------------------------
@app.route('/categories/<int:cat_id>/attributes', methods=['GET', 'POST'])
def attributes(cat_id):
    cat = get_category(cat_id)
    if not cat:
        return "Category not found", 404

    if request.method == 'POST':
        # attribute form fields: name, slug, data_type, required (checkbox)
        name = request.form.get('name', '').strip()
        slug = request.form.get('slug', '').strip()
        dtype = request.form.get('data_type', '').strip()
        required = 1 if request.form.get('required') else 0

        if not name or not slug:
            flash('Attribute name and slug are required', 'error')
            return redirect(url_for('attributes', cat_id=cat_id))

        create_attribute(cat_id, name, slug, dtype, required)
        flash('Attribute added', 'success')
        return redirect(url_for('attributes', cat_id=cat_id))

    attrs = list_attributes_for_category(cat_id) or []
    return render_template('attributes.html', category=cat, attributes=attrs, dashboard_page=False)


# -------------------------
# Products list
# -------------------------
@app.route('/products')
def products():
    prods = list_products_simple() or []
    return render_template('products.html', products=prods, dashboard_page=False)


# -------------------------
# Add product to a category (form + file uploads)
# -------------------------
@app.route('/products/add/<int:cat_id>', methods=['GET', 'POST'])
def add_product(cat_id):
    cat = get_category(cat_id)
    if not cat:
        return 'Category not found', 404

    attrs = list_attributes_for_category(cat_id) or []

    if request.method == 'POST':
        # normalize price
        price_raw = request.form.get('price', '').strip()
        try:
            price = float(price_raw) if price_raw else 0.0
        except ValueError:
            price = 0.0

        # handle uploaded files list (images)
        uploaded_files = request.files.getlist('images')

        # build payload — attribute keys expected as Slug in attribute objects
        payload = {
            'name': request.form.get('name', '').strip(),
            'sku': request.form.get('sku', '').strip(),
            'price': price,
            'category_id': cat_id,
            'attributes': {a.get('Slug'): request.form.get(a.get('Slug')) for a in attrs}
        }

        # delegate creation to product service (should save images and return product id)
        prod_id = create_product(payload, uploaded_files=uploaded_files)
        flash('Product created successfully!', 'success')
        return redirect(url_for('product_detail', product_id=prod_id))

    return render_template('product_form.html', category=cat, attributes=attrs, dashboard_page=False)


# -------------------------
# Product detail
# -------------------------
@app.route('/products/<int:product_id>')
def product_detail(product_id):
    prod = get_product(product_id)
    if not prod:
        return 'Product not found', 404
    # 'attributes' key expected on product dict (service-controlled)
    return render_template('product_detail.html', product=prod, details=prod.get('attributes', []), dashboard_page=False)


# -------------------------
# Run
# -------------------------
if __name__ == '__main__':
    app.run(debug=True)
