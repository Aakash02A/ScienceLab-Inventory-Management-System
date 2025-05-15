from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import sqlite3
import os
import bcrypt
from datetime import datetime, timedelta
import json

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key_here')

# Database path
DATABASE = 'laboratory.db'

# Initialize the database
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        name TEXT NOT NULL,
        email TEXT,
        role TEXT CHECK(role IN ('admin', 'lab_manager', 'researcher', 'student')) NOT NULL,
        department TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create locations table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS locations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        capacity INTEGER,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create suppliers table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS suppliers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        contact_person TEXT,
        email TEXT,
        phone TEXT,
        address TEXT,
        notes TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create items table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT CHECK(category IN ('chemicals', 'equipment', 'consumables', 'glassware')) NOT NULL,
        description TEXT,
        barcode TEXT UNIQUE,
        quantity REAL NOT NULL,
        unit TEXT CHECK(unit IN ('units', 'bottles', 'boxes', 'packs', 'grams', 'liters')),
        min_quantity REAL,
        price REAL,
        location_id INTEGER,
        supplier_id INTEGER,
        expiry_date TEXT,
        hazard_type TEXT CHECK(hazard_type IN ('flammable', 'corrosive', 'toxic', 'oxidizing', 'explosive', 'harmful', 'irritant', 'environmental')),
        storage_condition TEXT CHECK(storage_condition IN ('room_temperature', 'refrigerated', 'frozen', 'dry', 'dark', 'ventilated')),
        msds_url TEXT,
        status TEXT CHECK(status IN ('in_stock', 'low_stock', 'out_of_stock', 'expiring_soon')) DEFAULT 'in_stock',
        last_updated_by INTEGER,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (location_id) REFERENCES locations (id),
        FOREIGN KEY (supplier_id) REFERENCES suppliers (id),
        FOREIGN KEY (last_updated_by) REFERENCES users (id)
    )
    ''')
    
    # Create transactions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        quantity REAL NOT NULL,
        type TEXT CHECK(type IN ('check_in', 'check_out', 'restock', 'dispose')) NOT NULL,
        notes TEXT,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (item_id) REFERENCES items (id),
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Create orders table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        supplier_id INTEGER,
        ordered_by INTEGER NOT NULL,
        approved_by INTEGER,
        status TEXT CHECK(status IN ('pending', 'approved', 'ordered', 'received', 'cancelled')) DEFAULT 'pending',
        notes TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (supplier_id) REFERENCES suppliers (id),
        FOREIGN KEY (ordered_by) REFERENCES users (id),
        FOREIGN KEY (approved_by) REFERENCES users (id)
    )
    ''')
    
    # Create order_items table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        item_id INTEGER,
        name TEXT NOT NULL,
        quantity REAL NOT NULL,
        unit TEXT,
        price REAL,
        FOREIGN KEY (order_id) REFERENCES orders (id),
        FOREIGN KEY (item_id) REFERENCES items (id)
    )
    ''')
    
    # Insert default admin user if not exists
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
    if cursor.fetchone()[0] == 0:
        # Hash the password
        hashed_password = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute('''
        INSERT INTO users (username, password, name, email, role, department)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', ('admin', hashed_password, 'Administrator', 'admin@lab.edu', 'admin', 'Administration'))
    
    # Insert sample locations if empty
    cursor.execute("SELECT COUNT(*) FROM locations")
    if cursor.fetchone()[0] == 0:
        locations = [
            ('Storage Room A', 'Main chemical storage room', 500),
            ('Equipment Room B', 'Scientific equipment storage', 250),
            ('Cold Storage', 'Refrigerated storage for temperature sensitive items', 100)
        ]
        cursor.executemany('''
        INSERT INTO locations (name, description, capacity)
        VALUES (?, ?, ?)
        ''', locations)
    
    # Insert sample suppliers if empty
    cursor.execute("SELECT COUNT(*) FROM suppliers")
    if cursor.fetchone()[0] == 0:
        suppliers = [
            ('Sigma-Aldrich', 'John Smith', 'jsmith@sigma.com', '555-123-4567', '123 Science Blvd, St. Louis, MO'),
            ('Fisher Scientific', 'Jane Doe', 'jdoe@fisher.com', '555-987-6543', '456 Lab Ave, Pittsburgh, PA'),
            ('VWR International', 'Bob Johnson', 'bjohnson@vwr.com', '555-456-7890', '789 Research Rd, Radnor, PA')
        ]
        cursor.executemany('''
        INSERT INTO suppliers (name, contact_person, email, phone, address)
        VALUES (?, ?, ?, ?, ?)
        ''', suppliers)
    
    # Create recommendations table for storing personalized recommendations
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS recommendations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        item_id INTEGER NOT NULL,
        score REAL NOT NULL,
        reason TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (item_id) REFERENCES items (id)
    )
    ''')
    
    # Create equipment_maintenance table for tracking maintenance history
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS equipment_maintenance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        equipment_id INTEGER NOT NULL,
        maintenance_date TEXT NOT NULL,
        maintenance_type TEXT CHECK(maintenance_type IN ('routine', 'repair', 'calibration', 'inspection')) NOT NULL,
        status TEXT CHECK(status IN ('scheduled', 'completed', 'postponed', 'canceled')) NOT NULL,
        technician TEXT,
        description TEXT,
        cost REAL,
        hours_used_before INTEGER,
        issue_detected TEXT,
        parts_replaced TEXT,
        notes TEXT,
        created_by INTEGER,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (equipment_id) REFERENCES items (id),
        FOREIGN KEY (created_by) REFERENCES users (id)
    )
    ''')
    
    # Create equipment_usage table for tracking usage
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS equipment_usage (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        equipment_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        start_time TEXT NOT NULL,
        end_time TEXT,
        duration INTEGER,
        project TEXT,
        notes TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (equipment_id) REFERENCES items (id),
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Create maintenance_predictions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS maintenance_predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        equipment_id INTEGER NOT NULL,
        prediction_date TEXT NOT NULL,
        maintenance_type TEXT NOT NULL,
        confidence_score REAL NOT NULL,
        predicted_issue TEXT,
        days_until_maintenance INTEGER,
        is_critical BOOLEAN DEFAULT 0,
        last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (equipment_id) REFERENCES items (id)
    )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

# Helper function to convert SQLite rows to dictionaries
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

# Initialize database
init_db()

# Authentication check decorator
def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__  # Preserve the function name
    return decorated_function

# Role check decorator
def role_required(allowed_roles):
    def decorator(f):
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in first.', 'danger')
                return redirect(url_for('login'))
            
            # Get the user's role
            conn = sqlite3.connect(DATABASE)
            conn.row_factory = dict_factory
            cursor = conn.cursor()
            cursor.execute("SELECT role FROM users WHERE id = ?", (session['user_id'],))
            user = cursor.fetchone()
            conn.close()
            
            if not user or user['role'] not in allowed_roles:
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('dashboard'))
            
            return f(*args, **kwargs)
        decorated_function.__name__ = f.__name__  # Preserve the function name
        return decorated_function
    return decorator

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['name'] = user['name']
            session['role'] = user['role']
            flash(f'Welcome back, {user["name"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        email = request.form['email']
        role = request.form['role']
        department = request.form['department']
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Check if username already exists
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            conn.close()
            flash('Username already exists. Please choose another.', 'danger')
            return render_template('register.html')
        
        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        try:
            cursor.execute('''
            INSERT INTO users (username, password, name, email, role, department)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (username, hashed_password, name, email, role, department))
            conn.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            conn.rollback()
            flash(f'An error occurred during registration: {str(e)}', 'danger')
        finally:
            conn.close()
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    # Get total number of items
    cursor.execute("SELECT COUNT(*) as count FROM items")
    total_items = cursor.fetchone()['count']
    
    # Get items with low stock
    cursor.execute("SELECT COUNT(*) as count FROM items WHERE status = 'low_stock'")
    low_stock = cursor.fetchone()['count']
    
    # Get total number of transactions in the last 30 days
    cursor.execute("""
    SELECT COUNT(*) as count FROM transactions
    WHERE datetime(timestamp) >= datetime('now', '-30 days')
    """)
    recent_transactions = cursor.fetchone()['count']
    
    # Get pending orders
    cursor.execute("SELECT COUNT(*) as count FROM orders WHERE status = 'pending'")
    pending_orders = cursor.fetchone()['count']
    
    # Get recently added items
    cursor.execute("""
    SELECT i.*, l.name as location_name, s.name as supplier_name
    FROM items i
    LEFT JOIN locations l ON i.location_id = l.id
    LEFT JOIN suppliers s ON i.supplier_id = s.id
    ORDER BY i.created_at DESC LIMIT 5
    """)
    recent_items = cursor.fetchall()
    
    # Get recent transactions
    cursor.execute("""
    SELECT t.*, i.name as item_name, u.name as user_name
    FROM transactions t
    JOIN items i ON t.item_id = i.id
    JOIN users u ON t.user_id = u.id
    ORDER BY t.timestamp DESC LIMIT 5
    """)
    recent_transaction_list = cursor.fetchall()
    
    # Get user's top 3 personalized recommendations
    cursor.execute("""
    SELECT r.*, i.name as item_name, i.category, i.quantity, i.unit, i.status
    FROM recommendations r
    JOIN items i ON r.item_id = i.id
    WHERE r.user_id = ?
    ORDER BY r.score DESC
    LIMIT 3
    """, (session['user_id'],))
    top_recommendations = cursor.fetchall()
    
    # If no recommendations exist, generate them
    if not top_recommendations:
        generate_recommendations(session['user_id'])
        
        # Get the newly generated recommendations
        cursor.execute("""
        SELECT r.*, i.name as item_name, i.category, i.quantity, i.unit, i.status
        FROM recommendations r
        JOIN items i ON r.item_id = i.id
        WHERE r.user_id = ?
        ORDER BY r.score DESC
        LIMIT 3
        """, (session['user_id'],))
        top_recommendations = cursor.fetchall()
    
    conn.close()
    
    return render_template(
        'dashboard.html',
        total_items=total_items,
        low_stock=low_stock,
        recent_transactions=recent_transactions,
        pending_orders=pending_orders,
        recent_items=recent_items,
        recent_transaction_list=recent_transaction_list,
        top_recommendations=top_recommendations
    )

@app.route('/items')
@login_required
def items():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT i.*, l.name as location_name, s.name as supplier_name
    FROM items i
    LEFT JOIN locations l ON i.location_id = l.id
    LEFT JOIN suppliers s ON i.supplier_id = s.id
    ORDER BY i.name
    """)
    items = cursor.fetchall()
    
    cursor.execute("SELECT * FROM locations ORDER BY name")
    locations = cursor.fetchall()
    
    cursor.execute("SELECT * FROM suppliers ORDER BY name")
    suppliers = cursor.fetchall()
    
    conn.close()
    
    return render_template('items.html', items=items, locations=locations, suppliers=suppliers)

@app.route('/items/add', methods=['POST'])
@login_required
@role_required(['admin', 'lab_manager'])
def add_item():
    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        description = request.form.get('description', '')
        barcode = request.form.get('barcode', '')
        quantity = float(request.form['quantity'])
        unit = request.form['unit']
        min_quantity = float(request.form.get('min_quantity', 0))
        price = float(request.form.get('price', 0))
        location_id = request.form.get('location_id', None)
        if location_id == '':
            location_id = None
        supplier_id = request.form.get('supplier_id', None)
        if supplier_id == '':
            supplier_id = None
        expiry_date = request.form.get('expiry_date', '')
        hazard_type = request.form.get('hazard_type', '')
        storage_condition = request.form.get('storage_condition', '')
        msds_url = request.form.get('msds_url', '')
        
        status = 'in_stock'
        if quantity <= 0:
            status = 'out_of_stock'
        elif min_quantity > 0 and quantity <= min_quantity:
            status = 'low_stock'
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT INTO items (
                name, category, description, barcode, quantity, unit, min_quantity,
                price, location_id, supplier_id, expiry_date, hazard_type,
                storage_condition, msds_url, status, last_updated_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                name, category, description, barcode, quantity, unit, min_quantity,
                price, location_id, supplier_id, expiry_date, hazard_type,
                storage_condition, msds_url, status, session['user_id']
            ))
            
            item_id = cursor.lastrowid
            
            # Create transaction record for initial stock
            cursor.execute('''
            INSERT INTO transactions (item_id, user_id, quantity, type, notes)
            VALUES (?, ?, ?, ?, ?)
            ''', (item_id, session['user_id'], quantity, 'restock', 'Initial inventory'))
            
            conn.commit()
            flash('Item added successfully!', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
        finally:
            conn.close()
        
        return redirect(url_for('items'))

@app.route('/items/view/<int:item_id>')
@login_required
def view_item(item_id):
    """
    View detailed information about a specific item
    """
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    try:
        # Get the item with its foreign key data
        item = cursor.execute('''
            SELECT i.*, l.name as location_name, s.name as supplier_name
            FROM items i 
            LEFT JOIN locations l ON i.location_id = l.id
            LEFT JOIN suppliers s ON i.supplier_id = s.id
            WHERE i.id = ?
        ''', (item_id,)).fetchone()
        
        if not item:
            flash('Item not found.', 'error')
            return redirect(url_for('items'))
            
        # Get transaction history for this item
        transactions = cursor.execute('''
            SELECT t.*, u.name as user_name 
            FROM transactions t
            JOIN users u ON t.user_id = u.id
            WHERE t.item_id = ?
            ORDER BY t.timestamp DESC
            LIMIT 10
        ''', (item_id,)).fetchall()
        
        return render_template('view_item.html', item=item, transactions=transactions)
        
    except Exception as e:
        flash(f'Error retrieving item: {str(e)}', 'error')
        return redirect(url_for('items'))
    finally:
        conn.close()

@app.route('/items/edit/<int:item_id>', methods=['GET', 'POST'])
@login_required
@role_required(['admin', 'lab_manager'])
def edit_item(item_id):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        description = request.form.get('description', '')
        barcode = request.form.get('barcode', '')
        quantity = float(request.form['quantity'])
        unit = request.form['unit']
        min_quantity = float(request.form.get('min_quantity', 0))
        price = float(request.form.get('price', 0))
        location_id = request.form.get('location_id', None)
        if location_id == '':
            location_id = None
        supplier_id = request.form.get('supplier_id', None)
        if supplier_id == '':
            supplier_id = None
        expiry_date = request.form.get('expiry_date', '')
        hazard_type = request.form.get('hazard_type', '')
        storage_condition = request.form.get('storage_condition', '')
        msds_url = request.form.get('msds_url', '')
        
        status = 'in_stock'
        if quantity <= 0:
            status = 'out_of_stock'
        elif min_quantity > 0 and quantity <= min_quantity:
            status = 'low_stock'
        
        try:
            # Get current quantity to calculate difference
            cursor.execute("SELECT quantity FROM items WHERE id = ?", (item_id,))
            current_item = cursor.fetchone()
            old_quantity = current_item['quantity']
            quantity_difference = quantity - old_quantity
            
            cursor.execute('''
            UPDATE items SET
                name = ?, category = ?, description = ?, barcode = ?, quantity = ?,
                unit = ?, min_quantity = ?, price = ?, location_id = ?, supplier_id = ?,
                expiry_date = ?, hazard_type = ?, storage_condition = ?, msds_url = ?,
                status = ?, last_updated_by = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            ''', (
                name, category, description, barcode, quantity, unit, min_quantity,
                price, location_id, supplier_id, expiry_date, hazard_type,
                storage_condition, msds_url, status, session['user_id'], item_id
            ))
            
            # Create transaction record if quantity changed
            if quantity_difference != 0:
                transaction_type = 'restock' if quantity_difference > 0 else 'dispose'
                cursor.execute('''
                INSERT INTO transactions (item_id, user_id, quantity, type, notes)
                VALUES (?, ?, ?, ?, ?)
                ''', (
                    item_id, session['user_id'], abs(quantity_difference), 
                    transaction_type, f'Quantity adjusted during item update'
                ))
            
            conn.commit()
            flash('Item updated successfully!', 'success')
            return redirect(url_for('items'))
        except Exception as e:
            conn.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
    
    # GET request or after error
    cursor.execute("""
    SELECT * FROM items WHERE id = ?
    """, (item_id,))
    item = cursor.fetchone()
    
    cursor.execute("SELECT * FROM locations ORDER BY name")
    locations = cursor.fetchall()
    
    cursor.execute("SELECT * FROM suppliers ORDER BY name")
    suppliers = cursor.fetchall()
    
    conn.close()
    
    if not item:
        flash('Item not found.', 'danger')
        return redirect(url_for('items'))
    
    return render_template('edit_item.html', item=item, locations=locations, suppliers=suppliers)

@app.route('/items/delete/<int:item_id>', methods=['POST'])
@login_required
@role_required(['admin', 'lab_manager'])
def delete_item(item_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    try:
        # Check if item exists
        cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
        item = cursor.fetchone()
        if not item:
            conn.close()
            flash('Item not found.', 'danger')
            return redirect(url_for('items'))
        
        # Delete related transactions
        cursor.execute("DELETE FROM transactions WHERE item_id = ?", (item_id,))
        
        # Delete item
        cursor.execute("DELETE FROM items WHERE id = ?", (item_id,))
        
        conn.commit()
        flash('Item deleted successfully!', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'An error occurred: {str(e)}', 'danger')
    finally:
        conn.close()
    
    return redirect(url_for('items'))

@app.route('/transactions')
@login_required
def transactions():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT t.*, i.name as item_name, u.name as user_name
    FROM transactions t
    JOIN items i ON t.item_id = i.id
    JOIN users u ON t.user_id = u.id
    ORDER BY t.timestamp DESC
    """)
    transactions = cursor.fetchall()
    
    cursor.execute("SELECT * FROM items ORDER BY name")
    items = cursor.fetchall()
    
    conn.close()
    
    return render_template('transactions.html', transactions=transactions, items=items)

@app.route('/transactions/add', methods=['POST'])
@login_required
def add_transaction():
    if request.method == 'POST':
        item_id = request.form['item_id']
        quantity = float(request.form['quantity'])
        transaction_type = request.form['type']
        notes = request.form.get('notes', '')
        
        # Role-based restrictions:
        # Students can only perform check_out transactions and with limited quantity
        if session.get('role') == 'student':
            if transaction_type != 'check_out':
                flash('As a student, you can only check out items.', 'danger')
                return redirect(url_for('transactions'))
            # Limit check-out quantity for students (max 5 units per transaction)
            if quantity > 5:
                flash('Students can only check out up to 5 units per transaction.', 'danger')
                return redirect(url_for('transactions'))
        
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        
        try:
            # Get current item data
            cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
            item = cursor.fetchone()
            
            if not item:
                conn.close()
                flash('Item not found.', 'danger')
                return redirect(url_for('transactions'))
            
            # Update item quantity based on transaction type
            new_quantity = item['quantity']
            if transaction_type == 'check_in' or transaction_type == 'restock':
                new_quantity += quantity
            elif transaction_type == 'check_out' or transaction_type == 'dispose':
                if item['quantity'] < quantity:
                    conn.close()
                    flash('Not enough quantity available.', 'danger')
                    return redirect(url_for('transactions'))
                new_quantity -= quantity
            
            # Determine item status
            status = 'in_stock'
            if new_quantity <= 0:
                status = 'out_of_stock'
            elif item['min_quantity'] and new_quantity <= item['min_quantity']:
                status = 'low_stock'
            
            # Update item quantity
            cursor.execute("""
            UPDATE items SET quantity = ?, status = ?, last_updated_by = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """, (new_quantity, status, session['user_id'], item_id))
            
            # Create transaction record
            cursor.execute('''
            INSERT INTO transactions (item_id, user_id, quantity, type, notes)
            VALUES (?, ?, ?, ?, ?)
            ''', (item_id, session['user_id'], quantity, transaction_type, notes))
            
            conn.commit()
            flash('Transaction added successfully!', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
        finally:
            conn.close()
        
        return redirect(url_for('transactions'))

@app.route('/locations')
@login_required
def locations():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM locations ORDER BY name")
    locations = cursor.fetchall()
    
    # Count items in each location
    for location in locations:
        cursor.execute("SELECT COUNT(*) as count FROM items WHERE location_id = ?", (location['id'],))
        location['item_count'] = cursor.fetchone()['count']
    
    conn.close()
    
    return render_template('locations.html', locations=locations)

@app.route('/locations/add', methods=['POST'])
@login_required
@role_required(['admin', 'lab_manager'])
def add_location():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form.get('description', '')
        capacity = request.form.get('capacity', 0)
        if capacity == '':
            capacity = 0
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT INTO locations (name, description, capacity)
            VALUES (?, ?, ?)
            ''', (name, description, capacity))
            
            conn.commit()
            flash('Location added successfully!', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
        finally:
            conn.close()
        
        return redirect(url_for('locations'))

@app.route('/locations/edit/<int:location_id>', methods=['GET', 'POST'])
@login_required
@role_required(['admin', 'lab_manager'])
def edit_location(location_id):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form.get('description', '')
        capacity = request.form.get('capacity', 0)
        if capacity == '':
            capacity = 0
        
        try:
            cursor.execute('''
            UPDATE locations SET name = ?, description = ?, capacity = ?
            WHERE id = ?
            ''', (name, description, capacity, location_id))
            
            conn.commit()
            flash('Location updated successfully!', 'success')
            return redirect(url_for('locations'))
        except Exception as e:
            conn.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
    
    # GET request or after error
    cursor.execute("SELECT * FROM locations WHERE id = ?", (location_id,))
    location = cursor.fetchone()
    
    conn.close()
    
    if not location:
        flash('Location not found.', 'danger')
        return redirect(url_for('locations'))
    
    return render_template('edit_location.html', location=location)

@app.route('/locations/delete/<int:location_id>', methods=['POST'])
@login_required
@role_required(['admin', 'lab_manager'])
def delete_location(location_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    try:
        # Check if location is being used by any items
        cursor.execute("SELECT COUNT(*) FROM items WHERE location_id = ?", (location_id,))
        if cursor.fetchone()[0] > 0:
            conn.close()
            flash('Cannot delete location because it is being used by items.', 'danger')
            return redirect(url_for('locations'))
        
        # Delete location
        cursor.execute("DELETE FROM locations WHERE id = ?", (location_id,))
        
        conn.commit()
        flash('Location deleted successfully!', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'An error occurred: {str(e)}', 'danger')
    finally:
        conn.close()
    
    return redirect(url_for('locations'))

@app.route('/suppliers')
@login_required
def suppliers():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM suppliers ORDER BY name")
    suppliers = cursor.fetchall()
    
    # Count items for each supplier
    for supplier in suppliers:
        cursor.execute("SELECT COUNT(*) as count FROM items WHERE supplier_id = ?", (supplier['id'],))
        supplier['item_count'] = cursor.fetchone()['count']
    
    conn.close()
    
    return render_template('suppliers.html', suppliers=suppliers)

@app.route('/suppliers/add', methods=['POST'])
@login_required
@role_required(['admin', 'lab_manager'])
def add_supplier():
    if request.method == 'POST':
        name = request.form['name']
        contact_person = request.form.get('contact_person', '')
        email = request.form.get('email', '')
        phone = request.form.get('phone', '')
        address = request.form.get('address', '')
        notes = request.form.get('notes', '')
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT INTO suppliers (name, contact_person, email, phone, address, notes)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, contact_person, email, phone, address, notes))
            
            conn.commit()
            flash('Supplier added successfully!', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
        finally:
            conn.close()
        
        return redirect(url_for('suppliers'))

@app.route('/suppliers/edit/<int:supplier_id>', methods=['GET', 'POST'])
@login_required
@role_required(['admin', 'lab_manager'])
def edit_supplier(supplier_id):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    if request.method == 'POST':
        name = request.form['name']
        contact_person = request.form.get('contact_person', '')
        email = request.form.get('email', '')
        phone = request.form.get('phone', '')
        address = request.form.get('address', '')
        notes = request.form.get('notes', '')
        
        try:
            cursor.execute('''
            UPDATE suppliers SET name = ?, contact_person = ?, email = ?, phone = ?, address = ?, notes = ?
            WHERE id = ?
            ''', (name, contact_person, email, phone, address, notes, supplier_id))
            
            conn.commit()
            flash('Supplier updated successfully!', 'success')
            return redirect(url_for('suppliers'))
        except Exception as e:
            conn.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
    
    # GET request or after error
    cursor.execute("SELECT * FROM suppliers WHERE id = ?", (supplier_id,))
    supplier = cursor.fetchone()
    
    conn.close()
    
    if not supplier:
        flash('Supplier not found.', 'danger')
        return redirect(url_for('suppliers'))
    
    return render_template('edit_supplier.html', supplier=supplier)

@app.route('/suppliers/delete/<int:supplier_id>', methods=['POST'])
@login_required
@role_required(['admin', 'lab_manager'])
def delete_supplier(supplier_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    try:
        # Check if supplier is being used by any items
        cursor.execute("SELECT COUNT(*) FROM items WHERE supplier_id = ?", (supplier_id,))
        if cursor.fetchone()[0] > 0:
            conn.close()
            flash('Cannot delete supplier because it is being used by items.', 'danger')
            return redirect(url_for('suppliers'))
        
        # Check if supplier is being used by any orders
        cursor.execute("SELECT COUNT(*) FROM orders WHERE supplier_id = ?", (supplier_id,))
        if cursor.fetchone()[0] > 0:
            conn.close()
            flash('Cannot delete supplier because it is being used by orders.', 'danger')
            return redirect(url_for('suppliers'))
        
        # Delete supplier
        cursor.execute("DELETE FROM suppliers WHERE id = ?", (supplier_id,))
        
        conn.commit()
        flash('Supplier deleted successfully!', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'An error occurred: {str(e)}', 'danger')
    finally:
        conn.close()
    
    return redirect(url_for('suppliers'))

@app.route('/orders')
@login_required
def orders():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT o.*, s.name as supplier_name, u1.name as ordered_by_name, u2.name as approved_by_name
    FROM orders o
    LEFT JOIN suppliers s ON o.supplier_id = s.id
    JOIN users u1 ON o.ordered_by = u1.id
    LEFT JOIN users u2 ON o.approved_by = u2.id
    ORDER BY o.created_at DESC
    """)
    orders = cursor.fetchall()
    
    # Get items for each order
    for order in orders:
        cursor.execute("""
        SELECT oi.*, i.name as original_item_name
        FROM order_items oi
        LEFT JOIN items i ON oi.item_id = i.id
        WHERE oi.order_id = ?
        """, (order['id'],))
        order['order_items'] = cursor.fetchall()
        
        # Calculate total cost
        order['total_cost'] = sum(item['quantity'] * (item['price'] or 0) for item in order['order_items'])
    
    cursor.execute("SELECT * FROM suppliers ORDER BY name")
    suppliers = cursor.fetchall()
    
    cursor.execute("SELECT * FROM items ORDER BY name")
    items = cursor.fetchall()
    
    conn.close()
    
    # Add the current date for use in templates
    now = datetime.now()
    return render_template('orders.html', orders=orders, suppliers=suppliers, items=items, now=now)

@app.route('/orders/add', methods=['POST'])
@login_required
@role_required(['admin', 'lab_manager', 'researcher'])
def add_order():
    if request.method == 'POST':
        supplier_id = request.form.get('supplier_id', None)
        if supplier_id == '':
            supplier_id = None
        notes = request.form.get('notes', '')
        
        # Get order items (from form with multiple item fields)
        item_ids = request.form.getlist('item_id[]')
        item_names = request.form.getlist('item_name[]')
        quantities = request.form.getlist('quantity[]')
        units = request.form.getlist('unit[]')
        prices = request.form.getlist('price[]')
        
        if len(item_names) == 0:
            flash('Please add at least one item to the order.', 'danger')
            return redirect(url_for('orders'))
        
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        
        try:
            # Create order
            cursor.execute('''
            INSERT INTO orders (supplier_id, ordered_by, status, notes)
            VALUES (?, ?, ?, ?)
            ''', (supplier_id, session['user_id'], 'pending', notes))
            
            order_id = cursor.lastrowid
            
            # Add order items
            for i in range(len(item_names)):
                item_id = item_ids[i] if item_ids[i] != '' else None
                cursor.execute('''
                INSERT INTO order_items (order_id, item_id, name, quantity, unit, price)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (order_id, item_id, item_names[i], float(quantities[i]), units[i], float(prices[i]) if prices[i] else None))
            
            conn.commit()
            flash('Order created successfully!', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
        finally:
            conn.close()
        
        return redirect(url_for('orders'))

@app.route('/orders/update_status/<int:order_id>', methods=['POST'])
@login_required
@role_required(['admin', 'lab_manager'])
def update_order_status(order_id):
    if request.method == 'POST':
        status = request.form['status']
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        try:
            # If status is being changed to 'approved', set approved_by
            if status == 'approved':
                cursor.execute('''
                UPDATE orders SET status = ?, approved_by = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                ''', (status, session['user_id'], order_id))
            else:
                cursor.execute('''
                UPDATE orders SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                ''', (status, order_id))
            
            # If status is 'received', update inventory
            if status == 'received':
                conn.row_factory = dict_factory
                cursor = conn.cursor()
                
                # Get order items
                cursor.execute("SELECT * FROM order_items WHERE order_id = ?", (order_id,))
                order_items = cursor.fetchall()
                
                for item in order_items:
                    if item['item_id']:
                        # Existing item - update quantity
                        cursor.execute("SELECT * FROM items WHERE id = ?", (item['item_id'],))
                        existing_item = cursor.fetchone()
                        
                        new_quantity = existing_item['quantity'] + item['quantity']
                        status = 'in_stock'
                        if new_quantity <= 0:
                            status = 'out_of_stock'
                        elif existing_item['min_quantity'] and new_quantity <= existing_item['min_quantity']:
                            status = 'low_stock'
                        
                        cursor.execute('''
                        UPDATE items SET quantity = ?, status = ?, 
                            last_updated_by = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                        ''', (new_quantity, status, session['user_id'], item['item_id']))
                        
                        # Add transaction record
                        cursor.execute('''
                        INSERT INTO transactions (item_id, user_id, quantity, type, notes)
                        VALUES (?, ?, ?, ?, ?)
                        ''', (item['item_id'], session['user_id'], item['quantity'], 'restock', f'Received from order #{order_id}'))
            
            conn.commit()
            flash(f'Order status updated to {status}!', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
        finally:
            conn.close()
        
        return redirect(url_for('orders'))

@app.route('/orders/delete/<int:order_id>', methods=['POST'])
@login_required
@role_required(['admin', 'lab_manager'])
def delete_order(order_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    try:
        # Delete order items
        cursor.execute("DELETE FROM order_items WHERE order_id = ?", (order_id,))
        
        # Delete order
        cursor.execute("DELETE FROM orders WHERE id = ?", (order_id,))
        
        conn.commit()
        flash('Order deleted successfully!', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'An error occurred: {str(e)}', 'danger')
    finally:
        conn.close()
    
    return redirect(url_for('orders'))

@app.route('/users')
@login_required
@role_required(['admin', 'lab_manager'])
def users():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users ORDER BY username")
    users = cursor.fetchall()
    
    conn.close()
    
    return render_template('users.html', users=users)

@app.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@role_required(['admin'])
def edit_user(user_id):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    if request.method == 'POST':
        name = request.form['name']
        email = request.form.get('email', '')
        role = request.form['role']
        department = request.form.get('department', '')
        
        try:
            cursor.execute('''
            UPDATE users SET name = ?, email = ?, role = ?, department = ?
            WHERE id = ?
            ''', (name, email, role, department, user_id))
            
            conn.commit()
            flash('User updated successfully!', 'success')
            return redirect(url_for('users'))
        except Exception as e:
            conn.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
    
    # GET request or after error
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    
    conn.close()
    
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('users'))
    
    return render_template('edit_user.html', user=user)

@app.route('/users/reset_password/<int:user_id>', methods=['POST'])
@login_required
@role_required(['admin'])
def reset_password(user_id):
    if request.method == 'POST':
        new_password = request.form['new_password']
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        success = False
        message = ""
        
        try:
            # Hash the new password
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            cursor.execute('''
            UPDATE users SET password = ?
            WHERE id = ?
            ''', (hashed_password, user_id))
            
            conn.commit()
            success = True
            message = 'Password reset successfully!'
            flash(message, 'success')
        except Exception as e:
            conn.rollback()
            message = f'An error occurred: {str(e)}'
            flash(message, 'danger')
        finally:
            conn.close()
        
        # Check if this is an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': success,
                'message': message
            })
        
        # For regular form submissions, redirect to users page
        return redirect(url_for('users'))

@app.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
@role_required(['admin'])
def delete_user(user_id):
    # Don't allow deleting yourself
    if user_id == session['user_id']:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('users'))
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    try:
        # Check if user has transactions
        cursor.execute("SELECT COUNT(*) FROM transactions WHERE user_id = ?", (user_id,))
        if cursor.fetchone()[0] > 0:
            conn.close()
            flash('Cannot delete user because they have transaction records.', 'danger')
            return redirect(url_for('users'))
        
        # Check if user has orders
        cursor.execute("SELECT COUNT(*) FROM orders WHERE ordered_by = ? OR approved_by = ?", (user_id, user_id))
        if cursor.fetchone()[0] > 0:
            conn.close()
            flash('Cannot delete user because they have order records.', 'danger')
            return redirect(url_for('users'))
        
        # Delete user
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        
        conn.commit()
        flash('User deleted successfully!', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'An error occurred: {str(e)}', 'danger')
    finally:
        conn.close()
    
    return redirect(url_for('users'))

@app.route('/profile')
@login_required
def profile():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],))
    user = cursor.fetchone()
    
    # Get user's recent transactions
    cursor.execute("""
    SELECT t.*, i.name as item_name
    FROM transactions t
    JOIN items i ON t.item_id = i.id
    WHERE t.user_id = ?
    ORDER BY t.timestamp DESC LIMIT 10
    """, (session['user_id'],))
    transactions = cursor.fetchall()
    
    conn.close()
    
    return render_template('profile.html', user=user, transactions=transactions)

@app.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form.get('email', '')
        department = request.form.get('department', '')
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            UPDATE users SET name = ?, email = ?, department = ?
            WHERE id = ?
            ''', (name, email, department, session['user_id']))
            
            conn.commit()
            session['name'] = name
            flash('Profile updated successfully!', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
        finally:
            conn.close()
        
        return redirect(url_for('profile'))

@app.route('/profile/change_password', methods=['POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        if new_password != confirm_password:
            flash('New passwords do not match.', 'danger')
            return redirect(url_for('profile'))
        
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        
        # Verify current password
        cursor.execute("SELECT password FROM users WHERE id = ?", (session['user_id'],))
        user = cursor.fetchone()
        
        if not bcrypt.checkpw(current_password.encode('utf-8'), user['password'].encode('utf-8')):
            conn.close()
            flash('Current password is incorrect.', 'danger')
            return redirect(url_for('profile'))
        
        try:
            # Hash the new password
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            cursor.execute('''
            UPDATE users SET password = ?
            WHERE id = ?
            ''', (hashed_password, session['user_id']))
            
            conn.commit()
            flash('Password changed successfully!', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
        finally:
            conn.close()
        
        return redirect(url_for('profile'))

@app.route('/reports')
@login_required
@role_required(['admin', 'lab_manager', 'researcher'])
def reports():
    return render_template('reports.html')

@app.route('/maintenance')
@login_required
@role_required(['admin', 'lab_manager'])
def maintenance():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    # Get all equipment
    cursor.execute("""
    SELECT i.*, l.name as location_name
    FROM items i
    LEFT JOIN locations l ON i.location_id = l.id
    WHERE i.category = 'equipment'
    ORDER BY i.name
    """)
    equipment = cursor.fetchall()
    
    # Get maintenance history
    cursor.execute("""
    SELECT m.*, i.name as equipment_name, u.name as created_by_name
    FROM equipment_maintenance m
    JOIN items i ON m.equipment_id = i.id
    LEFT JOIN users u ON m.created_by = u.id
    ORDER BY m.maintenance_date DESC
    """)
    maintenance_history = cursor.fetchall()
    
    # Get maintenance predictions
    cursor.execute("""
    SELECT p.*, i.name as equipment_name
    FROM maintenance_predictions p
    JOIN items i ON p.equipment_id = i.id
    ORDER BY p.days_until_maintenance ASC
    """)
    predictions = cursor.fetchall()
    
    # Count critical predictions
    cursor.execute("""
    SELECT COUNT(*) as count
    FROM maintenance_predictions
    WHERE is_critical = 1
    """)
    critical_count = cursor.fetchone()['count']
    
    # Run prediction algorithm if no predictions exist
    if not predictions:
        predict_equipment_maintenance()
        # Fetch the newly generated predictions
        cursor.execute("""
        SELECT p.*, i.name as equipment_name
        FROM maintenance_predictions p
        JOIN items i ON p.equipment_id = i.id
        ORDER BY p.days_until_maintenance ASC
        """)
        predictions = cursor.fetchall()
        
        # Count critical predictions again
        cursor.execute("""
        SELECT COUNT(*) as count
        FROM maintenance_predictions
        WHERE is_critical = 1
        """)
        critical_count = cursor.fetchone()['count']
    
    conn.close()
    
    return render_template(
        'maintenance.html',
        equipment=equipment,
        maintenance_history=maintenance_history,
        predictions=predictions,
        critical_count=critical_count
    )

@app.route('/maintenance/log', methods=['POST'])
@login_required
@role_required(['admin', 'lab_manager'])
def log_maintenance():
    if request.method == 'POST':
        equipment_id = request.form['equipment_id']
        maintenance_date = request.form['maintenance_date']
        maintenance_type = request.form['maintenance_type']
        status = request.form['status']
        technician = request.form.get('technician', '')
        description = request.form.get('description', '')
        cost = request.form.get('cost', 0)
        hours_used_before = request.form.get('hours_used_before', 0)
        issue_detected = request.form.get('issue_detected', '')
        parts_replaced = request.form.get('parts_replaced', '')
        notes = request.form.get('notes', '')
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT INTO equipment_maintenance (
                equipment_id, maintenance_date, maintenance_type, status,
                technician, description, cost, hours_used_before,
                issue_detected, parts_replaced, notes, created_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                equipment_id, maintenance_date, maintenance_type, status,
                technician, description, cost, hours_used_before,
                issue_detected, parts_replaced, notes, session['user_id']
            ))
            
            conn.commit()
            
            # If maintenance is completed, update maintenance predictions
            if status == 'completed':
                predict_equipment_maintenance()
            
            flash('Maintenance record added successfully!', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
        finally:
            conn.close()
        
        return redirect(url_for('maintenance'))

@app.route('/maintenance/usage', methods=['POST'])
@login_required
def log_equipment_usage():
    if request.method == 'POST':
        equipment_id = request.form['equipment_id']
        start_time = request.form['start_time']
        end_time = request.form.get('end_time', '')
        duration = request.form.get('duration', 0)
        project = request.form.get('project', '')
        notes = request.form.get('notes', '')
        
        # Calculate duration if end_time is provided but duration is not
        if end_time and not duration:
            try:
                start = datetime.strptime(start_time, '%Y-%m-%dT%H:%M')
                end = datetime.strptime(end_time, '%Y-%m-%dT%H:%M')
                duration = int((end - start).total_seconds() / 3600)  # in hours
            except ValueError:
                # Handle parsing errors
                duration = 0
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT INTO equipment_usage (
                equipment_id, user_id, start_time, end_time, duration, project, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                equipment_id, session['user_id'], start_time, end_time, 
                duration, project, notes
            ))
            
            conn.commit()
            flash('Equipment usage logged successfully!', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
        finally:
            conn.close()
        
        return redirect(url_for('maintenance'))

@app.route('/maintenance/predict')
@login_required
@role_required(['admin', 'lab_manager'])
def run_maintenance_prediction():
    num_predictions = predict_equipment_maintenance()
    flash(f'Successfully generated {num_predictions} maintenance predictions!', 'success')
    return redirect(url_for('maintenance'))

@app.route('/recommendations')
@login_required
def recommendations():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    # Check for refresh parameter
    refresh = request.args.get('refresh', 'false')
    
    # If refresh is requested, regenerate recommendations
    if refresh == 'true':
        generate_recommendations(session['user_id'])
        flash('Your recommendations have been refreshed!', 'success')
    
    # Get the user's personalized recommendations
    cursor.execute("""
    SELECT r.*, i.name as item_name, i.category, i.description, i.quantity, i.unit, i.status, i.barcode,
           l.name as location_name, s.name as supplier_name
    FROM recommendations r
    JOIN items i ON r.item_id = i.id
    LEFT JOIN locations l ON i.location_id = l.id
    LEFT JOIN suppliers s ON i.supplier_id = s.id
    WHERE r.user_id = ?
    ORDER BY r.score DESC
    LIMIT 10
    """, (session['user_id'],))
    user_recommendations = cursor.fetchall()
    
    # If no recommendations exist yet, generate them
    if not user_recommendations:
        generate_recommendations(session['user_id'])
        
        # Get the newly generated recommendations
        cursor.execute("""
        SELECT r.*, i.name as item_name, i.category, i.description, i.quantity, i.unit, i.status, i.barcode,
               l.name as location_name, s.name as supplier_name
        FROM recommendations r
        JOIN items i ON r.item_id = i.id
        LEFT JOIN locations l ON i.location_id = l.id
        LEFT JOIN suppliers s ON i.supplier_id = s.id
        WHERE r.user_id = ?
        ORDER BY r.score DESC
        LIMIT 10
        """, (session['user_id'],))
        user_recommendations = cursor.fetchall()
    
    conn.close()
    
    return render_template('recommendations.html', recommendations=user_recommendations)

def predict_equipment_maintenance():
    """
    Predict equipment maintenance needs based on usage patterns and maintenance history.
    This is a simplified prediction algorithm that demonstrates the concept.
    In a real-world implementation, this would use more sophisticated machine learning techniques.
    """
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    # Clear previous predictions
    cursor.execute("DELETE FROM maintenance_predictions")
    
    # Get all equipment items
    cursor.execute("""
    SELECT id, name, created_at 
    FROM items 
    WHERE category = 'equipment'
    """)
    equipment_items = cursor.fetchall()
    
    predictions = []
    current_date = datetime.now()
    
    for equipment in equipment_items:
        equipment_id = equipment['id']
        
        # Get maintenance history
        cursor.execute("""
        SELECT maintenance_date, maintenance_type, issue_detected, hours_used_before
        FROM equipment_maintenance
        WHERE equipment_id = ?
        ORDER BY maintenance_date DESC
        """, (equipment_id,))
        maintenance_history = cursor.fetchall()
        
        # Get usage data
        cursor.execute("""
        SELECT start_time, end_time, duration
        FROM equipment_usage
        WHERE equipment_id = ?
        ORDER BY start_time DESC
        """, (equipment_id,))
        usage_data = cursor.fetchall()
        
        # Calculate total usage hours
        total_usage_hours = 0
        for usage in usage_data:
            if usage['duration']:
                total_usage_hours += usage['duration']
        
        # Determine time since last maintenance
        days_since_last_maintenance = 365  # Default assumption
        if maintenance_history:
            last_maintenance = maintenance_history[0]
            last_date = datetime.strptime(last_maintenance['maintenance_date'], '%Y-%m-%d')
            days_since_last_maintenance = (current_date - last_date).days
        
        # Default prediction values
        prediction_date = (current_date + timedelta(days=90)).strftime('%Y-%m-%d')
        maintenance_type = 'routine'
        confidence_score = 0.7
        predicted_issue = None
        is_critical = False
        
        # Analyze usage patterns and maintenance history to make predictions
        if total_usage_hours > 0 or maintenance_history:
            # Predict routine maintenance
            if maintenance_history:
                # Find patterns in maintenance intervals
                maintenance_intervals = []
                for i in range(1, len(maintenance_history)):
                    date1 = datetime.strptime(maintenance_history[i-1]['maintenance_date'], '%Y-%m-%d')
                    date2 = datetime.strptime(maintenance_history[i]['maintenance_date'], '%Y-%m-%d')
                    interval = (date1 - date2).days
                    maintenance_intervals.append(interval)
                
                # If we have interval data, use it for prediction
                if maintenance_intervals:
                    avg_interval = sum(maintenance_intervals) / len(maintenance_intervals)
                    next_maintenance_days = max(0, avg_interval - days_since_last_maintenance)
                    prediction_date = (current_date + timedelta(days=next_maintenance_days)).strftime('%Y-%m-%d')
                    
                    # Adjust confidence based on consistency of intervals
                    if len(maintenance_intervals) > 1:
                        variance = sum((x - avg_interval) ** 2 for x in maintenance_intervals) / len(maintenance_intervals)
                        std_dev = variance ** 0.5
                        if std_dev < avg_interval / 4:  # Low variation = higher confidence
                            confidence_score = 0.9
                        elif std_dev < avg_interval / 2:
                            confidence_score = 0.8
                        else:
                            confidence_score = 0.7
            
            # Predict based on usage
            if total_usage_hours > 0:
                # Calculate average usage hours between maintenance
                avg_hours_between_maintenance = 500  # Default assumption
                if maintenance_history and len(maintenance_history) > 1:
                    hours_data = [m['hours_used_before'] for m in maintenance_history if m['hours_used_before']]
                    if hours_data:
                        avg_hours_between_maintenance = sum(hours_data) / len(hours_data)
                
                # Check recent heavy usage patterns
                recent_usage = sum(u['duration'] for u in usage_data[:10] if u['duration']) if len(usage_data) >= 10 else 0
                if recent_usage > avg_hours_between_maintenance / 4:
                    # Heavy recent usage might indicate earlier maintenance need
                    days_until_maintenance = max(0, int(avg_hours_between_maintenance - total_usage_hours) / 10)
                    usage_based_date = (current_date + timedelta(days=days_until_maintenance)).strftime('%Y-%m-%d')
                    
                    # If usage-based prediction is earlier, use it with appropriate confidence
                    if datetime.strptime(usage_based_date, '%Y-%m-%d') < datetime.strptime(prediction_date, '%Y-%m-%d'):
                        prediction_date = usage_based_date
                        confidence_score = 0.75
            
            # Check for recurring issues
            if len(maintenance_history) >= 2:
                # Look for repeated issues
                issues = [m['issue_detected'] for m in maintenance_history if m['issue_detected']]
                if issues:
                    from collections import Counter
                    issue_counts = Counter(issues)
                    most_common_issue = issue_counts.most_common(1)[0]
                    if most_common_issue[1] >= 2:  # Same issue occurred at least twice
                        predicted_issue = most_common_issue[0]
                        # If repeated issues, may need maintenance sooner and it's more critical
                        prediction_date = (current_date + timedelta(days=max(30, days_since_last_maintenance // 2))).strftime('%Y-%m-%d')
                        confidence_score = 0.85
                        is_critical = True
            
            # Determine maintenance type based on patterns
            repair_count = sum(1 for m in maintenance_history if m['maintenance_type'] == 'repair')
            calibration_count = sum(1 for m in maintenance_history if m['maintenance_type'] == 'calibration')
            
            if repair_count > len(maintenance_history) / 3:
                maintenance_type = 'repair'
                confidence_score = min(0.9, confidence_score + 0.1)
            elif calibration_count > len(maintenance_history) / 3:
                maintenance_type = 'calibration'
            
            # Calculate days until maintenance
            days_until_maintenance = (datetime.strptime(prediction_date, '%Y-%m-%d') - current_date).days
            
            # Add to predictions
            predictions.append({
                'equipment_id': equipment_id,
                'prediction_date': prediction_date,
                'maintenance_type': maintenance_type,
                'confidence_score': round(confidence_score, 2),
                'predicted_issue': predicted_issue,
                'days_until_maintenance': days_until_maintenance,
                'is_critical': 1 if is_critical else 0
            })
    
    # Insert predictions into database
    for prediction in predictions:
        cursor.execute("""
        INSERT INTO maintenance_predictions (
            equipment_id, prediction_date, maintenance_type, confidence_score,
            predicted_issue, days_until_maintenance, is_critical
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            prediction['equipment_id'],
            prediction['prediction_date'],
            prediction['maintenance_type'],
            prediction['confidence_score'],
            prediction['predicted_issue'],
            prediction['days_until_maintenance'],
            prediction['is_critical']
        ))
    
    conn.commit()
    conn.close()
    
    return len(predictions)

def generate_recommendations(user_id):
    """Generate personalized inventory recommendations for a user"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    # Clear existing recommendations for this user
    cursor.execute("DELETE FROM recommendations WHERE user_id = ?", (user_id,))
    
    # Get user department and role
    cursor.execute("SELECT department, role FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    department = user['department']
    role = user['role']
    
    # Get user's transaction history (what they've used)
    cursor.execute("""
    SELECT item_id, COUNT(*) as usage_count 
    FROM transactions 
    WHERE user_id = ? AND type = 'check_out'
    GROUP BY item_id
    ORDER BY usage_count DESC
    """, (user_id,))
    user_items = {row['item_id']: row['usage_count'] for row in cursor.fetchall()}
    
    # Get department transaction patterns (what similar users use)
    cursor.execute("""
    SELECT t.item_id, COUNT(*) as dept_usage_count
    FROM transactions t
    JOIN users u ON t.user_id = u.id
    WHERE u.department = ? AND t.type = 'check_out' AND u.id != ?
    GROUP BY t.item_id
    ORDER BY dept_usage_count DESC
    """, (department, user_id))
    dept_items = {row['item_id']: row['dept_usage_count'] for row in cursor.fetchall()}
    
    # Get role transaction patterns (what users in same role use)
    cursor.execute("""
    SELECT t.item_id, COUNT(*) as role_usage_count
    FROM transactions t
    JOIN users u ON t.user_id = u.id
    WHERE u.role = ? AND t.type = 'check_out' AND u.id != ?
    GROUP BY t.item_id
    ORDER BY role_usage_count DESC
    """, (role, user_id))
    role_items = {row['item_id']: row['role_usage_count'] for row in cursor.fetchall()}
    
    # Get all available items
    cursor.execute("""
    SELECT id, name, category, quantity, status 
    FROM items 
    WHERE status != 'out_of_stock'
    """)
    all_items = cursor.fetchall()
    
    recommendations = []
    
    for item in all_items:
        item_id = item['id']
        score = 0
        reason = []
        
        # Personal usage pattern (highest weight)
        if item_id in user_items:
            personal_score = min(user_items[item_id] * 0.5, 5)  # Cap at 5 points
            score += personal_score
            reason.append(f"You've used this item {user_items[item_id]} times")
        
        # Department relevance (medium weight)
        if item_id in dept_items:
            dept_score = min(dept_items[item_id] * 0.2, 3)  # Cap at 3 points
            score += dept_score
            reason.append(f"Popular in your department")
        
        # Role relevance (medium weight)
        if item_id in role_items:
            role_score = min(role_items[item_id] * 0.3, 4)  # Cap at 4 points
            score += role_score
            reason.append(f"Commonly used by {role}s")
        
        # Item is low in stock (lower priority)
        if item['status'] == 'low_stock':
            score -= 1
            reason.append("Low in stock")
        
        # For researchers, prioritize chemicals and equipment
        if role == 'researcher' and item['category'] in ['chemicals', 'equipment']:
            score += 2
            reason.append(f"Relevant for research")
        
        # For students, prioritize consumables and glassware
        if role == 'student' and item['category'] in ['consumables', 'glassware']:
            score += 2
            reason.append(f"Recommended for students")
        
        # Only add items with some relevance
        if score > 0:
            recommendations.append({
                'item_id': item_id,
                'score': score,
                'reason': ", ".join(reason)
            })
    
    # Sort by score (highest first) and take top 15
    recommendations.sort(key=lambda x: x['score'], reverse=True)
    recommendations = recommendations[:15]
    
    # Store recommendations in database
    for rec in recommendations:
        cursor.execute("""
        INSERT INTO recommendations (user_id, item_id, score, reason)
        VALUES (?, ?, ?, ?)
        """, (user_id, rec['item_id'], rec['score'], rec['reason']))
    
    conn.commit()
    conn.close()

@app.route('/reports/inventory_status')
@login_required
@role_required(['admin', 'lab_manager', 'researcher'])
def inventory_status_report():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    # Get counts by status
    cursor.execute("""
    SELECT status, COUNT(*) as count
    FROM items
    GROUP BY status
    """)
    status_counts = cursor.fetchall()
    
    # Get counts by category
    cursor.execute("""
    SELECT category, COUNT(*) as count
    FROM items
    GROUP BY category
    """)
    category_counts = cursor.fetchall()
    
    # Get low stock items
    cursor.execute("""
    SELECT i.*, l.name as location_name, s.name as supplier_name
    FROM items i
    LEFT JOIN locations l ON i.location_id = l.id
    LEFT JOIN suppliers s ON i.supplier_id = s.id
    WHERE i.status = 'low_stock' OR i.status = 'out_of_stock'
    ORDER BY i.status, i.name
    """)
    low_stock_items = cursor.fetchall()
    
    # Get expiring items (if expiry_date is within 30 days)
    cursor.execute("""
    SELECT i.*, l.name as location_name, s.name as supplier_name,
        julianday(i.expiry_date) - julianday('now') as days_until_expiry
    FROM items i
    LEFT JOIN locations l ON i.location_id = l.id
    LEFT JOIN suppliers s ON i.supplier_id = s.id
    WHERE i.expiry_date IS NOT NULL 
        AND i.expiry_date != ''
        AND julianday(i.expiry_date) - julianday('now') <= 30
        AND julianday(i.expiry_date) - julianday('now') > 0
    ORDER BY days_until_expiry
    """)
    expiring_items = cursor.fetchall()
    
    # Get total value by category
    cursor.execute("""
    SELECT category, SUM(quantity * price) as total_value
    FROM items
    WHERE price IS NOT NULL AND price > 0
    GROUP BY category
    """)
    category_values = cursor.fetchall()
    
    # Get total inventory value
    cursor.execute("""
    SELECT SUM(quantity * price) as total_value
    FROM items
    WHERE price IS NOT NULL AND price > 0
    """)
    total_inventory_value = cursor.fetchone()['total_value'] or 0
    
    conn.close()
    
    # Add current datetime for the report generation timestamp
    from datetime import datetime
    current_datetime = datetime.now()
    
    return render_template(
        'inventory_status_report.html',
        status_counts=status_counts,
        category_counts=category_counts,
        low_stock_items=low_stock_items,
        expiring_items=expiring_items,
        category_values=category_values,
        total_inventory_value=total_inventory_value,
        now=current_datetime
    )

@app.route('/reports/transaction_history')
@login_required
@role_required(['admin', 'lab_manager'])
def transaction_history_report():
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    transaction_type = request.args.get('type', '')
    
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    # Build query based on filters
    query = """
    SELECT t.*, i.name as item_name, i.category, u.name as user_name, u.role as user_role
    FROM transactions t
    JOIN items i ON t.item_id = i.id
    JOIN users u ON t.user_id = u.id
    WHERE 1=1
    """
    params = []
    
    if start_date:
        query += " AND date(t.timestamp) >= date(?)"
        params.append(start_date)
    
    if end_date:
        query += " AND date(t.timestamp) <= date(?)"
        params.append(end_date)
    
    if transaction_type:
        query += " AND t.type = ?"
        params.append(transaction_type)
    
    query += " ORDER BY t.timestamp DESC"
    
    cursor.execute(query, params)
    transactions = cursor.fetchall()
    
    # Get summary statistics
    summary_query = """
    SELECT
        COUNT(*) as total_transactions,
        SUM(CASE WHEN t.type = 'check_in' THEN 1 ELSE 0 END) as check_in_count,
        SUM(CASE WHEN t.type = 'check_out' THEN 1 ELSE 0 END) as check_out_count,
        SUM(CASE WHEN t.type = 'restock' THEN 1 ELSE 0 END) as restock_count,
        SUM(CASE WHEN t.type = 'dispose' THEN 1 ELSE 0 END) as dispose_count
    FROM transactions t
    WHERE 1=1
    """
    
    if start_date:
        summary_query += " AND date(t.timestamp) >= date(?)"
    
    if end_date:
        summary_query += " AND date(t.timestamp) <= date(?)"
    
    if transaction_type:
        summary_query += " AND t.type = ?"
    
    cursor.execute(summary_query, params)
    summary = cursor.fetchone()
    
    # Get transaction count by category
    category_query = """
    SELECT
        i.category,
        COUNT(*) as transaction_count,
        SUM(CASE WHEN t.type IN ('check_in', 'restock') THEN t.quantity ELSE 0 END) as quantity_in,
        SUM(CASE WHEN t.type IN ('check_out', 'dispose') THEN t.quantity ELSE 0 END) as quantity_out
    FROM transactions t
    JOIN items i ON t.item_id = i.id
    WHERE 1=1
    """
    
    if start_date:
        category_query += " AND date(t.timestamp) >= date(?)"
    
    if end_date:
        category_query += " AND date(t.timestamp) <= date(?)"
    
    if transaction_type:
        category_query += " AND t.type = ?"
    
    category_query += " GROUP BY i.category"
    
    cursor.execute(category_query, params)
    category_stats = cursor.fetchall()
    
    # Get transaction count by user
    user_query = """
    SELECT
        u.name as user_name,
        u.role as user_role,
        COUNT(*) as transaction_count
    FROM transactions t
    JOIN users u ON t.user_id = u.id
    WHERE 1=1
    """
    
    if start_date:
        user_query += " AND date(t.timestamp) >= date(?)"
    
    if end_date:
        user_query += " AND date(t.timestamp) <= date(?)"
    
    if transaction_type:
        user_query += " AND t.type = ?"
    
    user_query += " GROUP BY t.user_id ORDER BY transaction_count DESC"
    
    cursor.execute(user_query, params)
    user_stats = cursor.fetchall()
    
    conn.close()
    
    # Add current datetime for the report generation timestamp
    from datetime import datetime
    current_datetime = datetime.now()
    
    return render_template(
        'transaction_history_report.html',
        transactions=transactions,
        summary=summary,
        category_stats=category_stats,
        user_stats=user_stats,
        start_date=start_date,
        end_date=end_date,
        transaction_type=transaction_type,
        now=current_datetime
    )

@app.route('/api/items')
@login_required
def api_items():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT i.*, l.name as location_name, s.name as supplier_name
    FROM items i
    LEFT JOIN locations l ON i.location_id = l.id
    LEFT JOIN suppliers s ON i.supplier_id = s.id
    ORDER BY i.name
    """)
    items = cursor.fetchall()
    
    conn.close()
    
    return jsonify(items)

@app.route('/api/item/<int:item_id>')
@login_required
def api_get_item(item_id):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT i.*, l.name as location_name, s.name as supplier_name
    FROM items i
    LEFT JOIN locations l ON i.location_id = l.id
    LEFT JOIN suppliers s ON i.supplier_id = s.id
    WHERE i.id = ?
    """, (item_id,))
    item = cursor.fetchone()
    
    conn.close()
    
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    
    return jsonify(item)

@app.route('/api/low_stock_items')
@login_required
def api_low_stock_items():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT i.*, l.name as location_name, s.name as supplier_name
    FROM items i
    LEFT JOIN locations l ON i.location_id = l.id
    LEFT JOIN suppliers s ON i.supplier_id = s.id
    WHERE i.status = 'low_stock' OR i.status = 'out_of_stock'
    ORDER BY i.status, i.name
    """)
    items = cursor.fetchall()
    
    conn.close()
    
    return jsonify(items)

@app.route('/api/locations')
@login_required
@role_required(['admin', 'lab_manager', 'researcher'])
def api_locations():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM locations ORDER BY name")
    locations = cursor.fetchall()
    
    conn.close()
    
    return jsonify(locations)

@app.route('/api/suppliers')
@login_required
@role_required(['admin', 'lab_manager', 'researcher'])
def api_suppliers():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM suppliers ORDER BY name")
    suppliers = cursor.fetchall()
    
    conn.close()
    
    return jsonify(suppliers)

@app.route('/api/item_by_barcode/<barcode>')
@login_required
def api_item_by_barcode(barcode):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT i.*, l.name as location_name, s.name as supplier_name
    FROM items i
    LEFT JOIN locations l ON i.location_id = l.id
    LEFT JOIN suppliers s ON i.supplier_id = s.id
    WHERE i.barcode = ?
    """, (barcode,))
    item = cursor.fetchone()
    
    conn.close()
    
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    
    return jsonify(item)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('not_found.html'), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)