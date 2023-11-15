#!/usr/bin/env python 
import pandas as pd, psycopg

#Convert the xls to csv
def convert(xls_file: str, csv_file: str) -> None:
    input = pd.read_excel(xls_file, decimal=",")
    input.to_csv(csv_file, sep=";", index=False)
    print(f'{xls_file} has been converted to {csv_file}')

# Get the data needed from the csv file and return a pandas datafram
def get_data(file: str) -> pd:
    if file.endswith("csv"):
        pd_data = pd.read_csv(file, decimal=",", delimiter=";") #.replace(regex="[-<>]", value=None)
    elif file.endswith("xls"):
        pd_data = pd.read_excel(file, decimal=",") #.replace(regex="[-<>]", value=None)
    return pd_data

# Create nutrient table and insert data
def nutrient(cur: psycopg, pd_data: pd) -> None:
    table = "nutrient"
    start = list(pd_data.keys()).index("Eau (g/100 g)")
    nut_names = pd_data.keys()[start:]

    # Drop Table if exists
    cur.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")
    print(f'{table} table dropped')
    
    # Create the table
    cur.execute(f"""CREATE TABLE {table} (
                    id serial PRIMARY KEY,
                    name text)""")
    print(f'{table} table ---------> created')

    # Query to insert
    query = f"INSERT INTO {table} (name) VALUES (%s)"
    for nut_name in nut_names:
        cur.execute(query, [nut_name])
    print(f'{table} ------------------------> id and name inserted')

# Create grp table and insert data
def grp(cur: psycopg, pd_data: pd) -> None:
    table = "grp"
    # Drop Table if exists
    cur.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")
    print(f'{table} table dropped')
    
    # Create the table
    cur.execute(f"""CREATE TABLE {table} (
                    id integer primary key, 
                    name text)""")
    print(f'{table} table ---------> created')
    
    # Insert data
    query = f"INSERT INTO {table} (id, name) VALUES (%s, %s) ON CONFLICT (id) DO NOTHING"
    for id, name in zip(pd_data["alim_grp_code"], pd_data["alim_grp_nom_fr"]):
        cur.execute(query, (id, [name]))
    print(f"{table} ------------------------> id and name inserted")

# Create food table and insert data
def food(cur: psycopg, pd_data: pd) -> None:
    table = "food"

    # Drop Table if exists
    cur.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")
    print(f'{table} table dropped')
    
    # Create the table
    cur.execute(f"""CREATE TABLE {table} (
                    id integer primary key,
                    name text,
                    grp_id integer references grp(id) on delete cascade)""")
    print(f"{table} table ---------> created")
    
    # Insert data
    query = f"INSERT INTO {table} (id, name, grp_id) VALUES (%s, %s, %s) ON CONFLICT (id) DO NOTHING"
    for id, name, grp_id in zip(pd_data["alim_code"], pd_data["alim_nom_fr"], pd_data["alim_grp_code"]):
        cur.execute(query, (id, name, grp_id))
    print(f"{table} ------------------------> id, name and grp_id inserted")

# Create nutdata table and insert data
def nutdata(cur: psycopg, pd_data: pd) -> None:
    table = "nutdata"

    # Check the needed tables
    cur.execute("""SELECT table_name FROM information_schema.tables
       WHERE table_schema = 'public'""")
    tables = set([table[0] for table in cur.fetchall()])
    needed_tables = set(["nutrient", "grp","food"])    
    if needed_tables & tables != needed_tables:
        raise ValueError

    # Drop Table if exists
    cur.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")
    print(f"{table} table dropped")
    
    # Create the table
    cur.execute(f"""CREATE TABLE {table} (
                    id serial primary key,
                    food_id integer references food(id) on delete cascade,
                    nutrient_id integer references nutrient(id) on delete cascade,
                    value text)""")
    print(f"{table} table ---------> created")
    
    # Get nutrient_id
    query = f"SELECT id, name FROM nutrient;"
    cur.execute(query)
    response = cur.fetchall()
    nutrient_ids = [id[0] for id in response]
    nut_names = [id[1] for id in response]

    query = f"SELECT id FROM food;"
    cur.execute(query)
    food_ids = [id[0] for id in cur.fetchall()]

    start = list(pd_data.keys()).index("Eau (g/100 g)")
    # nut_names = pd_data.keys()[start:]

    # Insert data
    query = f"INSERT INTO {table} (food_id, nutrient_id, value) VALUES (%s, %s, %s)"

    for row, food_id in enumerate(food_ids):
        for nutrient_id, nut_name in zip(nutrient_ids, nut_names):
            cur.execute(query, (food_id, nutrient_id, str(pd_data[nut_name][row])))         
    print(f"{table} ------------------------> data inserted")

def main():
    try:
        # Convert xls to csv
        # convert("./src/ciqual_data/in.xls", "./src/ciqual_data/out.csv")

        # Retrieve data anoter possibilty --> pd_data = get_data("./src/ciqual_data/sample.csv")
        pd_data = get_data("./src/ciqual_data/in.xls")
        
        # Database info connection
        db_name = 'ciqual'
        db_user = ''

        create = False # True
        if create:
            # Connect to the database
            with psycopg.connect(dbname=db_name, user=db_user) as conn:

                # Open a cursor to make some operations
                with conn.cursor() as cur:
                    # Create tables and insert data
                    nutrient(cur, pd_data)
                    grp(cur, pd_data)
                    food(cur, pd_data)
                    nutdata(cur, pd_data)
                    
                    # Commit the changes to the database
                    conn.commit()

        find = True
        if find:
        # Connect to the database
            with psycopg.connect(dbname=db_name, user=db_user) as conn:

                # Open a cursor to make some operations
                with conn.cursor() as cur:
                    # Select data
                    query = """SELECT food.name, 
                            CASE 
                                WHEN value ~ '^[0-9]+(\.[0-9]+)?$' THEN CAST(value AS NUMERIC)
                                ELSE 0
                            END as calcium 
                            FROM food, nutdata, nutrient 
                            WHERE nutrient.name = 'Calcium (mg/100 g)' and nutrient.id = nutdata.nutrient_id and food.id = nutdata.food_id 
                            order by calcium DESC LIMIT 10;"""

                    df = pd.read_sql_query(query, conn)
                    print(df)

                    
    except pd.errors.EmptyDataError as e:
        print(e)
    except Exception as e:
        print(e)
    

if __name__ == "__main__":
    main()