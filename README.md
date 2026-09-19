# POS Backend API
This project is a complete Point of Sale (POS) backend system built for a small boutique shop. It provides a secure way to handle daily retail tasks like tracking shop attendants, managing clothing and accessory inventory, recording sales transactions, and logging customer payments.
The application is written in Python. It uses FastAPI to build the web links (endpoints), SQLAlchemy to handle database queries using Python objects, and PostgreSQL as the relational database to save all store transactions safely.

## Folder Structure
The system is organized into a clean, layered structure to keep the code manageable. Here is what each folder inside the app directory does:
*app/models/*: Defines the database tables. This is where we design what our data looks like in PostgreSQL, including columns, data types and links between tables (Foreign Keys).
*app/schemas/*: Handles data validation rules. These files use Pydantic to double-check incoming user inputs (like checking if an email is valid or ensuring an item price value is not negative) before processing it.
*app/repositories/*: Manages direct database communication. This layer contains the raw database query logic to add, read, update or remove records from the tables.
*app/services/*: Holds core business calculations. This layer processes business logic and applies boutique rules (like processing discounts or computing totals) before database entry.
*app/routers/*: Creates the web endpoints. These files map the backend logic to specific URLs so they can be securely requested by frontend apps or tested inside Swagger UI.
*env/*: The Python virtual environment folder. It isolates all installed packages required by this project.

## Relational Database Management
The system utilizes PostgreSQL to ensure structural data integrity and transaction safety. Relational constraints are strictly enforced across all data tables:   
- Foreign Keys: Links payments to sales, and sales to both customers and shop attendants.  
- Cascading Rules: Prevents orphaned records if a parent transaction or user account is modified.  
- UUID Keys: Employs globally unique identifiers for IDs to protect internal transaction counts from exposure.  
- Timezone Consistency: Configured to handle database timestamps smoothly without mismatching sales dates.

**Core Features and Validation**
The backend handles the vital operational workflows of a retail boutique:  
**Inventory Control**: Tracks stock levels and prevents sales of items not currently in inventory.  
**Role Enforcement**: Restricts sensitive management functions to authorized store managers.  
**Pydantic Validation**: Inspects incoming API requests to ensure strings match expected formats (e.g., valid emails).  
**Business Calculations**: Computes transaction totals, tax variations, and payment balances dynamically. 

## Endpoints Summary
The API splits your boutique’s web endpoints into sections to handle different parts of the business:  
*/users*: Registers shop attendants and manages secure login access.  
*/customers*: Keeps track of buyer profiles and contact histories.  
*/suppliers*: Manages the clothing brands and vendors providing store inventory.  
*/categories*: Groups boutique items logically (e.g., Dresses, Shoes, Accessories).  
*/product*: Controls item names, size options, costs and stock volumes.  
*/sale*: Launches checkout sessions and creates transaction logs.  
*/sale_item*: Breaks down individual quantities and line items inside a specific receipt.  
*/payment*: Processes cash or digital payments and links them immediately to an open sale.  
*/receipt*: Finalizes transactions and compiles clean printable summary balances.

## System Dependencies
The application relies on a modern, high-performance Python ecosystem:  
**FastAPI**: A high-speed web framework used to construct the API routing paths.    
**SQLAlchemy**: An Object-Relational Mapper (ORM) that translates Python code into secure SQL statements.    
**Uvicorn**: An ASGI web server implementation used to run the application locally.    
**Psycopg2**: The database adapter required for Python to communicate directly with PostgreSQL. 

## Running Tests

This project uses `pytest` with an isolated SQLite database, so tests never touch your real PostgreSQL database.

### Setup

Make sure your virtual environment is active and dependencies are installed:

​```bash
pip install -r requirements.txt
​```

### Run the full test suite

From the project root:

​```bash
pytest
​```

### Run a specific file or test

​```bash
pytest tests/test_products.py          # one file
pytest tests/test_products.py::test_create_product_as_admin   # one test
pytest -v                              # verbose output, shows each test name
​```

Tests run automatically on every push and pull request via GitHub Actions (see `.github/workflows/tests.yml`).
