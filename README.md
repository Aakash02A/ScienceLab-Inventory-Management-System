# Science Laboratory Inventory Management System (SLIMS)

A comprehensive inventory management system designed specifically for scientific research environments, featuring advanced tracking capabilities, role-based access control, and intelligent recommendation algorithms.

## Features

### Core Functionality
- **Complete Inventory Management**: Track chemicals, equipment, glassware, and consumables with detailed metadata
- **Location Tracking**: Organize inventory by location with capacity monitoring
- **Transaction History**: Full audit trail of item movements and usage
- **Order Management**: Request and track orders from suppliers
- **Reporting & Analytics**: Generate insights from inventory and usage data

### Advanced Features
- **Personalized Recommendation Engine**: Context-aware item suggestions based on:
  - Personal usage patterns (50% weight)
  - Department relevance (20% weight)
  - Role-specific patterns (30% weight)
  - Stock availability and category adjustments
- **Role-Based Access Control**: Permissions tailored to different laboratory roles:
  - Admin: Full system access
  - Lab Manager: Inventory management and reporting
  - Researcher: Usage tracking and ordering
  - Student: Limited viewing and basic transactions
- **Safety Compliance**: Track safety data, hazard classifications, and storage requirements

### Technical Highlights
- **Three-Tier Architecture**:
  - Frontend: HTML/CSS/JavaScript with Bootstrap for responsive design
  - Backend: Python Flask framework
  - Database: SQLite for persistent storage
- **RESTful API**: Enables integration with other laboratory systems
- **Barcode/RFID Ready**: Support for scanning technology

## Getting Started

### Prerequisites
- Python 3.x
- Flask and related packages
- Modern web browser
- Internet connection for external API features

### Installation
1. Clone the repository
2. Install required Python packages:
   ```
   pip install -r requirements.txt
   ```
3. Initialize the database:
   ```
   python app.py init_db
   ```
4. Start the application:
   ```
   python run.py
   ```

### Default Credentials
- **Admin**: username: `admin`, password: `admin123`
- **Lab Manager**: username: `manager`, password: `manager123`
- **Researcher**: username: `researcher`, password: `researcher123`
- **Student**: username: `student`, password: `student123`

## Usage Guide

### Navigation
- **Dashboard**: Overview of key metrics and personalized recommendations
- **Inventory**: Direct access to item management
- **Management**: Access locations, suppliers, and reports
- **Orders**: Track and manage purchase orders
- **Recommendations**: View all personalized item suggestions

### Key Workflows
1. **Adding New Items**: Inventory → Add Item
2. **Checking Out Items**: Inventory → View Item → Check Out
3. **Placing Orders**: Orders → New Order
4. **Viewing Reports**: Management → Reports
5. **Managing Locations**: Management → Locations

## Recommendation Algorithm

The system uses a sophisticated weighted scoring system to generate personalized inventory recommendations:

- **Personal Usage Score** (0-5 points, 0.5 weight multiplier)
  - Based on frequency and recency of personal use
  
- **Department Relevance** (0-3 points, 0.2 weight multiplier)
  - Based on department-wide usage patterns
  
- **Role Patterns** (0-4 points, 0.3 weight multiplier)
  - Based on typical usage for user's role
  
- **Adjustments**:
  - Low stock: -1 point
  - Role-category match: +2 points for relevant categories
  
The system stores up to 15 recommendations with the top 3 displayed on the dashboard.

## Security and Permissions

- **Role-Based Access Control**: Different permissions for various user types
- **Transaction Logging**: All actions are recorded for audit purposes
- **Data Validation**: Input validation to prevent security vulnerabilities

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- Bootstrap for responsive UI components
- Flask framework for backend functionality
- SQLite for database storage