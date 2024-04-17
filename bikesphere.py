import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
import mysql.connector
from mysql.connector import Error

# Database connection parameters
db_config = {
    'host': 'localhost',
    'user': 'root',        # Default XAMPP MySQL username
    'password': '',        # No password for XAMPP MySQL by default
    'database': 'BikeSphere'
}

# Establish connection to MySQL
def connect():
    try:
        conn = mysql.connector.connect(**db_config)
        if conn.is_connected():
            return conn
    except Error as e:
        messagebox.showerror("Error", str(e))

# Function to execute SQL queries
def execute_sql(sql, params=None, commit=False):
    try:
        conn = connect()
        cursor = conn.cursor()
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        if commit:
            conn.commit()
            return cursor.rowcount
        else:
            return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

# GUI setup
root = tk.Tk()
root.title('BikeSphere Management System')
root.geometry('1200x600')  # Adjust the window size

# Style configuration
style = ttk.Style()
style.configure('TButton', font=('Helvetica', 12), padding=10)
style.configure('TLabel', font=('Helvetica', 12), padding=10)
style.configure('TEntry', font=('Helvetica', 12), padding=10)

# Frame for Data Output
frame = ttk.Frame(root, padding="10 10 10 10")
frame.grid(column=0, row=1, columnspan=7, sticky=(tk.W, tk.E, tk.N, tk.S))
frame.columnconfigure(0, weight=1)
frame.rowconfigure(0, weight=1)

# Function to update GUI with query results
def display_results(records, columns):
    for widget in frame.winfo_children():
        widget.destroy()
    tree = ttk.Treeview(frame, columns=columns, show="headings", height=8)
    tree.grid(column=0, row=0, sticky='nsew', padx=5, pady=5)
    for col in columns:
        tree.heading(col, text=col)
    for record in records:
        tree.insert("", tk.END, values=record)

# Bike CRUD Functions
def add_bike():
    model = simpledialog.askstring("Input", "Enter bike model:")
    status = simpledialog.askstring("Input", "Enter status (available/rented):")
    location_id = simpledialog.askinteger("Input", "Enter location ID:")
    sql = "INSERT INTO Bikes (Model, Status, LocationID) VALUES (%s, %s, %s)"
    execute_sql(sql, (model, status, location_id), commit=True)
    messagebox.showinfo("Info", "Bike added successfully")

def update_bike():
    bike_id = simpledialog.askinteger("Input", "Enter bike ID to update:")
    new_status = simpledialog.askstring("Input", "Enter new status (available/rented):")
    sql = "UPDATE Bikes SET Status = %s WHERE BikeID = %s"
    execute_sql(sql, (new_status, bike_id), commit=True)
    messagebox.showinfo("Info", "Bike updated successfully")

def delete_bike():
    bike_id = simpledialog.askinteger("Input", "Enter bike ID to delete:")
    sql = "DELETE FROM Bikes WHERE BikeID = %s"
    execute_sql(sql, (bike_id,), commit=True)
    messagebox.showinfo("Info", "Bike deleted successfully")

def display_bikes():
    sql = "SELECT BikeID, Model, Status, LocationID FROM Bikes"
    records = execute_sql(sql)
    display_results(records, ['BikeID', 'Model', 'Status', 'LocationID'])

# Customer CRUD Functions
def add_customer():
    first_name = simpledialog.askstring("Input", "Enter customer's first name:")
    last_name = simpledialog.askstring("Input", "Enter customer's last name:")
    email = simpledialog.askstring("Input", "Enter customer's email:")
    phone = simpledialog.askstring("Input", "Enter customer's phone number:")
    sql = "INSERT INTO Customers (FirstName, LastName, Email, Phone) VALUES (%s, %s, %s, %s)"
    execute_sql(sql, (first_name, last_name, email, phone), commit=True)
    messagebox.showinfo("Info", "Customer added successfully")

def display_customers():
    sql = "SELECT CustomerID, FirstName, LastName, Email, Phone FROM Customers"
    records = execute_sql(sql)
    display_results(records, ['CustomerID', 'FirstName', 'LastName', 'Email', 'Phone'])
    
def add_new_rental():
    # Popup to get rental information
    customer_id = simpledialog.askinteger("Input", "Enter Customer ID:")
    bike_id = simpledialog.askinteger("Input", "Enter Bike ID:")
    start_date = simpledialog.askstring("Input", "Enter Start Date (YYYY-MM-DD):")
    
    # SQL query to insert a new rental
    sql = """
    INSERT INTO Rentals (BikeID, CustomerID, StartDate, EndDate)
    VALUES (%s, %s, %s, NULL)
    """
    params = (bike_id, customer_id, start_date)
    
    # Execute SQL and handle exceptions
    try:
        execute_sql(sql, params, commit=True)
        messagebox.showinfo("Success", "New rental added successfully.")
        complex_query()  # Refresh the active rentals display
    except Error as e:
        messagebox.showerror("Error", "Failed to add new rental: " + str(e))


# Complex Query Example
def complex_query():
    sql = """
    SELECT c.FirstName, c.LastName, b.Model, r.StartDate, r.EndDate
    FROM Customers c
    JOIN Rentals r ON c.CustomerID = r.CustomerID
    JOIN Bikes b ON r.BikeID = b.BikeID
    WHERE r.EndDate IS NULL
    """
    try:
        records = execute_sql(sql)
        if records:
            display_results(records, ['FirstName', 'LastName', 'Model', 'StartDate', 'EndDate'])
        else:
            messagebox.showinfo("Result", "No active rentals found.")
    except Error as e:
        messagebox.showerror("SQL Error", str(e))

def detailed_rental_report():
    # SQL query that joins multiple tables to provide comprehensive rental information
    sql = """
    SELECT c.FirstName, c.LastName, b.Model, l.Address, r.StartDate, r.EndDate, r.TotalCost
    FROM Rentals r
    INNER JOIN Customers c ON r.CustomerID = c.CustomerID
    INNER JOIN Bikes b ON r.BikeID = b.BikeID
    INNER JOIN Locations l ON b.LocationID = l.LocationID
    ORDER BY r.StartDate DESC
    """
    try:
        records = execute_sql(sql)
        if records:
            display_results(records, ['FirstName', 'LastName', 'Model', 'Address', 'StartDate', 'EndDate', 'TotalCost'])
        else:
            messagebox.showinfo("Result", "No rental records found.")
    except Error as e:
        messagebox.showerror("SQL Error", str(e))



# Buttons for operations
ttk.Button(root, text="Add New Customer", command=add_customer, style='TButton').grid(column=0, row=0, sticky=tk.W, padx=10, pady=10)
ttk.Button(root, text="Display All Customers", command=display_customers, style='TButton').grid(column=1, row=0, sticky=tk.W, padx=10, pady=10)
ttk.Button(root, text="Add New Bike", command=add_bike, style='TButton').grid(column=2, row=0, sticky=tk.W, padx=10, pady=10)
ttk.Button(root, text="Update Bike Status", command=update_bike, style='TButton').grid(column=3, row=0, sticky=tk.W, padx=10, pady=10)
ttk.Button(root, text="Delete Bike", command=delete_bike, style='TButton').grid(column=4, row=0, sticky=tk.W, padx=10, pady=10)
ttk.Button(root, text="Display All Bikes", command=display_bikes, style='TButton').grid(column=5, row=0, sticky=tk.W, padx=10, pady=10)
ttk.Button(root, text="Active Rentals", command=complex_query, style='TButton').grid(column=6, row=0, sticky=tk.W, padx=10, pady=10)
ttk.Button(root, text="Add New Rental", command=add_new_rental, style='TButton').grid(column=7, row=0, sticky=tk.W, padx=10, pady=10)
ttk.Button(root, text="Detailed Rental Report", command=detailed_rental_report, style='TButton').grid(column=8, row=0, sticky=tk.W, padx=10, pady=10)

root.mainloop()
