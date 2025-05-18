'''Create/update database for film collection'''

import pandas as pd
import sqlite3

# Read the csv file in
csv_file = pd.read_csv('bluray_dvd_collection - Collection.csv')

# Create a database connection
conn = sqlite3.connect('collection.db')

# Read the csv file into the database and replace data if it already exists
csv_file.to_sql('collection', 
                conn, 
                if_exists='replace', 
                index=False)

conn.close()  # Close the database connection