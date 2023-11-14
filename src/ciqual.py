#!/home/arii/workspaces/unix/nosave/ux/bin/python
import pandas as pd
import csv
import psycopg

#Convert the xls to csv
def convert(xls_file: str, csv_file: str) -> list:
    # Create the 
    input = pd.read_excel(xls_file, decimal=",").fillna(value="-")
    input.to_csv(csv_file, sep=";", index=False)

    # Print when it's done
    print(f'{xls_file} has been converted to {csv_file}')

# Call convert
#convert('in.xls', 'out.csv')

#import database into a list:
def import_csv(csv_file:str):
    # Initialize an empty list to store the data
    data_list = []

    # Open and read the CSV file
    with open(csv_file, mode='r') as lines:
        # Create a CSV reader object
        list_lines = csv.reader(lines, delimiter=';')
        data_pd = pd.read_csv(lines, delimiter=';') 

        # Iterate over each row in the CSV file
        for line in list_lines:
            data_list.append(line)
    print(data_pd)
    return data_list

# Get the data needed from the csv file and return list and dict
def get_data(csv_file: str) -> (list, dict, dict, list):
    all = import_csv(csv_file)
    header = all[0]

    # Get Nutrient names
    start = header.index("Eau (g/100 g)")
    nut_name = all[0][start:]
    
    # Prepare grp data
    grp_id_index = header.index("alim_grp_code")
    grp_nom_index = header.index("alim_grp_nom_fr")
    grp_id_name = dict()

    # Prepare Food data
    food_id_index = header.index("alim_code")
    food_name_index = header.index("alim_nom_fr")
    food_id_name_grpid = dict()

    # Prepare nutrient data
    nut_data = dict()

    for data in all[1:]:
        if data[grp_id_index] not in grp_id_name:
            grp_id_name[data[grp_id_index]] = data[grp_nom_index]
        if data[food_id_index] not in food_id_name_grpid:
            food_id_name_grpid[data[food_id_index]] = (data[food_name_index], data[grp_id_index])
        
#########   Use the panda ??? ###################
######### Create a dict with a list of "3 tupples" ?? #############
        nut_data.append(data[start:])
    return nut_name, grp_id_name, food_id_name_grpid, nut_data


def nutrient(cur, nut_name):
    table = "nutrient"

    # Drop Table if exists
    cur.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")
    
    # Execute a command: this creates a new table
    cur.execute(f"""
        CREATE TABLE {table} (
            id serial PRIMARY KEY,
            name text)
        """)
    
    # Pass data to fill a query placeholders and let Psycopg perform
    # the correct conversion (no SQL injections!)
    query = f"INSERT INTO {table} (name) VALUES (%s)"
    for values in nut_name:
        cur.execute(query, [values])

    # Query the database and obtain data as Python objects.
    # cur.execute(f"SELECT * FROM {table} WHERE name = %s", ['Potassium (mg/100 g)',])
    cur.execute(f"SELECT * FROM {table}")
    names = cur.fetchall()
    # will return (1, 100, "abc'def")

    # You can use `cur.fetchmany()`, `cur.fetchall()` to return a list
    # of several records, or even iterate on the cursor
    for name in names:
        print(name)

    # Make the changes to the database persistent
    # conn.commit()

def grp(cur, grp_id_name):
    table = "grp"

    # Drop Table if exists
    cur.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")
    
    # Execute a command: this creates a new table
    cur.execute(f"""
        CREATE TABLE {table} (
            id integer unique,
            name text)
        """)
    
    # Pass data to fill a query placeholders and let Psycopg perform
    # the correct conversion (no SQL injections!)
    query = f"INSERT INTO {table} (id, name) VALUES (%s, %s)"

    for id, name in grp_id_name.items():
        cur.execute(query, (id, name))

    # Query the database and obtain data as Python objects.
    # cur.execute(f"SELECT * FROM {table} WHERE name = %s", ['Potassium (mg/100 g)',])
    cur.execute(f"SELECT * FROM {table}")
    id_names = cur.fetchall()
    # will return (1, 100, "abc'def")

    # You can use `cur.fetchmany()`, `cur.fetchall()` to return a list
    # of several records, or even iterate on the cursor
    for id, names in id_names:
        print(id, name)

    # Make the changes to the database persistent
    # conn.commit()


def food(cur, food_id_name_grpid):
    table = "food"

    # Drop Table if exists
    cur.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")
    
    # Execute a command: this creates a new table
    cur.execute(f"""
        CREATE TABLE {table} (
            id text unique,
            name text,
            grp_id integer references grp(id) on delete cascade)
        """)
    
    # Pass data to fill a query placeholders and let Psycopg perform
    # the correct conversion (no SQL injections!)
    query = f"INSERT INTO {table} (id, name, grp_id) VALUES (%s, %s, %s)"

    for id, (name, grp_id) in food_id_name_grpid.items():
        cur.execute(query, (id, [name], grp_id))

    # Query the database and obtain data as Python objects.
    # cur.execute(f"SELECT * FROM {table} WHERE name = %s", ['Potassium (mg/100 g)',])
    cur.execute(f"SELECT * FROM {table}")
    names = cur.fetchall()
    # will return (1, 100, "abc'def")

    # You can use `cur.fetchmany()`, `cur.fetchall()` to return a list
    # of several records, or even iterate on the cursor
    for name in names:
        print(name)

    # Make the changes to the database persistent
    # conn.commit()

def nutdata(cur, nut_data):
    table = "nutdata"

    # Drop Table if exists
    cur.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")
    
    # Execute a command: this creates a new table
    cur.execute(f"""
        CREATE TABLE {table} (
            id serial primary key,
            food_id integer references food(id) on delete cascade,
            grp_id integer references grp(id) on delete cascade,
            value text)
        """)
    
    # Pass data to fill a query placeholders and let Psycopg perform
    # the correct conversion (no SQL injections!)
    query = f"INSERT INTO {table} (id, name, grp_id) VALUES (%s, %s, %s)"

    for id, (name, grp_id) in nut_data:
        cur.execute(query, (id, [name], grp_id))

    # Query the database and obtain data as Python objects.
    # cur.execute(f"SELECT * FROM {table} WHERE name = %s", ['Potassium (mg/100 g)',])
    cur.execute(f"SELECT * FROM {table}")
    names = cur.fetchall()
    # will return (1, 100, "abc'def")

    # You can use `cur.fetchmany()`, `cur.fetchall()` to return a list
    # of several records, or even iterate on the cursor
    for name in names:
        print(name)

    # Make the changes to the database persistent
    # conn.commit()

def main():
    import_csv("./src/ciqual_data/sample.csv")
    # Treat csv
    # nut_name, grp_id_name, food_id_name_grpid, nut_data = get_data("./src/ciqual_data/sample.csv")
    # # A personaliser plus tard
    # db_name = 'ciqual'
    # db_user = 'arii'


    # # Connect to an existing database
    # with psycopg.connect(dbname=db_name, user=db_user) as conn:

    #     # Open a cursor to perform database operations
    #     with conn.cursor() as cur:
    #         nutrient(cur, nut_name)
    #         grp(cur, grp_id_name)
    #         food(cur, food_id_name_grpid)
            

            # Make the changes to the database persistent
            # conn.commit()

if __name__ == "__main__":
    main()



# Nutrient
#    id: int (autoincrement)
#    name string

# Food
#    id: string
#    name: string
#    grp_id: string (clé étrangère vers Grp(id))

# Grp
#    id: string
#    name: string

# NutData
#    id: int (autoincrement)
#    food_id: string (clé étrangère vers Food(id))
#    nutrient_id: int (clé étrangère vers Nutrient(id))
#    value: string