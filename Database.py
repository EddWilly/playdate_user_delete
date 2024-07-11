# Establish MySQL connection
import mysql.connector
import os
from dotenv import load_dotenv
class Database:
  load_dotenv()
  def startDatabase(self):
    try:
      mydb = mysql.connector.connect(
          host = os.getenv('DB_HOST'),
          user = os.getenv('DB_USER'),
          password = os.getenv('DB_PASSWORD'),
          database = os.getenv('DB_DATABASE'),
          port = os.getenv('DB_PORT')
      )
      mycursor = mydb.cursor()
      return (mydb, mycursor)
    except mysql.connector.Error as err:
        print(f"MySQL Error: {err}")
        raise err
  
  