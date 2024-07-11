# Establish MySQL connection
import mysql.connector
import os
from dotenv import load_dotenv
class Database:
  load_dotenv()
  def startDatabase(self):
    try:
      mydb = mysql.connector.connect(
          db_host = os.getenv('DB_HOST'),
          db_user = os.getenv('DB_USER'),
          db_password = os.getenv('DB_PASSWORD'),
          db_database = os.getenv('DB_DATABASE'),
          db_port = os.getenv('DB_PORT')
      )
      mycursor = mydb.cursor()
      return (mydb, mycursor)
    except mysql.connector.Error as err:
        print(f"MySQL Error: {err}")
        raise err
  
  