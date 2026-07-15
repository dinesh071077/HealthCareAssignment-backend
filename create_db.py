import pymysql

connection = pymysql.connect(
    host='localhost',
    user='root',
    password='Dinesh936044@',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

try:
    with connection.cursor() as cursor:
        cursor.execute("CREATE DATABASE IF NOT EXISTS crm_db;")
    connection.commit()
    print("Database crm_db created successfully.")
finally:
    connection.close()
