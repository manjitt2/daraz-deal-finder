# database.py
import sqlite3
import datetime

def initialize_db():
    """Creates the database and the 'prices' table if they don't already exist."""
    # conn establishes a connection to the database file. If the file doesn't exist, it will be created.
    conn = sqlite3.connect('price_tracker.db')
    cursor = conn.cursor() # The cursor is used to execute SQL commands.

    # This SQL command creates a table named 'prices' with four columns.
    # CREATE TABLE IF NOT EXISTS ensures we don't get an error if the table is already there.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prices (
            id INTEGER PRIMARY KEY,
            product_title TEXT NOT NULL,
            price INTEGER NOT NULL,
            timestamp DATETIME NOT NULL
        )
    ''')
    
    # conn.commit() saves the changes (in this case, creating the table).
    conn.commit()
    # It's good practice to always close the connection when you're done.
    conn.close()
    print("Database initialized successfully.")

def save_price(title, price):
    """Saves a new price entry to the database."""
    conn = sqlite3.connect('price_tracker.db')
    cursor = conn.cursor()
    
    # Get the current time to store along with the price.
    current_timestamp = datetime.datetime.now()
    
    # The '?' are placeholders to prevent SQL injection, a common security risk.
    # We provide the actual values (title, price, timestamp) in the second argument.
    cursor.execute("INSERT INTO prices (product_title, price, timestamp) VALUES (?, ?, ?)", 
                   (title, price, current_timestamp))
    
    conn.commit()
    conn.close()

def get_lowest_price(title):
    """Gets the lowest price ever recorded for a specific product title."""
    conn = sqlite3.connect('price_tracker.db')
    cursor = conn.cursor()
    
    # This SQL command selects the minimum value from the 'price' column, but only for
    # rows where the 'product_title' matches the one we're checking.
    cursor.execute("SELECT MIN(price) FROM prices WHERE product_title = ?", (title,))
    
    # fetchone() retrieves the first row of the result. Our result is just one value.
    # It will be in a tuple, like (3599,), so we use [0] to get the value itself.
    result = cursor.fetchone()[0]
    
    conn.close()
    
    # If no price has ever been saved for this item, the 'result' will be None.
    # In that case, we return infinity, so the first price we see will always be lower.
    if result is None:
        return float('inf')
    else:
        return result