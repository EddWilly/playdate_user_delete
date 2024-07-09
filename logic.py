import mysql.connector
import re
from fastapi import FastAPI, HTTPException
from Database import Database

app = FastAPI()

database = Database()
mydb = None 

def initDB():
    global mydb
    mydb, mycursor = database.startDatabase()
    useDatabase = "USE ebdb;"
    mycursor.execute(useDatabase)
    mycursor.close()

def fetch_results(query, params=None):
    print("Starting execution of query for fetching results...")
    try:
        mycursor = mydb.cursor(buffered=True)
        if params:
            mycursor.execute(query, params)
        else:
            mycursor.execute(query)
        results = mycursor.fetchall()
        print(f"Fetched results for query: {query} with params: {params}")
        mycursor.close()
        return results
    except mysql.connector.Error as err:
        print(f"Error fetching results for query: {query} with params: {params}")
        print(f"MySQL Error: {err}")
        mycursor.close()
        raise err

def decode_if_byte(data):
    if isinstance(data, (bytes, bytearray)):
        return data.decode('utf-8')
    return data

def get_primary_key_column(table_name):
    query = """
    SELECT COLUMN_NAME
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = 'ebdb'
    AND TABLE_NAME = %s
    AND COLUMN_KEY = 'PRI'
    """
    primary_key_column = fetch_results(query, (table_name,))
    if primary_key_column:
        return decode_if_byte(primary_key_column[0][0])
    else:
        raise Exception(f"No primary key found for table {table_name}")

def delete_related_records(table_name, primary_key_column, primary_key_value):
    # Find all constraints referencing this table
    constraints_query = """
        SELECT TABLE_NAME, COLUMN_NAME
        FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
        WHERE REFERENCED_TABLE_SCHEMA = %s
        AND REFERENCED_TABLE_NAME = %s
        AND REFERENCED_COLUMN_NAME = %s
    """
    constraints = fetch_results(constraints_query, ('ebdb', table_name, primary_key_column))

    # Recursively delete from child tables first
    for constraint in constraints:
        child_table = decode_if_byte(constraint[0])
        child_column = decode_if_byte(constraint[1])

        # Get primary key column of the child table
        child_pk_column = get_primary_key_column(child_table)

        # Fetch records that need to be deleted from child table
        select_child_query = f"SELECT `{child_pk_column}` FROM `{child_table}` WHERE `{child_column}` = %s"
        child_records = fetch_results(select_child_query, (primary_key_value,))

        # Recursively delete child records
        for child_record in child_records:
            delete_related_records(child_table, child_pk_column, child_record[0])

        # Delete the records from the child table
        delete_child_query = f"DELETE FROM `{child_table}` WHERE `{child_column}` = %s"
        mycursor = mydb.cursor(buffered=True)
        mycursor.execute(delete_child_query, (primary_key_value,))
        mydb.commit()
        mycursor.close()

    # Delete the record from the current table
    delete_parent_query = f"DELETE FROM `{table_name}` WHERE `{primary_key_column}` = %s"
    mycursor = mydb.cursor(buffered=True)
    mycursor.execute(delete_parent_query, (primary_key_value,))
    mydb.commit()
    mycursor.close()

@app.get("/delete_user/{email}")
async def delete_user(email: str):
    try:
        initDB()
        print(f"Database switched to: ebdb")

        # Step 1: Find the user ID
        user_query = "SELECT id FROM playdate_auth_account WHERE email = %s"
        user_result = fetch_results(user_query, (email,))

        if not user_result:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_id = user_result[0][0]
        print(f"User found with ID: {user_id} and email {email}. Proceeding with deletion...")

        # Step 2: Delete related records recursively
        delete_related_records("playdate_auth_account", "id", user_id)
        return {"status": "Success", "message": f"User {email} and related data successfully deleted."}

    except mysql.connector.Error as err:
        print(f"Error occurred: {err}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
