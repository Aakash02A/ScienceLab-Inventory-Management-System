# Architecture: Science Laboratory Inventory Management System (SLIMS)

## 1. Overview

The Science Laboratory Inventory Management System (SLIMS) is a comprehensive web-based application designed to manage inventory for scientific research environments. It provides facilities for tracking chemicals, equipment, glassware, and consumables with detailed metadata, location tracking, transaction history, order management, and analytics.

The system follows a three-tier architecture with a clear separation of concerns:
- **Frontend**: HTML/CSS/JavaScript with Bootstrap for responsive design
- **Backend**: Python Flask framework for server-side logic
- **Database**: SQLite for persistent storage

The application implements role-based access control with four roles (Admin, Lab Manager, Researcher, and Student) and features a personalized recommendation engine that suggests items based on usage patterns, department relevance, and role-specific patterns.

## 2. System Architecture

### 2.1 High-Level Architecture

SLIMS follows a classic three-tier architecture:

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Frontend  │────▶│   Backend   │────▶│   Database  │
│  (HTML/JS)  │◀────│   (Flask)   │◀────│   (SQLite)  │
└─────────────┘     └─────────────┘     └─────────────┘
```

1. **Presentation Layer (Frontend)**:
   - HTML templates with Jinja2 templating engine
   - CSS with Bootstrap for responsive design
   - JavaScript for client-side interactions
   - Animate.css for animations

2. **Application Layer (Backend)**:
   - Flask web framework for request handling
   - Python business logic
   - RESTful API endpoints
   - Session-based authentication

3. **Data Layer (Database)**:
   - SQLite database
   - SQL queries for data manipulation
   - In-memory caching for performance

### 2.2 Component Diagram

```
┌────────────────────────────────────────────────────────┐
│                      Client Browser                     │
└───────────────────────────┬────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────┐
│                      Flask Application                  │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
│  │    Views    │───▶│  Controllers│───▶│   Models    │ │
│  │  (Templates)│◀───│   (Routes)  │◀───│  (DB Logic) │ │
│  └─────────────┘    └─────────────┘    └──────┬──────┘ │
└────────────────────────────────────────────┬──┴────────┘
                                             │
┌────────────────────────────────────────────▼────────────┐
│                     SQLite Database                      │
└────────────────────────────────────────────────────────┘
```

## 3. Key Components

### 3.1 Frontend Components

The frontend is built using HTML templates with Bootstrap for responsive design and JavaScript for interactivity:

- **Base Template**: Provides the common layout and navigation elements
- **Dashboard**: Main user interface with key metrics and recent activity
- **Inventory Management**: UI for managing laboratory items
- **Transaction Management**: Interface for recording and viewing item movements
- **Order Management**: UI for creating and tracking purchase orders
- **Reports and Analytics**: Dashboards and visualizations for data analysis
- **User Management**: Interfaces for user administration

The frontend uses several technologies for enhanced user experience:
- **Bootstrap 5**: For responsive design and UI components
- **Animate.css**: For animations and transitions
- **Font Awesome/Bootstrap Icons**: For iconography
- **Custom JavaScript**: For client-side interactivity

### 3.2 Backend Components

The backend is built using Flask, a Python web framework:

1. **Authentication and Authorization**:
   - Session-based authentication
   - Role-based access control (Admin, Lab Manager, Researcher, Student)
   - Password hashing with bcrypt

2. **Route Controllers**:
   - HTTP endpoint handlers
   - Request validation
   - Response formatting

3. **Database Models**:
   - SQLite connection management
   - Data access and manipulation logic
   - Transaction handling

4. **Business Logic Services**:
   - Inventory management
   - Transaction processing
   - Order management
   - Recommendation engine

### 3.3 Database Schema

The database uses SQLite and follows a relational model with the following key tables:

1. **Users**: Store user accounts and role information
   - Fields: id, username, password, name, email, role, department, created_at

2. **Locations**: Track storage locations within the laboratory
   - Fields: id, name, description, capacity, created_at

3. **Suppliers**: Track vendor information
   - Fields: id, name, contact_person, email, phone, address, notes

4. **Items**: Store inventory items
   - Fields: id, name, category, barcode, description, quantity, min_quantity, unit, location_id, hazard_level, storage_requirements, supplier_id, unit_cost

5. **Transactions**: Record item movements and usage
   - Fields: id, item_id, type, quantity, timestamp, user_id, notes

6. **Orders**: Manage purchase requests
   - Fields: id, supplier_id, status, created_at, user_id, notes, total_cost

### 3.4 Recommendation Engine

The system includes a personalized recommendation engine that suggests items based on:
- Personal usage patterns (50% weight)
- Department relevance (20% weight)
- Role-specific patterns (30% weight)
- Stock availability and category adjustments

The engine uses historical data to generate context-aware recommendations, helping users discover items relevant to their work.

## 4. Data Flow

### 4.1 Authentication Flow

```
┌────────┐    ┌─────────────┐    ┌──────────────┐    ┌──────────┐
│  User  │───▶│ Login Form  │───▶│ Authenticate │───▶│ Dashboard│
└────────┘    └─────────────┘    └──────────────┘    └──────────┘
                                         │
                                         ▼
                                  ┌──────────────┐
                                  │  User Table  │
                                  └──────────────┘
```

1. User submits login credentials
2. Backend verifies credentials against the database
3. On success, a session is created and user is redirected to dashboard
4. On failure, an error message is displayed

### 4.2 Inventory Management Flow

```
┌────────┐    ┌───────────────┐    ┌──────────────┐
│  User  │───▶│ Inventory UI  │───▶│ Add/Edit/    │
└────────┘    └───────────────┘    │ Delete Item  │
                                   └──────┬───────┘
                                          │
                                          ▼
                                   ┌──────────────┐
                                   │  Items Table │
                                   └──────────────┘
```

1. User navigates to the inventory management interface
2. User performs CRUD operations on items
3. Backend validates and persists changes to the database
4. UI is updated to reflect changes

### 4.3 Transaction Flow

```
┌────────┐    ┌───────────────┐    ┌──────────────┐    ┌──────────────┐
│  User  │───▶│ Transaction UI│───▶│ Record       │───▶│ Update Item  │
└────────┘    └───────────────┘    │ Transaction  │    │ Quantity     │
                                   └──────┬───────┘    └──────┬───────┘
                                          │                    │
                                          ▼                    ▼
                                   ┌──────────────┐    ┌──────────────┐
                                   │Transactions  │    │  Items Table │
                                   │Table         │    │              │
                                   └──────────────┘    └──────────────┘
```

1. User records a transaction (check-in, check-out, restock, dispose)
2. Backend validates the transaction
3. Item quantities are updated accordingly
4. Transaction is recorded in the database

## 5. External Dependencies

### 5.1 Frontend Dependencies

- **Bootstrap 5**: Frontend framework for responsive design
- **Bootstrap Icons**: Icon library
- **Animate.css**: Animation library
- **Various JavaScript libraries**: For enhanced UI interactions

### 5.2 Backend Dependencies

- **Flask**: Web framework
- **Flask-CORS**: Cross-origin resource sharing
- **Flask-Session**: Session management
- **Jinja2**: Templating engine
- **bcrypt**: Password hashing
- **python-dotenv**: Environment variable management
- **Werkzeug**: WSGI utilities

### 5.3 Development and Deployment Dependencies

- **Node.js**: JavaScript runtime
- **Better-SQLite3**: SQLite database driver
- **esbuild**: JavaScript bundler
- **vite**: Frontend build tool
- **TypeScript**: Typed JavaScript
- **tsx**: TypeScript execution environment

## 6. Deployment Strategy

The application is configured for multiple deployment scenarios:

### 6.1 Development Environment

- Uses `npm run dev` script to start the development server
- Flask runs in debug mode for easier development
- Auto-opens browser for local testing

### 6.2 Production Deployment

- Two-step build process:
  1. Build frontend assets with Vite
  2. Bundle server code with esbuild
- Configured for serverless deployment with Replit
- Environment variables used for configuration

### 6.3 Deployment Configuration

The repository includes:
- `.replit` configuration for Replit deployment
- `Procfile`-like configuration in package.json for general deployment
- PORT environment variable support for flexible hosting

### 6.4 Database Strategy

- SQLite for simplicity and portability
- Database initialization script included
- Backup and migration capabilities via export/import

## 7. Security Considerations

### 7.1 Authentication Security

- Passwords hashed using bcrypt
- Session-based authentication
- HTTPS recommended for production

### 7.2 Authorization Controls

- Role-based access control
- Permission checking on both frontend and backend
- Session validation for all protected routes

### 7.3 Data Protection

- Input validation for all form submissions
- SQL query parameters to prevent injection
- Session secret stored in environment variables

## 8. Future Extensibility

The architecture is designed to be extensible in several ways:

1. **API Development**: The system can be extended to provide RESTful APIs for integration with other laboratory systems.

2. **Barcode/RFID Integration**: The system is ready for integration with scanning technology for more automated inventory tracking.

3. **Advanced Analytics**: The data model supports expansion for more sophisticated reporting and business intelligence.

4. **Cloud Storage**: The system can be modified to use cloud storage for attachments and documentation.

5. **Mobile Application**: The architecture supports the development of companion mobile applications through API exposure.