import sqlite3
import hashlib
import datetime
import random

# Simple password hashing function instead of werkzeug
def generate_password_hash(password):
    salt = datetime.datetime.now().isoformat()
    return hashlib.sha256((password + salt).encode()).hexdigest()

def dict_factory(cursor, row):
    """Convert database row objects to a dictionary"""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def init_db():
    """Create and initialize the database with sample data"""
    conn = sqlite3.connect('laboratory.db')
    conn.row_factory = dict_factory
    
    print("Adding sample data to the database...")
    
    add_sample_users(conn)
    add_sample_locations(conn)
    add_sample_suppliers(conn)
    add_sample_items(conn)
    add_sample_transactions(conn)
    add_sample_orders(conn)
    
    conn.close()
    print("Sample data successfully added to the database!")

def add_sample_users(conn):
    """Add sample users with various roles"""
    cursor = conn.cursor()
    
    # Check if we already have sample users
    cursor.execute("SELECT COUNT(*) as count FROM users")
    result = cursor.fetchone()
    
    if result['count'] > 1:
        print("Users already exist in the database, skipping sample user creation.")
        return
    
    # Sample users data
    users = [
        # Admin users
        {
            'username': 'admin1',
            'password': generate_password_hash('admin123'),
            'name': 'Alex Johnson',
            'email': 'alex.johnson@scilabims.com',
            'role': 'admin',
            'department': 'IT Administration',
            'created_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'username': 'admin2',
            'password': generate_password_hash('admin456'),
            'name': 'Jamie Smith',
            'email': 'jamie.smith@scilabims.com',
            'role': 'admin',
            'department': 'System Administration',
            'created_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        
        # Lab Manager users
        {
            'username': 'labmanager1',
            'password': generate_password_hash('manager123'),
            'name': 'Morgan Lee',
            'email': 'morgan.lee@scilabims.com',
            'role': 'lab_manager',
            'department': 'Chemistry',
            'created_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'username': 'labmanager2',
            'password': generate_password_hash('manager456'),
            'name': 'Taylor Rodriguez',
            'email': 'taylor.rodriguez@scilabims.com',
            'role': 'lab_manager',
            'department': 'Biology',
            'created_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        
        # Researcher users
        {
            'username': 'researcher1',
            'password': generate_password_hash('research123'),
            'name': 'Jordan Patel',
            'email': 'jordan.patel@scilabims.com',
            'role': 'researcher',
            'department': 'Chemistry',
            'created_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'username': 'researcher2',
            'password': generate_password_hash('research456'),
            'name': 'Casey Wong',
            'email': 'casey.wong@scilabims.com',
            'role': 'researcher',
            'department': 'Biology',
            'created_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        
        # Student users
        {
            'username': 'student1',
            'password': generate_password_hash('student123'),
            'name': 'Riley Chen',
            'email': 'riley.chen@scilabims.com',
            'role': 'student',
            'department': 'Chemistry',
            'created_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'username': 'student2',
            'password': generate_password_hash('student456'),
            'name': 'Quinn Martinez',
            'email': 'quinn.martinez@scilabims.com',
            'role': 'student',
            'department': 'Biology',
            'created_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    ]
    
    for user in users:
        cursor.execute("""
            INSERT INTO users (username, password, name, email, role, department, created_at)
            VALUES (:username, :password, :name, :email, :role, :department, :created_at)
        """, user)
    
    conn.commit()
    print(f"Added {len(users)} sample users")

def add_sample_locations(conn):
    """Add sample storage locations"""
    cursor = conn.cursor()
    
    # Check if we already have sample locations
    cursor.execute("SELECT COUNT(*) as count FROM locations")
    result = cursor.fetchone()
    
    if result['count'] > 0:
        print("Locations already exist in the database, skipping sample location creation.")
        return
    
    # Sample locations data
    locations = [
        {
            'name': 'Main Storage Room',
            'description': 'Primary storage area for laboratory supplies and equipment',
            'capacity': 100,
            'created_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'name': 'Chemical Cabinet A',
            'description': 'Secure storage for hazardous chemicals and reagents',
            'capacity': 50,
            'created_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'name': 'Equipment Shelf B',
            'description': 'Storage for laboratory equipment and instruments',
            'capacity': 30,
            'created_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'name': 'Refrigerator 1',
            'description': 'Cold storage for temperature-sensitive materials (2-8°C)',
            'capacity': 20,
            'created_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'name': 'Freezer Unit',
            'description': 'Freezer storage for samples and materials (-20°C)',
            'capacity': 15,
            'created_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'name': 'Glassware Cabinet',
            'description': 'Storage for various laboratory glassware',
            'capacity': 40,
            'created_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    ]
    
    for location in locations:
        cursor.execute("""
            INSERT INTO locations (name, description, capacity, created_at)
            VALUES (:name, :description, :capacity, :created_at)
        """, location)
    
    conn.commit()
    print(f"Added {len(locations)} sample locations")

def add_sample_suppliers(conn):
    """Add sample suppliers"""
    cursor = conn.cursor()
    
    # Check if we already have sample suppliers
    cursor.execute("SELECT COUNT(*) as count FROM suppliers")
    result = cursor.fetchone()
    
    if result['count'] > 0:
        print("Suppliers already exist in the database, skipping sample supplier creation.")
        return
    
    # Sample suppliers data
    suppliers = [
        {
            'name': 'SciSupply Inc.',
            'contact_person': 'Emma Johnson',
            'email': 'orders@scisupply.com',
            'phone': '555-123-4567',
            'address': '123 Research Blvd, Science City, SC 12345',
            'notes': 'Offers bulk discounts for orders over $1000'
        },
        {
            'name': 'LabEquip Co.',
            'contact_person': 'Michael Brown',
            'email': 'sales@labequip.com',
            'phone': '555-987-6543',
            'address': '456 Laboratory Ave, Tech Town, TT 67890',
            'notes': 'Specializes in high-end lab equipment and calibration services'
        },
        {
            'name': 'ChemPure Reagents',
            'contact_person': 'Sarah Miller',
            'email': 'info@chempure.com',
            'phone': '555-456-7890',
            'address': '789 Chemical Dr, Reagent City, RC 45678',
            'notes': 'High-purity reagents with certified analysis reports'
        },
        {
            'name': 'GlassTech Solutions',
            'contact_person': 'David Wilson',
            'email': 'service@glasstech.com',
            'phone': '555-789-0123',
            'address': '321 Glass Way, Crystal Falls, CF 98765',
            'notes': 'Custom glassware fabrication available upon request'
        },
        {
            'name': 'Bio-Research Supplies',
            'contact_person': 'Jennifer Lee',
            'email': 'orders@bioresearch.com',
            'phone': '555-321-6547',
            'address': '654 Biology Street, Cell City, CC 23456',
            'notes': 'Specializes in cell culture and molecular biology supplies'
        }
    ]
    
    for supplier in suppliers:
        cursor.execute("""
            INSERT INTO suppliers (name, contact_person, email, phone, address, notes)
            VALUES (:name, :contact_person, :email, :phone, :address, :notes)
        """, supplier)
    
    conn.commit()
    print(f"Added {len(suppliers)} sample suppliers")

def add_sample_items(conn):
    """Add sample inventory items"""
    cursor = conn.cursor()
    
    # Check if we already have sample items
    cursor.execute("SELECT COUNT(*) as count FROM items")
    result = cursor.fetchone()
    
    if result['count'] > 0:
        print("Items already exist in the database, skipping sample item creation.")
        return
    
    # Get location IDs
    cursor.execute("SELECT id, name FROM locations")
    locations = cursor.fetchall()
    location_map = {}
    for loc in locations:
        location_map[loc['name']] = loc['id']
    
    # Define required locations
    required_locations = ['Main Storage Room', 'Chemical Cabinet A', 'Equipment Shelf B', 
                         'Refrigerator 1', 'Freezer Unit', 'Glassware Cabinet']
    
    # Create any required locations that don't exist yet
    for loc_name in required_locations:
        if loc_name not in location_map:
            print(f"Creating missing location: {loc_name}")
            cursor.execute("""
                INSERT INTO locations (name, description, capacity, created_at)
                VALUES (?, ?, ?, ?)
            """, (loc_name, f"Storage location for {loc_name}", 50, 
                  datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            conn.commit()
            
            # Get the new ID
            cursor.execute("SELECT id FROM locations WHERE name = ?", (loc_name,))
            new_loc = cursor.fetchone()
            location_map[loc_name] = new_loc['id']
    
    # Get supplier IDs
    cursor.execute("SELECT id, name FROM suppliers")
    suppliers = cursor.fetchall()
    supplier_map = {}
    for sup in suppliers:
        supplier_map[sup['name']] = sup['id']
    
    # Define required suppliers
    required_suppliers = ['SciSupply Inc.', 'LabEquip Co.', 'ChemPure Reagents', 
                          'GlassTech Solutions', 'Bio-Research Supplies']
    
    # Create any required suppliers that don't exist yet
    for sup_name in required_suppliers:
        if sup_name not in supplier_map:
            print(f"Creating missing supplier: {sup_name}")
            cursor.execute("""
                INSERT INTO suppliers (name, contact_person, email, phone, address, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (sup_name, f"Contact for {sup_name}", f"contact@{sup_name.lower().replace(' ', '')}.com", 
                  "555-123-4567", f"{sup_name} Address", f"Supplier for {sup_name} products"))
            conn.commit()
            
            # Get the new ID
            cursor.execute("SELECT id FROM suppliers WHERE name = ?", (sup_name,))
            new_sup = cursor.fetchone()
            supplier_map[sup_name] = new_sup['id']
    
    # Define allowed units based on database constraint
    # unit TEXT CHECK(unit IN ('units', 'bottles', 'boxes', 'packs', 'grams', 'liters'))
    
    # Sample items data
    items = [
        # Chemicals
        {
            'name': 'Sodium Hydroxide',
            'category': 'chemicals',
            'barcode': '10010001',
            'description': 'Highly caustic base used in various laboratory applications',
            'quantity': 5.0,
            'min_quantity': 1.0,
            'unit': 'grams',
            'location_id': location_map['Chemical Cabinet A'],
            'supplier_id': supplier_map['ChemPure Reagents'],
            'price': 45.99,
            'status': 'in_stock',
            'hazard_type': 'corrosive',
            'storage_condition': 'dry',
            'msds_url': 'https://example.com/msds/naoh.pdf'
        },
        {
            'name': 'Hydrochloric Acid',
            'category': 'chemicals',
            'barcode': '10010002',
            'description': 'Strong acid solution (37%) for chemical reactions and pH adjustments',
            'quantity': 2.0,
            'min_quantity': 0.5,
            'unit': 'liters',
            'location_id': location_map['Chemical Cabinet A'],
            'supplier_id': supplier_map['ChemPure Reagents'],
            'price': 38.50,
            'status': 'in_stock',
            'hazard_type': 'corrosive',
            'storage_condition': 'ventilated',
            'msds_url': 'https://example.com/msds/hcl.pdf'
        },
        {
            'name': 'Ethanol (99.5%)',
            'category': 'chemicals',
            'barcode': '10010003',
            'description': 'High-purity ethanol for molecular biology and general lab use',
            'quantity': 10.0,
            'min_quantity': 2.0,
            'unit': 'liters',
            'location_id': location_map['Chemical Cabinet A'],
            'supplier_id': supplier_map['ChemPure Reagents'],
            'price': 52.75,
            'status': 'in_stock',
            'hazard_type': 'flammable',
            'storage_condition': 'room_temperature',
            'msds_url': 'https://example.com/msds/ethanol.pdf'
        },
        {
            'name': 'Methylene Blue',
            'category': 'chemicals',
            'barcode': '10010004',
            'description': 'Biological stain for microscopy and cell staining applications',
            'quantity': 0.1,
            'min_quantity': 0.05,
            'unit': 'grams',
            'location_id': location_map['Chemical Cabinet A'],
            'supplier_id': supplier_map['ChemPure Reagents'],
            'price': 75.00,
            'status': 'low_stock',
            'hazard_type': 'harmful',
            'storage_condition': 'room_temperature',
            'msds_url': 'https://example.com/msds/methylene-blue.pdf'
        },
        {
            'name': 'Acetic Acid Glacial',
            'category': 'chemicals',
            'barcode': '10010005',
            'description': 'Concentrated acetic acid (99.5%) for various laboratory applications',
            'quantity': 2.5,
            'min_quantity': 1.0,
            'unit': 'liters',
            'location_id': location_map['Chemical Cabinet A'],
            'supplier_id': supplier_map['ChemPure Reagents'],
            'price': 42.25,
            'status': 'in_stock',
            'hazard_type': 'corrosive',
            'storage_condition': 'ventilated',
            'msds_url': 'https://example.com/msds/acetic-acid.pdf'
        },
        {
            'name': 'Formaldehyde Solution',
            'category': 'chemicals',
            'barcode': '10010006',
            'description': '37% formaldehyde solution for tissue preservation and fixation',
            'quantity': 0.0,
            'min_quantity': 1.0,
            'unit': 'liters',
            'location_id': location_map['Chemical Cabinet A'],
            'supplier_id': supplier_map['ChemPure Reagents'],
            'price': 35.99,
            'status': 'out_of_stock',
            'hazard_type': 'toxic',
            'storage_condition': 'ventilated',
            'msds_url': 'https://example.com/msds/formaldehyde.pdf'
        },
        
        # Equipment
        {
            'name': 'Digital Analytical Balance',
            'category': 'equipment',
            'barcode': '20010001',
            'description': 'High-precision balance with 0.0001g readability for accurate mass measurements',
            'quantity': 2.0,
            'min_quantity': 1.0,
            'unit': 'units',
            'location_id': location_map['Equipment Shelf B'],
            'supplier_id': supplier_map['LabEquip Co.'],
            'price': 1250.00,
            'status': 'in_stock',
            'hazard_type': '',
            'storage_condition': 'room_temperature',
            'msds_url': ''
        },
        {
            'name': 'Hot Plate Stirrer',
            'category': 'equipment',
            'barcode': '20010002',
            'description': 'Combined hot plate and magnetic stirrer for heating and mixing solutions',
            'quantity': 3.0,
            'min_quantity': 1.0,
            'unit': 'units',
            'location_id': location_map['Equipment Shelf B'],
            'supplier_id': supplier_map['LabEquip Co.'],
            'price': 385.50,
            'status': 'in_stock',
            'hazard_type': '',
            'storage_condition': 'room_temperature',
            'msds_url': ''
        },
        {
            'name': 'Laboratory Centrifuge',
            'category': 'equipment',
            'barcode': '20010003',
            'description': 'Bench-top centrifuge for sample separation with maximum speed of 4500 RPM',
            'quantity': 1.0,
            'min_quantity': 1.0,
            'unit': 'units',
            'location_id': location_map['Equipment Shelf B'],
            'supplier_id': supplier_map['LabEquip Co.'],
            'price': 2750.00,
            'status': 'in_stock',
            'hazard_type': '',
            'storage_condition': 'room_temperature',
            'msds_url': ''
        },
        {
            'name': 'Digital pH Meter',
            'category': 'equipment',
            'barcode': '20010004',
            'description': 'Accurate pH measurement device with automatic temperature compensation',
            'quantity': 0.0,
            'min_quantity': 1.0,
            'unit': 'units',
            'location_id': location_map['Equipment Shelf B'],
            'supplier_id': supplier_map['LabEquip Co.'],
            'price': 495.00,
            'status': 'out_of_stock',
            'hazard_type': '',
            'storage_condition': 'room_temperature',
            'msds_url': ''
        },
        
        # Glassware
        {
            'name': 'Beaker Set (50-1000mL)',
            'category': 'glassware',
            'barcode': '30010001',
            'description': 'Set of borosilicate glass beakers in various sizes (50, 100, 250, 500, 1000mL)',
            'quantity': 5.0,
            'min_quantity': 2.0,
            'unit': 'units',
            'location_id': location_map['Glassware Cabinet'],
            'supplier_id': supplier_map['GlassTech Solutions'],
            'price': 85.75,
            'status': 'in_stock',
            'hazard_type': '',
            'storage_condition': 'room_temperature',
            'msds_url': ''
        },
        {
            'name': 'Erlenmeyer Flask Set',
            'category': 'glassware',
            'barcode': '30010002',
            'description': 'Set of borosilicate glass Erlenmeyer flasks (100, 250, 500mL)',
            'quantity': 3.0,
            'min_quantity': 1.0,
            'unit': 'units',
            'location_id': location_map['Glassware Cabinet'],
            'supplier_id': supplier_map['GlassTech Solutions'],
            'price': 75.50,
            'status': 'in_stock',
            'hazard_type': '',
            'storage_condition': 'room_temperature',
            'msds_url': ''
        },
        {
            'name': 'Volumetric Flask (100mL)',
            'category': 'glassware',
            'barcode': '30010003',
            'description': 'Class A volumetric flask with ground glass stopper for precise measurements',
            'quantity': 8.0,
            'min_quantity': 2.0,
            'unit': 'units',
            'location_id': location_map['Glassware Cabinet'],
            'supplier_id': supplier_map['GlassTech Solutions'],
            'price': 28.95,
            'status': 'in_stock',
            'hazard_type': '',
            'storage_condition': 'room_temperature',
            'msds_url': ''
        },
        {
            'name': 'Glass Petri Dishes',
            'category': 'glassware',
            'barcode': '30010004',
            'description': 'Borosilicate glass petri dishes (100mm diameter) for cell culture and microbiological applications',
            'quantity': 15.0,
            'min_quantity': 5.0,
            'unit': 'units',
            'location_id': location_map['Glassware Cabinet'],
            'supplier_id': supplier_map['GlassTech Solutions'],
            'price': 8.50,
            'status': 'in_stock',
            'hazard_type': '',
            'storage_condition': 'room_temperature',
            'msds_url': ''
        },
        {
            'name': 'Glass Test Tubes',
            'category': 'glassware',
            'barcode': '30010005',
            'description': 'Standard borosilicate glass test tubes (16x150mm) for various laboratory procedures',
            'quantity': 50.0,
            'min_quantity': 10.0,
            'unit': 'units',
            'location_id': location_map['Glassware Cabinet'],
            'supplier_id': supplier_map['GlassTech Solutions'],
            'price': 0.75,
            'status': 'in_stock',
            'hazard_type': '',
            'storage_condition': 'room_temperature',
            'msds_url': ''
        },
        
        # Consumables
        {
            'name': 'Nitrile Gloves (Small)',
            'category': 'consumables',
            'barcode': '40010001',
            'description': 'Powder-free nitrile examination gloves, small size, 100 gloves per box',
            'quantity': 10.0,
            'min_quantity': 3.0,
            'unit': 'boxes',
            'location_id': location_map['Main Storage Room'],
            'supplier_id': supplier_map['SciSupply Inc.'],
            'price': 12.99,
            'status': 'in_stock',
            'hazard_type': '',
            'storage_condition': 'room_temperature',
            'msds_url': ''
        },
        {
            'name': 'Nitrile Gloves (Medium)',
            'category': 'consumables',
            'barcode': '40010002',
            'description': 'Powder-free nitrile examination gloves, medium size, 100 gloves per box',
            'quantity': 8.0,
            'min_quantity': 3.0,
            'unit': 'boxes',
            'location_id': location_map['Main Storage Room'],
            'supplier_id': supplier_map['SciSupply Inc.'],
            'price': 12.99,
            'status': 'in_stock',
            'hazard_type': '',
            'storage_condition': 'room_temperature',
            'msds_url': ''
        },
        {
            'name': 'Nitrile Gloves (Large)',
            'category': 'consumables',
            'barcode': '40010003',
            'description': 'Powder-free nitrile examination gloves, large size, 100 gloves per box',
            'quantity': 2.0,
            'min_quantity': 3.0,
            'unit': 'boxes',
            'location_id': location_map['Main Storage Room'],
            'supplier_id': supplier_map['SciSupply Inc.'],
            'price': 12.99,
            'status': 'low_stock',
            'hazard_type': '',
            'storage_condition': 'room_temperature',
            'msds_url': ''
        },
        {
            'name': 'Pipette Tips (10µL)',
            'category': 'consumables',
            'barcode': '40010004',
            'description': 'Sterile micropipette tips for 0.1-10µL pipettes, 96 tips per rack',
            'quantity': 15.0,
            'min_quantity': 5.0,
            'unit': 'packs',
            'location_id': location_map['Main Storage Room'],
            'supplier_id': supplier_map['Bio-Research Supplies'],
            'price': 9.95,
            'status': 'in_stock',
            'hazard_type': '',
            'storage_condition': 'room_temperature',
            'msds_url': ''
        },
        {
            'name': 'Pipette Tips (200µL)',
            'category': 'consumables',
            'barcode': '40010005',
            'description': 'Sterile micropipette tips for 20-200µL pipettes, 96 tips per rack',
            'quantity': 18.0,
            'min_quantity': 5.0,
            'unit': 'packs',
            'location_id': location_map['Main Storage Room'],
            'supplier_id': supplier_map['Bio-Research Supplies'],
            'price': 10.50,
            'status': 'in_stock',
            'hazard_type': '',
            'storage_condition': 'room_temperature',
            'msds_url': ''
        },
        {
            'name': 'Pipette Tips (1000µL)',
            'category': 'consumables',
            'barcode': '40010006',
            'description': 'Sterile micropipette tips for 100-1000µL pipettes, 96 tips per rack',
            'quantity': 1.0,
            'min_quantity': 5.0,
            'unit': 'packs',
            'location_id': location_map['Main Storage Room'],
            'supplier_id': supplier_map['Bio-Research Supplies'],
            'price': 12.75,
            'status': 'low_stock',
            'hazard_type': '',
            'storage_condition': 'room_temperature',
            'msds_url': ''
        },
        {
            'name': 'Microcentrifuge Tubes (1.5mL)',
            'category': 'consumables',
            'barcode': '40010007',
            'description': 'Clear polypropylene microcentrifuge tubes, 1.5mL capacity, 500 tubes per pack',
            'quantity': 3.0,
            'min_quantity': 1.0,
            'unit': 'packs',
            'location_id': location_map['Main Storage Room'],
            'supplier_id': supplier_map['Bio-Research Supplies'],
            'price': 18.95,
            'status': 'in_stock',
            'hazard_type': '',
            'storage_condition': 'room_temperature',
            'msds_url': ''
        },
        {
            'name': 'PCR Tubes (0.2mL)',
            'category': 'consumables',
            'barcode': '40010008',
            'description': 'Clear 0.2mL PCR tubes with attached caps, compatible with standard thermal cyclers, 1000 tubes per pack',
            'quantity': 2.0,
            'min_quantity': 1.0,
            'unit': 'packs',
            'location_id': location_map['Main Storage Room'],
            'supplier_id': supplier_map['Bio-Research Supplies'],
            'price': 35.00,
            'status': 'in_stock',
            'hazard_type': '',
            'storage_condition': 'room_temperature',
            'msds_url': ''
        }
    ]
    
    # Get the current timestamp
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Add default values for required fields
    for item in items:
        item['expiry_date'] = None
        item['created_at'] = current_time
        
        # Empty hazard_type is not allowed, must be one of the allowed values
        if 'hazard_type' in item and (item['hazard_type'] is None or item['hazard_type'] == ''):
            item['hazard_type'] = 'harmful'  # Set a default value
    
    # Generate expiry dates for chemicals (some past, some coming soon, some far in future)
    for item in items:
        if item['category'] == 'chemicals':
            days = random.choice([-90, -30, 30, 60, 180, 365])
            exp_date = (datetime.datetime.now() + datetime.timedelta(days=days)).strftime('%Y-%m-%d')
            item['expiry_date'] = exp_date
            
            # Mark as expiring soon if within 30 days
            if 0 < days <= 30 and item['status'] == 'in_stock':
                item['status'] = 'expiring_soon'
    
    for item in items:
        cursor.execute("""
            INSERT INTO items (name, category, barcode, description, quantity, min_quantity, 
                unit, location_id, supplier_id, price, status, hazard_type, 
                storage_condition, msds_url, expiry_date, created_at)
            VALUES (:name, :category, :barcode, :description, :quantity, :min_quantity, 
                :unit, :location_id, :supplier_id, :price, :status, :hazard_type, 
                :storage_condition, :msds_url, :expiry_date, :created_at)
        """, item)
    
    conn.commit()
    print(f"Added {len(items)} sample inventory items")

def add_sample_transactions(conn):
    """Add sample transaction records"""
    cursor = conn.cursor()
    
    # Check if we already have sample transactions
    cursor.execute("SELECT COUNT(*) as count FROM transactions")
    result = cursor.fetchone()
    
    if result['count'] > 0:
        print("Transactions already exist in the database, skipping sample transaction creation.")
        return
    
    # Get user IDs
    cursor.execute("SELECT id, username FROM users")
    users = cursor.fetchall()
    user_ids = [user['id'] for user in users]
    
    # Get item IDs
    cursor.execute("SELECT id, name, quantity FROM items")
    items = cursor.fetchall()
    item_ids = [item['id'] for item in items]
    
    # Transaction types
    transaction_types = ['check_in', 'check_out', 'restock', 'dispose']
    
    # Generate random transactions for the past 90 days
    transactions = []
    for _ in range(50):
        # Choose a random date within the past 90 days
        days_ago = random.randint(0, 90)
        transaction_date = (datetime.datetime.now() - datetime.timedelta(days=days_ago)).strftime('%Y-%m-%d %H:%M:%S')
        
        # Random item and user
        item_id = random.choice(item_ids)
        user_id = random.choice(user_ids)
        
        # Random type and quantity
        transaction_type = random.choice(transaction_types)
        if transaction_type == 'restock':
            quantity = round(random.uniform(5, 20), 2)
        elif transaction_type == 'check_out' or transaction_type == 'dispose':
            quantity = round(random.uniform(0.1, 5), 2)
        else:  # check_in
            quantity = round(random.uniform(0.1, 3), 2)
        
        transactions.append({
            'item_id': item_id,
            'type': transaction_type,
            'quantity': quantity,
            'timestamp': transaction_date,
            'user_id': user_id,
            'notes': f'Sample {transaction_type} transaction'
        })
    
    for transaction in transactions:
        cursor.execute("""
            INSERT INTO transactions (item_id, type, quantity, timestamp, user_id, notes)
            VALUES (:item_id, :type, :quantity, :timestamp, :user_id, :notes)
        """, transaction)
    
    conn.commit()
    print(f"Added {len(transactions)} sample transactions")

def add_sample_orders(conn):
    """Add sample order records"""
    cursor = conn.cursor()
    
    # Check if we already have sample orders
    cursor.execute("SELECT COUNT(*) as count FROM orders")
    result = cursor.fetchone()
    
    if result['count'] > 0:
        print("Orders already exist in the database, skipping sample order creation.")
        return
    
    # Get supplier IDs
    cursor.execute("SELECT id FROM suppliers")
    suppliers = cursor.fetchall()
    supplier_ids = [supplier['id'] for supplier in suppliers]
    
    # Get user IDs with admin or lab_manager roles
    cursor.execute("SELECT id FROM users WHERE role IN ('admin', 'lab_manager')")
    users = cursor.fetchall()
    user_ids = [user['id'] for user in users]
    
    # Order statuses
    statuses = ['pending', 'approved', 'ordered', 'received', 'cancelled']
    
    # Generate random orders for the past 180 days
    orders = []
    for i in range(15):
        # Choose a random date within the past 180 days
        days_ago = random.randint(0, 180)
        order_date = (datetime.datetime.now() - datetime.timedelta(days=days_ago)).strftime('%Y-%m-%d %H:%M:%S')
        
        # Random supplier and user
        supplier_id = random.choice(supplier_ids)
        user_id = random.choice(user_ids)
        
        # Random status based on days ago (ensuring all weights are positive)
        base_weight = 5
        status_weight = max(1, base_weight - min(int(days_ago / 40), 4))  # Ensure minimum weight of 1
        weights = [
            status_weight,                     # pending
            max(1, status_weight - 1),         # approved
            max(1, status_weight - 2),         # ordered 
            max(1, status_weight - 3),         # received
            1                                  # cancelled
        ]
        status = random.choices(statuses, weights=weights)[0]
        
        # Random total cost
        total_cost = round(random.uniform(100, 2000), 2)
        
        orders.append({
            'supplier_id': supplier_id,
            'status': status,
            'created_at': order_date,
            'ordered_by': user_id,
            'notes': f'Sample order #{i+1} (Estimated cost: ${total_cost:.2f})'
        })
    
    for order in orders:
        cursor.execute("""
            INSERT INTO orders (supplier_id, status, created_at, ordered_by, notes)
            VALUES (:supplier_id, :status, :created_at, :ordered_by, :notes)
        """, order)
    
    conn.commit()
    print(f"Added {len(orders)} sample orders")

if __name__ == '__main__':
    init_db()