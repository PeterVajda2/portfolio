import pyodbc

server = '10.49.34.76' 
database = 'Provozni_data' 
username = 'stavy_r' 
password = 'Stavy_R10' 
cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = cnxn.cursor()

cursor.execute("SELECT * FROM dbo.OBC_Linka3") 
row = cursor.fetchone() 
while row: 
    print(row[0])
    row = cursor.fetchone()