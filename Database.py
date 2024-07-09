# Establish MySQL connection
import mysql.connector

class Database:
  def startDatabase(self):
    try:
      mydb = mysql.connector.connect(
          host="awseb-e-miyj3vcadm-stack-awsebrdsdatabase-6f6zhnae7nyo.cuvtcsmymjms.eu-west-2.rds.amazonaws.com",
          user="playdateProd",
          password="0l9yD$t20_a#p",
          database="ebdb",
          port=3306,
      )
      mycursor = mydb.cursor()
      return (mydb, mycursor)
    except mysql.connector.Error as err:
        print(f"MySQL Error: {err}")
        raise err
  
  