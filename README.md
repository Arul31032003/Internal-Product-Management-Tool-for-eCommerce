# Internal Product Management Tool (Modular)
Flask + pyodbc project (modular) for managing categories, attributes and products.

## Structure
- app.py                -> Flask routes (imports services)
- config.py             -> Configuration (DB conn)
- db.py                 -> DB connection helpers (pyodbc)
- services/
    - category_service.py
    - attribute_service.py
    - product_service.py
- templates/            -> Jinja2 templates (HTML)
- static/style.css      -> Basic styling
- schema.sql            -> SQL Server schema to create the database/tables

## Setup
1. Create the database in SQL Server by running `schema.sql` (use SSMS).
2. Install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Set environment variable `PRODUCT_DB_CONN` with your ODBC connection string:
   Example:
   ```
   DRIVER={ODBC Driver 18 for SQL Server};SERVER=127.0.0.1,1433;DATABASE=ProductMgmt;UID=sa;PWD=YourPassword;TrustServerCertificate=yes
   ```
   On Windows (PowerShell):
   ```
   $env:PRODUCT_DB_CONN='DRIVER={ODBC Driver 18 for SQL Server};SERVER=localhost,1433;DATABASE=ProductMgmt;UID=sa;PWD=YourPassword;TrustServerCertificate=yes'
   ```
4. Run the app:
   ```bash
   python app.py
   ```
5. Open `http://127.0.0.1:5000/`.
