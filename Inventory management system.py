import sqlite3
from datetime import datetime

# Establish a connection to the SQLite database
conn = sqlite3.connect("inventory_management.db")
cursor = conn.cursor()

# Step 1: Initialize Database Tables
def initialize_db():
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Items (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            contact_info TEXT,
            description TEXT,
            quantity INTEGER NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Transactions (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER,
            action_type TEXT,
            quantity INTEGER,
            date_time TEXT,
            description TEXT,
            FOREIGN KEY(item_id) REFERENCES Items(item_id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Updates (
            update_id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER,
            updated_field TEXT,
            old_value TEXT,
            new_value TEXT,
            update_time TEXT,
            FOREIGN KEY(item_id) REFERENCES Items(item_id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Payments (
            payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id INTEGER,
            amount_paid REAL,
            payment_method TEXT,
            payment_status TEXT,
            FOREIGN KEY(transaction_id) REFERENCES Transactions(transaction_id)
        )
    ''')
    conn.commit()
    print("Database initialized successfully.")

# Step 2: Data Entry Form
def add_item():
    name = input("Enter Item Name: ")
    contact_info = input("Enter Supplier Contact (phone/email): ")
    description = input("Enter Item Description: ")
    quantity = int(input("Enter Quantity: "))

    cursor.execute("INSERT INTO Items (name, contact_info, description, quantity) VALUES (?, ?, ?, ?)",
                   (name, contact_info, description, quantity))
    conn.commit()
    print("Item added successfully.")

# Step 3: Transaction Form
def record_transaction():
    item_id = int(input("Enter Item ID: "))
    action_type = input("Enter Action Type (Purchase/Sale): ")
    quantity = int(input("Enter Quantity: "))
    description = input("Enter Description of Action: ")
    date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Check if sufficient quantity exists for a sale
    cursor.execute("SELECT quantity FROM Items WHERE item_id = ?", (item_id,))
    result = cursor.fetchone()
    if result:
        current_quantity = result[0]
        if action_type.lower() == "sale" and current_quantity < quantity:
            print("Insufficient stock for sale.")
            return

        # Update item quantity for sale or purchase
        new_quantity = current_quantity + quantity if action_type.lower() == "purchase" else current_quantity - quantity
        cursor.execute("UPDATE Items SET quantity = ? WHERE item_id = ?", (new_quantity, item_id))

        # Record transaction
        cursor.execute("INSERT INTO Transactions (item_id, action_type, quantity, date_time, description) VALUES (?, ?, ?, ?, ?)",
                       (item_id, action_type, quantity, date_time, description))
        conn.commit()
        print("Transaction recorded successfully.")
    else:
        print("Item not found.")

# Step 4: Update/Modification Form
def update_item():
    item_id = int(input("Enter Item ID to update: "))
    field_to_update = input("Enter field to update (name/contact_info/description/quantity): ")
    new_value = input("Enter new value: ")
    
    # Fetch current value
    cursor.execute(f"SELECT {field_to_update} FROM Items WHERE item_id = ?", (item_id,))
    result = cursor.fetchone()
    if result:
        old_value = result[0]
        # Update the field in Items table
        cursor.execute(f"UPDATE Items SET {field_to_update} = ? WHERE item_id = ?", (new_value, item_id))

        # Log update in Updates table
        update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO Updates (item_id, updated_field, old_value, new_value, update_time) VALUES (?, ?, ?, ?, ?)",
                       (item_id, field_to_update, old_value, new_value, update_time))
        conn.commit()
        print("Item updated successfully.")
    else:
        print("Item not found.")

# Step 5: Payment/Status Update Form
def record_payment():
    transaction_id = int(input("Enter Transaction ID: "))
    amount_paid = float(input("Enter Amount Paid: "))
    payment_method = input("Enter Payment Method (Cash/Credit): ")
    payment_status = input("Enter Payment Status (Paid/Pending): ")

    cursor.execute("INSERT INTO Payments (transaction_id, amount_paid, payment_method, payment_status) VALUES (?, ?, ?, ?)",
                   (transaction_id, amount_paid, payment_method, payment_status))
    conn.commit()
    print("Payment recorded successfully.")

# Step 6: Report Generation
def generate_report():
    report_type = input("Enter Report Type (overview/transaction/payment): ")
    if report_type == "overview":
        cursor.execute("SELECT * FROM Items")
        items = cursor.fetchall()
        print("\n--- Item Overview Report ---")
        for item in items:
            print(item)
    elif report_type == "transaction":
        cursor.execute("SELECT * FROM Transactions")
        transactions = cursor.fetchall()
        print("\n--- Transaction Report ---")
        for transaction in transactions:
            print(transaction)
    elif report_type == "payment":
        cursor.execute("SELECT * FROM Payments")
        payments = cursor.fetchall()
        print("\n--- Payment Report ---")
        for payment in payments:
            print(payment)
    else:
        print("Invalid report type.")

# Main Menu
def main_menu():
    initialize_db()
    while True:
        print("\n--- Inventory Management System ---")
        print("1. Add Item")
        print("2. Record Transaction")
        print("3. Update Item")
        print("4. Record Payment")
        print("5. Generate Report")
        print("6. Exit")
        choice = input("Select an option: ")

        if choice == "1":
            add_item()
        elif choice == "2":
            record_transaction()
        elif choice == "3":
            update_item()
        elif choice == "4":
            record_payment()
        elif choice == "5":
            generate_report()
        elif choice == "6":
            print("Exiting system.")
            break
        else:
            print("Invalid choice. Please try again.")

# Run the main menu
if __name__ == "__main__":
    main_menu()
    conn.close()