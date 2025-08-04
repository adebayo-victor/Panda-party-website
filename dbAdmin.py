# Import the CS50 library to handle database connections and queries.
from cs50 import SQL

# Establish a connection to the database.
# This will create a file named "your_database_name.db" if it does not already exist.
db = SQL("sqlite:///party.db")

# ----------------------------------------------------------------------
# DATABASE SETUP: Create tables and insert dummy data
# ----------------------------------------------------------------------

# Drop existing tables to ensure a clean slate every time the script is run.
# This is useful for testing and demonstration purposes.
db.execute("DROP TABLE IF EXISTS ticket_purchases;")
db.execute("DROP TABLE IF EXISTS ticket_info;")
db.execute("DROP TABLE IF EXISTS clients;")

# Create the clients table with columns for name, email (unique), password hash, and phone number.
db.execute("""
    CREATE TABLE clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        phone_number TEXT NOT NULL
    );
""")

# Create the ticket_info table to store the names of different tickets.
# Updated to include price (using REAL for floating-point numbers) and description.
db.execute("""
    CREATE TABLE ticket_info (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        description TEXT
    );
""")

# Create the ticket_purchases table to link clients and tickets.
# It includes foreign key constraints to ensure data integrity.
db.execute("""
    CREATE TABLE ticket_purchases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER NOT NULL,
        ticket_id INTEGER NOT NULL,
        purchase_date TEXT NOT NULL,
        FOREIGN KEY (client_id) REFERENCES clients(id),
        FOREIGN KEY (ticket_id) REFERENCES ticket_info(id)
    );
""")

# Insert dummy data into the clients table.
db.execute("""
    INSERT INTO clients (name, email, password_hash, phone_number) VALUES
    ('Jane Doe', 'jane.doe@example.com', 'hashed_password_123', '555-1234'),
    ('John Smith', 'john.smith@example.com', 'hashed_password_456', '555-5678'),
    ('Alice Johnson', 'alice.j@example.com', 'hashed_password_789', '555-9012');
""")

# Insert dummy data into the ticket_info table.
# Updated to include dummy values for price and description.
db.execute("""
    INSERT INTO ticket_info (name, price, description) VALUES
    ('Concert Ticket', 75.50, 'A pass for the annual summer music festival.'),
    ('Movie Pass', 12.00, 'Single-use ticket for any movie.'),
    ('Museum Admission', 25.00, 'Access to all permanent and temporary exhibits.'),
    ('Theatre Show', 50.75, 'A seat for the evening performance of a new play.');
""")

# Insert dummy data into the ticket_purchases table for our clients.
# 'jane.doe@example.com' has made a few purchases.
# John Smith has also made a purchase.
db.execute("""
    INSERT INTO ticket_purchases (client_id, ticket_id, purchase_date) VALUES
    (1, 1, '2025-08-01'),  -- Jane Doe: Concert Ticket
    (1, 2, '2025-07-25'),  -- Jane Doe: Movie Pass
    (2, 3, '2025-08-02'),  -- John Smith: Museum Admission
    (1, 4, '2025-08-03');  -- Jane Doe: Theatre Show
""")

# ----------------------------------------------------------------------
# QUERY EXECUTION: Find tickets for a specific client
# ----------------------------------------------------------------------

# Define the email address of the client you want to search for.
client_email = "jane.doe@example.com"

# Execute the SQL query to find the client's purchased tickets.
# The query is updated to select the new price and description columns.
tickets = db.execute("""
    SELECT
        c.name AS client_name,
        c.password_hash,
        c.phone_number,
        ti.name AS ticket_name,
        ti.price,
        ti.description,
        tp.purchase_date
    FROM
        clients AS c
    JOIN
        ticket_purchases AS tp ON c.id = tp.client_id
    JOIN
        ticket_info AS ti ON tp.ticket_id = ti.id
    WHERE
        c.email = ?
    ORDER BY
        tp.purchase_date DESC;
""", client_email)

# Check if any tickets were found.
if tickets:
    # Print the client's details just once at the beginning.
    print(f"Client Details:")
    print("-" * 50)
    print(f"Name:         {tickets[0]['client_name']}")
    print(f"Password Hash: {tickets[0]['password_hash']}")
    print(f"Phone Number: {tickets[0]['phone_number']}")

    # Print a header for the tickets.
    print("\nTickets Purchased:")
    print("-" * 50)
    
    # Iterate through the returned rows and print the details of each ticket.
    # The print statements are updated to show the new price and description.
    for ticket in tickets:
        print(f"Ticket Name:    {ticket['ticket_name']}")
        print(f"Price:          ${ticket['price']:.2f}")
        print(f"Description:    {ticket['description']}")
        print(f"Purchase Date:  {ticket['purchase_date']}")
        print("-" * 50)
else:
    # If no tickets were found, print a message.
    print(f"No tickets found for the client with email: {client_email}.")
